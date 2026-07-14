# Agility source tables — 2026-07-13

This is a read-only source harvest for the future AnkiScape Agility implementation. It preserves the required hierarchy exactly: 2011Scape values ship wherever that source implements the course; pinned pre-EOC RuneScape Wiki values fill only courses absent from 2011Scape; Darkan values never ship and appear only as divergences or leads; caches prove client object identity, never XP or server mechanics. `source_blocked` is deliberate wherever the approved sources do not prove a value.

## Citation key and interpretation rules

- `S-GNOME` = `~/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/agility/gnome_agility.plugin.kts`
- `S-BARB` = `~/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/agility/barbarian_agility.plugin.kts`
- `S-WILD` = `~/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/agility/wilderness_agility.plugin.kts`
- `S-SHORT` = `~/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/agility/agility_shortcuts.plugin.kts`
- `S-OBJS` = `~/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Objs.kt`
- `D-*` = the named file under `~/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/`.
- `W-* oldid=N` = literal wikitext from the pinned RuneScape Wiki revision `https://runescape.wiki/?oldid=N` resolved by `tools/wiki_parity.py` before `2012-11-20`.
- `C742 object N` and `C741 object N` = object definition returned from the named OpenRS2 disk cache by `tools/query_openrs2_cache_definitions.sh`. The two primary caches produced identical names/options for every ID cited below.
- A stage number is a course-local ordered checkpoint. For trusted courses it is the exact 2011Scape counter. For wiki gap-fill courses it is the traversal position stated by the pinned page. `finish (requires N; reset 0)` means the final handler does not advance to `N+1`; it checks the prior stage and pays the bonus.
- All XP values are unmodified base XP. Every positive course `addXp` call in the three trusted course files passes `checkBrawlingGloves = true`; brawling gloves are therefore an external XP modifier and must not be baked into these values or applied twice. `[S-GNOME:65,80,95,112,127,146,159,184,242,275,278,281,338,341; S-BARB:85,100,114,139,172,194,196,199,217,235,247,257,268,286,289; S-WILD:131,154,244,257,273]`
- No XP/hour figure is adopted as an implementation constant. Period wiki rate examples variously include penance horns, brawling gloves, Sköll boots, pendants, Karamja gloves, uninterrupted play, or no failures; they are not base per-obstacle data.

Pinned wiki revisions: Gnome Stronghold `6391497` (`2012-10-12T18:29:49Z`); Barbarian Outpost `6549278` (`2012-11-12T10:22:50Z`); Wilderness `6487716` (`2012-10-28T02:29:46Z`); Burthorpe `6130636` (`2012-08-23T14:17:25Z`); Agility Pyramid `6457748` (`2012-10-23T02:32:50Z`); Ape Atoll `6538325` (`2012-11-06T00:27:47Z`); Werewolf `6288778` (`2012-09-24T05:54:46Z`); Dorgesh-Kaan `6547042` (`2012-11-10T19:12:05Z`); Penguin `5988056` (`2012-07-25T13:51:02Z`); Brimhaven `6556177` (`2012-11-15T03:00:35Z`); Agility Arena ticket `5777910` (`2012-06-19T01:59:09Z`); Pirate Jackie `6225118` (`2012-09-09T21:46:21Z`).

## Coverage

| Course/activity | 2011Scape? | Pinned wiki oldid | Darkan? | Cache corroborated? | Tier of shipped value |
|---|---:|---:|---:|---:|---|
| Gnome Stronghold + Advanced fork | Yes — trusted trunk/branches `[S-GNOME:35-53,55-345]` | `6391497` (requirements/failure/conflict only) | Yes; divergent normal/advanced values | Not required for shipping | Tier 1: 2011Scape |
| Barbarian Outpost + Advanced fork | Yes — trusted trunk/branches `[S-BARB:46-64,65-291]` | `6549278` (course requirement/failure only) | Yes; major normal-course divergence | Not required for shipping | Tier 1: 2011Scape; wiki fills the absent level-35 course gate only |
| Wilderness | Yes — trusted ordered course `[S-WILD:30-38,81-279]` | `6487716` (failure/conflict only) | Yes; values agree, object revision differs | Not required for shipping | Tier 1: 2011Scape |
| Burthorpe / Gnome beginner | No | `6130636` | Yes; final XP differs | Yes — all seven rows in C742/C741 | Tier 2: pinned wiki |
| Agility Pyramid | No | `6457748` | Yes; ordered lead and multiple divergences | Partial — all named interactive types except “moving blocks” | Tier 2 for type XP/counts; ordered occurrence table is `source_blocked` |
| Ape Atoll | No | `6538325` | Yes; XP table is wholly divergent | Yes — all six rows in C742/C741 | Tier 2: pinned wiki |
| Werewolf (Canifis) | No | `6288778` | Yes; stick/failure divergences | Yes — all five rows in C742/C741 | Tier 2: pinned wiki |
| Dorgesh-Kaan | No | `6547042` | No | Yes — all eight route rows in C742/C741 | Tier 2: pinned wiki |
| Penguin | No | `5988056` | No | Partial — interactive object groups identified; course-label mapping noted | Tier 2: pinned wiki |
| Brimhaven Agility Arena | No lap implementation | `6556177`; ticket `5777910`; Pirate Jackie `6225118` | Partial controller; no payout | Yes — dispensers 3581/3608 in C742/C741 | Tier 2: pinned wiki; Darkan only divergence |

## 1. Gnome Stronghold: shared trunk with two branches

Course requirement: none for the normal route `[W-GNOME oldid=6391497]`. Advanced fork requirement: current Agility `> 84`, i.e. level 85 `[S-GNOME:150-166]`. Normal completion bonus: `39.0 XP` `[S-GNOME:6]`. Advanced completion bonus: `605.0 XP` `[S-GNOME:7]`.

The two counters advance only when `stage + 1 == newStage` `[S-GNOME:35-52]`. The first three obstacles write/advance both counters; the level-85 tree advances the advanced counter and resets the normal counter `[S-GNOME:55-98,150-162]`. The branches are therefore not independent courses.

### Shared trunk

| Traversal | Obstacle / interaction | Object ID | Level | Base XP | Stage effect | Darkan divergence (never ships) |
|---:|---|---:|---:|---:|---|---|
| 1 | Log balance / Walk-across | `2295` `[S-OBJS:1287]` | none `[S-GNOME:55-68]` | `7.5` `[S-GNOME:65]` | normal `1`, advanced `1` `[S-GNOME:66-67]` | agrees on `7.5` `[D-GnomeAgility.java:146-148]` |
| 2 | Obstacle net / Climb-over | `2285` `[S-OBJS:1282]` | none `[S-GNOME:71-83]` | `7.5` `[S-GNOME:80]` | normal `2`, advanced `2` `[S-GNOME:81-82]` | agrees on `7.5` `[D-GnomeAgility.java:160-164]` |
| 3 | Tree branch / Climb | `35970` `[S-GNOME:86]` | none `[S-GNOME:86-99]` | `5.0` `[S-GNOME:95]` | normal `3`, advanced `3` `[S-GNOME:97-98]` | agrees on `5` `[D-GnomeAgility.java:172-176]` |

