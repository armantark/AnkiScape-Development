# Pre-EOC Farming source dossier for AnkiScape

Source cutoff: **2012-11-20**

Source shorthand used below:

- **GM** — `/Users/ArmanTarkhanian1/Downloads/game-main`, a revision-667/October 4, 2011 emulator snapshot.
- **DK** — commit `7e7d67b` from `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`, read through `git show` without changing its checkout.
- **AS** — `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`.

The Darkan checkout’s current `HEAD` was `9ce5fc2b9095612c0a16795db23ba12dc86e076d`, not the requested pin. All Darkan findings in this dossier therefore come from objects read directly at commit `7e7d67b`; no checkout or Git state was changed.

## 1. game-main completeness verdict

### Verdict

GM’s Farming plugin is a **substantial, playable end-to-end implementation**, not a stub. It contains roughly 4,947 lines of Farming code and 54 active seed/crop definitions. A player can rake a patch, compost it, plant seeds or saplings, water eligible crops, wait through persistent growth cycles, encounter disease and death, cure diseased plants, pay nearby farmers for protection, check tree or bush health, harvest produce, clear patches, fill compost bins, use magic secateurs, and have tool leprechauns note produce.

Its limitation is **content breadth**, not absence of the core loop. It models the conventional 2011 farming network—four allotment/flower/herb complexes, hops, bushes, fruit trees, ordinary trees, and calquat—but omits several special or later patches and crops needed for broad November 2012 parity.

### Implemented end to end

- Persistent patch state, including crop, growth stage, compost state, watering, disease, death, harvest lives, and offline growth replay:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/core/FarmPatch.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/core/FarmTicker.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/core/FarmingWorld.kt`
- Five-minute global Farming ticks and crop-specific growth frequencies:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/core/FarmTicker.kt:12-15`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/SeedType.kt:5-101`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/Constants.kt:23-24`
- Raking, planting, watering, disease, death, plant cure, clearing, health checks, and harvesting:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/RakingHandler.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/PlantingHandler.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/WateringHandler.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/GrowingHandler.kt:14-65`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt:21-120`
- Compost and supercompost, including compost bins:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/CompostState.kt:8-18`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/CompostBin.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/CompostBinHandler.kt`
- Farmer protection payments and flower-based allotment protection:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:25-1601`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/GrowingHandler.kt:14-65`
- Variable allotment, herb, and hops yields; fixed/regenerating bush, fruit-tree, and calquat yields:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt:21-120`
- Magic-secateurs yield bonus:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt:106-120`
- Sapling creation, ordinary-tree chopping, root recovery, and fruit/bush regrowth:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/SaplingHandler.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/TreeChoppingHandler.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt`
- Tool-leprechaun produce noting:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/ToolLeprechaun.kt`
- Thirty-four crop-patch instances plus four compost bins:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Patch.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/CompostBin.kt`

The 34 crop patches comprise 8 allotment, 4 flower, 4 herb, 4 hops, 4 bush, 4 fruit-tree, 5 ordinary-tree, and 1 calquat patch. With the four compost bins, GM defines 38 patch/bin objects. These counts come from the complete declarations in `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Patch.kt` and `CompostBin.kt`.

### Partial, stubbed, or missing

- White lily exists only as a commented-out definition because its patch varbits were unresolved:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:596-601`
- No active definitions were found for:
  - cactus;
  - bittercap or morchella mushrooms;
  - belladonna;
  - spirit tree;
  - jade vine;
  - evil turnip;
  - Herblore Habitat vine herbs, blossoms, lergberry, or kalferberry;
  - Trollheim, Harmony, Lletya, Wilderness, Herblore Habitat, or other special-patch expansion content.
- GM’s active herb table stops at torstol and does not include wergali, fellstalk, or goutweed:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:25-429`
- GM contains only conventional compost and supercompost; it has no juju-farming-potion mechanics:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/CompostState.kt:8-18`
- Some numeric rows are plainly suspect:
  - Every fruit tree is assigned `1,199.5` check-health XP despite different level requirements; DK supplies distinct values:
    - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:1158-1346`
    - `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:77-83`
  - GM and DK disagree on several allotment protection payments and on calquat growth frequency. These conflicts require pinned wiki confirmation.

## 2. Crop tables

### Shared GM mechanics needed to read the tables

- One Farming tick is five minutes:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/core/FarmTicker.kt:12-15`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/Constants.kt:23-24`
- Seed quantities per planting are:
  - allotment: 3;
  - flower: 1;
  - herb: 1;
  - hops: 4;
  - bush: 1;
  - tree/fruit tree/calquat: 1 sapling.
  - Source: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/SeedType.kt:5-101`
- Unless a row says otherwise:
  - allotment, herb, and hops start with 3 harvest lives;
  - compost adds 1 life;
  - supercompost adds 2 lives;
  - each harvested item consumes one life unless the yield roll saves it.
  - Sources:
    - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/CompostState.kt:8-18`
    - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt:106-120`
- GM’s chance to preserve a harvest life is:

```text
ceil(
  min(minSlots + current Farming level - crop requirement, maxSlots)
  × (1.1 while magic secateurs are equipped, otherwise 1.0)
) / 256
```

  Sources:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt:106-120`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/util/World.kt:603-609`
- Compost tiers:
  - none: disease factor `1.00`, 0 compost XP, +0 harvest lives;
  - compost: disease factor `0.28`, 18 XP, +1 harvest life;
  - supercompost: disease factor `0.14`, 26 XP, +2 harvest lives.
  - Source: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/CompostState.kt:8-18`
- GM’s per-stage disease roll is:

```text
floor(
  diseaseSlots
  × compost disease factor
  × (0.9 if the crop is watered, otherwise 1.0)
) / 128
```

  Paid-for crops, flower-protected allotments, immune crops, and crops in their first stage are exempt. A crop already diseased when its next growth cycle occurs dies. Source: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/GrowingHandler.kt:14-65`.
- Watering applies to allotments, flowers, and hops. A watering can has 8 charges. Watering lasts for the current growth stage and multiplies GM’s disease roll by `0.9`; it does not accelerate growth:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/WateringHandler.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/GrowingHandler.kt:14-65`

### Allotments

All allotments use 3 seeds. They use variable yields with 3 base harvest lives, minimum save slot 130, maximum save slot 200, and disease slot 30. Each growth stage is 10 minutes. Sources for every row and those shared values: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:606-794`.

