# Combat Dwarf Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/dwarf_level_10_11.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Gems.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/MegaRare.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Implemented Scope

- Added two enabled ordinary Combat rows from the complete local source variants:
  - `dwarf_level_10`: `Npcs.DWARF_118`, `Npcs.DWARF_3221`, `Npcs.DWARF_3272`.
  - `dwarf_level_11`: `Npcs.DWARF_3219`, `Npcs.DWARF_3220`, `Npcs.DWARF_3268`, `Npcs.DWARF_3269`, `Npcs.DWARF_3270`.
- Preserved source combat stats, attack speeds, respawn delay `50`, Slayer XP `16.0`, and the source attack/defence bonuses.
- Shared the source Dwarf drop table across both rows: guaranteed Bones; 128-slot main table; Bronze bolts x2-12; ores, bars, Hammer, Bronze pickaxe, Bronze/Iron battleaxes; 1000-slot charms; and 128-slot easy clue tertiary.
- Added first-class Combat references for the global no-Ring-of-Wealth `Gems.gemTable` and nested `MegaRare.megaRareTable` rather than flattening those drops.
- Added Combat-owned icon/provenance coverage for the rare-table outputs not already owned by another skill manifest: Rune javelin, Loop half of a key, Tooth half of a key, Rune spear, Shield left half, and Dragon spear.

## Deferred Or Blocked

- Ring of Wealth boosted gem and mega-rare slots are not active yet. The source tables branch on worn Ring of Wealth, while the current Combat drop roller has no equipment-conditioned drop modifiers. AnkiScape stores the default no-Ring-of-Wealth slot weights now and should add the boosted branch only when the Combat drop engine can evaluate equipment-specific table variants.
- Common Dwarf drops such as Bronze pickaxe, Bronze med helm, Bronze battleaxe, Iron battleaxe, Bronze bolts, ores, bars, Chaos talisman, Nature talisman, and uncut gems reuse existing Mining, Smithing, Fletching, Runecrafting, and gem item registry entries.

## Verification

- Focused tests added:
  - `CombatLogicTest.test_dwarf_import_rows_match_source_and_nested_global_gem_tables`
  - `CombatLogicTest.test_dwarf_drop_rolls_quantity_range_charms_and_tertiary_tables`
  - `CombatLogicTest.test_dwarf_drop_rolls_nested_gem_table`
  - `CombatLogicTest.test_dwarf_drop_rolls_nested_mega_rare_table`
- Manual QA after this slice: open the Combat hub, confirm the Humanoids group includes `Dwarf (level 10)` and `Dwarf (level 11)`, select each row, and verify the tooltip shows Dwarf drops including the nested gem-table outputs without any special Ring of Wealth claim.
