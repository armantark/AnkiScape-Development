# Papercuts fixed — 2026-08-11

## Re-land review — 2026-08-19

The slice was re-merged against main snapshot
`323bf39090023319eb4e5a80acf6e162d331fa4a`. The focused-selector guard was
extended to resolve an exact path such as `tests/test_bone_sources.py` to the
discovered component `test_bone_sources`, while fuzzy module substitutions now
fail closed instead of silently running a different scope. The advisory
worktree-ownership feature was dropped after two review rounds showed that it
broke the read-only layout audit and did not detect first-claim collisions. The
reachability instrument had changed
substantially on main; only the orthogonal `--summary` output/exit contract was
carried across, with the new graph logic left intact. Main and the merged tree
both report `1571 actions; 2266 reachable items; 84 orphan inputs; 87 blocked
actions`; parsed `--json` reports are equal with canonical SHA-256
`287670c806ca798123bcd758a6a578049af685531c7680a7312474a6c2fe43e3`.
Full plain discovery passes `Ran 4152 tests in 346.387s` with
`skipped=499`. The real offscreen Qt lane was split into five independent
processes because the monolithic lane exceeds the 600-second command cap; the
partitions ran 1,015, 904, 1,036, 566, and 631 tests (4,152 total) with three
skips in aggregate. No
gameplay or period value changed.

The occurrence counts below are conservative exact-failure counts from the 371-line log. The fixes are tooling-only; the item-reachability JSON report is byte-for-byte equivalent after JSON parsing.

## Generated catalogs overwhelm broad searches — 24 occurrences

Recorded lines: 34, 35, 97, 108, 129–131, 161, 172, 183, 191, 217, 231, 271, 275, 287, 294, 297, 307, 311, 319, 334, 339, 348.

Fix: the root `.ignore` was removed because it hid `data/shop_data.py` and `data/construction_data.py` from every ordinary ripgrep search. `tools/repo_search.py` excludes those files by basename only in its bounded default mode, so an explicit `data` search root cannot defeat the wrapper exclusion; `--include-large` deliberately restores them.

Before: the recorded explicit-root form `rg --glob '!data/shop_data.py' ... data` could include the generated catalog because ripgrep saw `shop_data.py`, not `data/shop_data.py`. The first attempted fix moved the exclusions into `.ignore`, which made the catalogs invisible even when a caller explicitly needed them.

After: ordinary `rg` can see the catalogs again; `python3 tools/repo_search.py shop_data data --names` exits 1 by default, while the same command with `--include-large` prints `data/shop_data.py` and exits 0.

## Guessed unittest selectors — 32 occurrences

Recorded lines: 10, 27, 36, 47, 51, 55, 56, 89, 116, 143, 163, 187, 197, 198, 222, 234, 240, 249, 251, 254, 268, 284, 306, 313, 321, 328, 329, 337, 342, 343, 349, 360.

Fix: `run_tests.py` resolves exact unittest ID fragments and exact `tests/test_*.py` paths. Unmatched selectors fail and print candidates rather than substituting a different module.

Before: `python3 -m unittest tests.test_main_menu_widget.MainMenuWidgetTests` failed with `AttributeError: module 'tests.test_main_menu_widget' has no attribute 'MainMenuWidgetTests'`. The first guardrail revision silently substituted `MainMenuWidgetTest`, so a typo could run a different scope than the caller requested.

After: `python3 run_tests.py MainMenuWidgetTests --list --max-results 5` exits 2 with `No unambiguous unittest ID matched: MainMenuWidgetTests`; `python3 run_tests.py tests/test_main_menu_widget.py --list --max-results 2000` resolves the exact file path.

## Unmatched zsh globs — 23 occurrences

Recorded lines: 64, 67, 73, 81, 82, 85, 87, 99, 118, 121, 133, 166, 232, 277, 281, 283, 286, 291, 305, 306, 336, 347, 358.

Fix: `tools/repo_search.py --names` remains the sanctioned file-discovery path and accepts directories instead of shell globs. For direct zsh commands, `setopt nonomatch` makes an unmatched optional pattern reach the command instead of aborting the shell.

