# Combat Simple Enemies Audit - 2026-06-23

Status: implemented ordinary-enemy expansion slice.

## Scope

- Adds three source-backed ordinary Combat targets that fit the existing Combat
  V1 runtime without new drop-table semantics: Cow calf, Ram, and Seagull.
- Keeps richer candidates deferred until their missing prerequisites are built:
  quantity ranges, nested shared tables, broader combat item manifest coverage,
  charm assets, or variant split decisions.

## Source Evidence

| Target | Source | Captured facts |
| --- | --- | --- |
| Cow calf | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/cow_calf_level_2.plugin.kts:6-63` | NPC IDs 2310/12364/12366; combat level 2; attack speed 4; respawn 45; 60 lifepoints; stats 1/1/1/1/1; defence bonuses -26; guaranteed Bones, Raw beef, Cowhide; Cow Slayer XP 6.0. |
| Ram | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/ram_level_2.plugin.kts:5-55` | NPC IDs 3672/3673/5168/12369/12370/12371; combat level 2; attack speed 4; respawn 45; 80 lifepoints; stats 1/1/1/1/1; defence bonuses -21; guaranteed Bones. |
| Seagull | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/seagull_level_2.plugin.kts:6-61` | NPC IDs 6115/6116; combat level 2; attack speed 4; respawn 25; 60 lifepoints; stats 1/1/1/1/1; defence bonuses -42; guaranteed Bones; Bird Slayer XP 5.0. |

## Assets

- Bones already resolves through existing Hunter item art.
- Raw beef already resolves through existing Cooking item art.
- Cowhide now resolves through `combatitems/cowhide.png`, fetched with
  `tools/fetch_assets.py` and recorded in `assets_provenance.json`.

## Deferred Candidates

- Spider/Giant spider: wait for charm icon coverage and quantity-range drop
  support.
- Goblins: wait for explicit armed/unarmed split and broader low-tier item
  manifest coverage.
- Farmers/Al-Kharid warriors: wait for nested shared herb/seed table support.
- Highwayman: wait for quantity-range support and attack-style subtype notes.

## Verification

- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_simple_enemy_import_rows_match_source tests.test_combat_logic.CombatLogicTest.test_cow_calf_burst_grants_source_guaranteed_drops tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_is_selectable_and_shows_simple_enemy_targets`
- `python3 run_tests.py` passed with 567 tests (128 skipped).
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 567 tests.
- `git diff --check`
