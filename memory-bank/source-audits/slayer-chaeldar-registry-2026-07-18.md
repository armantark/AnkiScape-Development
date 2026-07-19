# Slayer Chaeldar hidden-registry activation — 2026-07-18

Status: **implemented and verified; master remains hidden**.
Cutoff: `2012-11-20T00:00:00Z`.

## Result

The complete source-reconciled Chaeldar ordinary pool is now executable data:
34 master-specific rows, a provisional 388-point denominator, Combat 70, Lost
City access, and every sourced count range and player gate. It is deliberately
not a live assignment source. `runtime_enabled=False` prevents player
selection and weight renormalization while Combat dependencies remain absent.

The stable family registry gained the seventeen identities that were not
already shared with Turael, Mazchna, or Vannaka. Future Combat rows now have
one declared target identity and one explicit obligation vocabulary:

- dragonfire for Blue and Bronze dragons;
- light and protective equipment for Cave horrors;
- protective equipment and disease damage for Fever spiders;
- neem-oil interaction for Fungal magi, Grifolapines, and Grifolaroos;
- a Rock-hammer finisher for Gargoyles;
- assignment-only attackability and poison for Jungle strykewyrms;
- restricted weapons for Kurasks and Vyrewatch;
- fungicide finishing for Mutated zygomites; and
- crystal-chime vulnerability for Warped tortoises.

These keys are completeness declarations, not synthetic mechanics. Readiness
will remain blocked until the matching Combat target supplies positive Slayer
XP and every declared feature.

## Exact current readiness

The generated readiness ledger originally reported **19/34** families ready.
The Fire giant and Blue dragon family closures recorded in
`slayer-fire-giant-combat-2026-07-18.md` and
`slayer-blue-dragon-family-combat-2026-07-18.md` advance the live ledger to
**21/34**. The following thirteen identities remain absent from
`COMBAT_ENEMY_DATA` and each produces one
stable `combat_target` blocker:

1. Bronze dragons
2. Cave horrors
3. Dagannoths
4. Elves
5. Fever spiders
6. Fungal magi
7. Grifolapines
8. Grifolaroos
9. Jungle strykewyrms
10. Kurasks
11. Trolls
12. Vyrewatch
13. Warped tortoises

Gargoyles and both Mutated-zygomite rows were already complete and now
certify their families through the shared finisher engine. The twenty-one ready
families do not make Chaeldar selectable: the runtime registry excludes all
hidden masters, and catalog integrity rejects a hidden pool only after it is
fully certified.

## Quest and route boundaries

The registry reuses exact current quest IDs for Lost City, Cabin Fever,
Regicide, Legends' Quest, The Branches of Darkmeyer, and The Path of
Glouphrie. Fever spiders deliberately do **not** require Rum Deal completion.
The source proves Braindeath Island access after the quest is started but does
not close the exact assignment-time stage predicate, while the current family
gate schema represents completion only. Encoding completion would be a false
restriction. The Combat target remains absent, so no partial route is exposed.

Brine rats keep their existing `partial_quest_access` completeness feature for
the same reason: Olaf's Quest stage access belongs to the Darkan quest
permission seam, not a fabricated completion rule in this registry slice.

## Verification

- Source authority:
  `source-audits/slayer-chaeldar-pool-2026-07-17.md`.
- Registry implementation: `slayer_data.py`.
- Derived completeness engine: `slayer_readiness.py`.
- Regression contract: `tests/test_slayer_logic.py`.
- Focused Slayer/Combat/metadata run: 89 tests passed.
- Full non-Qt discovery: 1,663 tests passed with 215 declared Qt-environment
  skips.
- Full real offscreen Qt discovery: all 1,663 tests passed with no skips,
  failures, or errors.
- Test-quality audit: zero hard issues across 73 files; the four reported
  structural-clone groups are the unchanged review-only baseline.
- Documentation audit: 336 Markdown and 345 HTML files passed.
- Reachability remained at the established 1,253-action, 1,851-reachable,
  293-orphan, 320-blocked baseline; this data-only slice adds no items.
- Catalog integrity: no issues.
- Compilation and diff checks: passed.
- Worktree layout: safe.

Codex Workflows run `a82b5794-6565-4243-bd95-fef7076daa80` attempted two
independent read-only checks on build
`0.1.0+codex.20260718215406`. Both jobs failed before session creation with
zero tokens and zero tool calls: `provider emitted no startup event within
30s`. Their stderr reported a stale model-cache schema missing
`supports_reasoning_summaries` and model-refresh child-process timeouts. No
review conclusion was produced or used; the primary independently reproduced
the complete ledger and blocker set.

## Design-gap result

No owner-facing design decision emerged. Remaining work is source harvesting,
Combat implementation, asset acquisition, and quest-permission integration.
The hidden master must not be exposed until the generated ledger reaches
34/34.
