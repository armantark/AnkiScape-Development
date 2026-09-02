# Horror from the Deep source harvest — 2026-09-02

## Scope and evidence boundary

This is the source record for replacing Horror from the Deep's seven generated
stage sentinels. The cutoff is immediately before EOC:
`2012-11-20T00:00:00Z`.

The seven numbers below are an AnkiScape grouping of the period route, not a
claim that the 2012 game exposed a seven-stage model. Darkan's modern
restoration uses stages `0` through `10`; those implementation integers are
not historical source values and must not be copied into AnkiScape.

The other project's complete target contract is a narrowly authorized
mechanical boundary, not a substitute for period provenance. Its accepted E2
run independently observed the listed reconstructed transactions, but it is
not native-client evidence and it does not close details outside its contract.
The wiki sources are one lineage even where the article, quick guide, and
requirements template agree. The Darkan/rev-727 pair is likewise one source:
rev 727 is Darkan's cache base. The values called Proven below therefore name
the distinct corroboration that closes them.

## Ownership check and premise measurement

No current AnkiScape thread holds this unit. At the check, the only branch name
containing `horror` was `skeletal-horror-phase-depth`; no branch or linked
worktree was named for Horror from the Deep. A search across every local branch
found only the generated catalog and the Dominion Tower's existing use of the
quest, not an active HFTD slice. The shared harvest ledger has no HFTD claim.

