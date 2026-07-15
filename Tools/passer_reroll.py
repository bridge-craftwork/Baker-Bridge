#!/usr/bin/env python3
"""Phase B: unified BBA-reject passer re-roll with a committed cache (issue #21).

The build fills the missing East/West (passer) hands two ways, and BOTH can produce a
*biddable passer* that breaks a lesson's intended quiet auction:
  1. `constructed_hands.csv` (fill_hands.py) -- the loose `auction_calm` constraint.
  2. `bb_fill.py`'s `assign_to_east_west` -- an UNSEEDED random shuffle, used for every
     board not in `missing_bids.csv` (all the Partnership-* lessons).

This step runs AFTER bb_fill, over the assembled `BakerBridgeFull.csv`, and re-rolls the
passers for exactly the boards that need it -- E/W empty in the *source* AND E/W the quiet
(all-pass) side -- using the validated managed-variety BBA-reject loop (Phase A). It
supersedes both passer sources with one deterministic, audit-clean result.

Determinism + stability come from a **committed cache** (`passer_cache.csv`) keyed by board
identity (Subfolder, DealNumber) + the fixed bidding hands + auction. A board is re-rolled
only when it has no cached fill or its bidding hands/auction changed (or `--revalidate`),
so normal builds are fast and diffs are small. This also unifies the retired mac/windows
split: one cache, machine-independent.

Usage:
    python3 passer_reroll.py BakerBridgeFull.csv [--sme BakerBridge-sme.csv]
        [--cache passer_cache.csv] [--variety 0.35] [--max-suit 6]
        [--seed 20260714] [--revalidate] [--dry-run]
Rewrites BakerBridgeFull.csv in place (unless --dry-run) and updates the cache.
"""
import csv, os, re, sys, tempfile, zlib
from collections import Counter

import audit_passers as ap
import fill_bba_reject as fr

SEATS = ["N", "E", "S", "W"]
DEALER_LETTER = {"NORTH": "N", "EAST": "E", "SOUTH": "S", "WEST": "W",
                 "N": "N", "E": "E", "S": "S", "W": "W"}
CACHE_FIELDS = ["Subfolder", "DealNumber", "Dealer", "AuctionSig",
                "NorthHand", "SouthHand", "EastHand", "WestHand", "attempts"]


def hand_to_dotted(h):
    """'S:AKQ H:.. D:.. C:..' -> 'spades.hearts.diamonds.clubs' (empty suit => '')."""
    d = {"S": "", "H": "", "D": "", "C": ""}
    for part in h.split():
        if ":" in part:
            s, c = part.split(":", 1); d[s.upper()] = c
    return f"{d['S']}.{d['H']}.{d['D']}.{d['C']}"


def dotted_to_hand(dotted):
    s, h, d, c = dotted.split(".")
    return f"S:{s} H:{h} D:{d} C:{c}"


def parse_auction(a):
    """Auction string -> list of raw call tokens (stop at 'all'; keep pass/x/xx/bids)."""
    toks = []
    for t in a.replace("|", " ").split():
        if ap.CALL_RE.match(t):
            toks.append(t)
        else:
            break  # 'all' (all-pass) or stray => auction ends
    return toks


def auction_sig(calls):
    return " ".join(ap.norm_prefix_tok(c) or c for c in calls)


def board_seed(base, sub, num):
    return base + (zlib.crc32(f"{sub}|{num}".encode()) & 0xFFFFFF)


# Outlier policy escalation. Gentle default first; relax only when a deal FORCES
# distribution (e.g. a suit exhausted for E/W -> a forced void), never gratuitously.
# (max_suit, allow_void, allow_two_suiter)
POLICIES = [(6, False, False), (6, True, False), (7, True, False), (13, True, True)]


def is_outlier(hand, max_suit, allow_void, allow_two_suiter):
    L = fr.shape(hand)  # descending suit lengths
    if L[0] > max_suit: return True
    if L[3] == 0 and not allow_void: return True
    if L[0] >= 5 and L[1] >= 5 and not allow_two_suiter: return True
    return False


def is_balanced(hand):
    return fr.shape(hand) in fr.BALANCED_SHAPES


def generate_clean_fill(bidding, dealer, vuln, calls, quiet, turns,
                        variety, policy, prefer_modest, seed, tmp):
    """Draw E/W with no shape constraint; hard-reject outliers (per `policy`);
    BBA-reject biddable; steer toward/away from a modest hand per `prefer_modest`.
    Return (ew_dotted, attempts) or (None, attempts)."""
    max_suit, allow_void, allow_two = policy
    seat_hands = dict(bidding)  # dotted, bidders only
    accepted = None; fallback = None; attempts = 0; dseed = seed
    while attempts < fr.MAX_DRAWS and accepted is None:
        cands = fr.draw_candidates([s for s in SEATS if s in bidding],
                                   seat_hands, fr.BATCH, dseed)
        if dseed is not None: dseed += 1
        if not cands: break
        for cand in cands:
            attempts += 1
            trial = dict(seat_hands)
            for s in quiet: trial[s] = cand[s]
            if any(is_outlier(trial[s], max_suit, allow_void, allow_two) for s in quiet):
                if attempts >= fr.MAX_DRAWS: break
                continue
            all_balanced = all(is_balanced(trial[s]) for s in quiet)
            matches_aim = (not all_balanced) if prefer_modest else all_balanced
            # Only spend BBA calls on aim-matching candidates, plus one clean fallback.
            if matches_aim:
                if not fr.candidate_biddable(trial, dealer, vuln, calls, quiet, turns, tmp):
                    accepted = trial; break
            elif fallback is None:
                if not fr.candidate_biddable(trial, dealer, vuln, calls, quiet, turns, tmp):
                    fallback = trial
            if attempts >= fr.MAX_DRAWS: break
    hands = accepted or fallback
    if hands is None:
        return None, attempts
    return {s: hands[s] for s in quiet}, attempts


