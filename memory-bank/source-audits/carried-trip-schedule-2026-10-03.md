# Carried trip schedule selection — 2026-10-03

Author branch: `goal/carried-trip-schedule-2026-10-03`. Frozen base: `94420078f978c2281144a144857dc805f9042cde`.
The selector owns active, due and inactive schedule choice. The dispatcher retains gates, cadence, Winter Storage, arrivals and settlement.
The selector preserves the default constant read, active precedence, nested review fallback/clamp and initializer signature.
Static scope: one new selector and one dispatcher change. All other top-level source declarations have equal ASTs.
Installed metrics: dispatcher CCN 51 → 48, cognitive 55 → 52, Halstead difficulty 7.754098360655738 → 7.7.
Selector: CCN 4, cognitive 3, Halstead difficulty 0.5. Limits: 15, 15, 80. Dispatcher closure is incomplete.
Physical file: 991 → 999 lines. Final source SHA-256: `2ae9086d7f58a8be2a893e0e33e8186e88dfecc6395ac78fe4f8a60b2609428b`.
No new tests or changed instruments. Before-edit failure modes are in the raw evidence.
Static documentation, test-quality, worktree and whitespace audits passed. Test quality: 5169 tests, 331 files, 0 hard issues, 32 clone groups.
Root must obtain complete differential traces, focused tests, full branch plain, exact merged plain/Qt, reachability and native review/save/reload/Undo evidence.
No product execution, remote command, native check or behavior-preservation claim came from this author.
Raw evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-03-codex-resume/carried-schedule-evidence`. Root handoff: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-03-codex-resume/carried-schedule.md`.
Existing meaningful coverage: new-bank-trip, real-handler travel/Firemaking, processing reconciliation, Keep settlement, Winter Storage rollback, cadence, hood, urns and direct-action Undo.

| Raw artifact | SHA-256 |
| --- | --- |
| `baseline-overlay.py` | `1a6c391585ba7f256141af5d6710adca14a72351022e520db86999338e81849b` |
| `pre-edit-failure-modes.md` | `1c179e74d3b198ea93e7659bb05ea6594962c3a869ff1d2e3ed9d0ceba81daf3` |
| `metrics-before.json` | `559a020244fb99e0904319da5f09945074ac025dceaf09fcd3aae9e18c9280da` |
| `metrics-after.json` | `814eb959ab1e89b726a8b2cb7f0503e3cb9400ce13fb2c2f85f747751e10d2e9` |
| `static-scope.log` | `f6897d7cc5d453d7fdfaca6f468c82292437824c0403623cb265aa5ac6262027` |
| `source.diff` | `bf74ea3aec816809abd0471416a6b4f9ba2cc1e03a4c32b07d3fe4265189126d` |
| `audit-test-quality.log` | `f5903a59d79286ed031f10ea0e9265682e587ba6278f9b3885c8b024675195ba` |
| `worktree-guard.log` | `cc6202cc6351917cf1a616a7e6260503ba977a2974a999173c9d89c038c3f572` |
| `diff-check.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
