# Native review fixture, 2026-10-07

Source candidate: `9e53240d02a4c6816cb3e003080e0228008e07ea`; base: `d919d479838724fd16bad91c1aff60d67ba488e3`.
Only `tools/native/review_fixture.py` and `tests/skills/test_native_review_fixture.py` are added.
Both equal the preserved source `f7f9d505df9ae830e3a6253047bac4a4aa797078` byte for byte.
Helper SHA-256: `2a3cc5922a7a7f325f8bb60d09d89f5609b8a510cfe30c88ff38cb832d8d0bec`.
Test SHA-256: `59b1de80d6db55a921712f252a58363e9a3cdd229268593595b9dbbd660f3026`.
The explicit helper requires a fresh collection below a resolved temporary base before any collection method runs.
It seeds default game state, the Firemaking scenario and twenty real cards. Normal close and profile reopen remain required.
It does not launch Anki or alter gameplay hooks. Native use remains separate acceptance.
Stock remote inventory collected two tests. The Qt focused run passed both in 0.046s with zero skips and actual exit 0.
That run proves real Collection close/reopen persistence, safety refusals and refusal to reseed. It does not prove gameplay.
Raw focused log SHA-256: `fbd3d5c219296c56e45ed18426270ca14eef998afd3c62faea236e0e2de199f4`.
Astra and Kimi K3 independently approved the exact source with no findings. Both reviews were static; root owns behavior proof.
Kimi raw output SHA-256: `53098ca4707303ec85e27785d0ba95b87d19e483567c19a2b15a1ec67eeccdfb`.
Root retains raw controls and reviews outside the worktree. Official full-gate and landing receipts govern promotion status.
No historical compressed publication or sandbox reports are copied into this slice. The original branch remains preserved.
Retained source proof manifest: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/9e53240d02a4c6816cb3e003080e0228008e07ea/native-review-fixture-proof/retention-manifest.json`; SHA-256 `6f4c47373720cd0ba0a7967d32332721656c391fe52d70c156684eeb78a42ed0`.
