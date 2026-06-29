# Baker Bridge

A tool for extracting, validating, and repackaging bridge lesson content from the Baker Bridge website (bakerbridge.coffeecup.com) into standardized PBN (Portable Bridge Notation) and PDF formats.

## Two Build Products

This project produces two distinct outputs from the same source content:

### Package (for Bridge Classroom app)

The `Package/` folder contains PBN and PDF files served via GitHub raw URLs to the [Bridge Classroom](https://github.com/bridge-craftwork/Bridge-Classroom) web app. The app renders lessons interactively with bidding prompts, hand visibility control, and step-by-step analysis. PBN files include control directives (`[show]`, `[BID]`, `[NEXT]`, etc.) that drive the app's UI.

### Rotations (for live teacher classes)

The `Rotations/` folder contains PBN and PDF files organized for in-person bridge instruction. Lessons are split into board sets (4/5/6 boards), rotated for different seat positions (South, North-South, all four hands), and formatted for use with dealing machines. All four hands must be present since physical cards are dealt.

## Project Structure

```
Baker-Bridge/
+-- Website/           # HTTrack mirror of bakerbridge.coffeecup.com
+-- Tools/             # Build scripts and intermediate data
|   +-- bbparse.py     # HTML parser -> CSV
|   +-- CSV_to_PBN.py  # CSV -> PBN converter
|   +-- build-mac.sh   # Build pipeline orchestrator
|   +-- pbns/          # Generated PBN + PDF files
|   +-- pdfs/          # Generated intro PDFs
|   +-- Anchors/       # Debug output from HTML parsing
|   +-- auction-fixes/ # SME corrections and BBA validation
|   +-- Archive/       # Previous script versions
+-- Package/           # -> Bridge Classroom app (PBN + PDF + toc.json)
+-- Presentation/      # Intermediate: organized by category, cleaned for print
+-- Rotations/         # -> Live classes (rotated, sliced, with dealing sheets)
```

## Prerequisites

- Python 3.x with BeautifulSoup4 (`pip install beautifulsoup4`)
- [dealer3](https://github.com/dealer3) (Rust) - for generating constrained hands
- [bridge-wrangler](https://github.com/bridge-wrangler) (Rust) - for PBN-to-PDF and hand rotations
- html2pdf (optional) - for lesson intro pages: `brew install ilaborie/tap/html2pdf`

## Quick Start

```bash
cd Tools

# Build for Bridge Classroom app (reuses existing constructed_hands.csv)
./build-mac.sh classroom

# Build rotations for live classes (reuses existing constructed_hands.csv)
./build-mac.sh rotations

# Regenerate constrained hands from scratch (slow - runs dealer3)
./build-mac.sh classroom --generate
./build-mac.sh rotations --generate
```

## Build Pipeline

The build script `Tools/build-mac.sh` orchestrates the full pipeline. Both the `classroom` and `rotations` shortcuts share the same core phases; `rotations` adds presentation and rotation steps at the end.

```
HTML Files -> bbparse.py -> BakerBridge.csv
                               |
                     validate + correct + sme
                               |
                        BakerBridge-sme.csv
                               |
               +---------------+---------------+
               |                               |
         [--generate]                   (reuse existing)
               |                               |
     missing -> generate             constructed_hands.csv
               |                               |
               +---------------+---------------+
                               |
                      fill -> BakerBridgeFull.csv
                               |
                    CSV_to_PBN.py -> pbns/*.pbn
                               |
                  convert_pbns_to_pdfs.py -> pbns/*.pdf
                               |
                     package_results.py -> Package/
                               |
                  +------------+------------+
                  |                         |
             (classroom)              (rotations)
              done here            package_presentation.py
                                         |
                                   Presentation/
                                         |
                              rotate_lesson_collection.sh
                                         |
                                    Rotations/
```

### Build Phases

| Phase | Script | Description |
|-------|--------|-------------|
| **parse** | `bbparse.py` | Parse HTML lessons, extract hands/auctions/analysis -> `BakerBridge.csv` |
| **validate** | `bbcheck.py` | Check for card data errors -> `bbcheck.txt` |
| **correct** | `bb_correct.py` | Auto-fix duplicate card errors |
| **sme** | `apply_sme_corrections.py` | Apply subject-matter-expert corrections -> `BakerBridge-sme.csv` |
| **missing** | `check_missing_bids.py` | Find deals where E/W bid but have no cards -> `missing_bids.csv` |
| **generate** | `fill_hands.py` | Generate constrained E/W hands using dealer3 -> `constructed_hands.csv` |
| **fill** | `bb_fill.py` | Merge generated hands into full dataset -> `BakerBridgeFull.csv` |
| **pbn** | `CSV_to_PBN.py` | Convert CSV to PBN files -> `pbns/` |
| **pbn-pdf** | `convert_pbns_to_pdfs.py` | Convert PBNs to PDFs using bridge-wrangler |
| **package** | `package_results.py` | Copy PBN/PDF files to `Package/`, generate `toc.json` |
| **presentation** | `package_presentation.py` | Organize into `Presentation/` by category, strip interactive directives |
| **rotate** | `rotate_lesson_collection.sh` | Slice into board sets, rotate hands, generate dealing sheets -> `Rotations/` |

### The --generate Flag

The **generate** phase (running dealer3 to produce `constructed_hands.csv`) is the slowest step in the build. By default, both `classroom` and `rotations` shortcuts skip it and reuse the existing `constructed_hands.csv`. Pass `--generate` to regenerate it when improving hand quality or after changing bidding constraints.

### Running Individual Phases

Any phase can be run independently:

```bash
./build-mac.sh parse        # Just re-parse the HTML
./build-mac.sh pbn          # Just regenerate PBNs
./build-mac.sh rotate       # Just redo rotations
./build-mac.sh '*'          # Run all phases sequentially
./build-mac.sh --clean '*'  # Clean artifacts, then run all phases
```

## Data Files

| File | Description |
|------|-------------|
| `BakerBridge.csv` | Initial extraction from HTML (partial hands) |
| `BakerBridge-sme.csv` | After SME corrections applied |
| `BakerBridgeFull.csv` | Complete dataset with all four hands filled |
| `constructed_hands.csv` | Generated E/W hands satisfying bidding constraints |
| `missing_bids.csv` | Deals requiring constrained hand generation |
| `titles.csv` | Lesson-to-category folder mapping (in Package/) |

## PBN Control Directives

The PBN files include custom directives that control the Bridge Classroom app:

| Directive | Purpose |
|-----------|---------|
| `[show S]`, `[show NS]`, `[show NESW]` | Control which hands are visible |
| `[NEXT]` | End of step, show Next button |
| `[ROTATE]` | Like NEXT but rotates the table view |
| `[BID X]` | Prompt student to bid (X = expected bid) |
| `[PLAY N:SK,S:H3]` | Mark cards as played |
| `[RESET]` | Reset hands to original state |
| `[AUCTION on/off]` | Show/hide the auction table |
| `[SHOW_LEAD]` | Display the opening lead banner |

## Lesson Categories

48 lessons organized into 7 categories:

1. **Basic Bidding** - Major/Minor suit openings, Notrump
2. **Bidding Conventions** - Stayman, Transfers, Blackwood, 2/1, etc.
3. **Competitive Bidding** - Overcalls, Doubles, DONT, Michaels
4. **Declarer Play** - Finesses, Entries, Squeezes, Elimination
5. **Defense** - Opening Leads, Signals, 2nd/3rd Hand Play
6. **Practice Deals** - 100 Miscellaneous, 100 NT Openings
7. **Partnership Bidding** - Progressive practice sets

## License

See [LICENSE](LICENSE) file.

## Acknowledgments

Content sourced from [Baker Bridge](https://bakerbridge.coffeecup.com/) with permission from the site owner.
