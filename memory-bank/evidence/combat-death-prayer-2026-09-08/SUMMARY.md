# Raw evidence retained outside the checkout

Moved 85 files recursively from `memory-bank/evidence/combat-death-prayer-2026-09-08/` (43 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/combat-death-prayer-2026-09-08.sha256.tsv`; SHA-256 `728a46e2092ea90988a9df2789d6da0bc800fd599264f505f81d3a814c6f3f6f`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).

Live inputs stay in the checkout:
- `baseline-engine.py.gz` — `tools/combat/compare_death_prayer.py` reads it.
- `baseline-specials.py.gz` — `tools/combat/compare_death_prayer.py` reads it.
