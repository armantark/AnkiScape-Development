# Pass 20 owner notes

The owner's Pass 20 play notes (2026-11-02), settled in a grill on 2026-11-03 and 2026-11-04. His notes and answers, word for word, are in `grill.md`, and they are the approval for exactly the changes this spec names, including the changes to existing screens. Code facts with citations, taken at `75f33bee9` (lines can have moved): `facts-queue.md`, `facts-small.md`, `facts-combat.md`. Quest stops, one row each: `quest-stop-scan.tsv`; its walker: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/scan/walk.py`. Terms: `GLOSSARY.md`.

## Problem Statement

The owner played Pass 19 in native Anki and hit these problems.

1. The queue has no reorder control.
2. "Train this skill" ahead of the queue ends at Bankstanding when it finishes. The queue does not continue, because a manual pause and a hand-started action share one flag.
3. Target clicks are unreliable while a queue entry runs on that skill. The click changes the Add record but not training, and the header button stays disabled. The count can show 0, can fail to follow a new target, and a failed 0 add is remembered.
4. A quest finished by hand stays in the queue.
5. Quest-complete dialogs interrupt a queue that continues, and they say questing "has been switched off".
6. Jungle Potion stalls on its first stage with no notice: reviews pile up grimy herbs, and cleaning is a separate hand action. Other quests have similar hand stops.
7. Witch's House stops for "Wear insulating gloves". Demon Slayer stops for "Wield Silverlight" in the same way.
8. Adamant boots and 20 other equipment items cannot be owned or traded, although their stats exist.
9. A double click in a search box selects one word.
10. Searching "bat" in Combat shows 198/198, because every Combat tooltip says "combat level".
11. Claiming a Grand Exchange offer moves the later offers.
12. Combat at 10x pays less than 10 times its 1x XP per card. A bank run costs two whole cards at every speed (12 ticks at 1x, 120 at 10x), and a kill that needs a bank run ends its card early. Rest and grave recovery have the same whole-card charge. A quest kill also ends its card.

## Solution

The behavior in `grill.md`, answers 1 to 21, in the owner's terms:

- The queue reorders with Up and Down. An action started ahead of it runs until it stops by itself, and the queue then continues. A queue change shows no dialog.
- A row click never changes what runs when a queue entry runs on that skill. The header button starts the pick ahead of the queue.
- Bank run, rest and grave recovery take fixed 2012 play time at every speed. The remaining ticks of a card pay first, and play continues in the same card.
- The quest does its own item work and puts on what a stage needs, as the 2012 player did during the quest.
- The 21 items exist. Search and Grand Exchange slots behave as a player expects.

## User Stories

1. As a player, I want Up and Down on each queue row, so that I can change the order without clearing the queue.
2. As a player, I want a new top entry to start at once and the old entry to keep its remaining count, so that a move means what it shows.
3. As a player, I want "Train this skill" to run my pick until it stops by itself and the queue to continue from its top entry, so that a detour costs no clicks.
4. As a player, I want a free pickup started ahead of the queue to run until I press Stop or add to the queue, and Stop to return to the queue.
5. As a player, I want Stop on a running queue entry to pause at Bankstanding, and a hand start from a paused queue to leave it paused.
6. As a player, I want a finished quest to leave the queue in the same review, however I started it, with every entry for that quest removed.
7. As a player, I want a skill entry to count only work done while it runs.
8. As a player, I want a row click during a queue entry on that skill to select for Add to queue only, with the selected row and the training row looking different.
9. As a player, I want "Train this skill" enabled for that selection, because it compares what really runs with what I picked.
10. As a player, I want the count to follow supplies until I type a number, a typed number to stay until the target changes, and only an accepted add remembered.
11. As a player, I want the default count to be Bank input plus the output of earlier queue entries, never below 1.
12. As a player, I want no popup when the queue changes activity, because the queue exists to reduce interruptions and clicks.
13. As a player, I want a queue change to give one event log line and one Review HUD line, including the lamps waiting in Bank Claims.
14. As a player, I want an entry that cannot start to be skipped with a line and no popup.
15. As a player, I want the Wilderness confirmation when I add a Wilderness entry, with its kept and lost preview, and a skip with a line if my gear changes before the entry starts.
16. As a player, I want the old popup text only when the queue has nothing left to continue with.
17. As a player at 10x, I want a bank run to take 100 ticks (60 seconds of 2012 play), paid from the rest of the card, with the fight continuing after it.
18. As a player at 1x, I want the same 100 ticks, so that XP per hour of 2012 play is the same at both speeds.
19. As a player, I want Agility to shorten a Combat bank run: 7% at level 99, plus the existing small weight effect, and I want the bank transaction always to complete.
20. As a player, I want rest to take 180 ticks and grave recovery 300 ticks at every speed.
21. As a player, I want the remaining ticks after a quest kill to go to the next fight if the next quest step is also a fight, unless that raises deaths.
22. As a player, I want Witch's House to put on accepted gloves I hold, and Demon Slayer to wield Silverlight, so that neither quest stops for a menu visit.
23. As a player, I want my old item back at the first bank run after the quest stops needing the slot, or at once if the quest ends or stops first, and I want a change of that slot by hand to cancel the return.
24. As a player, I want Jungle Potion to search, clean and hand in by itself, one card each, 15 cards and no action switches, with 2.5 Herblore XP per cleaning.
25. As a player, I want a step skipped when I already hold its product, so that herbs I hold count.
26. As a player, I want a quest to stop and name what is missing when I lack the level, coins or equipment for its step.
27. As a player, I want the 23 clear item stops in `quest-stop-scan.tsv` folded into their quests, so that Cook's Assistant fetches its bucket.
28. As a player, I want the other 47 stops in those 67 quests folded in where the period guide shows no fight is needed.
29. As a player, I want Adamant boots and the other 20 items in the game with a period check, a Grand Exchange row if they trade and 2012 art where it exists.
30. As a player, I want a double click in any search box to select the whole phrase.
31. As a player, I want Combat search to match the monster name, group and logged drops only.
32. As a player, I want Grand Exchange offers to keep their slots, and a new offer to take the first empty slot.
33. As the owner, I want the 131 other quests handed to the Sol loop as briefs that use the new supply step.

