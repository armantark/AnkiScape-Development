# Combat Wolves Source Audit - 2026-06-23

## Source

- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/wolf_lvl_11.plugin.kts`
- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/white_wolf_lvl_25.plugin.kts`
- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/white_wolf_lvl_38.plugin.kts`
- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/big_wolf_lvl_73.plugin.kts`
- Source IDs: `Npcs.WOLF_4414`, `Npcs.WOLF_11263`, `Npcs.WHITE_WOLF`, `Npcs.WOLF_4413`, `Npcs.WOLF_6047`, `Npcs.WHITE_WOLF_97`, and `Npcs.BIG_WOLF_6046`.
- Drop callbacks: each file registers a `DropTableFactory` table and calls `getDrop(...)` in `on_npc_death`.
- Combat definitions: all four rows use attack speed 4, respawn 90, aggro radius 4, and Slayer assignment `WOLF` level 1. Source Slayer XP is 10.0, 34.0, 44.0, and 74.0.

## Implemented

- Added `COMBAT_ENEMY_DATA["wolf"]` as the level-11 Animals target with 100 LP, 10 Attack, 10 Strength, and 10 Defence.
- Added `COMBAT_ENEMY_DATA["white_wolf_level_25"]` with 340 LP, 20 Attack, 16 Strength, and 22 Defence.
- Added `COMBAT_ENEMY_DATA["white_wolf_level_38"]` with 440 LP, 30 Attack, 31 Strength, and 32 Defence.
- Added `COMBAT_ENEMY_DATA["big_wolf"]` with 740 LP, 60 Attack, 61 Strength, and 62 Defence.
- Added the level-11 Wolf drop table: guaranteed Wolf bones and Bones, then a 1000-slot table with Gold charm 20, Green charm 30, Crimson charm 50, Blue charm 10, and 890 empty slots.
- Added the shared White wolf/Big wolf drop table: guaranteed Wolf bones, then a 1000-slot table with Gold charm 110, Green charm 50, Crimson charm 140, Blue charm 80, and 620 empty slots.
- Added `Wolf bones` to the Combat item registry and fetched `combatitems/wolf_bones.png` with provenance.

## Deferred

- Aggro radius and the level-11 source `StyleType.STAB` attack style are recorded in source strings but do not change current review gameplay.

## Backend Notes

- No runtime engine changes were required; the rows use existing guaranteed drop and weighted table behavior.
- Tests cover source stats, Slayer XP, guaranteed drops, charm weights, drop rolls, target tooltip metadata, and the `Wolf bones` asset path.

## Frontend Notes

- No frontend component change is required. The existing Combat target selector exposes the wolf rows, drops, source files, and Wolf bones icon through existing row metadata and item registry plumbing.

## Assets

- Fetched `combatitems/wolf_bones.png` from the RuneScape wiki fetcher with provenance at `combatitems/wolf_bones.provenance.json`.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py tests/test_skill_and_item_registry.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_wolf_rows_match_source_and_charm_tables tests.test_combat_logic.CombatLogicTest.test_wolf_drop_rolls_use_source_charm_tables tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata tests.test_skill_and_item_registry`
- `git diff --check`
- `python3 run_tests.py` - 672 tests OK, 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` - 672 tests OK.
