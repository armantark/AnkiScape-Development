# Combat Black Knight Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/black_knight_level_33.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/DropTableFactory.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Seeds.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Gems.kt`

## Implemented Scope

- Added `black_knight` as a selectable Humanoids Combat target from
  `Npcs.BLACK_KNIGHT`.
- Preserved source combat level 33, attack speed 5, respawn delay 25, 420
  lifepoints, Attack 25, Strength 25, Defence 25, and source attack/defence
  bonuses. Magic and Ranged remain at AnkiScape's existing default `1` for
  source rows that omit those stats.
- Imported guaranteed Bones, the Black knight main table, the 1000-slot charm
  table, and nested references to the global minor herb, allotment seed, and
  no-Ring-of-Wealth gem tables.
- Reused existing item/equipment/icon coverage for all Black knight drops:
  weapons, armour, runes, arrows, bars/ore, Pot of flour, Bread, Coins, global
  herb/seed/gem items, and charms.

## Drop Table Note

The Black knight source main table declares `total(128)`, but its listed slots
add to `116`. `DropTableFactory` rolls with `entries.last().index`, so
AnkiScape stores the active main table total as `116` while recording the source
declared total mismatch in the row provenance.

## Deferred Or Blocked

- Black Knights' Fortress quest disguise/progress handling remains quest-stage
  data. This ordinary target is not a replacement for quest-specific stealth or
  route requirements.
- Location/rank/faction interactions are not modeled in ordinary Combat target
  selection yet.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_black_knight_row_matches_source_and_active_slot_total tests.test_combat_logic.CombatLogicTest.test_black_knight_drop_rolls_nested_seed_table_and_charms tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets`
- `git diff --check`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
