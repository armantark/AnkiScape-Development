# Papercuts fixed — 2026-10-14

## Image-history requests use supported parameters

Disposition: fixed.

Evidence: Source 11d4910b24a1d86a14118259fc9f078479e4e138 removes only unsupported iidir from tools/audit_asset_cutoff.py. The pinned iistart, iilimit=1, four-attempt retry, post-cutoff refusal, alias and checkpoint behavior remain. Disposable protocol canary was red before repair; all 8 module tests then passed. Primary MediaWiki imageinfo parameter schema and raw receipts: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-query-param. S15 correction source `d59568900e6cdcd14ca52db151e977256ffa4a70` also repairs the original icon getter and both equivalent fetchers, refuses mixed newer-first results, and retains a successful live canary/report outside the checkout. Final focused10 has no skips; unchanged-checkpoint behavior is inspection-only. Independent re-review and exact merged promotion remain pending.

- 2026-10-02T18:54:44-07:00 — Telegrab icon provenance lookup: the wiki imageinfo API returned `Unrecognized parameter: iidir.`; `iistart=2012-11-19T23:59:59Z` still returned the required `2011-11-29T14:12:02Z` revision. `tools/audit_asset_cutoff.py::_request_batch` also supplies this unsupported parameter.

## Citation audit attributes dirty record lines to their own bytes

Disposition: fixed.

Evidence: tools/audit_citation_drift.py GitRepository.blame_commits now runs git blame --contents - on the exact record bytes the parser reads, so uncommitted lines have no committed origin and unchanged lines keep theirs; a HEAD tree Git cannot read, a blame failure or a line-count mismatch raises. Regression: tests/test_citation_drift_audit.py test_dirty_record_lines_keep_only_the_origins_of_their_own_bytes, test_record_lines_git_cannot_count_fail_attribution and test_head_tree_git_cannot_read_fails_attribution (red at 2e7b6378, green on the repaired source). Real Memory Bank probe in a disposable clone: one uncommitted line prepended to 256 records changed 0 of 2513 origin commits (old auditor: 580).

- 2026-10-13T21:28-07:00 Staleness sweep: re-running `tools/audit_citation_drift.py` on the uncommitted fixed tree reported 284 actionable rows, including rows just repointed (`future-work-kanban.md:27` flagged `__init__.py:5432` as moved to 5363), because `git blame HEAD` resolves edited lines against their old commit; a sweep that may not commit has to measure in a throwaway `git clone` with the diff committed (157 there).

## Slop preflight help and unsupported arguments

Disposition: fixed.

Evidence: The accompanying CLI source parses arguments before any Git/index/gate operation, against main2e7b6378871e0096515e1aaab7a64061c7aff7bc. Two original CLI regressions fail before the fix; all four existing/new cases pass after it, preserving no-argument status, diagnostics and real index bytes. Original proof: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/slop-preflight-args/green.receipt.json. Independent source review and exact merged gate/official land remain pending.

- 2026-10-07T05:45:44.248347+00:00 Root asked tools/maintenance/slop_gate_preflight.py --help; the script has no argument parser and began a second full gate with a disposable index. Stopped only root-owned PIDs 72670,70972,70925 with SIGTERM; normal commit gate, source/index and product proof runs were preserved. Read non-argparse utility source before requesting help.

## Mutation reads use isolated bytecode

Disposition: fixed.

Evidence: Officially landed d7bc03fe0a6c8ca3bf8ca3fb78f347e36ee8c7f2 gives each mutation a fresh PYTHONPYCACHEPREFIX; original RED57659 and configured full9 passed. The resolved cache-path fixture and all earlier NOT-red/failed receipts remain retained under mutation-bytecode-isolation. No original outcome was rewritten.

- 2026-10-14T14:53:16.070692+00:00 — Inspecting mutation/cache handling: a guessed tools/test_host search root did not exist (rg exit2: No such file or directory). The mutation guard source itself still sets only PYTHONDONTWRITEBYTECODE=1, which suppresses writes but permits existing bytecode reads; source-validity proof remains to be established before any repair.
- 2026-10-14T15:24:08.715765+00:00 — New final-test RED attempt10158 through the official mutation guard returned1, Ran5tests1.864s OK, Mutation proof: NOT red; fixed source restored exactly. Reconciliation briefly recorded outer0/red without inspecting that actual completion; corrected receipt now preserves actual1/NOTred. Investigate fixture cache-path identity under the outer PYTHONPYCACHEPREFIX before a new baseline.

