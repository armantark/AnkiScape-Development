# Combat Thug Audit - 2026-06-23

Status: implemented ordinary Combat target expansion for the local 2011Scape
level-10 Thug row.

## Implemented Scope

- Added `thug` as a selectable Humanoids target using local 2011Scape level-10
  data: attack speed 4, respawn delay 50, 180 lifepoints, Attack 7, Strength 5,
  Defence 9, stab/crush attack bonuses 5/5, and stab/slash/crush defence
  bonuses 2/3/3.
- Imported all seven source IDs (`THUG_7106`, `THUG_7107`, `THUG_7109`,
  `THUG_7110`, `THUG_7112`, `THUG_7113`, and `THUG_7114`) into the target
  source note because they share one stat block and one drop table.
- Imported the Thug's guaranteed Bones, 128-slot main table, nested
  `minorHerbTable` slot, 1000-slot charm table, and 128-slot easy clue tertiary
  table.
- Reused existing registry coverage for the Thug drops: smithed Iron equipment,
  Steel hatchet, Runecrafting runes, Mining ores/bars, Coins, grimy herbs,
  charms, Bones, and easy clues.

## Source Anchors

- Thug:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/thug_level_10.plugin.kts`
- Minor herb table:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- Item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Deferred

- Human death sounds/animations, spawn maps, and location/access routing remain
  out of scope for the current flat target table.
- Thieving or crime-related gameplay is not inferred from the enemy name; this
  checkpoint only imports ordinary Combat behavior from the NPC definition.
- Broader humanoid rows such as Thief, Guard, and White Knight remain future
  source-backed enemy expansion slices.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_thug_import_row_matches_source_minor_herbs_and_charms tests.test_combat_logic.CombatLogicTest.test_thug_drop_rolls_main_charms_and_tertiary_tables tests.test_combat_logic.CombatLogicTest.test_humanoid_drop_tables_reach_nested_minor_herbs`
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
