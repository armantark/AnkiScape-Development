# Historical Pass 15b failure diagnosis

This checkpoint is retained from progress.md. Its figures and paths are historical.

## Pass 15b failure diagnosis and final verification — 2026-10-02

Both original tests pass on main `60d7bd835c77b08f7040c67c77db4da7a233e648` and fail on clean branch HEAD `075e90a9b627dacd0bf63859e0a34c5e05d02ad7`. Copies came from `git archive` and the comparisons ran under
`/tmp/pass15b-diagnosis-emr0sp1z/{main,head}` without the alchemy edits.
No stash, checkout, worktree change or canonical-checkout edit was used.
- Asset cutoff: `075e90a9` changed the constant imported by the unchanged audit
  from `2012-11-20T23:59:59Z` to `2012-11-19T23:59:59Z`, leaving its report stale.
  `1fc5cb70` made the crafting fetcher use that shared cutoff. The consistency
  test is right; its exact failure was `AssertionError: '2012-11-20T23:59:59Z' != '2012-11-19T23:59:59Z'`.
  The strict boundary is settled in `pre-eoc-source-verification-standard.md`,
  RuneScape Wiki Procedure step 1. The unchanged audit was run twice at that
  boundary, first into `/tmp`, then at its normal path. Every row and summary
  agreed. The refreshed report selects the Rune crossbow revision at
  `2012-10-08T17:06:29Z` instead of `2012-11-20T21:58:46Z`. The audit code,
  test and asset bytes are unchanged. Its 100 removed historical rows each
  have current provenance at or before the stricter cutoff. The missing Spike
  trap source remains explicit as `unresolved`, with no invented evidence.
- Fletching: `987f4bcc` applies the belt predicate to eligibility and tooltips.
  The original metadata test failed with `AssertionError: True is not false`.
  `design-thread-queue.md` section 4.28.6 settles presence without ownership
  for listed belt tools; `core/tool_belt.py` includes Chisel. Changed only the
  three replaced expectations: enabled without a Bank Chisel, no required-tool
  heading, and no missing-Chisel tooltip. Material and owned-Chisel checks stay.
- Fix commit: `a2fbd1a3`; the pre-commit hook passed. Focused verification:
  `Ran 81 tests in 0.822s`; `OK`.
Evidence is under `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/`:
`diagnosis-{main,head}-*-2026-10-02.log`, `strict-asset-audit*-2026-10-02.log`,
`failure-fixes-focused-2026-10-02.log`, and `alchemy-equivalence-2026-10-02.log`.
Full plain lane (one final invocation; runner exit 0):

```text
Ran 5164 tests in 448.663s
OK (skipped=581)
```

Log: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/final-full-plain-2026-10-02.log`.
Full Qt lane (one final invocation; runner exit 1):

```text
Ran 5164 tests in 674.026s
FAILED (failures=1, skipped=6)
error: remote qt lane failed with exit 1
```

Additional failure: `test_fletching_is_selectable_and_shows_grouped_target_tree (tests.test_main_menu_widget.MainMenuWidgetTest.test_fletching_is_selectable_and_shows_grouped_target_tree)`, `tests/test_main_menu_widget.py:7248`. Exact assertion:

```text
AssertionError: 'Chisel x1' not found in 'Requires Fletching level 42. You have 99 (base 99).\nOutput: Long kebbit bolts x6\nMaterials:\nLong kebbit spike x1 (you have 1)'
```

The same owner decision in `design-thread-queue.md` section 4.28.6 replaces this expectation. The original test also passes on main `60d7bd83` and fails on clean branch HEAD `075e90a9` in the disposable `/tmp` copies. Commit `f6b16b4a` changes only `assertIn` to `assertNotIn` for the Chisel tooltip; the pre-commit hook passed. Focused local offscreen Qt after the correction: `Ran 1 test in 2.422s`; `OK`, with no skips. Evidence: `qt-fletching-{main,head,fixed}-2026-10-02.log`.
Log: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/final-full-qt-2026-10-02.log`.
Both full lanes were invoked exactly once. No production code changed after either snapshot. The Qt assertion correction was verified with the focused run; the full Qt lane was not repeated, and no full Qt pass is claimed. The shared alchemy table and these result lines are committed together, with no separate progress-note commit.

### 2026-10-02 — Pass 15b review fixes, earlier lane snapshot
- Shades: reverted the unsupported belt changes from 987f4bcc; Tool belt oldid 6538396 (2012-11-06) and Shades oldid 6397774 (2012-10-13) do not establish temple belt use. Sources: https://runescape.wiki/w/Tool_belt?oldid=6538396 ; https://runescape.wiki/w/Shades_of_Mort%27ton?oldid=6397774 .
- Shield: retain 54 with an open owner question; non-beta oldid 5641898 (2012-05-22) contradicts quest oldid 6540919 (2012-11-07) and restored Darkan 56. Sources: https://runescape.wiki/w/Fremennik_round_shield?oldid=5641898 ; https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919 .
- Art: 37 release-day-end and 11 midnight fetchers now share the strict cutoff; real Crafting dry runs prove historical selection and release-day refusal. Other review dispositions are in memory-bank/source-audits/pass15b-review-fixes-2026-10-02.md.
- One full invocation per lane: plain-1790995340-7d42a60a; qt-1790997113-b6a4f429.
```text
Remote plain lane summary:
Ran 5164 tests in 453.701s
OK (skipped=581)
Remote qt lane summary:
Ran 5164 tests in 682.246s
OK (skipped=6)
```
- Raw logs and verification-results.json: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/review-fixes/ These earlier runs precede the final Shades revert and fixes 6–7; final-snapshot results are recorded below.

### 2026-10-02: Pass 15b final-snapshot verification
- Commit `2764efef3e4b6cb82ecaafbe43fe83e8688d37e8` passed the pre-commit hook; fix 8 is dropped, Shades is reverted, and fixes 6–7 remain.
- One full invocation per lane, plain then qt: plain-1791000720-6f809456; qt-1791003920-fb193bcd. Python code is unchanged after the commit.
```text
Remote plain lane summary:
Ran 5164 tests in 458.477s
OK (skipped=581)
Remote qt lane summary:
Ran 5164 tests in 688.836s
OK (skipped=6)
```
- Captured logs and verification-results.json: /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/pass15b-logic-followups/review-finish/

