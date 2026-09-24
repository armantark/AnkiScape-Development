# Raw evidence retained outside the checkout

Moved 3 files recursively from `memory-bank/evidence/pass9-2026-08-11/` (3 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/pass9-2026-08-11.sha256.tsv`; SHA-256 `029ead5133958156bb08d0674c4045173957c66f52ff99b7cdadb530494cb327`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).
Moved files (SHA-256, producing commit):
- `native-combat-target.png` `504874a0c4e196a2ba161921c6460f1acdc350fbbbf038594474f94ed44021b9` `7ba4e5d61ef82711dfda03004edf8b9613872eee`
- `native-level-up-dialog.png` `df54da2f48a8d1062202ea1c959dfcac88499bc2e2a1bca92ceb7fdacb45e0ae` `7ba4e5d61ef82711dfda03004edf8b9613872eee`
- `native-slayer-guide.png` `7b5401ed4e8eb87edf659311bb22bc8c55c35fd120d21368d03738ec421284ba` `7ba4e5d61ef82711dfda03004edf8b9613872eee`
