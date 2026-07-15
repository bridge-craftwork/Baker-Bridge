# Passer-hand fill redesign: BBA-validated "quiet opponents"

**Status:** Design / roadmap. Prototype-first.
**Owner:** (to be walked in a fresh session)
**Related:** GitHub issue **#21**, `fill_hands.py`, `auction_templates.dlr`.

---

## TL;DR

Baker Bridge lessons specify only the **bidding** hands (usually N/S). The **passer**
hands (the opponents who are meant to stay silent) are **generated** by a fill step,
because they aren't in the source HTML. Two problems came out of a real class on
2026-07-14:

1. **Biddable passers.** NMF board 3's East was dealt `AKJ853` — a mandatory 2♠
   overcall — which blows up the intended quiet auction. The dealer constraint that is
   supposed to keep opponents quiet (`auction_calm`) is too loose.
2. **Divergence.** The same board had *different* passer hands in the dealer-machine file
   vs. the handout, because they came from two separately-generated caches (Windows vs
   Mac). The passer fill is non-deterministic and was cached in two split copies.

**Proposed fix:** stop trying to *constrain* passers into being quiet (brittle, and it
makes every hand balanced). Instead, deal **varied** passer hands and **empirically
reject** any where a bidding engine (BBA) shows the opponents would act. Then **cache the
validated fills** so they are never re-rolled, and unify on a single cache.

All the tooling this needs now exists (native Mac BBA CLI + droplet BBA server, both with
an `--auction-prefix` feature). The approach was proven on the exact failing deal.

---

## Background: how passer hands are made today

Pipeline (see `CLAUDE.md` → "Build Process" and `Tools/build-mac.sh`):

```
HTML → bbparse.py → CSV (bidding hands only; passers blank)
     → fill_hands.py  (deals the missing passer hands with dealer3 + constraints)
     → bb_fill.py / constructed_hands.csv  (the cached filled hands)
     → CSV_to_PBN.py → Package/*.pbn
```

- **`Tools/fill_hands.py`** builds, per deal, a `dealer3` script that **predeals** the
  known (bidding) hands and **deals** the passers subject to `condition <label>`, where the
  label comes from `Tools/missing_bids.csv` (`BidSequence` column). For NMF every row is
  `Calm`, so `label = auction_calm`.
- **`Tools/auction_templates.dlr`** defines the conditions. The relevant one:
  ```
  balanced_west = shape(west, any 5332 + any 4432 + any 4333 + 1xxx)
  delta_points  = |hcp(west) - hcp(east)|
  auction_calm  = balanced_west and delta_points <= 4
  ```
- **`Tools/constructed_hands.csv`** (and `BakerBridgeFull.csv`) hold the generated hands.
  They are **committed** — i.e. the fill *is* cached — but there are **two split copies**:
  `constructed_hands.csv` / `constructed_hands-windows.csv` and
  `BakerBridgeFull.csv` / `BakerBridgeFull-windows.csv`.
- `fill_hands.py` already has optional BBA validation (`--validate-bba`, `call_bba_batch`),
  but it currently shells to a **Windows** BBA over SSH (`BBA_CLI_PATH = C:\BBA-CLI\bba-cli`,
  `ssh_runner`). Slow; the "expensive process" from the earlier attempt.

---

## Root-cause analysis

### Problem 1 — `auction_calm` doesn't keep opponents quiet

`auction_calm = balanced_west and delta_points <= 4` fails for two reasons:

1. **East's shape is never constrained.** Only *West* is shaped; East is limited only by
   the HCP delta to West. So East can hold a 6-card suit and overcall while still
   satisfying the condition.
2. **`balanced_west` isn't balanced.** The `1xxx` term matches any singleton-spade hand,
   so an unbalanced West passes as "balanced." (`1xxx` presumably leaked in from another
   scenario.)

Evidence — NMF board 3, the two cached versions (N/S identical; E/W differ):

| | West | North | East | South |
|---|---|---|---|---|
| Windows cache (dealer file) | `T.JT8.A9432.QT76` (1-3-5-4) | `962.A53.KQJ5.K84` | **`AKJ853.97.T6.J92`** (6 spades!) | `Q74.KQ642.87.A53` |
| Mac cache (handout) | `K53.JT87.932.Q76` | `962.A53.KQJ5.K84` | `AJT8.9.AT64.JT92` (10 HCP, singleton) | `Q74.KQ642.87.A53` |

Both satisfy `auction_calm` (checked): Windows West is 1-3-5-4 (passes via `1xxx`), delta 2;
Mac West is 4-4-3-2 balanced, delta 4. Neither *East* is checked for biddability. So the
constraint is systematically too loose — it never asks "can this hand overcall or double?"

### Problem 2 — divergence between the two files

