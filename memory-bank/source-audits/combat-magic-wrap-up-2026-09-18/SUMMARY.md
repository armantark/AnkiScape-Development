# Raw evidence retained outside the checkout

Moved 6 files recursively from `memory-bank/source-audits/combat-magic-wrap-up-2026-09-18/` (6 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/source-audits/combat-magic-wrap-up-2026-09-18.sha256.tsv`; SHA-256 `3c5282ce2e873f7290bbd5ee083892c71aab725fcc3cef6b8374e5c1066a3f55`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).
Moved files (SHA-256, producing commit):
- `ankiscape-magic-source-plain-failure-2026-09-18.log.gz` `eec4e0a67f65334000257380425f2a5e1e580bada8b1139fbf7af170abf81a0e` `7eaa9910e59c587eb9c4ebac05b8d0bcc9883219`
- `ankiscape-magic-source-plain-failure-2026-09-18.log.json` `016c83a344b44c71500aca675bbb1434a3820d945822b7c254447f5bbdf7eed8` `7eaa9910e59c587eb9c4ebac05b8d0bcc9883219`
- `full-source-gate-result.json` `bfed9b2ec68e621bd0c0cf5267af1151c1346cb09d99f78f9bd5be3850172ec0` `7f736d5c63ca0d301b1789798e75fa2737435f4c`
- `full-source-gate.log.gz` `d377a6ea15e0abf882fbf394e4e6fea15bf0d0c0aa3eb9dca0afe4c7d55f1b1d` `7f736d5c63ca0d301b1789798e75fa2737435f4c`
- `root-final-retention.json` `abc05a2965444d4ae01f52af49223f6654918e7c7b0dea8a59631c42014ec03f` `c1741c3d2fbb14c36f9e759ac97b99d3f36e133f`
- `source-qt.log.gz` `65f4f267f8273d1ee5f5e329ca44a64a802676ae433cdb27148ca02e9020fa3d` `7f736d5c63ca0d301b1789798e75fa2737435f4c`
