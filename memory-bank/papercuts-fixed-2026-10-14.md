# Papercuts fixed — 2026-10-14

## Citation audit attributes dirty record lines to their own bytes

Disposition: fixed.

Evidence: tools/audit_citation_drift.py GitRepository.blame_commits now runs git blame --contents - on the exact record bytes the parser reads, so uncommitted lines have no committed origin and unchanged lines keep theirs; a HEAD tree Git cannot read, a blame failure or a line-count mismatch raises. Regression: tests/test_citation_drift_audit.py test_dirty_record_lines_keep_only_the_origins_of_their_own_bytes, test_record_lines_git_cannot_count_fail_attribution and test_head_tree_git_cannot_read_fails_attribution (red at 2e7b6378, green on the repaired source). Real Memory Bank probe in a disposable clone: one uncommitted line prepended to 256 records changed 0 of 2513 origin commits (old auditor: 580).

- 2026-10-13T21:28-07:00 Staleness sweep: re-running `tools/audit_citation_drift.py` on the uncommitted fixed tree reported 284 actionable rows, including rows just repointed (`future-work-kanban.md:27` flagged `__init__.py:5432` as moved to 5363), because `git blame HEAD` resolves edited lines against their old commit; a sweep that may not commit has to measure in a throwaway `git clone` with the diff committed (157 there).
