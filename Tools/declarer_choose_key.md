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

- **Ask before telling.** A question never follows text that states its answer: Baker's
  sentence naming the play moves to after the choice, as its explanation. A plan step that
  sets up a decision carries the question itself (no NEXT between them). The first
  decision, when it is at trick 1, is asked on the first step.
- **Declarer plays both hands.** When the other declarer hand has a card that would be a
  mistake (dummy's ♠3 instead of an honour, ♥A instead of low in a Bath coup), its card is
  asked too. Routine follows (spot cards where any will do) stay narrated.
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
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card DA]
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

East follows with the \S9 and you discard the \C3. Holding up the \SA until the third round helps your chances.
>>>

<<<
You can help your chances by a hold-up of the \SA until the third round.
===
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

You held up your \DA until the third round to exhaust East of \Ds.
>>>

<<<
To exhaust East of \Ds you hold-up your \DA until the third round.
===
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

You ducked the second \S and took your \SK on the third round.
>>>

<<<
So you duck the second \S and take your \SK when they play a third round.
===
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

You held up the \DA until the third round, everybody following.
>>>

<<<
So hold up the \DA until the third round, everybody following.
===
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

Dummy plays low to the first heart and you duck; play low again on the second and win it
with dummy's ♥K. The endgame is rebuilt trick by trick from the deal in place of the old
eight-card [showcards].

<<<
South is to play 3NT. West leads the \H7. East plays the \H10.
===
[showcards W:H7] South is to play 3NT. West leads the \H7.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card H8]

[showcards E:HT]

East plays the \H10. Which card do you play? [choose-card any:H5,H9]
>>>

<<<
Let East have the first \H and win the next \H in dummy.
===
>>>

<<<
[PLAY N:HK,N:H8,S:H9,S:H5]
===
[PLAY W:H7,E:HT] [showcards E:HQ]

East continues with the \HQ. Which card do you play? [choose-card any:H9,H5]

[showcards W:H3]

West follows with the \H3. Which card do you play from dummy? [choose-card HK]

[PLAY E:HQ,W:H3]

You let East have the first \H and won the next \H in dummy.
>>>

<<<
[PLAY N:DK,N:D6,N:D5,S:DJ,S:D9,S:D2]
===
[PLAY N:DK,E:D3,S:D2,W:D4,N:D6,E:D7,S:DJ,W:D8,S:D9,W:DA,N:D5,E:C2]
>>>

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
Needing only one more winner you decide to hold up on the first \H and also the \H continuation. You take your \HA on the third round, West having used the \H3 to drive out your \HA.
===
You need only one more winner.
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

Needing only one more winner, you held up on the first \H and on the continuation, taking your \HA on the third round.
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
[showcards W:HK] South is to play 3NT. West leads the \HK.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:H3,H2]

[showcards E:H6]

East plays the \H6. Which card do you play? [choose-card H7]
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
Win the first trick (if you don't West might switch to \Cs) and play a small \S toward dummy's \SQ. It holds the trick.

Click NEXT. [NEXT]

[PLAY N:SQ,N:H4,S:S4,S:HK]
===
Win the first trick (if you don't West might switch to \Cs).

[PLAY W:HQ,N:H4,E:H2]

Which card do you lead now? [choose-card any:S8,S6,S4]

[showcards W:S2]

West plays low. Which card do you play from dummy? [choose-card any:SQ,SK]

[showcards E:S5]

A small \S toward dummy's honours, and it holds the trick.

Click NEXT. [NEXT]

[PLAY W:S2,E:S5]
>>>

<<<
Then play another small \S toward dummy's \SK. This also wins.

Click NEXT. [NEXT]

[PLAY N:SK,N:DA,N:DQ,N:D7,N:D3,S:S6,S:DK,S:DJ,S:DT,S:D2]
===
[PLAY N:D3,E:D4,S:DK,W:D5,S:D2,W:D9,N:DA,E:D6,N:DQ,E:D8,S:DT,W:H8,N:D7,E:C5,S:DJ,W:C3]

Which card do you lead now? [choose-card any:S8,S6,S4]

[showcards W:S7]

West plays low again. Which card do you play from dummy? [choose-card any:SK,SQ]

[showcards E:S9]

Another small \S toward dummy's remaining honour. This also wins.
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
[PLAY W:SK,N:S2,E:S5]

You won the \SA. Which card do you lead now? [choose-card D8]

[showcards W:D5]

West plays low. Which card do you play from dummy? [choose-card DQ]

[showcards E:D2]

Win the \SA, lead your singleton \D and finesse the \DQ. Your luck has returned, the \DQ wins. [NEXT]

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

West plays low. Which card do you play from dummy? [choose-card any:CT,CJ]

[showcards E:CK]
>>>

<<<
Lead a small \C and play the \CT if West plays low. Let's say East wins the \CK and returns a \H.
===
A small \C, playing the \C10 (or \CJ) when West plays low: the first of your two \C finesses. Let's say East wins the \CK and returns a \H.
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

[showcards E:C3]

East plays low. Which card do you play? [choose-card CQ]

[showcards W:C2]
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

You held up the \DA until the third round just to be safe.

[PLAY W:DJ,N:D7,E:S6,S:C2,W:C4,N:CA,E:C3,N:CK,E:C7,S:C9,W:C8,N:C6,E:CT,S:CJ,W:D5,S:CQ,W:D9,N:C5,E:S7]

You cash four rounds of \Cs, ending in your hand. Which card do you lead now? [choose-card HJ]

[showcards W:HQ]

West covers with the \HQ. Which card do you play from dummy? [choose-card HA]

[showcards E:H2]
>>>

<<<
Hold up the \DA until the third round just to be safe.
===
>>>

## Finesse 9

Lead a small spade and finesse the ♠J, playing West for the doubleton ♠K.

<<<
[PLAY N:HT,N:H9,N:H6,N:D5,S:H7,S:H4,S:H2,S:DK]
===
[PLAY W:H5,N:H6,E:HQ,S:H2,E:HA,S:H4,W:H8,N:H9,E:H3,S:H7,W:HK,N:HT,W:D4,N:D5,E:D2,S:DK]
>>>

<<<
The odds aren't in your favor, but you have no choice but to play West for the doubleton King.

Click NEXT. [NEXT]
===
Which card do you lead? [choose-card any:S6,S5,S3]

[showcards W:S2]

West plays low. Which card do you play from dummy? [choose-card SJ]

[showcards E:S8]

The odds aren't in your favor, but you have no choice but to play West for the doubleton King.
>>>

<<<
Lead a small \S from your hand and when West plays low put on the \SJ. When this holds the trick plunk down the \SA and hope.
===
So: a small \S from your hand, putting on the \SJ when West plays low. When this holds the trick plunk down the \SA and hope.
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
But you will only be in dummy once more so you <b>MUST</b> make the first finesse right now. Play a small \C from dummy and play the \CT. West wins with the \CQ and plays another trump.
===
[PLAY W:H3,E:H6,S:H2]

Which card do you lead from dummy? [choose-card any:C8,C5,C3,C2]

[showcards E:C4]

East plays low. Which card do you play? [choose-card any:CT,CJ]

[showcards W:CQ]

You will only be in dummy once more, so you <b>MUST</b> make the first finesse right now: a small \C from dummy to your \C10 (or \CJ). West wins with the \CQ and plays another trump.
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

East plays low. Which card do you play? [choose-card any:CJ,CT]

[showcards W:C6]

A small \C to your remaining honour.
>>>

## Finesse 11

Ruff, draw trumps, then lead a low heart toward dummy's ♥J before trying the spade finesse.

<<<
You can give yourself a second chance by playing West to hold the \HQ.
===
>>>

<<<
Ruff the opening \C lead, pull trumps with the \DK, (they split 1-1), and play a low \H toward the \HJ. West fidgets, then puts on the \HQ and plays another \C which you ruff.
===
[PLAY W:CK,N:C6,E:C3,S:D6,S:DK,W:D5,N:D2,E:D4]

You ruff the opening \C lead and pull trumps with the \DK (they split 1-1). Which card do you lead now? [choose-card any:H7,H5]

[showcards W:HQ]

West fidgets, then puts on the \HQ. Which card do you play from dummy? [choose-card H6]

[showcards E:H8]

A low \H toward the \HJ gives you a second chance, by playing West to hold the \HQ. West plays another \C, which you ruff.
>>>

<<<
[PLAY N:H6,N:D2,N:C7,N:C6,S:H5,S:DK,S:D6,S:D3]
===
[PLAY W:HQ,E:H8,W:CQ,N:C7,E:C5,S:D3]
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
Which card do you play now? [choose-card any:CA,CT]

[showcards W:C3]

The \CA and \CK (in either order), hoping the \CQ falls.
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
You could lead toward the \SQ, winning a trick if West holds BOTH the \SA and \SK. Or you could finesse the \ST, gaining a trick if West holds the \SJ. Obviously the second choice is more likely.

Click NEXT. [NEXT]
===
>>>

<<<
Having won the first \H trick in your hand, play a small \S and finesse the \ST. Suppose East wins the \SK and returns a \H. Take your \HA and play another \S, going up with the \SQ if West plays low.
===
[PLAY W:H3,N:H4,E:HJ]

Which card do you lead? [choose-card any:S8,S7,S3]

[showcards W:S4]

West plays low. Which card do you play from dummy? [choose-card ST]

[showcards E:SK]

You could lead toward the \SQ, winning a trick if West holds BOTH the \SA and \SK. Or you could finesse the \S10, gaining a trick if West holds the \SJ. The second is more likely. Suppose East wins the \SK. [NEXT]

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

[showcards N:SQ E:S3]

You lead the \SQ from dummy and East plays low. Which card do you play? [choose-card any:SJ,ST]

[showcards W:S7]

The \SQ from dummy, and the \SJ (or 10) from your hand when East plays low.
>>>

<<<
[PLAY N:SQ,N:HA,S:ST,S:H4]
===
[PLAY N:SQ,E:S3,W:S7]
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

[showcards W:D4]

West plays low. Which card do you play from dummy? [choose-card DQ]

[showcards E:D3]

You test the \D suit: a small one to dummy's \DQ, then the \DK and \DA. [NEXT]

[PLAY W:D4,E:D3,N:D2,E:D8,S:DK,W:D9,S:DA,W:DJ,N:D7,E:DT]

Both defenders followed three times, so your last \D is a winner. Which card do you play? [choose-card any:D6,D5]

[showcards W:S4 N:C5 E:S2]

You cash it.
>>>

<<<
[PLAY N:DQ,N:D7,N:D2,N:C5,S:DA,S:DK,S:D6,S:D5]
===
[PLAY W:S4,N:C5,E:S2]
>>>

<<<
Before you put all your eggs in the \C finesse basket there is one thing you should do first.

Click NEXT. [NEXT]
===
Before you put all your eggs in the \C finesse basket there is one thing you should do first.
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
So you must turn to the \Ss for the extra two winners.

Click NEXT. [NEXT]

[PLAY N:H2,S:HK]
===
So you must turn to the \Ss for the extra two winners.

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

You held up the \DA until the third round to confirm that East has only 2. He does.

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

<<<
Hold up the \DA until the third round to confirm that East has only 2. He does.
===
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
But is that all there is to it?

Click NEXT. [NEXT]
===
But is that all there is to it?

[PLAY W:HQ,N:H5,E:H2]

You have won the \HA. Which card do you lead now? [choose-card any:C9,C4,C3]

[showcards W:C2]

West plays low. Which card do you play from dummy? [choose-card CJ]

[showcards E:C6]
>>>

<<<
So win the \HA and immediately play a \C to dummy's \CJ, which holds the trick.
===
That is why you win the \HA and immediately play a \C to dummy's \CJ, which holds the trick.
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


## Entries 1

Win the opening club with dummy's ♣K to keep the ♣A as the entry to the spades.

<<<
South is to play 3NT. West leads the \C3.
===
[showcards W:C3] South is to play 3NT. West leads the \C3.
>>>

<<<
So what should you do?

Click [NEXT]
===
So what should you do? Which card do you play from dummy? [choose-card CK]
>>>

<<<
It's easy once you think about it.
===
[showcards E:C9 S:C2]

It's easy once you think about it.
>>>

## Entries 3

Jump up with dummy's ♣A; then ♦A and the ♦10 overtaken, with no finesse.

<<<
South is to play 3NT. West leads the \C4.
===
[showcards W:C4] South is to play 3NT. West leads the \C4.
>>>

<<<
So what is your first key move?

Click NEXT. [NEXT]
===
So what is your first key move? Which card do you play from dummy? [choose-card CA]
>>>

<<<
The \C situation is exactly the same
===
[showcards E:C5 S:C3]

The \C situation is exactly the same
>>>

<<<
Having done that, are your problems (and thinking) over?

Click NEXT. [NEXT]
===
Having done that, are your problems (and thinking) over?

[PLAY W:C4,E:C5,S:C3]

Which card do you lead from dummy? [choose-card DA]

[showcards E:D2 S:D3 W:D5]

Everyone follows low. [NEXT]

[PLAY E:D2,S:D3,W:D5]

Which card do you lead from dummy now? [choose-card DT]

[showcards E:D4]

East plays low. Which card do you play? [choose-card any:DQ,DJ]

[showcards W:D6]
>>>

## Entries 4

Ruff the third club high, saving the ♥5 as the second trump entry to dummy.

<<<
That won't be a problem, will it?

Click NEXT. [NEXT]
===
That won't be a problem, will it?

[PLAY W:CA,N:C4,E:C5,S:C2,W:CK,N:C9,E:C7,S:C6] [showcards W:CQ N:CJ E:CT]

West continues with the \CQ; dummy plays the \CJ and East the \C10. Which card do you play? [choose-card any:HK,HQ,HJ,H9,H8]
>>>

## Entries 5

Unblock the clubs, starting with one of dummy's high ones and keeping the ♣5 for last.

<<<
Is there any other pitfall you might need to worry about?

Click NEXT. [NEXT]
===
Is there any other pitfall you might need to worry about?

[PLAY W:S5,N:SA,E:S8,S:S3]

You win the \SA. Which card do you lead from dummy? [choose-card any:CQ,C8,C7]
>>>

## Entries 6

Win the first trick with dummy's ♠A so both ♠K and ♠J are entries.

<<<
South is to play 3NT. West leads the \S5.
===
[showcards W:S5] South is to play 3NT. West leads the \S5.
>>>

<<<
The \S suit will provide one entry easily, but should you depend on the \HQ for the second entry?

Click NEXT. [NEXT]
===
The \S suit will provide one entry easily, but should you depend on the \HQ for the second entry? Which card do you play from dummy? [choose-card SA]
>>>

<<<
No, for two reasons.
===
[showcards E:S3 S:S4]

No, for two reasons.
>>>

## Entries 7

Win the first club with a top honour, not cheaply, to make a club entry to dummy.

<<<
South is to play 3NT. West leads the \C5. You play low from dummy and East plays the \C6.
===
[showcards W:C5 N:C2 E:C6] South is to play 3NT. West leads the \C5. You play low from dummy and East plays the \C6.
>>>

<<<
But you need that fourth \D winner. Can you get it?

Click NEXT. [NEXT]
===
But you need that fourth \D winner. Can you get it? Which card do you play to this first trick? [choose-card any:CA,CK]
>>>

## Entries 8

Cash the diamond honours from hand, keeping the ♦5 to reach dummy's ♦6 for a second finesse.

<<<
Can you find them?

Click NEXT. [NEXT]
===
Can you find them?

[PLAY W:SQ,N:S3,E:SK,S:S6,E:S2,S:SA,W:S5,N:S8]

You won the second \S. Which card do you lead now? [choose-card any:DK,DQ,DJ]
>>>

## Entries 9

Win the diamond; lead a low club toward dummy's ♣9-8 for a sure entry.

<<<
South is to play 6\C. West leads the \DQ.
===
[showcards W:DQ N:D3 E:D4] South is to play 6\C. West leads the \DQ, dummy plays the \D3 and East the \D4.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:DA,DK]
>>>

<<<
see if you can find a way to fight yourself over to dummy and those three beautiful \Ss.

Click NEXT. [NEXT]
===
see if you can find a way to fight yourself over to dummy and those three beautiful \Ss.

[PLAY W:DQ,N:D3,E:D4]

Which card do you lead now? [choose-card any:C7,C5,C4]

[showcards W:CT N:C8 E:C2]

West plays the \C10, dummy the \C8 and East the \C2.
>>>

## Entries 10

Discard a diamond from dummy on the second spade instead of ruffing.

<<<
Do you see a way around this?

Click NEXT. [NEXT]
===
Do you see a way around this?

[PLAY W:SA,N:S9,E:S2,S:S3] [showcards W:SK]

West continues with the \SK. Which card do you play from dummy? [choose-card any:D6,D5]
>>>

## Entries 11

Unblock the ♣K under East's ♣A, making the ♣10 a second entry to dummy.

<<<
South is to play 3NT. West leads the \C3, East plays the \CA.
===
[showcards W:C3 N:C7 E:CA] South is to play 3NT. West leads the \C3, dummy plays the \C7 and East the \CA.
>>>

<<<
Do you have them?

Click NEXT. [NEXT]
===
Do you have them? Which card do you play to this first trick? [choose-card CK]
>>>

## Entries 12

Take the ♦K at once; then use both heart honours as dummy entries.

<<<
South is to play 3NT. West leads the \D5, East plays the \DQ.
===
[showcards W:D5 N:D4 E:DQ] South is to play 3NT. West leads the \D5, dummy plays the \D4 and East the \DQ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card DK]
>>>

