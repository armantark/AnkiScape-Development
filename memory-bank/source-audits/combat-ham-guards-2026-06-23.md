# Combat H.A.M. guards source audit - 2026-06-23

## Scope

Added the ordinary fightable H.A.M. guard rows from local 2011Scape source:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/ham_guard_level_12_18_22.plugin.kts`

The plugin registers normal pre-death and death-drop callbacks for
`Npcs.HAM_GUARD`, `Npcs.HAM_GUARD_1711`, and `Npcs.HAM_GUARD_1712`. There is no
quest, route, required-item, Slayer, or faction gate in this combat definition,
so these rows are safe as ordinary source-backed Combat targets.

## Combat rows

All three rows use melee, attack speed 7, respawn delay 25, and the shared H.A.M.
guard drop table.

- `ham_guard_level_12`: 150 LP, Attack 8, Strength 12, Defence 8, Magic 1,
  Ranged 1; Defence Stab/Slash/Ranged 5.
- `ham_guard_level_18`: 200 LP, Attack 14, Strength 18, Defence 12, Magic 1,
  Ranged 1; Defence Stab/Slash/Ranged 6.
- `ham_guard_level_22`: 300 LP, Attack 16, Strength 20, Defence 12, Magic 1,
  Ranged 1; Defence Stab/Slash/Ranged 7.

The source has no attack slash or melee strength bonus entries, so those local
fields stay at zero.

## Drop tables

The rows guarantee Bones, then roll a main table and a tertiary easy clue table.
The source main table declares `total(660)`, but its active entries sum to 648.
The local source `DropTableFactory` logs a mismatch and rolls against the active
entry index, so AnkiScape preserves `total: 648`, following the same convention
used for Guard, Black knight, Outlaw, and White knight mismatches.

Main table highlights:

- Bronze/Iron hatchets, daggers, and pickaxes
- Leather body, Steel hatchet, Steel dagger, and Steel pickaxe
- H.A.M. boots, cloak, gloves, hood, logo, robe, and shirt
- Bronze arrows x1-12 and Steel arrows x1-10
- Grimy guam, Grimy marrentill, Grimy tarromin, and nested allotment seed table
- Cowhide x1-3, Logs x1-3, Raw anchovies x1-3, and Raw chicken x1-3
- Uncut opal, Uncut jade, Iron ore, Coal, Coins x1-20
- Buttons, Damaged armour, Rusty sword, Knife, Needle, Tinderbox, Feather x1-6,
  and Thread x1-10

Tertiary table:

- Clue scroll (easy) 1/55

## Item registry

The H.A.M.-specific drops and small material drops were missing from the Combat
item registry. The following are now registered and have fetched icons:

- H.A.M. boots, H.A.M. cloak, H.A.M. gloves, H.A.M. hood, H.A.M. logo,
  H.A.M. robe, H.A.M. shirt
- Buttons, Damaged armour, Rusty sword, Needle, Thread

H.A.M. clothing is registered as equipment-category inventory data, matching the
existing Combat pattern for equippable drops whose full equipment-slot behavior
is not modeled in this slice.

## Verification hooks

Targeted coverage was added for:

- Source stats, bonuses, timing, shared drops, active main-table denominator, and
  tertiary table total.
- Quantity-range rolls, nested allotment seed rolls, H.A.M. clothing drops, and
  easy clue rolls.
- Combat target tooltip metadata for H.A.M. clothing, nested seed tables, Coins,
  Thread, clues, and source file provenance.
- Combat item registry and icon presence for the newly registered H.A.M. drops.
