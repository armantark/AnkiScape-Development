# Combat Magic Strike Ladder And Elemental Staves

Date: 2026-06-23

## Scope

This slice expands the Combat Magic proof from Wind Strike only to the
source-backed standard Strike ladder and basic elemental staff rune substitution.
It does not add battlestaves, noncombat Magic spells, defensive autocast UI,
rune loadout controls, or a standalone Magic skill panel.

## Primary Source Evidence

- `2011Scape/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/SpellbookData.kt`
  - `WIND_STRIKE`: lines 39-48, Magic level 1, Air rune x1, Mind rune x1.
  - `WATER_STRIKE`: lines 50-59, Magic level 5, Air rune x1, Mind rune x1, Water rune x1.
  - `EARTH_STRIKE`: lines 72-81, Magic level 9, Air rune x1, Mind rune x1, Earth rune x2.
  - `FIRE_STRIKE`: lines 94-103, Magic level 13, Air rune x1, Mind rune x1, Fire rune x3.
- `2011Scape/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/magic/CombatSpell.kt`
  - `WIND_STRIKE`: lines 39-49, max hit 2, cast XP 5.5.
  - `WATER_STRIKE`: lines 51-61, max hit 4, cast XP 7.5.
  - `EARTH_STRIKE`: lines 63-73, max hit 6, cast XP 9.5.
  - `FIRE_STRIKE`: lines 75-85, max hit 8, cast XP 11.5.
- `2011Scape/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicStaves.kt`
  - Lines 15, 20, 25, and 30 map Fire, Water, Air, and Earth runes to their
    basic staff and battlestaff item IDs.
- `2011Scape/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicSpells.kt`
  - Lines 35-47 check the equipped weapon slot for a matching staff.
  - Lines 60-64 skip rune availability checks for staff-provided runes.
  - Lines 87-98 skip rune removal for staff-provided runes.
- `2011Scape/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`
  - Lines 555-559 define Fire/Water/Air/Earth/Mind rune IDs 554-558.
  - Lines 1322-1328 define Staff of air/water/earth/fire IDs 1381/1383/1385/1387.
- `2011Scape/data/cfg/items.yml`
  - Lines 17751-17900 define the four basic elemental staves as weapon-slot
    equipment with attack speed 5, +10 Magic attack, +10 Magic defence, and
    their melee staff bonuses.

## Implemented Rows

| Spell | Level | Runes | Max hit | Base Magic XP |
| --- | ---: | --- | ---: | ---: |
| Wind Strike | 1 | Air x1, Mind x1 | 2 | 5.5 |
| Water Strike | 5 | Air x1, Mind x1, Water x1 | 4 | 7.5 |
| Earth Strike | 9 | Air x1, Mind x1, Earth x2 | 6 | 9.5 |
| Fire Strike | 13 | Air x1, Mind x1, Fire x3 | 8 | 11.5 |

| Staff | Source item ID | Provided rune |
| --- | ---: | --- |
| Staff of air | 1381 | Air rune |
| Staff of water | 1383 | Water rune |
| Staff of earth | 1385 | Earth rune |
| Staff of fire | 1387 | Fire rune |

## Runtime Decision

AnkiScape keeps source spell costs in `COMBAT_MAGIC_SPELL_DATA` and models staff
substitution as equipment-provided runes in `COMBAT_MAGIC_STAFF_DATA`. A covered
rune is not treated as missing, is not loaded from the bank, and is not consumed
on cast. If a covered rune was already in the carried rune loadout, safe-boundary
refill returns it to inventory instead of deleting it.

## Assets

`Staff of air` already had `combatitems/staff_of_air.png`. This pass fetched:

- `combatitems/staff_of_water.png`
- `combatitems/staff_of_earth.png`
- `combatitems/staff_of_fire.png`

The fetch used `tools/fetch_assets.py` against OSRS wiki item art as a practical
unchanged-icon fallback, and `assets_provenance.json` records each file.

## Deferred

- Battlestaff and mystic staff rune substitution.
- Autocast-specific UI and defensive autocast XP style.
- More combat spell tiers beyond the Strike ladder.
- Noncombat Magic action families.
- Player-facing rune loadout controls.
- A standalone Magic skill panel, which should wait until Magic has a playable
  noncombat action family rather than a hollow row.
