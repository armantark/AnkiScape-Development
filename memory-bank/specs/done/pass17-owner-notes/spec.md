# Pass 17 owner notes

Source: the owner's notes file `~/Downloads/ankiscape notes.rtfd` on the Mac
Studio, section "Pass 17 (starting 10/18/2026)", 11 notes, read on
2026-10-26. The grill answers of 2026-10-26 settle every decision below; they
are quoted in `grill-decisions.md`. Code facts with citations at main
`2e885047f`: `code-facts.md`. Period sources:
`memory-bank/source-audits/pass17-wicked-hood-and-field-crops-2026-10-26.md`
and `memory-bank/source-audits/pass17-pickables-harvest-2026-10-26.md`.

## Problem Statement

The owner played at the new 10x game speed and hit these problems:

- At 10x an action uses up its materials in a few cards. The game then
  switches to Bankstanding, and the owner must open the menu, find the next
  action and start it, again and again. Nothing lets him plan a chain such as
  mine, smelt, smith.
- When a quest or action stops for a missing item, the owner fixes the cause,
  then must go back through the Quests tab or the skill lists to restart it.
- The event log shows "+62 XP · Smithing" but not what the review made or
  used, and a failing action fills the log with the same line: five
  "The ore was too impure" rows for one review.
- A mouse wheel over a number box changes its value when the owner only
  wanted to scroll the page.
- In combat, ticking "Prayers/Curses" and choosing Burst of Strength does
  nothing: a hidden uptime setting in the "Advanced preset editor" starts at
  "Off". Nothing during play shows which prayers run, and the max-hit
  tooltip does not change. The whole combat setup panel, from "Combat mode"
  to "Current target", is hard to read and hard to use.
- Poison and antipoison show "150 ticks", which means nothing to a player who
  counts cards. Other timers show ticks too.
- The Wicked hood hands out its 100 daily essence one pack at a time, and its
  text says "refills every 240 answered cards" when the owner's world day is
  100 cards.
- Cabbages, potatoes, onions, berries, bananas and pineapples exist and feed
  recipes and quests, but the player cannot pick them from the world.
- The play checklist sent the owner to a max-hit indicator with no place
  named, and told him to press an Undo he could not find.
- Five existing gathering and recipe entries carry wrong or non-period
  sources.

## Solution

- An **action queue** of up to five entries. Each entry is one action and a
  count in that action's own unit; the queue works through the entries once,
  top to bottom. An entry that cannot continue gives a notice and the next
  entry starts. An empty queue ends at Bankstanding with the usual notice.
- A **Resume** button on the **review HUD** restarts the last action, a quest
  at its current step, whenever the player is at Bankstanding.
- Each XP line in the event log lists the review's item changes; the popup
  shows the product count. Identical lines next to each other within one
  review collapse into one line with " - x5".
- The mouse wheel never changes a number box in AnkiScape windows; it scrolls
  the page.
- The combat setup panel is rebuilt by a hill-climb loop judged by a naive
  player probe and a taste vote. Its first candidate makes a ticked
  "Prayers/Curses" mean that the chosen prayers stay on all fight, and shows
  the active prayers on the review HUD.
- Every remaining time that the player reads in ticks shows "N cards left".
- "Withdraw essence" sends all the hood's remaining essence to the Bank in one
  click, and the refill text names the player's own world-day length.
- Seven "Pick" entries join Utilities > Gathering at their main 2012 places.
- The play checklist names exact places and settings, and the five source
  faults are fixed.

## User Stories

