# Independent review dispositions

The raw Opus review is retained in `opus-source-review.txt`. Its verdict accepts the source audit for retention with eight corrections. It did not recompute hashes or run code. This document records each disposition; no review claim changes product behavior or source policy.

| Review item | Disposition | Result |
| --- | --- | --- |
| 1. Shield code versus qualification summary | Clarification accepted; the claim of an omitted source check is not accepted. | The original contract already said that the current Darkan action checks 56 and separately quoted the qualification summary. The revised contract now includes the exact function excerpt, supplying commit, and explicit separation between the two. |
| 2. Additional quest references to 56 | Accepted as context, not independent evidence. | Both literal lines are retained in the contract. The same article contains the shield, split-log and overall production statements. Three statements in one article do not provide independent corroboration. |
| 3. Search hierarchy as authority ranking | Rejected. | The standard explicitly names two axes: search order and corroboration. It does not rank Darkan above contradictory period evidence. The check comes from a July 2026 restoration and its independence from the cited quest article is not established. Neither 54 nor 56 is promoted by provider or search position. The source field remains blocked. |
| 4. Emerald attachment XP divergence | Accepted. | The contract records that restored Darkan makes no XP award while period item revision 5504656 explicitly awards 20 Crafting XP. The missing implementation award is not evidence for period zero XP and does not create another source blocker. |
| 5. Emerald enchant level divergence | Accepted. | The contract records Darkan's explicit Magic 49 check and distinguishes it from standard Level 2 Enchant at 27. The own-quest eligibility still requires Magic 49, so this difference is unobservable on the valid route. The proposed implementation must preserve that quest gate. |
| 6. Rod ID framing | Accepted in part; authority ranking rejected. | Current Anki's raw 7637 is explicitly described as disputed implementation data. Darkan's 7620-to-7637 mapping is retained with its supplying restoration history, not promoted because Darkan appears first in search order. Numeric state identity remains blocked. |
| 7. Mould retention provenance | Accepted. | The dated walkthrough does not state retention. The contract now attributes it to the current recipe's retained `required_items` and the existing 2011 action, which checks the mould but removes only the Silver bar and extra ingredients. Exact source excerpts and hashes are retained. |
| 8. Existing start-side Crafting gate | Accepted. | The plan names `_can_start_crafting_action` at `runtime/runtime_actions_gates.py:589–596` and reuses its pure readiness function. Only the missing matching mutation-side check is proposed; the existing start check must not be duplicated. |

The minor wording correction is also applied: the quest says “two arctic logs”; the shield article says “two [[arctic pine logs]]”.

Local history attributes `craftShield` to `adb5dd15fe6272fd3c639d5de698f3633ba117b0`, the rod identity constants to `d335ce5e37e9cdc19286dc5efb8c95ce93c8d6ee`, and both Legacy preparation functions to `63b3c901cb8debf42d66cbf50fe84eaeb79fcc92`. These are supplying restoration commits. They establish local provenance, not historical correctness or independent corroboration.

The original review packet remains frozen under `tmp/review/genuine-quest-actions`. The updated audit is available for the parent's targeted document review. Product implementation, source fetching, runtime work, MBP access, staging and committing remain unauthorized at this step.
