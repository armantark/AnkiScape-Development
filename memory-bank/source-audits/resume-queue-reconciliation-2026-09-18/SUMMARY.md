# Raw evidence retained outside the checkout

Moved 6 files recursively from `memory-bank/source-audits/resume-queue-reconciliation-2026-09-18/` (5 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/source-audits/resume-queue-reconciliation-2026-09-18.sha256.tsv`; SHA-256 `4a56d6c616f2d0d809d999683f69bbf86a76a89fcbcb604ae5fd70e37c468544`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).
Moved files (SHA-256, producing commit):
- `full-source-gate/gate.log` `50aaf169b8f95006ebca587464bdf155682f9026e4daa0fbea3a274679e9c4f7` `24fa1487d1cb5cc503e5eac90b319269d20b0503`
- `full-source-gate/manifest.json` `555fdc1b6d2717ef145bb6ccb3a20f5d1e03f4c32914350790ff2bf43b00ad34` `24fa1487d1cb5cc503e5eac90b319269d20b0503`
- `opus-review.stderr.txt` `e32933c3e7308af68c980b23b79041ff53c3f9d4d98d5be733457a3cfe11eeea` `953d5197f1bb7d323f2c44958277c5c913a739d6`
- `opus-review.stdout.txt` `7fb1f1f3c3ca27b9930942bccd1ea38f68e05a3abf7b9d9cdb56b2afa0b99cde` `953d5197f1bb7d323f2c44958277c5c913a739d6`
- `review-retention.json` `4e81e3e8f2e9770267297107e3583b9ac84e65e957aa8d152cd6eb50d55ca590` `953d5197f1bb7d323f2c44958277c5c913a739d6`
