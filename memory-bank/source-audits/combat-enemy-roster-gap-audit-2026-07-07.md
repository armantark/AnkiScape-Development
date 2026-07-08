# Combat Enemy Roster-Gap Audit — 2026-07-07

**Scope:** Audit only. No enemies implemented, no `.py` files changed. This document
enumerates what the local 2011Scape source (`.../npcs/definitions/`) contains that
`COMBAT_ENEMY_DATA` in `combat_data.py` has not yet pulled in, classifies each gap by
priority and by the engine mechanics it needs, and gives a staged build recommendation.

## Executive summary

- **Current roster:** 94 enemies in `COMBAT_ENEMY_DATA` (`combat_data.py`, keys `chicken`
  … `giant_spider_level_50`), citing **93 distinct source plugin files** (a few files back
  more than one roster entry — e.g. `goblin_level_2.plugin.kts` → armed/unarmed, `duck_level_1.plugin.kts` → land/water).
- **Source tree:** **180** `*.plugin.kts` combat definitions under
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/`.
- **Gap:** **87 source definition files** exist that no roster entry references. Every one
  is pre-baseline (rev 667 = 2011-10-04) — there is nothing near-baseline or post-EOC in the
  gap, so era is not a blocker for any of them.
- **Biggest omissions:** the entire `dragons/` folder (8 files), the entire `demons/` folder
  (10 files), most `undeads/revenants/` (15 files), and a large block of Slayer monsters in
  `critters/`, `demons/`, `undeads/`, and `other/`.
- **Mechanic ceiling:** AnkiScape's model gives every enemy one `attack_style: "melee"` (the
  style *they* hit you with) and has no field for magic/ranged attackers, protection prayers,
  phases, shields, dragonfire, or a required *player* attack style. Roughly a third of the
  gap is pure-melee and fits the current model as a data-only extraction; the rest is blocked
  on new engine mechanics.
- **Tormented Demon verdict:** a real gap, not an intentional exclusion. It exists in the
  source *only* as an NPC id (`Npcs.TORMENTED_DEMON = 8349`, Npcs.kt:7560) and world spawns
  (`areas/spawns/spawns_10329.plugin.kts`); there is **no `set_combat_def` plugin for it
  anywhere in the tree**, so even its stats would have to come from the wiki. It is era-valid
  (While Guthix Sleeps, 26 Nov 2008, pre-baseline) but blocked on the deepest engine work of
  any gap enemy.

---

## 1. Roster inventory (94 current enemies)

The roster is grouped in `COMBAT_ENEMY_DATA` by an in-game `group` field, not by source
folder. Below it is organized by source folder for cross-checking against the gap list.
All 94 are backed by a `source` pointing at a real `definitions/*.plugin.kts` file that was
confirmed to exist. The 56 `combat-*.md` per-enemy audit docs under
`memory-bank/source-audits/` cover the families below; audit coverage is by *family*, not one
doc per NPC id (e.g. `combat-skeletons-2026-06-23.md` covers all skeleton levels).

### animals/ (in roster)
| Roster key(s) | Source file | Audit doc |
|---|---|---|
| `chicken` | `animals/chicken_level_1.plugin.kts` | combat-simple-enemies / tutorial-starter-kit |
| `cow`, `cow_calf` | `animals/cow_level_2`, `cow_calf_level_2` | combat-simple-enemies |
| `ram` | `animals/ram_level_2.plugin.kts` | combat-simple-enemies |
| `duck_land`, `duck_water` | `animals/duck_level_1.plugin.kts` | combat-ducks |
| `unicorn`, `black_unicorn` | `animals/unicorn_level_15`, `black_unicorn_level_27` | combat-rats-unicorns |
| `black_bear` | `animals/black_bear_level_19.plugin.kts` | combat-black-bear |
| `wolf`, `white_wolf_level_25`, `white_wolf_level_38`, `big_wolf` | `animals/wolf_lvl_11`, `white_wolf_lvl_25`, `white_wolf_lvl_38`, `big_wolf_lvl_73` | combat-wolves |
| `seagull` | `animals/seagull_level_2.plugin.kts` | (via simple enemies) |

### critters/ (in roster)
| Roster key(s) | Source file | Audit doc |
|---|---|---|
| `rat`, `giant_rat`, `giant_rat_level_6`, `giant_rat_level_26` | `critters/rat_level_1`, `giant_rat_level_2/6/26` | combat-rats-unicorns |
| `spider`, `giant_spider` | `critters/spider_level_1`, `giant_spider_level_2` | combat-simple-enemies / spider-drop-range |
| `giant_bat` | `critters/giant_bat_level_27.plugin.kts` | combat-giant-bat |
| `poison_scorpion`, `scorpion`, `king_scorpion`, `pit_scorpion`, `scorpion_level_59` | `critters/poison_scorpion_lvl_20`, `scorpion_level_14`, `king_scorpion_level_32`, `pit_sorpion_lvl_28`, `scorpion_level_59` | combat-scorpion-spider-variants |
| `poison_spider`, `poison_spider_level_64`, `spider_level_24`, `deadly_red_spider`, `giant_spider_level_50` | `critters/poison_spider_lvl_31/64`, `spider_level_24`, `deadly_red_spider_level_34`, `giant_spider_level_50` | combat-scorpion-spider-variants / poison-enemies |

### demons/ (in roster)
| Roster key | Source file | Audit doc |
|---|---|---|
| `imp` | `demons/imp_level_2.plugin.kts` | combat-imp |

### humanoids/ (in roster)
Al-Kharid warrior, barbarian (lvl 8/9/10/17 variants), black knight, chaos druid, chaos
dwarf, citizen (`citizen_level_2`), cuffs, farmer, guards (Varrock/sword/battleaxe, market,
jail), Haakon, H.A.M. guards (12/18/22), highwayman, monk (`monk_level_5`), monk of Zamorak
(`monk_of_zamorak_lvl_45`), mugger, narf/jeff/rusty, outlaw, pirate, thief, thug, dwarf
(10/11), white knights (36/38/39/42). Audited across combat-barbarian*, combat-guard,
combat-white-knights, combat-thief, combat-thug, combat-mugger, combat-outlaw,
combat-monk-of-zamorak, combat-ham-guards, combat-haakon-the-champion, combat-chaos-dwarf,
combat-black-knight, combat-chaos-druid, combat-farmer, combat-al-kharid-warrior,
combat-market-jail-guards, combat-highwayman, combat-pirate, combat-citizen.

### other/ (in roster)
Goblins (2 armed/unarmed, 5, 11, 13, 16, 25), hobgoblins (armed/unarmed 28), TzHaar-Ket
(`tzhaar_ket_lvl_149`), hill/moss/ice giants. Audited via combat-higher-goblins,
combat-goblin-level-2, combat-hobgoblins, combat-tzhaar-ket, combat-giants.

### undeads/ (in roster)
Ghost (`ghost_level_19`), zombies (13/18/24/25/30/44/53), skeletons (21/22/25/45/60/68/85).
Audited via combat-ghost, combat-zombies, combat-skeletons.

**Present-but-family-audited note:** every roster enemy falls under one of the 56
`combat-*.md` docs' families. No roster enemy is entirely unaudited; the missing coverage is
in the *source*, not the roster.

---

## 2. The gap list — 87 source definitions not in the roster

Present-in-source minus present-in-roster, computed by matching every `definitions/*.plugin.kts`
path against the `source` strings in `combat_data.py`. Priority is by how iconic / commonly
fought the enemy is in a skilling-add-on context (a monster you would actually grind on),
**not** by combat level. "Model fit" flags whether it drops into the current single-`melee`
model as a data-only extraction (✅), needs new enemy-attack-style support (⚠️ magic/ranged),
or needs a bespoke mechanic (⛔).

### HIGH priority (iconic, commonly fought)

| Enemy | Source file | Model fit | Note |
|---|---|---|---|
| Green dragon | `dragons/green_dragon_level_79.plugin.kts` | ⛔ dragonfire | Classic Wildy money monster; needs dragonfire + antifire mechanic |
| Blue dragon | `dragons/blue_dragon_level_111.plugin.kts` | ⛔ dragonfire | Taverley dungeon staple |
| Red dragon | `dragons/red_dragon_level_152.plugin.kts` | ⛔ dragonfire | |
| Black dragon | `dragons/black_dragon_level_227.plugin.kts` | ⛔ dragonfire | |
| Baby dragon | `dragons/baby_dragon_level_48.plugin.kts` | ✅ melee | No dragonfire on babies; near data-only |
| Baby black dragon | `dragons/baby_black_dragon_level_83.plugin.kts` | ✅ melee | No dragonfire; data-only |
| King Black Dragon | `dragons/king_black_dragon_level_276.plugin.kts` | ⛔ dragonfire/phases | Boss; multi-style dragonfire |
| Lesser demon | `demons/lesser_demon_lvl_82.plugin.kts` | ✅ melee (SLASH) | Iconic; fits model |
| Greater demon | `demons/greater_demon_level_92.plugin.kts` | ✅ melee (SLASH) | Slayer + iconic; fits model |
| Black demon | `demons/black_demon_lvl_172.plugin.kts` | ✅ melee (SLASH) | Fits model |
| Abyssal demon | `demons/abyssal_demon_level_124.plugin.kts` | ✅ melee (SLASH) | Marquee slayer monster (whip source); teleports in real RS but hits melee |
| Bloodveld | `demons/bloodveld_level_76.plugin.kts` | ⚠️ MAGIC_MELEE | Slayer staple; melee that ignores melee-defence |
| Hellhound | `animals/hellhound_level_122.plugin.kts` | ✅ melee | Slayer staple |
| Rock crab | `critters/rock_crab_lvl_13.plugin.kts` | ✅ melee (STAB) | Extremely common low-level training monster |
| Ghoul | `undeads/ghoul_level_42.plugin.kts` | ✅ melee | Very common (Canifis) |
| Werewolf | `other/werewolf_level_88.plugin.kts` | ✅ melee | Canifis; common |
| Ice warrior | `other/ice_warrior_level_57.plugin.kts` | ✅ melee (SLASH) | Common (White Wolf Mtn / Asgarnia ice caves) |
| Earth warrior | `other/earth_warrior_level_51.plugin.kts` | ✅ melee | Common (Edgeville dungeon) |
| Dark wizard | `humanoids/dark_wizard_lvl_7.plugin.kts`, `dark_wizard_lvl_20.plugin.kts` | ⚠️ magic | Iconic low-level mage |
| Wizard | `humanoids/wizard_lvl_9.plugin.kts` | ⚠️ magic | Common tower mage |

### MEDIUM priority (well-known, mostly Slayer / regional)

| Enemy | Source file | Model fit |
|---|---|---|
| Nechryael | `demons/nechryael_lvl_115.plugin.kts` | ✅ melee (SLASH) (spawns adds in real RS) |
| Pyrefiend | `demons/pyrefiend_lvl_43.plugin.kts` | ⚠️ MAGIC_MELEE |
| Icefiend | `demons/icefiend_level_13.plugin.kts` | ⚠️ MAGIC_MELEE |
| Death spawn | `demons/death_spawn_lvl_46.plugin.kts` | ✅ melee (SLASH) |
| Banshee | `undeads/banshee_level_23.plugin.kts` | ✅ melee (CRUSH) (earmuffs mechanic in real RS) |
| Cave crawler | `critters/cave_crawler_lvl_23.plugin.kts` | ✅ melee (STAB) |
| Cockatrice | `critters/cockatrice_level_37.plugin.kts` | ✅ melee (STAB) (mirror-shield mechanic) |
| Rockslug | `critters/rockslug_lvl_29.plugin.kts` | ✅ melee |
| Cave bug | `critters/cave_bug_lvl_6.plugin.kts` | ✅ melee |
| Cave slime | `critters/cave_slime_lvl_23.plugin.kts` | ✅ melee |
| Flesh crawler ×3 | `critters/flesh_crawler_lvl_28/35/41.plugin.kts` | ✅ melee (Stronghold of Security AFK spot) |
| Gargoyle | `other/gargoyle_lvl_111.plugin.kts` | ✅ melee (SLASH) (rock-hammer finish) |
| Aberrant spectre | `undeads/aberrant_spectre_lvl_96.plugin.kts` | ⚠️ magic (nosepeg mechanic) |
| Infernal mage | `humanoids/infernal_mage_level_66.plugin.kts` | ⚠️ magic |
| Crawling hand | `other/crawling_hand_level_8.plugin.kts` | ✅ melee (starter slayer) |
| Ankou ×3 | `undeads/ankou_lvl_75/82/86.plugin.kts` | ✅ melee (Stronghold of Security) |
| Shade | `undeads/shade_level_83.plugin.kts` | ✅ melee (CRUSH) |
| Ghost (level 77) | `undeads/ghost_level_77.plugin.kts` | ✅ melee (higher-level ghost variant) |
| Skeleton warlock | `undeads/skeleton_warlock_lvl_11.plugin.kts` | ⚠️ magic (only pure-MAGIC attackStyle in tree) |
| Catablepon ×3 | `other/catablepon_lvl_49/64/68.plugin.kts` | ✅ melee (Stronghold of Security) |
| Minotaur ×2 | `other/minotaur/minotaur_lvl_12/27.plugin.kts` | ✅ melee (Stronghold of Security) |
| Cave goblin | `other/cave_goblin_level_3.plugin.kts` | ✅ melee |
| Canifis citizen | `humanoids/canifis_citizen_level_24.plugin.kts` | ✅ melee (pickpocket target family) |
| TzHaar-Hur | `other/tzhaar_hur_lvl_74.plugin.kts` | ✅ melee |
| TzHaar-Xil | `other/tzhaar_xil_lvl_133.plugin.kts` | ⚠️ ranged (throwing) |
| TzHaar-Mej | `other/tzhaar_mej_lvl_103.plugin.kts` | ⚠️ magic |
| Count Draynor | `undeads/count_draynor_level_37.plugin.kts` | ✅ melee — quest boss (Vampyre Slayer), needs stake to kill in real RS |

### LOW priority (PvP-flavored, quest-gated, minigame, or hybrid/mining)

| Enemy | Source file | Model fit / reason |
|---|---|---|
| Revenants ×15 | `undeads/revenants/revenant_*.plugin.kts` (imp 7 … dragon 135) | ⛔ multi-style — real revenants switch melee/ranged/magic every attack; also very high magic stats. Wilderness/PvP flavor, low skilling relevance |
| Battle mages ×3 (Guthix/Saradomin/Zamorak lvl 54) | `humanoids/guthix_battle_mage_lvl_54.plugin.kts` etc. | ⚠️ magic — Mage Arena minigame |
| Shadow warrior | `humanoids/shadow_warrior_lvl_48.plugin.kts` | ✅ melee — Legends' Quest gated |
| Weaponsmaster | `humanoids/weaponsmaster_level_23.plugin.kts` | ✅ melee — minigame/Champions'-flavored |
| Jailer | `humanoids/jailer_level_47.plugin.kts` | ✅ melee |
| Johnny the beard | `humanoids/johnny_the_beard_level_2.plugin.kts` | ✅ melee — Shield of Arrav quest NPC |
| Gardener | `humanoids/gardener_lvl_4_quest.plugin.kts` | ✅ melee — quest NPC |
| Monks of Zamorak (alt) | `humanoids/monks_of_zamorak.plugin.kts` | ✅ melee — **duplicate** of the roster's monk of Zamorak with different NPC ids (1044–1046, HP 400); low value |
| Abyssal guardian/leech/walker | `other/abyssal_guardian`, `abyssal_leech`, `abyssal_walker.plugin.kts` | ✅/⚠️ — Abyss (Runecrafting) creatures |
| Tree spirit | `undeads/tree_spirit_lv_101.plugin.kts` | ✅ melee — Enchanted Key / random-event flavor |
| Living rock protector | `other/living_rock_protector.plugin.kts` | ⛔ mining-hybrid — gated on 73 Mining, drops ores; not a normal kill |
| Temple Guardian | `animals/template_guardian_lvl_30.plugin.kts` | ⛔ — Priest in Peril quest boss, `defenceMagic = 999999` (magic-immune); quest-only |
| Rocks (Rock Crab hidden form) | `critters/rocks.plugin.kts` | ⛔ **not a distinct enemy** — the camouflaged `Npcs.ROCKS` state of the Rock Crab; do not add separately |

**Exclusion candidates within the gap (recommend *not* adding as ordinary enemies):**
`critters/rocks.plugin.kts` (Rock Crab disguise, not a real enemy),
`animals/template_guardian_lvl_30.plugin.kts` (quest boss, magic-immune),
`other/living_rock_protector.plugin.kts` (mining activity, not a combat kill),
`humanoids/monks_of_zamorak.plugin.kts` (duplicate id-set of an existing roster enemy),
`humanoids/gardener_lvl_4_quest.plugin.kts` and `humanoids/johnny_the_beard_level_2.plugin.kts`
(single-instance quest NPCs). Everything else is a legitimate huntable enemy.

---

## 3. Mechanic-support analysis

Today every `COMBAT_ENEMY_DATA` entry has `attack_style: "melee"` — the style the enemy uses
against the player — and there is no field for enemy attack-style variety, protection prayers,
phases, shields, dragonfire, or a required *player* attack style. Mapping that against the
source's `StyleType` enum
(`STAB`, `SLASH`, `CRUSH` = melee; `MAGIC`, `RANGED`, `MAGIC_MELEE` = non-melee/hybrid):

**Fits the current model as-is (data-only extraction) — melee STAB/SLASH/CRUSH:**
baby dragon, baby black dragon, lesser/greater/black demon, abyssal demon, nechryael, death
spawn, hellhound, rock crab, ghoul, werewolf, ice/earth warrior, banshee, shade, ghost 77,
cave crawler, cockatrice, rockslug, cave bug, cave slime, flesh crawler ×3, gargoyle, crawling
hand, ankou ×3, catablepon ×3, minotaur ×2, cave goblin, canifis citizen, TzHaar-Hur, count
Draynor, shadow warrior, weaponsmaster, jailer, tree spirit, and the quest/minigame melee NPCs.
These are the cheap wins — extract `stats`, `bonuses`, `attackSpeed`, `respawnDelay`, drops
from the plugin and add.

**Needs enemy magic/ranged attack support (a new `enemy_attack_style` value):**
- *Magic attackers* (`StyleType.MAGIC` or high `magic` stat driving a magic strategy):
  dark wizard (7/20), wizard (9), infernal mage, aberrant spectre, skeleton warlock (the only
  pure-`MAGIC` attackStyle in the tree), TzHaar-Mej, the three lvl-54 battle mages.
- *Ranged attackers:* TzHaar-Xil (throwing rings).
- *Hybrid `MAGIC_MELEE`* (melee swing that rolls against magic defence, ignoring melee
  defence): bloodveld, pyrefiend, icefiend.
  Faithfully modeling these means at minimum a field describing the style the enemy attacks
  with, so the player can be told to pray/avoid appropriately. It does not necessarily require
  a full prayer system, but it does require the roster schema to stop assuming "melee."

**Needs bespoke mechanics beyond attack-style:**
- *Dragonfire* — green/blue/red/black dragons and KBD. Real damage gate is an antifire shield
  or potion; without it the fight is unfaithfully lethal. Needs a dragonfire-mitigation check.
- *Multi-style switching* — revenants ×15 cycle melee/ranged/magic; the King Black Dragon
  alternates dragonfire with melee.
- *Mining hybrid* — living rock protector is a Mining activity, not a normal kill.
- *Style-rotation + shield + quest gate* — Tormented Demon (below).

### Tormented Demon (investigated per request)

- **Presence in source:** Only as `Npcs.TORMENTED_DEMON = 8349` (and 8350–8363 variants) in
  `game/plugins/.../api/cfg/Npcs.kt:7560` and as five world spawns in
  `game/plugins/.../content/areas/spawns/spawns_10329.plugin.kts` (tiles around 2588–2609 /
  5717–5736, the While Guthix Sleeps Chasm-of-Tears dungeon). **There is no `set_combat_def`
  plugin for it anywhere in the tree** — confirmed by grepping every file containing
  `set_combat_def` for `TORMENTED_DEMON` (no hits). So unlike every other gap enemy, its
  combat stats cannot be extracted from the source; they would have to come from the wiki.
- **Real mechanic** (RuneScape wiki): attacks with **melee, ranged, and magic**, and every
  ~150 damage taken (~25% of its 700-ish HP) it **switches its protection prayer to the last
  combat style it was damaged with** — so the player must rotate through at least two attack
  styles to keep dealing damage. It also carries a **fire shield** that reduces non-demonbane /
  non-abyssal damage by ~20%.
- **Era:** released with **While Guthix Sleeps on 26 November 2008**, comfortably pre-baseline
  (rev 667 = 2011-10-04). Era-valid; its absence is an audit gap, not an intentional exclusion.
- **What AnkiScape would need to build to support it faithfully:**
  1. **Per-style enemy attacks** — the enemy must be able to hit with melee *and* ranged *and*
     magic (superset of the magic/ranged support the mages above need).
  2. **A protection-prayer / style-rotation mechanic** — the enemy adopts a protection
     prayer against the player's current style and switches it based on the style that last
     damaged it, forcing the player to alternate attack styles. This is the novel piece:
     AnkiScape has no concept of the enemy reacting to the player's chosen style, nor of a
     required *player* attack style at all.
  3. **A shield / damage-reduction modifier** — the fire shield's ~20% reduction against
     non-demonbane weapons.
  4. **A quest gate** — availability gated on completing While Guthix Sleeps (which itself
     chains off a long quest line). AnkiScape would need a WGS completion flag.
  Because all four are net-new engine features, the Tormented Demon is the single most
  expensive gap enemy and should be the *last* thing built, after the general per-style-attack
  and prayer scaffolding already needed by the mages and dragons exists.

---

## 4. Recommendation & staging

All 87 gap files are pre-baseline, so era gates nothing. The real axis is engine cost. A
sensible build order:

**Stage 1 — Cheap wins (data-only, no engine work).** Extract stats/bonuses/drops straight
from the plugin for the pure-melee, commonly-fought monsters. Highest value first:
lesser demon, greater demon, black demon, abyssal demon, hellhound, rock crab, ghoul,
werewolf, ice warrior, earth warrior, baby dragon, baby black dragon, then the Slayer/Stronghold
melee block (nechryael, death spawn, gargoyle, banshee, shade, cave crawler, cockatrice,
rockslug, cave bug, cave slime, flesh crawler ×3, crawling hand, ankou ×3, catablepon ×3,
minotaur ×2, cave goblin, canifis citizen, TzHaar-Hur, ghost 77). This alone roughly doubles
the melee roster and is low-risk. Skip the exclusion candidates (rocks, temple guardian,
living rock protector, monks_of_zamorak duplicate, single-instance quest NPCs) unless a quest
system later wants them.

**Stage 2 — Add an enemy-attack-style field.** Introduce a way to record that an enemy attacks
with magic or ranged (and the `MAGIC_MELEE` hybrid), so the roster schema stops assuming
"melee." Then bring in the mages and ranged/hybrid attackers: dark wizard (7/20), wizard,
infernal mage, aberrant spectre, skeleton warlock, TzHaar-Mej, TzHaar-Xil, the lvl-54 battle
mages, bloodveld, pyrefiend, icefiend. Scope this deliberately to "describe the threat," not a
full prayer engine.

**Stage 3 — Dragonfire mitigation.** Add the antifire shield/potion damage gate, then the
adult dragons (green, blue, red, black) and the King Black Dragon.

**Stage 4 — Multi-style / reactive mechanics.** Revenants (multi-style cycling) if wilderness
content is ever wanted; then the Tormented Demon last, since it needs per-style attacks (Stage
2), a shield modifier, the novel protection-prayer/style-rotation reaction, *and* a While
Guthix Sleeps gate — none of which exist today.

### Confidence / caveats

- The gap set (87 files) is computed, not guessed: source paths were regex-matched against the
  `source` strings in `combat_data.py`; there were zero referenced-but-missing files, so the
  roster's citations are all real.
- `StyleType` classifications come straight from each plugin's `attackStyle` / `magic` /
  `ranged` fields. Where a file sets no `attackStyle` but a high `magic` stat (mages, dragons),
  I inferred a magic/dragonfire attacker from the stat and wiki knowledge; treat those as
  "needs verification when implemented," not gospel.
- Release dates other than the Tormented Demon's are from RuneScape-wiki knowledge, not the
  source tree (the source has no dates). All named gap enemies are clearly RSC/RS2-era
  (2001–2009) and pre-baseline; none are near-baseline exceptions or post-EOC, so this did not
  require per-enemy date verification. The one era-critical check — the Tormented Demon at
  26 Nov 2008 — was confirmed against the wiki.

**Sources (Tormented Demon era/mechanics):**
[Tormented Demon — OSRS Wiki](https://oldschool.runescape.wiki/w/Tormented_Demon),
[While Guthix Sleeps — OSRS Wiki](https://oldschool.runescape.wiki/w/While_Guthix_Sleeps).
