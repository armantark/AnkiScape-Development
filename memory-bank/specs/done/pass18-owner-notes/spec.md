# Pass 18 owner notes

The owner's Pass 18 notes (2026-10-27), settled in three grilling rounds. The
owner's answers, word for word, are in `grill-decisions.md`; code facts with
citations are in `code-facts.md`; period sources are in
`memory-bank/source-audits/pass18-woad-dyes-goblin-diplomacy-2026-10-27.md`.
Native looks in real Anki before the build are in
`/Users/armantarkhanian/Code/ankiscape-pass18/native/look-1/` and `look-2/`.

## Problem Statement

The owner played Pass 17 in native Anki on macOS and hit these problems:

1. The action queue makes far more than the count he picks. He queued 3 goblin
   mail, 3 redberries and 28 onions at 10x and got 30, 40 and 280, because the
   queue checks its count only after a whole card, and one card at 10x runs 10
   steps of one full batch each.
2. Finished entries stay in the queue box and keep one of its five places.
3. Clear queue does not always end at Bankstanding: when the plan waits behind
   an action he started by hand, that action keeps running.
4. The queue box is two rows tall with a scroll bar, even with one entry, so
   from the third entry on a new entry is hidden. An add shows no feedback, and
   every refusal says "Type a count of 1 or more." whatever the cause.
5. Goblin Diplomacy needs seven Utilities actions picked by hand (crates, three
   Aggie dyes, mixing, two dyeings) before the quest can start.
6. The game has no way to mix dyes by using one on another, and Utilities
   offers only orange.
7. Woad leaves come only from Farming or the GE; Wyson the gardener in Falador
   Park, who sold them in 2012, is missing.
8. Both top-level tab arrows sit together at the right end of the tab bar.
9. Bank rows overlap vertically with a bank his size: at the default menu width
   rows overlap by about 14 points and hide the item counts, and category
   headings run into the squares above them.
10. The GE offer panel squashed its rows to half height (his screenshot). His
    Anki has run `33163df1b` since 09:45 on 2026-10-27; `1e5d71015` already made
    the GE tab scroll instead of squeezing, but Pass 18 makes the queue box,
    which takes height from every tab, taller.
11. The menu copy written in the Pass 17 hill-climb rounds reads as cringe to
    him. Menu text must be elegant and minimal.

## Solution

- The action queue makes exactly the count the player picks, in every unit.
  The step that reaches the count makes only the remainder, and the rest of
  the card goes to the next entry. Done and stopped entries leave the queue at
  once; the Event log keeps their lines. Clear queue always ends at
  Bankstanding, with Resume for what ran.
- The queue box shows every entry with no scroll bar and folds from its title
  line. Each add highlights its new row and the Add button confirms it for a
  moment; each refusal names its cause.
- Quests gain supply steps: when a quest needs an item the player can make from
  supplies he holds, each quest card makes the next missing item. Goblin
  Diplomacy is the first quest with supply steps; the player brings only
  redberries, onions, woad leaves and coins.
- Utilities gains "Mix green dye" and "Mix purple dye"; the Bank gains a "Mix
  with" menu on each dye that mixes one pair at once.
- The Shop tab gains Wyson the gardener with two offers: 2 woad leaves for 20
  coins, 1 for 15.
- The tab bar has one arrow at each end. Bank rows never overlap. The GE panel
  stays whole with a full queue box.
- Opus rewrites the Pass 17 hill-climb copy and writes all new Pass 18 text,
  elegant and minimal.
- Every screen change is looked at in real Anki before review.

## User Stories

1. As a player, I want a queue entry of 3 redberries to make exactly 3, so that
   the queue does what I asked and my bank is not flooded.
2. As a player at 10x game speed, I want the rest of the card that finished an
   entry to work on the next entry, so that no play time is lost between
   entries.
3. As a player, I want a queued count of 1 platebody to make 1 platebody, so
   that skill entries follow the same rule as gathering entries.
4. As a player, I want a kill entry of 5 kills to stop at 5 kills, as a Slayer
   task stops at its last kill, so that I do not fight past my plan.
5. As a player, I want a finished entry to leave the queue box at once, so that
   the box shows only what is still to do and the place is free for a new
   entry.
