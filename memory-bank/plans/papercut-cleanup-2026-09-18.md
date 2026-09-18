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
