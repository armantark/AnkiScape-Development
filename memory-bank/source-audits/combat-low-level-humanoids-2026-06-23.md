# Combat Low-Level Humanoids Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/monk_level_5.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/cuffs_level_3.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/narf_jeff_rusty_level_2.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/johnny_the_beard_level_2.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Implemented Scope

- Added `monk` as the source level-5 Monk row for `Npcs.MONK_7727`.
- Preserved Monk attack speed `4`, respawn delay `25`, lifepoints `150`, combat stats, and Bones-only drop table.
- Added `cuffs` as the source level-3 Cuffs row for `Npcs.CUFFS`.
- Preserved Cuffs attack speed `4`, respawn delay `25`, lifepoints `70`, attack/strength/defence/magic/ranged stats, defensive bonuses, guaranteed Bones, 1024-slot main table, nested `Herbs.minorHerbTable`, and easy clue tertiary.
- Added `narf_jeff_rusty` as one shared source level-2 row for `Npcs.NARF`, `Npcs.JEFF`, and `Npcs.RUSTY`.
- Preserved the shared Narf/Jeff/Rusty attack speed `4`, respawn delay `25`, lifepoints `70`, combat stats, defensive bonuses, guaranteed Bones, 1024-slot main table, nested `Herbs.minorHerbTable`, and easy clue tertiary.
- Reused the existing low-level human drop table object because Cuffs and Narf/Jeff/Rusty match Citizen's imported source drop table.
- Reused existing item and asset coverage for all Cuffs and Narf/Jeff/Rusty drops.

## Deferred Or Blocked

- `johnny_the_beard` remains deferred. The local source file declares hitpoints and drops, but omits attack/strength/defence/magic/ranged stats; importing it safely needs an audit of `set_combat_def` default-stat semantics rather than assuming the missing fields.
- No source-specific access lock or special combat mechanic was found for Monk, Cuffs, or Narf/Jeff/Rusty in the audited local files.

## Verification

- Focused tests added:
  - `CombatLogicTest.test_low_level_humanoid_rows_match_source`
  - `CombatLogicTest.test_low_level_humanoid_drop_rolls`
- Manual QA after this slice: open the Combat hub, confirm the Humanoids group includes `Monk`, `Cuffs`, and `Narf/Jeff/Rusty`, then verify Monk shows only Bones while Cuffs and Narf/Jeff/Rusty show the low-level human drop table without new iconless items.
