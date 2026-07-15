#!/usr/bin/env python3
"""Phase A prototype: BBA-reject passer fill (Mac-native).

Redesign of the passer fill (issue #21, Tools/passer-fill-bba-redesign.md). Instead of
*constraining* the passers to be balanced (brittle `auction_calm`), deal VARIED passers
and empirically REJECT any where a bidding engine (BBA/EPBot) shows the opponents would
act, then keep the survivor.

Prototype scope: one lesson (default NMF). For each board it
  1. keeps the bidding side's hands exactly (parsed from the released PBN),
  2. redraws the quiet (passer) pair from the complementary 26 cards with NO shape
     constraint (dealer3, predeal the bidders), and
  3. accepts a candidate only if EPBot passes at every quiet-side turn when the true
     scripted auction is asserted via `bba-cli --auction-prefix` -- the exact acceptance
     test used by the Phase 0 audit, so re-auditing the output must yield 0 biddable.

Backend: native Mac bba-cli + dealer3 (no Windows/SSH). The acceptance probe is imported
from audit_passers.py so "accepted" == "audit-clean" by construction.

Usage:
    python3 fill_bba_reject.py [LESSON ...]        # default: NMF
    python3 fill_bba_reject.py --seed 1 NMF        # reproducible dealer3 draw
Writes Package-shaped PBNs to Tools/bba_reject_out/<LESSON>.pbn and prints stats.
"""
import os, re, sys, subprocess, tempfile, time
from collections import Counter

import audit_passers as ap

DEALER = os.path.expanduser("~/Development/GitHub/dealer3/target/release/dealer")
OUT_DIR = os.path.join(ap.REPO, "Tools", "bba_reject_out")
SEATS = ["N", "E", "S", "W"]
BATCH = 24          # candidates drawn per dealer3 call
MAX_DRAWS = 400     # give up on a board after this many candidates


def deal_to_seats(deal):
    """'W:s.h.d.c n e s' -> {seat: 'spades.hearts.diamonds.clubs'}."""
    lead, rest = deal.split(":", 1)
    hands = rest.split()
    start = SEATS.index(lead)
    return {SEATS[(start + k) % 4]: h for k, h in enumerate(hands)}


def seats_to_deal(seat_hands, lead="N"):
    start = SEATS.index(lead)
    order = [SEATS[(start + k) % 4] for k in range(4)]
    return f"{lead}:" + " ".join(seat_hands[s] for s in order)


def predeal_arg(hand):
    """'spades.hearts.diamonds.clubs' -> dealer3 'S<c>,H<c>,D<c>,C<c>' (empty => letter)."""
    s, h, d, c = hand.split(".")
    return ",".join(f"{L}{cards}" for L, cards in zip("SHDC", (s, h, d, c)))


def draw_candidates(predeal_seats, seat_hands, n, seed=None):
    """dealer3: predeal the bidding seats, deal the rest; return n full seat-hand dicts."""
    lines = [f"produce {n}", "generate 100000"]
    for seat in predeal_seats:
        lines.append(f"predeal {seat.lower()} {predeal_arg(seat_hands[seat])}")
    lines.append("action printoneline")
    with tempfile.NamedTemporaryFile("w", suffix=".dlr", delete=False) as f:
        f.write("\n".join(lines)); path = f.name
    try:
        cmd = [DEALER]
        if seed is not None:
            cmd += ["-s", str(seed)]
        cmd.append(path)
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    finally:
        os.unlink(path)
    cands = []
    for ln in out.stdout.splitlines():
        m = re.match(r'^n\s+(\S+)\s+e\s+(\S+)\s+s\s+(\S+)\s+w\s+(\S+)\s*$', ln, re.I)
        if m:
            cands.append({"N": m.group(1), "E": m.group(2), "S": m.group(3), "W": m.group(4)})
    return cands


def candidate_biddable(seat_hands, dealer, vuln, calls, quiet, turns, tmp):
    """Return offense string if the quiet side would act, else '' (audit-clean)."""
    pref = [ap.norm_prefix_tok(c) for c in calls]
    for seat in sorted(quiet):
        for (p, _c) in turns[seat]:
            deal = seats_to_deal(seat_hands, dealer)
            toks = ap.run_bba(deal, dealer, vuln, pref[:p], tmp)
            got = toks[p] if p < len(toks) else "?"
            if not ap.is_pass(got):
                return f"{seat}@t{p}:{got}"
    return ""


