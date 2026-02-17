import os
import re
import csv
from bs4 import BeautifulSoup

# Rename Bidpractice/SetN subfolders to descriptive Partnership-* names
BIDPRACTICE_RENAMES = {
    "Bidpractice/Set1":  "Partnership-BasicNotrump",
    "Bidpractice/Set2":  "Partnership-BasicMajor",
    "Bidpractice/Set3":  "Partnership-BasicBidding",
    "Bidpractice/Set4":  "Partnership-StaymanTransfers",
    "Bidpractice/Set5":  "Partnership-WeakTwos",
    "Bidpractice/Set6":  "Partnership-TwoClub",
    "Bidpractice/Set7":  "Partnership-Blackwood",
    "Bidpractice/Set8":  "Partnership-RomanKeyCard",
    "Bidpractice/Set9":  "Partnership-Jacoby2NT",
    "Bidpractice/Set10": "Partnership-Overcalls",
    "Bidpractice/Set11": "Partnership-NegativeDoubles",
    "Bidpractice/Set12": "Partnership-AdvancedForcing",
}

def remove_voids_from_hands(hands_dict):
    return {seat: hand.replace("-", "") if hand else hand for seat, hand in hands_dict.items()}

def extract_hands(soup):
    hands = {"North": None, "East": None, "West": None, "South": None}
    
    # Find all <td> elements for standard deals
    td_elements = soup.find_all("td")

    # Extract North hand (standard deal format)
    north_hands = [td for td in td_elements if "♠" in td.get_text() and ("width:6em" in td.get("style", "") or "width:7em" in td.get("style", "") or "width:8em" in td.get("style", ""))]
    if north_hands:
        # iterate through the North hands, and save the longest (this handles cases where play of cards is included):
        for hand in north_hands:
            this_hand = parse_hand(hand.get_text())
            if not hands["North"] or len(hands["North"]) < len(this_hand):
                hands["North"] = this_hand
        # print("Got a North hand:",north_hands,"parsed:",hands["North"])

    # Extract South hand (standard deal format)
    south_hands = [td for td in td_elements if "♠" in td.get_text() and "800px" in td.get("height", "")]
    if south_hands:
        for hand in south_hands:
            this_hand = parse_hand(hand.get_text())
            if not hands["South"] or len(hands["South"]) < len(this_hand):
                hands["South"] = this_hand

    # Extract East and West hands
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 3:
            if tds[1].find("img", {"src": "../t1.gif"}):  # Check for t1.gif in the second <td>
                west_td = tds[0]
                east_td = tds[2]

                if "♠" in west_td.get_text():
                    this_hand = parse_hand(west_td.get_text())
                    if not hands["West"] or len(hands["West"]) < len(this_hand):
                        hands["West"] = this_hand
                if "♠" in east_td.get_text():
                    this_hand = parse_hand(east_td.get_text())
                    if not hands["East"] or len(hands["East"]) < len(this_hand):
                        hands["East"] = this_hand

    # Look for Bidpractice format
    bidhands_div = soup.find("div", class_="bidhands")
    if bidhands_div:
        text = bidhands_div.get_text("\n", strip=True).split("\n")
        # print("bidhand:", text)
        current_seat = None
        parsed_hands = {"North": [], "South": []}
        
        for line in text:
            if "NORTH" in line:
                current_seat = "North"
            elif "SOUTH" in line:
                current_seat = "South"
            elif current_seat and any(s in line for s in "♠♥♦♣AKQJ0123456789"):
                parsed_hands[current_seat].append(line)
        
        hands["North"] = parse_hand(" ".join(parsed_hands["North"]))
        hands["South"] = parse_hand(" ".join(parsed_hands["South"]))
        
    # Remove dashes (used in the HTML to indicate voids):
    return remove_voids_from_hands(hands)

def has_card_values(text):
    """Check if text contains actual card values, not just suit symbols.

    Empty hand placeholders have suit symbols but no card values.
    A valid hand must have at least one card rank (A, K, Q, J, T, 9-2).
    """
    # Look for any card rank character
    return any(c in text for c in 'AKQJT98765432')

def extract_hands_from_table(table):
    """Extract N/S/E/W hands from a single table element."""
    hands = {"North": None, "South": None, "East": None, "West": None}

    td_elements = table.find_all("td")

    # Extract North hand (width:6em/7em/8em style)
    # Must have ALL 4 suit symbols AND actual card values (not empty placeholders)
    for td in td_elements:
        style = td.get("style", "")
        text = td.get_text()
        if ("width:6em" in style or "width:7em" in style or "width:8em" in style):
            # Require all 4 suits AND actual card values to identify as a hand
            if "♠" in text and "♥" in text and "♦" in text and "♣" in text and has_card_values(text):
                hands["North"] = parse_hand(text)
                break

    # Extract South hand (height:800px)
    for td in td_elements:
        text = td.get_text()
        if "800px" in td.get("height", ""):
            # Require all 4 suits AND actual card values
            if "♠" in text and "♥" in text and "♦" in text and "♣" in text and has_card_values(text):
                hands["South"] = parse_hand(text)
                break

    # Extract East and West hands (in same row as t1.gif image)
    for tr in table.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 3:
            if tds[1].find("img", {"src": "../t1.gif"}):  # Check for t1.gif in the second <td>
                west_td = tds[0]
                east_td = tds[2]

                west_text = west_td.get_text()
                east_text = east_td.get_text()

                # Check if West hand is visible (has all 4 suits AND card values)
                if "♠" in west_text and "♥" in west_text and "♦" in west_text and "♣" in west_text and has_card_values(west_text):
                    hands["West"] = parse_hand(west_text)

                # Check if East hand is visible (has all 4 suits AND card values)
                if "♠" in east_text and "♥" in east_text and "♦" in east_text and "♣" in east_text and has_card_values(east_text):
                    hands["East"] = parse_hand(east_text)

    return remove_voids_from_hands(hands)

def parse_hand_to_cards(hand_str):
    """Convert a hand string like 'S:AK4 H:AT865 D:Q3 C:AJ4' to a set of cards like {'SA', 'SK', 'S4', 'HA', ...}"""
    if not hand_str:
        return set()
    return set(_parse_hand_to_card_list(hand_str))