## Full inventories remain in bounded proof files

Disposition: record_only.

Evidence: Current Sawmill codex-continuation inventory-full-plain.log retains the original complete output; receipt-full-plain.json binds5330/666.315s/580skip. Its launcher redirects the count once and projects the measured count. The original display truncation is preserved; this closes that recovered incident without claiming a general output-reader repair.

- 2026-10-14T15:01:24.485417+00:00 — Full plain selection count for mutation-bytecode-isolation returned Matching tests: 5327, but run_tests.py --count also printed every static skip (23303tokens), exceeding the display bound. The count is preserved with explicit truncated-metadata qualification; no execution proof was lost. Future full inventories must redirect once to the evidence log and project only count/tail.

## Revision and gate-report bindings use measured evidence

Disposition: fixed.

Evidence: Current continuation and mutation official-land reconciliation use actual Git/final-binding revision d7bc03fe0a6c8ca3bf8ca3fb78f347e36ee8c7f2. Retained mutation gate reports select the unique actual host plain/Qt run by namespace, existence and lane section. Original66559 all9 and official land returned0; no product check was replayed.

- 2026-10-14T16:01:41.411891+00:00 — Root continuation record manually expanded d7bc03fe into incorrect d7bc03fed120d8b861e11fce49d45a05717635f2; corrected from final-binding.json actual Git revision d7bc03fe0a6c8ca3bf8ca3fb78f347e36ee8c7f2. Continuation revision writes now consume the measured binding instead of manual expansion.
- 2026-10-14T16:36:52.007766+00:00 — Root mutation-gate evidence retention selected the last nested runner-test ID across both lanes, yielding FileNotFoundError: [Errno 2] No such file or directory: /tmp/tmpja5b9t0r/reports/plain-1791995416-0a76d734.report. Original66559 completed0 and all9 certificate checks remain accepted; bind actual host reports by namespace/existence and lane section, without replay.

## Leaves receive bounded catalog projections

Disposition: fixed.

Evidence: Root exclusively owns monolithic catalog access. Quest, Mogre and Bittercap leaf contracts consume selected structured projections with source/head hashes. Empty-pot, Mogre shop and beginner input packets are retained outside the repository; subsequent leaves requested those inputs rather than reading the catalog. Original giant read and failed Assign-only projection remain verbatim.

- 2026-10-14T16:22:58.592964+00:00 — Astra quest-root qualification repeated raw shop read: sed -n 1,58p data/shop_data.py emitted original_token_count:630939 and truncated. Root replaced the leaf catalog input with bounded AST-projected Empty pot1931/provider metadata and exact source revision/hash; Root alone reads the monolith. Initial Root projection handled only ast.Assign, causing KeyError: SHOP_DATA; AST inventory identified annotated constants and ast.AnnAssign projection succeeded.

## Earned Bittercap route survives seed-provider differences

Disposition: fixed.

Evidence: Codex proof2 checks actual provider stock rows before purchase and resumes hash-qualified earned checkpoints. P1/P2 terminal RED/GREEN now exit0 with real Farming53/combat/Priest/Vinesweeper/Undo/JSON/harvest proof. Original pending receipts, StopIteration logs and unbound exit markers remain unchanged.

- 2026-10-14T17:14:36.825705+00:00 — Both original Bittercap earned-route logs end in "StopIteration" at earned_route.py:137 after farm_until calls buy_seeds; recorded PIDs 91891/91893/97512/97513 are absent. Original pending receipts and checkpoints stay preserved; no completion or exit code is inferred.

## Preserve the two resolved integration conflicts

Disposition: record_only.

Evidence: Both original parent sections survive in the dated fixed log. Official citation77e3 and S15 2fe land receipts remain accepted. These conflicts required record reconciliation, not a product repair.

- 2026-10-14T03:53:12.224684-07:00 — Citation integration had add/add conflict in memory-bank/papercuts-fixed-2026-10-14.md: citation closure and landed preflight closure each created the dated file. Combined both original sections under their identical header, preserved every nonempty original line, then used existing no-loss checks against both parents. Source/audit limits and original successful proofs were unchanged.
- 2026-10-14T11:43:57.989729+00:00 — Integrating accepted S15 with citation landing: Git reported `CONFLICT (add/add): Merge conflict in memory-bank/papercuts-fixed-2026-10-14.md`; preserved both parent sections under their identical header and checked every parent line survives before staging.

