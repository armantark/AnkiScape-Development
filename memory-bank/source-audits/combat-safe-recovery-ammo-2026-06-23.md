# Combat Safe Recovery Ammo Refill Audit - 2026-06-23

## Scope

This slice closes the safe-boundary loadout parity gap for Ranged Combat.
Successful noncombat reviews already applied one rollback-safe Combat recovery
packet and refilled food plus Magic runes. Ranged ammo now follows the same safe
boundary rule.

## Implemented Contract

- `apply_safe_combat_recovery_pure()` still applies one recovery packet per
  successful noncombat review.
- If the current Combat style is Ranged, safe recovery resolves the equipped
  Ranged weapon by exact `COMBAT_RANGED_WEAPON_DATA` name and refills compatible
  ammo from inventory into `combat_supply_loadout["ammo"]`.
- The existing no-mid-fight rule is unchanged: active Combat bursts still do not
  refill ammo from inventory mid-encounter.
- Undo remains safe because the existing review snapshot captures both inventory
  and `combat_supply_loadout`.

## Tests

- `tests.test_combat_logic.CombatLogicTest.test_safe_recovery_refills_ranged_ammo_at_safe_boundary`
- `tests.test_integration_smoke.TestIntegrationSmoke.test_successful_noncombat_review_applies_one_safe_combat_recovery_and_undo_restores_it`

## Deferred

- Broader ammo/equipment support beyond Shortbow plus Bronze arrows remains
  future Combat equipment work.
- Arrow recovery after shots remains deferred.