<<<
You need dummy entries, and they must be in \Hs.

Click NEXT. [NEXT]
===
You need dummy entries, and they must be in \Hs.

[PLAY W:D5,N:D4,E:DQ]

Which card do you lead now? [choose-card any:HJ,HK]
>>>

## Entries 13

Win the first heart with the ♥A, keeping the ♥Q-10 as a later entry to dummy.

<<<
South is to play 3NT. West leads the \H4, you play low in dummy and East plays the \H8.
===
[showcards W:H4 N:H3 E:H8] South is to play 3NT. West leads the \H4, you play low in dummy and East plays the \H8.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card HA]
>>>

## Entries 14

Duck the first spade to keep the ♠A as the entry to the clubs.

<<<
South is to play 3NT. West leads the \S9, and East plays the \SK.
===
[showcards W:S9 N:ST E:SK] South is to play 3NT. West leads the \S9, dummy plays the \S10 and East the \SK.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:S4,S3]
>>>

## Entries 15

Take the ♥K now; test the diamonds from the top before using dummy's ♦A.

<<<
South is to play 3NT. West leads the \H3, you play dummy's \HJ and East plays the \HQ.
===
[showcards W:H3 N:HJ E:HQ] South is to play 3NT. West leads the \H3, you play dummy's \HJ and East plays the \HQ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card HK]
>>>

<<<
Got it?

Click NEXT. [NEXT]
===
Got it?

[PLAY W:H3,N:HJ,E:HQ]

Which card do you lead now? [choose-card any:DK,DQ]
>>>

## Entries 16

Win the first club with the ♣K; cross with the ♣9 to the ♣J; lead the ♠10 underplaying the ♠8.

<<<
South is to play 3NT. West leads the \C4, you play dummy's \C5 and East plays the \C7.
===
[showcards W:C4 N:C5 E:C7] South is to play 3NT. West leads the \C4, you play dummy's \C5 and East plays the \C7.
>>>

<<<
Do you see a way to avoid the problem?

Click NEXT. [NEXT]
===
Do you see a way to avoid the problem? Which card do you play to this first trick? [choose-card CK]
>>>

<<<
Don't win the first trick with the \C9, win with the \CK. Then at trick two enter dummy by playing your \C9 and finessing the \CJ! You are pretty sure West has led from the \CQ so you expect this to work. Then play the \ST, underplaying your \S8. You had better cash the \CA next, then the \SQ, letting it ride if not covered. Finally, one last \S finesse gives you 4 \S winners.
===
Don't win the first trick with the \C9, win with the \CK.

[PLAY W:C4,N:C5,E:C7]

Which card do you lead now? [choose-card C9]

[showcards W:C8]

West plays low. Which card do you play from dummy? [choose-card CJ]

[showcards E:C2]

At trick two you enter dummy by playing your \C9 and finessing the \CJ! You are pretty sure West has led from the \CQ so you expect this to work. [NEXT]

[PLAY W:C8,E:C2]

Which card do you lead from dummy? [choose-card any:ST,SQ]

[showcards E:S2]

East plays low. Which card do you play? [choose-card any:S8,S9]

[showcards W:S4]

Lead the \S10 (or \SQ) and underplay it with your \S8 (or \S9), so you stay in dummy. You had better cash the \CA next, then the \SQ, letting it ride if not covered. Finally, one last \S finesse gives you 4 \S winners.
>>>

## Entries 17

Win the spade, then unblock the ♥A or lead the ♦J before touching the diamond winners.

<<<
South is to play 3NT. West leads the \SQ.
===
[showcards W:SQ N:S4 E:S3] South is to play 3NT. West leads the \SQ, dummy plays the \S4 and East the \S3.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:SA,SK]
>>>

<<<
Can you work those two possibilities into a strategy?

