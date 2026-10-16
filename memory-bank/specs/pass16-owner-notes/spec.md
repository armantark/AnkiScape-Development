# Pass 16 owner notes

Source: the owner's notes file `~/Downloads/ankiscape notes.rtfd`, Pass 16 and
the last Pass 15 line, read on 2026-10-15. Grill answers of 2026-10-15 settle
every decision below. Fact-finding notes with code citations at main
`839b86a7`: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass16/facts.md`.

## Problem Statement

The owner played through Priest in Peril, Stolen Hearts, Skippy and the
Mogres, Runecrafting and Prayer, and hit eleven separate problems:

- Searches miss what the owner typed. "tara" finds no tiara, "Stolen Hearts"
  is the last of 11 quest results, and the Utilities list has no search bar.
- The filters under the quest search bar are spaced unevenly.
- Snape grass has no gathering source, and the nettle tea step is hidden
  behind a Cooking row called "Boil nettle-water".
- The tiara mould looks impossible to add to the tool belt. It is already on
  the belt, but nothing in the Bank says so.
- The progression guide sends the owner to Mazchna, but the Slayer Masters
  tab offers only Turael.
- Quest lamps arrive silently in Bank Claims. A lamp fixed to one skill still
  opens the skill grid, and no lamp can be destroyed.
- The Wicked hood works only from a card in the Runecrafting panel and only
  when it sits in a carried pack, and feeding a talisman to it costs a review.
- The Prayer panel puts "Gilded altar mode: Hosted - 350% XP" above every
  target. The owner thought plain Bury was an altar offering.
- Every 28 bones, plain Bury pays a 2-3 review "Running to the altar" trip.
- XP drops truncate tenths: a 4.5 XP burial shows "+4 XP" every time.

## Solution

- One shared search matcher serves every search bar. It ranks name matches
  before metadata matches and forgives one missing letter.
- The Utilities and Activities lists get the same search bar as the Skills
  lists.
- The quest filter row is laid out on one spacing scale.
- A "Gather snape grass" row at the Hobgoblin Peninsula site joins the
  gathering group, and the nettle tea Cooking row names its product.
- A Bank tool that is on the tool belt says so in its right-click menu.
- The Slayer Masters tab shows every live master, with locked masters greyed
  and their reason stated. Mazchna needs combat level 20 only.
- Quest completion names the lamps that wait in Bank Claims. Fixed-skill lamps
  pay on "Claim". Every lamp row can be destroyed after a confirmation.
- The Wicked hood gets right-click menus in the Bank and on the Equipment head
  slot, and the Runecrafting card stays. A fed hood is packed for Runecrafting
  automatically. A talisman or tiara feeds the hood from its own right-click
  menu, at once.
- The Prayer panel shows the altar mode box only for an altar target, and
  Bury and Scatter work at the bank with no travel.
- XP drops show the change in each skill's whole-number total, so tenths carry
  forward: +4, +5, +4, +5.

## User Stories

1. As a player, I want to type "tara" and see the tiaras, so that one typo does not hide an item.
2. As a player, I want the quest named "Stolen Hearts" first when I type its name, so that I do not scroll past quests that only list it as a requirement.
3. As a player, I want my chosen quest Sort to order the results inside each match group, so that the Sort still means something while I search.
4. As a player, I want the Bank, Grand Exchange, shop, quest, Help and skill target searches to behave the same way, so that I learn one search.
5. As a player, I want a search bar on the Utilities list, so that I find "Fill bowl with water" among 166 rows.
6. As a player, I want a search bar on the Activities list, so that it matches the Utilities list.
7. As a player, I want a search on Utilities or Activities to leave my current action unchanged, so that typing never starts or stops anything.
8. As a player, I want the quest filters to sit on one even spacing, with each label next to its box, so that the filter row reads cleanly at 720 px.
9. As a player, I want a Utilities row that gathers snape grass and says where, so that I can make the hangover cure for Skippy and the Mogres.
10. As a player, I want the Cooking row that makes nettle tea to be called by its product, so that I find it when I look for nettle tea.
11. As a player, I want the Cooking drinks group to have a readable name, so that I do not see a raw internal word.
12. As a player, I want a right-click on a Bank tiara mould to tell me it is already on my tool belt, so that I know I do not need to add it.
13. As a player, I want every on-belt chip in the Toolbelt panel to say it is always on the belt, so that the panel explains itself.
14. As a player, I want the Toolbelt panel hint to cover every tool, not only hatchets and pickaxes, so that the hint is true.
15. As a player at combat level 20 or more, I want to choose Mazchna in the Slayer Masters tab, so that I can follow the progression guide.
16. As a player below a master's requirement, I want to see that master greyed with the reason, so that I know what to train.
17. As a player, I want each master card to show the master's name and chathead, so that I know who gives the task.
18. As a player, I want "Get assignment" to use the master I last used and can still use, so that I do not reselect each time.
19. As a player, I want a locked master to refuse a task even through a stale button, so that the rule holds everywhere.
20. As a player, I want the quest-complete message to say how many lamps wait in Bank Claims and how much XP each gives, so that I do not miss them.
21. As a player, I want a lamp fixed to one skill to pay that skill when I click "Claim", so that I do not pick from a one-skill grid.
22. As a player, I want a choice lamp to keep the select-then-confirm skill grid, so that I choose where the XP goes.
23. As a player, I want to destroy a lamp I do not want after a confirmation that warns it is gone for good, so that my Bank Claims stays clean.
24. As a player, I want Undo to restore a lamp I destroyed by mistake, so that one wrong click is reversible.
25. As a player, I want the Elder Kiln lamp to need level 75 as in 2012, so that its rule matches the game.
26. As a player, I want to right-click the Wicked hood in the Bank and see "Withdraw essence" with the count left, so that I use it without the Runecrafting panel.
27. As a player, I want rune withdrawals and teleports as submenus of fed altars, each with the count left and any level lock, so that I see my options in one place.
28. As a player, I want the same hood menu on the Equipment head slot when I wear the hood, so that a worn hood works the same way.
29. As a player, I want the Runecrafting hood card to stay, so that I can still use the controls I know.
30. As a player in the Auto carried layout, I want a fed hood packed for the Runecrafting target whose altar it fed, so that I do not set up a custom pack.
31. As a player, I want to right-click a talisman or tiara and feed it to the hood at once, so that feeding does not cost a review.
32. As a player, I want Undo to reverse a hood feed, so that a wrong feed is reversible.
33. As a player, I want the gilded altar mode box only when an altar target is selected, so that plain Bury does not look like an altar offering.
34. As a player, I want the Prayer panel to make the selected method obvious, so that I know whether I bury, scatter, or offer.
35. As a player who buries bones, I want my bank trips to cost no travel, because I bury at the bank, so that 1 bone per review is the real pace.
36. As a player at an altar or the Ectofuntus, I want the existing altar trip cost to stay, so that those methods keep their sourced pace.
37. As a player, I want a 4.5 XP burial to show +4, then +5, then +4, so that the drops add up to my real gain.
38. As a player, I want a skill whose whole-number XP did not change to stay out of the XP drop, so that I never see "+0 XP".
39. As a player, I want the event log to keep exactly what the XP drop showed, so that the log and the popup agree.

## Implementation Decisions

- **Search matcher.** One pure matcher module returns a match tier or no
  match for a query against a primary name and optional metadata. Tiers, best
  first: exact name, name prefix, every token in the name, every token in name
  or metadata, then fuzzy. A query token of four or more characters matches
  fuzzily when it is an in-order subsequence of a word or within edit
  distance 1 of one. Shorter tokens match only as substrings, so short
  queries do not flood the list. Every search bar uses it: the shared filter
  bar, the Skills target lists, the quest list, Bank, Grand Exchange, shops,
  Help, Achievements and Collections. While a query is present, results sort
  by tier first and by the chosen Sort inside each tier. Help keeps its own
  title ranking only where the shared tiers cannot express it.
- **Utilities and Activities search.** The list builder that draws both lists
  gets the shared filter bar above its tree. Filtering never changes the
  current utility or activity. Favourites, the context menu, the details
  stack and the landmarks group keep working on a filtered tree.
- **Quest filter spacing.** Opus 5.5 authors this ticket at the owner's
  request. The flow layout centres items vertically on each line, each
  label-and-box pair gets an explicit small gap, and the filter bar and quest
  tab use one spacing scale. The flow layout and filter bar are shared, so the
  ticket recaptures every surface that uses them.
- **Snape grass.** One gathering Utility row, "Gather snape grass", models the
  2012 Hobgoblin Peninsula spawn: 3 clumps a trip, no requirement, the
  existing snape grass icon, and the site named in its text. Source: Snape
  grass oldid 6269500 and the Darkan spawn list.
- **Nettle tea.** The Cooking row that turns nettle-water into nettle tea is
  named for its product, as the other Cooking rows are, and the drinks family
  gets a readable group label.
- **Tool belt.** The Bank right-click menu shows a disabled "On tool belt"
  entry for any item that is on the player's belt, with a tooltip that says
  the belt copy is used. Each on-belt chip carries the always-on tooltip, and
  the panel hint covers all belt tools. The belt data does not change.
- **Bank right-click menu module.** The Bank item right-click menu builder
  leaves the main UI module for its own UI module before any ticket adds
  entries to it, because three tickets add entries and the main UI module
  cannot grow.
- **Slayer masters.** This builds the recorded owner decision 6 in the Slayer
  contract (progression-visible master roster): one card per live master, in
  roster order, with name and chathead from the master persona; ineligible
  masters greyed with each unmet requirement stated. A pure locked-reasons
  function owns eligibility, and the assignment command refuses a locked
  master. "Get assignment" on the Assignment tab and its empty state use the
  last master the player used who is still eligible, else the default. The
  stale "More masters unlock..." note goes. Mazchna's quest requirement goes,
  because Priest in Peril stopped gating Morytania in March 2012 (Priest in
  Peril oldid 6487728; Mazchna oldid 6548393 names combat 20 only); the source
  audit and its test record the correction.
- **Quest lamps.**
  - A lamp whose allowed skills are exactly one is a fixed-skill lamp. Its row
    button reads "Claim" and pays that skill with no grid. Three quest claims
    qualify today: the Stolen Hearts Agility and Thieving lamps and the Myths
    of the White Lands Agility reward.
  - A choice lamp keeps the shared icon-grid select-then-confirm dialog, even
    when only one allowed skill meets the minimum level.
  - The quest-complete message adds one sentence that names the lamps now
    waiting in Bank Claims, with count and XP. Every quest completion path
    that shows that message gets it.
  - Every lamp row gets "Destroy". A confirmation shows the 2012 destroy
    warning; on confirm the claim is forfeited, leaves the inbox, and never
    returns. Destroy is an undoable direct action, like Claim. Forfeit is a
    claim state that the eligibility rules treat like claimed.
  - The Elder Kiln lamp's minimum level becomes 75.
- **Wicked hood menu.**
  - The hood's right-click menu, in the Bank and on the Equipment head slot,
    offers "Withdraw essence (N left)", a "Withdraw runes" submenu of fed
    altars with counts, a "Teleport" submenu of fed altars marked with any
    level lock, and the existing Wear or Remove entry.
  - Every entry calls the existing hood command API, which keeps its rules.
    An entry the command would refuse is disabled with the refusal reason.
  - A hood held in the Bank is operable from these menus. Output still goes
    to the current Runecrafting target's carried pack, per the recorded hood
    ruling.
  - The Runecrafting panel card stays as it is (owner, 2026-10-15: "no harm in
    having two interfaces").
  - In the Auto carried layout, a fed hood that is not worn joins the pack of
    a Runecrafting target whose altar it fed when no tiara or staff already
    gives access. A carried hood grants that altar's access like a talisman.
- **Hood feeding.** Each talisman and tiara that the hood can take gets "Feed
  to Wicked hood" in its Bank right-click menu. Feeding consumes it at once
  through the existing feed rule, as an undoable direct action. The
  review-driven "Hood feeding" Runecrafting targets go. The 2012 sources say
  feeding gave Runecrafting XP with no amount; the ticket looks for the amount
  in the Darkan source first, and with none found the feed stays at 0 XP as a
  registered placeholder.
- **Prayer panel.** The gilded altar mode box shows only while a gilded altar
  target is selected. The panel names the selected method and its multiplier
  in its status line, so Bury, Scatter, Ectofuntus and Gilded altar read
  differently.
- **Prayer bank trips.** Bury and Scatter targets work at the bank: their
  trip has no travel, like Crafting and Herblore. The 2.678-review altar
  trip, derived from the gilded altar method in the trip-cost source audit,
  stays for gilded altar targets; Ectofuntus keeps its own cost.
- **XP drops.** For each skill, the drop is the change in the whole-number
  total from before to after the review. A skill with a zero change is left
  out, and a review with no change shows no XP drop. The stored XP and every
  award stay exact floats. The same text feeds the popup, the event log and
  the Qt fallback.

## Testing Decisions

- A good test drives the real kernel or the real widget and checks what the
  player sees or what the save holds. No test stubs the system under test.
- Seams and layers:
  - **Pure logic, unit layer:** the search matcher tiers and fuzzy cases
    ("tara" finds "Tiara", a near miss is rejected), Slayer locked reasons,
    lamp claim and forfeit state, and the XP drop whole-number change.
  - **Review kernel, integration layer:** each gameplay ticket answers real
    reviews through the review handler: snape grass gathered, a Bury trip
    with 0 travel reviews, an altar trip unchanged, a quest completion
    message naming its lamps, a hood feed and a menu essence withdrawal, a
    locked master refused, and four 4.5 XP burials showing +4, +5, +4, +5.
  - **Offscreen Qt, end-to-end layer:** every ticket that changes what the
    player sees builds the main menu offscreen at 560 px tall, after
    `show()`, `resize()` and event processing, per the AGENTS.md rules.
    It checks `text_fit_defects` and saves before and after captures as the
    ticket's evidence. It adds one line to `memory-bank/play-checklist.md`.
    These checks carry the verification weight for UI tickets.
  - **Owner in Anki:** the quest filter spacing ticket ends `built` until the
    owner looks at it in Anki. Every other ticket is `done` when its
    automated layers pass.
- Prior art: `tests/ui_flows/test_skill_target_search.py`,
  `tests/ui_flows/test_tool_belt_panel.py`,
  `tests/ui_flows/test_slayer_progress.py`, `tests/test_slayer_logic.py`,
  `tests/test_undo_seam_wickedhood.py`, `tests/mogres/test_miniquest_and_target.py`,
  `tests/test_integration_smoke.py`, `tests/ui_flows/test_bank_quest_fit.py`.
- Each ticket runs its focused tests locally. The run's landing passes the
  full promotion gate with `--remote-lanes`.

## Out of Scope

- The parked notes, on the Kanban: one-off item uses such as filling a water
  jug, with a manual cap per card, and a queue of actions so a run of
  resources does not end in Bankstanding.
- 12 other 2012 quest choice rewards that the game lacks, on the Kanban. Reward
  revisions: A Tail of Two Cats 6430177, Legends' Quest 6529921, Shadow of the
  Storm 6555496, Meeting History 6534402, Blood Runs Deep 6558062, While
  Guthix Sleeps 6584290, The Void Stares Back 6549183, Ritual of the Mahjarrat
  6564051, Branches of Darkmeyer 6588545, the third 23,000 XP Temple at
  Senntisten lamp 6516464, Death Plateau 6547020, and the Myths of the White
  Lands 500 XP Antique lamp 6555850.
- The Waterbirth Island snape grass site: 27 clumps in 2012 (16 in Darkan),
  needs The Fremennik Trials or a 1,000-coin trip (Snape grass oldid 6269500).
- Glove protection when picking nettles and the second nettle the Skippy step
  consumes; both are qualified limits in the Mogre source audit.
- Slayer task families gated on Priest in Peril for Morytania access; they may
  rest on the same stale reading as Mazchna's gate (Morytania oldid 6309115).
  Surfaced, not fixed.
- A Bank right-click "Bury" on bones (owner, 2026-10-15: it does not matter).

## Further Notes

- Every implementer obeys
  `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` in full. Its rules on
  guarded worktrees, the canonical checkout, git and sourcing are binding.
- slop-gate refuses a commit that grows a code or test file already above
  1000 lines (the main UI module is about 29,000 lines and the add-on entry
  module about 5,700), refuses cyclomatic or cognitive complexity above 15 or
  Halstead difficulty above 80 in a touched function, and refuses a new code
  file in a directory that already holds 40 (`logic/`, `logic_pure/`, `data/`,
  `tools/` and `tests/` are full; `ui/` and `core/` have room). Hold an
  oversized file at net zero by moving a self-contained block into a new
  module. `python3 tools/maintenance/function_metrics.py` measures a function
  exactly as the hook does.
- The native-check goal in another thread lands on main through the same
  promotion gate and owns the native GUI and the MacBook mirror. A remote run
  that prints "Remote mirror busy; waiting" is queued; let it wait.