### Normal branch

| Traversal | Obstacle / interaction | Object ID | Level | Base XP | Stage effect | Darkan divergence (never ships) |
|---:|---|---:|---:|---:|---|---|
| 4N | Balancing rope / Walk-on | `2312` `[S-OBJS:1302]` | none `[S-GNOME:102-115]` | `7.5` `[S-GNOME:112]` | normal `4` `[S-GNOME:114]` | Darkan/wiki use `7`, not `7.5` `[D-GnomeAgility.java:196-200; W-GNOME oldid=6391497]` |
| 5N | Tree branch / Climb-down | `2314` or `2315` `[S-OBJS:1304; S-GNOME:117-118]` | none `[S-GNOME:117-131]` | `5.0` `[S-GNOME:127]` | normal `5` `[S-GNOME:129]` | agrees on `5` `[D-GnomeAgility.java:211-215]` |
| 6N | Obstacle net / Climb-over | `2286` `[S-GNOME:133]` | none `[S-GNOME:133-149]` | `7.5` `[S-GNOME:146]` | normal `6` `[S-GNOME:147]` | Darkan/wiki use `8`, not `7.5` `[D-GnomeAgility.java:223-227; W-GNOME oldid=6391497]` |
| 7N | Obstacle pipe / Squeeze-through | `43543` or `43544` `[S-GNOME:285-287]` | none `[S-GNOME:287-345]` | `7.5` `[S-GNOME:338-341]` | finish; requires normal `6`, then normal reset `0` `[S-GNOME:289,337-342]` | Darkan uses base `7` plus bonus `39.5`; both differ `[D-GnomeAgility.java:248-252]` |

Normal lap total: `86.5 XP = 47.5 obstacle XP + 39.0 bonus` `[S-GNOME:65,80,95,112,127,146,338; S-GNOME:6]`.

### Advanced branch

| Traversal | Obstacle / interaction | Object ID | Level | Base XP | Stage effect | Darkan divergence (never ships) |
|---:|---|---:|---:|---:|---|---|
| 4A | Advanced tree / Climb-up | `43528` `[S-GNOME:150]` | `85` `[S-GNOME:151,165]` | `25.0` `[S-GNOME:159]` | advanced `4`; normal reset `0` `[S-GNOME:161-162]` | Darkan uses object `69506` and `19 XP` `[D-GnomeAgility.java:90-98]` |
| 5A | Signpost / Run-across | `43581` `[S-OBJS:20563]` | branch gate already passed | `25.0` `[S-GNOME:184]` | advanced `5` `[S-GNOME:186]` | Darkan uses object `69514` and `22 XP` `[D-GnomeAgility.java:81-87]` |
| 6A | Pole / Swing-to | `43529` `[S-OBJS:20546]` | branch gate already passed | `25.0` `[S-GNOME:242]` | advanced `6` `[S-GNOME:244]` | agrees on `25`, different object handler generation `[D-GnomeAgility.java:45-71]` |
| 7A | Barrier / Jump-over into pipe | `43539` `[S-OBJS:20550]` | branch gate already passed | intended table value `25.0` `[S-GNOME:275,278,281]` | finish; requires advanced `6` `[S-GNOME:249,277]` | Darkan uses `25` plus `605` when complete `[D-GnomeAgility.java:100-120]` |

Advanced lap total for the data table: `725 XP = 120 obstacle XP + 605 bonus` `[S-GNOME:65,80,95,159,184,242,275; S-GNOME:7]`.

Implementation defects to preserve as audit findings, not constants:

- The final advanced handler always grants `25`, then grants another `25 + 605` on a completed lap (or another `25` on an incomplete lap), so runtime awards are `25 XP` too high `[S-GNOME:275-281]`.
- The completed advanced handler calls `setGnomeAgilityStage(0)`, not `setAdvancedGnomeAgilityStage(0)` `[S-GNOME:277-279]`. The next log directly writes advanced stage `1`, so a new lap self-recovers `[S-GNOME:66-67]`.
- The pinned wiki gives normal rope/net XP `7`/`8` and normal bonus `39.5`; Tier 1 wins with `7.5`/`7.5`/`39.0` `[W-GNOME oldid=6391497; S-GNOME:6,112,146]`.

## 2. Barbarian Outpost: shared trunk with two branches

Normal course requirement: level `35` and Bar Crawl access `[W-BARB oldid=6549278]`; 2011Scape does not enforce that course-entry gate inside this file, so this requirement is the narrow wiki gap. Advanced fork requirement: current Agility `> 89`, i.e. level `90` `[S-BARB:208-224]`. Normal completion bonus: `46.2 XP` `[S-BARB:17]`. Advanced completion bonus: `615 XP` `[S-BARB:18]`.

The normal and advanced counters use the same ordered `stage + 1 == newStage` rule `[S-BARB:46-63]`. The first two obstacles advance both. Normal obstacle three resets the advanced counter; advanced obstacle three resets the normal counter `[S-BARB:65-116,208-220]`.

### Shared trunk

| Traversal | Obstacle / interaction | Object ID | Level | Base XP | Stage effect | Darkan divergence (never ships) |
|---:|---|---:|---:|---:|---|---|
| 1 | Rope swing / Swing-on | `43526` `[S-OBJS:20543]` | course gate `35` `[W-BARB oldid=6549278]` | `22.0` `[S-BARB:85]` | normal `1`, advanced `1` `[S-BARB:86-87]` | Darkan uses `28.0` `[D-BarbarianOutpostAgility.kt:61-75]` |
| 2 | Log balance / Walk-across | `43595` `[S-OBJS:20567]` | course gate `35` `[W-BARB oldid=6549278]` | `13.7` `[S-BARB:100]` | normal `2`, advanced `2` `[S-BARB:101-102]` | Darkan uses `20.7` `[D-BarbarianOutpostAgility.kt:80-89]` |

### Normal branch