Click NEXT. [NEXT]
===
Can you work those two possibilities into a strategy?

[PLAY W:SQ,N:S4,E:S3]

Which card do you lead now? [choose-card any:HA,DJ]
>>>

## Entries 18

Win the diamond in dummy, cash the ♠K, then run the ♣10 through East.

<<<
South is to play 3NT. West leads the \D2.
===
[showcards W:D2] South is to play 3NT. West leads the \D2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:DA,DK,DQ]
>>>

<<<
Which way will you finesse, and why?

Click NEXT. [NEXT]
===
Which way will you finesse, and why?

[PLAY W:D2,E:D3,S:D4,N:SK,E:S2,S:S3,W:S4]

You win the \D in dummy and play the \SK, which the defenders let hold. Which card do you lead from dummy? [choose-card CT]

[showcards E:C2]

East plays low. Which card do you play? [choose-card C3]

[showcards W:CQ]
>>>

## Entries 19

Overtake the ♥K with dummy's ♥A to save heart entries, then finesse the ♣9.

<<<
South is to play 6NT. West leads the \ST.
===
[showcards W:ST N:S6 E:S3] South is to play 6NT. West leads the \ST, dummy plays the \S6 and East the \S3.
>>>

<<<
Can it be done?

Click NEXT. [NEXT]
===
Can it be done?

[PLAY W:ST,N:S6,E:S3,S:SA] [showcards S:HK W:H2]

You win the \S lead in your hand, then lead the \HK and West plays low. Which card do you play from dummy? [choose-card HA]

[showcards E:H6]

East follows with the \H6. [NEXT]

[PLAY S:HK,W:H2,E:H6]

Which card do you lead from dummy? [choose-card any:C6,C4,C2]

[showcards E:C3]

East plays low. Which card do you play? [choose-card C9]

[showcards W:CK]
>>>

## Entries 20

Win the diamond and lay down the ♣J: either way you reach dummy's hearts.

<<<
South is to play 6\S. West leads the \DQ.
===
[showcards W:DQ N:D4 E:D7] South is to play 6\S. West leads the \DQ, dummy plays the \D4 and East the \D7.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:DA,DK]
>>>

<<<
There is actually a play that is 100% certain, no matter who holds the \CK.

Click NEXT. [NEXT]
===
There is actually a play that is 100% certain, no matter who holds the \CK.

[PLAY W:DQ,N:D4,E:D7]

Which card do you lead now? [choose-card CJ]
>>>

## Establishment 1

Win trick 1 with a dummy honour, saving the ♠Q as the entry; unblock with dummy's ♦Q.

<<<
South is to play 3NT. West leads the \SJ.
===
[showcards W:SJ] South is to play 3NT. West leads the \SJ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:SK,SA]
>>>

<<<
Winners:   \S = 3
===
[showcards E:S5 S:S3] East plays the \S5 and you the \S3.

Winners:   \S = 3
>>>

<<<
[PLAY N:SK,S:S3]
===
[PLAY W:SJ,E:S5,S:S3]

Which card do you lead from dummy? [choose-card DQ]

[showcards E:D2 S:D4 W:D6]
>>>

<<<
Next start playing \Ds, first \DQ, then \DK.
===
You start on \Ds with the \DQ, then the \DK.
>>>

<<<
[PLAY N:DQ,N:D3,S:DK,S:D4]
===
[PLAY E:D2,S:D4,W:D6,N:D3,E:D5,S:DK,W:DA]
>>>

## Establishment 2

Dummy plays low at trick 1, keeping its trump entries.

<<<
South is to play 4\S. West leads the \S6, East plays \S4.
===
[showcards W:S6] South is to play 4\S. West leads the \S6.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card S2]

[showcards E:S4 S:SA]

East plays the \S4 and you win with the \SA. [NEXT]
>>>

<<<
[PLAY N:S2,S:SA]
===
[PLAY W:S6,E:S4,S:SA]
>>>

## Establishment 3

Duck a club: a small one from each hand.

<<<
South is to play 3NT. West leads the \DJ, East plays \DK.
===
[PLAY W:DJ,N:D6,E:DK,S:DA] South is to play 3NT. West leads the \DJ, East plays the \DK and you win with the \DA.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:C6,C2]

[showcards W:C5]

West plays low. Which card do you play from dummy? [choose-card any:C4,C3]

[showcards E:C7]

East wins with the \C7. [NEXT]
>>>

<<<
[PLAY N:D6,N:C3,S:DA,S:C2]
===
[PLAY W:C5,E:C7]
>>>

## Establishment 4

Duck a club from dummy at once, keeping a club to reach the long suit.

<<<
South is to play 3NT. West leads the \H5, East plays the \H2.
===
[PLAY W:H5,N:HT,E:H2,S:H3] South is to play 3NT. West leads the \H5, dummy plays the \H10, East the \H2 and you the \H3. Dummy wins.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to lead. [choose-card any:C8,C7,C6,C4,C3]

[showcards E:CJ S:C2 W:C5]

East wins with the \CJ. [NEXT]
>>>

<<<
[PLAY N:HT,S:H3]
===
[PLAY E:CJ,S:C2,W:C5]
>>>

## Establishment 5

Win the spade, then duck a diamond from both hands.

<<<
South is to play 3NT. West leads the \S2, East plays the \SJ.
===
[showcards W:S2 N:S4 E:SJ] South is to play 3NT. West leads the \S2, dummy plays the \S4 and East the \SJ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:SK,SA]

[PLAY W:S2,N:S4,E:SJ]

Which card do you lead now? [choose-card any:D7,D6,D3]

[showcards W:D9]

West plays low. Which card do you play from dummy? [choose-card any:D8,D5,D4,D2]

[showcards E:DJ]

East wins with the \DJ. [NEXT]
>>>

## Establishment 6

Win the ♠K in hand (dummy low), then ♥Q-♥J overtaking the second with dummy's ♥K.

<<<
South is to play 3NT. West leads the \S2.
===
[showcards W:S2] South is to play 3NT. West leads the \S2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:S7,S4]

[showcards E:SJ S:SK]

East plays the \SJ and you win with the \SK. [NEXT]

[PLAY W:S2,E:SJ,S:SK]

Which card do you lead now? [choose-card any:HQ,HJ]

[showcards W:H2]

West plays low. Which card do you play from dummy? [choose-card any:H9,H8,H3]

[showcards E:H5]

East plays low too. [NEXT]

[PLAY W:H2,E:H5]

Which card do you lead now? [choose-card any:HJ,HQ]

[showcards W:H4]

West plays low. Which card do you play from dummy? [choose-card HK]

[showcards E:H6]

East holds up his \HA again. [NEXT]
>>>

## Establishment 7

Win the ♥A, draw trumps, then start on dummy's clubs.

<<<
South is to play 6\S. West leads the \HK.
===
[showcards W:HK N:H5 E:H3] South is to play 6\S. West leads the \HK, dummy plays the \H5 and East the \H3.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card HA]

[PLAY W:HK,N:H5,E:H3,S:SK,W:S3,N:S4,E:D4,S:SQ,W:ST,N:S6,E:D9]

You win the \HA and draw trumps with the \SK and \SQ. Which card do you lead now? [choose-card any:C5,C2]

[showcards W:C8]

West plays low. [NEXT]
>>>

## Establishment 8

Attack spades, the suit where the defenders have winners anyway.

<<<
Make a Plan, then click NEXT. [NEXT]
===
[PLAY W:D6,N:D5,E:DJ,S:D3,E:DQ,S:D4,W:D2,N:D7,E:D9,S:DA,W:D8,N:C3]

Make a Plan, then play a card from your hand. [choose-card any:SQ,SJ,S5]
>>>

## Establishment 9

Win the second spade in hand with dummy playing low; unblock the clubs, overtaking with the
♣A, then lead a club to establish the ♣9 while the ♠Q is still an entry.

<<<
South is to play 3NT. West leads the \S9, taken by East with the \SA. East next plays the \S4.
===
[PLAY W:S9,N:S2,E:SA,S:S7] [showcards E:S4] South is to play 3NT. West leads the \S9, taken by East with the \SA. East next plays the \S4.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
[showcards S:SK W:S3]

You win with the \SK and West plays low. Make a Plan, then choose dummy's card to this trick. [choose-card ST]

[PLAY E:S4,S:SK,W:S3]

Which card do you lead now? [choose-card any:CK,CQ]

[showcards W:C2 N:C3 E:C4]

Everyone follows low. [NEXT]

[PLAY W:C2,N:C3,E:C4]

Which card do you lead now? [choose-card any:CQ,CK]

[showcards W:C6]

West plays low. Which card do you play from dummy? [choose-card CA]

[showcards E:C5]

East follows with the \C5. [NEXT]

[PLAY W:C6,E:C5]

Which card do you lead from dummy? [choose-card any:CT,C9,C8]

[showcards E:CJ]

East wins with the \CJ. [NEXT]
>>>

## Establishment 10

Win the club and play spades, hoping for a 3-3 split.

<<<
South is to play 2NT. West leads the \CK.
===
[showcards W:CK N:C3 E:C2] South is to play 2NT. West leads the \CK, dummy plays the \C3 and East the \C2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card CA]

[PLAY W:CK,N:C3,E:C2]

Which card do you lead now? [choose-card any:S7,S6,S3]

[showcards W:S4]

West plays low. [NEXT]
>>>

## Establishment 11

Win the ♣A and lead the ♠Q at once; win the trump return in dummy; ruff a spade high.

<<<
South is to play 4\H. West leads the \CK.
===
[showcards W:CK N:C3 E:C5] South is to play 4\H. West leads the \CK, dummy plays the \C3 and East the \C5.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card CA]

[PLAY W:CK,N:C3,E:C5]

Which card do you lead now? [choose-card SQ]

[showcards W:S4 N:S2 E:SK]

East wins the \SK. [NEXT]

[PLAY W:S4,N:S2,E:SK] [showcards E:H2 S:H6 W:H3]

East plays a trump, you follow low and West too. Which card do you play from dummy? [choose-card any:HA,HK,HJ]

[NEXT]

[PLAY E:H2,S:H6,W:H3] [showcards N:S3 E:S7]

Dummy leads a \S and East plays low. Which card do you play? [choose-card any:HQ,HT,H9]

[showcards W:ST]
>>>

## Establishment 12

Win the diamond in dummy and start hearts before drawing trumps.

<<<
South is to play 7\C. West leads the \DQ.
===
[showcards W:DQ] South is to play 7\C. West leads the \DQ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:DA,DK]

[showcards E:D2 S:D4]

East plays the \D2 and you the \D4. [NEXT]

[PLAY W:DQ,E:D2,S:D4]

