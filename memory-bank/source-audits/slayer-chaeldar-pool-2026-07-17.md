# Slayer Chaeldar assignment-pool audit — 2026-07-17

Status: **functional source contract provisionally closed; runtime hidden**.
Cutoff: `2012-11-20T00:00:00Z`.

Implementation status, 2026-07-18: the complete 34-row pool is now encoded as
a hidden registry contract. The historical readiness snapshot near the end of
this audit is preserved as evidence of the 2026-07-17 checkout; current
readiness is derived in
`source-audits/slayer-chaeldar-registry-2026-07-18.md`.

## Finding

Chaeldar's cutoff ordinary pool contains **34 families**:

- 32 families appear on the cutoff master table and cross-master table; and
- Grifolapines and Grifolaroos are recovered from their cutoff individual
  pages and the executable emulator table.

Darkan has 32 executable rows totaling 368 raw weight points. It includes the
two recovered Polypore families but omits Shadow warriors and Mutated
zygomites. Restoring those two cutoff families at explicit 10-point
common-baseline abstractions produces a provisional denominator of **388**.
Every weight remains implementation calibration, not a recovered RuneScape
fact.

Chaeldar requires Combat 70 and practical access through Lost City/Zanaris.
There is no master-level Slayer requirement. Her post-Smoking-Kills point
schedule is **10 / 50 / 150**. The cutoff master page's `100` fiftieth-task
value is an anonymous typo contradicted by the cutoff Slayer-points table, both
emulators, and the same master page's unchanged 16-point long-run average.

## Reconciled ordinary pool

`D` means the cutoff default count `110–170`. `Weight` is a raw hidden
roll-table value. `Gate` is authentic player eligibility, not current
AnkiScape readiness. A protective item, restricted weapon, finisher, or route
is an end-to-end Combat obligation.