| Crop | Seed → produce | Level | Plant XP | Per-harvest XP | Stages | Total time | Farmer protection in GM |
|---|---|---:|---:|---:|---:|---:|---|
| Potato | Potato seed → potato | 1 | 8.0 | 9.0 | 4 | 40 min | 2 buckets of compost |
| Onion | Onion seed → onion | 5 | 9.5 | 10.5 | 4 | 40 min | 1 sack of potatoes containing 10 potatoes |
| Cabbage | Cabbage seed → cabbage | 7 | 10.0 | 11.5 | 4 | 40 min | 1 sack of onions containing 10 onions |
| Tomato | Tomato seed → tomato | 12 | 12.5 | 14.0 | 4 | 40 min | 2 sacks of cabbages, 10 cabbages each |
| Sweetcorn | Sweetcorn seed → sweetcorn | 20 | 17.0 | 19.0 | 6 | 60 min | 1 basket of 5 apples |
| Strawberry | Strawberry seed → strawberry | 31 | 26.0 | 29.0 | 6 | 60 min | 10 curry leaves |
| Watermelon | Watermelon seed → watermelon | 47 | 48.5 | 54.5 | 8 | 80 min | 5 jangerberries |

DK conflicts with GM on the final three payments:

- sweetcorn: 10 jute fibres;
- strawberry: 1 basket of 5 apples;
- watermelon: 10 curry leaves.

Source: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:37-43`. These values are more internally plausible than GM’s shifted-looking sequence but remain wiki-pin candidates rather than adopted corrections.

Flower protection of adjacent allotments in GM:

| Flower | Protected allotment crops |
|---|---|
| Marigold | Potato, onion, and tomato |
| Rosemary | Cabbage |
| Nasturtium | Watermelon |
| Scarecrow | Sweetcorn |

Source: GM flower/allotment protection declarations in `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:434-794`.

### Flowers

Flowers use 1 seed, 4 growth stages, and 20 minutes total growth time. Sources for all active rows: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:434-595`.

| Crop | Seed → produce | Level | Plant XP | Check-health XP | Per-harvest XP | Yield | Disease slots | Protection payment |
|---|---|---:|---:|---:|---:|---|---:|---|
| Marigold | Marigold seed → marigolds | 2 | 8.5 | — | 47.0 | 1 flower | 30 | None |
| Rosemary | Rosemary seed → rosemary | 11 | 12.0 | — | 66.5 | 1 flower | 25 | None |
| Nasturtium | Nasturtium seed → nasturtiums | 24 | 19.5 | — | 111.0 | 1 flower | 20 | None |
| Woad | Woad seed → woad leaf | 25 | 20.5 | — | 115.5 | 3 leaves | 15 | None |
| Limpwurt | Limpwurt seed → limpwurt root | 26 | 21.5 | — | 120.0 | At least 3 roots; special extra-yield rolls | 10 | None |
| Scarecrow | Scarecrow item → scarecrow | 1 in GM | 0 | — | 0 | Persistent scarecrow | Immune | None |

GM’s limpwurt path starts with 3 roots and performs crop-specific extra-yield rolls rather than the ordinary allotment/herb life formula: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt:45-58`.

DK requires level 23 to place a scarecrow, while GM requires level 1:

- `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:50`
- `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:569-595`

White lily is not active in GM. Its commented definition says level 58, 42 planting XP, and 250 harvest XP, but explicitly notes unresolved/invalid varbits: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:596-601`. DK instead gives level 52, 70 planting XP, and 250 harvest XP: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:51`. The level and planting XP require a wiki pin.

### Herbs

All GM herbs use 1 seed, 4 growth stages, 20 minutes per stage, and 80 minutes total. They have 3 base harvest lives, disease slot 27, maximum save slot 80, and the per-row minimum save slot shown below. Sources for every GM row and shared value: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:25-429`.

| Herb | Seed → grimy herb | Level | Plant XP | Per-harvest XP | Minimum save slot | Total time |
|---|---|---:|---:|---:|---:|---:|
| Guam | Guam seed → grimy guam | 9 | 11.0 | 12.5 | 24 | 80 min |
| Marrentill | Marrentill seed → grimy marrentill | 14 | 13.5 | 15.0 | 28 | 80 min |
| Tarromin | Tarromin seed → grimy tarromin | 19 | 16.0 | 18.0 | 31 | 80 min |
| Harralander | Harralander seed → grimy harralander | 26 | 21.5 | 24.0 | 36 | 80 min |
| Ranarr | Ranarr seed → grimy ranarr | 32 | 27.0 | 30.5 | 39 | 80 min |
| Spirit weed | Spirit weed seed → grimy spirit weed | 36 | 32.0 | 36.0 | 43 | 80 min |
| Toadflax | Toadflax seed → grimy toadflax | 38 | 34.0 | 38.5 | 43 | 80 min |
| Irit | Irit seed → grimy irit | 44 | 43.0 | 48.5 | 46 | 80 min |
| Avantoe | Avantoe seed → grimy avantoe | 50 | 54.5 | 61.5 | 50 | 80 min |
| Kwuarm | Kwuarm seed → grimy kwuarm | 56 | 69.0 | 78.0 | 54 | 80 min |
| Snapdragon | Snapdragon seed → grimy snapdragon | 62 | 87.5 | 98.5 | 57 | 80 min |
| Cadantine | Cadantine seed → grimy cadantine | 67 | 106.5 | 120.0 | 60 | 80 min |
| Lantadyme | Lantadyme seed → grimy lantadyme | 73 | 135.5 | 151.5 | 64 | 80 min |
| Dwarf weed | Dwarf weed seed → grimy dwarf weed | 79 | 170.5 | 192.0 | 67 | 80 min |
| Torstol | Torstol seed → grimy torstol | 85 | 199.5 | 224.5 | 71 | 80 min |

DK assigns lantadyme 134.5 planting XP rather than GM’s 135.5: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:68`. This requires wiki confirmation.

Additional DK herb-like rows absent from GM:

| Crop | Seed → produce | Level | Plant XP | Per-harvest XP | Stages | Growth frequency | Total time | DK save slots |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Wergali | Wergali seed → grimy wergali | 46 | 52.8 | 52.8 | 4 | 20 min | 80 min | 48–80 |
| Fellstalk | Fellstalk seed → grimy fellstalk | 91 | 225.0 | 315.6 | 4 | 20 min | 80 min | 15–90 |
| Goutweed/tuber crop | Gout tuber → goutweed | 29 | 105.0 | 45.0 | 4 | 20 min | 80 min | 57–80 |

Sources:

- Numeric rows: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`
- Goutweed’s Eadgar’s Ruse requirement: `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:217-225`

### Hops

