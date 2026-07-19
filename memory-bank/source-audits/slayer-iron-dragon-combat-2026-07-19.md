# Slayer Iron dragon Combat source audit — 2026-07-19

## Decision

Implement the ordinary pre-EOC level-189 Iron dragon as Sumona's nineteenth
executable family. Reuse the settled metal-dragon dragonfire reducer, preserve
the guaranteed five-bar drop and exact lower-tier selectors, and keep the
master hidden until every family is ready.

The Combat model has no player-to-enemy distance. As already settled and
implemented for Bronze dragons, it represents the encounter at melee distance
and uses Darkan's exact adjacent 1/2 melee-versus-dragonfire selector. This is
the existing metal-dragon pattern, not a new design interpretation.

Kuradal's Dungeon, the Brimhaven resource dungeon, Ghorrock route effects,
quest-only tail bones, the Love Story pit variant, post-cutoff data, and
Daemonheim/Dungeoneering are excluded from this ordinary certifying target.

## Period authority

RuneScape Wiki `Iron dragon`, oldid
[`6530527`](https://runescape.wiki/w/Iron_dragon?oldid=6530527), timestamp
`2012-11-04T05:37:41Z`, is inside the frozen cutoff. Later revisions on
`2012-11-20` contain EOC-converted combat data and are excluded.

The period revision establishes:

- combat level 189, 1,650 LP, and 173.2 Slayer XP;
- aggressive six-tick melee plus long-range and melee-range dragonfire;
- a 203-LP melee maximum and 500-plus dragonfire;
- non-poisonous attacks and susceptibility to player poison;
- stab/fire-spell weakness context;
- guaranteed Dragon bones and five Iron bars;
- assignment by Sumona, Duradel/Lapalok, and Kuradal; and
- the ordinary Gielinor target is distinct from the level-204 Love Story pit
  variant and from Daemonheim Iron dragons.

The existing `Dragonfire` oldid `6534496`, timestamp
`2012-11-04T21:56:22Z`, remains the shared metal-dragon authority: Protect from
Magic does not protect against dragonfire; one shield or ordinary antifire
layer gives partial protection; shield plus antifire or super antifire gives
full protection.

## Executable combat definition

Darkan commit `c343a917712649675989315009ce250639e0850f` provides the
ordinary NPC record:

- `data/npcs/combatdefs/uncategorized/iron_dragon/iron_dragon_(189).json`:
  1,650 LP, Attack/Strength/Defence 165, Magic 100, Ranged 1, 203 maximum,
  aggressive behavior, and 59-tick respawn;
- `developer-information/npcListBonuses.txt:1591`: exact
  stab/slash/crush/magic/ranged defences of 50/70/70/30/90; and
- `src/main/java/com/rs/game/content/world/npcs/MetalDragonCombat.java:41-61`:
  one of two adjacent attacks is melee and the other is dragonfire, with the
  shared 0–50 partial and zero full-protection tiers.

The frozen 500-plus dragonfire envelope is represented conservatively as a
500-LP maximum, matching the already-live Bronze-dragon abstraction rather
than importing Darkan's possible 600-LP roll.

## Drops

Darkan `data/npcs/drops/iron_dragon.json` supplies guaranteed Dragon bones and
five Iron bars plus one 128-slot ordinary selector:

| Output | Slots |
|---|---:|
| Coins ×270 | 20 |
| Adamant javelins ×4 | 19 |
| Blood runes ×15 | 19 |
| Coins ×550 | 10 |
| Super strength (1) | 8 |
| Rune darts (p) ×9 | 7 |
| Adamant bolts ×2–12 | 6 |
| Soul runes ×3 | 5 |
| Runite limbs | 5 |
| Adamant 2h sword | 4 |
| Adamant hatchet | 3 |
| Adamant battleaxe | 3 |
| Rune knives ×5 | 3 |
| Adamant bars ×2 | 3 |
| Curry | 3 |
| Darkan gem table | 3 |
| Darkan standard rare table | 2 |
| Adamant sq shield | 1 |
| Rune med helm | 1 |
| Rune battleaxe | 1 |
| Coins ×990 | 1 |
| Empty | 1 |

The rows total 127/128, so the final empty slot is explicit rather than
renormalized.

`data/npcs/charmDrops.txt:97` supplies thresholds `12-32-13-3`, and
`CharmDrop.java` makes Iron-dragon charms quantity two. Lossless enumeration
of the inclusive multi-threshold chooser produces a 1,212-slot selector:
48 Gold, 282 Green, 54 Crimson, 12 Blue, and 816 empty.

The two rate-1/1,024 rows remain independent Dragon plateskirt and Dragon
platelegs rolls. The 1/10,000 Draconic visage remains independent.
`NPCClueDrops.java:134` supplies an independent 1/128 hard clue. Period-visible
rarity-only rows without an executable denominator are not invented.

## Asset

`combatenemies/iron_dragon.png` uses the pre-cutoff
`File:Iron dragon.png` revision from `2010-12-29T13:34:17Z`, SHA-1
`76c989a0a0730df9cb66ceb98e0cfd78edf77609`. The standard Combat-enemy fetcher
owns normalization and `assets_provenance.json`.

## Readiness and design result

Registering `iron_dragon` advances Sumona from 18/37 to 19/37. Eighteen
families remain blocked, and Sumona stays hidden and unrenormalized.

No owner-facing design gap emerged.
