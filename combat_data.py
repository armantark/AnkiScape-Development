"""Source-backed Combat V1 data.

The enabled rows below are intentionally small: they have complete 2011Scape
combat stats and drop behavior, so runtime combat can fail closed for everything
else while the broader enemy audit continues.
"""

from __future__ import annotations

from typing import Dict, Tuple


DEFAULT_COMBAT_TARGET = "chicken"
DEFAULT_COMBAT_ATTACK_STYLE = "accurate"
DEFAULT_COMBAT_SPELL = "wind_strike"
COMBAT_BURST_TICKS = 50

COMBAT_SOURCE_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main"
MELEE_FORMULA_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MeleeCombatFormula.kt"
)
MELEE_STRATEGY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MeleeCombatStrategy.kt"
)
RANGED_FORMULA_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/RangedCombatFormula.kt"
)
RANGED_STRATEGY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/RangedCombatStrategy.kt"
)
RANGED_BOW_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/weapon/BowType.kt"
)
RANGED_ARROW_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/ranged/ammo/Arrows.kt"
)
MAGIC_FORMULA_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MagicCombatFormula.kt"
)
MAGIC_STRATEGY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MagicCombatStrategy.kt"
)
MAGIC_SPELL_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/magic/CombatSpell.kt"
)
MAGIC_SPELLBOOK_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/SpellbookData.kt"
)
MAGIC_SPELL_REQUIREMENT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicSpells.kt"
)
MAGIC_STAVES_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/magic/MagicStaves.kt"
)
FOOD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/food/Food.kt"
)
POTION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/potion/Potion.kt"
)
POTION_TYPE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/potion/PotionType.kt"
)
ITEM_ID_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt"
)
GLOBAL_HERBS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt"
)
GLOBAL_SEEDS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Seeds.kt"
)


COMBAT_ATTACK_STYLE_DATA: Dict[str, dict] = {
    "accurate": {
        "display_name": "Accurate",
        "combat_class": "melee",
        "xp_mode": "attack",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.ACCURATE",
    },
    "aggressive": {
        "display_name": "Aggressive",
        "combat_class": "melee",
        "xp_mode": "strength",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.AGGRESSIVE",
    },
    "defensive": {
        "display_name": "Defensive",
        "combat_class": "melee",
        "xp_mode": "defense",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.DEFENSIVE",
    },
    "controlled": {
        "display_name": "Controlled",
        "combat_class": "melee",
        "xp_mode": "shared",
        "source": f"{MELEE_FORMULA_SOURCE_PATH}: WeaponStyle.CONTROLLED",
    },
    "ranged_accurate": {
        "display_name": "Ranged accurate",
        "combat_class": "ranged",
        "xp_mode": "ranged",
        "source": f"{RANGED_FORMULA_SOURCE_PATH}: WeaponStyle.ACCURATE",
    },
    "ranged_rapid": {
        "display_name": "Ranged rapid",
        "combat_class": "ranged",
        "xp_mode": "ranged",
        "attack_speed_delta": -1,
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/"
            "CombatConfigs.kt: WeaponStyle.RAPID"
        ),
    },
    "ranged_longrange": {
        "display_name": "Ranged longrange",
        "combat_class": "ranged",
        "xp_mode": "ranged_defense",
        "source": f"{RANGED_FORMULA_SOURCE_PATH}: WeaponStyle.LONG_RANGE",
    },
    "magic_standard": {
        "display_name": "Magic standard",
        "combat_class": "magic",
        "xp_mode": "magic",
        "source": f"{MAGIC_FORMULA_SOURCE_PATH}: Combat.CASTING_SPELL + MagicCombatStrategy.addCombatXp",
    },
}


COMBAT_RANGED_WEAPON_DATA: Dict[str, dict] = {
    "Shortbow": {
        "equipment_type": "shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS",
    },
    "Longbow": {
        "equipment_type": "longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS",
    },
    "Oak shortbow": {
        "equipment_type": "oak_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: OAK_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS",
    },
    "Oak longbow": {
        "equipment_type": "oak_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: OAK_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS",
    },
    "Willow shortbow": {
        "equipment_type": "willow_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: WILLOW_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS",
    },
    "Willow longbow": {
        "equipment_type": "willow_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: WILLOW_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS",
    },
    "Maple shortbow": {
        "equipment_type": "maple_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAPLE_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS",
    },
    "Maple longbow": {
        "equipment_type": "maple_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAPLE_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS",
    },
    "Yew shortbow": {
        "equipment_type": "yew_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: YEW_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS",
    },
    "Yew longbow": {
        "equipment_type": "yew_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: YEW_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS",
    },
    "Magic shortbow": {
        "equipment_type": "magic_shortbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAGIC_SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS; BROAD_ARROWS deferred until ammo skill gates exist",
    },
    "Magic longbow": {
        "equipment_type": "magic_longbow",
        "compatible_ammo": ("Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows", "Adamant arrows", "Rune arrows"),
        "source": f"{RANGED_BOW_SOURCE_PATH}: MAGIC_LONGBOW accepts BRONZE_ARROWS + IRON_ARROWS + STEEL_ARROWS + MITHRIL_ARROWS + ADAMANT_ARROWS + RUNE_ARROWS; BROAD_ARROWS deferred until ammo skill gates exist",
    },
}


COMBAT_RANGED_AMMO_DATA: Dict[str, dict] = {
    "Bronze arrows": {
        "source_item_id": 882,
        "source_item_name": "Bronze arrow",
        "ranged_strength": 7,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: BRONZE_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 882"
        ),
    },
    "Iron arrows": {
        "source_item_id": 884,
        "source_item_name": "Iron arrow",
        "ranged_strength": 10,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: IRON_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 884"
        ),
    },
    "Steel arrows": {
        "source_item_id": 886,
        "source_item_name": "Steel arrow",
        "ranged_strength": 16,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: STEEL_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 886"
        ),
    },
    "Mithril arrows": {
        "source_item_id": 888,
        "source_item_name": "Mithril arrow",
        "ranged_strength": 22,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: MITHRIL_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 888"
        ),
    },
    "Adamant arrows": {
        "source_item_id": 890,
        "source_item_name": "Adamant arrow",
        "ranged_strength": 31,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: ADAMANT_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 890"
        ),
    },
    "Rune arrows": {
        "source_item_id": 892,
        "source_item_name": "Rune arrow",
        "ranged_strength": 49,
        "source": (
            f"{RANGED_ARROW_SOURCE_PATH}: RUNE_ARROWS; "
            f"{COMBAT_SOURCE_ROOT}/data/cfg/items.yml item 892"
        ),
    },
}


