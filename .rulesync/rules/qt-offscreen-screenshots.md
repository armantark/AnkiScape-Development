---
root: false
targets:
  - '*'
description: Show offscreen Qt dialogs before screenshot capture
---
# Offscreen Qt screenshots lie until the dialog is shown

`dialog.grab()` under `QT_QPA_PLATFORM=offscreen` renders **stale child
geometry** when the dialog was never shown: layouts haven't activated, so the
screenshot can show clipped/overlapping sections that don't exist (and,
worse, can *hide* real overlap by rendering pre-resize positions). This
produced two false readings during the 2026-07-06 Shop-tab work.

Rules for offscreen visual smoke checks:

1. `dialog.show()` first, then `resize(...)`, then several
   `QApplication.processEvents()` passes **before** any `grab()`.
2. Trust widget geometry probes over pixels: `widget.height()`,
   `scroll.viewport().height()`, `hbar.maximum()` are authoritative. If a
   full-dialog grab contradicts the probes, grab the individual widget
   (`scroll.grab()`) — it renders correctly.
3. Reproduce the user's real window size (Anki dialogs run ~560 logical
   points tall on a laptop; a 900px test dialog hides min-height overflow
   bugs). Screenshot at both the default size and the reported size.
4. For dark-mode checks, set a Fusion dark `QPalette` on the QApplication —
   offscreen never inherits the OS theme.
