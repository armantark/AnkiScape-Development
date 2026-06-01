# Woodcutting 2011Scape Source Audit

## Scope

This audit supports the Woodcutting backend parity pass. It replaces AnkiScape's older display-name tree table with stable target IDs, real log output items, source-audited hatchet ratios, and bird nest drop/open tables.

## Primary Sources

- Tree targets: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/woodcutting/TreeType.kt`
- Hatchet tiers: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/woodcutting/AxeType.kt`
- Runtime chop/drop behavior: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/woodcutting/Woodcutting.kt`
- Bird nest subtype/opening tables: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/birdnests/bird_nest.plugin.kts`

## Implemented Targets

| Target ID | Display | Level | Base XP | Output |
| --- | --- | ---: | ---: | --- |
| `tree` | Tree | 1 | 25.0 | Logs |
| `achey` | Achey | 1 | 25.0 | Achey tree logs |
| `oak` | Oak | 15 | 37.5 | Oak logs |
| `willow` | Willow | 30 | 67.5 | Willow logs |
| `teak` | Teak | 35 | 85.0 | Teak logs |
| `maple` | Maple | 45 | 100.0 | Maple logs |
| `hollow` | Hollow | 45 | 82.0 | Bark |
| `mahogany` | Mahogany | 50 | 125.0 | Mahogany logs |
| `yew` | Yew | 60 | 175.0 | Yew logs |
| `ivy` | Ivy | 68 | 332.5 | No item |
| `magic` | Magic | 75 | 250.0 | Magic logs |

Redwood is intentionally removed from normal content because it is absent from the 2011Scape Woodcutting source and belongs to OSRS-era content.

## Hatchet Tiers

Implemented as source data and mechanics: Bronze, Iron, Steel, Black, Mithril, Adamant, Rune, Dragon.

Inferno adze is recorded as deferred special content only. Its All Fired Up acquisition route and Firemaking/incineration behavior need a broader special-reward/Firemaking design.

## AnkiScape Translation

- One eligible successful Anki review still performs one Woodcutting action attempt.
- Woodcutting remains RNG-based, matching the previous add-on behavior.
- 2011Scape low/high chance and hatchet ratio are preserved as source data.
- Runtime probability uses a source-shaped Anki-tuned adapter because 2011Scape rolls every few ticks while AnkiScape rolls once per card.
- Hatchets increase success chance, not log quantity.
- Hatchets resolve from a hybrid tool model: bound toolbelt IDs and ordinary inventory items are both accepted.
- Existing/new saves get a bound Bronze hatchet so Woodcutting is never bricked by the new tool requirement.

## Bird Nests

Woodcutting can drop source subtypes:

- Bird's nest (seeds)
- Bird's nest (ring)
- Bird's nest (Zamorak egg)
- Bird's nest (Guthix egg)
- Bird's nest (Saradomin egg)

`Open bird nests` is a no-XP Utility/Activities action. It opens up to 28 nests per review and awards the source contents plus an empty nest. Farming, Herblore, and broader loot uses are intentionally deferred; the items are safe to sit inert in inventory.
