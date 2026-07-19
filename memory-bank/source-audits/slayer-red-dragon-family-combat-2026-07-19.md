# Slayer Red dragon family Combat source audit — 2026-07-19

## Decision

Implement the ordinary level-152 Red dragon and the level-48 Baby red dragon
together as Sumona's twentieth executable family. The cutoff adult page
explicitly permits Baby red dragons as assignment substitutes. The adult
preserves dragonfire; the baby is melee-only and must not inherit it.

This family slice does not add locations, Wilderness behavior, dungeon fees,
quest routes, construction-dungeon variants, challenge drops, or
Daemonheim/Dungeoneering. No owner-facing design choice is required.

## Period authority

RuneScape Wiki `Red dragon`, oldid
[`6506523`](https://runescape.wiki/w/Red_dragon?oldid=6506523), timestamp
`2012-10-30T20:48:20Z`, is inside the frozen cutoff. Literal wikitext
establishes:

- combat level 152, 1,400 LP, and 142.5 Slayer XP;
- aggressive six-tick melee plus dragonfire;
- a 158-LP melee maximum and 500-plus dragonfire;
- non-poisonous attacks and susceptibility to player poison;
- guaranteed Dragon bones and Red dragonhide;
- Sumona assignment and Baby red dragon substitution; and
- exclusion of the separately linked Daemonheim variant.

RuneScape Wiki `Baby red dragon`, oldid
[`6516030`](https://runescape.wiki/w/Baby_red_dragon?oldid=6516030),
timestamp `2012-11-01T11:24:19Z`, establishes combat level 48, 500 LP,
50 Slayer XP, six-tick melee, a 54-LP maximum, no dragonfire, guaranteed Baby
dragon bones, and the distinction from the level-65 player-owned-house
variant.

The rev-742 cache independently contains the ordinary Red dragon IDs 53 and
4669–4672 and Baby red dragon IDs 1589, 3588, 4667, and 4668, each with
`Attack`. The marked level-scaled Red dragons 10815–10820 are separate
contexts and are excluded.

## Executable combat definitions and conflict

Darkan commit `a802b254cd2bf90d08dda3d56638db2b09158c0b` provides:

- `data/npcs/combatdefs/uncategorized/red_dragon/red_dragon_(152).json:1-31`:
  1,400 LP, Attack/Strength/Defence 130, Magic/Ranged 1, melee style, and
  59-tick respawn;
- `developer-information/npcListBonuses.txt:55`: adult
  stab/slash/crush/magic/ranged defences of 50/70/70/60/50;
- `data/npcs/combatdefs/uncategorized/baby_red_dragon/`
  `baby_red_dragon_(48) (noanims).json:1-30`: 500 LP,
  Attack/Strength/Defence 40, Magic/Ranged 1, 54 maximum, melee style, and
  59-tick respawn; and
- `developer-information/npcListBonuses.txt:1591`: baby defences of
  30/50/50/40/30.

Darkan's adult record says a 144-LP maximum, conflicting with the direct
cutoff page's explicit 158. Per the corroboration gate, the emulator value is
a lead rather than authority to overwrite the period record. AnkiScape
therefore preserves 158 and records the conflict in both data and tests.

## Dragonfire

`src/main/java/com/rs/game/content/world/npcs/LeatherDragonCombat.java:34-62`
binds Red dragons to the shared leather-dragon script. At adjacent range,
`Utils.getRandomInclusive(3)` produces one dragonfire branch and three melee
branches. The 1/4 selector remains labeled `provisional/darkan`: the cutoff
page proves dragonfire and its damage envelope, but not a period numeric
selection rate.

The adult reuses the already-live leather-dragon protection seam:

- no protection: 0–500 LP;
- one shield or ordinary antifire layer: 0–50 LP; and
- full protection: zero dragonfire damage.

The baby has no dragonfire definition.

## Drops

Darkan `data/npcs/drops/red_dragon.json:1-271` supplies guaranteed Dragon
bones and Red dragonhide plus one 128-slot ordinary selector:

| Output | Slots |
|---|---:|
| Coins ×196 | 39 |
| Coins ×66 | 28 |
| Coins ×330 | 9 |
| Rune arrows ×4 | 8 |
| Law runes ×4 | 5 |
| Darkan gem table | 5 |
| Mithril 2h sword | 4 |
| Blood runes ×2 | 4 |
| Mithril hatchet | 3 |
| Mithril battleaxe | 3 |
| Rune darts ×8 | 3 |
| Death runes ×5 | 3 |
| Chocolate cakes ×3 | 3 |
| Darkan herb table | 2 |
| Mithril javelins ×20 | 1 |
| Mithril kiteshield | 1 |
| Adamant platebody | 1 |
| Rune longsword | 1 |
| Coins ×690 | 1 |
| Adamant bar | 1 |
| Empty | 3 |

The executable rows total 125/128. The three empty slots are explicit rather
than renormalized.

`data/npcs/charmDrops.txt:139` supplies thresholds `18-44-17-4`. Lossless
enumeration of Darkan's inclusive multi-threshold choice produces a
1,212-slot selector: 73 Gold, 385 Green, 67 Crimson, 15 Blue, and 672 empty.
Each successful charm output has quantity one.

The independent 1/2,000 Red dragon egg row is retained with the period
Summoning-99 gate. `src/main/java/com/rs/utils/NPCClueDrops.java:138`
supplies an independent 1/128 hard-clue roll. Challenge-only scales,
quest-only tail bones, spins, and rarity-only rows without executable
denominators are excluded.

Darkan `data/npcs/drops/baby_red_dragon.json:1-19` supplies only guaranteed
Baby dragon bones for the ordinary baby representative.

## Assets

`combatenemies/red_dragon.png` uses the pre-cutoff
`File:Red dragon old 5.png` revision from `2010-07-05T19:36:16Z`, SHA-1
`dfd0b198c9534a7667adffaf4191bba26c4b8f81`.

`combatenemies/baby_red_dragon.png` uses the pre-cutoff
`File:Baby red dragon.png` revision from `2011-12-11T10:26:02Z`, SHA-1
`83cf8e56994cdab47ea1d81364f3c0a22ea16b46`.

Both are fetched and normalized through the standard Combat-enemy asset
pipeline, with complete entries in `assets_provenance.json`.

## Readiness and design result

Registering both representatives advances Sumona from 19/37 to 20/37.
Seventeen families remain blocked, and Sumona stays hidden and
unrenormalized.

No owner-facing design gap emerged.
