# Combat Barbarian Level 17 Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_greataxe_lvl_17.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_spear_lvl_17.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_twohand_sword_lvl_17.plugin.kts`

## Implemented Scope

- Added `barbarian_level_17` as a selectable Humanoids Combat target grouping
  the complete level-17 source weapon variants:
  - Greataxe IDs `Npcs.BARBARIAN` and `Npcs.BARBARIAN_3248`.
  - Spear ID `Npcs.BARBARIAN_3260`.
  - Two-handed sword ID `Npcs.BARBARIAN_3249`.
- Preserved source combat level 17, attack speed 4, respawn delay 50, 240
  lifepoints, Attack 15, Strength 14, Defence 10, Magic 1, Ranged 1, and the
  shared source attack/defence bonuses.
- Imported the shared Barbarian drop table shape already used by the level 8/9
  and level 10 Barbarian rows: guaranteed Bones, the 1024-slot main table,
  1000-slot charm table, and 128-slot easy clue tertiary table.
- Reused existing item/icon coverage for the shared Barbarian drops, so this
  slice required no new asset fetch.

## Deferred Or Blocked

- Weapon animations are recorded only through source-file provenance. Current
  AnkiScape Combat resolves the selected enemy's melee attack stats rather than
  rendering per-NPC weapon animations.
- Broader Barbarian and Barbarian Assault/minigame context rows remain separate
  future audits; this slice covers only the three ordinary level-17 source rows
  listed above.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_barbarian_level_17_import_row_groups_weapon_source_variants tests.test_combat_logic.CombatLogicTest.test_barbarian_level_17_drop_rolls_include_source_charms tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets`
- `git diff --check`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
