# Dream transaction proof matrix

**Status:** proposed proof only. No case below has been run. Dream implementation remains blocked until Magic is accepted and landed. The only accepted helper contract is:

```
_apply_dream_transaction(data, dream_cost, max_lp_for_dream) -> result | None
```

The source baseline is P8 `b044efa72670d6c26749d9218d5b84a274c72eb9`, specifically `logic_pure/logic_pure_combat_engine.py:1230-1272`; the transaction being extracted is `:1257-1267`. Costs are `DREAM_COST = {"Astral rune": 2, "Cosmic rune": 1, "Body rune": 5}` at `data/magic_data.py:616`.

## Reusable fixtures and proof mechanism

Use the existing `_player` fixture in `tests/test_combat_logic.py:109-138` with an explicit `enemy_data={}` when a normal target-validation continuation is required. A valid Dream base is:

```
current_combat_target="missing_target"
equipment={}
magic_level=99
constitution_level=10              # max LP 100
quests={"dream_mentor": {"completed": True}}
combat_dream_thrift=True
combat_encounter={}
inventory={"Astral rune": 2, "Cosmic rune": 1, "Body rune": 5}
```

No equipment means the selected standard spell does not enter the preset spellbook set; valid Dream can reach the transaction. `enemy_data={}` makes a non-Dream path deterministically reach the existing target lock at engine `:1270-1272` without combat rolls.

Use ordinary `unittest` assertions already used by `tests/combat/test_magic_module.py:69-88`: `deepcopy` for no-write checks, `assertIs` for identity, and `assertRaisesRegex` for raw failures. A focused test in the existing combat test suite may import the engine module and call the private helper directly. This adds cases, not a new test framework.

## Full-burst cases

| ID | Concrete variation | Source-derived expectation | Contract clauses covered |
|---|---|---|---|
| FB-1 | Base player plus `equipment={"weapon": "Slayer's staff"}`, `current_combat_spell="wind_strike"`, and no `combat_spellbook_swap`. | The preset is rejected as a mixed-spellbook preset before the Dream max-LP read or helper call. Return is the original supplied player, `False`, and the existing `combat_locked` result. Patch the engine max-LP function and helper with fail-on-call sentinels. | Engine retains preset-lock rejection and ordering (`:1246-1248`). |
| FB-2 | Parameterize the base player into: (a) `combat_dream_thrift=False`, (b) active `combat_encounter={"target_id": "chicken", "enemy_lifepoints": 1}`, (c) `combat_lifepoints=100`, and (d) omit `combat_lifepoints`. | In every subcase, the engine makes its unconditional max-LP read at `:1251`, does not calculate cost or call the helper, then reaches normal target validation. The returned tuple is the existing target lock for `missing_target`. Spy on the max-LP read and use fail-on-call cost/helper sentinels. The omitted-LP subcase confirms the caller gate treats the missing value as max; sanitation may materialize that value before the check, so it is not a proof of the helper's different default. | Unconditional max-LP read; flag, active-encounter, and below-max eligibility; no cost at an ineligible gate; no early Dream return. |
| FB-3 | Base player with `combat_lifepoints=50` and `inventory={"Astral rune": 1, "Cosmic rune": 1, "Body rune": 5}`. | Cost is computed before the helper. The helper returns `None`; there is no Dream result, no early success, and normal target validation returns the existing locked tuple. Wrap the cost function and helper with a two-entry event list, then assert `cost` before `helper`; direct cases below prove the no-write rule. | Caller-owned effective-cost timing; unaffordable return path; caller continues after `None`. |
| FB-4 | Base player with sufficient runes; subcases `(combat_lifepoints, expected_healed, expected_lp) = (20, 50, 70)` and `(75, 25, 100)`. | Each call succeeds before target validation despite `missing_target`, returns `reason == "dream"`, and has `ticks == ticks_elapsed == 0`. Inventory debits to zero, Magic XP rises by 82.0, and `result["runes_used"]` equals the supplied effective cost. Assert `out is not player`, `out["combat_last_result"] is result`, and key order `Astral rune`, `Cosmic rune`, `Body rune`. The first row proves the 50-LP cap; the second proves the maximum-LP cap. | Affordability/debit/heal/XP/result; early `(data, True, result)` tuple; same result object stored and returned; copied ordered `runes_used`. |

FB-4's source mutation sequence is fixed and must remain: copy inventory, debit each cost entry, write `data["inventory"]`, calculate and write LP, write Magic XP, construct `result`, then the caller writes `data["combat_last_result"]` and returns (`:1260-1269`). The test observes the externally visible boundaries and identity; the static check below pins the otherwise unobservable internal write ordering.

## Direct helper cases

These cases intentionally bypass full-burst sanitation and eligibility. They test the transaction's literal boundary, not user-reachable malformed combat state.

