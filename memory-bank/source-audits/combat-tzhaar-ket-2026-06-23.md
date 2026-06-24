# Combat TzHaar-Ket source audit - 2026-06-23

## Scope

Added the ordinary fightable TzHaar-Ket row from local 2011Scape source:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/other/tzhaar_ket_lvl_149.plugin.kts`

The plugin registers a pre-death sound effect and a normal death-drop callback
for `Npcs.TZHAARKET_2616`. There is no source combat special attack in the
plugin.

## Combat row

- Target id: `tzhaar_ket`
- Display: `TzHaar-Ket`
- Combat level: 149
- Group: TzHaar
- Attack style: melee
- Attack speed: 4
- Respawn delay: 50
- Stats: 1400 LP, Attack 120, Strength 140, Defence 120, Magic 40, Ranged 1
- Bonuses: all zero in the plugin combat stats

## Drop tables

The row has no guaranteed drops. It rolls a 128-slot main table, a 512-slot
Obsidian table, and a 1000-slot Charms table.

Main table:

- Tokkul x100-2000 at 69/128
- Fire battlestaff x1 at 1/128
- Super strength (1) x1 at 4/128
- Super defence (1) x1 at 4/128
- Uncut sapphire x1 at 12/128
- Uncut emerald x1 at 12/128
- Uncut ruby x1 at 6/128
- Uncut diamond x1 at 6/128
- Lobster x1 at 6/128
- Chilli potato x1 at 6/128
- Pure essence x5-10 at 1/128
- Onyx bolt tips x1-4 at 1/128

Obsidian table:

- Tzhaar-ket-om x1 at 1/512
- Toktz-ket-xil x1 at 1/512
- Obsidian cape x1 at 1/512

Charms table:

- Obsidian charm x2 at 720/1000

## Item registry and equipment

Added Combat item/icon registration for Chilli potato, Fire battlestaff,
Obsidian cape, Obsidian charm, Super defence (1), Super strength (1), Tokkul,
Toktz-ket-xil, and Tzhaar-ket-om. Onyx bolt tips and Pure essence already exist
under Fletching and Mining ownership, so Combat reuses those item definitions
instead of duplicating them.

`Food.kt` defines Chilli potato healing as 140 lifepoints. `data/cfg/items.yml`
equipment blocks define the TzHaar equipment bonuses. Fire battlestaff now uses
the extended equipment requirement contract because the source item requires
both Attack 30 and Magic 30. Toktz-ket-xil requires Defence 60, and
Tzhaar-ket-om requires Strength 60.

Fetched icons:

- `combatitems/chilli_potato.png`
- `combatitems/fire_battlestaff.png`
- `combatitems/obsidian_cape.png`
- `combatitems/obsidian_charm.png`
- `combatitems/super_defence_1.png`
- `combatitems/super_strength_1.png`
- `combatitems/tokkul.png`
- `combatitems/toktz_ket_xil.png`
- `combatitems/tzhaar_ket_om.png`

## Deferred TzHaar rows

TzHaar-Xil, TzHaar-Hur, and TzHaar-Mej remain deferred until Combat supports
source-backed enemy Ranged and Magic attack strategies. The current row is safe
to ship because TzHaar-Ket is a melee row with complete source stats and normal
drop callbacks.

## Verification hooks

Targeted coverage was added for:

- Source stats, timing, source path provenance, and all three drop tables.
- Quantity ranges for Tokkul, Pure essence, and Onyx bolt tips.
- Obsidian table and Obsidian charm table deterministic rolls.
- Target tooltip metadata for TzHaar-Ket drops and source file provenance.
- Combat item registry and icon presence for newly registered TzHaar items.
- TzHaar equipment metadata and multi-skill equip gating for Fire battlestaff.
