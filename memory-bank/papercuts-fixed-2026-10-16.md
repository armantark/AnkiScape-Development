# Papercuts fixed — 2026-10-16

## Pass 16 retro: text-fit check reads item views and message boxes

Disposition: fixed.

Evidence: commit f2cef509: text_fit_defects measures every laid-out item-view cell in its painted text rectangle and builds button style options without the protected initStyleOption. The two other observations in this entry stay open as a new 2026-10-16 entry.

- 2026-10-16: Pass 16 offscreen Qt: `text_fit_defects` skips QTreeWidget item text (the snape grass row clipped unflagged) and raises "no access to protected functions" on QMessageBox children; `QMessageBox.question` is not `activeModalWidget()` offscreen; a Fusion dark palette set role by role leaves the Disabled group with Normal colours.