1. As a player at 10x speed, I want to queue mining, smelting and smithing with a count each, so that I keep studying while the chain runs.
2. As a player, I want each queue entry counted in the action's own unit (ores mined, bars made, kills), so that I know what "100" means.
3. As a player, I want the count box to start at the most my Bank allows now, so that a sensible count needs no arithmetic.
4. As a player, I want to type a larger count than my Bank allows now, so that a later entry can use what an earlier entry makes.
5. As a player, I want a quest in my queue to run until the quest stops, so that quests fit the same plan.
6. As a player, I want an entry that runs out of materials to give a notice and pass to the next entry, so that one shortfall does not stop my whole plan.
7. As a player, I want the queue to end at Bankstanding with the usual notice, so that I know my plan is finished.
8. As a player, I want the queue to hold at most five entries and never repeat, so that I still plan my training.
9. As a player, I want a manual Stop to pause the queue, and Resume to continue the current entry, so that a stop to sell items does not lose my plan.
10. As a player, I want a Clear control on the queue, so that I can drop a plan.
11. As a player, I want the queue saved with my profile, so that it survives closing Anki.
12. As a player whose quest stopped for a missing item, I want "Resume Black Knights' Fortress" on the review HUD, so that I restart it in one click after I buy the item.
13. As a player, I want Resume to show the same reason when the requirement is still missing, so that I know why nothing started.
14. As a player, I want Resume after any switch to Bankstanding, automatic or manual, so that a manual stop also has a way back.
15. As a player, I want each XP line to show what the review made and used, such as "+2 Iron bar · −4 Iron ore", so that I see my materials move.
16. As a player, I want a potion drunk in combat to show as "−1 Antipoison (3)", so that I see my supplies fall.
17. As a player, I want the XP popup to show the product count, such as "+2 Iron bar", so that the popup stays short.
18. As a player, I want five identical failure lines in one review shown as one line with " - x5", with "x5" in muted orange, so that the log stays readable.
19. As a player, I want lines from different reviews kept apart, so that "0 reviews ago" and "1 review ago" stay true.
20. As a player, I want the mouse wheel to scroll the page and never change a number box, so that I do not change settings by accident.
21. As a player, I want a ticked "Prayers/Curses" with a chosen prayer to make that prayer run in my fights, so that the setting does what it says.
22. As a player, I want to see on the review HUD which prayers are on during a fight, so that I know they work.
23. As a player, I want the max-hit tooltip to change at once when I change a prayer setting, and to use the same prayer drain as a real fight, so that the number is true.
24. As a player who has read no guide, I want every control from "Combat mode" to "Current target" to be clear about what it does and where its state shows, so that I set up a fight without trial and error.
25. As a player, I want the advanced preset editor to keep every setting it has now, so that nothing I use disappears.
26. As a player, I want "Poison immune: 3 cards left" in place of "Poison immune: 150 ticks", so that I can plan by cards.
27. As a player, I want the same card count for the Mining extra-ore bonus, Fist of Guthix, Tears of Guthix and every other remaining time, so that every timer speaks one unit.
28. As a player, I want "Withdraw essence" to put all my remaining hood essence in the Bank at once, so that I do not click four times a day.
29. As a player, I want the hood to keep the 2012 amount, 100 essence plus 25 per Runespan robe piece, so that the game stays true to 2012.
30. As a player, I want the hood's refill text to name my own world-day length, so that it matches my settings.
31. As a player, I want to pick cabbages north of Lumbridge, potatoes north of the Lumbridge chicken farm, onions at Fred the Farmer's, redberries south-east of Varrock, cadava berries south of Varrock, bananas at Musa Point and pineapples at the Brimhaven Dungeon entrance, so that recipes and quests do not need a shop or a farm.
32. As a player, I want each Pick entry to give no XP and need no level, as in 2012, so that picking is an errand and not a skill.
33. As a player, I want the play checklist to name the exact screen, hover and setting for each check, so that I can find what it asks me to see.
34. As a player, I want the play checklist to say "Edit > Undo (Cmd+Z)" wherever it uses the undo, so that I can find it.
35. As the owner, I want gathering and recipe sources to cite period sources, so that the 2012 claim of each entry holds.
36. As the owner, I want the run checked natively in Anki by Codex before it reaches main, so that the new screens work in the real reviewer.

## Implementation Decisions

### Review item changes (shared by the event log, the popup and the queue)

- A new pure function compares the save before a review with the save after
  it and returns the item changes of that review, Bank and carried pack
  together, as a mapping from item name to a signed count. The review
  context already holds the before-review save.
- The event log's XP line appends the changes: gains first, then losses, each
  as "+N Item" or "−N Item", joined by " · ". The popup shows only the gain of
  the action's product item.
- Collapsing happens where the event log builds its rows: identical
  consecutive rows that share one review age become one row whose text ends
  in " - xN". Only "xN" takes the new muted orange, a new named colour in the
  event-log tone set, legible in dark and light themes. No collapsing crosses
  a review age.

### Last action and Resume

- The switch to Bankstanding saves a **last action** record before it clears
  the action: the action kind (skill, utility or activity, quest, combat)
  and every key that the start path needs (the skill and its target key, the
  utility id, the quest id, the combat target and combat action).
- The review HUD shows "Resume" plus the action's display name beside "Bank
  run" whenever the current action is Bankstanding and a last action
  exists. A click starts the action through the same start function its tab
  uses, so the same requirement checks run; a refusal shows the same reason
  text and starts nothing. A quest resumes at its saved step.
- When the queue is empty, the last action is the last queue entry.

### Action queue

