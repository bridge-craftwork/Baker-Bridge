"""
Per-lesson bidding/defense context reminders for Baker Bridge.

Goal: when a deal appears in a mixed Bridge-Classroom assignment (without the
lesson title visible), give the student a one-line reminder of *which
conventions are in play that differ from common modern defaults* — e.g. plain
Blackwood vs Keycard, no Jacoby 2NT, one-round FSF, Reverse Drury.

These are reminders, not teaching material. We do NOT spell out response
structures (that's what the student is memorizing). We do NOT mention
universally-played conventions (Stayman, Jacoby Transfers, Negative Doubles,
takeout doubles, etc.). The Intro PDFs cover the details for each lesson.

Empty string = nothing to flag for this lesson; no comment is injected.

Source of truth: this file. A separate build step injects/refreshes a
%bridge-context line at the top of every PBN in Package/.
"""

LESSONS = {
    # ---- Basic bidding ----
    "Major":     "No Jacoby 2NT; plain Blackwood",
    "Minor":     "No 2/1; plain Blackwood",
    "Notrump":   "NO Stayman, NO Jacoby Transfers (natural responses only); plain Blackwood; Gerber 4C over NT openings",
    "Stayman":   "",
    "Transfers": "",
    "Blackwood": "Plain Blackwood (Aces); Gerber 4C over NT openings",
    "2Club":     "Strong 2C (22+); 2D = waiting/negative",
    "Weak2":     "2M-2NT = Feature ask (NOT Ogust)",
    "Ogust":     "2M-2NT = Ogust (NOT Feature)",
    "Preempt":   "",
    "FSF":       "FSF = one-round force only (invitational), NOT game-forcing",
    "NMF":       "",
    "Reverse":   "",
    "Drury":     "REVERSE Drury (2C); Opener's 2D rebid = light 3rd-seat opening",
    "Help":      "Help-Suit Game Try (NOT Short-Suit)",
    "Cue-bid":   "Support cue-bid = limit raise+ with trump support",
    "Negative":  "Negative Doubles, no upper level",
    "Michaels":  "Michaels cue-bid; Unusual 2NT",
    "DONT":      "DONT over opp's 1NT (not Cappelletti/Meckwell/etc.)",
    "Leben":     "Lebensohl over 2-level overcalls of 1NT (fast denies); applies over 2C as well (no 'systems on')",
    "Overcalls": "",
    "Takeout":   "",
    "100NT":     "Plain Blackwood; Lebensohl over interference",
    "100Deals":  "Standard American; NO 2/1; NO Jacoby 2NT; plain Blackwood",

    # ---- Jacoby 2NT ----
    "Jacoby":                "Jacoby 2NT (1M-2NT = GF raise); Splinter bids; plain Blackwood",
    "Partnership-Jacoby2NT": "Jacoby 2NT (1M-2NT = GF raise); Splinter bids",

    # ---- RKCB ----
    "Roman":                    "RKCB 1430; Jacoby 2NT; control bids",
    "Partnership-RomanKeyCard": "RKCB 1430",

    # ---- 2/1 ----
    "2over1": "2/1 Game Force; Forcing 1NT response; Jacoby 2NT; Keycard 1430",

    # ---- Partnership-* shells ----
    "Partnership-BasicBidding":     "Standard American; no conventions",
    "Partnership-BasicMajor":       "No Jacoby 2NT; plain Blackwood",
    "Partnership-BasicNotrump":     "NO Stayman, NO Jacoby Transfers (natural responses only)",
    "Partnership-Blackwood":        "Plain Blackwood (Aces); Gerber 4C over NT openings",
    "Partnership-NegativeDoubles":  "",
    "Partnership-Overcalls":        "",
    "Partnership-StaymanTransfers": "",
    "Partnership-TwoClub":          "Strong 2C (22+); 2D = waiting/negative",
    "Partnership-WeakTwos":         "2M-2NT = Feature ask (NOT Ogust)",
    "Partnership-AdvancedForcing":  "FSF one-round force only; Help-Suit Game Try",

    # ---- Defense (carding only where the student is signaling) ----
    "Signals":    "Standard carding",
    "ThirdHand":  "Standard carding",
    "SecondHand": "Standard carding",
    "OLead":      "",

    # ---- Declarer play ----
    "Eliminations":  "",
    "Holdup":        "",
    "Entries":       "",
    "Finesse":       "",
    "Trumpmgmt":     "",
    "Squeeze":       "",
    "Establishment": "",
}


def render(lesson_stem: str) -> str:
    """Return the %bridge-context line for a lesson, or '' if the stem is
    unknown or has no reminder. The line is a valid PBN comment, easy to grep
    for the PDF builder, and idempotent to replace.
    """
    note = LESSONS.get(lesson_stem, "")
    if not note:
        return ""
    return f"%bridge-context: {note}\n"


if __name__ == "__main__":
    import sys
    stems = sys.argv[1:] or sorted(LESSONS.keys())
    missing = [s for s in stems if s not in LESSONS]
    if missing:
        print(f"Unknown lesson stems: {missing}", file=sys.stderr)
        sys.exit(1)
    width = max(len(s) for s in stems)
    for stem in stems:
        note = LESSONS[stem]
        marker = note if note else "(none)"
        print(f"{stem:<{width}}  {marker}")