All GM hops use 4 seeds and variable yields with 3 base harvest lives, minimum save slot 100, and maximum save slot 180. Each stage is 10 minutes. Sources for every row and shared value: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:799-987`.

| Crop | Seed → produce | Level | Plant XP | Per-harvest XP | Stages | Total time | Disease slots | Farmer protection |
|---|---|---:|---:|---:|---:|---:|---|
| Barley | Barley seed → barley | 3 | 8.5 | 9.5 | 4 | 40 min | 15 | 3 buckets of compost |
| Hammerstone hops | Hammerstone seed → hammerstone hops | 4 | 9.0 | 10.0 | 4 | 40 min | 14 | 1 marigold |
| Asgarnian hops | Asgarnian seed → asgarnian hops | 8 | 10.9 | 12.0 | 5 | 50 min | 13 | 1 sack of 10 onions |
| Jute | Jute seed → jute fibre | 13 | 13.0 | 14.5 | 5 | 50 min | 12 | 6 barley malt |
| Yanillian hops | Yanillian seed → yanillian hops | 16 | 14.5 | 16.0 | 6 | 60 min | 11 | 1 basket of 5 tomatoes |
| Krandorian hops | Krandorian seed → krandorian hops | 21 | 17.5 | 19.5 | 7 | 70 min | 10 | 3 sacks of 10 cabbages |
| Wildblood hops | Wildblood seed → wildblood hops | 28 | 23.0 | 26.0 | 8 | 80 min | 9 | 1 nasturtium |

DK uses 3 seeds for jute while GM’s family rule uses 4: `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:243-253`. This needs wiki confirmation.

### Bushes

Bushes use 1 seed, 20-minute stages, and 4 fixed/regenerating harvest lives. Disease slot is 15 except for immune poison ivy. Sources for every GM row and shared values: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:992-1153`.

| Bush | Seed → berry | Level | Plant XP | Check-health XP | Per-harvest XP | Stages | Total time | Farmer protection |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Redberry | Redberry seed → redberries | 10 | 11.5 | 64.0 | 4.5 | 5 | 100 min | 4 sacks of 10 cabbages |
| Cadavaberry | Cadavaberry seed → cadava berries | 22 | 18.0 | 102.5 | 7.0 | 6 | 120 min | 3 baskets of 5 tomatoes |
| Dwellberry | Dwellberry seed → dwellberries | 36 | 31.5 | 177.5 | 12.0 | 7 | 140 min | 3 baskets of 5 strawberries |
| Jangerberry | Jangerberry seed → jangerberries | 48 | 50.5 | 284.5 | 19.0 | 8 | 160 min | 6 watermelons |
| Whiteberry | Whiteberry seed → white berries | 59 | 78.0 | 437.5 | 29.0 | 8 | 160 min | 8 bittercap mushrooms |
| Poison ivy | Poison ivy seed → poison ivy berries | 70 | 120.0 | 675.0 | 45.0 | 8 | 160 min | None; disease-immune |

After depletion, GM bush produce regenerates rather than requiring replanting: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt`.

### Ordinary trees

Trees use 1 sapling. Every stage lasts 40 minutes. Trees award planting XP and a one-time check-health XP reward; chopping Woodcutting output is separate, and the Farming harvest XP is 0. Roots are recovered when the stump is cleared. Sources for all rows: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:1351-1481` and GM tree chopping/clearing handlers.

| Tree | Seed/sapling | Level | Plant XP | Check-health XP | Stages | Total time | Disease slots | Farmer protection |
|---|---|---:|---:|---:|---:|---:|---|
| Oak | Acorn → oak sapling | 15 | 14.0 | 467.3 | 5 | 200 min | 17 | 1 basket of 5 tomatoes |
| Willow | Willow seed → willow sapling | 30 | 25.0 | 1,456.5 in GM | 6 | 240 min | 15 | 1 basket of 5 apples |
| Maple | Maple seed → maple sapling | 45 | 45.0 | 3,403.4 | 8 | 320 min | 13 | 1 basket of 5 oranges |
| Yew | Yew seed → yew sapling | 60 | 81.0 | 7,069.9 | 10 | 400 min | 11 | 10 cactus spines |
| Magic | Magic seed → magic sapling | 75 | 145.5 | 13,768.3 | 12 | 480 min | 9 | 25 coconuts |

DK gives willow check-health XP as 1,456.3 rather than GM’s 1,456.5: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:85-89`.

### Fruit trees

Fruit trees use 1 sapling, 6 growth stages, 160 minutes per stage, 16 hours total, disease slot 18, and 6 fixed/regenerating fruits. Sources for all GM rows and shared values: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:1158-1346`.

GM assigns every fruit tree 1,199.5 check-health XP. Because that repeated value is an obvious copy/paste defect, the table includes DK’s distinct candidate values instead of presenting GM’s repetitions as authoritative.

| Fruit tree | Seed/sapling → fruit | Level | Plant XP | GM check XP | DK check XP candidate | Per-fruit XP | Total time | Farmer protection |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Apple | Apple tree seed → cooking apple | 27 | 22.0 | 1,199.5 | 1,199.5 | 8.5 | 16 h | 9 sweetcorn |
| Banana | Banana tree seed → banana | 33 | 28.0 | 1,199.5 | 1,750.5 | 10.5 | 16 h | 4 baskets of 5 apples |
| Orange | Orange tree seed → orange | 39 | 35.5 | 1,199.5 | 2,470.2 | 13.0 | 16 h | 3 baskets of 5 strawberries |
| Curry | Curry tree seed → curry leaf | 42 | 40.0 | 1,199.5 | 2,906.9 | 15.0 | 16 h | 5 baskets of 5 bananas |
| Pineapple | Pineapple seed → pineapple | 51 | 57.0 | 1,199.5 | 4,605.7 | 21.5 | 16 h | 10 watermelons |
| Papaya | Papaya tree seed → papaya fruit | 57 | 72.0 | 1,199.5 | 6,146.4 | 27.0 | 16 h | 10 pineapples |
| Palm | Palm tree seed → coconut | 68 | 110.5 | 1,199.5 | 10,150.1 | 41.5 | 16 h | 15 papaya fruits |

DK candidate check-health values: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:77-83`.

### Calquat

| Crop | Seed → produce | Level | Seeds | Plant XP | Check-health XP | Per-fruit XP | Stages | GM total time | Yield | Disease slots | Farmer protection |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| Calquat | Calquat seed → calquat fruit | 72 | 1 | 129.5 | 12,096.0 | 48.5 | 8 | 21 h 20 min | 6 fixed/regenerating fruits | 18 | 8 poison ivy berries |

GM source: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:1486-1512`. GM gives calquat a 32-tick growth frequency, meaning 160 minutes per stage and 1,280 minutes total: `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/SeedType.kt:96-101`.

DK uses a 16-tick frequency, giving 80 minutes per stage and 10 hours 40 minutes total: `DK/src/main/java/com/rs/game/content/skills/farming/PatchType.java`. This conflict needs a wiki pin.

### Special patches present in DK but absent from GM

DK’s ordinary special-patch rows use the crop definitions in `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`, frequencies in `PatchType.java`, initial lives in `FarmPatch.java`, and harvest handling in `HarvestPatch.java`.