Before: `zsh -c 'rg --files memory-bank/*grind*'` failed before `rg` ran with `zsh:1: no matches found: memory-bank/*grind*`.

After: `python3 tools/repo_search.py '<pattern>' memory-bank --names` searches the existing parent safely. The shell-level `setopt nonomatch` form no longer aborts in zsh.

## Stale module paths — 10 occurrences

Recorded lines: 3, 9, 66, 80, 82, 83, 96, 140, 177, 274.

Fix: `tools/repo_search.py --names` is the repository path resolver; missing explicit paths already return a bounded hint to locate moved files from an existing parent.

Before: a faithful stale-path probe returned `No such file or directory` for `ui.py`, `runtime_actions.py`, and `logic_pure.py`.

After: the name resolver locates `ui/ui.py`, `runtime/runtime_actions.py`, and `logic_pure/logic_pure_production.py` without a broad content search.

## Generator direct invocation and `pkg_alias` — 2 occurrences

Recorded lines: 37, 122.

Fix: the affected generators already bootstrap the repository root before importing `pkg_alias`; focused tests now protect both `generate_equipment_data.py` and `generate_ge_period_data.py` direct invocation.

Before: the recorded commands failed with `ModuleNotFoundError: No module named 'pkg_alias'`.

After: equipment direct invocation reaches argparse help with exit 0; GE direct invocation reaches its own usage gate, not an import failure.

## zsh `status` and clipped test wrappers — 2 exact `status` failures, plus recurring long-lane clipping

Recorded lines: 18, 103, 104, 200, 361.

Fix: `tools/run_logged.py` is the sanctioned lane wrapper. It stores the complete combined output, prints a bounded tail, and returns the child exit code without assigning any shell variable. `run_tests.py --quiet` suppresses per-test names while retaining failures and the final summary.

Before: `zsh -c 'false; status=$?'` failed with `zsh:1: read-only variable: status`; verbose full lanes clipped the useful tail.

After: a child exit 7 is returned as exit 7 with its full log retained, and the quiet focused proof prints `Ran 1 test` and `OK` without the test name.

## Reachability chaining hazard — 2 exact closure failures

Recorded lines: 345, 357.

Fix: `tools/audit_item_reachability.py --summary` prints only the four graph counts while preserving the audit's finding in its exit status. Default, `--summary`, `--json`, and `--json --summary` now all exit 1 while orphan inputs remain.

Before: `--json` wrote a valid report and exited 1, which stopped later `&&` gates; the first fix made `--summary` chain-safe by masking that finding with exit 0, including when combined with `--json`.

After: `--summary` prints `1571 actions; 2266 reachable items; 84 orphan inputs; 87 blocked actions` and exits 1, matching every other output format on the same tree.

## Qt harness font startup — 5 occurrences, partially fixed

Recorded lines: 115, 132, 134–136.

Fix: `run_tests.py` registers installed `Arial` as Qt's substitution for the missing default `Sans Serif` family. It does not create a `QApplication`, so test-owned application lifecycle and modal behavior remain unchanged.

Before: the focused offscreen Qt proof emitted `Replace uses of missing font family "Sans Serif"` and spent 1021 ms populating aliases. The first fix created a global application before discovery, which made `MilestoneCapeTest.test_a_cape_woven_through_the_real_crafting_path_can_be_worn` enter a real `QDialog::exec()` and hang.

After: the targeted milestone-cape startup path completes in 0.018 seconds without the `Sans Serif` warning and without a harness-created application. Other UI tests can still request that family later and emit the same warning; the harness does not rewrite production stylesheet inputs merely to hide a cosmetic cost.

## Not fixed

- External or provider failures, browser/computer-use failures, Workflows budget/schema mistakes, wiki 403s, source-specific guesses, patch-context misses, and one-off command errors remain historical because repository tooling cannot reliably remove them.
- Generic `monospace` in shipped stylesheet inputs was not rewritten in the test harness. Doing so would test modified inputs and could hide real UI regressions; the remaining font alias message is therefore documented as a partial fix.