The other project's ledger row is
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/ledgers/quests.jsonl:58`,
`quests-horror-from-the-deep`. It is `COMPLETE` with
`completion_reachable: true`, an accepted E1/E2 record, and the target contract
below. Its active context does not claim an in-flight HFTD unit. `COMPLETE`
documents its already-restored server behavior; it is not a current cross-project
claim, so this harvest may proceed.

The queue premise partly inverts on measurement. At canonical revision
`014dcc159bb1a42857cd12d2939af2c02af27ff9`, the live `QUESTS` record contains
exactly **7** stage-requirement rows, **7** generated `Complete Horror from the
Deep stage N objective` actions, **0** substantive required actions, and **0**
auto-actions. It contains **2** generic combat encounter rows, both incorrectly
attached to stage 6. There is no HFTD-specific action proof, stage replacement,
or runtime action implementation. This is not a seven-string edit: it is a
seven-deed feature slice that needs exact, source-specific action emission.

More importantly, the proposed “no prerequisites” profile is false in the
implementation sense. The period record requires Bar Crawl to speak to Gunnjorn.
The live add-on has only one reader of `bar_crawl_completed`, at
`logic/agility_logic.py:281-283`; a source-wide writer search found no writer.
The same search found ordinary completion-state writers for unrelated positive
controls such as `logic/gnome_ball_logic.py:310` and
`logic/agility_logic.py:840`. Thus HFTD cannot faithfully enforce its Bar Crawl
gate until a player-reachable Bar Crawl completion route exists. This is a
measured prerequisite blocker, not a reason to silently omit the gate.

Two further live-catalog discrepancies are direct implementation work:

- `generated/quest_catalog_generated.py:7900-7903` promotes Prayer 43 from a
  recommendation into a hard requirement. The period source calls it “HIGHLY
  recommended”; it is not a start gate.
- The generated/live row requires one plank at stage 2 and puts the hammer at
  stage 1. The period route requires a hammer plus **2** planks and **60** steel
  nails across the two bridge halves. The live cleanup at
  `data/quest_data.py:9182-9187` also removes the source-required sword and
  arrow from stage 6 because the generic inventory representation cannot
  identify their eligible variants or consume them.

## Pinned inputs

| Key | Dated identifier and immutable source | Role in this audit |
| --- | --- | --- |
| D | Darkan restoration commit `b1f8cc04a0dc7ea82391e13e9e352690d7c65ac6`, `2026-07-13T16:16:41-07:00`, “Restore Horror from the Deep progression and recovery”; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/horrorfromthedeep/HorrorFromTheDeep.kt` | Inspected first. A modern reconstruction, newly introduced by this commit, not preserved period server code. It supplies a traceable implementation lead only. Its matching integration paths are Lighthouse.java, Jossik.java, Rellekka.java, and Agility.java under the same source root. |
| C | `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/horror-from-the-deep-target-contract.json`, SHA-256 `119dc82cf6ff4eaa1ef8497d662c8f2448195ca7c315adda86bca7c747054359`; external ledger row `quests-horror-from-the-deep` at `.../ledgers/quests.jsonl:58` | The approved COMPLETE target boundary: bridge, lighthouse, wall, six mother forms, casket recovery, completion rewards, and unlocks. It does not authorize exact dialogue, modern spins, post-EOC rewards, or native-client claims. |
| E2 | `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/runtime/quests/horror-from-the-deep/horror-from-the-deep-e2-20260713T232021Z.json`, SHA-256 `b651494a220935c0564213d510ebb43fdc84a7d49453470c277406fd96b862a6`, correction commit `0b52dd4ed6ba3e2ad830ae566d03eec07ce35c1c` | Accepted headless runtime record: **3/3** observed checks for bridge/lighthouse/wall, six-form attack gating, and full-inventory casket recovery through rewards. The separate `...231732Z.json` is retained diagnostic evidence, not a pass. |
| R7 | rev `727`, `2012-07-24`, OpenRS2 archive `309`, SHA-256 `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`; `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/` | Darkan's client configuration base. It directly supplies quest, item, NPC, object, option, placement, and varbit identities; it does not prove server transactions, XP, or hidden combat behavior. |
| G | `/Users/ArmanTarkhanian1/Downloads/game-main` (2011Scape rev-667-style config download; no `.git`, therefore no commit identifier) | Searched after R7. Its zero-byte cache files mean its checked-in `data/cfg/*.yml` dumps are the usable independent client layer. It corroborates selected names/IDs and varbit 34, but has no HFTD implementation and conflicts on generic mother-family numbering; see Conflicts. |
| R8–R42 | Extracted caches `728-2012-08-01`, `729-2012-08-11`, `736-2012-10-09`, `741-2012-11-04`, and `742-2012-11-07` under `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/<rev-date>/cache/`; R42 is rev `742`, OpenRS2 archive `544`, SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8` | Later pre-cutoff cache comparison. The listed HFTD item and object definition rows are structurally identical in all six caches, and NPC IDs `1347`, `1351`–`1356` remain combat level 100 in all six. NPC display aliases `1335`–`1337` become null in rev 736 onward; options and IDs remain. |
| B | [Horror from the Deep — oldid 5903527](https://runescape.wiki/w/Special:PermanentLink/5903527), `2012-07-08T02:56:37Z` UTC; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/horror-from-the-deep-build727-oldid-5903527.json` | Last pinned walkthrough before the R7 snapshot. Its `Getting started`, `Fixing the Lighthouse`, `The Wall`, `The Horror`, `Finishing Up`, and `Reward` sections supply the route and values used below. |
| F | [Horror from the Deep — oldid 6447471](https://runescape.wiki/w/Special:PermanentLink/6447471), `2012-10-20T20:19:09Z` UTC; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/horror-from-the-deep-final-preeoc-oldid-6447471.json` | Nearest pinned pre-EOC walkthrough. Its `Unattended`, `Diary of the.. Presumably Dead`, `Elementary`, `The Horror`, `The God Books`, and `Reward` sections corroborate B's route and reward choices. |
| Q | [Template:Questreq — oldid 5981134](https://runescape.wiki/w/Special:PermanentLink/5981134), `2012-07-23T14:16:09Z` UTC; `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/questreq-template-horror-from-the-deep-build727-oldid-5981134.json` | The `Horror from the Deep` switch entry expands to `[[Barcrawl]]`, establishing the omitted miniquest gate. |
| K | [Horror from the Deep/Quick guide — oldid 6343123](https://runescape.wiki/w/Special:PermanentLink/6343123), `2012-10-04T01:24:21Z` UTC; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/tools/.cache/pre_eoc_quest_catalog/wikitext_horror_from_the_deep_quick_guide_old.json` | Current generated journal source. Useful checklist corroboration only; it is the same wiki lineage as B/F. |
| T | `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/horror-from-the-deep-transcript-history.json` | Excludes exact period dialogue: earliest `Transcript:Horror from the Deep` is oldid `7537437`, `2013-03-08T19:37:59Z`; `Horror from the Deep/Transcript` begins at oldid `16472938`, `2016-04-05T21:50:13Z`. Both are after cutoff. |

D was inspected before R7, G, R8–R42, and the wiki. R7 is not independent
corroboration of D. B, F, Q, and K are cited as permanent pre-cutoff records,
never as mutable-page claims.

## Current generated sentinels

`data/quest_data.py` derives the active row from
`generated/quest_catalog_generated.py:7882-8052` and applies the cleanup noted
above. The current live row has seven literal generated actions and a
completion line after stage 7.

| Stage | Exact current required action | Source-faithful correction |
| ---: | --- | --- |
| 1 | `Complete Horror from the Deep stage 1 objective` | Start by accepting Larrissa's request after the boostable 35 Agility gate. |
| 2 | `Complete Horror from the Deep stage 2 objective` | Complete Bar Crawl, obtain the key from Gunnjorn, and repair both bridge halves. |
| 3 | `Complete Horror from the Deep stage 3 objective` | Return to Larrissa and enter the lighthouse with the key. |
| 4 | `Complete Horror from the Deep stage 4 objective` | Search the bookcase and read the three lighthouse books. |
| 5 | `Complete Horror from the Deep stage 5 objective` | Repair and light the lighthouse mechanism. |
| 6 | `Complete Horror from the Deep stage 6 objective` | Open the strange wall with its six consumed offerings. |
| 7 | `Complete Horror from the Deep stage 7 objective` | Defeat the two encounters, recover the casket, make the god-book choice with Jossik, and complete the quest. |

The generated stage-6 combat rows must move into the final deed. They are not
evidence that combat is complete at the wall-opening stage.

## Replacement deeds, in period order

| Stage | Period deed replacing the sentinel | Pinned evidence and exact boundary |
| ---: | --- | --- |
| 1 | Speak to Larrissa outside the lighthouse and accept her request to investigate the missing Jossik. | B/F start sections; R7 identifies Larrissa as `1336`/`1337`, both `Talk-to`. Start requires **35 Agility**, boosts allowed. No exact dialogue is claimed. |
| 2 | After Bar Crawl, speak to Gunnjorn for lighthouse key `3848`; repair both sides of the broken bridge with **2** planks `960`, **60** steel nails `1539`, and hammer `2347`. Consume one plank and **30** nails on each side; retain the hammer. | Q establishes Bar Crawl; B/F `Fixing the Lighthouse`/`Diary...`; C and E2 close the two-side transactional mapping. R7 identifies bridge `73681`, patched states `73682`/`73683`, and client varbits `36`/`37`. |
| 3 | Return to Larrissa, use the key to enter the lighthouse, and search for Jossik. | B/F; R7 doorway `4577` has `Walk-through`. Exact dialogue/state text remains blocked. |
| 4 | Search bookcase `4617`, obtain and read Journal `3845`, Diary `3846`, and Manual `3847`. | B/F detailed route names all three; K names Manual and Ancient diary, so the source union retains the third book. R7/R42 item names have `Read`; C closes the all-three contract. |
| 5 | Repair the mechanism with molten glass `1775` and swamp tar `1939`, then light it using inventory tinderbox `590`. Consume glass and tar; retain a non-toolbelt tinderbox. | B/F; R7/R42 mechanism `4587` has `Light`; C/E2 close consumption and retention. Cache's `Add-to-toolbelt` option does not prove toolbelt eligibility for this server action. |
| 6 | At the strange wall `4543`–`4546`, consume one each of fire `554`, water `555`, air `556`, and earth `557` rune, then one sword and one eligible arrow (not ogre or training). | B/F `The Wall`/`Elementary`; R7/R42 distinguish `Study` wall states `4543`/`4544` from `Open` states `4545`/`4546`; C/E2 close the six-offering transaction. The source supplies category rules, not a fixed list of sword/arrow IDs. |
| 7 | Descend, protect Jossik, defeat Baby Dagannoth `1347`, then the Dagannoth mother in its six forms `1351`–`1356`; recover Rusty casket `3849` from Jossik if full inventory prevented direct receipt; present it to surface Jossik `1334`, select Saradomin `3839`, Zamorak `3841`, or Guthix `3843` damaged book, then complete. | B/F `The Horror`/`The God Books`; R7/R42 names and combat levels; C/E2 close the ordered combat, form gate, casket recovery, choice, and completion transaction. |

## Proven

This table is the complete positive boundary for an AnkiScape implementation.
Values are source-backed only to the extent stated; the surrounding unpinned
server representation must not be copied from Darkan.

| Proven item | Source |
| --- | --- |
| Quest identity: `105`, `Horror from the Deep`, zero quest-point prerequisite, **2** point reward, client quest varbit tuple `[34, 1, 10]`. | R7 cache quest definition; G independently names `Varbits.HORROR_FROM_THE_DEEP_PROGRESS = 34`. Cache configuration is client identity evidence, not proof of server transition values. |
| No ordinary quest prerequisite and no quest-point prerequisite; **Bar Crawl** miniquest gate. | R7 has `quest_prerequisite_ids: null` and point prerequisite 0; Q explicitly expands HFTD to Barcrawl; B/F describe the Gunnjorn access gate. |
| Start is Larrissa `1336`/`1337` outside the Lighthouse; **35 Agility**, boostable, is the hard skill gate. | B/F `Quest details` and start sections; R7 identifies Larrissa options; C's target contract records `agility: 35, boostable: true`. |
| Prayer **43** is recommended, not required. | B/F literal “HIGHLY recommended” wording, reinforced by its placement outside `{{Skillreq}}`; K renders the same distinction. |
| Bridge materials and transactions: `960` Plank ×2, `1539` Steel nails ×60, `2347` Hammer retained; **30** nails and one plank per side. | B/F and C; E2 observes both bridge varbits `[1, 1]`. R7/R42 identify all three items and bridge `73681`, `73682`, `73683`. |
| Lighthouse items and transaction: `1775` Molten glass ×1 and `1939` Swamp tar ×1 consumed; `590` Tinderbox must be carried and remains. | B/F, C, and E2; R7/R42 item identities and `4587` `Light` option. |
| Wall runes `554` Fire, `555` Water, `556` Air, `557` Earth, each quantity one and consumed; one sword and one non-ogre/non-training arrow are also consumed. | B/F exact list and exclusions; C/E2 verifies transaction shape. R7/R42 prove rune identities and strange-wall options, not server-side eligibility. |
| Quest-item identities: Journal **3845**, Diary **3846**, Manual **3847**, Lighthouse key **3848**, Rusty casket **3849**. | R7/R42 items; G `Items.kt` and `data/cfg/items.yml` independently corroborate the client identities. |
| Client-facing NPC identities: Gunnjorn **607**; Jossik **1334**/`1335`; Larrissa **1336**/`1337`; Baby Dagannoth **1347**; mother forms **1351–1356**. All seven combat NPC IDs are level **100** in R7, R8, R9, R36, R41, and R42. | R7 definitions and all-cache `--combat-levels` comparison. R36–R42 retain null names for aliases `1335`–`1337`, so their names rely on R7 and B/F rather than falsely claiming six-cache agreement. |
| Client-facing objects: Strange wall **4543–4546** (`Study`, `Study`, `Open`, `Open`); doorway **4577** (`Walk-through`); lighting mechanism **4587** (`Light`) / `4589`; bookcase **4617** (`Search`); iron ladders **4383** / `4485`; broken bridge **73681** (`Cross`); patched states **73682** / `73683`. | R7/R42 definitions, structurally identical across every dated cache. R7 map placements include `73681` at `(2596, 3608, 0)` in region `10296`, `4577` at `(2509, 3636, 0)`, `4587` at `(2507, 3639, 2)`, and `4617` at `(2508, 3644, 1)` in region `10040`. |
| Mother attack gate: initial white form `1351`; white/air magic, blue/water magic, red/fire magic, brown/earth magic, green/ranged, orange/melee; wrong attack deals **0** damage. Subsequent form order is random. | B/F weakness table; C exact contract; E2 observes initial `1351` and wrong damage 0 for all six forms. |
| Full-inventory recovery: Jossik retains the casket until it can be recovered; defeating the baby may persist before leaving/logging out; interrupted mother combat restarts. | B/F casket prose; C and E2's recorded recovery transaction. This closes behavior, not a particular historical storage schema. |
| Completion choice: Saradomin **3839**, Zamorak **3841**, or Guthix **3843** damaged book; **2** quest points; **4,662** XP each in Magic, Strength, and Ranged. | F `The God Books`/`Reward`; R7/R42 identify the three damaged-book client items; C and E2 observe the choice/reward path and exact XP deltas. |
| Completion unlocks: lighthouse general store and post-quest Dagannoth caves. | F `Reward`; C exact unlock list; E2 reaches completion. |

## Conflicts and exclusions

| Matter | Evidence and resolution |
| --- | --- |
| game-main mother IDs differ from R7 | G's generic rev-667-style constants identify `DAGANNOTH_MOTHER = 1348` and forms `1349`–`1356`; R7/R42's HFTD evidence is Baby `1347` and mother forms `1351`–`1356`. G has no HFTD quest logic or combat definitions and is older. Use R7/R42 IDs for this quest; use G only for corroborated broad client identities. |
| Bar Crawl enforcement in Darkan | Q/B/F establish the gate, but Darkan's modern HFTD handler accepts active quest players at Gunnjorn without checking Bar Crawl. The target contract lists Bar Crawl as a dependency. AnkiScape must not inherit Darkan's omission. |
| Quick-guide book and return-to-Larrissa details | K names Manual and Ancient diary and adds an extra Larrissa talk after lighting; F's detailed walkthrough also names Jossik's diary and does not make that later talk a clear gate. C's all-three-book contract resolves the book union. No additional dialogue checkpoint is asserted. |
| Squeal of Fortune spins | F lists **2** spins, but C expressly excludes modern spins/post-EOC rewards and the current target contract does not grant them. They are excluded from this sentinel contract, not silently reclassified as an entitlement. |

## Not recovered

These unknowns do not enter the implementation contract. They are
`source_blocked`, not guesses or provisional defaults.

| Item | Status and what would settle it |
| --- | --- |
| Exact dialogue, player choices, and wording. | **Source-blocked.** T proves both transcript pages start after cutoff. A pre-EOC transcript, dated Wayback capture, or official dialogue archive would settle it. |
| Original server stage integers, phase-change interval, no-immediate-repeat rule, exact mother despawn/restart timer, damage caps, HP/stats, and exact attack cadence. | **Source-blocked.** Darkan's `20`-tick phase timer, its owned-NPC representation, and its combat numbers are modern reconstruction choices. B/F never state these server values. Period server evidence or a separately corroborated period implementation is required. In particular, do not promote the existing generated encounter stat blocks as source-closed merely because they name Darkan JSON files. |
| Exact enumerable sword and eligible-arrow IDs. | **Source-blocked as an enumerated set.** B/F settle the category rule—any disposable sword and an arrow except ogre/training—but do not list every allowed ID. Implement only an existing exact item-category predicate; do not substitute a string heuristic or a fabricated enumeration. |
| Members-only gate, music unlock execution, post-quest level-74/92 Dagannoth combat details, Dagannoth ribs, and God-book page/reassembly behavior. | **Not required for this seven-sentinel contract and not independently closed here.** B/F mentions parts of this surface, but no independent period layer was recovered for the operative behavior. |

No registered AnkiScape placeholder is emitted by this read-only harvest. The
placeholder audit scans shipped Python and requires each marker to have a
matching row in `memory-bank/placeholder-values.md`; this task may create only
this audit and may not modify either surface. None of the source-blocked values
above is permitted to cross into the implementation as a numerical or behavioral
default. If a future implementation genuinely needs one, it must add a
`# PLACEHOLDER(horror_from_the_deep.<value>): <specific settling evidence>`
marker in shipped Python and a matching register row atomically. Until then it
must fail closed or omit the unsourced behavior.

## Handoff boundary

All seven replacement-deed headlines, hard start conditions, transactional
items, identities, combat form gate, casket recovery, reward amounts, and two
completion unlocks are pinned for a source-faithful stage contract. The
implementation must keep Prayer 43 non-gating, move combat from stage 6 to
stage 7, restore the two-side bridge transaction, and never credit a generic
item/magic/combat event as a quest deed.

The measured Bar Crawl writer absence is a genuine blocker to faithfully
implementing the stated prerequisite. It requires a player-reachable Bar Crawl
completion action before HFTD can enforce it. No one should replace that gate
with an invented bypass, a default-true state, or an unlabeled reconstruction.
