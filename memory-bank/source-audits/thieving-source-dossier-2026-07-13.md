# RuneScape Thieving pre-EOC source dossier

Audit date: 2026-07-13. Cutoff: behavior available strictly before EOC,
`2012-11-20T00:00:00Z`, as required by the repository verification standard
(`/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pre-eoc-source-verification-standard.md:15-25`).

This is a research dossier, not an implementation decision to silently fill
gaps. `proven` means the value is stated by a pinned period page or survives an
independent cache/implementation cross-check. `lead` means an emulator or
cache exposes a candidate but the period behavior does not corroborate it.
`source_blocked` means the exact value cannot be established from the sources
available in this pass.

## 1. Scope, cutoff, and method

### Source tiers and exact source records

| Key | Tier | Exact source opened | What it was used for |
|---|---|---|---|
| `STD` | Repository standard | `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/pre-eoc-source-verification-standard.md:15-137` | Cutoff, source order, corroboration gate, and explicit warning that Darkan `pickDoor()` and `checkTrapsChest()` are leads only. |
| `D` | Tier 1 | Darkan repository `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`, commit `91d0911b5209e78449b4641a0a4b1ed6ef41c0fc` | Candidate server behavior, IDs, formulas, tables, and local implementation conflicts. |
| `C727` | Tier 2 | `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/runescape-727-2012-07-24-openrs2-309-disk.zip`, SHA-256 `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8` | Direct NPC/object/item definition queries. |
| `G` | Tier 3 | 2011Scape rev-667 snapshot `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/thieving/` | Independent implementation comparison: `PickpocketTarget.kt`, `Pickpocketing.kt`, `StallTarget.kt`, `Stalls.kt`, and `thieving.plugin.kts`. The snapshot is not a Git checkout, so no commit hash exists. |
| `C742` | Tier 4 | `/Users/ArmanTarkhanian1/Library/Caches/codex/2012scape-openrs2/runescape-742-2012-11-07-openrs2-544-disk.zip`, SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8` | Closest-to-cutoff client definition queries. |
| `W-T` | Tier 5 | RuneScape Wiki, **Thieving**, oldid `6563563`, UTC `2012-11-16T07:03:40Z`, <https://runescape.wiki/w/Thieving?oldid=6563563> | Period pickpocket, stall, chest, door, and other-skill tables; multi-loot thresholds; owner/guard prose. |
| `W-S` | Tier 5 | RuneScape Wiki, **Stalls**, oldid `6563566`, UTC `2012-11-16T07:03:57Z`, <https://runescape.wiki/w/Stalls?oldid=6563566> | Dedicated stall roster and respawns. |
| `W-C` | Tier 5 | RuneScape Wiki, **Dorgesh-Kaan Chest**, oldid `6298289`, UTC `2012-09-26T05:31:50Z`, <https://runescape.wiki/w/Dorgesh-Kaan_Chest?oldid=6298289>; **Reinforced chest (Dorgesh-Kaan)**, oldid `6298402`, UTC `2012-09-26T06:13:37Z`, <https://runescape.wiki/w/Reinforced_chest_%28Dorgesh-Kaan%29?oldid=6298402> | Dorgesh-Kaan chest identity, rich-chest level/XP/loot, and the period general chest table. The resolver could not find an independent pre-cutoff **Dorgesh-Kaan Average Chest** revision. |
| `W-WS` | Tier 5 | RuneScape Wiki, **Wall safe**, oldid `6357305`, UTC `2012-10-06T17:15:25Z`, <https://runescape.wiki/w/Wall_safe?oldid=6357305> | Rogue's Den wall-safe level, XP, trap damage, stethoscope, and one loot list. |
| `W-RD` | Tier 5 | RuneScape Wiki, **Rogues' Den**, oldid `6343875`, UTC `2012-10-04T15:19:24Z`, <https://runescape.wiki/w/Rogues%27_Den?oldid=6343875> | Direct access to safes, no maze requirement, and the other period loot list. |
| `W-BJ` | Tier 5 | RuneScape Wiki, **Blackjacks**, oldid `6115926`, UTC `2012-08-20T01:34:28Z`, <https://runescape.wiki/w/Blackjacks?oldid=6115926> | Blackjack types, acquisition, The Feud gate, and two-pickpocket/three-pickpocket behavior. |
| `W-MT` | Tier 5 | RuneScape Wiki, **Menaphite Thug**, oldid `6546629`, UTC `2012-11-10T14:34:07Z`, <https://runescape.wiki/w/Menaphite_Thug?oldid=6546629> | Menaphite level, XP, loot, knockout XP, failure damage, attack behavior, and two pickpockets. |
| `W-MKF` | Tier 5 | RuneScape Wiki, **Monkey knife fighter**, oldid `6551753`, UTC `2012-11-13T05:54:40Z`, <https://runescape.wiki/w/Monkey_knife_fighter?oldid=6551753> | Monkey quest gate, knockout/pickpocket XP, damage, loot, and two-pickpocket limit. |
| `W-TR` | Tier 5 | RuneScape Wiki, **Trader**, oldid `6382333`, UTC `2012-10-11T05:21:26Z`, <https://runescape.wiki/w/Trader?oldid=6382333> | Dwarf-trader release, level, XP, loot, failure damage, and Giant Dwarf context. |
| `W-PM` | Tier 5 | RuneScape Wiki, **Pompous merchant**, oldid `6437126`, UTC `2012-10-18T18:30:22Z`, <https://runescape.wiki/w/Pompous_merchant?oldid=6437126> | Pompous Merchant release, level-1 behavior, XP, loot, failure damage, and tutorial context. |
| `W-DP` | Tier 5 | RuneScape Wiki, **Desert Phoenix**, oldid `6295341`, UTC `2012-09-25T17:19:30Z`, <https://runescape.wiki/w/Desert_Phoenix?oldid=6295341> | Desert Phoenix release, feather action, XP, and The Golem context. |
| `W-ELF` | Tier 5 | RuneScape Wiki, **Elf**, oldid `6555584`, UTC `2012-11-14T20:21:37Z`, <https://runescape.wiki/w/Elf?oldid=6555584> | Lletya elf level, XP, loot, and Mourning's End Part I gate. |
| `W-PMK` | Tier 5 | RuneScape Wiki, **Prifddinas**, oldid `6504482`, UTC `2012-10-30T18:39:51Z`, <https://runescape.wiki/w/Prifddinas?oldid=6504482> | Proof that Prifddinas was inaccessible before its announced early-2014 release. |
| `W-GS` | Tier 5 | RuneScape Wiki, **Gloves of silence**, oldid `6543982`, UTC `2012-11-08T23:42:26Z`, <https://runescape.wiki/w/Gloves_of_silence?oldid=6543982> | Gloves route, Hunter/Crafting levels, charges, degradation, and repair. |
| `W-DK` | Tier 5 | RuneScape Wiki, **Dark kebbit**, oldid `6016035`, UTC `2012-07-30T13:49:14Z`, <https://runescape.wiki/w/Dark_kebbit?oldid=6016035> | Falconry route and the Hunter level for Dark kebbit fur. |
| `W-RGE` | Tier 5 | RuneScape Wiki, **Rogue equipment**, oldid `6100896`, UTC `2012-08-17T07:46:03Z`, <https://runescape.wiki/w/Rogue_equipment?oldid=6100896> | Pre-EOC acquisition route and the absence of a documented outside-minigame XP bonus. |
| `W-AC` | Tier 5 | RuneScape Wiki, **Ardougne cloak 3**, oldid `6356969`, UTC `2012-10-06T15:42:33Z`, <https://runescape.wiki/w/Ardougne_cloak_3?oldid=6356969>; **Ardougne achievements**, oldid `6579397`, UTC `2012-11-18T22:07:06Z`, <https://runescape.wiki/w/Ardougne_achievements?oldid=6579397> | Achievement-diary route and period statement that the cloak improves pickpocketing. |
| `W-FEUD` | Tier 5 | RuneScape Wiki, **The Feud**, oldid `6542289`, UTC `2012-11-08T01:28:44Z`, <https://runescape.wiki/w/The_Feud?oldid=6542289> | Blackjack quest section, level gate, and quest reward path. |
| `W-MEP1` | Tier 5 | RuneScape Wiki, **Mourning's End Part I**, oldid `6579284`, UTC `2012-11-18T19:24:14Z`, <https://runescape.wiki/w/Mourning%27s_End_Part_I?oldid=6579284> | Elf-area quest gate. |
| `W-DTD` | Tier 5 | RuneScape Wiki, **Death to the Dorgeshuun**, oldid `6564288`, UTC `2012-11-16T21:26:08Z`, <https://runescape.wiki/w/Death_to_the_Dorgeshuun?oldid=6564288> | Dorgesh-Kaan access as a quest reward and H.A.M. gates. |
| `W-GD` | Tier 5 | RuneScape Wiki, **The Giant Dwarf**, resolved pre-cutoff oldid not needed for a separate numeric claim here; `W-TR` states the Trader’s release and location, and `W-T` states the Thieving quest column. | Giant Dwarf gate for Dwarf Traders and Keldagrim stalls. |
| `W-ROGUE` | Tier 5 | RuneScape Wiki, **Rogues' Den**, `W-RD`; **Rogue equipment**, `W-RGE` | Rogue's Den entrance and Flash Powder Factory route. |

### Cache pass actually performed

The new read-only helper `tools/OpenRs2CacheDefinitionSearch.java` and wrapper
`tools/query_openrs2_cache_definitions.sh` were added because the existing
cache tool only searched items. Both `C727` and `C742` were opened and queried
for NPC and object definitions; no cache files were modified.

Queries and results:

- Object `22681` and object `22697` were named `Chest` and had `Pick-lock` in
  both `C727` and `C742`; object `22683` was the opened chest definition. Object
  `7235` was `Wall safe` in both caches. This proves period client identities and
  options, not XP, loot weights, timers, or traps (`C727/C742`, definitions
  `22681`, `22697`, `22683`, and `7235`; `STD:67-69`).
- Stall definitions in both caches included object IDs `635` Tea, `4277` and
  `4705` Fish, `4278` Fur, `4706` and `4708` Vegetable, `4874` Crafting, `4875`
  Food, `4876` General, `4877` Magic, `4878` Scimitar, `6162` Gem, `6163`
  Bakery, `6164` Silver, `6166` Crafting, `17031` Crossbow, and `34382` through
  `34387` Silver/Silk/Baker/Gem/Spice/Fur. Where the definition exposed it, the
  action was `Steal-from` or `Steal from` (`C727/C742`, those object definition
  IDs). The definitions do not encode the period server-side guard assignment.
- NPC `14911` Pompous Merchant existed in both caches but exposed `Talk-to` and
  no `Pickpocket`; NPC `1911` Desert Phoenix existed but exposed `Grab-feather`,
  not `Pickpocket` (`C727/C742`, definitions `14911` and `1911`).
- NPC `13212` Monkey knife fighter exposed `Pickpocket` in both caches; NPCs
  `13195` and `13213` had no pickpocket option. NPCs `2364`, `2365`, and `2366`
  exposed `Pickpocket` in both caches, even though rev-742 returned null names
  for two of them. NPC `1905` Menaphite Thug exposed `Pickpocket`, `Lure`, and
  `Knock-Out`; NPC `1903` had no decoded definition in either queried cache
  (`C727/C742`, exact NPC IDs).
- Trader IDs `2109`, `2110`, `2123`, `2125`, `2126`, `8824`, and `8827` exposed
  `Pickpocket` in both caches. Some rev-742 definitions returned a null name,
  but the option was still present (`C727/C742`, exact NPC IDs). This is the
  cache proof for the Dwarf Trader era check.
- A name search for `Elf` returned no literal NPC name in either cache, so the
  exact-ID query for `2364-2366` was necessary. The name search being negative
  is not evidence that the elf NPCs were absent; the exact IDs and options are
  positive evidence (`C727/C742`, exact NPC IDs).
- A name search for `Pick-lock` does not work as an option search in the helper;
  the object-name query for `door` showed objects `2554-2559` named `Door` with
  `Open` and `Pick-lock` in both caches. This confirms that pick-lockable door
  definitions existed, but not the skill formula or XP (`C727/C742`, object
  definitions `2554-2559`).

The six dated archive hashes were also checked against `STD:85-100`. Only the
rev-727 and rev-742 definition sets were needed for the mechanic and era proof;
no claim below treats the intermediate archive hashes as a definition query.

## A. Pickpocketing

### A1-A2. Reconciled target roster

The pinned period table is the canonical roster for ordinary NPC
pickpocketing. It contains 23 standard rows, plus the separate Tower of Life
worker exception. Darkan has 22 enum rows, but one `BANDIT` row merges distinct
level-45, level-53, and level-55 period targets, and it adds Pompous Merchant
and Desert Phoenix. The game-main enum contains 16 rows, not the often-quoted
17: its last enum entry is Hero at `PickpocketTarget.kt:514-535`, and the enum
starts at `:22`; the extra period rows are not registered by that snapshot
(`G:PickpocketTarget.kt:11-21,22-535`; `D:PickPocketableNPC.java:31-185`; `W-T`).

The table below deliberately separates period values from emulator candidate
parameters. `GM r1/r99` is game-main’s private minimum/maximum chance pair;
`Darkan r1/r99` is Darkan’s pair. These are implementation leads, not proven
period probabilities. `Period stun` is the wiki’s seconds column. `GM ticks`
and `Darkan stun` are the emulator fields; neither proves an authentic tick
conversion. Loot is the period page’s possible-loot description, not an
invented probability table.

| Target | Period level; XP; loot; quest gate | Period failure damage; period stun | Candidate success parameters; emulator stun | Corroboration and status |
|---|---|---|---|---|
| Man/Woman | level `1`; `8` XP; `3 coins`; no quest | `10`; `5 seconds` | GM `180/240`; `8 ticks`; Darkan `177/240`; `4` | `W-T` table; `G:PickpocketTarget.kt:22-75`; `D:PickPocketableNPC.java:40-45`. Level/XP/loot/damage/stun are corroborated by the period table; exact chance and tick mapping are `source_blocked`. |
| Farmer | level `10`; `14.5` XP; `9 coins` and potato seeds; no quest | `10`; `5 seconds` | GM `150/240`; `8 ticks`; Darkan `155/240`; `4` | `W-T`; `G:76-96`; `D:47-52`. Wiki and both implementations agree on level/XP and the broad loot; chance, exact weights, and ticks are `source_blocked`. |
| Female H.A.M. member | level `15`; `18.5` XP; coins, tools, clothing, gems, clue, food, herbs, ore, and related H.A.M. finds; no quest | `10-30`; `4 seconds` | GM `135/240`; `7 ticks`; Darkan `135/240`; `3` | `W-T`; `G:97-158`; `D:54-59`. Parameters agree between emulators, but not with a period numeric roll source; exact loot weights and tick unit are `source_blocked`. |
| Male H.A.M. member | level `20`; `22.5` XP; broad H.A.M. loot; no quest | `10-30`; `4 seconds` | GM `117/240`; `7 ticks`; Darkan `135/240`; `3` | `W-T`; `G:159-220`; `D:61-66`. Chance parameter conflict is explicit; period success endpoints are `source_blocked`. |
| H.A.M. Guard | level `20`; `22.5` XP; male H.A.M. finds plus bronze, iron, steel, and silver H.A.M. keys; `Death to the Dorgeshuun` | `10-30`; `4 seconds` | GM absent; Darkan `135/240`; `3` | `W-T`; `D:68-73`; `W-DTD`. Darkan is the only local implementation; its chance and exact key weights are `source_blocked`. |
| Warrior woman / Al-Kharid Warrior | level `25`; `26` XP; `18 coins` and court summons; no quest | `20`; `5 seconds` | GM `100/240`; `8 ticks`; Darkan `125/240`; `5` | `W-T`; `G:221-235`; `D:75-80`. XP and loot are corroborated; chance/ticks are not. |
| Rogue | level `32`; `35.5` XP; `25-40 coins`, wine, air runes, poisoned iron dagger, lockpick, and egg; no quest | `20`; `5 seconds` | GM `74/240`; `8 ticks`; Darkan `115/240`; `4` | `W-T`; `G:236-255`; `D:82-87`. GM XP `36.5` is a conflict with both the wiki and Darkan; use `35.5` as the period value. Exact chance and loot weights are `source_blocked`. |
| Cave goblin | level `36`; `40` XP; coins, lamp/lantern/torch, tinderbox, swamp tar, cave-goblin foods, iron ore, and wire; `Death to the Dorgeshuun` | `10`; `5 seconds` | GM `72/240`; `8 ticks`; Darkan `100/240`; `4` | `W-T`; `G:256-287`; `D:89-94`; `W-DTD`. The implementations disagree on chance; period loot weights are `source_blocked`. |
| Master Farmer | level `38`; `43` XP; allotment, flower, and herb seeds; no quest | `30`; `5 seconds` | GM `90/240`; `8 ticks`; Darkan `90/240`; `4` | `W-T`; `G:288-345`; `D:96-101`. Chance endpoints happen to agree between implementations, but are still not independently proven. |
| Guard | level `40`; `46.5` XP; `30 coins`; no quest | `20`; `5 seconds` | GM `50/240`; `8 ticks`; Darkan `45/240`; `4` | `W-T`; `G:346-390`; `D:103-108`. GM XP `46.8` conflicts with the period table and Darkan; use `46.5`. |
| Fremennik Citizen | level `45`; `65` XP; `40 coins`; `The Fremennik Trials` | `20`; `5 seconds` | GM `65/240`; `8 ticks`; Darkan `35/240`; `4` | `W-T`; `G:391-416`; `D:110-115`. Quest and reward are corroborated; chance conflict remains. |
| Bearded Pollnivnian Bandit | level `45`; `65` XP; `40 coins`; no quest | `50`; `5 seconds` | GM absent; Darkan absent as a distinct row | `W-T`. Darkan’s level-55 `BANDIT` alias cannot close this row; exact NPC ID mapping and implementation parameters are `source_blocked`. |
| Desert Bandit | level `53`; `79.5` XP; `30 coins`, antipoison, and lockpick; no quest | `30`; `5 seconds` | GM `50/240`; `8 ticks`; Darkan absent as a distinct row | `W-T`; `G:417-434`; `D:131-136`. Darkan’s merged bandit row is not the period level-53 target; exact period chance is `source_blocked`. |
| Knight of Ardougne | level `55`; `84.3` XP; `50 coins` and court summons; no quest | `30`; `5 seconds` | GM `50/240`; `8 ticks`; Darkan `41/240`; `4` | `W-T`; `G:435-449`; `D:124-129`. Chance parameters conflict; XP and broad loot agree. |
| Pollnivnian Bandit | level `55`; `84.3` XP; `50 coins`; no quest | `50`; `5 seconds` | GM absent; Darkan merged `35/240`; `4` | `W-T`; `D:131-136`. Darkan’s IDs include period bandits but do not separate this row from other bandits; exact mapping and chance are `source_blocked`. |
| Yanille Watchman | level `65`; `137.5` XP; `60 coins` and bread; no quest | `30`; `5 seconds` | GM `15/160`; `8 ticks`; Darkan `17/156`; `4` | `W-T`; `G:450-465`; `D:138-143`. Period XP/loot agree; exact chance is unresolved. |
| Menaphite Thug | level `65`; `137.5` XP; `60 coins`; no quest for ordinary pickpocketing; The Feud is required for blackjack use | `50`; `5 seconds` | GM absent; Darkan `17/156`; `4` | `W-T`; `W-MT`; `D:138-143`. Darkan uses NPC `1905` in its ordinary enum, while its blackjack handlers use `1903`; `C727/C742` confirms `1905` has the option and `1903` is null. |
| Paladin | level `70`; `151.75` XP; `80 coins`, two chaos runes, and court summons; no quest | `30`; wiki stun blank | GM `50/150`; `8 ticks`; Darkan `17/150`; `4` | `W-T`; `G:466-481`; `D:145-150`. Authentic stun duration is `source_blocked`; emulator units and chance conflict with the blank period field. |
| Monkey knife fighter | level `70`; `150` XP per pickpocket, plus `20` XP for a successful knockout; coins, black knives, lobsters, and mithril/adamant/rune/dragon scimitars; `Do No Evil` | `60`; wiki stun blank | GM absent; Darkan `15/200`; `4` | `W-MKF`; `W-T`; `G:97-113` for the two-pick multi logic; `D:152-157`; `C727/C742` NPC `13212`. Darkan omits the separate `20` knockout XP and uses a different damage/stun candidate; exact ordinary pickpocket parameter is `source_blocked`. |
| Gnome | level `75`; `198.5` XP; `300 coins`, earth rune, gold ore, fire orb, swamp toad, king worm, and court summons; no quest | `10`; `5 seconds` | GM `8/120`; `8 ticks`; Darkan `13/120`; `4` | `W-T`; `G:482-513`; `D:159-164`. Chance conflict is explicit. |
| Hero | level `80`; `273.3` XP; `200-300 coins` and the listed runes/orbs/diamond/ore/wine/court summons; no quest | `40`; `6 seconds` | GM `6/100`; `10 ticks`; Darkan `13/120`; `5` | `W-T`; `G:514-535`; `D:166-171`. Darkan XP `275` conflicts with the period table; use `273.3`. |
| Elf, Lletya/Isafdar target | level `85`; `353` XP; `250-350 coins`, fire orb, gold ore, wine, death runes, cut diamonds, unicorn horn, dark wizard robe, and nature runes; `Mourning's End Part I` | `50`; `6 seconds` | GM absent; Darkan `6/98`; `10` | `W-T`; `W-ELF`; `W-MEP1`; `D:173-178`; `C727/C742` NPC `2364-2366`. This is not Prifddinas; the period page places the thievable target in Lletya. |
| Dwarf Trader | level `90`; `556.5` XP; `100-400 coins`, noted bars/ores, coal, level-3 clue scroll, and court summons; `The Giant Dwarf` | `10`; `5 seconds` | GM absent; Darkan `1/150`; `6` | `W-T`; `W-TR`; `D:180-185`; `C727/C742` Trader IDs. The era check is positive; Darkan’s exact chance is `source_blocked`. |