## Implementation Decisions

**Queue state.** A manual pause and a hand-started action become two different saved states. Only a queue set aside by a hand-started action returns by itself, from its top entry, when that action stops by itself or the player presses Stop. A saved `paused` queue stays paused. Only Clear or an empty queue ends at Bankstanding. The Pass 19 rule stays: an add starts the queue at once unless the queue already runs.

**Reorder.** Up and Down reuse the look and move rule of the Farming queue rows. The top control of the first row and the bottom control of the last row are disabled. Moving a running entry down, or another entry to the top, starts the new top entry at once.

**Target click.** The hold decision compares the action that really runs with the row. The header button compares the skill and the target, not only the skill name. The "held" Add record stays; the difference between the selected row and the training row uses the existing selection and current-row styles, in both themes.

**Count.** An untouched default recomputes on target and supply change. The default is Bank input plus the promised output of earlier queue entries, floor 1. Typed state clears on target change. Only an accepted add writes the remembered count.

**Notices.** One seam decides between a popup and a line: when the queue continues, the quest-complete, "Activity locked", "Activity switched off" and Wilderness notices become a line. The line for a quest names the quest, the next entry and any lamps: "Pirate's Treasure complete. Next: Mining." followed by the existing lamp text. Menu text stays minimal.

**Wilderness.** The existing fingerprint and confirmation run at add time. At entry start, a fingerprint mismatch skips the entry.

**Adjacent fixes in the queue tickets.** The "Now" label can be wrong before the next review. A same-surface queue takeover can leave the panel stale. The final counted entry has no "Queue: <name> done" line. "1 reviews remaining" has a grammar fault.

**Timed delays.** Combat bank run, quest combat bank run, rest and grave recovery store remaining ticks in place of remaining reviews, and they spend the card's tick budget. Base values: bank run 100 ticks, rest 180 ticks, grave recovery 300 ticks. A saved delay in the old form finishes at the next card, with no conversion. The bank run base is a Placeholder with the repository's marker, with no period source. The bank transaction, encounter end for ordinary combat, and enemy LP kept for quest combat do not change. A bank trip no longer ends a Combat card; every other danger stop stays. Remaining ticks after the trip go back to the fight, or to the next queue entry through the existing handover. A trip that outlasts the card shows remaining reviews in the Review HUD, computed from the current speed.

**Agility.** Combat joins the Agility travel profile with the weak tier (7% at 99), carried weight effect and run energy credit, as `memory-bank/agility-run-energy-contract-2026-07-14.md` sets for Combat. Agility shortens the cost and never skips the transaction. A roll, if the profile needs one, happens only when a trip is due, so other RNG streams do not move.

**Skilling trips do not change.** They already spend ticks: iron pays 30.742 XP per card at 1x and 313.075 at 10x with items kept.

**Quest fights.** After a quest kill, if the next quest step is also a fight, the remaining ticks go to it. A stage whose only deed is the fight advances inside the card so the next fight can start. A non-fight step stays one card, because quests "are already faster than 2012 at ×1". Every danger stop still ends the card. A seeded comparison measures deaths per quest fight with and without the carry over the quests the walk finishes that have two or more consecutive fights. If the pooled death rate rises by more than four standard errors of the paired difference, the carry does not land and the ticket reports the table.

