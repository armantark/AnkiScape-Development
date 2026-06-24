# Combat Haakon the Champion source audit - 2026-06-23

## Scope

Added the ordinary fightable Haakon the Champion row from local 2011Scape source:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/haakon_the_champion_lvl_29.plugin.kts`

The plugin registers normal pre-death and death-drop callbacks for
`Npcs.HAAKON_THE_CHAMPION`. There is no quest, route, required-item, Slayer, or
faction gate in this combat definition, so it is safe as an ordinary
source-backed Combat target.

## Combat row

- Target id: `haakon_the_champion`
- Display: `Haakon the Champion`
- Combat level: 29
- Group: Humanoids
- Attack style: melee
- Attack speed: 6
- Respawn delay: 50
- Stats: 350 LP, Attack 22, Strength 22, Defence 25, Magic 1, Ranged 1
- Bonuses: Attack Stab 8, Attack Crush 9, Defence Stab 12, Defence Slash 14,
  Defence Crush 10, Defence Magic -1, Defence Ranged 11

The source has no `attackSlash` or `meleeStrength` bonus entries, so those local
fields stay at zero.

## Drop tables

The row guarantees Bones, then rolls a 1024-slot main table and a 128-slot
tertiary easy clue table. The source defines no Charms table for this NPC, so no
Charms table was added.

Main table highlights:

- Iron hatchet 48/1024
- Bronze battleaxe 32/1024
- Iron mace 8/1024
- Chaos rune x3 at 32/1024
- Bronze arrows x10, Earth rune x5, and Iron arrows x8 at 24/1024 each
- Fire rune x8 and Mind rune x10 at 16/1024 each
- Law rune x2 at 8/1024
- Coins at 317/1024, 76/1024, 45/1024, and 26/1024
- Empty slot 288/1024
- Tin ore, Bear fur, Beer, Cooked meat, and Ring mould at 8/1024 each

Tertiary table:

- Clue scroll (easy) 1/128

## Item registry

No new item registry entries were required. Every source drop already resolves
through existing Combat, Skill, or equipment item data and existing icon assets.

## Verification hooks

Targeted coverage was added for:

- Source stats, bonuses, timing, exact main table total, and tertiary table total.
- A deterministic tail-slot roll for Ring mould plus the easy clue table.
- Combat target tooltip metadata for Bronze battleaxe, Coins x8, easy clue, and
  source file provenance.