### Period special rows omitted or differently named by the emulators

| Target/action | Period value | Source tier and exact citation | Corroboration/conflict |
|---|---|---|---|
| Pompous Merchant | Release `31 January 2012`; level-1 man/woman-equivalent pickpocket; `8` XP; `3 coins`; failed attempt stuns for a few seconds and removes `10` life points; no quest gate to the action, but the NPC is introduced by the Troll Warzone tutorial | Tier 5 `W-PM`; Darkan candidate `D:PickPocketableNPC.java:33-38`; cache `C727/C742`, NPC `14911` | The pinned page proves pre-cutoff existence and values. Both caches show NPC `14911` but no `Pickpocket` option, while Darkan wires it as pickpocketable. Action-option conflict is `source_blocked`; do not ship the client interaction as cache-proven. Exact stun ticks are also `source_blocked`. |
| Desert Phoenix | Release `11 April 2005`; `26` XP for grabbing a Phoenix feather; loot is one Phoenix feather; associated quest `The Golem`; no period Thieving level is stated on the pinned page | Tier 5 `W-DP`; Darkan candidate `D:117-122`; cache `C727/C742`, NPC `1911` | Both caches show the NPC and `Grab-feather`, not `Pickpocket`; the period page describes a feather action, not a normal pocket. Darkan’s level-25 candidate, damage `20`, and stun `4` are `source_blocked`. Include only if the implementation models the distinct Grab-feather action. |
| Tower of Life workers | level `1`; `8` XP; triangle sandwich; workers Black-eye, Gummy, No fingers, and The Guns; no quest completion gate | Tier 5 `W-T`, text immediately after the standard table; corroborating quest context `W-Tower of Life`, oldid `6588693`, UTC `2012-11-19T21:10:36Z` | Neither emulator roster includes this exception. The period page explicitly says the workers can be pickpocketed before or after quest completion. |

