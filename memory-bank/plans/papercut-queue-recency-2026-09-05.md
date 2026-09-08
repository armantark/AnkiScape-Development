# Current papercuts in the queue packet

The owner requested a bounded papercut pass while the dispatcher gate runs. The queue packet currently recognises only bulleted incidents and selects the first eight entries. The ledger contains both bulleted and plain timestamp records and mixes older prepended sections with later appended incidents. The packet therefore hides current failures.

## Contract

Update only the papercut selection in tools/memory_bank_queue_packet.py and its focused tests. Recognise timestamped incident starts with or without a bullet, using the actual ledger formats. Select the eight most recent dated incidents rather than the first eight physical records. Use the recorded calendar date as the ordering authority; preserve deterministic source-line ordering for entries with the same date, preferring later appended entries. Do not invent timezone or missing-time precision. Keep each selected record's original text and source line references intact. Retain the current context limit, UTF-8 byte cap and complete omission/truncation reporting. Update the omission wording to describe the selected dated entries accurately. Do not change unrelated queue or backlog selection.

The author owns this tool, tests/test_memory_bank_queue_packet.py, and this slice's Memory Bank notes in pool 8. No other agent writes those files. Cover plain and bulleted timestamps, mixed file ordering, records with the same date, adjacent record boundaries, and preservation of byte-cap reporting. Reuse existing fixtures and avoid a general event parser or new framework.

The author performs static preparation only while session 80555 owns the MacBook mirror. The orchestrator will arrange runtime verification on the MacBook. No product imports or test runs on this Mac, no remote sync, no live Anki, no canonical edits, no gate weakening, and no push. Return a bounded diff for review before a normal author commit. Full slice and merged-tree gates remain required.

## Execution

The pool initially refused allocation with: all 16 worktrees are in use or dirty (max_trees = 16). The orchestrator verified pool 8 was clean, idle, unmarked by any active gate, and fully merged at constants commit 9f54377b0aa1e1072ec56b20ea3714ba060edd2a. It returned that completed lease and acquired pool 8 for this branch, without raising or bypassing the cap.
