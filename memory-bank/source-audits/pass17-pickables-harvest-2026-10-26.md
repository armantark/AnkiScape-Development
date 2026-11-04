# Pass 17: hand-picked world objects in November 2012, and AnkiScape status

Read-only source harvest, 2026-10-26, Opus 5.5 fact-finder. P = period wiki page
https://runescape.wiki/w/<Title>?oldid=<id>, every revision before 2012-11-20.
Pk = Darkan emulator evidence, "darkan-world-server/src/main/java/com/rs/game/content/world/Pickables.kt".
Scratch fetches: /tmp/pass17-facts/E/.

## Pickable objects (17 found; Farming patches and ground spawns excluded)

| Object -> item | Main locations (F2P first) | Members | Level / XP / gates | Yield and regrowth |
|---|---|---|---|---|
| Banana tree -> Banana | Musa Point, Karamja; Ape Atoll (P Banana 6436240: "Many banana trees are located in the plantation on [[Musa Point]]") | Item members = No | None stated; emulator no XP (Pk:39-43) | "There are 33 banana trees in the plantation, each with 5 bananas on each tree" (P Musa_Point 6487976). Regrowth: emulator only, 5 picks then one back every 15 s (Pk:29-51) |
| Redberry bush -> Redberries | Two bushes south-east of Varrock (P Redberries 6563826) | No | None stated | "Two berries may be picked from each bush. They take 2 minutes to regrow" (P Redberries 6563826); "take 95 seconds" (P Redberry_bush 6021052) - pages disagree |
| Cadava bush -> Cadava berries | "south of [[Varrock]], just west of the [[East Varrock Mine]]" (P Cadava_berries 6357137) | No | "does not give any [[farming]] experience" | Yield: emulator only, 2 picks, 15 s regrowth step (Pk:35-51) |
| Cabbage | North of Lumbridge, south of Falador, Draynor Manor; members Taverley etc. (P Cabbage 6174079) | No | None stated | Abbey of St. Elspeth: "cabbages always respawn immediately when picked" |
| Draynor Manor cabbage | Draynor Manor (P Cabbage_(Draynor_Manor) 6397732) | No | None stated; Black Knights' Fortress | Heals 20, Defence boost; emulator object 11494 -> item 1967 (Pk:19) |
| Potato | Two fields north of Lumbridge; Hemenster (members) (P Raw_potato 6510109) | No | "no skill experience given from picking potatoes" | Emulator removed 1 min (Pk:74) |
| Onion | Fred the Farmer's yard, north of Rimmington, south of Draynor bank; members Rellekka (P Onion 6454587) | No | None stated | Emulator removed 1 min (Pk:74) |
| Wheat (formerly "Grain") | East of Draynor, north of Cooks' Guild, south-east of Champions' Guild; members Yanille etc. (P Wheat 5908312, "'Pick Wheat'") | No | None stated | Emulator removed 1 min (Pk:74) |
| Flax | South of Seers' Village, Tree Gnome Stronghold, Lletya (P Flax_(scenery) 6101341) | Yes: "All of the flax fields are [[Members]] only" | None for picking | "a flax spot disappears when all the flax in that spot is picked. They reappear later after approximately 5 seconds" |
| Pineapple plant -> Pineapple | Brimhaven Dungeon entrance, Ape Atoll Agility Course (P Pineapple 6454592) | Yes | None stated | Emulator 1 in 5 empty for 1 min (Pk:72) |
| Nettles | Edgeville yews, Draynor jail, Lumbridge Swamp, north-east of Canifis (P Nettles 6579371) | Yes | "Players must wear gloves in order to pick nettles"; without gloves "up to 60 [[Life Points]] of damage" | Emulator removed 20 s (Pk:73) |
| Sq'irk tree -> sq'irks | Sorceress's Garden, Al Kharid (P Sorceress's_Garden 6466752) | Yes | Thieving 1/25/45/65; Farming XP 30/40/50/60 | "You can only pick one fruit per trip" |
| Sorceress's Garden herbs | Same | Yes | Summer "50 farming experience" | "you will always get two grimy herbs before you are teleported out" |
| Mort Myre logs/bushes/twigs -> fungus, pear, stem | Mort Myre Swamp (P Bloom 6178399) | Yes | Nature Spirit; Bloom with blessed sickle or Ivandis flail, "about 30 or 40 prayer points" | Morytania legs 1+: 2 fungi per log (P Mort_myre_fungus 6178396) |
| Doogle bush -> Doogle leaves | South of Gertrude's house, Feldip Hills, east of Rellekka (P Doogle_leaves 6287188) | Yes | None stated | Not stated |
| Fever grass, Lavender, Tansymum | "grows west of [[Oo'glog]]" (P Fever_grass 6106077, Lavender 6333491, Tansymum 6106155) | Yes | As a First Resort | Not stated |
| Quest-only: Trollweiss (P 5826344), Glowing fungus (P 6569840) | Trollweiss Mountain; Haunted Mine | Yes | Troll Romance; Haunted Mine | Not stated |