| Crop | Patch type | Seed → produce | Level | Plant XP | Check-health XP | Per-harvest XP | Stages | DK total time | Seeds | Yield/protection |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Cactus | Cactus | Cactus seed → cactus spine | 55 | 66.5 | 374.0 | 24.9375 from `66.5 × 0.375` | 7 | 9 h 20 min | 1 | 3 regenerating spines; 6 cadava berries |
| Bittercap mushroom | Mushroom | Mushroom spore → bittercap mushroom | 53 | 61.5 | — | 57.7 | 6 | 4 h | 1 | 6 fixed mushrooms; no payment |
| Morchella mushroom | Mushroom | Morchella spore → morchella mushroom | 74 | 160.0 | — | 77.7 | 6 | 4 h | 1 | 9 fixed mushrooms; no payment |
| Belladonna | Belladonna | Belladonna seed → cave nightshade | 63 | 91.0 | — | 512.0 | 4 | 2 h 40 min | 1 | 1 harvest; no payment |
| Evil turnip | Evil turnip | Evil turnip seed → evil turnip | 42 | 41.0 | — | 46.0 | 1 | 5 min | 1 | 1 harvest; disease-immune |
| Spirit tree | Spirit tree | Spirit seed → mature spirit tree | 83 | 199.5 | 19,301.8 | — | 12 | 64 h | 1 | No crop harvest |
| Jade vine | Jade vine | Jade vine seed → prunable jade vine | 53 | 50.0 | 1,500.0 | 30.0 per branch | 6 | 16 h | 1 | Intended 6 branches; 10 wildblood hops |
| White lily | Flower | White lily seed → white lily | 52 | 70.0 | — | 250.0 | 4 | 20 min | 1 | 1 flower |

Darkan’s cactus harvest XP is derived by its generic special-crop formula from planting XP, not stored as an independent historical number: `DK/src/main/java/com/rs/game/content/skills/farming/HarvestPatch.java`.

The jade-vine path appears broken at the pinned commit: its harvest path requires remaining lives, but `FarmPatch.setInitialLives` does not initialize `JADE_VINE`, leaving it at zero. Sources:

- `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java`
- `DK/src/main/java/com/rs/game/content/skills/farming/HarvestPatch.java`

Jade vine is gated by Back to My Roots in DK: `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java`. Its intended 6 branches and 10-wildblood-hops protection are therefore implementation intent, not proof that the pinned code completes the harvest loop successfully.

### Herblore Habitat crops in DK

All values below come from `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`, with stage frequency from `PatchType.java`.

#### Vine herbs

Each vine herb uses 1 seed, 4 stages, 20 minutes per stage, and 80 minutes total.

| Crop | Level | Plant XP | Per-harvest XP |
|---|---:|---:|---:|
| Erzille | 58 | 87.0 | 87.0 |
| Argway | 65 | 110.0 | 125.0 |
| Ugune | 70 | 135.0 | 152.0 |
| Shengo | 76 | 140.5 | 160.0 |
| Samaden | 80 | 170.0 | 190.0 |

#### Blossoms

Each blossom uses 1 seed, requires level 54, grants 52 planting XP and 255 harvest XP, has 4 stages, takes 20 minutes total, and yields 1 blossom.

| Crop |
|---|
| Red blossom |
| Blue blossom |
| Green blossom |

Source: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`.

#### Herblore Habitat bushes

Both use 1 seed, 6 stages, 20 minutes per stage, 2 hours total, and 4 regenerating berries.

| Crop | Level | Plant XP | Check-health XP | DK per-berry XP | Farmer protection |
|---|---:|---:|---:|---:|---|
| Lergberry | 61 | 145.5 | 236.3 | 54.5625 from `145.5 × 0.375` | 3 red blossoms |
| Kalferberry | 77 | 220.0 | 375.0 | 82.5 from `220 × 0.375` | 3 lergberries |

Sources:

- Definitions: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`
- Generic special-harvest XP calculation: `DK/src/main/java/com/rs/game/content/skills/farming/HarvestPatch.java`

## 3. Cross-cutting mechanics inventory

| Mechanic | Historical/design significance | GM | DK at `7e7d67b` |
|---|---|---|---|
| Compost | Reduces disease and raises variable yield; applying it grants XP | Implemented: factor 0.28, 18 XP, +1 life | Present, but application code appears defective |
| Supercompost | Stronger disease reduction and yield bonus | Implemented: factor 0.14, 26 XP, +2 lives | Present, but application code appears to collapse ordinary compost into supercompost |
| Compost bins | Convert suitable produce into compost and support bucket extraction | 4 bins implemented | Present |
| Juju farming potion | Chance for extra herbs; relevant only with Herblore Habitat | Missing | Implemented as an independent `1/3` extra-herb roll |
| Plant cure | Cures diseased crops | Implemented | Implemented, but awards a suspicious 90 Farming XP |
| Secateurs | Tool for pruning diseased bushes/trees in the historical game | Ordinary tool exists in item data; exact GM interaction breadth needs contract verification | Present |
| Magic secateurs | Historical 10% produce boost after Fairytale I | Implemented as a `1.1` multiplier to yield-save slots while equipped | Implemented as a `1.1` multiplier |
| Watering can | Waters allotments, flowers, and hops; 8 charges | Implemented; 10% relative disease-roll reduction for one stage | Implemented |
| Seed dibber | Required to plant seeds | Implemented | Required even for saplings, which is likely an implementation oddity |
| Rake | Clears weeds and is needed to prepare patches | Implemented | Implemented |
| Spade | Harvesting, clearing dead crops, and related patch work | Implemented | Implemented |
| Gardening trowel | Potted-tree/sapling workflow | Implemented | Present |
| Plant pot and watering | Seed-to-sapling preparation | Implemented | Seed plus pot becomes a sapling immediately in `TreeSaplings.java`, simplifying the historical intermediate growth |
| Farmer protection | Payment makes a crop disease-proof | Implemented from per-seed payment data | Implemented |
| Flower protection | Certain flowers protect adjacent allotments | Implemented | Implemented |
| Scarecrow protection | Protects sweetcorn | Implemented; level 1 placement | Implemented; level 23 placement |
| Tool leprechaun storage | Stores Farming tools and can note eligible produce | Produce noting implemented; storage breadth should be checked separately | Full storage table and interactions in `ToolLeprechaun.kt` and `StorableItem.kt` |
| Farming amulet | Monitors the state of an assigned patch | No complete mechanic found | No complete mechanic found in the inspected Farming implementation |
| Amulet of nature | Monitors a bound Farming patch and reports disease/growth state | No complete mechanic found | No complete mechanic found in the inspected Farming implementation |
| Greenfingers aura | Later-era yield bonus | Missing | Implemented as 3%, 5%, 7%, or 10% independent extra-produce chances |
| Patch bomb | Instant/accelerated harvesting reward mechanic | Missing | Implemented by up to 50 harvest iterations |
| Scroll of life | Chance to return seeds | Missing | Implemented: 10% for non-tree/non-flower crops and 5% for trees/fruit trees |
| Fairytale I gate | Magic-secateurs acquisition and Farming progression context | Magic-secateurs effect exists; quest acquisition was not proved by Farming code | Quest handler is commented out; completion rewards list 3,500 Farming, 2,000 Attack, and 1,000 Magic XP plus item 7410 |
| Eadgar’s Ruse gate | Goutweed farming access | Goutweed absent | Explicitly checked |
| Back to My Roots gate | Jade-vine access | Jade vine absent | Explicitly checked |
| Disease | Stage-based risk, affected by compost, water, and protection | Diseased crop dies on its next due growth cycle | Diseased crop has a 50% death roll on a subsequent growth cycle |
| Offline growth | Patches continue advancing while the player is away | Implemented by replaying elapsed ticks | Persistent patch data exists; parity of offline replay was not proved |
| Crop regrowth | Bushes, fruit trees, cactus, and calquat regain produce | Bushes, fruit trees, and calquat implemented | Bushes, fruit trees, cactus, calquat, and Habitat bushes represented |
| Produce noting | Reduces inventory friction at a patch | Tool leprechaun implemented | Tool leprechaun implemented |

