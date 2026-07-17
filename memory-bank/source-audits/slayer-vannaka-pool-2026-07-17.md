# Slayer Vannaka assignment-pool audit — 2026-07-17

Status: **functional source contract provisionally closed; runtime hidden**.
Cutoff: `2012-11-20T00:00:00Z`.

## Finding

Vannaka's ordinary cutoff pool contains **35 families**. The cutoff master page
contains the complete family union but only one observed Grotworm count. Darkan
contains 34 executable rows, but adds Trolls and cannot instantiate Mogres or
Sea snakes because those two family enum entries are comments.

The accepted pool therefore:

- keeps all 35 cutoff Vannaka families;
- rejects Darkan's extra Troll row, which is contradicted by both the cutoff
  Vannaka page and the cutoff cross-master assignment table;
- uses Darkan's ordinary `60–120` range for Grotworms instead of treating one
  observed task of 69 as a complete range; and
- gives Mogres and Sea snakes explicit 10-point common-baseline abstractions
  because their hidden period weights did not survive.

The resulting provisional raw-weight denominator is **460**. Those weights are
implementation calibration, not recovered RuneScape facts. The cutoff Vannaka
page additionally says higher-level monsters were assigned more frequently to
higher-Combat players. That note describes unresolved within-family variant
selection, not a published family-weight algorithm; its exact function remains
`source_blocked`.

## Reconciled ordinary pool

`Weight` is a raw hidden roll-table value. `Gate` is authentic player
eligibility, not implementation readiness. A protective item or special kill
method is an end-to-end Combat obligation and cannot be erased by omitting the
family.

| Family | Weight | Count | Gate | Combat/context obligation | Provenance |
|---|---:|---:|---|---|---|
| Aberrant spectres | 25 | 60–120 | Slayer 60; Priest in Peril route | Nose peg, Slayer helmet, or full Slayer helmet | weight `provisional/darkan`; count/level closed |
| Ankou | 10 | 60–120 | baseline | none | weight `provisional/darkan`; count closed |
| Banshees | 15 | 60–120 | Slayer 15; Priest in Peril route | Earmuffs or accepted helmet equivalent | weight `provisional/darkan`; count/level closed |
| Basilisks | 10 | 60–120 | Slayer 40; Defence 20 | Mirror shield | weight `provisional/darkan`; count/level closed |
| Bloodveld | 20 | 60–120 | Slayer 50 | none beyond variant combat | weight `provisional/darkan`; count/level closed |
| Brine rats | 20 | 60–120 | Slayer 47; partial Olaf's Quest | Brine Rat Cavern access | weight `provisional/darkan`; count/level closed |
| Cockatrice | 10 | 60–120 | Slayer 25; Defence 20 | Mirror shield | weight `provisional/darkan`; count/level closed |
| Crocodiles | 10 | 30–60 | baseline | desert route/context | weight `provisional/darkan`; count closed |
| Cyclopes | 10 | 60–120 | Attack + Strength 130 | Warriors' Guild tokens and Cyclops room | weight `provisional/darkan`; count closed |
| Dust devils | 25 | 60–120 | Slayer 65 | Facemask, masked earmuffs, or accepted helmet equivalent | weight `provisional/darkan`; count/level closed |
| Earth warriors | 15 | 30–60 | baseline | Wilderness risk for the ordinary period location | weight `provisional/darkan`; count closed |
| Ghouls | 10 | 60–120 | baseline | Morytania route/context | weight `provisional/darkan`; count closed |
| Green dragons | 10 | 30–60 | baseline | dragonfire protection and Wilderness risk | weight `provisional/darkan`; count closed |
| Grotworms | 15 | 60–120 | baseline | ordinary Grotworm target/context | membership closed; weight `provisional/darkan`; count `abstraction/vannaka-default+darkan` |
| Harpie bug swarms | 20 | 60–120 | Slayer 33 | Lit bug lantern; 33 Firemaking to light it | weight `provisional/darkan`; count/level closed |
| Hill giants | 10 | 60–120 | baseline | none | weight `provisional/darkan`; count closed |
| Ice giants | 10 | 60–120 | baseline | none | weight `provisional/darkan`; count closed |
| Ice warriors | 10 | 60–120 | baseline | none | weight `provisional/darkan`; count closed |
| Infernal mages | 10 | 60–120 | Slayer 45 | none beyond variant combat | weight `provisional/darkan`; count/level closed |
| Jellies | 20 | 60–120 | Slayer 52 | none beyond variant combat | weight `provisional/darkan`; count/level closed |
| Jungle horrors | 10 | 60–120 | Cabin Fever route | Mos Le'Harmless access | weight `provisional/darkan`; count closed |
| Killerwatts | 20 | 60–120 | Slayer 37; Ernest the Chicken | Insulated boots protect against the Killerwatt Plane | weight `provisional/darkan`; count/level closed |
| Lesser demons | 10 | 60–120 | baseline | none | weight `provisional/darkan`; count closed |
| Mogres | 10 | 60–120 | Slayer 32; Skippy and the Mogres | Fishing explosive or super fishing explosive to lure | membership/count closed; weight `abstraction/common-vannaka-baseline` |
| Molanisks | 10 | 60–120 | Slayer 39; Death to the Dorgeshuun | Slayer bell, light source, and dungeon access | weight `provisional/darkan`; count/level closed |
| Moss giants | 10 | 60–120 | baseline | none | weight `provisional/darkan`; count closed |
| Ogres | 10 | 60–120 | baseline | none | weight `provisional/darkan`; count closed |
| Otherworldly beings | 10 | 60–120 | Lost City | Zanaris access | weight `provisional/darkan`; count closed |
| Pyrefiends | 10 | 60–120 | Slayer 30 | none beyond variant combat | weight `provisional/darkan`; count/level closed |
| Sea snakes | 10 | 30–60 | Royal Trouble route | dungeon access and poison | membership/count closed; weight `abstraction/common-vannaka-baseline` |
| Shades | 10 | 60–120 | baseline for the Stronghold variant | variant-specific XP; Shades of Mort'ton for catacomb variants | weight `provisional/darkan`; count closed |
| Shadow warriors | 10 | 60–120 | Legends' Quest | Legends' Guild basement access | weight `provisional/darkan`; count closed |
| Turoth | 20 | 60–120 | Slayer 55 | leaf-bladed weapon, broad ammunition, or Magic Dart | weight `provisional/darkan`; count/level closed |
| Vampyres | 15 | 60–120 | Priest in Peril route | variant-specific vampyre combat | weight `provisional/darkan`; count closed |
| Werewolves | 10 | 60–120 | Priest in Peril route | ordinary Canifis transformation/combat | weight `provisional/darkan`; count closed |

