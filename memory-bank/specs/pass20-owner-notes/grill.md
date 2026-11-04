# Pass 20 grill record

Owner notes: `~/Downloads/ankiscape notes.rtfd/TXT.rtf`, section "Pass 20 (11/2/26 start)".

## Answers, word for word

Each question lists the recommendation the owner answered.

1. A hand-started action runs until it stops by itself (supplies out, requirement lost, quest complete). The queue then continues from its top entry. A free pickup runs until the player presses Stop or adds to the queue, and Stop also returns to the queue. Only a manual Clear ends at Bankstanding. Owner: "1. Yes"
2. Queue reorder: Up and Down buttons on each row, like the Farming queue. This answer is the interface approval. Owner: "2. A"
3. When the top entry moves, the new top entry starts at once and the old entry keeps its remaining count. Owner: "3. Yes"
4. A row click while a queue entry runs on that skill selects for Add to queue only. The header button becomes an enabled "Train this skill", and a click on it starts the pick ahead of the queue. The selected row and the training row look different. Owner: "4. Yes"
5. An untyped count follows supplies. A typed count stays until the target changes. Only an accepted add is remembered. The default is Bank input plus the output of earlier queue entries, never below 1. Owner: "5. Yes"
6. Stop on a running queue entry pauses at Bankstanding. A hand start from a paused queue leaves it paused. Only an interrupted queue returns by itself. A finished quest removes every entry for that quest in the same review. Skill entries count only work done while running. Owner: "6. Yes"
7. Owner: "7. Yes but I don't think it should give a popup when the queue changes activities, tbh. The whole point of the queue is to lower interruptions and clicking around". So a queue handover shows no dialog.
8. Jungle Potion becomes automatic search, clean and hand-in, one card each, 15 cards and no action switches. A step is skipped if the product is held. Cleaning pays 2.5 Herblore XP and stops naming a low level. Owner: "8. Yes. Again, we need to do this for similar quest steps for things that can/should be done during the quest."
9. Register all 21 unregistered equipment items with a period check per item, a Grand Exchange row if the item trades, and 2012 art where it exists. No invented shop or recipe. The Mutated bloodveld and Giant frog drop gap is recorded and not fixed. Owner: "9. Yes obviously"
10. Grand Exchange offers keep their slot numbers. A new offer takes the first empty slot. Saved offers keep their current positions. Owner: "10. Yes"
11. Combat search matches monster name, group and logged drops only. Owner: "11. Yes. though I had also assumed that it was \"bat\" was too short of a word?"
12. Owner: "12. I guess? Why is it not just a simple 10x of what it was before? A bank run would fit inside the 10x with time scaled automatically"
13. Owner: "13. No I'd want it to physically be switched out during the period and then switch back after a bank run"

Decided without a question: a double click in any of the 27 search boxes selects the whole phrase.

## Facts behind the answers

- "bat" length: `core/search_match.py:42` needs 4 letters only for fuzzy matching. A 3-letter token still matches as a substring. Combat showed 198/198 because every Combat tooltip contains "combat level", and "combat" contains "bat".
- Combat at 1x and 10x, 200 cards, one seed, stocked fixture (XP per card): level 1 Man 2.843 and 24.043; level 20 Hill giant 8.008 and 75.918; level 40 Moss giant 24.019 and 164.933; level 70 Fire giant 51.789 and 468.909. XP per tick of combat time is close at both speeds, so the loss comes from time outside combat.
- `logic_pure/logic_pure_state.py:75` `COMBAT_BANK_RUN_REVIEWS = 2` charges two whole cards at every speed, and a kill that needs a bank run ends its card early. Two cards are 12 ticks at 1x and 120 ticks at 10x.

## Quest stop scan

`quest-stop-scan.tsv` holds the 519 rows of the quest scan that are not already automatic: revision `264ef9696`, 198 ledger entries, 1154 requirement rows. A walk with every item held finished 56 entries. Of the 142 others, 131 stopped at `Action required: Complete <quest> stage <n> objective`, which no game action emits. The verdicts are the scan agent's: 117 fold into quest, 15 player brings, 387 unresolved. Only 2 wearing rows stop a quest in code: Demon Slayer stage 7 (`Wield Silverlight to damage Delrith`) and Witch's House stage 6 (`Wear insulating gloves to pass the electric gate`). The other wearing rows are journal text with no slot check. Only Goblin Diplomacy declares supply recipes today.