Which card do you lead from dummy? [choose-card any:H8,H7,H5,H3,HK]
>>>

## Establishment 13

Win the spade and finesse the ♦10, establishing the diamonds.

<<<
South is to play 3NT. West leads the \S4.
===
[showcards W:S4 N:S3 E:SJ] South is to play 3NT. West leads the \S4, dummy plays the \S3 and East the \SJ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:SA,SK]

[PLAY W:S4,N:S3,E:SJ]

Which card do you lead now? [choose-card any:D7,D5,D3]

[showcards W:D4]

West plays low. Which card do you play from dummy? [choose-card DT]

[showcards E:DJ]

East wins with the \DJ. [NEXT]
>>>

## Establishment 14

Duck West's ♣K in dummy, keeping the ♣A as the entry.

<<<
What do you do next?
===
What do you do next?

[PLAY W:S4,N:S7,E:SA,S:S3,E:S8,S:SQ,W:S2,N:S9] [showcards S:CQ W:CK]

Which card do you play from dummy? [choose-card any:C8,C6,C5,C3]

[showcards E:C4]
>>>

<<<
Click NEXT. [NEXT]

[PLAY N:S9,N:S7,S:SQ,S:S3]
===
>>>

## Establishment 15

Win with the ♠Q, then duck a heart in dummy.

<<<
South is to play 3NT. West leads the \S2. East puts on the \SJ.
===
[showcards W:S2 N:S4 E:SJ] South is to play 3NT. West leads the \S2, dummy plays the \S4 and East puts on the \SJ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card SQ]

[PLAY W:S2,N:S4,E:SJ]

Which card do you lead now? [choose-card any:H6,H3]

[showcards W:H4]

West plays low. Which card do you play from dummy? [choose-card any:H8,H7,H5]

[showcards E:H9]

East wins with the \H9. [NEXT]
>>>

## Establishment 16

Ruff the third spade, then lead the ♦Q (dummy low) before touching trumps.

<<<
Make a Plan, then click NEXT. [NEXT]
===
[PLAY W:SK,N:S3,E:SA,S:S4,E:S2,S:S7,W:ST,N:S5,W:SQ,N:S6,E:S9,S:H2]

You ruff the third \S. Make a Plan, then play a card from your hand. [choose-card DQ]

[showcards W:D3]

West plays low. Which card do you play from dummy? [choose-card any:D8,D5]

[showcards E:D2]

East ducks. [NEXT]
>>>

## Establishment 17

Win the first trick with the ♠A to unblock, keeping the ♠QJ as dummy's entry.

<<<
South is to play 3NT. West leads the \S6, you play dummy's \S9 and  East contributes the \S2.
===
[showcards W:S6 N:S9 E:S2] South is to play 3NT. West leads the \S6, you play dummy's \S9 and  East contributes the \S2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card SA]
>>>

## Establishment 18

Win the first trick with the ♠A, keeping two spade entries to dummy.

<<<
South is to play 3NT. West leads the \S2, you play dummy's \S4 and  East plays the \S8.
===
[showcards W:S2 N:S4 E:S8] South is to play 3NT. West leads the \S2, you play dummy's \S4 and  East plays the \S8.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card SA]
>>>

## Establishment 19

Cover the ♠10 with dummy's ♠J; cross to the ♦10; lead the ♠Q to ruff out East's honours.

<<<
South is to play 5\D. West leads the \ST.
===
[showcards W:ST] South is to play 5\D. West leads the \ST.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card SJ]

[showcards E:SK S:D2]

East plays the \SK and you ruff with the \D2. [NEXT]

[PLAY W:ST,E:SK,S:D2]

Which card do you lead now? [choose-card any:D7,D6,D5]

[showcards W:D3]

West plays low. Which card do you play from dummy? [choose-card DT]

[showcards E:S3]

East shows out. [NEXT]

[PLAY W:D3,E:S3]

Which card do you lead from dummy? [choose-card SQ]

[showcards E:SA]

East covers with the \SA. [NEXT]
>>>

## Establishment 20

After trumps, the top clubs and the ♦A, exit with the ♦5 to make the defenders help you.

<<<
After pulling trumps, play the \C A K, then \DA. Next exit with a small \D.

Click NEXT to see the position. [NEXT]

[PLAY N:S6,N:S4,N:D8,N:D6,N:C4,N:C3,S:SA,S:SQ,S:DA,S:D5,S:CA,S:CK]
===
After pulling trumps, play the \C A K, then \DA.

[PLAY W:S5,N:S4,E:S8,S:SQ,S:SA,W:S3,N:S6,E:S2,S:CA,W:C5,N:C3,E:C2,S:CK,W:CT,N:C4,E:C7,S:DA,W:D2,N:D6,E:D4]

Which card do you lead now? [choose-card D5]

[showcards W:D3 N:D8 E:DT]

You exit with a small \D and East wins. [NEXT]
>>>

## Trumpmgmt 1

Grab the ♣A at trick 2 and draw trumps, rather than risk the club finesse and ruffs.

<<<
South is to play 4\S. West leads the \DK. East overtakes with the \DA and returns the \C4.
===
[PLAY W:DK,N:D6,E:DA,S:D2] [showcards E:C4] South is to play 4\S. West leads the \DK. East overtakes with the \DA and returns the \C4.
>>>

<<<
What could go wrong? [NEXT]
===
What could go wrong? Which card do you play? [choose-card CA]
>>>

<<<
What could go wrong is that
===
[showcards W:C6 N:C3]

What could go wrong is that
>>>

## Trumpmgmt 2

Win the club and give up a heart at once, before any trumps.

<<<
The most important question right now is how many rounds of trumps to pull before you give up a \H? [NEXT]
===
The most important question right now is how many rounds of trumps to pull before you give up a \H?

[PLAY W:CQ,N:C3,E:C2,S:CA]

You win the \CA. Which card do you lead now? [choose-card any:HQ,HT,H7]
>>>

## Trumpmgmt 3

From dummy, lead a spade toward your hand at once and put up an honour.

<<<
South is to play 4\H. West leads the \H7.
===
[showcards W:H7 N:HA E:H4 S:H2] South is to play 4\H. West leads the \H7, won by dummy's \HA.
>>>

<<<
You are in dummy right now, and you are only going to be in dummy once more. [NEXT]
===
You are in dummy right now, and you are only going to be in dummy once more.

[PLAY W:H7,N:HA,E:H4,S:H2]

Which card do you lead from dummy? [choose-card any:S8,S7,S3,S2]

[showcards E:S6]

East plays low. Which card do you play? [choose-card any:SK,SQ]

[showcards W:S5]
>>>

## Trumpmgmt 4

Lead your spade toward dummy's honours before touching trumps.

<<<
South is to play 5\D. West leads the \CT. You play dummy's \CJ and East puts on the \CK.
===
[showcards W:CT N:CJ E:CK S:CA] South is to play 5\D. West leads the \CT. You play dummy's \CJ and East puts on the \CK; you win the \CA.
>>>

<<<
Anything you can think of to do about that? [NEXT]
===
Anything you can think of to do about that?

[PLAY W:CT,N:CJ,E:CK,S:CA]

Which card do you lead now? [choose-card S8]

[showcards W:S2]

West plays low. Which card do you play from dummy? [choose-card any:SK,SQ]

[showcards E:SA]
>>>

## Trumpmgmt 5

Cash the ♦A and ♦K without finessing, keeping trumps in dummy for the cross-ruff.

<<<
Try something else. [NEXT]
===
Try something else.

[PLAY W:CJ,N:C2,E:C3,S:CA,S:D3,W:D2,N:DA,E:DT] [showcards N:D4 E:D6]

You win the \C and cash the \DA. Dummy leads the \D4 and East plays low. Which card do you play? [choose-card DK]

[showcards W:D9]
>>>

## Trumpmgmt 6

Duck the ♥Q and the ♥J; after three rounds of trumps, leave West's master trump out and
switch to clubs.

<<<
South is to play 4\S. West leads the \HQ.
===
[showcards W:HQ] South is to play 4\S. West leads the \HQ.
>>>

<<<
Do you cover the \HQ or not? [NEXT]
===
Do you cover the \HQ or not? Which card do you play from dummy? [choose-card any:H6,H5]

[showcards E:H2 S:H4]

East plays the \H2 and you the \H4. [NEXT]

[PLAY W:HQ,E:H2,S:H4] [showcards W:HJ]

West continues with the \HJ. Which card do you play from dummy? [choose-card any:H6,H5]

[showcards E:H7 S:H9]
>>>

<<<
But don't give it to him now!
===
[PLAY W:HJ,E:H7,S:H9,W:HT,N:HK,E:HA,S:S4,S:S7,W:S3,N:SA,E:S6,N:S2,E:D7,S:SK,W:S5,S:SQ,W:ST,N:S8,E:D9]

Which card do you lead now? [choose-card any:CA,CK,C6]

[showcards W:C3]

But don't give it to him now!
>>>

## Trumpmgmt 7

Unblock the ♥A before trumps, then lead small trumps toward dummy's ♠10-8.

<<<
Can you? [NEXT]
===
Can you?

[PLAY W:DQ,N:D2,E:D5,S:DA]

You win the \DA. Which card do you lead now? [choose-card HA]

[showcards W:H2 N:H6 E:H3]

Everyone follows. [NEXT]

[PLAY W:H2,N:H6,E:H3]

Which card do you lead now? [choose-card any:S5,S3]

[showcards W:S4 N:S8 E:SJ]

East wins the \SJ.
>>>

## Trumpmgmt 8

Win trick 1 in dummy, then lead a heart for the deep finesse of the ♥9.

<<<
South is to play 5\C. West leads the \SJ.
===
[showcards W:SJ N:SQ E:S2 S:S9] South is to play 5\C. West leads the \SJ; dummy wins with the \SQ, East plays the \S2 and you the \S9.
>>>

<<<
Should you pull trumps right away? [NEXT]
===
Should you pull trumps right away?

[PLAY W:SJ,N:SQ,E:S2,S:S9]

Which card do you lead from dummy? [choose-card any:H6,H4,H3]

[showcards E:H2]

East plays low. Which card do you play? [choose-card H9]

[showcards W:HQ]
>>>

## Trumpmgmt 9

After West shows out in trumps, drive out East's trump winners with small trumps.

<<<
Time for a change in plans? [NEXT]
===
Time for a change in plans?

[PLAY W:DK,N:DA,E:D2,S:D6,N:H6,E:H2,S:HA,W:H4,S:HK,W:D3,N:H8,E:HT]

Which card do you lead now? [choose-card any:H9,H7,H5,H3]
>>>

## Trumpmgmt 10

Win the ♣A and lead toward the diamonds twice before touching trumps.

