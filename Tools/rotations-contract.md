# Rotations producer contract (v1 draft)

> **Superseded framing:** this is now **Baker Bridge's instantiation** of the shared,
> cross-collection **`face-to-face-contract.md`** (which generalizes this structure so
> sibling collections — e.g. Grant Robinson — produce the same artifacts). Baker's
> parameters: `namePrefix = "Baker Bridge "`, `setSizes = [4,5,6]`, `companionDoc =
> _Intro.pdf`, numbered categories. See the shared contract for the size-conditional
> slicing rule and per-collection knobs.

**Status:** Draft for review. **Related:** issue #21, `face-to-face-contract.md`,
`passer-fill-bba-redesign.md`, `build-mac.sh` (`presentation` + `rotate` phases),
the shared `package.sh` (bridge-lesson-packaging).

A second producer contract, alongside the Bridge-Classroom contract (`Collection/manifest.json`).
Where that contract describes the **app's** interactive files, this describes the **face-to-face
teaching materials** in `Rotations/` — the physical handouts, dealer files, and bidding sheets
used in live classes. It is a *standard structure*: any lesson set (Baker Bridge or another)
that feeds the pipeline produces the same shape, so a teacher always finds the same artifacts
in the same place.

## Source of truth

`Rotations/` is built **from `Collection/`** (the master), NOT from `bridge-classroom/`:

```
Collection/  ──package_presentation.py──▶  Presentation/  ──package.sh (shared)──▶  Rotations/
             (strip app control tags,                      (slice, rotate, replicate,
              organize by taxonomy)                         render PDFs)
```

The passers in `Rotations/` are therefore the same BBA-clean, cached passers as the app
(Phase B) — the two exports can no longer diverge (the 2026-07-14 class bug).

## Taxonomy

`Rotations/{Category}/{Lesson Title}/…`, seven ordered categories:

1. Basic Bidding · 2. Bidding Conventions · 3. Competitive Bidding · 4. Declarer Play ·
5. Defense · 6. Practice Deals · 7. Partnership Bidding

Lesson → folder mapping comes from `titles.csv` (`Lesson,Folder`).

## Per-lesson standard structure

For a lesson of *B* boards, the producer emits:

```
{Lesson}/
  Baker Bridge {Lesson}.pbn                     full lesson, control tags stripped
  Baker Bridge {Lesson}_Intro.pdf               companion intro (optional; present iff a lesson intro exists)
  All/
    Baker Bridge {Lesson} (B hands).pbn         all boards, one file
    Baker Bridge {Lesson} (B hands) - S.pbn/.pdf     South-only (student handout view)
    Baker Bridge {Lesson} (B hands) - NS.pbn/.pdf     North-South view
    Baker Bridge {Lesson} (B hands) - NESW.pbn/.pdf    full-table view
  {4,5,6}-Board Sets/                           the lesson split into sets of that size
    Baker Bridge {Lesson}_Intro.pdf
    Full Table/
      … Set N (K hands)  NESW.pbn/.pdf          one rotated set, K = boards in the set
      … Set N - {K}x{T}.pbn/.pdf                block-replicated for T tables
      … Set N (K hands)  NESW Dealer Summary.pdf     non-standard dealer summary
      … Set N (K hands)  NESW Declarers Plan.pdf
      … Set N (K hands)  NESW Handouts.pdf
      … Set N Bidding Sheets.pdf
      … Set N Handouts.pdf
    North-South/  … Set N (K hands) NS.pbn/.pdf
    South/        … Set N (K hands) South.pbn/.pdf
```

### Artifact roles (the "standard artifacts" every lesson set produces)

| Artifact | Role |
|---|---|
| `{Lesson}.pbn` | canonical full deal file (teacher reference) |
| `_Intro.pdf` | companion introduction (optional) |
| `All/… (B hands)` | whole lesson in one file, per table-view |
| `{N}-Board Sets/` | lesson chunked into teachable sets of N boards |
| `Full Table … NESW` | all four hands — the dealer/reference file |
| `… - {K}x{T}` | one set replicated across T physical tables |
| `Dealer Summary` | who deals / vulnerability sheet for non-standard rotations |
| `Declarers Plan` | declarer-play planning sheet |
| `Handouts` | per-student handout |
| `Bidding Sheets` | bidding-practice sheet |
| `North-South` / `South` | reduced-seat views (partnership / single-student practice) |

### Table views

- **S** — only the student seat (South by default; the lesson's `[Student]`).
- **NS** — the partnership (North-South).
- **NESW** — all four hands (Full Table / dealer file).

## Producer rules (proposed)

- **R1.** Every lesson emits `{Lesson}.pbn` (tags stripped) and the `All/` views.
- **R2.** Every lesson emits `4-`, `5-`, and `6-Board Sets/` (the standard slice sizes),
  each with `Full Table/`, `North-South/`, `South/`.
- **R3.** `_Intro.pdf` is optional — emitted iff the lesson has an intro; consumers must not
  require it. (Matches the Bridge-Classroom contract's optional `intro`.)
- **R4.** Passers come from `Collection/` (Phase B BBA-clean cache) — never regenerated
  independently here.
- **R5. (proposed) `Rotations/manifest.json`** — a machine-readable index of the structure:
  per lesson its category/folder, board count, set sizes, and the emitted artifact paths.
  Lets a consumer (or a different lesson set) verify completeness without walking the tree.

## Open questions for review

1. **Manifest (R5): build it now, or is the standardized directory structure enough?**
2. **Slice sizes** — always {4,5,6}, or per-lesson configurable?
3. **Scope of "standard artifacts"** — is the table above the full required set, or are some
   (e.g. Declarers Plan) lesson-type-specific (declarer-play lessons only)?
4. **Naming** — keep the `Baker Bridge ` filename prefix, or make it collection-agnostic
   (e.g. `{CollectionName} {Lesson}`) so other lesson sets slot in cleanly?
