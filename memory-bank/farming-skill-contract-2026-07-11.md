# Farming Skill Contract — closed 2026-07-11

Status: **implemented on `main` at `9a88c56`; the 2026-07-16 replacement and
preset amendment is implemented at `9b65f45`.** The body below preserves the
original contract and its post-closure amendment. The source research record is
`memory-bank/source-audits/farming-source-dossier-2026-07-11.md` (cited below
as "dossier"); its per-row citations into game-main (GM) and the Darkan pin
`7e7d67b` (DK) are the extraction map and are not repeated here.

Source rule for numeric conflicts (dossier Q27, settled): GM wins unless internally defective (e.g. the seven identical 1,199.5 fruit-tree check-XP rows); a defective or disputed GM value is settled by a pre-2012-11-20 pinned wiki revision, with DK as corroboration only. DK-only content (specials, Habitat) needs wiki pins wherever DK derives values instead of storing them (its `plantXP × 0.375` special-harvest formula). No disputed number ships without a pin.

## 1. Growth model (owner-settled)

1. **Growth is review-ticked, never wall-clock.** Nothing in Farming reads real time. The conversion is **240 answered cards = 24 hours**, i.e. one answered card advances the farm clock by **6 era-minutes**.
2. **Every answered card ticks the clock, including failures.** This is AnkiScape's first counter driven by all answers rather than successes only: the clock models elapsed time, not skill. Failed reviews tick the clock and do nothing else (they never execute queued steps).
3. Authentic era growth data is kept honest: each crop stores its GM/DK/pinned stage count and per-stage minutes; a global farm-clock counter (total answered-card minutes) plus a per-patch `planted_at` derive elapsed minutes and current stage. Sample pacing: a potato (40 min) ripens in ~7 reviews; a herb (80 min) in ~14; a magic tree (480 min) in 80; a fruit tree (16 h) in 160; a spirit tree (64 h) in 640.
4. **Ticks process eagerly during review dispatch**, 6 minutes per answered card, with disease/death rolls fired at each stage boundary crossed and full state stored after each card, so Anki undo restores the exact prior farm state (rolls included). No lazy offline replay is needed — the clock only moves when cards move.

## 2. Skill archetype and queue semantics (owner-settled)

5. **Farming is the first pure background skill: it has no active-target list.** Its skill tab is the farm sheet itself. Farming XP arrives only through queued detour steps; Farming is never the "active skill" in the reviewer sense.
6. **The step queue preempts the active skill.** When the queue holds N steps, the next N *successful* reviews execute one farm step each — instead of the active skill's normal action — with a visible indicator that a farm detour is in progress; control then returns to the active skill. Failed reviews never consume or execute steps.
7. **"Harvest and replant same" is a first-class shortcut** (owner-mandated). Each patch remembers its last-planted crop as its plan; the shortcut queues harvest + replant-same as consecutive steps. The first use on a patch (or any time the plan is unset) walks through the plan setup UI (crop, compost tier, protection intent).
8. Queued steps must satisfy the standard material/level checks at execution time (seeds may have been consumed by an earlier step); a step that can no longer run is skipped with a log line, never silently converted.

## 3. Verb cost table (owner-approved verbatim)

**Cost 1 review each** (queueable steps, authentic XP):