### A3. Success formula

The independent emulator formulas are:

- game-main evaluates `level.interpolate(minChance, maxChance, 1, 99, 255)`;
  the target-specific `minChance`/`maxChance` values are in
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/thieving/pickpocketing/PickpocketTarget.kt:539-551`.
- Darkan passes its target `rate1`/`rate99` to `Utils.skillSuccess`, after aura,
  Ardougne cloak, and Gloves of Silence multipliers, at
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/thieving/PickPocketableNPC.java:199-207,281-291`.
  The helper implementation was not treated as period evidence.
- The pinned period page describes an observed linear relation of approximately
  `1.011%` success per Thieving level above the target requirement, with the
  same-level floor described as approximately `1.011%` (`W-T`, Pickpocketing
  prose). That prose does not state the server’s integer roll, endpoint pair, or
  whether it was measured with equipment/aura assumptions.

**Resolution:** no exact authentic formula is source-closed. The GM and Darkan
parameter pairs disagree on many rows and their same-level endpoint behavior
does not directly match the period prose. The defensible downstream contract is
`source_blocked` for the exact integer formula and target parameters. If a
temporary abstraction is unavoidable, the narrowest one is a monotone linear
function of the Thieving-level overshoot, clamped to the target’s usable range,
with the parameters explicitly labeled provisional; neither emulator formula
should be described as historical truth.

### A4. Multi-loot tiers

