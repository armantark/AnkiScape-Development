# Class rulings for the Sol loop questions of 2026-10-28

Date: `2026-10-28`

Status: **owner-settled, eleven rulings and three interface approvals.**

These rulings continue the numbering of `grill-decisions-2026-10-25.md`. Each ruling
settles a class of contract questions. A contract cites the ruling and quotes its
ruling line, and then it does not ask the owner a question of that class again.

The owner started this grill on 2026-10-28 with: "There are too many questions on
the Sol loop, can you pose them to me in grill me format in frontiers". At that
time, 23 parked AnkiScape items held 25 open questions.

The owner answered at 13:57 PDT: "2. Yes", "3. Yes", and "4. Yes. It should boot
you out when you don't have the requirements though (gp, level, equipment)".

## 7. Quest details where period sources disagree

Ruling line: when period sources disagree about a detail of a quest or a quest
item, ruling 6 decides it: the contract picks the simpler option that keeps the
quest playable, and it does not ask the owner. When both options are equally
simple, the contract takes the option that more dated sources give and records
the other in the evidence.

- This narrows ruling 1 of 2026-10-25 ("When two period sources disagree with each
  other, the question still goes to the owner") to details outside quests, such as
  item stats, drop tables, skill values and rewards.
- The basis is the owner's ruling 6 sentence: "No one is going to look too closely
  at quests and quest items I reckon, as a principle going forward".
- Precedents, from the table the owner accepted:
  - 3320 Monkey Madness: talk to Daero, then fly with Waydar.
  - 3390 Pirate's Treasure: hide the rum first, then load the bananas.
  - 3280 Dwarf Cannon: the toolbelt hammer, and no inventory hammer.
  - 3690 Lunar Diplomacy: one spool of thread, 4 coins.
  - 3500 As a First Resort: no unlit Fever grass bait; the burning lure only.
  - 3730 Mountain Daughter: always supply the pole; no staff skips it.
  - 3350 Waterfall Quest: no equipment check at the tomb.
  - 3260 Shilo Village: a failed passage deals 260, a failed rock search 60.

## 8. Quest cards take the taught route and never start a fight

Ruling line: a quest card takes the route the period guides teach and adds no
optional or conditional danger. A supply step never starts a fight, and an item
that only a fight gives stays an item the player brings.

- Ruling 3 still holds: an action that could fail in 2012 can fail on a card.
- Precedents:
  - 3420 Fishing Contest: red vine worms with no guard-dog fight.
  - 3340 Shilo Village: the protected tomb route only, with the Beads of the Dead
    worn before entry.
  - 3710 Merlin's Crystal: the player brings Bat bones from Combat.

## 9. Supply steps pay the period price and give the period XP

Ruling line: a supply step buys a missing item from the seller that the quest
guide names, at the period price, and gives the XP that a period source states for
its action. When the player lacks the coins, skill level or equipment that the
step needs, the quest stops and names what is missing.

- The stop is the owner's addition: "It should boot you out when you don't have
  the requirements though (gp, level, equipment)".
- Precedents:
  - 3560 Cold War: the cowbell theft gives 16 Thieving XP.
  - 3670 Legends' Quest: the quest buys missing charcoal at 45 coins each.
  - 3790 Rat Catchers: the quest buys Ali's music scroll and snake charm for 100
    coins; the ring of charos discount is later work.

## Round 2

The owner answered at 14:07 PDT: "1. Ok yes but why is monkey madness (and other
incomplete quests) even available to play if it's not fully in yet lol. Breadth
first development only makes sense if the breadth that you build can at least
make a whole gameplay loop", "5. I'm thinking we need to rethink the free items,
but yes I'd say. I'm not sure how to change it though but having a massive list
of free pickups is indeed annoying. Come up with a few proposals", "6. Yes" and
"7. Yes".

## 10. Supply steps release before the rest of their quest

