# Next cleanup boundary: Dream transaction

## Status and priority

This is read-only selection evidence from main `0d606cfd3e79fa660223a5b0a00974c9098a9447`, not implementation or acceptance authorization. Ruling 47 makes the largest exposed engine function the priority. Ruling 48 requires a responsibility seam, and ruling 53 forbids a reverse dependency.

The source-only Lizard command is:

```sh
/Users/ArmanTarkhanian1/.local/bin/lizard --csv logic_pure/logic_pure_combat_engine.py | rg 'apply_combat_burst_pure@'
```

Its raw record begins `1213,299,6303,11,1276`: NLOC is **1213** and Lizard CCN is **299**. A separate source-only Complexipy run reports cognitive **561**. These are current-function measurements, not a prediction for a helper.

## Ownership contract

Dream is `logic_pure/logic_pure_combat_engine.py:1080-1100`. The engine keeps, in the existing order:

1. preset-lock rejection;
2. unconditional `max_lp_for_dream` read;
3. Dream flag, no-active-encounter, and below-maximum-LP eligibility;
4. `dream_cost = effective_magic_rune_cost_pure(data, DREAM_COST)`;
5. after a successful helper result, the `combat_last_result` write and the exact early `(data, True, result)` return.

The helper is exactly:

```text
_apply_dream_transaction(data, dream_cost, max_lp_for_dream) -> result | None
```

It mutates the supplied `data` mapping in place and owns only affordability, debit, healing, Magic XP, and construction of `result`. It returns `None` when unaffordable and returns no replacement `data` mapping.

The helper must preserve these source details:

- The engine eligibility check defaults a missing `combat_lifepoints` to `max_lp_for_dream`; the transaction's heal and LP writes default that same missing field to `0`. The helper keeps the `0` default.
- `inventory = data.get("inventory", {}) or {}` normalizes falsy inventory values only. An arbitrary truthy non-Mapping is not normalized and retains its existing downstream failure behavior.
- Affordability uses `_non_negative_int(inventory.get(rune, 0), 0)`, but debit remains raw `inventory[rune] -= amount`. Do not add a debit guard: an absent rune with a zero cost passes affordability then raises `KeyError`; incompatible raw stored values retain their existing exception behavior.
- On an unaffordable result, it writes neither inventory nor another state field. In particular, a normalized local inventory must not be written back over `None`.
- Both cost loops use the supplied mapping's iteration order. `runes_used` is `dict(dream_cost)`, a copy.
- The engine stores the one returned result object directly in `data["combat_last_result"]` and returns that same object as tuple element three. Neither side copies it.

The existing main dependency is indirect: `logic_pure_combat_engine` reaches magic behavior through `logic_pure_combat_model`, not through a direct `logic_pure_combat_magic` import. An accepted magic module is an explicit prerequisite before Dream implementation or landing. The final binding may change the module surface, but it must keep the direction away from a magic-to-engine import.

## Behavioral proof to require

This is a proof plan, not a completed test claim.

Full-burst comparison cases:

- Dream disabled, active encounter, and full LP: retain the unconditional max-LP read but no cost calculation, debit, XP, result, or early return.
- Eligible with one rune short: calculate cost before affordability, make no mutation, and continue into normal target validation.
- Eligible with exactly sufficient runes: preserve debit mapping order, then inventory write, LP write, Magic XP write, result construction, direct `combat_last_result` storage, and the same early tuple.
- Eligible with partial healing room: preserve both 50-LP and maximum-LP caps and the 82.0 Magic XP change.

Direct transaction cases, for literal transaction behavior that full-burst sanitation or caller eligibility may prevent from reaching this block:

- missing `combat_lifepoints`: preserve the transaction's `0` default;
- `inventory` set to `None`: return unaffordable without overwriting that stored value;
- zero-cost absent rune: preserve the raw-debit `KeyError` after affordability;
- returned result identity: the engine stores and returns one shared result object.

The unchanged source gate must measure the exact helper. This small transaction alone does not close the engine complexity obligation.

## Fallback only: gathering Drop

The fallback seam is `runtime/runtime_actions_carried_overlay.py:784-790`: a pure transformation from `inv_after` plus already-filtered gains to drained inventory. The caller retains the conditional, assignment, save, handler call, Winter Storage rollback, cadence rollback, and return order.

The settled authority is the accepted Keep settlement handoff, which expressly leaves Drop, save, rollback, and wrapper behavior with the caller. The broader historical `_settle_gathering_keep_drop` candidate is integration-blocked: preserved static evidence measured CCN 13 and cognitive 17 against the fixed cognitive limit of 15. It remains fallback evidence only.
