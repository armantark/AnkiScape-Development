# Slayer Black dragon Combat source audit — 2026-07-19

## Decision

Implement the ordinary level-227 Black dragon as Duradel's thirteenth
executable family and as a future Kuradal family dependency. The already-live
Baby black dragon and King Black Dragon remain valid family substitutes, but
this slice does not modify either representative.

This slice excludes Queen Black Dragon, locations, quest routes, lair access,
Wilderness behavior, Daemonheim/Dungeoneering, and post-cutoff variants. No
owner-facing design choice is required.

## Period authority

RuneScape Wiki `Black dragon`, oldid
[`6580941`](https://runescape.wiki/w/Black_dragon?oldid=6580941), timestamp
`2012-11-19T06:45:32Z`, is inside the frozen cutoff. Literal wikitext
establishes:

- combat level 227, 1,900 LP, and 199.4 Slayer XP;
- aggressive six-tick melee plus dragonfire;
- a 214-LP melee maximum and 500-plus dragonfire;
- non-poisonous attacks and susceptibility to player poison;
- guaranteed Dragon bones and Black dragonhide;
- Duradel and Kuradal assignment, with Baby black dragon and King Black
  Dragon substitution; and
- exclusion of the separately linked Daemonheim variant.

The period page also gates Black dragon eggs behind Summoning 99. It describes
the Draconic visage only with an estimate, so that estimate is not promoted to
an executable rate.

## Executable combat definitions

Darkan commit `c343a917712649675989315009ce250639e0850f` provides:

- `data/npcs/combatdefs/uncategorized/black_dragon/`
  `black_dragon_(227).json:1-31`: IDs 54 and 4673–4676, 1,900 LP, 214
  maximum, Attack/Strength/Defence 200, Magic 100, Ranged 1, melee style,
  aggression, and a 59-tick respawn;
- `developer-information/npcListBonuses.txt:56`: stab/slash/crush/magic/ranged
  defences of 50/70/70/60/50; and
- `src/main/java/com/rs/game/content/world/npcs/`
  `LeatherDragonCombat.java:34-62`: the shared adjacent leather-dragon melee
  and dragonfire selector.

The independently pinned game-main Black dragon definition agrees on the
1,900 LP, combat levels, and defences. Its four-tick attack speed and 30-tick
respawn conflict with the direct period six-tick value and Darkan's established
59-tick ordinary-dragon respawn. The period value and existing AnkiScape
dragon convention therefore remain authoritative.

## Dragonfire

`LeatherDragonCombat.java:34-62` binds Black dragons to the shared
leather-dragon script. At adjacent range, `Utils.getRandomInclusive(3)`
produces one dragonfire branch and three melee branches. The 1/4 selector
remains labeled `provisional/darkan`: the cutoff page proves dragonfire and
its damage envelope, but not a period numeric selection rate.

The target reuses the existing leather-dragon protection seam:

- no protection: 0–500 LP;
- one shield or ordinary antifire layer: 0–50 LP; and
- full protection: zero dragonfire damage.

## Drops

The independently pinned game-main file
`game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/`
`dragons/black_dragon_level_227.plugin.kts` supplies guaranteed Dragon bones
and Black dragonhide plus a complete 1,024-slot ordinary selector. Every row
divides losslessly by eight:

| Output | Slots |
|---|---:|
| Mithril 2h sword | 4 |
| Mithril hatchet | 3 |
| Mithril battleaxe | 3 |
| Rune knives ×2 | 3 |
| Mithril kiteshield | 1 |
| Adamant platebody | 1 |
| Rune longsword | 1 |
| Adamant javelins ×30 | 20 |
| Fire runes ×50 | 8 |
| Adamant darts (p) ×16 | 7 |
| Law runes ×10 | 5 |
| Blood runes ×15 | 3 |
| Air runes ×75 | 1 |
| Coins ×196 | 40 |
| Coins ×330 | 10 |
| Coins ×690 | 1 |
| Adamant bar | 3 |
| Chocolate cake | 3 |
| Darkan gem table | 3 |
| Darkan standard rare table | 2 |
| Empty | 6 |

The rows total exactly 128. Darkan's ordinary JSON omits eighteen selector
slots, so it is retained as corroboration rather than used as an incomplete
table.

Darkan `data/npcs/charmDrops.txt:22` supplies thresholds `9-27-7-1`, and
`src/main/java/com/rs/tools/old/CharmDrop.java:40-85` makes every successful
Black dragon charm quantity three. Lossless enumeration of the inclusive
multi-threshold choice produces a 1,212-slot selector: 42 Gold, 258 Green, 30
Crimson, 6 Blue, and 876 empty.

The independent 1/2,000 Black dragon egg row in
`data/npcs/drops/black_dragon.json` is retained with the period Summoning-99
gate. Darkan and game-main independently converge on a 1/10,000 Draconic
visage. `src/main/java/com/rs/utils/NPCClueDrops.java:132,170` supplies
independent 1/128 hard-clue and 1/500 elite-clue rolls.

## Asset

`combatenemies/black_dragon.png` uses the newest pre-cutoff revision of
`File:Black dragon.png`, timestamp `2010-12-28T12:10:25Z`, SHA-1
`89b2073177dac9d194efecaf4489e856beb0f20b`.

The standard Combat-enemy asset pipeline records the original URL, title,
timestamp, checksum, and transformation in `assets_provenance.json`.

## Readiness and design result

Registering the ordinary representative advances Duradel from 12/35 to 13/35.
Twenty-two families remain blocked, and Duradel stays hidden and
unrenormalized.

No owner-facing design gap emerged.