def _parse_hand_to_card_list(hand_str):
    """Convert a hand string to a list of cards preserving HTML order."""
    if not hand_str:
        return []

    cards = []
    current_suit = None

    for part in hand_str.split():
        if part.startswith('S:'):
            current_suit = 'S'
            card_chars = part[2:]
        elif part.startswith('H:'):
            current_suit = 'H'
            card_chars = part[2:]
        elif part.startswith('D:'):
            current_suit = 'D'
            card_chars = part[2:]
        elif part.startswith('C:'):
            current_suit = 'C'
            card_chars = part[2:]
        else:
            card_chars = part

        if current_suit:
            for c in card_chars:
                if c in 'AKQJT98765432':
                    cards.append(current_suit + c)

    return cards

def extract_hands_by_anchor(soup):
    """
    Extract hands at each anchor section and detect which cards were played
    and when E/W hands become visible.
    Returns a list of dicts with 'anchor', 'played_north', 'played_south',
    'played_east', 'played_west', 'show_directive' keys.
    """
    # Look for both id and name attributes - some HTML files use id="1", others use name="1"
    anchors = soup.find_all("a", attrs={"id": True}) + soup.find_all("a", attrs={"name": True})

    section_hands = []

    for anchor in anchors:
        # Check both id and name attributes
        anchor_name = anchor.get("id") or anchor.get("name", "")
        if not anchor_name or not anchor_name.isdigit():
            continue

        # Find the next table after this anchor
        table = anchor.find_next("table")
        if not table:
            continue

        hands = extract_hands_from_table(table)

        # Convert hands to card sets
        north_cards = parse_hand_to_cards(hands.get("North"))
        south_cards = parse_hand_to_cards(hands.get("South"))
        east_cards = parse_hand_to_cards(hands.get("East"))
        west_cards = parse_hand_to_cards(hands.get("West"))

        # Track E/W visibility (True if hand is present)
        east_visible = hands.get("East") is not None
        west_visible = hands.get("West") is not None

        section_hands.append({
            "anchor": anchor_name,
            "north": north_cards,
            "south": south_cards,
            "east": east_cards,
            "west": west_cards,
            "north_raw": hands.get("North"),
            "south_raw": hands.get("South"),
            "east_raw": hands.get("East"),
            "west_raw": hands.get("West"),
            "east_visible": east_visible,
            "west_visible": west_visible
        })

    # Compare consecutive sections to find played cards and visibility changes
    played_by_section = []

    # Minimum cards to consider a hand "fully visible" vs just showing played cards
    MIN_FULL_HAND = 5

    for i in range(len(section_hands)):
        if i == 0:
            # First section - determine initial hand visibility
            # Full hands (5+ cards) go in [show X]
            # Partial hands (1-4 cards) go in [showcards X:card1,card2]
            section = section_hands[i]
            visible_seats = []
            partial_cards = {}  # seat -> list of cards

            for seat, cards_key, raw_key in [("N", "north", "north_raw"), ("E", "east", "east_raw"),
                                                ("S", "south", "south_raw"), ("W", "west", "west_raw")]:
                cards = section[cards_key]
                if cards:
                    if len(cards) >= MIN_FULL_HAND:
                        visible_seats.append(seat)
                    else:
                        # Partial hand - preserve HTML order (play order)
                        partial_cards[seat] = _parse_hand_to_card_list(section[raw_key])

            initial_show = None
            if visible_seats:
                initial_show = "[show " + "".join(visible_seats) + "]"

            # Generate [showcards] directive for partial hands
            # Use space between seats, comma between cards for same seat
            showcards_directive = None
            if partial_cards:
                parts = []
                for seat in ["N", "E", "S", "W"]:
                    if seat in partial_cards:
                        cards_str = ",".join(partial_cards[seat])
                        parts.append(f"{seat}:{cards_str}")
                showcards_directive = "[showcards " + " ".join(parts) + "]"

            played_by_section.append({
                "anchor": section["anchor"],
                "played_north": set(),
                "played_south": set(),
                "played_east": set(),
                "played_west": set(),
                "show_directive": initial_show,
                "showcards_directive": showcards_directive
            })
        else:
            prev = section_hands[i-1]
            curr = section_hands[i]

            # Only detect played cards if BOTH sections have valid (non-empty) hands
            # If either section's hand is empty, the table structure changed - not card play
            played_north = set()
            played_south = set()
            played_east = set()
            played_west = set()

            if prev["north"] and curr["north"]:
                # Cards that were in previous section but not in current = played cards
                played_north = prev["north"] - curr["north"]

            if prev["south"] and curr["south"]:
                played_south = prev["south"] - curr["south"]

            if prev["east"] and curr["east"]:
                played_east = prev["east"] - curr["east"]

            if prev["west"] and curr["west"]:
                played_west = prev["west"] - curr["west"]

            # Detect visibility changes - generate [show ...] when full hands appear
            # Use MIN_FULL_HAND threshold to distinguish full hands from partial (played cards)
            show_directive = None
            showcards_directive = None

            # Check what's visible now vs before (only count full hands)
            curr_full_visible = []
            prev_full_visible = []
            curr_partial = {}

            for seat, cards_key, raw_key in [("N", "north", "north_raw"), ("E", "east", "east_raw"),
                                                ("S", "south", "south_raw"), ("W", "west", "west_raw")]:
                curr_cards = curr[cards_key]
                prev_cards = prev[cards_key]

                if curr_cards and len(curr_cards) >= MIN_FULL_HAND:
                    curr_full_visible.append(seat)
                elif curr_cards and len(curr_cards) > 0:
                    # Preserve HTML order (play order)
                    curr_partial[seat] = _parse_hand_to_card_list(curr[raw_key])

                if prev_cards and len(prev_cards) >= MIN_FULL_HAND:
                    prev_full_visible.append(seat)

            # If full visibility changed, generate new show directive
            if set(curr_full_visible) != set(prev_full_visible) and len(curr_full_visible) > len(prev_full_visible):
                show_directive = "[show " + "".join(curr_full_visible) + "]"

            # Generate showcards for any newly appearing partial hands
            # Use space between seats, comma between cards for same seat
            if curr_partial:
                parts = []
                for seat in ["N", "E", "S", "W"]:
                    if seat in curr_partial:
                        cards_str = ",".join(curr_partial[seat])
                        parts.append(f"{seat}:{cards_str}")
                showcards_directive = "[showcards " + " ".join(parts) + "]"

            played_by_section.append({
                "anchor": curr["anchor"],
                "played_north": played_north,
                "played_south": played_south,
                "played_east": played_east,
                "played_west": played_west,
                "show_directive": show_directive,
                "showcards_directive": showcards_directive
            })

    return played_by_section