<<<
So after you win your \CA do you play a trump? [NEXT]
===
So after you win your \CA do you play a trump?

[PLAY W:CJ,N:C4,E:C2,S:CA]

Which card do you lead now? [choose-card any:D7,D4]

[showcards W:D5]

West plays low. Which card do you play from dummy? [choose-card any:DQ,DK]

[showcards E:D2]
>>>

## Trumpmgmt 11

Dummy reversal: ruff dummy's spades high in your hand.

<<<
South is to play 4\H. West leads the \SK, taken by dummy's \SA.
===
[showcards W:SK N:SA E:S4 S:ST] South is to play 4\H. West leads the \SK, taken by dummy's \SA.
>>>

<<<
If you don't see a better Plan than these two, just put yourself in Dummy's seat and pretend you are playing 4\H from that side of the table. [NEXT]
===
If you don't see a better Plan than these two, just put yourself in Dummy's seat and pretend you are playing 4\H from that side of the table.

[PLAY W:SK,N:SA,E:S4,S:ST] [showcards N:S2 E:S8]

Dummy leads a \S and East plays low. Which card do you play? [choose-card any:HA,HK,HJ]

[showcards W:S3]
>>>

## Trumpmgmt 12

Win the ♦A and lead a club from hand at once: no finesse, no trumps.

<<<
What else might you try? [NEXT]
===
What else might you try?

[PLAY W:DK,N:D2,E:D3,S:DA]

You win the \DA. Which card do you lead now? [choose-card any:CQ,CJ,CA]
>>>

## Trumpmgmt 13

Ruff your third diamond with dummy's ♥A, not the ♥5.

<<<
Next play your \D3. East plays the \DQ and you do what? [NEXT]
===
[PLAY W:CK,N:CA,E:C3,S:C5,N:DK,E:D5,S:D2,W:D4,N:D8,E:DJ,S:DA,W:D7] [showcards S:D3 W:DQ]

Next you play your \D3 and West plays the \DQ. Which card do you play from dummy? [choose-card HA]

[showcards E:C7]
>>>

## Trumpmgmt 14

Ruff the fourth club with dummy's ♠9, over West's ♠7.

<<<
So you should plan to ruff the fourth \C in dummy.   [NEXT]
===
So you should plan to ruff the fourth \C in dummy.

[PLAY W:HA,N:H3,E:H6,S:HJ,W:HK,N:H5,E:H7,S:HQ,W:HT,N:H9,E:H8,S:ST,S:CA,W:C9,N:C2,E:C5,S:CK,W:CQ,N:C4,E:C8,S:C3,W:H4,N:C7,E:CJ] [showcards E:CT S:C6 W:S7]

You ruff the third \H, cash the \C A K and give up a \C to East, West discarding a \H. East leads his last \C, you follow and West ruffs with the \S7. Which card do you play from dummy? [choose-card S9]
>>>

## Trumpmgmt 15

Ruff the third heart and duck a club before drawing two rounds of trumps.

<<<
So you should plan to ruff the fourth \C in dummy.   [NEXT]
===
So you should plan to ruff the fourth \C in dummy.

[PLAY W:HA,N:H3,E:H6,S:HJ,W:HK,N:H5,E:H7,S:HQ,W:HT,N:H9,E:H8,S:ST]

You ruff the third \H. Which card do you lead now? [choose-card any:C6,C3]

[showcards W:C9 N:C2 E:C5]

West wins with the \C9.
>>>

## Trumpmgmt 16

Win the ♣A in dummy, cash the ♥K, then finesse the ♥J for a club discard.

<<<
What does that leave you? [NEXT]
===
What does that leave you?

[PLAY W:CK,N:CA,E:C7,S:C4]

You win the \CA in dummy. Which card do you lead from dummy? [choose-card HK]

[showcards E:H3 S:H2 W:H4]

Everyone follows low. [NEXT]

[PLAY E:H3,S:H2,W:H4]

Which card do you lead from dummy? [choose-card H6]

[showcards E:H8]

East plays low. Which card do you play? [choose-card HJ]

[showcards W:H5]
>>>

## Trumpmgmt 17

Win the heart in dummy, lead a spade honour and discard a club loser on it.

<<<
South is to play 4\H. West leads the \H3.
===
[showcards W:H3] South is to play 4\H. West leads the \H3.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:HQ,HJ]
>>>

<<<
Losers:
===
[showcards E:S2 S:H2] East discards a \S and you play the \H2.

Losers:
>>>

<<<
But dummy has some nice \Ss. Can you use them?   [NEXT]
===
But dummy has some nice \Ss. Can you use them?

[PLAY W:H3,E:S2,S:H2]

Which card do you lead from dummy? [choose-card any:SQ,SJ,ST]

[showcards E:S4]

East plays low. Which card do you play? [choose-card any:C7,C5]

[showcards W:SA]
>>>

## Trumpmgmt 18

Win the ♥A, cash one trump, and unblock the ♦A-Q before crossing to dummy's ♠K.

<<<
Make a Plan, then click NEXT. [NEXT]
===
[showcards W:HK N:H2 E:H3] South is to play 4\S. West leads the \HK, dummy plays the \H2 and East the \H3. Make a Plan, then play a card from your hand. [choose-card HA]

[PLAY W:HK,N:H2,E:H3,S:SA,W:S3,N:S6,E:S2]

You win the \HA and cash the \SA. Which card do you lead now? [choose-card any:DA,DQ]

[showcards W:D4]

West plays low. [NEXT]
>>>

## Trumpmgmt 19

Ruff the spade in dummy, then duck a round of trumps.

<<<
South is to play 6\H. West leads the \SQ.
===
[showcards W:SQ] South is to play 6\H. West leads the \SQ.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:HT,H9,H6]
>>>

<<<
Losers:
===
[showcards E:S8 S:S2] East plays the \S8 and you the \S2.

Losers:
>>>

<<<
There <b>IS</b> a way around the problem.  [NEXT]
===
There <b>IS</b> a way around the problem.

[PLAY W:SQ,E:S8,S:S2]

Which card do you lead from dummy? [choose-card any:HT,H9,H6]

[showcards E:H5]

East plays low. Which card do you play? [choose-card any:H8,H7,H4]

[showcards W:HJ]

West wins with the \HJ.
>>>

## Trumpmgmt 20

Take only the two top spades you need, then the minor aces, before the cross-ruff.

<<<
So you win the \SA, then take the \SK, then . . . what? [NEXT]
===
So you win the \SA, then take the \SK, then . . . what?

[PLAY W:SJ,N:SA,E:S5,S:S2,N:SK,E:S6,S:S4,W:S3]

Which card do you lead from dummy? [choose-card any:DA,C5]
>>>

## Eliminations 1

The throw-in: after eliminating clubs, lead a heart.

