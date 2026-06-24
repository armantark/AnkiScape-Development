# Combat Chaos dwarf source audit - 2026-06-23

## Scope

Added the ordinary fightable Chaos dwarf row from local 2011Scape source:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/chaos_dwarf_lvl_48.plugin.kts`

The plugin registers normal pre-death/death callbacks for `Npcs.CHAOS_DWARF`.
There is no quest, route, or required-item gate in this combat definition. The
source adds `SlayerAssignment.DWARF` with level 1 and 61.0 XP, which is stored as
enemy metadata only; Slayer task assignment remains deferred.

## Combat row

- Target id: `chaos_dwarf`
- Display: `Chaos dwarf`
- Combat level: 48
- Group: Humanoids
- Attack style: melee
- Attack speed: 4
- Respawn delay: 50
- Slayer XP metadata: 61.0
- Stats: 610 LP, Attack 38, Strength 42, Defence 28, Magic 1, Ranged 1
- Bonuses: Attack Stab 13, Attack Crush 9, Defence Stab 40, Defence Slash 34,
  Defence Crush 25, Defence Magic 10, Defence Ranged 35
- Aggro radius: 4, recorded in the source note

## Drop tables

The row guarantees Bones, then rolls a 128-slot main table and a Charms table.

Main table highlights:

- Steel full helm 2/128
- Mithril longsword 1/128
- Mithril sq shield 1/128
- Law rune x3 at 4/128
- Air rune x24, Chaos rune x10, Mind rune x37, Nature rune x9, Cosmic rune x3,
  Death rune x3, and Water rune x10
- Coins at 40/128, 18/128, 11/128, 10/128, 2/128, and 2/128
- Coal 1/128
- Muddy key 7/128
- Cheese 1/128
- Mithril bar 6/128
- Tomato 1/128

Charms table:

- Gold charm 100/1000
- Green charm 50/1000
- Crimson charm 20/1000
- Blue charm 20/1000

## Item registry

`Muddy key` was missing from the item registry. It is now registered as a Combat
material from `Items.MUDDY_KEY` and has a fetched icon at
`combatitems/muddy_key.png` with provenance in `assets_provenance.json`.

## Verification hooks

Targeted coverage was added for:

- Source stats, bonuses, Slayer XP metadata, and exact table totals.
- Muddy key and Charms drop rolls.
- Target tooltip metadata for Muddy key, Mithril bar, charms, and source file
  provenance.
- Combat item registry and icon presence for `Muddy key`.
