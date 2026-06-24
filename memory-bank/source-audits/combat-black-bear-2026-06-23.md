# Combat Black Bear Source Audit - 2026-06-23

## Source

- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/black_bear_level_19.plugin.kts`
- Source ID: `Npcs.BLACK_BEAR`
- Drop callback: `on_npc_death(*ids)` calls `DropTableFactory.getDrop(...)`.
- Combat definition: attack speed 4, respawn 50, hitpoints 250, Attack 15, Strength 16, Defence 13, aggro radius 4, and Slayer assignment `BEAR` level 1 with 25.0 XP.

## Implemented

- Added `COMBAT_ENEMY_DATA["black_bear"]` as an Animals melee target at combat level 19.
- Added guaranteed drops: Bones, Bear fur, and Raw bear meat.
- Added the source 1000-slot charm table: Gold charm 180, Green charm 8, Crimson charm 11, Blue charm 5, and 796 empty slots.
- Reused existing item registry/icon coverage for Bones, Bear fur, Raw bear meat, and charms.

## Deferred

- Aggro radius is recorded in the row source string but does not change review gameplay yet.

## Backend Notes

- No runtime engine changes were required; the row uses existing guaranteed drop and charm-table behavior.
- Tests cover source stats, Slayer XP, guaranteed drops, charm weights, drop rolls, and target tooltip metadata.

## Frontend Notes

- No frontend component change is required. The existing Combat target selector exposes `Black bear`, guaranteed drops, charm chances, and the source file through `combat_target_rows(...)`.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_giant_rat_and_unicorn_variants_match_source tests.test_combat_logic.CombatLogicTest.test_giant_rat_and_unicorn_drop_rolls tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata`
- `git diff --check`
- `python3 run_tests.py` - 670 tests OK, 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` - 670 tests OK.