<<<
With all the eliminations completed you are ready for the throw-in. Lead a \H from either hand. One of the defenders will win, (you don't care which), and will be end-played.
===
With all the eliminations completed you are in your hand. Which card do you lead? [choose-card H3]

[showcards W:HJ N:H6 E:HK]

The throw-in: a \H from either hand. One of the defenders wins (you don't care which), and is end-played.
>>>

<<<
[PLAY N:H6,S:H3]
===
[PLAY W:HJ,N:H6,E:HK]
>>>

## Eliminations 2

The throw-in: after eliminating clubs, lead the small heart.

<<<
The eliminations are complete and it is time for the throw-in. Play the small \H from whichever hand you are in. This will be taken by one of the defenders.
===
The eliminations are complete and you are in your hand. Which card do you lead? [choose-card H3]

[showcards W:HJ N:H6 E:HK]

It is time for the throw-in: the small \H, taken by one of the defenders.
>>>

<<<
[PLAY N:H6,S:H3]
===
[PLAY W:HJ,N:H6,E:HK]
>>>

The reveal's [PLAY S:D6] names a card South doesn't hold (source data); it goes.

<<<
[PLAY S:D6]
===
>>>

## Eliminations 3

The throw-in with a heart. The source's [PLAY] lists named cards the hands don't hold, so
the trump and club tricks are corrected.

<<<
[PLAY N:SK,N:S4,N:H4,N:CK,N:C2,S:SA,S:S3,S:HA,S:CQ]
===
[PLAY N:SK,N:S4,N:H4,S:SA,S:S3,S:HA]
>>>

<<<
[PLAY N:CQ,N:CJ,N:C8,S:CA,S:CK,S:C5]
===
[PLAY N:CK,N:C8,N:C2,S:CA,S:CQ,S:C5]
>>>

<<<
Now execute the throw-in by leading a \H from either hand.
===
You are in your hand. Which card do you lead now? [choose-card H3]

[showcards W:HJ N:H6 E:HK]

You execute the throw-in by leading a \H.
>>>

<<<
[PLAY N:H6,S:H3]
===
[PLAY W:HJ,N:H6,E:HK]
>>>

## Eliminations 4

The throw-in: lead a spade.

<<<
Execute the throw-in by leading a \S.
===
Which card do you lead now? [choose-card any:S8,S6,S5]

[showcards W:S4 N:S3 E:ST]

You execute the throw-in by leading a \S.
>>>

<<<
[PLAY N:S3,S:S5]
===
[PLAY W:S4,N:S3,E:ST]
>>>

## Eliminations 5

Exit with a heart rather than guessing the clubs.

<<<
Now exit with a \H. The defenders win this and take another \H trick, leaving this position.
===
Which card do you lead now? [choose-card any:HT,H4]

[showcards W:H5 N:H7 E:HK]

You exit with a \H. The defenders win this and take another \H trick, leaving this position.
>>>

<<<
[PLAY N:HQ,N:H7,S:HT,S:H4]
===
[PLAY N:HQ,N:H7,S:HT,S:H4,W:H5,E:HK]
>>>

## Eliminations 6

The throw-in: a spade to East's master ♠Q.

<<<
You are ready for the throw-in. Play a \S to East's \SQ.
===
You are ready for the throw-in. Which card do you lead? [choose-card any:S8,S7]

[showcards W:C3 N:S6 E:SQ]

A \S to East's \SQ.
>>>

<<<
[showcards N:ST,CK,CT,C2 S:S8,CA,CJ,C7]
===
>>>

<<<
[PLAY N:S6,S:S7]
===
[PLAY W:C3,N:S6,E:SQ]
>>>

## Eliminations 7

After the ♦K and ♦A, lead the ♦J as the throw-in.

<<<
Eliminate \Ds by playing \DK, \DA, \DJ.
===
[PLAY N:DK,S:D7,N:D5,S:DA]

You cash the \DK and \DA. Which card do you lead now? [choose-card DJ]

[showcards W:DQ N:D9 E:D4]

You eliminate \Ds with the \DK, \DA and \DJ.
>>>

<<<
[showcards N:H8,CK,CT,C2 S:HJ,CA,CJ,C4]
===
>>>

<<<
[PLAY N:DK,N:D9,N:D5,S:DA,S:DJ,S:D7]
===
[PLAY W:DQ,N:D9,E:D4]
>>>

## Eliminations 8

Lead a club from hand and play dummy's ♣9 when West plays low.

<<<
At last it is time to play \Cs. Lead a \C from your hand and play dummy's \C9 if West plays low.
===
At last it is time to play \Cs. Which card do you lead? [choose-card any:C7,C6,C4,C3]

[showcards W:C5]

West plays low. Which card do you play from dummy? [choose-card C9]

[showcards E:CT]

A \C from your hand, playing dummy's \C9 when West plays low.
>>>

## Eliminations 9

The throw-in must be a diamond, not a spade.

<<<
The stage is now set for the throw-in. Be <b>SURE</b> to lead a \D for the throw-in, not a \S.
===
The stage is now set for the throw-in. Which card do you lead? [choose-card any:D8,D5]

[showcards W:DT N:D2 E:D3]

Be <b>SURE</b> to lead a \D for the throw-in, not a \S.
>>>

<<<
[PLAY N:D2,S:D5]
===
[PLAY W:DT,N:D2,E:D3]
>>>

## Eliminations 10

Enter dummy with a trump, then let dummy's ♣10 ride.

<<<
You want to play the first \C from dummy, so enter dummy with a trump.
===
You want to play the first \C from dummy. Which card do you lead? [choose-card any:DT,D8]

[showcards W:H8 N:DJ E:S3]

You enter dummy with a trump.
>>>

<<<
[PLAY N:DJ,S:D8]
===
[PLAY W:H8,N:DJ,E:S3] [showcards N:CT E:C6]
>>>

<<<
Play the \CT from dummy and let it ride if East does not produce the \CQ or \CK.
===
Dummy leads the \C10 and East plays low. Which card do you play? [choose-card any:C9,C3]

[showcards W:CQ]

Play the \C10 from dummy and let it ride if East does not produce the \CQ or \CK.
>>>

## Eliminations 11

The throw-in: a club from dummy.

<<<
You have done all the eliminating, time to throw in somebody. Play a \C.
===
You have done all the eliminating, time to throw in somebody. Which card do you lead from dummy? [choose-card any:C8,CJ,CQ]

[showcards E:H2 S:C6 W:CK]

You play a \C to throw West in.
>>>

<<<
[PLAY N:C8,S:C6]
===
[PLAY E:H2,S:C6,W:CK]
>>>

## Eliminations 12

From dummy, lead a club and insert the ♣10.

<<<
Conveniently in dummy, you play a \C and insert the \CT if East plays low.
===
Conveniently you are in dummy. Which card do you lead from dummy? [choose-card any:C7,C6,C3]

[showcards E:C2]

East plays low. Which card do you play? [choose-card CT]

[showcards W:CJ]

You play a \C from dummy and insert the \C10 when East plays low.
>>>

<<<
[showcards N:HA,H6,C7,C6 S:HK,HQ,CA,CQ]
===
>>>

<<<
[PLAY N:C3,S:CT]
===
[PLAY E:C2,W:CJ]
>>>

## Eliminations 13

Lead dummy's ♠J and let it ride: West wins and is endplayed.

<<<
You now play the \SJ from dummy and let it ride when East follows with a low card.
===
Which card do you lead from dummy? [choose-card any:SJ,ST]

[showcards E:S3]

East plays low. Which card do you play? [choose-card any:S9,S6]

[showcards W:SQ]

You play the \SJ from dummy and let it ride when East follows with a low card.
>>>

<<<
[PLAY N:SJ,S:S6]
===
[PLAY E:S3,W:SQ]
>>>

## Eliminations 14

The throw-in with the master trump: lead a trump.

<<<
Now you administer the coup de gras, you lead a trump.
===
Now you administer the coup de grace. Which card do you lead from dummy? [choose-card any:ST,S7]

[showcards E:H3 S:S6 W:SQ]

You lead a trump.
>>>

<<<
[showcards N:ST,DJ,D5,D4 S:SJ,DQ,D8,D7]
===
>>>

<<<
[PLAY N:S7,S:S6]
===
[PLAY E:H3,S:S6,W:SQ]
>>>

## Eliminations 15

The throw-in with a spade; then don't play the ♦J on East's diamond lead.

<<<
Now execute the throw-in by leading a \S.
===
Which card do you lead now? [choose-card S4]

[showcards W:S2 N:S5 E:S8]

You execute the throw-in by leading a \S.
>>>

<<<
[PLAY N:S5,S:S4]
===
[PLAY W:S2,N:S5,E:S8]
>>>

<<<
<b>DO NOT PLAY THE JACK!</b>
===
[showcards E:D5]

East leads a small \D. Which card do you play? [choose-card D3]

[showcards W:DQ]

<b>DO NOT PLAY THE JACK!</b>
>>>

## Eliminations 16

On the ♥J, discard a diamond from dummy so both hands are out of diamonds.

<<<
Now eliminate \Hs from your hand and dummy by playing \HK, \HA, \HJ.<b>BUT BE CAREFUL!</b> On the \HJ you must discard a \D from dummy so both of you will be out of \Ds at the throw-in.
===
[PLAY N:HK,S:H5,N:HQ,S:HA] [showcards S:HJ W:H8]

You eliminate the \Hs: the \HK, the \HQ overtaken by your \HA, then the \HJ. Which card do you play from dummy? [choose-card any:D9,D8]

[showcards E:H6]

<b>BE CAREFUL!</b> On the \HJ you must discard a \D from dummy so both of you will be out of \Ds at the throw-in.
>>>

<<<
[PLAY N:HK,N:HQ,N:D8,S:HA,S:HJ,S:H5]
===
[PLAY S:HJ,W:H8,E:H6]
>>>

## Eliminations 17

Don't ruff West's good heart: discard a club from dummy and a diamond from hand.

<<<
So he leads one of them, and you <b>DO NOT RUFF</b>. Instead you discard a \C from dummy and a \D from your own hand.
===
[showcards W:HQ]

So he leads the \HQ. Which card do you play from dummy? [choose-card C6]

[showcards E:C2]

Which card do you play? [choose-card any:D4,D3]

You <b>DO NOT RUFF</b>. Instead you discard a \C from dummy and a \D from your hand.
>>>

## Eliminations 18

From dummy, lead the ♦J and discard a heart: West wins and is endplayed.

<<<
So here you are in dummy. Do you finesse the \H now? Of course not. You play the \DJ and discard a small \H from your hand.
===
So here you are in dummy. Do you finesse the \H now? Which card do you lead from dummy? [choose-card DJ]

[showcards E:D4]

East plays low. Which card do you play? [choose-card H3]

[showcards W:DQ]

Of course not. You play the \DJ and discard a small \H from your hand.
>>>

## Eliminations 19

Throw West in with the ♣10.

<<<
Now throw West in (you hope!) with the \CT.
===
[PLAY N:S8,N:HQ,S:H5,S:H2]

You are back in your hand. Which card do you lead now? [choose-card CT]

[showcards W:CJ N:C8 E:C2]

Now throw West in (you hope!) with the \C10.
>>>

<<<
[PLAY N:S8,N:HQ,N:C8,S:H5,S:H2,S:CT]
===
[PLAY W:CJ,N:C8,E:C2]
>>>

## Eliminations 20

Duck the diamonds in dummy; at the end, discard a club on the ♦A instead of ruffing.

<<<
Make a Plan, then click NEXT. [NEXT]
===
[showcards W:DQ] Make a Plan, then choose dummy's card to this trick. [choose-card any:D6,D3]

[showcards E:D2 S:D7]

East plays the \D2 and you the \D7. [NEXT]

[PLAY W:DQ,E:D2,S:D7] [showcards W:DJ]

West continues with the \DJ. Which card do you play from dummy? [choose-card any:D6,D3]

[showcards E:D5 S:SQ]

East plays low and you ruff with the \SQ.
>>>

<<<
[PLAY N:D6,N:D3,S:SQ,S:D7]
===
[PLAY W:DJ,E:D5,S:SQ]
>>>

<<<
You are in dummy, just where you want to be. Play the \DK, and when East plays the \DA don't ruff but instead discard a \C from your hand.
===
You are in dummy, just where you want to be. Which card do you lead from dummy? [choose-card DK]

[showcards E:DA]

East plays the \DA. Which card do you play? [choose-card any:C7,C6,C4]

[showcards W:DT]

Play the \DK, and when East plays the \DA don't ruff but instead discard a \C from your hand.
>>>

<<<
[showcards N:SJ,CK,C5,C3 S:S6,S3,C7,C6]
===
>>>

<<<
[PLAY N:DK,S:C4]
===
[PLAY E:DA,W:DT]
>>>

## Eliminations 21

Win the ♠A, cross with the ♦J to the ♦K, and discard the ♠J on the ♦A.

<<<
South plays 6\H. West leads the \S5, East plays the \SK.
===
[showcards W:S5 N:S6 E:SK] South plays 6\H. West leads the \S5, dummy plays the \S6 and East the \SK.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card SA]

[PLAY W:S5,N:S6,E:SK]

Which card do you lead now? [choose-card DJ]

[showcards W:D7 N:DK E:D2]

Dummy wins the \DK. [NEXT]

[PLAY W:D7,N:DK,E:D2] [showcards N:DA E:D3]

Dummy leads the \DA and East follows. Which card do you play? [choose-card SJ]

[showcards W:D9]
>>>

<<<
[PLAY N:S6,N:DA,N:DK,S:SA,S:SJ,S:DJ]
===
[PLAY N:DA,E:D3,W:D9]
>>>

## Eliminations 22

Lead a spade and duck West's ♠10 in dummy: West must lead into the ♠A-Q.

<<<
[showcards N:SA,S7,S2 S:SQ,S9,S4]
===
>>>

<<<
Keeping your fingers crossed that West must win the next trick you play the \S9. West puts on the \ST, you play low in dummy, and East (thankfully) discards a \H.
===
Keeping your fingers crossed that West must win the next trick, which card do you lead? [choose-card any:S9,S4]

[showcards W:ST]

West puts on the \S10. Which card do you play from dummy? [choose-card any:S7,S2]

[showcards E:H2]

East (thankfully) discards a \H.
>>>

<<<
[showcards N:SA,S7 S:SQ,S4]
===
>>>

<<<
[PLAY N:S2,S:S9]
===
[PLAY W:ST,E:H2]
>>>

## Eliminations 23

The throw-in: dummy's ♠7 to East, who has only spades left.

<<<
[showcards N:S7,HQ,D5,D4 S:S8,HK,HT,D7]
===
>>>

<<<
Play dummy's \S7. East will win, but he has nothing left but \Ss.
===
Which card do you lead from dummy? [choose-card S7]

[showcards E:S9 S:S8 W:CT]

Dummy's \S7: East wins, but he has nothing left but \Ss.
>>>

## Eliminations 24

Eliminate and throw in with the diamonds from dummy.

<<<
Next eliminate \Ds by playing \DA then another \D. This does the elimination and throw-in at the same time.
===
Which card do you lead from dummy? [choose-card any:DA,D2]

[showcards E:D4]

Next eliminate \Ds by playing \DA then another \D. This does the elimination and throw-in at the same time.
>>>

<<<
[PLAY N:DA,N:D2,S:DQ,S:D7]
===
[PLAY N:DA,N:D2,S:DQ,S:D7,E:D4]
>>>

## Eliminations 25

The throw-in: a low spade from both hands, won by East.

<<<
Now play a low \S from both hands. West doesn't follow suit as East wins with a small card.
===
Which card do you lead from dummy? [choose-card any:S5,S2]

[showcards E:S6 S:S4 W:H4]

A low \S from both hands. West doesn't follow suit as East wins with a small card.
>>>

<<<
[PLAY N:S2,S:S4]
===
[PLAY E:S6,S:S4,W:H4]
>>>

## Squeeze 1

The squeeze card: the ♣A.

<<<
Now you play the \CA.
===
Which card do you lead now? [choose-card CA]

[showcards W:C8 N:C4 E:S8]

Now you play the \CA.
>>>

<<<
[PLAY E:SJ,E:ST,E:S9,E:S8,E:HJ,W:S7,W:S6,W:CJ,W:C9,W:C8]
===
[PLAY E:SJ,E:ST,E:S9,E:S8,E:HJ,W:S7,W:S6,W:CJ,W:C9,W:C8,N:C4]
>>>

## Squeeze 3

Rectify the count by ducking the ♣K; then the squeeze card ♥A with dummy's club discard.

<<<
The problem is that you have to <b>RECTIFY THE COUNT</b>. [NEXT]
===
The problem is that you have to <b>RECTIFY THE COUNT</b>. Which card do you play from dummy? [choose-card any:C8,C6]

[showcards E:C7 S:C5]
>>>

<<<
[PLAY N:CA,N:C6,E:C7,E:C3,S:CT,S:C5,W:CK,W:CQ]
===
[PLAY N:CA,E:C7,E:C3,S:CT,S:C5,W:CK,W:CQ]
>>>

<<<
Here is the situation just as you are about to play the Squeeze Card, the \HA.
===
Here is the situation. Which card do you lead? [choose-card HA]

[showcards W:HT]

West follows. Which card do you play from dummy? [choose-card any:C8,C6]

[showcards E:D4]

The Squeeze Card is the \HA.
>>>

<<<
You will toss dummy's \C8 and East
===
You toss dummy's last small \C and East
>>>

## Squeeze 4

Duck the ♠K to rectify the count; then the squeeze card ♣A, dummy discarding a spade.

<<<
South is to play 6NT. West leads the \SK.
===
[showcards W:SK N:S2 E:S5] South is to play 6NT. West leads the \SK, dummy plays the \S2 and East the \S5.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card S3]
>>>

