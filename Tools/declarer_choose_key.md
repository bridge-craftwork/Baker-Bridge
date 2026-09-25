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

## Finesse 1

Win the ♥ lead, then lead small spades toward dummy's ♠Q and ♠K.

<<<
South is to play 3NT. West leads the \HQ.
===
[showcards W:HQ N:H4 E:H2] South is to play 3NT. West leads the \HQ, dummy plays the \H4 and East the \H2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:HK,HA]
>>>

<<<
It holds the trick.

Click NEXT. [NEXT]

[PLAY N:SQ,N:H4,S:S4,S:HK]
===
Click NEXT. [NEXT]

[PLAY W:HQ,N:H4,E:H2]

Which card do you lead? [choose-card any:S8,S6,S4]

[showcards W:S2 N:SQ E:S5]

West plays low and dummy's \SQ holds the trick.
>>>

<<<
This also wins.

Click NEXT. [NEXT]

[PLAY N:SK,N:DA,N:DQ,N:D7,N:D3,S:S6,S:DK,S:DJ,S:DT,S:D2]
===
Click NEXT. [NEXT]

[PLAY W:S2,N:SQ,E:S5,N:D3,E:D4,S:DK,W:D5,S:D2,W:D9,N:DA,E:D6,N:DQ,E:D8,S:DT,W:H8,N:D7,E:C5,S:DJ,W:C3]

You are back in your hand after four \D tricks. Which card do you lead? [choose-card any:S8,S6,S4]

[showcards W:S7 N:SK E:S9]

West plays low again and dummy's \SK wins.
>>>

## Finesse 2

Win the ♦A at once, run the hearts, then finesse the ♠Q.

<<<
South is to play 3NT. West leads the \D3.
===
[showcards W:D3] South is to play 3NT. West leads the \D3.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card DA]
>>>

<<<
Winners:   \S = 1
===
[showcards E:DT S:D2] East plays the \D10 and you the \D2.

Winners:   \S = 1
>>>

<<<
[PLAY N:HA,N:HK,N:HQ,N:HJ,N:H4,N:DA,S:S7,S:HT,S:H6,S:D2,S:C4,S:C3]
===
[PLAY W:D3,E:DT,S:D2,N:HA,E:H3,S:H6,W:H2,N:HK,E:H5,S:HT,W:H8,N:HQ,E:H7,S:S7,W:H9,N:HJ,E:C5,S:C4,W:C7,N:H4,E:CT,S:C3,W:C9]
>>>

<<<
You can't put it off any longer so play a small \S from dummy and put the \SQ on.
===
You can't put it off any longer. Which card do you lead from dummy? [choose-card any:S9,S8,S6]

[showcards E:S2]

East plays low. Which card do you play? [choose-card SQ]

[showcards W:S3]

A small \S from dummy, putting the \SQ on.
>>>

## Finesse 3

Win the ♥, cash the clubs ending in dummy, then lead toward the ♠K.

<<<
South is to play 3NT. West leads the \HQ.
===
[showcards W:HQ N:H2 E:H3] South is to play 3NT. West leads the \HQ, dummy plays the \H2 and East the \H3.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:HK,HA]
>>>

<<<
[PLAY N:H2,N:CK,N:CJ,N:C5,N:C2,S:HK,S:CA,S:CQ,S:C8,S:C7]
===
[PLAY W:HQ,N:H2,E:H3,S:CA,W:C3,N:C2,E:C4,S:CQ,W:C6,N:C5,E:C9,S:C8,W:CT,N:CJ,E:D2,N:CK,E:H5,S:C7,W:D4]
>>>

<<<
The moment of truth. You lead a small \S from dummy. East plays low and you play the \SK.
===
The moment of truth. Which card do you lead from dummy? [choose-card any:S6,S5,S3]

[showcards E:S4]

East plays low. Which card do you play? [choose-card SK]

[showcards W:SA]

A small \S from dummy, and the \SK when East plays low.
>>>

## Finesse 4

Win the ♠A, lead the singleton ♦ to the ♦Q, discard a spade on the ♦A.

<<<
South is to play 4\H. West leads the \SK.
===
[showcards W:SK N:S2 E:S5] South is to play 4\H. West leads the \SK, dummy plays the \S2 and East the \S5.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card SA]
>>>

<<<
So win the \SA, lead your singleton \D and finesse the \DQ. Your luck has returned, the \DQ wins and you discard one of your \S losers on the \DA.
===
So win the \SA, lead your singleton \D and finesse the \DQ.

