# Combat Standard Spell Ladder Audit - 2026-06-23

Status: implemented the standard elemental combat spell ladder from Bolt
through Wave on top of the existing shared Combat Magic burst path.

## Scope

- Adds source-backed standard spell rows for Wind/Water/Earth/Fire Bolt,
  Blast, and Wave.
- Reuses the existing Combat Magic engine: selected spell level gate, rune
  readiness, elemental staff substitution, source base Magic XP on cast
  attempts, Magic damage XP, Constitution damage XP, and 5-tick spell speed.
- Does not add god spells, Ancient spells, Lunar spells, noncombat Magic, or a
  standalone Magic skill panel.

## Sources

| Source | Used for |
| --- | --- |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/magic/CombatSpell.kt` | Standard combat spell unique id, component id, max hit, autocast id, and base experience. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/SpellbookData.kt` | Standard spell Magic level and rune costs. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicSpells.kt` | Source rune requirement checks, elemental staff substitution, and rune removal behavior. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt` | Rune item constants: Air, Water, Earth, Fire, Chaos, Death, and Blood runes. |

## Imported Rows

| Spell | Level | Runes | Max hit | Base XP | Unique/component/autocast |
| --- | ---: | --- | ---: | ---: | --- |
| Wind Bolt | 17 | Air x2, Chaos x1 | 9 | 13.5 | 73 / 34 / 11 |
| Water Bolt | 23 | Air x2, Water x2, Chaos x1 | 10 | 16.5 | 76 / 39 / 13 |
| Earth Bolt | 29 | Air x2, Earth x3, Chaos x1 | 11 | 19.5 | 79 / 42 / 15 |
| Fire Bolt | 35 | Air x3, Fire x4, Chaos x1 | 12 | 22.5 | 82 / 45 / 17 |
| Wind Blast | 41 | Air x3, Death x1 | 13 | 25.5 | 85 / 49 / 19 |
| Water Blast | 47 | Air x3, Water x3, Death x1 | 14 | 28.5 | 88 / 52 / 21 |
| Earth Blast | 53 | Air x3, Earth x4, Death x1 | 15 | 31.5 | 90 / 58 / 23 |
| Fire Blast | 59 | Air x4, Fire x5, Death x1 | 16 | 34.5 | 95 / 63 / 25 |
| Wind Wave | 62 | Air x5, Blood x1 | 17 | 36.0 | 96 / 70 / 27 |
| Water Wave | 65 | Air x5, Water x7, Blood x1 | 18 | 37.5 | 98 / 73 / 29 |
| Earth Wave | 70 | Air x5, Earth x7, Blood x1 | 19 | 40.0 | 101 / 77 / 31 |
| Fire Wave | 75 | Air x5, Fire x7, Blood x1 | 20 | 42.5 | 102 / 80 / 33 |

## Excluded Rows

- Saradomin Strike, Claws of Guthix, and Flames of Zamorak are deferred because
  they need god staff requirements, unlock/effect gates, and source-specific
  side effects rather than plain-damage treatment.
- Wind Rush and Surge-era rows remain deferred because they are outside the
  initial normal elemental ladder slice and need a separate era/source pass.
- Ancient and Lunar combat spells remain deferred behind spellbook and quest
  access gates.

## Verification

- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata tests.test_main_menu_widget.MainMenuWidgetTest.test_combat_exposes_style_and_spell_controls`
- `python3 -m unittest tests.test_skill_and_item_registry`