<<<
[showcards N:S7,S4,HA,H3 E:S9,S8,S6,C8 S:SA,SJ,H7,CA W:SQ,ST,HJ,H9]
===
>>>

<<<
When you now play your \CA, discarding a \S from dummy, West is squeezed.
===
Which card do you lead now? [choose-card CA]

[showcards W:H9]

West discards the \H9. Which card do you play from dummy? [choose-card any:S7,S4]

[showcards E:C8]

When you play your \CA, discarding a \S from dummy, West is squeezed.
>>>

## Squeeze 5

Duck the ♥K to rectify the count; then the squeeze card, dummy's ♦J.

<<<
South is to play 6NT. West leads the \HK.
===
[showcards W:HK N:H2 E:H5] South is to play 6NT. West leads the \HK, dummy plays the \H2 and East the \H5.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card any:H8,HT]
>>>

<<<
[PLAY N:H4,N:H2,E:H5,E:D2,S:HA,S:H8,W:HK,W:HQ]
===
[PLAY N:H4,N:H2,E:H5,E:D2,S:HA,W:HK,W:HQ]
>>>

<<<
Now for the squeeze. Play dummy's \DJ and discard your \H10.
===
Now for the squeeze. Which card do you lead from dummy? [choose-card DJ]

[showcards E:C4]

East discards. Which card do you play? [choose-card any:HT,H8]

[showcards W:H9]

Play dummy's \DJ and discard your last small \H.
>>>

## Squeeze 6

Let the ♥K hold; then the squeeze card ♦7, discarding dummy's useless ♠Q.

<<<
South is to play 6\D. West leads the \HK.
===
[showcards W:HK] South is to play 6\D. West leads the \HK.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then choose dummy's card to this trick. [choose-card any:H8,H2]
>>>

<<<
[PLAY N:H2,N:D4,E:H3,E:DT,S:H4,S:DA,W:HK,W:D2]
===
[PLAY N:D4,E:H3,E:DT,S:H4,S:DA,W:HK,W:D2]
>>>

<<<
[showcards N:SQ,HA,H8 E:SJ,S9,H9 S:HJ,H7,D7 W:SK,HQ,HT]
===
>>>

<<<
But when you play the \D7 he is squeezed.
===
Which card do you lead now? [choose-card D7]

[showcards W:HT]

West discards the \H10. Which card do you play from dummy? [choose-card SQ]

[showcards E:S9]

When you play the \D7 he is squeezed.
>>>

## Squeeze 7