6. As a player, I want a stopped entry to leave the box too, with its reason
   kept in the Event log and on the review HUD, so that I still learn why it
   stopped.
7. As a player, I want Clear queue to put me at Bankstanding whatever was
   running, so that clearing the plan always stops the work.
8. As a player who cleared the queue, I want Resume to offer the action that
   ran, so that I can pick it up again in one click.
9. As a player, I want the queue box to show every entry without a scroll bar,
   so that I can see my whole plan.
10. As a player on a short menu, I want to fold the queue box by its title
    line, so that the tab above gets its height back when I need it.
11. As a player, I want the new row to light up and the Add button to say
    "Added ✓ (3 of 5)" for a moment, so that I know each add worked.
12. As a player whose add was refused, I want the message to name the real
    cause (queue full, nothing chosen, quest locked), so that I know what to
    change.
13. As a player starting Goblin Diplomacy with 3 redberries, 2 onions, 2 woad
    leaves and 15 coins, I want each quest card to do the next missing step,
    so that I finish the quest without picking seven Utilities rows by hand.
14. As a player who already holds orange dye, I want the quest to skip the red
    dye, yellow dye and mixing steps, so that I never pay for an item I hold.
15. As a player missing a supply, I want the quest to stop with a reason such
    as "Needs 3 Redberries for Aggie's red dye", so that I know what to bring.
16. As a player, I want the quest journal or card to show the next supply step,
    so that I can see what the next card will do.
17. As a player, I want to right-click a dye in the Bank and mix it with
    another dye I hold, so that I can mix dyes the way 2012 players did.
18. As a player, I want "Mix green dye" and "Mix purple dye" in Utilities, so
    that I can mix in batches on cards as I do orange.
19. As a player, I want to buy woad leaves from Wyson the gardener in the Shop
    tab, so that I do not need Farming level 25 or the GE for blue dye.
20. As a player on a narrow menu, I want "<" at the left end of the tab bar and
    ">" at the right end, each greyed out at its end, so that the arrows read
    as directions.
21. As a player, I want the tab I select always fully in view, so that no tab
    name is cut.
22. As a player with a large bank, I want every bank row and category heading
    to keep its full height at any menu size, so that I can read every item
    count.
23. As a player, I want the Bank Claims lines whole, so that no claim text is
    cut.
24. As a player with a full queue box on a short menu, I want the GE offer
    panel to keep every row at full height and scroll, so that I can place
    offers.
25. As a player, I want menu text that is short and plain, so that the menu
    reads as part of the game and not as instructions.
26. As the owner, I want every screen change looked at in real Anki before
    review, so that macOS-only defects do not reach me.
27. As the owner, I want the other 46 quests with "obtained during quest"
    items converted by the Sol loop after Pass 18 lands, so that the supply-step
    feature spreads without blocking the queue fixes.

## Implementation Decisions

### Action queue: exact counts (ticket 01)

- The count is checked after every step, not only after the card. The card's
  step loop asks the queue whether the current entry's remainder is reached
  before each further step.
- The step that reaches the count makes only the remainder. For utilities, the
  existing batch cap of the production step carries the remainder. For skill
  steps that can make more than one unit in a step, the step takes the same
  cap; the implementer lists every such step handler and caps each. For kill
  entries, the combat burst takes the remaining kills as its stop count, the
  way the Slayer kill cap works, and the smaller of the two caps wins.
- A step that can only make a whole lot (15 arrow shafts from one log) keeps the
  whole lot, and the entry ends at its count: 2012 never made part of a lot, and
  removing products after their inputs were spent would lose what the player
  paid for. Orchestrator decision during the build, for the owner's review.
- When an entry reaches its count inside a card, the queue starts the next
  entry in the same review, and the card's remaining ticks go to it when it is
  a skill or utility entry. A combat or quest entry starts on the next card,
  because combat runs one burst per card and quests advance one stage per
  review. When no entry is left, the queue switches to Bankstanding and the
  rest of the card is spent there.
- Review-count entries are unchanged (one per card). Quest entries have no
  count.

### Action queue: ended entries and Clear (ticket 02)

- The queue holds only entries still to run: the first entry is the current
  one. A done or stopped entry is removed when it ends. The Event log keeps
  "Queue: <name> done" and the stop line; the review HUD shows the stop reason
  as now.
