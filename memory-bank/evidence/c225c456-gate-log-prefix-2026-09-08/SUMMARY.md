# Raw evidence retained outside the checkout

Moved 6 files recursively from `memory-bank/evidence/c225c456-gate-log-prefix-2026-09-08/` (6 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/c225c456-gate-log-prefix-2026-09-08.sha256.tsv`; SHA-256 `686794a388a98ca427cc989178e4e87822bc3096a0bc3ca47b637737d0a5e27f`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).
Moved files (SHA-256, producing commit):
- `before-final-stdout.raw.log.gz` `2c51d277373a43d911cb1ce7acd6a504cde5c90712f724ef7856f618aac3b5dd` `afca8a376cb6868f427fabea930786d85678c8b4`
- `final-overwritten.raw.log.gz` `b80259816cb46ae7b460a29364e066e6d22d746b3661c1fa209094557f175cc1` `afca8a376cb6868f427fabea930786d85678c8b4`
- `identity.json.gz` `565c51f49512fac22fc7fd6636349efc958f970ee391e709cab3358dba50514b` `afca8a376cb6868f427fabea930786d85678c8b4`
- `manifest.json` `c4411dba4cee575a55b94a862696baa7b8c41f49fd5718653a047beffda71897` `afca8a376cb6868f427fabea930786d85678c8b4`
- `reconstructed-complete.log.gz` `687d66cf8e21158071e525fe1f9e2124b42dca6f50b189819c397a9887e3778c` `afca8a376cb6868f427fabea930786d85678c8b4`
- `reconstruction.json.gz` `a203b77ca7fe63beb2d8436af79813fed334305c8ec945efaf75ffd67349856c` `afca8a376cb6868f427fabea930786d85678c8b4`
