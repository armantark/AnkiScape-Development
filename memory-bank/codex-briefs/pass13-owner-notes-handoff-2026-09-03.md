# Pass 13 owner notes — handoff brief, 2026-09-03

Design seat: Fable, session 61069f54. Rulings: `memory-bank/design-thread-queue.md`
§4.24. Every dispatched agent obeys `memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`
in full. The orchestrator is parked (rulings ledger §57); the design seat runs this
programme alone.

## Goal

Close the Pass 13 owner notes: diary deeds that read as their own, one-click
activity starts, one Bankstanding notice per switch, bones learned as a drop,
quest fights that resolve, level-ordered target lists, Amulet of glory in the
Grand Exchange (GE), 2012 icons, and a Fish Flingers payout equal to the real
November 2012 game with a rollback of the owner's past games.

## Owner notes (verbatim, 2026-08-30 to 2026-09-03)

> The targets in the skills list (at least, herblore, I didn't bother to check
> the others) are not in level order. They should be
> If there already is a popup saying that you're out of material, then there
> doesn't need to be a second bankstanding warning notification. I was talking
> about the ones that were completely silent
> Mithril platebody icon is the old design
> Don't think regular amulet of glory is in the grand exchange? Only the trimmed
> versions
> There's no way to simply keep bones from enemies. I'm assuming "auto-bury
> bones" off means it just leaves them behind? idk? Edit: just learned that you
> never "learn" bones are a drop if "auto-bury bones" is on. Fix that
> [two dialogs: "Demon Slayer is blocked: Combat locked until battle support is
> enabled: Delrith level 27..." and the same for Vampyre Slayer, Count Draynor
> level 37] tf?
> Again, with activities: why do I have to press one button and THEN do "start
> activity"? It should just be one click. I just encountered this with a
> shooting star
> I know I keep asking about Fish Flingers but it is absolutely insane that I
> get TWO LEVELS worth of xp at level 39, like wtf dude. I REALLY need you to
> dig and figure out one last time why tf it is so high
> [three popups: "The Coal Train", "Fun For the Whole Family", "I Heard You
> Like Mudskips"] ?? And a bunch of other achievement diaries that I randomly
> got for no reason. May be a backlog from having reloaded the app but wtf,
> most of the ones didn't even make sense.

## Rulings (from §4.24)

1. A translated or invented deed shows its own name and sentence. Nothing in
   the game refers to the source deed. The source stays in the ledger.
2. A translated deed keeps the source's region, family, and difficulty, and
   must be fun. "Anywhere" translations are a lazy flattening and are rewritten.
3. One button starts every activity. Big Top keeps its queue as configuration.
4. Bones are learned as a drop before the bury step.
5. Fish Flingers pays the real November 2012 amount for the level and score.
   No invented rate. The owner's past games are rolled back to that amount.
6. The quest-combat resolver flag is deleted. Quest fights resolve.
7. Retroactive diary popups stay as they are.
8. Target lists sort by level in every skill. One Bankstanding notice per switch.
9. Amulet of glory (uncharged, (4)) enters the GE with a citation. Every icon
   with an Old School source is refetched from the 2012 wiki.

## Facts (fact-finders of 2026-09-03, read-only)

- The ledger `memory-bank/diary-curation-ledger/dormant-task-ledger.jsonl`
  holds 320 rows: 125 translated, 37 invented, 42 active, 116 dormant. Only
  the 37 invented rows carry `designed_name` and `designed_description`.
  `tools/achievement_diary_ledger.py:421-427` returns the source text for every
  row that is not invented. So the game shows "Dial to the fairy ring on
  Mudskipper Point" for a row that fires on one big-net catch.
- The popup `ui/ui.py:4565-4590` shows `task.name` and `task.description`;
  `DiaryTask` (`data/achievement_diaries/contract.py:39-54`) has no other text
  field. Reload shows no popups; the first review after a reload rescans every
  row and queues one popup per newly satisfied row (`core/logic.py:151-196`,
  `__init__.py:1344-1353,1561-1578`). Ruling 7: no change.
- Quest fights: `logic_pure/logic_pure_quest.py:109-124` reads
  `quest_combat_config["resolver_enabled"]`, default false, initialised at
  `core/storage_pure.py:701-704`. No production code sets it; tests set it at
  `tests/test_logic.py:10313-10324`. The message is built at
  `logic_pure/logic_pure_quest.py:846-862` and wrapped at
  `runtime/runtime_actions_production.py:1327-1335` and `1354-1361`. The
  levels shown are boss display levels. Demon Slayer stage 7
  (`data/quest_data.py:7055-7094`) is unreachable for every player today.
- Bankstanding: the seam `__init__.py:1604-1645` accepts `caller_owns_notice`;
  only two Crafting paths use it (`runtime/runtime_actions_shared.py:397-417`).
  Every other exhausted-material branch shows its own popup and then the
  deferred "Switched to Bankstanding" modal (`ui/ui.py:4600-4645`). Affected
  branches: gathering `:451-459,592-600`; production `:511-539,575-607,647-656,
  724-739,779-841,863-908,958-966,1031-1061,1181-1241,1387-1442`; utility
  `:773-928`; activities encounters `:76-96`; distractions `:135-158`; combat
  `:422-512`.
- Activities: the shared seam is target selection then
  `_start_surface_activity()` (`ui/ui.py:8927-8937,20431-20447,21298-21308`).
  Evil Tree arms only (`ui/ui.py:9117-9143`, "Select full event"). Shooting
  star's handler passes `activate=True` (`ui/ui.py:9465-9608`). Fish Flingers
  (`ui/ui.py:13743-13917`) and Big Top (`ui/ui.py:14877-15438`) have a "Start
  activity" control. The owner's shooting star two-step needs a reproduction.
- Bones: `combat_auto_prayer_training` ("Auto-bury bones",
  `ui/ui.py:7871-7876`) removes every bone from the kill's drops, awards Prayer
  XP, and adds two ticks per bone (`data/prayer_data.py:60-71,91-105`,
  `logic_pure/logic_pure_urns.py:405-416`). The learning record stores the
  drops after that step (`logic_pure/logic_pure_combat_model.py:1068-1094`), so
  the keep/drop list (`ui/ui.py:8161-8176`, `__init__.py:2099-2109`) never
  shows bones. Bank "Bury" targets already exist (`data/prayer_data.py:38-39`).
- Targets: `core/target_metadata.py:70-85` makes `sort_key` optional. Flat
  lists keep insertion order (`core/target_metadata.py:748-855`). Trees sort by
  `sort_key` or label (`ui/ui.py:5385-5553`); Herblore is a tree
  (`ui/ui.py:5555-5640`, groups at `data/herblore_data.py:353-365,425-435`).
- GE: `data/grand_exchange_data.py:41-67,100-109` derives the catalog from
  `item.tradeable` plus the generated exchangeable set
  (`generated/grand_exchange_period_generated.py`). `data/mining_data.py:87-98,
  370-395` marks Amulet of glory, (1) to (4), as not tradeable; only (t) and
  (t4) reach the GE.
- Icons: `assets_provenance.json` records 558 assets with an
  `oldschool.runescape.wiki` source (shopitems 166, smithingitems 66,
  combatenemies 62, questitems 40, crafteditems 32, prayeritems 32, and more).
  `smithingitems/mithril_platebody.png` is one (fetched 2021-08-20). The batch
  scraper precedent is `tools/fetch_smithing_assets.py`.
- Fish Flingers: `logic/fish_flingers_logic.py:270-316` pays
  `floor(max(162, 235*level - 73) * score / 48)` on review 8 of 8, reachable
  scores 28 to 43. At level 39: 5,303 to 8,144 XP per game. The formula is a
  Darkan reconstruction; the pinned wiki oldid 6529096 gives no table. The
  2012 research is in progress; slice S9 waits for it.

## Slices

### S1 `diary-deed-text` — the creative pass and the generator

Design seat authors. Fable subagents, one per region, draft; the design seat
reviews every row.

1. Extend `tools/achievement_diary_ledger.py`: `text_for` returns the designed
   name and description for `translated` rows too. Validation fails when a
   translated or invented row lacks either field, or when a designed
   description equals the source description.
2. For each of the 162 translated and invented rows, write `designed_name` and
   `designed_description`, and re-judge the trigger against ruling 2. A trigger
   that drops the region or the family gets a new trigger on an existing seam
   in the same region. Record each change in `notes` with the reason.
3. Regenerate the catalog through `tools/generate_achievement_diary_data.py`.
   Never edit the generated modules by hand.
4. Tests: no translated or invented task shows its source name or sentence;
   the catalog is reproducible from the generator; unique seams still hold.

Fix sites: `tools/achievement_diary_ledger.py`, the ledger, `data/achievement_diaries/*.py`
(generated). Tests: `tests/test_achievement_diaries.py`,
`tests/test_achievement_diaries_integration.py`.

### S2 `activity-one-click`

1. Every activity row exposes one Start button. The handler selects the target
   and calls the shared start seam in one click.
2. Evil Tree's "Select full event" and "Select nurture only" become Start
   buttons with the same names minus "Select".
3. Reproduce the owner's shooting star two-step on the offscreen harness: open
   the Activities tab, click the star row's button, and read the active
   target. Fix the path that left it armed but not started.
4. Big Top keeps its queue editor. Its Start button runs the current queue.

Fix sites: `ui/ui.py:9117-9143,9465-9608,13743-13917,14877-15438,8927-8937`.
Tests: `tests/test_main_menu_widget.py` (activity handlers),
`tests/test_circus.py`. Frontend-taste review before promotion (project rule).

### S3 `bankstand-single-notice`

1. Every exhausted-material branch listed in the facts routes its reason
   through the switch seam. The seam shows one modal whose text is the material
   reason. The separate error popup on that path goes away.
2. A switch with no prior popup (invalid target, "ended", "star unminable")
   keeps the modal as it is.
3. Tests: one dialog per switch on each affected branch; the event log keeps
   one entry per switch.

Fix sites: `__init__.py:1604-1645`, the runtime branch files. Tests:
`tests/test_runtime_actions.py`, `tests/test_integration_smoke.py`.

### S4 `bones-learned`

1. The learning record stores the kill's drops before the bury step.
2. Bones appear in the keep/drop list. With auto-bury on, kept bones are
   buried; with a "drop" override, they are left. With auto-bury off, they go to
   the pack as today.
3. Tests: an auto-buried kill learns Bones; the keep/drop override is honoured
   under both settings.

Fix sites: `logic_pure/logic_pure_combat_model.py:1068-1094`,
`logic_pure/logic_pure_urns.py:405-416`. Tests: `tests/test_runtime_actions.py`.

### S5 `quest-combat-flag-removal`

1. Delete `resolver_enabled` from `logic_pure/logic_pure_quest.py`, the
   default state in `core/storage_pure.py`, and every test that sets it.
2. Delete both message strings. The questing review action resolves the fight
   through the resolver; a fight the player cannot win reports the resolver's
   own outcome.
3. A save migration drops the stale key.
4. Tests: Demon Slayer stage 7 resolves with Silverlight; the player-level gate
   from §4.22 still applies where an encounter declares one.

Tests: `tests/test_logic.py:10313-10324` and quest-combat neighbours.

### S6 `target-level-order`

1. Every target row gets a `sort_key` of (level, label).
2. Flat lists and tree groups sort by that key. Tree groups keep their order.
3. Tests: Herblore, Mining, and one tree skill list in level order.

Fix sites: `core/target_metadata.py`, `ui/ui.py:5385-5553`.

### S7 `glory-ge`

1. Mark Amulet of glory (uncharged) and Amulet of glory (4) tradeable and add
   them to the exchangeable set; (1) to (3) stay off the GE. Cite the 2012 GE
   page for each row.
2. Tests: the GE catalog lists both; the partly charged ones stay absent.

Fix sites: `data/mining_data.py:87-98,370-395`, the generated exchangeable set.

### S8 `icon-2012-sweep`

1. Write `tools/fetch_2012_icons.py`: for every asset with an Old School
   source in `assets_provenance.json` (279 entries; each carries two Old
   School URLs), query the RuneScape wiki file history, take the last revision
   strictly before 2012-11-20T00:00:00Z (the pre-EOC cutoff in
   `memory-bank/pre-eoc-source-verification-standard.md`), download it, and
   rewrite the provenance entry. Retries and a checkpoint file are required.
2. Report every asset with no pre-cutoff revision in the wiki. Do not guess an
   icon for it; the report goes to the owner.
3. Visual check: a contact sheet of before and after icons per directory.

### S9 `fish-flingers-2012` — waits for the research

1. Implement the sourced November 2012 payout with a citation per term.
2. Write a save migration that recomputes the XP of every recorded past game
   under the new formula and subtracts the difference. The migration reports
   what it changed in the event log.
3. Tests: level 39 pays the sourced amount at the sourced score; the migration
   on the owner's save shape is exact.

## Coordination

- `ui/ui.py` is touched by S2, S3, S6. Authors declare their line ranges.
- `core/storage_pure.py` migrations: S5 then S9, in that landing order.
- S1's creative pass is the long pole and blocks nothing else.
- The canonical checkout is the owner's live Anki install. No slice edits it.
  Pooled worktrees only, through `tools/worktree_guard.py lease`.

## Verification

Per slice: focused suites plus neighbours; both lanes and offscreen Qt
screenshots where the UI changes. Promotion: `tools/promotion_gate.py` on the
merged tree, one batch, after re-absorbing `main`. The owner does the
real-reviewer pass in the morning.
