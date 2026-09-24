# Raw evidence retained outside the checkout

Moved 109 files recursively from `memory-bank/evidence/unproductive-activity-selector-2026-09-08/` (28 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/unproductive-activity-selector-2026-09-08.sha256.tsv`; SHA-256 `2d3dde87bea1d87603d100174810e5db8956e9b777d413a9640223f3f7ad36e0`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).

Live inputs stay in the checkout:
- `baseline-entrypoint.py.gz` — `tools/runtime/compare_unproductive_activity_selector.py` reads it.
- `baseline-runtime-actions.py.gz` — `tools/runtime/compare_unproductive_activity_selector.py` reads it.
- `selection-rows.json` — `tools/runtime/compare_unproductive_activity_selector.py` reads it.
