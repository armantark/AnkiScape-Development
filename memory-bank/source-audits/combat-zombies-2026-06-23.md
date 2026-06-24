# Combat Zombies Source Audit - 2026-06-23

## Source

- Local source files:
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_13.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_18.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_24.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_25.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_30.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_44.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/zombie_lvl_53.plugin.kts`
- Source IDs: `Npcs.ZOMBIE`, `Npcs.ZOMBIE_74`, `Npcs.ZOMBIE_75`, `Npcs.ZOMBIE_76`, `Npcs.ZOMBIE_5375`, `Npcs.ZOMBIE_4392`, `Npcs.ZOMBIE_5376`, `Npcs.ZOMBIE_4393`, `Npcs.ZOMBIE_5377`, `Npcs.ZOMBIE_5378`, `Npcs.ZOMBIE_4394`, `Npcs.ZOMBIE_5379`, and `Npcs.ZOMBIE_5380`.
- Drop callbacks: all seven files register a drop table and call `table.getDrop(...)` from `on_npc_death`.
- Shared drop table: guaranteed Bones; 128-slot main table with Iron hatchet, Bronze longsword, Bronze med helm, Bronze kiteshield, arrows, runes, nested `Herbs.minorHerbTable`, Coins, empty slots, Fishing bait, and Copper ore; 1000-slot charm table.
- Source exception: level 25 uses Iron hatchet 5/128 and empty 6/128. The other six files use Iron hatchet 3/128 and empty 8/128.
- Combat definitions: attack speed 5, respawn 35, Zombie Slayer assignment level 1, and source hitpoints/stat/bonus data per variant.

## Implemented

- Added source path constants for all seven Zombie files.
- Added `ZOMBIE_DROPS` and `ZOMBIE_LEVEL_25_DROPS`.
- Added enabled Undead rows for Zombie levels 13, 18, 24, 25, 30, 44, and 53.
- Preserved source Slayer XP values: 22.0, 24.0, 30.0, 30.0, 30.0, 30.0, and 50.0.

## Deferred

- No Zombie-specific mechanics were deferred. The source death sound callback has no current gameplay effect and is not modeled.

## Backend Notes

- No runtime engine changes were required; existing nested table and multi-table drop rolling handles the Zombie drops.
- Tests cover row stats, shared/drop-variant table data, nested minor herb rolls, and the level-25 table difference.

## Frontend Notes

- No frontend component change is required. The existing Combat target selector exposes the new Zombie rows, drop summaries, and source files through `combat_target_rows(...)`.

## Assets

- No new assets were required. Drops resolve through existing item registries for Combat extras, Woodcutting, Smithing/equipment, Fletching, Runecrafting, Mining, Fishing, and herbs.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py`
- `git diff --check`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_zombie_rows_match_source_and_level_25_drop_variant tests.test_combat_logic.CombatLogicTest.test_zombie_drop_rolls_nested_minor_herbs_and_level_25_variant tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets` - 3 tests OK.
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata` - 127 tests OK.
- `python3 run_tests.py` - 678 tests OK, 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` - 678 tests OK.
