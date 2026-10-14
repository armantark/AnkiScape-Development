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

## Direct source-packet CLI startup

Disposition: fixed.

Evidence: The CLI bootstrap uses the script checkout before repository imports in tools/native/freeze_source.py and tools/maintenance/retain_evidence.py. Original direct --help receipts both returned exit 1 with ModuleNotFoundError: No module named tools. The existing test_source_packet_scripts_reach_argument_parser_from_unrelated_directory failed all four canaries before the repair, then passed one test with exit 0 and zero skips. Evidence: /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/papercut-qualified-batch-1/original-receipts.json and /Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/papercut-qualified-batch-1/final-cli-proof.json. Module commands and packet/retention safeguards retain the existing interfaces. Mixed incidents with guessed paths or host-key errors remain open. Full merged gates and landing remain Root-owned.

- 2026-10-08T02:05:24.428137+00:00 Native freezer direct invocation `python3 tools/native/freeze_source.py --help` failed with `ModuleNotFoundError: No module named 'tools'`; the supported package invocation is `python3 -m tools.native.freeze_source`. No tool/source change or verification rerun.
