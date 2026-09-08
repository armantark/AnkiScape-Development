# Gate log prefix incident — 2026-09-08

Root redirected shell stdout to the same path owned by the gate's internal logger. The final stdout path overwrote the first 96 bytes of the raw gate log. The canonical raw log was not rewritten.

A precompletion snapshot already held 5,180 bytes, SHA-256 `2f90f34866a87e2484b5cc50620dd6381fbb1e843f72ae7d5a235f34c6fe4041`. Its 5,084 bytes after the overwritten prefix match the final raw log at the same offsets. The reconstructed log consists only of the first 96 snapshot bytes followed by the final raw log from byte 96 onward. No header was guessed and no gate was rerun.

The final raw log has 8,225 bytes and SHA-256 `4eee2bed4aa1b513582703377ee960907385403c63a70b7a41d5cc1eafb1b948`. The reconstructed log has 8,225 bytes and SHA-256 `a54202f9ee12fbc58ba5323f9c5efbd4ec995dd707dde24cb08fe8a1231394bd`. Both are retained unchanged in deterministic gzip, together with the original snapshot, identity, and reconstruction record. `manifest.json` binds original paths, stored and decoded hashes, and byte counts.

Root read the complete reconstructed log and the all-eight receipt for source `c225c456934f7f052854938c619d801d9474dc17`, gate session `99807`, exit 0 at `2026-09-08T14:12:03-07:00`. Root reported plain: 5,622 tests in 573.999s, 1,367 skips; Qt: 5,622 tests in 1102.561s, 5 skips. This documentation task did not execute those tests.

Future gate commands must not redirect stdout to the gate-owned log path. Let the gate own its log; use a different capture path if a shell transcript is needed.

Source acceptance does not establish combined-tree, canonical-main, or native acceptance. Root merged this source into integration `b2306c3ebc963779d53328b3139536fa5c99ed7e`. Canonical main remains `1bf2cfe2fa77cea2bb24528c6844d7473b1c2d12`, and no post-merge gate has run for this combined tree.
