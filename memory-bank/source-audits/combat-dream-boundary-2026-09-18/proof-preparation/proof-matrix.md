# Dream transaction proof matrix

**Status:** proposed proof only. No case below has been run. Dream implementation remains blocked until Magic is accepted and landed. The accepted helper contract is exactly:

```
_apply_dream_transaction(data, dream_cost, max_lp_for_dream) -> result | None
```

The prior packet is preserved at `/tmp/ankiscape-dream-proof-matrix-2026-09-18.before-fixture-audit.md`. This revision corrects fixture reachability against P8 `b044efa72670d6c26749d9218d5b84a274c72eb9`.

## Reachable fixture

Use the existing `_player` fixture at `tests/test_combat_logic.py:109-138`, plus this **truthy** enemy map and matching target:

```
enemy_data = {"dream_dummy": {}}
current_combat_target = "dream_dummy"
equipment_data = {}
equipment = {}
magic_level = 99
constitution_level = 10
quests = {"dream_mentor": {"completed": True}}
combat_dream_thrift = True
combat_encounter = {}
combat_lifepoints = 50
combat_target_overrides = {}
combat_target_presets = {}
inventory = {"Astral rune": 2, "Cosmic rune": 1, "Body rune": 5}
allow_bank_run = False
```

This map is necessary. At engine `logic_pure/logic_pure_combat_engine.py:1227`, `enemy_data = enemy_data or COMBAT_ENEMY_DATA`; `{}` therefore selects the global roster. The same fallback is repeated in `sanitize_combat_state_pure` at `logic_pure/logic_pure_combat_model.py:1060-1068`, which also replaces an unknown target with the default target, or the first key of a truthy custom map. The matching one-entry map therefore keeps `dream_dummy` through sanitation and target overrides. If Dream does not return early, the engine safely completes style and spell selection (`:1273-1288`), then `combat_target_locked_reasons_pure` returns `("missing source combat stats",)` for the empty enemy record (`logic_pure/logic_pure_combat_model.py:1268-1282`). With `allow_bank_run=False`, engine `:1303-1309` returns that lock before enemy setup, the later max-LP read at `:1377`, or RNG.

Pre-Dream audit for this fixture:

1. The engine copies data then calls sanitation (`logic_pure/logic_pure_combat_engine.py:1073-1075`). Sanitation independently reads max LP at model `:1082` and materializes a valid `combat_lifepoints` field. That is distinct from the engine's unconditional Dream max-LP read at engine `:1251`.
2. With empty target-preset maps, engine `:1241-1245` uses `apply_combat_target_overrides_pure`; it has no Dream-setting override to replace. The function only applies entries in `COMBAT_PRESET_FIELDS` for the exact target (`logic_pure/logic_pure_combat_model.py:510-518`).
3. Empty `equipment` means the ordinary selected spell does not enter the Magic preset effect set. Valid Dream is then the only effect and passes the preset gate. `equipment_data={}` is accepted by engine `:1228`; it is passed through the safe empty-equipment style, ranged-spec, and lock calls at `:1273-1289`, before the deterministic lock.
4. An active case must use `combat_encounter={"target_id": "dream_dummy", "enemy_lifepoints": 1}`. Sanitation keeps a Mapping encounter; `combat_has_active_encounter_pure` tests that its target is a string and is not disengaged (`logic_pure/logic_pure_combat_engine.py:1959-1965`).

Costs are `DREAM_COST = {"Astral rune": 2, "Cosmic rune": 1, "Body rune": 5}` at `data/magic_data.py:616`.

Use ordinary `unittest` patterns already present in `tests/combat/test_magic_module.py:69-88`: `deepcopy` for no-write checks, `assertIs` for identity, `assertRaisesRegex` for raw failures, and `unittest.mock.patch.object(..., wraps=...)` for call-order observation. A focused test in the existing combat suite may import the engine module and call the private helper directly. This is not a new test framework.

## Full-burst cases

| ID | Concrete variation from the reachable base | Source-derived expectation |
|---|---|---|
| FB-1 | Set `equipment={"weapon": "Slayer's staff"}` and keep `current_combat_spell="wind_strike"`; no `combat_spellbook_swap`. | The Magic preset gate sees standard spell plus Lunar Dream and returns the existing mixed-spellbook lock before the **engine Dream** max-LP read or helper call (`engine:1246-1251`; magic `:32-53`). Return is the original supplied player, `False`, and the existing `combat_locked` result. Patch the engine's imported `combat_max_lifepoints_pure` and the helper with fail-on-call sentinels. Do not treat sanitation's earlier model-owned max-LP read as a failure of this ordering proof. |
| FB-2 | The reachable base is injured at LP 50 and has sufficient runes. Parameterize: (a) set `combat_dream_thrift=False` while keeping no encounter; (b) keep Dream enabled and sufficient runes, but use the active encounter from the audit above; (c) override LP to 100; (d) remove `combat_lifepoints` from the `_player(...)` result before the burst. Keep `allow_bank_run=False`. | The engine performs its unconditional Dream max-LP read at `:1251`, makes no effective-cost or helper call, then reaches the deterministic `missing source combat stats` lock through `:1273-1309`. Each row isolates its intended false eligibility condition instead of also being full LP. Spy on the engine's imported max-LP binding and assert one call; use fail-on-call cost/helper sentinels. Case (d) confirms the caller gate sees the sanitized/default-max LP. It is deliberately not the helper-default proof. |
| FB-3 | Set `combat_lifepoints=50`, `inventory={"Astral rune": 1, "Cosmic rune": 1, "Body rune": 5}`, and retain `allow_bank_run=False`. | Effective cost is called before the helper. The helper returns `None`; no Dream result or early success occurs, and the deterministic target lock follows through `:1273-1309`. Wrap the cost function and helper with a two-entry event list and assert `cost` then `helper`. Direct cases DT-3 and DT-4 prove the helper's no-write path. |
| FB-4 | Sufficient runes; subcases `(combat_lifepoints, expected_healed, expected_lp) = (20, 50, 70)` and `(75, 25, 100)`. | Dream returns before the invalid enemy's lock: `ok is True`, `reason == "dream"`, and `ticks == ticks_elapsed == 0`. Inventory debits to zero; Magic XP rises by 82.0; `runes_used` is the effective cost in `Astral rune`, `Cosmic rune`, `Body rune` order. Assert `out is not player` and `out["combat_last_result"] is result`. The two rows prove the 50-LP and maximum-LP caps. |