- A pure queue module owns the state: up to five entries; each entry holds
  an action (in the last-action shape) and a target count; the queue holds a
  current index, the done count of the current entry, and a paused flag. It
  saves in the profile.
- The queue counts in the action's own unit. Skill, utility and activity
  entries count the review's gain of the action's output item, from the
  review item changes. Combat counts kills. A quest entry has no count and
  ends when the quest stops.
- After each review the runtime advances the queue: when the current entry
  reaches its count, the next entry starts. When the runtime is about to
  switch to Bankstanding for a missing material or requirement, the queue
  first gives the notice for that entry and starts the next one; only an
  empty or finished queue lets the switch to Bankstanding happen, with the
  usual notice.
- A manual Stop pauses the queue; Resume continues the current entry. Clear
  empties it. The queue never repeats and holds at most five entries.
- The queue panel's place and look come from the hill-climb loop. Its
  first candidate: an "Add to queue" control beside each Start control, the
  count box (whose default is the most the Bank allows now), and a compact
  list on the review HUD's side of the main menu with Clear.

### Mouse wheel

- One event filter, installed by AnkiScape's own windows and dialogs and not
  on Anki's widgets, ignores wheel events on number boxes and passes them to
  the scroll area under the pointer. It covers every number box, including
  boxes built in loops and the new queue count box, without edits at each
  construction site. If Anki's widget style lets the wheel change a
  drop-down list, the same filter covers drop-down lists.

### Combat setup panel and prayers

- Prefactor first: the combat setup panel moves out of the main menu module
  into its own module with no visible change, so that the hill-climb can
  rebuild it without growing the main menu file.
- The prayer rule of the first candidate: when "Prayers/Curses" is ticked,
  the chosen prayers are on for the whole fight ("Always 100%") unless the
  advanced editor sets a lower uptime; when no prayer is chosen, the game
  picks the best prayers by the rule that "Supply mode" uses now. Saves that
  hold the old "Off" uptime follow the new rule.
- The max-hit preview uses the same prayer drain per card as a real fight,
  and every prayer setting change rebuilds the target tooltips.
- During a fight, the review HUD shows the active prayers beside the prayer
  points, for example "Prayer 38/43 · Burst of Strength".
- The hill-climb loop may change any part of the rule above and any part of
  the panel's layout, labels, grouping and defaults, but it keeps every
  setting the panel has now reachable.

### The hill-climb loop (combat setup panel, queue panel, Resume button)

- Objective: a player who has read no guide completes each task of the
  screen's task list from the screenshots alone, with no wrong step, and the
  taste vote approves.
- Task list for the combat setup panel: make Burst of Strength run in the next
  fight and say how you know it runs; set auto-eat to 50%; leave loot worth
  under 1,000 coins; choose the Strength attack style; save a preset for
  this target; find your max hit with the prayer on. Task list for the queue:
  queue 100 iron ore then smelt them into bars, then clear the queue. Task
  list for Resume: restart the quest that stopped.
- Each round: the implementer builds a candidate and captures offscreen
  screenshots at 560 points tall, in dark and light themes; the orchestrator
  gives a fresh naive model only the screenshots and the task list, and gets
  a frontend-taste vote on the same screenshots from a different lineage;
  the implementer keeps or rejects the candidate by those results.
- Stop when the probe passes and the vote approves. After five rounds without
  a pass, keep the best candidate and report it.
- The maker never judges its own candidate: the probe and the vote run in the
  orchestrator, outside the implementer's context.

### Durations in cards

- One shared formatter turns a remaining tick count into "N cards left" at the
  player's current game speed, rounded up, "1 card left" in the singular. It
  uses the existing ticks-to-cards converter.
- It replaces every remaining-time text in ticks: poison and poison immunity
  on the review HUD and the combat target, the Mining extra-ore bonus, Fist
  of Guthix, Tears of Guthix, collection ticks and Juna's cavern time. Setting
  labels that are not remaining times keep their wording.

### Wicked hood

- "Withdraw essence" moves the whole remaining daily allowance into the Bank
  in one click. The menu label and the Runecrafting card's tooltip say so.
  The daily amount stays 100 plus 25 per Runespan robe piece, up to 175.
- The refill text reads the player's world-day length, not a fixed 240.
- Altar access is unchanged: a worn hood crafts 28 essence per trip, a packed
  hood 27.

### Pick entries

