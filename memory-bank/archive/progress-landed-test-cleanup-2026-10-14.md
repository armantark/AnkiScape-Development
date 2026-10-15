# Landed assertion and method cleanup checkpoint

Historical completed work, preserved verbatim from progress.md. Current source and native queues stay in activeContext.md and their source checkpoints.

Root verified main `ca859eb0ef06a0b298d25bcedd9338a1120afabc` clean at 2026-10-04T04:24:05.550171+00:00. Seven October 3 landings are on main: documentation `06480995`, S01 `046d5f53`, S03 `da02e004`, S12 `58438c4d`, assertion trims `d2aa35d2`, covered-method deletions `28481d9295db918396d5d0188f69c1ea36f102b5` and documentation `ca859eb0ef06a0b298d25bcedd9338a1120afabc`.

The ten assertion trims landed at `d2aa35d20d7b8ef18f2af42f88018641b439a8c8` through the official land command after all nine promotion checks passed. The exact receipt records `remote_lanes=true` and `plain_only=false`. Both lanes ran 5223 tests: plain 453.956s with 581 skips; Qt 673.591s with 7 skips. Root verified all nine final test-file hashes on main. No test method was removed in that slice.

Current review of all 614 historical nominations yields 601 keep, 10 landed assertion trims and 3 landed method deletions. Sol and GLM agree on each deletion; root verified the actual methods, fixtures and surviving fault assertions. Of 35 covered nominations, 32 stay. Firemaking stays because its independent fixture and lane gap remain.

The deletion operator passed ten refusal canaries without writes. It removed three methods across three files, with 24 net lines removed. Whole-module AST comparisons show only these method deletions. All three broader methods and the Firemaking file remain unchanged. The three-method deletion slice landed at `28481d9295db918396d5d0188f69c1ea36f102b5` through the official land command. All nine promotion checks passed. Both lanes ran 5220 tests: plain 461.986s with 581 skips; Qt 677.356s with 7 skips. The exact receipt records `remote_lanes=true` and `plain_only=false`. Root verified all three final test-file hashes on clean main.

The fresh coverage subset contains 146 cases, with 21 plain skips and no Qt skips. Independent raw-map verification passed. This subset is not a whole-suite coverage map.

