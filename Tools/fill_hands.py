#!/usr/bin/env python3
"""
fill_hands.py - generate constrained opponent hands with the dealer3 Rust binary.

For each deal in missing_bids.csv where an opponent bids but has no cards, this builds a
dealer3 script that predeals the known hands and deals the missing seat(s) subject to the
shape/HCP condition named by the deal's BidSequence (see auction_templates.dlr). Output:
constructed_hands.csv.

Note (issue #21, Phase B): the *quiet* ("Calm") passers this used to constrain with the
loose `auction_calm` template are now re-rolled downstream by `passer_reroll.py`, which
deals varied passers and BBA-rejects any that would break the quiet auction. This script
still generates the *interference*-lesson hands (the opponent that is meant to bid a
specific sequence). The old Windows/SSH BBA-validation path was removed in Phase B; see
git history and Tools/passer-fill-bba-redesign.md for that previous implementation.

Usage:
    python3 fill_hands.py [--dealer PATH] [--input missing_bids.csv] [--output constructed_hands.csv]
"""

import csv
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Default path to dealer binary - adjust if needed
DEALER_PATH = Path.home() / "Development/GitHub/dealer3/target/release/dealer"

# Input/output files (defaults, can be overridden via args)
DEFAULT_MISSING_BIDS_PATH = "missing_bids.csv"
AUCTION_TEMPLATES_PATH = "auction_templates.dlr"
DEFAULT_OUTPUT_CSV = "constructed_hands.csv"


def load_auction_templates(path: str) -> str:
    """Load auction templates file content (lowercased for matching)."""
    with open(path, 'r') as f:
        return f.read().lower()


def format_hand(hand_string: str) -> str:
    """
    Convert period-delimited hand string (Spades.Hearts.Diamonds.Clubs)
    into format: S:{cards} H:{cards} D:{cards} C:{cards}
    """
    suits = hand_string.split('.')
    if len(suits) == 4:
        return f"S:{suits[0]} H:{suits[1]} D:{suits[2]} C:{suits[3]}"
    else:
        print(f"Warning: Hand string '{hand_string}' does not have 4 parts", file=sys.stderr)
        return hand_string


def convert_hand_to_predeal(hand: str) -> str:
    """
    Convert hand from CSV format (S:xx H:xx D:xx C:xx) to dealer predeal format (Sxx,Hxx,Dxx,Cxx).
    """
    return hand.replace(" ", ",").replace(":", "")


def swap_east_west(content: str) -> str:
    """Swap east and west references in template content."""
    content = content.replace("east", "__TEMP__")
    content = content.replace("west", "east")
    content = content.replace("__TEMP__", "west")
    return content