| Traversal | Obstacle / interaction | Object ID | Level | Base XP | Stage effect | Darkan divergence (never ships) |
|---:|---|---:|---:|---:|---|---|
| 3N | Obstacle net / Climb-over | `20211` `[S-OBJS:11670]` | course gate `35` `[W-BARB oldid=6549278]` | `8.2` `[S-BARB:114]` | normal `3`; advanced reset `0` `[S-BARB:115-116]` | Darkan uses `10.2` `[D-BarbarianOutpostAgility.kt:93-100]` |
| 4N | Balancing ledge / Walk-across | `2302` `[S-OBJS:1292]` | course gate `35` | `22.0` `[S-BARB:139]` | normal `4` `[S-BARB:140]` | Darkan uses `26.0` `[D-BarbarianOutpostAgility.kt:102-125]` |
| connector | Ladder / Climb-down | `3205` `[S-OBJS:1935]` | none in handler `[S-BARB:143-150]` | `0` `[S-BARB:143-150]` | unchanged `[S-BARB:143-150]` | no material data effect |
| 5N | First crumbling wall / Climb-over | `1948` `[S-OBJS:1053]` | course gate `35` | `13.7` `[S-BARB:153-173]` | normal `5` `[S-BARB:173]` | Darkan uses `16.2` `[D-BarbarianOutpostAgility.kt:129-146]` |
| 6N | Second crumbling wall / Climb-over | `1948` `[S-OBJS:1053]` | course gate `35` | intended table value `13.7` `[S-BARB:176-200]` | finish; requires normal `5`, then normal reset `0` `[S-BARB:177,195-197]` | Darkan uses `16.2` plus bonus `56.7` `[D-BarbarianOutpostAgility.kt:129-152]` |

Normal lap total for the data table: `139.5 XP = 93.3 obstacle XP + 46.2 bonus` `[S-BARB:85,100,114,139,172,194; S-BARB:17]`.

### Advanced branch

| Traversal | Obstacle / interaction | Object ID | Level | Base XP | Stage effect | Darkan divergence (never ships) |
|---:|---|---:|---:|---:|---|---|
| 3A | Wall run / Run-up | `43533` `[S-OBJS:20549]` | `90` `[S-BARB:209,223]` | `15.0` `[S-BARB:217]` | advanced `3`; normal reset `0` `[S-BARB:219-220]` | agrees on `15` `[D-BarbarianOutpostAgility.kt:156-169]` |
| 4A | Wall climb / Climb-up | `43597` `[S-OBJS:20568]` | branch gate already passed | `15.0` `[S-BARB:235]` | advanced `4` `[S-BARB:236]` | agrees `[D-BarbarianOutpostAgility.kt:173-188]` |
| 5A | Spring device / Fire | `43587` `[S-OBJS:20564]` | branch gate already passed | `15.0` `[S-BARB:247]` | advanced `5` `[S-BARB:248]` | agrees `[D-BarbarianOutpostAgility.kt:192-203]` |
| 6A | Balance beam / Cross | `43527` `[S-OBJS:20544]` | branch gate already passed | `15.0` `[S-BARB:257]` | advanced `6` `[S-BARB:258]` | agrees `[D-BarbarianOutpostAgility.kt:209-223]` |
| 7A | Gap / Jump-over | `43531` `[S-OBJS:20547]` | branch gate already passed | `15.0` `[S-BARB:268]` | advanced `7` `[S-BARB:269]` | agrees `[D-BarbarianOutpostAgility.kt:227-246]` |
| 8A | Roof / Slide-down | `43532` `[S-OBJS:20548]` | branch gate already passed | `15.0` `[S-BARB:286-289]` | finish; requires advanced `7`, then advanced reset `0` `[S-BARB:273,285-287]` | agrees, including `615` bonus `[D-BarbarianOutpostAgility.kt:251-267]` |

Advanced lap total: `740.7 XP = 125.7 obstacle XP + 615 bonus` `[S-BARB:85,100,217,235,247,257,268,286; S-BARB:18]`.

Implementation defect: the second normal wall grants an unconditional `13.7`, then another `13.7 + 46.2` on completion (or another `13.7` if incomplete), making runtime awards `13.7 XP` higher than the audited table `[S-BARB:194-200]`. The file itself says `TO-DO: Add Fail changes` `[S-BARB:10-14]`.

## 3. Wilderness course

2011Scape’s entry handler actually requires current level `>= 53`, while its message says “level 52” `[S-WILD:39-43]`. Tier 1 therefore ships course requirement `53`; the pinned wiki’s pre-EOC requirement `52` is a recorded conflict `[W-WILD oldid=6487716]`. Completion bonus: `499.0 XP` `[S-WILD:15]`. Ordered advancement is `stage + 1 == newStage` `[S-WILD:30-38]`.

| Traversal | Obstacle / interaction | Object ID | Level | Base XP | Stage effect | Darkan divergence (never ships) |
|---:|---|---:|---:|---:|---|---|
| 1 | Obstacle pipe / Squeeze-through | `2288` `[S-OBJS:1284]` | course gate `53` `[S-WILD:39-43]` | `12.5` `[S-WILD:131]` | direct stage `1` `[S-WILD:130]` | value agrees; Darkan uses revised object `65362` `[D-WildernessAgility.kt:113-140]` |
| 2 | Rope swing / Swing-on | `2283` `[S-OBJS:1281]` | course gate `53` | `20.0` `[S-WILD:154]` | stage `2` `[S-WILD:155]` | value agrees; Darkan object `64696` `[D-WildernessAgility.kt:144-187]` |
| 3 | Stepping stones / Cross | `37704` `[S-OBJS:18190]` | course gate `53` | `20.0` `[S-WILD:244]` | stage `3` `[S-WILD:243]` | value agrees; Darkan object `64699` `[D-WildernessAgility.kt:195-225]` |
| 4 | Log balance / Walk-across | `2297` `[S-OBJS:1289]` | course gate `53` | `20.0` `[S-WILD:257]` | stage `4` `[S-WILD:258]` | value agrees; Darkan object `64698` `[D-WildernessAgility.kt:228-271]` |
| 5 | Rocks / Climb | `2328` `[S-OBJS:1318]` | course gate `53` | `0.0` `[S-WILD:273-276]` | finish; requires stage `4`, then reset `0` `[S-WILD:262,272-274]` | bonus agrees; Darkan revised cliff object `65734` `[D-WildernessAgility.kt:275-294]` |

Lap total: `571.5 XP = 72.5 obstacle XP + 499 bonus` `[S-WILD:131,154,244,257,273; S-WILD:15]`.

The pinned wiki also describes a `15 XP` access walkway that can fail before the main course `[W-WILD oldid=6487716]`. 2011Scape does not implement that obstacle in its trusted course file, and Tier 2 was authorised only to fill wholly absent courses, so it is a documented non-shipping omission rather than silently appended to the table.

## 4. Burthorpe / Gnome beginner course

Course requirement: level `1` `[W-BURTHORPE oldid=6130636]`. Perfect-lap total: `79.5 XP` `[W-BURTHORPE oldid=6130636]`. The page gives the final Leap of Faith as `46.5 XP` but does not decompose it into final-obstacle base XP versus a lap bonus; completion bonus is therefore `source_blocked` rather than inferred as `41.0`.

The pinned table is read row-wise, consistent with the same wiki’s Gnome and Ape Atoll traversal tables. C742 and C741 expose matching client objects/options for every named interaction.

