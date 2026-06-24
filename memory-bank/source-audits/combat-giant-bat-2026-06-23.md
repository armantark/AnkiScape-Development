# Combat Giant Bat Source Audit - 2026-06-23

## Source

- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/giant_bat_level_27.plugin.kts`
- Source ID: `Npcs.GIANT_BAT`
- Drop callback: the file registers a `DropTableFactory` table and calls `getDrop(...)` in `on_npc_death`.
- Combat definition: attack speed 4, respawn 35, hitpoints 320, Attack 22, Strength 22, Defence 22, defence bonuses 10/10/12/10/8, aggro radius 4, and Slayer assignment `BAT` level 1 with 32.0 XP.

## Implemented

- Added `COMBAT_ENEMY_DATA["giant_bat"]` as a Bats melee target at combat level 27.
- Added guaranteed Bat bones as the source drop table.
- Added source defence bonuses for stab, slash, crush, magic, and ranged defence.
- Added `Bat bones` to Combat item data and reused the existing quest Bat bones icon through `QUEST_ITEM_IMAGES` fallback.

## Deferred

- Aggro radius is recorded in the row source string but does not change review gameplay yet.

## Backend Notes

- No runtime engine changes were required; the row uses existing guaranteed drop behavior.
- Tests cover source stats, Slayer XP, defence bonuses, guaranteed drops, drop rolls, target tooltip metadata, and the reused Bat bones asset path.

## Frontend Notes

- No frontend component change is required. The existing Combat target selector exposes `Giant bat`, Bat bones, and the source file through `combat_target_rows(...)`.

## Assets

- Reused existing `questitems/bat_bones.png`; no new asset fetch was required.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py tests/test_skill_and_item_registry.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_giant_bat_row_matches_source tests.test_combat_logic.CombatLogicTest.test_giant_bat_drop_rolls_guaranteed_bat_bones tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata tests.test_skill_and_item_registry`
- `git diff --check`
- `python3 run_tests.py` - 674 tests OK, 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` - 674 tests OK.
