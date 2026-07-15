#!/bin/bash
#
# build-mac.sh - Mac build pipeline for Baker Bridge lesson collection
#
# This script runs the complete build process using Rust tools (dealer3, bridge-wrangler)
# instead of Windows tools (dealer.exe, BridgeComposer).
#
# Usage:
#   ./build-mac.sh [phase] [options]
#
# Shortcuts:
#   classroom      Build Package for bridge-classroom app
#                  parse → validate → correct → sme → fill → pbn → pbn-pdf
#                  → package
#   rotations      Build Rotations for live teacher classes
#                  parse → validate → correct → sme → fill → pbn → pbn-pdf
#                  → package → presentation → rotate
#   Both reuse existing constructed_hands.csv unless --generate is specified.
#
# Individual phases:
#   (none)         Show list of available phases
#   *              Run all phases
#   parse          Parse HTML and extract hands
#   validate       Validate card data
#   correct        Auto-correct duplicate cards
#   sme            Apply SME corrections (dealer, card exchanges)
#   missing        Identify hands with missing bidders
#   generate       Generate constrained hands
#   fill           Fill missing hands
#   pbn            Convert to PBN format
#   intro-pdf      Convert introduction pages to PDF
#   pbn-pdf        Convert PBNs to PDFs
#   package        Package results
#   presentation   Create presentation structure
#   rotate         Generate rotations for multi-table play
#   publish        Mirror Rotations/ to the public Google Drive teacher folder
#
# Options:
#   --lesson NAME  Filter to a specific lesson (for presentation/rotate/publish steps)
#   --generate     Regenerate constrained hands (with classroom/rotations)
#   --clean        Remove existing build artifacts before building
#   --help         Show this help message
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Build folder layout (issue #21, Phase B). The merge+stamp+manifest steps write the
# shared master, Collection/ (replacing Package/'s old role; Package/ is a frozen orphan).
# Two exports diverge from Collection/ — they are NOT chained through each other:
#   - bridge-classroom/  the app's contracted files (control-tag PBNs + manifest/toc/titles
#                        + optional intros), copied out of Collection/ by the `export` phase.
#   - Presentation/ -> Rotations/  the face-to-face teaching materials (tags stripped, table
#                        rotations), built from Collection/ by presentation/rotate.
# BB_PACKAGE_DIR points the package/stamp/manifest/toc/presentation/audit scripts at the
# master; override it to rebuild elsewhere.
COLLECTION_DIR="${BB_PACKAGE_DIR:-$REPO_ROOT/Collection}"
BRIDGE_CLASSROOM_DIR="$REPO_ROOT/bridge-classroom"
export BB_PACKAGE_DIR="$COLLECTION_DIR"
# Back-compat alias: several helpers below still say PACKAGE_DIR meaning the master.
PACKAGE_DIR="$COLLECTION_DIR"

# Publish target: the public-readable Google Drive copy of Rotations/ that teachers use
# (easier to access than GitHub). Override with BB_PUBLISH_DIR. The `publish` phase mirrors
# Rotations/ here with rsync --delete (so files removed from the master are removed here too).
PUBLISH_DIR="${BB_PUBLISH_DIR:-/Users/rick/Library/CloudStorage/GoogleDrive-bridge.craftwork@gmail.com/My Drive/For Teachers/Lesson Collections/Baker Bridge Collection}"

# Tool paths
DEALER_PATH="$HOME/Development/GitHub/dealer3/target/release/dealer"
BRIDGE_WRANGLER_PATH="$HOME/Development/GitHub/bridge-wrangler/target/release/bridge-wrangler"

# Build phases: name|description
PHASES=(
    "parse|Parse HTML and extract hands"
    "validate|Validate card data"
    "correct|Auto-correct duplicate cards"
    "sme|Apply SME corrections"
    "missing|Identify hands with missing bidders"
    "generate|Generate constrained hands"
    "fill|Fill missing hands"
    "reroll|Re-roll quiet passers (BBA-reject, managed variety)"
    "pbn|Convert to PBN format"
    "intro-pdf|Convert introduction pages to PDF"
    "pbn-pdf|Convert PBNs to PDFs"
    "package|Package results"
    "stamp|Stamp board tokens and generate manifest"
    "export|Export bridge-classroom contract files from Collection"
    "presentation|Create presentation structure"
    "rotate|Generate rotations for multi-table play"
    "publish|Publish Rotations/ to the public Google Drive teacher folder (delete + copy; explicit, excluded from '*')"
)

# Parse arguments
CLEAN=false
GENERATE=false
LESSON=""
PHASE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --generate)
            GENERATE=true
            shift
            ;;
        --lesson)
            if [[ -z "$2" || "$2" == -* ]]; then
                echo "Error: --lesson requires a name"
                exit 1
            fi
            LESSON="$2"
            shift 2
            ;;
        --help|-h)
            head -42 "$0" | tail -39
            exit 0
            ;;
        -*)
            echo "Unknown option: $1"
            exit 1
            ;;
        *)
            if [[ -z "$PHASE" ]]; then
                PHASE="$1"
            else
                echo "Error: Multiple phases specified"
                exit 1
            fi
            shift
            ;;
    esac
