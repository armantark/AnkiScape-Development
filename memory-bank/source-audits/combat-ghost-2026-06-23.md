# Combat Ghost Source Audit - 2026-06-23

## Source

- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/undeads/ghost_level_19.plugin.kts`
- Source IDs: `Npcs.GHOST`, `Npcs.GHOST_104`, `Npcs.GHOST_5349`, `Npcs.GHOST_5350`, `Npcs.GHOST_5351`, and `Npcs.GHOST_5352`.
- Drop callback: none. The file defines `on_npc_pre_death(*ghosts)` for sound only and does not define an `on_npc_death` drop callback.
- Combat definition: attack speed 4, respawn 40, hitpoints 250, Attack 13, Strength 13, Defence 18, defence bonuses 5/5/5/-5/5, and Slayer assignment `GHOST` level 1 with 25.0 XP.

## Implemented

- Added `COMBAT_ENEMY_DATA["ghost"]` as an Undead melee target at combat level 19.
- Added source defence bonuses for stab, slash, crush, magic, and ranged defence.
- Added empty drops because the source file has no death drop callback.

## Deferred

- The source `StyleType.CRUSH` attack style is recorded in the row source string but does not change current review gameplay.

## Backend Notes

- No runtime engine changes were required; the row uses the existing no-drop behavior.
- Tests cover source stats, Slayer XP, defence bonuses, explicit no-drop behavior, drop rolls, and target tooltip metadata.

## Frontend Notes

- No frontend component change is required. The existing Combat target selector exposes `Ghost`, the no-drop summary, and the source file through `combat_target_rows(...)`.

## Assets

- No item assets were required because the source row has no drops.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_ghost_row_matches_source_and_has_no_death_drops tests.test_combat_logic.CombatLogicTest.test_ghost_drop_rolls_no_items tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata` - 125 tests OK.
- `git diff --check`
- `python3 run_tests.py` - 676 tests OK, 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` - 676 tests OK.
