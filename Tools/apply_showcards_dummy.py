#!/usr/bin/env python3
"""Apply the defense-lesson [showcards] dummy-card fixes from the answer key.

Background: bbparse.py generates [showcards] directives from partial-hand diffs
in the source HTML. Because dummy is shown as a full hand, its *played* card is
never a diffable partial hand, so every defense-lesson [showcards] omits dummy's
card (and a few originals are malformed). The correct card can't be recovered
from the HTML, so it's supplied out of band via Tools/showcards_dummy_key.md and
injected here as a build step. See issues #11/#12 (and #13 for the deferred
under-specified boards).

Runs after CSV_to_PBN.py, over pbns/*.pbn, so the fix flows through packaging to
Package/ (and into the PDFs). Idempotent and re-applied every build: it finds a
board's exact original directive and replaces it with the corrected one, scoped
to that board (the same directive text recurs across boards with different fixes,
so a global replace would be wrong).

Key format, one entry per line:
    <Lesson> <Board> | [showcards …FROM…] => [showcards …TO…]   # optional note
Lines beginning with '#' and lines without '=>' are ignored.
"""

import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(HERE, "showcards_dummy_key.md")

# FROM is always a single [showcards …]; TO is the rest of the line (one or more
# directives, e.g. "[PLAY …] [showcards …]"), minus any trailing "# comment".
ENTRY_RE = re.compile(r'^(\w+)\s+(\d+)\s*\|\s*(\[showcards[^\]]*\])\s*=>\s*(.+)$')


def load_key(path):
    """Return {lesson: [(board, from_directive, to_directives), ...]}."""
    entries = defaultdict(list)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or "=>" not in line:
                continue
            m = ENTRY_RE.match(line)
            if m:
                lesson, board, frm, to = m.groups()
                to = re.sub(r'\s+#.*$', '', to).strip()  # drop trailing note
                entries[lesson].append((int(board), frm, to))
    return entries


def apply_to_file(path, items):
    """Apply this lesson's (board, from, to) fixes in place. Returns
    (applied, not_found) lists of board numbers."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    parts = re.split(r'(?=\[Event ")', content)
    board_index = {}
    for i, part in enumerate(parts):
        bm = re.search(r'\[Board "(\d+)"\]', part)
        if bm:
            board_index[int(bm.group(1))] = i

    applied, not_found = [], []
    for board, frm, to in items:
        i = board_index.get(board)
        if i is None or frm not in parts[i]:
            not_found.append(board)
            continue
        parts[i] = parts[i].replace(frm, to)  # all copies within the board
        applied.append(board)

    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(parts))
    return applied, not_found


def main():
    target_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "pbns")
    key = load_key(KEY_PATH)
    total_applied = 0
    problems = []
    for lesson, items in sorted(key.items()):
        path = os.path.join(target_dir, f"{lesson}.pbn")
        if not os.path.exists(path):
            problems.append(f"{lesson}.pbn not found in {target_dir}")
            continue
        applied, not_found = apply_to_file(path, items)
        total_applied += len(applied)
        print(f"{lesson}.pbn: applied {len(applied)}/{len(items)}")
        for b in not_found:
            problems.append(f"{lesson} board {b}: original directive not found "
                            "(already applied, or the directive changed)")

    key_total = sum(len(v) for v in key.values())
    print(f"\nApplied {total_applied}/{key_total} showcards fixes.")
    if problems:
        print("\nWARNINGS:")
        for p in problems:
            print(f"  {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