Darkan's 34 executable rows total 450. Removing its unsupported Troll row
subtracts 10; restoring the two cutoff families at the common 10-point baseline
adds 20, producing `450 - 10 + 10 + 10 = 460`.

## Period master and family evidence

RuneScape Wiki, `Vannaka`, oldid `6534207`, timestamp
`2012-11-04T18:34:25Z`, is the cutoff master page:
<https://runescape.wiki/w/Vannaka?oldid=6534207>.

It establishes:

- Combat 40 and no quest requirement for the master himself;
- 4 ordinary, 20 tenth-task, and 60 fiftieth-task points after Smoking Kills;
- all 35 accepted families and the count ranges above; and
- the note that player Combat level affected which monster levels were assigned
  more frequently.

Grotworms entered the table at oldid `6534202`, timestamp
`2012-11-04T18:32:05Z`, through an edit explicitly described as adding
Grotworms:
<https://runescape.wiki/w/Vannaka?oldid=6534202>. The new row recorded exactly
69, not a minimum and maximum. Talk:Vannaka oldid `5715609`, timestamp
`2012-06-05T21:55:36Z`, independently reports 78 Grotworms from Vannaka:
<https://runescape.wiki/w/Talk:Vannaka?oldid=5715609>. The contradiction proves
69 is not a fixed contract. The historical range is `source_blocked`;
Darkan's `60–120` is retained as the smallest explicit Vannaka-default
abstraction, and both observations fall inside it.

The cutoff cross-master `Slayer assignment` table, oldid `6303852`, timestamp
`2012-09-27T13:49:08Z`, independently assigns Mogres and Sea snakes to Vannaka
but assigns Trolls only to Chaeldar and Sumona:
<https://runescape.wiki/w/Slayer_assignment?oldid=6303852>.

