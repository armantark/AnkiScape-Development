# Combat White knights source audit - 2026-06-23

## Scope

Added ordinary fightable White knight variants from local 2011Scape plugin
sources:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/white_knight_level_36.plugin.kts`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/white_knight_level_38.plugin.kts`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/white_knight_level_39.plugin.kts`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/white_knight_level_42.plugin.kts`

All four plugins register normal `on_npc_death` drop callbacks and a human
death sound. No White Knight rank, quest, faction, or membership gate appears in
these combat-definition files, so the rows are safe as ordinary source-backed
Combat targets.

## Combat rows

- `white_knight_level_36`: `Npcs.WHITE_KNIGHT`, combat level 36, 520 LP,
  Attack 27, Strength 29, Defence 21, attack speed 7, respawn 50.
- `white_knight_level_38`: `Npcs.WHITE_KNIGHT_3348`, combat level 38, 520 LP,
  Attack 30, Strength 29, Defence 25, attack speed 7, respawn 50.
- `white_knight_level_39`: `Npcs.WHITE_KNIGHT_3349`, combat level 39, 520 LP,
  Attack 32, Strength 29, Defence 27, attack speed 7, respawn 50.
- `white_knight_level_42`: `Npcs.WHITE_KNIGHT_3350`, combat level 42, 520 LP,
  Attack 32, Strength 29, Defence 27, attack speed 7, respawn 50.

All four source rows use `attackBonus = 30` and `strengthBonus = 31`. Following
the existing Combat data convention for source `attackBonus`, this maps to
`attack_stab`, `attack_slash`, and `attack_crush` of 30, with
`melee_strength` 31. Shared defences are Stab 83, Slash 76, Crush 70, Magic
-11, and Ranged 74.

## Drop tables

Each row guarantees Bones and has a main table plus a `Tertiary` clue table with
`Clue scroll (easy)` at 8/1024.

The level-36 main table exactly matches the declared `total(128)`. The other
three sources declare `total(128)` but build a different active entry index:

- Level 38 active slots sum to 130.
- Level 39 active slots sum to 127.
- Level 42 active slots sum to 127.

The local source `DropTableFactory` logs a total mismatch but rolls with
`entries.last().index`, so the active slot sum is the runtime denominator. The
AnkiScape tables preserve that runtime behavior, matching the existing Guard
and Black knight mismatch precedent.

Nested source tables are reused directly:

- `Herbs.minorHerbTable`
- `Seeds.allotmentSeedTable`
- `Gems.gemTable` without Ring of Wealth modifiers

## Item registry

`Half an apple pie` is a real source food item:

- `Items.HALF_AN_APPLE_PIE`
- `Food.HALF_AN_APPLE_PIE(item = Items.HALF_AN_APPLE_PIE, heal = 70)`

The item is registered as a Combat food extra with a fetched icon at
`combatitems/half_an_apple_pie.png` and provenance in `assets_provenance.json`.

## Verification hooks

Targeted coverage was added for:

- Combat row stats, bonuses, source notes, nested tables, and active slot totals.
- Drop rolling for quantity ranges, nested allotment seed table, nested gem
  table, and tertiary clue table.
- Target metadata tooltips for level 36 and level 42 variants.
- Combat item registry and icon presence for `Half an apple pie`.
