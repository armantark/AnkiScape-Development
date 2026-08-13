# Farming pre-EOC wiki-pin ledger — 2026-07-11

> **Supersession notes:**
>
> - 2026-08-09: the Fellstalk entry under missing acquisition routes is
>   superseded by `source-audits/fellstalk-seed-acquisition-2026-08-09.md`.
>   Cutoff Master Farmer oldid `6565826` proves one Fellstalk seed at `Very
>   Rare`; only its hidden relative weight remains a registered placeholder.
> - 2026-08-13: the crop dispositions below were re-audited with dedicated
>   item pages, stage tables, Darkan path history, and the real AnkiScape
>   kernels. White lily, Wergali, Red blossom, Green blossom, and Kalferberry
>   now ship; Blue blossom, Lergberry, Goutweed, and Spirit tree remain blocked
>   for the exact fields recorded in section H. Where section H conflicts with
>   the original July verdicts, section H governs.

Cutoff: strictly before `2012-11-20T00:00:00Z`. Wiki evidence is literal `runescape.wiki` wikitext resolved by `tools/wiki_parity.py`; “GM” is `/Users/ArmanTarkhanian1/Downloads/game-main`; “DK” is Darkan commit `7e7d67b`, read only with `git show`. A modern page is mentioned only once, as a lead proving that Patch bomb belongs to a later update; it is not promoted to period proof.

## A. Resolution table

Exactly **35 of the 38 requested page titles resolved to a pre-cutoff revision**. Three requested titles had no pre-cutoff revision: `Fruit tree patch`, `Farming Patch Bomb`, and `Vine bush patch`. The fruit-tree and vine-bush questions are recoverable from other pinned pages; Patch bomb is struck as post-cutoff.

| # | Requested page | Resolved period page | oldid | UTC timestamp | Verdict | Note |
|---:|---|---|---:|---|---|---|
| 1 | Farming | Farming | 6565110 | 2012-11-17T05:59:19Z | partial | Broad loop and tables settle most questions; its period text conflicts with dedicated pages on secateurs, watering yield, and some growth data. |
| 2 | Farming/Patches | Farming/Patch locations | 6552430 | 2012-11-13T19:21:29Z | settled | Obvious-title variant resolved; combined with Herblore Habitat oldid 6513740 it enumerates the repeatable map. |
| 3 | Compost | Compost | 6337625 | 2012-10-02T20:38:53Z | partial | Settles capacity, collection/application XP, and a maturation range; exact disease multiplier and exact extra lives are absent. |
| 4 | Supercompost | Supercompost | 6337626 | 2012-10-02T20:39:13Z | partial | Settles capacity, collection/application XP, and maturation; exact disease multiplier and exact extra lives are absent. |
| 5 | Seeds | Seeds | 6565109 | 2012-11-17T05:58:56Z | partial | Main crop tables settle most disputes; a few rows conflict with dedicated articles or contain `?`. |
| 6 | Allotment patch | Allotment patch | 924755 | 2009-02-09T01:23:32Z | settled | Redirect; substantive table comes from Seeds oldid 6565109 and Farming oldid 6565110. |
| 7 | Flower patch | Flower Patch | 245960 | 2007-10-17T15:37:02Z | partial | Redirect; scarecrow settles via oldid 6487851, but white-lily plant XP remains conflicted. |
| 8 | Herb patch | Herb patch | 6567051 | 2012-11-17T17:14:11Z | partial | Standard herbs settle; wergali harvest XP conflicts with Seeds oldid 6565109. |
| 9 | Hops patch | Hops Patch | 3917667 | 2011-02-21T11:30:03Z | settled | Redirect; Farming oldid 6565110 explicitly special-cases jute to 3 seeds. |
| 10 | Bush patch | Bush Patch | 3649739 | 2010-12-28T23:27:36Z | settled | Redirect; conventional table is present in Farming/Seeds oldids 6565110/6565109. |
| 11 | Tree patch | Tree patch | 6531843 | 2012-11-04T09:11:49Z | partial | Willow decimal settles, but several growth durations conflict with Farming/Seeds. |
| 12 | Fruit tree patch | — | — | — | settled | Exact title has no pre-cutoff revision; complete distinct table is in Seeds oldid 6565109 and Herblore Habitat oldid 6513740. |
| 13 | Calquat tree | Calquat Tree | 5539026 | 2012-04-27T10:32:07Z | settled | Dedicated page says 1,200 minutes; nearer Seeds table says 1,280 minutes and agrees with GM. Nearest table wins. |
| 14 | Cactus | Cactus | 6125072 | 2012-08-21T14:10:53Z | settled | Combined with Seeds oldid 6565109, closes level, XP, time, yield, regrowth, and payment. |
| 15 | Mushroom patch | Mushroom patch | 5432839 | 2012-03-28T02:00:28Z | settled | Combined with Seeds closes both mushrooms and the optional Task-set disease-immunity benefit. |
| 16 | Belladonna | Cave nightshade (Farming) | 3617211 | 2010-12-20T20:29:58Z | settled | Redirect; Seeds oldid 6565109 carries the complete numeric row. |
| 17 | Spirit tree | Spirit tree | 6549224 | 2012-11-12T08:44:58Z | partial | Level/XP/payment/locations settle; period sources disagree on exact stage count and total time. |
| 18 | Jade vine | Jade vine | 6579442 | 2012-11-18T23:48:25Z | settled | Complete era grow/check/prune/regrow/monster/seed-return loop is explicit. |
| 19 | Evil turnip | Evil turnip | 6538769 | 2012-11-06T07:37:42Z | settled | Combined with Seeds oldid 6565109, proves an era grow-and-harvest loop; exact disease immunity is not stated by the wiki. |
| 20 | Goutweed | Goutweed | 5668713 | 2012-05-28T01:00:52Z | partial | Crop row settles; exact yield and whether planting itself requires Eadgar’s Ruse are not established. |
| 21 | White lily | White lily | 6579222 | 2012-11-18T17:41:44Z | source_blocked | Level and harvest XP settle; planting XP conflicts between this page and Seeds oldid 6565109. |
| 22 | Magic secateurs | Magic secateurs | 6549114 | 2012-11-12T06:09:19Z | settled | Dedicated article says 15%, but Farming and Fairytale I say 10%; GM and DK both implement ×1.1. The 10% reading wins by corroboration. |
| 23 | Fairytale I – Growing Pains | A Fairy Tale I - Growing Pains | 6565661 | 2012-11-17T08:51:40Z | settled | Obvious-title variant resolved; requirements, secateurs route, and rewards are explicit. |
| 24 | Plant cure | Plant cure | 6530314 | 2012-11-04T01:28:45Z | settled | Price/use settle; Farming’s exhaustive minor-XP list omits cure, supporting 0 XP rather than DK’s 90. |
| 25 | Watering can | Watering can | 5529251 | 2012-04-25T05:43:22Z | partial | Eight charges and one-cycle disease reduction settle; category and yield wording conflict, and no exact multiplier is pinned. |
| 26 | Farmer | Farmer | 5906402 | 2012-07-08T11:22:07Z | partial | Generic NPC page is not the gardener contract; Farming oldid 6565110 supplies payment semantics. |
| 27 | Tool leprechaun | Tool leprechaun | 6226101 | 2012-09-09T22:38:26Z | settled | Storage capacities, shared access, noting, and exclusions are explicit. |
| 28 | Amulet of farming | Amulet of farming | 6391494 | 2012-10-12T18:26:36Z | settled | Patch categories, binding, alerts, and charges are explicit. |
| 29 | Amulet of nature | Amulet of nature | 6447594 | 2012-10-20T21:37:50Z | partial | Monitoring/teleport/remote gardener settle; exact yield bonus is unstated. |
| 30 | Scroll of life | Scroll of life | 6151122 | 2012-08-26T22:45:36Z | settled | Percentages and exceptions are explicit. |
| 31 | Greenfingers aura | Greenfingers aura | 6016051 | 2012-07-30T14:14:59Z | settled | Base tier settles; tier pins 5906688, 5827643, and 6282706 close the full ladder. |
| 32 | Juju farming potion | Juju farming potion | 6566235 | 2012-11-17T15:19:41Z | settled | Duration, eligibility, roll, ingredients, and no-extra-XP rule are explicit. |
| 33 | Farming Patch Bomb | — | — | — | source_blocked | No requested or obvious title had a pre-cutoff revision. A current lead identifies Patch bomb as a 2014 activity reward, so it is struck. |
| 34 | Herblore Habitat | Herblore Habitat | 6513740 | 2012-10-31T21:20:32Z | partial | Activity, patch inventory, crop tables, shop, and Jadinko routes settle; several crop timings/yields remain absent. |
| 35 | Vine flower patch | Vine flower patch | 4804401 | 2011-10-01T22:49:41Z | settled | Redirect to Herblore Habitat oldid 6513740; three blossom rows settle. |
| 36 | Vine herb patch | Vine herb patch | 4613386 | 2011-08-10T02:34:34Z | partial | Redirect to Herblore Habitat; XP/payments settle, exact times and yields do not. |
| 37 | Vine bush patch | — | — | — | partial | No pre-cutoff revision under the exact title; Herblore Habitat oldid 6513740 settles XP/payments but not stages/time/yield. |
| 38 | Jadinko | Jadinkos | 5917881 | 2012-07-10T13:09:23Z | settled | Primary vine drops and seed-family drops are explicit. |