Vannaka oldid `4334033`, timestamp `2011-05-29T12:23:15Z`, records the explicit
Knowledge Base removal of Elves and Terror dogs:
<https://runescape.wiki/w/Vannaka?oldid=4334033>. The cutoff cross-master table
still lists Terror dogs for Vannaka, but `Terror dog` oldid `6547220`, timestamp
`2012-11-10T22:08:35Z`, names Sumona and Kuradal rather than Vannaka:
<https://runescape.wiki/w/Terror_dog?oldid=6547220>. The explicit Knowledge
Base removal plus individual page wins; Terror dogs are the excluded 36th
candidate family.

Cyclopes have the inverse table conflict. They appear in cutoff Vannaka and the
individual `Cyclops` page, oldid `6565802`, but the cross-master table omits
Vannaka. The two direct Vannaka attestations win.

The distinctive period obligations are pinned by the following cutoff pages:

- `Aberrant spectre`, oldid `6555339`: Slayer 60 and protective headgear:
  <https://runescape.wiki/w/Aberrant_spectre?oldid=6555339>.
- `Banshee`, oldid `6589075`: Slayer 15 and the unprotected stat/lifepoint
  consequence: <https://runescape.wiki/w/Banshee?oldid=6589075>.
- `Basilisk`, oldid `6565796`, and `Cockatrice`, oldid `6579848`: mirror
  shields and Defence-20 assignment eligibility:
  <https://runescape.wiki/w/Basilisk?oldid=6565796> and
  <https://runescape.wiki/w/Cockatrice?oldid=6579848>.
- `Brine rat`, oldid `6555564`: Slayer 47 and partial Olaf's Quest:
  <https://runescape.wiki/w/Brine_rat?oldid=6555564>.
- `Dust devil`, oldid `6529409`: Slayer 65 and the facemask/helmet kill
  requirement: <https://runescape.wiki/w/Dust_devil?oldid=6529409>.
- `Harpie Bug Swarm`, oldid `6530649`: Slayer 33, lit bug lantern, and the
  explicit fact that assignment can precede Firemaking 33:
  <https://runescape.wiki/w/Harpie_Bug_Swarm?oldid=6530649>.
- `Mos Le'Harmless`, oldid `6549119`: Cabin Fever access for Jungle horrors:
  <https://runescape.wiki/w/Mos_Le%27Harmless?oldid=6549119>.
- `Killerwatt`, oldid `6469837`, and `Ernest the Chicken`, oldid `6542622`:
  Slayer 37, insulated-boots consequences, and the quest's Killerwatt Plane
  unlock:
  <https://runescape.wiki/w/Killerwatt?oldid=6469837> and
  <https://runescape.wiki/w/Ernest_the_Chicken?oldid=6542622>.
- `Mogre`, oldid `6493220`: Slayer 32, the miniquest, and explosive lure:
  <https://runescape.wiki/w/Mogre?oldid=6493220>.
- `Molanisk`, oldid `6565831`, `Slayer bell`, oldid `6121349`, and
  `Dorgesh-Kaan South Dungeon`, oldid `6393410`: Slayer 39, bell, light, and
  Death to the Dorgeshuun access:
  <https://runescape.wiki/w/Molanisk?oldid=6565831>,
  <https://runescape.wiki/w/Slayer_bell?oldid=6121349>, and
  <https://runescape.wiki/w/Dorgesh-Kaan_South_Dungeon?oldid=6393410>.
- `Sea Snake Hatchling`, oldid `6448392`, and
  `Miscellania and Etceteria dungeon`, oldid `6436494`: the 30–60 family,
  Royal Trouble access, and poison:
  <https://runescape.wiki/w/Sea_Snake_Hatchling?oldid=6448392> and
  <https://runescape.wiki/w/Miscellania_and_Etceteria_dungeon?oldid=6436494>.
- `Cyclops`, oldid `6565802`: the Attack-plus-Strength 130 and Warriors' Guild
  token access:
  <https://runescape.wiki/w/Cyclops?oldid=6565802>.
- `Shadow warrior`, oldid `6555920`: post-Legends' Quest Vannaka assignment:
  <https://runescape.wiki/w/Shadow_warrior?oldid=6555920>.
- `Turoth`, oldid `6565315`: Slayer 55 and the restricted weapon/ammunition
  set: <https://runescape.wiki/w/Turoth?oldid=6565315>.
- `Shade`, oldid `6564222`: the Stronghold Shade gives one-quarter ordinary
  combat XP and only 5% normal Slayer XP, explicitly 3.5:
  <https://runescape.wiki/w/Shade?oldid=6564222>.

