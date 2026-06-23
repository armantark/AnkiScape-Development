# Combat Spider Drop-Range Audit - 2026-06-23

Status: implemented Spider/Giant spider ordinary-enemy slice plus Combat
quantity-range drop support.

## Scope

- Adds source-backed Spider and level-2 Giant spider as ordinary Combat targets.
- Extends the existing Combat drop slot contract with `quantity_range` for
  inclusive source ranges such as `Items.AIR_RUNE, quantityRange = 4..6`.
- Keeps higher-risk spider variants deferred: level-50 Giant spider, deadly red
  spider, poison spiders, and any access/special-mechanic rows.
- Fetches missing combat-only item icons for charms and Staff of air while
  reusing existing Runecrafting, Smithing, and Fletching art for rune/bronze/bow
  drops.

## Source Evidence

| Target | Source | Captured facts |
| --- | --- | --- |
| Spider | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/spider_level_1.plugin.kts:6-66` | NPC ID `Npcs.SPIDER`; main table total 200 with Gold/Green/Crimson/Blue charm slots 5/7/3/2 and 183 nothing; death handler rolls the table; attack speed 4; respawn 35; 20 lifepoints; stats 1/1/1/1/1; stab/crush attack penalties -35/-58; defence bonuses -53; Spider Slayer XP 2.0. |
| Giant spider | `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/giant_spider_level_2.plugin.kts:6-95` | NPC IDs `GIANT_SPIDER`, `GIANT_SPIDER_60`, `GIANT_SPIDER_12352`; main table total 48 with Air rune quantity range 4..6, Earth rune x4, Fire rune x6, Body rune x7, and 24 nothing; Secondary, Tertiary, and Charms tables; death handler rolls the table; attack speed 4; respawn 30; 50 lifepoints; stats 1/1/1/1/1; attack/defence bonuses -10; Spider Slayer XP 5.0. |

## Item Sources

- Rune constants: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:555-560`
- Bronze ammunition constants:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:877-882`
- Staff of air constant:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:1322`
- Charm constants:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt:10766-10771`

## Assets

- New `combatitems/` icons: Gold charm, Green charm, Crimson charm, Blue charm,
  and Staff of air.
- Existing reused icons: Air/Earth/Fire/Body rune from Runecrafting; Bronze med
  helm and Bronze kiteshield from Smithing; Bronze bolts, Bronze arrows, and
  Longbow from Fletching; Sling from existing Combat metadata.
- All new fetches are recorded in `assets_provenance.json`.

## Runtime Notes

- `quantity_range` rolls only after a slot wins, using the same injected RNG
  stream as table selection. Invalid ranges fall back to fixed `quantity`.
- Existing guaranteed drops and fixed table quantities are unchanged.
- The Combat target tooltip now renders ranged quantities as `x4-6`.

## Deferred Candidates

- Level-50 Giant spider is a future dangerous-target/access slice.
- Deadly red spider and poison spiders need a separate poisonous/high-risk
  enemy pass.
- Goblins still need armed/unarmed split and wider low-tier item coverage.
- Farmers, Al-Kharid warriors, and other human NPCs still need nested/shared
  herb/seed table support.

## Verification

- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_spider_import_rows_match_source_and_quantity_range tests.test_combat_logic.CombatLogicTest.test_giant_spider_quantity_range_drop_rolls_inclusive_high tests.test_target_metadata.TargetMetadataTest.test_combat_rows_expose_enabled_source_backed_enemy_targets tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_is_selectable_and_shows_simple_enemy_targets`
- `python3 run_tests.py` passed with 569 tests (128 skipped).
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 569 tests.
- `git diff --check`
