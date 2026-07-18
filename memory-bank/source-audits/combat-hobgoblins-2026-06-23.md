# Combat Hobgoblins source audit - 2026-06-23

## Scope

Added the ordinary fightable level-28 Hobgoblin rows from local 2011Scape
source:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/hobgoblin_unarmed_level_28.plugin.kts`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/hobgoblin_armed_lvl_28.plugin.kts`

Both plugins register normal pre-death and death-drop callbacks. The armed row
has source aggro radius 4, which is recorded in provenance but does not change
review combat yet.

## Combat rows

- `hobgoblin_unarmed`: 290 LP, Attack 22, Strength 24, Defence 24, Magic 1,
  Ranged 1; attack speed 4, respawn delay 50; 29 Slayer XP.
- `hobgoblin_armed`: 490 LP, Attack 33, Strength 31, Defence 36, Magic 1,
  Ranged 1; attack speed 6, respawn delay 30; Attack Stab 8, Attack Crush 10,
  Defence Stab 1, Defence Slash 1; 49 Slayer XP.

The XP values were closed on 2026-07-18 from RuneScape Wiki `Hobgoblin`
oldid `6448782`, timestamp `2012-10-21T14:16:05Z`. Its literal infobox maps
the ordinary 290/490-LP variants to 29/49 Slayer XP. The independent OSRS
lineage table retains the same two values; it corroborates rather than supplies
the pre-EOC rows.

Both source files omit Magic and Ranged stats, so they use AnkiScape's existing
default `1` convention for rows that already provide melee-critical Attack,
Strength, and Defence stats.

## Drop tables

Both rows guarantee Bones.

The unarmed main table declares `total(128)` but builds 127 active slots at
runtime. AnkiScape stores the active 127-slot denominator. It includes Bronze
spear, Iron sword, Steel dagger, Iron spear, Steel spear, Steel longsword,
runes, Coins, Limpwurt root, Goblin mail, nested minor herb, allotment seed, and
gem tables. Its Charms table declares `total(1024)` but builds 1000 active
slots; AnkiScape stores 1000.

The armed main table is an exact 128-slot table. It includes Iron sword, Steel
dagger, Steel longsword, runes, Iron javelin x5, nested minor herb and uncommon
seed tables, Coins, Limpwurt root, Goblin mail, and the gem table. Its Charms
table is an exact 1000-slot table.

## Item registry

Added Combat item/icon registration for:

- Iron javelin, kept material-category and inventory-only until thrown-weapon
  combat is widened.
- Iron spear and Steel spear, registered as equipment and added to
  `equipment_data.py` with source item ids, two-handed spear metadata, attack
  requirements, attack speed, and melee bonuses from `data/cfg/items.yml`.

The fetched icons are:

- `combatitems/iron_javelin.png`
- `combatitems/iron_spear.png`
- `combatitems/steel_spear.png`

## Verification hooks

Targeted coverage was added for:

- Source stats, bonuses, timing, aggro provenance, and runtime drop denominators.
- Exact 29/49 Slayer XP and the pinned pre-EOC oldid in both live variants.
- Nested minor herb, allotment seed, uncommon seed, and gem table references.
- Deterministic drop rolls through a normal main slot, Charms table, and nested
  uncommon seed table.
- Combat target tooltip metadata for Hobgoblin drops and source file provenance.
- Combat item registry, icon presence, and spear equipment metadata.
