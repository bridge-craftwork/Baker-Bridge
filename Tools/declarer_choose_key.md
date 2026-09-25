# Declarer-play choose-card key

Turns the declarer-play lessons' key decisions into `[choose-card]` steps, so the boards
record progress in Bridge Classroom (a board with only `[NEXT]` steps records nothing).
`apply_declarer_choose.py` applies this key to `pbns/*.pbn` every build, right after
`apply_showcards_dummy.py`, then replays each keyed board's directives and fails the build
if a choice isn't a legal play from the position the directives set up.

## How an entry is written

Each board is a `## <Lesson> <Board>` heading followed by one or more replacements:

    <<<
    exact text from the board's commentary (must occur exactly once in the board)
    ===
    replacement text
    >>>

Keep FROM snippets short (one line where possible) so they don't depend on the build's
blank-line runs.

## Authoring rules

- **Ask the lesson's decisions, not every card.** A choice goes where Baker's prose teaches
  a play (the hold-up, the unblock, the squeeze discard), before the prose that gives the
  answer away. Routine plays stay narrated.
- **The answer card names the hand.** A choice is answered from whichever hand holds the
  card, so a dummy play is just `[choose-card S6]`. Every card of an `any:` list must be
  in that one hand.
- **Set up the trick.** Before a choice, the current trick's earlier cards go on the table
  with `[showcards]`, and every earlier trick is gathered with `[PLAY]` (all four cards,
  defenders included — pick sensible defender cards where the prose doesn't say).
- **Never name the student's chosen card in a later `[PLAY]`.** The app keeps a chosen
  card played: it stays in the trick until the next `[PLAY]` gathers it, and is struck from
  then on (a wrong choice is gathered as the first expected card). With an `any:` list only
  the app knows which card that was.
- **Don't ask a choice whose card a later `[PLAY]` depends on.** If later tricks name
  specific cards from an `any:` group, one of them may already be gone.

---

## Entries 2

Overtake dummy's ♦9 with the ♦A at trick 1 to keep ♦QJ as entries.

<<<
South is to play 3NT. West leads the \D5. You play the \D9 from dummy and East plays the \D4.
===
[showcards W:D5 N:D9 E:D4] South is to play 3NT. West leads the \D5. You play the \D9 from dummy and East plays the \D4.
>>>

<<<
Click [NEXT]
===
Which card do you play to this first trick? [choose-card DA]
>>>

## Holdup 2

Hold up dummy's ♠A until the third round.

<<<
South is to play 3NT. West leads the \SK.
===
[showcards W:SK] South is to play 3NT. West leads the \SK.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:S7,S6]
>>>

<<<
Winners:   \S = 1
===
[showcards E:S3 S:S2] East follows with the \S3 and you play the \S2.

Winners:   \S = 1
>>>

<<<
[PLAY N:SA,N:S7,N:S6,S:S8,S:S2,S:C3]
===
[PLAY W:SK,E:S3,S:S2] [showcards W:SQ]

West continues with the \SQ. Which card do you play from dummy? [choose-card any:S7,S6]

[PLAY W:SQ,E:S4,S:S8] [showcards W:SJ]

East follows with the \S4 and you play the \S8. West continues with the \SJ. Which card do you play from dummy? [choose-card SA]

[PLAY W:SJ,E:S9,S:C3]

East follows with the \S9 and you discard the \C3.
>>>

## Squeeze 2

Lead the squeeze card (♣A), then discard dummy's ♥Q once West has thrown a diamond.

<<<
On the \SK you discarded dummy's small \H and West also discarded a \H.
===
On the \SK you discarded dummy's small \H and West also discarded a \H. Which card do you lead now? [choose-card CA]
>>>

<<<
But now you play the SQUEEZE card, the \CA. West absolutely cannot throw away his \HA, so he discards a \D instead.
===
[showcards W:D3] The \CA is the SQUEEZE card. West absolutely cannot throw away his \HA, so he discards a \D instead. Which card do you discard from dummy? [choose-card HQ]
>>>

<<<
Since he still has the \HA you know dummy's \HQ is useless so you discard it. Dummy's fourth \D has become a winner. [NEXT]
===
[showcards E:H9] Since he still has the \HA you know dummy's \HQ is useless, so you discard it; East throws the \H9. Dummy's fourth \D has become a winner. [NEXT]
>>>

## Holdup 1

Hold up the ♦A until the third round.

<<<
South is to play 3NT. West leads the \DK.
===
[showcards W:DK N:D2 E:D4] South is to play 3NT. West leads the \DK, dummy plays the \D2 and East the \D4.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:D8,D3]
>>>

<<<
[PLAY N:D6,N:D2,N:C3,S:DA,S:D8,S:D3]
===
[PLAY W:DK,N:D2,E:D4] [showcards W:DQ N:D6 E:D7]

West continues with the \DQ; dummy plays the \D6 and East the \D7. Which card do you play? [choose-card any:D8,D3]

[PLAY W:DQ,N:D6,E:D7] [showcards W:DJ N:C3 E:D9]

