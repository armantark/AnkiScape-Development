# Combat Guard Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/guard_level_21.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/DropTableFactory.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Seeds.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Implemented Scope

- Added three enabled ordinary Combat rows from the complete melee source variants:
  - `guard_varrock`: `Npcs.GUARD_5919`, `Npcs.GUARD_5920`.
  - `guard_sword`: Falador sword guards `Npcs.GUARD`, `Npcs.GUARD_3228`, plus Edgeville guards `Npcs.GUARD_296`, `Npcs.GUARD_297`, `Npcs.GUARD_298`, `Npcs.GUARD_299`, `Npcs.GUARD_3407`, and `Npcs.GUARD_3408`.
  - `guard_battleaxe`: `Npcs.GUARD_3230`, `Npcs.GUARD_3241`.
- Preserved source combat stats, attack speed `4`, respawn delay `50`, lifepoints `220`, and each variant's attack/defence bonuses.
- Shared the source Guard drop table across the three enabled variants: guaranteed Bones; main table with bolts/arrows/runes/Coins/Iron dagger/talismans/Grain/Iron ore/allotment seeds; medium clue tertiary table; and charms.
- Added `Clue scroll (medium)` as a Combat extra item with a fetched `combatitems/clue_scroll_medium.png` icon and provenance.

## Deferred Or Blocked

- `faladorCrossbowId` (`Npcs.GUARD_3229`) is not enabled. The source file includes the NPC in the registered drop IDs but comments out its combat definition with `no definition yet, first npc ranged should be supported`. Enabling it as a melee or guessed ranged row would violate the complete-enabled-data rule.
- `Grain`, `Body talisman`, `Law talisman`, `Blood rune`, `Iron bolts`, and arrow drops reuse their existing Cooking/Runecrafting/Fletching item registry entries rather than creating duplicate Combat-owned definitions.

## Drop Table Note

The source Guard main table declares `total(128)` but its listed slots add to `146`. `DropTableFactory.TableBuilder.build()` only logs a mismatch, and runtime rolls with `entries.last().index`, so AnkiScape stores the active roll range as `146` for this row while preserving the source slot order.

## Verification

- Focused tests added:
  - `CombatLogicTest.test_guard_import_rows_match_source_split_variants_and_shared_drops`
  - `CombatLogicTest.test_guard_drop_rolls_quantity_range_medium_clue_and_charms`
  - `CombatLogicTest.test_guard_drop_rolls_nested_allotment_seed_table`
- Manual QA after this slice: open the Combat hub, confirm the Humanoids group includes the three Guard rows, select each enabled row, and verify no crossbow/ranged Guard row appears.