Ruling line: a supply step releases when its own steps work. Blockers outside
those steps stay with the quest's re-staging row, and the loop files missing
fights as their own rows.

- Precedents: 3530 Between a Rock (stout), 3580 Defender of Varrock (Blurite ore),
  3660 Land of the Goblins, 3720 Monkey Madness (bananas), 3770 One Small Favour
  (pigeon cages), 3810 Ritual of the Mahjarrat (pickaxe and spade), 3790 Rat
  Catchers.
- The owner's principle from the same answer, "Breadth first development only
  makes sense if the breadth that you build can at least make a whole gameplay
  loop", is still under grill for what a player sees of unfinished quests and for
  the loop's priorities.

## 11. Free quest pickups stay inside the quest

Ruling line: a free pickup that a quest step uses stays inside the quest. It is
also a repeatable Utilities action only when a period source shows the item
available to players outside the quest.

- Precedent: 3530 Between a Rock takes Khorvak's stout only on its quest card.
- Pickups that already exist, such as the Goblin Village crate, do not change
  under this ruling. The owner asked for proposals to rethink the existing free
  pickups; that question is still under grill.

## 12. Item variants without their own 2012 picture

Ruling line: when authenticated 2012 art exists for only some variants of an
item, the other variants use the nearest authenticated picture, and the name
carries the difference.

- Precedent: 3140 Underground Pass: the six other metals of wrapped and lit
  arrows use the two bronze pictures, and each name gives the metal and whether
  it is lit.

## Interface approval: the activity detail box grows to fit its text

The owner approved this change to an existing interface, as `AGENTS.md`
requires: the activity detail box under the main menu's activity list grows to
fit its wrapped text, for every activity. The trigger was item 1970, whose six
Easy map clue texts were cut at the 720×540 menu size (56 pixels shown where 84
were needed). The frontend-taste review and the native visual check still run.

## Applied with earlier rulings, with no owner objection

- 3500 As a First Resort catch rewards, by ruling 1's corroboration gate: each
  kebbit catch gives 1 Diseased kebbit fur and 1 Bones, each bird catch gives 1
  Raw bird meat and 1 Bones, matching RuneHQ's "4 Diseased kebbit furs, Wimpy
  feathers, 5 Raw bird meats, 9 Bones". Darkan's 167 Hunter XP per bird stands
  in as a placeholder, and ruling 2 sets the Wimpy feather count.
- 3150 The Fremennik Trials: Manni's distraction lasts 121 ticks, marked as a
  placeholder, the smallest value that lasts until the next card at every game
  speed (ruling 2). Darkan's 25 ticks end before the next card can swap the beer.

## Round 3

Before this round, the reachability audit's model found that 57 of the 198
quests can be finished from a new save and 141 cannot. 132 quests hold at least
one generated placeholder goal, such as "Complete Monkey Madness stage 2
objective", that no card can earn; 43 hold a fight with no combat stats; 34 need
an item that no route gives; 66 are blocked only by placeholder goals. The Start
button checked only start requirements, so a player could start all 141.
Utilities held 31 free pickups, all in its Gathering group of 34 rows.

The owner answered at 14:32 PDT: "8. A but say "Coming soon" instead", "9. Yes",
and "10. No, just B. Another option is just making it a tab under the shop tab,
in addition to the regular shops and minigame/activities rewards shops? But then
we need to balance for taking multiple inventories at once still. I mean I guess
it would still be queued actions. Otherwise if that's too complicated lmk (maybe
the game design compendium has something to say about it)".

## 13. Quests that cannot be finished show "Coming soon"

Ruling line: a quest that a player cannot finish from a new save shows "Coming
soon" on the Quests tab, and its Start button is disabled. A quest gets its Start
button when no placeholder goal, fight without stats or missing item remains in
it.

- "Hide unable to start" also hides these quests.
- A save that already started such a quest keeps its progress and sees the same
  label until the quest can be finished.
