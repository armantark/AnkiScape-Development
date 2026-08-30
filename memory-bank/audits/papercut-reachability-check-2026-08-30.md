# Reachability check mode audit — 2026-08-30

## Cause

`tools/audit_item_reachability.py` had only one success condition: no orphan inputs. A tree with an expected nonzero orphan baseline therefore returned 1 and stopped a compound `&&` verification chain even when every monitored count was unchanged. The output flags changed presentation, not that exit contract, so callers could not distinguish known audit debt from count drift.

## Scope

This slice adds `--check` with required integer pins for actions, reachable items, orphan inputs, and blocked actions. Check mode compares those pins with the report's four corresponding counts, reports each mismatch on stderr, and returns success only for an exact match. Default, summary, JSON, and rank output behavior and non-check exit semantics remain unchanged; JSON diagnostics stay off stdout. The synthetic CLI regression lives in `tests/test_papercut_tools.py`; `tools/promotion_gate.py` is unchanged.

## Pending MacBook verification

No tests were run on the Mac Studio, as required by the guarded slice. On the MacBook, run `/opt/homebrew/bin/python3 run_tests.py tests/test_papercut_tools.py`, then invoke check mode with pins copied from that same tree's measured summary. Confirm an exact match exits 0, changing each pin produces exit 1 with one field diagnostic, and `--json` still parses as JSON in both cases. No numeric baseline is asserted by this audit.