| Family | Weight | Count | Gate | Combat/context obligation | Provenance |
|---|---:|---:|---|---|---|
| Aberrant spectres | 15 | D | Slayer 60; Morytania route | Nose peg or accepted Slayer helmet; unprotected LP/stat drain | weight `provisional/darkan`; count/gate closed |
| Banshees | 5 | D | Slayer 15; Morytania route | Earmuffs or accepted helmet; unprotected damage/stat drain | weight `provisional/darkan`; count/gate closed |
| Basilisks | 15 | D | Slayer 40; Defence 20 | Mirror shield; unprotected damage/stat drain | weight `provisional/darkan`; count/gate closed |
| Bloodvelds | 15 | D | Slayer 50 | Mutated variants retain their route gates | weight `provisional/darkan`; count/gate closed |
| Blue dragons | 10 | D | baseline | Adult and baby-blue membership; adult dragonfire | weight `provisional/darkan`; count closed |
| Brine rats | 10 | D | Slayer 47; partial Olaf's Quest | Brine Rat Cavern/spade access | weight `provisional/darkan`; count/gate closed |
| Bronze dragons | 10 | 30–60 | baseline | Dragonfire and metal-dragon behavior | weight `provisional/darkan`; count closed |
| Cave crawlers | 5 | D | Slayer 10 | Poison; one-off Monstrous cave-crawler variant after Smoking Kills | weight `provisional/darkan`; count/gate closed |
| Cave horrors | 15 | D | Slayer 58; Cabin Fever | Light, Mos Le'Harmless cave, conditional witchwood-icon scream consequence | weight `provisional/darkan`; count/gate closed |
| Crawling hands | 5 | D | Slayer 5 | Ordinary, Skeletal, and Zombie variants with explicit route gates | weight `provisional/darkan`; count/gate closed |
| Dagannoths | 10 | D | baseline | Ordinary forms and explicit boss/context variants | weight `provisional/darkan`; count closed |
| Dust devils | 15 | D | Slayer 65 | Continuous Face mask, Masked earmuffs, or accepted Slayer-helmet damage gate | weight `provisional/darkan`; count/gate/target closed |
| Elves | 10 | 60–90 | Regicide unlock/route | Explicit Elf-warrior membership | weight `provisional/darkan`; count/gate closed |
| Fever spiders | 10 | D | Slayer 42; Rum Deal started for route | Slayer gloves; otherwise disease and repeated damage | weight `provisional/darkan`; exact assignment-time quest predicate `source_blocked` |
| Fire giants | 10 | D | baseline | Ordinary non-excluded contexts | weight `provisional/darkan`; count closed |
| Fungal magi | 10 | 83–136 | Magic 50 to receive | Neem-oil infestation/attack interaction | weight `provisional/darkan`; count/gate closed |
| Gargoyles | 15 | D | Slayer 75 | Rock-hammer finisher; quick-finisher still requires hammer | weight `provisional/darkan`; count/gate closed |
| Grifolapines | 8 | 60–100 | Slayer 88; Magic 60 | Polypore context and neem-oil interaction | membership/gates closed; count/weight `provisional/darkan` |
| Grifolaroos | 8 | 60–100 | Slayer 82; Magic 60 | Polypore context and neem-oil interaction | membership/gates closed; count/weight `provisional/darkan` |
| Grotworms | 15 | 72–109 | baseline | Young, ordinary, and Mature variants; bosses remain explicit | membership closed; count `abstraction/history-envelope`; weight `provisional/darkan` |
| Harpie bug swarms | 20 | D | Slayer 33 | Lit bug lantern to damage; assignment may precede Firemaking 33 | weight `provisional/darkan`; count/gate closed |
| Jungle strykewyrms | 12 | 80–110 | Slayer 73 | Attackable only on assignment; poison and tunnelling behavior | weight `provisional/darkan`; count/gate closed |
| Infernal mages | 10 | D | Slayer 45 | Ordinary | weight `provisional/darkan`; count/gate closed |
| Jellies | 15 | D | Slayer 52 | Ordinary | weight `provisional/darkan`; count/gate closed |
| Jungle horrors | 15 | D | Cabin Fever/Mos Le'Harmless | Three cosmetic forms remain one family | weight `provisional/darkan`; count/gate closed |
| Kalphites | 10 | D | baseline | Worker, soldier, guardian, and Queen; non-attackable larva excluded | weight `provisional/darkan`; count closed |
| Kurasks | 15 | D | Slayer 70 | Restricted weapons/ammunition; one-off Overlord variant | weight `provisional/darkan`; count/gate closed |
| Lesser demons | 10 | D | baseline | Ordinary and Revenant demon; Champion remains disputed | weight `provisional/darkan`; count closed |
| Mutated zygomites | 10 | 30–60 | Slayer 57; Lost City route | Fungicide below 20 LP with charge spend | membership/count/gate closed; weight `abstraction/common-baseline` |
| Shadow warriors | 10 | D | Legends' Quest | Ordinary Shadow warrior | membership/count/gate closed; weight `abstraction/common-baseline` |
| Trolls | 10 | D | baseline | Explicit ordinary mountain/ice/river/undead variants | weight `provisional/darkan`; count closed |
| Turoths | 15 | D | Slayer 55 | Restricted weapons/ammunition; one-off Mightiest variant | weight `provisional/darkan`; count/gate closed |
| Vyrewatch | 10 | 89–106 | Slayer 67; Branches of Darkmeyer route | Restricted weapons; explicit Vyrewatch/Vyrelady/Vyrelord boundary | membership/gate closed; count/weight `provisional/darkan` |
| Warped tortoises | 10 | D | Slayer 56; Path of Glouphrie | Crystal chime creates a 45-second vulnerability window | weight `provisional/darkan`; count/gate closed |

Darkan's 32 rows total 368. Adding the two missing cutoff families at the
common 10-point baseline produces `368 + 10 + 10 = 388`.

## Period master evidence

RuneScape Wiki, `Chaeldar`, oldid `6493174`, timestamp
`2012-10-29T17:31:51Z`, is the cutoff master page:
<https://runescape.wiki/w/Chaeldar?oldid=6493174>.

It establishes Combat 70, the 32-row table and ordinary counts, the point
paragraph, and the experimental-fungicide challenge. `Lost City` oldid
`6564063`, timestamp `2012-11-16T19:00:23Z`, makes Zanaris and Chaeldar
access explicit:
<https://runescape.wiki/w/Lost_City?oldid=6564063>.

`Slayer points` oldid `6520963`, timestamp `2012-11-02T15:54:41Z`, gives
Chaeldar's 10/50/150 schedule:
<https://runescape.wiki/w/Slayer_points?oldid=6520963>. The cutoff Chaeldar
page's anonymous oldid `6328382`, timestamp `2012-10-01T07:55:30Z`, changed
150 to 100 without changing the claimed 16-point average:
<https://runescape.wiki/w/Chaeldar?oldid=6328382>. With 45 ordinary tasks,
four tenth tasks and one fiftieth task, only
`(45×10 + 4×50 + 150) / 50 = 16`; `100` yields 15.

