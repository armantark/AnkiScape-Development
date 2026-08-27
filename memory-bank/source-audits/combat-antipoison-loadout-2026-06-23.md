# Combat Antipoison Loadout - 2026-06-23

## Scope

This slice adds the narrow potion-loadout behavior needed by the current poison
status path: loaded Antipoison and Super antipoison doses automatically cure
active player poison, replace the consumed dose with the next source dose item,
and grant the source poison-immunity timer.

## Source Anchors

- Local potion dose source:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/potion/Potion.kt`
- Local potion effect source:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/potion/PotionType.kt`
- Local poison immunity check:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/PawnExt.kt`
- Local item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Source Facts

- `Potion.kt` maps Antipoison (4/3/2/1) to Antipoison (3/2/1) and Vial.
- `Potion.kt` maps Super antipoison (4/3/2/1) to Super antipoison (3/2/1)
  and Vial.
- `PotionType.kt` clears active poison state for both potion families.
- `PotionType.kt` gives Antipoison `POISON_IMMUNITY = 1500`.
- `PotionType.kt` gives Super antipoison `POISON_IMMUNITY = 6000`.
- `PawnExt.kt` checks poison immunity before applying poison.

## Implemented Scope

- `COMBAT_ANTIPOISON_POTION_DATA` records the dose replacement and immunity
  ticks for Antipoison and Super antipoison.
- Combat item registration now includes Antipoison and Super antipoison doses
  as inventory-visible material items, while Vial reuses the existing crafted
  item row.
- `combat_supply_loadout["potions"]` now sanitizes to the supported antipoison
  dose names instead of accepting arbitrary potion strings.
- Manual refill, fresh fights, kills, and safe noncombat recovery can move
  supported antipoison doses from inventory into the finite potion loadout.
- If poison is active, a loaded antipoison dose auto-cures it before status
  ticks can deal poison damage.
- Antipoison dose replacement stays in the potion loadout when the replacement
  is another antipoison dose; one-dose potions return Vial to inventory.
- Active poison immunity decrements on Combat and safe recovery ticks, blocks
  new enemy poison application, and appears in poison status summaries and
  target previews.
- The Combat hub loadout summary now shows loaded potion doses.

## Deferred

- Manual potion preference controls beyond using loaded antipoison dose order.
- Broader potion effects such as restores, Prayer restore, antifire, and boosts.
- Herblore brewing, potion decanting, weapon poison, disease, venom, bleed-style
  statuses, and non-antipoison immunity sources.
- Potion-specific icons/assets beyond current item registration.

## Verification

- `python3 -m py_compile combat_data.py logic_pure.py ui.py tests/test_combat_logic.py tests/test_skill_and_item_registry.py tests/test_main_menu_widget.py tests/test_integration_smoke.py`
- `python3 -m unittest tests.test_combat_logic.CombatLogicTest.test_antipoison_potions_match_2011scape_source tests.test_combat_logic.CombatLogicTest.test_antipoison_loadout_auto_cures_poison_before_safe_recovery_tick tests.test_combat_logic.CombatLogicTest.test_poison_enemy_antipoison_loadout_auto_cures_after_source_poison tests.test_combat_logic.CombatLogicTest.test_poison_immunity_blocks_enemy_poison_without_spending_antipoison tests.test_combat_logic.CombatLogicTest.test_manual_refill_loadout_uses_food_queue_and_current_magic_spell tests.test_combat_logic.CombatLogicTest.test_unload_combat_supply_loadout_returns_supplies_to_bank tests.test_combat_logic.CombatLogicTest.test_combat_preview_marks_poison_enemies_as_food_advised`
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_repairs_stale_loadout_before_exposing_controls tests.test_integration_smoke.TestIntegrationSmoke.test_combat_loadout_menu_callbacks_refill_and_unload_supplies`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
