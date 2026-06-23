# Combat Magic/Runes Audit - 2026-06-23

Status: implemented first source-backed combat Magic path.

## Implemented Scope

- Added Wind Strike as the first source-backed combat spell:
  level 1 Magic, Air rune x1, Mind rune x1, max hit 2 old HP / 20 LP,
  5.5 base Magic XP, and 5-tick attack speed.
- Added `magic_standard` as the first Magic attack style in the shared Combat
  engine.
- Added `current_combat_spell` to the flat combat save state, defaulting to
  `wind_strike`.
- Extended `apply_combat_burst_pure()` so combat Magic uses the same bounded
  review burst engine as melee and Ranged.
- Magic combat now:
  - requires the selected spell's Magic level and runes before starting;
  - refills `combat_supply_loadout["runes"]` from inventory only at fresh-fight
    or safe-boundary refill points;
  - consumes Air rune x1 and Mind rune x1 per Wind Strike attack attempt;
  - does not pull banked runes mid-encounter;
  - uses Magic attack and Magic defence bonuses for accuracy;
  - uses the selected combat spell's source max hit plus magic-damage bonus;
  - awards Wind Strike base Magic XP on every cast, including splashes;
  - awards Magic damage XP plus Constitution XP on damage.
- Combat target rows now show the selected spell plus loaded/banked rune
  readiness for Magic-ready rows and lock on missing runes.
- The Combat hub exposes a spell selector next to the existing attack-style
  selector and persists changes through `current_combat_spell`.

## Source Anchors

- Magic combat formula:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MagicCombatFormula.kt`
- Magic combat strategy, rune removal, and XP routing:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MagicCombatStrategy.kt`
- Combat spell constants:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/magic/CombatSpell.kt`
- Standard spellbook Wind Strike row:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/SpellbookData.kt`
- Magic spell requirement/removal helper:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicSpells.kt`
- Rune item IDs/names:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`
  and `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`

## Decisions

- Wind Strike is the only enabled spell in this checkpoint. It is the safest
  first row because the starter kit already grants Air/Mind runes and the
  source spellbook row has complete level, rune, XP, and max-hit data.
- Runes use `combat_supply_loadout["runes"]`, mirroring the new ammo loadout
  path. This keeps the flat save model and makes active encounters unable to
  pull the whole bank mid-fight.
- The current UI keeps combat Magic under the synthetic `Combat` action rather
  than turning `Magic` into a standalone selectable skill row. The registry row
  should become live when there is a real Magic panel/noncombat spell family;
  otherwise it would render as a hollow implemented skill while all review work
  still runs through Combat.

## Deferred

- Staff rune substitution.
- Autocast equipment metadata and spell selection from weapons.
- Additional strike/bolt/blast/wave spells and other spellbooks.
- Stack-aware rune pouch behavior.
- Player-facing rune loadout controls beyond the current auto-refill model.
- Noncombat Magic actions such as teleports, enchanting, and alchemy.
- Making the Magic skill registry row playable once it has a real panel/action
  family.
- Quest combat migration onto the shared Combat burst engine.

## Verification

- `python3 -m py_compile combat_data.py constants.py logic_pure.py target_metadata.py ui.py __init__.py tests/test_combat_logic.py tests/test_runtime_actions.py tests/test_target_metadata.py tests/test_storage_pure.py tests/test_main_menu_widget.py`
- `python3 -m unittest tests.test_combat_logic tests.test_runtime_actions tests.test_target_metadata tests.test_storage_pure` (103 tests)
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget` (129 tests)