COMBAT_MAGIC_SPELL_DATA: Dict[str, dict] = {
    "wind_strike": {
        "display_name": "Wind Strike",
        "spellbook": "standard",
        "required_magic_level": 1,
        "rune_cost": {"Air rune": 1, "Mind rune": 1},
        "max_hit_old_hp": 2,
        "base_magic_xp": 5.5,
        "attack_speed": 5,
        "unique_id": 15,
        "component_id": 25,
        "autocast_id": 3,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_STRIKE maxHit=2 experience=5.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_STRIKE level=1 runes AIR_RUNE x1 MIND_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_strike": {
        "display_name": "Water Strike",
        "spellbook": "standard",
        "required_magic_level": 5,
        "rune_cost": {"Air rune": 1, "Mind rune": 1, "Water rune": 1},
        "max_hit_old_hp": 4,
        "base_magic_xp": 7.5,
        "attack_speed": 5,
        "unique_id": 17,
        "component_id": 28,
        "autocast_id": 5,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_STRIKE maxHit=4 experience=7.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_STRIKE level=5 runes AIR_RUNE x1 MIND_RUNE x1 WATER_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_strike": {
        "display_name": "Earth Strike",
        "spellbook": "standard",
        "required_magic_level": 9,
        "rune_cost": {"Air rune": 1, "Mind rune": 1, "Earth rune": 2},
        "max_hit_old_hp": 6,
        "base_magic_xp": 9.5,
        "attack_speed": 5,
        "unique_id": 19,
        "component_id": 30,
        "autocast_id": 7,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_STRIKE maxHit=6 experience=9.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_STRIKE level=9 runes AIR_RUNE x1 MIND_RUNE x1 EARTH_RUNE x2; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_strike": {
        "display_name": "Fire Strike",
        "spellbook": "standard",
        "required_magic_level": 13,
        "rune_cost": {"Air rune": 1, "Mind rune": 1, "Fire rune": 3},
        "max_hit_old_hp": 8,
        "base_magic_xp": 11.5,
        "attack_speed": 5,
        "unique_id": 71,
        "component_id": 32,
        "autocast_id": 9,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_STRIKE maxHit=8 experience=11.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_STRIKE level=13 runes AIR_RUNE x1 MIND_RUNE x1 FIRE_RUNE x3; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "wind_bolt": {
        "display_name": "Wind Bolt",
        "spellbook": "standard",
        "required_magic_level": 17,
        "rune_cost": {"Air rune": 2, "Chaos rune": 1},
        "max_hit_old_hp": 9,
        "base_magic_xp": 13.5,
        "attack_speed": 5,
        "unique_id": 73,
        "component_id": 34,
        "autocast_id": 11,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_BOLT maxHit=9 experience=13.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_BOLT level=17 runes AIR_RUNE x2 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_bolt": {
        "display_name": "Water Bolt",
        "spellbook": "standard",
        "required_magic_level": 23,
        "rune_cost": {"Air rune": 2, "Water rune": 2, "Chaos rune": 1},
        "max_hit_old_hp": 10,
        "base_magic_xp": 16.5,
        "attack_speed": 5,
        "unique_id": 76,
        "component_id": 39,
        "autocast_id": 13,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_BOLT maxHit=10 experience=16.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_BOLT level=23 runes AIR_RUNE x2 WATER_RUNE x2 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_bolt": {
        "display_name": "Earth Bolt",
        "spellbook": "standard",
        "required_magic_level": 29,
        "rune_cost": {"Air rune": 2, "Earth rune": 3, "Chaos rune": 1},
        "max_hit_old_hp": 11,
        "base_magic_xp": 19.5,
        "attack_speed": 5,
        "unique_id": 79,
        "component_id": 42,
        "autocast_id": 15,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_BOLT maxHit=11 experience=19.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_BOLT level=29 runes AIR_RUNE x2 EARTH_RUNE x3 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_bolt": {
        "display_name": "Fire Bolt",
        "spellbook": "standard",
        "required_magic_level": 35,
        "rune_cost": {"Air rune": 3, "Fire rune": 4, "Chaos rune": 1},
        "max_hit_old_hp": 12,
        "base_magic_xp": 22.5,
        "attack_speed": 5,
        "unique_id": 82,
        "component_id": 45,
        "autocast_id": 17,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_BOLT maxHit=12 experience=22.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_BOLT level=35 runes AIR_RUNE x3 FIRE_RUNE x4 CHAOS_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "wind_blast": {
        "display_name": "Wind Blast",
        "spellbook": "standard",
        "required_magic_level": 41,
        "rune_cost": {"Air rune": 3, "Death rune": 1},
        "max_hit_old_hp": 13,
        "base_magic_xp": 25.5,
        "attack_speed": 5,
        "unique_id": 85,
        "component_id": 49,
        "autocast_id": 19,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_BLAST maxHit=13 experience=25.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_BLAST level=41 runes AIR_RUNE x3 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_blast": {
        "display_name": "Water Blast",
        "spellbook": "standard",
        "required_magic_level": 47,
        "rune_cost": {"Air rune": 3, "Water rune": 3, "Death rune": 1},
        "max_hit_old_hp": 14,
        "base_magic_xp": 28.5,
        "attack_speed": 5,
        "unique_id": 88,
        "component_id": 52,
        "autocast_id": 21,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_BLAST maxHit=14 experience=28.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_BLAST level=47 runes AIR_RUNE x3 WATER_RUNE x3 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_blast": {
        "display_name": "Earth Blast",
        "spellbook": "standard",
        "required_magic_level": 53,
        "rune_cost": {"Air rune": 3, "Earth rune": 4, "Death rune": 1},
        "max_hit_old_hp": 15,
        "base_magic_xp": 31.5,
        "attack_speed": 5,
        "unique_id": 90,
        "component_id": 58,
        "autocast_id": 23,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_BLAST maxHit=15 experience=31.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_BLAST level=53 runes AIR_RUNE x3 EARTH_RUNE x4 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_blast": {
        "display_name": "Fire Blast",
        "spellbook": "standard",
        "required_magic_level": 59,
        "rune_cost": {"Air rune": 4, "Fire rune": 5, "Death rune": 1},
        "max_hit_old_hp": 16,
        "base_magic_xp": 34.5,
        "attack_speed": 5,
        "unique_id": 95,
        "component_id": 63,
        "autocast_id": 25,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_BLAST maxHit=16 experience=34.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_BLAST level=59 runes AIR_RUNE x4 FIRE_RUNE x5 DEATH_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "wind_wave": {
        "display_name": "Wind Wave",
        "spellbook": "standard",
        "required_magic_level": 62,
        "rune_cost": {"Air rune": 5, "Blood rune": 1},
        "max_hit_old_hp": 17,
        "base_magic_xp": 36.0,
        "attack_speed": 5,
        "unique_id": 96,
        "component_id": 70,
        "autocast_id": 27,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WIND_WAVE maxHit=17 experience=36.0; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WIND_WAVE level=62 runes AIR_RUNE x5 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "water_wave": {
        "display_name": "Water Wave",
        "spellbook": "standard",
        "required_magic_level": 65,
        "rune_cost": {"Air rune": 5, "Water rune": 7, "Blood rune": 1},
        "max_hit_old_hp": 18,
        "base_magic_xp": 37.5,
        "attack_speed": 5,
        "unique_id": 98,
        "component_id": 73,
        "autocast_id": 29,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: WATER_WAVE maxHit=18 experience=37.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: WATER_WAVE level=65 runes AIR_RUNE x5 WATER_RUNE x7 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "earth_wave": {
        "display_name": "Earth Wave",
        "spellbook": "standard",
        "required_magic_level": 70,
        "rune_cost": {"Air rune": 5, "Earth rune": 7, "Blood rune": 1},
        "max_hit_old_hp": 19,
        "base_magic_xp": 40.0,
        "attack_speed": 5,
        "unique_id": 101,
        "component_id": 77,
        "autocast_id": 31,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: EARTH_WAVE maxHit=19 experience=40.0; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: EARTH_WAVE level=70 runes AIR_RUNE x5 EARTH_RUNE x7 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
    "fire_wave": {
        "display_name": "Fire Wave",
        "spellbook": "standard",
        "required_magic_level": 75,
        "rune_cost": {"Air rune": 5, "Fire rune": 7, "Blood rune": 1},
        "max_hit_old_hp": 20,
        "base_magic_xp": 42.5,
        "attack_speed": 5,
        "unique_id": 102,
        "component_id": 80,
        "autocast_id": 33,
        "source": (
            f"{MAGIC_SPELL_SOURCE_PATH}: FIRE_WAVE maxHit=20 experience=42.5; "
            f"{MAGIC_SPELLBOOK_SOURCE_PATH}: FIRE_WAVE level=75 runes AIR_RUNE x5 FIRE_RUNE x7 BLOOD_RUNE x1; "
            f"{MAGIC_SPELL_REQUIREMENT_SOURCE_PATH}: canCast/removeRunes"
        ),
    },
}


COMBAT_MAGIC_STAFF_DATA: Dict[str, dict] = {
    "Staff of air": {
        "covered_runes": ("Air rune",),
        "source_item_id": 1381,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: AIR_RUNE uses STAFF_OF_AIR; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_AIR",
    },
    "Staff of water": {
        "covered_runes": ("Water rune",),
        "source_item_id": 1383,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: WATER_RUNE uses STAFF_OF_WATER; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_WATER",
    },
    "Staff of earth": {
        "covered_runes": ("Earth rune",),
        "source_item_id": 1385,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: EARTH_RUNE uses STAFF_OF_EARTH; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_EARTH",
    },
    "Staff of fire": {
        "covered_runes": ("Fire rune",),
        "source_item_id": 1387,
        "source": f"{MAGIC_STAVES_SOURCE_PATH}: FIRE_RUNE uses STAFF_OF_FIRE; {ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_FIRE",
    },
}


GOBLIN_LEVEL_2_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_2.plugin.kts"
)
GOBLIN_LEVEL_5_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_5.plugin.kts"
)
GOBLIN_LEVEL_11_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_11.plugin.kts"
)
GOBLIN_LEVEL_13_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_13.plugin.kts"
)
GOBLIN_LEVEL_16_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_16.plugin.kts"
)
GOBLIN_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/goblin/goblin_level_25.plugin.kts"
)
ALKHARID_WARRIOR_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/alkharid_warrior_level_9.plugin.kts"
)
MUGGER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/mugger_level_6.plugin.kts"
)
THUG_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/thug_level_10.plugin.kts"
)
THIEF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/thief_level_16.plugin.kts"
)
FARMER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/farmer_level_7.plugin.kts"
)