def longest_suit(hand):
    return max(len(s) for s in hand.split("."))


def main():
    args = sys.argv[1:]
    seed = None
    if "--seed" in args:
        i = args.index("--seed"); seed = int(args[i + 1]); del args[i:i + 2]
    lessons = args or ["NMF"]
    os.makedirs(OUT_DIR, exist_ok=True)

    for lesson in lessons:
        path = os.path.join(ap.REPO, "Package", lesson + ".pbn")
        src = open(path, encoding="utf-8", errors="replace").read()
        boards = ap.parse_boards(path)
        stats = {"boards": 0, "regenerated": 0, "skipped": 0,
                 "draws": 0, "accepts": 0, "failed": 0}
        old_len = Counter(); new_len = Counter()
        replaced = {}   # board number -> new deal string
        t0 = time.time()
        with tempfile.TemporaryDirectory() as tmp:
            for b in boards:
                stats["boards"] += 1
                qs = ap.quiet_side(b["dealer"], b["calls"])
                if qs is None:
                    stats["skipped"] += 1
                    continue
                quiet, turns = qs
                bidders = [s for s in SEATS if s not in quiet]
                seat_hands = deal_to_seats(b["deal"])
                old_len[max(longest_suit(seat_hands[s]) for s in quiet)] += 1
                accepted = None
                draws = 0
                dseed = seed
                while draws < MAX_DRAWS and accepted is None:
                    cands = draw_candidates(bidders, seat_hands, BATCH, dseed)
                    if dseed is not None:
                        dseed += 1   # vary seed across batches for reproducibility
                    if not cands:
                        break
                    for cand in cands:
                        draws += 1; stats["draws"] += 1
                        # keep bidders exact, take quiet seats from candidate
                        trial = dict(seat_hands)
                        for s in quiet:
                            trial[s] = cand[s]
                        off = candidate_biddable(trial, b["dealer"], b["vuln"],
                                                 b["calls"], quiet, turns, tmp)
                        if not off:
                            accepted = trial; stats["accepts"] += 1
                            break
                        if draws >= MAX_DRAWS:
                            break
                if accepted is None:
                    stats["failed"] += 1
                    print(f"  !! {lesson} b{b['number']}: no clean fill in {draws} draws")
                    continue
                stats["regenerated"] += 1
                new_len[max(longest_suit(accepted[s]) for s in quiet)] += 1
                replaced[b["number"]] = seats_to_deal(accepted, b["dealer"])
        dt = time.time() - t0

        # write new PBN: replace each board's [Deal] line, keep everything else
        def repl(m):
            return m.group(0)  # default; handled below per-board
        out_lines = []
        cur_board = None
        for ln in src.splitlines():
            mb = re.match(r'^\[Board "(\d+)"\]', ln)
            if mb:
                cur_board = mb.group(1)
            if ln.startswith("[Deal ") and cur_board in replaced:
                out_lines.append(f'[Deal "{replaced[cur_board]}"]')
            else:
                out_lines.append(ln)
        outp = os.path.join(OUT_DIR, lesson + ".pbn")
        with open(outp, "w") as f:
            f.write("\n".join(out_lines) + "\n")

        print(f"\n=== {lesson} ===")
        print(f"  boards={stats['boards']} regenerated={stats['regenerated']} "
              f"skipped(competitive)={stats['skipped']} failed={stats['failed']}")
        acc_rate = stats['accepts'] / stats['draws'] if stats['draws'] else 0
        print(f"  candidate draws={stats['draws']} accepts={stats['accepts']} "
              f"(accept rate {acc_rate:.1%}); wall={dt:.1f}s")
        print(f"  quiet-side longest-suit distribution (old -> new):")
        for k in sorted(set(old_len) | set(new_len)):
            print(f"     {k}-card: {old_len.get(k,0):3} -> {new_len.get(k,0):3}")
        print(f"  wrote {outp}")


if __name__ == "__main__":
    main()