### Darkan compost defect

In DK’s compost-application path, the held item is changed to a bucket before the code tests which compost item was used. Consequently, the ordinary-compost and supercompost branches appear to collapse into compost level 2, while both award 18 XP. Source: `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:268-285`.

The values in this path should not be used as historical authority. GM’s explicit three-tier data structure is more reliable for conventional compost mechanics.

### Darkan disease model

DK’s disease chance is based on:

```text
(6 - compostLevel) / 128
```

with water and protection affecting eligibility, and a diseased crop has a 50% chance to die on a later growth cycle. Source: `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:455-479`.

This differs materially from GM’s per-crop disease-slot model and certain death on the next due growth cycle. Neither codebase alone settles exact live-game disease odds.

### Darkan juju and aura yield modifiers

- Juju farming potion: `Utils.random(3) == 0`, giving a 1-in-3 independent chance for an extra herb.
- Greenfingers aura tiers: 3%, 5%, 7%, and 10% independent chances for extra produce.

Source: `DK/src/main/java/com/rs/game/content/skills/farming/HarvestPatch.java:95-127`.

### Patch-location coverage

- GM: 34 crop patches plus 4 compost bins:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Patch.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/CompostBin.kt`
- DK: 57 declared Farming locations, comprising 51 crop patches and 6 compost locations:
  - `DK/src/main/java/com/rs/game/content/skills/farming/PatchLocation.java:24-97`

The contract must decide whether “pre-EOC parity” means every geographically available patch, a representative patch per category, or location-independent actions.

## 4. Darkan deltas

### Darkan has content GM lacks

- White lily.
- Wergali and fellstalk.
- Goutweed/gout-tuber farming with an Eadgar’s Ruse gate.
- Cactus.
- Bittercap and morchella mushrooms.
- Belladonna.
- Evil turnip.
- Spirit tree.
- Jade vine with a Back to My Roots gate.
- Herblore Habitat vine herbs:
  - erzille;
  - argway;
  - ugune;
  - shengo;
  - samaden.
- Herblore Habitat blossoms:
  - red;
  - blue;
  - green.
- Herblore Habitat bushes:
  - lergberry;
  - kalferberry.
- Juju farming-potion extra-herb rolls.
- Greenfingers aura yield bonuses.
- Patch-bomb harvesting.
- Scroll-of-life seed returns.
- A larger location table: 51 crop patches and 6 compost locations rather than GM’s 34 and 4.
- Broader explicit tool-leprechaun storage.

Primary files:

- `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`
- `DK/src/main/java/com/rs/game/content/skills/farming/PatchType.java`
- `DK/src/main/java/com/rs/game/content/skills/farming/PatchLocation.java:24-97`
- `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java`
- `DK/src/main/java/com/rs/game/content/skills/farming/HarvestPatch.java`
- `DK/src/main/java/com/rs/game/content/skills/farming/ToolLeprechaun.kt:38-174`
- `DK/src/main/java/com/rs/game/content/skills/farming/StorableItem.kt:22-118`

### GM has stronger or clearer behavior than Darkan

- A cleaner explicit compost model with distinct none/compost/supercompost data.
- Per-crop disease slots and explicit water/compost factors.
- A transparent variable-yield formula with minimum and maximum save slots.
- Explicit per-crop harvest lives and compost additions.
- A coherent persistent growth ticker with five-minute cycles and offline replay.
- A working conventional crop loop without relying on the special-content branches that contain obvious DK defects.
- Explicitly modeled flower-based adjacent allotment protection.
- More trustworthy handling of basic compost application than DK’s item-mutation branch.

### Obvious Darkan oddities and defects

1. **Checkout mismatch:** The working checkout is at `9ce5fc2b9095612c0a16795db23ba12dc86e076d`; this dossier read commit `7e7d67b` directly and did not switch it.

2. **Compost-level bug:** DK mutates the held compost item to a bucket before determining its type, apparently causing ordinary and supercompost to set the same level. Both award 18 XP:
   - `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:268-285`

3. **Plant-cure XP:** Curing a plant awards 90 Farming XP, which is suspicious and needs wiki verification:
   - `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:286-301`

4. **Seed dibber for saplings:** DK’s generic planting path requires a seed dibber even when planting a sapling:
   - `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:235-260`

5. **Instant sapling conversion:** A seed and plant pot become a sapling immediately rather than retaining a watered-pot growth interval:
   - `DK/src/main/java/com/rs/game/content/skills/farming/TreeSaplings.java:21-50`

6. **Jade-vine harvest appears broken:** Jade vine lacks an initial-lives case, but pruning requires positive lives:
   - `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java`
   - `DK/src/main/java/com/rs/game/content/skills/farming/HarvestPatch.java`

7. **Derived special-crop XP:** DK computes several bush/fruit/cactus/calquat harvest rewards as `plantingExperience × 0.375`, rather than storing independently sourced harvest XP:
   - `DK/src/main/java/com/rs/game/content/skills/farming/HarvestPatch.java`

8. **Fruit-tree data exposes GM copy/paste:** GM gives every fruit tree 1,199.5 health XP; DK provides differentiated values:
   - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:1158-1346`
   - `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:77-83`

9. **Allotment payments conflict:** GM’s sweetcorn/strawberry/watermelon sequence differs from DK’s and looks shifted:
   - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:714-794`
   - `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:37-43`

10. **Calquat timing conflict:** GM gives 21 hours 20 minutes; DK gives 10 hours 40 minutes:
    - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/SeedType.kt:96-101`
    - `DK/src/main/java/com/rs/game/content/skills/farming/PatchType.java`

