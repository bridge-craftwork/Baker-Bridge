#!/usr/bin/env python3
"""Final build step: stamp board-identity metadata onto released PBN files.

Runs LAST in the build pipeline — after ``package_results.py`` has copied the
generated PBNs and merged in the curated boards — so it operates on the final
``Package/*.pbn`` artifacts. That guarantees every released board (generated,
merged, and any future pure-curated file) is covered uniformly.

For every ``Package/*.pbn`` file it:

  1. Ensures the file-level ``%bridge-classroom-stable: true`` header is present
     (backstop for files that bypass CSV_to_PBN.py, e.g. pure-curated ones).
  2. Stamps ``[BoardVersionToken "<64-hex-sha256>"]`` on every board — a
     rotation-canonical content hash of the deal + auction (see below).
  3. Audits ``[SkillPath]`` on every board (non-empty, not "uncategorized").

Bridge Classroom treats the token as OPAQUE: it records and echoes it, never
recomputes or compares. Making it rotation-canonical means the token is
identical across every rotational variant of a deal, so a "Report a Problem"
can be matched across all rotations.

------------------------------------------------------------------------------
FROZEN NORMALIZATION -- DO NOT CHANGE ONCE BOARDS HAVE SHIPPED.
Changing any of the rules below changes every token and breaks the ability of
Bridge Classroom to match previously-recorded tokens. If a genuinely new
canonicalization is ever needed, it must be a versioned, additive change.
------------------------------------------------------------------------------

Canonicalization:
  * Parse the [Deal] value (seat-prefix agnostic: "N:"/"E:"/"S:"/"W:").
  * Find the seat holding the ace of spades (SA). Rotate all four hands AND the
    auction dealer by the same amount so that seat becomes North (seats cycle
    clockwise N->E->S->W). Every complete deal has exactly one SA, so the
    rotation is unique.
  * canonicalDeal   = "N:<N> <E> <S> <W>" after the rotation, single-space
                      normalized (values extracted, not raw file bytes).
  * canonicalAuction = the rotation-shifted dealer, followed by the call
                      sequence: whitespace-normalized, calls upper-cased,
                      alert/annotation markers and note references stripped.
  * token = sha256(canonicalDeal + "|" + canonicalAuction), lowercase hex.
"""

import glob
import hashlib
import os
import re
import sys

STABLE_HEADER = "%bridge-classroom-stable: true"

# Seats in clockwise order. A PBN [Deal] lists hands clockwise starting from the
# seat named in its prefix; the auction proceeds clockwise from the dealer.
SEATS_CW = ["N", "E", "S", "W"]


def normalize_calls(tokens):
    """Frozen call normalization: upper-case, drop annotations + note refs."""
    calls = []
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        if re.fullmatch(r"=\d+=", tok):
            continue  # PBN note reference, not a call
        tok = tok.replace("!", "").replace("?", "")  # strip alert markers
        if not tok:
            continue
        calls.append(tok.upper())
    return calls


def parse_deal(deal_value):
    """Return {seat: hand} from a [Deal] value like 'W:h h h h'.

    Raises ValueError if the deal cannot be parsed into four hands.
    """
    if ":" not in deal_value:
        raise ValueError(f"deal has no seat prefix: {deal_value!r}")
    prefix, rest = deal_value.split(":", 1)
    prefix = prefix.strip().upper()
    if prefix not in SEATS_CW:
        raise ValueError(f"bad deal seat prefix: {prefix!r}")
    hands = rest.split()
    if len(hands) != 4:
        raise ValueError(f"expected 4 hands, got {len(hands)}: {deal_value!r}")
    start = SEATS_CW.index(prefix)
    return {SEATS_CW[(start + i) % 4]: hands[i] for i in range(4)}


