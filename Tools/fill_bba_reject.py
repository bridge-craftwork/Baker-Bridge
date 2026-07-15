#!/usr/bin/env python3
"""Phase A prototype: BBA-reject passer fill (Mac-native), with a *managed* variety bias.

Redesign of the passer fill (issue #21, Tools/passer-fill-bba-redesign.md). Instead of
*constraining* the passers to be balanced (brittle `auction_calm`), deal VARIED passers
and empirically REJECT any where a bidding engine (BBA/EPBot) shows the opponents would
act, then keep the survivor.

Phase A found that *reject-only* skews the survivors MORE balanced (long-suit hands are the
ones that overcall, so they get rejected). This adds a **managed** nudge back the other way:

  - HARD shape filter (always reject, regardless of BBA): "outlier" freak shapes -- a suit
    of length > --max-suit (default 6), any void, or a 5-5+ two-suiter. We never want these.
  - Among clean, non-outlier candidates, STEER toward a target fraction of *modestly*
    unbalanced quiet hands (5-4-2-2, 6-3-2-2, 5-4-3-1, 4-4-4-1, ...): --variety (default
    0.35). Greedy per-board steering nudges the achieved fraction toward the target and no
    further -- it pushes *some* hands off the balanced norm without chasing outliers, and
    falls back to a balanced clean hand when no modest one passes BBA for that board.

Acceptance for biddability is imported from audit_passers.py, so "accepted" is audit-clean
by construction (re-auditing the output yields 0 biddable). Bidding hands are untouched.

Backend: native Mac bba-cli + dealer3 (no Windows/SSH).

Usage:
    python3 fill_bba_reject.py [--variety 0.35] [--max-suit 6] [--seed 1] [LESSON ...]
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

BALANCED_SHAPES = {(4, 3, 3, 3), (4, 4, 3, 2), (5, 3, 3, 2)}


def shape(hand):
    return tuple(sorted((len(s) for s in hand.split(".")), reverse=True))


def classify(hand, max_suit):
    """'balanced' | 'modest' (mildly unbalanced) | 'outlier' (freak, always excluded)."""
    L = shape(hand)
    if L[0] > max_suit or L[3] == 0 or (L[0] >= 5 and L[1] >= 5):
        return "outlier"
    if L in BALANCED_SHAPES:
        return "balanced"
    return "modest"


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


def main():
    args = sys.argv[1:]
    seed = None
    variety = 0.35     # target fraction of quiet hands that are modestly unbalanced
    max_suit = 6       # longest quiet suit allowed; longer => outlier (hard reject)
    for flag, cast in (("--seed", int), ("--variety", float), ("--max-suit", int)):
        if flag in args:
            i = args.index(flag); val = cast(args[i + 1]); del args[i:i + 2]
            if flag == "--seed": seed = val
            elif flag == "--variety": variety = val
            else: max_suit = val
    lessons = args or ["NMF"]
    os.makedirs(OUT_DIR, exist_ok=True)

    for lesson in lessons:
        path = os.path.join(ap.REPO, "Package", lesson + ".pbn")
        src = open(path, encoding="utf-8", errors="replace").read()
        boards = ap.parse_boards(path)
        stats = {"boards": 0, "regenerated": 0, "skipped": 0, "draws": 0,
                 "accepts": 0, "failed": 0, "outliers_rejected": 0}
        old_cls = Counter(); new_cls = Counter()   # per quiet-hand shape class
        replaced = {}
        n_hands = 0; n_unbal = 0                    # running per-hand tally for steering
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
                for s in quiet:
                    old_cls[classify(seat_hands[s], max_suit)] += 1

                # steer (bang-bang controller): under target -> prefer a modest hand;
                # at/over target -> prefer an all-balanced fill so the fraction converges.
                cur_frac = (n_unbal / n_hands) if n_hands else 0.0
                prefer_modest = cur_frac < variety

                accepted = None      # first clean candidate that also adds a modest hand
                fallback = None      # first clean candidate of any (non-outlier) shape
                draws = 0; dseed = seed
                while draws < MAX_DRAWS and accepted is None:
                    cands = draw_candidates(bidders, seat_hands, BATCH, dseed)
                    if dseed is not None: dseed += 1
                    if not cands: break
                    for cand in cands:
                        draws += 1; stats["draws"] += 1
                        trial = dict(seat_hands)
                        for s in quiet: trial[s] = cand[s]
                        classes = [classify(trial[s], max_suit) for s in quiet]
                        if "outlier" in classes:            # hard shape filter
                            stats["outliers_rejected"] += 1
                            if draws >= MAX_DRAWS: break
                            continue
                        if candidate_biddable(trial, b["dealer"], b["vuln"],
                                              b["calls"], quiet, turns, tmp):
                            if draws >= MAX_DRAWS: break
                            continue
                        # clean & non-outlier
                        if fallback is None: fallback = trial
                        ok = ("modest" in classes) if prefer_modest \
                            else all(c == "balanced" for c in classes)
                        if ok:
                            accepted = trial; break
                        if draws >= MAX_DRAWS: break
                if accepted is None: accepted = fallback  # no modest hit -> take clean balanced
                if accepted is None:
                    stats["failed"] += 1
                    print(f"  !! {lesson} b{b['number']}: no clean fill in {draws} draws")
                    continue
                stats["accepts"] += 1; stats["regenerated"] += 1
                for s in quiet:
                    c = classify(accepted[s], max_suit); new_cls[c] += 1
                    n_hands += 1; n_unbal += (c != "balanced")
                replaced[b["number"]] = seats_to_deal(accepted, b["dealer"])
        dt = time.time() - t0

        out_lines, cur_board = [], None
        for ln in src.splitlines():
            mb = re.match(r'^\[Board "(\d+)"\]', ln)
            if mb: cur_board = mb.group(1)
            if ln.startswith("[Deal ") and cur_board in replaced:
                out_lines.append(f'[Deal "{replaced[cur_board]}"]')
            else:
                out_lines.append(ln)
        outp = os.path.join(OUT_DIR, lesson + ".pbn")
        with open(outp, "w") as f:
            f.write("\n".join(out_lines) + "\n")

        def bal_frac(c):
            t = sum(c.values()); return (c["balanced"] / t) if t else 0
        print(f"\n=== {lesson}  (variety target {variety:.0%} unbalanced, max-suit {max_suit}) ===")
        print(f"  boards={stats['boards']} regenerated={stats['regenerated']} "
              f"skipped(competitive)={stats['skipped']} failed={stats['failed']}")
        acc = stats['accepts'] / stats['draws'] if stats['draws'] else 0
        print(f"  draws={stats['draws']} accepts={stats['accepts']} (rate {acc:.1%}) "
              f"outliers hard-rejected={stats['outliers_rejected']}; wall={dt:.1f}s")
        print(f"  quiet-hand shape class (old -> new):")
        for cls in ("balanced", "modest", "outlier"):
            print(f"     {cls:<9} {old_cls.get(cls,0):3} -> {new_cls.get(cls,0):3}")
        print(f"  balanced fraction: {bal_frac(old_cls):.0%} -> {bal_frac(new_cls):.0%} "
              f"(target {1-variety:.0%})   outliers in output: {new_cls.get('outlier',0)}")
        print(f"  wrote {outp}")


if __name__ == "__main__":
    main()
