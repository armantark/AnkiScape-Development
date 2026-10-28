# Design queue: owner rulings that remove the nits (2026-10-15)

Owner instruction, 2026-10-15 18:25 PDT, in T3 thread `ea1723e0-072e-47ba-a6bc-bcb2d551734f`: "Remove all the nits from the open design queue with reasons".

Claude Opus 5.5 classified every open item in `memory-bank/design-thread-queue.md` at `main` `839b86a7`. The owner delegated the rulings for nits. The owner answered the one item that was not a nit. No item in the design queue stays open.

## How to apply

1. Record each ruling below as an answered owner decision in `memory-bank/design-thread-queue.md`. Replace the "Open" heading of each item. Keep the evidence links.
2. Update each hold in `memory-bank/GOAL-BLOCKED.md` that cites one of these items.
3. Do not apply a ruling to a case that its reason does not cover. Record that case as a new open question.

## General rulings

These four rulings answer most items. Each item in the table below names the rulings that apply to it.

- **R1. Source-correct content.** Quest journal text, stage endpoints, requirement readouts, start gates and copy can change to match a qualified period source. A level that the source calls "recommended" stops being a start gate. R1 covers text and values only. It does not authorize new widgets or layout changes. Reason: the queue held about 30 separate requests for the same type of change. The fidelity rule already selects the period source. The rule against interface changes protects layout and widgets, not sourced text.
- **R2. Stage-1 endpoint.** Stage 1 ends at the first performed deed in the period source. A talk-only step never ends a stage. Deeds that the source puts in the opening move into stage 1. A quest with branches gets one journal and one endpoint for each branch. Reason: the glossary defines a deed as a performed action, and an earlier endpoint never claims actions that the player did not do.
- **R3. Enforce every constraint that the game can check.** The game enforces weight limits, required or forbidden items, and quiz answers. When the player does not meet the constraint, the quest step refuses the player and shows the reason. Only free-form content that the player must produce and the game cannot check goes in the quest journal instead. The Cold War greeting is the example (`design-thread-queue.md:2924`): "Yeah that's just pedantry. It can save it to the quest journal. The user doesn't have to actually produce it". Owner correction, 2026-10-15 18:35 PDT, after an earlier draft of this rule skipped checks: "It should in fact perform the weight check and kick you out of the quest telling you you're too heavy" and "These should also be enforced".
- **R4. Truncation.** Truncated text in an existing interface is a defect. Fix it without separate approval. Reason: the owner's standing rule says that truncation and ellipses "should always be fixed when seen", unless the design truncates secondary text on purpose and the full value stays one hover away.

## Rulings by item

