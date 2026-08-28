# Goal paused, canonical main moved during active slice work

- Blocked: Promotion and integration of the native tab-overflow slice stopped when canonical `main` moved from expected `9ca56ff199e27a9458a94f85af09787baa988618` to `60d709847e378cca2f8d86c5cfc0ae50c72ef65c` during active work.
- Tried: The orchestrator stopped both active agents, inspected the new one-line Memory Bank commit, and made no repair or reconciliation attempt. Candidate branch `goal/native-tab-overflow` remains unmerged at `1eedceb40dbdc8342ae71fa030605915daeafc09`; its tests were not run.
- Unblock: The owner explicitly confirms `60d709847e378cca2f8d86c5cfc0ae50c72ef65c` as the new canonical baseline and asks to resume this goal.
- Paused: 2026-08-28T10:26:05-07:00

## Goal (restore verbatim)

Finish all unblocked, owner-settled AnkiScape implementation recorded in the newest Memory Bank, one atomic breadth-first slice at a time, with every accepted slice landed on canonical main through the promotion gate below. Preserve mechanic-complete end-to-end paths for every skill, activity, feature family, and shared substrate. With horizontal breadth complete, prioritize shared tooling, player-visible defects, readily recoverable period values, registered placeholders, and recorded data-depth debt.

Sourcing and scope: follow the pre-EOC evidence standard and the newest owner-approved contracts. Settled designs stay settled. Coordinate with the Darkan restoration thread instead of duplicating its quest work or source harvesting. Use a registered placeholder only for a period value that remains unrecovered. Record contract conflicts and owner-only decisions in the Memory Bank and continue independent work.

Slice acceptance: each slice is authored by dispatched agents in an independent worktree on its own goal/* branch. A slice is accepted when it has focused regression coverage, both repository verification lanes green (plain and offscreen Qt), the documentation, test-quality, diff, reachability, asset, and worktree checks passing, source and Memory Bank updates, an independent cross-lineage review of its diff with all findings resolved, and one attributable commit on its branch.

Promotion to main: merging accepted slices onto main is part of this goal — do it without waiting for the owner. Only the orchestrator seat merges; dispatched agents never commit to main. Merge in a worktree, re-run both verification lanes and the repository checks on the merged tree, and land on main only when that post-merge run is fully green. The owner actively uses this Anki install, so main never holds an unverified tree. On an another-writer collision on main, stop and record it; attempt no repair. Never push to any remote.

Fixed rails: tests, audits, and pinned baselines are measuring instruments; a slice that weakens them to pass is rejected. Baseline at goal-set: main at 125bf965 with both lanes green.

Completion: a fresh queue audit shows no unblocked settled implementation remains and no accepted slice is still unmerged; every remaining entry is verified complete, classified as deferred data depth, or recorded with exact evidence as owner-, source-, dependency-, quota-, or integration-blocked.

Run the work through dynamic workflows and dispatched agents; the orchestrator verifies and never authors code. Utilize the /agentic-loop-design skill. Use Computer Use agent on the MacBook Pro on the network for in-game testing; and use the same MBP over Tailscale/SSH for headless testing instead of this Mac Studio.

This goal is also satisfied if I record a genuine blocker in memory-bank/GOAL-BLOCKED.md (or ./GOAL-BLOCKED.md where there is no memory bank) naming what is blocked, what I tried, and the single thing that would unblock it. Quota exhaustion, a needed decision only the owner can make, and a missing external dependency all count. Preferring not to do the work does not.