[PLAY W:SK,N:S2,E:S5]

Which card do you lead? [choose-card D8]

[showcards W:D5]

West plays low. Which card do you play from dummy? [choose-card DQ]

[showcards E:D2]

Your luck has returned, the \DQ wins. [NEXT]

[PLAY W:D5,E:D2] [showcards N:DA E:D3]

Dummy leads the \DA and East follows. Which card do you discard? [choose-card any:S7,S4]

[showcards W:D6]

You discard one of your \S losers on the \DA.
>>>

<<<
[PLAY N:S2,N:DA,N:DQ,S:SA,S:S4,S:D8]
===
[PLAY N:DA,E:D3,W:D6]
>>>

## Finesse 5

Run the spades and diamonds keeping both clubs; take the first club finesse; take the ♥A,
not the heart finesse. The old eight-card end-position [showcards] is rebuilt trick by trick.

<<<
[showcards N:H9,CA,CJ,CT S:HA,HQ,C8,C3]
===
[PLAY W:S3,N:SJ,E:S4,S:S5,N:SQ,E:S6,S:S9,W:S7,N:SA,E:H4,S:H2,W:S8,N:S2,E:H5,S:SK,W:ST,S:D7,W:D2,N:DA,E:D3,N:DK,E:D4,S:D8,W:D6,N:D5,E:D9,S:DQ,W:H3,S:DJ,W:C4,N:H7,E:HT,S:DT,W:C9,N:H6,E:C2]
>>>

<<<
[PLAY N:SA,N:SQ,N:SJ,N:S2,N:H7,N:H6,N:DA,N:DK,N:D5,S:SK,S:S9,S:S5,S:H2,S:DQ,S:DJ,S:DT,S:D8,S:D7]
===
You have run the \Ss and \Ds and are in your hand. Which card do you lead? [choose-card any:C8,C3]

[showcards W:C6]

West plays low. Which card do you play from dummy? [choose-card CT]

[showcards E:CK]
>>>

<<<
Lead a small \C and play the \CT if West plays low. Let's say East wins the \CK and returns a \H.
===
A small \C, playing the \C10 when West plays low: the first of your two \C finesses. Let's say East wins the \CK and returns a \H.
>>>

<<<
[showcards N:H9,CA,CJ S:HA,HQ,C8]
===
[PLAY W:C6,E:CK] [showcards E:HJ]
>>>

<<<
[PLAY N:CT,S:C3]
===
East returns the \HJ. Which card do you play? [choose-card HA]

[showcards W:H8 N:H9]
>>>

## Finesse 6

Duck the first diamond, win the second in dummy, then take the club finesse.

<<<
South is to play 4\S. West leads the \DK.
===
[showcards W:DK] South is to play 4\S. West leads the \DK.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:D6,D5,D3]
>>>

<<<
Losers:   \S = 1
===
[showcards E:D2 S:D4] East plays the \D2 and you the \D4.

Losers:   \S = 1
>>>

<<<
But he doesn't, he continues with the \DQ which you take with dummy's \DA.

Click NEXT. [NEXT]

[PLAY N:DA,N:D3,S:D8,S:D4]
===
But he doesn't. [NEXT]

[PLAY W:DK,E:D2,S:D4] [showcards W:DQ]

West continues with the \DQ. Which card do you play from dummy? [choose-card DA]

[showcards E:D9 S:D8]

You take it with dummy's \DA. [NEXT]

[PLAY W:DQ,E:D9,S:D8]
>>>

<<<
You need to try a finesse right now, but which one?
===
You need to try a finesse right now, but which one? Which card do you lead from dummy? [choose-card any:CJ,CT,C9,C5]
>>>

## Finesse 7

Win the ♥A, draw trumps, cross to the ♣A, then lead the ♣Q for a ruffing finesse.

<<<
South is to play 6\S. West leads the \HK.
===
[showcards W:HK N:H6 E:H3] South is to play 6\S. West leads the \HK, dummy plays the \H6 and East the \H3.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card HA]
>>>

<<<
[PLAY N:S7,N:S3,N:H6,S:SK,S:SQ,S:HA]
===
[PLAY W:HK,N:H6,E:H3,S:SK,W:S2,N:S3,E:H7,S:SQ,W:ST,N:S7,E:D4]
>>>

<<<
Next play your \C7 to dummy's \CA. Then lead the \CQ from dummy.
===
Which card do you lead now? [choose-card C7]