def find_spade_ace(seat_hand):
    """Return the seat holding the ace of spades, or raise ValueError."""
    holders = []
    for seat in SEATS_CW:
        hand = seat_hand.get(seat, "-")
        spades = hand.split(".")[0]  # spade suit is the first of S.H.D.C
        if "A" in spades:
            holders.append(seat)
    if len(holders) != 1:
        raise ValueError(f"expected exactly one spade ace, found {holders}")
    return holders[0]


def compute_token(deal_value, dealer, call_tokens):
    """Compute the rotation-canonical BoardVersionToken (lowercase sha256 hex)."""
    seat_hand = parse_deal(deal_value)
    holder = find_spade_ace(seat_hand)
    k = SEATS_CW.index(holder)  # rotation: shift so `holder` becomes North

    # canonicalDeal: N-first, clockwise from the spade-ace holder.
    rotated_seats = [SEATS_CW[(k + i) % 4] for i in range(4)]
    canonical_deal = "N:" + " ".join(seat_hand[s] for s in rotated_seats)

    # canonicalAuction: dealer label shifted by the same rotation; calls unchanged.
    d = SEATS_CW.index(dealer)
    new_dealer = SEATS_CW[(d - k) % 4]
    calls = normalize_calls(call_tokens)
    canonical_auction = " ".join([new_dealer] + calls)

    payload = canonical_deal + "|" + canonical_auction
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def extract_auction(lines):
    """Return (dealer, [call tokens]) parsed from a board's line list.

    Falls back to the [Dealer] tag and an empty auction if no [Auction] section
    is present.
    """
    dealer = None
    calls = []
    for i, line in enumerate(lines):
        m = re.match(r'\[Auction "([^"]*)"\]', line.strip())
        if m:
            dealer = m.group(1).strip().upper()
            for cont in lines[i + 1:]:
                s = cont.strip()
                if not s or s[0] in "[{%":
                    break
                calls.extend(s.split())
            break
    if dealer is None:
        for line in lines:
            m = re.match(r'\[Dealer "([^"]*)"\]', line.strip())
            if m:
                dealer = m.group(1).strip().upper()
                break
    return dealer, calls


def insert_token(board_text, token):
    """Return board_text with [BoardVersionToken] inserted/replaced.

    Placed among the optional metadata tags: after [BCFlags] when present,
    otherwise just before the first other optional tag or commentary.
    """
    lines = board_text.split("\n")
    lines = [l for l in lines if not l.strip().startswith("[BoardVersionToken")]
    token_line = f'[BoardVersionToken "{token}"]'

    idx = None
    for i, l in enumerate(lines):
        if l.strip().startswith("[BCFlags"):
            idx = i + 1
            break
    if idx is None:
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith(("[Category", "[Difficulty", "[SkillPath", "[Student")):
                idx = i
                break
    if idx is None:
        for i, l in enumerate(lines):
            if l.strip().startswith("{"):
                idx = i
                break
    if idx is None:
        last_tag = 0
        for i, l in enumerate(lines):
            if l.strip().startswith("["):
                last_tag = i + 1
        idx = last_tag

    lines.insert(idx, token_line)
    return "\n".join(lines)


def ensure_stable_header(preamble):
    """Return preamble guaranteed to contain the stable header comment."""
    lines = preamble.split("\n") if preamble else []
    if any(l.strip().startswith("%bridge-classroom-stable:") for l in lines):
        return preamble
    # Prefer to sit next to %bridge-context:, else after %HRTitleEvent, else top.
    insert_at = None
    for i, l in enumerate(lines):
        if l.strip().startswith("%bridge-context:"):
            insert_at = i
            break
    if insert_at is None:
        for i, l in enumerate(lines):
            if l.strip().startswith("%HRTitleEvent"):
                insert_at = i + 1
                break
    if insert_at is None:
        # No recognizable header block (e.g. a bare curated file): prepend one.
        return STABLE_HEADER + "\n" + preamble if preamble else STABLE_HEADER + "\n"
    lines.insert(insert_at, STABLE_HEADER)
    return "\n".join(lines)


