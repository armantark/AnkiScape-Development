# Combat Ducks Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/duck_level_1.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Implemented Scope

- Added `duck_land` for the source land-duck IDs `Npcs.DUCK_6113` and `Npcs.DRAKE`.
- Preserved land-duck attack speed `4`, respawn delay `25`, lifepoints `30`, combat stats, defensive penalties, Bird Slayer XP `3.0`, and guaranteed Bones drop table.
- Added `duck_water` for the source water-duck IDs `Npcs.DUCK` and `Npcs.DUCK_2693`.
- Preserved water-duck attack speed `4`, respawn delay `25`, lifepoints `30`, combat stats, defensive penalties, and Bird Slayer XP `3.0`.
- Kept water-duck drops empty because the local source only registers a death drop callback for `landDucks`.

## Deferred Or Blocked

- No source-specific access lock or special combat mechanic was found in the local Duck file.
- Duck variants remain separate rows so future source corrections can change land or water drop behavior independently.

## Verification

- Focused tests added:
  - `CombatLogicTest.test_duck_rows_split_land_and_water_source_drops`
  - `CombatLogicTest.test_duck_drop_rolls_follow_land_water_source_split`
- Extended target metadata coverage:
  - `TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets`
- Manual QA after this slice: open the Combat hub, confirm `Duck (land)` and `Duck (water)` are separate Birds rows, verify land ducks show Bones, and verify water ducks show the no-drop source note instead of a Bones drop.
