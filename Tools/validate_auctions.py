#!/usr/bin/env python3
"""
Validate bridge auctions in PBN files.

Scans all .pbn files in the Package folder and checks each auction for:
- Valid calls (bids, pass, X/dbl, XX/Rdbl)
- Bids must increase (higher level, or same level with higher suit)
- Can't double your own side
- Can't double when no opposing bid precedes
- Can't redouble without a preceding double
- Can't redouble your own side's double
- Auction must end with 3 consecutive passes (after at least one bid),
  or 4 passes if no bid was made (all-pass)
- "all pass" / "AP" recognized as PBN shorthand for remaining passes

Usage:
    python3 validate_auctions.py              # scan Package/*.pbn
    python3 validate_auctions.py path/to/*.pbn  # scan specific files
"""

import os
import sys
import glob
import re

SEATS = ["N", "E", "S", "W"]
SUIT_RANK = {"C": 0, "D": 1, "H": 2, "S": 3, "NT": 4}

# Regex for a standard bid: level (1-7) followed by suit
BID_RE = re.compile(r'^([1-7])(C|D|H|S|NT)$')


def parse_pbn_boards(filepath):
    """Parse a PBN file and yield (board_number, dealer, auction_seat, tokens) tuples."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    boards = re.split(r'(?=\[Board\s+")', content)

    for block in boards:
        board_match = re.search(r'\[Board\s+"(\d+)"\]', block)
        if not board_match:
            continue
        board_num = board_match.group(1)

        dealer_match = re.search(r'\[Dealer\s+"([NESW])"\]', block)
        dealer = dealer_match.group(1) if dealer_match else None

        auction_match = re.search(r'\[Auction\s+"([NESW])"\]\s*\n(.+?)(?:\n\[|\Z)',
                                  block, re.DOTALL)
        if not auction_match:
            continue

        auction_seat = auction_match.group(1)
        auction_line = auction_match.group(2).strip()
        auction_tokens = auction_line.split()

        yield board_num, dealer, auction_seat, auction_tokens


def normalize_tokens(tokens):
    """
    Normalize auction tokens:
    - 'dbl'/'Dbl' → 'X'
    - 'Rdbl'/'rdbl' → 'XX'
    - 'AP' → handled as all-pass marker
    - 'all' 'pass' (two tokens) → merged into 'AP' marker

    Returns normalized token list.
    """
    normalized = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]

        # "all pass" as two tokens
        if tok.lower() == "all" and i + 1 < len(tokens) and tokens[i + 1].lower() == "pass":
            normalized.append("AP")
            i += 2
            continue

        # Single "AP" token
        if tok.upper() == "AP":
            normalized.append("AP")
            i += 1
            continue

        # dbl/Dbl → X
        if tok.lower() == "dbl":
            normalized.append("X")
            i += 1
            continue

        # Rdbl/rdbl → XX
        if tok.lower() == "rdbl":
            normalized.append("XX")
            i += 1
            continue

        normalized.append(tok)
        i += 1

    return normalized


def bid_rank(bid_str):
    """Return (level, suit_rank) for comparison. Higher = stronger bid."""
    m = BID_RE.match(bid_str)
    if not m:
        return None
    level = int(m.group(1))
    suit = m.group(2)
    return (level, SUIT_RANK[suit])


def seat_index(seat_char):
    return SEATS.index(seat_char)


def partnership(seat_idx):
    """0 for N/S, 1 for E/W."""
    return seat_idx % 2


def validate_auction(board_num, dealer, auction_seat, raw_tokens, filename):
    """Validate a single auction. Returns list of error/warning strings."""
    errors = []
    base_label = f"{filename} Board {board_num}"

    if not raw_tokens:
        errors.append(f"{base_label}: Empty auction")
        return errors

    if dealer and dealer != auction_seat:
        errors.append(f"{base_label}: Dealer is {dealer} but Auction starts with {auction_seat}")

    # Normalize tokens (dbl→X, Rdbl→XX, "all pass"→AP)
    tokens = normalize_tokens(raw_tokens)

    start_idx = seat_index(auction_seat)
    highest_bid = None
    highest_bid_str = None
    last_real_bid_partnership = None
    last_action = None          # 'bid', 'X', 'XX', or 'pass'
    last_double_partnership = None
    consecutive_passes = 0
    any_bid_made = False
    saw_ap = False              # saw "all pass" / AP marker

    for i, token in enumerate(tokens):
        current_seat_idx = (start_idx + i) % 4
        current_seat = SEATS[current_seat_idx]
        current_side = partnership(current_seat_idx)
        label = f"{base_label} call #{i+1} ({current_seat})"

        # Handle AP (all pass) marker
        if token == "AP":
            if not any_bid_made:
                # AP before any bid = all 4 pass (only valid at start)
                if i != 0:
                    errors.append(f"{label}: 'all pass' in unexpected position")
            saw_ap = True
            # AP terminates the auction validly
            break

        tok = token

        if tok.lower() == "pass":
            consecutive_passes += 1
            last_action = "pass"
            continue
        elif tok == "X":
            consecutive_passes = 0
            if not any_bid_made:
                errors.append(f"{label}: Double with no preceding bid")
                last_action = "X"
                last_double_partnership = current_side
                continue
            if last_action == "X":
                errors.append(f"{label}: Double when already doubled")
            elif last_action == "XX":
                errors.append(f"{label}: Double when already redoubled")
            if last_real_bid_partnership == current_side:
                errors.append(f"{label}: Doubling own side's bid ({highest_bid_str})")
            last_action = "X"
            last_double_partnership = current_side
            continue
        elif tok == "XX":
            consecutive_passes = 0
            if last_action != "X":
                errors.append(f"{label}: Redouble without preceding double (last action: {last_action})")
            if last_double_partnership is not None and last_double_partnership == current_side:
                errors.append(f"{label}: Redoubling own side's double")
            last_action = "XX"
            continue
        else:
            m = BID_RE.match(tok)
            if not m:
                errors.append(f"{label}: Invalid call '{token}'")
                continue

            consecutive_passes = 0
            rank = bid_rank(tok)

            if highest_bid is not None:
                if rank <= highest_bid:
                    errors.append(
                        f"{label}: Bid {tok} does not exceed current highest bid {highest_bid_str}"
                    )

            highest_bid = rank
            highest_bid_str = tok
            last_real_bid_partnership = current_side
            last_action = "bid"
            any_bid_made = True
            last_double_partnership = None
            continue

    # Check auction ending (only if no AP marker)
    if not saw_ap:
        if any_bid_made:
            if consecutive_passes < 3:
                errors.append(
                    f"{base_label}: Auction ends with only {consecutive_passes} pass(es) "
                    f"after a bid (need 3)"
                )
        else:
            if consecutive_passes != 4:
                errors.append(
                    f"{base_label}: All-pass auction should have exactly 4 passes, "
                    f"found {consecutive_passes}"
                )

    return errors


def main():
    if len(sys.argv) > 1:
        pbn_files = sorted(sys.argv[1:])
    else:
        package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Package")
        pbn_files = sorted(glob.glob(os.path.join(package_dir, "*.pbn")))

    if not pbn_files:
        print("No .pbn files found.")
        sys.exit(1)

    total_boards = 0
    all_errors = []

    for filepath in pbn_files:
        filename = os.path.basename(filepath)

        for board_num, dealer, auction_seat, tokens in parse_pbn_boards(filepath):
            total_boards += 1
            errors = validate_auction(board_num, dealer, auction_seat, tokens, filename)
            all_errors.extend(errors)

    # Print results
    if all_errors:
        print(f"Found {len(all_errors)} error(s) across {total_boards} boards:\n")
        current_file = None
        for err in all_errors:
            file_part = err.split(" Board")[0]
            if file_part != current_file:
                current_file = file_part
                print(f"--- {current_file} ---")
            print(f"  {err}")
        print()

    print(f"Scanned {len(pbn_files)} files, {total_boards} boards.")
    if all_errors:
        print(f"{len(all_errors)} error(s) found.")
        sys.exit(1)
    else:
        print("All auctions valid!")


if __name__ == "__main__":
    main()