11. **Jute seed-count conflict:** GM’s hops-family rule requires 4 seeds; DK special-cases jute to 3:
    - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/SeedType.kt`
    - `DK/src/main/java/com/rs/game/content/skills/farming/FarmPatch.java:243-253`

12. **White-lily conflict:** GM’s disabled row says level 58 and 42 planting XP; DK says level 52 and 70 planting XP:
    - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:596-601`
    - `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:51`

13. **Scarecrow conflict:** GM requires level 1; DK requires level 23:
    - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:569-595`
    - `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:50`

14. **Scroll-of-life inference:** DK implements 10% seed return for non-tree/non-flower crops and 5% for trees and fruit trees. Its own comment links wiki oldid `6151122` and acknowledges balancing inference for fruit-tree behavior:
    - `DK/src/main/java/com/rs/game/content/dungeoneering/rewards/DungeonRewards.java:247-297`

15. **Fairytale I is not operational proof:** DK contains a commented quest handler. Its reward constants—3,500 Farming XP, 2,000 Attack XP, 1,000 Magic XP, and item 7410—show intent, not a working quest/acquisition path:
    - DK Fairytale I quest handler, lines 8-43 at commit `7e7d67b`

## 5. Wiki pins needed

The command requested for wiki retrieval was run from AS for:

- `Farming`
- `Farming/Patches`
- `Compost`
- `Supercompost`

Each call failed during network name resolution with `socket.gaierror`, before the helper could resolve a pre-cutoff revision. Therefore, **no new wiki page was successfully consulted and no oldid can honestly be reported for those attempted pages**.

The implementation should pin the following pages before settling disputed or unproved numbers.

### Highest-value table pins

1. **Farming**
   - Proves the high-level loop, tool requirements, disease/watering behavior, magic-secateurs effect, experience rules, growth-cycle semantics, and crop-category overview.
   - Must resolve a revision at or before 2012-11-20.

2. **Farming/Patches**
   - Proves the complete November 2012 patch inventory and locations.
   - Needed to distinguish core patches from quest-, area-, or activity-specific patches and settle the expected patch count.

3. **Compost**
   - Proves compost inputs, bin capacity, processing time, application XP, disease effect, and yield effect.

4. **Supercompost**
   - Proves eligible ingredients, application XP, disease reduction, and extra-yield behavior.

5. **Seeds**
   - Proves seeds per planting, seed names, and category membership, especially GM/DK’s jute conflict and sapling handling.

### Crop-table pins

6. **Allotment patch**
   - Complete level, planting XP, harvest XP, stages, growth time, seed count, protection, and flower-protection table.
   - Must settle sweetcorn, strawberry, and watermelon payments.

7. **Flower patch**
   - Levels, XP, growth times, disease behavior, allotment-protection pairings, scarecrow requirement, and white-lily values.

8. **Herb patch**
   - Levels, XP, stage count, growth time, and yield mechanics for standard herbs, wergali, fellstalk, and any quest crop treated as a herb.

9. **Hops patch**
   - Levels, XP, seed counts, growth times, protection payments, and especially jute’s required seed count.

10. **Bush patch**
    - Levels, planting/check/harvest XP, growth time, regrowth interval, protection, and poison-ivy immunity.

11. **Tree patch**
    - Levels, planting/check XP, growth times, protection payments, roots, and exact sapling workflow.
    - Must settle willow’s 1,456.3 versus 1,456.5 check-health XP.

12. **Fruit tree patch**
    - The authoritative distinct check-health XP table, growth times, yields, and protection payments.
    - This is necessary because GM’s repeated 1,199.5 is defective.

13. **Calquat tree**
    - Must settle the 10-hour-40-minute versus 21-hour-20-minute conflict, yield, regrowth, XP, and payment.

14. **Cactus**
    - Level, stages, total time, spine count, regrowth, XP, and protection payment.

15. **Mushroom patch**
    - Bittercap and morchella level, XP, stages, growth time, fixed yield, disease, and protection behavior.

16. **Belladonna**
    - Level, XP, stages, growth time, single-yield behavior, quest/access requirements, and cave-nightshade output.

17. **Spirit tree**
    - Level, stages, exact growth time, health XP, number and locations of patches, gardener payments, quest gates, and whether the Farming action produces any item.

18. **Jade vine**
    - Level, XP split, stages, growth time, branch count, pruning/regrowth, payment, and Back to My Roots requirements.

19. **Evil turnip**
    - Era validity, level, XP, growth time, patch location, yield, and disease immunity.

20. **Goutweed**
    - Whether gout tuber farming belongs in the normal crop table, Eadgar’s Ruse gating, level, XP, growth time, and yield.

21. **White lily**
    - Must settle GM’s disabled level-58/42-XP row against DK’s level-52/70-XP row.

### Cross-cutting pins

22. **Magic secateurs**
    - Exact yield bonus, eligible crop categories, equipment requirement, and Fairytale I acquisition.

23. **Fairytale I – Growing Pains**
    - Quest gate and reward verification, especially magic-secateurs availability.

24. **Plant cure**
    - Price/acquisition, eligible patch states, and whether curing grants any Farming XP; needed because DK’s 90 XP is suspect.

25. **Watering can**
    - Charge count, refill behavior, eligible crop types, exact disease effect, and whether repeated watering matters.

26. **Farmer**
    - Payment rules, noted-item acceptance if any, payment timing, and protection duration.

27. **Tool leprechaun**
    - Storage quantities, produce noting, exclusions, and whether remote storage access existed by the cutoff.

28. **Amulet of farming**
    - Patch binding, charges, monitored patch categories, and messages.

29. **Amulet of nature**
    - Binding and monitoring behavior, disease alerts, teleport or rub behavior if applicable, and relationship to Farming.

30. **Scroll of life**
    - Exact seed-return percentages and crop-category exceptions.
    - DK embeds oldid `6151122`, but this should be revalidated as a historical source rather than accepted from a code comment.

31. **Greenfingers aura**
    - Era validity by 2012-11-20, tier percentages, qualifying crops, and stacking.

32. **Juju farming potion**
    - Duration, 1-in-3 extra-herb effect, eligible patch types, whether the bonus XP follows the extra herb, and stacking with secateurs/aura.

33. **Farming Patch Bomb**
    - Era validity, eligible patch types, harvest behavior, and reward source.

### Herblore Habitat pins

34. **Herblore Habitat**
    - Existing AS provenance records oldid `6513740`, dated 2012-10-31:
      - `memory-bank/source-audits/gap-grills-1-9-provenance-2026-07-10.md:42-50`
    - This pin should prove the activity’s patch types and broad crop/Jadinko relationships, but crop-level tables may still need dedicated pins.

35. **Vine flower patch**
    - Red, blue, and green blossom requirements, XP, growth, and yields.

36. **Vine herb patch**
    - Erzille, argway, ugune, shengo, and samaden requirements, XP, growth, yield, and disease.

37. **Vine bush patch**
    - Lergberry and kalferberry requirements, XP, growth, yield, regrowth, and protection.

38. **Jadinko**
    - Proves that corrupt, shadow, marble, plant-teeth, aquatic, oily, draconic, Saradomin, Guthix, and Zamorak vines come from Jadinko hunting rather than ordinary Farming.

## 6. Economy cross-reference

The current reachability audit was inspected through:

```text
python3 tools/audit_item_reachability.py --json
```

The recorded baseline comprises 1,061 transformations, 1,679 reachable items, 690 recipe inputs, 267 orphan inputs, 136 root orphans, 131 cascade orphans, and 303 blocked transformations. Source: AS reachability audit output and the corresponding current audit records under `AS/memory-bank/source-audits/`.

“Made obtainable” below means that Farming would provide the named crop itself, assuming seeds/saplings and any required activity gates receive valid acquisition paths. It does not mean every downstream recipe automatically becomes reachable.

### Herblore herbs currently unobtainable that conventional Farming can supply

| Farming output | Downstream significance | Current status |
|---|---|---|
| Grimy snapdragon | Standard Herblore input | Orphan input; Farming would provide it |
| Grimy spirit weed | Standard Herblore input | Orphan input; Farming would provide it |
| Grimy toadflax | Standard Herblore input | Orphan input; Farming would provide it |
| Grimy torstol | High-level Herblore input | Orphan input; Farming would provide it |
| Grimy wergali | Summoning-related potion line | Orphan input; DK special herb content would provide it |
| Grimy fellstalk | High-level potion input | Orphan input; DK late herb content would provide it |

Source modules and audit surfaces:

- `AS/ankiscape/data/skills/herblore_data.py`, or the repository’s corresponding Herblore data module containing herb and secondary input declarations.
- `AS/tools/audit_item_reachability.py`
- Current AS reachability audit output.

Guam, marrentill, tarromin, harralander, ranarr, irit, avantoe, kwuarm, cadantine, lantadyme, and dwarf weed already have reachable acquisition paths in the current economy audit, so Farming would add thematic parity and alternative supply rather than close root orphans.

### Herblore Habitat herbs currently unobtainable

| Farming output | Current status |
|---|---|
| Grimy erzille | Orphan input |
| Grimy argway | Orphan input |
| Grimy ugune | Orphan input |
| Grimy shengo | Orphan input |
| Grimy samaden | Orphan input |

Sources:

- DK crop definitions: `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`
- AS Herblore inputs: current Herblore data module.
- AS reachability result: `AS/tools/audit_item_reachability.py --json`

Farming alone would not complete the full juju-potion economy. The Herblore Habitat vine secondaries—corrupt vine, shadow vine, marble vine, plant teeth, aquatic vine, oily vine, draconic vine, Saradomin vine, Guthix vine, and Zamorak vine—are Jadinko rewards rather than farmed crops. For example, the juju farming potion needs an ugune potion (unf) plus marble vine; Farming can supply ugune, but marble vine still needs the Hunter/Jadinko side. Source: current AS Herblore data and `memory-bank/source-audits/gap-grills-1-9-provenance-2026-07-10.md:42-50`.

Dungeoneering herbs remain a separate closed economy and should not be treated as supplied by overworld Farming merely because both are “herbs.” Source: AS Herblore data’s separate Dungeoneering herb and potion declarations.

### Farming secondaries that close Herblore gaps

| Farming output | Herblore use | Reachability effect |
|---|---|---|
| Jangerberries | Zamorak brew secondary | Currently orphaned; jangerberry bushes would supply it |
| Papaya fruit | Recover special secondary | Currently orphaned; papaya trees would supply it |
| Morchella mushroom | Prayer renewal secondary | Currently orphaned; DK mushroom patches would supply it |

Sources:

- Crop provenance:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:1073-1099`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:1293-1319`
  - `DK/src/main/java/com/rs/game/content/skills/farming/ProduceType.java:27-121`
- Recipe and orphan status:
  - AS Herblore data module.
  - `AS/tools/audit_item_reachability.py --json`

A cactus crop produces **cactus spines**, not **potato cactus**. Therefore, shipping ordinary cactus Farming would not by itself close the potato-cactus Herblore orphan. Source: DK cactus crop definition in `ProduceType.java` and AS Herblore secondary inputs.

Limpwurt roots and white berries already have reachable acquisition routes in the current audit. Farming would add canonical renewable sources but would not close their current root reachability.

### Cooking inputs

The Farming ship would directly close current orphan inputs for:

| Farming output | Cooking significance |
|---|---|
| Sweetcorn | Cooked sweetcorn and downstream combination recipes |
| Strawberry | Strawberry-based food and basket contents |
| Watermelon | Slices and downstream food inputs |

Sources:

- Crop definitions:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/data/Seed.kt:714-794`
- AS Cooking recipes and acquisition notes:
  - `data/cooking_data.py:257-272`
  - `data/cooking_data.py:379-404`
