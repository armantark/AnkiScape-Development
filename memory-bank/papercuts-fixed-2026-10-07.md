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

## 2026-10-09T18:53:31.776038+00:00 Tribal Totem context timestamp correction

Disposition: record_only.

Evidence: The original event time is unverified. The author-recorded2026-10-09T18:10:00Z is incorrect as an event timestamp: source commit04e4800726fea99fbb8a950754fd3e4afe87f69c was created at2026-10-09T06:56:44-07:00 and already contained this row. Retained run receipts do not establish the exact recovery time. Preserve the original row verbatim below as a historical erroneous recording, not a verified timestamp; this correction was recorded at2026-10-09T18:53:31.776038+00:00. The recovered paths and errors remain exact. No product edit, test replay or invented past event time was used.

- 2026-10-09T18:10:00Z — Tribal Totem opening context: combined reads truncated repeatedly; guessed paths returned rg: data/quest/generated*: No such file or directory (os error 2), rg: runtime/runtime_actions_quest.py: No such file or directory (os error 2), rg: runtime/runtime_actions_common.py: No such file or directory (os error 2), and sed: logic_pure/action_telemetry.py: No such file or directory. Bounded exact reads recovered existing runtime_actions_production.py, logic_pure_telemetry.py and immutable Lost City test43c25e0d; no product edit preceded recovery.
