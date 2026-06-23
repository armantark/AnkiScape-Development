# Combat Barbarian Source Audit - 2026-06-23

## Scope

This slice imports the ordinary level 8/9 Barbarian definitions only. The level
10 greataxe Barbarian has a different source file, stats, and drop table, so it
remains deferred until the broader Barbarian/Humanoid pass.

## Source Files

| Local source | Imported facts |
| --- | --- |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_lvl_8.plugin.kts` | NPC `BARBARIAN_5909`, combat level 8 row. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/barbarian_lvl_9.plugin.kts` | NPC `BARBARIAN_3263`, combat level 9 twin row. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt` | Item constants for Staff, Bear fur, Coins, runes, Bronze hatchet, Iron mace, Beer, Ring mould, and easy clue scroll. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` | Generic `Staff` equipment bonuses and attack speed. |

## Imported Enemy Contract

- AnkiScape exposes one `barbarian` target because the level 8 and level 9
  source files share the same stats, bonuses, respawn, and drop table.
- Stats: 140 lifepoints, Attack 6, Strength 5, Defence 5, Magic 1, Ranged 1.
- Timing: attack speed 6, respawn delay 25.
- Bonuses: attack stab 8, attack crush 10, defence stab 1, defence slash 1.
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

- `Bronze hatchet`, `Iron mace`, runes, `Bronze arrows`, `Tin ore`,
  `Cooked meat`, and `Ring mould` reuse existing skill/quest item registries.
- `Staff`, `Bear fur`, `Beer`, `Coins`, and `Clue scroll (easy)` are registered
  through Combat so Barbarian drops have Bank-visible item definitions and icons.
- Generic `Staff` uses item id 1379 and the exact `items.yml` equipment bonuses:
  attack slash -1, attack crush 7, attack magic 4, defence stab 2, defence slash
  3, defence crush 1, defence magic 4, melee strength 3, attack speed 5.

## Deferred

- The level 10 greataxe Barbarian remains deferred because it is not identical
  to the level 8/9 source rows.
- Barbarian location-specific spawn grouping is still a later world-map/UI pass;
  this target remains grouped under `Humanoids`.
