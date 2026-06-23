# Combat Highwayman Audit - 2026-06-23

Status: implemented Highwayman ordinary-enemy slice.

## Scope

- Adds source-backed Highwayman as the first enabled humanoid Combat target.
- Reuses the existing inclusive `quantity_range` drop slot support for Iron
  bolts x2-12.
- Registers Cape as a Combat drop item with a fetched icon and source-backed
  cape-slot equipment metadata from local 2011Scape `items.yml`.
- Keeps broader humanoid candidates deferred when they need nested/shared tables,
  variant splits, quest/access gates, or wider item support.

## Source Evidence

| Target | Source | Captured facts |
| --- | --- | --- |
| Highwayman | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/highwayman_level_5.plugin.kts:5-66` | NPC IDs `HIGHWAYMAN`, `HIGHWAYMAN_2677`, `HIGHWAYMAN_7443`; guaranteed Bones and `Items.CAPE_1019`; main table total 20 with `Items.IRON_BOLTS` quantity range 2..12 at 1 slot and 19 nothing slots; death handler rolls the table; attack speed 4; respawn 60; 130 lifepoints; stats 2/2/4/1/1; generic attack bonus 6; strength bonus 7; defence slash 3, crush 2, ranged 2; aggro radius 4. |

## Item Sources

- Cape constant:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:960`
- Iron bolts constant:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:8260`
- Cape item/equipment block:
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:10592-10621`
- Iron bolts item name:
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:99150-99151`

## Assets

- New `combatitems/cape.png` icon fetched from the `Black cape` wiki file while
  preserving the local source display/drop name `Cape`.
- `Iron bolts` reuses the existing Fletching item definition and
  `fletcheditems/iron_bolts.png`.
- The new fetch is recorded in `assets_provenance.json`.

## Runtime Notes

- The Highwayman drop roll grants guaranteed Bones and Cape before rolling the
  main table.
- A winning Iron bolts slot rolls the inclusive source range 2-12.
- The Combat target tooltip renders the new humanoid row as a normal enabled
  target with `Cape x1` and `Iron bolts x2-12 (1/20)` in the drop summary.

## Deferred Candidates

- Goblins still need an armed/unarmed split and broader low-tier item coverage.
- Farmers, Al-Kharid warriors, and many other humanoids need nested/shared herb
  or seed table support.
- Barbarians need weapon-variant decisions and wider equipment item support.

## Verification

- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_highwayman_import_row_matches_source_and_quantity_range tests.test_combat_logic.CombatLogicTest.test_highwayman_quantity_range_drop_rolls_with_guaranteed_cape tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_is_selectable_and_shows_simple_enemy_targets`
- `python3 run_tests.py` passed with 571 tests (128 skipped).
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 571 tests.
- `git diff --check`
