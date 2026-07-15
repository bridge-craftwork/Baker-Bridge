# Shared face-to-face lesson contract (v1 draft)

**Status:** Draft for review. **Scope:** cross-collection — the standard structure for the
**face-to-face teaching materials** a bridge lesson collection produces (the physical
handouts, dealer files, and bidding sheets used in live classes). It is the shared successor
to Baker Bridge's `Tools/rotations-contract.md`, generalized so sibling collections produce
the *same* artifacts in the *same* shape.

Known instantiations:

| Collection | Repo | Output folder | Lessons | Boards/lesson (median) |
|---|---|---|---:|---:|
| Baker Bridge | `Baker-Bridge` | `Rotations/` | 50 | **20** (8–100) |
| Grant Robinson | `bridge-lessons-by-grant-robinson` | `Packaged/` | 55 | **6** (2–9) |

Both already build with the **same tools** (`bridge-wrangler` + `pdf-handouts`), so a shared
builder is feasible; this contract defines the artifacts and the per-collection knobs a
shared builder would read.

## Design principle: per-lesson slicing (automatic, by size)

The single biggest structural difference between collections is **lesson size**, and it
drives output volume. A "set" is what one table plays in a session (≈4–9 boards). Slicing is
decided **per lesson, automatically, from its own board count** — there is no per-collection
"slice / don't slice" switch:

> **For each declared set size S, a lesson of B boards is sliced into ⌈B / S⌉ sets — but only
> when B > S. A lesson with B ≤ S is emitted as a single (unsliced) set.**

So the same rule produces very different volumes without any special-casing:

- Baker: median 20 boards, all ≥ 8 → every lesson slices into 4/5/6-board sets → several
  sets/lesson (the ~18k-file multiplier).
- Grant: median 6, max 9 → the **vast majority (≤ S) are single sets, unsliced**; only the
  occasional larger lesson (e.g. a 9-board lesson with S = 6) gets sliced. ~1 set/lesson,
  ~900 files.

The multiplier is intrinsic to lesson size, applied uniformly. Small-lesson collections stay
lean automatically; large-lesson collections get teachable chunks — from one rule.

## Per-collection parameters (the config a builder reads)

