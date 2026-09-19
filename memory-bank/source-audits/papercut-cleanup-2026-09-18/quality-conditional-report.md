# Conditional TestCase import: reviewed candidate ready

Recorded: 2026-09-19T09:56:50-07:00
Candidate root: `/private/tmp/ankiscape-quality-conditional-2026-09-19`
Unified patch: `/private/tmp/ankiscape-quality-conditional-2026-09-19/conditional-import.patch`
No repository files were edited. All three original source hashes still match the startup snapshot. Root owns application after the active source gate.

## Final change

The resolver walks module control-flow containers and returns their actual binding nodes. Class and function scopes remain leaves. It requires exactly one binding, so the real caller's single import inside `try` resolves while alternate imports, assignments and capture bindings are rejected.

The binding matcher explicitly handles `ast.ExceptHandler.name`, `ast.MatchAs.name`, `ast.MatchStar.name` and `ast.MatchMapping.rest`. These fields store plain strings and do not appear as `ast.Name` nodes. This closes both reviewed fail-open cases without adding runtime control-flow evaluation.

The target-level-order candidate removes only the redundant `unittest.TestCase` base: `TargetLevelOrderWidgetTest(MainMenuWidgetTest)`. No product behavior or runtime import handler changed.

Two new tooling methods cover eight conditional-import/scope cases and four string-binding cases. The conditional cases are unique import, alternate handler import, handler assignment, later assignment, unrelated class scope, unrelated function scope, ordinary imported base and missing imported base. The string-binding cases are an exception alias, a match capture, a starred match capture and mapping-rest capture. The match fixtures use concrete empty collections; they do not depend on an undefined match subject.

## Before/after evidence

`PYTHONDONTWRITEBYTECODE=1 python3 check.py` ran under `/private/tmp/ankiscape-quality-conditional-2026-09-19` and exited 0.

- Copied tooling tests: 16 run, 0 failures, 0 errors, 0 skips. This is 13 quality-audit tests plus 3 vacuous-source-scan tests.
- Original resolver against the conditional-import regression: exactly 3 positive subtest failures and 0 errors. The unique import and both scope-isolation positives were rejected before the fix.
- Reviewed candidate against the new string-binding regression: exactly 4 failures and 0 errors. All four cases were incorrectly accepted before the string-field fix. The reviewed source is preserved under `review-baseline/tools/audit_test_quality.py`.
- The real copied caller has exactly one base, `MainMenuWidgetTest`, and two widget methods: `test_mining_flat_list_renders_level_ordered` and `test_herblore_tree_groups_render_level_ordered`.
- On that base-removed source, the original resolver does not recognize `TargetLevelOrderWidgetTest`; the final candidate does.
- Original auditor on the copied suite: 281 files, 4852 recognized methods, exactly 2 hard issues. The only issues are those two real caller methods, at lines 143 and 160.
- Final candidate on the same suite: 281 files, 4854 recognized methods, 0 hard issues, 31 structural clone groups.
- The harness asserts that no `pkg_alias`, `ankiscape`, `aqt` or `PyQt` module was imported. The real caller and its harness were parsed as source only.
- All three candidate files compiled from strings without execution or bytecode writes. All three passed a trailing-whitespace check.

Logs: `tooling-tests.log`, `before-regression.log`, `review-before-regression.log`. Data: `evidence.json`, `check.stdout.json`. Reproducer: `check.py`. All are under the candidate root. The `suite/` subtree contains source copies for static auditing; no product test from it was executed.

## Fixed complexity and size rails

`PYTHONDONTWRITEBYTECODE=1 python3 check_metrics.py` exited 0. It uses installed `/Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py` functions on the original/candidate copies, without Git/index mutation or hook execution.

Loaded caps remain CCN 15, cognitive 15, Halstead difficulty 80 and file lines 1000. No complexity regressions exceed the caps. There are no new dead-code or layout findings.

- `_module_binds_name`: CCN remains 12; cognitive 13 to 12; Halstead difficulty 2.5.
- New `_module_binding_nodes`: CCN 5; cognitive 5; Halstead difficulty 0.
- Resolver `binding_node`: CCN 5 to 3; cognitive 4 to 2.
- New conditional-import test: CCN 2; cognitive 1.
- New string-binding test: CCN 3; cognitive 3.
- File lengths: audit 845, tooling tests 419, target-level-order tests 188. Unrelated legacy complexity is unchanged.

Exact metrics: `/private/tmp/ankiscape-quality-conditional-2026-09-19/metrics.json`.

## Candidate hashes (SHA-256)

- `tools/audit_test_quality.py`: `e66eafedaf5a59787aa242524578477fafb53ddc5c4c004000442c11d5bd6be4`
- `tests/test_test_quality.py`: `596803c61bb2bc783d0eb85fd137747e5c2f445a8f7fede918d99a0b04d99ae5`
- `tests/skills/test_target_level_order.py`: `99077b8f6761f2ab87f9aff5c4dda5315125e05d8eb90b3909812c9b8e136f0d`

Original hashes remain in `source-hashes-before.json`. `check.py` confirmed the original repository files still match. The final candidate files and regenerated unified patch are frozen.

## Static-analysis limits

A unique conditional import is treated as a source binding. The resolver does not prove that a runtime import succeeds, evaluate branches or model exception execution. Multiple recorded bindings remain fail closed.

Class and function definitions stay scope leaves. Rare module-scope bindings inside expressions evaluated by those definitions, such as walrus assignments in decorators, class bases or function defaults, are not counted. For example, a default argument that assigns to an imported base name can remain a false negative in binding detection. This reviewed limit is documented rather than expanded into interpreter work.

Comprehension targets and lambda-local walrus bindings may be counted conservatively and can reject valid ancestry. Nested test classes inside conditional statements remain outside the existing top-level method audit. Arbitrary decorators, metaclasses, factories, import hooks and runtime module mutation are not executed or interpreted.

No product imports/tests, remote calls, browser/native actions, repository edits, commits, Git configuration/index changes, pushes, hook bypasses, other worktrees, subagents, global-file writes or task messages occurred. Root retains remote acceptance and application ownership.

## Papercuts for root

- A source search in the initial follow-up included every widget test name and reached output truncation; the later proof selected only the exact class through AST.
- The first combined conditional-binding walker measured cognitive complexity 18 against cap 15 despite CCN 14. Separating leaf matching from the scope-aware walk passed without changing caps.
- 2026-09-19T09:56:50-07:00: Review exposed string-valued AST bindings that `ast.Name` traversal misses: `ExceptHandler.name`, `MatchAs.name`, `MatchStar.name`, and `MatchMapping.rest`. Four before/after rejection fixtures now cover those nodes.
