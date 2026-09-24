# Raw evidence retained outside the checkout

Moved 31 files recursively from `memory-bank/evidence/carried-processing-reconciliation-2026-09-07/runtime-hook-corrected-2026-09-07/` (2 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/carried-processing-reconciliation-2026-09-07/runtime-hook-corrected-2026-09-07.sha256.tsv`; SHA-256 `184d849c38777e80ad56aaf0691ba45ac2d9bbe9252defd274f68cf0e9c467c2`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).