done

# Helper functions
step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

warn() {
    echo -e "${YELLOW}Warning: $1${NC}"
}

error() {
    echo -e "${RED}Error: $1${NC}"
    exit 1
}

check_tool() {
    if [[ ! -x "$1" ]]; then
        error "$2 not found at $1. Please build it first."
    fi
}

show_phases() {
    echo -e "${GREEN}Shortcuts:${NC}"
    echo ""
    printf "  %-14s %s\n" "classroom" "Build Package for bridge-classroom app (fast)"
    printf "  %-14s %s\n" "rotations" "Build Rotations for live teacher classes"
    echo ""
    echo -e "${GREEN}Individual phases:${NC}"
    echo ""
    for entry in "${PHASES[@]}"; do
        local name="${entry%%|*}"
        local desc="${entry#*|}"
        printf "  %-14s %s\n" "$name" "$desc"
    done
    echo ""
    echo -e "${GREEN}Options:${NC}"
    echo ""
    printf "  %-18s %s\n" "--lesson NAME" "Filter to a specific lesson (presentation/rotate steps)"
    printf "  %-18s %s\n" "--generate" "Regenerate constrained hands (with classroom/rotations)"
    printf "  %-18s %s\n" "--clean" "Remove build artifacts before building"
    echo ""
    echo "Examples:"
    echo "  ./build-mac.sh classroom                       Quick build for app testing"
    echo "  ./build-mac.sh rotations                       Build rotations (all lessons)"
    echo "  ./build-mac.sh rotations --lesson Ogust        Build rotations for one lesson"
    echo "  ./build-mac.sh rotations --generate            Regenerate constrained hands"
    echo "  ./build-mac.sh rotate --lesson Finesse         Just rotate one lesson"
    echo "  ./build-mac.sh publish                         Mirror all Rotations to Google Drive"
    echo "  ./build-mac.sh publish --lesson Ogust          Publish just one lesson"
    echo "  PUBLISH_ARGS=-n ./build-mac.sh publish         Dry-run the publish (show changes only)"
    echo "  ./build-mac.sh parse                           Run a single phase"
    echo "  ./build-mac.sh '*'                             Run all phases"
}

# Phase functions
phase_parse() {
    step "Parse HTML and Extract Hands"
    cd "$SCRIPT_DIR"
    python3 bbparse.py
    echo "Output: BakerBridge.csv"
}

phase_validate() {
    step "Validate Card Data"
    cd "$SCRIPT_DIR"
    if [[ ! -f "BakerBridge.csv" ]]; then
        error "BakerBridge.csv not found. Run 'parse' phase first."
    fi
    python3 bbcheck.py BakerBridge.csv > bbcheck.txt
    ERRORS=$(grep -c "ERROR" bbcheck.txt 2>/dev/null || true)
    ERRORS=${ERRORS:-0}
    echo "Output: bbcheck.txt (found $ERRORS errors)"
}

phase_correct() {
    step "Auto-Correct Duplicate Cards"
    cd "$SCRIPT_DIR"
    if [[ ! -f "BakerBridge.csv" ]]; then
        error "BakerBridge.csv not found. Run 'parse' phase first."
    fi
    python3 bb_correct.py BakerBridge.csv --apply 2>/dev/null || true
    echo "Applied corrections to BakerBridge.csv"
}

phase_sme() {
    step "Apply SME Corrections"
    cd "$SCRIPT_DIR"
    if [[ ! -f "BakerBridge.csv" ]]; then
        error "BakerBridge.csv not found. Run 'parse' phase first."
    fi
    if [[ -f "auction-fixes/sme_corrections.txt" ]]; then
        python3 auction-fixes/apply_sme_corrections.py
    else
        echo "No sme_corrections.txt found - skipping"
    fi
}

