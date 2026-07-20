# Farming item-reachability route correction — 2026-07-20

## Finding

`tools/audit_item_reachability.py` treated live Farming produce as if it had no
producer. The runtime already grows and harvests those items, but the audit
graph omitted `FARMING_CROPS` and `SAPLING_RECIPES`. This falsely classified
ordinary outputs such as Sweetcorn, Strawberry, Watermelon, Jangerberries,
Morchella mushroom, Papaya fruit, and tree roots as root acquisition gaps.

## Correction

The audit now registers three existing runtime route families:

- seed, Plant pot, Gardening trowel, and either Watering-can state produce the
  seedling and matured sapling;
- the crop's seed or sapling plus its live planting and harvest tools produce
  its ordinary harvest item; and
- a live tree crop plus a usable hatchet and Spade produces its root item when
  the stump is cleared.

Only crops whose existing `CropDefinition.runnable` property is true enter the
graph. This is a quantity-free acquisition audit, so it records whether a route
exists without claiming a yield, growth rate, or success probability.

## Result

The deterministic report changes from 1,268 actions, 1,889 reachable items,
284 orphan inputs, and 302 blocked actions to:

- 1,342 actions;
- 1,982 reachable items;
- 253 orphan inputs: 98 root and 155 cascade; and
- 268 blocked actions.

Focused regression coverage pins representative allotment, bush, mushroom,
sapling, fruit, and tree-root routes. No gameplay state, UI, source value, or
owner-settled design changed.