- Current reachability audit:
  - `AS/tools/audit_item_reachability.py --json`

The Cooking module notes that temporary gathering bridges for several farm products were retired because shops already supplied them: `data/cooking_data.py:399-404`. Consequently, crops such as potatoes, onions, cabbages, tomatoes, apples, bananas, oranges, pineapples, and other ordinary farm foods may add a canonical source without changing current root reachability.

### Crafting and other skill inputs

| Farming output | Downstream use | Reachability effect |
|---|---|---|
| Jute fibre | Empty-sack crafting | Currently orphaned; jute farming would supply it |
| Oak roots | Crossbow string/root processing family | Currently orphaned root input |
| Willow roots | Crossbow string/root processing family | Currently orphaned root input |
| Maple roots | Crossbow string/root processing family | Currently orphaned root input |
| Yew roots | Crossbow string/root processing family | Currently orphaned root input |
| Magic roots | Crossbow string and magic-string-related processing | Currently orphaned root input |
| Willow branches | Basket crafting | Potential Farming supply, but the exact branch acquisition loop needs a wiki pin |

Sources:

- `data/crafting_data.py:216-222`
- `data/crafting_data.py:326-327`
- `AS/tools/audit_item_reachability.py --json`
- GM tree/root behavior:
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/TreeChoppingHandler.kt`
  - `GM/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/farming/handlers/HarvestingHandler.kt`

Spirit roots are distinct from ordinary tree roots. A spirit-tree implementation should not be assumed to provide the ordinary root items unless a pinned source says so.

### Economy caveat: seed acquisition

A Farming action table does not make an output sustainably obtainable unless its seeds, spores, tubers, or saplings also enter the economy. Neither GM nor DK crop definitions prove that AnkiScape currently has an acquisition source for every seed. The implementation needs a separate seed-source audit covering monster drops, shops, thieving, nests, activities, quests, and seed returns.

## 7. Open design questions

1. **How does real-time growth map to successful reviews?**  
   Source data establishes five-minute ticks and crop-specific stage counts, but it does not decide whether AnkiScape should use wall-clock time, reviews, XP thresholds, session boundaries, scheduled checkpoints, or a hybrid.

2. **What is one Farming action?**  
   Planting, watering, curing, checking health, harvesting one item, harvesting an entire patch, clearing a patch, filling a compost bin, and paying a farmer are distinct source actions. The product contract must decide which consume reviews and which are state transitions or utility actions.

3. **Should crops grow passively between reviews?**  
   GM supports offline time progression, but a review-based game could instead advance only on successful reviews. The data does not settle the desired player experience.

4. **How should long growth times be compressed?**  
   A 40-minute potato and a 64-hour spirit tree cannot map literally to the same review cadence without deciding whether elapsed time, difficulty, and expected card volume all matter.

5. **How should variable harvest yields map to reviews?**  
   Possible interpretations include one review per harvested item, one review to harvest the whole patch, a probabilistic item bundle, or a limited harvest window. The emulator formulas do not choose among these product models.

6. **What should compost alter in AnkiScape?**  
   Historical mechanics affect disease and yield, but the design must decide whether compost changes review count, success chance, output quantity, growth steps, failure forgiveness, or some combination.

7. **How should disease work when an Anki answer fails?**  
   The sources model random per-stage disease, not review correctness. The contract must decide whether failure causes disease, only raises its chance, delays growth, consumes protection, or remains unrelated.

8. **Can plants die while the user is absent?**  
   GM’s diseased crops can die on later passive ticks. That may create punitive offline loss in AnkiScape unless explicitly adapted.

9. **How should watering be represented?**  
   Watering historically applies only to allotments, flowers, and hops and modestly reduces disease. The design must decide whether it is a required review action, optional consumable preparation, automatic utility, or omitted friction.

10. **Should farmer protection be paid from the live economy?**  
    Historical payment quantities can create valuable crop sinks, but they can also form circular dependencies—for example, one crop protecting another before its own supply exists.

11. **How should flower protection work without spatial patch adjacency?**  
    The historical mechanic depends on a flower patch beside two allotments. AnkiScape must decide whether to model locations/plots explicitly or represent flowers as a global or loadout-style modifier.

12. **How many simultaneous patches can a player own or operate?**  
    The sources prove physical locations, not the appropriate number of concurrent AnkiScape jobs.

13. **Does parity require every physical patch location?**  
    GM has 34 crop patches; DK has 51. A review game may need crop categories rather than a world-map simulation, but that is a product choice.

14. **Which 2012 special patches are launch scope?**  
    The data proves candidates—calquat, cactus, mushroom, belladonna, spirit tree, jade vine, evil turnip, goutweed, and Herblore Habitat crops—but not whether they belong in the first Farming ship.

15. **Is evil turnip desirable even if era-valid?**  
    Its one-stage, five-minute loop is mechanically unlike conventional Farming and may belong to a quest/activity family rather than the core skill.

16. **How should quest gates work?**  
    Magic secateurs, goutweed, jade vine, and some patch access depend on quests. The contract must decide whether to require achievements, explicit quest flags, substitute skill thresholds, or omit gated actions until quests exist.

17. **Should magic secateurs be equipment, a permanent unlock, or an achievement modifier?**  
    The source proves an equipped 10% yield effect but not the best AnkiScape representation.

18. **Should juju farming potion and Greenfingers aura stack?**  
    DK models independent rolls, but exact live-game stacking needs wiki proof and the product must decide whether these systems fit AnkiScape’s consumable/modifier model.

19. **How are tools handled?**  
    The design must choose between persistent inventory requirements, a tool-leprechaun loadout, permanent unlocks, automatic use, or simplified action prerequisites.

20. **How are watering-can charges and compost buckets replenished?**  
    Historical refill and bucket loops may create excessive review friction if translated literally.

21. **Does checking tree health consume a review and award its full XP at once?**  
    Tree XP is heavily concentrated in one check-health action. That can produce large XP spikes unless deliberately preserved or normalized.

22. **How should tree chopping interact with Woodcutting?**  
    A grown Farming tree naturally becomes a Woodcutting target. The contract must define ownership of logs, roots, stump clearing, regrowth, and cross-skill XP.

23. **How are fruit and bush regrowth cycles represented?**  
    The sources model regenerating harvest lives. The design must decide whether regrowth is time-based, review-based, automatic, or reset per study session.

24. **Are seed returns necessary for economy sustainability?**  
    Scroll of life and ordinary seed drops may affect whether high-tier seeds are renewable. A seed-source and seed-sink model is needed before locking costs.

25. **Should every crop output enter the global economy?**  
    Some outputs are protection payments, quest items, activity ingredients, or cross-skill materials. The product must decide whether Farming is primarily an XP action family, an economy source, or both.

26. **How should inaccessible downstream chains be surfaced?**  
    Farming can supply ugune but not marble vine; it can supply cactus spines but not potato cactus. The UI and contract must avoid implying that planting one crop unlocks an entire downstream recipe family.

27. **Which source wins unresolved numeric conflicts?**  
    GM is primary, but its fruit-tree XP table is demonstrably defective. The contract needs an explicit rule: use GM unless internally inconsistent, then DK, then a pinned pre-cutoff wiki revision.

28. **How should exact historical randomness be adapted?**  
    GM’s yield and disease formulas use slot rolls over 256 and 128 respectively. The design must decide whether to preserve those probabilities, convert them into deterministic expected values, or expose them as visible modifiers.

29. **Should protection eliminate random disease or protect against review failure?**  
    Historical farmers prevent disease. In a review game, translating that into immunity from failed answers could undermine learning incentives, so the semantic mapping must be chosen deliberately.

30. **What is the Farming achievement contract?**  
    Neither emulator decides AnkiScape milestones, unlock pacing, mastery targets, or whether completing crop families, visiting patch categories, producing quantities, and closing economy gaps should award achievements.

31. **How should patch state survive deck/profile changes?**  
    The source proves persistent player patch state, but the product must decide whether state is global, per Anki profile, per deck, or per skill loadout.

32. **What happens after the user changes system time or misses many days?**  
    A wall-clock implementation needs explicit catch-up, maximum-advance, and anti-exploit rules. A review-only implementation avoids that issue but departs from historical passive growth.

33. **Should the initial release reproduce bugs or intended behavior?**  
    GM’s fruit-tree XP repetition and DK’s compost and jade-vine defects are implementation errors, not parity targets. The contract should distinguish evidence of intended content from code that must be corrected.

34. **What is the minimum wiki-verification gate before implementation?**  
    The unresolved fruit-tree XP, allotment payments, calquat timing, white-lily values, scarecrow level, jute seed count, willow XP, plant-cure XP, and special-patch data should not silently become production constants without pinned pre-cutoff evidence.

