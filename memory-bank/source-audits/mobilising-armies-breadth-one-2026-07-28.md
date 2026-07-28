# Mobilising Armies — breadth-one source audit

Date: `2026-07-28`. Family shipped on `families/mobilising-armies` at schema 96.

## Sources used, in evidence order

Darkan has **no Mobilising Armies minigame**. Grepping the whole checkout for
`mobilis` returns only reward-item names in the developer item lists, a music
track row, a spirit-tree destination, an achievement string, and the teleport
spell — no scenario controller, no shop, no squads. That absence was confirmed
against the second emulator before any wiki value was recorded.

`game-main` (2011Scape) is therefore the primary source for **item identity**,
and it is complete: `data/cfg/items.yml` carries every reward item this family
ships, with exact ids and, for the imbued rings, exact equipment blocks.

| source | what it settled |
| --- | --- |
| `game-main data/cfg/items.yml` ids 15001-15004 | Quest kit (basic/medium/advanced/elite) |
| `game-main data/cfg/items.yml` ids 15005-15008 | Inferior/Poor/Good/Superior locator |
| `game-main data/cfg/items.yml` ids 15009-15014, 15016, 15017 | Every imbued ring's exact attack and defence bonus block |
| `game-main data/cfg/items.yml` ids 15022-15026, 15336 | The six Serjeant uniform pieces |
| `game-main data/cfg/items.yml` id 14940 | Special unit contract |
| Wiki `Mobilising Armies` oldid=6514352 (2012-11-01T00:57:11Z) | Squad roster, combat triangle, formations and their rank gates, special units and their damage bands, explore loot pool and race restrictions, investment-credit rule and wallet cap, rank award rules and the hourly cap, scenario list and unlock chain |
| Wiki `Mobilising Armies/Rewards` oldid=6339595 (2012-10-03T11:14:47Z) | The reward-credit formula, the rank band table, every Officer Tower price, the four floors and their rank gates, the Spoils of War tables and the three-of-five draw, the refund rates |
| Wiki `Mobilising Armies/Investments` oldid=6538687 (2012-11-06T04:51:16Z) | Seven independent credit figures used to verify the investment formula |
| Wiki `Mobilising Armies/Conflict` oldid=5371840 | Duration, rank thresholds, special-terrain doubling, the healing find |
| Wiki `Mobilising Armies/Siege` oldid=6002719 | Both win routes; the catapult's four named parts and four rocks per shot |
| Wiki `Mobilising Armies/Hoard` oldid=3819762 | The three exact gold amounts: −5,000, −500, +2,500 |
| Wiki `Mobilising Armies/Rescue` oldid=6492730 | The 28-TzHaar target and the steal command |
| Wiki `Locator` oldid=5509339 | Each locator's rank gate, price, and destination list |
| Wiki `Quest kit` oldid=5565058 | Each kit's exact cumulative contents, including the two elite replacements |
| Wiki `Serjeant top` oldid=6339598 | Slot, untradeability, and the explicit statement that uniforms give no stat bonuses |

## The one derivation worth recording

The Investments page states the rule as `((low alch value)/2)+1` per item, and
this repo already derives low alchemy as 40% of the cache store value
(`data/grand_exchange_data.py:90`). Composing the two and checking against seven
unrelated rows of the Investments table reproduces every figure exactly:

| item | store value | low alchemy | formula | page says |
| --- | --- | --- | --- | --- |
| Adamant bar | 640 | 256 | 129 | 129 |
| Adamant bolts | 58 | 23 | 12 | 12 |
| Adamant javelin | 246 | 98 | 50 | 50 |
| Agility potion (4) | 200 | 80 | 41 | 41 |
| Air rune | 17 | 6 | 4 | 4 |
| Amulet of fury | 202,000 | 80,800 | 40,401 | 40,401 |
| Amulet of glory | 17,625 | 7,050 | 3,526 | 3,526 |

Seven for seven, across four orders of magnitude. The investment wallet therefore
prices **every** item in the AnkiScape registry exactly, with no table to
maintain, and `tests/test_mobilising_armies.py` pins all seven figures.

## Labelled abstraction

One translation, disclosed at the constant and in the cadence row: a thirty-minute
scenario becomes **eighteen review beats, one productive beat per squad order**.
That is the same event-scaled treatment Soul Wars uses for its twenty-minute
match. It is chosen so the sourced ten-order rank threshold stays a gate the
player can miss — under any coarser mapping the threshold would be unreachable or
free, and the source's whole "fast ranks" tension would vanish.

The end-condition modifiers are sourced on the Siege example (150% primary
objective, 120% elimination, 100% loss) and applied across all four scenarios.
Conflict's elimination win takes the primary-objective modifier because
elimination is its only win condition.

## Placeholders

Six, all registered in `memory-bank/placeholder-values.md`:
`objective_rates`, `squad_combat_resolution`, `reward_time_bonus_curve`,
`special_unit_credit_cost`, `explore_outcomes`, `rank_window_reviews`. Every one
of them is a rate or a per-second server behaviour. Every *target*, price, gate,
formula and item identity is exact.

## Deferred data depth (not placeholders — real period content, absent tables)

- **Three of the four A.R.M.S. uniform sets.** The Serjeant set ships complete at
  six pieces. Commander, War-chief and Lord Marshal are the same mechanic at
  higher rank gates, and the quest kits, locators and imbued rings already prove
  every floor's gate independently.
- **Five imbued rings whose base ring AnkiScape does not stock yet**: Lunar,
  Seers', Warrior's, Archer's, Berserker. Those base items belong to families that
  have not shipped. The eight rings that do ship cover all four floors.
- **Two locator destination kinds with no gathering target**: the Herblore
  secondary sites, and Eucalyptus trees.

## What is not modelled at all, and why that is honest

The period activity is a real-time strategy game on a tile map: squad facing,
rear and flank attacks, 2x2 special terrain, formations as physical layouts,
camera control, and quick chat. AnkiScape has no map, so formations ship as a
rank-gated named choice rather than a geometry, and the terrain, first-strike and
rear-attack bonuses are folded into the disclosed
`squad_combat_resolution` placeholder rather than invented as separate
multipliers. The combat triangle, which the sources treat as the decisive
mechanic, ships as a real doubling and does decide fights.