def run_dealer(script_content: str, dealer_path: Path, num_hands: int = 1) -> list[str]:
    """
    Run dealer with the given script content and return output lines.
    Returns list of hand lines (one per generated hand).
    """
    # Replace produce count
    script_content = re.sub(r'produce \d+', f'produce {num_hands}', script_content)

    with tempfile.NamedTemporaryFile(mode='w', suffix='.dlr', delete=False) as f:
        f.write(script_content)
        temp_path = f.name

    try:
        result = subprocess.run(
            [str(dealer_path), temp_path],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print(f"Dealer error: {result.stderr}", file=sys.stderr)
            return []

        lines = result.stdout.strip().split('\n')
        # Filter to only hand lines (start with 'n ')
        return [line for line in lines if line.lower().startswith('n ')]

    except subprocess.TimeoutExpired:
        print("Dealer timed out", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Error running dealer: {e}", file=sys.stderr)
        return []
    finally:
        os.unlink(temp_path)


def parse_dealer_output(line: str) -> dict | None:
    """
    Parse dealer printoneline output.
    Format: n {north} e {east} s {south} w {west}
    Where each hand is in period-delimited format (e.g., AK32.QJ5.T98.762)
    """
    pattern = r'^n\s*(?P<north>.*?)\s*e\s*(?P<east>.*?)\s*s\s*(?P<south>.*?)\s*w\s*(?P<west>.*)$'
    match = re.match(pattern, line, re.IGNORECASE)

    if match:
        return {
            'north': format_hand(match.group('north').strip()),
            'east': format_hand(match.group('east').strip()),
            'south': format_hand(match.group('south').strip()),
            'west': format_hand(match.group('west').strip()),
        }
    return None


def main():
    dealer_path = DEALER_PATH
    missing_bids_path = DEFAULT_MISSING_BIDS_PATH
    output_csv = DEFAULT_OUTPUT_CSV

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--dealer' and i + 1 < len(args):
            dealer_path = Path(args[i + 1]); i += 2
        elif args[i] == '--input' and i + 1 < len(args):
            missing_bids_path = args[i + 1]; i += 2
        elif args[i] == '--output' and i + 1 < len(args):
            output_csv = args[i + 1]; i += 2
        else:
            i += 1

    if not dealer_path.exists():
        print(f"Error: dealer binary not found at {dealer_path}", file=sys.stderr)
        print("Use --dealer PATH to specify the location", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(AUCTION_TEMPLATES_PATH):
        print(f"Error: {AUCTION_TEMPLATES_PATH} not found", file=sys.stderr)
        sys.exit(1)

    auction_templates = load_auction_templates(AUCTION_TEMPLATES_PATH)

    if not os.path.exists(missing_bids_path):
        print(f"Error: {missing_bids_path} not found", file=sys.stderr)
        sys.exit(1)

    # Initialize output CSV
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Subfolder', 'Deal', 'NorthHand', 'EastHand', 'SouthHand', 'WestHand', 'label'])

    unsupported_bid_sequences = set()
    unprocessed_hands = 0
    supported_hands = 0
    max_hands = 5000

    with open(missing_bids_path, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            bid_sequence = row.get('BidSequence', '').strip()
            subfolder = row.get('Subfolder', '')
            deal_num = row.get('Deal', '')

            # Determine label
            if not bid_sequence:
                label = "auction_calm"
            else:
                modified_bid_sequence = bid_sequence.replace("-", "_")
                label = f"auction_{modified_bid_sequence}".lower()

            if label not in auction_templates:
                unsupported_bid_sequences.add(bid_sequence or "(empty)")
                unprocessed_hands += 1
                continue

            # Get template content, swap if needed
            template_content = auction_templates
            if row.get('Seat', '').lower() == 'east':
                template_content = swap_east_west(template_content)

            # Build dealer script
            script_lines = [
                "produce 1",  # Will be replaced by run_dealer
                "generate 100000",
                template_content,
            ]

            # Add predeal statements for existing hands
            existing_hands = {}
            for seat in ['North', 'South', 'East', 'West']:
                hand = row.get(f"{seat}Hand", '').strip()
                if hand:
                    script_lines.append(f"predeal {seat.lower()} {convert_hand_to_predeal(hand)}")
                    existing_hands[seat.lower()] = hand

            script_lines.append(f"condition {label}")
            script_lines.append("action printoneline")
            script_content = '\n'.join(script_lines)

            output_lines = run_dealer(script_content, dealer_path, 1)
            if not output_lines:
                print(f"Error: No dealer output for {subfolder}/{deal_num}, label {label}", file=sys.stderr)
                continue

            hands = parse_dealer_output(output_lines[0])
            if not hands:
                print(f"Error: No valid hands parsed for {subfolder}/{deal_num}", file=sys.stderr)
                continue
            # Merge with existing hands
            for seat, hand in existing_hands.items():
                hands[seat] = hand

            with open(output_csv, 'a', newline='') as csvfile:
                csv.writer(csvfile).writerow([
                    subfolder, deal_num,
                    hands['north'], hands['east'], hands['south'], hands['west'], label
                ])
            supported_hands += 1

            if supported_hands >= max_hands:
                print(f"Reached maximum supported hands ({max_hands}). Stopping.")
                break

    print(f"\nUnsupported bid sequences: {sorted(unsupported_bid_sequences)}")
    print(f"Total unprocessed hands: {unprocessed_hands}")
    print(f"Successfully processed {supported_hands} hands.")


if __name__ == '__main__':
    main()
