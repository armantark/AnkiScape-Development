# Papercuts fixed — 2026-10-07

## Native receipt reader and exact integer repair

Disposition: fixed.

Evidence: Current receipt reading compares the actual before/reopened snapshots instead of the derived observed summary. The raw final-integrity.json verifies exact mtime_ns 1790036557987862453, and current acceptance prose uses that Python integer. All native proof was preserved; no native rerun.

- 2026-10-07T20:34:33+00:00 Native menu report rendered mtime_ns as `1790036557987862500`, while earlier raw baseline reports `1790036557987862453`; qualify this exact prose discrepancy and resolve from raw Python integers without repeating successful native product verification.
- 2026-10-07T21:19:32.978097+00:00 Root retention reader assumed `player` in derived `mining-retention-observed.json` and exited 1 with `KeyError: 'player'`. Inspected the actual schema and compared raw `mining-retention-before-reopen.json` with `mining-retention-reopened.json`; scoped fields, positive inventory, selected skill, cards and review rows match. No successful native verification was rerun.

## Startup budget restored without changing its limit

Disposition: fixed.

Evidence: The stock move removes three resolved lines from startup while preserving every byte in the dated fixed ledger. The fixed limit remains less than 3000.

- 2026-10-07T21:24:12.967009+00:00 Native acceptance notes hit `startup_line_budget_exceeded: 3000 startup lines must stay under 3000: memory-bank/activeContext.md=70, memory-bank/progress.md=866, memory-bank/future-work-kanban.md=1580, memory-bank/goal-priority-matrix.md=221, memory-bank/loop-queue.md=0, memory-bank/papercuts.md=263`. Move only resolved receipt-reader and integer-report entries with the stock ledger tool; keep the limit unchanged and preserve completed product verification.

## 2026-10-09 Tree Gnome source verification recovery

Disposition: fixed.

Evidence: Verified source paths and archive shape recovered without product changes. Original493-case repair81941 returned0 (Ran 493 tests in 1.532s; OK); failed45939 and19096 raw logs/receipts remain in /private/tmp/ankiscape-tree-gnome-village-opening-2026-10-09. Normal supply consumption reconciles Bank quantity and used_review, with every full-state assertion retained. Restored unrelated original blank lines; moving the three resolved incidents through the existing helper preserves each corrected literal record and the fixed startup cap.

- 2026-10-09T15:14:17.844707+00:00 — Tree Gnome opening author guessed tests/runtime_actions/test_woodcutting.py, data/skill/woodcutting.py, data/quest/stage_overrides/sources.py and members/modern/as_a_first_resort.py; rg returned No such file or directory (os error 2). Subsequent verified rg --files resolved data/quest/sources.py and members/later. Combined broad bank/output reads were truncated; use bounded verified-path reads, no product verification replay.
- 2026-10-09T15:14:51.256671+00:00 — Tree Gnome retained archive read assumed revisions at the wiki record root and then pages as a dict: KeyError: 'revisions'; AttributeError: 'list' object has no attribute 'values'. Actual retained shape is wiki[key]['query']['pages'][0]['revisions']; source archive unchanged.
- 2026-10-09T15:25:12.461079+00:00 — Tree Gnome original focused45939 returned1: "Ran 493 tests in 1.575s", "FAILED (failures=1)", full-state handoff expected Bank metadata Logs quantity8/used_review0 versus actual2/2. Diagnostic19096: "Ran 1 test in 1.249s", "FAILED (failures=1)" confirmed only those fields; normal save reconciliation tracks six Logs consumed at review2. Expected metadata corrected, all player/config assertions retained; failed raw/receipts preserved. During diagnosis rg also guessed runtime/runtime_actions_support.py, runtime/review_undo.py and hooks (No such file or directory (os error 2)); use verified /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/promote-game-2026-09-27b/__init__.py and /Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/promote-game-2026-09-27b/logic/bank_layout_logic.py.
