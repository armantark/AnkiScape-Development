# Next cleanup boundary: Dream transaction

## Status and authority

This is read-only selection evidence from main `0d606cfd3e79fa660223a5b0a00974c9098a9447`. It does not authorize implementation, a test run, a commit, or acceptance.

The priority follows the largest-first cleanup programme in ruling 47. The engine is the largest relevant exposed function. Rule 48 requires a real responsibility seam, rather than a line-range split. Rule 53 forbids a split part from depending on the root module's globals or other reverse dependency. The fixed gate continues to govern a changed helper independently.

Current source-only measurement command:

```sh
/Users/ArmanTarkhanian1/.local/bin/lizard --csv logic_pure/logic_pure_combat_engine.py | rg 'apply_combat_burst_pure@'
```

Its raw record begins `1213,299,6303,11,1276`: **NLOC is 1213; Lizard CCN is 299**. A separate source-only Complexipy run reports cognitive complexity 561. These are observations of the current function, not a predicted metric for a future helper.

## Current boundary

The Dream block is `logic_pure/logic_pure_combat_engine.py:1080-1100` inside `apply_combat_burst_pure`.

Before the transaction, the engine:

1. Copies and sanitizes player state, prepares a target-local carried view, and applies the pinned preset or target overrides.
2. Rejects a locked magic preset at lines 1246-1248.
3. Unconditionally reads maximum LP at line 1251.
4. Evaluates the Dream flag, absence of an active encounter, and current-LP-below-maximum eligibility at lines 1252-1256.
5. Calculates the effective Dream rune cost at line 1257.

Only after those reads does the existing code perform the transaction: check every rune balance, copy and debit inventory in cost-mapping iteration order, write inventory, calculate healing, write LP, write Magic XP, construct the result mapping, write `combat_last_result`, and early-return `(data, True, result)`.

## Proposed ownership contract

The candidate helper has exactly three inputs:

```text
_apply_dream_transaction(data, dream_cost, max_lp_for_dream) -> result | None
```

The engine retains all prior ownership and timing: unconditional maximum-LP read; flag, active-encounter, and current-LP eligibility; effective-rune-cost calculation; `combat_last_result`; and the exact early `(data, True, result)` return.

The helper owns only the transaction after those caller-owned conditions are satisfied:

1. Read the current inventory and verify every already-calculated rune cost is affordable.
2. Return `None` without a mutation when it is not affordable.
3. Copy the inventory and debit each rune in the existing mapping order.
4. Write that inventory to `data`.
5. Calculate the capped 50-LP heal using the caller-supplied maximum; write LP, then write the 82.0 Magic XP increase.
6. Construct and return the same result mapping, including `runes_used` as a copy of the caller-supplied cost.

After a non-`None` result, the engine writes `combat_last_result` and immediately returns the unchanged outer tuple. No helper decides whether Dream is eligible, recomputes max LP or cost, chooses a spellbook, sees combat state through an engine import, or alters later combat setup.

## Dependency direction

The intended edge is `logic_pure_combat_engine -> logic_pure_combat_magic`. The magic module may use its existing state sanitizer import for non-negative numeric handling. It must not import `combat_has_active_encounter_pure`, `combat_max_lifepoints_pure`, or any other engine function: the caller supplies the two derived values it needs. The P8 draft magic module already imports `_non_negative_int` from `logic_pure_state` and has no engine import, so this three-input shape fits its current lower-layer direction.

## Smallest behavioral proof to require before acceptance

This is a proof plan, not a completed test claim. A focused pure comparison of the whole `apply_combat_burst_pure` before and after the extraction should pin:

- Dream disabled, active encounter, and full LP: maximum LP is still read at the existing point; no rune-cost calculation, debit, XP, result, or early return occurs.
- Eligible but insufficient runes: cost is calculated before affordability, no state mutation occurs, and normal target validation continues.
- Eligible with exactly sufficient runes: source mapping order drives debits; inventory write precedes LP, LP precedes Magic XP, Magic XP precedes result construction, and `combat_last_result` remains immediately before the same early tuple.
- Eligible with only partial healing room: the heal is capped at 50 and by the caller-computed maximum; runes and 82.0 Magic XP still follow the same transaction.

The source gate must then measure the exact changed helper under the unchanged limits. This packet makes no prediction that it passes.

## Fallback only: gathering Drop

If Dream is not admitted, the fallback is the small pure transformation at `runtime/runtime_actions_carried_overlay.py:784-790`: take `inv_after` plus the already-filtered ordinary gains and return the inventory with only those gains drained. The caller must retain the `elif gains`, `player_data["inventory"]` assignment, save, handler call, Winter Storage rollback, cadence rollback, and return ordering.

This is not the earlier combined gathering-settlement candidate. That candidate combined gain derivation, Keep, Drop, and notification in `_settle_gathering_keep_drop`; preserved static evidence measured CCN 13 and cognitive 17, which exceeds the fixed cognitive limit of 15. It is integration-blocked in `memory-bank/goal-priority-matrix.md`. The accepted Keep settlement handoff explicitly leaves Drop handling, saves, rollback, and wrapper behavior with the caller. Those records settle the fallback boundary; they do not authorize it.
