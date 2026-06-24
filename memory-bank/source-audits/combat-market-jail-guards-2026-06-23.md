# Combat Market And Jail Guards Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/market_guard_level_20.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/jail_guard_level_26.plugin.kts`

## Implemented Scope

- Added `market_guard` as a selectable Humanoids Combat target using the local
  2011Scape `Npcs.MARKET_GUARD_2236` row: combat level 20, attack speed 5,
  respawn delay 50, 220 lifepoints, Attack 17, Strength 18, Defence 13, Magic
  1, Ranged 1, and the source attack/defence bonuses.
- Added `jail_guard` as a selectable Humanoids Combat target using the local
  2011Scape Jail guard ID set: `Npcs.JAIL_GUARD`, `Npcs.JAIL_GUARD_448`,
  `Npcs.JAIL_GUARD_449`, and `Npcs.JAIL_GUARD_917`. The row preserves combat
  level 26, attack speed 5, respawn delay 30, aggro radius 4 in the source note,
  320 lifepoints, Attack 19, Strength 23, Defence 21, Magic 1, Ranged 1, and
  the source attack/defence bonuses.
- Preserved the source guaranteed Bones-only death drops for both rows.
- Reused the existing Bones item/icon coverage, so this slice required no new
  item asset fetch.

## Deferred Or Blocked

- `Jailer` is deferred because its source row drops a `Jail key`; adding that
  target safely needs the key item, route/use semantics, and quest-stage
  implications to be audited together.
- Weaponsmaster and Temple-guardian style rows remain out of ordinary Combat
  expansion until their route or quest semantics are deliberately modeled.
- Aggro radius is recorded in the source note only. Current Combat still
  resolves one selected enemy at a time.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_market_and_jail_guard_rows_match_source tests.test_combat_logic.CombatLogicTest.test_low_level_humanoid_drop_rolls tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets`
- `git diff --check`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