- The **dealer-machine file** used in class (`…NMF Set 1 - 5x7.pbn`, dated Apr 2025) is
  **byte-identical** to the repo's `Rotations-windows/.../Baker Bridge NMF Set 1 - 5x7.pbn`
  (the Windows lineage; passers from `Tools/pbns-windows/NMF.pbn`).
- The **handout** (dated Jul 2026) matches the **Mac** `Package/NMF.pbn` (current), whose
  NMF passers have been stable since the repo's first commit (2026-02-04).
- The two builds ran the non-deterministic fill independently → different random passers
  for the same deals. Sourcing the machine file from the Windows tree and the handout from
  the Mac tree produced the mismatch.

Teaching impact was limited (the students' *bidding* hands matched; only passers differed),
but a biddable passer (Problem 1) is disruptive regardless.

---

## Available tooling (all confirmed working)

- **Native Mac BBA CLI**: `~/Development/GitHub/BBA-tools/bba-cli/target/release/bba-cli`
  (Rust/NativeAOT, no .NET, no SSH). Interface:
  ```
  bba-cli --input <in.pbn> --output <out.pbn> \
          --ns-conventions <NS.bbsa> --ew-conventions <EW.bbsa> \
          [--auction-prefix "1D Pass 1H Pass ..."] [--dry-run] ...
  ```
- **Droplet `bba-server`**: same engine over HTTP (`auctionPrefix` request field),
  byte-identical to the CLI. Either can be the validation backend.
- **`--auction-prefix`**: forces the first N bids of every auction; EPBot resumes normal
  bidding after. This is the key that makes the earlier attempt viable now.
- **Convention file**: `Tools/BAKER-BRIDGE.bbsa` (used for both N-S and E-W today).

### Proof the approach works

Running the Mac BBA on the exact broken board-3 deal (Baker convention, dealer N):

```
N     E     S     W
1D    2S    X     Pass
3H    Pass  Pass  Pass
```

BBA independently has **East overcalling 2♠** — the same interference seen in class. A
BBA-reject pass would have discarded this fill. (Command used: `bba-cli -i in.pbn -o
out.pbn --ns-conventions BAKER-BRIDGE.bbsa --ew-conventions BAKER-BRIDGE.bbsa`.)

---

## Proposed solution

Replace "constrain passers to balanced" with "**deal varied passers, reject the ones that
would bid**", and cache the survivors.

1. **Loosen the dealer constraint.** Predeal N/S; deal E/W with light or no shape limits
   (variety, realism). Keep only cheap sanity limits if useful (e.g. avoid absurd 8-card
   suits) — the real filter is BBA.
2. **BBA-reject interference.** For each candidate deal, ask BBA whether the opponents stay
   silent:
   - Force the lesson's bidding-side auction with `--auction-prefix` so E/W face the true
     context (this is what the old approach lacked — it relied on BBA to reproduce the
     *bidders'* calls, which it doesn't do reliably).
   - **Accept only if E and W pass at every one of their turns.** Any non-pass ⇒ reject and
     draw another candidate.
   - Backend: native Mac `bba-cli` (batch a PBN of candidates) or the droplet server.
3. **Cache validated fills.** Persist accepted E/W per deal (e.g. into
   `constructed_hands.csv`), commit them, and on subsequent builds **reuse the cache** —
   only run the fill+BBA loop for deals with no cached fill (new/changed). This removes both
   the re-roll and the mac/windows divergence. **Unify on one cache**; retire the
   `-windows` copies and regenerate the Windows dealer/rotation files from the same source.

### Why `--auction-prefix` is the unlock

The earlier attempt generated many hands, let BBA bid all four, and kept deals whose
auction matched the target. It failed because BBA wouldn't reliably reproduce the
*bidders'* scripted auction. With `--auction-prefix` we **assert** the bidders' calls and
only ask BBA the one thing it's reliable at: *given this opening/sequence, do the opponents
have anything to say?*

Open question on how to apply the prefix (decide during prototype):
- **Per-turn probing** (most correct): force the lesson auction up to each E/W turn, let
  EPBot decide that single call; reject on any non-pass. ~2–4 BBA calls per deal.
- **Opening-only prefix** (cheapest): force just the opener's first bid, let EPBot bid the
  rest naturally; reject if E/W ever bid. One call per deal. On board 3 this already caught
  the 2♠ overcall (BBA opened 1D naturally and East acted). Good default; verify coverage.

---

## Implementation roadmap

### Phase 0 — Audit the existing fills (measure the blast radius) ✅ DONE (2026-07-14)
Ran the BBA-reject *check* over the current `Package/*.pbn` (no fills changed).
- **Tool:** `Tools/audit_passers.py` · **Data:** `Tools/audit_passers_results.csv` ·
  **Write-up:** `Tools/passer-fill-phase0-audit.md`.
- **Result:** **64 biddable-passer boards across 19 fill lessons** (of 141 total incl.
  non-fill). 58 act early (turn ≤ 3); 46 are suit overcalls/openings — the disruptive class.
  Worst: **Reverse (8), Minor (6)**; then 2Club/2over1/Jacoby/Roman/Stayman/Weak2 (5 each).
  Spot-checked hands confirm genuine 6–7 card overcalls (e.g. Roman b15 East `AK95432…` into
  a 6♥ auction) — the loose constraint is **systemic**, not one board.
- **Baseline for Phase A/B:** drive the 64 → 0; re-run the tool to check regressions.
- Method note (implemented differently than first sketched, better): probe is **per-board,
  one bba-cli run per quiet-side turn** — `--auction-prefix` = the scripted auction up to
  that turn, then read EPBot's single call. Not batched (prefix is a per-run global), but the
  native CLI is fast enough (~65s full corpus). The "quiet side" is derived from the scripted
  auction itself (the all-pass partnership), which cleanly auto-excludes competitive lessons.

### Phase A — Prototype on NMF (small, verifiable)
- [ ] Add a Mac-native BBA backend to the fill (point at
      `BBA-tools/bba-cli/target/release/bba-cli`, or the droplet server URL). Make the
      Windows/SSH path optional/legacy.
- [ ] Implement the loop for NMF only: loosen the E/W constraint, draw candidates, run BBA
      with `--auction-prefix`, accept when E/W stay silent.
- [ ] Decide the prefix strategy (opening-only vs per-turn) by measuring rejection rate and
      catching known-bad cases (board 3's `AKJ853` East must be rejected).
- [ ] Compare against current NMF passers: confirm (a) no biddable opponents, (b) more shape
      variety than the all-balanced output, (c) acceptable wall-clock (native CLI should be
      far faster than the old SSH path).
- [ ] Sanity-check that N/S bidding hands are untouched and the intended auctions still hold.

### Phase B — Generalize + cache + unify
- [ ] Extend to all `Calm` lessons (and any other "quiet opponents" scenarios). Note some
      lessons *want* interference (e.g. overcall lessons) — those must be excluded and keep
      their existing scripted constraints.
- [ ] Add the fill cache: reuse `constructed_hands.csv`; only fill+validate deals missing
      from it; make regeneration explicit/incremental (a flag or a per-deal "revalidate"),
      not automatic on every build.
- [ ] Unify mac/windows: retire `*-windows.csv` and `pbns-windows`/`Rotations-windows`
      lineages, or regenerate them from the single Mac cache so dealer files and handouts
      always agree.
- [ ] Regenerate affected lessons once, verify, and reissue any dealer/rotation files so
      class materials and handouts match.

### Interim (optional, if a class needs NMF before A/B lands)
- Tighten `auction_calm` in `auction_templates.dlr` to constrain **both** seats and remove
  the `1xxx` loophole — roughly, per seat: `hcp ≤ 11 and every suit ≤ 5 and (every suit ≤ 4
  or hcp ≤ 7)`. Then re-roll just NMF. This is a band-aid; the BBA approach is the real fix
  and gives more variety.

---

## Design decisions & open questions
- **Prefix strategy** (opening-only vs per-turn) — settle in Phase A by measuring.
- **Convention for opponents.** Today `--ew-conventions` = the same `BAKER-BRIDGE.bbsa`.
  Consider whether "would a typical opponent bid?" wants a more standard/aggressive E-W
  card so we don't under-reject.
- **Determinism.** Even with BBA-reject, the *candidate draw* is random. The cache makes the
  committed result stable; decide whether to also seed the dealer draw for reproducibility.
- **Rejection-rate blowups.** If loosening + BBA-reject rejects too often for a tightly
  predealt deal, fall back to a mild shape constraint before BBA (e.g. no 6-card suits) to
  cut the candidate count.
- **Which lessons are "quiet."** Audit `missing_bids.csv` labels; not everything is `Calm`.

## Key files & commands
- `Tools/fill_hands.py` — fill loop, dealer3 invocation, BBA hook (`call_bba_batch`).
- `Tools/auction_templates.dlr` — dealer conditions (`auction_calm`, etc.).
- `Tools/missing_bids.csv` — per-deal `BidSequence` → label.
- `Tools/constructed_hands.csv`, `Tools/BakerBridgeFull.csv` — the fill cache (+ `-windows`).
- `Tools/BAKER-BRIDGE.bbsa` — BBA convention card.
- BBA CLI: `~/Development/GitHub/BBA-tools/bba-cli/target/release/bba-cli`
- dealer3: `~/Development/GitHub/dealer3/target/release/dealer` (per `fill_hands.py`).
- Smoke test command (proof section) reproduces the board-3 overcall.