- A saved queue that still holds passed entries (the Pass 17 shape, with an
  index past them) loads with those entries dropped. This is the existing
  load-time cleanup, not a migration.
- The five places count only entries still to run.
- Clear queue always stops what runs and switches to Bankstanding with the
  reason "The queue was cleared.", with no dialog. Resume offers the action
  that ran, including a hand-started action. The Pass 17 rule that adding a
  plan never stops a hand-started action is unchanged.

### Queue box and add feedback (ticket 03)

- The queue box has no scroll area. It is as tall as its entries, one to five
  rows; a long entry wraps. The tab page above gives up the height, and on a
  short menu the tab page scrolls.
- A click on the title line folds the box to that line and unfolds it again.
  It starts open. The folded state persists like the menu's other remembered
  folds.
- After an add, the new row gets a short accent highlight that fades out in
  about 1.5 seconds, and the Add button reads "Added ✓ (n of 5)" for the same
  time.
- A refused add shows its real cause. The refusal reasons come from the queue
  itself, one text per cause; the generic "Type a count of 1 or more." stays
  only for a count below 1.
- The queue box hint no longer leaves a single word on its last line.
- This ticket writes working text; ticket 10 sets the final copy.

### Supply steps (ticket 04)

- A quest can declare supply recipes: for an item a quest stage needs, the
  recipe that makes it, by reference to the existing Utility recipe where one
  exists (for Goblin Diplomacy: crates for goblin mail, Aggie's three dyes,
  mixing orange, dyeing the mail orange and blue).
- On a quest review whose stage item is missing, the quest walks the recipes
  from the needed item down and runs the first recipe whose inputs the player
  holds and whose product is still needed. One recipe runs per quest review,
  one batch. A recipe whose product, or a product further along the chain, the
  player holds is skipped. The stage hand-in runs on its own review once the
  item is held.
- A recipe whose inputs are missing and cannot be made from held supplies stops
  the quest with a reason naming the missing supply and the step it is for.
- Goblin Diplomacy from raw supplies takes 10 quest reviews: crates, red dye,
  yellow dye, mix orange, dye orange mail, hand in orange, blue dye, dye blue
  mail, hand in blue, hand in plain mail. With three dyed or plain mails held
  as needed, it takes 3.
- The quest card and journal show the next supply step.
- The feature is data-driven so that the later loop briefs add recipes to other
  quests without code changes.

### Dyes (ticket 05)

- Two Utility rows join "Mix orange dye": "Mix green dye" (Blue dye + Yellow
  dye) and "Mix purple dye" (Blue dye + Red dye), each one of each input to
  one output, 0 XP, in the same group as orange, citing the Dyes revision
  5953125 quote in the source audit.
- The Bank's right-click menu on a dye gains "Mix with", listing each dye the
  player holds that mixes with it and the result. A click mixes one pair at
  once, with no card, as one Edit > Undo step. The menu reads the same three
  recipes as the Utility rows; there is no second recipe table.

### Wyson the gardener (ticket 06)

- Two one-click vendor purchases in the Shop tab, as Wyson the gardener in
  Falador Park: 20 Coins for 2 Woad leaves and 15 Coins for 1 Woad leaf,
  free-to-play, one purchase per click, citing revision 6226377. The shop data
  is regenerated from its generator.

### Tab arrows (ticket 07)

- The tab bar keeps Qt's own scrolling; a style override moves the left scroll
  button to the left end and offsets the tabs by that button's width (fact
  report B, option 1, tested natively). Each arrow is disabled at its end. The
  selected tab scrolls fully into view.

### Bank rows (ticket 08)

- Find what gives the bank grid less height than its rows need with a bank of
  the owner's size, and fix that cause so every row and heading keeps its full
  height and the grid scrolls. The owner's save copy for local reproduction is
  `/Users/armantarkhanian/Code/ankiscape-pass18/native/owner-player-data.json`
  (never committed).
- The cut Bank Claims description line shows whole.
- Nothing else on the Bank tab changes.

### GE with a full queue box (ticket 09)

- With the queue box at 2 and 5 entries, at the default menu size and 560
  points tall, every GE offer control keeps its full height and the page
  scrolls. Fix whatever squeezes it.

