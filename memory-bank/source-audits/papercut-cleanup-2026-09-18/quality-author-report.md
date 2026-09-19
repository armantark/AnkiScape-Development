# Static TestCase ancestry maintenance: complete

Recorded: 2026-09-19T09:22:20-07:00
Checkout: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pool/.treehouse/ankiscape_fork-091389/4/ankiscape_fork`
Baseline HEAD: `ff44ddf641abdc7b7325c97351744972e9592b4d`
Scope: `tools/audit_test_quality.py` and `tests/test_test_quality.py` only.
The implementation goal stays paused. The files are frozen for root review.

## Result

The audit follows local imported TestCase ancestry without importing product or fixture code. Package `__init__.py` relative imports keep the package component. An unaliased dotted import binds the top-level package. A shared cached source record parses a file only when the audit needs it; unrelated invalid syntax and non-UTF-8 helpers do not abort the audit. Actual test source failures and failures in a required ancestor remain explicit.

A cohesive resolver owns module bindings, cycle detection and resolved ancestry. It rejects missing, ordinary, dynamic-call, cyclic, shadowed and rebound class/module bindings. It accepts direct, aliased, relative and dotted local ancestry, plus explicit `unittest`, `unittest.case`, and TestCase aliases. The standard-library marker cannot collide with a local module key.

## Checks run

All commands ran in the checkout above unless an absolute path is shown.

1. `python3 -m unittest discover -s tests -p test_test_quality.py`
   - 11 tests run; 11 passed; 0 skips, 0 errors, 0 failures.
   - Log: `/tmp/ankiscape-quality-after-2026-09-19.log`.
2. `python3 -m unittest discover -s tests/promotion -p test_vacuous_source_scan_audit.py`
   - 3 tests run; 3 passed; 0 skips, 0 errors, 0 failures.
   - Log: `/tmp/ankiscape-quality-source-scan-tests-2026-09-19.log`.
3. `python3 tools/audit_test_quality.py --json`
   - 281 files; 4852 methods; 0 hard issues; 31 structural clone groups.
   - Output: `/tmp/ankiscape-quality-final-audit-2026-09-19.json`.
4. `python3 /tmp/ankiscape-quality-baseline-2026-09-19.py --tests-root tests --json`
   - HEAD auditor on the same current tests: 281 files; 4852 methods; 0 hard issues; 31 clone groups.
   - Output: `/tmp/ankiscape-quality-baseline-audit-2026-09-19.json`.
5. `python3 -m py_compile tools/audit_test_quality.py tests/test_test_quality.py`
   - Exit 0.
6. `git diff --check -- tools/audit_test_quality.py tests/test_test_quality.py`
   - Exit 0.
7. `python3 /tmp/ankiscape-quality-check-2026-09-19.py`
   - Uses the installed `/Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate.py` metric and ratchet functions on temporary HEAD/current snapshots. It does not stage files or invoke a commit.
   - Loaded caps: CCN 15, cognitive 15, Halstead 80, file lines 1000.
   - No CCN, cognitive or Halstead regressions. No new dead-code or layout findings.
   - Maximum new/changed CCN: 14. Maximum new/changed cognitive complexity: 13. Maximum changed Halstead difficulty: 4.75.
   - `audit_test_suite` was CCN 19 in HEAD and is still 19. Its cognitive complexity was 43 and is still 43. Existing unrelated complexity was not refactored.
   - The supplied intermediate `imported_binding` was CCN 22. Import decoding is now CCN 14, and resolver `imported_binding` is CCN 2.
   - File lengths: 829 lines for the audit; 365 lines for its tests. Both fit the loaded 1000-line cap.
   - Exact metric data and source hashes: `/tmp/ankiscape-quality-metrics-2026-09-19.json`.

## Regression evidence

The final two defect-focused test methods were replayed with `audit_test_suite` from `/tmp/ankiscape-quality-before-finish-2026-09-19.py`, the supplied uncommitted source before this pass. They produced the expected 4 subtest failures and 1 error. The harness asserted those exact failure/error counts and exited 0. The failures cover the two package-relative directions and the dotted-import genuine/ordinary directions. The error was `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte` from an unrelated fixture.

Evidence: `/tmp/ankiscape-quality-final-regression-before-2026-09-19.log`.

A separate temporary-source probe confirmed explicit `SyntaxError` for malformed `test_broken.py`, explicit `UnicodeDecodeError` for non-UTF-8 `test_broken.py`, and explicit `SyntaxError` for a malformed `harness.py` whose base was required by a test. These cases are not silently skipped.

## Review dispositions

- Finding 10: accepted. Package identity is retained in the lazy source record through its actual `__init__.py` path. Tests use `tests.package` so the prior wrong parent lookup is exercised in both directions.
- Finding 11: accepted. No-`as` dotted imports bind their first component; explicit aliases bind the complete module. Attribute chains follow only known module paths.
- Finding 12: accepted. The eager AST index was removed. The path/source index shares a cached parse between aliases and the audit pass.
- Finding 13: verified. The real static suite has zero hard issues both with HEAD and the final auditor. Explicit `unittest.case.TestCase` ancestry is now recognized rather than rejected.
- Signature simplification: accepted in equivalent form. The resolver owns the shared modules and `class_names` takes only the already-computed module name; it no longer receives redundant tree/path/root arguments or recomputes the module name.
- Standard-library marker suggestion: accepted. `<stdlib unittest>` has a separate key space.
- Removal of local-unittest shadow checks: rejected. This is a source auditor over an arbitrary supplied test root, not proof about a particular runner's preloaded `sys.modules`. Assuming the real `unittest` is already cached can accept a local ordinary `TestCase`. The explicit local-shadow regression remains fail closed. No runtime runner change or product import was used to justify deleting this guard.
- Suggestions outside the two owned files were left to root.

## Limitations and safety

This is static source ancestry, not a Python execution model. It does not execute decorators, metaclasses, arbitrary factories, assignments that alias classes, import hooks or runtime module mutation. External non-unittest harnesses remain unresolved. Multiple writes to a name, including conditional writes and star imports, are rejected conservatively rather than evaluated as runtime dataflow. Source parse errors are still raised when a file is actually required.

No product modules or product tests were executed locally. No remote, browser or native calls ran. No Git/index mutation, commit, Git config change, push, hook bypass, other checkout edit, skill installation or agent delegation was performed. Full remote product acceptance and the real staged commit hook remain root-owned checks; the metric probe above is not a claim that either has run.

## Frozen file hashes (SHA-256)

- `tools/audit_test_quality.py`: `cca13ca7c039083d6324b0695fd6ddc71efafe595528468a4766f5928aae2df4`
- `tests/test_test_quality.py`: `5e20ab96c19497f93b8a50bb72be4669d4fcaf72c1f79a92363e76cb26677f30`

## Small friction for root's shared papercuts log

- 2026-09-19T09:22:20-07:00: During initial quality-audit inspection, the zsh operand `tools/check*` matched no files and prevented the `rg` command from running: `zsh:1: no matches found: tools/check*`. Subsequent searches used explicit paths.
- 2026-09-19T09:22:20-07:00: Two tool orchestration snippets used `"workdir"` without an object value and failed before execution with `SyntaxError: Unexpected string`; the calls were rebuilt from a command list and a single shared options object.
- 2026-09-19T09:22:20-07:00: Broad memory-bank and baseline output hit output truncation during startup; subsequent reads used bounded relevant ranges.
- 2026-09-19T09:22:20-07:00: A guessed split gate file did not exist: `rg: /Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate_python.py: IO error for operation on /Users/ArmanTarkhanian1/fleet/config/git/hooks/slop_gate_python.py: No such file or directory (os error 2)`. The actual installed gate is one `slop_gate.py` file.
- 2026-09-19T09:22:20-07:00: The first resolver draft passed CCN but failed the installed cognitive ratchet because Complexipy charged nested resolver closures to their outer function (`_test_case_class_names`, 45 versus baseline 19). A single state-owning resolver class removed the capture nesting; final metrics pass without threshold changes.
