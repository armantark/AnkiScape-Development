# Combat Goblin Level 2 Source Audit - 2026-06-23

## Scope

This slice imports only `goblin_level_2.plugin.kts`. It intentionally splits
the armed and unarmed level-2 Goblins because the source shares one drop table
but gives the armed ID different Attack and Defence stats.

## Source Files

| Local source | Imported facts |
| --- | --- |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/goblin/goblin_level_2.plugin.kts` | Level-2 Goblin IDs, local drop table, attack speed, respawn, stats, bonuses, Slayer XP. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt` | Item constants for Goblin drops. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` | Bronze spear, Chef's hat, and Brass necklace equipment metadata. |

## Imported Enemy Contract

- `goblin_level_2_unarmed`: display `Goblin (unarmed)`, combat level 2,
  hitpoints 50, Attack 1, Strength 1, Defence 1, Magic 1, Ranged 1.
- `goblin_level_2_armed`: display `Goblin (armed)`, combat level 2,
  hitpoints 50, Attack 3, Strength 1, Defence 4, Magic 1, Ranged 1.
- Both rows use attack speed 4, respawn delay 35, Slayer XP 5.0, and the same
  source-backed drops.
- Bonuses for both rows: attack stab -21, attack crush -15, defence stab/slash/
  crush/magic/ranged -15.

## Drop Table

| Table | Slots |
| --- | --- |
| Guaranteed | Bones x1 |
| Main 1024 | Bronze sq shield x1 (24), Bronze spear x1 (32), Sling x1 (32), Water rune x6 (48), Body rune x7 (40), Earth rune x4 (24), Bronze bolts x8 (24), Coins x5 (224), Coins x9 (24), Coins x15 (24), Coins x20 (16), Coins x1 (8), nothing (272), Hammer x1 (120), Goblin book x1 (16), Goblin mail x1 (40), Chef's hat x1 (24), Beer x1 (16), Brass necklace x1 (8), Air talisman x1 (8) |
| Charms 1024 | Gold charm x1 (82), Green charm x1 (21), Crimson charm x1 (9), Blue charm x1 (1), nothing (911) |
| Tertiary 1024 | Clue scroll (easy) x1 (6), nothing (1018) |

## Asset and Registry Notes

- Existing item registries cover Bronze sq shield, Sling, Water rune, Body rune,
  Earth rune, Bronze bolts, Coins, Hammer, Goblin mail, Beer, Air talisman,
  charms, and Clue scroll (easy).
- This slice adds Combat item registrations and icons for Bronze spear,
  Goblin book, Chef's hat, and Brass necklace.
- Bronze spear is registered as a two-handed weapon with item id 1237, attack
  stab/slash/crush 5, defence stab/slash 1, melee strength 6, and attack speed
  5. Chef's hat and Brass necklace use their zero-bonus source equipment rows.

## Deferred

- Higher-level Goblins remain deferred because their tables include
  `minorHerbTable`, which needs first-class shared/global drop-table support.
- Farmer and Al-Kharid Warrior remain deferred for the same shared-table reason.