[showcards W:C3]

West plays low. Which card do you play from dummy? [choose-card CA]

[showcards E:C2]

Your \C7 to dummy's \CA. [NEXT]

[PLAY W:C3,E:C2]

Which card do you lead from dummy? [choose-card CQ]

The \CQ from dummy: a ruffing finesse.
>>>

## Finesse 8

Hold up the ♦A, cash the clubs ending in hand, then lead the ♥J.

<<<
South is to play 3NT. West leads the \DK.
===
[showcards W:DK N:D3 E:D2] South is to play 3NT. West leads the \DK, dummy plays the \D3 and East the \D2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:DT,D4]
>>>

<<<
[PLAY N:D7,N:D6,N:D3,N:CA,N:CK,N:C6,N:C5,S:DA,S:DT,S:D4,S:CQ,S:CJ,S:C9,S:C2]
===
[PLAY W:DK,N:D3,E:D2] [showcards W:DQ N:D6 E:D8]

West continues with the \DQ; dummy plays the \D6 and East the \D8. Which card do you play? [choose-card any:DT,D4]

[PLAY W:DQ,N:D6,E:D8] [showcards W:DJ N:D7 E:S6]

West continues with the \DJ; dummy plays the \D7 and East discards a \S. Which card do you play? [choose-card DA]

[PLAY W:DJ,N:D7,E:S6,S:C2,W:C4,N:CA,E:C3,N:CK,E:C7,S:C9,W:C8,N:C6,E:CT,S:CJ,W:D5,S:CQ,W:D9,N:C5,E:S7]

You cash four rounds of \Cs, ending in your hand. Which card do you lead now? [choose-card HJ]

[showcards W:HQ]

West covers with the \HQ. Which card do you play from dummy? [choose-card HA]

[showcards E:H2]
>>>

## Finesse 9

Lead a small spade and finesse the ♠J, playing West for the doubleton ♠K.

<<<
[PLAY N:HT,N:H9,N:H6,N:D5,S:H7,S:H4,S:H2,S:DK]
===
[PLAY W:H5,N:H6,E:HQ,S:H2,E:HA,S:H4,W:H8,N:H9,E:H3,S:H7,W:HK,N:HT,W:D4,N:D5,E:D2,S:DK]
>>>

<<<
Lead a small \S from your hand and when West plays low put on the \SJ. When this holds the trick plunk down the \SA and hope.
===
Which card do you lead? [choose-card any:S6,S5,S3]

[showcards W:S2]

West plays low. Which card do you play from dummy? [choose-card SJ]

[showcards E:S8]

A small \S from your hand, putting on the \SJ when West plays low. When this holds the trick plunk down the \SA and hope.
>>>

## Finesse 10

Win the trump switch in dummy and take the first club finesse at once; back in dummy with
the other trump honor, take the second.

<<<
South is to play 4\H. West leads the \DA. The defenders take two \D tricks, then switch to a trump.
===
[PLAY W:DA,N:D4,E:D2,S:DJ,W:DK,N:D5,E:D3,S:DQ] [showcards W:H3] South is to play 4\H. West leads the \DA. The defenders take two \D tricks, then switch to a trump.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:HQ,HA]
>>>

<<<
[PLAY N:HQ,N:D5,N:D4,S:H2,S:DQ,S:DJ]
===
[showcards E:H6 S:H2]
>>>

<<<
Play a small \C from dummy and play the \CT. West wins with the \CQ and plays another trump.
===
[PLAY W:H3,E:H6,S:H2]

Which card do you lead from dummy? [choose-card any:C8,C5,C3,C2]

[showcards E:C4]

East plays low. Which card do you play? [choose-card CT]

[showcards W:CQ]

A small \C from dummy to your \C10. West wins with the \CQ and plays another trump.
>>>

<<<
[PLAY N:HA,N:C2,S:H4,S:CT]
===
[PLAY E:C4,W:CQ] [showcards W:H5]

West leads the \H5. Which card do you play from dummy? [choose-card any:HA,HQ]
>>>

<<<
You play a small \C to your \CJ.
===
[PLAY W:H5,E:S3,S:H4]

Which card do you lead from dummy? [choose-card any:C8,C5,C3,C2]

[showcards E:C7]

East plays low. Which card do you play? [choose-card CJ]

[showcards W:C6]

A small \C to your \CJ.
>>>

## Finesse 11