### Menu copy (ticket 10)

- Opus rewrites the text of the Pass 17 hill-climb screens (the Resume and stop
  lines on the review HUD, the queue box, the combat setup panel) and sets the
  final text of every Pass 18 string. The rule: elegant and minimal; a label
  where a label serves; no sentence that explains what a control already
  shows. This is the owner's explicit choice of model for menu text, so the
  `write-like-me` copy-model route does not apply.
- `AGENTS.md` gains one line with that rule.

### After landing (not a ticket)

- After Pass 18 is on main, the orchestrator writes one harvest brief for each
  of the other 46 quests in the quest audit
  (`/Users/armantarkhanian/Code/ankiscape-pass18/facts/E-quest-supply-steps.md`)
  into `~/.local/state/sol-loop/ankiscape/harvest-briefs/<order>-<slug>/brief.md`,
  naming the quest's items, the wiki quote and the supply-step feature.

## Testing Decisions

- Good tests drive the real review handler or the real widget and check what
  the player gets or sees: items in the bank, the queue box rows, the HUD line,
  widget geometry. They never stub the system under test.
- **Exact counts (01)** carry the most weight. An end-to-end test runs real
  reviews through the dispatch path. A Monte Carlo sweep over every queueable
  skill target, utility and combat target that the seeded bank can run, with
  random counts from 1 to three batches and speeds 1x, 5x and 10x, asserts
  that each entry ends with exactly its count, or stops short with a reason.
  The sweep writes its table under
  `/Users/armantarkhanian/Code/ankiscape-pass18/evidence/01/`. The existing
  tests that pin overshoot (`test_queue_reviews` platebody, `test_queue_state`
  count 10 to 13) change to the new rule.
- **Ended entries and Clear (02)**: end-to-end through the review handler and
  the menu command, including Clear while a hand-started action runs, and a
  Pass 17 save shape that loads with its passed entries dropped.
- **Queue box (03)**: Qt widget tests for height with one to five entries, no
  scroll bar, folding, the highlight and button text after an add, and each
  refusal text; offscreen screenshots at 560 points tall, dark and light.
- **Supply steps (04)**: end-to-end through the quest review handler from raw
  supplies (10 reviews, exact end state), from partial holdings (skips), and
  with a missing supply (stop reason). Prior art: the Goblin Diplomacy chain
  test and the early Darkan quest stage-gate test.
- **Dyes (05)** and **Wyson (06)**: logic tests for the recipes and purchases,
  a Qt test for the Bank "Mix with" menu, and the existing vendor-action
  tests.
- **Tab arrows (07)**: the tab-bar test changes so that it checks arrow
  positions under the product style instead of replacing the style.
- **Bank rows (08)**: a Qt test with a bank of about 150 item kinds across the
  auto categories, at the default size, 560 points tall and full width,
  asserting that no two cells or headings overlap.
- **GE (09)**: the macOS layout test runs the GE tab with the queue box at 2
  and 5 entries.
- **Native looks**: after each screen ticket (03, 05, 07, 08, 09, 10), the
  orchestrator runs a native look in real Anki through the Codex computer-use
  tester and gives its screenshots to the implementer. These looks are the
  check the owner weighs most. A final native check covers the whole build
  before the promotion gate.
- **Taste review**: before promotion, Kimi K3.1 reviews the native screenshots
  of the new interfaces (queue box, add feedback, Mix with menu, tab arrows),
  as `AGENTS.md` requires.

## Out of Scope

- A GE redesign; the hill-climb loop.
- Supply steps for quests other than Goblin Diplomacy (they go to the loop).
- "Use item on item" beyond mixing dyes; dyeing goblin mail stays a Utilities
  row and a Goblin Diplomacy supply step.
- Wyson's mole-part exchange.
- The Achievements rows drawn as stacked outlined boxes, and the Utilities
  search box that cuts the start of a long search: reported to the owner, not
  fixed.
- The native-check guard refusing real save keys, and manual native runs
  sharing no lock with the loop's native lane: recorded as papercuts.

## Further Notes

- The owner's Anki must restart to load new code.
- Codex reset to 0% weekly use at 23:42; the run may use Codex freely within
  the quota line.
