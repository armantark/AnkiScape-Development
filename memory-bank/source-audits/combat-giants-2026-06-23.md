# Combat Giants Source Audit - 2026-06-23

## Source

- Local source files:
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/hill_giant_lvl_28.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/moss_giant_level_42.plugin.kts`
  - `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/ice_giant_level_53.plugin.kts`
- Source IDs:
  - Hill giant: `Npcs.HILL_GIANT`.
  - Moss giant: `Npcs.MOSS_GIANT`, `Npcs.MOSS_GIANT_1587`, `Npcs.MOSS_GIANT_1588`, `Npcs.MOSS_GIANT_4688`.
  - Ice giant: `Npcs.ICE_GIANT`, `Npcs.ICE_GIANT_3072`, `Npcs.ICE_GIANT_4685`, `Npcs.ICE_GIANT_4686`, `Npcs.ICE_GIANT_4687`.
- Drop callbacks: all three files register a drop table and call `table.getDrop(...)` from `on_npc_death`.
- Combat definitions:
  - Hill giant: attack speed 6, respawn 30, attack style CRUSH, hitpoints 350, Attack 18, Strength 22, Defence 26, attackStab 18, attackCrush 16, Hill Giant Slayer XP 35.0.
  - Moss giant: attack speed 6, respawn 30, attack style CRUSH, hitpoints 600, Attack/Strength/Defence 30, attackStab 33, attackCrush 31, Moss Giant Slayer XP 60.0.
  - Ice giant: attack speed 5, respawn 30, attack style SLASH, hitpoints 700, Attack/Strength/Defence 40, generic `attackBonus = 29`, `strengthBonus = 31`, defenceSlash 3, defenceCrush 2, Ice Giant Slayer XP 70.0.
- Drop tables:
  - Hill giant uses guaranteed Big bones, a 128-slot main table with equipment, runes/arrows, nested `Herbs.minorHerbTable`, nested `Seeds.allotmentSeedTable`, coins, Limpwurt root, Beer, Body talisman, nested `Gems.gemTable`, and a 1000-slot charm table.
  - Moss giant uses guaranteed Big bones, a 128-slot main table with equipment, runes/arrows, coins, Steel bar, Coal, Spinach roll, nested `Herbs.minorHerbTable`, nested `Seeds.uncommonSeedTable`, nested `Gems.gemTable`, and a 1000-slot charm table.
  - Ice giant uses guaranteed Big bones, a declared 1024-slot main table with equipment, runes/arrows, nested `Seeds.allotmentSeedTable`, coins, Jug of wine, Mithril ore, Banana, nested `Gems.gemTable`, and a 100000-slot tertiary table for Long bone, Curved bone, and `Champion's scroll`.

## Implemented

- Added source path constants for the three giant files.
- Added `COMBAT_UNCOMMON_SEED_DROP_TABLE` from `Seeds.uncommonSeedTable`.
- Added `HILL_GIANT_DROPS`, `MOSS_GIANT_DROPS`, and `ICE_GIANT_DROPS`.
- Added enabled Combat targets `hill_giant`, `moss_giant`, and `ice_giant`.
- Preserved the Ice giant source anomaly where `total(1024)` has slots that sum to 1026. The runtime roll keeps the declared total, so the final two gem-table slots are unreachable as in the source-shaped table.
- Translated Ice giant's generic `attackBonus = 29` into all three melee attack bonus fields, matching existing row treatment for source generic attack bonuses.
- Registered new Combat item data for Big bones, Black sq shield, Black kiteshield, Magic staff, Mithril spear, Banana, Jug of wine, Spinach roll, Long bone, Curved bone, `Champion's scroll`, Limpwurt root, and the uncommon seed table outputs.

## Deferred

- Ring of Wealth boosted gem/mega-rare branches remain deferred globally; these rows use the existing no-Ring-of-Wealth gem table.
- Source-exact champion scroll race variants remain deferred. Ice giant stores the source item as `Champion's scroll`; the icon uses the Giant Champion scroll sprite because the drop is from the giant family.

## Backend Notes

- No combat-engine change was required. Existing guaranteed, multi-table, nested-table, quantity, and declared-total drop semantics cover these rows.
- Existing dangerous-target confirmation applies through the current risk preview path for higher-level giants.

## Frontend Notes

- No component change was required. Existing Combat target metadata exposes the Giants group, drop summaries, and source file references in the target selector.

## Assets

- Fetched Combat sprites with per-file provenance for:
  - `combatitems/big_bones.png`
  - `combatitems/black_sq_shield.png`
  - `combatitems/black_kiteshield.png`
  - `combatitems/magic_staff.png`
  - `combatitems/mithril_spear.png`
  - `combatitems/banana.png`
  - `combatitems/jug_of_wine.png`
  - `combatitems/spinach_roll.png`
  - `combatitems/long_bone.png`
  - `combatitems/curved_bone.png`
  - `combatitems/champion_s_scroll.png`

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_target_metadata.py tests/test_skill_and_item_registry.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_giant_rows_match_source_and_drop_tables tests.test_combat_logic.CombatLogicTest.test_giant_drop_rolls_use_nested_source_tables tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons` - 4 tests OK.
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata tests.test_skill_and_item_registry` - 158 tests OK.
- `git diff --check`
- `python3 run_tests.py` - 682 tests OK, 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` - 682 tests OK.
