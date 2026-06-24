# Combat Imp source audit - 2026-06-23

## Scope

Added the ordinary fightable Imp row from local 2011Scape source:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/demons/imp_level_2.plugin.kts`

The plugin registers normal pre-death and death-drop callbacks for `Npcs.IMP`
and `Npcs.IMP_709`. The source also teleports imps around their current region
on a timer, but that is spatial movement rather than a special combat rule or
drop condition, so it is recorded in provenance and not modeled as a Combat
target blocker.

## Combat row

- Target id: `imp`
- Display: `Imp`
- Combat level: 2
- Group: Demons
- Attack style: melee
- Attack speed: 4
- Respawn delay: 50
- Stats: 80 LP, Attack 1, Strength 1, Defence 1, Magic 1, Ranged 1
- Bonuses: Attack Stab -42, Attack Crush -37, Defence Stab/Slash/Crush/Magic/Ranged -42

The source has no `attackSlash` or `meleeStrength` bonus entries, so those local
fields stay at zero.

## Drop tables

The row guarantees Impious ashes, then rolls one 1024-slot main table.

Main table highlights:

- Black bead, Red bead, White bead, and Yellow bead at 40/1024 each
- Bronze bolts and Wizard hat at 64/1024 each
- Egg and Raw chicken at 47/1024 each
- Burnt bread, Burnt meat, and Shears at 39/1024 each
- Hammer and Ball of wool at 47/1024 each
- Mind talisman at 55/1024
- Ashes at 48/1024
- Cadava berries and Clay at 32/1024 each
- Chef's hat at 16/1024

The source defines no tertiary clue table and no Charms table for this NPC.

## Item registry

The Imp-specific drops and several small skilling/material drops were missing
from the Combat item registry. The following are now registered and have fetched
icons:

- Impious ashes
- Black bead, Red bead, White bead, Yellow bead
- Wizard hat
- Shears
- Jug
- Cadava berries

Wizard hat is registered as equipment, Shears as a tool, and the other new drops
as materials, matching existing item category conventions.

## Verification hooks

Targeted coverage was added for:

- Source stats, bonuses, timing, exact main table total, Imp Catcher bead slots,
  and source teleport provenance.
- Deterministic bead and tail-slot drop rolls.
- Combat target tooltip metadata for Impious ashes, beads, Wizard hat, Chef's
  hat, and source file provenance.
- Combat item registry and icon presence for the newly registered Imp drops.
