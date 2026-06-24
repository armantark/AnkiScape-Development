# Combat Outlaw source audit - 2026-06-23

## Scope

Added the ordinary fightable Outlaw row from local 2011Scape source:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/outlaw_level_35.plugin.kts`

The plugin registers a normal `on_npc_death` drop callback, a human death sound,
and a shared combat definition for `Npcs.OUTLAW` through `Npcs.OUTLAW_5851`.
There is no quest, faction, Slayer, route, or required-item gate in this combat
definition, so it is safe as an ordinary source-backed Combat target.

## Combat row

- Target id: `outlaw`
- Display: `Outlaw`
- Combat level: 35
- Group: Humanoids
- Attack style: melee
- Attack speed: 4
- Respawn delay: 2
- Source XP multiplier: `0.025`
- Stats: 200 LP, Attack 35, Strength 30, Defence 25, Magic 1, Ranged 1
- Bonuses: Attack Crush -21, all other attack/defence bonuses default to 0

The row preserves the very small source `xpMultiplier = 0.025` by setting
`xp_multiplier` on the enemy data. The current combat engine already multiplies
damage XP by this field.

## Drop tables

The row guarantees Bones, then rolls a main table and a Charms table.

The source main table declares `total(128)` but its active slot entries sum to
127. The local source `DropTableFactory` logs a mismatch and rolls against the
last active entry index, so AnkiScape preserves `total: 127`, following the same
runtime-denominator convention used for Guard, Black knight, and White knight
mismatches.

Main table highlights:

- Bronze med helm 2/127
- Mind rune x9, Water rune x6, and Earth rune x5 at 2/127 each
- Coins at 12/127, 4/127, and 1/127
- Rope 46/127
- Fishing bait 15/127
- Cabbage 6/127
- Copper ore 2/127
- Knife 1/127
- Nested `Herbs.minorHerbTable` 32/127

Charms table:

- Gold charm 360/1000
- Green charm 30/1000
- Crimson charm 30/1000
- Blue charm 7/1000

## Verification hooks

Targeted coverage was added for:

- Source stats, source `xp_multiplier`, bonuses, and active drop denominator.
- Nested minor-herb rolls and Charms rolls.
- Combat target tooltip metadata for Rope, the nested herb table, charms, and
  source file provenance.