## Preserve the correctly refused lease release

Disposition: record_only.

Evidence: The original gate completed before guarded checkout12 release. The unchanged source checkout12 now holds lease32f64c336d0c00792badebbe61403a43; bittercap-seed-identity/codex-continuation/reconciliation.json retains that acquisition.

- 2026-10-14T14:50:28.784955+00:00 — Releasing unchanged NPC reproduction checkout12 with worktree_guard release: error: Promotion landing lock held; stale recovery is disabled (exit2). Source8 original full gate owns that lock; no release occurred and no lock recovery/bypass was attempted. Retry the same guarded release only after the original gate finishes.

## Use the canonical combat catalog for bounded inputs

Disposition: fixed.

Evidence: bittercap-seed-identity/codex-proof-2/qualified-beginner-combat-input-2.json uses COMBAT_ENEMY_DATA and records47 imported module hashes. The empty293-byte AST input stays disqualified. Successful real combat/quest routes consume the actual projected rows.

- 2026-10-14T18:22:25.112737+00:00 — Root beginner combat AST projection wrote an empty293-byte input because _ENEMIES_BY_ID starts empty; the guessed subscript projection then raised "AssertionError: No selected canonical combat assignments". The existing Qt-free COMBAT_ENEMY_DATA API produced qualified-beginner-combat-input-2.json with actual rows and47 module hashes. Original empty input is explicitly disqualified and preserved.

## Refill food through real shops in the earned combat proof

Disposition: fixed.

Evidence: bittercap-seed-identity/codex-proof-2/terminal-reconciliation.json binds actual zero exits for farming53, route-red-2 and route-green. The driver replaces the exhausted-food policy with genuine refills and Defense-first training. Original route-red exit-15 and assertion-stop-canary exit1 remain.

- 2026-10-14T17:46:28.227805+00:00 — Earned combat proof bought only10 Lobsters with75% auto-eat and did not replenish supplies; at review36000 Attack4/XP277.6799999999998, current_skill Utilities, Lobster bank/loadout0, LP70. Terminated child48902 with SIGTERM, child exit-15 / wrapper241; saved review38000 checkpoint preserved. Proof-only policy now uses exact ungated stocked food rows, replenishes through real shops and callbacks, and trains Defense first.

## Keep the bounded projection within fixed limits

Disposition: fixed.

Evidence: bounded-shop-tool-verification/metrics-2.json passes the same installed instruments after _shops owns exact literal decoding and project owns row selection. Original metrics.json retains project cognitive17>15. The original entry timestamp19:00 was manually supplied and is not a measured event time; this closure is measured 2026-10-14T18:39:39.058749+00:00.

- 2026-10-14T19:00:00+00:00 — New bounded shop projection metrics refused exit1: project cognitive17 >15. No grandfathered baseline applies to this new function. Preserve metrics.json and split the exact literal-catalog reader from row projection without changing limits.
## Direct source-packet CLI startup

Disposition: fixed.

Evidence: The CLI bootstrap uses the script checkout before repository imports in tools/native/freeze_source.py and tools/maintenance/retain_evidence.py. Original direct --help receipts both returned exit 1 with ModuleNotFoundError: No module named tools. The existing test_source_packet_scripts_reach_argument_parser_from_unrelated_directory failed all four canaries before the repair, then passed one test with exit 0 and zero skips. Evidence: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/papercut-qualified-batch-1/original-receipts.json and /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/papercut-qualified-batch-1/final-cli-proof.json. Module commands and packet/retention safeguards retain the existing interfaces. Mixed incidents with guessed paths or host-key errors remain open. Full merged gates and landing remain Root-owned.

- 2026-10-08T02:05:24.428137+00:00 Native freezer direct invocation `python3 tools/native/freeze_source.py --help` failed with `ModuleNotFoundError: No module named 'tools'`; the supported package invocation is `python3 -m tools.native.freeze_source`. No tool/source change or verification rerun.

## Preserve both source-closure sections

Disposition: fixed.

Evidence: Root merged1f0976a3 preserves every nonempty line of both parent fixed ledgers; the three code files equal accepted source49bdf2e2.

- 2026-10-14T21:04:56.555928+00:00 — Integrating direct-CLI source49bdf2e2 into Root26280f90: Git reported CONFLICT (content) in memory-bank/papercuts-fixed-2026-10-14.md. Removed only conflict markers, retained both parent sections and verified every original nonempty parent line survives; no successful product check was replayed.
