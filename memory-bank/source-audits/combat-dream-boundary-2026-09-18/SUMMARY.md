# Raw evidence retained outside the checkout

Moved 6 files recursively from `memory-bank/source-audits/combat-dream-boundary-2026-09-18/` (6 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/source-audits/combat-dream-boundary-2026-09-18.sha256.tsv`; SHA-256 `2a6c553aed04d6ff9e377ed60651560fdcd13c9fd8f98d132f9be08f39b2980b`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).
Moved files (SHA-256, producing commit):
- `manifest.json` `8f621d077479d9c835c792377af6b76e1cf13fe7ebb882d07e6f6d775a866238` `14d12c04e6a6b20d6abe0d6c1179bf219295331d`
- `opus-review.stderr.txt` `1a548cb5edfa76b2fe7fe4ea6be8002f830b8ee0823a2ff84895d189db63448e` `14d12c04e6a6b20d6abe0d6c1179bf219295331d`
- `opus-review.stdout.txt` `f12557ee21527af490346b166e7f573fca74205423596c3b1309fc66dbc16b96` `14d12c04e6a6b20d6abe0d6c1179bf219295331d`
- `proof-preparation/disposition.json` `585ee50da50942811f84820249ac84eef7f0199a9f7c50dbc7b81012e83a5709` `c1741c3d2fbb14c36f9e759ac97b99d3f36e133f`
- `proof-preparation/independent-review.stderr` `4eb1e3527b3d35b2dfe8a31a3b9ac76a301164ff655aeb804555ea1064368b5f` `c1741c3d2fbb14c36f9e759ac97b99d3f36e133f`
- `proof-preparation/independent-review.txt` `bb5c7b0ada413572b84429718c55dea360ba6fb53269335220b3fd52d3efae6a` `c1741c3d2fbb14c36f9e759ac97b99d3f36e133f`