def main():
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print("usage: passer_reroll.py BakerBridgeFull.csv [opts]", file=sys.stderr); sys.exit(2)
    full_csv = args[0]; args = args[1:]
    sme_csv = "BakerBridge-sme.csv"
    cache_csv = "passer_cache.csv"
    variety, max_suit, seed = 0.35, 6, 20260714
    revalidate = dry = False
    it = iter(range(len(args)))
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--sme": sme_csv = args[i + 1]; i += 2
        elif a == "--cache": cache_csv = args[i + 1]; i += 2
        elif a == "--variety": variety = float(args[i + 1]); i += 2
        elif a == "--max-suit": max_suit = int(args[i + 1]); i += 2
        elif a == "--seed": seed = int(args[i + 1]); i += 2
        elif a == "--revalidate": revalidate = True; i += 1
        elif a == "--dry-run": dry = True; i += 1
        else: i += 1

    # boards whose source E/W were empty == the generated-passer universe
    generated = set()
    with open(sme_csv, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            if not r["EastHand"].strip() and not r["WestHand"].strip():
                generated.add((r["Subfolder"], r["DealNumber"]))

    cache = {}
    if os.path.exists(cache_csv):
        with open(cache_csv, encoding="utf-8", errors="replace") as f:
            for r in csv.DictReader(f):
                cache[(r["Subfolder"], r["DealNumber"])] = r

    with open(full_csv, encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f); rows = list(reader); fields = reader.fieldnames

    st = Counter()
    cls_tally = Counter()          # accepted quiet-hand shape classes (for variety steering)
    n_hands = n_unbal = 0
    with tempfile.TemporaryDirectory() as tmp:
        for row in rows:
            key = (row["Subfolder"], row["DealNumber"])
            if key not in generated:
                continue
            dealer = DEALER_LETTER.get((row.get("Dealer") or "").strip().upper())
            calls = parse_auction(row.get("Auction", ""))
            qs = ap.quiet_side(dealer, calls) if dealer else None
            if qs is None:
                continue
            quiet, turns = qs
            if quiet != {"E", "W"}:      # only ever re-roll the generated E/W pair
                st["skip_ns_quiet"] += 1
                continue
            st["eligible"] += 1
            sig = auction_sig(calls)
            n_hand = hand_to_dotted(row["NorthHand"]); s_hand = hand_to_dotted(row["SouthHand"])

            c = cache.get(key)
            reuse = (c and not revalidate and c.get("AuctionSig") == sig
                     and hand_to_dotted(c["NorthHand"]) == n_hand
                     and hand_to_dotted(c["SouthHand"]) == s_hand)
            if reuse:
                ew = {"E": hand_to_dotted(c["EastHand"]), "W": hand_to_dotted(c["WestHand"])}
                st["reused"] += 1
            else:
                cur_frac = (n_unbal / n_hands) if n_hands else 0.0
                prefer_modest = cur_frac < variety
                bidding = {"N": n_hand, "S": s_hand}
                # Escalate the outlier policy only if the gentle default can't be met
                # (e.g. a suit exhausted for E/W forces a void). Same seed each try =>
                # deterministic; escalation just relaxes which clean hands are allowed.
                policies = [(max_suit, False, False), (max_suit, True, False),
                            (max(max_suit, 7), True, False), (13, True, True)]
                ew = None; used = 0
                for pi, pol in enumerate(policies):
                    ew, attempts = generate_clean_fill(
                        bidding, dealer, "None", calls, quiet, turns,
                        variety, pol, prefer_modest, board_seed(seed, *key), tmp)
                    if ew is not None:
                        used = pi; break
                if ew is None:
                    st["failed"] += 1
                    print(f"  !! {key[0]} d{key[1]}: no clean fill (all policies)", file=sys.stderr)
                    continue
                if used > 0:
                    st["escalated"] += 1
                    print(f"  ~ {key[0]} d{key[1]}: escalated to policy {used} "
                          f"{policies[used]} (deal forces distribution)", file=sys.stderr)
                st["regenerated"] += 1
                cache[key] = {"Subfolder": key[0], "DealNumber": key[1],
                              "Dealer": dealer, "AuctionSig": sig,
                              "NorthHand": row["NorthHand"], "SouthHand": row["SouthHand"],
                              "EastHand": dotted_to_hand(ew["E"]),
                              "WestHand": dotted_to_hand(ew["W"]), "attempts": attempts}
            for s in ("E", "W"):
                cl = fr.classify(ew[s], max_suit); cls_tally[cl] += 1
                n_hands += 1; n_unbal += (cl != "balanced")
            row["EastHand"] = dotted_to_hand(ew["E"])
            row["WestHand"] = dotted_to_hand(ew["W"])

    if not dry:
        with open(full_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
        with open(cache_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CACHE_FIELDS)
            w.writeheader()
            for k in sorted(cache):
                w.writerow({fld: cache[k].get(fld, "") for fld in CACHE_FIELDS})

    bal = cls_tally["balanced"]; tot = sum(cls_tally.values())
    print(f"passer_reroll: eligible={st['eligible']} "
          f"regenerated={st['regenerated']} reused={st['reused']} "
          f"failed={st['failed']} (ns-quiet skipped={st['skip_ns_quiet']})")
    print(f"  quiet-hand shape: balanced={cls_tally['balanced']} "
          f"modest={cls_tally['modest']} outlier={cls_tally['outlier']} "
          f"(balanced {bal/tot:.0%}, target {1-variety:.0%})" if tot else "  (no hands)")
    if dry: print("  [dry-run: no files written]")


if __name__ == "__main__":
    main()
