# Combat Farmer Audit - 2026-06-23

Status: implemented ordinary Combat target expansion for the local 2011Scape
level-7 Farmer row and its shared allotment seed drop table.

## Implemented Scope

- Added `COMBAT_ALLOTMENT_SEED_DROP_TABLE` from local 2011Scape
  `Seeds.allotmentSeedTable`: 90 total slots across Potato, Onion, Cabbage,
  Tomato, Sweetcorn, Strawberry, and Watermelon seeds.
- Added `farmer` as a selectable Humanoids target using local 2011Scape level-7
  data: attack speed 6, respawn delay 25, 120 lifepoints, Attack 3, Strength 4,
  Defence 8, stab/crush attack bonuses 5/6, and no defensive bonuses.
- Imported the Farmer's guaranteed Bones, 128-slot main table, nested
  `minorHerbTable` slot, nested `allotmentSeedTable` slot, farming tool drops,
  and 128-slot easy clue tertiary table.
- Registered Farmer-specific seed and farming-tool drops as inventory-visible
  Combat items. Seeds and Gardening boots remain material items for now because
  Farming and equipment metadata for those boots are not playable surfaces yet;
  Rake, Seed dibber, Secateurs, and Watering can (8) are registered as tools.

## Source Anchors

- Farmer:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/farmer_level_7.plugin.kts`
- Allotment seed table:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Seeds.kt`
- Minor herb table:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- Item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Deferred

- Farming gameplay remains deferred; the allotment seeds are inventory-visible
  drops only.
- `Seeds.uncommonSeedTable` and other global seed tables are not imported until a
  source-backed enemy or activity needs them.
- Gardening boots are not wearable equipment yet because no local equipment
  metadata has been imported for them.

## Verification

- `python3 -m py_compile combat_data.py target_metadata.py tests/test_combat_logic.py tests/test_skill_and_item_registry.py tests/test_target_metadata.py tests/test_main_menu_widget.py`
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_is_selectable_and_shows_simple_enemy_targets`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
