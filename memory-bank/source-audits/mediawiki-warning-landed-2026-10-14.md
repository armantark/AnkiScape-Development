# MediaWiki warnings stay visible — 2026-10-14

Exact commit69a22761bedb6b269e0b34d1dcf0b05c7d595470 is officially landed on clean main.
The shared asset client writes nonempty MediaWiki warnings to stderr and returns the complete valid payload unchanged. Empty warnings remain silent; no UI, prices, cutoff or retry policy changed.

[Astra review](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/c2-warning-astra-review/verdict.json) and [Zhipu review](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/c2-warning-glm-review/verdict.json) accept the final source with no findings or valid simplification deletions. Root verified the reviewed bytes and receipt bindings. The Zhipu comment about other decoders is outside scope and establishes no owner decision.
The original red run reports two tests and three failures. The final focused run reports29 tests/2.254s/no skips/actual0. Its inventory excludes the two existing static-Pillow skips.
[The exact gate](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/c2-warning-contract/exact-merged-verification/exact-gate-verified.json) passed all nine checks with remote_lanes=true, plain_only=false and actual0: plain5332/595.112s/580 skips; Qt5332/851.615s/5 skips.
[Official land](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/c2-warning-contract/exact-merged-verification/official-land-receipt.json) returned0; exact main was clean. No push occurred. The successful normal source commit transcript is retained; no separately logged hook-internal claim is made.
[The retention receipt](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/warning-diagnostic-retention.json) records42 files/133833 bytes/actual0, manifest SHA256`a0fe16fd2d69ad47a3322ced4b526b7c18cdf63efaf0877b11a6e3aa562ed18b`.
