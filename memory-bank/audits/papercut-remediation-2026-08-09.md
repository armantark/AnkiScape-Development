# Papercut Remediation — 2026-08-09

## Scope and accounting

This audit accounts for every incident in the 2026-08-09 00:25 checkout
snapshot of `memory-bank/papercuts.md` (snapshot lines 3-121). The incident log
remains append-only evidence. A papercut is closed here when it has a durable
guard, an existing regression oracle, or an explicit external/source boundary;
closure does not erase the original failure.

## Durable fixes

| Snapshot lines | Incidents | Resolution |
| --- | --- | --- |
| 3-7, 9, 14, 34-35, 62-64, 66-68, 73, 77, 79-83, 85-90, 93-99, 108, 118, 121 | Stale paths, unmatched zsh globs, broad searches, giant one-line/generated matches, and combined reads | `tools/repo_search.py` now provides bounded content and filename discovery, validates paths before invoking `rg`, caps results and line width, and excludes the known giant generated/archive surfaces by default. `memory-bank/techContext.md` records the canonical split-module and no-glob workflow. |
| 10, 27, 36, 47, 51, 55-56, 116-117 | Guessed unittest class names, all-skipped focused lanes, and high-volume per-row failure output | `run_tests.py` now discovers first and selects by case-insensitive test-ID fragment. Unknown selectors return close discovered names, `--list` is bounded, and a focused lane in which every selected test skips exits 2 with the real-Qt command. Tests that report catalog-wide invariants must aggregate offending names before one assertion. |
| 18-19, 21, 25, 46, 48-49, 52, 54, 72, 76, 101, 103-105, 107 | Verbose suites, audits, delegated output, and partial artifacts overflowing the model channel | `run_tests.py` defaults to compact verbosity. `tools/run_logged.py` preserves complete per-command logs, exit codes, and bounded tails. Workflow partials remain authoritative evidence and are not replayed wholesale. |
| 31, 39, 43, 45, 49, 53, 75-76, 101, 106-107, 111 | Invalid workflow modes/budgets/schemas, incomplete frozen packets, inherited-context costs, and agents escaping read bounds | `tools/workflow_manifest_guard.py` rejects the recurring schema mistakes before launch. The technical context requires explicit new-file contents, realistic inherited-instruction budgets, frozen inputs for checkers, and preservation of typed partial artifacts. The guard cannot make a model honor a prompt; hard tool-output and processed-token budgets remain the containment boundary. |
| 37, 109 | Equipment generator direct execution and external source-root ambiguity | `tools/generate_equipment_data.py` adds the add-on root before importing `pkg_alias`, supports direct `--help`/execution, and labels `--game-root` as the external 2011Scape checkout. The technical context records the absolute pinned `items.yml` path. |
| 58 | Dead status-artifact example path | Removed the nonexistent `mobile-ux-fixes-2026-05-18.html` example from the shared `status-artifact` skill and verified its frontmatter plus absence directly. |
| 102 | `/tmp` probes could not import `tests` | The technical context now gives the canonical `PYTHONPATH="$PWD"` and `pkg_alias` probe rules. |
| 104 | zsh reserves `status` | `tools/run_logged.py` owns exit-code propagation, so closure commands no longer need an ad hoc shell variable. |
| 114 | The shared skill validator required unavailable PyYAML | No dependency was installed for a one-line skill deletion. Ruby's standard YAML parser verified the frontmatter, and an exact search verified removal; the missing optional validator dependency remains environment-owned. |

## Existing fixes retained as regression evidence

