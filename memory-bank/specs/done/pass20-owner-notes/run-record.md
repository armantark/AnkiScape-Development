# Pass 20 run record

What the build left for the owner: decisions made during the build that he has not approved, findings outside the tickets, and the checks that wait. The route is in `route.md`, and his answers are in `grill.md`. Worker reports, evidence and native screenshots: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/` on the Mac Studio.

## Measurements

Combat XP per card, 200 cards at 10x and 2,000 cards at 1x (12,000 ticks each), one seed, stocked fixture:

| Level, target | Old 10x | New 10x | New 1x x 10 |
|---|---:|---:|---:|
| 1, Man | 24.043 | 25.256 | 25.142 |
| 20, Hill giant | 75.918 | 76.379 | 80.683 |
| 40, Moss giant | 164.933 | 194.306 | 194.306 |
| 70, Fire giant | 468.909 | 493.355 | 493.755 |

Those rows predate the danger-stop fix for quest fights, which does not touch ordinary combat.

Quest fight carry, 64 seeds, 12 quests, levels 20, 40 and 60, speeds 10x and 20x, danger stops in both arms: carry off 297 deaths in 18,239 fights, carry on 294 in 18,122; paired difference -0.0000604, paired standard error 0.0000984. Before the danger-stop fix the same comparison gave 880 in 18,239 and 873 in 18,233, and 28,942 and 20,706 cards.

## Native check in real Anki (GPT-6.1 Terra, computer use)

`native/final-check/` at `eca6af1ed`: queue Up and Down, row click and start button, counts, search double click, Combat "bat" search (2/198), Adamant boots row, Moss giant bank run with "2 reviews remaining" then "1 review remaining", Demon Slayer's Silverlight switch and return, Jungle Potion in 15 reviews with "Jungle Potion complete. Next: Pick onions.". The tester called the run a fail for three reasons that are not defects: a "Switched to Bankstanding" dialog after the queue emptied, which answer 17 keeps; Clear was not exercised, because the queue was already empty, and tests cover it; the other appearance mode was not tested. Only the owner's play checks a kill with ticks left, Witch's House gloves and a Grand Exchange claim in real Anki; offscreen flows cover all three.

## Decisions made during the build, for the owner

1. A move in a paused or set-aside queue changes the order and starts nothing. Default: keep.
2. A move that starts an activity asks before it leaves a running minigame, as an add does. Default: keep.
3. An accepted add remembers only a typed count, so an untouched default keeps following supplies. Default: keep.
4. A Herblore row with no herbs stays disabled, so an empty Bank cannot pick a later step even when an earlier entry promises its herb. Default: keep; the owner's "not update even after you select it" can include this.
5. The Activities panel has no header Start, so a row held there has no button that starts it ahead of the queue. Default: keep.
6. Unselected gravestones keep their review-count expiry; only the chosen walk spends ticks. Default: keep.
7. Live quest combat now stops at the danger tick, a change that the Astra review asked for and that was not in the grill. It lowers deaths in quest fights. Default: keep.

## Findings outside the tickets (not fixed)

- Black mask (10) requires Defence 20 and Strength 10; period page oldid 5393767 says Defence 10, Strength 20, Combat 40.
- Shade robe item 546 has Prayer 9; the period page's 9 describes the set, and rev 742 gives 5.
- Barrows, Void knight, Ghostly, Penance and Flame gloves are absent from the equipment data.
- The five grimy Jungle Potion herbs have no icons. Adamant dart (p) and Steel arrow (p) have no period poisoned icon.
- Adamant boots do not drop from Mutated bloodvelds or Giant frogs, which the period page names.
- Dragon and gilded pickaxes have no acquisition route.
- Dropped from the item stops: Defender of Varrock, Hazeel Cult and Dealing with Scabaras, whose quests stop elsewhere; their briefs go to the Sol loop.
- `tests.native.test_session_bootstrap` fails on the Mac Studio with 16 failures at this branch and at base `85156cdc0`: `/Users/ArmanTarkhanian1/Library/Application: bad interpreter: Permission denied`, because a test shebang splits on the space in `Application Support`.