| Stage | Obstacle / interaction | C742/C741 client object | Level | Shipped XP | Darkan divergence (never ships) |
|---:|---|---|---:|---:|---|
| 1 | Log beam / Walk | `66894`, `Log beam`, `[Walk]` `[C742 object 66894; C741 object 66894]` | `1` course gate `[W-BURTHORPE oldid=6130636]` | `5.5` `[W-BURTHORPE oldid=6130636]` | agrees `[D-BurthorpeAgility.java:26]` |
| 2 | Wall / Climb-up | `66912`, `Wall`, `[Climb-up]` `[C742 object 66912; C741 object 66912]` | `1` | `5.5` `[W-BURTHORPE oldid=6130636]` | agrees `[D-BurthorpeAgility.java:27]` |
| 3 | Balancing ledge / Walk-across | `66909`, `Balancing ledge`, `[Walk-across]` `[C742 object 66909; C741 object 66909]` | `1` | `5.5` `[W-BURTHORPE oldid=6130636]` | agrees `[D-BurthorpeAgility.java:30]` |
| 4 | Obstacle low wall / Climb-over | `66902`, `Obstacle low wall`, `[Climb-over]` `[C742 object 66902; C741 object 66902]` | `1` | `5.5` `[W-BURTHORPE oldid=6130636]` | agrees `[D-BurthorpeAgility.java:31]` |
| 5 | Rope swing / Swing-on | `66904`, `Rope swing`, `[Swing-on]` `[C742 object 66904; C741 object 66904]` | `1` | `5.5` `[W-BURTHORPE oldid=6130636]` | agrees `[D-BurthorpeAgility.java:28]` |
| 6 | Monkey bars / Swing-across | `66897`, `Monkey bars`, `[Swing-across]` `[C742 object 66897; C741 object 66897]` | `1` | `5.5` `[W-BURTHORPE oldid=6130636]` | agrees `[D-BurthorpeAgility.java:29]` |
| 7 / finish | Leap of Faith / Jump-down | `66910`, `Ledge`, `[Jump-down]` `[C742 object 66910; C741 object 66910]` | `1` | `46.5`, inclusive final award `[W-BURTHORPE oldid=6130636]` | Darkan awards `46`, a `0.5 XP` shortfall `[D-BurthorpeAgility.java:33-36]` |

## 5. Agility Pyramid

Course requirement: level `30` `[W-PYRAMID oldid=6457748]`. Shipped completion bonus: `300 XP` `[W-PYRAMID oldid=6457748]`. Perfect ascent total: `1,014 XP` `[W-PYRAMID oldid=6457748]`.

The pinned wiki proves obstacle types, XP, occurrence counts, and damage, but it does **not** print the occurrence-by-occurrence traversal order in wikitext; the order exists only in an embedded map image. Darkan prints a 25-stage order, but Darkan cannot supply shipping order under this audit. Therefore the shippable type ledger is complete, while every exact Pyramid stage index is `source_blocked`. The future implementation must not promote Darkan’s order without independent period proof.

| Obstacle type | Occurrences | Cache object identity | Level | Shipped XP each | Stage index | Darkan divergence (never ships) |
|---|---:|---|---:|---:|---|---|
| Rolling blocks | `5` `[W-PYRAMID oldid=6457748]` | `10875/10876`, `Stone block`, no option `[C742 objects 10875-10876; C741 objects 10875-10876]` | `30` course gate | `12` `[W-PYRAMID oldid=6457748]` | `source_blocked` | Darkan also has five roller stages, but orders them at indices `0,4,10,20,23` `[D-AgilityPyramidController.java:44-92]` |
| Climb-over low wall | `4` `[W-PYRAMID oldid=6457748]` | `10865`, `Low wall`, `[Climb-over]` `[C742 object 10865; C741 object 10865]` | `30` | `8` `[W-PYRAMID oldid=6457748]` | `source_blocked` | Darkan has **five** wall stages `1,12,14,19,22`, contradicting the wiki count `[D-AgilityPyramidController.java:47-81,95-101]` |
| Moving blocks | `2` `[W-PYRAMID oldid=6457748]` | `source_blocked`: no named/interactive “moving block” definition was returned by the primary-cache name search | `30` | `0` `[W-PYRAMID oldid=6457748]` | `source_blocked` | omitted from Darkan’s 25-stage ledger `[D-AgilityPyramidController.java:44-84]` |
| Cross ledge | `4` `[W-PYRAMID oldid=6457748]` | `10860/10886-10888`, `Ledge`, `[Cross]` `[C742 objects 10860,10886-10888; C741 same]` | `30` | `52` `[W-PYRAMID oldid=6457748]` | `source_blocked` | four Darkan shimmy-sideways stages `2,6,11,15`, agrees on count `[D-AgilityPyramidController.java:47-81,119-125]` |
| Cross plank | `2` `[W-PYRAMID oldid=6457748]` | `10867/10868`, `Plank`, `[Cross]` `[C742 objects 10867-10868; C741 same]` | `30` | `56.4` `[W-PYRAMID oldid=6457748]` | `source_blocked` | two Darkan walk-log stages `3,17`, agrees on count `[D-AgilityPyramidController.java:47-81,111-117]` |
| Cross gap | `3` `[W-PYRAMID oldid=6457748]` | `10861-10864/10882-10885`, `Gap`, `[Cross]` `[C742 objects 10861-10864,10882-10885; C741 same]` | `30` | `56.4` `[W-PYRAMID oldid=6457748]` | `source_blocked` | three Darkan shimmy-handhold stages `5,7,9`, agrees on count `[D-AgilityPyramidController.java:47-81,127-133]` |
| Jump gap | `6` `[W-PYRAMID oldid=6457748]` | `10859`, `Gap`, `[Jump]` `[C742 object 10859; C741 object 10859]` | `30` | `22` `[W-PYRAMID oldid=6457748]` | `source_blocked` | six Darkan jump-gap stages `8,13,16,18,21,24`, agrees on count `[D-AgilityPyramidController.java:56-81,103-109]` |
| Climb-up stairs | `5` `[W-PYRAMID oldid=6457748]` | `10857/10858`, `Stairs`, `[Climb-up]/[Climb-down]` `[C742 objects 10857-10858; C741 same]` | `30` | `0` `[W-PYRAMID oldid=6457748]` | `source_blocked` | omitted from Darkan’s XP-stage ledger `[D-AgilityPyramidController.java:44-84]` |
| Finish / retrieve top and descend | `1` bonus `[W-PYRAMID oldid=6457748]` | `10851` Climbing rocks `[Climb]`; `10855/10856` Doorway `[Enter]` `[C742 objects 10851,10855-10856; C741 same]` | `30` | `300` completion bonus `[W-PYRAMID oldid=6457748]` | finish | Darkan awards `500`, not `300` `[D-AgilityPyramidController.java:287-297]` |

Darkan-only ordered lead, **not shippable**: `roller, wall, ledge, plank, roller, cross-gap, ledge, cross-gap, jump-gap, cross-gap, roller, ledge, wall, jump-gap, wall, ledge, jump-gap, plank, jump-gap, wall, roller, jump-gap, wall, roller, jump-gap` at indices `0–24` `[D-AgilityPyramidController.java:44-84]`. It contains five walls where the period wiki says four and excludes the wiki’s two moving blocks and five stair traversals; every index remains `source_blocked`.

