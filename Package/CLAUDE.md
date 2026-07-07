# Package/ — Bridge Classroom Served Collection

This folder **is** the collection Bridge Classroom (BC) serves to students. BC fetches
these files at runtime from
`raw.githubusercontent.com/bridge-craftwork/Baker-Bridge/main/Package/` — there is no
staging/served split, so **`Package/*.pbn` is exactly what students get.**

Because of that, this repo is a **content producer** under BC's
[collection-producer contract](https://github.com/bridge-craftwork/Bridge-Classroom/blob/main/documentation/adr/collection-producer-contract.md).
This file records the producer obligations so authoring and generation adhere to them
automatically. It is **scoped and additive** — it does not repeat the root
[../CLAUDE.md](../CLAUDE.md), which owns the build pipeline and the mechanics of the
board-identity tags (see its "Running the Build" and "Board Identity Metadata" sections).

> **Do not hand-edit `Package/*.pbn` directly.** They are build output. Change the source
> (`Tools/*.html`, the CSV, `Tools/CSV_to_PBN.py`) or `Curated/*.pbn`, then rebuild. The
> only exception the contract anticipates is an in-place edit that preserves a stable
> board's position (see R2).

---

## The four producer obligations

The contract defines four obligations (R1–R4). Three are wired into the build; **R2 is
human discipline** and is the one to be most careful about.

### R1 — Declare release status  *(wired)*
Every file carries a header comment `%bridge-classroom-stable: true|false`; individual
boards may override with `[Stable "true"|"false"]`. **Absent ⇒ prerelease (not stable).**

- `stable=true` boards count toward student **mastery** and are selectable into teacher
  exercises. Prerelease boards stay playable but are excluded from mastery/stats.
- Baker content is mature and vetted, so `Tools/CSV_to_PBN.py` emits
  `%bridge-classroom-stable: true` on every generated file, and `stamp_board_tokens.py`
  backstops it on every released file (including curated-only files).
- **New or unvetted content must be prerelease.** Mark a single unfinished board with a
  board-level `[Stable "false"]`; do not promote it until R4's skill path is assigned.

### R2 — Freeze stable positions  *(human discipline — no tooling guard yet)*
BC keys mastery to **position**: `(collection, subfolder/lesson, board number)`, not to
content. So once a board is `stable=true`:

- **Never renumber it.** Board 5 stays board 5, forever.
- Editing a stable board **in place** is fine (fixing a card, an auction, commentary).
- A **replacement** must occupy the **same position**, itself be `stable=true`, and match
  the original **difficulty**.
- **Regeneration must not reshuffle numbers.** Board numbers come from the `DealNumber`
  column of the source CSV (`Tools/BakerBridge*.csv`) — they are *not* reindexed at
  generation. Renumbering `DealNumber`, reordering the numbered `<a name="…">` anchors in
  an HTML lesson, or changing a curated board's `[Board "…"]` will silently move a stable
  position and **corrupt student history**. Don't.

Why it matters: every time a student plays a board, BC stores a self-contained
observation with the full deal frozen — so an in-place edit can never corrupt history,
**as long as the position is stable.** Renumbering breaks that guarantee.

### R3 — Stamp the board-version token  *(wired)*
Every board carries `[BoardVersionToken "<64-hex>"]`, a rotation-canonical
`sha256(deal + "|" + auction)` (deal + auction rotated so the ♠A holder is North),
lowercase hex over extracted values. It is **derived, never hand-maintained** —
`Tools/stamp_board_tokens.py` recomputes it every build (run **last**, after the curated
merge). BC treats it as **opaque**: it records/echoes the token, never recomputes or
matches it byte-for-byte. The normalization is **frozen** — see the module docstring in
`stamp_board_tokens.py` and the root CLAUDE.md before touching it.

### R4 — Real skill path before promotion  *(wired, with one caveat)*
Every `stable=true` board must carry a genuine `[SkillPath "…"]`. `uncategorized` (or
blank) is permitted **only while a board is prerelease** — skill path feeds mastery, which
prerelease is excluded from. Assign the real path **before** flipping to stable.

- `Tools/CSV_to_PBN.py` derives `[SkillPath]` from the lesson taxonomy;
  `stamp_board_tokens.py` audits it and **fails the build** on any blank/`uncategorized`
  path.
- Caveat: that audit currently fails on `uncategorized` regardless of stable status, so a
  prerelease board with an unassigned path would fail the build today. Fine now (no
  prerelease boards exist); a refinement to exempt `stable=false` boards is tracked as a
  follow-up.

---

## Do NOT put these in the PBN  (§7 — Bridge-Classroom-owned)

These are BC config, not producer output. Do not add tags/headers for them:

- **`collection` id** — BC stamps it from its own `COLLECTIONS[]` config.
- **`report` flag** (Report-a-Problem button) — a BC collection-level switch.
- **`prerelease`** — BC's consumer-side inverse of our `stable` declaration.

(The long-standing `[BCFlags "1f"]` tag is an unrelated BridgeComposer display flag, not
the §7 `report` switch.)

---

## Promotion checklist (before flipping a board to `stable=true`)

1. Board carries a real `[SkillPath "…"]` (no blank, no `uncategorized`).
2. Board has a fresh `[BoardVersionToken]` (automatic — just rebuild).
3. Its **position is final** — from here on the board number is frozen (R2).
4. Any replacement keeps the same position + `stable=true` + comparable difficulty.

## Reference

- Producer contract: <https://github.com/bridge-craftwork/Bridge-Classroom/blob/main/documentation/adr/collection-producer-contract.md>
- Board identity & history integrity (contracts C1–C7, §7 ownership): <https://github.com/bridge-craftwork/Bridge-Classroom/blob/main/documentation/adr/board-identity-and-history-integrity.md>
- ADR-0001, positional board identity: <https://github.com/bridge-craftwork/Bridge-Classroom/blob/main/documentation/adr/0001-positional-board-identity.md>
- Build pipeline & tag mechanics: [../CLAUDE.md](../CLAUDE.md)
