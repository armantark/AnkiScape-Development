# Early Darkan Quest Stage Batch - 2026-06-22

This slice continues the all-quest stage-parity goal, but it does not complete
that goal. It replaces generated broad rows for Goblin Diplomacy, Ernest the
Chicken, and Black Knights' Fortress with focused Darkan-backed stage chains,
adds quest-item assets for the new blockers, and leaves branch-heavy Shield of
Arrav deferred because the current model cannot honestly express its
Phoenix/Black Arm/partner-exchange state yet.

## Source Hierarchy

- Local 2011Scape item identity was checked through
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` for quest
  item names before wiring inventory keys.
- Darkan/2012scape supplied Goblin Diplomacy mechanics:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/goblindiplomacy/GoblinDiplomacy.java`
  defines the orange, blue, and regular/brown goblin mail hand-ins as separate
  stage transitions and deletes the submitted mail at each transition.
- Darkan/2012scape supplied Ernest the Chicken mechanics:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/ernestthechicken/ErnestTheChicken.java`
  and `OddensteinErnestChickenD.java` define the Oddenstein start dialogue,
  machine-part requirements, poisoned fish food, pressure gauge, grimy key,
  rubber tube, oil can, and final hand-in.
- Darkan/2012scape supplied Black Knights' Fortress mechanics:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/blackknightsfortress/BlackKnightsFortress.java`
  and `SirAmikVarzeBlackKnightsFortressD.java` define the 12 quest point start
  requirement, Iron chainbody/Bronze med helm disguise, grill-listening step,
  cabbage cauldron sabotage, Sir Amik report, and 2,500 coin reward.
- Shield of Arrav was audited against Darkan `shieldofarrav` sources and local
  item identity, but it remains deferred. It needs a route-bundle model for
  Phoenix Gang versus Black Arm Gang, partner exchange state for the shield
  halves, and branch-specific hand-ins. Flattening those into one all-item stage
  would recreate the old start-only mistake in a different shape.

## Implemented Model

Backend:

- `quest_data.py` now defines focused overrides for Goblin Diplomacy, Ernest the
  Chicken, and Black Knights' Fortress.
- Goblin Diplomacy has four internal stages. Stage 1 consumes Orange goblin
  mail, stage 2 consumes Blue goblin mail, stage 3 consumes Goblin mail, and
  valid completion grants 5 quest points, one Gold bar, and 200 Crafting XP.
- Ernest the Chicken has nine internal stages. Oddenstein dialogue gates the
  start, fish food plus poison produce Poisoned fish food, poisoned food
  produces the Pressure gauge, Spade produces the Grimy key, Grimy key produces
  the Rubber tube, the lever puzzle produces the Oil can, and the final hand-in
  consumes Pressure gauge, Rubber tube, and Oil can before awarding 3,000 Coins,
  10 Eggs, and 300 Feathers.
- Black Knights' Fortress now uses the sourced 12 quest point start requirement.
  Iron chainbody and Bronze med helm are required tools for the infiltration
  stage, the grill-listening step is a required action, stage 3 consumes
  Cabbage, and the Sir Amik report completes the quest for 3 quest points and
  2,500 Coins.
- `logic_pure._has_quest_tool()` now accepts required quest tools from worn
  equipment as well as inventory, so the Black Knights disguise works when the
  player has equipped the gear.

Frontend:

- The existing Quests tab blocker surface now covers the new stage chains
  without new UI-specific state. The Qt proof case is Ernest the Chicken stage 3,
  which shows `Blocked: Needs Fish food x1, Needs Poison x1`.
- Existing `can_start`, `in_progress`, `blocked_at_stage`, `completed`, and
  `locked` states are preserved. The Black Knights disguise is a finishability
  gate after the quest starts; it is not flattened into a start lock.

Assets:

- Added quest item icons for Orange goblin mail, Blue goblin mail, Goblin mail,
  Fish food, Poison, Poisoned fish food, Pressure gauge, Grimy key, Rubber tube,
  and Oil can under `questitems/`.
- Provenance is recorded in `assets_provenance.json`. Mechanics remain sourced
  from local item identity and Darkan quest code; OSRS/RS wiki art is visual
  fallback only.

## Audit Numbers

`python3 tools/audit_quest_stage_gate_coverage.py` after this slice:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 412
quests_with_item_or_tool_blockers: 174
quests_with_combat_blockers: 119
combat_encounter_rows: 283
combat_encounters_with_any_stats: 176
combat_encounters_with_resolver_stats: 175
requirement_row_kinds:
  consumed_inventory: 30
  consumed_inventory_options: 1
  inventory: 207
  inventory_options: 58
  produced_inventory: 19
  tools: 94
quests_without_stage_requirements:
```

Focused stage-row accounting from `quest_data.py` replacement/addition maps:

```text
quests: 194
stage_rows: 412
focused_rows: 93
generated_rows: 319
focused_quests: 24
```

## Remaining Gaps

- Full all-quest minute-detail parity remains open. The plugin has
  machine-readable blockers for every quest, but 319 rows are still generated
  broad rows rather than exact source-backed stage chains.
- Shield of Arrav is the next obvious F2P source-backed replacement, but it
  needs route-bundle and partner-exchange semantics before implementation.
- Combat remains globally fail-closed by default. Resolver-ready coverage is
  175/283 combat rows; no-stats combat rows remain blocked.
- Exact generated per-stage extraction, branch/route state, follower/puzzle
  state, and full combat simulation remain out of scope for this slice.

## Verification

- `python3 -m unittest tests.test_logic tests.test_runtime_actions tests.test_integration_smoke tests.test_skill_and_item_registry`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget`

## Manual Anki Test Instructions

1. Start Anki with this add-on installed and open the AnkiScape main menu.
2. Set Quest training to Goblin Diplomacy with the quest started at stage 1 and
   no goblin mail in inventory. Confirm the Quests tab shows
   `Blocked: Needs Orange goblin mail x1` and the Quest review button is
   disabled.
3. Add Orange goblin mail, Blue goblin mail, and Goblin mail to inventory, then
   answer Quest review cards. Confirm each mail is consumed at its own stage and
   completion grants 5 quest points, one Gold bar, and 200 Crafting XP.
4. Set Ernest the Chicken to stage 3 with no Fish food or Poison. Confirm the
   Quests tab shows `Blocked: Needs Fish food x1, Needs Poison x1`.
5. Add Fish food, Poison, and Spade, then progress Ernest through the machine
   part stages. Confirm Poisoned fish food, Pressure gauge, Grimy key, Rubber
   tube, and Oil can are produced/consumed in order, and completion grants
   3,000 Coins, 10 Eggs, and 300 Feathers.
6. Set Black Knights' Fortress to 11 quest points and confirm it is locked on
   `12 quest points`. Raise quest points to 12, start it, equip Iron chainbody
   and Bronze med helm, and confirm the disguise stage can progress from worn
   equipment. Add Cabbage at stage 3 and confirm it is consumed before the Sir
   Amik completion step.
