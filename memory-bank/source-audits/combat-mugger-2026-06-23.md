# Combat Mugger Audit - 2026-06-23

Status: implemented ordinary Combat target expansion for the local 2011Scape
level-6 Mugger row and another source-backed nested minor-herb drop consumer.

## Implemented Scope

- Added `mugger` as a selectable Humanoids target using local 2011Scape level-6
  data: attack speed 4, respawn delay 25, 80 lifepoints, Attack 5, Strength 5,
  Defence 5, and source `strengthBonus = -21`.
- Imported all three source IDs (`MUGGER`, `MUGGER_7161`, and `MUGGER_7162`)
  into the target source note because they share the same stats and drop table.
- Imported the Mugger's guaranteed Bones, 1024-slot main table, nested
  `minorHerbTable` slot, Bronze bolts x2-12 quantity range, rune/coin/rope/bait
  and ordinary item drops, and 128-slot easy clue tertiary table.
- Registered `Knife` as a Combat-visible material item from `Items.KNIFE` so
  the Mugger drop table does not rely only on older quest provenance. Existing
  item registry rows already covered Bronze bolts, runes, Coins, Rope, Fishing
  bait, Copper ore, Bronze med helm, Cabbage, Bones, and easy clues.

## Source Anchors

- Mugger:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/mugger_level_6.plugin.kts`
- Minor herb table:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- Item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Deferred

- Source aggro radius 4 is not modeled yet because ordinary Combat currently
  resolves one selected enemy at a time.
- Human death sounds/animations, spawn maps, and location/access routing remain
  out of scope for the current flat target table.
- Broader humanoid rows such as Thug and Guard are deferred to future
  source-backed enemy expansion slices.
- Knife has no dedicated Bank icon yet; this checkpoint only ensures it is a
  valid inventory item for the drop table.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_skill_and_item_registry.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_mugger_import_row_matches_source_and_nested_minor_herbs tests.test_combat_logic.CombatLogicTest.test_humanoid_quantity_range_drop_rolls tests.test_combat_logic.CombatLogicTest.test_humanoid_drop_tables_reach_nested_minor_herbs tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