West continues with the \DJ; dummy discards the \C3 and East plays the \D9. Which card do you play? [choose-card DA]

[PLAY W:DJ,N:C3,E:D9]
>>>

## Holdup 3

Duck the second spade (♠9), win the third with the ♠K.

<<<
South is to play 3NT. West leads the \S3. East wins the first trick with the \SA and returns the \S8.
===
[PLAY W:S3,N:S5,E:SA,S:S4] [showcards E:S8] South is to play 3NT. West leads the \S3. East wins the first trick with the \SA and returns the \S8.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card S9]
>>>

<<<
Winners:   \S = 1
===
[showcards W:SQ N:ST] West plays the \SQ and dummy the \S10.

Winners:   \S = 1
>>>

<<<
[PLAY N:ST,N:S5,N:H4,S:SK,S:S9,S:S4]
===
[PLAY E:S8,W:SQ,N:ST] [showcards W:SJ N:H4 E:S6]

West continues with the \SJ; dummy discards a \H and East plays the \S6. Which card do you play? [choose-card SK]

[PLAY W:SJ,N:H4,E:S6]
>>>

## Holdup 4

Hold up the ♦A until the third round.

<<<
South is to play 3NT. West leads the \DK.
===
[showcards W:DK N:D2 E:D6] South is to play 3NT. West leads the \DK, dummy plays the \D2 and East the \D6.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:D8,D3]
>>>

<<<
[PLAY N:D7,N:D5,N:D2,S:DA,S:D8,S:D3]
===
[PLAY W:DK,N:D2,E:D6] [showcards W:DQ N:D5 E:D9]

West continues with the \DQ; dummy plays the \D5 and East the \D9. Which card do you play? [choose-card any:D8,D3]

[PLAY W:DQ,N:D5,E:D9] [showcards W:DJ N:D7 E:DT]

West continues with the \DJ; dummy plays the \D7 and East the \D10. Which card do you play? [choose-card DA]

[PLAY W:DJ,N:D7,E:DT]
>>>

## Holdup 5

Hold up: duck the first heart.

<<<
South is to play 3NT. West leads the \H6. East plays the \HJ.
===
[showcards W:H6 N:H3 E:HJ] South is to play 3NT. West leads the \H6, dummy plays the \H3 and East the \HJ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card H2]
>>>

<<<
[PLAY N:H7,N:H5,N:H3,S:HK,S:HQ,S:H2]
===
[PLAY W:H6,N:H3,E:HJ,E:H9,S:HQ,W:HA,N:H5,W:HT,N:H7,E:C4,S:HK]
>>>

## Holdup 6

Don't hold up: win the first heart (the ♥K, keeping West guessing about the ♥Q).

<<<
South is to play 3NT. West leads the \H6. East plays the \HJ.
===
[showcards W:H6 N:H3 E:HJ] South is to play 3NT. West leads the \H6, dummy plays the \H3 and East the \HJ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:HK,HQ]
>>>

<<<
[PLAY N:SJ,N:H3,N:DA,S:S2,S:HK,S:D4]
===
[PLAY W:H6,N:H3,E:HJ,S:D4,W:D3,N:DA,E:D2,N:SJ,E:S5,S:S2,W:SK]
>>>

## Holdup 7

Don't hold up: win the first heart.

<<<
South is to play 3NT. West leads the \H4. East plays the \H10.
===
[showcards W:H4 N:H3 E:HT] South is to play 3NT. West leads the \H4, dummy plays the \H3 and East the \H10.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card HA]
>>>

## Holdup 8

Let East's ♣K hold (duck with the ♣J) so West never gets the lead.

<<<
South is to play 4\S. West leads the \C2. East plays the \CK.
===
[showcards W:C2 N:C5 E:CK] South is to play 4\S. West leads the \C2, dummy plays the \C5 and East the \CK.
>>>

<<<
Having gone through that thought process what is your Plan?

Click NEXT. [NEXT]
===
Having gone through that thought process what is your Plan? Play a card from your hand. [choose-card CJ]
>>>

<<<
[PLAY N:C9,N:C5,S:CA,S:CJ]
===
[PLAY W:C2,N:C5,E:CK,E:C3,S:CA,W:C4,N:C9]
>>>

## Holdup 9

Duck the first heart, play low again on the second and win it with dummy's ♥K.

<<<
South is to play 3NT. West leads the \H7. East plays the \H10.
===
[showcards W:H7 N:H8 E:HT] South is to play 3NT. West leads the \H7, dummy plays the \H8 and East the \H10.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:H5,H9]
>>>

<<<
[PLAY N:HK,N:H8,S:H9,S:H5]
===
[PLAY W:H7,N:H8,E:HT] [showcards E:HQ]

East continues with the \HQ. Which card do you play? [choose-card any:H9,H5]

[showcards W:H3]

West follows with the \H3. Which card do you play from dummy? [choose-card HK]

[PLAY E:HQ,W:H3]
>>>

<<<
[PLAY N:DK,N:D6,N:D5,S:DJ,S:D9,S:D2]
===
[PLAY N:DK,E:D3,S:D2,W:D4,N:D6,E:D7,S:DJ,W:D8,S:D9,W:DA,N:D5,E:C2]
>>>

