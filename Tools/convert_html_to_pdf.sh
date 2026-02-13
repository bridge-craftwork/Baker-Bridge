#!/bin/bash
#
# convert_html_to_pdf.sh - Convert HTML lesson pages to PDF using html2pdf
#
# Generates three types of PDFs:
#   1. Intro PDFs from deal00.html (lesson intro pages)
#   2. Intro PDFs from Bidpractice review.html (partnership bidding intros)
#   3. Deal PDFs from Bidpractice deal*.html (partnership bidding deal sheets)
#
# Preprocessing:
#   - Removes trailing "Deal 1" link (not useful in PDF)
#   - Overrides body background to white for clean printing
#   - Replaces t1.gif/tvs.gif with inline SVGs
#   - Fixes CSS/image paths to absolute file:// URLs
#
# Usage:
#   ./convert_html_to_pdf.sh [--source DIR] [--dest DIR]
#

set -e

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default paths
SOURCE_ROOT="$SCRIPT_DIR/../Website/Baker Bridge/bakerbridge.coffeecup.com"
DEST_FOLDER="$SCRIPT_DIR/pdfs"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --source)
            SOURCE_ROOT="$2"
            shift 2
            ;;
        --dest)
            DEST_FOLDER="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--source DIR] [--dest DIR]"
            echo ""
            echo "Options:"
            echo "  --source DIR  Source directory containing deal00.html files"
            echo "  --dest DIR    Destination directory for PDF output"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check html2pdf is installed
if ! command -v html2pdf &> /dev/null; then
    echo "Error: html2pdf not found. Install with: brew install ilaborie/tap/html2pdf"
    exit 1
fi

# Check source directory exists
if [[ ! -d "$SOURCE_ROOT" ]]; then
    echo "Error: Source directory not found: $SOURCE_ROOT"
    exit 1
fi

# Create destination folder
mkdir -p "$DEST_FOLDER"

# Bidpractice Set → Partnership name mapping (function for bash 3 compat)
get_partnership_name() {
    case "$1" in
        Set1)  echo "Partnership-BasicNotrump" ;;
        Set2)  echo "Partnership-BasicMajor" ;;
        Set3)  echo "Partnership-BasicBidding" ;;
        Set4)  echo "Partnership-StaymanTransfers" ;;
        Set5)  echo "Partnership-WeakTwos" ;;
        Set6)  echo "Partnership-TwoClub" ;;
        Set7)  echo "Partnership-Blackwood" ;;
        Set8)  echo "Partnership-RomanKeyCard" ;;
        Set9)  echo "Partnership-Jacoby2NT" ;;
        Set10) echo "Partnership-Overcalls" ;;
        Set11) echo "Partnership-NegativeDoubles" ;;
        Set12) echo "Partnership-AdvancedForcing" ;;
        *)     echo "" ;;
    esac
}

# Create temp directory for preprocessed files
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Converting HTML intro pages to PDF..."
echo "  Source: $SOURCE_ROOT"
echo "  Dest:   $DEST_FOLDER"
echo ""

# Track statistics
total=0
converted=0
failed=0

# Find all deal00.html files
while IFS= read -r -d '' html_file; do
    total=$((total + 1))

    # Get relative path from source root
    rel_path="${html_file#$SOURCE_ROOT/}"
    rel_dir="$(dirname "$rel_path")"

    # Generate PDF name from relative directory path
    if [[ "$rel_dir" == "." ]]; then
        pdf_name="root.pdf"
    else
        # Replace path separators with underscores
        pdf_name="${rel_dir//\//_}.pdf"
    fi

    pdf_path="$DEST_FOLDER/$pdf_name"

    echo "Converting: $rel_dir/deal00.html -> $pdf_name"

    # Preprocess: copy to temp dir (preserving relative path for CSS references)
    temp_subdir="$TEMP_DIR/$rel_dir"
    mkdir -p "$temp_subdir"
    temp_file="$temp_subdir/deal00.html"

    # Resolve the CSS path to an absolute file:// URL
    css_path="$(cd "$(dirname "$html_file")/.." && pwd)/deal.css"

    # Inline SVG compass to replace t1.gif (full NESW compass box)
    read -r -d '' COMPASS_SVG << 'SVGEOF' || true