POISON_SCORPION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/poison_scorpion_lvl_20.plugin.kts"
)
POISON_SPIDER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/poison_spider_lvl_31.plugin.kts"
)
SCORPION_LEVEL_14_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/scorpion_level_14.plugin.kts"
)
SPIDER_LEVEL_24_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/spider_level_24.plugin.kts"
)
DEADLY_RED_SPIDER_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/deadly_red_spider_level_34.plugin.kts"
)
GIANT_SPIDER_LEVEL_50_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_spider_level_50.plugin.kts"
)


COMBAT_MINOR_HERB_DROP_TABLE = {
    "name": "Minor herb",
    "source": f"{GLOBAL_HERBS_SOURCE_PATH}: Herbs.minorHerbTable",
    "total": 1024,
    "slots": (
        {"item": "Grimy guam", "quantity": 1, "slots": 249},
        {"item": "Grimy marrentill", "quantity": 1, "slots": 198},
        {"item": "Grimy tarromin", "quantity": 1, "slots": 146},
        {"item": "Grimy harralander", "quantity": 1, "slots": 114},
        {"item": "Grimy ranarr", "quantity": 1, "slots": 85},
        {"item": "Grimy irit", "quantity": 1, "slots": 64},
        {"item": "Grimy avantoe", "quantity": 1, "slots": 49},
        {"item": "Grimy kwuarm", "quantity": 1, "slots": 39},
        {"item": "Grimy cadantine", "quantity": 1, "slots": 32},
        {"item": "Grimy lantadyme", "quantity": 1, "slots": 24},
        {"item": "Grimy dwarf weed", "quantity": 1, "slots": 24},
    ),
}