- Seven Utilities > Gathering entries in the existing gathering data shape:
  "Pick cabbages", "Pick potatoes", "Pick onions", "Pick redberries", "Pick
  cadava berries", "Pick bananas", "Pick pineapples". Each names its main
  2012 place in its description, cites its period source revision and, where
  only Darkan supplies yield or regrowth, records a placeholder in
  `memory-bank/placeholder-values.md`. No XP and no level; "Pick pineapples"
  follows the game's existing members rules. Pace follows the existing
  gathering entries.
- The "Pick" verb is the 2012 menu verb. Existing "Gather" entries keep their
  names unless the source fixes below change them.

### Source fixes

- "Gather flax" and "Gather wool" cite period revisions in place of their
  current OSRS pages.
- "Grain" and "Wheat": first establish from period revisions whether the 2012
  item, not only the field, was called "Wheat". Rename the item only when the
  item page confirms it, and then migrate saves; otherwise rename nothing
  and record the finding.
- Flax spinning level: change from Crafting 10 to 1 only when the period Bow
  string and Spinning wheel pages agree with the Flax page; otherwise keep 10
  and record the conflict.
- The quest cleanup that names "Raw potato" uses "Potato".
- Source paths under one machine's home folder become machine-independent
  citations of the Darkan repository path and commit.

### Play checklist

- Each ticket that changes what the player sees adds one checklist line.
- The max-hit line names the Combat target row tooltip and the exact prayer
  settings the final rule needs.
- The hood feeding line loses its undo step; every remaining undo step says
  "Edit > Undo (Cmd+Z)".

## Testing Decisions

- A good test drives the real kernel or the real widget and checks what the
  player sees or what the save holds. No test stubs the system under test.
- Seams and layers:
  - **Pure logic, unit layer:** the review item changes, the queue state
    machine (advance on count, pass on shortfall, pause, clear, five-entry
    cap, no repeat), the last-action record, the cards-left formatter, and
    the hood withdraw-all.
  - **Review kernel, integration layer:** answer real reviews through the
    review handler: a three-entry chain (mine iron ore, smelt, smith) that
    passes on a shortfall and ends at Bankstanding; Black Knights' Fortress
    blocked for an iron chainbody, then resumed at its step after the item
    arrives; a fight with Prayers/Curses ticked that drains prayer points and
    raises the max hit; an XP line with item changes and a collapsed
    "too impure" line; each Pick entry gathering its item; a hood
    withdraw-all into the Bank. These carry the verification weight for the
    gameplay tickets.
  - **Offscreen Qt, end-to-end layer:** every ticket that changes what the
    player sees builds the main menu offscreen at 560 points tall, after
    `show()`, `resize()` and event processing, per the AGENTS.md rules;
    checks `text_fit_defects`; and saves before and after captures as
    evidence. A wheel test sends a wheel event over a number box inside a
    scroll area and checks that the value stays and the area scrolls.
  - **Hill-climb loop:** the naive probe and the taste vote judge the combat
    setup panel, the queue panel and the Resume button, as above.
  - **Native check:** before the merge, one Codex native check runs the new
    screens in the real Anki reviewer, on GPT-6.1 Terra first and on GPT-6.1
    Sol when Terra blocks or passes a check without evidence.
- Prior art: `tests/test_undo_seam_wickedhood.py`,
  `tests/runtime_actions/test_wicked_hood_pack.py`,
  `tests/ui_flows/test_bank_quest_fit.py`, `tests/test_integration_smoke.py`,
  and the Pass 16 ticket tests named in
  `memory-bank/specs/pass16-owner-notes/spec.md`.
- Each ticket runs its focused tests locally. The run's landing passes the
  full promotion gate with `--remote-lanes`.

## Out of Scope

- The Bloom spell and the Mort Myre fungus, pears and stems it yields (parked
  in the kanban).
- The Sorceress's Garden, which has its own activity; quest-only plants; the
  Oo'glog herbs and other plants whose items the game does not have.
- Queue loops or repeats, and queues of more than five entries.
- One-off item uses (the Pass 16 parked water-jug idea).
- Scaling the hood's essence with Runecrafting level or card volume.
- An in-game Undo button; the Edit > Undo (Cmd+Z) undo stays as it is.
- The game-speed fallback that reads 1x for a profile with no stored speed
  while the sanitizer defaults to 10x (surfaced, not fixed).

## Further Notes

- Loops: the owner paused both Sol loops before this run, so main does not
  move while the integration branch grows.
- The memory bank startup files sit at 2,999 of 3,000 lines. Tickets add no
  lines to them; the results commit rotates progress.
- Codex quota is critical; the hill-climb probes and votes run on Claude and
  Kimi, and Codex is spent on the native check.
