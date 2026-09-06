# Run the remote surface guard without weakening it — 2026-09-05

## Proven defect

The existing remote Qt lane skips both root-surface tests because tests/test_module_surface.py expects ROOT/.venv-qt while the runner excludes that directory and uses an external virtual environment. A separate unchanged-main probe at ffb846d6631e4b73731f6573dd8d7c0e77e439db, with canonical package basename ankiscape_fork and the expected Qt symlink, executes the test and fails. Its root digest is fa36126b7ddff3d7d7d6582f80a12000d811533689fe3330e4e3864bb8641732; the pinned digest is 2625d3d2bb6110c0faee0a33863cf1bf8e921fe0591460eed25d071bec85e26d.

The commit that introduced the pin, 4bdc1596, reproduces that exact pinned digest on the same MacBook interpreter and canonical package basename. A full dump comparison proves that unchanged main differs only by missing the public BIG_CHINCHOMPA_UTILITY_ID and EVIL_TREE_UTILITY_ID records, with values big_chinchompa and evil_tree. No environment-normalization or pin change is needed to repair that regression. Evidence: /tmp/dispatcher-state-pinned-canonical-surface.txt, /tmp/dispatcher-state-baseline-canonical-surface.txt, and /tmp/dispatcher-state-baseline-root-pin-probe.txt.

## Owner and implementation boundary

The dispatcher_state agent temporarily owns this prerequisite slice in goal/remote-surface-guard-2026-09-05, safe pool slot 8, lease 51d6a51f4b7625e308b3300a9c4d0d5b. Its state restructure remains separate in pool3. The driver owns this plan and all promotion; the author may include the plan in the branch commit.

Restore the two public imports at their original root import sites. Preserve all current runtime bodies and the complete pinned public surface. Repair the remote runner setup so its disposable mirror has the canonical ankiscape_fork package basename and exposes the already-installed remote Qt interpreter at the path the unchanged tests expect. Recreate only that known remote-local virtual-environment symlink after sync; continue excluding and removing incoming Studio virtual-environment symlinks. Preserve the old mirror directory and all reports; do not delete user state or repurpose it. No installed dependencies, global configuration, product UI, state-object implementation, source values, or live Anki profile may change.

Keep tests/test_module_surface.py, all digest values, serializer semantics, lane thresholds, and unrelated audits unchanged. Add only focused regression evidence for safe remote mirror setup and for actual root-guard execution; do not broaden the repair. The original raw rsync boundary test must keep rejecting copied Studio symlinks. If the gate reports another real difference, record exact evidence and diagnose it rather than relax a check.

## Verification and promotion

CHECK: the restored root matches the existing pinned digest in the real remote environment, and the Qt root guard actually executes without a skip. EXPECT: the existing measuring instrument now detects future root-surface regressions. Prove the focused setup behavior on the MacBook and preserve its canary cleanup boundary; no product test runs on the Studio.

Require a complete diff, source/Memory Bank evidence, focused regression coverage, independent cross-lineage review with findings resolved, an attributable agent-authored branch commit, and both full MacBook lanes plus all repository checks. The orchestrator then merges in a separate worktree, repeats the full gate, and lands only the exact verified tree on canonical main. Never push or bypass hooks. No author main commits, destructive Git, configuration change, installation, sibling-task messages, child agents, or HTML artifacts.

## Restore the original Qt-specific shop pin — 2026-09-05

Enabling the previously skipped Qt interpreter exposes a second recorded instrument defect. Commit 4ba6568d originally pinned the unchanged shop module to plain digest 3a4cb59b8b9881f1eb788a745e37044532ecd1bbb309d7c6cbcf0463a6572056 and Qt override 2ddacc925cbf537db4587117312620d7d1546e9fad2ff9c0f167afea710d09db. Commit d89b31ac replaced both entries with the plain digest. Current full dumps on the MacBook reproduce both original per-environment hashes; ui/ui_tab_shop.py is unchanged since the original instrument commit.

The dump difference consists of 17 real Qt class imports and CatalogFilterBar's Qt signature, whose non-Qt stub supplies two empty-string defaults. This is a genuine conditional import surface, covered by ruling 38.1. Evidence: /tmp/remote-surface-guard-shop-plain.txt and /tmp/remote-surface-guard-shop-qt.txt; driver independently inspected both historical pin commits.

The driver authorizes restoring only QT_DIGEST_OVERRIDES["ui/ui_tab_shop.py"] to its original exact Qt value, 2ddacc925cbf537db4587117312620d7d1546e9fad2ff9c0f167afea710d09db. Keep the plain pin, root pin, every other digest, serializer and assertion unchanged. This named historical restoration is the only exception to the earlier no-pin-change boundary. Require the complete existing module-surface test suite to pass with the Qt root guard executed.
