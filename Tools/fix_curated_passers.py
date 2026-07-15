#!/usr/bin/env python3
"""Fix biddable quiet passers in CURATED bidding-lesson PBNs (issue #21 follow-up).

Curated boards (Curated/*.pbn) are merged over the generated deals at package time, so they
bypass passer_reroll's BBA-reject fill -- a curated bidding lesson can still carry a biddable
passer (e.g. 2over1 b10's wild 1-0-7-5 East that overcalls 3D into a 2/1 slam auction).

This re-rolls ONLY the biddable quiet-E/W boards, keeping N/S + auction + commentary, using
the same managed-variety BBA-reject loop as passer_reroll (deterministic, imported). It is
minimal: a board is touched only if EPBot would have E/W break silence.

Scope: pass CURATED *bidding* lessons only. Do NOT pass play/practice lessons (100NT), whose
E/W are real deals, not passers.

Usage:
    python3 fix_curated_passers.py [Curated/2over1.pbn Curated/Leben.pbn Curated/Weak2.pbn]
Rewrites each file in place; prints which boards changed.
"""
import os, re, sys, tempfile

import audit_passers as ap
import fill_bba_reject as fr
import passer_reroll as pr

DEFAULT = ["Curated/2over1.pbn", "Curated/Leben.pbn", "Curated/Weak2.pbn"]


def main():
    files = sys.argv[1:] or [os.path.join(ap.REPO, f) for f in DEFAULT]
    for path in files:
        if not os.path.exists(path):
            print(f"skip (missing): {path}"); continue
        lesson = os.path.splitext(os.path.basename(path))[0]
        src = open(path, encoding="utf-8", errors="replace").read()
        boards = ap.parse_boards(path)
        replaced = {}
        with tempfile.TemporaryDirectory() as tmp:
            for b in boards:
                # Skip boards with unfilled hands ('...'): the curated merge fills those
                # from the re-rolled pipeline deal, so they're already BBA-clean. Only
                # fully-specified curated deals keep their own (possibly biddable) passers.
                if "..." in b["deal"]:
                    continue
                qs = ap.quiet_side(b["dealer"], b["calls"])
                if qs is None:
                    continue
                quiet, turns = qs
                if quiet != {"E", "W"}:
                    continue
                seat_hands = fr.deal_to_seats(b["deal"])
                off = fr.candidate_biddable(seat_hands, b["dealer"], b["vuln"],
                                            b["calls"], quiet, turns, tmp)
                if not off:
                    continue  # already clean; leave the curator's hand untouched
                bidding = {"N": seat_hands["N"], "S": seat_hands["S"]}
                ew = None
                for pol in [(6, False, False), (6, True, False), (7, True, False), (13, True, True)]:
                    ew, _ = pr.generate_clean_fill(
                        bidding, b["dealer"], b["vuln"], b["calls"], quiet, turns,
                        0.35, pol, False, pr.board_seed(20260714, lesson, b["number"]), tmp)
                    if ew is not None:
                        break
                if ew is None:
                    print(f"  !! {lesson} b{b['number']}: no clean fill"); continue
                new_hands = dict(seat_hands); new_hands.update(ew)
                replaced[b["number"]] = fr.seats_to_deal(new_hands, b["dealer"])
                print(f"  {lesson} b{b['number']}: was biddable ({off}) -> re-rolled")
        if not replaced:
            print(f"{lesson}: no biddable curated passers"); continue
        out, cur = [], None
        for ln in src.splitlines():
            mb = re.match(r'^\[Board "(\d+)"\]', ln)
            if mb: cur = mb.group(1)
            if ln.startswith("[Deal ") and cur in replaced:
                out.append(f'[Deal "{replaced[cur]}"]')
            else:
                out.append(ln)
        open(path, "w").write("\n".join(out) + "\n")
        print(f"{lesson}: rewrote {len(replaced)} board(s)")


if __name__ == "__main__":
    main()