## 6. Ape Atoll

Course requirement: level `48`, a small ninja greegree, and Monkey Madness chapter 2 completion `[W-APE oldid=6538325]`. Completion bonus: `300 XP` paid with the final climb-down after the full sequence `[W-APE oldid=6538325]`. Perfect-lap total: `580 XP` `[W-APE oldid=6538325]`.

| Stage | Obstacle / interaction | C742/C741 client object | Level | Shipped XP | Darkan divergence (never ships) |
|---:|---|---|---:|---:|---|
| 1 | Jump-to stepping stone | `12568`, `Stepping stone`, `[Jump-to]` `[C742 object 12568; C741 object 12568]` | `48` `[W-APE oldid=6538325]` | `40` `[W-APE oldid=6538325]` | Darkan’s stepping-stone path awards `15` and can randomly fail `[D-ApeAtollAgility.java:96-134]` |
| 2 | Climb tropical tree | `12570`, `Tropical tree`, `[Climb]` `[C742 object 12570; C741 object 12570]` | `48` | `40` `[W-APE oldid=6538325]` | Darkan awards `25` for climb-up `[D-ApeAtollAgility.java:73-81]` |
| 3 | Swing across monkeybars | `12573/12575`, `Monkeybars`, `[Swing Across]` `[C742 objects 12573,12575; C741 same]` | `48` | `40` `[W-APE oldid=6538325]` | Darkan awards `35` `[D-ApeAtollAgility.java:84-93]` |
| 4 | Climb-up skull slope | `12576`, `Skull slope`, `[Climb-up]` `[C742 object 12576; C741 object 12576]` | `48` | `60` `[W-APE oldid=6538325]` | Darkan awards `45` `[D-ApeAtollAgility.java:64-70]` |
| 5 | Swing rope | `12578`, `Rope`, `[Swing]` `[C742 object 12578; C741 object 12578]` | `48` | `100` `[W-APE oldid=6538325]` | Darkan awards `22` `[D-ApeAtollAgility.java:136-143]` |
| 6 / finish | Climb-down tropical tree/vine | `12618`, `Tropical tree`, `[Climb-down]` `[C742 object 12618; C741 object 12618]` | `48` | `100` base + `300` completion bonus `[W-APE oldid=6538325]` | Darkan has separate tree/vine handlers awarding `55`/`36` and no ordered lap bonus `[D-ApeAtollAgility.java:44-61]` |

## 7. Werewolf (Canifis)

Course requirement: level `60`, Creature of Fenkenstrain completion, and Ring of Charos for entry/turn-in `[W-WEREWOLF oldid=6288778]`. Successful course XP before the optional hand-in bonus: `350` `[W-WEREWOLF oldid=6288778]`. Stick completion bonus: `190 XP`; total with stick: `540 XP` `[W-WEREWOLF oldid=6288778]`.

| Stage | Obstacle / interaction | C742/C741 client object | Level | Shipped XP | Darkan divergence (never ships) |
|---:|---|---|---:|---:|---|
| 1 | Stepping stones | `35996`, `Stepping stone`, `[Jump-to]` `[C742 object 35996; C741 object 35996]` | `60` `[W-WEREWOLF oldid=6288778]` | `50` for the group `[W-WEREWOLF oldid=6288778]` | Darkan awards `10` per one of five stones, totalling `50` `[D-WerewolfAgility.kt:29-34,73-108,256-260]` |
| 2 | Hurdles | `5133/5134/5135`, `Hurdle`, `[Jump]` `[C742 objects 5133-5135; C741 same]` | `60` | `60` for the group `[W-WEREWOLF oldid=6288778]` | Darkan awards `20` per hurdle, totalling `60` `[D-WerewolfAgility.kt:110-116]` |
| 3 | Pipe | `5152`, `Pipe`, `[Squeeze-through]` `[C742 object 5152; C741 object 5152]` | `60` | `15` `[W-WEREWOLF oldid=6288778]` | agrees `[D-WerewolfAgility.kt:118-125]` |
| 4 | Skull slope | `5136`, `Skull slope`, `[Climb-up]` `[C742 object 5136; C741 object 5136]` | `60` | `25` `[W-WEREWOLF oldid=6288778]` | agrees `[D-WerewolfAgility.kt:127-134]` |
| 5 / finish | Deathslide / teeth-grip zip line | `5139/5140/5141`, `Zip line`, `[Teeth-grip]` `[C742 objects 5139-5141; C741 same]` | `60` | `200` on success; `180–<200` on an early/partial fall `[W-WEREWOLF oldid=6288778]` | Darkan uses failure XP `120` or `140`, not the wiki’s `180–200` range `[D-WerewolfAgility.kt:194-224]` |
| deferred bonus | Return fetched stick to trainer | NPC action; no course object | Ring of Charos needed for turn-in `[W-WEREWOLF oldid=6288778]` | `190` `[W-WEREWOLF oldid=6288778]` | Darkan awards `380 × stick count`, double the pinned value `[D-WerewolfAgility.kt:52-58]` |

## 8. Dorgesh-Kaan

Course requirement: level `80` Agility, Death to the Dorgeshuun completion, and a light source `[W-DORGESH oldid=6547042]`. This table is the Agility route both directions; the requested heavy generator part is retrieved between outbound and return legs. Each one-way route pays `159 XP`; two directions pay `318 XP`; Turgall’s correct heavy-item hand-in pays a `2,057 XP` completion bonus, totaling `2,375 XP` `[W-DORGESH oldid=6547042]`. Neither emulator implements this course.