Ruff, draw trumps, then lead a low heart toward dummy's ♥J before trying the spade finesse.

<<<
Ruff the opening \C lead, pull trumps with the \DK, (they split 1-1), and play a low \H toward the \HJ. West fidgets, then puts on the \HQ and plays another \C which you ruff.
===
[PLAY W:CK,N:C6,E:C3,S:D6,S:DK,W:D5,N:D2,E:D4]

You ruff the opening \C lead and pull trumps with the \DK (they split 1-1). Which card do you lead now? [choose-card any:H7,H5]

[showcards W:HQ N:H6 E:H8]

A low \H toward the \HJ. West fidgets, then puts on the \HQ and plays another \C which you ruff.
>>>

<<<
[PLAY N:H6,N:D2,N:C7,N:C6,S:H5,S:DK,S:D6,S:D3]
===
[PLAY W:HQ,N:H6,E:H8,W:CQ,N:C7,E:C5,S:D3]
>>>

## Finesse 12

After the spade and diamond winners, try to drop the ♣Q before the heart finesse.

<<<
[PLAY N:SK,N:SJ,N:S7,N:DA,N:DJ,N:DT,N:D8,N:C6,S:SA,S:SQ,S:S5,S:S3,S:DK,S:DQ,S:C7,S:C2]
===
[PLAY W:ST,N:S7,E:S4,S:SQ,S:DK,W:D3,N:D8,E:D2,S:DQ,W:D5,N:DT,E:D4,S:S3,W:S8,N:SK,E:S6,N:DA,E:D6,S:C2,W:D9,N:DJ,E:D7,S:C7,W:H3,N:SJ,E:H2,S:SA,W:S9,S:S5,W:S2,N:C6,E:H4]
>>>

<<<
Now play the \CA, then \CK, hoping the \CQ falls.
===
Which card do you play now? [choose-card CA]

[showcards W:C3 N:C9 E:C5]

The \CA, then the \CK, hoping the \CQ falls.
>>>

## Finesse 13

Win the first heart; finesse the ♠10, then lead toward the ♠Q.

<<<
South is to play 3NT. West leads the \H3.
===
[showcards W:H3 N:H4 E:HJ] South is to play 3NT. West leads the \H3, dummy plays the \H4 and East the \HJ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:HK,HA]
>>>

<<<
Having won the first \H trick in your hand, play a small \S and finesse the \ST. Suppose East wins the \SK and returns a \H. Take your \HA and play another \S, going up with the \SQ if West plays low.
===
[PLAY W:H3,N:H4,E:HJ]

Having won the first \H trick in your hand, which card do you lead? [choose-card any:S8,S7,S3]

[showcards W:S4]

West plays low. Which card do you play from dummy? [choose-card ST]

[showcards E:SK]

East wins the \SK. [NEXT]

[PLAY W:S4,E:SK] [showcards E:H9]

East returns a \H. Which card do you play? [choose-card any:HA,HK]

[PLAY E:H9,W:H7,N:H6]

West follows and dummy plays the \H6. Which card do you lead now? [choose-card any:S8,S7,S3]

[showcards W:SJ]

West plays the \SJ. Which card do you play from dummy? [choose-card SQ]

[showcards E:S6]

The \SQ wins the trick.
>>>

## Finesse 14

Cross to the ♥A, lead the ♠Q, then the ♠9 with the ♠8 under it, to pick up East's ♠K.

<<<
[PLAY N:D8,N:D6,N:D4,N:C3,S:DQ,S:D5,S:D3,S:CJ]
===
[PLAY W:D2,N:D4,E:DA,S:D3,E:DT,S:DQ,W:DK,N:D6,W:DJ,N:D8,E:D7,S:D5,W:C2,N:C3,E:C7,S:CJ]
>>>

<<<
In your hand with a \C you play over to dummy's \HA. Now lead the \SQ from dummy and when East plays low play the \SJ (or 10) from your hand.
===
You are in your hand, having won the \C switch. Which card do you lead? [choose-card H4]

[showcards W:H3]

West plays low. Which card do you play from dummy? [choose-card HA]

[showcards E:H2]

Over to dummy's \HA. [NEXT]

[PLAY W:H3,E:H2]

Which card do you lead from dummy? [choose-card SQ]

[showcards E:S3]

East plays low. Which card do you play? [choose-card any:SJ,ST]

[showcards W:S7]

The \SQ from dummy, and the \SJ (or 10) from your hand when East plays low.
>>>

