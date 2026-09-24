# Raw evidence retained outside the checkout

Moved 21 files recursively from `memory-bank/evidence/barcrawl-clean-fixture-2026-09-18/` (20 listed in the local manifest).
Each original path is stored byte-for-byte at `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/<producer-commit>/<original-path>`.
Local digest manifest: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/manifests/memory-bank/evidence/barcrawl-clean-fixture-2026-09-18.sha256.tsv`; SHA-256 `c2360f97a7d7ed264dd85f4014f9340daa4bc72c6b07d7eb09bd38078aa7f98a`.
Producer lookup: `git log --diff-filter=A --format=@@@%H --name-only -- memory-bank/evidence memory-bank/source-audits` (use `-m` for merge additions).
Byte checks run before removal: `git show "HEAD:$artifact" | shasum -a 256` and `shasum -a 256 "$evidence/$commit/$artifact"`.
Complete digest index: `$(git rev-parse --git-common-dir)/ankiscape-promotion-evidence/goal-evidence-out-of-tree-2026-09-23/migration-index.tsv`; SHA-256 `7f6ffac777c0d0f0d44ffd46fca43d2c425befb5706d6d10ec69b7fccd1a790c` (includes subdirectories).
Moved files (SHA-256, producing commit):
- `baseline-gate.log` `81c6570e531aaeca29b6927290c3a1b360e69c5ddb447fd803aa9d2aae389014` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `failed-green-wrapper-plain.identity.json` `3be3e12775bed9429ba8dce877160ebc2f8c2a743ad80b82a0a4067e4f38128b` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `failed-green-wrapper-plain.log` `22a6675140a1c568864aca3f10ed59f7def5b8feccfaef3d4a078f2ceeb71915` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-plain/accepted.json` `71d77219ff6b651f4979dc1dae81c187f82b686dc5cf26dfb9fa997d5dddafe3` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-plain/completion.json` `bd8009f7cb062a9ee19d320a15e02e6793554b9fbdfc7cd416999fe888976645` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-plain/driver.log` `7c2ef16a4d2bc87e9e68210810a3b8b7a5204dfefcd63d4823dc5188164dfcbe` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-plain/identity.json` `2e72194c7d15d3a4f65849354030b6e5e844de131a402e34ddfc2ffcc5e9443b` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-plain/run.log` `095d92113a8bdab449eea23927984466eb79b322369073606f7a6dd07c308b6e` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-qt/accepted.json` `71d77219ff6b651f4979dc1dae81c187f82b686dc5cf26dfb9fa997d5dddafe3` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-qt/completion.json` `bd8009f7cb062a9ee19d320a15e02e6793554b9fbdfc7cd416999fe888976645` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-qt/driver.log` `8793e1035d4d5e22cba46a5a0fcbadd3568cdcde8563490d7184834a90252e4d` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-qt/identity.json` `9d7f46d02a7a62ccfb75e9681e0c23dc52f94f0c83e4b2f87f9ead0fe113f9ab` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `focused-qt/run.log` `88c177732413ec962af4fb566b1fd4944796eb77287637ea2126818a45e6dbd5` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `full-source-gate/gate.log` `0e2a31ed76e9f85bacc920b1f847b270fb12cb2a17c50cf1687ac058d17e583a` `7b2486a84ce6aad446df03d8d177bbddd9c5d5d1`
- `full-source-gate/manifest.json` `584476d40ccc73d129b8c0fab7835ef55c36eb72cb5d5ee9910220a63c66ab79` `7b2486a84ce6aad446df03d8d177bbddd9c5d5d1`
- `manifest.json` `814857ed37f9006cd50408e7fa4d5b38dd9ee63610a2415a4f304b462efb63e7` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `narrow-red.identity.json` `5312af73f668cc6de00a56f6d7eb16bcf78747f7237e69d6ca0661e7242d04fc` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `narrow-red.log` `1e618ee21c891a279338e1d5b7dcda85f4fa9db09d5da39dd3df63adc1fcb65b` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `review.stderr.txt` `bb3f1c9457b62c9237c30030c0871832afd92e6ef835bbcdb3eb3fa9fab23f86` `0bd11b878969a513c61c5080c5c32cf63741976a`
- `review.stdout.txt` `b97ba3021dda57f06bb81382e8a7aa9ae30cbea101d157fa206b9cd11cd11200` `0bd11b878969a513c61c5080c5c32cf63741976a`