| ID | Direct inputs | Source-derived expectation | Contract clauses covered |
|---|---|---|---|
| DT-1 | `data={"inventory": {"Body rune": 5, "Astral rune": 2, "Cosmic rune": 1}, "combat_lifepoints": 75, "magic_exp": 3.0}`, `dream_cost={"Body rune": 5, "Astral rune": 2, "Cosmic rune": 1}`, `max_lp_for_dream=100`. | The helper returns the Dream result with `healed=25`; it mutates that same `data` mapping in place, replaces `data["inventory"]` with a copied/debited dict, sets LP 100 and Magic XP 85.0. `runes_used` is a distinct `dict(dream_cost)` with the exact supplied key order. | In-place data mutation; supplied cost iteration/copy; debit, maximum cap, XP, and result construction. |
| DT-2 | Same sufficient inventory and standard cost, but omit `combat_lifepoints`; `max_lp_for_dream=100`. | Return `healed=50` and write `combat_lifepoints=50`. This deliberately differs from the full-burst eligibility default, which treats a missing LP as max at `:1255`. | Required LP-default asymmetry: transaction uses zero at `:1264-1265`; caller retains its max default. |
| DT-3 | One Astral rune short, with a sentinel `combat_last_result`, `combat_lifepoints=50`, and `magic_exp=3.0`; retain the original inventory object and a deep copy of all data. | Return `None`; `data` equals the deep copy, its inventory remains the same object, and the sentinel remains. | Affordability returns `None`; no inventory, LP, XP, result, or other write on unaffordable input. |
| DT-4 | `data={"inventory": None, "combat_lifepoints": 50, "magic_exp": 3.0}`, standard cost, max 100. | Return `None`; `data["inventory"] is None`, and no field changes. The local `or {}` normalization does not write back. | Falsy-inventory normalization and no-write failure path. |
| DT-5 | `data={"inventory": {}, "combat_lifepoints": 50}`, `dream_cost={"missing rune": 0}`, max 100. | Affordability passes, then raw `inventory["missing rune"] -= 0` raises `KeyError`. No data write precedes it, so the original empty inventory remains attached to `data`. | Raw debit and exception ordering; no newly added debit guard. |
| DT-6 | `data={"inventory": {"Astral rune": "2", "Cosmic rune": "1", "Body rune": "5"}, "combat_lifepoints": 50}`, standard cost, max 100. | The affordability conversion accepts the numeric strings, then raw subtraction raises `TypeError` on the first debit; no `data` field is written first. `_non_negative_int` parses with `int` at `logic_pure/logic_pure_state.py:50-56`. | Raw stored-value exception behavior and debit-before-write ordering. |
| DT-7 | `data={"inventory": ["truthy non-mapping"], "combat_lifepoints": 50}`, standard cost, max 100. | The truthy list is retained by `data.get("inventory", {}) or {}` and `.get` raises `AttributeError`; it is not normalized. Data remains unchanged. | Truthy non-Mapping behavior, precisely distinguished from falsy normalization. |

DT-5 through DT-7 use `assertRaisesRegex` and a pre-call deep copy. They must assert the original mapping/field identity where stated, rather than merely comparing a sanitized replacement. DT-1 and FB-4 together require `runes_used is not dream_cost` as well as equal contents and preserved key order.

## Static and differential proof

Retain the existing pinned two-graph comparator, `tools/combat/compare_magic_module.py`:

* Its source guards refuse unpinned graphs before product imports (`:73-137`), preserve the baseline corpus, run the same cases in isolated baseline and candidate graphs (`:335-367`), and keep every current direct and route observation equal. Do not weaken or replace those guards.
* Its current `ROUTES` list already covers the three legacy Dream gates at `:35-54`, including active encounter. It has no successful eligible-Dream or short-rune continuation route.
* Do **not** add candidate-only unittest names to `ROUTES`: the baseline corpus cannot contain those methods. Instead, extend the comparator's existing `route_observations` mechanism with two shared, inline scenario observations built from the FB-3 and FB-4 inputs. They run against both frozen baseline and candidate graphs and compare the complete recorded entrypoint return/state/rng snapshots. This is an extension of the established comparator, not another harness.
* `snapshot` and `recorded_entrypoint` deep-copy values (`:226-292`), so they cannot prove that `combat_last_result` and tuple element three are the same object. Record a boolean identity field before copying in that existing observation path, and retain the direct `assertIs` in FB-4. Do not infer identity from equal dict contents.
* Extend the existing source/AST guard pattern in `tools/combat/check_magic_module_guards.py` to require the exact helper signature, `None` unaffordable path, two `dream_cost.items()` traversals, `dict(dream_cost)`, raw subscript debit, and caller-side direct last-result assignment/early tuple. This static check is where the exact internal mutation order is pinned; it must not use a looser result-only comparison.

## Coverage check

| Accepted clause | Cases/check |
|---|---|
| Caller owns lock, unconditional max LP, eligibility, cost timing, last-result, early tuple | FB-1 through FB-4 plus static guard |
| Helper owns affordability, debit, heal, XP, result | FB-4, DT-1, DT-2 |
| `None` unaffordable and no writes | FB-3, DT-3, DT-4 |
| Missing-LP default asymmetry | FB-2(d), DT-2 |
| Falsy versus truthy inventory behavior | DT-4, DT-7 |
| Raw debit exceptions and ordering | DT-5, DT-6, static guard |
| Mapping order and copied `runes_used` | FB-4, DT-1, static guard |
| One shared result object stored and returned | FB-4 plus comparator identity boolean |
| No reverse import / Magic prerequisite | Existing Magic guard and acceptance gate; no Dream implementation or comparison run before they pass |

No measured outcome, gate status, or runtime claim is made in this packet.
