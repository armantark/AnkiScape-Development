# Raw evidence retained outside the checkout

Moved 121 files recursively from `memory-bank/evidence/carried-processing-reconciliation-2026-09-07/` (58 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/carried-processing-reconciliation-2026-09-07.sha256.tsv`; SHA-256 `bb633a12440fefa3a9b6f2a90668c1de39ec08b1c94a2f974db217d7f5806ce3`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).

Live inputs stay in the checkout:
- `baseline-overlay.py.gz` — `tools/carried/compare_processing_reconciliation.py` reads it.
- `final-source-manifest.json.gz` — `tools/carried/run_processing_reconciliation_remote.py` reads it.