COMBAT_ALLOTMENT_SEED_DROP_TABLE = {
    "name": "Allotment seed",
    "source": f"{GLOBAL_SEEDS_SOURCE_PATH}: Seeds.allotmentSeedTable",
    "total": 90,
    "slots": (
        {"item": "Potato seed", "quantity": 4, "slots": 32},
        {"item": "Onion seed", "quantity": 4, "slots": 25},
        {"item": "Cabbage seed", "quantity": 4, "slots": 16},
        {"item": "Tomato seed", "quantity": 3, "slots": 9},
        {"item": "Sweetcorn seed", "quantity": 3, "slots": 5},
        {"item": "Strawberry seed", "quantity": 2, "slots": 2},
        {"item": "Watermelon seed", "quantity": 2, "slots": 1},
    ),
}


GOBLIN_LEVEL_2_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Bronze sq shield", "quantity": 1, "slots": 24},
                {"item": "Bronze spear", "quantity": 1, "slots": 32},
                {"item": "Sling", "quantity": 1, "slots": 32},
                {"item": "Water rune", "quantity": 6, "slots": 48},
                {"item": "Body rune", "quantity": 7, "slots": 40},
                {"item": "Earth rune", "quantity": 4, "slots": 24},
                {"item": "Bronze bolts", "quantity": 8, "slots": 24},
                {"item": "Coins", "quantity": 5, "slots": 224},
                {"item": "Coins", "quantity": 9, "slots": 24},
                {"item": "Coins", "quantity": 15, "slots": 24},
                {"item": "Coins", "quantity": 20, "slots": 16},
                {"item": "Coins", "quantity": 1, "slots": 8},
                {"slots": 272},
                {"item": "Hammer", "quantity": 1, "slots": 120},
                {"item": "Goblin book", "quantity": 1, "slots": 16},
                {"item": "Goblin mail", "quantity": 1, "slots": 40},
                {"item": "Chef's hat", "quantity": 1, "slots": 24},
                {"item": "Beer", "quantity": 1, "slots": 16},
                {"item": "Brass necklace", "quantity": 1, "slots": 8},
                {"item": "Air talisman", "quantity": 1, "slots": 8},
            ),
        },
        {
            "name": "Charms",
            "total": 1024,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 82},
                {"item": "Green charm", "quantity": 1, "slots": 21},
                {"item": "Crimson charm", "quantity": 1, "slots": 9},
                {"item": "Blue charm", "quantity": 1, "slots": 1},
                {"slots": 911},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6},
                {"slots": 1018},
            ),
        },
    ),
}


GOBLIN_HIGHER_LEVEL_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Bronze spear", "quantity": 1, "slots": 9},
                {"item": "Bronze hatchet", "quantity": 1, "slots": 3},
                {"item": "Bronze scimitar", "quantity": 1, "slots": 1},
                {"item": "Bronze arrows", "quantity": 7, "slots": 3},
                {"item": "Mind rune", "quantity": 2, "slots": 3},
                {"item": "Earth rune", "quantity": 4, "slots": 3},
                {"item": "Body rune", "quantity": 2, "slots": 3},
                {"item": "Bronze javelin", "quantity": 5, "slots": 2},
                {"item": "Chaos rune", "quantity": 1, "slots": 1},
                {"item": "Nature rune", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 1, "slots": 34},
                {"item": "Coins", "quantity": 3, "slots": 13},
                {"item": "Coins", "quantity": 5, "slots": 8},
                {"item": "Coins", "quantity": 16, "slots": 7},
                {"item": "Coins", "quantity": 24, "slots": 3},
                {"item": "Hammer", "quantity": 1, "slots": 9},
                {"item": "Goblin book", "quantity": 1, "slots": 2},
                {"item": "Goblin mail", "quantity": 1, "slots": 10},
                {"item": "Grapes", "quantity": 1, "slots": 1},
                {"item": "Tin ore", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 2},
                {"slots": 8},
            ),
        },
        {
            "name": "Charms",
            "total": 1024,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 82},
                {"item": "Green charm", "quantity": 1, "slots": 21},
                {"item": "Crimson charm", "quantity": 1, "slots": 9},
                {"item": "Blue charm", "quantity": 1, "slots": 1},
                {"slots": 911},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 6},
                {"slots": 1018},
            ),
        },
    ),
}


