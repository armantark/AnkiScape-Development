# Crafting 2011Scape Source Audit

## Status

Backend parity foundation completed on 2026-06-03. Crafting now has a focused source-data module, `crafting_data.py`, keyed by stable recipe IDs while inventory remains keyed by real item names.

## Primary Sources

Local 2011Scape rev 667 source under `/Users/ArmanTarkhanian1/Downloads/game-main`:

- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/gems/GemData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/pottery/PotteryData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/pottery/AddRuneAction.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/spinning/SpinningData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/silver/SilverData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/jewellery/JewelleryData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/leather/LeatherData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/glassblowing/GlassData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/weaponry/BattlestaffData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/crafting/weaving/WeavingData.kt`
- `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/combine/CombinationData.kt`
- `data/cfg/items.yml` for canonical display names and tradability.

## Implemented Backend Scope

`crafting_data.py` encodes live Crafting targets for the source-backed categories that matter to the AnkiScape economy now: gem cutting, pottery including representative urn flows, spinning, silver, jewellery including dragonstone/onyx, leather, glass, battlestaves, weaving, and selected Crafting combinations. All clear-source rows are ordinary runnable recipe data; there is no artificial hidden/locked state. If an input has no acquisition route yet, the target naturally reports missing materials until a future skill, drop, market, or Utility/Activity supplies the item.

Important corrected values from 2011Scape:

- Emerald cutting is 67.0 Crafting XP, not the legacy pilot's 67.5.
- Sapphire necklace is 55.0 Crafting XP, not the legacy pilot's 60.
- Ball of wool and Bow string are XP-bearing Crafting actions and therefore run one action per review. The old 28x batch behavior belongs only to no-XP Utility/Activities.

## Backend Decisions

- Stable recipe IDs now live in `current_craft`; legacy display names migrate through `LEGACY_CRAFTING_TARGETS`.
- `Soft clay` remains a no-XP Utility/Activity target and migrates to `current_utility = make_soft_clay`.
- Crafting tools/stations such as chisels, moulds, needles, furnaces, potter's wheels, ovens, looms, and glassblowing pipes remain implicit. They are source requirements but not gameplay objects yet.
- Semiprecious gem crush chances are documented in source but not modeled. One successful review represents one successful Crafting action.
- Dragonstone, onyx, battlestaff-orb, hide/tanning, molten-glass, root, and rune-dependent content is live but input-starved until acquisition systems exist.

## Tests

Coverage added/updated for stable IDs, corrected 2011Scape values, live input-starved dragonstone targets, legacy migration, no XP-bearing Crafting batching, item manifest registration, review dispatch, and undo-safe Utility regression coverage.