The cutoff cross-master `Slayer assignment` table, oldid `6303852`, timestamp
`2012-09-27T13:49:08Z`, independently corroborates the 32-family table and
most required equipment/variants:
<https://runescape.wiki/w/Slayer_assignment?oldid=6303852>.

Grifolapines and Grifolaroos are absent from those stale overview tables, but
their individual cutoff pages explicitly mark Chaeldar and agree with Darkan:

- `Grifolapine`, oldid `6548124`, timestamp `2012-11-11T15:39:49Z`,
  requires Slayer 88 and Magic 60 to receive:
  <https://runescape.wiki/w/Grifolapine?oldid=6548124>.
- `Grifolaroo`, oldid `6377087`, timestamp `2012-10-09T23:49:53Z`,
  requires Slayer 82 and Magic 60 to receive:
  <https://runescape.wiki/w/Grifolaroo?oldid=6377087>.

## Material count and gate conflicts

- Elves are `60–90`, not Darkan's `60–150`. `Regicide` oldid `6505748`
  records the ability to receive Chaeldar/Sumona Elf assignments at 60–90:
  <https://runescape.wiki/w/Regicide?oldid=6505748>. Darkan's later
  Mourning's Ends Part I gate is rejected.
- Grotworm edits accumulated observed envelopes from `90–?` through
  `72–109`. Darkan's `70–100` excludes the observed 109. The historical
  generator range remains `source_blocked`; `72–109` is explicitly the
  smallest observed-history envelope, not a recovered algorithm. Key oldids
  are `5655801`, `5668364`, `5850489`, `5851060`, `5854189`, `5870806`,
  and `5880781`.
- Fungal-mage observations closed at `83–136`, matching Darkan, but the
  individual cutoff page also requires Magic 50 to receive the task:
  `Fungal mage` oldid `6580164`, timestamp `2012-11-19T05:48:51Z`:
  <https://runescape.wiki/w/Fungal_mage?oldid=6580164>.
- `Vyrewatch` oldid `6552643`, timestamp `2012-11-13T22:48:45Z`, requires
  Slayer 67 for assignment and establishes restricted weapons:
  <https://runescape.wiki/w/Vyrewatch?oldid=6552643>. The Branches of
  Darkmeyer cutoff quest reward supplies the assignment unlock. Darkan's
  quest-only family gate omits Slayer 67; its `89–106` count is retained only
  as a provisional implementation value.
- `Braindeath Island` oldid `5905468`, timestamp `2012-07-08T10:26:40Z`,
  says the only Fever-spider location becomes accessible by starting Rum Deal:
  <https://runescape.wiki/w/Braindeath_Island?oldid=5905468>. Darkan's
  Cabin Fever gate is rejected. Whether the assignment roll checked a precise
  Rum Deal stage remains `source_blocked`.

Cutoff `Talk:Chaeldar` oldid `4946880`, timestamp
`2011-11-18T03:58:20Z`, explains that the early count ranges were accumulated
from player observations and rejects its own rarity column as inadequately
investigated:
<https://runescape.wiki/w/Talk:Chaeldar?oldid=4946880>. Its reports of many
Jelly tasks, one Blue-dragon task in roughly 100, and a count-less Vyrewatch
assignment are clues, not hidden weights.

## Distinctive obligation pins

The most consequential individual pages are:

- `Banshee`, oldid `6589075`: protective headgear, unprotected
  Constitution-derived damage and combat-stat drains:
  <https://runescape.wiki/w/Banshee?oldid=6589075>.
- `Cave horror`, oldid `6550392`: Slayer 58, Cabin Fever, light and the
  conditional witchwood-icon scream:
  <https://runescape.wiki/w/Cave_horror?oldid=6550392>.
- `Fever spider`, oldid `6469080`: Slayer 42, Slayer-glove protection,
  disease and repeated unprotected damage:
  <https://runescape.wiki/w/Fever_spider?oldid=6469080>.
- `Gargoyle`, oldid `6579781`: Slayer 75 and the rock-hammer finisher:
  <https://runescape.wiki/w/Gargoyle?oldid=6579781>.
- `Jungle strykewyrm`, oldid `6588104`: Slayer 73, assignment-only
  attackability, poison and tunnelling:
  <https://runescape.wiki/w/Jungle_strykewyrm?oldid=6588104>.