The endgame, rebuilt trick by trick from the deal in place of the old eight-card
[showcards]: the ♣A, the last diamond and the spade to East's ♠A are gathered, then East
leads a heart to South's ♥A.

<<<
[showcards N:ST,S6,C8,C7 S:SK,SJ,CK,CT]
===
[PLAY W:CQ,N:C3,E:C4,S:CA,S:DT,W:S2,N:DQ,E:H2,N:SQ,E:SA,S:S7,W:S4] [showcards E:H4]
>>>

<<<
[PLAY N:SQ,N:DQ,N:C5,N:C3,S:S7,S:HA,S:DT,S:CA]
===
[clear-commentary]
>>>

<<<
East glares at you, (because you still have the \HA), and plays another \H to your Ace. You take your 3 tricks and let West have the last \C.
===
East glares at you, (because you still have the \HA), and plays another \H. Which card do you play? [choose-card HA]

[showcards W:S5 N:C5] You take your 3 tricks and let West have the last \C.
>>>

## Holdup 10

Bath coup: duck the ♥K, playing the ♥7 (not the ♥3).

<<<
South is to play 3NT. West leads the \HK. East plays the \H6.
===
[showcards W:HK N:H2 E:H6] South is to play 3NT. West leads the \HK, dummy plays the \H2 and East the \H6.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card H7]
>>>

## Holdup 11

Don't hold up: win the ♥A.

<<<
South is to play 3NT. West leads the \HJ. You try dummy's \HQ but East plays the \HK.
===
[showcards W:HJ N:HQ E:HK] South is to play 3NT. West leads the \HJ. You try dummy's \HQ but East plays the \HK.
>>>

<<<
First problem: Do you hold up the \HA or not?

Click NEXT. [NEXT]
===
First problem: Do you hold up the \HA or not? Play a card from your hand. [choose-card HA]
>>>

## Holdup 12

Hold up twice, win the third heart; later, with dummy leading a club, play the ♣K. The
end position is rebuilt trick by trick from the deal (the source crammed it into one
eight-card [showcards]).

<<<
South is to play 3NT. West leads the \H6. East plays the \HQ.
===
[showcards W:H6 N:H5 E:HQ] South is to play 3NT. West leads the \H6, dummy plays the \H5 and East the \HQ.
>>>

<<<
Make a Plan, then click . [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:H7,H2]
>>>

<<<
[PLAY N:H8,N:H5,N:C2,S:HA,S:H7,S:H2]
===
[PLAY W:H6,N:H5,E:HQ] [showcards E:HT]

East returns the \H10. Which card do you play? [choose-card any:H7,H2]

[PLAY E:HT,W:HJ,N:H8] [showcards W:H3 N:C2 E:H4]

West wins with the \HJ and continues with the \H3; dummy discards a \C and East plays the \H4. Which card do you play? [choose-card HA]

[PLAY W:H3,N:C2,E:H4]
>>>

<<<
[showcards N:S7,C7,C5,C4 S:SK,CK,CJ,C6]
===
[clear-commentary] [showcards N:C4 E:C3]
>>>

<<<
[PLAY N:SQ,N:S4,N:DK,N:DJ,N:DT,N:D3,S:SA,S:S5,S:DA,S:DQ,S:D6,S:D5]
===
[PLAY S:DA,W:D2,N:D3,E:D7,S:DQ,W:D4,N:DT,E:D9,S:D5,W:D8,N:DK,E:S2,N:DJ,E:S8,S:D6,W:S9,N:S4,E:ST,S:SA,W:S3,S:S5,W:S6,N:SQ,E:SJ]
>>>

<<<
This is not a guess.
===
[choose-card CK]

This is not a guess.
>>>

## Holdup 13

Duck the first diamond (♦8) to West, the safe hand.

<<<
South is to play 4\S. West leads the \DQ. East plays the \D9.
===
[showcards W:DQ N:D3 E:D9] South is to play 4\S. West leads the \DQ, dummy plays the \D3 and East the \D9.
>>>

<<<
Make a Plan, then click . [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card D8]
>>>

<<<
[PLAY N:D5,N:D3,S:DA,S:D8]
===
[PLAY W:DQ,N:D3,E:D9,W:DJ,N:D5,E:D2,S:DA]
>>>

## Holdup 14

Bath coup: duck the ♥K, playing the ♥7 to hide the ♥4.

<<<
South is to play 3NT. West leads the \HK.
===
[showcards W:HK N:H2 E:H6] South is to play 3NT. West leads the \HK, dummy plays the \H2 and East the \H6.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card H7]
>>>

## Holdup 15

Don't duck: go up with dummy's ♠A to block the spades.

<<<
South is to play 3NT. West leads the \S7.
===
[showcards W:S7] South is to play 3NT. West leads the \S7.
>>>

<<<
So what is the best approach, hold up or not hold up?

Click NEXT. [NEXT]
===
So what is the best approach, hold up or not hold up? Choose dummy's card to this trick. [choose-card SA]
>>>
