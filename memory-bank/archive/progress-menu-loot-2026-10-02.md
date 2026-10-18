# Menu loot preference source history

Current helper code is on main at 8b7adb0b. The live successor is core/menu_loot.py. The priority matrix owns current native and menu acceptance holds. This archive changes no acceptance. The complete historical section follows verbatim.

## Main-menu loot preference cleanup, 2026-10-02

The menu keeps the same behavior. A maintainer can change gathering Keep/Drop and combat loot preferences in `core/menu_loot.py` without reading the full menu closure. The root menu binds the live add-on module with the same `functools.partial` pattern as `core/menu_cooking.py`; callbacks resolve the current profile and skill on every call.

Branch: `goal/menu-dispatch-split-2026-10-02`. Base: `60d7bd835c77b08f7040c67c77db4da7a233e648`.
Worktree: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02`.
Evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/`.

### Function metrics

| Function | CCN before | CCN after | Cognitive before | Cognitive after | Halstead before | Halstead after |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `_on_main_menu` | 1 | 1 | 969 | 944 | 7.094117647058823 | 7.148148148148148 |
| `_current_gathering_target` | n/a | 4 | n/a | 3 | n/a | 0.5 |
| `current_gathering_keep_drop_state` | n/a | 3 | n/a | 1 | n/a | 1.0 |
| `set_carried_keep_drop` | n/a | 4 | n/a | 4 | n/a | 1.0 |
| `current_combat_loot_rows` | n/a | 4 | n/a | 3 | n/a | 1.0 |
| `set_loot_override` | n/a | 3 | n/a | 3 | n/a | 1.0 |

Root metric exits 1 reflect the existing cognitive complexity above 15; the helper exits 0.

### Exact verification records

local-before-inventory: `python3 run_tests.py --count test_dispatcher_state test_combat_main_menu_loot_rows_only_include_observed_drops`; exit 0, Matching tests: 20.
before-inventory: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02' plain --collect-only --select test_dispatcher_state --select test_combat_main_menu_loot_rows_only_include_observed_drops`; exit 0, Matching tests: 20.
before-focused: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02' plain --select test_dispatcher_state --select test_combat_main_menu_loot_rows_only_include_observed_drops --expected-tests 20`; exit 0, Ran 20 tests in 5.364s; OK.
after-local-inventory: `python3 run_tests.py --count test_dispatcher_state test_combat_main_menu_loot_rows_only_include_observed_drops`; exit 0, Matching tests: 20.
after-focused: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02' plain --select test_dispatcher_state --select test_combat_main_menu_loot_rows_only_include_observed_drops --expected-tests 20`; exit 0, Ran 20 tests in 5.397s; OK.
neighbor-inventory: `python3 run_tests.py --count test_integration_smoke test_direct_action_undo_seam test_module_surface test_promotion_gate test_memory_bank_queue_packet`; exit 0, Matching tests: 312.
after-neighbors: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02' plain --select test_integration_smoke --select test_direct_action_undo_seam --select test_module_surface --select test_promotion_gate --select test_memory_bank_queue_packet --expected-tests 312`; exit 0, Ran 312 tests in 144.326s; OK.
full-plain: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02' plain`; exit 0, Ran 5158 tests in 444.815s; OK (skipped=579).
differential-final: `python3 '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/differential.py'`; exit 0, Differential cases: 12050; Generated cases: 12000; Directed cases: 50; Differences: 0; Old unexecuted statements: []; New unexecuted statements: [].
differential-report-proof: `python3 '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/differential.py'`; exit 0, Differential cases: 12050; Generated cases: 12000; Directed cases: 50; Differences: 0; Old unexecuted statements: []; New unexecuted statements: [].
baseline-final-metrics: `python3 tools/maintenance/function_metrics.py --output '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/main-menu-before-final.json' '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/main-init.py' _on_main_menu`; exit 1, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/baseline-final-metrics.log.
final-metrics: `python3 tools/maintenance/function_metrics.py --output '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/main-menu-after-final.json' __init__.py _on_main_menu`; exit 1, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/final-metrics.log.
helper-final-metrics: `python3 tools/maintenance/function_metrics.py --output '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/menu-loot-after-final.json' core/menu_loot.py _current_gathering_target current_gathering_keep_drop_state set_carried_keep_drop current_combat_loot_rows set_loot_override`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/helper-final-metrics.log.
before-surface: `env QT_QPA_PLATFORM=offscreen .venv-qt/bin/python tools/module_surface.py --digest-only __init__.py`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/before-surface.log.
after-surface: `env QT_QPA_PLATFORM=offscreen .venv-qt/bin/python tools/module_surface.py --digest-only __init__.py`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/after-surface.log.
audit-docs: `python3 tools/audit_docs.py`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/audit-docs.log.
audit-test-quality: `python3 tools/audit_test_quality.py`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/audit-test-quality.log.
before-reachability: `python3 tools/audit_item_reachability.py --check`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/before-reachability.log.
after-reachability: `python3 tools/audit_item_reachability.py --check`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/after-reachability.log.
worktree-audit: `python3 tools/worktree_guard.py audit`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/worktree-audit.log.
diff-check: `git diff --check`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/diff-check.log.

Root module surface and reachability output are byte-identical before and after; tests and module-surface pins stay fixed.

### Approved review fixes

Restored both loot comments and the carried-pack comment reference. Each handler binds live player data inside its body; behavior remains unchanged. The path and runtime-fakes papercuts remain.
review-fixes-differential: `python3 '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/differential.py'`; exit 0, Differential cases: 12050; Generated cases: 12000; Directed cases: 50; Differences: 0; Old unexecuted statements: []; New unexecuted statements: [].
review-fixes-helper-metrics: `python3 tools/maintenance/function_metrics.py --output '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/menu-loot-review-fixes.json' core/menu_loot.py _current_gathering_target current_gathering_keep_drop_state set_carried_keep_drop current_combat_loot_rows set_loot_override`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/review-fixes-helper-metrics.log.
review-fixes-plain: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02' plain --select test_dispatcher_state --select test_combat_main_menu_loot_rows_only_include_observed_drops --expected-tests 20`; exit 0, Ran 20 tests in 5.469s; OK.
review-fixes-qt: `/opt/homebrew/bin/python3 tools/run_remote_tests.py '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/goal-menu-dispatch-split-2026-10-02' qt --select test_dispatcher_state --select test_combat_main_menu_loot_rows_only_include_observed_drops --expected-tests 20`; exit 0, Ran 20 tests in 5.757s; OK.
review-fixes-docs: `python3 tools/audit_docs.py`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/review-fixes-docs.log.
review-fixes-docs-final: `python3 tools/audit_docs.py`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/review-fixes-docs-final.log.
review-fixes-diff-check: `git diff --check`; exit 0, output in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-menu-dispatch-split-2026-10-02/review-fixes-diff-check.log.

<!-- End of preserved historical section. -->
