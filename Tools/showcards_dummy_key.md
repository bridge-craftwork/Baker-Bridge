# showcards dummy-card key

Answer key for the defense-lesson `[showcards]` dummy-card fix (companion to #11/#12;
under-specified remainder tracked in #13). Each entry maps a board's current
`[showcards]` directive to the corrected one. A build step applies these to the
generated PBNs (durable across regen). **dummy-only** policy: add North's cards; for
malformed originals (West listed twice) also consolidate/de-dup.

Format per line: `Lesson Board | FROM => TO`  ·  `#` = note/flag.

## A. Single-trick (32) — auto, verified in North's hand

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
Signals 15 | [showcards S:S8,S5 W:SA,SQ,SK] => [showcards S:S8,S5 W:SA,SQ,SK N:S2]
Signals 20 | [showcards W:CA E:C2 S:C9] => [showcards W:CA E:C2 S:C9 N:C4]

## B. Multi-trick, clean dummy-add (15) — reconstructed & confirmed

Signals 4  | [showcards W:D5 E:DQ,D7,D3 S:D6,DT,DA,CQ] => [showcards W:D5 N:D4,D8,H2 E:DQ,D7,D3 S:D6,DT,DA,CQ]
Signals 6  | [showcards W:SA E:S9,S3 S:S5,S8] => [showcards W:SA N:S2,S4 E:S9,S3 S:S5,S8]
Signals 7  | [showcards S:HA,DJ W:HQ,D2] => [showcards S:HA,DJ W:HQ,D2 N:H2,D4]
Signals 8  | [showcards W:H4 E:S2,HJ S:SJ,ST,HA] => [showcards W:H4 N:H7,S3 E:S2,HJ S:SJ,ST,HA]
Signals 10 | [showcards W:H4 E:HA,H3 S:H8,H5] => [showcards W:H4 N:H2,HJ E:HA,H3 S:H8,H5]
Signals 16 | [showcards W:CK] => [showcards W:CK N:CJ]
Signals 18 | [showcards S:HA,DA,DJ,CQ W:H5,D2,D6,C4] => [showcards S:HA,DA,DJ,CQ W:H5,D2,D6,C4 N:H4,D3,D8,C3]
SecondHand 2  | [showcards W:CJ E:C2 S:H2,CA] => [showcards W:CJ N:C7 E:C2 S:H2,CA]
SecondHand 4  | [showcards W:HJ E:HA,HK,H2 S:S4,S2,H9,H4] => [showcards W:HJ N:HQ,H3,H6 E:HA,HK,H2 S:S4,S2,H9,H4]
SecondHand 6  | [showcards W:ST E:S3 S:SA,C3] => [showcards W:ST N:S5 E:S3 S:SA,C3]
SecondHand 8  | [showcards W:D5 S:DK,C9] => [showcards W:D5 N:D3 S:DK,C9]
SecondHand 10 | [showcards W:S7 E:S2 S:SQ,C6] => [showcards W:S7 N:S3 E:S2 S:SQ,C6]
SecondHand 12 | [showcards W:CK E:S4,C5,C3 S:H4,CA,C6,C2] => [showcards W:CK N:C4,C9,CT E:S4,C5,C3 S:H4,CA,C6,C2]
SecondHand 14 | [showcards W:SJ E:S3,H7,H4 S:S5,HA,H2,C2] => [showcards W:SJ N:SK,HK,H3 E:S3,H7,H4 S:S5,HA,H2,C2]
SecondHand 17 | [showcards S:SA,C2 W:SK] => [showcards S:SA,C2 W:SK N:S2,CA,HJ]
ThirdHand 12 | [showcards W:SA,SK] => [showcards W:SA,SK N:S3,SJ]

## C. Multi-trick REBUILD — original malformed (West listed twice); consolidated + dummy (4) — please confirm

Signals 17 | [showcards W:CA S:C5 W:DA,CA] => [showcards W:CA,DA N:C2,D3 S:C5]     # dropped dup ♣A; East's ♣3 left out (dummy-only)
SecondHand 9  | [showcards W:H4 S:S6,H8 W:S2,H4] => [showcards W:H4,S2 N:H7,SK,DT S:S6,H8]     # dummy: ♥7 low, ♠K entry(won), ♦T led
SecondHand 11 | [showcards W:DQ S:S4,DA W:S2,DQ] => [showcards W:DQ,S2 N:D2,SK,S6 S:S4,DA]     # dummy: ♦2 low, ♠K(won), ♠6 led
SecondHand 19 | [showcards W:H3 S:HA,H2 W:H7,H3] => [showcards W:H3,H7 N:H6,HQ,S6 S:HA,H2]     # dummy: ♥6 low, ♥Q(won), ♠6 led(singleton)

## D. Multi-trick REBUILD — full reconstruction from your play-by-play (verified vs deal)

# Signals 14: T1 ♠ W♠5 · N♠7(singleton) · E♠T(3rd-hand-high) · S♠K(won); T2 S leads ♣T, West (void ♣) discards.
Signals 14 | [showcards W:S5 S:SK] => [showcards W:S5 N:S7 E:ST S:SK,CT]
# SecondHand 3: T1 ♣K,2,9,6 · T2 ♣Q,4,3,8 · T3 ♣5,T,A,J · T4 ♦T,J,2,K(dummy wins) · T5 dummy leads ♥J.
SecondHand 3  | [showcards W:CK S:DJ,CJ,C8,C6 W:D2,CK,CQ,C5] => [showcards W:CK,CQ,C5,D2 N:C2,C4,CT,DK,HJ E:C9,C3,CA,DT S:C6,C8,CJ,DJ]
# SecondHand 15: T1 ♠6,4,A,J · T2 ♠9,Q,?,5 (West's T2 spade = ??) · T3 ♣3,9,A,8 · T4 dummy leads ♦2.
SecondHand 15 | [showcards S:SQ,SJ,C3 W:S6,S2,C6] => [showcards W:S6,S2 N:S4,S5,CA,D2 E:SA,S9,C8 S:SJ,SQ,C3]     # West T2 = ♠2 (count: 6 was 4th-best from 5)
