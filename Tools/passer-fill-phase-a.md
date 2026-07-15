# Phase A — NMF prototype of the BBA-reject passer fill

**Status:** Done (2026-07-14). **Related:** issue #21, `Tools/passer-fill-bba-redesign.md`,
Phase 0 (`Tools/passer-fill-phase0-audit.md`). **Tool:** `Tools/fill_bba_reject.py`.

Prototype of the redesign: stop *constraining* passers to be balanced (`auction_calm`) and
instead **deal varied passers, then BBA-reject any where the opponents would act.** Native
Mac backend (`bba-cli` + `dealer3`), no Windows/SSH.

## What it does

For each board in a lesson:
1. Keep the **bidding side's** hands exactly (parsed from the released PBN).
2. Redraw the **quiet (passer) pair** from the complementary 26 cards with **no shape
   constraint** — `dealer3` predeals the bidders and deals the rest.
3. Accept a candidate only if EPBot **passes at every quiet-side turn** when the true
   scripted auction is asserted via `bba-cli --auction-prefix`. This acceptance test is
   *imported from* `audit_passers.py`, so **"accepted" ≡ "audit-clean" by construction** —
   re-auditing the output is guaranteed to report 0 biddable.

The quiet side is derived from the scripted auction (the all-pass partnership), so
competitive boards are auto-skipped and left untouched.

## Results

| lesson | boards | regenerated | Phase 0 biddable → after | draws / accepts (rate) | wall |
|---|---:|---:|---|---|---:|
| NMF | 14 | 14 | **2 → 0** | 18 / 14 (78%) | 1.5s |
| Reverse | 14 | 14 | **8 → 0** | 22 / 14 (64%) | 1.4s |

- **(a) No biddable opponents.** Re-audit of both regenerated lessons = **0 biddable**.
- **(b) Bidding hands untouched.** N/S are **byte-identical** to the originals on every
  board (only `[Deal]` changes; auction, commentary, tokens-to-be-restamped unchanged). The
  intended auctions therefore hold trivially.
- **(c) Wall-clock.** ~1.5s per 14-board lesson on the native CLI — the "expensive process"
  from the earlier SSH attempt is gone. Accept rate 64–78% ⇒ ~1.3–1.6 draws per board.
- **Historical failure rejected.** Fed the exact Windows-cache fill that broke the
  2026-07-14 class (NMF b3 East `AKJ853.97.T6.J92`), the acceptance test returns
  `REJECTED (E@t1:2S)` — the redesign would have prevented the incident.
- **Reproducible.** `--seed` threads a seed to `dealer3` (which supports `-s`); two seeded
  runs are byte-identical. This is the hook Phase B needs to make cached fills deterministic.

## Key finding: reject-only *reduces* shape variety (does not increase it)

The redesign doc hoped varied-draw + reject would yield **more** shape variety than the
all-balanced `auction_calm` output. It does the opposite:

| | balanced quiet hands |
|---|---|
| NMF old (auction_calm) | 20/28 (71%) |
| NMF new (reject-only) | 24/28 (86%) |

Unbalanced hands (long suits) are exactly the ones that overcall, so they're
preferentially rejected and the survivors skew **more** balanced. This is not a bug — the
passers are correctly quiet — but "realistic variety" is **not** a free side effect.

**Implication for Phase B:** if variety is a goal, bias the *draw* toward unbalanced-but-
quiet shapes (e.g., accept a quota of 5-4 / weak-6-card hands that still pass BBA) rather
than relying on uniform random draw. Note reject-only still admits some long suits when they
genuinely don't bid (regenerated Reverse kept 2 six-card quiet suits), so the skew is mild.

## Decision: prefix strategy = per-turn probing

The roadmap left "opening-only vs per-turn" open. **Per-turn wins** here: it's the precise
definition of "biddable" (matches the Phase 0 baseline exactly), and its cost is negligible
because the accept rate is high (few candidates, ~1.5 draws/board, 1.5s/lesson). Opening-only
would trade precision for a speed we don't need. Per-turn also short-circuits on the first
non-pass, so rejected candidates are cheap (~1 BBA call).

## Deferred to Phase B

- Generalize to all `Calm`/quiet lessons (exclude lessons that *want* interference).
- Cache validated fills (seeded, deterministic) and reuse across builds; only fill+validate
  new/changed deals. Unify the mac/windows split (`constructed_hands.csv` vs `-windows`).
- Integrate into `fill_hands.py` (make the Windows/SSH path legacy) or replace it.
- Optional: a draw bias for shape variety (see finding above).
- Token re-stamping: changing passers changes `[BoardVersionToken]`; the build's
  `stamp_board_tokens.py` re-stamps, but a fill regeneration is a board-identity change BC
  will see — coordinate per the producer contract when this actually reships.

## Reproduce

```bash
cd Tools
python3 fill_bba_reject.py NMF Reverse         # regenerate; writes bba_reject_out/*.pbn
python3 fill_bba_reject.py --seed 1 NMF        # deterministic draw
python3 audit_passers.py NMF                   # baseline check (audits Package/, not the output)
```
(Prototype outputs land in `Tools/bba_reject_out/` and are intentionally **not committed** —
they're regenerable and, unseeded, non-deterministic.)
