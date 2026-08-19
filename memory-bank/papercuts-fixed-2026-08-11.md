# Papercuts fixed — 2026-08-11

## Re-land review — 2026-08-19

The slice was re-merged against main snapshot
`323bf39090023319eb4e5a80acf6e162d331fa4a`. None of its implemented guardrails
had been superseded on main, so none were dropped. The focused-selector guard
was extended to resolve the subsequently recorded mistake
`tests/test_bone_sources.py` to discovered component `test_bone_sources` while
retaining the ambiguity refusal. The reachability instrument had changed
substantially on main; only the orthogonal `--summary` output/exit contract was
carried across, with the new graph logic left intact. Main and the merged tree
both report `1571 actions; 2266 reachable items; 84 orphan inputs; 87 blocked
actions`; parsed `--json` reports are equal with canonical SHA-256
`287670c806ca798123bcd758a6a578049af685531c7680a7312474a6c2fe43e3`.
Full plain discovery passes `Ran 4156 tests in 242.767s` with `skipped=499`;
real offscreen Qt passes `Ran 4156 tests in 552.881s` with `skipped=3`. No
gameplay or period value changed.

The occurrence counts below are conservative exact-failure counts from the 371-line log. The fixes are tooling-only; the item-reachability JSON report is byte-for-byte equivalent after JSON parsing.

## Generated catalogs overwhelm broad searches — 24 occurrences

Recorded lines: 34, 35, 97, 108, 129–131, 161, 172, 183, 191, 217, 231, 271, 275, 287, 294, 297, 307, 311, 319, 334, 339, 348.

Fix: `.ignore` excludes `data/shop_data.py` and `data/construction_data.py` for ordinary `rg` searches from either the repository root or `data/`; `tools/repo_search.py` also excludes those files by basename, so an explicit `data` search root cannot defeat the exclusion.

Before: the recorded explicit-root form `rg --glob '!data/shop_data.py' ... data` could include the generated catalog because ripgrep saw `shop_data.py`, not `data/shop_data.py`.

After: ordinary `rg` from the repository root and from inside `data/` returns zero generated-catalog bytes for a catalog-only term; `python3 tools/repo_search.py 'Dragon hatchet' data` returns five bounded live-source matches and no generated catalog.

## Guessed unittest selectors — 32 occurrences

Recorded lines: 10, 27, 36, 47, 51, 55, 56, 89, 116, 143, 163, 187, 197, 198, 222, 234, 240, 249, 251, 254, 268, 284, 306, 313, 321, 328, 329, 337, 342, 343, 349, 360.

Fix: `run_tests.py` resolves a fuzzy selector only when one candidate has a strong, unambiguous lead. Ambiguous guesses fail and print candidates rather than silently running the wrong scope.

Before: `python3 -m unittest tests.test_main_menu_widget.MainMenuWidgetTests` failed with `AttributeError: module 'tests.test_main_menu_widget' has no attribute 'MainMenuWidgetTests'`.

After: `python3 run_tests.py MainMenuWidgetTests --list --max-results 5` resolves to `MainMenuWidgetTest`; the corresponding Runtime Actions and Integration Smoke guesses also resolve. A deliberately ambiguous `test_alpha_onf` fixture is refused by focused coverage.

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

Fix: `tools/audit_item_reachability.py --summary` prints the four graph counts and exits 0 for chain-safe informational use. Default and `--json` modes preserve exit 1 while unresolved debt remains.

Before: `--json` wrote a valid report and exited 1, silently stopping later `&&` gates.

After: `--summary` prints `1556 actions; 2573 reachable items; 102 orphan inputs; 101 blocked actions` and exits 0; `--json` still exits 1.

## Qt harness font startup — 5 occurrences, partially fixed

Recorded lines: 115, 132, 134–136.

Fix: `run_tests.py` registers installed `Arial` as Qt's substitution for the missing default `Sans Serif` family. It does not create a `QApplication`, so test-owned application lifecycle and modal behavior remain unchanged.

Before: the focused offscreen Qt proof emitted `Replace uses of missing font family "Sans Serif"` and spent 1021 ms populating aliases. The first fix created a global application before discovery, which made `MilestoneCapeTest.test_a_cape_woven_through_the_real_crafting_path_can_be_worn` enter a real `QDialog::exec()` and hang.

After: the exact `Sans Serif` warning is gone, and the real milestone-cape test completes in 0.005 seconds without a harness-created application. A production stylesheet legitimately requests generic `monospace`, so Qt may still emit the same class of warning for `Monospace`; the harness does not rewrite production stylesheet inputs merely to hide that cosmetic cost.

## Concurrent worktree writers — newly reported defect

Fix: `tools/worktree_guard.py` records `.ankiscape-worktree-owner` when it creates a worktree, exposes `claim` with deliberate `--take-over`, and makes `audit` fail when the current linked worktree belongs to another caller. Initial claims use exclusive file creation so the filesystem selects exactly one winner. Claims reject the canonical checkout and unregistered paths because neither target can be enforced by audit. Only `add` and `claim` idempotently install the marker in the repository-wide common `info/exclude`; read-only `audit` does not mutate shared Git state. An identified caller must claim an older unowned worktree before audit accepts it, while callers without a session identity can still run the documented layout audit.

Before: `worktree_guard.py owner` and `audit --owner` were unsupported, so two sessions could edit the same checkout without a warning. The first read-then-write implementation was also racy: the 300-round before-fix process probe reported `rounds=300 double_successes=300`.

After: the same 300-round process probe reports `rounds=300 double_successes=0`; a worktree claimed by `session-a` audited as `session-b` exits 2 with `Linked worktrees are owned by another session`; takeover must be explicit, invalid claim targets fail, and a temporary worktree on an older branch remains clean after the guard installs the shared exclude and writes the owner file. Concurrent exclude installers use append-only writes: their lines cannot interleave, and harmless duplicate patterns are tolerated rather than risking another writer's entries through whole-file replacement.

Check-then-act audit: initial owner creation is arbitrated by exclusive file creation; shared-exclude setup serializes check-and-append with `fcntl` on POSIX and emits a warning before using an append-only best-effort fallback elsewhere; destination/branch creation is delegated to Git, whose `worktree add`/`-b` fails atomically if another caller wins. Explicit takeover remains an advisory last-writer-wins operation by design, because each caller deliberately authorizes replacement and the owner record is not a lock.

Limits: ownership is advisory rather than enforcing; exclude-install atomicity is POSIX-only; duplicate exclude entries are harmless and tolerated by design; stale owner records require deliberate `--take-over`; and the ownership signal identifies another present caller but does not prove that a particular file write landed.

## Not fixed

- External or provider failures, browser/computer-use failures, Workflows budget/schema mistakes, wiki 403s, source-specific guesses, patch-context misses, and one-off command errors remain historical because repository tooling cannot reliably remove them.
- Generic `monospace` in shipped stylesheet inputs was not rewritten in the test harness. Doing so would test modified inputs and could hide real UI regressions; the remaining font alias message is therefore documented as a partial fix.
- The owner record is a warning and deliberate takeover mechanism, not a lock. A dead session cannot strand a worktree.
