# Combat Higher Goblins Audit - 2026-06-23

Status: implemented ordinary Combat target expansion for the local 2011Scape
Goblin level 5, 11, 13, 16, and 25 rows.

## Implemented Scope

- Added `goblin_level_5`, `goblin_level_11`, `goblin_level_13`,
  `goblin_level_16`, and `goblin_level_25` as selectable Goblins targets.
- Reused the existing nested drop-table primitive to import the shared source
  `minorHerbTable` slot instead of flattening the herb table.
- Added a shared higher-Goblin drop table matching the source rows: guaranteed
  Bones, 128-slot main table, 1024-slot Charms table, and 1024-slot easy clue
  tertiary table.
- Preserved the source main table shape where `total(128)` has 127 explicit
  slots, leaving one implicit no-drop slot beyond the declared
  `nothing(slots = 8)`.
- Registered Bronze javelin and Grapes as inventory-visible Combat material
  drops. Bronze scimitar and Nature rune reuse existing Smithing and
  Runecrafting item definitions/assets. Bronze javelin remains inventory-only
  until the broader thrown-weapon Ranged slice exists.
- Updated Combat drop tooltips to show explicit nested table slots such as
  `Minor herb table (2/128)` rather than omitting table-only rows.

## Source Anchors

- Goblin level 5:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/goblin/goblin_level_5.plugin.kts`
- Goblin level 11:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/goblin/goblin_level_11.plugin.kts`
- Goblin level 13:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/goblin/goblin_level_13.plugin.kts`
- Goblin level 16:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/goblin/goblin_level_16.plugin.kts`
- Goblin level 25:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/goblin/goblin_level_25.plugin.kts`
- Minor herb table:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- Item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Deferred

- Farmer remains deferred because it also needs `Seeds.allotmentSeedTable`.
- Cave slime remains deferred behind Slayer gates and shared gem-table drops.
- Bronze javelin is not usable equipment yet; thrown weapons belong to the
  broader Ranged equipment/ammunition backlog.

## Verification

- `python3 -m py_compile combat_data.py target_metadata.py tests/test_combat_logic.py tests/test_skill_and_item_registry.py tests/test_target_metadata.py tests/test_main_menu_widget.py`
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_is_selectable_and_shows_simple_enemy_targets`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
