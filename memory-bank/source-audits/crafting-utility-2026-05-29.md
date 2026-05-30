# Crafting And Utility Source Audit

## Scope

This audit supports the Crafting/Utility backend pilot. It intentionally implements a curated slice instead of dumping the full OSRS Crafting page into the add-on.

## Source Pages

- OSRS Crafting: https://oldschool.runescape.wiki/w/Crafting
- OSRS Soft clay: https://oldschool.runescape.wiki/w/Soft_clay
- OSRS Ball of wool: https://oldschool.runescape.wiki/w/Ball_of_wool
- OSRS Bow string: https://oldschool.runescape.wiki/w/Bow_string
- OSRS Silver bolts (unf): https://oldschool.runescape.wiki/w/Silver_bolts_(unf)

## Implemented Utility/Activities

| Activity | Source section | Source row | Backend decision |
| --- | --- | --- | --- |
| Make soft clay | Soft clay > Creation > Container | Clay x1 + water container -> Soft clay x1, no Crafting XP | No-XP Utility/Activity. Water container/tool is implicit. Batch up to 28 Clay per successful card. |
| Gather wool | Material source simplification | Wool is the input for Ball of wool creation | No-XP Utility/Activity so early spinning has a material source. Batch up to 28 Wool per successful card. |
| Gather flax | Bow string > Strategy > Manual Spinning | Flax is picked before spinning bow strings | No-XP Utility/Activity so bow string has a material source. Batch up to 28 Flax per successful card. |

## Implemented Crafting Actions

| Target | Source section | Source row | Backend data |
| --- | --- | --- | --- |
| Unfired pot | Crafting > Pottery | Level 1 Pot shaping: Soft clay -> Unfired pot, 6.3 XP | `Soft clay x1 -> Unfired pot x1`, level 1, 6.3 XP |
| Pot | Crafting > Pottery | Level 1 Pot firing: Unfired pot -> Pot, 6.3 XP | `Unfired pot x1 -> Pot x1`, level 1, 6.3 XP |
| Unfired pie dish | Crafting > Pottery | Level 7 Pie dish shaping: Soft clay -> Unfired pie dish, 15 XP | `Soft clay x1 -> Unfired pie dish x1`, level 7, 15 XP |
| Pie dish | Crafting > Pottery | Level 7 Pie dish firing: Unfired pie dish -> Pie dish, 10 XP | `Unfired pie dish x1 -> Pie dish x1`, level 7, 10 XP |
| Unfired bowl | Crafting > Pottery | Level 8 Bowl shaping: Soft clay -> Unfired bowl, 18 XP | `Soft clay x1 -> Unfired bowl x1`, level 8, 18 XP |
| Bowl | Crafting > Pottery | Level 8 Bowl firing: Unfired bowl -> Bowl, 15 XP | `Unfired bowl x1 -> Bowl x1`, level 8, 15 XP |
| Ball of wool | Crafting > Spinning / Ball of wool > Creation | Level 1, Wool x1 -> Ball of wool x1, 2.5 XP | Batched Crafting action, up to 28 per successful card |
| Bow string | Crafting > Spinning / Bow string > Creation | Level 10, Flax x1 -> Bow string x1, 15 XP | Batched Crafting action, up to 28 per successful card |
| Silver bolts (unf) | Silver bolts (unf) > Creation | Level 21, Silver bar x1 -> Silver bolts (unf) x10, 50 XP | Crafting action, one silver bar per successful card |

## Deferred

| Content | Reason |
| --- | --- |
| Empty cup, plant pot, pot lid | Members-only and/or quest-gated enough to defer until the broader Crafting list is ready. |
| Weaving targets | Materials such as linen yarn, jute fibre, hemp yarn, willow branches, and cotton yarn need source loops. |
| Leather/dragonhide armour | Depends on combat drops, tanning, tools, and larger equipment modeling. |
| Battlestaves and orbs | Depends on Magic/Runecrafting/combat material sources. |
| Amethyst tips and high-tier jewellery | Depends on Mining expansion and late-game gems/materials. |

## Balance Notes

- Base XP mirrors audited OSRS source rows.
- The global AnkiScape XP multiplier should scale XP after base recipe XP is calculated.
- No-XP Utility/Activities batch up to 28 because they are material preparation, not skill training.
- Spinning actions award Crafting XP and are batched because OSRS spinning processes inventories quickly compared with Anki review pacing.