| Step | Effect |
|---|---|
| Plant | Bundles raking + compost application + seeding. Awards compost XP (18 compost / 26 super) plus plant XP. Consumes the seed count + compost bucket. Implicit raking yields the patch's 3 weeds to inventory. |
| Harvest | Harvests the **whole patch** in one step, running the full GM save-slot life loop per item (exact `/256` probabilities, secateurs ×1.1), awarding per-item harvest XP. |
| Check health | Trees/fruit trees/bushes/calquat/cactus/spirit tree: one-time check XP (the big spike — preserved as-is per parity policy). |
| Cure | Cures a diseased crop (plant cure consumed). Farming XP only if the plant-cure pin proves any (DK's 90 is suspect). |
| Clear | Clears a dead crop or a stump; stump clearing returns the tree's roots. |
| Chop | Chops a grown farm tree: awards the existing Woodcutting per-review log batch and WC XP for that tree type, leaving a stump. No persistent WC unlock — WC targets are already global. |
| Compost bin | Fill (15 eligible items) and collect (needs buckets) are one step each; bin maturation minutes come from the Compost/Supercompost pins and ride the same review clock. |
| Make sapling | Seed + plant pot (+ trowel owned) → sapling, batched up to 28 pairs per step like other prep utilities; the sapling matures after one 5-minute clock tick (GM's watered-pot interval). |

**Free, provided the tool/goods sit in the bank** (no review cost, no XP):

- Raking (implicit in plant), the tool leprechaun (fully abstracted — noting/storage friction does not exist here).
- Watering: owning a watering can auto-applies the ×0.9 disease factor to eligible categories (allotments, flowers, hops) every stage. No charges tracked.
- Farmer protection payments: paying consumes the real goods from the bank (GM per-crop payment tables; the three disputed allotment payments ride pins) and makes that planting disease-proof.

## 4. Patch map and scope (owner-settled)

9. **Full November-2012 roster, location-modeled.** All GM patches (8 allotment, 4 flower, 4 herb, 4 hops, 4 bush, 4 fruit-tree, 5 tree, 1 calquat, 4 compost bins) plus the DK/wiki special patches (cactus, 2 mushroom-capable, belladonna, spirit tree, evil turnip, jade vine, Trollheim/special herb patches, Herblore Habitat vine flower/herb/bush patches, extra compost locations) — reconciled against the `Farming/Patches` pin, which is authoritative for the final inventory (GM 34 vs DK 51 is a coverage delta, not a conflict).
10. **Each patch row carries its access gate**: Farming level, quest requirement (from the 194-row catalog), or activity requirement. The pin phase must also check whether any patch was Task-set (achievement-diary) gated by 2012-11-20 (owner asked; record the answer either way).
11. **Flower protection is natural under the location model**: a flower patch protects the allotments in its own complex (Falador marigolds protect Falador potatoes/onions/tomatoes), per the GM pairing table. Scarecrows protect same-complex sweetcorn.
12. **Habitat patches ship live but emergently inert** per the input-starved policy: their seeds are Jadinko-hunting rewards that don't exist yet, which is the standard you-have-zero-of-the-input state, with no special labeling. Same for any crop whose seed route is starved.
13. **Jade vine and evil turnip ship only if their pins prove complete era loops** (DK's jade vine is broken at the pin — no initial lives; evil turnip's 5-minute one-stage loop needs era validation). If unproven, they are recorded as source-blocked, not shipped broken.
14. White lily ships with pinned values (GM's disabled row says 58/42 XP, DK says 52/70 — pin decides).

## 5. Disease and death (owner-settled: full parity)

15. **GM model exactly**: per-stage roll `floor(diseaseSlots × compostFactor × (0.9 if watered)) / 128`; first-stage, paid, flower-protected, scarecrow-protected, and immune crops are exempt; a crop still diseased at its next stage boundary **dies**. Compost factors: none 1.00, compost 0.28, supercompost 0.14 (GM `CompostState.kt:8-18`; DK's compost path is defective and is not authority).
16. Crops can die unattended — that is the accepted stake. Visibility is the counterweight: the HUD badge flags disease the moment it rolls, and cure is a single queueable step.
17. Disease is pure era RNG, never coupled to review correctness (dossier Q29): protection means disease-proof, exactly as in the era, and has no interaction with failed answers.

## 6. UI surface (owner-settled)

18. **HUD sprout button with badge**: states none / N ready / disease-or-death alert. Clicking opens the compact status list (one line per active patch: crop, stage/ready, disease flag); from there the full farm view opens.
19. **Full farm view**: patch cards grouped by location complex, per-patch detail (plan, compost tier, protection payment, harvest-and-replant-same shortcut), the step queue panel with reorder/remove, and a **"Queue full run"** button.
20. **Queue full run executes the player's own plans — no auto-suggestions** (owner rejected "best at my level": too automatic, and players farm for specific ingredients). It queues: harvest every ready patch, cure every diseased one, clear every dead one, and replant-same wherever a plan exists; patches without a plan are skipped untouched.
21. Casual surface stays minimal per the standing minimalism policy: the one bulk button plus per-patch plans. Full control lives in the patch detail view. No global checkbox wall.

### 6a. Instant-transaction amendment (post-closure owner clarification, 2026-07-11)

The farm view behaves like the NPC shop interface: clicks take effect **instantaneously in the UI**, with no confirm/apply flows and no review round-trips, wherever the action is transactional rather than a field verb.

- **Instant, no review cost**: queue add/remove/reorder; plan setup and compost-tier choice; farmer protection payment (goods leave the bank the moment you click, the planting is disease-proof immediately — exactly like a shop purchase deducting coins); **make sapling** (seed + pot convert in the bank instantly; the sapling still matures over one clock tick); **compost bin fill and collect** (fill instantly from banked produce, collect instantly with buckets; bin maturation still rides the review clock). Make-sapling and compost-bin steps thereby move out of the 1-review verb table — an owner-directed amendment to the §3 table, since they are pure bank transactions that award no XP at transaction time (compost XP stays attached to application at plant time, per GM).
- **Still 1 review each** (the field verbs that earn XP or produce): plant, harvest, check health, cure, clear, chop.
- Instant actions mutate bank/config state outside review dispatch, so they follow the shop surface's persistence model rather than the review-undo contract; review-executed steps keep full Anki-undo rollback.
- Insufficient goods/level grey the control with the standard tooltip, per the existing disabled-row rule.

## 7. Modifiers, tools, and items

22. **Magic secateurs**: bank-ownership pattern (mirrors the crystal saw substrate), gated behind Fairytale I — Growing Pains in the quest catalog; applies the ×1.1 save-slot multiplier (GM `HarvestingHandler.kt:106-120`). Acquisition/effect details ride the Magic secateurs + Fairytale I pins.
23. **Juju farming potion**: era-valid (Herblore Habitat, Nov 2010). The 1-in-3 extra-herb roll (DK `HarvestPatch.java:95-127`) ships wired to the potion item through the existing potion-boost substrate, with the pin settling duration/eligibility/stacking. The potion itself is emergently unobtainable until Jadinko hunting supplies marble vine — standard input-starved state.
24. **Greenfingers aura**: era-valid but its acquisition is the Members Loyalty Programme, an account-meta system with no AnkiScape analog. Recorded as future content pending a loyalty/aura grill; no mechanics ship now.
25. **Patch bomb**: Solomon's store item — era validity by 2012-11-20 must be pinned; if post-cutoff, it is struck as contamination. Not in launch scope either way.
26. **Scroll of life**: Dungeoneering reward; defers to the Dungeoneering ship. DK's 10%/5% seed-return rates and its embedded oldid `6151122` are recorded for that future card.
27. **Amulet of farming / amulet of nature**: no complete mechanic in either source, and their era purpose — remote patch monitoring — is wholly superseded by the HUD badge. No mechanics ship; the items stay function-trailed.
28. **Cure Plant / Fertile Soil** (Magic contract decision 9, owner-mandated): both gain real function now. Cure Plant becomes an alternative cure step (Magic XP + cure, Lunar preset required); Fertile Soil becomes an alternative compost application at plant time (Magic XP + supercompost effect, rune costs authentic).
29. **Tool and seed shops**: one era farming-supplies shop (pinned stock: rake, dibber, spade, trowel, plant pots, buckets, watering can, plant cure, compost where era-attested) joins the NPC shop surface, plus the Draynor seed market with pinned era stock. Bird-nest seed tables (existing nest chain) and era monster seed drops complete the authentic routes. Master Farmer pickpocketing waits for Thieving. A dedicated seed-source audit is part of the build (dossier §6 caveat).

## 8. Economy effects (from dossier §6)

Farming closes current root orphans: grimy snapdragon/spirit weed/toadflax/torstol (plus wergali/fellstalk and the five Habitat vine herbs when seed routes allow), jangerberries, papaya, morchella, sweetcorn, strawberry, watermelon, jute fibre, and oak/willow/maple/yew/magic roots. Cactus yields spines, not potato cactus — that orphan stays open. Habitat vine secondaries (marble vine etc.) remain Jadinko rewards, not farmed. Willow branches need their own pin before joining basket crafting.

## 9. Verification gate — wiki pins

The dossier's 38-pin list (§5 there) is the minimum evidence gate. Highest-stakes pins: fruit-tree check-health XP (GM defective), calquat timing (21h20m vs 10h40m), sweetcorn/strawberry/watermelon payments, jute seed count, white lily, scarecrow level, willow check XP decimal, lantadyme plant XP, plant-cure XP, every special patch, compost bin capacity/timing, and the full `Farming/Patches` inventory. Pins are resolved with `tools/wiki_parity.py` (network available outside the read-only sandbox) and cited per row in the data module, per the standing verification standard.

## 10. Storage, tests, and build shape

- **Storage v32**: farm sheet — global farm-clock minutes; per-patch records (patch id, crop, planted-at, stage, compost tier, lives, diseased/dead flags, protection state, plan, regrowth produce count); compost bin states; the step queue. Flat keys, migration from v31, unknown-key preservation.
- **Undo**: every review's farm mutations (clock tick, stage rolls, step execution, XP, inventory) roll back with Anki undo, matching the existing reward-rollback contract.
- **Regrowth** (bushes, fruit trees, calquat, cactus, Habitat bushes) rides the same clock using pinned regrowth intervals.
- **Assets**: mandatory full pass — seeds, saplings, spores, produce, tools, compost items, the sprout HUD icon — manifest derived from the data module, provenance recorded, path tests.
- **Achievements**: registry-generated generics (first plant, level 10/30/60/99, produce counts) plus a few flavored ones (first tree health check, first full farm run).
- **Tests**: pure (clock math, exact slot-roll probabilities, disease/death transitions, queue semantics, undo, migration), data integrity against pinned citations, offscreen Qt (HUD badge states, farm view, plan setup, disabled-row non-selection), and low-level manual instructions (the owner plays from level 1: plant a potato, answer ~7 cards, harvest).
- **Build shape**: delegated Sol build from this contract per the established work-order pattern (scoped to this repo, no commits, no memory-bank writes, no Darkan/game-main modification), independently verified before commit; plan artifact frozen pre-build, results artifact after.

## 10a. Pin-phase reconciliation (2026-07-11, after the ledger closed)

The verification gate ran and produced `memory-bank/source-audits/farming-wiki-pin-ledger-2026-07-11.md` (35 of 38 pins resolved, every value carrying an oldid). It amends this contract as follows; the ledger is authoritative wherever it disagrees with the text above.

- **Darkan beat game-main on most disputes.** Pinned wins: the three allotment payments (sweetcorn 10 jute fibres, strawberry 5 apples, watermelon 10 curry leaves), jute's genuine 3-seed exception, scarecrow level 23, willow 1,456.3, lantadyme 134.5, and the distinct fruit-tree check XP (GM's seven identical rows confirmed defective). Plant cure awards **0** Farming XP — DK's 90 was invented.
- **Compost**: application XP 18/26 and bin capacity 15 are pinned; era bin maturation is 35–50 min (regular) and 90 min (supercompost), so GM's uniform 25-minute bin timer is **not** the era timer and must not ship. The exact disease factors (0.28/0.14) and +1/+2 lives are not wiki-attested; they ship from GM under the standing primary-source rule (GM wins on what it implements; the pins contradict nothing quantitatively) and are cited as GM-sourced, not wiki-sourced.
- **§5.15 "disease-proof" is overstated.** The period page says a watched crop may still enter the diseased state and the gardener cures it, so protection guarantees *survival*, not immunity. GM models it as immunity; that is the shipping behavior (GM is primary for what it implements), but the contract's wording is corrected here and the divergence is cited.
- **Patch bomb is struck** — it arrived 14 Apr 2014, post-cutoff. §7.25 is closed as contamination, not deferred.
- **Jade vine and evil turnip survive** the era check with complete loops, so both ship (§4.13 resolved affirmatively).
- **Patch map**: 51 crop patches + 6 compost bins is the correct repeatable inventory (plus two one-off quest patches, excluded). **No patch was achievement-diary gated** — the owner's question, answered.
- **Belladonna is 5 h 20 min** (not DK's 2 h 40 min), and DK's derived Habitat-bush harvest XP is wrong (lergberry 31.5, kalferberry 52.5 per berry).
- **Existing shop-data contamination found**: AnkiScape currently sells the five Habitat vine-herb seeds at Papa Mambo's for 10,000 coins, but the period shop stocked only the three blossom colours. That stock is not authentic, must be removed, and those five seeds revert to input-starved pending Jadinko hunting.
- **Twenty inputs have no authentic route today** and ship input-starved with no invented substitutes: nasturtium, woad, white lily, gout tuber, spirit weed, wergali, fellstalk, redberry, cadavaberry, dwellberry, bittercap spore, morchella spore, evil turnip, and the seven Habitat crops.
- **Still `source_blocked`, do not guess**: white-lily planting XP (50 vs 70 vs GM's 42), the exact watering multiplier and its yield effect, spirit-tree exact stage timing, wergali harvest XP, goutweed exact yield/quest gate, and several Habitat stage/time/yield decimals.

## 11. Recorded answers to owner questions

- **Era active-training analogs (owner asked "what's the Tithe Farm analog?")**: pre-EOC Farming had no true active method; the closest analogs are Vinesweeper (2009 — flag/dig minigame paying Farming XP and seeds; the era's nearest Tithe Farm equivalent), the Evil Tree D&D (nurturing grants Farming XP), Livid Farm (July 2011, mostly Magic XP — already deferred to its own activity card), and fast-cycle Herblore Habitat vine farming. All are Activities with their own future grills; Farming ships as the pure background skill, and Vinesweeper is the strongest future-activity candidate for players wanting active Farming training.
- **Diary gating**: whether any patch was Task-set-gated by the cutoff is a pin-phase fact to record (§4.10).

## Post-closure replacement and preset amendment — 2026-07-16

Status: **implemented and verified on `main` at `9b65f45`.**

- Add `Dig up` as a one-review field verb for a healthy mature regrowth crop.
  It requires a Spade, returns no produce, and leaves the patch empty. It never
  silently plants another crop.
- `Queue full run` continues to execute only the player's saved plans. When the
  saved crop differs from a mature regrowth crop, it queues `Dig up` followed by
  `Plant`; manually adding `Dig up` queues only that verb.
- Add compact, user-named whole-farm presets as snapshots of selected patch
  plans. A preset stores patch inclusion plus each included patch's crop,
  compost, gardener policy, watering, cure, and other supported plan fields.
  Existing expanded patch cards remain the only plan editor; presets do not
  create a second configuration surface.
- The compact control row is `Preset [name] [modified] [Apply plans]
  [Presets...]`, followed by `Queue full run` and its ready-step count. Saving
  asks only for a name and included patches. Management supports update,
  included patches, rename, duplicate, and delete.
- Selecting a preset is inert. `Apply plans` copies its plan data into the live
  patch plans without queuing steps or consuming goods. A `modified` marker
  appears when live plans diverge from the selected snapshot.
- This amendment supersedes the immediate-payment sentence in §6a for planned
  gardener protection. An explicit `Queue full run` pays each selected gardener
  from the Bank before constructing that patch's steps. If the goods are
  missing, that patch is skipped and reported rather than silently planted
  unprotected. A manually assembled queue may still deliberately plant without
  protection. Watering must function end to end before it appears as a preset
  field.
- The queued planting step owns a validated escrow record for a newly paid
  gardener. Removing or clearing that step, or skipping it because its planting
  requirements changed, refunds the exact source-defined payment. Successful
  planting consumes it. Legacy already-paid plans remain compatible.
