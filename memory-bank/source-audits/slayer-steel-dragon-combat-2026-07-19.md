# Slayer Steel dragon Combat source audit — 2026-07-19

## Decision

Implement the ordinary pre-EOC level-246 Steel dragon as
Duradel/Lapalok's fourteenth executable family. Reuse the settled metal-dragon
dragonfire reducer, preserve the guaranteed five-bar drop, close Darkan's
five-slot ordinary-table gap with one explicitly provisional OSRS-lineage
row, and keep the master hidden until every family is ready.

The Combat model has no player-to-enemy distance. As already settled for
Bronze and Iron dragons, it represents the encounter at melee distance and
uses Darkan's exact adjacent 1/2 melee-versus-dragonfire selector. This is the
existing pattern-determined metal-dragon abstraction.

Kuradal's Dungeon, the Brimhaven resource dungeon, player-owned-house forms,
quest-only tail bones, post-cutoff drops, and Daemonheim/Dungeoneering are
excluded from this ordinary certifying target.

## Period authority

RuneScape Wiki `Steel dragon`, oldid
[`6582075`](https://runescape.wiki/w/Steel_dragon?oldid=6582075), timestamp
`2012-11-19T08:09:42Z`, is the nearest revision strictly before the frozen
cutoff.

The period revision establishes:

- combat level 246, 2,100 LP, and 220.4 Slayer XP;
- aggressive six-tick melee plus long-range and melee-range dragonfire;
- a 225-LP infobox melee maximum and 490-LP unprotected dragonfire maximum;
- non-poisonous attacks and susceptibility to player poison;
- Fire-spell, stab, and crush weakness context;
- guaranteed Dragon bones and five Steel bars;
- assignment by Duradel/Lapalok and Kuradal; and
- an ordinary main-drop set including the commonly reported Coins x470 and
  Coins x650 rows.

The prose later says a 229-LP melee maximum, conflicting with the same
revision's 225-LP infobox. Darkan's executable definition independently gives
225, so the corroborated infobox value wins.

RuneScape Wiki `Dragonfire`, oldid `6534496`, timestamp
`2012-11-04T21:56:22Z`, remains the shared metal-dragon authority: Protect from
Magic does not protect against metal-dragon breath; one shield or ordinary
antifire layer is partial protection; shield plus antifire or Super antifire
is full protection.

## Executable combat definition

Darkan commit `c343a917712649675989315009ce250639e0850f` provides the
ordinary NPC record:

- `data/npcs/combatdefs/uncategorized/steel_dragon.json`: 2,100 LP,
  Attack/Strength/Defence 215, Magic 100, Ranged 1, 225 maximum, aggressive
  behavior, and 59-tick respawn;
- `developer-information/npcListBonuses.txt:1594,3592`: exact
  stab/slash/crush/magic/ranged defences of 50/70/70/30/90; and
- `src/main/java/com/rs/game/content/world/npcs/MetalDragonCombat.java:41-61`:
  one of two adjacent attacks is melee and the other is dragonfire, with the
  shared 0-50 partial and zero full-protection tiers.

Rev-742 NPC definitions independently contain attackable level-246 Steel
dragons at IDs 1592 and 3590. The frozen 490-LP unprotected breath is
represented by the already-settled conservative 500-LP metal-dragon envelope,
not by Darkan's possible 600-LP roll.

## Drops

Darkan `data/npcs/drops/steel_dragon.json` supplies guaranteed Dragon bones and
five Steel bars plus 123 declared slots of a 128-slot ordinary selector:

| Output | Slots |
|---|---:|
| Rune javelins x7 | 20 |
| Blood runes x20 | 19 |
| Coins x470 | 17 |
| Super attack (3) | 13 |
| Runite limbs | 8 |
| Rune darts (p) x12 | 7 |
| Runite bolts x2-12 | 6 |
| Soul runes x5 | 5 |
| Rune mace | 4 |
| Darkan standard rare table | 4 |
| Darkan gem table | 4 |
| Rune knives x7 | 3 |
| Runite bar | 3 |
| Super defence (2) | 3 |
| Adamant kiteshield | 2 |
| Rune hatchet | 2 |
| Rune full helm | 1 |
| Curry | 1 |
| Curry x2 | 1 |

The file declares every row against 128 but totals only 123. It is therefore
not a complete executable selector by itself.

The current
[OSRS Steel dragon table](https://oldschool.runescape.wiki/w/Steel_dragon)
matches those 19 rows, quantities, and rates row-for-row and supplies a
five-slot conditional row. OSRS revision `4153370`,
`2017-06-11T22:35:54Z`, first records Coins x650 on the fork; revision
`4912720`, `2017-10-09T06:09:02Z`, records that post-2016 Dragon-javelin-head
drops replace that coin branch only after Monkey Madness II; and revision
`9122199`, `2019-04-16T19:00:54Z`, records the exact 5/128 denominator.
The current page labels its rates as Jagex-provided and has no listed
Steel-dragon drop-table replacement before that conditional quest addition.

Because the target existed in the 2007 fork, the period page independently
attests Coins x650, Darkan independently declares a 128-way table with exactly
five missing slots, and every other OSRS row matches Darkan, AnkiScape fills
the gap with Coins x650 at 5/128. This row is explicitly
`provisional/osrs-lineage`; it is not described as historically closed. The
post-cutoff Dragon-javelin-head replacement is excluded.

`data/npcs/charmDrops.txt:152` supplies thresholds `14-35-14-3`, and
`CharmDrop.java:43-49` makes Steel-dragon charms quantity three. Lossless
enumeration of the inclusive multi-threshold chooser produces a 1,212-slot
selector: 56 Gold, 308 Green, 56 Crimson, 12 Blue, and 780 empty.

The independent tertiary rolls are:

- Dragon plateskirt, 1/512;
- Dragon platelegs, 1/512;
- Draconic visage, 1/10,000;
- hard clue, 1/64; and
- elite clue, 1/500.

The first three come from `steel_dragon.json`; the clue rates come from
`NPCClueDrops.java:148,194`. Period-visible rarity-only rows without an
executable denominator are not invented.

## Asset

`combatenemies/steel_dragon.png` uses the pre-cutoff
`File:Steel dragon.png` revision from `2011-11-29T04:55:54Z`, source SHA-1
`5912e48a6da4ecff30b93fc0a761f219a4de41ab`. The standard Combat-enemy
fetcher normalizes it to 48x48 and records the source in
`assets_provenance.json`.

## Readiness and design result

Registering `steel_dragon` advances Duradel/Lapalok from 13/35 to 14/35.
Twenty-one families remain blocked, and the master stays hidden and
unrenormalized.

No owner-facing design gap emerged.