def format_played_directive(played_north, played_south, played_east=None, played_west=None):
    """Format played cards into a [PLAY ...] directive with seat:card format.

    Args:
        played_north: set of cards played by North (e.g., {'SK', 'S4'})
        played_south: set of cards played by South (e.g., {'S3', 'DK'})
        played_east: set of cards played by East (e.g., {'H5'})
        played_west: set of cards played by West (e.g., {'C2'})

    Returns:
        String like '[PLAY N:SK,N:S4,S:S3,E:H5,W:C2]' or empty string if no cards played
    """
    if not played_north and not played_south and not played_east and not played_west:
        return ""

    # Sort cards by suit then rank for consistent output
    suit_order = {'S': 0, 'H': 1, 'D': 2, 'C': 3}
    rank_order = {'A': 0, 'K': 1, 'Q': 2, 'J': 3, 'T': 4, '9': 5, '8': 6, '7': 7, '6': 8, '5': 9, '4': 10, '3': 11, '2': 12}

    def sort_key(card):
        return (suit_order.get(card[0], 9), rank_order.get(card[1], 99))

    # Format as seat:suitCard (e.g., N:SK means North played Spade King)
    plays = []
    for card in sorted(played_north or [], key=sort_key):
        # card is like 'SK' (Spade King) -> format as N:SK
        plays.append(f"N:{card}")
    for card in sorted(played_east or [], key=sort_key):
        plays.append(f"E:{card}")
    for card in sorted(played_south or [], key=sort_key):
        plays.append(f"S:{card}")
    for card in sorted(played_west or [], key=sort_key):
        plays.append(f"W:{card}")

    return "[PLAY " + ",".join(plays) + "]"

def pad_auction_passes(auction_str):
    """Ensure auction ends with 3 passes after the last bid/X/XX."""
    bids = auction_str.split()
    if not bids:
        return auction_str
    # Count trailing passes
    trailing = 0
    for b in reversed(bids):
        if b.lower() == "pass":
            trailing += 1
        else:
            break
    # Need 3 trailing passes after a bid
    if trailing < 3 and len(bids) > trailing:
        bids.extend(["pass"] * (3 - trailing))
    return " ".join(bids)

########## C H O O S E - C A R D   F O R   D E F E N S E   L E S S O N S ###########
#
#   Adds [choose-card XX] directives to defense lessons (OLead, SecondHand,
#   ThirdHand, Signals) where the student must choose a card to play.
#   Parses "Lead the !XX" / "Play the !XX" / "Overtake...!XX" from the answer
#   text after [NEXT], and inserts the directive before that [NEXT].
#   Hard-codes outlier deals where the pattern isn't cleanly parseable.
#
#####################################################################################

# Hard-coded choose-card values for outlier deals
CHOOSE_CARD_OVERRIDES = {
    "OLead": {
        6:  "any:S9,S4,S3",   # "Lead any spade"
        10: "H9",             # "probably the H9" (process of elimination)
        19: "any:D2,S9",      # "Lead the D2, or perhaps the S9"
        20: "CA",             # "Lead the CA, then follow..."
    },
    "SecondHand": {
        11: "any:D8,D6,D3",  # "Do not ruff" - discard a diamond
    },
    "ThirdHand": {
        3:  "CJ",             # "you should play the CJ" (lowest of equals)
        6:  "any:H9,H7,H4,H3", # "Play a small H"
        12: "any:H7,H3,H2",  # Ruff with any small trump
    },
    "Signals": {
        6:  "S7",             # "lead a low S"
        9:  "any:D3,S2",      # "Play the D3 (or the S2)"
        10: "any:C4,C3",      # "Play a low C"
    },
}

def add_choose_card(analysis, subfolder, deal_number):
    """Add [choose-card XX] to defense lessons before the [NEXT] that precedes the answer."""
    if subfolder not in CHOOSE_CARD_OVERRIDES and subfolder not in ("OLead", "SecondHand", "ThirdHand", "Signals"):
        return analysis

    # Check for hard-coded override
    overrides = CHOOSE_CARD_OVERRIDES.get(subfolder, {})
    if deal_number in overrides:
        card = overrides[deal_number]
        if card is None:
            return analysis  # No choose-card for this deal
    else:
        # Parse card from answer text after [NEXT]:
        # "Lead the !HK" or "Play the !SQ" or "Overtake...!CA" or "Play the ! D10"
        # The ! prefix marks suit symbols from replace_suits()
        # Also handle "Play the ! D10" (space between ! and card)
        next_idx = analysis.find("[NEXT]")
        if next_idx < 0:
            return analysis
        after_next = analysis[next_idx:]
        match = re.search(r'(?:Lead|Play|Overtake[^!]*?) (?:the |with (?:the |your )?)?!([SHDC])\s*(\w+)', after_next)
        if not match:
            return analysis
        card = match.group(1) + match.group(2)

    # Find the [NEXT] that precedes the answer
    # For OLead deal 20, the answer follows the second [NEXT]
    if subfolder == "OLead" and deal_number == 20:
        first = analysis.find("[NEXT]")
        insert_pos = analysis.find("[NEXT]", first + len("[NEXT]"))
    else:
        insert_pos = analysis.find("[NEXT]")

    if insert_pos >= 0:
        analysis = analysis[:insert_pos] + "[choose-card " + card + "] " + analysis[insert_pos:]

    return analysis


