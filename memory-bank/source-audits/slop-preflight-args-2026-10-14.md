# Preflight argument safety: source proof

Base: landed main `2e7b6378871e0096515e1aaab7a64061c7aff7bc`.
Help and unsupported options now finish before any Git/index/gate operation. No-argument invocation still delegates to the installed gate with unchanged diagnostics and exit status.
The two prepared CLI regressions fail on original source through a disposable fake Git refusal. That canary stops before any valuable index or gate is exposed.
The complete existing/new focused suite has four tests, exit 0, no skips; the no-argument gate cases preserve real fixture index bytes and status.
The exact original incident moves verbatim through the existing preservation utility. No cap, hook, audit, preset or baseline changes.
Receipts bind the recorded dirty source by per-file digest. Independent source review, exact merged full remote-lane gate and official land remain pending.

| Original artifact | SHA-256 |
| --- | --- |
| `failure-modes.md` | `35fe1021ba1883eabb2a89b8d5d88d056b667917714b1739f747661a46e99d41` |
| `baseline-inventory.log` | `8f225756ce4db37c9c86c5084fa0842c75054a0e64149b615664d08f92e7328a` |
| `baseline.log` | `d9d77bf73013e1ef040de9b8f173acc4dcb5a785a0d043408e5717de3207c119` |
| `baseline.receipt.json` | `9e53fd563901e2bafcfdca5b5d20722986da5d720edd8fb3272af0cb3c00239b` |
| `green-inventory.log` | `4a4d4ad17b49d07555d90431bdc19f08d4c24959c3872824aec8c4394e000c00` |
| `green.log` | `bd2eba4a1aba0f8807e9d8258c30dcf3e40ae4617731a6d921be6e741dd38e89` |
| `green.receipt.json` | `41a7b64fa108d1f2a93d856738c2dd070551f36c2e48ac1c9dc112f690aeed20` |
| `move-plan.json` | `7236f39eb0fd81cf9d4c4d3d5ecdb700adf12226647f15ae4a66cd1603e683b3` |

Raw evidence: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/slop-preflight-args`.
