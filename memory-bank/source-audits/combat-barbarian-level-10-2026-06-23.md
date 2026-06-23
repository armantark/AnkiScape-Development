# Combat Barbarian Level 10 Source Audit - 2026-06-23

## Scope

This slice imports the ordinary level 10 Barbarian weapon variants as one
separate `barbarian_level_10` Combat target. It intentionally does not merge the
row into the earlier level 8/9 `barbarian` target because the level 10 source
rows have different stats, bonuses, attack speed, and respawn timing.

## Source Files

| Local source | Imported facts |
| --- | --- |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_greataxe_lvl_10.plugin.kts` | NPCs `BARBARIAN_3250`, `BARBARIAN_3251`, `BARBARIAN_3252`, `BARBARIAN_3257`, and `BARBARIAN_3258`; shared level 10 stats, bonuses, timing, and drop table. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_spear_lvl_10.plugin.kts` | NPCs `BARBARIAN_3261` and `BARBARIAN_3262`; same stats, bonuses, timing, and drop table with spear animations. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_twohand_sword_lvl_10.plugin.kts` | NPC `BARBARIAN_3256`; same stats, bonuses, timing, and drop table with two-hand sword animation. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_2hsword_lvl_10.plugin.kts` | NPC `BARBARIAN_3255`; same stats, bonuses, timing, and drop table with 2h sword animation. |

## Imported Enemy Contract

- AnkiScape exposes one `barbarian_level_10` target because all four level 10
  weapon-variant files share identical combat stats, bonuses, timing, and drops.
- Stats: 180 lifepoints, Attack 8, Strength 7, Defence 3, Magic 1, Ranged 1.
- Timing: attack speed 4, respawn delay 50.
- Bonuses: attack stab 9, attack crush 15, defence slash 3, defence crush 2,
  defence magic -3, defence ranged 2.
- Guaranteed drops: Bones x1.
- Main table total: 1024 slots.
- Charm table total: 1000 slots.
- Tertiary table total: 128 slots.

## Drop Table

| Table | Slots |
| --- | --- |
| Guaranteed | Bones x1 |
| Main 1024 | Bronze hatchet x1 (48), Staff x1 (32), Iron mace x1 (8), Chaos rune x2 (32), Bronze arrows x15 (24), Earth rune x2 (24), Fire rune x5 (16), Mind rune x5 (16), Law rune x2 (8), Coins x5 (341), Coins x8 (76), Coins x17 (45), Coins x27 (26), nothing (288), Tin ore x1 (8), Bear fur x1 (8), Beer x1 (8), Cooked meat x1 (8), Ring mould x1 (8) |
| Charms 1000 | Gold charm x1 (50), Green charm x1 (10), Crimson charm x1 (5), Blue charm x1 (5), nothing (930) |
| Tertiary 128 | Clue scroll (easy) x1 (1), nothing (127) |

## Asset and Registry Notes

- No new item assets or registry rows were needed. This target reuses the
  already-registered Barbarian drop items, runes, Bronze arrows, food, crafting
  tools, charms, currency, and easy clue scroll.
- The source files differ only in ids and weapon animations after the shared
  stats/drop contract, so this pass records all four file names in the target
  source string instead of exposing four duplicate AnkiScape rows.

## Deferred

- Weapon-animation-specific presentation remains deferred because the current
  Combat target list does not expose enemy animation or model variants.
- Location-specific Barbarian spawn grouping remains a later world-map/UI pass;
  this target stays grouped under `Humanoids`.