| Stage | Direction | Obstacle / interaction | C742/C741 client object | Level | Shipped XP | Darkan divergence |
|---:|---|---|---|---:|---:|---|
| 1 | outbound | Cable balance / Walk-across | `22569`, `Cable`, `[Walk-across]` `[C742 object 22569; C741 object 22569]` | `80` `[W-DORGESH oldid=6547042]` | `25` `[W-DORGESH oldid=6547042]` | absent |
| 2 | outbound | Cable swing / Swing | `22572`, `Cable`, `[Swing]` `[C742 object 22572; C741 object 22572]` | `80` | `22` `[W-DORGESH oldid=6547042]` | absent |
| 3 | outbound | Ladder / Swing-across (“Monkey bars” in wiki table) | `22564`, `Ladder`, `[Swing-across]` `[C742 object 22564; C741 object 22564]` | `80` | `25` `[W-DORGESH oldid=6547042]` | absent |
| 4 | outbound | Cable swing / Swing | `22572`, `Cable`, `[Swing]` `[C742 object 22572; C741 object 22572]` | `80` | `22` `[W-DORGESH oldid=6547042]` | absent |
| 5 | outbound | Jutting wall / Squeeze-past | `22552`, `Jutting wall`, `[Squeeze-past]` `[C742 object 22552; C741 object 22552]` | `80` | `7.5` `[W-DORGESH oldid=6547042]` | absent |
| 6 | outbound | Tunnel / Squeeze-through | `22557`, `Tunnel`, `[Squeeze-through]` `[C742 object 22557; C741 object 22557]` | `80` | `7.5` `[W-DORGESH oldid=6547042]` | absent |
| 7 | outbound | Cable balance / Walk-across | `22569`, `Cable`, `[Walk-across]` `[C742 object 22569; C741 object 22569]` | `80` | `25` `[W-DORGESH oldid=6547042]` | absent |
| 8 | outbound | Ladder / Swing-across | `22564`, `Ladder`, `[Swing-across]` `[C742 object 22564; C741 object 22564]` | `80` | `25` `[W-DORGESH oldid=6547042]` | absent |
| midpoint | retrieve requested heavy part | generator interaction; exact object ID `source_blocked` | `80` | `0` `[W-DORGESH oldid=6547042]` | absent |
| 9 | return | Ladder / Swing-across | `22564` `[C742 object 22564; C741 object 22564]` | `80` | `25` `[W-DORGESH oldid=6547042]` | absent |
| 10 | return | Cable balance / Walk-across | `22569` `[C742 object 22569; C741 object 22569]` | `80` | `25` `[W-DORGESH oldid=6547042]` | absent |
| 11 | return | Tunnel / Squeeze-through | `22557` `[C742 object 22557; C741 object 22557]` | `80` | `7.5` `[W-DORGESH oldid=6547042]` | absent |
| 12 | return | Jutting wall / Squeeze-past | `22552` `[C742 object 22552; C741 object 22552]` | `80` | `7.5` `[W-DORGESH oldid=6547042]` | absent |
| 13 | return | Cable swing / Swing | `22572` `[C742 object 22572; C741 object 22572]` | `80` | `22` `[W-DORGESH oldid=6547042]` | absent |
| 14 | return | Ladder / Swing-across | `22564` `[C742 object 22564; C741 object 22564]` | `80` | `25` `[W-DORGESH oldid=6547042]` | absent |
| 15 | return | Cable swing / Swing | `22572` `[C742 object 22572; C741 object 22572]` | `80` | `22` `[W-DORGESH oldid=6547042]` | absent |
| 16 | return | Cable balance / Walk-across | `22569` `[C742 object 22569; C741 object 22569]` | `80` | `25` `[W-DORGESH oldid=6547042]` | absent |
| finish | hand requested heavy part to Turgall | NPC hand-in | correct requested item `[W-DORGESH oldid=6547042]` | `2,057` completion bonus `[W-DORGESH oldid=6547042]` | absent |

The pinned page also defines a grapple/Ranged route. It is outside this Agility-table scope except that mixing one Agility leg with one grapple leg changes the payout; no mixed-route number is imported into the lap above `[W-DORGESH oldid=6547042]`.

## 9. Penguin course

Course requirement: level `30`, Cold War completion, and a Penguin suit `[W-PENGUIN oldid=5988056]`. Completion bonus: `65 XP` `[W-PENGUIN oldid=5988056]`. Perfect-lap total: `540 XP` `[W-PENGUIN oldid=5988056]`. Neither emulator implements this course.

| Stage | Obstacle group | C742/C741 client object pin | Level | Shipped XP | Darkan divergence |
|---:|---|---|---:|---:|---|
| 1 | Ice crushers | Entry interaction `21120`, `Stepping Stone`, `[Climb]`; crusher scenery itself has no named interactive definition `[C742 object 21120; C741 object 21120]` | `30` `[W-PENGUIN oldid=5988056]` | `55` `[W-PENGUIN oldid=5988056]` | absent |
| 2 | Complete platform jumps | `21126, 21128-21133`, `Stepping Stone`, `[Jump]` `[C742 objects 21126,21128-21133; C741 same]` | `30` | `80` for the complete group `[W-PENGUIN oldid=5988056]` | absent |
| 3 | Icicles / Tread-softly | `21134`, `Icicles`, `[Tread-softly]` `[C742 object 21134; C741 object 21134]` | `30` | `40 each`, `160 total` `[W-PENGUIN oldid=5988056]` | absent |
| 4 | Ice slope | `21142/21143`, `Snow jump`, `[Jump]`, followed by `21148-21156`, `Ice`, `[Cross]` `[C742 objects 21142-21143,21148-21156; C741 same]` | `30` | `180` `[W-PENGUIN oldid=5988056]` | absent |
| finish | Agility bonus | no separate interactive object proven | completed all four groups `[W-PENGUIN oldid=5988056]` | `65` `[W-PENGUIN oldid=5988056]` | absent |

Cache qualification: the exact split between the wiki label “Ice crushers” and its stepping-stone/scenery objects, and between “Ice slope” and the Snow jump + Ice object sequence, is not stated server-side by either emulator. The client objects are real in both primary caches, but any narrower one-ID mapping is `source_blocked`.

## 10. Brimhaven Agility Arena — streak currency, not a lap

Brimhaven has no lap bonus. It is a random active-pillar streak mechanic that awards a currency, followed by a deferred player-chosen exchange.

### Pillar flagging and streak state

| Mechanic | Shipped rule | Evidence | Darkan divergence/implementation note |
|---|---|---|---|
| Arena layout | `25` platforms in a `5×5` grid; `24` have pillars and one has the exit | `[W-BRIM oldid=6556177]` | Darkan randomly chooses among `5×5` coordinates and excludes the exit tile `[D-BrimhavenAgilityController.java:85-92]` |
| Active pillar | One active pillar is flagged by a yellow minimap arrow; it changes every `60 seconds` | `[W-BRIM oldid=6556177]` | Darkan schedules selection every one minute and adds a hint icon `[D-BrimhavenAgilityController.java:62-64,83-117]` |
| Client identity | Taggable dispenser object IDs are `3581` and `3608`, name `Ticket Dispenser`, option `[Tag]` | `[C742 objects 3581,3608; C741 objects 3581,3608]` | Darkan accepts exactly those IDs and only the currently flagged tile `[D-BrimhavenAgilityController.java:121-125]` |
| Initial state | Player begins inactive/red; tagging the active pillar makes the player active/green but yields no ticket | `[W-BRIM oldid=6556177]` | Darkan sets its temp stage and varbit and prints “You get tickets by tagging more than one pillar in a row” `[D-BrimhavenAgilityController.java:126-130]` |
| Streak | Every subsequent active pillar tagged before it changes yields a ticket; missing an active pillar resets the player inactive, so the next tag only restarts the streak | `[W-BRIM oldid=6556177]` | Darkan’s intended award branch adds item `2996 × 1` `[D-BrimhavenAgilityController.java:133-140]` |
| Tickets per qualifying tag | `1` ticket `[W-BRIM oldid=6556177; W-TICKET oldid=5777910]` | Period wiki; Karamja gloves 4 additionally give a `25%` chance of double tickets `[W-TICKET oldid=5777910]` | Darkan adds exactly `1` item `2996` `[D-BrimhavenAgilityController.java:138-140]` |