- `Kurask`, oldid `6581220`, and `Turoth`, oldid `6565315`: restricted
  weapon/ammunition sets:
  <https://runescape.wiki/w/Kurask?oldid=6581220> and
  <https://runescape.wiki/w/Turoth?oldid=6565315>.
- `Mutated zygomite`, oldid `6530349`: Slayer 57 and fungicide below 20 LP:
  <https://runescape.wiki/w/Mutated_zygomite?oldid=6530349>.
- `Warped tortoise`, oldid `6547916`: Slayer 56, Path of Glouphrie and
  crystal-chime vulnerability:
  <https://runescape.wiki/w/Warped_tortoise?oldid=6547916>.
- `Crawling hand`, oldid `6530506`: the level/LP/Slayer-XP tuples
  `7/150/15`, `8/160/16`, `11/180/18`, and `12/190/19`:
  <https://runescape.wiki/w/Crawling_hand?oldid=6530506>.

## Challenge boundary

Chaeldar's challenge is outside the ordinary weighted pool. It requires exactly
ten Mutated zygomites, experimental spray at 20 LP or below, three random
outcomes—rage/partial healing and faster attacks, full healing, or immediate
death—and a return report to Chaeldar. It awards 10,000 Slayer XP, 25 bonus
points after Smoking Kills, and one streak task. The quick-finisher unlock does
not apply.

The prerequisite, offer probability, outcome probabilities, rage duration,
attack-speed change and partial-heal magnitude remain `source_blocked`. The
owner-authorized five-task/10% challenge abstraction in the Slayer contract is
implementation-only.

## Emulator evidence and limits

Darkan:

- `Task.java:108-139` has 32 executable Chaeldar rows totaling 368;
- `Master.java:26` corroborates Combat 70 and 10/50/150 points;
- `TaskMonster.java` supplies many family gates, but omits the Magic gates for
  Fungal magi and both Grifo families, uses the wrong Elf and Fever-spider quest
  gates, and omits Vyrewatch's Slayer 67;
- `TaskMonster.java:97` leaves Mutated zygomites as a comment;
- Shadow warriors are an executable family but have no Chaeldar task row; and
- `SlayerTaskManager.java:116-146` executes the table, but display-name
  substring credit is too broad for the future stable variant registry.

Pinned repository:
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`,
Slayer files pinned at commit `c343a917712649675989315009ce250639e0850f`.

game-main has no Chaeldar assignment data: missing masters resolve to an empty
list, and her dialogue registration is commented out. Its master enum
corroborates Combat 70 and 10/50/150 points, while its Lost City reward copy
incorrectly says 75. It is useful for shared Combat definitions, not Chaeldar
pool completeness.

Pinned snapshot:
`/Users/ArmanTarkhanian1/Downloads/game-main`; `SlayerMaster.kt` SHA-256
`066b13c9a288fcd9603413b2fe7c1af1b9798a9dbd205764bbcaa0246ce8c8b9`.

## Current AnkiScape readiness

This audit does **not** authorize a partial live Chaeldar role.

Only Cave crawler, Crawling hand and Lesser demon are complete ordinary Combat
candidates. Banshee exists but has no earmuff/helmet consequence. The generic
Baby dragon row collapses blue and red source ids and therefore cannot certify
stable Blue-dragon-family membership. The other 29 families have no direct
target. No current target has Slayer family binding, so end-to-end readiness is
0/34.

The existing Combat schema also lacks quest/player assignment gates,
protection-item consequences, restricted weapons, finishers and contexts. The
stable assignment-family registry and live master generator do not exist.

This source pass found and fixed one independent Combat-data defect. The live
level-8 Crawling hand copied game-main's conflicting 12 Slayer XP even though
the cutoff tuple is level 8, 160 LP and 16 Slayer XP. The row now carries 16
and cites oldid `6530506`; a focused regression pins all four fields.

Banshee's missing protection behavior is deliberately not patched with a
partial max-hit tweak: its cutoff contract includes Constitution-derived
damage, multiple combat-stat drains, ranged scream behavior and several
qualifying head items. Baby-blue identity likewise needs a stable variant
registry rather than renaming a row that currently represents multiple source
ids.

No owner-level design question emerged. Remaining work is source/data and
implementation: build the stable family/variant registry, add the 29 absent
families, split the generic dragon identity, implement the protective,
restricted-weapon, finisher and context loops, and certify the complete role
before exposing Chaeldar.
