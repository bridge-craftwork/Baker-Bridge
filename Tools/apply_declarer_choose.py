#!/usr/bin/env python3
"""Apply the declarer-play [choose-card] key, then check every keyed board's play.

Background: the declarer-play lessons came out of bbparse.py with only [NEXT] steps, and
Bridge Classroom records a board only when it has a [BID] or [choose-card] step — so
none of them counted toward progress. Tools/declarer_choose_key.md turns each board's key
decisions into [choose-card] steps (with the [showcards]/[PLAY] position they need). The
decisions are editorial, so they are supplied out of band and injected here as a build
step, like apply_showcards_dummy.py.

Runs after apply_showcards_dummy.py, over pbns/*.pbn. Idempotent: a replacement whose
FROM text is gone but whose TO text is present counts as already applied.

After applying, each keyed board's directives are replayed card by card (see
check_board) and the build fails on any choice that isn't a legal play from the
position the directives set up — the directives, not the prose, are what the app shows.
"""

import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(HERE, "declarer_choose_key.md")

HEADING_RE = re.compile(r'^## (\S+) (\d+)\s*$')
SEATS = "NESW"
SUITS = "SHDC"


def load_key(path):
    """Return {lesson: {board: [(from_text, to_text), ...]}}."""
    key = defaultdict(lambda: defaultdict(list))
    lesson = board = None
    block, part = None, None
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if block is None:
                m = HEADING_RE.match(line)
                if m:
                    lesson, board = m.group(1), int(m.group(2))
                elif line == "<<<":
                    if lesson is None:
                        raise SystemExit(f"{path}: replacement before any '## Lesson Board' heading")
                    block, part = {"from": [], "to": []}, "from"
            elif line == "===" and part == "from":
                part = "to"
            elif line == ">>>" and part == "to":
                key[lesson][board].append(("\n".join(block["from"]), "\n".join(block["to"])))
                block = part = None
            else:
                block[part].append(line)
    if block is not None:
        raise SystemExit(f"{path}: unterminated replacement in {lesson} {board}")
    return key


def split_boards(content):
    parts = re.split(r'(?=\[Event ")', content)
    index = {}
    for i, part in enumerate(parts):
        bm = re.search(r'\[Board "(\d+)"\]', part)
        if bm:
            index[int(bm.group(1))] = i
    return parts, index


def parse_deal(board_text):
    """{seat: set of card codes like 'SA', 'HT'} from the board's [Deal]."""
    m = re.search(r'\[Deal "([NESW]):([^"]+)"\]', board_text)
    first, hands = m.group(1), m.group(2).split()
    out = {}
    for k, hand in enumerate(hands):
        seat = SEATS[(SEATS.index(first) + k) % 4]
        out[seat] = {s + r for s, holding in zip(SUITS, hand.split(".")) for r in holding}
    return out


def seat_cards(value):
    """'N:SA,S7 E:S3' / 'N:SA,N:S7' -> [('N','SA'), ('N','S7'), ('E','S3')]."""
    out, seat = [], None
    for tok in re.split(r'[,\s]+', value.strip()):
        m = re.match(r'^(?:([NESW]):)?([SHDC](?:10|[2-9TJQKA]))$', tok, re.I)
        if not m:
            continue
        seat = (m.group(1) or seat).upper()
        out.append((seat, m.group(2).upper().replace("10", "T")))
    return out


TAG_RE = re.compile(r'\[(PLAY|showcards|choose-card|RESET)\b\s*([^\]]*)\]', re.I)


