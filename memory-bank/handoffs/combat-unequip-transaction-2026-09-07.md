# Enemy unequip preparation handoff

## Goal

Finish the parent review and the authorized runtime checks for the enemy unequip extraction. P13 starts at `5888f215ee1bd6fb6cdc3e003a7dfe57a2f4c56a`.

## Context

This handoff contains the static preparation and the retained result of the
parent-executed runtime checks. No full branch gate, exact merged-tree gate,
native program acceptance, commit, merge, or push ran.

The parent owns the shared MacBook mirror, commit, merge, and native program
acceptance.

## Source boundary

The new private helper owns only the existing unequip transaction and its event mapping. It preserves these behaviors:

- Select the weapon first.
- Otherwise, select the first nonempty slot in sorted order.
- Add the item to the bank and the target carried pack.
- Synchronize the equipment instance after the ordinary views change.
- Return an empty unequip event when no item can move.

The caller still owns the enemy schedule, attack selection, random number generation, event append, loop break, and encounter persistence. The extraction does not change teleport, attack, user interface, or period data.

The frozen baseline engine has SHA-256 `486a532d00d4e5693894b77a022ef83a32e03f55e841c2ff92ab12fc7e9ad2d4`. The candidate engine has SHA-256 `1ef64d445983f5512a27d298aa22da81479f9b1be9d2132939fde57b9485be3a`.

The source inventory has 877 entries. Its SHA-256 is `6144b3ffe002b2c41ae1447f5bd6c8fcdfa6a2fcec82f5244f42a3c7c6ff8e17`.

## Static verification

The installed complexity and layout no-growth ratchets passed. The candidate engine has 3,009 lines, and the baseline has 3,010 lines.

The engine exceeds the global 1,000-line limit. The static pass confirms no growth; it does not claim threshold compliance.

The structural proof confirms all of these facts:

- All other module definitions and statements are unchanged.
- The moved transaction abstract syntax tree is equal to the baseline branch.
- The event mapping abstract syntax tree is equal to the baseline mapping.
- The helper has one call site and one equipment-instance synchronization call.
- The caller keeps schedule order, attack selection, event append, and loop break.
- The helper does not own random number generation or loop-control state.

These checks are static evidence. They are not behavior evidence.

## Required verification

Review `product-review.diff` and `operational-review.diff` first. Then run the guard before all product imports.

The focused selection has four test methods. Its three new methods contain four scenarios, and the existing regression adds the fifth scenario.

The comparison has four named labels across live and legacy cadence.

The comparison records complete returned values, input immutability, ordered random draws, and the captured generator state. Each case also has a route assertion.

The fixed 100-draw prefix means these cases do not advance the underlying pseudo-random generator. Do not treat that state trace as independent seeded-state coverage.

The completed runtime used this verification contract in each authorized host
lane:

```sh
python3 -B tools/combat/check_enemy_unequip_guards.py --candidate-sha256 1ef64d445983f5512a27d298aa22da81479f9b1be9d2132939fde57b9485be3a --inventory-sha256 6144b3ffe002b2c41ae1447f5bd6c8fcdfa6a2fcec82f5244f42a3c7c6ff8e17 > /tmp/ankiscape-enemy-unequip-guards-corrected-2026-09-07.json
python3 -B run_tests.py --verbosity 2 EnemyUnequipTransactionTest ChaosElementalTests.test_unequip_special_moves_weapon_to_carried_pack_and_preserves_encounter
python3 -B tools/combat/compare_enemy_unequip_transaction.py --baseline memory-bank/evidence/combat-unequip-transaction-2026-09-07/baseline-engine.py.gz --candidate-sha256 1ef64d445983f5512a27d298aa22da81479f9b1be9d2132939fde57b9485be3a --inventory memory-bank/evidence/combat-unequip-transaction-2026-09-07/source-inventory.json.gz --inventory-sha256 6144b3ffe002b2c41ae1447f5bd6c8fcdfa6a2fcec82f5244f42a3c7c6ff8e17 --output /tmp/ankiscape-enemy-unequip-comparison-2026-09-07.json
```

Require all seven guard cases to pass before product imports. The guard also refuses `PYTHONOPTIMIZE=0` because its source pins use assertions.

Require unittest to report four methods and zero skips. The passing subtest does not add another method to that count.

Require these comparison labels: `weapon:live-resume`, `sorted-fallback:legacy`, `empty:legacy`, and `condition:live-resume`. Each equality flag and route flag must be true.

Review the complete values and random state in each retained lane. Confirm the bank, carried pack, condition, and encounter observations.

Preserve the raw reports and bind them to this source inventory. Any source correction requires a new source freeze and new runtime evidence.

## Parent runtime result

The parent completed the authorized four-job run in the plain and Qt host
lanes. All four jobs exited zero. Each focused lane passed four unittest methods
with zero skips in 0.009 seconds. The selection covers five scenario cases.

Both comparison lanes passed the four ordered labels
`weapon:live-resume`, `sorted-fallback:legacy`, `empty:legacy`, and
`condition:live-resume`. Complete returned-value pickle bytes, random draws,
captured random state, input immutability, and route assertions matched.

The retained runtime evidence contains all 37 original files from
`/tmp/ankiscape-enemy-unequip-runtime-2026-09-07` plus the driver console log.
The 38 deterministic gzip archives decode to 6,859,348 original bytes. Their
decoded and stored SHA-256 hashes are recorded in
`memory-bank/evidence/combat-unequip-transaction-2026-09-07/runtime/index.json`.
The runtime index has SHA-256
`fcb3c89c10b90d5b3e64ec0b2967fa3f955aed5de12bc2aa620ac28d78769df0`.

The runtime evidence remains bound to the 877-entry source inventory with
SHA-256 `6144b3ffe002b2c41ae1447f5bd6c8fcdfa6a2fcec82f5244f42a3c7c6ff8e17`.
The product and operational reviews are closed.

`manifest.json`, `runtime-preparation.json`, and `review-packets.json` remain
frozen preparation records. Their pre-execution status fields are historical;
the runtime index and this handoff are the current authority for the completed
focused runtime.

## Open work

The parent must complete these items:

1. Run the normal commit hooks and full branch gate.
2. Run the exact merged-tree gate.
3. Complete native program acceptance.
4. Obtain commit authorization, then commit and merge the accepted source.
