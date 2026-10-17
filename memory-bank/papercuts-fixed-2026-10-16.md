# Papercuts fixed — 2026-10-16

## Pass 16 retro: text-fit check reads item views and message boxes

Disposition: fixed.

Evidence: commit f2cef509: text_fit_defects measures every laid-out item-view cell in its painted text rectangle and builds button style options without the protected initStyleOption. The two other observations in this entry stay open as a new 2026-10-16 entry.

- 2026-10-16: Pass 16 offscreen Qt: `text_fit_defects` skips QTreeWidget item text (the snape grass row clipped unflagged) and raises "no access to protected functions" on QMessageBox children; `QMessageBox.question` is not `activeModalWidget()` offscreen; a Fusion dark palette set role by role leaves the Disabled group with Normal colours.

## Pass 16 retro: to-tickets writes tickets where ready.py reads them

Disposition: fixed.

Evidence: fleet commit 390d065: to-tickets and to-spec now put ticket files in <spec-dir>/tickets/, the folder implement-spec's ready.py reads; the owner audited the diff.

- 2026-10-15: Pass 16 to-tickets: the to-tickets skill puts ticket files beside spec.md, but implement-spec's scripts/ready.py reads only <spec-dir>/tickets/[0-9]*-*.md, so tickets beside the spec print "0 tickets". Followed ready.py.