| Tier | Period rule | Roll probability | Corroboration and recommendation |
|---|---|---|---|
| Double | target base level + `10` Thieving and +`0` Agility | `source_blocked` | `W-T` gives the threshold. GM requires Thieving overshoot at least `10`, Agility overshoot at least `0`, and `world.random(7)==1` (`G:Pickpocketing.kt:97-113`). Darkan checks both arrays and uses `Utils.getRandomInclusive(50)<5` (`D:PickPocketAction.java:149-158`). |
| Triple | target base level +`20` Thieving and +`10` Agility | `source_blocked` | `W-T`; GM `G:97-113`; Darkan target arrays `D:PickPocketableNPC.java:35-185`. |
| Quadruple | target base level +`30` Thieving and +`20` Agility | `source_blocked` | `W-T`; GM `G:97-113`; Darkan `D:149-158`. |

The real tiers and both-stat gate are period-correlated; the probability is not.
GM’s `random(7)==1` and Darkan’s inclusive-`50` roll are conflicting emulator
leads. Recommend shipping the three thresholds and requiring both Thieving and
Agility overshoots, while leaving the roll probability `source_blocked`.

### A5. Era checks

| Candidate | Result | Exact evidence and conflict |
|---|---|---|
| Dwarf Trader, level `90`, `556.5` XP | **Pre-cutoff; include as a period target.** | `W-TR` says the Trader was released `9 September 2009`, is pickpocketable at level `90`, and awards `556.5` XP. `C727/C742` exact Trader IDs expose `Pickpocket`. Darkan’s row is therefore not post-EOC merely because game-main omitted it (`D:180-185`). |
| Pompous Merchant | **Pre-cutoff existence; client-option conflict.** | `W-PM` says release `31 January 2012`, `8` XP, and pickpocket behavior. `C727/C742` NPC `14911` exists but has no Pickpocket option; Darkan adds the interaction. Keep the row as a period behavior lead, but keep the exact cache interaction `source_blocked`. |
| Desert Phoenix | **Pre-cutoff, but not a normal pocket row.** | `W-DP` says release `11 April 2005`, `26` XP for stealing a feather; `C727/C742` NPC `1911` has `Grab-feather`, not Pickpocket. Darkan’s special row is directionally correct but its level/roll/stun fields are not period-proven (`D:117-122`). |
| Monkey knife fighter | **Pre-cutoff.** | `W-MKF` says release `1 December 2010`, requires `Do No Evil`, and gives `20` knockout plus `150` pickpocket XP. `C727/C742` NPC `13212` has Pickpocket and Punch. |
| Elf | **Pre-cutoff for Lletya/Isafdar only.** | `W-ELF` states level `85`, `353` XP, and Lletya; `W-MEP1` supplies the quest gate; `C727/C742` IDs `2364-2366` expose Pickpocket. Prifddinas is separately excluded below. |

## B. Stalls

### B1. Full period stall roster

The dedicated period table has 18 stall families, including Customs evidence
files, which neither emulator registers. Respawn values below are the period
table’s seconds, not emulator tick fields. Loot lists are possible item sets;
the page does not provide a probability distribution for most rows.

| Stall | Level; XP | Loot | Locations and quest gate | Respawn | Source tier, citation, corroboration |
|---|---|---|---|---|---|
| Vegetable | `2`; `10` | onion, cabbage, potato, tomato, garlic | Miscellania/Etceteria/Burthorpe; Fremennik Trials for Miscellania/Etceteria | `2 seconds`; `0.5 seconds` Burthorpe | Tier 5 `W-S`; GM `G:StallTarget.kt:22-39`; Darkan `D:Thieving.java:51-54`. |
| Baker’s | `5`; `16` | cake, bread, chocolate slice | East Ardougne/Keldagrim/Burthorpe; Giant Dwarf for Keldagrim | `2.5 seconds` | `W-S`; GM `G:40-59`; Darkan `D:55-58`. |
| Crafting | `5`; `16` | chisel, ring mould, necklace mould | Ape Atoll/Keldagrim/Burthorpe; Monkey Madness for Ape Atoll, Giant Dwarf for Keldagrim | `7 seconds` | `W-S`; GM `G:60-80`; Darkan `D:59-61`. |
| Monkey Food | `5`; `16` | banana | Ape Atoll; Monkey Madness | `7 seconds` | `W-S`; GM `G:81-97`; Darkan `D:63-64`. GM also includes monkey nuts, banana stew, and monkey bar, which is an implementation conflict with the period table. |
| Monkey general | `5`; `16` | pot, hammer, tinderbox | Ape Atoll; Monkey Madness | `7 seconds` | `W-S`; GM `G:98-113`; Darkan `D:65-66`. |
| Tea | `5`; `16` | cup of tea | Varrock; none | `7 seconds` | `W-S`; GM `G:114-126`; Darkan `D:67-68`. |
| Silk | `20`; `24` | silk | East Ardougne; none | `8 seconds` | `W-S`; GM `G:127-139`; Darkan `D:69-70`. |
| Wine | `22`; `27` | jug of water, jug of wine, grapes, jug, bottle of wine | Draynor/Burthorpe; none | `16 seconds` | `W-S`; GM `G:140-158`; Darkan `D:71-73`. |
| Seed | `27`; `10` | various seeds | Draynor/Burthorpe; none | `11 seconds` | `W-S`; GM `G:159-189`; Darkan `D:74-75`. |
| Fur | `35`; `36` | fur, grey wolf fur | East Ardougne/Rellekka; Fremennik Trials for Rellekka | `15 seconds` | `W-S`; GM `G:190-206`; Darkan `D:77-79`. |
| Fish | `42`; `42` | raw salmon, raw tuna, raw lobster | Rellekka/Miscellania/Etceteria; Fremennik Trials | `16 seconds` | `W-S`; GM `G:207-227`; Darkan `D:80-82`. |
| Crossbow | `49`; `52` | bronze bolts (3), bronze limbs, wooden stock | Keldagrim; Giant Dwarf | `11 seconds` | `W-S`; GM `G:228-243`; Darkan `D:83-84`. |
| Silver | `50`; `54` | silver ore | East Ardougne/Keldagrim; Giant Dwarf for Keldagrim | `30 seconds` | `W-S`; GM `G:266-282`; Darkan `D:85-87`. |
| Customs evidence files | `63`; `75` | rune scimitar, uncut diamond/ruby/emerald/sapphire, sharks, mithril/gold/iron bars, pirate clothing, steel/iron/bronze weapons, clue scroll, `300 coins` | Rock Island Prison; Rocking Out | `30-60 seconds` | Tier 5 `W-S` only. No Darkan or GM row is present, so exact object IDs and server loot weights are `source_blocked`. |
| Spice | `65`; `81` | spice | East Ardougne; none | `80 seconds` | `W-S`; GM `G:283-295`; Darkan `D:88-89`. |
| Magic | `65`; `100` | air, earth, fire, water, or law runes | Ape Atoll; Monkey Madness | `80 seconds` | `W-S`; GM `G:296-311`; Darkan `D:90-91`. |
| Scimitar | `65`; `100` | iron scimitar | Ape Atoll; Monkey Madness | `80 seconds` | `W-S`; GM `G:312-326`; Darkan `D:92-93`. GM’s `160` XP conflicts with both the period page and Darkan; use `100`. |
| Gem | `75`; `160` | uncut sapphire, emerald, ruby, diamond | East Ardougne/Keldagrim; Giant Dwarf for Keldagrim | `3 minutes` | `W-S`; GM `G:327-347`; Darkan `D:94-95`. Darkan’s `16` XP is a clear conflict/bug; use `160`. |

The period page adds a location-specific note: in Keldagrim the gem and silver
stalls respawn twice as fast and give half XP, while the bakery stall respawns
twice as slowly and gives twice XP (`W-S`). The exact object-to-location mapping
and whether every Keldagrim variant uses the note are `source_blocked`; do not
derive them from Darkan’s `seconds * 2` conversion (`D:105-113,154-185`).

### B2. Who catches the player, and how often?