def replace_suits(text,use_colon):
    if not text:
        return text
    if use_colon:
        suits = {"♠": "S:", "♥": " H:", "♦": " D:", "♣": " C:"}
    else:
        suits = {"♠": "!S", "♥": "!H", "♦": "!D", "♣": "!C"}

    for suit_symbol, suit_initial in suits.items():
        text = text.replace(suit_symbol, suit_initial)

    # Only convert "10" to "T" when it's part of card notation (after suit indicator)
    # Match patterns like "S:10", "!S10", or within card sequences like "AKQ10"
    text = re.sub(r'([SHDC][:\!]?)10', r'\1T', text)
    text = re.sub(r'([AKQJ])10', r'\1T', text)  # Also handle 10 after other card ranks
    text = re.sub(r'([2-9])10', r'\1T', text)   # Also handle 10 after numeric card ranks
    text = text.replace("--","")

    return text

def clean_up_suits(text,use_colon):

    if use_colon:
        text = text.replace(" ","")
        
    text = replace_suits(text,use_colon)
    
    if use_colon:
        text = text.replace("  "," ")
    
    return text
    
def rotate_hand_180_degrees(hands, rotate_ew=True):
    """
    Rotate hands 180 degrees (swap N↔S and optionally E↔W).

    When [ROTATE] is detected in Baker Bridge HTML:
    - N/S hands are extracted from pre-rotation sections → need rotation
    - E/W hands are extracted from post-rotation full deal → already rotated
    - So we only rotate N/S, not E/W
    """
    temp = hands["North"]
    hands["North"] = hands["South"]
    hands["South"] = temp
    if rotate_ew:
        temp = hands["East"]
        hands["East"] = hands["West"]
        hands["West"] = temp
    
def rotate_seat_180_degrees(seat):
    partners = {
        'N': 'S',
        'S': 'N',
        'E': 'W',
        'W': 'E',
        'North': 'South',
        'South': 'North',
        'East': 'West',
        'West': 'East'
    }
    return partners.get(seat)    

def parse_hand(hand_text):
    hand = []
    # print("Parsing hand", hand_text)
    for line in hand_text.splitlines():
        line = line.strip()
        if line:
            hand.append(clean_up_suits(line,True))
    return " ".join(hand).replace("  ", " ")
    