Left out as ground spawns: grapes, dwellberries, white berries, jangerberries, tomato, garlic. Farming only: strawberry, watermelon, sweetcorn, papaya, orange, bittercap. Shops only: lime, lemon (P Lime 6362301); Ogleroot from Farmer Blinkin (P Ogleroot 6564850).

## AnkiScape status (main 2e885047f)

| Item | In data? | How obtained now | Uses |
|---|---|---|---|
| Banana | data/combat/items.py:55 | Farming data/farming_data.py:321; Monkey food stall data/thieving_data.py:160; Bones to Bananas data/magic_data.py:393; drop | Ape Atoll teleport data/magic_data.py:114; Tai Bwo Wannai Trio |
| Redberries | data/cooking_data.py:451 | Farming only data/farming_data.py:266 | Redberry pie data/cooking_data.py:381; Aggie's red dye activity_updates.py:291 |
| Cadava berries | data/combat/items.py:137 | Farming data/farming_data.py:267; imp drop | Cactus Farming payment data/farming_data.py:332 |
| Cabbage | data/cooking_data.py:455 (ID 1965) | Farming :202; Vegetable stall data/thieving_data.py:157; drops | Garden pie data/cooking_data.py:391; Black Knights' Fortress |
| Draynor Manor cabbage | No (ID 1967 absent) | - | - |
| Potato | data/cooking_data.py:444 | Farming :200; Vegetable stall | Fish pie, Admiral pie, stew data/cooking_data.py:392-396 |
| Onion | data/cooking_data.py:447 | Farming :201; Vegetable stall | Chopped onion, Garden pie; yellow dye activity_updates.py:301 |
| Grain | data/cooking_data.py:423 | "Gather grain" data/cooking_data.py:327; drops | Flour data/cooking_data.py:335 |
| Flax | yes | "Gather flax" activity_updates.py:104; Miscellania | Bow string, Unfinished net |
| Pineapple | data/cooking_data.py:516 | Farming :324; rare Slayer drop | Pineapple chunks data/cooking_data.py:418 |
| Nettles | data/cooking_data.py:539 | "Pick nettles" activity_updates.py:123 | Nettle tea; Skippy and the Mogres |
| Sq'irk, garden herbs | data/sorceress_garden_data.py | Sorceress's Garden activity | Sq'irk juice |
| Mort myre fungus | yes | Slayer drop only; no Bloom | Super energy data/herblore_data.py:222 |
| Mort myre pear, stem | No | - | - |
| Doogle leaves | yes | "Gather Doogle leaves" activity_updates.py:181 | Gertrude's Cat |
| Fever grass, Lavender, Tansymum, Trollweiss, Glowing fungus | No | - | - |

No shop in data/shop_data.py sells any of these items.

## Claims without a period source
- Regrowth for bananas, cadava, cabbage, onion, potato, wheat, pineapple, nettles (Darkan only).
- Cadava yield per bush (Darkan only: 2).
- Ape Atoll banana trees as pickable trees.
- "Pick" as the menu option on Doogle bushes and Oo'glog plants.
- No XP / no level for bananas, cabbage, onion, wheat, pineapple (Darkan only; period no-XP only for potatoes and cadava).
- Farming XP for Winter, Spring and Autumn garden herbs.
- Redberry regrowth: 2 minutes vs 95 seconds.

