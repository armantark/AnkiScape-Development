# Combat unequip transaction

Base: `5888f215ee1bd6fb6cdc3e003a7dfe57a2f4c56a`. This plan is immutable before implementation. P13 owns only this source slice. The parent owns runtime authorization, mirror state, review, commit, and promotion.

## Contract

Extract the existing enemy unequip transaction into one private helper in `logic_pure/logic_pure_combat_engine.py`. Inputs are the burst-owned working player data and target ID. Return the updated player data and the existing event mapping. Preserve weapon-first then sorted-slot selection, exact bank and carried-pack arithmetic, empty-item event behavior, equipment-instance synchronization after the ordinary views are written, and rebinding of the synchronized result.

Keep enemy attack scheduling, attack selection, RNG, event aggregation, loop interruption, and encounter persistence in the caller. Do not extend the helper into teleport, attack selection, condition mechanics, UI, or public interfaces.

## Evidence and acceptance

The full baseline engine is retained as `baseline-engine.py.gz`; `initial-pins.json` binds its decoded hash and the installed static gate and measuring tools. Neither may change.

Use a few whole-burst checks for real weapon removal, deterministic sorted fallback, no removable equipment, and a condition-bearing item. Cover both cadences and resumed encounter state without invented compound mechanics. Prepare a whole-engine differential comparison of complete returned values, supplied-input nonmutation, RNG draws and generator state, with explicit assertions that each intended route occurred.

Prepare negative source and optimized-interpreter guards that stop before product imports. Static preparation may run only AST, layout, installed metric ratchets, and documentation checks. Retain the explicit source inventory, whole-file restorable product diff, raw static evidence, and final hashes. Keep product/test/probe and operational-metadata review packets separate and at most 25,000 bytes each. No runtime, product imports, test discovery, remote action, mirror synchronization, commit, or push is authorized in this slice.