<<<
[PLAY N:SQ,N:HA,S:ST,S:H4]
===
[PLAY E:S3,W:S7]
>>>

<<<
Play the \S9, and when East doesn't cover, play your \S8 under it.
===
Which card do you lead from dummy? [choose-card S9]

[showcards E:S4]

East doesn't cover. Which card do you play? [choose-card S8]

[showcards W:C4]

The \S9, playing your \S8 under it.
>>>

## Finesse 15

Test the diamonds (a small one to the ♦Q, then ♦K, ♦A) and cash the long one before any
club finesse.

<<<
[PLAY N:HT,N:H5,S:HK,S:H4]
===
[PLAY W:H7,N:H5,E:HA,S:H4,E:H2,S:HK,W:H3,N:HT]
>>>

<<<
You should test the \D suit by playing \DQ, \DK, \DA. Both defenders follow three times and your \D6 has become a winner, which you cash.
===
Which card do you lead? [choose-card any:D6,D5]

[showcards W:D4 N:DQ E:D3]

You test the \D suit: a small one to dummy's \DQ, then the \DK and \DA. [NEXT]

[PLAY W:D4,N:DQ,E:D3,N:D2,E:D8,S:DK,W:D9,S:DA,W:DJ,N:D7,E:DT]

Both defenders followed three times, so your last \D is a winner. Which card do you play? [choose-card any:D6,D5]

[showcards W:S4 N:C5 E:S2]

You cash it.
>>>

<<<
[PLAY N:DQ,N:D7,N:D2,N:C5,S:DA,S:DK,S:D6,S:D5]
===
[PLAY W:S4,N:C5,E:S2]
>>>

## Finesse 16

Win the heart, lead a small spade to the ♠A, then a small one back toward the ♠QJ.

<<<
South is to play 3NT. West leads the \HQ.
===
[showcards W:HQ N:H2 E:H6] South is to play 3NT. West leads the \HQ, dummy plays the \H2 and East the \H6.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:HA,HK]
>>>

<<<
[PLAY N:H2,S:HK]
===
[PLAY W:HQ,N:H2,E:H6]
>>>

<<<
You win the first \H and lead . . . which \S?
===
You won the first \H. Which card do you lead? [choose-card any:S7,S4]

[showcards W:S2]

West plays low. Which card do you play from dummy? [choose-card SA]

[showcards E:S9]

Which \S was right?
>>>

<<<
So play a \S to dummy's \SA and then a small \S back toward your \S Q J. Here East puts the \SK on and you are home-free.
===
So play a \S to dummy's \SA and then a small \S back toward your \S Q J. [NEXT]

[PLAY W:S2,E:S9]

Which card do you lead from dummy? [choose-card any:S6,S3]

[showcards E:SK]

East puts on the \SK. Which card do you play? [choose-card any:S7,S4]

[showcards W:S5]

You are home-free.
>>>

## Finesse 17

Enter dummy with a heart and lead toward the ♠Q.

<<<
[PLAY N:C9,N:C6,N:C3,S:CJ,S:C7,S:C4]
===
[PLAY W:CA,N:C3,E:C5,S:C4,W:CK,N:C6,E:S4,S:C7,W:C2,N:C9,E:H2,S:CJ]
>>>

<<<
So you should enter dummy with a \H and play a small \S toward your \SQ.
===
Which card do you lead? [choose-card H5]

[showcards W:H6]

West plays low. Which card do you play from dummy? [choose-card any:HJ,HA]

[showcards E:H4]

You enter dummy with a \H. [NEXT]

[PLAY W:H6,E:H4]

Which card do you lead from dummy? [choose-card any:S7,S5]

[showcards E:S8]

East plays low. Which card do you play? [choose-card SQ]

[showcards W:S2]

A small \S toward your \SQ.
>>>

## Finesse 18

Hold up the ♦A, cash the clubs ending in hand, lead the ♥J, then the backward finesse of the ♥9.

<<<
South is to play 3NT. West leads the \DK.
===
[showcards W:DK N:D3 E:D2] South is to play 3NT. West leads the \DK, dummy plays the \D3 and East the \D2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:DT,D4]
>>>

<<<
[PLAY N:D7,N:D6,N:D3,N:CA,N:CK,N:C6,N:C5,S:DA,S:DT,S:D4,S:CQ,S:CJ,S:C9,S:C2]
===
[PLAY W:DK,N:D3,E:D2] [showcards W:DQ N:D6 E:D8]

