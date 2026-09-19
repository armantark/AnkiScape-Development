# One-time papercut cleanup

## Contract

The owner requested all papercuts fixed, an account of architectural obstacles
in this run and the Union Alpha trial, and a file for a later grill with Fable.
The implementation goal stays paused. No automatic restart or remote push is
authorized.

Baseline: main `7f736d5c63ca0d301b1789798e75fa2737435f4c`.
The incident log has 2467 lines at this baseline. Preserve its exact text.

Inventory every incident in the main log and all tracked pending papercut logs.
Group duplicates by cause. Verify each proposed repair against current source.
Use these dispositions: fixed-before, repair-now, operator-error,
external-blocker, design-decision, paused-feature. Every disposition requires
evidence. A historical record alone does not establish a current defect.

## Ownership and outputs

Root owns this worktree, the final ledger, all shared memory-bank files,
the remote test mirror, commits, integration and promotion. Read-only audit
leaves own only their named files under /tmp. They must not edit any checkout.

1. audit_early: incident starts on lines 1-825. Write
   /tmp/ankiscape-papercuts-early-2026-09-18.json.
2. audit_middle: incident starts on lines 826-1650. Write
   /tmp/ankiscape-papercuts-middle-2026-09-18.json.
3. audit_recent: incident starts on lines 1651-2467 and tracked pending logs.
   Write /tmp/ankiscape-papercuts-recent-2026-09-18.json.
4. Root: verify Union Alpha evidence, current maintenance tools and acceptance
   records; integrate the inventory; select and assign concrete repairs.

Each audit output is a JSON object with baseline, range, groups and uncovered.
Each group has id, incident_lines, disposition, cause, evidence, repair and
architecture. Evidence names actual source paths or verified commits.
Use one group per cause, not per date. Retain uncertain cases explicitly.
Do not label an unverified current behavior fixed.

## Acceptance

CHECK: each incident start belongs to exactly one group.
EXPECT: no gaps or duplicate assignments after root reconciliation.
CHECK: inspect current source for each actionable group.
EXPECT: a real remaining defect, a verified existing fix, or a named constraint.
CHECK: run regression and failure canaries for each repair, then required full
source and merged-tree promotion gates on the MacBook Pro.
EXPECT: all required checks pass, with unchanged safety thresholds and pins.

Do not advance the paused gameplay or module-extraction queue. Do not apply
UI design decisions, install tools, alter test thresholds, or bypass hooks.
Pure/static tooling probes may run locally. Product execution belongs on the
MacBook Pro. Root is the only remote operator.

The final report must account for every incident and state any work that
cannot close without an external fix or owner decision. The Fable handoff must
state decisions made, unresolved choices, source evidence and a complete
grilling prompt. No Fable call is part of this request.

## Events

- 2026-09-18: Main is clean. The existing goal is paused.
- 2026-09-18: Root returned the completed, clean, merged Barcrawl lease.
  The cleanup uses pool 4, lease 337a792ec885efd93ec3fce660284b1a.

- 2026-09-18: Root verified current worktree release can detach/return while a
  promotion marker names that checkout. It also allocates before duplicate-branch
  detection. The prior proposal is now authorized by this one-time cleanup.
- Implementation ownership will use disjoint files in the root maintenance
  worktree. Root is the only Git/index writer. Agents return patches and static
  evidence; root commits after all writers stop. This avoids additional leases
  while the release guard itself needs repair.

- Root owns tools/run_remote_tests.py and tests/test_remote_test_host.py. Add
  an explicit focused selection with an exact expected test count and zero
  skips. Leave full-lane commands, floors, locking and durable-run recovery
  unchanged. Synthetic tests must reject wrong counts, skips, missing summary
  and incomplete arguments before a real focused run is accepted.

- Asset author owns fetch_assets, fetch_hunter_assets, trim_icons and their
  named tests, the Hunter shared-image mapping, and skipped-source labels in
  seven related asset fetchers. Product paths and exports must stay identical.
- Quality author owns audit_test_quality and its tests. Imported TestCase
  ancestry must resolve from source; unknown classes must still fail closed.
- Root owns module-surface failure reporting and promotion lane diagnostics.
  All digest pins and failure conditions remain unchanged.
- Root verified early inventory coverage: 796 incidents, each once. Root
  verified middle coverage: 787 incidents, each once. Author classification
  remains subject to root source review.
- Focused-runner inert canaries rejected the baseline and passed the candidate.
  Its complete local tooling suite passed 19 tests; the real MacBook focused
  plain run passed 19 tests with zero skips.

- The owner supplied a simplification principle: use lessons from traces so a
  later task needs fewer steps and less supervision. Prefer shared tools and
  correct defaults over additional caller instructions. This does not authorize
  a goal restart, remote push, new skill, or weaker acceptance rule.
- Root combined the three source audits into inventory.json. Its checker
  verifies 2333 incident records across 17 frozen source files with no missing,
  extra, or duplicate assignments. Multiple logs can record the same event.
- Guard author owns worktree_guard.py, minimal locking.py additions, and
  worktree/promotion guard tests. Root remains the sole Git/index writer.
- 2026-09-19: Continuation reconciled the clean canonical main and paused goal.
  Previous authors have stopped. A quality repair leaf owns only audit_test_quality
  and its tests. A guard verification leaf has read-only access and owns only
  /tmp/ankiscape-papercut-guard-verification-2026-09-19.md. Root owns all other
  files, review resolution, remote execution, the index and promotion.