The Vienna Coup (dummy's ♦A first); then the squeeze card ♥6, discarding dummy's ♦6.

<<<
You plan to squeeze East by running the long \Hs in your hand, but the problem is that the \DQ is not a Threat card yet. To make it a Threat you need to unblock dummy's \DA. So play the \DA, then pull trumps with the \H A Q.
===
You plan to squeeze East by running the long \Hs in your hand. Which card do you lead from dummy? [choose-card DA]

[showcards E:DT S:D7 W:D3]

The \DQ was not a Threat card yet: to make it a Threat you had to unblock dummy's \DA. Then you pull trumps with the \H A Q.
>>>

<<<
[showcards N:SA,SK,SJ,D6 E:SQ,ST,S9,DK S:S8,S7,H6,DQ W:S6,S5,D9,D8]
===
>>>

<<<
Play the \H6 and throw dummy's \D6.
===
Which card do you lead now? [choose-card H6]

[showcards W:D8]

West discards. Which card do you play from dummy? [choose-card D6]

[showcards E:S9]

Play the \H6 and throw dummy's \D6.
>>>

## Squeeze 8

Give up a heart to rectify the count; the Vienna Coup with dummy's ♠A; the squeeze card ♣7.

<<<
In case the squeeze becomes necessary you should rectify the count, so you win the first trick, pull trumps in two rounds, then give up a \H trick. [NEXT]
===
[PLAY W:HK,N:H3,E:H2,S:HA,S:C3,W:C4,N:CK,E:S3,N:CQ,E:S4,S:C2,W:C8]

You win the first trick and pull trumps in two rounds, ending in dummy. Which card do you lead from dummy? [choose-card H9]

[showcards E:HT S:H4 W:HJ]

In case the squeeze becomes necessary you rectify the count by giving up a \H.
>>>

<<<
[PLAY N:H9,N:H3,N:CK,N:CQ,E:S4,E:S3,E:HT,E:H2,S:HA,S:H4,S:C3,S:C2,W:HK,W:HJ,W:C8,W:C4]
===
[PLAY E:HT,S:H4,W:HJ]
>>>

<<<
You now make the key play of taking dummy's \SA before running three rounds of \Cs.
===
[PLAY W:D9,N:D6,E:D3,S:DQ]

Which card do you lead now? [choose-card S7]

[showcards W:S5]

West plays low. Which card do you play from dummy? [choose-card SA]

[showcards E:S8]

The key play: taking dummy's \SA before running three rounds of \Cs.
>>>

<<<
[showcards N:S2,DA,DK,D8 E:SK,DJ,DT,D7 S:SQ,D5,D4,C7 W:SJ,ST,HQ,D2]
===
>>>

<<<
[PLAY N:SA,N:D6,N:CT,N:C6,N:C5,E:S9,E:S8,E:H8,E:H6,E:D3,S:S7,S:DQ,S:CA,S:CJ,S:C9,W:S6,W:S5,W:H7,W:H5,W:D9]
===
[PLAY N:SA,N:CT,N:C6,N:C5,E:S9,E:S8,E:H8,E:H6,S:S7,S:CA,S:CJ,S:C9,W:S6,W:S5,W:H7,W:H5]
>>>

<<<
As you see, East was able to find discards on your first three trump leads, but when you play the \C7 and discard dummy's \S2 he is squeezed.
===
Which card do you lead now? [choose-card C7]

[showcards W:SJ]

West discards. Which card do you play from dummy? [choose-card S2]

[showcards E:SK]

East was able to find discards on your first three trump leads, but when you play the \C7 and discard dummy's \S2 he is squeezed.
>>>

## Squeeze 9

Test the clubs before the spades; then the squeeze card ♦A.

<<<
Win the \DK and (<b>IMPORTANT!</b>) test the \Cs first by playing \C A K Q.
===
[PLAY W:DQ,N:D5,E:D8,S:DK]

You win the \DK. Which card do you lead now? [choose-card any:CA,CK,CQ]

[showcards W:C7 N:C3 E:C4]

Win the \DK and (<b>IMPORTANT!</b>) test the \Cs first by playing \C A K Q.
>>>

<<<
[PLAY N:S2,N:D5,N:C6,N:C3,E:D8,E:C9,E:C8,E:C4,S:DK,S:CA,S:CK,S:CQ,W:DQ,W:D2,W:CT,W:C7]
===
[PLAY N:S2,N:C6,N:C3,E:C9,E:C8,E:C4,S:CA,S:CK,S:CQ,W:D2,W:CT,W:C7]
>>>

<<<
Play your \DA. East must give up.
===
Which card do you lead now? [choose-card DA]

[showcards W:D4 N:D7 E:S6]

Play your \DA. East must give up.
>>>

## Squeeze 10

Take the clubs first; then the squeeze card ♠J, discarding dummy's ♦9 when West keeps the ♦10.

<<<
You are going to now run your black suit winners, but take the \Cs first so you can be playing winners from your hand when you squeeze West.
===
Which card do you lead now? [choose-card any:CT,C8,C7,C4]

[showcards W:C3]

You are going to run your black suit winners, taking the \Cs first so you can be playing winners from your hand when you squeeze West.
>>>

<<<
[showcards N:HA,HK,H8,D9 E:S9,HJ,H4,D6 S:SJ,H9,H5,H3 W:HQ,HT,H7,DT]
===
>>>

<<<
Play your \SJ and watch what West discards.
===
Which card do you lead now? [choose-card SJ]

[showcards W:H7]

West discards the \H7, holding on to the \D10. Which card do you play from dummy? [choose-card D9]

[showcards E:S9]

Play your \SJ and watch what West discards.
>>>

## Squeeze 11

The Vienna Coup (a club to dummy's ♣A); then the squeeze card ♦3, discarding dummy's ♣10.

<<<
The solution is the Vienna Coup. Play a \C to the \CA at trick 3.
===
Which card do you lead now? [choose-card any:C8,C3]

[showcards W:C6]

West plays low. Which card do you play from dummy? [choose-card CA]

[showcards E:C2]

The solution is the Vienna Coup: a \C to the \CA at trick 3.
>>>

<<<
You play your \D3 and discard dummy's \CT.
===
Which card do you lead now? [choose-card D3]

[showcards W:HT]

West discards. Which card do you play from dummy? [choose-card CT]

[showcards E:S6]

You play your \D3 and discard dummy's \C10.
>>>

## Squeeze 12

The squeeze card ♥2, discarding dummy's ♦6.

<<<
Play your \H2 and dump dummy's \D6.
===
Which card do you lead now? [choose-card H2]

[showcards W:D9]

West discards. Which card do you play from dummy? [choose-card D6]

[showcards E:C3]

Play your \H2 and dump dummy's \D6.
>>>

## Squeeze 13

Win the ♥A; discard the useless ♠7 on dummy's last diamond; then dummy's ♠5 to your ♠K.

<<<
South is to play 7NT. West leads the \HK.
===
[showcards W:HK N:H6 E:H2] South is to play 7NT. West leads the \HK, dummy plays the \H6 and East the \H2.
>>>

<<<
Make a Plan, then click NEXT. [NEXT]
===
Make a Plan, then play a card from your hand. [choose-card HA]
>>>

<<<
When you play the \D5 East must keep both \Ss to guard against your \S7.
===
Which card do you lead from dummy? [choose-card D5]

[showcards E:C6]

East discards the \C6. Which card do you play? [choose-card S7]

[showcards W:HT]

When you play the \D5 East must keep both \Ss to guard against your \S7.
>>>

<<<
[showcards N:S5,HJ,CK,C7 E:SJ,ST,CQ,CT S:SK,CA,C8,C4 W:HQ,CJ,C9,C5]
===
>>>

<<<
Play dummy's \S5 to your \SK.
===
Which card do you lead from dummy? [choose-card S5]

[showcards E:ST S:SK W:C5]

Play dummy's \S5 to your \SK.
>>>

## Squeeze 14

Dummy's ♦4 squeezes East, and your ♠7 discard then squeezes West.

<<<
[showcards N:S9,H6,D4,C8 E:HQ,H9,H8,CJ S:S7,HA,HK,H5 W:SJ,HJ,HT,H7]
===
>>>

<<<
Play dummy's \D4.
===
Which card do you lead from dummy? [choose-card D4]

[showcards E:H8]

East discards a \H. Which card do you play? [choose-card S7]

[showcards W:H7]

You play dummy's \D4.
>>>

## Squeeze 15

Ruff a spade to transfer the guard to West; then the squeeze card ♥A, dummy discarding
whichever black card is useless.

<<<
Play dummy's \HQ and \H10, then ruff a \S, then pull the last trump.
===
[PLAY N:HQ,E:H2,S:H8,W:H4,N:HT,E:H5,S:H9,W:H6]

You draw two rounds of trumps with dummy's \HQ and \H10. Which card do you lead from dummy? [choose-card S8]

[showcards E:SQ S:HJ W:S9]

East plays the \SQ and you ruff. Then you pull the last trump.
>>>

<<<
[PLAY N:S8,N:HQ,N:HT,N:C5,E:SQ,E:H7,E:H5,E:H2,S:HK,S:HJ,S:H9,S:H8,W:S9,W:S4,W:H6,W:H4]
===
[PLAY N:S8,N:C5,E:SQ,E:H7,S:HK,S:HJ,W:S9,W:S4]
>>>

<<<
[showcards N:ST,CA,C9 E:DJ,D9,CJ S:HA,C8,C6 W:SJ,CQ,CT]
===
>>>

<<<
So you play your \HA and West must give up one of his guards.
===
Which card do you lead now? [choose-card HA]

[showcards W:CT]

West discards the \C10, holding on to the \SJ. Which card do you play from dummy? [choose-card ST]

[showcards E:D9]

You play your \HA and West must give up one of his guards.
>>>

## Squeeze 16

Lead a spade back at trick 2 (the suicide squeeze); discard clubs; then the squeeze card ♣A.

<<<
But how can you squeeze him? [NEXT]
===
But how can you squeeze him?

[PLAY N:ST,E:S5,S:S4,W:S3]

Dummy's \S10 won the first trick. Which card do you lead from dummy? [choose-card SQ]

[showcards E:S6 S:S7 W:SK]
>>>

<<<
[PLAY N:ST,E:S5,S:S4,W:S3]

[clear-commentary]

The answer
===
[clear-commentary]

The answer
>>>

<<<
You discard 2 \Ds from dummy and a \C from your hand.
===
[PLAY W:SA,N:D6,E:S8,S:SJ] [showcards W:S9 N:D3 E:C9]

West continues with the \SA and the \S9; dummy discards two \Ds. Which card do you discard? [choose-card any:C7,C3]

You discard 2 \Ds from dummy and a \C from your hand.
>>>

<<<
[PLAY N:D6,N:D3,E:S8,E:C9,S:SJ,S:C3,W:SA,W:S9]
===
[PLAY W:S9,N:D3,E:C9]
>>>

<<<
In your hand with the \CK, you now play the \CA.
===
You are in your hand with the \CK. Which card do you lead now? [choose-card CA]

[showcards W:C6 N:C8 E:D4]

You play the \CA.
>>>

## Squeeze 17

Ruff a diamond to make the ♦J a threat; then the squeeze card ♣8, discarding dummy's ♠J.

<<<
Think squeeze instead. Ruff a \D. This turns the \DJ into a Threat card against East's \DQ.
===
Think squeeze instead. Which card do you lead from dummy? [choose-card any:D8,D7]

[showcards E:DT S:C7 W:S6]

You ruff a \D. This turns the \DJ into a Threat card against East's \DQ.
>>>

<<<
[PLAY N:D7,E:DT,S:C7,W:S6]
===
[PLAY E:DT,S:C7,W:S6] [showcards S:CJ W:S9]

You play your \CJ. Which card do you play from dummy? [choose-card any:D8,D7]

[showcards E:ST]
>>>

<<<
[showcards N:SJ,HK,H7,DJ E:HJ,HT,H2,DQ S:HA,H6,H3,C8 W:SQ,HQ,H9,H8]
===
>>>

<<<
[PLAY N:H4,N:D8,E:ST,E:S7,S:CJ,S:C9,W:S9,W:H5]
===
[PLAY N:H4,E:ST,E:S7,S:CJ,S:C9,W:S9,W:H5]
>>>

<<<
You are there. Play your \C8.
===
You are there. Which card do you lead now? [choose-card C8]

[showcards W:H8]

West gives up the \H8. Which card do you play from dummy? [choose-card SJ]

[showcards E:H2]

Your \C8 does it.
>>>

## Squeeze 18

Duck a diamond to rectify the count; a diamond to dummy's ♦K; then dummy's ♥J squeezes East.

<<<
So you play a low \D from each hand.
===
Which card do you lead now? [choose-card any:D6,D3]

[showcards W:DT]

West plays the \D10. Which card do you play from dummy? [choose-card any:D7,D5]

[showcards E:D4]

So you play a low \D from each hand.
>>>

<<<
[PLAY N:D5,E:D4,S:D3,W:DT]
===
[PLAY E:D4,W:DT]
>>>

<<<
Now play a small \D to dummy's \DK. [NEXT]
===
Which card do you lead now? [choose-card any:D6,D3]

[showcards W:S3]

West discards. Which card do you play from dummy? [choose-card DK]

[showcards E:D9]

A small \D to dummy's \DK. [NEXT]
>>>

<<<
[showcards N:HJ,D7,C8,C6 E:DQ,DJ,CJ,CT S:DA,D8,CQ,C4 W:SJ,S8,S6,S5]
===
>>>

<<<
[PLAY N:DK,E:D9,S:D6,W:S3]
===
[PLAY E:D9,W:S3]
>>>

<<<
Play dummy's \HJ.
===
Which card do you lead from dummy? [choose-card HJ]

You play dummy's \HJ.
>>>

## Squeeze 19

Let West hold the first trick; then the squeeze card ♥5, discarding dummy's ♠K.

<<<
What is your first act? [NEXT]
===
What is your first act? Which card do you play from dummy? [choose-card any:D8,D5]

[showcards E:D9 S:D3]
>>>

<<<
[PLAY N:H4,N:D5,E:H2,E:D9,S:HQ,S:D3,W:H3,W:DK]
===
[PLAY N:H4,E:H2,E:D9,S:HQ,S:D3,W:H3,W:DK]
>>>

<<<
[showcards N:SK,DA,D8 E:SJ,S8,D4 S:H5,DJ,D6 W:SA,DQ,DT]
===
>>>

<<<
At last you play the \H5, and West is done, he just doesn't know it yet.
===
Which card do you lead now? [choose-card H5]

[showcards W:DT]

West bares his \DQ. Which card do you play from dummy? [choose-card SK]

[showcards E:S8]

At last you play the \H5, and West is done, he just doesn't know it yet.
>>>

## Squeeze 20

The Vienna Coup (dummy's ♦A); then the squeeze card ♠2, discarding dummy's ♣4.

<<<
You do that by playing the \DA immediately, a Vienna Coup.
===
Which card do you lead now? [choose-card D3]

[showcards W:D4]

West plays low. Which card do you play from dummy? [choose-card DA]

[showcards E:D8]

You play the \DA immediately, a Vienna Coup.
>>>

<<<
[showcards N:CA,CJ,C4 E:DK,CK,CT S:S2,DJ,CQ W:D6,C9,C8]
===
>>>

<<<
Play your \S2 and discard dummy's \C4.
===
Which card do you lead now? [choose-card S2]

[showcards W:C8]

West discards. Which card do you play from dummy? [choose-card C4]

[showcards E:CT]

Play your \S2 and discard dummy's \C4.
>>>
