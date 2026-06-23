# Combat Ranged/Ammo Audit - 2026-06-23

Status: implemented first source-backed Ranged combat path.

## Implemented Scope

- Added source-backed Ranged attack styles to `combat_data.py`:
  `ranged_accurate`, `ranged_rapid`, and `ranged_longrange`.
- Added Shortbow as the first bow-backed Combat weapon using the local
  2011Scape `items.yml` equipment block: weapon slot, Ranged skill,
  two-handed, attack speed 4, and `attack_ranged = 8`.
- Added Bronze arrows as the first supported ammunition stack for Combat:
  item id 882, `ranged_strength = 7`, and Shortbow compatibility.
- Extended `apply_combat_burst_pure()` so Ranged uses the shared Combat burst
  engine instead of failing as an unsupported combat class.
- Ranged combat now:
  - requires a supported Ranged weapon and compatible ammunition;
  - refills `combat_supply_loadout["ammo"]` from inventory only at fresh-fight
    or safe-boundary refill points;
  - consumes one arrow per player attack attempt;
  - does not pull banked arrows mid-encounter;
  - uses Ranged attack/defence bonuses, source-shaped Ranged effective level,
    Ranged accuracy, and Ranged max hit;
  - routes `ranged_accurate` and `ranged_rapid` damage XP to Ranged;
  - routes `ranged_longrange` damage XP to split Ranged/Defence;
  - continues awarding Constitution XP per damage.
- Combat target metadata now passes equipment data into lock checks and shows
  player max hit plus loaded/banked ammo for Ranged-ready rows.
- Runtime Combat readiness and review handling now pass `EQUIPMENT_DATA` into
  the same lock helper, so the Skills hub and review handler agree.
- Existing Fletching assets are reused for Shortbow and Bronze arrows:
  `fletcheditems/shortbow.png` and `fletcheditems/bronze_arrows.png`.

## Source Anchors

- Ranged formula:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/RangedCombatFormula.kt`
- Ranged strategy, can-attack ammo checks, ammo removal, and XP routing:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/RangedCombatStrategy.kt`
- Bow compatibility:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/weapon/BowType.kt`
- Arrow family IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/ammo/Arrows.kt`
- Item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`
- Shortbow and Bronze arrow item stat blocks:
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`

## Decisions

- Ammunition is modeled through `combat_supply_loadout["ammo"]`, not the
  Equipment tab's `ammunition` slot, because the current equipment save model is
  one item name per slot and cannot represent stacked arrows.
- AnkiScape consumes one arrow per attack attempt and does not yet recover,
  break, or drop fired arrows. The source removes ammo from the quiver and may
  drop/break it, but AnkiScape does not yet have a ground-ammo recovery model.
- The first Ranged slice intentionally supports only Shortbow plus Bronze
  arrows, because both are already acquired through the Tutorial Island starter
  kit/Fletching route and have local source stats and assets.

## Deferred

- Stack-aware `ammunition` equipment slot behavior.
- Arrow recovery/drop/break modeling.
- More bows, crossbows, thrown weapons, and arrow/bolt tiers.
- Ranged loadout controls in the UI.
- Magic/rune combat routing.
- Quest combat migration onto the shared Combat burst engine.

## Verification

- `python3 -m py_compile logic_pure.py target_metadata.py runtime_actions.py combat_data.py equipment_data.py`
- `python3 -m unittest tests.test_combat_logic tests.test_equipment_data tests.test_target_metadata tests.test_runtime_actions tests.test_skill_and_item_registry`
- `python3 run_tests.py` (578 tests, 128 skipped)
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` (578 tests)
- `git diff --check`
