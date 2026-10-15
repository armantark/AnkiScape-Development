# Historical asset timestamps cannot bypass qualification — 2026-10-14

Exact commit812e0ec1a4378af5e1128edd4cd336116b4faa84 is officially landed on clean main.
The shared client refuses missing, empty and nonstring historical timestamps before download or provenance writes.
Valid period/exact-cutoff selection and nonhistorical behavior remain exact. No UI, artwork or cutoff changed.

[Sol review](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-cutoff-timestamp-sol-review/verdict.json) and [Zhipu review](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-cutoff-timestamp-glm-review/verdict.json) accept the final bytes with no findings.
The original red proof has five failing subcases across two tests. Final27 supported cases pass without skips.
The earlier remote focused run precedes the redundant-branch cleanup; the final local receipt binds the committed code.

[Exact gate](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-cutoff-timestamp/exact-merged-verification/exact-gate-verified.json):all nine checks pass, remote_lanes=true, plain_only=false, original outer exit0.
Full plain:5330 tests/595.358s/580 skips. Full Qt:5330 tests/804.317s/5 skips.
[Official land](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-cutoff-timestamp/exact-merged-verification/official-land-receipt.json) returned0. Root verified the exact clean main; no push occurred.

[Retention receipt](/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/asset-cutoff-retention.json):49 files/136260 bytes, original exit0; manifest SHA256`61d25398d6b196de5d956954130aac30f5b5fc46f0d4e4b217f645b3acedaade`.
The source hook success remains Root-observed without a separate transcript. This does not replace the accepted exact full gate.