## Papercuts (surfaced, not in Pass 17 scope)
- activity_updates.py:107 gather_flax and :97 gather_wool cite OSRS pages (not period sources).
- pick_nettles (activity_updates.py:128) and WHEAT_PICK_SOURCE_PATH (data/cooking_data.py:104-107) point to /Users/ArmanTarkhanian1/...
- AnkiScape item "Grain"; period name "Wheat": "'''Wheat''' (previously ''Grain'')" (P Wheat 5908312).
- data/quest/stage_cleanups.py:245 uses "Raw potato"; item is "Potato" elsewhere; data/quest/item_names.py:67 maps only "Potatoes".
- Spinning flax needs level 10 (data/crafting_data.py:220); period Flax page says "level 1 [[Crafting]]".
- Banana Tree, Pineapple Plant and Potato/Wheat (scenery) pages have no revision before 2013-11-20; only item pages serve.

## Source fixes findings (Pass 17 ticket 11, 2026-10-27)
Wikitext read through the MediaWiki API at the 2012-11-20 cutoff; caches read with `tools/query_openrs2_cache.sh`.

### Grain or Wheat: the item was "Wheat"; renamed, with a save migration
- Item page, P Wheat 5908312 (2012-07-08T12:34:17Z; title "Grain" redirects here): infobox `|name = Wheat`, `|AKA=Grain`, `|examine=Some wheat heads.`; body "'''Wheat''' (previously ''Grain'') is obtained by selecting 'Pick Wheat' in wheat fields".
- Cache item 1947 is named "Wheat" in rev-727 (2012-07-24) and rev-742 (2012-11-07). Item 5607 is "Grain" in rev-742, a wearable, non-exchangeable item (the Recruitment Drive grain), not the cooking item.
- Field: Darkan Pickables.kt at commit 1912a55cb245cc4410e51b200f9ad4c5e480510f, line 21: `"Wheat" -> pick(player, obj, 1947)`. "Wheat (scenery)" has no revision before 2013-11-20.
- Market row, P Exchange:Wheat 6571952 (2012-11-18T06:22:44Z): `|Item=Wheat`, `|ItemId=1947`, `|Price=18`, `|Limit=1000`; the buy-limit table P Calculator:Grand_Exchange_buying_limits 6457777 lists `[[Exchange:Wheat|Wheat]]` at 1000. Added to `data/grand_exchange_period_source.json` because the cache marks 1947 exchangeable, so Wheat now enters the Grand Exchange.
- Result: item 1947 is stored as "Wheat". Old saves migrate "Grain" to "Wheat" through `LEGACY_COOKING_ITEM_MIGRATIONS` (data/cooking_data.py). The rename also gives the "Wheat" that Eadgar's Ruse, Missing My Mummy and Let Them Eat Pie require, and removes the cape-slot equipment entry the name "Grain" had matched to item 5607.

### Flax spinning level: all three pages agree on Crafting 1; changed from 10
- P Flax 6564477 (2012-11-17T00:56:14Z): "'''Flax''' is a plant that [[Pay-to-play|members]] with level 1 [[Crafting]] can use on a [[spinning wheel]] to create a [[bow string]], granting 15 Crafting [[experience]]."
- P Bow_string 6547251 (2012-11-10T22:57:54Z): "It is created by using [[flax]] with a [[spinning wheel]], which requires level 1 [[Crafting]] and grants a player 15 Crafting [[experience]]."
- P Spinning_wheel 6566263 (2012-11-17T15:37:46Z), table row: `|[[Flax]]` / `|[[Bow string]]` / `|1` (Level Required).
- Darkan SpinningWheel.java at commit 1912a55cb245cc4410e51b200f9ad4c5e480510f, line 32: `FLAX(new int[] { 1779 }, 1777, 1, 15.0)`.

### Gather wool and Gather flax citations
- P Wool 5942277 (2012-07-15T21:25:02Z): "Wool is gathered from [[sheep]] by using [[shears]] on them when they have a full coat."
- P Flax 6564477: "It is possible to pick multiple flax from one plant."; Darkan Pickables.kt line 18: `"Flax" -> pick(player, obj, 1779)`.

### Quest "Raw potato"
- The Fremennik Trials stage 3 cleanup matches the catalog's own spelling, because cleanups run before `QUEST_STAGE_ITEM_NAME_OVERRIDES` (data/quest/catalog.py `_quest_with_stage_requirements`). Changing the cleanup to "Potato" would leave the stage requiring a potato. The override map now resolves "Raw potato" to "Potato", which fixes Let Them Eat Pie stage 2.
- The rev-742 cache names item 1942 "Raw potato"; AnkiScape stores it as "Potato".