## Variant boundary

The cutoff family union does not close every qualifying variant.

- Mutated bloodvelds, brutal green dragons, young and mature Grotworms, ogress
  warriors/champions, Loar/Phrin/Riyl/Asyn/Fiyr shades, Mightiest turoth, and
  the ordinary revenant-werewolf relation have positive period evidence, but
  several carry their own quest, reward, or context gates.
- Mighty banshees, Icelords, Zogres/Skogres, and the two ordinary Sea-snake
  variants have corroborating task-substitution evidence but require their
  exact gates and mechanics in the stable variant ledger.
- Champion variants are not admitted by name matching. `Giant Champion` oldid
  `6521208` explicitly says it does not count toward Hill-giant tasks:
  <https://runescape.wiki/w/Giant_Champion?oldid=6521208>. Ghoul and Lesser
  Demon Champions remain disputed unique encounters.
- Revenant pyrefiends and the Giant Sea Snake remain disputed. The latter is a
  Royal Trouble quest boss; `Giant Sea Snake` oldid `6351211` neither names
  Vannaka nor supplies an ordinary task contract:
  <https://runescape.wiki/w/Giant_Sea_Snake?oldid=6351211>.
- Exact cutoff Vampyre forms remain `source_blocked` because the master and
  cross-master pages point through an incomplete imported page lineage.

Darkan's display-name substring matching is not acceptable evidence for these
edges: it can make `ogre` absorb Mogres/Jogres/Zogres and admit named bosses.
AnkiScape's future ledger must use explicit stable variant ids.

## Emulator evidence and limits

Darkan:

- `Task.java:72-105` contains 34 executable Vannaka rows and their raw weights
  and counts;
- `TaskMonster.java:90` and `:94` leave Mogres and Sea snakes as enum comments,
  explaining their absence from executable tasks;
- `TaskMonster.java:41` and `Task.java:102` incorrectly admit Trolls to
  Vannaka; and
- `Master.java:25` corroborates the Combat-40 master gate and 4/20/60 points.

Pinned repository:
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`,
nested commit `c343a917712649675989315009ce250639e0850f`.

game-main's Vannaka block is explicitly incomplete and includes filler families
until Morytania is unlocked. It is useful for individual implemented mechanics,
not pool membership or completeness. Its eight explicit ordinary-family
weights are `2.17`, exactly the two-decimal rendering of `10 / 460 × 100`, which
independently corroborates the reconciled provisional denominator. The other
executable rows fall back to `1.0`, however, so its current active runtime table
is not a coherent parity reproduction and cannot override the cutoff master and
cross-master tables.

Pinned snapshot:
`/Users/ArmanTarkhanian1/Downloads/game-main`.

The snapshot does have a live talk-to assignment path:
`slayer_masters_dialogue.plugin.kts:30-42` calls `giveTask`, whose
`:152-179` block filters player requirements and rolls the remaining weights.
That corrects the earlier Turael audit's claim that no active generator consumes
the table; the runtime exists, but its input data remains intentionally partial.

## Current AnkiScape readiness

This audit does **not** authorize a partial live Vannaka role.

The Combat registry has at least one ordinary target for only 12 of 35
families: Ankou, Banshees, Cockatrice, Earth warriors, Ghouls, Hill giants, Ice
giants, Ice warriors, Lesser demons, Moss giants, Shades, and Werewolves.
Twenty-three families have no target at all.

The existing Banshee and Cockatrice rows still omit their protective-equipment
consequences, and the Combat target gate does not yet express the quest,
Slayer, Defence, context, lure, lantern, bell, restricted-weapon, dragonfire,
or Wilderness obligations needed by the full pool. There is still no stable
Slayer family-to-variant registry or live master assignment generator.

This source pass found and fixed one independent Combat defect. The live
Stronghold `Shade` previously copied game-main's conflicting 4.2 Slayer XP and
granted ordinary combat XP. It now carries the cutoff 3.5 Slayer XP and uses the
existing `xp_multiplier = 0.25` path for Attack/Strength/Defence/Ranged/Magic
damage XP and Constitution XP. A deterministic burst regression proves the
quarter-rate consequence.

No owner-level design question emerged. Remaining work is source/data and
implementation: complete the stable family/variant registry, add the 23 absent
families, implement the distinctive kill loops and routes, resolve or abstract
the Combat-level variant-selection function, and certify the whole pool before
exposing Vannaka.
