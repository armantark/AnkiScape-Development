# Bar Crawl source harvest — 2026-09-02

## Scope and evidence boundary

This is the source record for giving the **Alfred Grimhand Bar Crawl** miniquest
a player-reachable completion route. The cutoff is immediately before EOC:
`2012-11-20T00:00:00Z`.

The initial claim is
`memory-bank/pending/bar-crawl-claim-2026-09-02.md:12-32`. It establishes that
Darkan is an implementation lead, not period proof, and that the other
project's two completed quest rows prove only their dependent gates. This
harvest owns the internal Bar Crawl values for the first time; no Bar Crawl row
exists in that project's ledger or runtime-evidence directory.

Darkan was inspected first, then its rev-727 configuration base, then
game-main, then the remaining dated caches, and finally the historical wiki
records. The Darkan/rev-727 pair is one lineage because rev 727 is Darkan's
cache base. No detailed Darkan server behavior is promoted merely because it
exists in a runnable reconstruction. In particular, timing, exact stat drains,
random-number boundaries, card replacement, banking behavior, and asynchronous
handler details remain unclosed unless an independent period source says them.

The ten bars may be visited in any order. That statement, the full drink table,
the nominal total of **208 coins**, card-signing completion condition, and the
downstream quest dependencies are carried by the historical source A below.
The total was remeasured from A's ten price cells:
`50 + 10 + 15 + 12 + 8 + 18 + 10 + 7 + 70 + 8 = 208`.

## Ownership check and premise measurement

At canonical revision `014dcc159bb1a42857cd12d2939af2c02af27ff9`, Bar Crawl is
not a partially implemented quest. Its entire live completion footprint is:

| Surface | Measured state |
| --- | --- |
| Completion-state reader | `logic/agility_logic.py:280-285` has the sole Python reference: `_quest_complete(..., "bar_crawl")` reads `player_data.get("bar_crawl_completed", False)` at line **282**. A source-wide exact search found **1** matching Python file and no writer. |
| Current gated content | `data/agility_data.py:178-189` and `data/agility_data.py:191-210` assign `quest_gate="bar_crawl"` to the normal and advanced Barbarian Outpost courses: **2** gates. `logic/agility_logic.py:333-335` enforces either gate through the reader above. |
| Existing item data | `generated/item_values_generated.py:903` lists `Barcrawl card` at value **10**, but has no card lifecycle or quest logic. |
| Existing bars and drinks | An exact search of shipped Python found **0** occurrences of any of the ten required specialty-drink names. Venue names survive only as unrelated quest, diary, music, or generic-shop text; there is no Bar Crawl venue entity, drink transaction, signed-card state, bartender route, or test reference. |
| Reusable machinery | Generic bartender vendor actions exist at `data/shop_data.py:23` and `logic/shop_logic.py:630-653`; generic quest/action-proof machinery exists at `logic_pure/logic_pure_quest.py:1165-1183,1441` and `data/quest_action_proof_data.py:13-36`. Neither writes `bar_crawl_completed` or names a Bar Crawl drink. |

The premise therefore holds, rather than inverts: this is an
unstartable-quest defect. The measured implementation scope is one miniquest
completion route consisting of a guard/card lifecycle, **10** explicit
bar-drink deeds, **10** price/effect specifications, and one real completion
writer. The two existing course gates must remain consumers of that writer;
they are not a substitute for it. No physical-location subsystem need be
invented, because the existing quest/action layer can own the ordered proof.

## Pinned inputs