def extract_analysis_text(td_text):
    # remove any grey text:
    black_text = re.sub(r'<font[^>]*?>.*?</font>', '', td_text, flags=re.DOTALL)
    # Remove any nested tables (auction tables) first
    black_text = re.sub(r'<table[^>]*>.*?</table>', '', black_text, flags=re.DOTALL)
    # Extract all content from the TD
    # Match content after the opening <td...> tag up to closing </td>
    match = re.search(r'<td[^>]*>(.*?)</td>', black_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""
    
def clean_up_analysis(analysis,td_str,last_bid):
#     if "partner's minor suit opening you should have" in analysis:
#         print("-----",analysis,"-----")
#     if "But even with this type of hand you should" in analysis:
#         print("-----",analysis,"-----")
    analysis = analysis.replace("\t", "")               # remove tabs (used for indentation in original)
    analysis = analysis.replace("\xa0.",".").replace("\xa0"," ")    # remove non-blank spaces
    
    analysis = analysis.replace("\n  ", "")               # remove hard line breaks
    analysis = analysis.replace("\n ", "")               # remove hard line breaks
    analysis = analysis.replace("\n", "")               # remove hard line breaks
    # Handle both <br> and <br/> variants
    analysis = re.sub(r'<br\s*/?>\s*<br\s*/?>', r'\\n', analysis)  # convert double line breaks to \n
    analysis = re.sub(r'<br\s*/?>', '', analysis)                   # remove single line breaks
    analysis = replace_suits(analysis,False)
    analysis = re.sub(r'<font.*?>.*?</font>', "", analysis, flags=re.DOTALL)
    analysis = analysis.replace("</font>","")           # remove trailing font tags
    # Remove <span> tags but keep the text inside
    analysis = re.sub(r'</?span.*?>', '', analysis, flags=re.DOTALL)
    # Remove <a>...</a> tags and their contents
    analysis = re.sub(r'<a.*?>.*?</a>', '', analysis, flags=re.DOTALL)
    # Normalize <strong>/<em> to <b>/<i> (BridgeComposer formatting)
    analysis = analysis.replace("<strong>", "<b>").replace("</strong>", "</b>")
    analysis = analysis.replace("<em>", "<i>").replace("</em>", "</i>")
    analysis = re.sub(r'\.([A-Za-z])', r'. \1', analysis)   # Add space after periods, when text is following
    analysis = re.sub(r'\?([A-Za-z])', r'? \1', analysis)   # Add space after periods, when text is following
    analysis = analysis.strip()
    analysis = analysis.rstrip("\\n")                # remove trailing new lines (sometimes separating anchors which are already gone)
#    analysis = analysis.replace("\n", r"\n")
    # Check for rotation instruction first (may appear with NEXT button)
    if "rotate" in analysis.lower():
        analysis = analysis + " [ROTATE]"
        analysis = analysis.replace("lickto", "lick NEXT to")
        analysis = analysis.replace("lick.", "lick NEXT.")
    elif "NEXT" in td_str:
        analysis = analysis + " [NEXT]"
        analysis = analysis.replace("lickto", "lick NEXT to")
        analysis = analysis.replace("lick.", "lick NEXT.")
    elif "ROTATE" in td_str:
        analysis = analysis + " [ROTATE]"
        analysis = analysis.replace("lickto", "lick ROTATE to")
        analysis = analysis.replace("lick.", "lick ROTATE.")
    elif not 'href="deal' in td_str:
        analysis = analysis + " [BID " + replace_suits(last_bid,False) + "]"

#     if "partner's minor suit opening you should have" in analysis:
#         print("*****",analysis,"*****")
#     if "But even with this type of hand you should" in analysis:
#         print("*****",analysis,"*****")

    return analysis


########## E X T R A C T   P R O G R E S S I V E   A N A L Y S I S #################
#
#   Takes a table with the HTML auction.  Returns the auction in
#   table format, as well as Dealer, Declarer and Contract.
#
####################################################################################

def extract_progressive_analysis(soup,filepath):

# Standard layout:
#
#   Each step has an anchor <a>:
#       Each contains a table:
#           Sub-table: Auction so far
#       Analysis for this step
#
# General approach:
#
#   1. get full auction as a simple list
#   2. Iterate through tables (Steps)
#       - find auction-so-far as a simple list.  This auction will end with "BID"
#           - Look into the full auction to see what BID will become
#               - This will be the label for this step
#       - Pull the text from the outer table, following the inner table.  Also
#               exclude the <font> enclosed text (prior steps in grey).
#       - Save the analysis as a new list element, with [BID] prepended.

    analysis_lines = []

    # Extract played cards by section (for declarer play scenarios)
    played_by_section = extract_hands_by_anchor(soup)

    final_auction_table = extract_final_auction_table(soup)
    
    dealer, auction_str, contract, declarer, analysis_str = extract_auction_info(final_auction_table,filepath)

#   Remove the vertical bars, and parse into a list
    auction_str = auction_str.replace(" |", "")
    
#   all_bids = ["pass", "1♠", "pass", "2♠", "pass", "4♠"]
    all_bids = auction_str.split()

    # Fix bare suit symbols with no level (e.g., Transfers deal10 has "♦" instead of "3♦")
    # Look for bids that are just a suit symbol and recover the level from the prior auction tables
    suit_symbols = {"♦", "♥", "♠", "♣"}
    for idx, bid in enumerate(all_bids):
        if bid in suit_symbols:
            # Search inner auction tables (no nested tables) for the correct bid at this position
            for table in soup.find_all('table'):
                if table.find('table'):
                    continue  # skip outer layout tables
                first_row_cells = [cell.get_text(strip=True) for cell in table.find('tr').find_all('td')]
                if 'WEST' not in first_row_cells:
                    continue  # not an auction table
                rows = table.find_all("tr")
                table_bids = [cell.get_text(strip=True) or "" for row in rows[1:] for cell in row.find_all("td")]
                # Strip leading empties to match all_bids indexing (extract_auction_info strips these)
                while table_bids and table_bids[0].strip() == "":
                    table_bids.pop(0)
                while table_bids and table_bids[-1].strip() == "":
                    table_bids.pop()
                if idx < len(table_bids) and table_bids[idx] not in suit_symbols and table_bids[idx] not in ["", "BID", "pass"]:
                    all_bids[idx] = table_bids[idx]
                    break

#     print("auction_str:", auction_str)
#     print("")
    # print("all_bids:", all_bids)
    # print("")
    
    all_tds = soup.find_all('td')


#   Iterate all tables which contain subtables.  These will normally have the auction
#   in the inner table, then analysis following in the outer table:

    table_tds = [td for td in all_tds if td.find('table')]
    prev_had_next = False
    for td in table_tds:
        partial_dealer, partial_auction_str, partial_contract, partial_declarer, partial_analysis_str = extract_auction_info(td,filepath)
        partial_auction_str = partial_auction_str.replace(" |", "")
        partial_auction_list = partial_auction_str.split()
        last_bid = partial_auction_list[-1]
        if last_bid == "BID":
            if len(partial_auction_list) > len(all_bids):
                print("***")
                print("problem with " + filepath)
                print("all_bids:            ", all_bids)
                print("partial_auction_list:", partial_auction_list)
            else:
                last_bid = all_bids[len(partial_auction_list)-1]

        td_str = str(td)
        analysis = extract_analysis_text(td_str)
        analysis = clean_up_analysis(analysis,td_str,last_bid)
        # Detect clear-commentary: prior section ended with [NEXT] and
        # current TD has no grey <font> tags (not a continuation)
        if prev_had_next and '<font' not in td_str:
            analysis = "[clear-commentary]\\n" + analysis
        analysis_lines.append(analysis)
        prev_had_next = analysis.endswith("[NEXT]")
#   Now iterate TDs which do not contain an inner table, but do contain the text "NEXT"

    non_table_tds = [td for td in all_tds if not td.find('table')]
    for td in non_table_tds:
#        print("td:", str(td))
        if "3" in td.get("rowspan",""):
            td_str = str(td)
            analysis = extract_analysis_text(td_str)
            analysis = clean_up_analysis(analysis,td_str,"")
            # Detect clear-commentary for non-table sections too
            if prev_had_next and '<font' not in td_str:
                analysis = "[clear-commentary]\\n" + analysis
            analysis_lines.append(analysis)
            prev_had_next = analysis.endswith("[NEXT]")

#         print(analysis)
#         print()

    # Inject [PLAY] and [show] directives into analysis lines based on section
    # The played_by_section list matches anchors 1, 2, 3... to analysis lines
    for i, section_info in enumerate(played_by_section):
        played_n = section_info.get("played_north", set())
        played_s = section_info.get("played_south", set())
        played_e = section_info.get("played_east", set())
        played_w = section_info.get("played_west", set())
        show_directive = section_info.get("show_directive")
        showcards_directive = section_info.get("showcards_directive")

        if i < len(analysis_lines):
            prefix = ""
            # Add show directive if full hands became visible
            if show_directive:
                prefix = show_directive + "\\n"
            # Add showcards directive if partial hands (played cards) are visible
            if showcards_directive:
                prefix += showcards_directive + "\\n"
            # Add play directive if cards were played
            if played_n or played_s or played_e or played_w:
                prefix += format_played_directive(played_n, played_s, played_e, played_w) + "\\n"
            if prefix:
                analysis_lines[i] = prefix + analysis_lines[i]

    # Add [RESET] tag to step AFTER one that mentions "complete deal" or "full deal"
    # This shows original hands when viewing the complete deal
    for i in range(len(analysis_lines) - 1):
        line_lower = analysis_lines[i].lower()
        if "complete deal" in line_lower or "full deal" in line_lower:
            # Add [RESET] to the next step
            analysis_lines[i + 1] = "[RESET]\\n" + analysis_lines[i + 1]

    return "\\n".join(analysis_lines)

########## E X T R A C T   A U C T I O N   I N F O ##################
#
#   Takes a table with the HTML auction.  Returns the auction in
#   table format, as well as Dealer, Declarer and Contract.
#
#####################################################################

def extract_auction_info(auction_table,filepath):

    positions = ["West", "North", "East", "South"]

#         Converts an HTML table like this:
#         WEST   NORTH   EAST    SOUTH
#         pass   1♠      pass    2♠
#         pass   4♠      pass    pass
#         
#         Into "auction" a list like this:
#         [
#             ["pass", "1♠", "pass", "2♠"],
#             ["pass", "4♠", "pass", "pass"]
#         ]

    rows = auction_table.find_all("tr")
    auction = [[td.get_text(strip=True) or "" for td in row.find_all("td")] for row in rows[1:]]
    
#   Flatten the auction into a single list:
#   all_bids = ["pass", "1♠", "pass", "2♠", "pass", "4♠", "pass", "pass", "pass"]

    all_bids = [bid for round_bids in auction for bid in round_bids]
    
    while all_bids and all_bids[-1].strip() == "":
        all_bids.pop()

#   dealer is first non-blank:
    dealer = next((positions[i % 4] for i, bid in enumerate(all_bids) if bid.lower() not in [""]), None)
    
#   contract is final bid, excluding pass, double, or redouble.
#   challenge is "", double or redouble.
#   strain is the final bid, less the level.
#   declarer is either the auction winner or their partner - whichever first bid the strain.

    # Initialize variables
    strain, contract, declarer, challenge = None, None, None, None
    
    suffix = ""
    
    # Identify the contract (excluding pass, double, redouble)
    for i in range(len(all_bids) - 1, -1, -1):
        bid = all_bids[i].lower()
        if bid not in ["", "pass", "all pass", "double", "redouble"]:
            contract = all_bids[i]  # The final contract bid
            strain = contract[1:]  # Strain is the contract without the level
            break
    
    # Identify the challenge (double, redouble, or blank)
    if i < len(all_bids) - 1:
        next_bid = all_bids[i + 1].lower()
        if next_bid == "double":
            challenge = "double"
            suffix = "X"
        elif next_bid == "redouble":
            challenge = "redouble"
            suffix = "XX"
        else:
            challenge = ""
            suffix = ""
    
    # Determine the declarer
    positions = ["West", "North", "East", "South"]
    contract_seat = i % 4  # The position of the final contract bid

    # Find who first bid the strain (either the contract winner or their partner)
    for j in range(i):
        bid = all_bids[j]
        if j % 2 == contract_seat % 2:  # only consider bids by the winning pair:
            if bid and bid[1:] == strain:  # A bid matching the strain
                declarer = positions[j % 4]
                break
                
    # for some reason, the above loop doesn't find the declarer if the final bid set the
    # strain, so we'll cover that case here:
    if declarer == None:
        declarer = positions[contract_seat]

    analysis_start = False
    analysis_lines = []
    pass_count = 0

    analysis_str = "\\n".join(analysis_lines)
    auction_str = " | ".join([" ".join(bid_row) for bid_row in auction])
    auction_str = ' '.join(auction_str.split())

    contract = contract + suffix
    
    if "double pass pass pass" in auction_str:
        contract = contract + "X"
#    print (filepath, ", Dealer", dealer, ", contract", contract, ", declarer", declarer, ", auction", auction_str)

    return dealer, auction_str, contract, declarer, analysis_str

def extract_final_auction_table(soup):

    # Find all tables
    tables = soup.find_all('table')

    # Filter tables that contain the auction (WEST NORTH EAST SOUTH row)
    auction_tables = [
        table for table in tables
        if any("WEST" in cell.get_text(strip=True) for cell in table.find_all("td")) and
           any("NORTH" in cell.get_text(strip=True) for cell in table.find_all("td"))
    ]
    if not auction_tables:
        return None

    # Select the last auction table
    return auction_tables[-1]

def extract_bidding_info(soup,filepath):
    # Check for the standard bidding div first
    bidding_div = soup.find("div", class_="bidding")
    if bidding_div:
        table = bidding_div.find("table")
        if not table:
            return None, None, None, None, None
            
        dealer, auction_str, contract, declarer, analysis_str = extract_auction_info(table,filepath)

        # Extract analysis text after the auction table
        # Remove the table from a copy so we only get the commentary
        bidding_copy = BeautifulSoup(str(bidding_div), "html.parser")
        for tbl in bidding_copy.find_all("table"):
            tbl.decompose()
        # Convert <br><br> to paragraph markers before extracting text
        html_str = str(bidding_copy)
        html_str = re.sub(r'<br\s*/?>\s*<br\s*/?>', ' \\\\n ', html_str)
        html_str = re.sub(r'<br\s*/?>', ' ', html_str)
        commentary = BeautifulSoup(html_str, "html.parser")
        analysis_str = commentary.get_text()
        # Clean up whitespace: collapse multiple spaces, trim
        analysis_str = re.sub(r'[ \t]+', ' ', analysis_str).strip()
        # Remove leading paragraph markers (from <br><br> before commentary starts)
        while analysis_str.startswith('\\n'):
            analysis_str = analysis_str[2:].strip()
        # Apply suit symbol conversion
        analysis_str = replace_suits(analysis_str, False)
        
        return dealer, auction_str, contract, declarer, analysis_str

    # Handle the alternative format

    auction_table = extract_final_auction_table(soup)

#    print("auction_table:", auction_table)

    dealer, auction_str, contract, declarer, analysis_str = extract_auction_info(auction_table,filepath)

    analysis_str = extract_progressive_analysis(soup,filepath)

    return dealer, auction_str, contract, declarer, analysis_str

def extract_lesson_kind(soup):
    # Extract all anchor tags
    anchors = soup.find_all("a")

    # Collect unique non-blank text
    kind_texts = set()

    for anchor in anchors:
        text = anchor.get_text(strip=True)
        if text and ( not text.startswith("Deal")
                    and "summary" not in text.lower()
                    and "lesson" not in text.lower()
                    and "back" not in text.lower()
                    and "introduction" not in text.lower()
                    # and "rotate" not in text.lower()
                    and "home" not in text.lower()
                    and "review" not in text.lower()):
            kind_texts.add(text)

    return "+".join(sorted(kind_texts)) if kind_texts else None

def extract_opening_lead(soup,filepath):
    # Find all text nodes that contain the phrase "leads the"
    lead_text = soup.find(string=lambda text: text and ( "leads" in text or "OL:" in text or "Partner led" in text or "Lead the" in text or "probably the" in text))
    
    if not lead_text:
        return None
    # print(filepath + ":")
    # print("lead_text", lead_text)
    # Move up to the parent <td> element to access the HTML structure
    lead_td = lead_text.find_parent("td")
    if not lead_td:
        return None
    # print(str(lead_td))
    
    # Regular expression to match "leads the" followed by a rank and suit, with optional <span> in between
    pattern_1 = r'leads (?:the )?\s*(?:<span.*?>)?([♠♥♦♣])(?:<\/span.*?>)?\s*(\d+|[AKQJT0123456789])'
    pattern_2 = r'OL\:\s*(?:<span.*?>)?([♠♥♦♣])(?:<\/span.*?>)?\s*(\d+|[AKQJT0123456789])'
    pattern_3 = r'Partner led the (?:<span.*?>)?([♠♥♦♣])(?:<\/span.*?>)?\s*(\d+|[AKQJT0123456789])'
    pattern_4 = r'Lead the (?:<span.*?>)?([♠♥♦♣])(?:<\/span.*?>)?\s*(\d+|[AKQJT0123456789])'
    pattern_5 = r'probably the (?:<span.*?>)?([♠♥♦♣])(?:<\/span.*?>)?\s*(\d+|[AKQJT0123456789])'
    
    match = re.search(pattern_1, str(lead_td), re.DOTALL)
    if not match:
        match = re.search(pattern_2, str(lead_td), re.DOTALL)
    if not match:
        match = re.search(pattern_3, str(lead_td), re.DOTALL)
    if not match:
        match = re.search(pattern_4, str(lead_td), re.DOTALL)
    if not match:
        match = re.search(pattern_5, str(lead_td), re.DOTALL)

    if match:
        rank = match.group(1)
        suit = match.group(2)
        # print("Found it!")
        # print(f"{rank}{suit}")
        return f"{rank}{suit}"
    return ""
    
def process_files(folder_path, output_csv, max_files=3000):
    files = [
        os.path.join(dirpath, file)
        for dirpath, _, filenames in os.walk(folder_path)
        for file in filenames
        if file.startswith("deal") and file.endswith(".html") and file not in ["deal00.html", "deal000.html"]
    ]

    results = []

    for filepath in files[:max_files]:
        filename = os.path.basename(filepath)
        subfolder_path = os.path.relpath(os.path.dirname(filepath), folder_path)
        subfolder_path = BIDPRACTICE_RENAMES.get(subfolder_path, subfolder_path)

        match = re.search(r"deal(\d+)", filename)
        deal_number = int(match.group(1)) if match else None

        with open(filepath, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")
            hands = extract_hands(soup)
            dealer, auction_str, contract, declarer, analysis = extract_bidding_info(soup,filepath)
            contract = replace_suits(contract,False).replace("!", "")
            auction_str = replace_suits(auction_str,False).replace("!","").replace("redouble","XX").replace("double","X")
            # Fix concatenated bids from unclosed <td> tags in Set3/Set4 deal14
            auction_str = auction_str.replace("1NTpass3H", "1NT").replace("2Cpass2S", "2C")
            # Fix bare "D" bid from Transfers deal10 (missing level in HTML)
            auction_str = re.sub(r'\bpass D\b', 'pass 3D', auction_str)
            # Ensure auction ends with 3 passes
            auction_str = pad_auction_passes(auction_str)
            opening_lead = replace_suits(extract_opening_lead(soup,filepath),False)
            if opening_lead:
                opening_lead = opening_lead.replace("!","")
            kind = extract_lesson_kind(soup)

            if "[ROTATE]" in analysis:
                # N/S hands come from pre-rotation sections, need rotation
                # E/W hands come from post-rotation full deal, already correct
                # Dealer/declarer come from post-rotation auction, already correct
                rotate_hand_180_degrees(hands, rotate_ew=False)
                # Don't rotate dealer/declarer - they're from post-rotation auction
                
#           On most deals, the student sits in the South position:
            student = "South"
            if subfolder_path == "OLead":
                student = "West"
            if subfolder_path == "ThirdHand":
                student = "East"
            if subfolder_path == "SecondHand" or subfolder_path == "Signals":
                if "You are East" in analysis:
                    student = "East"
                else:
                    student = "West"
            
#         print()
#         print(filepath, ":")
#         print("Dealer:", dealer, "contract:", contract, "declarer:", declarer, "auction:", auction_str, "lead:", opening_lead)
#         print()
#         print("analysis:", analysis)
        
        results.append([
            subfolder_path, filename, deal_number, kind,
            hands["North"], hands["East"], hands["South"], hands["West"],
            dealer, student, auction_str, contract, declarer, opening_lead, analysis
        ])

    results.sort(key=lambda x: (x[0], x[1]))
    
    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow([
            "Subfolder", "Filename", "DealNumber", "Kind", "NorthHand", "EastHand", "SouthHand", "WestHand",
            "Dealer", "Student", "Auction", "Contract", "Declarer", "Lead", "Analysis"
        ])
        csvwriter.writerows(results)

def format_hand_display(hands):
    """Format hands as a fixed-width text display for debugging.

    Returns a string showing all four hands in a compass layout.
    """
    lines = []

    # Helper to format a single hand's suits
    def format_suits(hand):
        if not hand:
            return ["(no hand)", "", "", ""]
        # Parse hand like "S:QJ865 H:K92 D:AK C:863"
        suits = {"S": "", "H": "", "D": "", "C": ""}
        for part in hand.split():
            if part.startswith("S:"):
                suits["S"] = part[2:]
            elif part.startswith("H:"):
                suits["H"] = part[2:]
            elif part.startswith("D:"):
                suits["D"] = part[2:]
            elif part.startswith("C:"):
                suits["C"] = part[2:]
        return [
            f"S: {suits['S'] or '-'}",
            f"H: {suits['H'] or '-'}",
            f"D: {suits['D'] or '-'}",
            f"C: {suits['C'] or '-'}"
        ]

    north = format_suits(hands.get("North"))
    south = format_suits(hands.get("South"))
    west = format_suits(hands.get("West"))
    east = format_suits(hands.get("East"))

    # Calculate max width for each hand
    n_width = max(len(s) for s in north)
    s_width = max(len(s) for s in south)
    w_width = max(len(s) for s in west)
    e_width = max(len(s) for s in east)

    # Center padding
    center_pad = 20

    # North (centered)
    lines.append("")
    lines.append(" " * center_pad + "NORTH")
    for suit in north:
        lines.append(" " * center_pad + suit)

    # West and East side by side
    lines.append("")
    lines.append(f"{'WEST':<{center_pad}}{'':^10}{'EAST'}")
    for i in range(4):
        lines.append(f"{west[i]:<{center_pad}}{'':^10}{east[i]}")

    # South (centered)
    lines.append("")
    lines.append(" " * center_pad + "SOUTH")
    for suit in south:
        lines.append(" " * center_pad + suit)

    return "\n".join(lines)


def write_anchor_debug(filepath, folder_path, soup):
    """Write debug output showing what was extracted from each anchor."""

    # Create output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Anchors")
    os.makedirs(output_dir, exist_ok=True)

    # Get relative path for organizing output
    rel_path = os.path.relpath(filepath, folder_path)
    # Convert path like "NMF/deal01.html" to "NMF_deal01.txt"
    output_name = rel_path.replace(os.sep, "_").replace(".html", ".txt")
    output_path = os.path.join(output_dir, output_name)

    lines = []
    lines.append(f"Debug output for: {rel_path}")
    lines.append("=" * 60)

    # Find all anchors
    anchors = soup.find_all("a", attrs={"id": True}) + soup.find_all("a", attrs={"name": True})

    for anchor in anchors:
        anchor_id = anchor.get("id") or anchor.get("name", "")
        if not anchor_id or not anchor_id.isdigit():
            continue

        lines.append("")
        lines.append(f"ANCHOR #{anchor_id}")
        lines.append("-" * 40)

        # Find the next table after this anchor
        table = anchor.find_next("table")
        if not table:
            lines.append("  (no table found)")
            continue

        # Extract hands from this table
        hands = extract_hands_from_table(table)

        # Show which hands were found
        found = []
        if hands.get("North"): found.append("N")
        if hands.get("East"): found.append("E")
        if hands.get("South"): found.append("S")
        if hands.get("West"): found.append("W")
        lines.append(f"Hands found: {' '.join(found) if found else '(none)'}")

        # Display the hands
        lines.append(format_hand_display(hands))
        lines.append("")

    # Write output
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_path


def process_files(folder_path, output_csv, max_files=3000):
    files = [
        os.path.join(dirpath, file)
        for dirpath, _, filenames in os.walk(folder_path)
        for file in filenames
        if file.startswith("deal") and file.endswith(".html") and file not in ["deal00.html", "deal000.html"]
    ]

    results = []

    for filepath in files[:max_files]:
        filename = os.path.basename(filepath)
        subfolder_path = os.path.relpath(os.path.dirname(filepath), folder_path)
        subfolder_path = BIDPRACTICE_RENAMES.get(subfolder_path, subfolder_path)

        match = re.search(r"deal(\d+)", filename)
        deal_number = int(match.group(1)) if match else None

        with open(filepath, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file, "html.parser")

            # Generate debug anchor output
            write_anchor_debug(filepath, folder_path, soup)

            hands = extract_hands(soup)
            dealer, auction_str, contract, declarer, analysis = extract_bidding_info(soup,filepath)
            contract = replace_suits(contract,False).replace("!", "")
            auction_str = replace_suits(auction_str,False).replace("!","").replace("redouble","XX").replace("double","X")
            # Fix concatenated bids from unclosed <td> tags in Set3/Set4 deal14
            auction_str = auction_str.replace("1NTpass3H", "1NT").replace("2Cpass2S", "2C")
            # Fix bare "D" bid from Transfers deal10 (missing level in HTML)
            auction_str = re.sub(r'\bpass D\b', 'pass 3D', auction_str)
            # Ensure auction ends with 3 passes
            auction_str = pad_auction_passes(auction_str)
            opening_lead = replace_suits(extract_opening_lead(soup,filepath),False)
            if opening_lead:
                opening_lead = opening_lead.replace("!","")
            kind = extract_lesson_kind(soup)

            if "[ROTATE]" in analysis:
                # N/S hands come from pre-rotation sections, need rotation
                # E/W hands come from post-rotation full deal, already correct
                # Dealer/declarer come from post-rotation auction, already correct
                rotate_hand_180_degrees(hands, rotate_ew=False)
                # Don't rotate dealer/declarer - they're from post-rotation auction

#           On most deals, the student sits in the South position:
            student = "South"
            if subfolder_path == "OLead":
                student = "West"
            if subfolder_path == "ThirdHand":
                student = "East"
            if subfolder_path == "SecondHand" or subfolder_path == "Signals":
                if "You are East" in analysis:
                    student = "East"
                else:
                    student = "West"

            # Add [choose-card] directives to defense lessons
            analysis = add_choose_card(analysis, subfolder_path, deal_number)

        results.append([
            subfolder_path, filename, deal_number, kind,
            hands["North"], hands["East"], hands["South"], hands["West"],
            dealer, student, auction_str, contract, declarer, opening_lead, analysis
        ])

    results.sort(key=lambda x: (x[0], x[1]))

    with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow([
            "Subfolder", "Filename", "DealNumber", "Kind", "NorthHand", "EastHand", "SouthHand", "WestHand",
            "Dealer", "Student", "Auction", "Contract", "Declarer", "Lead", "Analysis"
        ])
        csvwriter.writerows(results)

folder_path = "/Users/rick/Documents/Bridge/Baker Bridge/Website/Baker Bridge/bakerbridge.coffeecup.com"
output_csv = "BakerBridge.csv"
process_files(folder_path, output_csv)