FB-4's required source sequence is: helper completes debit, inventory write, LP write, Magic XP write, and result construction; then the engine stores that returned object in `combat_last_result` and returns it. Root's extraction AST/source comparison checks that complete internal sequence. Final-state cases and the FB-3 call-order spy do not prove every internal write; they prove the observable result, caller timing, and the direct exception boundaries before a data-field write.

## Direct helper cases

These deliberately bypass full-burst sanitation and eligibility. They test the transaction's literal boundary, including malformed inputs that a real burst does not route into the block.

| ID | Direct inputs | Source-derived expectation |
|---|---|---|
| DT-1 | `data={"inventory": {"Body rune": 5, "Astral rune": 2, "Cosmic rune": 1}, "combat_lifepoints": 75, "magic_exp": 3.0}`, `dream_cost={"Body rune": 5, "Astral rune": 2, "Cosmic rune": 1}`, max 100. | The helper mutates the supplied `data` mapping in place; returns `healed=25`; replaces inventory with a copied/debited dict; writes LP 100 and Magic XP 85.0. `runes_used` equals but is not `dream_cost`, and preserves the supplied Body/Astral/Cosmic order. |
| DT-2 | Sufficient standard cost and inventory, but omit `combat_lifepoints`; max 100. | Returns `healed=50` and writes LP 50. This proves the transaction's zero default, distinct from full-burst caller eligibility at engine `:1255`. |
| DT-3 | One Astral rune short, with sentinel `combat_last_result`, LP 50, Magic XP 3.0; retain original inventory identity and a deep copy. | Returns `None`; all data equals the deep copy, inventory remains the same object, and the sentinel remains. |
| DT-4 | `data={"inventory": None, "combat_lifepoints": 50, "magic_exp": 3.0}`, standard cost, max 100. | Returns `None`; stored inventory remains `None` and no field changes. Falsy inventory normalizes only in a local variable. |
| DT-5 | `data={"inventory": {}, "combat_lifepoints": 50}`, `dream_cost={"missing rune": 0}`, max 100. | Affordability passes, then raw debit raises `KeyError` before `data["inventory"]` is assigned. The original empty inventory stays attached. |
| DT-6 | `data={"inventory": {"Astral rune": "2", "Cosmic rune": "1", "Body rune": "5"}, "combat_lifepoints": 50}`, standard cost, max 100. | Affordability's integer conversion accepts the strings, then the first raw subtraction raises `TypeError` before any data-field write. `_non_negative_int` parses via `int` at `logic_pure/logic_pure_state.py:50-56`. |
| DT-7 | `data={"inventory": ["truthy non-mapping"], "combat_lifepoints": 50}`, standard cost, max 100. | The truthy list is retained by `data.get("inventory", {}) or {}`; `.get` raises `AttributeError`. It is not normalized, and data is unchanged. |

DT-3 through DT-7 use `assertRaisesRegex` where applicable plus a pre-call deep copy. They must assert identities where stated, not merely compare a sanitized replacement.

## Comparator reuse

Retain `tools/combat/compare_magic_module.py` and its pinned, isolated baseline/candidate graph checks. Its source guards run before product import (`:73-137`) and its worker compares both graphs (`:335-367`). Keep all current observations unchanged.

The existing `ROUTES` already include the three legacy Dream gate tests (`:35-54`) but no successful eligible Dream or short-rune continuation. Do not add candidate-only unittest names there because the frozen baseline corpus cannot contain them. After Magic is accepted, extend the comparator's existing `route_observations` with shared FB-3 and FB-4 scenario calls using the truthy `dream_dummy` map. Those scenarios run in both graphs and compare the recorded return, caller state, and RNG trace.

`snapshot`/`recorded_entrypoint` deep-copy values (`:226-292`), so they cannot prove shared object identity. Record an identity boolean in that existing observation path before copy, and retain FB-4's ordinary `assertIs`. No additional Dream-specific static implementation-shape checker is needed: the direct cases prove raw exceptions/no-write boundaries and the ordinary spies prove caller ordering.

## Clause coverage

| Accepted clause | Proof |
|---|---|
| Preset lock before engine max-LP and helper | FB-1 |
| Unconditional engine max-LP, flag/active/full eligibility, no early path | FB-2 |
| Caller effective-cost timing and `None` continuation | FB-3 |
| Helper debit/heal/XP/result and caller storage/early tuple | FB-4, DT-1, DT-2 |
| Both heal caps | FB-4 |
| No write on unaffordable or falsy inventory | DT-3, DT-4 |
| LP default asymmetry | FB-2(d), DT-2 |
| Raw debit exceptions and write order | DT-5, DT-6 |
| Falsy versus truthy inventory behavior | DT-4, DT-7 |
| Supplied mapping order and copied `runes_used` | FB-4, DT-1 |
| One result object stored and returned | FB-4 and comparator identity boolean |
| Magic prerequisite and no reverse import | Existing Magic acceptance/guard; no Dream code or comparison run before it passes |

No measured outcome, gate status, or runtime claim is made in this packet.
