# Overnight fresh-eyes audit — 2026-07-16

## Objective

Find and fix concrete defects and implementation imperfections across the AnkiScape repository before 09:00 America/Los_Angeles. Codex owns reproduction, implementation, tests, commits, and final decisions. Reviewer selection uses Claude Code's live `/usage` reading: Fable remains available while `Current week (Fable)` is safely below 30%, then Opus takes over. Workflow token telemetry is not treated as quota percentage.

## Fixed critic instruction

> Once again, check over everything again with fresh eyes looking for any blunders, mistakes, errors, oversights, omissions, problems, misconceptions, bugs, etc. Be SUPER thorough and meticulous!

## Inner loop

1. Select the next unreviewed scope from the coverage ledger.
2. Ask one independent Claude reviewer to inspect only that scope and report exact files, lines, failure mechanisms, and omitted areas. The reviewer may not edit, commit, or declare broad correctness.
3. Codex reproduces each candidate against current code and runtime.
4. Codex fixes only confirmed defects, with one attributable hypothesis per batch.
5. Run targeted unit, integration, end-to-end, and relevant offscreen Qt tests. Add regression tests that fail before the fix and protect real behavior.
6. Run the invariant holdouts listed below. Revert or repair any candidate that fails them.
7. Commit an accepted batch on `codex/overnight-fresh-eyes-2026-07-16`, then append evidence here and update the JSON state.

## Verifier and holdouts

- Targeted behavioral reproduction and regression tests.
- `python3 tools/worktree_guard.py audit` before and after worktree-sensitive operations.
- `/opt/homebrew/bin/python3 tools/audit_test_quality.py` after test changes.
- `python3 run_tests.py` at checkpoints and closure.
- Real offscreen Qt discovery for UI/runtime changes.
- `python3 tools/audit_item_reachability.py --json` for item/economy changes.
- `python3 -m compileall` and `git diff --check` before every accepted commit.
- Review undo, direct-action undo, deterministic RNG ordering, wall-clock prohibition, flat save migration, target-local carried inventory, and source provenance remain fixed invariants.

## Outer loop trigger

Do not change the search mechanism initially. After three consecutive independent passes with no material finding, switch from module-oriented review to a seam portfolio: producer/consumer item identity, persisted-state writer/reader symmetry, UI-selector/runtime-gate reachability, death/undo/rollback consequences, source-contract/code drift, and test-oracle blind spots. After two outer-loop passes with no material finding, stop for convergence even if the deadline has not arrived.

## Rollback and authority

Every accepted change is checkpointed in a normal commit. Failed candidates are reverted with a forward patch, never destructive Git commands. The loop may edit and commit only this worktree. It may not merge into `main`, push, publish, deploy, modify credentials, install dependencies, or expand product scope. Creative design choices that are not already settled go into the ranked morning design-gap file and remain unimplemented.

## Coverage ledger

| Pass | Scope | Reviewer | Candidates | Confirmed | Commit | Verification |
|---:|---|---|---:|---:|---|---|
| 1 | Agility, Thieving, Farming, Magic runtime seams | Fable | 14 | 9 | `01ef8d9` | 230 focused; 1 real offscreen Qt; 1,252 full; reachability; zero hard test-quality issues |
| 2 | Crafting and Magic item identity, registry, assets, reachability | Opus | 5 | 5 | `b263c15` | 252 focused; 1,258 full; reachability counts unchanged; zero hard test-quality issues |
| 3 | Lantern and lamp-oil state graph across Crafting, Smithing, Firemaking, shops, equipment, quests, assets, and saves | Fable pre-implementation; Codex verification | 7 | 7 | `37b46c5` | 270 focused; 179 real offscreen Qt; 1,265 full; 14 fewer cascade orphans; zero hard test-quality issues |

## Accepted fixes

- The Pit remains unlocked for its six-review active session, while malformed persisted session mappings are removed and cannot bypass the invitation.
- Fatal Agility failures deactivate training and report the established grave or auto-eat consequence.
- Thieving's runtime multi-pick roll now matches the inclusive `random(7)` source denominator of eight outcomes.
- Farming applies its settled watered-disease multiplier and exposes the existing Farming-spell patch selector in the Magic UI.
- Dragonstone enchant inputs use the canonical Crafting item identities.
- Thieving target metadata presents target-specific and wall-safe failure-damage ranges.
- Furnace Crafting now produces canonical unstrung amulet identities, while manual stringing and String Jewellery consume those identities and produce the separately registered strung equipment items. Existing saves keep their ambiguous legacy amulets as strung equipment, preserving the capability they already had.
- The seven unstrung and seven strung amulet assets now use distinct source images, and the asset fetcher can refresh a bounded named subset without re-downloading the full Crafting catalog.
- Lanterns now retain exact unfinished, empty, fuelled-unlit, and lit identities through Smithing, Crafting, one-review lamp-oil preparation, lighting, extinguishing, Thieving drops, shops, equipment, and quest gates.
- Lamp-oil preparation flattens swamp-tar distillation and filling into one explicit zero-XP review without using wall-clock time; candle insertion remains its own zero-XP review.
- Twenty-two distinct state sprites replace shared placeholders, and the generated-data checks cover both Mining helmet states plus the bullseye Smithing output.
- Legacy collapsed inventory names, equipped Mining helmets, persisted Miltog stock, and shop rollback events migrate to exact state names. Intrinsically ambiguous old Oil lamp keys resolve to the empty state so the complete preparation chain remains available.

## Rejected candidates

- A future change to Thieving stall respawn data could invalidate persisted cadence credit. Current shipped data does not do so, and save migration is required only with such a data change; no speculative runtime catch was added.
- Dragonstone jewellery inputs remain intentionally acquisition-blocked, as already recorded in Crafting data; this is not a newly unreachable identity.
- Legacy `Gold amulet`-style save keys were not migrated to `(u)` keys. Before this repair those keys could already be equipped and enchanted, so treating them as strung preserves player capability; only newly smelted amulets use the unstrung identities.
- Fable's claim that cave-goblin pickpocketing drops unfinished bullseye item 4544 was rejected: Darkan's exact `pp_cavegoblin.json` row uses fuelled-unlit item 4548. The implemented Thieving key follows that exact ID.
- A full regeneration of shop and equipment snapshots was rejected because the local external source trees had unrelated drift. The pinned generated snapshots received only the exact lantern-state corrections, and their existing coverage-count tests remain unchanged.

## Queued confirmed defects

- Three generated quest gates still require the literal pseudo-item `Light sources`. The next pass must replace those parser artifacts with source-appropriate exact lit-state alternatives for Tears of Guthix, Rag and Bone Man, and Land of the Goblins.

## Reviewer budget and availability

- Live Claude `/usage` reached 30% for Fable after the pass-3 review attempt, so no further Fable calls are permitted in this overnight run.
- The post-implementation Fable review exhausted the current Claude session before returning a verdict. An immediate Opus fallback was also blocked by the same account-wide session window and made no tool calls. Codex therefore accepted pass 3 only after its own full diff audit, targeted checks, full Python suite, real offscreen Qt suite, reachability comparison, compilation, diff check, and worktree audit. Opus resumes after the session reset.

## Closure

Pending.
