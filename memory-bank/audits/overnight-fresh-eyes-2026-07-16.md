# Overnight fresh-eyes audit — 2026-07-16

## Objective

Find and fix concrete defects and implementation imperfections across the AnkiScape repository before 09:00 America/Los_Angeles. Codex owns reproduction, implementation, tests, commits, and final decisions. Fable was limited to one read-only pass after that pass consumed 250,236 generated tokens; Opus is the reviewer for every later pass to protect the user's shared Fable quota.

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

## Accepted fixes

- The Pit remains unlocked for its six-review active session, while malformed persisted session mappings are removed and cannot bypass the invitation.
- Fatal Agility failures deactivate training and report the established grave or auto-eat consequence.
- Thieving's runtime multi-pick roll now matches the inclusive `random(7)` source denominator of eight outcomes.
- Farming applies its settled watered-disease multiplier and exposes the existing Farming-spell patch selector in the Magic UI.
- Dragonstone enchant inputs use the canonical Crafting item identities.
- Thieving target metadata presents target-specific and wall-safe failure-damage ranges.

## Rejected candidates

- A future change to Thieving stall respawn data could invalidate persisted cadence credit. Current shipped data does not do so, and save migration is required only with such a data change; no speculative runtime catch was added.
- Dragonstone jewellery inputs remain intentionally acquisition-blocked, as already recorded in Crafting data; this is not a newly unreachable identity.

## Queued confirmed defect

- Crafting V1 gives unstrung and strung amulets the same item key. Both manual stringing and String Jewellery can therefore award repeatable Crafting XP from the same items. The next producer/consumer-identity pass must split those identities and migrate the affected recipes, spells, registry rows, tests, and assets as one atomic change.

## Closure

Pending.