West continues with the \DQ; dummy plays the \D6 and East the \D8. Which card do you play? [choose-card any:DT,D4]

[PLAY W:DQ,N:D6,E:D8] [showcards W:DJ N:D7 E:S6]

West continues with the \DJ; dummy plays the \D7 and East discards a \S. Which card do you play? [choose-card DA]

[PLAY W:DJ,N:D7,E:S6,S:C2,W:C4,N:CA,E:C3,N:CK,E:C7,S:C9,W:C8,N:C6,E:CT,S:CJ,W:D5,S:CQ,W:D9,N:C5,E:S7]

You cash four rounds of \Cs, ending in your hand. Which card do you lead now? [choose-card HJ]

[showcards W:HQ]

West covers with the \HQ. Which card do you play from dummy? [choose-card HA]

[showcards E:H2]
>>>

<<<
Next play a small \H from dummy and finesse the \H9, hoping East has the \H10.
===
[PLAY W:HQ,E:H2]

Which card do you lead from dummy? [choose-card any:H8,H5]

[showcards E:H4]

East plays low. Which card do you play? [choose-card H9]

[showcards W:H3]

A small \H from dummy, finessing the \H9, hoping East has the \H10.
>>>

## Finesse 19

Hold up twice, win the third spade, then finesse the ♦10 into the safe hand.

<<<
South is to play 3NT. West leads the \S5, East plays the \SQ.
===
[showcards W:S5 N:S2 E:SQ] South is to play 3NT. West leads the \S5, dummy plays the \S2 and East the \SQ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:S7,S6]
>>>

<<<
[PLAY N:S2,S:S6]
===
[PLAY W:S5,N:S2,E:SQ] [showcards E:S8]
>>>

<<<
Do you hold up again?

Click NEXT. [NEXT]
===
Do you hold up again? Play a card from your hand. [choose-card any:S7,S6]
>>>

<<<
[PLAY N:S4,S:S7]
===
[PLAY E:S8,W:SJ,N:S4] [showcards W:S3 N:ST E:H2]
>>>

<<<
East discards a \H on the third \S.

Click NEXT. [NEXT]
===
East discards a \H on the third \S. Which card do you play? [choose-card SA]
>>>

<<<
[PLAY N:ST,S:SA]
===
[PLAY W:S3,N:ST,E:H2]
>>>

<<<
Silly question. Of course you play the \DK from your hand, then a small \D finessing dummy's \D10, which wins the trick - and the game - and the overtrick.
===
[PLAY S:DK,W:D4,N:D2,E:D5] [showcards S:D3 W:D8]

You play the \DK from your hand, then a small \D, and West plays low. Which card do you play from dummy? [choose-card DT]

[showcards E:D9]

Silly question. Of course you finesse into the safe hand: dummy's \D10 wins the trick - and the game - and the overtrick.
>>>

## Finesse 20

Win the ♥A and take the first club finesse before drawing trumps; later lead the ♣10 and
play low from dummy to stay in hand.

<<<
South is to play 6\S after North's Stayman bid. West leads the \HQ.
===
[showcards W:HQ N:H5 E:H2] South is to play 6\S after North's Stayman bid. West leads the \HQ, dummy plays the \H5 and East the \H2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card HA]
>>>

<<<
So win the \HA and immediately play a \C to dummy's \CJ, which holds the trick.
===
[PLAY W:HQ,N:H5,E:H2]

You have won the \HA. Which card do you lead now? [choose-card any:C9,C4,C3]

[showcards W:C2]

West plays low. Which card do you play from dummy? [choose-card CJ]

[showcards E:C6]

The \HA, then immediately a \C to dummy's \CJ, which holds the trick.
>>>

<<<
[PLAY N:SA,N:SQ,N:SJ,N:S9,N:CJ,S:SK,S:S7,S:S5,S:S3,S:HA,S:C3]
===
[PLAY W:C2,E:C6,N:SA,E:S2,S:S3,W:S6,N:SQ,E:S4,S:S5,W:H3,N:SJ,E:S8,S:S7,W:HT,N:S9,E:ST,S:SK,W:D2]
>>>

<<<
Next play your \CT, putting on the \C5 from dummy when West plays low again.
===
Which card do you lead now? [choose-card CT]

[showcards W:C7]

West plays low again. Which card do you play from dummy? [choose-card C5]

[showcards E:H4]

Your \C10, putting on the \C5 from dummy when West plays low again.
>>>