**Contract updates.** `memory-bank/cadence-kernel-contract-2026-07-13.md`, `memory-bank/systemPatterns.md` and the Combat line of the Agility contract change to match. The pace proof turns Combat banking on, so the equal-rate check covers it.

**Quest wear.** A quest row can declare a slot and its accepted items. The quest card, at no extra cost, puts on the first accepted item held, unless an accepted item is already worn. The switch goes through the existing equipment change transaction, and a small saved record holds quest, slot, old item and whether the quest still needs the slot. The record follows the existing Cooking gauntlets swap. The return runs at the first bank run after release, in both the Combat restock and the skilling arrival, or at once when the quest ends or stops. A change of that slot by hand clears the record. Review undo restores the record. This pass declares it for Witch's House stage 6 and Demon Slayer stage 7 only. Witch's House accepted gloves come from its existing list.

**Supply steps.** `QuestSupplyRecipe` grows from "names a Utility row" to one of: a Utility row, a Herblore row, or a quest-local action with inputs, product, coins, skill level and XP. A quest-local action adds no row to the Utilities tab. The planner, skip rule and stop rule stay. XP comes from a period source, or the step pays none and the source says so in the evidence. Level, coins and equipment gaps stop the quest and name what is missing, also for a quest already started.

**Jungle Potion.** Each of the five herbs becomes search, clean, hand in. A stage that held a repeatable search row loses it, and a save mid-quest continues with the herbs it holds.

**Item stops.** The 18 clear rows other than Jungle Potion, then the rows that `route-check.tsv` marks fold. Rulings 7 to 18 of `memory-bank/grill-decisions-2026-10-28.md` decide each row without an owner question: the taught route, no optional danger, no fight in a supply step, period price and XP.

**Items.** Register the 21 items named in `facts-small.md`. Add a Grand Exchange row where the period page says it trades, and art from the period art tools. No invented shop or recipe. Record the Mutated bloodveld and Giant frog drop gap and do not fix it.

**Search.** One search-specific line edit selects the whole phrase on a double click, in all 27 boxes. Combat search leaves out tooltip text; the `match_tooltip` option goes away with its only user.

**Grand Exchange.** Offers keep a stable slot number. A new offer takes the first empty slot. A saved compact list keeps its current positions as slot numbers.

## Testing Decisions

A good test drives the real review handler or the real widget, and it checks what the player sees: what runs, what the queue holds, what the bank holds, XP, cards. Prior art: `tests/action_queue/`, `tests/pace/rates/rate_property.py`, `tests/quests/`, `tests/ui_flows/`, the Goblin Diplomacy supply step tests.

- Queue: a played sequence through the review handler for each row of the owner's rules, plus a real widget flow for Up, Down, row click, header button and count. A Monte Carlo sweep of random add, move, hand-start, Stop, Clear and finish sequences keeps these invariants: at most five entries, the running action is the top entry or a hand-started action, no finished quest stays.
- Pace: the rate property at 1x and 10x with Combat banking on. A played fight through a bank run at 1x, 10x and 20x. Ticks spent per card equal the budget when no danger stop occurs. Agility 1 and 99. An XP-per-card table for the 4 Pass 20 fixtures goes in the report and compares with `facts-combat.md`.
- Quest wear: played quests from a new save. Old gloves return at the bank run, at quest end and at quest stop. A hand change cancels. Undo restores.
- Supply steps: each changed quest finishes from an empty bank through the real handler, at the card count the ticket states, except where the row's verdict is `player brings`. `/Users/ArmanTarkhanian1/Documents/ankiscape-pass20/scan/walk.py` shows no remaining stop for the folded rows.
- Items: each item in the catalog, Grand Exchange where it trades, and in a Gargoyle drop for Adamant boots.
- Search: "bat" gives Giant bat and Guard (battleaxe) in Combat. A real double-click event selects the phrase in every box.
- Grand Exchange: claim the middle offer of three; the others keep their slots; a new offer fills the gap.
- Visual: each ticket that changes a screen saves offscreen PNGs at the default size and 560 points tall, dark and light, and checks text fit. A frontend-taste model reviews the new queue controls and the row states before promotion. A native check runs in real Anki before promotion.

## Out of Scope

- Combat XP values, enemy stats, 2012 XP rates, and skilling trip lengths.
- The 131 quests that stop at a required action, except their briefs.
- The physical switch on the 75 wearing rows that are text or item checks. Each gets it when the Sol loop builds its quest.
- Mutated bloodveld and Giant frog drops.
- A per-target bank run length.

## Further Notes

Combat feel can only be judged in play. The results page states this. The estimates in `grill.md` compare trip lengths at 10x: +3% to +15% over today for 100 ticks, on one seed.
