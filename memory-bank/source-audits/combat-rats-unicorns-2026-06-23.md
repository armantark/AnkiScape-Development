# Combat Rats And Unicorns Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/giant_rat_level_6.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/giant_rat_level_26.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/unicorn_level_15.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/black_unicorn_level_27.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`
- `combatitems/unicorn_horn.provenance.json`

## Implemented Scope

- Added `giant_rat_level_6` for `Npcs.GIANT_RAT_2091`.
- Preserved level-6 Giant rat attack speed `4`, respawn delay `30`, lifepoints `100`, attack/strength/defence stats, and guaranteed Bones/Raw rat meat drops.
- Added `giant_rat_level_26` for `Npcs.GIANT_RAT_4944` and `Npcs.GIANT_RAT_4945`.
- Preserved level-26 Giant rat attack speed `4`, respawn delay `30`, lifepoints `250`, attack/strength/defence stats, and guaranteed Bones/Raw rat meat drops.
- Added `unicorn` for `Npcs.UNICORN`.
- Preserved Unicorn attack speed `4`, respawn delay `90`, lifepoints `190`, attack/strength/defence stats, guaranteed Bones/Unicorn horn, and the 1000-slot charm table.
- Added `black_unicorn` for `Npcs.BLACK_UNICORN`.
- Preserved Black unicorn attack speed `4`, respawn delay `90`, lifepoints `290`, attack/strength/defence stats, guaranteed Bones/Unicorn horn, and the shared 1000-slot charm table.
- Registered `Unicorn horn` as a Combat material item and fetched `combatitems/unicorn_horn.png` with provenance.

## Deferred Or Blocked

- Duck remains deferred in this slice because the source file has different land/water drop behavior: only land ducks register a Bones drop table, while water ducks share combat stats but have no death drop callback. Importing that cleanly should split land and water variants.
- No source-specific access lock or special combat mechanic was found for the Giant rat or Unicorn rows in the audited local files.

## Verification

- Focused tests added:
  - `CombatLogicTest.test_giant_rat_and_unicorn_variants_match_source`
  - `CombatLogicTest.test_giant_rat_and_unicorn_drop_rolls`
- Extended registry and target metadata tests:
  - `TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
  - `TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets`
- Manual QA after this slice: open the Combat hub, confirm `Giant rat` level 6/26, `Unicorn`, and `Black unicorn` are selectable, and verify Unicorn rows show `Unicorn horn` plus charm-table tooltip rows with a resolved icon.