FARMER_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Earth rune", "quantity": 4, "slots": 2},
                {"item": "Fire rune", "quantity": 6, "slots": 2},
                {"item": "Mind rune", "quantity": 9, "slots": 2},
                {"item": "Chaos rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 11},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 27},
                {"item": "Coins", "quantity": 3, "slots": 38},
                {"item": "Coins", "quantity": 25, "slots": 1},
                {"item": "Fishing bait", "quantity": 1, "slots": 5},
                {"item": "Rake", "quantity": 1, "slots": 3},
                {"item": "Earth talisman", "quantity": 1, "slots": 2},
                {"item": "Gardening boots", "quantity": 1, "slots": 2},
                {"item": "Seed dibber", "quantity": 1, "slots": 2},
                {"item": "Secateurs", "quantity": 1, "slots": 1},
                {"item": "Watering can (8)", "quantity": 1, "slots": 1},
                {"slots": 28},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


COMBAT_FOOD_DATA: Dict[str, dict] = {
    "Crayfish": {"heal_lifepoints": 20, "source": FOOD_SOURCE_PATH},
    "Shrimps": {"heal_lifepoints": 30, "source": FOOD_SOURCE_PATH},
    "Cooked chicken": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Cooked meat": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Trout": {"heal_lifepoints": 70, "source": FOOD_SOURCE_PATH},
    "Salmon": {"heal_lifepoints": 90, "source": FOOD_SOURCE_PATH},
    "Tuna": {"heal_lifepoints": 100, "source": FOOD_SOURCE_PATH},
    "Lobster": {"heal_lifepoints": 120, "source": FOOD_SOURCE_PATH},
    "Swordfish": {"heal_lifepoints": 140, "source": FOOD_SOURCE_PATH},
    "Monkfish": {"heal_lifepoints": 160, "source": FOOD_SOURCE_PATH},
    "Shark": {"heal_lifepoints": 200, "source": FOOD_SOURCE_PATH},
}


COMBAT_ANTIPOISON_POTION_DATA: Dict[str, dict] = {
    "Antipoison (4)": {
        "replacement": "Antipoison (3)",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON4; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Antipoison (3)": {
        "replacement": "Antipoison (2)",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON3; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Antipoison (2)": {
        "replacement": "Antipoison (1)",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON2; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Antipoison (1)": {
        "replacement": "Vial",
        "immunity_ticks": 1500,
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON1; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON",
    },
    "Super antipoison (4)": {
        "replacement": "Super antipoison (3)",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON4; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
    "Super antipoison (3)": {
        "replacement": "Super antipoison (2)",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON3; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
    "Super antipoison (2)": {
        "replacement": "Super antipoison (1)",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON2; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
    "Super antipoison (1)": {
        "replacement": "Vial",
        "immunity_ticks": 6000,
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON1; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON",
    },
}


COMBAT_ENEMY_DATA: Dict[str, dict] = {
    "chicken": {
        "display_name": "Chicken",
        "level": 1,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 3.0,
        "stats": {
            "hitpoints": 30,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -42,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Raw chicken", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Feather", "quantity": 5, "slots": 64},
                        {"item": "Feather", "quantity": 15, "slots": 32},
                        {"slots": 32},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/chicken_level_1.plugin.kts"
        ),
    },
    "rat": {
        "display_name": "Rat",
        "level": 1,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 1,
        "stats": {
            "hitpoints": 20,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -53,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/rat_level_1.plugin.kts"
        ),
    },
    "spider": {
        "display_name": "Spider",
        "level": 1,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 2.0,
        "stats": {
            "hitpoints": 20,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -35,
            "attack_slash": 0,
            "attack_crush": -58,
            "defence_stab": -53,
            "defence_slash": -53,
            "defence_crush": -53,
            "defence_magic": -53,
            "defence_ranged": -53,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 200,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 5},
                        {"item": "Green charm", "quantity": 1, "slots": 7},
                        {"item": "Crimson charm", "quantity": 1, "slots": 3},
                        {"item": "Blue charm", "quantity": 1, "slots": 2},
                        {"slots": 183},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/spider_level_1.plugin.kts"
        ),
    },
    "giant_rat": {
        "display_name": "Giant rat",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 50,
            "attack": 2,
            "strength": 3,
            "defence": 2,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1), ("Raw rat meat", 1)), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/giant_rat_level_2.plugin.kts"
        ),
    },
    "giant_spider": {
        "display_name": "Giant spider",
        "level": 2,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 50,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -10,
            "attack_slash": 0,
            "attack_crush": -10,
            "defence_stab": -10,
            "defence_slash": -10,
            "defence_crush": -10,
            "defence_magic": -10,
            "defence_ranged": -10,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 48,
                    "slots": (
                        {"item": "Air rune", "quantity_range": (4, 6), "slots": 7},
                        {"item": "Earth rune", "quantity": 4, "slots": 7},
                        {"item": "Fire rune", "quantity": 6, "slots": 7},
                        {"item": "Body rune", "quantity": 7, "slots": 3},
                        {"slots": 24},
                    ),
                },
                {
                    "name": "Secondary",
                    "total": 128,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 48},
                        {"item": "Bronze bolts", "quantity": 1, "slots": 12},
                        {"item": "Bronze arrows", "quantity": 1, "slots": 12},
                        {"item": "Longbow", "quantity": 1, "slots": 4},
                        {"item": "Bronze kiteshield", "quantity": 1, "slots": 1},
                        {"slots": 51},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Staff of air", "quantity": 1, "slots": 1},
                        {"item": "Sling", "quantity": 1, "slots": 1},
                        {"slots": 126},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 90},
                        {"item": "Green charm", "quantity": 1, "slots": 11},
                        {"item": "Crimson charm", "quantity": 1, "slots": 30},
                        {"item": "Blue charm", "quantity": 1, "slots": 9},
                        {"slots": 860},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/giant_spider_level_2.plugin.kts"
        ),
    },
    "goblin_level_2_unarmed": {
        "display_name": "Goblin (unarmed)",
        "level": 2,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 50,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -21,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -15,
            "defence_slash": -15,
            "defence_crush": -15,
            "defence_magic": -15,
            "defence_ranged": -15,
            "melee_strength": 0,
        },
        "drops": GOBLIN_LEVEL_2_DROPS,
        "source": f"{GOBLIN_LEVEL_2_SOURCE_PATH}: unarmed ids GOBLIN_4261/GOBLIN_4263-GOBLIN_4271",
    },
    "goblin_level_2_armed": {
        "display_name": "Goblin (armed)",
        "level": 2,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 50,
            "attack": 3,
            "strength": 1,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -21,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -15,
            "defence_slash": -15,
            "defence_crush": -15,
            "defence_magic": -15,
            "defence_ranged": -15,
            "melee_strength": 0,
        },
        "drops": GOBLIN_LEVEL_2_DROPS,
        "source": f"{GOBLIN_LEVEL_2_SOURCE_PATH}: armed id GOBLIN_4262",
    },
    "goblin_level_5": {
        "display_name": "Goblin",
        "level": 5,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 35,
        "slayer_xp": 12.0,
        "stats": {
            "hitpoints": 120,
            "attack": 3,
            "strength": 1,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 12,
            "attack_slash": 0,
            "attack_crush": 12,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_5_SOURCE_PATH}: ids GOBLIN_3265 et al.",
    },
    "goblin_level_11": {
        "display_name": "Goblin",
        "level": 11,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 160,
            "attack": 12,
            "strength": 13,
            "defence": 7,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_11_SOURCE_PATH}: ids GOBLIN_4409/GOBLIN_11259/GOBLIN_11260",
    },
    "goblin_level_13": {
        "display_name": "Goblin",
        "level": 13,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 120,
            "attack": 12,
            "strength": 13,
            "defence": 7,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_13_SOURCE_PATH}: ids GOBLIN_4408/GOBLIN_6283/GOBLIN_11261/GOBLIN_13097",
    },
    "goblin_level_16": {
        "display_name": "Goblin",
        "level": 16,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 170,
            "attack": 16,
            "strength": 13,
            "defence": 10,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_16_SOURCE_PATH}: id GOBLIN_4412",
    },
    "goblin_level_25": {
        "display_name": "Goblin",
        "level": 25,
        "group": "Goblins",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 350,
            "attack": 22,
            "strength": 17,
            "defence": 15,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 6,
            "attack_crush": 8,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": GOBLIN_HIGHER_LEVEL_DROPS,
        "source": f"{GOBLIN_LEVEL_25_SOURCE_PATH}: id GOBLIN_4411",
    },
    "farmer": {
        "display_name": "Farmer",
        "level": 7,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 120,
            "attack": 3,
            "strength": 4,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 6,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": FARMER_DROPS,
        "source": f"{FARMER_SOURCE_PATH}: ids FARMER/FARMER_1757/FARMER_1758",
    },
    "cow": {
        "display_name": "Cow",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "slayer_xp": 8.0,
        "stats": {
            "hitpoints": 80,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -15,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Sling", "quantity": 1, "slots": 64},
                        {"slots": 960},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 9},
                        {"item": "Green charm", "quantity": 1, "slots": 40},
                        {"item": "Crimson charm", "quantity": 1, "slots": 3},
                        {"item": "Blue charm", "quantity": 1, "slots": 1},
                        {"slots": 947},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/cow_level_2.plugin.kts"
        ),
    },
    "cow_calf": {
        "display_name": "Cow calf",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "slayer_xp": 6.0,
        "stats": {
            "hitpoints": 60,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -20,
            "attack_slash": 0,
            "attack_crush": -20,
            "defence_stab": -26,
            "defence_slash": -26,
            "defence_crush": -26,
            "defence_magic": -26,
            "defence_ranged": -26,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1), ("Raw beef", 1), ("Cowhide", 1)), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/cow_calf_level_2.plugin.kts"
        ),
    },
    "ram": {
        "display_name": "Ram",
        "level": 2,
        "group": "Lumbridge",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 45,
        "stats": {
            "hitpoints": 80,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -15,
            "attack_slash": 0,
            "attack_crush": -15,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/ram_level_2.plugin.kts"
        ),
    },
    "highwayman": {
        "display_name": "Highwayman",
        "level": 5,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "stats": {
            "hitpoints": 130,
            "attack": 2,
            "strength": 2,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 6,
            "attack_slash": 6,
            "attack_crush": 6,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": 0,
            "defence_ranged": 2,
            "melee_strength": 7,
        },
        "drops": {
            "guaranteed": (("Bones", 1), ("Cape", 1)),
            "tables": (
                {
                    "name": "Main",
                    "total": 20,
                    "slots": (
                        {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 1},
                        {"slots": 19},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/highwayman_level_5.plugin.kts"
        ),
    },
    "mugger": {
        "display_name": "Mugger",
        "level": 6,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 80,
            "attack": 5,
            "strength": 5,
            "defence": 5,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": -21,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 162},
                        {"item": "Mind rune", "quantity": 9, "slots": 24},
                        {"item": "Water rune", "quantity": 6, "slots": 16},
                        {"item": "Earth rune", "quantity": 5, "slots": 16},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 104},
                        {"item": "Coins", "quantity": 10, "slots": 104},
                        {"item": "Coins", "quantity": 5, "slots": 96},
                        {"item": "Coins", "quantity": 15, "slots": 24},
                        {"item": "Coins", "quantity": 25, "slots": 8},
                        {"item": "Rope", "quantity": 1, "slots": 270},
                        {"slots": 104},
                        {"item": "Fishing bait", "quantity": 1, "slots": 48},
                        {"item": "Copper ore", "quantity": 1, "slots": 16},
                        {"item": "Bronze med helm", "quantity": 1, "slots": 16},
                        {"item": "Knife", "quantity": 1, "slots": 8},
                        {"item": "Cabbage", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": f"{MUGGER_SOURCE_PATH}: ids = Npcs.MUGGER/Npcs.MUGGER_7161/Npcs.MUGGER_7162",
    },
    "thug": {
        "display_name": "Thug",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 180,
            "attack": 7,
            "strength": 5,
            "defence": 9,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 5,
            "defence_stab": 2,
            "defence_slash": 3,
            "defence_crush": 3,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Iron med helm", "quantity": 1, "slots": 4},
                        {"item": "Iron battleaxe", "quantity": 1, "slots": 2},
                        {"item": "Steel hatchet", "quantity": 1, "slots": 1},
                        {"item": "Nature rune", "quantity": 2, "slots": 13},
                        {"item": "Chaos rune", "quantity": 2, "slots": 4},
                        {"item": "Cosmic rune", "quantity": 2, "slots": 1},
                        {"item": "Law rune", "quantity": 2, "slots": 1},
                        {"item": "Death rune", "quantity": 2, "slots": 1},
                        {"item": "Iron ore", "quantity": 1, "slots": 4},
                        {"item": "Iron bar", "quantity": 1, "slots": 3},
                        {"item": "Coal", "quantity": 1, "slots": 2},
                        {"item": "Coins", "quantity": 8, "slots": 23},
                        {"item": "Coins", "quantity": 15, "slots": 12},
                        {"item": "Coins", "quantity": 30, "slots": 2},
                        {"item": "Coins", "quantity": 20, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 24},
                        {"slots": 30},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 120},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 8},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 857},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{THUG_SOURCE_PATH}: ids = Npcs.THUG_7106/Npcs.THUG_7107/"
            "Npcs.THUG_7109/Npcs.THUG_7110/Npcs.THUG_7112/Npcs.THUG_7113/Npcs.THUG_7114"
        ),
    },
    "thief": {
        "display_name": "Thief",
        "level": 16,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 170,
            "attack": 14,
            "strength": 13,
            "defence": 12,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 128,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 2},
                        {"item": "Iron dagger", "quantity": 1, "slots": 1},
                        {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 22},
                        {"item": "Bronze arrows", "quantity": 7, "slots": 3},
                        {"item": "Earth rune", "quantity": 4, "slots": 2},
                        {"item": "Fire rune", "quantity": 6, "slots": 2},
                        {"item": "Mind rune", "quantity": 9, "slots": 2},
                        {"item": "Chaos rune", "quantity": 2, "slots": 1},
                        {"item": "Coins", "quantity": 3, "slots": 38},
                        {"item": "Coins", "quantity": 5, "slots": 9},
                        {"item": "Coins", "quantity": 15, "slots": 4},
                        {"item": "Coins", "quantity": 25, "slots": 1},
                        {"item": "Fishing bait", "quantity": 1, "slots": 5},
                        {"item": "Copper ore", "quantity": 1, "slots": 2},
                        {"item": "Earth talisman", "quantity": 1, "slots": 2},
                        {"item": "Cabbage", "quantity": 1, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 23},
                        {"slots": 8},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": f"{THIEF_SOURCE_PATH}: ids = Npcs.THIEF_5926/Npcs.THIEF_5927/Npcs.THIEF_5928/Npcs.THIEF_5929",
    },
    "barbarian": {
        "display_name": "Barbarian",
        "level": 8,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 140,
            "attack": 6,
            "strength": 5,
            "defence": 5,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 1,
            "defence_slash": 1,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_lvl_8.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_lvl_9.plugin.kts"
        ),
    },
    "barbarian_level_10": {
        "display_name": "Barbarian",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 180,
            "attack": 8,
            "strength": 7,
            "defence": 3,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 9,
            "attack_slash": 0,
            "attack_crush": 15,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": -3,
            "defence_ranged": 2,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze hatchet", "quantity": 1, "slots": 48},
                        {"item": "Staff", "quantity": 1, "slots": 32},
                        {"item": "Iron mace", "quantity": 1, "slots": 8},
                        {"item": "Chaos rune", "quantity": 2, "slots": 32},
                        {"item": "Bronze arrows", "quantity": 15, "slots": 24},
                        {"item": "Earth rune", "quantity": 2, "slots": 24},
                        {"item": "Fire rune", "quantity": 5, "slots": 16},
                        {"item": "Mind rune", "quantity": 5, "slots": 16},
                        {"item": "Law rune", "quantity": 2, "slots": 8},
                        {"item": "Coins", "quantity": 5, "slots": 341},
                        {"item": "Coins", "quantity": 8, "slots": 76},
                        {"item": "Coins", "quantity": 17, "slots": 45},
                        {"item": "Coins", "quantity": 27, "slots": 26},
                        {"slots": 288},
                        {"item": "Tin ore", "quantity": 1, "slots": 8},
                        {"item": "Bear fur", "quantity": 1, "slots": 8},
                        {"item": "Beer", "quantity": 1, "slots": 8},
                        {"item": "Cooked meat", "quantity": 1, "slots": 8},
                        {"item": "Ring mould", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 50},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 5},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 930},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                        {"slots": 127},
                    ),
                },
            ),
        },
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_greataxe_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_spear_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_twohand_sword_lvl_10.plugin.kts; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_2hsword_lvl_10.plugin.kts"
        ),
    },
    "seagull": {
        "display_name": "Seagull",
        "level": 2,
        "group": "Coastal",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 5.0,
        "stats": {
            "hitpoints": 60,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": -47,
            "attack_slash": 0,
            "attack_crush": -42,
            "defence_stab": -42,
            "defence_slash": -42,
            "defence_crush": -42,
            "defence_magic": -42,
            "defence_ranged": -42,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/animals/seagull_level_2.plugin.kts"
        ),
    },
    "al_kharid_warrior": {
        "display_name": "Al-Kharid warrior",
        "level": 9,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 190,
            "attack": 7,
            "strength": 5,
            "defence": 4,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 10,
            "attack_slash": 10,
            "attack_crush": 10,
            "defence_stab": 12,
            "defence_slash": 15,
            "defence_crush": 10,
            "defence_magic": -1,
            "defence_ranged": 12,
            "melee_strength": 9,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 1024,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 16},
                        {"item": "Iron dagger", "quantity": 1, "slots": 8},
                        {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 146},
                        {"item": "Bronze arrows", "quantity": 7, "slots": 24},
                        {"item": "Earth rune", "quantity": 4, "slots": 16},
                        {"item": "Fire rune", "quantity": 6, "slots": 16},
                        {"item": "Mind rune", "quantity": 9, "slots": 16},
                        {"item": "Chaos rune", "quantity": 2, "slots": 8},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 84},
                        {"item": "Coins", "quantity": 3, "slots": 204},
                        {"item": "Coins", "quantity": 10, "slots": 84},
                        {"item": "Coins", "quantity": 5, "slots": 72},
                        {"item": "Coins", "quantity": 15, "slots": 32},
                        {"item": "Coins", "quantity": 25, "slots": 8},
                        {"slots": 146},
                        {"slots": 64},
                        {"item": "Fishing bait", "quantity": 1, "slots": 40},
                        {"item": "Copper ore", "quantity": 1, "slots": 16},
                        {"item": "Earth talisman", "quantity": 1, "slots": 16},
                        {"item": "Cabbage", "quantity": 1, "slots": 8},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 1024,
                    "slots": (
                        {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
                        {"slots": 1016},
                    ),
                },
            ),
        },
        "source": f"{ALKHARID_WARRIOR_SOURCE_PATH}: NPC_ID = Npcs.ALKHARID_WARRIOR",
    },
    "poison_scorpion": {
        "display_name": "Poison scorpion",
        "level": 20,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "poison_damage": 3,
        "slayer_xp": 23.0,
        "stats": {
            "hitpoints": 230,
            "attack": 16,
            "strength": 17,
            "defence": 15,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": f"{POISON_SCORPION_SOURCE_PATH}: Npcs.POISON_SCORPION poisonDamage=3; no DropTableFactory registration",
    },
    "scorpion": {
        "display_name": "Scorpion",
        "level": 14,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 170,
            "attack": 11,
            "strength": 12,
            "defence": 11,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 15,
            "defence_crush": 15,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 30},
                        {"item": "Green charm", "quantity": 1, "slots": 70},
                        {"item": "Crimson charm", "quantity": 1, "slots": 10},
                        {"item": "Blue charm", "quantity": 1, "slots": 5},
                        {"slots": 885},
                    ),
                },
            ),
        },
        "source": SCORPION_LEVEL_14_SOURCE_PATH,
    },
    "poison_spider": {
        "display_name": "Poison spider",
        "level": 31,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "poison_damage": 3,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 28,
            "strength": 28,
            "defence": 28,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 20,
            "defence_slash": 17,
            "defence_crush": 10,
            "defence_magic": 14,
            "defence_ranged": 14,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": f"{POISON_SPIDER_SOURCE_PATH}: Npcs.POISON_SPIDER_1009 poisonDamage=3; no DropTableFactory registration",
    },
    "spider_level_24": {
        "display_name": "Spider",
        "level": 24,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 27,
        "slayer_xp": 22.0,
        "stats": {
            "hitpoints": 220,
            "attack": 21,
            "strength": 21,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 53,
            "attack_slash": 0,
            "attack_crush": 53,
            "defence_stab": 53,
            "defence_slash": 53,
            "defence_crush": 53,
            "defence_magic": 53,
            "defence_ranged": 53,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 200,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 5},
                        {"item": "Green charm", "quantity": 1, "slots": 7},
                        {"item": "Crimson charm", "quantity": 1, "slots": 3},
                        {"item": "Blue charm", "quantity": 1, "slots": 2},
                        {"slots": 183},
                    ),
                },
            ),
        },
        "source": SPIDER_LEVEL_24_SOURCE_PATH,
    },
    "deadly_red_spider": {
        "display_name": "Deadly red spider",
        "level": 34,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 35.0,
        "stats": {
            "hitpoints": 350,
            "attack": 30,
            "strength": 25,
            "defence": 30,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 15,
            "defence_slash": 16,
            "defence_crush": 7,
            "defence_magic": 12,
            "defence_ranged": 16,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 260},
                        {"item": "Green charm", "quantity": 1, "slots": 11},
                        {"item": "Crimson charm", "quantity": 1, "slots": 20},
                        {"item": "Blue charm", "quantity": 1, "slots": 2},
                        {"slots": 707},
                    ),
                },
            ),
        },
        "source": DEADLY_RED_SPIDER_SOURCE_PATH,
    },
    "giant_spider_level_50": {
        "display_name": "Giant spider",
        "level": 50,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 500,
            "attack": 41,
            "strength": 51,
            "defence": 31,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 10,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 10,
            "defence_magic": 10,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (),
            "tables": (
                {
                    "name": "Main",
                    "total": 48,
                    "slots": (
                        {"item": "Air rune", "quantity_range": (4, 6), "slots": 7},
                        {"item": "Earth rune", "quantity": 4, "slots": 7},
                        {"item": "Fire rune", "quantity": 6, "slots": 7},
                        {"item": "Body rune", "quantity": 7, "slots": 3},
                        {"slots": 24},
                    ),
                },
                {
                    "name": "Secondary",
                    "total": 128,
                    "slots": (
                        {"item": "Bronze med helm", "quantity": 1, "slots": 48},
                        {"item": "Bronze bolts", "quantity": 1, "slots": 12},
                        {"item": "Bronze arrows", "quantity": 1, "slots": 12},
                        {"item": "Longbow", "quantity": 1, "slots": 4},
                        {"item": "Bronze kiteshield", "quantity": 1, "slots": 1},
                        {"slots": 51},
                    ),
                },
                {
                    "name": "Tertiary",
                    "total": 128,
                    "slots": (
                        {"item": "Staff of air", "quantity": 1, "slots": 1},
                        {"item": "Sling", "quantity": 1, "slots": 1},
                        {"slots": 126},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 90},
                        {"item": "Green charm", "quantity": 1, "slots": 11},
                        {"item": "Crimson charm", "quantity": 1, "slots": 30},
                        {"item": "Blue charm", "quantity": 1, "slots": 9},
                        {"slots": 860},
                    ),
                },
            ),
        },
        "source": GIANT_SPIDER_LEVEL_50_SOURCE_PATH,
    },
}


