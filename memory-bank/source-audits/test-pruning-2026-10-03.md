# Current test-pruning proof, 2026-10-03

Baseline: `d2aa35d20d7b8ef18f2af42f88018641b439a8c8`. The owner selected lean pruning in design-thread queue section 4.30.

The ten assertion trims landed at `d2aa35d20d7b8ef18f2af42f88018641b439a8c8` through the official land command after all nine promotion checks passed. The exact receipt records `remote_lanes=true` and `plain_only=false`. Both lanes ran 5223 tests: plain 453.956s with 581 skips; Qt 673.591s with 7 skips. Root verified all nine final test-file hashes on main. No test method was removed in that slice.

Current review of all 614 historical nominations yields 601 keep, 10 landed assertion trims and 3 qualified method deletions. Sol and GLM agree on each deletion; root verified the actual methods, fixtures and surviving fault assertions. Of 35 covered nominations, 32 stay. Firemaking stays because its independent fixture and lane gap remain.

The deletion operator passed ten refusal canaries without writes. It removed three methods across three files, with 24 net lines removed. Whole-module AST comparisons show only these method deletions. All three broader methods and the Firemaking file remain unchanged. The candidate still needs its own exact full promotion gate and official land.

The fresh coverage subset contains 146 cases, with 21 plain skips and no Qt skips. Independent raw-map verification passed. This subset is not a whole-suite coverage map. The collector ran on frozen `58438c4dbcd38f189cd2b3fd2b05933c901ce8a6`; root verified the cited small and broader source bindings unchanged on the deletion base.

The three deleted methods are the level-calculation multi-level case, the claimed-diary-item wear case and the chosen-skill lamp case. The surviving broader checks drive the multi-level popup and log, committed diary claim and wear, and a combat challenge through lamp rubbing.
The two wolf shared-drop identity assertions remain. No gameplay, UI, audit, limit or pinned baseline changed.

Ten-trim gate receipt SHA-256: `cd49b341456a4543c526eb9d80e1a38ad83ecc9ab119094b2e0d7c72a69ac0b8`.
Ten-trim post-land evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/test-prune-2026-10-01/ten-trims-postland-2026-10-04/retention-manifest.json`.
Current covered review and operator evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/test-prune-2026-10-01/current-covered-reviews-2026-10-04/retention-manifest.json`.
Qualified deletion plan SHA-256: `ef229f99fb8251173a55ebb409d672b751ae7775c3134d99f8d2ab8659b0190b`.
Final source binding SHA-256: `f19a32c3269bd7e8955f503bfd2a13888bd41cf18d3ebb0922790480ec7e8141`.
Coverage evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/test-prune-2026-10-01/current-covered-measurement-2026-10-04/retention-manifest.json`.

A replay gate loses a removed assertion; replay alone cannot establish independent fault protection.