Darkan controller bug: within this file the state is assigned only `-1` and `0`, while the item-award branch requires a value other than `-1` or `0`; no line sets such a value. The award branch therefore appears unreachable as written `[D-BrimhavenAgilityController.java:95-104,126-140]`. This is a divergence finding only and supplies no shipped mechanic.

### Ticket → XP exchange

The exact **approved pre-EOC** exchange schedule is:

| Player-chosen ticket bundle | Base XP | With Karamja gloves 2/3/4 (`+10%`) | Source |
|---:|---:|---:|---|
| `1` | `240` | `264` | `[W-BRIM oldid=6556177; W-TICKET oldid=5777910]` |
| `10` | `2,480` | `2,728` | `[W-BRIM oldid=6556177; W-TICKET oldid=5777910]` |
| `25` | `6,500` | `7,150` | `[W-BRIM oldid=6556177; W-TICKET oldid=5777910]` |
| `100` | `28,000` | `30,800` | `[W-BRIM oldid=6556177; W-TICKET oldid=5777910]` |
| `1,000` | `320,000` | `352,000` | `[W-BRIM oldid=6556177; W-TICKET oldid=5777910]` |

For chosen bundle counts `n1, n10, n25, n100, n1000`, the exact period-supported formula is:

```text
base_xp = 240*n1 + 2480*n10 + 6500*n25 + 28000*n100 + 320000*n1000
gloves_xp = base_xp * 1.10
```

The five allowed bundle values and exact 10% outputs are directly tabulated by the two pinned oldids above; the expression is only their additive restatement.

**Level-scaling audit:** the task premise says the exchange scales with Agility level, but the pinned arena and ticket oldids tabulate fixed bundle awards and state no level term `[W-BRIM oldid=6556177; W-TICKET oldid=5777910]`. Pirate Jackie’s own pinned page says only that Karamja gloves increase the exchange award by `10%`; it states no level term or formula `[W-JACKIE oldid=6225118]`. Darkan implements no exchange at all (`PirateJackieTheFruit.java` only exposes Achievement System dialogue `[D-PirateJackieTheFruit.java:12-20]`). A modern OSRS page is a lead for `+5 XP per ticket per Agility level above 40`, but modern OSRS is inadmissible under this audit. Therefore the level-scaling term is `source_blocked`; it must **not** ship. The fixed bundle schedule above is the complete formula supported by approved pre-EOC evidence.

### Arena obstacle/failure matrix

These XP values are immediate obstacle XP, separate from tickets. Karamja gloves 2/3/4 add `10%` to arena obstacle and ticket-exchange XP `[W-BRIM oldid=6556177]`.

| Level | Obstacle | Immediate XP | Pinned failure statement |
|---:|---|---:|---|
| none | Low wall | `8` | “tiny” chance `[W-BRIM oldid=6556177]` |
| none | Rope swing | `20` | `60% success` `[W-BRIM oldid=6556177]` |
| none | Log balance | `12` | low chance `[W-BRIM oldid=6556177]` |
| none | Ledge | `16` | wiki prints `10%` in the chance line `[W-BRIM oldid=6556177]` |
| none | Plank balance | `6` | correct plank cannot fail; two cracked planks are unsafe `[W-BRIM oldid=6556177]` |
| none | Pillars | `18` | medium; only the second pillar can fail `[W-BRIM oldid=6556177]` |
| none | Monkey bars | `14` | low chance `[W-BRIM oldid=6556177]` |
| none | Rope balance | `10` | medium chance `[W-BRIM oldid=6556177]` |
| none | Sawblade | `0` | timing-based, not a random failure; may damage/push back `[W-BRIM oldid=6556177]` |
| `20` | Spiked floor | `24` | high chance `[W-BRIM oldid=6556177]` |
| `20` | Pressure pads | `26` | wiki prints medium-high (`60%`) `[W-BRIM oldid=6556177]` |
| `20` | Hand-holds | `22` | wiki prints high (`70%`); only third hold can fail `[W-BRIM oldid=6556177]` |
| `40` | Spinning blades | `28` | wiki prints high (`70%`) `[W-BRIM oldid=6556177]` |
| `40` | Darts | `30` | high; failure drains `2 Agility levels` `[W-BRIM oldid=6556177]` |

All ordinary arena obstacle failures deal `20–60 life points` based on current life points; the pinned page provides no exact damage formula and no general level-to-fail-chance formula, so both are `source_blocked` beyond those bounds/qualitative rows `[W-BRIM oldid=6556177]`.

## 11. 2011Scape agility shortcuts

These are one-off traversal gates, not a lap or a training method. The file provides five logical shortcut entries through three executable behavior families: one monkey-bar crossing, two named stile locations sharing one handler, and the two directions through one pipe handler `[S-SHORT:33-89,91-96,234-244,409-506]`. None of these three `addXp` calls explicitly passes `checkBrawlingGloves = true`, so no brawling-glove multiplication is baked into the quoted XP `[S-SHORT:87,241,504]`.

| Logical shortcut | Object ID(s) | Level requirement | XP | Notes |
|---|---|---:|---:|---|
| Edgeville Dungeon monkey bars | `29375` `[S-OBJS:15608]` | `15` `[S-SHORT:43-47]` | `20.0` `[S-SHORT:87]` | one-off gate; this `addXp` call does not pass the course files’ brawling-glove flag `[S-SHORT:87]` |
| Fred the Farmer’s sheep-field stile | one of shared set `993, 7527, 29460, 45205, 34776, 48208`; exact location-to-ID mapping `source_blocked` `[S-SHORT:16-24,91-96; S-OBJS:561,4195,15659,17155,21454,22433]` | none `[S-SHORT:91-96,234-243]` | `3.0` `[S-SHORT:241]` | named as one of the two locations sharing the six-ID handler `[S-SHORT:91-96,234-243]` |
| Falador cabbage-patch stile | one of the same shared set; exact location-to-ID mapping `source_blocked` `[S-SHORT:16-24,91-96; S-OBJS:561,4195,15659,17155,21454,22433]` | none `[S-SHORT:91-96,234-243]` | `3.0` `[S-SHORT:241]` | named as the other location sharing the six-ID handler `[S-SHORT:91-96,234-243]` |
| Edgeville Dungeon → Varrock Sewers pipe | `29370` `[S-OBJS:15605]` | actual handler `53` `[S-SHORT:416-420]` | actual handler `7.5` `[S-SHORT:504]` | west-side entry takes the eastbound movement branch `[S-SHORT:421-424,435-467,458-504]`; comment says `51` and `10 XP`, but executable Tier-1 values win `[S-SHORT:409-420,504]` |
| Varrock Sewers → Edgeville Dungeon pipe | `29370` `[S-OBJS:15605]` | actual handler `53` `[S-SHORT:416-420]` | actual handler `7.5` `[S-SHORT:504]` | east-side entry takes the westbound movement branch `[S-SHORT:421-424,445-475,468-504]`; comment says `51` and `10 XP`, but executable Tier-1 values win `[S-SHORT:409-420,504]` |

