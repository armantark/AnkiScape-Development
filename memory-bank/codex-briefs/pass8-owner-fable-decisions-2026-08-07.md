# Pass 8 owner decisions — Fable co-ideation result

Date: 2026-08-07
Source handoff: `memory-bank/codex-briefs/pass8-owner-fable-co-ideation-handoff-2026-08-07.md`
Status: all five decisions are settled. Codex owns implementation, tests, native
verification, and commits.

This note records the owner's answers from the 2026-08-07 co-ideation session.
It does not reopen the settled Pass 8 requirements in the source handoff.

## 1. Owner answers

Multiple-choice answers, in session order:

1. Tab order: "After Equipment" — Shop and Grand Exchange go after Equipment.
2. Bank tabs: "One tab per item" — each item has exactly one home tab.
3. Bank drag: "Swap + Insert toggle" — full RS parity with a persistent mode
   toggle.
4. Category order (verbatim): "Different options within the categories: most
   recently used, date added, alphabetical, anything else that makes sense,
   and finally manual".
5. Headers with auto-categories off: "Headers disappear".
6. Tab controls (verbatim): "Add + drag-reorder tabs, Rename (tooltip names),
   Explicit delete, Custom icon picker, Whatever is better for game design.
   I'm fine with a little bit of contrivance on the UI compared to game
   content, since RS's UI is notoriously stupid sometimes and it take them
   forever to rework basic issues in the UI (for example, that you couldn't
   even edit a GE order until last year in OSRS??)".
7. Bank layout: "A: RS-classic top strip" — the ASCII frame is in section 3.
8. Skills guide placement: "Side-by-side".
9. Guide focus on target click: "Guide follows the click".
10. Guide row families (verbatim): "Actions/targets, Equipment, Whatever it is
    in-game".
11. Locked guide rows: "Full names, like RS".
12. First new collection family: "Boss/monster drop log".
13. Locked collection entries: "Source-chosen mix".
14. Collections navigation: "Left family list + right grid".
15. Completion totals: "Both global + per family".
16. Star exit, first pass (verbatim): "It's too easy to miss D&D
    notifications. Not sure. I was thinking it should just give you a heads up
    that the shooting star is unminable and then you can choose to wait or
    not".
17. Star exit scope: "All stars" — the old Casual waiting contract is retired.
18. Star watch follow-up: "Banner + one-click rejoin".

Answer 6 also sets a standing design principle: game content keeps strict RS
parity, but the UI can use modern conveniences when they are better than the
period RS interface.

## 2. Complete top tab order

The menu must show the top tabs in exactly this order:

`Skills | Stats | Bank | Equipment | Shop | Grand Exchange | Challenges | Quests | Achievements | Collections | Settings`

The current order in `ui/ui.py` is Skills, Shop, Grand Exchange, Quests, Bank,
Equipment, Stats, Challenges, Achievements, Collections, Settings. The
reorder must keep each tab's deferred-build behavior.

## 3. Bank grid and tabs contract

### Model

1. The bank grid is presentation state over the flat inventory. The flat
   store stays the single source of truth, per
   `memory-bank/inventory-carry-model-design-2026-07-07.md`.
2. Each item has exactly one home tab and one saved grid position. A move to
   another tab removes the item from the old tab.
3. New items without a saved position go to the end of the main tab.
4. Most-recently-used and date-added sorts need per-item counters. These
   counters must count answered reviews. They must not read wall-clock time.

### Layout (owner-selected frame A)

```
[Search____] [Sort: Manual v] [x] Auto-categories  [Swap|Insert]
[ALL][*][pick][food][swrd][+]        <- tab strip (drop targets)
+----------------------------------+---------------------+
|  -- Ores --                      | Selected: Coal x214 |
| [c][c][c][c][c][c][c][c]         | reqs / tooltip info |
| [c][c][c]                        | [Set carried qty..] |
|  -- Logs --                      |---------------------|
| [c][c][c][c][c]                  | Carried pack (4x7)  |
|  ... scrolls vertically ...      | Auto | Custom  grid |
+----------------------------------+---------------------+
```

1. The tab strip goes across the top of the grid, like the real bank.
2. The right column keeps the selected-item detail, the Bank actions, and the
   existing Auto/Custom carried-pack panel.
3. The grid uses 8 to 10 columns at the owner's 1280-by-752 menu size.
4. Item search, quantity display, and keyboard accessibility must survive.

### Tabs

1. A "+" target creates a tab when the user drops an item on it.
2. The user can drag tabs to reorder them.
3. A tab that becomes empty auto-deletes. Explicit delete is also available
   from the tab context menu; its items return to the main tab.
4. The default tab icon is the first item in the tab. The user can pick a
   custom icon from any owned item.
5. The user can rename a tab. The name shows as a tooltip or a small label.

### Drag and sort

1. A persistent Swap/Insert toggle controls drops on occupied cells. Swap
   exchanges the two items. Insert shifts the following items right.
2. A sort selector orders items inside each section: Manual, Most recently
   used, Date added, Alphabetical, plus other computed sorts that make sense
   (for example Quantity and Value). Manual is the only mode that permits
   drag reorder; computed sorts show a read-only order.

### Auto-categories

1. A checkbox at the bottom turns auto-categories on and off.
2. On: registry category headers render inside each tab, and the sort
   selector orders items inside each category section. A drag cannot change
   an item's category, because the category comes from the item registry.
3. Off: headers disappear and each tab is one flat RS-style grid under the
   same sort selector.

