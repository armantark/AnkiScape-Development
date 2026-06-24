# Combat Citizen Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/citizen_level_2.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Implemented Scope

- Added one enabled ordinary Combat row, `citizen`, displayed as `Man/Woman`, for the source's shared level-2 Man/Woman ID set.
- Preserved source attack speed `4`, respawn delay `25`, lifepoints `70`, attack/strength/defence/magic/ranged stats, and defence penalties.
- Preserved the source drop table: guaranteed Bones; 1024-slot main table; Bronze med helm; Bronze dagger; Bronze bolts x2-12; Sling; Bronze arrows; runes; nested `Herbs.minorHerbTable`; Coins; Fishing bait; Copper ore; Earth talisman; Cabbage; and 1024-slot easy clue tertiary.
- Reused existing item and asset coverage for all drops. Bronze dagger and Bronze med helm are already Smithing/equipment items; runes/talismans, ores, food/materials, Sling, and easy clue already resolve through existing registries.

## Deferred Or Blocked

- No source-specific access lock or special combat mechanic was found in the local Citizen file, so no extra gate was added.
- Citizen remains one shared row because all source Man/Woman IDs in this file share identical stats and drops.

## Verification

- Focused tests added:
  - `CombatLogicTest.test_citizen_row_matches_source_and_nested_minor_herbs`
  - `CombatLogicTest.test_citizen_quantity_range_and_tertiary_drop_rolls`
  - `CombatLogicTest.test_citizen_drop_rolls_nested_minor_herb_table`
- Manual QA after this slice: open the Combat hub, confirm the Humanoids group includes `Man/Woman`, select the row, and verify the tooltip shows Bones plus the Citizen drop table without introducing new iconless items.