def split_boards(content):
    """Return (preamble, [board_text, ...]) preserving original spacing."""
    first_event = content.find('[Event "')
    if first_event < 0:
        return content, []
    preamble = content[:first_event]
    rest = content[first_event:]
    parts = re.split(r'(?=\[Event ")', rest)
    return preamble, [p for p in parts if p]


def process_file(path):
    """Stamp one PBN file in place. Returns (stamped, skipped, skill_issues)."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    preamble, boards = split_boards(content)
    preamble = ensure_stable_header(preamble)

    stamped = 0
    skipped = 0
    skill_issues = []
    new_boards = []
    fname = os.path.basename(path)

    for board in boards:
        lines = board.split("\n")
        board_no = "?"
        for l in lines:
            m = re.match(r'\[Board "([^"]*)"\]', l.strip())
            if m:
                board_no = m.group(1)
                break

        # SkillPath audit
        skill_match = re.search(r'\[SkillPath "([^"]*)"\]', board)
        skill = skill_match.group(1).strip() if skill_match else ""
        if not skill or skill.lower() == "uncategorized":
            skill_issues.append(f"{fname} board {board_no}: SkillPath = {skill!r}")

        deal_match = re.search(r'\[Deal "([^"]*)"\]', board)
        if not deal_match:
            print(f"  WARNING: {fname} board {board_no}: no [Deal]; not stamped")
            skipped += 1
            new_boards.append(board)
            continue

        dealer, calls = extract_auction(lines)
        try:
            token = compute_token(deal_match.group(1), dealer, calls)
        except ValueError as exc:
            print(f"  WARNING: {fname} board {board_no}: cannot tokenize ({exc}); "
                  "not stamped")
            skipped += 1
            new_boards.append(board)
            continue

        new_boards.append(insert_token(board, token))
        stamped += 1

    with open(path, "w", encoding="utf-8") as f:
        f.write(preamble + "".join(new_boards))

    return stamped, skipped, skill_issues


def self_check():
    """Verify rotation-invariance: two rotational variants -> identical token."""
    # Variant A: spade ace in North.
    deal_a = "N:A32.KQ.JT.987 KQ4.JT.98.765 J65.98.76.543 T98.76.54.432"
    calls = ["1S", "Pass", "2S", "Pass"]
    tok_a = compute_token(deal_a, "N", calls)
    # Variant B: same physical deal rotated one seat clockwise (ace now in East),
    # dealer shifted the same way.
    deal_b = "N:T98.76.54.432 A32.KQ.JT.987 KQ4.JT.98.765 J65.98.76.543"
    tok_b = compute_token(deal_b, "E", calls)
    assert tok_a == tok_b, f"rotation-invariance broken: {tok_a} != {tok_b}"
    assert len(tok_a) == 64 and tok_a == tok_a.lower()


def main():
    self_check()

    target = (sys.argv[1] if len(sys.argv) > 1 else None) \
        or os.environ.get("BB_PACKAGE_DIR") \
        or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Package")
    pbn_files = sorted(glob.glob(os.path.join(target, "*.pbn")))
    if not pbn_files:
        print(f"No PBN files found in {target}")
        return 1

    print(f"Stamping board tokens in {target} ({len(pbn_files)} files)")
    total_stamped = 0
    total_skipped = 0
    all_skill_issues = []
    for path in pbn_files:
        stamped, skipped, skill_issues = process_file(path)
        total_stamped += stamped
        total_skipped += skipped
        all_skill_issues.extend(skill_issues)

    print(f"\nStamped {total_stamped} boards; {total_skipped} skipped "
          f"(could not tokenize).")

    if all_skill_issues:
        print(f"\nSkillPath audit FAILED ({len(all_skill_issues)} board(s)):")
        for issue in all_skill_issues:
            print(f"  {issue}")
    else:
        print("SkillPath audit passed: every board has a real [SkillPath].")

    # Fail the build if any board is untokenized or any SkillPath is missing --
    # the acceptance criteria require every released board to carry both.
    if total_skipped or all_skill_issues:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
