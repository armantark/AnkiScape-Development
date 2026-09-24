# Raw evidence retained outside the checkout

Moved 28 files recursively from `memory-bank/source-audits/cape-tradeability-implementation-2026-09-05/` (9 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/source-audits/cape-tradeability-implementation-2026-09-05.sha256.tsv`; SHA-256 `2fed72bc58de7f77d3edddf938c45944c82e1c35653358e4d8c4304676c2d9cc`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).

Live input stays in the checkout:
- `owner-snapshot.json` — `tests/item_tradeability/test_cape_tradeability.py` reads it.
