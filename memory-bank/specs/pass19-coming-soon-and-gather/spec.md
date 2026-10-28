# Pass 19: "Coming soon" quests and the Gather row

The owner settled this pass in the Sol loop grill of 2026-10-28, rulings 13 to
17 of `memory-bank/grill-decisions-2026-10-28.md`. The owner's answers, word for
word, are in that file. The glossary defines "Coming soon" and "Free pickup".

## Problem Statement

1. A player can start 141 of the 198 quests, but cannot finish them from a new
   save (reachability audit, `completable_quest_count` 57, 2026-10-28). 132
   quests hold a generated placeholder goal such as `Complete Monkey Madness
   stage 2 objective` that no card can earn. A started quest then shows
   `Blocked: Action required: Complete Monkey Madness stage 2 objective`. The
   owner: "why is monkey madness (and other incomplete quests) even available to
   play if it's not fully in yet lol. Breadth first development only makes sense
   if the breadth that you build can at least make a whole gameplay loop".
2. The Start button checks only start requirements
   (`logic_pure/logic_pure_quest.py:827-836`), and "Hide unable to start"
   (`ui/ui_tab_quests.py:115`) hides only quests with start locks.
3. 19 skill and Utilities targets need one of 10 quests that cannot be
   finished, for example death runes (Mourning's End Part II).
4. Utilities lists 31 free pickups as separate rows in its Gathering group of
   34 rows. The owner: "having a massive list of free pickups is indeed
   annoying".

## Solution

- A quest that a player cannot finish from a new save is **Coming soon**. The
  Quests tab shows "Coming soon" on it, and its Start button is disabled. "Hide
  unable to start" hides it. A save that already started it keeps its progress
  and sees the same label; its Continue button is also disabled.
- Content that needs a Coming soon quest shows "Coming soon" as its lock and
  stays locked, also when it needs only the quest's start. A save that already
  met the requirement keeps the content.
- The 31 free pickups leave the Utilities list as rows. One **Gather** row in
  the Gathering group replaces them. In its detail box, the player picks the
  item. Each gather still costs cards, and the action queue takes it with a
  count. Play does not change.

## User Stories

1. As a player, I want a quest that I cannot finish to say "Coming soon", so
   that I do not spend cards on it.
2. As a player, I want "Hide unable to start" to hide Coming soon quests, so
   that the list shows only quests I can play.
3. As a player with a started Coming soon quest, I want to keep my progress, so
   that it continues when the quest is finished.
4. As a player, I want a skill target that needs a Coming soon quest to say
   "Coming soon", so that I know it is not available yet.
5. As a player, I want one Gather row instead of 31 pickup rows, so that
   Utilities is short.
6. As a player, I want to queue "Gather" with an item and a count, so that
   gathering works as before.
7. As a player with a saved queue entry, current action or Resume for a free
   pickup, I want it to keep working after the change.

## Implementation Decisions

### Which quests are Coming soon (ticket 01)

- The set comes from the reachability audit: a quest is Coming soon when
  `tools/audit_item_reachability.py` does not count it as completable from a new
  save. A generated module holds the set as quest ids, because the audit is too
  slow to run at runtime.
- A test compares the generated set with the live audit. A change that makes a
  quest completable must regenerate the set in the same commit, so the quest
  gets its Start button when it lands.
- The quest lock is one more start lock reason, `Coming soon`, from
  `quest_locked_reasons_pure`. The Start button (`ui/ui_tab_quests.py:327-332`)
  and "Hide unable to start" already follow the lock reasons.
- A started Coming soon quest keeps its saved state. The quest card shows the
  same label, and its Continue button is disabled. Quest reviews refuse it with
  the same reason.

### Content that needs a Coming soon quest (ticket 02)

- `target_unlock_locked_reasons_pure` (`logic_pure/quest_runtime_rules.py:126`)
  returns `Coming soon` in place of the quest's own reason when the requirement
  names a Coming soon quest and the save does not meet it.
- A save that already meets a `quest_started` or `quest_stage` requirement keeps
  the target. Precedents: Ugthanki dung (The Feud), and cutting, splitting and
  burning Arctic pine (The Fremennik Isles).

### The Gather row (ticket 03)

- The 31 free-pickup Utility rows keep their ids and data. Quest supply steps,
  recipes, saves, the action queue and Resume keep using those ids. Only the
  Utilities list changes: it hides the 31 rows and shows one Gather row in the
  Gathering group.
- The Gather row's detail box lists the 31 items with their icons and lets the
  player pick one. Starting it, or adding it to the queue, starts the picked
  row's action. A queue entry and the Resume button name the item, for example
  "Gather Redberries".
- Utilities search finds the Gather row by any of the 31 item names and opens it
  with that item picked.
- Quest-gated pickups (for example Grab Desert Phoenix feather, The Golem) show
  in the picker with their lock reason and cannot be started while locked.
- The look of the detail box is new interface: it needs the frontend-taste
  review before promotion. The owner approved replacing the 31 rows (ruling 15).
- Menu text is elegant and minimal (AGENTS.md); Opus writes it.

## Testing Decisions

- Good tests drive the real quest review handler and the real widgets, and check
  what the player sees.
- Ticket 01: Monkey Madness shows "Coming soon" with Start disabled; "Hide
  unable to start" hides it; Cook's Assistant stays startable; a save with
  Monkey Madness started keeps its stage and sees the label; the generated set
  matches the live audit.
- Ticket 02: death runes show "Coming soon"; a save with The Feud started keeps
  Ugthanki dung; a new save does not get it.
- Ticket 03: Utilities shows one Gather row and none of the 31 rows; queuing
  "Gather Redberries" ×10 gives 10 redberries over the expected cards; a save
  whose current action is `pick_bananas` resumes it; Goblin Diplomacy's supply
  steps still run from raw supplies in 10 reviews.
- Offscreen Qt checks follow AGENTS.md: show, resize, process events, then
  grab; trust geometry probes; check 560 points tall and dark mode.
- One native check in Anki covers the Quests tab and the Gather row, with a
  truncation check on every new label.

## Out of Scope

- Making quests finishable. The Sol loop does that work under ruling 14.
- The taller activity detail box (item 1970) and the list keyboard and Bank
  refresh repair (item 1580). Loop fixer runs own them.
- Any change to free-pickup batch sizes, XP or levels.
