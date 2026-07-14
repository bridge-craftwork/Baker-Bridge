# showcards dummy-card key

Answer key for the defense-lesson `[showcards]` fix (companion to #11/#12). Each entry
maps a board's ORIGINAL `[showcards]` directive (what `CSV_to_PBN.py` emits) to the
corrected directive(s). `apply_showcards_dummy.py` applies these to `pbns/*.pbn` every
build.

Two kinds of fix:
- **Single-trick** (Section A): the position is one in-progress trick; just add dummy's
  missing card (verified in North's hand).
- **Multi-trick** (Section B): the old directive crammed several tricks into one
  `[showcards]`, which the play engine renders as a single trick (BC bug report on
  SecondHand b10). Corrected to `[PLAY <completed tricks, in play order>]` +
  `[showcards <current trick only>]`, so only the current trick shows. Missing non-dummy
  cards were reconstructed from the deal + narrative. The proper trick-by-trick redesign
  (with `[NEXT]` between tricks + signal highlighting) is tracked in #15; this is the
  stopgap that makes them playable.

Format: `<Lesson> <Board> | FROM => TO`  ·  `#` = note. `TO` may contain two directives.

## A. Single-trick — add dummy's card (32)

ThirdHand 1  | [showcards W:S2] => [showcards W:S2 N:S3]
ThirdHand 2  | [showcards W:HQ] => [showcards W:HQ N:H4]
ThirdHand 3  | [showcards W:C4] => [showcards W:C4 N:C3]
ThirdHand 4  | [showcards W:S3] => [showcards W:S3 N:S4]
ThirdHand 5  | [showcards W:S7] => [showcards W:S7 N:S3]
ThirdHand 6  | [showcards W:H8] => [showcards W:H8 N:H6]
ThirdHand 7  | [showcards W:HQ] => [showcards W:HQ N:H4]
ThirdHand 8  | [showcards W:H2] => [showcards W:H2 N:HA]
ThirdHand 9  | [showcards W:S5] => [showcards W:S5 N:S2]
ThirdHand 10 | [showcards W:H5] => [showcards W:H5 N:H8]
ThirdHand 11 | [showcards W:HQ] => [showcards W:HQ N:H6]
ThirdHand 13 | [showcards W:H8] => [showcards W:H8 N:HJ]
ThirdHand 14 | [showcards W:C9] => [showcards W:C9 N:CT]
ThirdHand 15 | [showcards W:HT] => [showcards W:HT N:HJ]
ThirdHand 16 | [showcards W:SQ] => [showcards W:SQ N:S2]
ThirdHand 17 | [showcards W:S9] => [showcards W:S9 N:S6]
ThirdHand 18 | [showcards W:CK] => [showcards W:CK N:C2]
ThirdHand 19 | [showcards W:CK] => [showcards W:CK N:C7]
ThirdHand 20 | [showcards W:DK] => [showcards W:DK N:D2]
SecondHand 1  | [showcards W:SJ] => [showcards N:D5]
SecondHand 5  | [showcards S:H4 W:H9] => [showcards N:S4]
SecondHand 13 | [showcards W:HT S:H4] => [showcards N:C3]
Signals 1  | [showcards W:SK E:S7 S:S5] => [showcards W:SK E:S7 S:S5 N:S3]
Signals 2  | [showcards W:SK E:S7 S:S8] => [showcards W:SK E:S7 S:S8 N:S3]
Signals 3  | [showcards W:CA] => [showcards W:CA N:C4]
Signals 5  | [showcards W:CA] => [showcards W:CA N:C2]
Signals 9  | [showcards W:H5] => [showcards W:H5 N:HT]
Signals 11 | [showcards W:DA] => [showcards W:DA N:D3]
Signals 12 | [showcards W:HA E:HQ S:H5] => [showcards W:HA E:HQ S:H5 N:H6]
Signals 13 | [showcards W:DA] => [showcards W:DA N:D2]
Signals 16 | [showcards W:CK] => [showcards W:CK N:CJ]
Signals 20 | [showcards W:CA E:C2 S:C9] => [showcards W:CA E:C2 S:C9 N:C4]

## B. Multi-trick — [PLAY] completed tricks + [showcards] current trick (23)

Signals 4  | [showcards W:D5 E:DQ,D7,D3 S:D6,DT,DA,CQ] => [PLAY W:D5,N:D4,E:DQ,S:D6,E:D7,S:DT,W:DJ,N:D8,W:DK,N:H2,E:D3,S:DA] [showcards S:CQ]
Signals 6  | [showcards W:SA E:S9,S3 S:S5,S8] => [PLAY W:SA,N:S2,E:S9,S:S5,W:SQ,N:S4,E:S3,S:S8]
Signals 7  | [showcards S:HA,DJ W:HQ,D2] => [PLAY W:HQ,N:H2,E:H3,S:HA] [showcards S:DJ W:D2 N:D4]
Signals 8  | [showcards W:H4 E:S2,HJ S:SJ,ST,HA] => [PLAY W:H4,N:H7,E:HJ,S:HA,S:SJ,W:S5,N:S3,E:S2] [showcards S:ST]
Signals 10 | [showcards W:H4 E:HA,H3 S:H8,H5] => [PLAY W:H4,N:H2,E:HA,S:H8,E:H3,S:H5,W:S3,N:HJ]
Signals 14 | [showcards W:S5 S:SK] => [PLAY W:S5,N:S7,E:ST,S:SK] [showcards S:CT]
Signals 15 | [showcards S:S8,S5 W:SA,SQ,SK] => [PLAY W:SA,N:S2,E:ST,S:S5,W:SQ,N:S6,E:S4,S:S8] [showcards W:SK N:S9]
Signals 17 | [showcards W:CA S:C5 W:DA,CA] => [PLAY W:CA,N:C2,E:C3,S:C5] [showcards W:DA N:D3]
Signals 18 | [showcards S:HA,DA,DJ,CQ W:H5,D2,D6,C4] => [PLAY W:H5,N:H4,E:HJ,S:HA,S:DA,W:D2,N:D3,E:D5,S:DJ,W:D6,N:D8,E:D7] [showcards S:CQ]
SecondHand 2  | [showcards W:CJ E:C2 S:H2,CA] => [showcards S:H2]     # board already has a post-decision [PLAY E:C2]; dummy plays after West here, so just show South's ♥2 lead
SecondHand 3  | [showcards W:CK S:DJ,CJ,C8,C6 W:D2,CK,CQ,C5] => [PLAY W:CK,N:C2,E:C9,S:C6,W:CQ,N:C4,E:C3,S:C8,W:C5,N:CT,E:CA,S:CJ,E:DT,S:DJ,W:D2,N:DK] [showcards N:HJ]
SecondHand 4  | [showcards W:HJ E:HA,HK,H2 S:S4,S2,H9,H4] => [PLAY W:HJ,N:HQ,E:HK,S:H9,E:HA,S:H4,W:H5,N:H3,E:H2,S:S2,W:H8,N:H6] [showcards S:S4]
SecondHand 6  | [showcards W:ST E:S3 S:SA,C3] => [PLAY W:ST,N:S5,E:S3,S:SA] [showcards S:C3]
SecondHand 8  | [showcards W:D5 S:DK,C9] => [PLAY W:D5,N:D3,E:DT,S:DK] [showcards S:C9]
SecondHand 9  | [showcards W:H4 S:S6,H8 W:S2,H4] => [PLAY W:H4,N:H7,E:H2,S:H8,S:S6,W:S2,N:SK,E:S3] [showcards N:DT]
SecondHand 10 | [showcards W:S7 E:S2 S:SQ,C6] => [PLAY W:S7,N:S3,E:S2,S:SQ] [showcards S:C6]
SecondHand 11 | [showcards W:DQ S:S4,DA W:S2,DQ] => [PLAY W:DQ,N:D2,E:D8,S:DA,S:S4,W:S2,N:SK,E:S7] [showcards N:S6]
SecondHand 12 | [showcards W:CK E:S4,C5,C3 S:H4,CA,C6,C2] => [PLAY W:CK,N:C4,E:C5,S:C6,W:CJ,N:C9,E:C3,S:C2,W:CQ,N:CT,E:S4,S:CA] [showcards S:H4]
SecondHand 14 | [showcards W:SJ E:S3,H7,H4 S:S5,HA,H2,C2] => [PLAY W:SJ,N:SK,E:S3,S:S5,N:HK,E:H7,S:H2,W:D8,N:H3,E:H4,S:HA,W:S6] [showcards S:C2]
SecondHand 15 | [showcards S:SQ,SJ,C3 W:S6,S2,C6] => [PLAY W:S6,N:S4,E:SA,S:SJ,E:S9,S:SQ,W:S2,N:S5,S:C3,W:C6,N:CA,E:C8] [showcards N:D2]
SecondHand 17 | [showcards S:SA,C2 W:SK] => [PLAY W:SK,N:S2,E:S3,S:SA,S:C2,W:C3,N:CA,E:C4] [showcards N:HJ]
SecondHand 19 | [showcards W:H3 S:HA,H2 W:H7,H3] => [PLAY W:H3,N:H6,E:HT,S:HA,S:H2,W:H7,N:HJ,E:H4] [showcards N:S6]
ThirdHand 12 | [showcards W:SA,SK] => [PLAY W:SA,N:S3,E:ST,S:S2] [showcards W:SK N:SJ]
