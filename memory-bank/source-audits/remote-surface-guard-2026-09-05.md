# Remote surface guard repair evidence — 2026-09-05

Status: the independent Opus review accepted the core repair. Its preflight, runbook, and durable evidence findings are resolved in the corrective draft. The corrected focused verification passed and the driver confirmed the final diff. Both full MacBook lanes and post-merge gates remain pending. Product tests ran only on the MacBook. No installed environment or live Anki profile was changed.

## Root surface defect and exact repair

The previous mirror path, `/Users/armantarkhanian/ankiscape-remote-test-host/repo`, used a noncanonical package basename and excluded the `.venv-qt` path that the existing module-surface tests inspect. The offscreen Qt lane therefore skipped its root guard. The runner now uses `/Users/armantarkhanian/ankiscape-remote-test-host/ankiscape_fork` and creates its `.venv-qt` symlink to the already installed `/Users/armantarkhanian/ankiscape-remote-test-host/.venv-qt` after rsync. The old mirror and reports stay intact. Rsync still removes incoming Studio `.venv-qt` symlinks; only the explicit remote setup recreates the known remote-local link. `ln -sfn` replaces that exact path without following it when a transport retry repeats the command.

An isolated archive of unchanged main `ffb846d6631e4b73731f6573dd8d7c0e77e439db`, under the canonical basename with that interpreter link, measured root digest `fa36126b7ddff3d7d7d6582f80a12000d811533689fe3330e4e3864bb8641732`. The pin-introducing commit `4bdc1596` reproduced pinned digest `2625d3d2bb6110c0faee0a33863cf1bf8e921fe0591460eed25d071bec85e26d` on the same interpreter. Their complete dumps differ only by these two missing public records:

```text
NAME BIG_CHINCHOMPA_UTILITY_ID = "big_chinchompa"
NAME EVIL_TREE_UTILITY_ID = "evil_tree"
```

Restoring those names through the existing `runtime.runtime_actions` import restores the entire root dump byte for byte. That module already imports both names directly from the data modules; no re-export layer or dependency edge was added. The root digest and serializer are unchanged. Evidence: `/tmp/dispatcher-state-pinned-canonical-surface.txt`, `/tmp/dispatcher-state-baseline-canonical-surface.txt`, `/tmp/remote-surface-guard-restored-surface.txt`.

## Previously unexecuted shop Qt guard

The first complete focused run executed 16 tests and exposed one additional guard defect: the shop Qt surface measured `2ddacc925cbf537db4587117312620d7d1546e9fad2ff9c0f167afea710d09db`, but its Qt override was `3a4cb59b8b9881f1eb788a745e37044532ecd1bbb309d7c6cbcf0463a6572056`. The root Qt guard passed, and the only skip was the plain interpreter root import that requires `aqt`.

Instrument commit `4ba6568d16586fe833ee2526c4ae11d3a03ee06c` originally recorded exactly the measured plain and Qt digests as distinct baselines. Commit `d89b31ac50214ad14f2d7bc7d82c45ccc0d03772` later replaced both entries with the plain digest. `ui/ui_tab_shop.py` has no diff from `4ba6568d` to the branch base. Full current dumps reproduce both original digests. The complete per-environment payload delta consists of 17 Qt class imports plus the real Qt `CatalogFilterBar` signature, whose two required string parameters have empty-string defaults in the non-Qt stub. Evidence: `/tmp/remote-surface-guard-shop-plain.txt` and `/tmp/remote-surface-guard-shop-qt.txt`. The driver independently verified both commits and authorized restoration of only that original Qt override under standing rule §38.1. All other pins, root digest, serializer, assertions, and thresholds remain unchanged.

## Focused coverage

The added setup canary uses temporary directories, actual rsync, and an executable interpreter link. It synchronizes twice, repeats each link creation without an intervening sync, verifies the canonical mirror basename, and rejects any nested `.venv-qt` link inside the shared virtual environment. It verifies the old mirror and report sentinels remain. The original raw-rsync incoming Studio symlink rejection test remains unchanged.