phase_missing() {
    step "Identify Hands with Missing Bidders"
    cd "$SCRIPT_DIR"
    if [[ ! -f "BakerBridge-sme.csv" ]]; then
        error "BakerBridge-sme.csv not found. Run 'sme' phase first."
    fi
    python3 check_missing_bids.py BakerBridge-sme.csv missing_bids.csv
    MISSING=$(wc -l < missing_bids.csv | tr -d ' ')
    echo "Output: missing_bids.csv ($((MISSING - 1)) hands need generation)"
}

phase_generate() {
    step "Generate Constrained Hands (using dealer3)"
    cd "$SCRIPT_DIR"
    check_tool "$DEALER_PATH" "dealer3"
    if [[ ! -f "missing_bids.csv" ]]; then
        error "missing_bids.csv not found. Run 'missing' phase first."
    fi
    python3 fill_hands.py --dealer "$DEALER_PATH"
    GENERATED=$(wc -l < constructed_hands.csv | tr -d ' ')
    echo "Output: constructed_hands.csv ($((GENERATED - 1)) hands generated)"
}

phase_fill() {
    step "Fill Missing Hands"
    cd "$SCRIPT_DIR"
    if [[ ! -f "BakerBridge-sme.csv" ]]; then
        error "BakerBridge-sme.csv not found. Run 'sme' phase first."
    fi
    if [[ ! -f "constructed_hands.csv" ]]; then
        error "constructed_hands.csv not found. Run 'generate' phase first."
    fi
    python3 bb_fill.py BakerBridge-sme.csv BakerBridgeFull.csv constructed_hands.csv
    TOTAL=$(wc -l < BakerBridgeFull.csv | tr -d ' ')
    echo "Output: BakerBridgeFull.csv ($((TOTAL - 1)) total hands)"
}

phase_reroll() {
    step "Re-roll Passer Hands (BBA-reject, managed variety)"
    cd "$SCRIPT_DIR"
    if [[ ! -f "BakerBridgeFull.csv" ]]; then
        error "BakerBridgeFull.csv not found. Run 'fill' phase first."
    fi
    # Unified BBA-reject re-roll of the generated *quiet* passers (issue #21, Phase B).
    # Supersedes both auction_calm (fill_hands) and bb_fill's random E/W assignment.
    # Reuses the committed passer_cache.csv; pass --revalidate (via REROLL_ARGS) to
    # re-check cached fills.
    python3 passer_reroll.py BakerBridgeFull.csv --sme BakerBridge-sme.csv \
        --cache passer_cache.csv $REROLL_ARGS
    echo "Output: BakerBridgeFull.csv (quiet passers BBA-clean) + passer_cache.csv"
}

phase_pbn() {
    local csv_file="${1:-BakerBridgeFull.csv}"
    step "Convert to PBN Format (from $csv_file)"
    cd "$SCRIPT_DIR"
    if [[ ! -f "$csv_file" ]]; then
        error "$csv_file not found."
    fi
    python3 CSV_to_PBN.py "$csv_file"
    # Inject the defense-lesson [showcards] dummy-card fixes (answer key; the
    # cards can't be recovered from the source HTML — see apply_showcards_dummy.py).
    python3 apply_showcards_dummy.py pbns
    PBN_COUNT=$(find pbns -name "*.pbn" | wc -l | tr -d ' ')
    echo "Output: pbns/ ($PBN_COUNT PBN files)"
}

