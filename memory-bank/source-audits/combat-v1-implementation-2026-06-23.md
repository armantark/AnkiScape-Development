# Combat V1 Implementation Audit - 2026-06-23

Status: implemented ordinary-combat V1 slice.

## Implemented Scope

- Combat is a general review action (`Combat`) routed through
  `action_registry.py` and `runtime_actions.py`, not a quest-only resolver and
  not a fake levelled registry skill.
- `combat_data.py` seeds source-backed ordinary enemies with complete combat
  stats and drop behavior: Chicken, Rat, Giant rat, and Cow.
- `apply_combat_burst_pure()` simulates bounded RuneScape-shaped combat time:
  50 ticks per `Actions per review`, player/enemy attack speed, accuracy rolls,
  max-hit rolls, persistent lifepoints, persistent partial enemy HP, auto-eat,
  death/grave state, per-damage XP, guaranteed drops, and one roll per
  non-guaranteed drop table.
- Melee styles route XP as Attack, Strength, Defence, or controlled shared
  Attack/Strength/Defence, with Constitution XP awarded per damage.
- The Skills hub has a Combat category/card, enemy target tree, attack-style
  selector, availability gate, and HUD target/lifepoint display.
- Storage config version 21 seeds and sanitizes Combat state while preserving
  the flat save model.

## Source Anchors

- Formula: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MeleeCombatFormula.kt`
- Damage roll/old-hitpoint scaling:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/PawnExt.kt`
- Damage XP routing:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MeleeCombatStrategy.kt`
- Food healing:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/food/Food.kt`
- Chicken:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/chicken_level_1.plugin.kts`
- Rat:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/rat_level_1.plugin.kts`
- Giant rat:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/giant_rat_level_2.plugin.kts`
- Cow:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/cow_level_2.plugin.kts`
- Drop item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Deferred

- Broader enemy registry import, including NPCs with global tables or special
  mechanics.
- Ranged/Magic combat routing, ammo/rune consumption, spell selection, and
  noncombat Magic actions.
- Prayer effects, drain, and Prayer skilling.
- Dangerous-target confirmation UX and richer risk previews.
- Full grave countdown and Death's Office reclaim UI; V1 records grave state
  but does not yet expose the full recovery loop.
- Quest combat migration from the existing lightweight quest resolver onto the
  shared combat engine.

## Verification

- `python3 -m py_compile combat_data.py constants.py logic_pure.py storage_pure.py action_registry.py runtime_actions.py target_metadata.py ui.py __init__.py`
- `python3 -m unittest tests.test_combat_logic tests.test_runtime_actions tests.test_storage_pure tests.test_skill_and_item_registry tests.test_target_metadata tests.test_review_hud`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