def check_board(board_text):
    """Replay a board's cardplay directives; return a list of problems.

    Tracks the cards gathered by [PLAY], the current trick (cards put on the table by
    [showcards] or by a choice, in order), and the cards of answered choices, which the
    app keeps on the table until the next [PLAY] and then treats as played. Each choice
    must come from one hand, be unplayed, and follow suit to the trick's first card when
    that hand can.
    """
    hands = parse_deal(board_text)
    comment = board_text[board_text.index("{"):]
    played = set()
    trick = []            # [(seat, card)] on the table, in order put there
    chosen_pending = []   # cards of answered choices not yet gathered
    alternates = set()    # cards of earlier any: lists — played only if the student chose them
    problems = []

    def holding(seat):
        return hands[seat] - played - {c for s, c in trick if s == seat}

    for m in TAG_RE.finditer(comment):
        kind, value = m.group(1).lower(), m.group(2)
        if kind == "reset":
            played.clear()
            trick.clear()
            chosen_pending.clear()
        elif kind == "play":
            played.update(chosen_pending)
            chosen_pending.clear()
            for seat, card in seat_cards(value):
                if card not in hands[seat]:
                    problems.append(f"[PLAY] {seat}:{card} is not in {seat}'s hand")
                elif card in played:
                    problems.append(f"[PLAY] {seat}:{card} was already played")
                played.add(card)
            trick = [(s, c) for s, c in trick if c not in played]
        elif kind == "showcards":
            by_seat = defaultdict(list)
            for seat, card in seat_cards(value):
                by_seat[seat].append(card)
            for seat, cards in by_seat.items():
                trick = [(s, c) for s, c in trick if s != seat]  # showcards replaces a seat
                for card in cards:
                    if card not in hands[seat]:
                        problems.append(f"[showcards] {seat}:{card} is not in {seat}'s hand")
                    elif card in played:
                        problems.append(f"[showcards] {seat}:{card} was already played")
                    trick.append((seat, card))
        else:  # choose-card
            spec = value.strip()
            body = spec[4:] if spec.lower().startswith("any:") else spec
            cards = [c.upper().replace("10", "T") for c in re.split(r'[,\s]+', body) if c]
            where = {card: next((s for s in SEATS if card in hands[s]), None) for card in cards}
            seats = set(where.values())
            label = f"[choose-card {spec}]"
            if None in seats or len(seats) != 1:
                problems.append(f"{label}: cards must all be in one hand ({where})")
                continue
            seat = seats.pop()
            if any(s == seat for s, _ in trick):
                problems.append(f"{label}: {seat} already has a card in this trick")
            # A card an earlier any: choice may have used is fine to list again (the app
            # strikes it, and struck cards can't be clicked) as long as one card is left.
            gone = [c for c in cards if c in played and c not in alternates]
            if gone or all(c in played for c in cards):
                problems.append(f"{label}: {gone or cards} already played")
            live = [c for c in cards if c not in played] or cards
            if trick:
                led = trick[0][1][0]
                if any(c[0] == led for c in holding(seat)):
                    off = [c for c in cards if c[0] != led]
                    if off:
                        problems.append(f"{label}: {off} don't follow the led suit ({led})")
            if len(cards) > 1:
                alternates.update(cards)
            chosen_pending.append(live[0])
            trick.append((seat, live[0]))
    return problems


def apply_to_file(path, boards):
    with open(path, "r", encoding="utf-8") as f:
        parts, index = split_boards(f.read())
    applied, problems = 0, []
    for board, reps in sorted(boards.items()):
        i = index.get(board)
        if i is None:
            problems.append(f"board {board} not found")
            continue
        for frm, to in reps:
            n, n_to = parts[i].count(frm), parts[i].count(to) if to else 0
            # Already applied: TO is present and every FROM left is one inside a TO (TO
            # may contain FROM; TO text may also occur elsewhere in the board). An empty
            # TO deletes FROM, so it is applied once FROM is gone.
            if (not to and n == 0) or (n_to and n == n_to * to.count(frm)):
                applied += 1
            elif n == 1:
                parts[i] = parts[i].replace(frm, to)
                applied += 1
            else:
                problems.append(f"board {board}: FROM text found {n} times: {frm[:60]!r}")
        problems += [f"board {board}: {p}" for p in check_board(parts[i])]
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    return applied, problems


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "pbns")
    key = load_key(KEY_PATH)
    total, problems = 0, []
    for lesson, boards in sorted(key.items()):
        path = os.path.join(target_dir, f"{lesson}.pbn")
        if not os.path.exists(path):
            problems.append(f"{lesson}.pbn not found in {target_dir}")
            continue
        n = sum(len(r) for r in boards.values())
        applied, probs = apply_to_file(path, boards)
        total += applied
        print(f"{lesson}.pbn: {len(boards)} boards, applied {applied}/{n} replacements")
        problems += [f"{lesson} {p}" for p in probs]
    print(f"\nApplied {total} declarer choose-card replacements.")
    if problems:
        print("\nERRORS:")
        for p in problems:
            print(f"  {p}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