| Line | Item | Ruling | Reason |
| --- | --- | --- | --- |
| 1519 | Pass-3 shop UI: where the other skillcapes come from | Adopt the recommendation. As each skillcape becomes obtainable, its skill master sells it in the Skillcapes part of the Shop tab, for 99,000 coins, with the hood. Item 2 of this section is already resolved. | The recommendation is the 2012 rule. |
| 1572 | 4.12 Gravestone expiry | Accept the implemented recommendation. | It matches the period behavior at the cutoff. |
| 1578 | 3.22 Dominion Tower reward items | Accept the implemented recommendation. | No source gives the items a bonus block, and this is the smallest invention. |
| 1619 | 3.24 Dominion Factor cost of a defeat | Accept the implemented recommendation. | It is the smallest reduction that makes the source's own advice correct. |
| 2902 | Fremennik shield Woodcutting | Use Woodcutting 56. | The 2012-11-07 revision is the newest source before the cutoff, and the Darkan restoration agrees with it. |
| 2912 | Poison status text | R4. The HUD must show the full text, for example "30 ticks". | The HUD shows "30 t" because the text is cut off. |
| 2916 | Myreque stage transition | R1. The fare comes after completion, as the period contract says. | Source-correct journal text. |
| 2928 | Taste observations about existing content | Move the suggestions to the list for a later design grill. Fix the clipped Challenges and Achievements labels under R4. | These are suggestions, not questions. The goal text sends suggestions to a later design grill. |
| 2932 | First Resort stage 4 | R1: the completed-stage display must not strike actions that the player did not do. Tatty furs are spent before regular furs. Register the order as a declared abstraction. | The display claims actions that did not happen. The source gives no order. Tatty-first keeps regular furs, which Summoning uses. The order has no XP effect. |
| 2936 | Giant Dwarf library load | R3. The game checks the weight of everything that the player carries and wears. Above 30 kg, the quest step refuses the player and says that the player is too heavy. Source the missing item weights as engineering work. Do not count an unknown weight as 0. Another Slice of H.A.M. and The Chosen Commander keep this dependency. | Owner ruling. The limit is a real constraint that the game can check. |
| 2940 | Shop reproduction contract | Remove it from the owner queue. Continue it as engineering work. | The item says: "engineering work, not a new owner-only question". |
| 2944 | Gunnar tab ellipses | R4. | The tab labels show "Ch…" and "Achieveme…". |
| 2948 | Roavar early purchase | The purchase becomes available at the quest stage that asks for it, after the accepted interview. Register it as an AnkiScape abstraction. | No period source gives earlier access. The quest order is the smaller assumption, and the player loses nothing. |
| 2952 | Three quest journals (Murder Mystery, Recruitment Drive, Tower of Life) | Murder Mystery: R1 and R2. Recruitment Drive: R3. The player must carry and wear nothing at entry, or the quest step refuses the player and says why. The bank does not need to be empty. The tests use the period test set with the game's seeded random source. Tower of Life: R1. Black Knights' Fortress: R1, so the copy says 13 quest points. | Source-correct text, plus the precedent for preparation steps. |
| 2956 | Horror from the Deep readout | R1. | Ruling 50 already says that Prayer 43 is recommended. |
| 2960 | Ghosts Ahoy first journal | R1 and R2. The port entry fare stays a source hold. | Source-correct text. |
| 2964 | Garden of Tranquillity and A Tail of Two Cats | Garden: R1 for the seven sourced answers, and R3 for the quiz. The player answers the Wise Old Man's questions, and a wrong answer follows the period retry rule. The quiz is a new interaction, so Claude (Opus) builds it, and a frontend-taste model reviews it. Tail: R1 and R2. | Owner ruling. The quiz is a real constraint that the game can check. |
| 2982-3102 | First journals, readouts and gates for 29 quests: Monkey Madness, Desert Treasure, Do No Evil, Ritual of the Mahjarrat, The Forgettable Tale, Legends' Quest, One Small Favour, Summer's End, The Chosen Commander, The Slug Menace, TokTz-Ket-Dill, Animal Magnetism, Eadgar's Ruse, Elemental Workshop III, Another Cook's Quest, Freeing King Awowogei, Royal Trouble, The Elder Kiln, Wanted!, Watchtower, Defender of Varrock, Another Slice of H.A.M., Dream Mentor, Enakhra's Lament, Grim Tales, Witch's House, Haunted Mine, Nature Spirit, Hazeel Cult | R1 for each. R2 where the item asks for an endpoint. Hazeel Cult gets one journal and one endpoint for each branch. The partial Lost Tribe threshold for Wanted! stays a source hold. | Each item asks for the same type of source-correct change. |
| 3106 | Pirate's hook catalog snapshot | Approve the change of the pinned totals to 1,443 prices and 1,838 limits. | Every earlier row stays identical. The total must increase when a correct sourced row is added. This updates a baseline and does not make the test weaker. |

## Owner answer to the one real question

| Line | Item | Owner ruling |
| --- | --- | --- |
| 2906 | Collections native acceptance | Owner, 2026-10-15 18:46 PDT: "12 a". Ship the main-menu repair (full tab names and standard scroll buttons) after a fresh merge onto current `main` and a new run of the full gate. The Collections content check is excused for this candidate only, because the Collections tab crashes Anki with or without the repair. Treat the crash as a separate bug with high priority. The handoff section "Collections crash" holds the evidence. |

## Holds that are not owner questions

These remain source work: the Ghosts Ahoy port fare, the partial Lost Tribe threshold for Wanted!, and the Cold War book requirement and suit identity.
