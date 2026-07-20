# Fist of Guthix equipment-instance implementation checkpoint

Date: `2026-07-20`

Status: **verified substrate; FoG activity remains in progress.**

Authority remains
`source-audits/fist-of-guthix-horizontal-mvp-harvest-2026-07-20.md`.
This checkpoint implements the generic per-copy condition prerequisite named by
that audit without claiming the match, shop, or UI is live yet.

## Implemented invariant

`equipment_instances` is the durable condition owner for equipment families
whose individual non-stackable copies can differ. The ordinary flat Bank counts,
worn slot names, grave item names, and Death's Office item names remain the
player-facing holders. A stable `equipment-N` record links one copy to its
family, exact hidden condition, canonical condition identity, and current holder.

The sanitizer preserves already-valid holder assignments before reconciling a
move. This matters when two `Combat hood 100` copies are within the same visible
20% band but have different exact ticks: moving the worn one to a grave must not
replace it with the healthier Bank copy. Old saves without instance records gain
one conservative record per extant condition item, derived from the visible
condition identity.

## Live consumers

- `Combat hood 100/80/60/40/20/0` uses the sourced 90,000-Combat-tick lifetime.
  Only elapsed Combat ticks reduce the worn instance; names change at the exact
  20% condition bands.
- `Bronze gauntlets` retains full charge during ordinary use and becomes
  `Worn-out bronze gauntlets` on unsafe death. A safe-activity path does not call
  the unsafe-death reducer.
- Equip, unequip, PVM death, Wilderness death, grave recovery, Death's Office
  recovery, and Bank Discard X reconcile the instance holder. Review undo and
  direct-action undo remain whole-player snapshots, so the ledger rolls back
  atomically with the existing state.

The generated equipment catalog now includes the eight period item identities
from local rev-667 `items.yml`, with the Combat hood's exact 20 Defence and 10
Magic requirements. Regeneration also surfaced six already-eligible equipment
rows from existing shop/drop/recipe sources that the checked-in generated file
had not yet incorporated; no new acquisition route was invented.

## Verification

- `python3 -m unittest tests.test_equipment_instance_logic tests.test_equipment_data tests.test_logic tests.test_combat_logic tests.test_storage_pure tests.test_integration_smoke`
  — `626` tests, all pass.
- Focused integration proves equip/unequip movement and exact Discard X undo.
- Focused Combat coverage proves six-tick degradation, unsafe-death discharge,
  and same-instance grave recovery.

Remaining FoG work: Reggie buy/recharge/uncharge actions, two-round match engine,
runtime/cadence/undo wiring, Activities/HUD UI, assets, taste review, real-Anki
verification, and full closure gates.
