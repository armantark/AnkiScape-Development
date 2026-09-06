# Diary ledger wiring review-fix contract

## Interfaces and ownership

- Direct-event validation must derive allowed event types and values from real emitter code, while preserving the existing action and farming rails.
- Leaf A owns `tools/achievement_diary_ledger.py` and `tests/test_achievement_diary_ledger_wiring.py`; it adds direct-event validation and five load-bearing execution tests.
- Leaf B owns `logic/temple_trekking_logic.py`, `logic/shades_of_mortton_logic.py`, `logic/managing_miscellania_logic.py`, and the managing-miscellania hook in `__init__.py`; it relocates emitters without touching runtime action handlers.
- Root owns `runtime/runtime_actions_activities.py`, `logic_pure/achievement_diary_events.py`, `logic_pure/logic_pure_prayer.py` only if needed, the ledger JSONL edits, papercut correction, generator complexity cleanup, and integration verification.
- No two leaves edit the same file. Root verifies all leaf claims and owns the single final commit.

## Tree and success criteria

- Leaf A: the generator rejects live clauses whose direct-event type/value has no emitter-derived support; five direct-event execution tests fail on the baseline and pass after the fix; focused test quality remains meaningful.
- Leaf B: Temple Trekking, Shades of Mort'ton, and Managing Miscellania emit only from their successful deed/command paths with the specified payloads; existing focused tests pass.
- Root: runtime combat emits derived prayer selection; agility forwards target id; the target-id allowlist and ledger clause are corrected; complexity-gate churn is removed; inert wrappers/parameters/imports are deleted or normalized; only items 1-11 change; designed triggers remain byte-identical except rows 8 and 11; catalog regeneration is deterministic.
- Integration: all focused/shared-file tests, required audits, `git diff --check`, and worktree audit pass; no `ui/` file changes; exactly one commit on `goal/diary-ledger-wiring-2026-09-01`.