## 4. Skill guide contract

> Owner correction, 2026-08-07 (later): the guide belongs in the **Stats**
> tab, not the Skills tab. Answers 8 and 9 in section 1 were given against
> the wrong surface and are superseded by items 1 and 2 below. The
> screenshot evidence is the red-outlined empty region under the selected
> skill's stats block in the Stats tab.

1. The guide fills the empty region in the Stats tab below the selected
   skill's stats block (current/base level, total experience, experience to
   next level, level progress). It uses the full width of that region and
   scrolls on its own. The stats block stays unchanged above it.
2. The Stats skill grid drives the guide: select a skill and its guide
   renders. The guide opens scrolled to the player's current level, so the
   next locked unlocks are visible. Guide rows are informational in the
   first build; they have no click behavior.
3. The first build ships the actions/targets family and the equipment family.
4. The section structure must copy the period in-game skill guide for each
   skill ("whatever it is in-game"). Harvest each skill's period guide
   sections through the normal evidence order before adding more families.
   Omit a section when no sourced registry data exists. Do not invent rows.
5. Locked rows show the level and the full item or action name, dimmed, like
   the real guide. The guide never shows sources, shops, drops, or trace
   data.
6. All rows derive from the current registries and source audits. Do not
   create a second unlock database.

## 5. Collections contract

1. Navigation: a left column lists collection families; the right side shows
   the selected family's grid or rows with its own search. Drop-log targets
   nest under their family in the left column.
2. Families: Music Log stays first. The boss/monster drop log is the second
   family. It records logged drops per target and replaces the low-level
   disclosure-triangle data path from the Pass 6 contract.
3. Locked entries use a per-family policy ("source-chosen mix"):
   - Music keeps its player-facing hints.
   - The drop log shows a dimmed entry with the item name after the player
     has killed the target at least once. Before that, entries show "???".
4. Totals: the Collections header shows one global collected count. Each
   family row in the left column shows its own n/m count.
5. The surface must not show source paths, oldids, trace state, internal
   status names, or debug labels.

## 6. Shooting Star low-level exit contract

1. Scope: every inaccessible layer triggers this flow, including a star that
   is too big at join time. This replaces the earlier Casual waiting
   contract for all stars. The old wait-visibly state is retired.
2. When the current layer requires more Mining than the player has, the
   activity auto-stops and the selection clears. Reviews continue on
   whatever the player selects next.
3. The heads-up must be unmissable: one event-log row plus one persistent
   banner in the review strip. The banner reads "Star unminable at your
   level" and offers two actions: "Watch this star" and "Dismiss". It is not
   a transient popup, and it persists across sessions until the user acts.
4. "Watch this star" arms a per-star watch. When a mineable layer or the
   Star sprite appears, a new persistent banner offers one-click "Mine star"
   rejoin. The watch never auto-rejoins and never interrupts the selected
   activity.
5. "Dismiss" removes the banner and ends tracking for that star.
6. All timing stays review-driven. No wall-clock reads.

## 7. Implementation acceptance checks

1. The top tab bar shows the exact section 2 order, with deferred tab builds
   intact.
2. Bank: one home tab per item survives save and reload; Swap and Insert both
   work; each sort mode orders one seeded fixture correctly; Manual is the
   only draggable mode; the auto-categories checkbox adds and removes
   headers; MRU and date-added counters advance by answered reviews only.
3. Bank layout: offscreen Qt geometry probes plus native MacBook Pro
   screenshots at the 1280-by-752 menu size show the full frame-A layout
   with search, quantity, actions, and the carried-pack panel intact.
4. Skill guide: rows come only from existing registries and audits (no new
   unlock data files); the guide renders in the Stats tab under the stats
   block; a skill selection in the Stats grid swaps the guide and opens it
   at the player's current level; locked rows are dimmed with full names;
   no source or trace strings render.
5. Collections: the left list and right grid render Music and the drop log;
   undiscovered targets show "???"; discovered items unlock per kill records;
   global and per-family totals agree with the view data; no debug strings.
6. Shooting Star: an inaccessible layer at join and at depletion both stop
   the activity, write the event row, and raise the persistent banner; the
   watch banner rejoins in one click; undo rolls the whole transition back;
   no wall-clock reads.
7. Both repository test lanes pass, and native MacBook Pro evidence exists
   for each UI surface, per the standing Pass 7 verification rules.

No unresolved conflict remains.

## 8. Owner visual parameters (2026-08-07, from the playground)

The owner explored `tools/playgrounds/pass8-ui-playground.html` and set these
parameters that the contracts above left open. More can follow; each addition
gets a dated entry here.

Bank tab, within frame A:

1. The item grid uses 12 columns of 54-pixel cells.
2. The tab strip shows icons with short names, not icons alone.
3. The right column (selected-item detail, Bank actions, 4-by-7 carried
   pack) gets about 280 pixels of width.

Collections, within the settled left-list and right-grid shape:

4. The left family column gets about 244 pixels of width.
5. The drop log presents as list rows, not an icon grid.
6. Discovered-but-unowned entries dim to about 58 percent opacity.
   Undiscovered entries stay concealed per section 5.

Shooting Star banners:

7. The banners use a neutral grey tone.
8. The banners use an outline style: transparent fill with a colored
   border and colored text, not a filled block.

The owner also confirmed the two section 4 mappings on 2026-08-07: the
guide opens scrolled to the player's current level, and guide rows have no
click behavior in the first build.