| Question | Established value | Citation and corroboration |
|---|---|---|
| Is there a per-attempt failure roll? | No authentic numeric per-attempt caught probability was found. The period article says nearby guards or the stall owner may see the player, attack, or prevent the theft; it does not state a roll. | `W-T`, Stalls prose. GM has no chance roll and only checks guards before success (`G:Stalls.kt:23-35,59-74`); Darkan always awards loot/XP and then checks guards (`D:Thieving.java:154-186`). This establishes emulator omission, not a period probability. |
| Can the stall owner catch independently? | **Yes.** The period text explicitly names the stall owner as an independent observer. It also says the owner shouts for guards when the player buys/sells from that stall type during a cooldown after theft. | `W-T`, Stalls prose. Neither emulator models the owner: GM only registers guard NPCs (`G:thieving.plugin.kts:40-44`); Darkan only calls `checkGuards()` (`D:Thieving.java:180-204`). |
| What is the actual owner/guard chance? | `source_blocked`. No pinned period page or cache definition supplies a numeric probability. | `W-T`; `C727/C742` object/NPC definitions contain names/options only, and not world-spawn visibility rules (`STD:67-69`). |
| What are actual guard assignments per stall? | `source_blocked`. Cache object definitions prove the stalls and NPC definitions prove candidate NPC options, but cache definitions do not encode map spawn relationships. | `C727/C742`; GM attaches only Market Guard `2236` to Wine and Seed (`G:StallTarget.kt:140-188`); Darkan recognizes guard IDs `{32,21,2256,2132,2236,23,8813}` and searches within `4` tiles with line of sight (`D:Thieving.java:148-152,190-204`). These are implementation candidates, not a period assignment list. |

### B3. Narrowest defensible abstraction

Use a stall visibility/catcher predicate with two independently modeled sources:

1. a nearby, line-of-sight guard where the world has a proven guard assignment;
2. a stall-owner observer where the world has a proven owner/side/visibility
   relation.

Do not add a hidden per-attempt random probability. If the current world model
cannot represent owners or line of sight, leave catching `source_blocked` rather
than making every stall safe or inventing one global chance. The evidence for
guards and owners is `W-T`; the evidence against the two emulator designs being
complete is `G:23-35,59-74` and `D:154-204`.

## C. Chests

### C1-C2. Period roster and values

| Chest | Level; XP | Loot | Respawn | Trap damage / trap status | Citation and corroboration |
|---|---|---|---|---|---|
| 10-coin chest | `13`; `7` | `10 coins` | `7 seconds` | The period table does not say this chest has a trap | `W-T`, Chests table. |
| Ogre coffin | `20`; `27` | various; article points to Ogre coffin page | `20 seconds` | Exact trap behavior not established in this pass | `W-T`. |
| Nature-rune chest | `28`; `25` | `3 coins` and nature runes | `12 seconds` | The table says to search for traps generally, but gives no chest-specific damage | `W-T`; Ardougne task text in `W-AC` confirms searching this chest for traps at level `28`. |
| Pirates' Hideout | `39`; XP shown as `?` | small amounts of coins and runes | `15 seconds` | `source_blocked` | `W-T`. The question-mark XP is the period source’s unresolved value, not a value to guess. |
| 50-coin chest | `43`; `125` | `50 coins` | `55 seconds` | `source_blocked` | `W-T`. |
| Arrowtip chest | `47`; `150` | `5 steel arrowtips` | `210 seconds` | `source_blocked` | `W-T`. |
| Dorgesh-Kaan Average Chest | `52`; `200` | see separate average-chest article | `210 seconds` | `source_blocked` | `W-T`; `W-C` disambiguation. The resolver found no pre-cutoff standalone Average Chest revision; no exact loot or trap damage is established. |
| Blood-rune chest | `59`; `250` | `500 coins` and `2 blood runes` | `210 seconds` | `source_blocked` | `W-T`. |
| Paladin chests, two | `72`; `500` | `1,000 coins`, raw sharks, adamant ores, uncut sapphire | `400 seconds` | `source_blocked` | `W-T`. |
| Dorgesh-Kaan Rich Chest / Reinforced chest | `78`; `650` | uncut sapphire/emerald/ruby/diamond/opal/jade/red topaz, bullseye lantern, mining helmet, frog-leather body/chaps, iron bar, light orb, empty light orb, charms | `400 seconds` | `source_blocked` | `W-T`; `W-C` oldid `6298402` explicitly confirms level `78` and `650` XP and enumerates the possible loot. |

The cache corroboration is exact: objects `22697` and `22681` are `Chest` with
`Pick-lock` in both `C727` and `C742`, and `22683` is the opened state. Darkan
maps `22697` to level `52`, XP `200`, respawn `210`, and `22681` to level `78`,
XP `650`, respawn `300`, at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/thieving/Thieving.java:262-292`.
The level/XP agreement is good; Darkan’s rich-chest `300`-second respawn
conflicts with the period table’s `400` seconds and should not be used.

### C3. Quest gate

Both Dorgesh-Kaan chest rows require access to Dorgesh-Kaan. The period quest
page lists Dorgesh-Kaan access among the rewards of **Death to the Dorgeshuun**
(`W-DTD`, Rewards section), while `W-T` places the chests in Dorgesh-Kaan and
the chest disambiguation `W-C` identifies both types there. Therefore the
defensible gate is `Death to the Dorgeshuun` for both Dorgesh chest families.

### Trap conclusion

Darkan’s `checkTrapsChest()` awards XP, changes the object, and gives loot with
no trap roll or damage at `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/thieving/Thieving.java:206-229`.
The period page says some chests have traps and describes the “Search for traps
Chest” action (`W-T`, Chests prose), but no source opened here states a
Dorgesh-specific damage range or caught probability. Exact trap behavior for
the two Dorgesh chests is therefore `source_blocked`; do not copy Darkan’s
trap-free behavior and do not invent a damage number.

## D. Pickable doors

### D1. Period roster and XP

The period Thieving table supplies authentic level/XP values for the skill-door
families below. A dash is a period table dash, not an invitation to fill a
value.

| Door/family | Level; XP | Lockpick requirement | Citation and cache cross-check |
|---|---|---|---|
| Cell in Port Sarim Jail | `-`; `-` | No | `W-T`, Pickable doors table. |
| Door to 10-coin chest | `1`; `3.5` | No | `W-T`; cache does not identify the world location from definition alone. |
| Door to Nature-rune chest | `14`; `15` | No | `W-T`; `W-AC` identifies the related Ardougne chest location. |
| Ardougne house door | `14`; `15` | No | `W-T`. |
| H.A.M. trapdoor | `15`; `4` | No | `W-T`; `W-DTD` describes the H.A.M. trapdoor context. |
| Axe hut door | `32`; `25` | Yes | `W-T`. |
| Ardougne sewer gate | `32`; `25` | No | `W-T`. |
| Pirates' Hideout | `39`; `35` | No | `W-T`. |
| Chaos druid tower | `46`; `37.5` | No | `W-T`; Darkan’s Ardougne source registers object `2554` separately for the tower, but not the historical Thieving formula (`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/world/areas/ardougne/Ardougne.java:291-295`). |
| Paladin door | `61`; `50` | No | `W-T`. |
| Yanille dungeon door | `82`; `50` | Yes | `W-T`; `W-AC` confirms the Yanille dungeon door is an achievement-diary task. |

The cache layer independently proves that pick-lockable door definitions existed:
objects `2554-2559` are named `Door` and expose `Open`/`Pick-lock` in both
`C727` and `C742`. It does not map every period table row to an object ID or
server script.

### D2. Formula decision

**Do not cut doors.** The period roster and XP values are source-backed and the
cache proves the interaction existed. The exact success formula is
`source_blocked`: Darkan’s `pickDoor()` uses a `numbFingers` counter, a random
ratio, combat-dependent thresholds `50`/`40`, and flat Gloves/Cape bonuses
`12`/`15` at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/thieving/Thieving.java:231-256`.
The verification standard explicitly identifies those details as unsupported
emulator invention (`STD:51-59`). Darkan’s handler also does not award the
period XP values (`D:231-247`). Preserve the period door roster and XP contract,
but mark the per-attempt formula, failure side effects, and exact object mapping
`source_blocked` until a period server/client script or independent historical
source closes them.

## E. Wall safes, Rogue's Den

