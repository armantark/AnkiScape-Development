# Combat Ranged Progression Audit - 2026-06-23

## Scope

This slice widens the first Combat Ranged path from one starter pair to the
standard source-backed bow and arrow progression already produced by Fletching,
through Magic bows and Rune arrows.

## Implemented Scope

- `COMBAT_RANGED_WEAPON_DATA` now supports:
  - Shortbow and Longbow with Bronze/Iron arrows.
  - Oak shortbow and Oak longbow with Bronze/Iron/Steel arrows.
  - Willow shortbow and Willow longbow with Bronze/Iron/Steel/Mithril arrows.
  - Maple shortbow and Maple longbow with Bronze/Iron/Steel/Mithril/Adamant
    arrows.
  - Yew shortbow, Yew longbow, Magic shortbow, and Magic longbow with
    Bronze/Iron/Steel/Mithril/Adamant/Rune arrows.
- `COMBAT_RANGED_AMMO_DATA` now supports:
  - Bronze arrows, item 882, ranged strength 7.
  - Iron arrows, item 884, ranged strength 10.
  - Steel arrows, item 886, ranged strength 16.
  - Mithril arrows, item 888, ranged strength 22.
  - Adamant arrows, item 890, ranged strength 31.
  - Rune arrows, item 892, ranged strength 49.
- `EQUIPMENT_DATA` now registers the same bow ladder as two-handed Ranged
  weapons with local `items.yml` attack speeds, Ranged attack bonuses, and
  Ranged level requirements.
- Existing Fletching item definitions and icons are reused for the new bow and
  arrow items.

## Source Anchors

- Bow compatibility:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/weapon/BowType.kt`
- Arrow family IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/ammo/Arrows.kt`
- Bow and arrow equipment stats:
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`
- Fletching acquisition rows:
  `fletching_data.py`

## Tests

- `tests.test_combat_logic.CombatLogicTest.test_standard_bow_and_arrow_rows_match_2011scape_source`
- `tests.test_combat_logic.CombatLogicTest.test_ranged_burst_accepts_higher_arrow_tiers_for_supported_bows`
- `tests.test_equipment_data.TestEquipmentData.test_standard_bows_are_ranged_weapons`
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`

## Deferred

- Broad arrows. The local source gives Broad arrows a Slayer requirement, and
  the current ammo path does not yet model per-ammo skill gates.
- Composite, ogre, dark, crystal, sling, thrown-weapon, crossbow, bolt, dart,
  and knife Combat support.
- Stack-aware ammunition equipment-slot behavior.
- Arrow recovery/drop/break modeling.
- Player-facing per-ammo preference controls.