## B. Disputed-value verdicts

| Value | GM | DK at `7e7d67b` | PINNED period value | Winner | Citation |
|---|---|---|---|---|---|
| Apple check-health XP | 1,199.5 | 1,199.5 | 1,199.5 | pinned/GM/DK | Seeds oldid 6565109; GM `Seed.kt:1158-1184`; DK `ProduceType.java:77`. |
| Banana check-health XP | 1,199.5 | 1,750.5 | 1,750.5 | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:1185-1211`; DK `ProduceType.java:78`. |
| Orange check-health XP | 1,199.5 | 2,470.2 | 2,470.2 | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:1212-1238`; DK `ProduceType.java:79`. |
| Curry check-health XP | 1,199.5 | 2,906.9 | 2,906.9 | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:1239-1265`; DK `ProduceType.java:80`. |
| Pineapple check-health XP | 1,199.5 | 4,605.7 | 4,605.7 | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:1266-1292`; DK `ProduceType.java:81`. |
| Papaya check-health XP | 1,199.5 | 6,146.4 | 6,146.4 | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:1293-1319`; DK `ProduceType.java:82`. |
| Palm check-health XP | 1,199.5 | 10,150.1 | 10,150.1 | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:1320-1346`; DK `ProduceType.java:83`. |
| Calquat total growth | 1,280 min (21 h 20 min) | 640 min (10 h 40 min) | 1,280 min in the nearest Seeds table; older dedicated page says 1,200 min | GM, corroborated by nearest pin | Seeds oldid 6565109; Calquat Tree oldid 5539026; GM `SeedType.kt:96-101`; DK `PatchType.java`. |
| Calquat check-health XP | 12,096 | 12,096 | 12,096 | pinned/GM/DK | Seeds oldid 6565109; Calquat Tree oldid 5539026; GM `Seed.kt:1486-1512`; DK `ProduceType.java`. |
| Sweetcorn protection | 1 basket of 5 apples | 10 jute fibres | 10 jute fibres | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:714-740`; DK `ProduceType.java:37-43`. |
| Strawberry protection | 10 curry leaves | 1 basket of 5 apples | 1 basket of 5 apples | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:741-767`; DK `ProduceType.java:37-43`. |
| Watermelon protection | 5 jangerberries | 10 curry leaves | 10 curry leaves | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:768-794`; DK `ProduceType.java:37-43`. |
| Jute seeds per planting | 4 | 3 | 3 | pinned/DK | Farming oldid 6565110; Seeds oldid 6565109; GM `SeedType.kt:25-40`; DK `FarmPatch.java:243-253`. |
| White-lily level | 58 (disabled row) | 52 | 52 | pinned/DK | White lily oldid 6579222; Seeds oldid 6565109; GM `Seed.kt:596-601`; DK `ProduceType.java:51`. |
| White-lily planting XP | 42 (disabled row) | 70 | **source_blocked:** 50 on White lily, 70 on Seeds | none | White lily oldid 6579222; Seeds oldid 6565109; GM `Seed.kt:596-601`; DK `ProduceType.java:51`. |
| Scarecrow placement/making level | 1 | 23 | 23 | pinned/DK | Scarecrow oldid 6487851; GM `Seed.kt:569-595`; DK `ProduceType.java:50`. |
| Willow check-health XP | 1,456.5 | 1,456.3 | 1,456.3 | pinned/DK | Tree patch oldid 6531843; Seeds oldid 6565109; GM `Seed.kt:1378-1404`; DK `ProduceType.java:85-89`. |
| Lantadyme planting XP | 135.5 | 134.5 | 134.5 | pinned/DK | Seeds oldid 6565109; GM `Seed.kt:349-375`; DK `ProduceType.java:68`. |
| Plant-cure Farming XP | 0 | 90 | 0; cure is absent from the period page’s exhaustive minor-XP list | pinned/GM | Plant cure oldid 6530314; Farming oldid 6565110; GM `logic/handler/CureHandler.kt:20-38` (no XP award); DK `FarmPatch.java:286-301`. |
| Compost application XP | 18 | 18 | 18 | pinned/GM/DK | Compost oldid 6337625; Farming oldid 6565110; GM `constants/CompostState.kt:15-17`; DK `FarmPatch.java:268-285`. |
| Supercompost application XP | 26 | 18 because of defect | 26 | pinned/GM | Supercompost oldid 6337626; Farming oldid 6565110; GM `constants/CompostState.kt:15-17`; DK `FarmPatch.java:268-285`. |
| Compost disease factor | 0.28 | defective level formula | **source_blocked:** wiki only says reduced | none | Compost oldid 6337625; Farming oldid 6565110; GM `constants/CompostState.kt:15-17`; DK `FarmPatch.java:455-479`. |
| Supercompost disease factor | 0.14 | defective level formula | **source_blocked:** Farming says 30% reduction while other prose says stronger than compost; no exact GM factor | none | Farming oldid 6565110; Supercompost oldid 6337626; GM `constants/CompostState.kt:15-17`; DK `FarmPatch.java:455-479`. |
| Compost extra harvest lives | +1 | defective/unclear | **source_blocked:** wiki says minimum and maximum yield increase, not +1 | none | Compost oldid 6337625; GM `constants/CompostState.kt:15-17`. |
| Supercompost extra harvest lives | +2 | defective/unclear | **source_blocked:** wiki says minimum and maximum yield increase, not +2 | none | Supercompost oldid 6337626; GM `constants/CompostState.kt:15-17`. |
| Compost-bin capacity | 15 | 15 candidate | 15 | pinned | Compost oldid 6337625; Supercompost oldid 6337626; GM `CompostBinHandler.kt:35-40,95-103`. |
| Compost maturation | 25 min in GM’s 5-state, 5-min tick implementation | not reliable | 35–50 min on Compost; Farming guide says 45 min | pinned wiki, represented as a range | Compost oldid 6337625; Farming oldid 6565110; GM `CompostBinState.kt:13-14`, `CompostBinHandler.kt:199-217`, `FarmTicker.kt:12-15`. |
| Supercompost maturation | 25 min in GM’s same 5-state path | not reliable | 90 min | pinned wiki | Supercompost oldid 6337626; GM `CompostBinState.kt:13-14`, `CompostBinHandler.kt:199-217`, `FarmTicker.kt:12-15`. |
| Magic-secateurs yield bonus | ×1.1 | ×1.1 | 10% for allotments, herbs, and hops; dedicated item article’s 15% is rejected as an isolated contradiction | GM/DK plus two period pins | Farming oldid 6565110; Fairytale I oldid 6565661; contradictory Magic secateurs oldid 6549114; GM `HarvestingHandler.kt:106-120`; DK `HarvestPatch.java`. |
| Watering categories | allotments, flowers, hops | allotments, flowers, hops, vine flowers | allotments, flowers, hops; seedlings also require water to become saplings | pinned/GM | Farming oldid 6565110; Tool leprechaun oldid 6226101; Watering can oldid 5529251; GM `WateringHandler.kt`; DK `FarmPatch.java:303-310`. |
| Watering effect | ×0.9 disease roll for current stage | eligibility flag | one growth cycle of reduced disease; exact multiplier and claimed slight-yield effect are **source_blocked** | qualitative pin only | Farming oldid 6565110; Watering can oldid 5529251; GM `GrowingHandler.kt:14-65`. |
| Watering-can charges | 8 | charge-bearing item | 8, refillable | pinned | Watering can oldid 5529251. AnkiScape’s no-charge handling is an explicit abstraction, not parity. |

## C. Complete November-2012 patch inventory

### Count verdict

The period pages do not print one grand total, but their literal rows enumerate **51 repeatable crop patches plus 6 compost bins = 57 repeatable Farming locations**. They also list **2 one-off quest patches**, making **59 physical patch/bin locations** if one-off quest scenery is included. DK’s `51 crop + 6 compost` count is therefore the correct repeatable map; GM’s `34 crop + 4 compost` covers only the conventional subset and is short by **17 repeatable crop patches and 2 compost bins**. [Farming/Patch locations oldid 6552430; Herblore Habitat oldid 6513740; DK `PatchLocation.java:24-97` at `7e7d67b`; GM `Patch.kt` and `CompostBin.kt`]

### Repeatable inventory

Counts in the “Qty” column are physical patches at that location, not crop varieties.

| Location complex | Type | Qty | Access gate by cutoff | Evidence |
|---|---|---:|---|---|
| South Falador | Allotment / flower / herb / compost | 2 / 1 / 1 / 1 | None; diary rings are travel conveniences only | oldid 6552430 |
| West of Port Phasmatys | Allotment / flower / herb / compost | 2 / 1 / 1 / 1 | No patch-specific gate stated; Morytania area access remains a world/quest concern | oldid 6552430 |
| North Catherby | Allotment / flower / herb / compost | 2 / 1 / 1 / 1 | None | oldid 6552430 |
| North Ardougne/Hemenster | Allotment / flower / herb / compost | 2 / 1 / 1 / 1 | None; Ardougne Task teleports are not access gates | oldid 6552430 |
| Wilderness western ruins | Limpwurt-only flower | 1 | Spirit of Summer; pin also names a 64 Agility shortcut | oldid 6552430 |
| Harmony Island | Allotment | 1 | The Great Brain Robbery | oldid 6552430 |
| Taverley/Burthorpe field | Potato-only allotment / compost | 1 / 1 | None; Head Farmer Jones supplies 3 potato seeds and watches the crop | oldid 6552430 |
| Troll Stronghold roof | Herb | 1 | My Arm’s Big Adventure; disease-free; cannot grow goutweed | oldids 6552430 and 6567051 |
| North Lumbridge farm | Hops | 1 | None | oldid 6552430 |
| North McGrubor’s Wood | Hops | 1 | None | oldid 6552430 |
| Yanille | Hops | 1 | None; Hard Ardougne Tasks alter a teleport, not patch access | oldid 6552430 |
| Entrana | Hops | 1 | None; Entrana item restrictions are travel/equipment rules | oldid 6552430 |
| West Champions’ Guild | Bush | 1 | None | oldid 6552430 |
| Rimmington | Bush | 1 | None | oldid 6552430 |
| South Ardougne | Bush | 1 | None | oldid 6552430 |
| Etceteria | Bush | 1 | Throne of Miscellania area access | Farming oldid 6565110; location oldid 6552430 |
| West Lumbridge | Tree | 1 | None | oldid 6552430 |
| Varrock Castle courtyard | Tree | 1 | None | oldid 6552430 |
| Falador Park | Tree | 1 | None | oldid 6552430 |
| Taverley | Tree | 1 | None | oldid 6552430 |
| Tree Gnome Stronghold | Tree | 1 | None stated for patch use | oldid 6552430 |
| Tree Gnome Stronghold | Fruit tree | 1 | None stated for patch use | oldid 6552430 |
| East Catherby | Fruit tree | 1 | None | oldid 6552430 |
| West Tree Gnome Village maze | Fruit tree | 1 | None stated for patch use | oldid 6552430 |
| North Brimhaven | Fruit tree | 1 | None | oldid 6552430 |
| Lletya | Fruit tree | 1 | Mourning’s End Part I | Farming oldid 6565110; location oldid 6552430 |
| Herblore Habitat middle camp | Fruit tree / vine flower / vine bush / vine herb / compost | 1 / 1 / 1 / 1 / 1 | No quest; crop levels start at 54 Farming | Herblore Habitat oldid 6513740 |
| Herblore Habitat east camp | Vine herb | 1 | 55 Agility shortcut to reach east camp; no quest | Herblore Habitat oldid 6513740 |
| Etceteria | Spirit tree | 1 | Area access; 83 Farming to plant; 86 Farming + The Prisoner of Glouphrie permits a second concurrent tree | Spirit tree oldid 6549224; location oldid 6552430 |
| East Port Sarim | Spirit tree | 1 | 83 Farming to plant; Tree Gnome Village unlocks network use | Spirit tree oldid 6549224; location oldid 6552430 |
| North Brimhaven | Spirit tree | 1 | 83 Farming to plant; Tree Gnome Village unlocks network use | Spirit tree oldid 6549224; location oldid 6552430 |
| Draynor Manor | Evil turnip | 1 | 42 Farming; no quest | Evil turnip oldid 6538769; Seeds oldid 6565109 |
| West Canifis | Mushroom | 1 | No access quest stated by pin; Medium Morytania Tasks grant disease immunity but do not unlock the patch | Mushroom patch oldid 5432839 |
| Al Kharid | Cactus | 1 | 55 Farming; no quest | Cactus oldid 6125072; Seeds oldid 6565109 |
| Draynor Manor | Belladonna | 1 | 63 Farming; no quest | Seeds oldid 6565109; location oldid 6552430 |
| Tai Bwo Wannai | Calquat | 1 | 72 Farming; Jungle Potion is required to pay Imiago, not to identify the patch | Calquat Tree oldid 5539026 |
| East Ardougne, Handelmort Mansion | Jade vine | 1 | Back to My Roots and 53 Farming | Jade vine oldid 6579442; location oldid 6552430 |

### One-off quest patches, excluded from the repeatable 51

| Location | Type | Qty | Gate | Evidence |
|---|---|---:|---|---|
| Taverley | Beanstalk | 1 | Grim Tales; leaves an irremovable beanstump | Farming/Patch locations oldid 6552430 |
| Falador Castle roof | Enriched-snapdragon herb | 1 | While Guthix Sleeps; one use | Farming/Patch locations oldid 6552430 |

The period Farming prose also names a Kelda-hops quest patch for Forgettable Tale of a Drunken Dwarf, but the pinned location table does not give it a physical patch row. It is therefore recorded as quest scenery, not added to the repeatable or physical-location totals. [Farming oldid 6565110]

### Diary/Task-set verdict

**No Farming patch was access-gated behind an Achievement Diary/Task-set completion by the cutoff.** Task sets supplied benefits: the Medium Morytania set made the already accessible mushroom patch disease-free, the Hard Falador set unlocked purchase of white-lily seeds, and several sets supplied teleports. None unlocked a patch itself. [Farming/Patch locations oldid 6552430; Mushroom patch oldid 5432839; White lily oldid 6579222]

### Flower protection by complex

At each of the four full complexes—South Falador, west of Port Phasmatys, north Catherby, and north Ardougne—the single flower patch protects only that complex’s two adjacent allotments. The mapping is: marigold → potato/onion/tomato; rosemary → cabbage; scarecrow → sweetcorn; nasturtium → watermelon; white lily → every allotment crop; strawberry has no ordinary flower protector. Mature flowers must remain in the co-located patch. [Farming oldid 6565110; Seeds oldid 6565109; Scarecrow oldid 6487851]

## D. Special-crop verdicts

`—` means the action does not exist for that crop; `source_blocked` means the pin did not establish it.

| Crop | Era-valid and complete? | Level / XP (plant; check; harvest) | Stages and time | Yield / protection / gate | Verdict and citations |
|---|---|---|---|---|---|
| Cactus | Yes | 55; 66.5; 374; 25 per spine | 7 × 80 min = 560 min | 3 regenerating spines; 6 cadava berries; no quest | **CLOSED.** Seeds oldid 6565109; Cactus oldid 6125072. DK’s derived 24.9375 is rejected. |
| Bittercap mushroom | Yes | 53; 61.5; —; 57.7 each | 6 × 40 min = 240 min | 6 fixed mushrooms; no farmer payment; Medium Morytania Tasks optionally immunise the patch | **CLOSED.** Seeds oldid 6565109; Mushroom patch oldid 5432839. |
| Morchella mushroom | Yes | 74; 160; —; 77.7 each | 6 × 40 min = 240 min | 9 fixed mushrooms; no farmer payment; same optional Task-set immunity | **CLOSED.** Seeds oldid 6565109; Mushroom patch oldid 5432839. |
| Belladonna | Yes | 63; 91; —; 512 | 4 × 80 min = 320 min | 1 cave nightshade; no farmer; no quest | **CLOSED.** Seeds oldid 6565109. This contradicts DK’s 160-min total. |
| Evil turnip | Yes | 42; 41; —; 46 | 1 × 5 min in Seeds; dedicated page says 4 min 30 sec | 1 turnip; no payment; no quest; wiki does not explicitly state disease immunity | **CLOSED for shipping.** The complete seed→grow→pick loop is pinned by Seeds oldid 6565109 and Evil turnip oldid 6538769. Use DK’s immunity only as reconciled implementation evidence, not a wiki-derived number. |
| Spirit tree | Yes, but timing partial | 83; 199.5; 19,301.8; — | **source_blocked:** Seeds says 11 × 320 min = 3,520 min; dedicated article says about 3,680 min; DK says 12 × 320 min = 3,840 min | No produce; 5 monkey nuts + 1 monkey bar + 1 ground Suqah tooth; 3 locations; first planted tree at 83, second at 86 plus The Prisoner of Glouphrie | **PARTIAL.** Seeds oldid 6565109; Spirit tree oldid 6549224; DK `PatchType.java`/`ProduceType.java`. |
| Jade vine | Yes | 53; 50; 1,500; 30 per pruned branch | 6 × 160 min = 960 min; branches regrow about every 30–60 min | 5 visible branches; the unseen 6th turns wild; fully pruning earns 6 × 30 XP; 10 wildblood hops; Back to My Roots; killing wild vine returns a seed | **CLOSED; SHIPS.** Jade vine oldid 6579442; Seeds oldid 6565109. The pin supersedes DK’s zero-lives bug. |
| Goutweed from gout tuber | Yes, row partial | 29; 105; —; 45 each | 4 × 20 min = 80 min | Variable herb yield is not pinned; no payment; tuber from Tai Bwo Wannai Cleanup or Scroll of life; pin does not prove DK’s Eadgar’s Ruse planting gate | **PARTIAL.** Seeds oldid 6565109; Goutweed oldid 5668713; DK `FarmPatch.java:217-225`. |
| Wergali | Yes | 46; 52.8; —; **source_blocked: 51.5 vs 52.8** | 4 × 20 min = 80 min | Variable herb yield; no payment; no quest | **PARTIAL.** Herb patch oldid 6567051 says 51.5 harvest XP; Seeds oldid 6565109 says 52.8. |
| Fellstalk | Yes | 91; 225; —; 315.6 | 4 × 20 min = 80 min | Variable herb yield; no payment; no quest | **CLOSED except exact yield distribution.** Seeds oldid 6565109; Herb patch oldid 6567051. |
| White lily | Yes, numeric block | 52; **source_blocked: 50 vs 70**; —; 250 | 4 × 20 min = 80 min | 1 lily becomes ashes; protects all allotments; seed purchase requires Hard Falador Tasks | **SOURCE_BLOCKED for implementation constant.** White lily oldid 6579222; Seeds oldid 6565109. |
| Red blossom | Yes | 54; 52; —; 255 | Total 20 min; exact stage count/time **source_blocked** | 1 blossom candidate; no payment; no quest; seed sold by Papa Mambo for 50 coins | **PARTIAL.** Herblore Habitat oldid 6513740; Seeds oldid 6565109; Papa Mambo’s Shop oldid 6393083. |
| Blue blossom | Yes | 54; 52; —; 255 | Total 20 min; exact stage count/time **source_blocked** | 1 blossom candidate; no payment; no quest; seed sold for 50 coins | **PARTIAL.** Same pins as red blossom. |
| Green blossom | Yes | 54; 52; —; 255 | Total 20 min; exact stage count/time **source_blocked** | 1 blossom candidate; no payment; no quest; seed sold for 50 coins | **PARTIAL.** Same pins as red blossom. |
| Erzille | Yes | 58; 87; —; 87 each | DK candidate 4 × 20 min = 80 min; pin says `?` | Yield **source_blocked**; 3 green blossoms; seed from Jadinkos; no quest | **PARTIAL/SOURCE_BLOCKED timing and yield.** Herblore Habitat oldid 6513740; Seeds oldid 6565109; DK `ProduceType.java`/`PatchType.java`. |
| Argway | Yes | 65; 110; —; 125 each | DK candidate 4 × 20 min = 80 min; pin says `?` | Yield **source_blocked**; 4 red blossoms; seed from Jadinkos | **PARTIAL/SOURCE_BLOCKED timing and yield.** Herblore Habitat oldid 6513740; Seeds oldid 6565109. |
| Ugune | Yes | 70; 135; —; 152 each | Pin gives 80 min total; exact stages **source_blocked** | Yield **source_blocked**; 3 blue blossoms; seed from Jadinkos | **PARTIAL.** Herblore Habitat oldid 6513740; Seeds oldid 6565109. |
| Shengo | Yes | 76; 140.5; —; 160 each | DK candidate 80 min; pin says `?` | Yield **source_blocked**; 5 lergberries; seed from Jadinkos | **PARTIAL/SOURCE_BLOCKED timing and yield.** Herblore Habitat oldid 6513740; Seeds oldid 6565109. |
| Samaden | Yes | 80; 170; —; 190 each | **source_blocked:** Seeds says 60 min; DK says 4 × 20 min = 80 min | Yield **source_blocked**; 5 kalferberries; seed from Jadinkos | **PARTIAL/SOURCE_BLOCKED timing and yield.** Herblore Habitat oldid 6513740; Seeds oldid 6565109. |
| Lergberry | Yes | 61; 145.5; 236.3; 31.5 each | Stages/time **source_blocked** (DK candidate 6 × 20 min = 120 min) | Regenerating count **source_blocked**; 3 red blossoms; seed from Jadinkos | **PARTIAL.** Herblore Habitat oldid 6513740; Seeds oldid 6565109. DK’s derived 54.5625 harvest XP is disproved. |
| Kalferberry | Yes | 77; **220.2 vs 220**; **375.3 vs 375**; 52.5 each | **source_blocked:** Seeds says 75 min; DK says 120 min | Regenerating count **source_blocked**; 3 lergberries; seed from Jadinkos | **PARTIAL/SOURCE_BLOCKED decimals and timing.** Herblore Habitat oldid 6513740; Seeds oldid 6565109. DK’s derived 82.5 harvest XP is disproved. |

## E. Cross-cutting verdicts

| Mechanic/item | Era verdict and exact period behavior | Evidence verdict |
|---|---|---|
| Juju farming potion | Released 24 Nov 2010; 5-minute effect; each herb picked from ordinary or Habitat herb patches has an independent 1-in-3 extra-herb roll; extra herb grants 0 XP; clean ugune + marble vine; no evidence of flower/fruit eligibility | **SURVIVES.** Juju farming potion oldid 6566235; Herblore Habitat oldid 6513740. |
| Greenfingers aura family | Base/greater/master/supreme are era-valid. Extra-yield chances are 3%/5%/7%/10%; each lasts 20 min and recharges in 1 h. Base through master prevent disease only during active cycles; supreme’s disease prevention explicitly excludes herbs. Extra produce grants 0 XP on the base tier. | **SURVIVES but remains deferred by product contract.** oldids 6016051, 5906688, 5827643, 6282706. |
| Farming patch bomb | No pre-cutoff revision. The current Patch bomb page identifies release on 14 Apr 2014 from Cabbage Facepunch Bonanza, not Solomon’s Store. | **STRUCK as post-cutoff.** No period oldid; modern lead oldid 37010730 is used only to identify the later update. |
| Scroll of life | Permanent unlock at 25 Farming + 25 Dungeoneering, bought for 10,000 tokens; 10% seed return from non-tree/non-flower patches, including dead ones; 5% from dead trees/stumps; works in Habitat; excludes special patches including spirit/calquat; live herbs return same seed, dead herbs random | **SURVIVES but defers to Dungeoneering.** Scroll of life oldid 6151122. |
| Amulet of farming | Binds all owned amulets to one allotment or ordinary flower patch; excludes vine flowers; 8 charges consumed by full rub checks; worn hum alerts disease/maturity without charge; no teleport | Era-valid but intentionally function-trailed by HUD. Amulet of farming oldid 6391494. |
| Amulet of nature | One owned; binds any patch; infinite checks; worn vibration plus login notification; rub status; can contact/pay gardener remotely and teleport only when diseased; slight yield bonus exists but exact percentage is **source_blocked** and does not stack with secateurs | Era-valid but intentionally function-trailed by HUD. Amulet of nature oldid 6447594; Farming oldid 6565110. |
| Fairytale I - Growing Pains | Start at Martin; prerequisite surface is transcluded by `Questreq` and therefore not fully literal in this revision. The route requires ordinary secateurs plus assigned items, Ghostspeak, Dramen/Lunar access, Nature Spirit enchantment, and killing level-111 Tanglefoot with magic secateurs. Rewards: 2 quest points, magic secateurs, 3,500 Farming XP, 2,000 Attack XP, 1,000 Magic XP, and 2 Squeal spins. Secateurs apply 10% to allotments/herbs/hops. | Route and rewards closed; transcluded prerequisite dependency remains outside this pin. Fairytale I oldid 6565661; Farming oldid 6565110. |
| Farmer protection | Payment may use noted items. Period wiki says the crop can still become diseased and the gardener cures it, guaranteeing survival but potentially delaying growth. This is not literally “never diseased.” | **Contract wording correction required.** Farming oldid 6565110. |
| Watering | Allotments, flowers, hops, and potted seedlings; reduces disease for one growth cycle. Eight charges are historically meaningful. Exact ×0.9 and slight-yield claims are not jointly pinned. | Disease semantics partial; AnkiScape’s untracked charges are an explicit abstraction. Farming oldid 6565110; Watering can oldid 5529251; Tool leprechaun oldid 6226101. |

## F. Seed acquisition audit

### Pinned era acquisition surfaces

#### Draynor Seed Market stock and era prices

Sell price is the player’s purchase price; stock `0` means the shop buys the seed but does not naturally stock it.

| Seed | Base stock | Sell price | Pin |
|---|---:|---:|---|
| Potato | 10 | 8 coins | Draynor Seed Market oldid 6476725 |
| Onion | 10 | 10 coins | oldid 6476725 |
| Cabbage | 10 | 25 coins | oldid 6476725 |
| Tomato | 0 | 4 coins | oldid 6476725 |
| Sweetcorn | 0 | 8 coins | oldid 6476725 |
| Strawberry | 0 | 18 coins | oldid 6476725 |
| Watermelon | 0 | 56 coins | oldid 6476725 |
| Barley | 10 | 38 coins | oldid 6476725 |
| Jute | 10 | 86 coins | oldid 6476725 |
| Marigold | 10 | 84 coins | oldid 6476725 |
| Rosemary | 10 | 98 coins | oldid 6476725 |
| Hammerstone | 10 | 52 coins | oldid 6476725 |
| Asgarnian | 10 | 60 coins | oldid 6476725 |
| Yanillian | 10 | 210 coins | oldid 6476725 |
| Krandorian | 10 | 8 coins | oldid 6476725 |
| Wildblood | 10 | 14 coins | oldid 6476725 |

Olivia’s level-27 Thieving stalls additionally yield all vegetable/flower/hops families, explicitly including nasturtium and dwellberry; rarity labels are qualitative, not weights. [Draynor Seed Market oldid 6476725]

#### Era farming-supplies stock

The four ordinary Farming shops are Vanessa (Catherby), Alice (Port Phasmatys), Sarah (Falador), and Richard (Hemenster). Nearby farmers sell unlimited compost 35 coins, plant cure 25, rake 15, seed dibber 15, gardening trowel 15, and watering can 8. The period shop page does not list spades, buckets, plant pots, baskets, or sacks in that farmer table, so those must not be invented into this exact stock from DK. [Farming shops oldid 5951351]

Papa Mambo authentically sells only red/blue/green blossom seeds among Habitat seeds, each at stock 10 and 50 coins. He does **not** sell the five vine-herb seeds in the period pin. [Papa Mambo’s Shop oldid 6393083; Herblore Habitat oldid 6513740]

#### Bird-nest tree/fruit/special seed table

The era pin proves that bird nests supply tree and fruit-tree seeds through Woodcutting and Wyson/mole exchanges. GM supplies the exact rev-667 weight table, total weight 1,024: Acorn 218; apple 174; willow 147; banana 114; orange 87; curry 69; maple 57; pineapple 42; papaya 34; yew 27; palm 22; calquat 17; spirit 11; magic 5. [Bird’s nests oldid 6550484; GM `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/birdnests/bird_nest.plugin.kts`; AS mirror `woodcutting_data.py:149-168`]

#### Master Farmer, monsters, quests, and activities

Master Farmers require 38 Thieving and yield every non-tree/non-fruit seed family shown in their period tables, including allotment, hops, bush, flower, herb, bittercap/morchella, cactus, and belladonna; tree/fruit seeds are explicitly excluded. The pin supplies quantities/rarity labels but no numeric weights. [Master Farmer oldid 6565826]

Period monster drops are a broad authentic route (the Farming pin names ogres, moss giants, aberrant spectres, and dagannoths); AS currently exposes many conventional seeds through Combat, especially black knights and level-75 ankous. Exact per-monster probabilities remain governed by their GM/DK drop citations rather than this Farming pin. [Seeds oldid 6565109; current AS route audit `tools/audit_item_reachability.py --json`; `combat_data.py`]

Quest/activity-specific routes: acorn and guam have a live Garden of Tranquillity route in AS; jade-vine seed has a live Back to My Roots route; gout tuber comes from Tai Bwo Wannai Cleanup; white-lily seed is a one-mole-skin Wyson exchange after Hard Falador Tasks; evil-turnip seed comes from seed nests/mole-skin exchange, implings, vyre cremation, or Soul Wars; papaya seed also comes from pawya trapping; watermelon seed also comes from Temple Trekking; Habitat vine-herb/bush seeds come from Jadinko hunting, while only blossom seeds are sold. [Goutweed oldid 5668713; White lily oldid 6579222; Evil turnip oldid 6538769; Seeds oldid 6565109; Herblore Habitat oldid 6513740; Jadinkos oldid 5917881]

Saplings are not separate economy drops: each acorn/tree/fruit/calquat seed is placed in a soil-filled plant pot, watered, and becomes a sapling after about 5 minutes. [Farming oldid 6565110; Tree patch oldid 6531843]

### Roster-by-route audit

Every roster input appears below at least once.

| Authentic route family | Seeds/spores/tubers in the roster | Reachable in AnkiScape today? | Evidence |
|---|---|---|---|
| Draynor stocked shop | potato, onion, cabbage, barley, jute, marigold, rosemary, hammerstone, asgarnian, yanillian, krandorian, wildblood | Yes, live shop | Draynor oldid 6476725; current AS route audit |
| Draynor zero-stock buyback plus other live Combat routes | tomato, sweetcorn, strawberry, watermelon | Yes via Combat, not natural shop stock | Draynor oldid 6476725; Seeds oldid 6565109; current AS route audit |
| Live conventional Combat/quest routes | guam, marrentill, tarromin, harralander, ranarr, toadflax, irit, avantoe, kwuarm, snapdragon, cadantine, lantadyme, dwarf weed, torstol, limpwurt, jangerberry, whiteberry, poison ivy, cactus, belladonna | Yes | Master Farmer oldid 6565826; Seeds oldid 6565109; current AS route audit |
| Live seed-nest route | acorn, willow, maple, yew, magic, apple, banana, orange, curry, pineapple, papaya, palm, calquat, spirit | Yes | Bird’s nests oldid 6550484; GM bird-nest table; current AS route audit |
| Live quest route | jade vine | Yes | Jade vine oldid 6579442; current AS route audit |
| Live Habitat shop | red blossom, blue blossom, green blossom | Yes | Papa Mambo oldid 6393083; current AS route audit |
| Thieving/stall route not yet implemented | nasturtium, woad, redberry, cadavaberry, dwellberry, bittercap mushroom spore, morchella mushroom spore | **No authentic live route** | Draynor oldid 6476725; Master Farmer oldid 6565826; current AS route audit |
| Missing quest/activity exchange | white lily, gout tuber, evil turnip | **No authentic live route** | White lily oldid 6579222; Goutweed oldid 5668713; Evil turnip oldid 6538769; current AS route audit |
| Missing authentic monster/Thieving source | spirit weed, wergali, fellstalk | **No authentic live route** | Seeds oldid 6565109; Herb patch oldid 6567051; current AS route audit |
| Missing Jadinko hunting | erzille, argway, ugune, shengo, samaden, lergberry, kalferberry | **No authentic live route** | Herblore Habitat oldid 6513740; Jadinkos oldid 5917881; current AS route audit. AS’s current Papa-Mambo routes for the five vine herbs are historically invalid. |

### Inputs with no authentic route reachable in AnkiScape today

**20 inputs:** nasturtium seed; woad seed; white-lily seed; gout tuber; spirit-weed seed; wergali seed; fellstalk seed; redberry seed; cadavaberry seed; dwellberry seed; bittercap mushroom spore; morchella mushroom spore; evil-turnip seed; erzille seed; argway seed; ugune seed; shengo seed; samaden seed; lergberry seed; kalferberry seed. [Current AS route audit `tools/audit_item_reachability.py --json`, reconciled against oldids 6476725, 6565826, 6579222, 5668713, 6538769, 6513740, and 5917881]

These crops may ship as ordinary input-starved targets. No replacement route is authorized.

## G. Anything the dossier or contract got wrong

1. **The three shifted allotment payments in GM are wrong.** The period table matches DK: sweetcorn costs 10 jute fibres, strawberry costs 1 basket of 5 apples, and watermelon costs 10 curry leaves. [Seeds oldid 6565109]
2. **Jute is a real 3-seed exception.** The GM family-wide 4-seed rule is wrong for jute. [Farming oldid 6565110; Seeds oldid 6565109]
3. **GM’s seven identical fruit-tree health-XP rows are a copy/paste defect.** The distinct DK values are exactly reproduced by the period tables. [Seeds oldid 6565109; Herblore Habitat oldid 6513740]
4. **GM’s calquat 21 h 20 min beats DK’s 10 h 40 min, but the older dedicated article says 20 h.** The nearest comprehensive period table supports GM; the discrepancy must remain in provenance. [Seeds oldid 6565109; Calquat Tree oldid 5539026]
5. **White lily is not closed by the requested pin.** Level 52 is firm, but its dedicated article says 50 planting XP while the near-cutoff Seeds table and DK say 70; GM says 42. The contract’s “ships with pinned values” assertion is premature until that conflict is resolved. [White lily oldid 6579222; Seeds oldid 6565109]
6. **Magic secateurs are not cleanly stated on the dedicated page.** That article says 15%, while Farming and the quest reward say 10%. GM/DK and two period pins support 10%, so ×1.1 is retained, but the contradiction must be cited. [oldids 6549114, 6565110, 6565661]
7. **The exact GM compost disease factors and +1/+2 lives are not wiki-confirmed.** The pins prove qualitative disease/yield improvement and 18/26 application XP, not factors 0.28/0.14 or exact extra lives. Those exact mechanics remain source_blocked. [Compost oldid 6337625; Supercompost oldid 6337626]
8. **GM’s compost-bin timer is not the era timer.** Its state machine matures either tier after 5 five-minute ticks (25 min), while period pins give regular compost 35–50 min (guide shorthand 45 min) and supercompost 90 min. [Compost oldid 6337625; Supercompost oldid 6337626; Farming oldid 6565110; GM `CompostBinState.kt:13-14`, `CompostBinHandler.kt:199-217`, `FarmTicker.kt:12-15`]
9. **Farmer protection guarantees survival, not literal immunity from entering the diseased state.** The period page says watched crops may become diseased and are cured by the gardener, potentially delaying growth. Contract §5.15 overstates “disease-proof.” [Farming oldid 6565110]
10. **Watering’s exact ×0.9 factor is not pinned, and the period pages conflict on yield.** One says no yield effect; another says yield may increase slightly. Only one-cycle disease reduction and the eligible categories are safe. [Watering can oldid 5529251; Farming oldid 6565110]
11. **Belladonna takes 5 h 20 min in the period Seeds table, not DK’s 2 h 40 min.** [Seeds oldid 6565109]
12. **Spirit-tree exact timing is not closed.** Period sources and DK disagree among roughly 58 h 40 min, 61 h 20 min, and 64 h. [Seeds oldid 6565109; Spirit tree oldid 6549224; DK `PatchType.java`]
13. **DK’s derived Habitat-bush harvest XP is wrong.** Period pin says lergberry 31.5 and kalferberry 52.5 per berry, not 54.5625 and 82.5. [Herblore Habitat oldid 6513740]
14. **Habitat’s five vine-herb seeds are not authentic Papa Mambo shop stock.** The period shop sells only the three blossom colours. Current AS shop data exposing erzille/argway/ugune/shengo/samaden at 10,000 coins is contamination and must not be treated as reachability. [Papa Mambo’s Shop oldid 6393083; Herblore Habitat oldid 6513740]
15. **Patch bomb is not a Solomon’s Store-era Farming item.** The named Patch bomb arrived on 14 Apr 2014 with Cabbage Facepunch Bonanza and is post-cutoff. [no pre-cutoff oldid; modern lead oldid 37010730]
16. **The complete physical inventory is larger than the contract’s repeatable shorthand.** The correct repeatable count is 51 crop patches plus 6 compost bins; two one-off quest patches also physically existed. [Farming/Patch locations oldid 6552430; Herblore Habitat oldid 6513740]

## Final gate disposition

- **Safe to implement from pinned values:** fruit-tree check XP; the three allotment payments; jute’s 3-seed rule; scarecrow level 23; willow 1,456.3; lantadyme 134.5; plant-cure 0 XP; application XP 18/26; bin capacity 15; regular compost 35–50 min and supercompost 90 min; cactus/bittercap/morchella/belladonna/fellstalk; jade-vine complete loop; evil-turnip complete loop; juju, aura, scroll, amulets, quest route, and the 51+6 repeatable map. [oldids cited above]
- **Still source_blocked:** white-lily planting XP; exact compost disease factors and extra lives; exact watering multiplier/yield effect; spirit-tree exact stage/time; wergali harvest XP; goutweed exact yield and planting quest gate; several Habitat stages/times/yields and kalferberry decimals. [oldids cited above]
- **Struck:** Patch bomb, post-cutoff 2014. [no pre-cutoff oldid; modern lead oldid 37010730]

## H. 2026-08-13 unresolved-crop re-audit

### Evidence method and Darkan provenance

This pass followed the current evidence order: Darkan, local OpenRS2 caches,
`game-main`, then exact pre-cutoff wiki revisions. Cache evidence was used only
for client-visible states/actions; it does not prove server XP, timing, yield,
or probability. Darkan `web/*AuditProbe.kt` files were excluded.

`git log --` was run over all three Darkan files used here:

- `src/main/java/com/rs/game/content/skills/farming/ProduceType.java`
- `src/main/java/com/rs/game/content/skills/farming/PatchType.java`
- `src/main/java/com/rs/game/content/skills/farming/FarmPatch.java`

The current paths descend through the 2022 package move (`8a953fdb5`) to the
original Farming implementation. `git blame` attributes White lily, all three
blossoms, Lergberry, Kalferberry, and the shared growth/disease routine to
original commit `c6fbe036b` (2021-06-16); Wergali is attributed to `41eb35491f`
(2022-01-06). Commit `33fdc1ec0` (2026-07-10), “Restore 2012 farming xp fidelity
in ProduceType,” is a recent wiki-derived restoration, but its diff changes
none of these rows. It therefore cannot corroborate this pass independently;
the relevant surviving candidate rows predate it. Darkan's shared disease test
is `Utils.random(128) < (6 - compostLevel)` in `FarmPatch.java:478-495`; it is a
general reconstruction, not a crop-specific period probability.

### Source-precedence rule

A dedicated crop or seed page governs that crop over an aggregate table when
it states the same field directly. This is a provenance decision, not a
preference for integers or decimals. The original July blocks were correct
safeguards: the ledger had identified real conflicts but had not yet applied
this rule consistently or inspected the dedicated stage/yield pages below.

### Crop dispositions

| Crop | Exact evidence and literal relevant text | Final mechanic | Disposition |
|---|---|---|---|
| White lily | White lily oldid `6579222`, `2012-11-18T17:41:44Z`: “Players gain 50 experience when planting, and 250 experience when harvesting.” Seeds oldid `6565109` gives 70 and GM's disabled row gives 42; the dedicated page wins. The same page and Seeds give level 52, four 20-minute stages, one lily, and allotment protection. | 50 plant XP; 250 harvest XP; 4 × 20 min; fixed yield 1. The page exposes diseased states but no probability, so the shared 6-slot registered placeholder supplies the hidden roll. | **Runnable.** The former XP conflict was a correct source block until page specificity was applied. |
| Wergali | Wergali seed oldid `6446873`, `2012-10-20T11:04:42Z`: `|time = 80 min (4x20 min)`, `|plant = 52.8`, `|check = N/A`, `|harvest = 52.8`. This dedicated row resolves Herb patch oldid `6567051`'s 51.5 aggregate conflict. | 52.8 plant XP; 52.8 XP per herb; 4 × 20 min; ordinary variable herb lives/save-slot kernel. | **Runnable.** The former harvest-XP block was a correct safeguard before the dedicated seed page was inspected. |
| Goutweed | Goutweed oldid `5668713` and Seeds oldid `6565109` prove level 29, 105 planting XP, 45 XP per goutweed, and 4 × 20 min. No period source states the exact harvest yield. Inferring seven from later economics assumes the quantity it is meant to prove. The candidate Eadgar's Ruse planting gate is also unusable today: each of the quest's six stages requires an action string with no emitter. | Yield and planting quest gate remain unrecovered. | **Blocked on `yield` and `quest_gate`.** No circular economics inference and no unsatisfiable invented gate. |
| Spirit tree | Seeds oldid `6565109` gives 11 × 320 = 3,520 minutes; Spirit tree oldid `6549224`, `2012-11-12T08:44:58Z`, says about 3,680 minutes; Darkan reconstructs 12 × 320 = 3,840 minutes. The dedicated page says the tree cannot be cut down and is removed with a Spade without yielding roots. Rev-727 and rev-742 client states expose `Check-health`/`Clear` and mature `Clear`, never `Chop`. | Lifecycle is plant → grow → check health → clear with Spade, with no harvest, stump, or roots. Exact stages/time remain unresolved. | **Blocked on `stages` and `stage_minutes`.** The generic no-output health-check/clear kernel now preserves the sourced lifecycle for when timing is recovered. |
| Red blossom | Red blossom seed oldid `5054589`, `2011-12-15T12:55:02Z`: “gives 52 experience for planting, and 255 experience for harvesting” and “approximately 20 minutes, in four five-minute stages.” | 52 plant XP; 255 harvest XP; 4 × 5 min. Period sources never state the picked count, so fixed yield 1 is registered as `farming.vine_blossom_yield`; the hidden disease roll uses `farming.shared_disease_slots`. | **Runnable with two explicit placeholders.** |
| Green blossom | Green blossom seed oldid `5562807`, `2012-05-03T21:17:28Z`: “It gives 52 experience when planted, and 255 experience when harvested” and “approximately 20 minutes, in four five-minute stages.” | Same exact timing/XP and placeholder boundaries as Red. | **Runnable with two explicit placeholders.** |
| Blue blossom | Blue blossom seed oldid `5054588`, `2011-12-15T12:53:01Z`: 52 plant XP, 255 harvest XP, and “Approximate time ... 18 to 20 minutes. (based on 2 timed observations).” It gives no stage count. | Red/Green timing is not inherited across sibling crops. | **Blocked on `stages` and `stage_minutes`.** The shared guide row may unlock from Red/Green while this data row remains non-runnable. |
| Lergberry | Lergberries oldid `6358880`, `2012-10-06T20:56:38Z`: “A full harvest yields 4 berries and earns 31.5 Farming experience for each” and the bush is renewable. Its seed page leaves time blank, Seeds records `?`, and Darkan's 6 × 20-minute row is not independently period-qualified. | Fixed yield 4 is recovered; XP/check/payment remain as previously pinned. Exact stages/time remain absent. | **Blocked on `stages` and `stage_minutes`.** Darkan's timing candidate is not promoted. |
| Kalferberry | Kalferberry seed oldid `5906898`, `2012-07-08T11:42:43Z`: `|time = 75`, `|plant = 220`, `|check = 375`, `|harvest = 52.5`; prose repeats all four. Its stage table labels the just-planted state 1 and mature state 6. Kalferberries oldid `6513798`, `2012-10-31T21:36:48Z`: “Each full harvest yields 4 berries and earns 52.5 Farming experience for each” and un-cleared bushes renew. Habitat oldid `6513740` gives aggregate 220.2/375.3/52.5; Seeds agrees with 220/375. The dedicated seed page governs planting and health XP, while all sources agree on harvest XP. | 220 plant XP; 375 check XP; 52.5 per berry; five 15-minute transitions = exact 75-minute maturity; fixed yield 4. Renewal is sourced but its interval is not: one six-minute review tick is registered as `farming.kalferberry_regrowth_minutes`. The shared disease placeholder supplies 6 slots. | **Runnable with two explicit placeholders.** Darkan's 10-minute renewal candidate is coupled to its contradicted 120-minute maturity reconstruction and is not period proof. |

### Stage-label control

AnkiScape stores a just-planted crop at kernel stage 0 and performs
`crop.stages` transitions. Period image tables often call that visible planted
state stage 1. Existing controls confirm the offset: Redberry displays stages
1–6 and uses five kernel transitions; Cadavaberry displays 1–7 and uses six.
Kalferberry's displayed stages 1–6 therefore mean five transitions, not six.
Seventy-five minutes divided across those transitions gives 15 minutes each.

### Placeholder boundaries

- `farming.shared_disease_slots = 6` represents Darkan's shared uncomposted
  `6/128` selector for White lily and runnable Habitat crops. It is not claimed
  as a crop-specific period rate, and ordinary-bush 15-slot data is not
  inherited into vine bushes.
- `farming.vine_blossom_yield = 1` preserves a complete single-output harvest
  because period Red/Green sources state XP and timing but never the count.
- `farming.kalferberry_regrowth_minutes = 6` preserves the explicitly sourced
  renewable bush. It is the smallest review-native interval and is not claimed
  as period-accurate. Darkan's 10-minute candidate was rejected for provenance
  and because its maturity reconstruction conflicts with the dedicated page.

### Runtime and reachability evidence

Real-kernel tests plant, grow, and harvest White lily, Wergali, Red blossom,
Green blossom, and Kalferberry. They prove the Habitat disease arithmetic,
Kalferberry's 75-minute boundary, health check, four-berry harvest, six-minute
renewal, and the generic Spirit-tree-style check-health → clear → replant queue.
The Kalferberry regression test was mutation-proved: changing its production
`regrowth` to `None` failed with `AssertionError: 0 != 1`, then passed after the
production value was restored.

Against the exact 1,563-action / 2,504-item / 96-orphan / 99-blocked baseline,
the post-change graph reports 1,568 actions / 2,506 reachable items / 98 orphan
inputs / 101 blocked actions. The five added Farming actions are White lily,
Wergali, Red blossom, Green blossom, and Kalferberry. The newly reachable items
are exactly `Red blossom` and `Green blossom`, each via its corresponding live
Papa Mambo seed → Farming route. Wergali seed is already reachable from the
Molanisk combat route, so `Grimy wergali` was already reachable through that
existing crop action; White lily seed and Kalferberry seed have no live
acquisition route, so their newly exposed actions add two root orphans and two
blocked actions rather than reachable outputs.

### Acquisition follow-up — 2026-08-13

Kalferberry seed is now live through the existing cannibal-jadinko Hunter route.
Cannibal jadinko oldid `5976665` says a successful catch gives Plant teeth and a
chance at vine-bush seeds; Herblore Habitat oldid `6513740` identifies Jadinko
hunting as the Kalferberry-seed route. Darkan
`data/npcs/drops/hunter/hunter_jadinko_cannibal.json` and
`data/npcs/drops/hunter/jadinko_sub/hh_bush_seed.json`, both introduced by commit
`087e34d11b59b1d81a6c8aadbf6150a7689c6f4c`, model a `12/256` parent roll and a
one-of-two quantity-one table containing Lergberry seed and Kalferberry seed.
Therefore Kalferberry seed's implemented `3/128`, quantity `1` result is derived
from those table constants, not quoted from the period pages.

The live route is Papa Mambo's Marasamaw plant stock → Hunter 75 cannibal
jadinko → Kalferberry seed → Farming 77 habitat vine-bush patch → four
Kalferberries. The reachability graph moves from 1,568 actions / 2,506 reachable
items / 98 orphan inputs / 101 blocked actions to 1,568 / 2,509 / 97 / 100.
The three newly reachable items are Lergberry seed, Kalferberry seed, and
Kalferberry. White lily seed remains a root orphan: oldid `6219558` sources the
Wyson one-Mole-skin exchange after Falador hard tasks, but Giant Mole, Mole skin,
Wyson exchange, and a claimable Falador shield 3 route are absent.