| Value | Period result | Candidate implementation and corroboration |
|---|---|---|
| Required Thieving level | **`25`** | `W-WS` says four Rogue’s Den safes require level `25`; `W-T` Other table also says Wall Safe level `25`. GM and Darkan both use level `50` (`G:StallTarget.kt:244-265`; `D:WallSafe.kt:16-24`), so `50` is rejected as a local implementation error. |
| Success XP | **`70`** | `W-WS`, `W-RD`, and both emulator rows agree on `70` (`G:244-265`; `D:16-18,91-94`). |
| Stethoscope | Raises success rate; sold by Martin Thwait | `W-WS` and `W-RD`; Darkan has item `5560` and two candidate rolls (`D:30-37`). Exact period parameters are `source_blocked`. |
| Failure trap | Trap springs and deals `20-60` life points | `W-WS` states `20-60`; Darkan uses `20..60` (`D:22-23,84-90`); GM uses `20..60` (`G:thieving.plugin.kts:84-94`). This is independently corroborated and can be used. |
| Loot | Period sources conflict: `W-WS` lists 20 coins, 40 coins, sapphire, emerald, ruby, diamond; `W-RD` lists gems sapphire through diamond and coins `10`, `20`, `40`, `50`; `W-T` lists coins `10`, `20`, `30`, `40` and sapphire through ruby | Darkan has coins `10`, `20`, `40` and sapphire/emerald/ruby (`D:39-48`); GM has a `128`-slot table with coins `10`, `20`, `40` and gems including diamond (`G:244-265`). The broad union is historically plausible, but exact period weights and the contradictory coin list are `source_blocked`. |
| Reachability | Reachable from the Rogues’ Den trapdoor without completing the Flash Powder Factory/maze activity | `W-RD` says the trapdoor in the Pick and Lute leads to the Den and separately says the Flash Powder Factory requires Thieving `75`, Agility `75`, and Herblore `50`; it places four wall safes in the center. The safe is therefore not gated by completing that activity. |

**Recommendation:** retain wall safes, set the required level to `25`, XP to
`70`, and failure damage to `20-60`. Keep the exact success roll and loot
weights `source_blocked`; use a source-documented broad loot set only if the
downstream contract can tolerate the `W-T`/`W-WS`/`W-RD` conflict.

## F. Blackjacking

### F1-F3. Targets and action loop

| Target/action | Level; XP; loot | Knockout and failure behavior | Citation and local conflict |
|---|---|---|---|
| Bearded Pollnivnian Bandit | level `45`; `65` XP per ordinary pickpocket; `40 coins` | Blackjacking is available after The Feud and the target is one of the period bandit tiers; exact knockout XP/failure damage for this tier is not separately stated | `W-T` target table; `W-BJ`; exact blackjacking per-target server formula `source_blocked`. |
| Pollnivnian Bandit | level `55`; `84.3` XP per ordinary pickpocket; `50 coins` | Same gate; exact knockout XP/failure damage for this tier is not separately stated | `W-T`; `W-BJ`. This is the bandit half of the blackjack meta missing from Darkan’s dedicated handler. |
| Menaphite Thug | level `65`; `137.5` XP per pickpocket; `60 coins`; `10` Thieving XP per successful knockout | Failed knockout deals `40` life points and the thug attacks; a successful knockout permits two pickpockets; failed ordinary pickpocket costs `50` life points in the period description | `W-MT`; `W-BJ`. Darkan’s `LootThug` gives `137.5` XP and `60` coins, and its knockout freezes NPC `1903` for `10` seconds (`D:Blackjacking.java:11-21`; `D:Knock-Out.kt:97-135`; `D:LootThug.java:39-66`). Its failed knockout attack behavior is corroborated, but Darkan does not apply the period `40` damage. |
| Monkey knife fighter | level `70`; `20` knockout XP and `150` pickpocket XP; coins `1-50`, black knives, lobsters, and scimitars | Must punch while wearing a gorilla greegree; two pickpockets per knockout; failure or conscious pickpocket causes `60` damage and stun | `W-MKF`; `W-T`; Darkan ordinary pickpocket row `D:152-157` omits the `20` knockout XP and uses `10` candidate stun damage. |

**How many picks?** For Pollnivnian bandits and Menaphite Thugs, the pinned
blackjacking page states two pickpockets per knockout and describes the
“Double Double Hit” loop (`W-BJ`). The Menaphite page independently says to
pickpocket twice and gives a `3.6-second` cycle (`W-MT`). The Monkey knife
fighter page independently says the maximum is two (`W-MKF`). The correct
period contract is therefore **two pickpockets per ordinary knockout**. The
period sources do not establish Darkan’s exact `10`-second freeze, so that timer
is a Darkan lead, not a closed historical value.

**Failed knockout:** the period Menaphite page says the player takes `40` life
points immediately and the thug begins attacking; the period blackjack page
says a failed knockout can be attacked and that the player should immediately
retry or pickpocket. Darkan’s failure branch force-talks and attacks but applies
no hit (`D:Knock-Out.kt:130-135`). Use the attack side effect; the missing
damage in Darkan is a fix lead, while the exact bandit-tier damage remains
`source_blocked`.

### F4. Blackjack, blackjack variants, and cosh items

The pre-cutoff item search in `C742` returned Oak-blackjack `4599`,
Willow-blackjack `4600` and `4612`, Oak offensive/defensive `6408-6411`,
Willow offensive/defensive `6412-6415`, Maple standard/offensive/defensive
`6416-6421`, and Rubber blackjack `18644`. The item definitions expose `Wield`
where the wieldable form is present (`C742`, exact item IDs). The pinned item
pages supply the period stats and routes:

| Item family | Period stats and gate | Acquisition | Citation |
|---|---|---|---|
| Oak blackjack, `4599` | `+2` Strength; attack speed `6`; no wielding level | Complete the blackjack section of Rogue Trader; also given by Ali the Operator during The Feud | Tier 5 **Oak-blackjack**, oldid `6359039`, UTC `2012-10-06T21:05:40Z`; `W-FEUD`; cache `C742` item `4599`. |
| Willow blackjack, `4600`/`4612` | `+8` Strength; attack speed `6`; no wielding level | Complete Rogue Trader; buy from Blackjack seller in Pollnivneach; also The Feud reward | Tier 5 **Willow-blackjack**, oldid `6459490`, UTC `2012-10-23T14:43:22Z`; `W-FEUD`; cache `C742` items `4600`, `4612`. |
| Maple blackjack, `6416` | `+20` Strength; attack speed `6`; Thieving level `30` to wield | Start The Feud by talking to Ali Morrisane; the blackjack page also states The Feud is required to use blackjacks | Tier 5 **Maple blackjack**, oldid `6269347`, UTC `2012-09-20T01:13:00Z`; `W-BJ`; `W-FEUD`; cache `C742` item `6416`. |
| Offensive/defensive variants, `6408-6415` and `6418-6421` | Same family behavior; offensive and defensive variants raise Strength plus their respective crush bonus. Exact individual bonus rows were not needed for Thieving and are not repeated here without a separate item-row citation. | Purchased through the same Rogue Trader/Ali Morrisane route, then switched through the Pollnivneach blackjack seller | `W-BJ`; cache `C742`, exact item IDs. Exact per-variant combat stat rows are `source_blocked` in this dossier. |
| Rubber blackjack, `18644` | `0` Strength; attack speed `6`; training-only cosh | Dodgy Derek’s Dirty Deals in the Thieves’ Guild for `1 coin` after The Feud blackjack section and two capers; also obtainable from the advanced trainer | Tier 5 **Rubber blackjack**, oldid `5907646`, UTC `2012-07-08T12:10:19Z`; `W-FEUD`; cache `C742` item `18644`; Darkan requires `18644` for training NPCs (`D:Knock-Out.kt:35-51`). |

Blackjacks are not a general NPC pickpocket shortcut: `W-BJ` says The Feud
must be completed before luring/knocking out Villagers, Bandits, or Menaphite
Thugs, and the player must meet the target’s Thieving level. The exact Darkan
NPC ID `1903` is not present in the queried client definitions; `1905` is the
cache-backed Menaphite Thug with all relevant options. This ID mismatch is an
implementation conflict, not permission to substitute a modern NPC.

## G. Bonus equipment

### G1. Gloves of Silence

| Value | Established result | Citation and status |
|---|---|---|
| Success bonus | The period page only says the gloves increase pickpocket success; it does not state a numeric multiplier. GM uses `1.05`; Darkan adds `0.05` to its multiplier (`G:Pickpocketing.kt:62-68`; `D:PickPocketableNPC.java:281-284`). Exact period bonus is `source_blocked`. |
| Charges | New gloves are destroyed after `62` failures from new; blackjacking wears them on every action, successful or not | `W-GS`; Darkan candidate `MAX_GLOVES_OF_SILENCE_CHARGES = 62` and degradation logic at `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/items/GlovesOfSilence.kt:11-16,77-91`. |
| Wear requirement | Hunter level `54` | `W-GS`; Darkan `GlovesOfSilence.kt:37-43`. |
| Acquisition | Catch Dark kebbits by Falconry at Hunter level `57`, obtain two Dark kebbit furs, and pay `600 coins` at the Fancy Clothes Store in south-east Varrock; the store route is not a quest gate | `W-GS`; `W-DK`; `W` Fancy Clothes Store, oldid `6392978`, UTC `2012-10-13T04:00:46Z`. |
| Repair | One Dark kebbit fur, needle, thread, and knife; Crafting level `64`; one reel of thread is consumed | `W-GS`; Darkan `GlovesOfSilence.kt:46-69`. |
| Repo reachability | The existing Hunter data has `Catch dark kebbit`, Falconry, level `57`, output Dark kebbit fur, source item `10115` | `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/hunter_data.py:558-572`. This confirms the acquisition source is reachable through the implemented Hunter family, subject to normal runtime integration. |

