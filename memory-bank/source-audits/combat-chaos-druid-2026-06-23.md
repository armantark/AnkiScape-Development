# Combat Chaos Druid Source Audit - 2026-06-23

## Sources

- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/chaos_druid_lvl_13.plugin.kts`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Gems.kt`
- `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Implemented Scope

- Added `chaos_druid` as a selectable Humanoids Combat target for
  `Npcs.CHAOS_DRUID_2547`, `Npcs.CHAOS_DRUID`, and `Npcs.CHAOS_DRUID_7105`.
- Preserved source combat level 13, attack speed 4, respawn delay 25, aggressive
  radius 4 provenance, 200 lifepoints, Attack 8, Strength 8, Defence 12, and
  Magic 10. Ranged remains AnkiScape's existing default `1` for source rows
  that omit that stat.
- Imported guaranteed Bones and the exact 128-slot main table, including
  Mithril bolts x2-12, runes, Coins, Vial of water, Bronze longsword, Snape
  grass, the nested `Herbs.minorHerbTable`, and the no-Ring-of-Wealth
  `Gems.gemTable`.
- Registered `Vial of water` as a Combat material item and fetched
  `combatitems/vial_of_water.png` through `tools/fetch_assets.py`; provenance is
  recorded in `assets_provenance.json`.

## Deferred Or Blocked

- Chaos druids are aggressive in the source plugin, but AnkiScape ordinary
  Combat still starts only from explicit target selection. Aggression remains
  source provenance and future risk-preview context, not background attacks.
- Herblore use of Vial of water and Snape grass remains a future skill surface;
  Combat only needs those items to enter the Bank through source drops.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py tests/test_skill_and_item_registry.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_chaos_druid_row_matches_source_and_nested_tables tests.test_combat_logic.CombatLogicTest.test_chaos_druid_drop_rolls_quantity_range_and_nested_tables tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
