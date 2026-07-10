# Runecrafting Source Audit - 2026-06-17

## Local source roots

- Standard runes and multiplier rolls: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/Rune.kt`
- Standard and combination rune runtime behavior: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/RunecraftAction.kt`
- Combination rune table: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/CombinationRune.kt`
- Altar access item table: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/Altar.kt`
- Tiara source table and runtime: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/Tiara.kt`, `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/tiara.plugin.kts`
- Pouch capacities and degradation: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting/pouches.plugin.kts`
- Rune Mysteries quest data: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/RuneMysteries.kt`
- Item IDs: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Implemented local facts

- Standard runes use local source levels and XP from Air through Blood, including Astral as a target with no modeled talisman/tiara access.
- Air through Body accept Rune essence or Pure essence. Higher runes use Pure essence only.
- Standard rune output uses the source multiplier table and interpolated chance for the next multiplier.
- Each standard crafting trip selects the first stocked valid essence family in source order and consumes only that stack, matching `RunecraftAction.kt:120-128`; Rune essence therefore takes priority over Pure essence for Air through Body without spilling into the second stack.
- Combination rune rows match all twelve local `CombinationRune.kt` variants, with source XP, required talisman, component rune, and altar.
- Combination trips use Pure essence, consume component runes, consume one opposite talisman, and use a base 26 essence cap before pouches.
- Tiara binding uses local active rows plus the local commented Body/Cosmic/Chaos/Nature/Law/Death rows and `Altar.kt` Blood access data. Blood tiara XP follows the 2.5 XP step pattern after Death.
- Pouches auto-cycle per simulated trip. Small/Medium/Large/Giant capacities are 3/6/9/12 at Runecrafting 1/25/50/75. Medium/Large/Giant degrade after 44/34/10 fills.
- Rune Mysteries uses the local source stage count of 6, 1 quest point, Air talisman reward, and source journal text normalized for AnkiScape display.

## External evidence

- Jagex Runecraft update, 2005-06-13: craftable tiara can be bound with any rune talisman, supporting the full tiara access set beyond the local active five rows. https://secure.runescape.com/m%3Dnews/runecraft-update--tweaks
- RuneScape Wiki, Wicked hood: released 2011-10-17 and stores talisman/tiara altar access. https://runescape.wiki/w/Wicked_hood
- RuneHQ, Wicked hood: independent item guide corroborating the pre-EOC hood behavior. https://www.runehq.com/item/wicked-hood
- RuneScape Wiki, Binding necklace: Runecrafting combination support with 15 charges in RuneScape. https://runescape.wiki/w/Binding_necklace
- RuneHQ, Binding necklace: 15-use RuneScape binding necklace guide. https://www.runehq.com/item/binding-necklace

## AnkiScape adaptations

- Quest progression is review-count based. Rune Mysteries advances one stage per successful quest review and caps at the remaining source stages; review multiplier never spills over after completion.
- Quest rewards are fixed and direct on completion, not scaled by review multiplier.
- Wicked hood is a one-time Bank Claim after Rune Mysteries with no Runecrafting level claim gate. Daily essence, teleports, reclaim, and free rune behavior are deferred.
- Wicked hood feeding is an explicit Runecrafting action. It consumes the fed talisman or tiara permanently and only grants standard altar access.
- Binding necklace is one visible equipment item with `item_charges["Binding necklace"]`, not 15 item variants. A fresh worn necklace initializes to 15 charges on first combination use and is destroyed at zero.
- Acquisition gaps remain natural inventory/material locks; player UI does not label those rows as future content.