- This is also the owner's interface approval for the label and the disabled
  Start button on the Quests tab.

## 14. The loop finishes whole quests first

Ruling line: the loop works on the unfinished quests with the fewest blockers
first. It fixes one quest's blockers in order until a player can finish that
quest. Work that adds a part to a quest that stays unfinished comes after.

- The owner's principle: "Breadth first development only makes sense if the
  breadth that you build can at least make a whole gameplay loop".
- The 66 quests blocked only by placeholder goals come first; for each, its
  re-staging row from ruling 3 is enough to finish it.
- The quest-selection order in `goal-priority-matrix.md` follows this ruling.

## 15. Free pickups become one Gather row

Ruling line: the free pickups become one Gather row. In its detail box, the
player picks the item to gather, and each gather still costs cards. Actions do
not pick up their own free inputs, and free items never cost zero cards.

- The owner chose only option B of four: A let each action pick up its own free
  inputs, C made free items cost no card, and D changed nothing.
- This is also the owner's interface approval for replacing the 31 free-pickup
  rows with one row. The frontend-taste review still runs on the new detail box.
- Ruling 16 places the row in Utilities.

## Round 4

Before this round: a Shop tab purchase is instant, coins for items at once, and
every Utilities row costs cards. 19 skill and Utilities targets need one of 10
quests that cannot be finished; 4 of them need only the quest's start (Ugthanki
dung from The Feud, and cutting, splitting and burning Arctic pine from The
Fremennik Isles).

The owner answered at 14:40 PDT: "11. Fine" and "12. Yes".

## 16. The Gather row lives in Utilities

Ruling line: the Gather row lives in Utilities and works like every other
Utilities row: each gather costs cards, and the action queue takes it with a
count.

- A list on the Shop tab was the owner's alternative. It lost because Shop
  buttons pay coins at once, and a free item there would need a button that
  starts card actions instead.

## 17. Content that needs a "Coming soon" quest locks with it

Ruling line: content that needs a "Coming soon" quest shows "Coming soon" too and
stays locked, even when it needs only the quest's start. A save that already met
the requirement keeps the content.

- Precedents: death runes (Mourning's End Part II), blood runes (Legacy of
  Seergaze), monkfish (Swan Song); Ugthanki dung (The Feud) and the three Arctic
  pine targets (The Fremennik Isles) lock for new players.

## Cards that arrived during the grill

At 14:41 PDT the dashboard showed 35 cards: the first 23 and 12 new ones with 14
questions. The rulings above settle 12 of the 14 (pending the owner's confirmation
of the session summary):

- 3830 Roving Elves: bring a lost Glarial's pebble; the quest supplies only the
  amulet (ruling 6, "how a lost item comes back").
- 3840 Rune Mechanics, 3850 Shades of Mort'ton, 3950 Wanted!, 3960 While Guthix
  Sleeps Q2: supply steps release now (ruling 10).
- 3910 The Fremennik Isles: Q1 keeps Crafting 30 and gives 25 Crafting XP per rope
  (ruling 9; the ordinary recipe does not change); Q2 supplies only the eight
  bridge ropes (ruling 6).
- 3930 The Tale of the Muspah: supply steps now; the twelve-gem ending is a
  separate correction that ruling 7 decides (ruling 10).
- 3960 While Guthix Sleeps Q1: Thaerisk sells the seed once for the dated 20,171
  coins (ruling 9, the period price).
- 3990 Nature Spirit: the journal after the Mirror. The two sources tie on count,
  so the wiki walkthrough decides (an extension of ruling 7's tie rule).
- 4000 Hazeel Cult: the wardrobe search completes the quest, as the wiki and its
  quick guide say against RuneHQ (ruling 7).
- 4020 Underground Pass: the orb arrives on the successful disarm (ruling 7).

Open for the owner: 1580 Oo'glog list keyboard and Bank refresh repair (an
existing interface), and 4050 Demon Slayer key pictures.
