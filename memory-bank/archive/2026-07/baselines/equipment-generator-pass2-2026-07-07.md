# Equipment Generator Pass 2

Date: 2026-07-07

`tools/generate_equipment_data.py` now treats implemented NPC shop stock and implemented combat drops as equipment acquisition sources, after smithing, mining bonus items, legacy preserved rows, crafting, and fletching. Source stats still come only from `data/cfg/items.yml` equipment blocks with mappable `equip_slot` values.

The generator resolves shop stock by `item_id` first, then name. Combat drops resolve by name, including singular/plural ammo aliases so source singular names such as `Bronze arrow` canonicalize to existing plural equipment rows such as `Bronze arrows` and do not duplicate fletched ammo.

A follow-up added a sixth source, `_smithing_recipe_equipment_items`, merged last. The
type-based `_smithing_equipment_items` selector maps armour and weapon families but skips
smithable tools that are also wieldable (hatchets), so higher tiers that nothing drops
(Mithril/Adamant/Rune hatchet) fell through. Merged last, the recipe-based source adds only
those net-new smithable names without relabelling any existing row.

After regeneration, `EQUIPMENT_DATA` has 553 rows, up from 227, with no previously generated
item removed. A source reconciliation confirms every item that is equippable in `items.yml`
and obtainable through an implemented path (smithing, crafting, fletching, NPC shops, or
combat drops) is now present; the only equippable items still excluded are the Fist of Guthix
metal gauntlets, which have no implemented acquisition path (parked with the minigames seed).
