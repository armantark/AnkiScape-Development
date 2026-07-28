# Goal blocked — three Achievement Diary clauses, 2026-07-27

**Status.** Thirteen of the design contract's sixteen clauses are MET, each with a
test named in
`memory-bank/source-audits/achievement-diary-completion-2026-07-27.md`. Three
cannot be met from inside this goal. `main` is clean at 3,169 tests, green in both
lanes.

Every clause that could be finished is finished, including all five that were
unbuilt when the goal was set, the dead `MUSIC_UNLOCK_TASK_COUNT`, and the six
defects an independent Sol pass found afterwards.

---

## Blocker 1 — D1: 384 regional tasks

**What is blocked.** 326 tasks ship. The contract asks for 384.

**What I tried.** The source harvest first took the catalog from 171 to 304. The
`any_of` and `derived_value` pass raised it to 310. The approved expansion then
added five condition kinds over existing save state and four contract-limited
telemetry tasks, reaching 326 without replacing a shipped task or exceeding a
regional tier's twelve-task budget.

**Why it stops here.** The remaining tasks need state outside the approved narrow
ledger extension: geography, emotes, inventory choreography, unimplemented enemy
or vendor routes, or wider mechanic-specific telemetry. Inventing predicates for
them would ship rows that cannot complete or that no longer describe the source
deed.

**The single thing that would unblock it.** Implement the missing authentic game
routes and their own durable event seams. The owner has answered the product
question about narrow existing-ledger keys; the remaining gap is implementation
breadth, not an unresolved telemetry policy.

---

## Blocker 2 — D12: the Dungeoneering skillcape

**What is blocked.** 24 of 25 skillcapes ship. Dungeoneering does not.

**What I tried.** Its period row is complete in `SKILLCAPES` with the sourced item
ids and its master. It is filtered out of the purchasable list at runtime.

**Why it stops here.** Nothing in the shipped runtime writes Dungeoneering
experience, so no save can reach level 99 in it. Shipping the cape would create a
row no player can ever buy — an inert row, the exact defect the goal forbids. The
row joins the shipped list automatically once the skill exists.

**The single thing that would unblock it.** Dungeoneering shipping as a trainable
skill. Its data module explicitly parks that surface, and
`memory-bank/breadth-next-tranche.md` lists it as an unstarted family.

---

## Blocker 3 — D15: the 25-skill Max cape gate

**What is blocked.** All four prestige capes are obtainable, but the Max gate
counts the 24 currently trainable skills rather than the period's 25.

**What I tried.** Enforcing 25 directly, which the contract's pinned Max revision
(oldid 6549092) requires.

**Why it stops here.** Enforcing 25 today makes Max, Completionist **and all nine
milestone capes** permanently unobtainable, because the 25th skill cannot be
trained. That trades one wrong number for eleven unreachable rewards. The gate is
therefore registry-derived and the shortfall is stated aloud through
`latent_cutoff_skills_pure()`. Design fork 3.11 records the choice and its
reasoning.

**The single thing that would unblock it.** The same as blocker 2: Dungeoneering
as a trainable skill. The gate then counts 25 by construction, with no further
change.

---

**Delete this file** when Dungeoneering ships, which clears blockers 2 and 3
together, and when the regional diary catalog reaches its 384-task contract.
