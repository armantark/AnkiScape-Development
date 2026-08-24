# Combat Thief Audit - 2026-06-23

Status: implemented ordinary Combat target expansion for the local 2011Scape
level-16 Thief row.

## Implemented Scope

- Added `thief` as a selectable Humanoids target using local 2011Scape level-16
  data: attack speed 4, respawn delay 25, 170 lifepoints, Attack 14, Strength
  13, and Defence 12.
- Imported all four source IDs (`THIEF_5926`, `THIEF_5927`, `THIEF_5928`, and
  `THIEF_5929`) into the target source note because they share one stat block
  and one drop table.
- Imported the Thief's guaranteed Bones, 128-slot main table, Bronze bolts
  x2-12 quantity range, nested `minorHerbTable` slot, and 128-slot easy clue
  tertiary table.
- Reused existing registry coverage for the Thief drops: Bronze and Iron
  equipment, Fletching ammunition, Runecrafting runes/talismans, Coins,
  Fishing bait, Copper ore, Cabbage, grimy herbs, Bones, and easy clues.

## Source Anchors

- Thief:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/thief_level_16.plugin.kts`
- Minor herb table:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- Item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Deferred

- Thieving gameplay remains deferred; this checkpoint only imports the ordinary
  enemy combat row.
- Human death sounds/animations, spawn maps, and location/access routing remain
  out of scope for the current flat target table.
- Broader humanoid rows such as Guard, White Knight, and Dark wizard remain
  future source-backed enemy expansion slices.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_thief_import_row_matches_source_and_nested_minor_herbs tests.test_combat_logic.CombatLogicTest.test_humanoid_quantity_range_drop_rolls tests.test_combat_logic.CombatLogicTest.test_humanoid_drop_tables_reach_nested_minor_herbs`
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