The complete focused MacBook rerun passed: `Ran 16 tests in 13.765s`, `OK (skipped=1)`. Both the strengthened setup canary and original raw-rsync rejection test passed. The unchanged Qt root guard and all first-wave environment digests executed and passed. The single skipped test was `ModuleSurfaceTest.test_root_initializer_is_reported_as_unavailable_without_aqt` in `tests/test_module_surface.py` (removed with the surface digest pins in cd9034ea), with reason `root initializer requires aqt; use the offscreen Qt interpreter`. Exact log: `/tmp/remote-surface-guard-focused.txt`; remote log: `/Users/armantarkhanian/ankiscape-remote-test-host/reports/remote-surface-guard-focused-2026-09-05.log`.

Static validation passed: documentation audit covered 654 Markdown and 445 HTML files; test-quality audit reported 4686 tests across 245 files, zero hard issues, and 31 structural clone candidate groups. `git diff --check` and the worktree safety audit passed. Independent review and its corrections are complete. Both full MacBook lanes and post-merge gates are still required.

## Independent review and durable evidence

The Opus review accepted the core repair and identified two adjacent corrections: the Qt executable check must run before both lanes, and the runbook must name the active canonical mirror in its sync description and environment rebuild commands. The existing check now runs in common preflight; the lane thresholds are unchanged. `memory-bank/remote-test-host.md` now documents the canonical mirror and the remote-local interpreter link.

The driver and author each verified that `ui/ui_tab_shop.py` at `4ba6568d16586fe833ee2526c4ae11d3a03ee06c` and `ffb846d6631e4b73731f6573dd8d7c0e77e439db` has the same Git blob: `dd444e90509aaf9907cbf9c1d9042dbf3136612c`. `git diff --exit-code 4ba6568d ffb846d6 -- ui/ui_tab_shop.py` returned 0. The original per-environment shop pins therefore apply to the same source.

The four full dumps are preserved under `memory-bank/source-audits/evidence/remote-surface-guard-2026-09-05/`. Its `manifest.json` records each plaintext hash, compressed hash, byte counts, source commit, serializer blob, command, origin directory, and interpreter environment. Gzip uses compression level 9 with mtime 0. The files total 21,462,933 bytes before compression and 1,859,096 bytes after compression. A round-trip check verified every hash and byte-identical recompression. The decompressed root payload comparison again found only the two authorized records. The restored candidate root is byte-identical to the pinned root dump, so a duplicate candidate dump is unnecessary.

The measured host is `macOS-26.4-arm64-arm-64bit-Mach-O`, with Python `3.14.6 (main, Jun 10 2026, 10:03:53) [Clang 21.0.0 (clang-2100.0.123.102)]`. The Qt environment contains `anki==25.9.4`, `aqt==25.9.4`, `PyQt6==6.11.0`, and `PyQt6-Qt6==6.11.1`. No package was installed or changed.

The final corrected focused suite passed on the MacBook: `Ran 16 tests in 13.765s`, `OK (skipped=1)`. Both lanes rejected a deliberately absent Qt interpreter before sync; both accepted the real interpreter and their prerequisites. The exact negative-preflight reports were `remote plain prerequisites failed after 3 attempts: no output` and `remote qt prerequisites failed after 3 attempts: no output`. No canary directory or interpreter was created. The mirror returned to the driver after the focused suite completed.

The final root edit changes only its existing import:

```python
from .runtime.runtime_actions import BIG_CHINCHOMPA_UTILITY_ID, EVIL_TREE_UTILITY_ID, RuntimeActionContext
```

The complete root dump after this import change is byte-identical to the stored pinned dump. A separate MacBook identity probe asserted that each root export `is` the corresponding data-module object; both assertions passed. The final focused suite again passed all 16 tests with the expected plain-root skip. Root line count and import fan-out are unchanged; the original hook rejection is recorded in the pending papercut note.
