# Combat Skeletons Source Audit - 2026-06-23

## Source

- Local source files:
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_lvl_21.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_lvl_22.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_lvl_25.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_level_45.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_lvl_60.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_lvl_68.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_lvl_85.plugin.kts`
- Source IDs: `Npcs.SKELETON_91`, `Npcs.SKELETON`, `Npcs.SKELETON_5332`, `Npcs.SKELETON_5333`, `Npcs.SKELETON_5334`, `Npcs.SKELETON_92`, `Npcs.SKELETON_93`, `Npcs.SKELETON_4385`, `Npcs.SKELETON_5365`, `Npcs.SKELETON_5366`, `Npcs.SKELETON_4384`, `Npcs.SKELETON_4386`, `Npcs.SKELETON_5367`, and `Npcs.SKELETON_5368`.
- Drop callbacks: all seven files register a drop table and call `table.getDrop(...)` from `on_npc_death`.
- Low Skeleton table: levels 21 and 22 use guaranteed Bones, a 1024-slot main table with arrows, runes, nested `Herbs.minorHerbTable`, Coins, empty slots, Iron dagger, Fire talisman, Iron ore, Grain, nested `Gems.gemTable`, and the 1000-slot Skeleton charm table.
- High Skeleton table: levels 25, 45, 60, 68, and 85 use guaranteed Bones, a 128-slot main table with iron equipment, runes, nested `Herbs.minorHerbTable`, Coins, empty slots, Bronze bar, nested `Gems.gemTable`, and the same 1000-slot charm table.
- Combat definitions: attack speed 4, source respawn delays, Skeleton Slayer assignment level 1, and source hitpoints/stat/bonus data per variant.

## Implemented

- Added source path constants for seven ordinary melee Skeleton files.
- Added `SKELETON_LOW_DROPS` and `SKELETON_HIGH_DROPS`.
- Added enabled Undead rows for Skeleton levels 21, 22, 25, 45, 60, 68, and 85.
- Preserved source Slayer XP values: 24.0, 29.0, 17.0, 59.0, 70.0, 65.0, and 65.0.

## Deferred

- `skeleton_warlock_lvl_11.plugin.kts` remains deferred. It is a `StyleType.MAGIC` enemy with spell `996`, so it belongs in a magic-enemy behavior pass rather than this melee Skeleton table import.

## Backend Notes

- No runtime engine changes were required for the seven melee rows; existing nested table and multi-table drop rolling handles their drops.
- Tests cover row stats, shared low/high drop tables, nested minor herb and gem rolls, and target tooltip metadata.

## Frontend Notes

- No frontend component change is required. The existing Combat target selector exposes the new Skeleton rows, drop summaries, and source files through `combat_target_rows(...)`.

## Assets

- No new assets were required. Drops resolve through existing item registries for Combat extras, Smithing/equipment, Fletching, Runecrafting, Mining, and herbs/gems.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py`
- `git diff --check`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_skeleton_rows_match_source_and_share_two_drop_tables tests.test_combat_logic.CombatLogicTest.test_skeleton_drop_rolls_nested_herb_and_gem_tables tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets` - 3 tests OK.
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata` - 129 tests OK.
- `python3 run_tests.py` - 680 tests OK, 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` - 680 tests OK.
