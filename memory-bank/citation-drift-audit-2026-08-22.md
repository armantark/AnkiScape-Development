# Citation drift audit — 2026-08-22

Status: implemented; existing drift is measured but deliberately not rewritten.

## Authority and method

Design-thread queue section 3.29 requires a mechanical check for Memory Bank
line citations. The parser accepts direct `path:line` and `path:start-end`
citations, comma-separated line lists, and the wrapped form that names a path
before saying `lines ...` on the next line.

For repository-local targets, `changed` compares the target slice at the commit
that `git blame HEAD` assigns to the cited Markdown line with the same line
interval in the working tree. This is the commit that last changed the current
record-line version, not proof of the author's intended claim or the target
text when an earlier version of that record line was first written. Therefore, `changed` is a review signal, not confirmed
citation drift. The terminal preview prints both compared texts when they differ.

The actionable headline includes only `moved`, `missing_lines`, and
`missing_file` results backed by repository history or a pinned external commit.
The same statuses against an unpinned current external tree are reported
separately because a current snapshot cannot establish historical drift.
`unresolved` means that no configured source could classify the citation.

The complete machine-readable result is
`memory-bank/citation-drift-results.json.gz`. Output paths must end in
`.json.gz`, and the tool rejects any path that resolves to a scanned Markdown
source record. It never rewrites a citation.

## Measured baseline

The 2026-08-22 run scanned 552 Markdown files and found 1,432 citations. It
resolved 1,413: 480 repository-local, 328 pinned external, and 605 against
current external trees.

The actionable headline is **261 citation drifts**:

- 143 `moved`
- 29 `missing_lines`
- 89 `missing_file`

Outside that headline, the audit found 136 `changed` review signals, 36
unpinned-current-tree mismatch signals (26 moved, 5 missing lines, and 5 missing
files), and 19 unresolved citations. The motivating split form in
`memory-bank/source-audits/grimy-herb-family-2026-08-11.md:128-130` now resolves
all six listed Hunter markers.

No citation or source record was edited from these findings. They are remediation
input for later documentation-only work, not permission for automatic rewrites.