| Param | Meaning | Baker | Grant |
|---|---|---|---|
| `namePrefix` | filename prefix | `Baker Bridge ` | *(none)* |
| `taxonomy` | category→lesson folder map | `titles.csv` | folder tree in `Originals/` |
| `setSizes` | board-set slice sizes | `[4, 5, 6]` | `[]` (single set) |
| `companionDoc` | per-lesson companion PDF | `_Intro.pdf` (optional) | `exercises.pdf` |
| `lin` | emit LIN files for online play | off | optional (`--lin`) |
| `source` | where deals come from | generated + BBA-clean (issue #21) | hand-authored PBN |

`setSizes: []` (or a size ≥ the largest lesson) is the "don't slice" policy that collapses to
one set per lesson.

## Standard per-lesson structure

For a lesson of *B* boards, given `setSizes`:

```
{Lesson}/
  {prefix}{Lesson}.pbn                     full lesson (all boards)
  {prefix}{Lesson}{companionDoc}           companion PDF (optional)
  <for each table view: Full Table / North-South / South>
    {prefix}{Lesson} <set label> <view>.pbn / .pdf
    {prefix}{Lesson} <set label> - {K}x{T}.pbn / .pdf   block-replicated for T tables
  <Full Table only:>
    ... Dealer Summary.pdf     non-standard dealer / vulnerability sheet
    ... Declarer's Plan.pdf
    ... Handouts.pdf           merged student handout
    ... Bidding Sheets.pdf
```

- **Set label** = `Set N (K hands)` when sliced; the plain lesson name (or `practice deals`)
  when the lesson is a single set. (Baker uses `Set N`; Grant uses `practice deals` — see
  Reconciliation.)
- When `setSizes` has more than one size, the lesson is emitted once per size (Baker's
  `4-Board Sets/`, `5-Board Sets/`, `6-Board Sets/`).

### Table views

| View | Hands shown | Use |
|---|---|---|
| **Full Table** (NESW) | all four | dealer file / reference |
| **North-South** (NS) | the partnership | partnership practice |
| **South** (S) | student seat only | single-student handout |

### Standard artifacts

| Artifact | Required? | Notes |
|---|---|---|
| full-lesson PBN | required | |
| Full Table / NS / S PBN+PDF | required | per set |
| block-replication (`{K}x{T}`) | required | multi-table play |
| Handouts (merged PDF) | required | per view |
| Bidding Sheets | required | Full Table |
| Declarer's Plan | **conditional** | declarer-play lessons (open question) |
| Dealer Summary | required | Full Table |
| companion doc (intro / exercises) | optional | `companionDoc` |
| LIN | optional | `lin` param |

## Optional metadata (per PBN)

Carried in the PBN when available; **not required** for the face-to-face product.

| Tag | Meaning | Baker | Grant | Purpose |
|---|---|---|---|---|
| `[SkillPath "…"]` | hierarchical skill classification (e.g. `bidding_conventions/new_minor_forcing`) | present (50/50, kept through to Rotations) | absent (0/220) | **filtered search** for lesson material across collections; also feeds Bridge Classroom's mastery app |

Recommendation: **support `[SkillPath]` as optional** in the shared contract. A collection
that adds it gets cross-collection filtered search "for free"; one that omits it (Grant
today) still conforms. It is cheap to add later — a per-lesson string — without touching the
deals. (App-only metadata — `[BoardVersionToken]`, `manifest.json`, `%bridge-classroom-stable`
— is **out of scope** for this contract; those belong to the Bridge Classroom product, which
the face-to-face materials don't use.)

## Reconciliation (where the two collections currently differ)

To converge on one builder, these need a shared decision:

1. **Set labelling.** Baker: `Set N (K hands)`. Grant: `practice deals`. → Propose: sliced
   sets use `Set N (K hands)`; a single-set lesson uses `practice deals` (or `(B hands)`).
2. **Component grouping.** Grant nests per-view component PDFs (exercises, practice deals,
   declarer's plan, dealer summary) in a `Components/` subfolder and merges them into one
   Handouts PDF. Baker keeps them as flat files. → Propose: keep `Components/` + a merged
   Handouts as the standard (cleaner for teachers), emit flat files only if requested.
3. **Companion doc.** Baker `_Intro.pdf` vs Grant `exercises.pdf` — both optional per-lesson
   PDFs; the `companionDoc` param covers both. A lesson may have both.
4. **Naming prefix.** Make `namePrefix` a parameter so filenames are collection-agnostic
   (drop the hard-coded `Baker Bridge ` in the shared builder).
5. **Numbered vs unnumbered categories.** Baker prefixes categories `1.`–`7.`; Grant does
   not. → Propose: optional `categoryOrder` param controlling the numeric prefix.

## Manifest (optional, deferred)

A machine-readable `manifest.json` per collection (per lesson: category/folder, board count,
set sizes, emitted artifact paths) would let a consumer verify completeness. Deferred to v2;
the standardized directory structure is the v1 contract.

## Open questions

1. **Slicing threshold vs. explicit `setSizes`.** Use an explicit per-collection `setSizes`
   (Baker `[4,5,6]`, Grant `[]`), or a global rule "slice only if B > maxSetSize"? (Explicit
   is more predictable; a threshold is less config.)
2. **Is Declarer's Plan universal or declarer-play-only?**
3. **Where does the shared contract + builder live** — a shared repo/tool both collections
   depend on, or vendored per repo? (Both currently have their own build script over the
   same two Rust tools.)
4. **Does the app product stay Baker-only,** or is a lightweight manifest worth adding to
   Grant later? (Out of scope here — this contract is face-to-face only.)