### G2. Rogue outfit

The outfit is **not** proven to be Rogues’ Den maze-only. The period Rogue
equipment page says the pieces were formerly random rewards from the historical
Rogues’ Den activity, but by the pinned revision they are obtained in the
**Flash Powder Factory** (`W-RGE`). The Rogues’ Den page separately states that
the Factory requires Thieving `75`, Agility `75`, and Herblore `50`, while the
wall safes are directly in the Den (`W-RD`). Therefore:

- acquisition route: Flash Powder Factory, not a required completed maze;
- the project’s unimplemented Factory still makes the outfit unreachable in the
  current scope;
- Darkan’s equipment IDs `21482` hat, `21480` chest, `21481` legs, and `21483`
  boots and its `totalXp *= 1.025` are local leads at
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/thieving/PickPocketAction.java:115-145`;
- the pinned Rogue equipment page does not state an outside-minigame Thieving
  XP bonus. The exact `2.5%` bonus is therefore `source_blocked`; do not ship it
  as an authenticated value.

### G3. Ardougne cloak

The period source establishes the route but not Darkan’s numeric multiplier.
Ardougne cloak 3 is the reward for completing easy, medium, and hard Ardougne
Tasks, and the hard-task reward says it gives a better chance at stealing chests
and pickpocketing anywhere (`W-AC`). Darkan’s `+0.1` multiplier is at
`PickPocketableNPC.java:281-291` and `Knock-Out.kt:13-18`; no pinned period page
states `+0.1`. The exact numeric bonus is `source_blocked`. The acquisition is
achievement-diary-only and therefore unreachable unless the diary reward is
implemented.

## H. Quest gates

This is the consolidated gate contract; “none” means the period table or page
explicitly gives no quest requirement for the action, not that the location is
globally reachable without any quest.

| Family/target | Quest gate |
|---|---|
| Ordinary Man/Woman, Farmer, Female/Male H.A.M. member, Warrior, Rogue, Master Farmer, Guard, Desert Bandit, Knight, Pollnivnian Bandit, Yanille Watchman, Menaphite Thug, Paladin, Gnome, Hero | None stated in the period Thieving table (`W-T`). |
| H.A.M. Guard and Cave goblin | Death to the Dorgeshuun (`W-T`; `W-DTD`). |
| Fremennik Citizen | The Fremennik Trials (`W-T`). |
| Bearded Pollnivnian Bandit | None for ordinary pickpocketing (`W-T`); The Feud is required for blackjack use (`W-BJ`, `W-FEUD`). |
| Elf in Lletya | Mourning’s End Part I (`W-T`, `W-ELF`, `W-MEP1`). |
| Dwarf Trader | The Giant Dwarf (`W-T`, `W-TR`). |
| Pompous Merchant | No action gate stated; introduced by the Troll Warzone tutorial (`W-PM`). |
| Desert Phoenix | The Golem is the associated quest requiring the feather, but the pinned page does not state that quest completion gates the feather action (`W-DP`). |
| Monkey knife fighter | Do No Evil; the player also needs a gorilla greegree and must wield it (`W-MKF`, `W-T`). |
| Blackjack use on Villagers, Bandits, Menaphite Thugs | Complete The Feud; blackjack acquisition uses the Rogue Trader activity section and the item-specific route (`W-BJ`, `W-FEUD`). |
| Ape Atoll stalls | Monkey Madness for the Ape Atoll stalls (`W-S`). |
| Rellekka/Miscellania/Etceteria stalls | The Fremennik Trials for the named Fremennik locations (`W-S`). |
| Keldagrim stalls | The Giant Dwarf (`W-S`). |
| Customs evidence files | Rocking Out (`W-S`). |
| Dorgesh-Kaan Average and Rich chests | Death to the Dorgeshuun for access to Dorgesh-Kaan (`W-C`, `W-DTD`). |
| Other period chests | No quest gate is stated in the period Thieving table; location access can still carry separate area requirements (`W-T`). |
| Pickable doors | No quest gate is stated in the period Pickable doors table; location access can still carry separate area requirements (`W-T`). |
| Rogue’s Den wall safes | No maze completion gate; the Rogues’ Den entrance is the Pick and Lute trapdoor (`W-RD`). |
| Rogue outfit | Flash Powder Factory route; the Factory itself requires Thieving `75`, Agility `75`, and Herblore `50` in the period page (`W-RD`, `W-RGE`). |
| Gloves of Silence | No quest; Hunter/Falconry and Fancy Clothes Store route (`W-GS`, `W-DK`). |
| Ardougne cloak 3 | Ardougne Tasks, easy through hard (`W-AC`). |

## Conflicts

1. **Roster count:** the requested GM count is 17, but the opened enum has 16
   entries. Darkan has 22 enum rows, while the period standard table has 23
   standard rows plus Tower of Life workers. Resolution: use the period table;
   treat Darkan’s merged bandit row and special rows as aliases/extra actions,
   not as proof of a smaller canonical roster (`G:PickpocketTarget.kt:11-535`;
   `D:PickPocketableNPC.java:31-185`; `W-T`).
2. **Success endpoints/formula:** GM uses interpolation with target-specific
   `minChance`/`maxChance`; Darkan uses `Utils.skillSuccess` with different
   endpoints on many rows. The period page gives only an approximate observed
   `1.011%`-per-level relation, not the integer implementation. Resolution:
   formula and exact endpoint data remain `source_blocked`; do not select an
   emulator formula as authentic.
3. **Multi-loot probability:** GM’s gate is approximately a one-in-seven roll
   (`random(7)==1`), while Darkan’s inclusive random condition is approximately
   five successes in 51 values. The period source corroborates thresholds and
   both-stat overshoot but gives no probability. Resolution: thresholds proven,
   roll probability `source_blocked` (`G:97-113`; `D:149-158`; `W-T`).
4. **Per-target chance, damage, and stun units:** period damage/stun seconds
   frequently differ from GM and Darkan constants; Paladin and Monkey rows have
   blank period stun values, and special rows use different actions. Resolution:
   period damage/stun seconds are the only shipped historical values; emulator
   tick fields and exact tick conversion remain `source_blocked` (`W-T`; `G`; `D`).
5. **Darkan Hero XP:** Darkan has `275`, GM has `273.3`, and the period table
   has `273.3`. Resolution: `273.3` (`W-T`; `G:514-535`; `D:166-171`).
6. **Darkan Rogue XP:** GM has `36.5`, while Darkan and the period table have
   `35.5`. Resolution: `35.5` (`W-T`; `G:236-255`; `D:82-87`).
7. **Darkan Guard XP:** GM has `46.8`, while Darkan and the period table have
   `46.5`. Resolution: `46.5` (`W-T`; `G:346-390`; `D:103-108`).
8. **Darkan Scimitar stall XP:** Darkan and the period table have `100`; GM
   has `160`. Resolution: `100` (`W-S`; `G:312-326`; `D:92-93`).
9. **Darkan Gem stall XP:** Darkan has `16`; GM and the period table have `160`.
   Resolution: `160` and treat Darkan’s `16` as a bug (`W-S`; `G:327-347`;
   `D:94-95`).
10. **Stall loot:** GM’s Monkey Food table includes items beyond the period
    table; exact period weights are not in the wiki. Resolution: preserve only
    the period item set until independent weights are found (`W-S`; `G:81-97`).
11. **Stall guard model:** GM only checks configured guards within line of sight
    and eight tiles; Darkan checks a broader ID set within four tiles; the period
    text names both guards and owners. Resolution: model both catcher classes;
    exact assignments and chance are `source_blocked` (`W-T`; `G:59-74`;
    `D:148-204`).
12. **Stall timers:** the period table reports seconds; GM stores ticks and
    Darkan multiplies a `seconds` field by `2`. Resolution: use period seconds
    in the audit; do not infer tick conversion from either emulator (`W-S`;
    `G:StallTarget.kt:11-20`; `D:Thieving.java:97-113,183`).
13. **Chest respawn:** Dorgesh Rich is `400 seconds` in the period table but
    Darkan uses `300`; resolution `400` (`W-T`; `D:275-290`).
14. **Chest traps:** Darkan’s method is trap-free; the period page says some
    chests have traps. Exact Dorgesh damage/roll is absent. Resolution:
    `source_blocked`, never inherit the trap-free implementation (`STD:51-59`;
    `W-T`; `D:206-229`).
15. **Doors:** period XP is documented, but Darkan’s formula includes
    `numbFingers` and flat `+12/+15` bonuses absent from period sources.
    Resolution: retain door roster/XP, block formula and unsupported bonuses
    (`W-T`; `D:231-256`; `STD:51-59`).
16. **Wall-safe level:** period sources say `25`; both emulators use `50`.
    Resolution: `25` (`W-T`; `W-WS`; `G:244-265`; `D:16-24`).
17. **Wall-safe loot:** `W-T`, `W-WS`, and `W-RD` disagree on coin quantities
    and whether diamond is included. Resolution: broad period union only if an
    abstraction is required; exact set/weights `source_blocked` (`W-T`; `W-WS`;
    `W-RD`; `G:244-265`; `D:39-48`).
18. **Blackjack NPC ID:** Darkan handlers use `1903`, but both queried caches
    expose Menaphite Thug pickpocket/lure/knockout options on `1905` and return no
    decoded definition for `1903`. Resolution: use a cache-backed ID only after
    the world’s NPC mapping is established; do not assume `1903` is period-valid
    (`C727/C742`; `D:Blackjacking.java:11-47`; `D:Knock-Out.kt:97-135`).
19. **Blackjack freeze:** Darkan freezes for `10` seconds; period pages close
    the two-pick loop but do not state this server freeze duration. Resolution:
    two picks proven, exact freeze `source_blocked` (`W-BJ`; `W-MT`; `D:Knock-Out.kt:119-129`).
20. **Gloves of Silence bonus:** GM’s `1.05` and Darkan’s `+0.05` agree with
    each other but the pinned page only says “increase success.” Resolution:
    exact numeric bonus `source_blocked`; charges and route are proven
    (`W-GS`; `G:62-68`; `D:281-284`).
21. **Rogue outfit:** the user-suspected maze-only route conflicts with the
    period page, which says the current route is Flash Powder Factory. Resolution:
    route is Factory; Factory remains outside the current shipped scope, and the
    outside-minigame `2.5%` XP bonus is `source_blocked` (`W-RGE`; `W-RD`;
    `D:115-145`).
22. **Ardougne cloak numeric bonus:** period pages establish better success and
    the diary route but not Darkan’s `+0.1`. Resolution: route proven, number
    `source_blocked` (`W-AC`; `D:PickPocketableNPC.java:281-291`).
23. **Dedicated stall-page location coverage:** `W-S` independently confirms
    the stall level/XP/loot/respawn rows but presents a narrower location table
    than the broader `W-T` Thieving table. For example, `W-S` lists Vegetable
    stalls only at Miscellania/Etceteria while `W-T` also lists Burthorpe, and
    `W-S` lists Wine and Seed only at Draynor while `W-T` also lists Burthorpe.
    Resolution: use `W-T` for the broader location and quest-gate roster, while
    retaining `W-S` as corroboration for the core stall values; do not infer
    that the narrower dedicated-page snapshot disproves the broader table.

## source_blocked

The following are the exact unresolved values, with the missing evidence that
would close each one:

- Exact pickpocket success formula, integer roll, and target-specific authentic
  endpoints. Missing: a period server script, a period client script that
  exposes the roll, or a dated empirical source with enough calibration points.
  The wiki’s approximate `1.011%` prose is not enough to choose GM or Darkan.
- Exact loot weights and quantity rolls for every ordinary pickpocket target.
  Missing: period drop tables or a dated server implementation independently
  corroborated by the period pages. The Darkan JSON files are implementation
  candidates only (`data/npcs/drops/pickpocketing/`), and the wiki mostly lists
  possible loot.
- Authentic pickpocket stun duration in game ticks and the conversion between
  the wiki’s seconds column and emulator fields. Missing: period timing/script
  evidence; Paladin and Monkey’s period stun cells are blank.
- Authentic multi-loot probability. Missing: a period source stating the roll;
  GM and Darkan disagree.
- Whether Pompous Merchant’s period client should expose Pickpocket. Missing: a
  client revision or interface/action script that resolves the `14911` cache
  option conflict; the wiki says the behavior existed, while both queried cache
  definitions expose no Pickpocket option.
- Desert Phoenix’s exact Thieving level, failure damage, stun duration, and
  success roll. Missing: a period source for the Grab-feather mechanic’s level
  and failure path; the wiki only closes release, XP, and feather purpose.
- Exact guard assignment and owner visibility geometry for every stall. Missing:
  period map NPC spawn/region data joined to object coordinates plus a server
  visibility script. Cache definitions alone do not contain this relationship.
- Any stall per-attempt caught probability. Missing: a period server rule or
  dated experiment that states one; the period prose only names observers.
- Keldagrim stall object-to-variant mapping and exact twice-fast/half-XP and
  twice-slow/double-XP application. Missing: dated map/object spawn data that
  identifies each Keldagrim stall instance.
- Customs evidence files object IDs and exact item weights. Missing: cache
  object/spawn mapping and a period drop table.
- Exact loot for the Dorgesh-Kaan Average Chest. Missing: the standalone
  Average Chest page did not resolve to a pre-cutoff revision, and the general
  table points to it without reproducing its items.
- Exact trap roll and damage for Dorgesh-Kaan Average and Rich chests. Missing:
  period chest scripts or a page that states the Dorgesh-specific trap values;
  the general page only says that some chests have traps.
- Exact server success formula and failure side effects for pickable doors.
  Missing: period door/Thieving server script; the cache proves options and the
  wiki proves level/XP but neither gives the roll. Darkan’s `numbFingers` and
  flat bonuses are explicitly rejected as unsupported.
- Exact wall-safe loot distribution and the resolution of the `W-T`/`W-WS`/
  `W-RD` coin-list conflict. Missing: period wall-safe server table or an
  empirical source with a clear revision date and complete sample method.
- Exact blackjacking knockout probability, exact freeze duration, and distinct
  failure damage for each Villager/Bandit/Menaphite tier. Missing: period
  blackjacking script or independently calibrated period data. Two picks per
  successful knockout and Menaphite failed-knockout `40` damage are proven.
- Exact per-variant combat bonuses for every offensive/defensive blackjack item.
  Missing: separate period item rows for all IDs; the family behavior and the
  required items are closed, but this dossier does not guess unused combat
  stats.
- Numeric Gloves of Silence success multiplier. Missing: period formula or a
  period empirical calibration that separates gloves from aura/cape/level.
- Rogue outfit’s outside-minigame Thieving XP multiplier. Missing: a period
  equipment bonus table or script; the pinned Rogue equipment page only states
  the Factory route and Factory-specific benefits.
- Numeric Ardougne cloak pickpocket multiplier. Missing: period script or
  calibration; diary route and qualitative improvement are proven.

## Era rejections

- **Prifddinas target content:** reject as a training location. The pinned
  `W-PMK` revision says the city was inaccessible to players and announced for
  early `2014`; the pre-cutoff Elf target is the Lletya/Isafdar elf row, not a
  Prifddinas elf. Do not import Prifddinas stalls, NPCs, or post-release outfit
  behavior (`W-PMK`; `W-ELF`).
- **Dwarf Trader:** **not rejected.** The suspicion that the level-`90`,
  `556.5`-XP row is post-EOC is disproved by the Trader page’s `9 September
  2009` release and the rev-727/rev-742 Pickpocket options (`W-TR`; `C727/C742`).
- **Pompous Merchant:** **not rejected as post-cutoff.** It released
  `31 January 2012`; the remaining issue is the cache action-option conflict,
  not era (`W-PM`; `C727/C742`).
- **Desert Phoenix:** **not rejected as post-cutoff.** It released
  `11 April 2005`; it is a special Grab-feather action rather than a normal
  pocket row (`W-DP`; `C727/C742`).
- **Monkey knife fighter:** **not rejected as post-cutoff.** It released
  `1 December 2010` and is present with a Pickpocket option on NPC `13212` in
  both queried caches (`W-MKF`; `C727/C742`).
- **Elf:** **not rejected as post-cutoff** when scoped to Lletya/Isafdar. The
  level-`85`, `353`-XP row and the Mourning’s End Part I gate are period-backed;
  only Prifddinas variants are excluded (`W-ELF`; `W-MEP1`; `W-PMK`).
