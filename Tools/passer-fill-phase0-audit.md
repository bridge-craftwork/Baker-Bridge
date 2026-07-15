# Phase 0 audit — biddable passers in the released Package (BBA-reject check)

**Status:** Done (2026-07-14). **Related:** issue #21, `Tools/passer-fill-bba-redesign.md`.
**Tool:** `Tools/audit_passers.py` · **Raw data:** `Tools/audit_passers_results.csv`

This is the Phase 0 measurement from the redesign roadmap: run the BBA-reject *check*
over the **current** `Package/*.pbn` (no fills changed) to see how widespread biddable
passers are. It scopes Phase A/B and is the regression baseline ("N biddable today → 0
after the redesign").

## Method

For every board:
1. Parse the dealer + scripted auction from the released PBN.
2. Identify the **quiet partnership** — the side (N/S or E/W) that passes throughout the
   scripted auction. Boards where *both* sides bid are **competitive lessons** (Overcalls,
   Michaels, DONT, Takeout, Negative, Leben, Cue-bid, …) and are correctly excluded — those
   passers are *supposed* to act.
3. Assert the true scripted auction with `bba-cli --auction-prefix` and ask EPBot what the
   quiet side does at each of its turns. **Any non-pass ⇒ biddable passer.** (First offense
   per seat is reported.)

Backend: native Mac `bba-cli` + `Tools/BAKER-BRIDGE.bbsa` for both partnerships. This is
exactly the mechanism the redesign will use to *reject* fills — Phase 0 just runs it as a
read-only check. Full corpus (1173 boards) runs in ~65s.

## Headline

| | boards |
|---|---|
| Total boards audited | 1173 |
| Quiet boards (one side silent) | ~880 |
| **Biddable-passer boards (all)** | **141** |
| — in **fill** lessons (redesign target) | **64** |
| — in non-fill lessons (play / Partnership-*) | 77 |

**The redesign target is the 64 fill-lesson boards.** (Non-fill lessons — `100Deals`,
`100NT`, the play lessons, and the `Partnership-*` sets — are *not* driven by the passer
fill; their opponent hands come from source/curated deals. Their 77 flags are informational
and skew toward marginal takeout doubles, consistent with EPBot doubling readily. See
Caveats.)

Of the 64 fill boards, **58 act early** (first offense at turn ≤ 3) and **46 are suit
overcalls/openings** — the unambiguous, disruptive class (EPBot doesn't overcall `1S`/`2S`
without a real suit). Only 12 are early double-only and 6 are late.

## Fill lessons — biddable-passer boards

| lesson | boards | offending boards (seat@turn:call) |
|---|---:|---|
| Reverse | 8 | b3:E`1S` b5:E`1D` b7:E`1S` b8:E`2S` b10:E`1S` b11:W`1S` b13:E`1H` b14:W`1S` |
| Minor | 6 | b1:W`1S` b3:E`3D` b11:E`1H` b13:E`1H` b17:E`1D` b20:E`1S` |
| 2Club | 5 | b2:E`X` b5:W`X` b6:E`2S`/W`2S` b7:E`2H` b11:E`2N` |
| 2over1 | 5 | b10:E`3D` b17:E`X` b18:E`5C` b20:E`2N` b25:W`X`(late) |
| Jacoby | 5 | b8:E`2S` b11:W`2S` b14:E`2S` b18:E`2S`/W`X` b24:E`3C` |
| Roman | 5 | b1:E`2N` b11:W`3C` b15:E`3S` b17:E`2H` b18:E`4S`(opens!) |
| Stayman | 5 | b10:W`X` b11:E`X`(late) b14:E`X` b15:E`X` b22:E`3C` |
| Weak2 | 5 | b1:W`X` b3:W`3H` b4:E`2S` b6:E`X` b17:W`2H` |
| Drury | 4 | b1:E`3S`/W`1D` b3:W`X`(late) b5:E`1S` b8:W`2D` |
| Blackwood | 2 | b1:E`1S` b5:E`3H` |
| FSF | 2 | b10:E`X`(late) b14:E`X`(late) |
| Help | 2 | b4:E`2S` b5:W`X`(late) |
| Major | 2 | b6:W`2N` b13:E`1S` |
| NMF | 2 | b7:E`1D` b12:W`2N` |
| Preempt | 2 | b4:E`X` b5:E`X` |
| DONT | 1 | b18:S`X` |
| Notrump | 1 | b8:E`2S` |
| Ogust | 1 | b8:E`2S` |
| Transfers | 1 | b1:W`X`(late) |

**64 boards across 19 lessons.** Worst: **Reverse (8)** and **Minor (6)** — East repeatedly
dealt a biddable major/suit and overcalling at its first turn.

### Spot-checks (confirmed genuine, not EPBot artifacts)

| board | quiet hand | scripted context | verdict |
|---|---|---|---|
| Roman b15 | E `AK95432.72.962.2` | 1♥(N)… → 6♥ slam | 7-card ♠AK — screaming overcall, into a slam auction |
| Jacoby b8 | E `T876542.74.54.AQ` | 1♥ → 4♥ | 7 spades — would overcall/preempt |
| Reverse b8 | E `A98432.J2.3.8642` | 1♦-1♠ | 6-card ♠ overcall |
| Minor b17 | E `T7.853.KQJ64.AT3` | 1♣ | ~11 HCP, `KQJ64` — clean 1♦ overcall |
| Weak2 b3 | W `A3.J9652.KJ9.KJ8` | 2♠(S) | 13 HCP, 5♥ — reasonable 3♥ overcall |

These are exactly the failure class from the 2026-07-14 class incident (NMF b3's Windows-cache
East `AKJ853` → forced 2♠). The loose constraint (`auction_calm` and its per-lesson analogs)
is **systemic**, not a one-board fluke.

## Interim priority (if a class needs a fix before the redesign lands)

Top-severity = early suit overcall at the 2-level+ (long-suit / jump / slam-auction
disruption). 30 boards, notably:

- **Roman** b1,b11,b15,b17,b18 · **Jacoby** b8,b11,b14,b18,b24 · **2Club** b6,b7,b11 ·
  **2over1** b10,b18,b20 · **Weak2** b3,b4,b17 · plus Blackwood b5, Minor b3, Reverse b8,
  Notrump b8, Ogust b8, Major b6, NMF b12, Stayman b22, Help b4, Drury b1/b8, Roman b11.

These are the boards most likely to look wrong to a student mid-auction and are the natural
first re-roll targets (or manual replacements) ahead of the full Phase A/B.

## Caveats

- **EPBot aggression on doubles.** Many *non-fill* flags (and a few fill ones) are first-turn
  takeout doubles `X`. EPBot with the Baker card doubles readily; a human might pass some.
  Suit overcalls have no such ambiguity — treat suit-overcall flags as hard, double-only
  flags as softer. The redesign's open question ("which E-W convention card to reject
  against") directly affects the double count; suit-overcall counts are card-insensitive.
- **Late offenses (turn ≥ 5)** are usually lead-directing / sacrifice doubles in a
  high auction — low teaching impact. Flagged (marked `(late)` above) but deprioritized.
- **Non-fill lessons are informational.** `100Deals`, `100NT`, play lessons, and
  `Partnership-*` are not fed by the fill; a biddable opponent there is a property of the
  source deal, not a fill bug. Listed for completeness in the CSV, not a redesign target.
- **First-offense-per-seat.** The tool reports the first turn a quiet seat acts, not every
  action. Sufficient for a boolean "is this board affected."

## Baseline

**64 fill-lesson biddable boards** is the number Phase A/B must drive to **0**. Re-run
`python3 Tools/audit_passers.py` after any fill change to check regressions.