COMBAT_EXTRA_ITEM_DATA: Dict[str, dict] = {
    "Antipoison (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_1"},
    "Antipoison (2)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_2"},
    "Antipoison (3)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_3"},
    "Antipoison (4)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ANTIPOISON_4"},
    "Bear fur": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEAR_FUR"},
    "Bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BONES"},
    "Brass necklace": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRASS_NECKLACE"},
    "Bronze javelin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_JAVELIN"},
    "Bronze spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_SPEAR"},
    "Cape": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CAPE_1019"},
    "Chef's hat": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHEFS_HAT"},
    "Cabbage seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CABBAGE_SEED"},
    "Clue scroll (easy)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CLUE_SCROLL_EASY"},
    "Coins": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COINS_995"},
    "Cowhide": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COWHIDE"},
    "Beer": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEER"},
    "Gardening boots": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GARDENING_BOOTS"},
    "Goblin book": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOBLIN_BOOK"},
    "Grapes": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRAPES"},
    "Grimy avantoe": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_AVANTOE"},
    "Grimy cadantine": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_CADANTINE"},
    "Grimy dwarf weed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_DWARF_WEED"},
    "Grimy guam": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_GUAM"},
    "Grimy harralander": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_HARRALANDER"},
    "Grimy irit": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_IRIT"},
    "Grimy kwuarm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_KWUARM"},
    "Grimy lantadyme": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_LANTADYME"},
    "Grimy marrentill": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_MARRENTILL"},
    "Grimy ranarr": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_RANARR"},
    "Grimy tarromin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GRIMY_TARROMIN"},
    "Knife": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KNIFE"},
    "Onion seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ONION_SEED"},
    "Potato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.POTATO_SEED"},
    "Rake": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAKE"},
    "Raw rat meat": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAW_RAT_MEAT"},
    "Secateurs": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SECATEURS"},
    "Seed dibber": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SEED_DIBBER"},
    "Sling": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SLING"},
    "Staff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF"},
    "Staff of air": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_AIR"},
    "Staff of water": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_WATER"},
    "Staff of earth": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_EARTH"},
    "Staff of fire": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_FIRE"},
    "Strawberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STRAWBERRY_SEED"},
    "Super antipoison (1)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_1"},
    "Super antipoison (2)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_2"},
    "Super antipoison (3)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_3"},
    "Super antipoison (4)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SUPER_ANTIPOISON_4"},
    "Sweetcorn seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SWEETCORN_SEED"},
    "Tomato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOMATO_SEED"},
    "Vial": {"category": "crafted", "source": f"{ITEM_ID_SOURCE_PATH}: Items.VIAL"},
    "Watering can (8)": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERING_CAN_8"},
    "Watermelon seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERMELON_SEED"},
    "Wooden shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOODEN_SHIELD"},
    "Tinderbox": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TINDERBOX_590"},
    "Gold charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOLD_CHARM"},
    "Green charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GREEN_CHARM"},
    "Crimson charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CRIMSON_CHARM"},
    "Blue charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLUE_CHARM"},
}


COMBAT_TARGET_GROUP_ORDER: Tuple[str, ...] = ("Lumbridge", "Spiders", "Scorpions", "Goblins", "Humanoids", "Coastal")
