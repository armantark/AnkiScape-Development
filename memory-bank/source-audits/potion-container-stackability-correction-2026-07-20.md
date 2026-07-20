# Potion-container stackability correction — 2026-07-20

## Finding

`potion_data.potion_items_as_dict()` omitted explicit stackability for empty
vials, empty potion flasks, ordinary potion doses, and potion-flask doses.
`item_registry` therefore applied its permissive legacy default and described
all of them as stackable.

That contradicted both live behavior and the existing source-backed model:

- `item_values.STACKABLE_ITEM_NAMES` excludes every tested vial/flask identity
  from the generated Darkan cache stackable set.
- `logic_pure._combat_supply_slots_used()` already treats potion doses as
  unstackable supplies that cost one carried slot per item.
- The owner-settled carried-inventory contract requires stackable and
  non-stackable quantities to remain distinct in the backend.

## Correction

Every item emitted by `potion_items_as_dict()` now declares
`stackable=False`. This aligns canonical item metadata with the cache-derived
runtime set and the existing carried-slot behavior. It does not change potion
effects, dose transitions, decanting, inventory quantities, UI, or save state.

## Verification

The focused registry regression covers both empty containers, vial dose
endpoints, and flask dose endpoints across ordinary stat and Prayer families.
Focused registry, cache-value, inventory, Combat, and Shop verification passes
416 tests. Complete non-Qt discovery passes all 1,910 tests with 251 expected
environment skips. Documentation, test-quality, compilation, diff, and
worktree-safety audits pass. No owner design gap surfaced.