phase_intro_pdf() {
    step "Convert Introduction Pages to PDF (using html2pdf)"
    cd "$SCRIPT_DIR"
    if command -v html2pdf &> /dev/null; then
        ./convert_html_to_pdf.sh 2>&1 | grep -E "^(Converting:|Conversion|  Total|  Converted|  Failed)"
        INTRO_PDF_COUNT=$(find pdfs -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
        echo "Output: pdfs/ ($INTRO_PDF_COUNT intro PDFs)"
    else
        warn "Skipping - html2pdf not found"
        warn "Install with: brew install ilaborie/tap/html2pdf"
        mkdir -p pdfs
    fi
}

phase_pbn_pdf() {
    step "Convert PBNs to PDFs (using bridge-wrangler)"
    cd "$SCRIPT_DIR"
    check_tool "$BRIDGE_WRANGLER_PATH" "bridge-wrangler"
    if [[ ! -d "pbns" ]]; then
        error "pbns/ not found. Run 'pbn' phase first."
    fi
    python3 convert_pbns_to_pdfs.py --bridge-wrangler "$BRIDGE_WRANGLER_PATH"
    PDF_COUNT=$(find pbns -name "*.pdf" | wc -l | tr -d ' ')
    echo "Generated $PDF_COUNT PDF files alongside PBNs"
}

phase_package() {
    step "Package Results"
    cd "$SCRIPT_DIR"
    mkdir -p "$PACKAGE_DIR"
    python3 package_results.py
    # titles.csv is a static asset (not generated); seed it into the output dir from the
    # canonical copy that still lives in the orphaned Package/.
    if [[ -f "$REPO_ROOT/Package/titles.csv" && ! -f "$PACKAGE_DIR/titles.csv" ]]; then
        cp "$REPO_ROOT/Package/titles.csv" "$PACKAGE_DIR/"
    fi
    # Companion lesson intros (*_Intro.pdf) are contract artifacts shown in the app. They are
    # generated by the intro-pdf phase (needs html2pdf); when that ran, package_results.py
    # already copied them. Otherwise seed the canonical committed intros from Package/.
    for intro in "$REPO_ROOT/Package"/*_Intro.pdf; do
        [[ -e "$intro" ]] || break
        [[ -f "$PACKAGE_DIR/$(basename "$intro")" ]] || cp "$intro" "$PACKAGE_DIR/"
    done
    PKG_COUNT=$(find "$PACKAGE_DIR" -type f | wc -l | tr -d ' ')
    echo "Output: $PACKAGE_DIR ($PKG_COUNT files)"
}

phase_stamp() {
    step "Stamp Board Tokens + Manifest"
    cd "$SCRIPT_DIR"
    # Must run AFTER package_results.py (curated merge): both the board-version
    # tokens and the manifest are stamped from the final released Package/ content.
    python3 stamp_board_tokens.py
    python3 generate_manifest.py
    echo "Output: $COLLECTION_DIR/*.pbn tokens + $COLLECTION_DIR/manifest.json"
}

phase_export() {
    step "Export Bridge-Classroom Contract Files (from Collection)"
    cd "$SCRIPT_DIR"
    # bridge-classroom/ is the app's contracted export, copied out of the Collection master:
    # control-tag PBNs + manifest.json + toc.json + titles.csv + optional *_Intro.pdf.
    # (PDFs other than intros are teaching artifacts and are NOT part of the app contract.)
    if [[ ! -d "$COLLECTION_DIR" ]]; then
        error "Collection/ not found. Run 'package' + 'stamp' first."
    fi
    mkdir -p "$BRIDGE_CLASSROOM_DIR"
    # Clear stale exports, then copy the current contract set.
    find "$BRIDGE_CLASSROOM_DIR" -type f \( -name '*.pbn' -o -name '*.json' \
        -o -name 'titles.csv' -o -name '*_Intro.pdf' \) -delete 2>/dev/null || true
    for pat in '*.pbn' 'manifest.json' 'toc.json' 'titles.csv' '*_Intro.pdf'; do
        for f in "$COLLECTION_DIR"/$pat; do
            [[ -e "$f" ]] && cp "$f" "$BRIDGE_CLASSROOM_DIR/"
        done
    done
    BC_COUNT=$(find "$BRIDGE_CLASSROOM_DIR" -type f | wc -l | tr -d ' ')
    echo "Output: bridge-classroom/ ($BC_COUNT contract files)"
}

phase_presentation() {
    step "Create Presentation Structure"
    cd "$REPO_ROOT"
    python3 Tools/package_presentation.py
    PRES_COUNT=$(find "$REPO_ROOT/Presentation" -type f | wc -l | tr -d ' ')
    echo "Output: Presentation/ ($PRES_COUNT files)"
}

phase_rotate() {
    local filter="${1:-*}"
    step "Generate Rotations (using bridge-wrangler) [filter: $filter]"
    cd "$REPO_ROOT"
    check_tool "$BRIDGE_WRANGLER_PATH" "bridge-wrangler"
    ./Tools/rotate_lesson_collection.sh "$filter" "*" 4 5 6
    ROT_COUNT=$(find "$REPO_ROOT/Rotations" -type f | wc -l | tr -d ' ')
    echo "Output: Rotations/ ($ROT_COUNT files)"
}

phase_publish() {
    # Publish Rotations/ (our face-to-face product) to the public Google Drive teacher folder.
    # Method: mass-delete the old copy, then ONE bulk copy of the new. On the Google Drive
    # FUSE mount this is far faster than a per-file rsync (Drive batches a bulk copy; a
    # per-file sync thrashes the mount). This is also how it's published by hand in Finder.
    # It inherently drops anything no longer in the master (the whole target is replaced).
    # Whole tree by default, or a single lesson with --lesson (matches the lesson folder name).
    # Deliberately NOT part of the classroom/rotations shortcuts or '*': publishing is an
    # explicit, outward-facing release action. PUBLISH_ARGS=-n previews without touching Drive.
    local filter="${LESSON:-}"
    local dry=""; [[ "$PUBLISH_ARGS" == *-n* ]] && dry=1
    step "Publish Rotations -> Google Drive"
    if [[ ! -d "$REPO_ROOT/Rotations" ]]; then
        error "Rotations/ not found. Run 'rotate' first."
    fi
    # Safety: never rm -rf an unsafe target.
    case "$PUBLISH_DIR" in
        ""|"/"|"$HOME"|"$HOME/") error "Refusing to publish to unsafe path: '$PUBLISH_DIR'" ;;
    esac
    local destparent; destparent="$(dirname "$PUBLISH_DIR")"
    if [[ ! -d "$destparent" ]]; then
        error "Publish target parent not found: $destparent
    (is Google Drive mounted? override the location with BB_PUBLISH_DIR=...)"
    fi
    if [[ -z "$filter" || "$filter" == "*" ]]; then
        echo "Replacing the entire collection at:"
        echo "  $PUBLISH_DIR"
        if [[ -n "$dry" ]]; then
            echo "[dry-run] rm -rf \"\$PUBLISH_DIR\" && cp -R Rotations \"\$PUBLISH_DIR\""
        else
            rm -rf "$PUBLISH_DIR"
            cp -R "$REPO_ROOT/Rotations" "$PUBLISH_DIR"
            echo "Published: entire tree ($(find "$PUBLISH_DIR" -type f | wc -l | tr -d ' ') files)."
        fi
    else
        local found=0 lessondir rel
        while IFS= read -r lessondir; do
            found=1
            rel="${lessondir#$REPO_ROOT/Rotations/}"
            if [[ -n "$dry" ]]; then
                echo "[dry-run] replace: $rel"
            else
                rm -rf "$PUBLISH_DIR/$rel"
                mkdir -p "$(dirname "$PUBLISH_DIR/$rel")"
                cp -R "$lessondir" "$PUBLISH_DIR/$rel"
                echo "Published: $rel"
            fi
        done < <(find "$REPO_ROOT/Rotations" -mindepth 2 -maxdepth 2 -type d -iname "*$filter*")
        [[ "$found" == 1 ]] || warn "No Rotations lesson folder matched '$filter'"
    fi
    echo "Done. Google Drive Desktop will sync in the background."
}

do_clean() {
    step "Cleaning build artifacts"
    cd "$SCRIPT_DIR"
    rm -rf pbns pdfs constructed_hands.csv BakerBridgeFull.csv
    rm -rf "$COLLECTION_DIR" "$BRIDGE_CLASSROOM_DIR" "$REPO_ROOT/Presentation" "$REPO_ROOT/Rotations"
    echo "Cleaned: pbns/, pdfs/, Package/, Presentation/, Rotations/, intermediate CSVs"
}

run_phase() {
    local phase="$1"
    case "$phase" in
        parse)        phase_parse ;;
        validate)     phase_validate ;;
        correct)      phase_correct ;;
        sme)          phase_sme ;;
        missing)      phase_missing ;;
        generate)     phase_generate ;;
        fill)         phase_fill ;;
        reroll)       phase_reroll ;;
        pbn)          phase_pbn ;;
        intro-pdf)    phase_intro_pdf ;;
        pbn-pdf)      phase_pbn_pdf ;;
        package)      phase_package ;;
        stamp)        phase_stamp ;;
        export)       phase_export ;;
        presentation) phase_presentation ;;
        rotate)       phase_rotate "${LESSON:-*}" ;;
        publish)      phase_publish ;;
        *)
            echo "Unknown phase: $phase"
            echo ""
            show_phases
            exit 1
            ;;
    esac
}

run_classroom() {
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       Baker Bridge - Classroom App Build                   ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    phase_parse
    phase_validate
    phase_correct
    phase_sme
    if [[ "$GENERATE" == true ]]; then
        check_tool "$DEALER_PATH" "dealer3"
        phase_missing
        phase_generate
    else
        cd "$SCRIPT_DIR"
        if [[ ! -f "constructed_hands.csv" ]]; then
            error "constructed_hands.csv not found. Run with --generate to create it."
        fi
        echo -e "\n${YELLOW}Reusing existing constructed_hands.csv${NC}"
    fi
    phase_fill
    phase_reroll
    phase_pbn "BakerBridgeFull.csv"
    phase_pbn_pdf
    phase_package
    phase_stamp
    phase_export

    echo ""
    echo -e "${GREEN}Classroom build complete.${NC}"
    PKG_COUNT=$(find "$PACKAGE_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "Output: Package/ ($PKG_COUNT files)"
}

run_rotations() {
    local filter="${LESSON:-*}"

    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       Baker Bridge - Rotations Build                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    if [[ "$filter" != "*" ]]; then
        echo "Lesson filter: $filter"
        echo ""
    fi

    check_tool "$BRIDGE_WRANGLER_PATH" "bridge-wrangler"

    phase_parse
    phase_validate
    phase_correct
    phase_sme
    if [[ "$GENERATE" == true ]]; then
        check_tool "$DEALER_PATH" "dealer3"
        phase_missing
        phase_generate
    else
        cd "$SCRIPT_DIR"
        if [[ ! -f "constructed_hands.csv" ]]; then
            error "constructed_hands.csv not found. Run with --generate to create it."
        fi
        echo -e "\n${YELLOW}Reusing existing constructed_hands.csv${NC}"
    fi
    phase_fill
    phase_reroll
    phase_pbn "BakerBridgeFull.csv"
    phase_pbn_pdf
    phase_package
    phase_stamp
    phase_export
    phase_presentation
    phase_rotate "$filter"

    echo ""
    echo -e "${GREEN}Rotations build complete.${NC}"
    ROT_COUNT=$(find "$REPO_ROOT/Rotations" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "Output: Rotations/ ($ROT_COUNT files)"
}

run_all_phases() {
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       Baker Bridge Mac Build Pipeline                      ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Repository: $REPO_ROOT"
    echo "Tools dir:  $SCRIPT_DIR"

    # Check required tools
    echo ""
    echo "Checking required tools..."
    check_tool "$DEALER_PATH" "dealer3"
    check_tool "$BRIDGE_WRANGLER_PATH" "bridge-wrangler"
    if command -v html2pdf &> /dev/null; then
        echo -e "${GREEN}✓${NC} html2pdf found"
    else
        warn "html2pdf not found - intro PDFs will be skipped"
        warn "Install with: brew install ilaborie/tap/html2pdf"
    fi
    echo -e "${GREEN}✓${NC} Required tools found"

    # Run all phases
    for entry in "${PHASES[@]}"; do
        local name="${entry%%|*}"
        # 'publish' pushes to a public Google Drive; never run it implicitly in a full build.
        [[ "$name" == "publish" ]] && continue
        run_phase "$name"
    done

    # Summary
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║       Build Complete                                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    PBN_COUNT=$(find "$SCRIPT_DIR/pbns" -name "*.pbn" 2>/dev/null | wc -l | tr -d ' ')
    PDF_COUNT=$(find "$SCRIPT_DIR/pbns" -name "*.pdf" 2>/dev/null | wc -l | tr -d ' ')
    PKG_COUNT=$(find "$PACKAGE_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
    PRES_COUNT=$(find "$REPO_ROOT/Presentation" -type f 2>/dev/null | wc -l | tr -d ' ')
    ROT_COUNT=$(find "$REPO_ROOT/Rotations" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "Build artifacts:"
    echo "  - Tools/pbns/          : $PBN_COUNT PBN files + $PDF_COUNT PDFs"
    echo "  - Package/             : $PKG_COUNT files"
    echo "  - Presentation/        : $PRES_COUNT files"
    echo "  - Rotations/           : $ROT_COUNT files"
    echo ""
}

# Main execution
if [[ "$CLEAN" == true ]]; then
    do_clean
fi

if [[ -z "$PHASE" ]]; then
    show_phases
    exit 0
elif [[ "$PHASE" == "classroom" ]]; then
    run_classroom
elif [[ "$PHASE" == "rotations" ]]; then
    run_rotations
elif [[ "$PHASE" == "*" ]]; then
    run_all_phases
else
    run_phase "$PHASE"
fi
