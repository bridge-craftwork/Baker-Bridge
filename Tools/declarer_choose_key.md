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
