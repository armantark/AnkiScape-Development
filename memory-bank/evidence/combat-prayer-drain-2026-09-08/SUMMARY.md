# Raw evidence retained outside the checkout

Moved 72 files recursively from `memory-bank/evidence/combat-prayer-drain-2026-09-08/` (30 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/combat-prayer-drain-2026-09-08.sha256.tsv`; SHA-256 `4d7311894f543ebb9d795d6c5c9e4437ceeb228d64ac2df01f0d2009e91fe7a6`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).

Live inputs stay in the checkout:
- `baseline-engine.py.gz` — `tools/combat/compare_prayer_drain.py` reads it.
- `baseline-specials.py.gz` — `tools/combat/compare_prayer_drain.py` reads it.