| Snapshot lines | Resolution state |
| --- | --- |
| 4 | The required papercut log now exists; this audit preserves rather than recreates it. |
| 15-17 | The D&D selector fixture, hidden-row click guard, and Qt-only role construction were fixed in the Activities pass. The named main-menu and pure-suite regressions remain the oracle. |
| 20 | Activities-only middle-column sizing replaced the global width change; the Farming narrow-dialog regression remains the oracle. |
| 27 | The footer-parent assertion replaced the invalid mixed-coordinate comparison. Test-ID discovery closes the paired class-name error. |
| 42 | The settings multiplier has a stable object name; tests no longer depend on Qt child traversal order. |
| 44 | Bank consumers use visible `bankGrid` helpers after removal of the compatibility list. |
| 50 | `pkg_alias.py` is the existing direct-probe package boundary; the rule is now indexed beside the new tools. |
| 81 | The cached wiki response's page-ID object shape was learned and recorded in the original incident; it is source-client-specific rather than a general product defect. |
| 91 | Heading discovery before section slicing is the retained parser rule; the corrected Shooting Stars parser is the regression surface. |
| 92, 95 | Order-sensitive/modal focused Qt aggregates are rejected as product oracles. Isolated target tests plus canonical full-suite discovery remain the closure gate. |

## Operator constraints, not code defects

| Snapshot lines | Boundary |
| --- | --- |
| 8, 23 | Workflow state and Git index writes depend on the host approval/sandbox profile. The current unrestricted checkout can write both, but repo code must not bypass a denied boundary. |
| 11, 26, 65, 74, 78, 88, 112 | Stale multi-hunk patch contexts are prevented by re-reading the local seam and applying function- or paragraph-sized patches. A generic patch wrapper would only duplicate `apply_patch` verification and weaken atomicity. |
| 12-13, 22, 25, 40, 43, 46, 48-49, 52, 54, 76, 100-101, 107, 111 | Provider output shape, inherited instructions, and model tool choices require typed parsing, frozen packets, ordinary-context diffs, explicit untracked contents, and hard budgets. Completed reads and bounded partials must be reused rather than rerun. |
| 24 | Commit hashes must be copied from `git rev-parse HEAD`; fabricating a suffix has no safe automated substitute. |
| 28-30, 57 | Native host/thread availability, text-vs-JSON connector results, and the connector's maximum `limit: 50` are external API contracts. No product change can make an unavailable host appear. |
| 32 | A moving canonical `main` is a concurrent-writer collision. The worktree/dirty-tree gate must stop rather than merge unowned changes implicitly. |
| 38 | Disposable `importlib` callers must register modules in `sys.modules`; normal imports remain the preferred path. |
| 41 | Recoverable `/usr/bin/trash` is the accepted cleanup path when destructive `rm` is denied. |

## External and source-blocked incidents

| Snapshot lines | Boundary |
| --- | --- |
| 33, 59-61 | PinchTab localhost snapshot/navigation timeouts, a busy local port, and Postplan authentication are external runtime conditions. Use text/screenshot fallback, an available ephemeral port, and authenticated publishing; do not weaken the artifact checker or restart shared browser state. |
| 69-71 | Tip.It denied direct access and one Wayback image body was absent. The accepted path is dated Wayback HTML plus CDX discovery of an independent image capture. |
| 84 | The burnt tiger shark wiki asset is post-cutoff; it remains a period-cache sprite or documented-fallback source gap, not permission to invent art. |
| 90 | Darkan implementation evidence lives in the external Gradle `rs.darkan/core` JAR and must be inspected there with `javap`; no sibling source tree is promised. |
| 115 | Qt's offscreen macOS platform reports its generic `Sans Serif` alias as missing and spends about 0.45 seconds populating aliases. No project source requests that family, focused tests pass, and replacing the application font in a test would stop exercising Anki's inherited font; retain the warning as harness-only performance noise. |

## Concurrent feature-owned incident

Snapshot line 110 records a newly expanded Mage Training Arena test that became
quadratic in practical runtime. That feature is changing concurrently in the
shared checkout. This pass does not edit or stage its files; its owning thread
must replace repeated deep-copy review loops with atomic full-wallet row checks
and retain one review-earned end-to-end example per distinct purchase mechanic.

## Remediation-pass friction

Snapshot lines 111-114 and 118-120 are the workflow-boundary overflow,
exact-tail patch context mismatch, method-local unittest-ID expectation,
optional validator dependency, unmatched-glob regression, JavaScript command
quoting error, and oversized diff-review read found during this pass. The
workflow failures are contained by frozen packets, hard budgets, and preserved
partials. The deterministic failures were corrected with exact reads,
fixture-derived IDs, serialized manifests, and no-glob repository discovery.