<svg xmlns="http://www.w3.org/2000/svg" width="72" height="72" viewBox="0 0 72 72"><rect width="72" height="72" rx="4" fill="#b8860b"/><text x="36" y="20" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="white">N</text><text x="12" y="44" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="white">W</text><text x="60" y="44" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="white">E</text><text x="36" y="64" text-anchor="middle" font-family="Arial,sans-serif" font-size="16" font-weight="bold" fill="white">S</text></svg>
SVGEOF

    # Inline SVG bar to replace tvs.gif (gold horizontal separator)
    read -r -d '' BAR_SVG << 'SVGEOF' || true
<svg xmlns="http://www.w3.org/2000/svg" width="72" height="16" viewBox="0 0 72 16"><rect width="72" height="16" rx="2" fill="#b8860b"/></svg>
SVGEOF

    # Copy the original, then apply fixes:
    # 1. Remove trailing deal link (e.g., <a href="deal01.html#1">...Deal 1...</a>)
    # 2. Inject CSS to override body background to white
    # 3. Rewrite CSS href to absolute path
    # 4. Replace t1.gif image with inline SVG compass
    sed -E "
        s|<a href=\"deal0?1\.html[^\"]*\">[^<]*<b>[^<]*Deal 1[^<]*</b>[^<]*</a>||g
        s|</head>|<style>body { background-color: #ffffff !important; } table { break-inside: avoid; }</style></head>|
        s|href=\"\.\./deal\.css\"|href=\"file://${css_path}\"|
        s|<img src=\"\.\./t1\.gif\"[^/]*/?>|${COMPASS_SVG}|g
        s|<img src=\"\.\./tvs\.gif\"[^/]*/?>|${BAR_SVG}|g
    " "$html_file" > "$temp_file"

    # Convert using html2pdf with background printing enabled
    if html2pdf "$temp_file" -o "$pdf_path" --background --paper Letter 2>/dev/null; then
        converted=$((converted + 1))
    else
        echo "  Warning: Failed to convert $html_file"
        failed=$((failed + 1))
    fi

done < <(find "$SOURCE_ROOT" -name "deal00.html" -type f -print0)

echo ""
echo "Intro page conversion complete:"
echo "  Total files: $total"
echo "  Converted:   $converted"
echo "  Failed:      $failed"

# ============================================================
# Section 2: Bidpractice review.html → Partnership Intro PDFs
# ============================================================
echo ""
echo "Converting Bidpractice review pages to Intro PDFs..."

bp_total=0
bp_converted=0
bp_failed=0

BIDPRACTICE_DIR="$SOURCE_ROOT/Bidpractice"
if [[ -d "$BIDPRACTICE_DIR" ]]; then
    for set_dir in "$BIDPRACTICE_DIR"/Set*/; do
        set_name=$(basename "$set_dir")
        review_file="$set_dir/review.html"

        if [[ ! -f "$review_file" ]]; then
            continue
        fi

        partnership_name="$(get_partnership_name "$set_name")"
        if [[ -z "$partnership_name" ]]; then
            echo "  Warning: No mapping for $set_name, skipping"
            continue
        fi

        bp_total=$((bp_total + 1))
        pdf_name="${partnership_name}.pdf"
        pdf_path="$DEST_FOLDER/$pdf_name"

        echo "  Converting: Bidpractice/$set_name/review.html -> $pdf_name"

        # Preprocess: white background, absolute CSS path
        css_path="$(cd "$set_dir/.." && pwd)/cardhand.css"
        temp_file="$TEMP_DIR/review_${set_name}.html"

        sed -E "
            s|</head>|<style>body { background-color: #ffffff !important; } .nav { display: none; } .space { display: none; } .hand { left: 0 !important; margin: 0 auto !important; }</style></head>|
            s|bgcolor=\"#cccc99\"|bgcolor=\"#ffffff\"|
            s|href=\"\.\./cardhand\.css\"|href=\"file://${css_path}\"|
            s|Click any Deal to start\.||
        " "$review_file" > "$temp_file"

        if html2pdf "$temp_file" -o "$pdf_path" --background --paper Letter 2>/dev/null; then
            bp_converted=$((bp_converted + 1))
        else
            echo "    Warning: Failed to convert $review_file"
            bp_failed=$((bp_failed + 1))
        fi
    done
fi

echo ""
echo "Bidpractice intro conversion complete:"
echo "  Total: $bp_total  Converted: $bp_converted  Failed: $bp_failed"