## 12. Period failure ledger

2011Scape implements no course failure roll. Barbarian and Wilderness explicitly carry `TO-DO: Add Fail changes` `[S-BARB:10-14; S-WILD:9-13]`; Gnome contains no failure branch. The rows below are period behavior evidence for future mechanics, not overrides of the trusted per-obstacle XP tables.

| Course | Obstacles that can fail | Damage / consequence | Level scaling stated by pinned wiki | Exact fail formula |
|---|---|---|---|---|
| Gnome normal | none identified; normal route cannot damage the player `[W-GNOME oldid=6391497]` | none `[W-GNOME oldid=6391497]` | n/a | n/a |
| Gnome advanced | Signpost run only `[W-GNOME oldid=6391497]` | up to `70 LP`; still crosses but lap does not count for Agile legs `[W-GNOME oldid=6391497]` | no failures from level `89` `[W-GNOME oldid=6391497]` | `source_blocked` |
| Barbarian normal | Rope swing, log balance, balancing ledge; wiki says all except obstacle net and crumbling walls are failable `[W-BARB oldid=6549278]` | damage amount not stated; rope/ledge failure requires recovery to the start `[W-BARB oldid=6549278]` | a flawless lap is not guaranteed until level `93` `[W-BARB oldid=6549278]` | `source_blocked` |
| Barbarian advanced | “several” obstacles; log balance explicitly still rarely fails at `92`, but the page does not enumerate the full set `[W-BARB oldid=6549278]` | `source_blocked` | all obstacles reach `100%` success at `93+` `[W-BARB oldid=6549278]` | `source_blocked` |
| Wilderness access walkway | walkway can fail and drops the player among wolves `[W-WILD oldid=6487716]` | exact damage `source_blocked` | `source_blocked` | `source_blocked` |
| Wilderness main course | rope swing, third stepping stone, log balance `[W-WILD oldid=6487716]` | stepping stone removes `26.6%` of remaining LP; the page gives conflicting maxima of `208` in the table and `200` underground. Rope/log drop to dungeon; their damage is not stated `[W-WILD oldid=6487716]` | `source_blocked` | `source_blocked`; preserve the `200`/`208` internal conflict |
| Burthorpe | Log beam and obstacle low wall `[W-BURTHORPE oldid=6130636]` | no damage `[W-BURTHORPE oldid=6130636]` | only during the first few Agility levels, with no exact cutoff `[W-BURTHORPE oldid=6130636]` | `source_blocked` |
| Agility Pyramid | rolling blocks; low walls; moving blocks; cross ledges; planks; cross gaps; jump gaps `[W-PYRAMID oldid=6457748]` | respectively `60, 40, 80, 100, 100, 80, 80 LP` `[W-PYRAMID oldid=6457748]` | level `51` is only a recommendation at which roughly `3–5` failures may occur; no guaranteed cutoff `[W-PYRAMID oldid=6457748]` | `source_blocked` |
| Ape Atoll | final climb-down is explicitly failable; the page does not safely enumerate any other failable obstacle `[W-APE oldid=6538325]` | about `70–80 LP` near full life, falling toward `30 LP` as current life decreases `[W-APE oldid=6538325]` | no failure at level `75+` `[W-APE oldid=6538325]` | `source_blocked` |
| Werewolf | deathslide only `[W-WEREWOLF oldid=6288778]` | up to/over `300 LP`; earlier falls cause more, near-end falls about `100–150 LP` `[W-WEREWOLF oldid=6288778]` | rare around level `72`; impossible from level `93` `[W-WEREWOLF oldid=6288778]` | `source_blocked`; weight may affect it, but the period page gives no formula `[W-WEREWOLF oldid=6288778]` |
| Dorgesh-Kaan | cables and ladders, even at level `99` `[W-DORGESH oldid=6547042]` | about `100 LP`, fall to lower dungeon, retrieved part damaged `[W-DORGESH oldid=6547042]` | decreases at higher Agility but never reaches zero `[W-DORGESH oldid=6547042]` | `source_blocked` |
| Penguin | all four groups; first platform jump and final ice-slope step cannot fail `[W-PENGUIN oldid=5988056]` | `source_blocked` | platform jump depends on Agility level, but no formula/cutoff is stated `[W-PENGUIN oldid=5988056]` | `source_blocked` |
| Brimhaven | all random obstacles as itemised in the arena matrix; sawblade/plank are timing/choice cases `[W-BRIM oldid=6556177]` | ordinary failures `20–60 LP` based on current LP; darts also drain `2 Agility levels` `[W-BRIM oldid=6556177]` | only qualitative/isolated percentages in the page `[W-BRIM oldid=6556177]` | `source_blocked` |

## 13. Shipping blockers and conflict ledger

1. **Agility Pyramid exact order:** `source_blocked`. The period oldid gives type counts, not a textual ordered traversal. Darkan’s 25-stage lead conflicts on low-wall count and omits moving blocks/stairs; it cannot ship.
2. **Burthorpe completion-bonus decomposition:** `source_blocked`. The period table gives final Leap of Faith `46.5 XP`, not a separate base-plus-bonus split.
3. **Penguin exact scenery split:** the four wiki action groups and XP ship, and the client objects exist, but the exact one-ID boundary for Ice crushers/Ice slope is `source_blocked` beyond the grouped IDs listed.
4. **Brimhaven level-scaling term:** `source_blocked`. Approved pre-EOC oldids prove only the fixed five-bundle schedule and 10% Karamja-glove outputs; Darkan has no exchange. The modern OSRS `+5/ticket/level above 40` statement is a lead only and must not ship.
5. **2011Scape shortcut structure:** the requested five logical entries are one monkey-bar crossing, the two named stile locations, and the two pipe directions; they share only three executable handlers. The exact mapping from each named stile location to one of the handler’s six object IDs is `source_blocked`.
6. **Trusted handler double-awards:** Gnome advanced final and Barbarian normal final contain extra base-XP calls. Their declared obstacle XP and separately declared completion-bonus constants are the data-table values; runtime defects are recorded, not normalized into rates.
7. **Trusted/wiki conflicts:** 2011Scape wins: Gnome rope/net/normal bonus `7.5/7.5/39.0` over wiki/Darkan `7/8/39.5`; Wilderness entry gate `53` over wiki `52`; the wiki-only Wilderness access walkway does not ship under the course-level authorization boundary.
8. **Darkan inventions/divergences:** Darkan’s Barbarian normal XP table, Ape Atoll table, Pyramid bonus/order, Werewolf stick/failure XP, Burthorpe final XP, and Brimhaven unreachable ticket branch are all non-shipping. Dorgesh-Kaan and Penguin have no Darkan implementation at all.