| Key | Dated identifier and immutable source | Role in this audit |
| --- | --- | --- |
| D | Darkan source root `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/`, checked at `dev` head `6277992980582f7b3da3a48e722e96cfa5b0a57d`, `2026-08-23T00:50:35-07:00`; `src/main/java/com/rs/game/content/miniquests/bar_crawl/BarCrawl.kt:20-188`, `BarEffects.kt:21-238`, and `BarbarianGuardD.kt:14-96` | Inspected first. The files were introduced in modern restoration commit `bb852c1b94bd5c108c959b09a6f126a8e2b908bf`, `2024-03-24T18:32:01Z`, “Add Barcrawl Miniquest.” `BarCrawl.kt` and `BarbarianGuardD.kt` were conversation-API rewritten in `2484d4b4573f49a412d72a02e0566f4de891a03a`, `2024-03-25T13:26:58Z`; `cee9c420535b40fb0d16589aec67d0647c708bed`, `2024-03-26T22:19:38Z`, changes only the Outpost annotation text. `BarEffects.kt` remains attributed to `bb852…`. D is a traceable modern implementation reference and later-audit comparator, never period proof. |
| R7 | rev `727`, `2012-07-24`, OpenRS2 archive `309`, SHA-256 `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`; `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/727-2012-07-24/cache/` | Direct English client identity/options source for card `455`, the guard, all bartender candidates, Blurberry, Zambo, and gate objects `2115`/`2116`. It does not prove the server drink purchase, effect, card signing, or completion transaction. |
| G | `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml:3152-3157` and `/Users/ArmanTarkhanian1/Downloads/game-main/src/main/kotlin/com/rs/cache/loaders/Items.kt:452-459` | Independent older client layer. It corroborates card item `455`; it has no Bar Crawl miniquest, handler, dialogue, bartender, or gate implementation. Its generic drink definitions are not linked to Bar Crawl. This checkout has no `.git`, so no commit identifier exists. |
| R8–R42 | `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/extracted/{728-2012-08-01,729-2012-08-11,736-2012-10-09,741-2012-11-04,742-2012-11-07}/cache/`; R42 is rev `742`, OpenRS2 archive `544`, SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8` | The exact definition outputs for item `455`, NPCs `384`, `568`, `731`, `733`–`739`, `848`, `3217`, and `3218`, and objects `2115`/`2116` are byte-identical across R7, R8, R9, R36, R41, and R42. This supplies a late pre-cutoff identity cross-check, not server mechanics. |
| A | [Bar Crawl (miniquest) — oldid 6304383](https://runescape.wiki/w/Special:PermanentLink/6304383), `2012-09-27T15:14:57Z` UTC, literal `Walkthrough → Starting out`, `Visiting the bars`, and `Required for completing` wikitext | Primary period narrative: all ten locations, drink names, prices, described effects, any-order route, the all-signatures return condition, and the Scorpion Catcher/Horror from the Deep dependencies. |
| C | [Barcrawl card — oldid 5912137](https://runescape.wiki/w/Special:PermanentLink/5912137), `2012-07-09T15:27:01Z` UTC | Period corroboration for the guard-issued card, Outpost access reward, loss restarting the crawl, and the distinction between Outpost access and the separate Agility **35** course gate. |
| B | [Barbarian guard — oldid 6221934](https://runescape.wiki/w/Special:PermanentLink/6221934), `2012-09-09T19:29:17Z` UTC | Period corroboration that this guard starts the miniquest and denies Outpost entry until it is complete. |
| H | [Template:Questreq — oldid 5981134](https://runescape.wiki/w/Special:PermanentLink/5981134), `2012-07-23T14:16:09Z` UTC, `Horror from the Deep → Barcrawl` switch branch | Independent historical route check for the Horror from the Deep prerequisite. |
| S | [Scorpion Catcher — oldid 6445052](https://runescape.wiki/w/Special:PermanentLink/6445052), `2012-10-19T22:46:03Z` UTC, `Walkthrough → Quest details → requirements` | Independent historical route check that Bar Crawl is a Scorpion Catcher requirement. |
| V | The ten period venue records listed directly below | Corroborate each named location and the local bartender/owner role. They are the same wiki lineage as A, so they add location/person context rather than a falsely independent server-value proof. |

The V records are all permanent pre-cutoff wikitext sources:

| Venue | Historical permanent record |
| --- | --- |
| Blue Moon Inn | [oldid 5998350](https://runescape.wiki/w/Special:PermanentLink/5998350), `2012-07-27T04:58:19Z` UTC |
| Blurberry's Bar | [oldid 6347325](https://runescape.wiki/w/Special:PermanentLink/6347325), `2012-10-05T01:04:59Z` UTC |
| Dead Man's Chest | [oldid 6338126](https://runescape.wiki/w/Special:PermanentLink/6338126), `2012-10-03T00:23:58Z` UTC |
| Dragon Inn | [oldid 6348810](https://runescape.wiki/w/Special:PermanentLink/6348810), `2012-10-05T03:44:19Z` UTC |
| Flying Horse Inn | [oldid 6258836](https://runescape.wiki/w/Special:PermanentLink/6258836), `2012-09-17T17:56:39Z` UTC |
| Forester's Arms | [oldid 5629538](https://runescape.wiki/w/Special:PermanentLink/5629538), `2012-05-19T07:16:10Z` UTC |
| Jolly Boar Inn | [oldid 6391474](https://runescape.wiki/w/Special:PermanentLink/6391474), `2012-10-12T18:14:48Z` UTC |
| Karamja Wines, Spirits, and Beers | [oldid 6342493](https://runescape.wiki/w/Special:PermanentLink/6342493), `2012-10-03T18:13:31Z` UTC |
| Rising Sun | [oldid 6588397](https://runescape.wiki/w/Special:PermanentLink/6588397), `2012-11-19T18:38:38Z` UTC |
| The Rusty Anchor | [oldid 5120865](https://runescape.wiki/w/Special:PermanentLink/5120865), `2012-01-07T23:28:31Z` UTC |

D was inspected before R7, G, R8–R42, and A/C/B/H/S/V. A, C, B, H, S,
and V are permanent historical records, not mutable-page claims.

## Ten required drinks and venue identities

The `Period effect` column is the literal level of precision that A supplies.
The exact price is carried by A and agrees with D. R7/R42 carry the relevant
NPC identity/option, while V corroborates its venue role. Coordinates and
numeric drain/damage code from D are deliberately not elevated into the table:
AnkiScape has no location layer, and those server values are assessed in
[Not recovered](#not-recovered).

| Bar and period location | NPC identity carried by R7/R42 | Required drink and price carried by A | Period effect carried by A |
| --- | --- | --- | --- |
| Blue Moon Inn — south-central Varrock | Bartender **733**, `Talk-to`; V identifies the Blue Moon bartender. | Uncle Humphrey's Gutrot — **50** coins | Lowers Attack, Defence, Strength, and Smithing; “up to 20 life points”; vomit/`Blearrgh!`. |
| Blurberry's Bar — first floor of the Grand Tree | Blurberry **848**, `Talk-to`; D also routes **849** to 848, but that redirect is Darkan-only. | Fire Toad Blast — **10** coins | “Lowers up to 47 life points.” |
| Dead Man's Chest — Brimhaven, south-west of the Agility Arena | Bartender **735**, `Talk-to`. | Supergrog — **15** coins | Lowers Attack, Defence, Herblore, Cooking, and Prayer; double vision. |
| Dragon Inn — Yanille | Bartender **739**, `Talk-to`. | Fire Brandy — **12** coins | Lowers Attack and Defence. |
| Flying Horse Inn — Ardougne, west of the North Bank | Bartender **738**, `Talk-to`. | Heart Stopper — **8** coins | Lowers life points by about **20–30%** of total; watery eyes. |
| Forester's Arms — Seers' Village | Bartender **737**, `Talk-to`. | Liverbane Ale — **18** coins | Lowers Attack, Defence, Fletching, Firemaking, and Woodcutting. |
| Jolly Boar Inn — Varrock beside the Lumber Yard | Bartender **731**, `Talk-to`. | Olde Suspiciouse — **10** coins | Lowers Attack, Defence, Mining, Crafting, Magic, Strength, and then repeats Mining in A's literal list; head spins. The duplicate is an unresolved source anomaly, not an implied second Mining drain. |
| Karamja Spirits Bar / Karamja Wines, Spirits, and Beers — Musa Point | Zambo **568**, `Talk-to` / `Trade`. | Ape Bite Liqueur — **7** coins | Lowers Attack and Defence. |
| Rising Sun — Falador | Barmaids Emily **736**, Kaylee **3217**, and Tina **3218**, each `Talk-to`. V identifies all three as the bar's servers; no one is silently chosen as the sole authentic provider. | Hand of Death Cocktail — **70** coins | Lowers Attack, Defence, Ranged, and Fishing; “up to 200 life points”; screen shake for **2–5** seconds. |
| Rusty Anchor — Port Sarim | Bartender **734**; R7/R42 have no listed interaction option for this row, so the `Talk-to` route remains evidence carried by A/V and D rather than falsely claimed as a cache option. | Black Skull Ale — **8** coins | Nothing beyond hiccups. |

No drink is a recoverable client item in this source set. R7 and R42 exact-name
queries for all ten names return zero item-definition matches, while the same
reader positively resolves card `455` and the named NPC definitions above.
D also has no drink item IDs: its purchase helper debits coins, applies an
effect, and signs the card without adding an inventory drink. This supports the
narrow conclusion that no client drink-item identity is available here; it does
not prove a historical server could not have represented a transient drink
internally.

## Completion, reward, and downstream unlocks

| Proven item | Source and bounded meaning |
| --- | --- |
| Start by speaking to a Barbarian guard at the entrance to the Barbarian Agility Training Course / Outpost and receive a Barcrawl card. | A `Starting out`; C; B. R7/R42 identify guard **384**, `Talk-to`, and card **455**, model **2430**, with client options `Read` and `Drop`. G independently corroborates item **455**. |
| Visit all **10** bars in any order, obtain each speciality drink/signature, then return the completed card to an Outpost guard. | A `Starting out` and `Visiting the bars`. This is the only period completion condition claimed. D's Boolean attributes, free-slot condition, delays, card removal, bank treatment, and stage integers are reconstruction details, not period facts. |
| Losing the card means the crawl must be restarted. | A `Starting out`; C. Exact loss detection, bank interaction, replacement timing, and partial-progress storage are not stated by period evidence. |
| Reward: access to the Barbarian Outpost. The Agility Course still requires **35 Agility**. | C. The Outpost guard relationship is independently corroborated by B. R7/R42 identify objects **2115** and **2116** with `Open`; their gate semantics remain server-side. No XP, coins, quest points, or item reward is attested here. |
| Unlock: the Bar Crawl requirement for Horror from the Deep. | A `Required for completing`; H explicitly nests `Barcrawl` beneath `Horror from the Deep`. This is the prerequisite whose absent completion writer makes the live HFTD slice unstartable. |
| Unlock: the Bar Crawl requirement for Scorpion Catcher. | A `Required for completing`; S independently lists the miniquest in Scorpion Catcher's requirements. |

D describes its modern miniquest as `Miniquest.BAR_CRAWL`, display name
`"Alfred Grimhand's Barcrawl"`, using card `455`, guard `384`, and states
`0`/`1`/`2`. Those names and integers are a later-restoration representation,
not a historical state model. The two other-project quest ledger rows
`quests-scorpion-catcher` and `quests-horror-from-the-deep` verify only that
those completed quest units name the dependency. They are not direct Bar Crawl
runtime proof and do not close its registration, bartender reachability, card
transaction, effects, gates, or target-era fidelity.

## Proven boundary

A source-faithful AnkiScape implementation may use the following without
copying a modern server's hidden representation:

- the named miniquest, guard/card start, ten venue/drink/deed pairs, ten prices,
  any-order collection, and return-to-guard completion condition;
- the client identities in the tables: card **455**, guard **384**, Zambo
  **568**, generic bartenders **731**, **733**–**735**, **737**–**739**,
  Blurberry **848**, and Rising Sun staff **736**, **3217**, **3218**;
- the period-stated effect categories and named affected skills, subject to the
  Olde Suspiciouse anomaly below; and
- Outpost access and the two downstream quest dependencies, without inventing
  XP, a card-removal result, a hidden state schema, or extra rewards.

The generic quest/action proof surfaces measured above may model the ten deeds,
but no generic purchase or consumption event may count as a Bar Crawl signature
unless it is bound to the relevant named venue/drink deed. That prevents a
player from completing a historical route through unrelated Beer actions.

## Conflicts and exclusions

| Matter | Evidence and resolution |
| --- | --- |
| Darkan implementation provenance | D's specific values were added in 2024, not preserved as a period server artifact. It is useful for audit comparison only. The explicit claim record fixes this classification, so its implementation numbers do not settle a period mechanic by themselves. |
| Gutrot damage maximum | A says “up to **20** life points.” Earlier [Bar Crawl oldid 5575732](https://runescape.wiki/w/Special:PermanentLink/5575732), `2012-05-07T07:32:42Z` UTC, says **200**. D uses `Utils.random(200)`. The period record conflicts; no damage maximum or random boundary is closed. |
| Fire Toad Blast | A says up to **47** life points and D uses `Utils.random(47)`. The outward maximum is corroborated, but inclusive/exclusive random semantics and exact damage transaction are not. |
| Heart Stopper and Hand of Death damage | A provides “about **20–30%**” and “up to **200**,” respectively. D implements a current-hitpoints percentage with `Utils.random(20, 30)` and `Utils.random(200)`. The period descriptions close the stated effect shape, not the integer arithmetic, random bound, protection ordering, or true-damage semantics. |
| Exact stat-drain amounts | A names affected stats but no numerical drain magnitudes. D contains concrete numbers (for example, Gutrot `8/7/7/6`, Supergrog `8/7/6/7` plus `60.0` Prayer drain, and Fire Brandy `11/10`), but those are unaudited restoration behavior. No numerical drain may be shipped as historical. |
| Olde Suspiciouse seventh stat | A's final 2012 table repeats Mining. Oldid `5575732` instead says Smithing; D uses neither a second Mining nor Smithing value. The unambiguous affected set is Attack, Defence, Strength, Mining, Crafting, and Magic. The seventh slot is unresolved, not silently repaired. |
| Camera and visual effects | A says Hand of Death shakes the screen for **2–5** seconds. D assigns a camera call to both Hand of Death and Liverbane Ale for a random **4–8**-second call. The discrepancy and the added Liverbane camera effect are not period-closed. |
| Card handling and completion presentation | C/A say loss restarts the crawl and that a completed card cannot be read; D clears attributes, removes card **455** from inventory and bank, and opens a completion interface. Only the period prose is usable. Do not infer removal, bank behavior, or an interface. |
| Gate mechanics | R7–R42 prove object identities/options only. D's pre-completion denial, ejection rectangles, login hook, and exact guard coordinates are modern server mechanics. They are excluded from a period claim. |
| The 2012 main source's “around 210” prose | A's introductory route prose calls the total “around 210 coins,” but its ten mandatory price cells sum exactly to **208**. The implementation price total uses the explicit cells, not an approximate travel-budget sentence. |

## Not recovered

The task is read-only and may create only this audit. `tests/test_placeholder_register.py:20-55` scans shipped Python for exact `PLACEHOLDER(<id>)` markers and requires a matching row in `memory-bank/placeholder-values.md`. No shipped Bar Crawl value exists yet, so adding either half would create a stale/mismatched register entry and violate the read-only boundary.

Accordingly, no registered placeholder is emitted by this harvest. The rows below
are **source_blocked** and name the mandatory marker that a future implementation
must add atomically in shipped Python and the live register if it needs the
value. Until then, the implementation must fail closed or omit the unsourced
behavior; it must not supply a plausible default.

| Future required marker | Source-blocked value | What would settle it |
| --- | --- | --- |
| `PLACEHOLDER(bar_crawl.stat_drain_magnitudes)` | Every numerical per-skill drain, including whether Olde Suspiciouse has a seventh distinct skill. | Period server evidence, a dated official mechanic guide, or an independently corroborated period implementation. |
| `PLACEHOLDER(bar_crawl.gutrot_damage_formula)` | Gutrot's damage maximum/formula and random boundary; the period records conflict between **20** and **200**. | A higher-quality dated official or period server source resolving the conflict. |
| `PLACEHOLDER(bar_crawl.drink_damage_transaction)` | Exact roll/arithmetic/protection/death semantics for Fire Toad Blast, Heart Stopper, and Hand of Death. | Period server behavior or a dated technical record that states the transaction. |
| `PLACEHOLDER(bar_crawl.drunk_visual_duration)` | Exact camera/visual effect duration and whether Liverbane Ale has one. | Period capture, dated official record, or period-client/server behavior that explicitly establishes it. |
| `PLACEHOLDER(bar_crawl.card_recovery_state)` | Exact loss detection, bank behavior, replacement prerequisites, partial-signature persistence, and completed-card disposition. | Period dialogue/transcript or independently corroborated period server behavior. |
| `PLACEHOLDER(bar_crawl.dialogue_and_timing)` | Exact dialogue, response choices, action delays, locks, animations, and completion-interface contents. | Pre-cutoff transcript/Wayback capture or official dialogue archive plus period behavior evidence. |

## Later Darkan-audit check list

A later audit of `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/` can check its unaudited implementation against these pins without treating the implementation as the source of history:

1. `BarCrawl.kt` must retain the **10** named venue/drink pairs, prices
   `50,10,15,12,8,18,10,7,70,8`, card **455**, guard **384**, and the
   R7/R42 NPC mapping in the venue table.
2. `BarEffects.kt` can be compared against A's affected-skill and visible-effect
   categories. Its numerical drains, `Utils.random` calls, animation **829**,
   true-damage calls, and camera timings are specifically *not* closed here and
   need their own period evidence before being promoted.
3. `BarbarianGuardD.kt` can be checked for period-compatible start/all-ten/return
   shape and access reward. Its state integers, inventory/bank/free-slot rules,
   exact spawn coordinates, gate/ejection logic, and completion UI remain
   implementation details awaiting evidence.
4. `BartenderUtils.kt:37-50` and the relevant area handlers can be checked to
   ensure each named bartender actually binds only the corresponding unvisited
   Bar Crawl deed. Their delay and lock mechanics require separate sourcing.
5. The project may cross-check its `quests-scorpion-catcher` and
   `quests-horror-from-the-deep` rows against the two historically pinned
   downstream dependencies above, but those runtime rows must not be expanded
   into proof of the miniquest internals.

## Handoff boundary

The route can now be implemented as a real, reachable miniquest: start with
card **455** from guard **384**, complete exactly the ten named price-backed
venue deeds in any order, return to the guard, write the completion state, and
thereby release the already-wired Barbarian Outpost course gates plus the
Horror from the Deep and Scorpion Catcher prerequisites.

The completion route, prices, client identities, named affected stats, visible
effects, Outpost reward, and downstream unlocks are pinned at the stated
boundary. Exact numeric drains, server damage arithmetic, visual timing, card
recovery, and dialogue remain source-blocked. No implementation may present
those Darkan reconstruction details as settled pre-EOC behavior.
