# Raw evidence retained outside the checkout

Moved 92 files recursively from `memory-bank/evidence/combat-food-module-2026-09-08/` (50 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/combat-food-module-2026-09-08.sha256.tsv`; SHA-256 `274a2763d8024513e726be166a42cc285879505fe067e572ebc8ac6237f3da20`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).

Live inputs stay in the checkout:
- `baseline-engine.py.gz` — `tools/combat/compare_preview_food.py` reads it.
- `baseline-model.py.gz` — `tools/combat/compare_preview_food.py` reads it.
- `baseline-supplies.py.gz` — `tools/combat/compare_preview_food.py` reads it.
