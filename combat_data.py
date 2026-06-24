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
GLOBAL_GEMS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Gems.kt"
)
GLOBAL_MEGA_RARE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/MegaRare.kt"
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
OUTLAW_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/outlaw_level_35.plugin.kts"
)
CHAOS_DWARF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/chaos_dwarf_lvl_48.plugin.kts"
)
HAAKON_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/haakon_the_champion_lvl_29.plugin.kts"
)
HAM_GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/ham_guard_level_12_18_22.plugin.kts"
)
THUG_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/thug_level_10.plugin.kts"
)
THIEF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/thief_level_16.plugin.kts"
)
CITIZEN_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/citizen_level_2.plugin.kts"
)
MONK_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/monk_level_5.plugin.kts"
)
MONK_OF_ZAMORAK_LEVEL_45_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/monk_of_zamorak_lvl_45.plugin.kts"
)
CUFFS_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/cuffs_level_3.plugin.kts"
)
NARF_JEFF_RUSTY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/narf_jeff_rusty_level_2.plugin.kts"
)
PIRATE_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/pirate_level_23.plugin.kts"
)
GIANT_RAT_LEVEL_6_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_rat_level_6.plugin.kts"
)
GIANT_RAT_LEVEL_26_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_rat_level_26.plugin.kts"
)
UNICORN_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/unicorn_level_15.plugin.kts"
)
BLACK_UNICORN_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/black_unicorn_level_27.plugin.kts"
)
BLACK_BEAR_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/black_bear_level_19.plugin.kts"
)
WOLF_LEVEL_11_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/wolf_lvl_11.plugin.kts"
)
WHITE_WOLF_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/white_wolf_lvl_25.plugin.kts"
)
WHITE_WOLF_LEVEL_38_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/white_wolf_lvl_38.plugin.kts"
)
BIG_WOLF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/big_wolf_lvl_73.plugin.kts"
)
GIANT_BAT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/giant_bat_level_27.plugin.kts"
)
HILL_GIANT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/hill_giant_lvl_28.plugin.kts"
)
MOSS_GIANT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/moss_giant_level_42.plugin.kts"
)
ICE_GIANT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/other/ice_giant_level_53.plugin.kts"
)
GHOST_LEVEL_19_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/ghost_level_19.plugin.kts"
)
ZOMBIE_LEVEL_13_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_13.plugin.kts"
)
ZOMBIE_LEVEL_18_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_18.plugin.kts"
)
ZOMBIE_LEVEL_24_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_24.plugin.kts"
)
ZOMBIE_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_25.plugin.kts"
)
ZOMBIE_LEVEL_30_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_30.plugin.kts"
)
ZOMBIE_LEVEL_44_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_44.plugin.kts"
)
ZOMBIE_LEVEL_53_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/zombie_lvl_53.plugin.kts"
)
SKELETON_LEVEL_21_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_21.plugin.kts"
)
SKELETON_LEVEL_22_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_22.plugin.kts"
)
SKELETON_LEVEL_25_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_25.plugin.kts"
)
SKELETON_LEVEL_45_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_level_45.plugin.kts"
)
SKELETON_LEVEL_60_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_60.plugin.kts"
)
SKELETON_LEVEL_68_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_68.plugin.kts"
)
SKELETON_LEVEL_85_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/undeads/skeleton_lvl_85.plugin.kts"
)
DUCK_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/animals/duck_level_1.plugin.kts"
)
GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/guard_level_21.plugin.kts"
)
JAIL_GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/jail_guard_level_26.plugin.kts"
)
MARKET_GUARD_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/market_guard_level_20.plugin.kts"
)
BLACK_KNIGHT_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/black_knight_level_33.plugin.kts"
)
CHAOS_DRUID_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/chaos_druid_lvl_13.plugin.kts"
)
WHITE_KNIGHT_LEVEL_36_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_36.plugin.kts"
)
WHITE_KNIGHT_LEVEL_38_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_38.plugin.kts"
)
WHITE_KNIGHT_LEVEL_39_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_39.plugin.kts"
)
WHITE_KNIGHT_LEVEL_42_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/white_knight_level_42.plugin.kts"
)
DWARF_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/humanoids/dwarf_level_10_11.plugin.kts"
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
POISON_SPIDER_LEVEL_64_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/poison_spider_lvl_64.plugin.kts"
)
SCORPION_LEVEL_14_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/scorpion_level_14.plugin.kts"
)
KING_SCORPION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/king_scorpion_level_32.plugin.kts"
)
PIT_SCORPION_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/pit_sorpion_lvl_28.plugin.kts"
)
SCORPION_LEVEL_59_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
    "definitions/critters/scorpion_level_59.plugin.kts"
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


COMBAT_UNCOMMON_SEED_DROP_TABLE = {
    "name": "Uncommon seed",
    "source": f"{GLOBAL_SEEDS_SOURCE_PATH}: Seeds.uncommonSeedTable",
    "total": 1048,
    "slots": (
        {"item": "Limpwurt seed", "quantity": 1, "slots": 137},
        {"item": "Strawberry seed", "quantity": 1, "slots": 131},
        {"item": "Marrentill seed", "quantity": 1, "slots": 125},
        {"item": "Jangerberry seed", "quantity": 1, "slots": 92},
        {"item": "Tarromin seed", "quantity": 1, "slots": 85},
        {"item": "Wildblood seed", "quantity": 1, "slots": 83},
        {"item": "Watermelon seed", "quantity": 1, "slots": 83},
        {"item": "Harralander seed", "quantity": 1, "slots": 86},
        {"item": "Ranarr seed", "quantity": 1, "slots": 49},
        {"item": "Whiteberry seed", "quantity": 1, "slots": 39},
        {"item": "Toadflax seed", "quantity": 1, "slots": 27},
        {"item": "Belladonna seed", "quantity": 1, "slots": 18},
        {"item": "Irit seed", "quantity": 1, "slots": 18},
        {"item": "Poison ivy seed", "quantity": 1, "slots": 13},
        {"item": "Avantoe seed", "quantity": 1, "slots": 18},
        {"item": "Cactus seed", "quantity": 1, "slots": 16},
        {"item": "Kwuarm seed", "quantity": 1, "slots": 13},
        {"item": "Snapdragon seed", "quantity": 1, "slots": 5},
        {"item": "Cadantine seed", "quantity": 1, "slots": 4},
        {"item": "Lantadyme seed", "quantity": 1, "slots": 3},
        {"item": "Dwarf weed seed", "quantity": 1, "slots": 2},
        {"item": "Torstol seed", "quantity": 1, "slots": 1},
    ),
}


COMBAT_MEGA_RARE_DROP_TABLE = {
    "name": "Mega rare",
    "source": f"{GLOBAL_MEGA_RARE_SOURCE_PATH}: MegaRare.megaRareTable without Ring of Wealth",
    "total": 1024,
    "slots": (
        {"slots": 904},
        {"item": "Rune spear", "quantity": 1, "slots": 64},
        {"item": "Shield left half", "quantity": 1, "slots": 32},
        {"item": "Dragon spear", "quantity": 1, "slots": 24},
    ),
}


COMBAT_GEM_DROP_TABLE = {
    "name": "Gem",
    "source": f"{GLOBAL_GEMS_SOURCE_PATH}: Gems.gemTable without Ring of Wealth",
    "total": 1024,
    "slots": (
        {"slots": 512},
        {"item": "Uncut sapphire", "quantity": 1, "slots": 240},
        {"item": "Uncut emerald", "quantity": 1, "slots": 112},
        {"item": "Uncut ruby", "quantity": 1, "slots": 64},
        {"item": "Chaos talisman", "quantity": 1, "slots": 24},
        {"item": "Nature talisman", "quantity": 1, "slots": 24},
        {"item": "Uncut diamond", "quantity": 1, "slots": 16},
        {"item": "Rune javelin", "quantity": 5, "slots": 8},
        {"item": "Loop half of a key", "quantity": 1, "slots": 8},
        {"item": "Tooth half of a key", "quantity": 1, "slots": 8},
        {"table": COMBAT_MEGA_RARE_DROP_TABLE, "slots": 8},
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


CHAOS_DRUID_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Law rune", "quantity": 2, "slots": 7},
                {"item": "Mithril bolts", "quantity_range": (2, 12), "slots": 5},
                {"item": "Air rune", "quantity": 36, "slots": 3},
                {"item": "Body rune", "quantity": 9, "slots": 2},
                {"item": "Earth rune", "quantity": 9, "slots": 2},
                {"item": "Mind rune", "quantity": 12, "slots": 2},
                {"item": "Nature rune", "quantity": 3, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 46},
                {"item": "Coins", "quantity": 3, "slots": 5},
                {"item": "Coins", "quantity": 8, "slots": 5},
                {"item": "Coins", "quantity": 29, "slots": 3},
                {"item": "Coins", "quantity": 35, "slots": 1},
                {"slots": 33},
                {"item": "Vial of water", "quantity": 1, "slots": 10},
                {"item": "Bronze longsword", "quantity": 1, "slots": 1},
                {"item": "Snape grass", "quantity": 1, "slots": 1},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
            ),
        },
    ),
}


WHITE_KNIGHT_LEVEL_36_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 1},
                {"item": "Steel med helm", "quantity": 1, "slots": 1},
                {"item": "Mind rune", "quantity": 5, "slots": 11},
                {"item": "Nature rune", "quantity": 4, "slots": 4},
                {"item": "Body rune", "quantity_range": (9, 13), "slots": 3},
                {"item": "Chaos rune", "quantity": 2, "slots": 3},
                {"item": "Water rune", "quantity_range": (25, 30), "slots": 3},
                {"item": "Mithril arrows", "quantity": 5, "slots": 2},
                {"item": "Adamant arrows", "quantity": 2, "slots": 1},
                {"item": "Blood rune", "quantity": 2, "slots": 1},
                {"item": "Law rune", "quantity": 2, "slots": 1},
                {"item": "Coins", "quantity": 48, "slots": 15},
                {"item": "Coins", "quantity": 15, "slots": 15},
                {"item": "Coins", "quantity": 8, "slots": 10},
                {"item": "Coins", "quantity_range": (45, 53), "slots": 10},
                {"item": "Coins", "quantity": 1, "slots": 5},
                {"item": "Coins", "quantity": 2, "slots": 5},
                {"item": "Coins", "quantity": 120, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 6},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"slots": 2},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 5},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 15},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
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
}


WHITE_KNIGHT_LEVEL_38_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 130,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 1},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 5, "slots": 8},
                {"item": "Nature rune", "quantity": 4, "slots": 4},
                {"item": "Body rune", "quantity_range": (10, 14), "slots": 3},
                {"item": "Chaos rune", "quantity": 3, "slots": 3},
                {"item": "Water rune", "quantity_range": (30, 35), "slots": 3},
                {"item": "Mithril arrows", "quantity": 5, "slots": 2},
                {"item": "Adamant arrows", "quantity": 2, "slots": 3},
                {"item": "Blood rune", "quantity": 2, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 1},
                {"item": "Coins", "quantity": 15, "slots": 13},
                {"item": "Coins", "quantity": 10, "slots": 15},
                {"item": "Coins", "quantity": 54, "slots": 10},
                {"item": "Coins", "quantity_range": (50, 58), "slots": 10},
                {"item": "Coins", "quantity": 3, "slots": 6},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 120, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 8},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
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
}


WHITE_KNIGHT_LEVEL_39_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 2},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 10, "slots": 8},
                {"item": "Nature rune", "quantity": 6, "slots": 4},
                {"item": "Body rune", "quantity_range": (15, 19), "slots": 3},
                {"item": "Chaos rune", "quantity": 4, "slots": 3},
                {"item": "Water rune", "quantity_range": (35, 40), "slots": 3},
                {"item": "Mithril arrows", "quantity": 7, "slots": 5},
                {"item": "Adamant arrows", "quantity": 4, "slots": 3},
                {"item": "Blood rune", "quantity": 3, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 1},
                {"item": "Coins", "quantity_range": (15, 19), "slots": 13},
                {"item": "Coins", "quantity": 15, "slots": 10},
                {"item": "Coins", "quantity_range": (55, 63), "slots": 10},
                {"item": "Coins", "quantity_range": (50, 69), "slots": 10},
                {"item": "Coins", "quantity": 5, "slots": 6},
                {"item": "Coins", "quantity": 120, "slots": 2},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 6},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
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
}


WHITE_KNIGHT_LEVEL_42_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Iron longsword", "quantity": 1, "slots": 2},
                {"item": "Steel sword", "quantity": 1, "slots": 2},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 12, "slots": 3},
                {"item": "Nature rune", "quantity": 7, "slots": 4},
                {"item": "Body rune", "quantity_range": (15, 24), "slots": 3},
                {"item": "Chaos rune", "quantity": 5, "slots": 3},
                {"item": "Water rune", "quantity_range": (40, 47), "slots": 3},
                {"item": "Mithril arrows", "quantity": 9, "slots": 5},
                {"item": "Adamant arrows", "quantity": 5, "slots": 3},
                {"item": "Blood rune", "quantity": 3, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 1},
                {"item": "Coins", "quantity_range": (51, 55), "slots": 13},
                {"item": "Coins", "quantity": 15, "slots": 10},
                {"item": "Coins", "quantity_range": (65, 73), "slots": 10},
                {"item": "Coins", "quantity": 8, "slots": 6},
                {"item": "Coins", "quantity_range": (50, 69), "slots": 5},
                {"item": "Coins", "quantity": 120, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 1},
                {"item": "Iron bar", "quantity": 2, "slots": 5},
                {"item": "Iron bar", "quantity": 1, "slots": 2},
                {"item": "Half an apple pie", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"item": "Pot of flour", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 28},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
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
}


OUTLAW_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 127,
            "slots": (
                {"item": "Bronze med helm", "quantity": 1, "slots": 2},
                {"item": "Mind rune", "quantity": 9, "slots": 2},
                {"item": "Water rune", "quantity": 6, "slots": 2},
                {"item": "Earth rune", "quantity": 5, "slots": 2},
                {"item": "Coins", "quantity": 5, "slots": 12},
                {"item": "Coins", "quantity": 15, "slots": 4},
                {"item": "Coins", "quantity": 25, "slots": 1},
                {"item": "Rope", "quantity": 1, "slots": 46},
                {"item": "Fishing bait", "quantity": 1, "slots": 15},
                {"item": "Cabbage", "quantity": 1, "slots": 6},
                {"item": "Copper ore", "quantity": 1, "slots": 2},
                {"item": "Knife", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 32},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 360},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 573},
            ),
        },
    ),
}


CHAOS_DWARF_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Steel full helm", "quantity": 1, "slots": 2},
                {"item": "Mithril longsword", "quantity": 1, "slots": 1},
                {"item": "Mithril sq shield", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 4},
                {"item": "Air rune", "quantity": 24, "slots": 3},
                {"item": "Chaos rune", "quantity": 10, "slots": 3},
                {"item": "Mind rune", "quantity": 37, "slots": 3},
                {"item": "Nature rune", "quantity": 9, "slots": 3},
                {"item": "Cosmic rune", "quantity": 3, "slots": 2},
                {"item": "Death rune", "quantity": 3, "slots": 1},
                {"item": "Water rune", "quantity": 10, "slots": 1},
                {"item": "Coins", "quantity": 92, "slots": 40},
                {"item": "Coins", "quantity": 47, "slots": 18},
                {"item": "Coins", "quantity": 25, "slots": 11},
                {"item": "Coins", "quantity": 150, "slots": 10},
                {"item": "Coins", "quantity": 350, "slots": 2},
                {"item": "Coins", "quantity": 15, "slots": 2},
                {"slots": 5},
                {"item": "Coal", "quantity": 1, "slots": 1},
                {"item": "Muddy key", "quantity": 1, "slots": 7},
                {"item": "Cheese", "quantity": 1, "slots": 1},
                {"item": "Mithril bar", "quantity": 1, "slots": 6},
                {"item": "Tomato", "quantity": 1, "slots": 1},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 100},
                {"item": "Green charm", "quantity": 1, "slots": 50},
                {"item": "Crimson charm", "quantity": 1, "slots": 20},
                {"item": "Blue charm", "quantity": 1, "slots": 20},
                {"slots": 810},
            ),
        },
    ),
}


HAAKON_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron hatchet", "quantity": 1, "slots": 48},
                {"item": "Bronze battleaxe", "quantity": 1, "slots": 32},
                {"item": "Iron mace", "quantity": 1, "slots": 8},
                {"item": "Chaos rune", "quantity": 3, "slots": 32},
                {"item": "Bronze arrows", "quantity": 10, "slots": 24},
                {"item": "Earth rune", "quantity": 5, "slots": 24},
                {"item": "Iron arrows", "quantity": 8, "slots": 24},
                {"item": "Fire rune", "quantity": 8, "slots": 16},
                {"item": "Mind rune", "quantity": 10, "slots": 16},
                {"item": "Law rune", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 8, "slots": 317},
                {"item": "Coins", "quantity": 12, "slots": 76},
                {"item": "Coins", "quantity": 25, "slots": 45},
                {"item": "Coins", "quantity": 32, "slots": 26},
                {"slots": 288},
                {"item": "Tin ore", "quantity": 1, "slots": 8},
                {"item": "Bear fur", "quantity": 1, "slots": 8},
                {"item": "Beer", "quantity": 1, "slots": 8},
                {"item": "Cooked meat", "quantity": 1, "slots": 8},
                {"item": "Ring mould", "quantity": 1, "slots": 8},
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


HAM_GUARD_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 648,
            "slots": (
                {"item": "Bronze hatchet", "quantity": 1, "slots": 18},
                {"item": "Bronze dagger", "quantity": 1, "slots": 18},
                {"item": "Bronze pickaxe", "quantity": 1, "slots": 18},
                {"item": "Iron hatchet", "quantity": 1, "slots": 18},
                {"item": "Iron dagger", "quantity": 1, "slots": 18},
                {"item": "Iron pickaxe", "quantity": 1, "slots": 18},
                {"item": "Leather body", "quantity": 1, "slots": 18},
                {"item": "Steel hatchet", "quantity": 1, "slots": 12},
                {"item": "Steel dagger", "quantity": 1, "slots": 12},
                {"item": "Steel pickaxe", "quantity": 1, "slots": 12},
                {"item": "H.A.M. boots", "quantity": 1, "slots": 12},
                {"item": "H.A.M. cloak", "quantity": 1, "slots": 6},
                {"item": "H.A.M. gloves", "quantity": 1, "slots": 15},
                {"item": "H.A.M. hood", "quantity": 1, "slots": 6},
                {"item": "H.A.M. logo", "quantity": 1, "slots": 8},
                {"item": "H.A.M. robe", "quantity": 1, "slots": 8},
                {"item": "H.A.M. shirt", "quantity": 1, "slots": 8},
                {"item": "Bronze arrows", "quantity_range": (1, 12), "slots": 16},
                {"item": "Steel arrows", "quantity_range": (1, 10), "slots": 12},
                {"item": "Grimy guam", "quantity": 1, "slots": 6},
                {"item": "Grimy marrentill", "quantity": 1, "slots": 3},
                {"item": "Grimy tarromin", "quantity": 1, "slots": 2},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 57},
                {"item": "Cowhide", "quantity_range": (1, 3), "slots": 18},
                {"item": "Logs", "quantity_range": (1, 3), "slots": 18},
                {"item": "Raw anchovies", "quantity_range": (1, 3), "slots": 12},
                {"item": "Raw chicken", "quantity_range": (1, 3), "slots": 12},
                {"item": "Uncut opal", "quantity": 1, "slots": 12},
                {"item": "Uncut jade", "quantity": 1, "slots": 12},
                {"item": "Iron ore", "quantity": 1, "slots": 12},
                {"item": "Coal", "quantity": 1, "slots": 12},
                {"item": "Coins", "quantity_range": (1, 20), "slots": 81},
                {"item": "Buttons", "quantity": 1, "slots": 24},
                {"item": "Damaged armour", "quantity": 1, "slots": 24},
                {"item": "Rusty sword", "quantity": 1, "slots": 24},
                {"item": "Knife", "quantity": 1, "slots": 12},
                {"item": "Needle", "quantity": 1, "slots": 12},
                {"item": "Tinderbox", "quantity": 1, "slots": 12},
                {"item": "Feather", "quantity_range": (1, 6), "slots": 18},
                {"item": "Thread", "quantity_range": (1, 10), "slots": 12},
            ),
        },
        {
            "name": "Tertiary",
            "total": 55,
            "slots": (
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 1},
                {"slots": 54},
            ),
        },
    ),
}


LOW_LEVEL_HUMANOID_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Bronze med helm", "quantity": 1, "slots": 16},
                {"item": "Bronze dagger", "quantity": 1, "slots": 8},
                {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 138},
                {"item": "Sling", "quantity": 1, "slots": 16},
                {"item": "Bronze arrows", "quantity": 7, "slots": 24},
                {"item": "Earth rune", "quantity": 4, "slots": 16},
                {"item": "Fire rune", "quantity": 6, "slots": 16},
                {"item": "Mind rune", "quantity": 9, "slots": 16},
                {"item": "Chaos rune", "quantity": 2, "slots": 8},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 152},
                {"item": "Coins", "quantity": 3, "slots": 277},
                {"item": "Coins", "quantity": 10, "slots": 138},
                {"item": "Coins", "quantity": 5, "slots": 73},
                {"item": "Coins", "quantity": 15, "slots": 32},
                {"item": "Coins", "quantity": 25, "slots": 8},
                {"slots": 16},
                {"item": "Fishing bait", "quantity": 1, "slots": 30},
                {"item": "Copper ore", "quantity": 1, "slots": 16},
                {"item": "Earth talisman", "quantity": 1, "slots": 16},
                {"item": "Cabbage", "quantity": 1, "slots": 8},
            ),
        },
        {
            "name": "Tertiary",
            "total": 1024,
            "slots": (
                {"slots": 1016},
                {"item": "Clue scroll (easy)", "quantity": 1, "slots": 8},
            ),
        },
    ),
}


PIRATE_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron dagger", "quantity": 1, "slots": 48},
                {"item": "Bronze scimitar", "quantity": 1, "slots": 32},
                {"item": "Iron platebody", "quantity": 1, "slots": 8},
                {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 80},
                {"item": "Chaos rune", "quantity": 2, "slots": 48},
                {"item": "Nature rune", "quantity": 2, "slots": 40},
                {"item": "Bronze arrows", "quantity": 9, "slots": 24},
                {"item": "Bronze arrows", "quantity": 12, "slots": 16},
                {"item": "Air rune", "quantity": 10, "slots": 16},
                {"item": "Earth rune", "quantity": 9, "slots": 16},
                {"item": "Fire rune", "quantity": 5, "slots": 16},
                {"item": "Law rune", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 4, "slots": 232},
                {"item": "Coins", "quantity": 25, "slots": 104},
                {"item": "Coins", "quantity": 7, "slots": 64},
                {"item": "Coins", "quantity": 12, "slots": 48},
                {"item": "Coins", "quantity": 35, "slots": 32},
                {"item": "Coins", "quantity": 55, "slots": 8},
                {"item": "Eye patch", "quantity": 1, "slots": 96},
                {"slots": 64},
                {"item": "Chef's hat", "quantity": 1, "slots": 8},
                {"item": "Iron bar", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 8},
            ),
        },
    ),
}


MONK_OF_ZAMORAK_LEVEL_45_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 20,
            "slots": (
                {"item": "Zamorak robe top", "quantity": 1, "slots": 1},
                {"item": "Zamorak robe bottom", "quantity": 1, "slots": 1},
                {"slots": 18},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 10},
                {"item": "Green charm", "quantity": 1, "slots": 100},
                {"item": "Crimson charm", "quantity": 1, "slots": 20},
                {"item": "Blue charm", "quantity": 1, "slots": 10},
                {"slots": 860},
            ),
        },
    ),
}


GIANT_RAT_DROPS = {"guaranteed": (("Bones", 1), ("Raw rat meat", 1)), "tables": ()}


DUCK_LAND_DROPS = {"guaranteed": (("Bones", 1),), "tables": ()}
DUCK_WATER_DROPS = {"guaranteed": (), "tables": ()}


UNICORN_DROPS = {
    "guaranteed": (("Bones", 1), ("Unicorn horn", 1)),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 130},
                {"item": "Green charm", "quantity": 1, "slots": 60},
                {"item": "Crimson charm", "quantity": 1, "slots": 40},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 765},
            ),
        },
    ),
}


BLACK_BEAR_DROPS = {
    "guaranteed": (("Bones", 1), ("Bear fur", 1), ("Raw bear meat", 1)),
    "tables": (
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 180},
                {"item": "Green charm", "quantity": 1, "slots": 8},
                {"item": "Crimson charm", "quantity": 1, "slots": 11},
                {"item": "Blue charm", "quantity": 1, "slots": 5},
                {"slots": 796},
            ),
        },
    ),
}


WOLF_LEVEL_11_DROPS = {
    "guaranteed": (("Wolf bones", 1), ("Bones", 1)),
    "tables": (
        {
            "name": "Main",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 20},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 50},
                {"item": "Blue charm", "quantity": 1, "slots": 10},
                {"slots": 890},
            ),
        },
    ),
}


WHITE_WOLF_DROPS = {
    "guaranteed": (("Wolf bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 110},
                {"item": "Green charm", "quantity": 1, "slots": 50},
                {"item": "Crimson charm", "quantity": 1, "slots": 140},
                {"item": "Blue charm", "quantity": 1, "slots": 80},
                {"slots": 620},
            ),
        },
    ),
}


GIANT_BAT_DROPS = {"guaranteed": (("Bat bones", 1),), "tables": ()}


SCORPION_CHARM_DROPS = {
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
}


HILL_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron full helm", "quantity": 1, "slots": 4},
                {"item": "Iron dagger", "quantity": 1, "slots": 5},
                {"item": "Iron kiteshield", "quantity": 1, "slots": 3},
                {"item": "Steel longsword", "quantity": 1, "slots": 2},
                {"item": "Iron arrows", "quantity": 3, "slots": 6},
                {"item": "Fire rune", "quantity": 15, "slots": 3},
                {"item": "Water rune", "quantity": 7, "slots": 3},
                {"item": "Law rune", "quantity": 2, "slots": 3},
                {"item": "Steel arrows", "quantity": 10, "slots": 2},
                {"item": "Mind rune", "quantity": 3, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 2},
                {"item": "Nature rune", "quantity": 6, "slots": 2},
                {"item": "Chaos rune", "quantity": 2, "slots": 1},
                {"item": "Death rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 7},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"item": "Coins", "quantity": 38, "slots": 15},
                {"item": "Coins", "quantity": 52, "slots": 10},
                {"item": "Coins", "quantity": 15, "slots": 8},
                {"item": "Coins", "quantity": 7, "slots": 6},
                {"item": "Coins", "quantity": 88, "slots": 2},
                {"slots": 1},
                {"item": "Limpwurt root", "quantity": 1, "slots": 11},
                {"item": "Beer", "quantity": 1, "slots": 6},
                {"item": "Body talisman", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 150},
                {"item": "Green charm", "quantity": 1, "slots": 10},
                {"item": "Crimson charm", "quantity": 1, "slots": 10},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 828},
            ),
        },
    ),
}


MOSS_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Black sq shield", "quantity": 1, "slots": 5},
                {"item": "Magic staff", "quantity": 1, "slots": 2},
                {"item": "Steel med helm", "quantity": 1, "slots": 2},
                {"item": "Mithril sword", "quantity": 1, "slots": 2},
                {"item": "Mithril spear", "quantity": 1, "slots": 2},
                {"item": "Steel kiteshield", "quantity": 1, "slots": 1},
                {"item": "Law rune", "quantity": 3, "slots": 4},
                {"item": "Air rune", "quantity": 18, "slots": 3},
                {"item": "Earth rune", "quantity": 27, "slots": 3},
                {"item": "Chaos rune", "quantity": 7, "slots": 3},
                {"item": "Nature rune", "quantity": 6, "slots": 3},
                {"item": "Cosmic rune", "quantity": 3, "slots": 2},
                {"item": "Iron arrows", "quantity": 15, "slots": 2},
                {"item": "Steel arrows", "quantity": 30, "slots": 1},
                {"item": "Death rune", "quantity": 3, "slots": 1},
                {"item": "Blood rune", "quantity": 1, "slots": 1},
                {"item": "Coins", "quantity": 37, "slots": 19},
                {"item": "Coins", "quantity": 2, "slots": 8},
                {"item": "Coins", "quantity": 119, "slots": 10},
                {"item": "Coins", "quantity": 300, "slots": 2},
                {"item": "Steel bar", "quantity": 1, "slots": 6},
                {"item": "Coal", "quantity": 1, "slots": 1},
                {"item": "Spinach roll", "quantity": 1, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 5},
                {"table": COMBAT_UNCOMMON_SEED_DROP_TABLE, "slots": 35},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 4},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 360},
                {"item": "Green charm", "quantity": 1, "slots": 30},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 573},
            ),
        },
    ),
}


ICE_GIANT_DROPS = {
    "guaranteed": (("Big bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Iron 2h sword", "quantity": 1, "slots": 40},
                {"item": "Black kiteshield", "quantity": 1, "slots": 32},
                {"item": "Steel hatchet", "quantity": 1, "slots": 32},
                {"item": "Steel sword", "quantity": 1, "slots": 32},
                {"item": "Iron platelegs", "quantity": 1, "slots": 8},
                {"item": "Mithril mace", "quantity": 1, "slots": 8},
                {"item": "Mithril sq shield", "quantity": 1, "slots": 8},
                {"item": "Adamant arrows", "quantity": 5, "slots": 48},
                {"item": "Nature rune", "quantity": 6, "slots": 32},
                {"item": "Mind rune", "quantity": 24, "slots": 24},
                {"item": "Body rune", "quantity": 37, "slots": 24},
                {"item": "Law rune", "quantity": 3, "slots": 16},
                {"item": "Water rune", "quantity": 12, "slots": 8},
                {"item": "Cosmic rune", "quantity": 4, "slots": 8},
                {"item": "Death rune", "quantity": 3, "slots": 8},
                {"item": "Blood rune", "quantity": 2, "slots": 8},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 64},
                {"item": "Coins", "quantity": 117, "slots": 224},
                {"item": "Coins", "quantity": 53, "slots": 76},
                {"item": "Coins", "quantity": 196, "slots": 72},
                {"item": "Coins", "quantity": 5, "slots": 64},
                {"item": "Coins", "quantity": 8, "slots": 54},
                {"item": "Coins", "quantity": 2, "slots": 48},
                {"item": "Coins", "quantity": 400, "slots": 16},
                {"item": "Jug of wine", "quantity": 1, "slots": 24},
                {"item": "Mithril ore", "quantity": 1, "slots": 8},
                {"item": "Banana", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 32},
            ),
        },
        {
            "name": "Tertiary",
            "total": 100000,
            "slots": (
                {"item": "Long bone", "quantity": 1, "slots": 250},
                {"item": "Curved bone", "quantity": 1, "slots": 20},
                {"item": "Champion's scroll", "quantity": 1, "slots": 20},
                {"slots": 99710},
            ),
        },
    ),
}


GHOST_DROPS = {"guaranteed": (), "tables": ()}


ZOMBIE_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron hatchet", "quantity": 1, "slots": 3},
                {"item": "Bronze longsword", "quantity": 1, "slots": 1},
                {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                {"item": "Bronze kiteshield", "quantity": 1, "slots": 3},
                {"item": "Iron arrows", "quantity": 5, "slots": 7},
                {"item": "Body rune", "quantity": 6, "slots": 5},
                {"item": "Mind rune", "quantity": 5, "slots": 5},
                {"item": "Air rune", "quantity": 13, "slots": 4},
                {"item": "Iron arrows", "quantity": 8, "slots": 4},
                {"item": "Steel arrows", "quantity": 6, "slots": 2},
                {"item": "Nature rune", "quantity": 6, "slots": 1},
                {"item": "Cosmic rune", "quantity": 4, "slots": 1},
                {"item": "Fire rune", "quantity": 7, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 25},
                {"item": "Coins", "quantity": 10, "slots": 36},
                {"item": "Coins", "quantity": 4, "slots": 4},
                {"item": "Coins", "quantity": 18, "slots": 3},
                {"item": "Coins", "quantity": 13, "slots": 2},
                {"item": "Coins", "quantity": 28, "slots": 2},
                {"slots": 8},
                {"item": "Fishing bait", "quantity": 5, "slots": 5},
                {"item": "Copper ore", "quantity": 1, "slots": 2},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 30},
                {"item": "Green charm", "quantity": 1, "slots": 17},
                {"item": "Crimson charm", "quantity": 1, "slots": 14},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 937},
            ),
        },
    ),
}


ZOMBIE_LEVEL_25_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron hatchet", "quantity": 1, "slots": 5},
                {"item": "Bronze longsword", "quantity": 1, "slots": 1},
                {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                {"item": "Bronze kiteshield", "quantity": 1, "slots": 3},
                {"item": "Iron arrows", "quantity": 5, "slots": 7},
                {"item": "Body rune", "quantity": 6, "slots": 5},
                {"item": "Mind rune", "quantity": 5, "slots": 5},
                {"item": "Air rune", "quantity": 13, "slots": 4},
                {"item": "Iron arrows", "quantity": 8, "slots": 4},
                {"item": "Steel arrows", "quantity": 6, "slots": 2},
                {"item": "Nature rune", "quantity": 6, "slots": 1},
                {"item": "Cosmic rune", "quantity": 4, "slots": 1},
                {"item": "Fire rune", "quantity": 7, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 25},
                {"item": "Coins", "quantity": 10, "slots": 36},
                {"item": "Coins", "quantity": 4, "slots": 4},
                {"item": "Coins", "quantity": 18, "slots": 3},
                {"item": "Coins", "quantity": 13, "slots": 2},
                {"item": "Coins", "quantity": 28, "slots": 2},
                {"slots": 6},
                {"item": "Fishing bait", "quantity": 5, "slots": 5},
                {"item": "Copper ore", "quantity": 1, "slots": 2},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 30},
                {"item": "Green charm", "quantity": 1, "slots": 17},
                {"item": "Crimson charm", "quantity": 1, "slots": 14},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 937},
            ),
        },
    ),
}


SKELETON_LOW_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 1024,
            "slots": (
                {"item": "Bronze arrows", "quantity": 2, "slots": 56},
                {"item": "Bronze arrows", "quantity": 5, "slots": 32},
                {"item": "Iron arrows", "quantity": 1, "slots": 32},
                {"item": "Steel arrows", "quantity": 1, "slots": 8},
                {"item": "Air rune", "quantity": 15, "slots": 16},
                {"item": "Earth rune", "quantity": 3, "slots": 16},
                {"item": "Fire rune", "quantity": 2, "slots": 16},
                {"item": "Chaos rune", "quantity": 3, "slots": 16},
                {"item": "Nature rune", "quantity": 3, "slots": 16},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 49},
                {"item": "Coins", "quantity": 2, "slots": 175},
                {"item": "Coins", "quantity": 12, "slots": 200},
                {"item": "Coins", "quantity": 4, "slots": 56},
                {"item": "Coins", "quantity": 16, "slots": 32},
                {"item": "Coins", "quantity": 25, "slots": 32},
                {"item": "Coins", "quantity": 33, "slots": 32},
                {"item": "Coins", "quantity": 48, "slots": 8},
                {"slots": 144},
                {"item": "Iron dagger", "quantity": 1, "slots": 48},
                {"item": "Fire talisman", "quantity": 1, "slots": 16},
                {"item": "Iron ore", "quantity": 1, "slots": 8},
                {"item": "Grain", "quantity": 1, "slots": 8},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 8},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 50},
                {"item": "Green charm", "quantity": 1, "slots": 12},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 14},
                {"slots": 894},
            ),
        },
    ),
}


SKELETON_HIGH_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Iron med helm", "quantity": 1, "slots": 6},
                {"item": "Iron sword", "quantity": 1, "slots": 4},
                {"item": "Iron hatchet", "quantity": 1, "slots": 2},
                {"item": "Iron scimitar", "quantity": 1, "slots": 1},
                {"item": "Air rune", "quantity": 15, "slots": 3},
                {"item": "Water rune", "quantity": 9, "slots": 3},
                {"item": "Chaos rune", "quantity": 5, "slots": 3},
                {"item": "Iron arrows", "quantity": 12, "slots": 2},
                {"item": "Law rune", "quantity": 2, "slots": 2},
                {"item": "Cosmic rune", "quantity": 2, "slots": 1},
                {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 20},
                {"item": "Coins", "quantity": 10, "slots": 24},
                {"item": "Coins", "quantity": 5, "slots": 25},
                {"item": "Coins", "quantity": 25, "slots": 8},
                {"item": "Coins", "quantity": 45, "slots": 4},
                {"item": "Coins", "quantity": 65, "slots": 3},
                {"item": "Coins", "quantity": 1, "slots": 2},
                {"slots": 8},
                {"item": "Bronze bar", "quantity": 1, "slots": 5},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 2},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 50},
                {"item": "Green charm", "quantity": 1, "slots": 12},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 14},
                {"slots": 894},
            ),
        },
    ),
}


DWARF_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 128,
            "slots": (
                {"item": "Bronze pickaxe", "quantity": 1, "slots": 13},
                {"item": "Bronze med helm", "quantity": 1, "slots": 4},
                {"item": "Bronze battleaxe", "quantity": 1, "slots": 2},
                {"item": "Iron battleaxe", "quantity": 1, "slots": 1},
                {"item": "Bronze bolts", "quantity_range": (2, 12), "slots": 7},
                {"item": "Chaos rune", "quantity": 2, "slots": 4},
                {"item": "Nature rune", "quantity": 2, "slots": 4},
                {"item": "Coins", "quantity": 4, "slots": 20},
                {"item": "Coins", "quantity": 10, "slots": 15},
                {"item": "Coins", "quantity": 30, "slots": 2},
                {"item": "Hammer", "quantity": 1, "slots": 10},
                {"item": "Bronze bar", "quantity": 1, "slots": 7},
                {"item": "Iron ore", "quantity": 1, "slots": 4},
                {"item": "Tin ore", "quantity": 1, "slots": 3},
                {"item": "Copper ore", "quantity": 1, "slots": 3},
                {"item": "Iron bar", "quantity": 1, "slots": 3},
                {"item": "Coal", "quantity": 1, "slots": 2},
                {"table": COMBAT_GEM_DROP_TABLE, "slots": 1},
                {"slots": 23},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 40},
                {"item": "Green charm", "quantity": 1, "slots": 20},
                {"item": "Crimson charm", "quantity": 1, "slots": 30},
                {"item": "Blue charm", "quantity": 1, "slots": 7},
                {"slots": 903},
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


GUARD_DROPS = {
    "guaranteed": (("Bones", 1),),
    "tables": (
        {
            "name": "Main",
            "total": 146,
            "slots": (
                {"item": "Iron bolts", "quantity_range": (2, 12), "slots": 10},
                {"item": "Steel arrows", "quantity": 1, "slots": 4},
                {"item": "Bronze arrows", "quantity": 1, "slots": 3},
                {"item": "Air rune", "quantity": 6, "slots": 2},
                {"item": "Earth rune", "quantity": 3, "slots": 2},
                {"item": "Fire rune", "quantity": 2, "slots": 2},
                {"item": "Bronze arrows", "quantity": 2, "slots": 2},
                {"item": "Blood rune", "quantity": 1, "slots": 1},
                {"item": "Chaos rune", "quantity": 1, "slots": 1},
                {"item": "Nature rune", "quantity": 1, "slots": 1},
                {"item": "Steel arrows", "quantity": 5, "slots": 1},
                {"item": "Coins", "quantity": 1, "slots": 19},
                {"item": "Coins", "quantity": 4, "slots": 8},
                {"item": "Coins", "quantity": 5, "slots": 18},
                {"item": "Coins", "quantity": 7, "slots": 16},
                {"item": "Coins", "quantity": 12, "slots": 9},
                {"item": "Coins", "quantity": 17, "slots": 4},
                {"item": "Coins", "quantity": 25, "slots": 4},
                {"item": "Coins", "quantity": 30, "slots": 2},
                {"item": "Iron dagger", "quantity": 1, "slots": 6},
                {"item": "Body talisman", "quantity": 1, "slots": 2},
                {"item": "Law talisman", "quantity": 1, "slots": 1},
                {"item": "Grain", "quantity": 1, "slots": 1},
                {"item": "Iron ore", "quantity": 1, "slots": 1},
                {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                {"slots": 8},
            ),
        },
        {
            "name": "Tertiary",
            "total": 128,
            "slots": (
                {"slots": 127},
                {"item": "Clue scroll (medium)", "quantity": 1, "slots": 1},
            ),
        },
        {
            "name": "Charms",
            "total": 1000,
            "slots": (
                {"item": "Gold charm", "quantity": 1, "slots": 70},
                {"item": "Green charm", "quantity": 1, "slots": 9},
                {"item": "Crimson charm", "quantity": 1, "slots": 5},
                {"item": "Blue charm", "quantity": 1, "slots": 2},
                {"slots": 914},
            ),
        },
    ),
}


COMBAT_FOOD_DATA: Dict[str, dict] = {
    "Crayfish": {"heal_lifepoints": 20, "source": FOOD_SOURCE_PATH},
    "Shrimps": {"heal_lifepoints": 30, "source": FOOD_SOURCE_PATH},
    "Cooked chicken": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Cooked meat": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Half an apple pie": {"heal_lifepoints": 70, "source": f"{FOOD_SOURCE_PATH}: HALF_AN_APPLE_PIE"},
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
        "drops": GIANT_RAT_DROPS,
        "source": (
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/critters/giant_rat_level_2.plugin.kts"
        ),
    },
    "giant_rat_level_6": {
        "display_name": "Giant rat",
        "level": 6,
        "group": "Rats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 100,
            "attack": 6,
            "strength": 5,
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
        "drops": GIANT_RAT_DROPS,
        "source": f"{GIANT_RAT_LEVEL_6_SOURCE_PATH}: id Npcs.GIANT_RAT_2091",
    },
    "giant_rat_level_26": {
        "display_name": "Giant rat",
        "level": 26,
        "group": "Rats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 250,
            "attack": 22,
            "strength": 23,
            "defence": 22,
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
        "drops": GIANT_RAT_DROPS,
        "source": f"{GIANT_RAT_LEVEL_26_SOURCE_PATH}: ids Npcs.GIANT_RAT_4944/Npcs.GIANT_RAT_4945",
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
    "chaos_druid": {
        "display_name": "Chaos druid",
        "level": 13,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 8,
            "strength": 8,
            "defence": 12,
            "magic": 10,
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
        "drops": CHAOS_DRUID_DROPS,
        "source": (
            f"{CHAOS_DRUID_SOURCE_PATH}: ids Npcs.CHAOS_DRUID_2547/Npcs.CHAOS_DRUID/"
            "Npcs.CHAOS_DRUID_7105; aggro radius 4"
        ),
    },
    "citizen": {
        "display_name": "Man/Woman",
        "level": 2,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": -21,
            "defence_slash": -21,
            "defence_crush": -21,
            "defence_magic": -21,
            "defence_ranged": -21,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": (
            f"{CITIZEN_SOURCE_PATH}: ids Npcs.MAN/Npcs.MAN_2/Npcs.MAN_3/Npcs.MAN_24/"
            "Npcs.WOMAN_BRUNETTE_LONGSKIRT_4/Npcs.WOMAN_BRUNETTE_PONYTAIL_5/"
            "Npcs.WOMAN_WOMAN_BLOND_PONYTAIL_6/Npcs.MAN_16/Npcs.MAN_3223/"
            "Npcs.WOMAN_BLOND_LONGSKIRT_3226"
        ),
    },
    "monk": {
        "display_name": "Monk",
        "level": 5,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 150,
            "attack": 2,
            "strength": 2,
            "defence": 3,
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
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": f"{MONK_SOURCE_PATH}: id Npcs.MONK_7727",
    },
    "cuffs": {
        "display_name": "Cuffs",
        "level": 3,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
            "attack": 1,
            "strength": 1,
            "defence": 3,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": 5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": f"{CUFFS_SOURCE_PATH}: id Npcs.CUFFS",
    },
    "narf_jeff_rusty": {
        "display_name": "Narf/Jeff/Rusty",
        "level": 2,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 70,
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": 5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": LOW_LEVEL_HUMANOID_DROPS,
        "source": f"{NARF_JEFF_RUSTY_SOURCE_PATH}: ids Npcs.NARF/Npcs.JEFF/Npcs.RUSTY",
    },
    "pirate": {
        "display_name": "Pirate",
        "level": 23,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 21,
            "strength": 21,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 8,
            "attack_crush": 8,
            "defence_stab": 3,
            "defence_slash": 2,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 10,
        },
        "drops": PIRATE_DROPS,
        "source": (
            f"{PIRATE_SOURCE_PATH}: ids Npcs.PIRATE/Npcs.PIRATE_183/Npcs.PIRATE_184; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses"
        ),
    },
    "monk_of_zamorak_level_45": {
        "display_name": "Monk of Zamorak",
        "level": 45,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 250,
        "stats": {
            "hitpoints": 400,
            "attack": 38,
            "strength": 38,
            "defence": 42,
            "magic": 40,
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
        "drops": MONK_OF_ZAMORAK_LEVEL_45_DROPS,
        "source": (
            f"{MONK_OF_ZAMORAK_LEVEL_45_SOURCE_PATH}: id Npcs.MONK_OF_ZAMORAK_190; "
            "Items.ZAMORAK_ROBE_1035 mapped to Zamorak robe top, "
            "Items.ZAMORAK_ROBE mapped to Zamorak robe bottom; aggro radius 4"
        ),
    },
    "unicorn": {
        "display_name": "Unicorn",
        "level": 15,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "stats": {
            "hitpoints": 190,
            "attack": 11,
            "strength": 13,
            "defence": 13,
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
        "drops": UNICORN_DROPS,
        "source": f"{UNICORN_SOURCE_PATH}: id Npcs.UNICORN",
    },
    "black_unicorn": {
        "display_name": "Black unicorn",
        "level": 27,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "stats": {
            "hitpoints": 290,
            "attack": 21,
            "strength": 21,
            "defence": 23,
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
        "drops": UNICORN_DROPS,
        "source": f"{BLACK_UNICORN_SOURCE_PATH}: id Npcs.BLACK_UNICORN",
    },
    "black_bear": {
        "display_name": "Black bear",
        "level": 19,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 15,
            "strength": 16,
            "defence": 13,
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
        "drops": BLACK_BEAR_DROPS,
        "source": f"{BLACK_BEAR_SOURCE_PATH}: id Npcs.BLACK_BEAR; SlayerAssignment.BEAR level 1 xp 25.0; aggro radius 4",
    },
    "wolf": {
        "display_name": "Wolf",
        "level": 11,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 10.0,
        "stats": {
            "hitpoints": 100,
            "attack": 10,
            "strength": 10,
            "defence": 10,
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
        "drops": WOLF_LEVEL_11_DROPS,
        "source": f"{WOLF_LEVEL_11_SOURCE_PATH}: ids Npcs.WOLF_4414/Npcs.WOLF_11263; SlayerAssignment.WOLF level 1 xp 10.0; aggro radius 4; attackStyle STAB",
    },
    "white_wolf_level_25": {
        "display_name": "White wolf",
        "level": 25,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 34.0,
        "stats": {
            "hitpoints": 340,
            "attack": 20,
            "strength": 16,
            "defence": 22,
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
        "drops": WHITE_WOLF_DROPS,
        "source": f"{WHITE_WOLF_LEVEL_25_SOURCE_PATH}: ids Npcs.WHITE_WOLF/Npcs.WOLF_4413/Npcs.WOLF_6047; SlayerAssignment.WOLF level 1 xp 34.0; aggro radius 4",
    },
    "white_wolf_level_38": {
        "display_name": "White wolf",
        "level": 38,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 44.0,
        "stats": {
            "hitpoints": 440,
            "attack": 30,
            "strength": 31,
            "defence": 32,
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
        "drops": WHITE_WOLF_DROPS,
        "source": f"{WHITE_WOLF_LEVEL_38_SOURCE_PATH}: id Npcs.WHITE_WOLF_97; SlayerAssignment.WOLF level 1 xp 44.0; aggro radius 4",
    },
    "big_wolf": {
        "display_name": "Big wolf",
        "level": 73,
        "group": "Animals",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 90,
        "slayer_xp": 74.0,
        "stats": {
            "hitpoints": 740,
            "attack": 60,
            "strength": 61,
            "defence": 62,
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
        "drops": WHITE_WOLF_DROPS,
        "source": f"{BIG_WOLF_SOURCE_PATH}: id Npcs.BIG_WOLF_6046; SlayerAssignment.WOLF level 1 xp 74.0; aggro radius 4",
    },
    "giant_bat": {
        "display_name": "Giant bat",
        "level": 27,
        "group": "Bats",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 32.0,
        "stats": {
            "hitpoints": 320,
            "attack": 22,
            "strength": 22,
            "defence": 22,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 10,
            "defence_slash": 10,
            "defence_crush": 12,
            "defence_magic": 10,
            "defence_ranged": 8,
            "melee_strength": 0,
        },
        "drops": GIANT_BAT_DROPS,
        "source": f"{GIANT_BAT_SOURCE_PATH}: id Npcs.GIANT_BAT; SlayerAssignment.BAT level 1 xp 32.0; aggro radius 4",
    },
    "hill_giant": {
        "display_name": "Hill giant",
        "level": 28,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "slayer_xp": 35.0,
        "stats": {
            "hitpoints": 350,
            "attack": 18,
            "strength": 22,
            "defence": 26,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 18,
            "attack_slash": 0,
            "attack_crush": 16,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": HILL_GIANT_DROPS,
        "source": (
            f"{HILL_GIANT_SOURCE_PATH}: id Npcs.HILL_GIANT; "
            "SlayerAssignment.HILL_GIANT level 1 xp 35.0; attackStyle CRUSH; aggro radius 4"
        ),
    },
    "moss_giant": {
        "display_name": "Moss giant",
        "level": 42,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 30,
        "slayer_xp": 60.0,
        "stats": {
            "hitpoints": 600,
            "attack": 30,
            "strength": 30,
            "defence": 30,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 33,
            "attack_slash": 0,
            "attack_crush": 31,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": MOSS_GIANT_DROPS,
        "source": (
            f"{MOSS_GIANT_SOURCE_PATH}: ids Npcs.MOSS_GIANT/Npcs.MOSS_GIANT_1587/"
            "Npcs.MOSS_GIANT_1588/Npcs.MOSS_GIANT_4688; SlayerAssignment.MOSS_GIANT level 1 "
            "xp 60.0; attackStyle CRUSH; aggro radius 4"
        ),
    },
    "ice_giant": {
        "display_name": "Ice giant",
        "level": 53,
        "group": "Giants",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 30,
        "slayer_xp": 70.0,
        "stats": {
            "hitpoints": 700,
            "attack": 40,
            "strength": 40,
            "defence": 40,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 29,
            "attack_slash": 29,
            "attack_crush": 29,
            "defence_stab": 0,
            "defence_slash": 3,
            "defence_crush": 2,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 31,
        },
        "drops": ICE_GIANT_DROPS,
        "source": (
            f"{ICE_GIANT_SOURCE_PATH}: ids Npcs.ICE_GIANT/Npcs.ICE_GIANT_3072/Npcs.ICE_GIANT_4685/"
            "Npcs.ICE_GIANT_4686/Npcs.ICE_GIANT_4687; SlayerAssignment.ICE_GIANT level 1 "
            "xp 70.0; attackStyle SLASH; attackBonus/strengthBonus; aggro radius 5"
        ),
    },
    "ghost": {
        "display_name": "Ghost",
        "level": 19,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 40,
        "slayer_xp": 25.0,
        "stats": {
            "hitpoints": 250,
            "attack": 13,
            "strength": 13,
            "defence": 18,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": -5,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": GHOST_DROPS,
        "source": f"{GHOST_LEVEL_19_SOURCE_PATH}: ids Npcs.GHOST/Npcs.GHOST_104/Npcs.GHOST_5349/Npcs.GHOST_5350/Npcs.GHOST_5351/Npcs.GHOST_5352; SlayerAssignment.GHOST level 1 xp 25.0; attackStyle CRUSH; no on_npc_death drop callback",
    },
    "zombie_level_13": {
        "display_name": "Zombie",
        "level": 13,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 22.0,
        "stats": {
            "hitpoints": 220,
            "attack": 8,
            "strength": 9,
            "defence": 10,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_13_SOURCE_PATH}: id Npcs.ZOMBIE; SlayerAssignment.ZOMBIE level 1 xp 22.0; aggro radius 4",
    },
    "zombie_level_18": {
        "display_name": "Zombie",
        "level": 18,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 24.0,
        "stats": {
            "hitpoints": 240,
            "attack": 13,
            "strength": 13,
            "defence": 18,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_18_SOURCE_PATH}: id Npcs.ZOMBIE_74; SlayerAssignment.ZOMBIE level 1 xp 24.0; aggro radius 4",
    },
    "zombie_level_24": {
        "display_name": "Zombie",
        "level": 24,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 300,
            "attack": 19,
            "strength": 21,
            "defence": 16,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 9,
            "defence_slash": 8,
            "defence_crush": 12,
            "defence_magic": 10,
            "defence_ranged": 11,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_24_SOURCE_PATH}: id Npcs.ZOMBIE_75; SlayerAssignment.ZOMBIE level 1 xp 30.0; aggro radius 4",
    },
    "zombie_level_25": {
        "display_name": "Zombie",
        "level": 25,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 300,
            "attack": 19,
            "strength": 21,
            "defence": 16,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 9,
            "defence_slash": 8,
            "defence_crush": 12,
            "defence_magic": 10,
            "defence_ranged": 11,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_LEVEL_25_DROPS,
        "source": f"{ZOMBIE_LEVEL_25_SOURCE_PATH}: id Npcs.ZOMBIE_76; SlayerAssignment.ZOMBIE level 1 xp 30.0; level-specific main table has Iron hatchet 5/128 and empty 6/128",
    },
    "zombie_level_30": {
        "display_name": "Zombie",
        "level": 30,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 300,
            "attack": 25,
            "strength": 29,
            "defence": 20,
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
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_30_SOURCE_PATH}: ids Npcs.ZOMBIE_5375/Npcs.ZOMBIE_4392/Npcs.ZOMBIE_5376; SlayerAssignment.ZOMBIE level 1 xp 30.0; aggro radius 4",
    },
    "zombie_level_44": {
        "display_name": "Zombie",
        "level": 44,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 30.0,
        "stats": {
            "hitpoints": 400,
            "attack": 35,
            "strength": 40,
            "defence": 40,
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
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_44_SOURCE_PATH}: ids Npcs.ZOMBIE_4393/Npcs.ZOMBIE_5377/Npcs.ZOMBIE_5378; SlayerAssignment.ZOMBIE level 1 xp 30.0; aggro radius 4",
    },
    "zombie_level_53": {
        "display_name": "Zombie",
        "level": 53,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 35,
        "slayer_xp": 50.0,
        "stats": {
            "hitpoints": 500,
            "attack": 55,
            "strength": 40,
            "defence": 48,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 19,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 0,
            "defence_slash": 18,
            "defence_crush": 0,
            "defence_magic": 20,
            "defence_ranged": 21,
            "melee_strength": 0,
        },
        "drops": ZOMBIE_DROPS,
        "source": f"{ZOMBIE_LEVEL_53_SOURCE_PATH}: ids Npcs.ZOMBIE_4394/Npcs.ZOMBIE_5379/Npcs.ZOMBIE_5380; SlayerAssignment.ZOMBIE level 1 xp 50.0; aggro radius 4",
    },
    "skeleton_level_21": {
        "display_name": "Skeleton",
        "level": 21,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 35,
        "slayer_xp": 24.0,
        "stats": {
            "hitpoints": 240,
            "attack": 17,
            "strength": 17,
            "defence": 17,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": SKELETON_LOW_DROPS,
        "source": f"{SKELETON_LEVEL_21_SOURCE_PATH}: id Npcs.SKELETON_91; SlayerAssignment.SKELETON level 1 xp 24.0; aggro radius 4",
    },
    "skeleton_level_22": {
        "display_name": "Skeleton",
        "level": 22,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 70,
        "slayer_xp": 29.0,
        "stats": {
            "hitpoints": 290,
            "attack": 15,
            "strength": 18,
            "defence": 17,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": SKELETON_LOW_DROPS,
        "source": f"{SKELETON_LEVEL_22_SOURCE_PATH}: ids Npcs.SKELETON/Npcs.SKELETON_5332/Npcs.SKELETON_5333/Npcs.SKELETON_5334; SlayerAssignment.SKELETON level 1 xp 29.0; aggro radius 4",
    },
    "skeleton_level_25": {
        "display_name": "Skeleton",
        "level": 25,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "slayer_xp": 17.0,
        "stats": {
            "hitpoints": 170,
            "attack": 24,
            "strength": 24,
            "defence": 24,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 15,
            "attack_slash": 0,
            "attack_crush": 14,
            "defence_stab": 9,
            "defence_slash": 11,
            "defence_crush": -2,
            "defence_magic": 1,
            "defence_ranged": 4,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_25_SOURCE_PATH}: id Npcs.SKELETON_92; SlayerAssignment.SKELETON level 1 xp 17.0; aggro radius 4",
    },
    "skeleton_level_45": {
        "display_name": "Skeleton",
        "level": 45,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "slayer_xp": 59.0,
        "stats": {
            "hitpoints": 590,
            "attack": 32,
            "strength": 35,
            "defence": 36,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 15,
            "attack_slash": 0,
            "attack_crush": 14,
            "defence_stab": 9,
            "defence_slash": 11,
            "defence_crush": -2,
            "defence_magic": 1,
            "defence_ranged": 4,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_45_SOURCE_PATH}: id Npcs.SKELETON_93; SlayerAssignment.SKELETON level 1 xp 59.0; no aggro block in source",
    },
    "skeleton_level_60": {
        "display_name": "Skeleton",
        "level": 60,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 70,
        "slayer_xp": 70.0,
        "stats": {
            "hitpoints": 700,
            "attack": 50,
            "strength": 50,
            "defence": 40,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 35,
            "defence_slash": 35,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 35,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_60_SOURCE_PATH}: ids Npcs.SKELETON_4385/Npcs.SKELETON_5365/Npcs.SKELETON_5366; SlayerAssignment.SKELETON level 1 xp 70.0; aggro radius 4",
    },
    "skeleton_level_68": {
        "display_name": "Skeleton",
        "level": 68,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "slayer_xp": 65.0,
        "stats": {
            "hitpoints": 700,
            "attack": 60,
            "strength": 50,
            "defence": 60,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 35,
            "defence_slash": 35,
            "defence_crush": -5,
            "defence_magic": 0,
            "defence_ranged": 35,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_68_SOURCE_PATH}: id Npcs.SKELETON_4384; SlayerAssignment.SKELETON level 1 xp 65.0; aggro radius 4",
    },
    "skeleton_level_85": {
        "display_name": "Skeleton",
        "level": 85,
        "group": "Undead",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 60,
        "slayer_xp": 65.0,
        "stats": {
            "hitpoints": 770,
            "attack": 74,
            "strength": 74,
            "defence": 74,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 15,
            "attack_slash": 14,
            "attack_crush": 0,
            "defence_stab": 79,
            "defence_slash": 31,
            "defence_crush": 20,
            "defence_magic": 5,
            "defence_ranged": 70,
            "melee_strength": 0,
        },
        "drops": SKELETON_HIGH_DROPS,
        "source": f"{SKELETON_LEVEL_85_SOURCE_PATH}: ids Npcs.SKELETON_4386/Npcs.SKELETON_5367/Npcs.SKELETON_5368; SlayerAssignment.SKELETON level 1 xp 65.0; aggro radius 4",
    },
    "duck_land": {
        "display_name": "Duck (land)",
        "level": 1,
        "group": "Birds",
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
        "drops": DUCK_LAND_DROPS,
        "source": f"{DUCK_SOURCE_PATH}: land ids Npcs.DUCK_6113/Npcs.DRAKE",
    },
    "duck_water": {
        "display_name": "Duck (water)",
        "level": 1,
        "group": "Birds",
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
        "drops": DUCK_WATER_DROPS,
        "source": f"{DUCK_SOURCE_PATH}: water ids Npcs.DUCK/Npcs.DUCK_2693; no death drop callback",
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
    "dwarf_level_10": {
        "display_name": "Dwarf (level 10)",
        "level": 10,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 50,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 160,
            "attack": 8,
            "strength": 8,
            "defence": 6,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 5,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": DWARF_DROPS,
        "source": f"{DWARF_SOURCE_PATH}: idsLevel10 Npcs.DWARF_118/Npcs.DWARF_3221/Npcs.DWARF_3272",
    },
    "dwarf_level_11": {
        "display_name": "Dwarf (level 11)",
        "level": 11,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 16.0,
        "stats": {
            "hitpoints": 180,
            "attack": 8,
            "strength": 8,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 5,
            "defence_ranged": 10,
            "melee_strength": 0,
        },
        "drops": DWARF_DROPS,
        "source": (
            f"{DWARF_SOURCE_PATH}: idsLevel11 Npcs.DWARF_3219/Npcs.DWARF_3220/"
            "Npcs.DWARF_3268/Npcs.DWARF_3269/Npcs.DWARF_3270"
        ),
    },
    "market_guard": {
        "display_name": "Market guard",
        "level": 20,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 17,
            "strength": 18,
            "defence": 13,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 9,
            "attack_slash": 0,
            "attack_crush": 7,
            "defence_stab": 24,
            "defence_slash": 14,
            "defence_crush": 19,
            "defence_magic": 4,
            "defence_ranged": 16,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": f"{MARKET_GUARD_SOURCE_PATH}: id Npcs.MARKET_GUARD_2236",
    },
    "jail_guard": {
        "display_name": "Jail guard",
        "level": 26,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 30,
        "stats": {
            "hitpoints": 320,
            "attack": 19,
            "strength": 23,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 5,
            "attack_slash": 0,
            "attack_crush": 9,
            "defence_stab": 8,
            "defence_slash": 9,
            "defence_crush": 10,
            "defence_magic": 4,
            "defence_ranged": 9,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (("Bones", 1),), "tables": ()},
        "source": (
            f"{JAIL_GUARD_SOURCE_PATH}: ids Npcs.JAIL_GUARD/Npcs.JAIL_GUARD_448/"
            "Npcs.JAIL_GUARD_449/Npcs.JAIL_GUARD_917; aggro radius 4"
        ),
    },
    "guard_varrock": {
        "display_name": "Guard (Varrock)",
        "level": 21,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 19,
            "strength": 18,
            "defence": 14,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 0,
            "attack_crush": 5,
            "defence_stab": 24,
            "defence_slash": 30,
            "defence_crush": 25,
            "defence_magic": -9,
            "defence_ranged": 25,
            "melee_strength": 0,
        },
        "drops": GUARD_DROPS,
        "source": f"{GUARD_SOURCE_PATH}: varrockId Npcs.GUARD_5919/Npcs.GUARD_5920; faladorCrossbowId excluded because source comments no definition yet",
    },
    "guard_sword": {
        "display_name": "Guard (sword)",
        "level": 21,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 19,
            "strength": 18,
            "defence": 14,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 4,
            "attack_slash": 0,
            "attack_crush": 5,
            "defence_stab": 18,
            "defence_slash": 25,
            "defence_crush": 19,
            "defence_magic": -4,
            "defence_ranged": 20,
            "melee_strength": 0,
        },
        "drops": GUARD_DROPS,
        "source": (
            f"{GUARD_SOURCE_PATH}: faladorSwordId Npcs.GUARD/Npcs.GUARD_3228; "
            "edgevilleId Npcs.GUARD_296/Npcs.GUARD_297/Npcs.GUARD_298/Npcs.GUARD_299/"
            "Npcs.GUARD_3407/Npcs.GUARD_3408; faladorCrossbowId excluded because source comments no definition yet"
        ),
    },
    "guard_battleaxe": {
        "display_name": "Guard (battleaxe)",
        "level": 21,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 220,
            "attack": 15,
            "strength": 15,
            "defence": 16,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 6,
            "attack_slash": 0,
            "attack_crush": 10,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 5,
            "defence_magic": -4,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": GUARD_DROPS,
        "source": f"{GUARD_SOURCE_PATH}: faladorBattleaxeId Npcs.GUARD_3230/Npcs.GUARD_3241; faladorCrossbowId excluded because source comments no definition yet",
    },
    "black_knight": {
        "display_name": "Black knight",
        "level": 33,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 5,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 420,
            "attack": 25,
            "strength": 25,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 18,
            "attack_slash": 0,
            "attack_crush": 16,
            "defence_stab": 73,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 72,
            "melee_strength": 0,
        },
        "drops": {
            "guaranteed": (("Bones", 1),),
            "tables": (
                {
                    "name": "Main",
                    "total": 116,
                    "slots": (
                        {"item": "Iron sword", "quantity": 1, "slots": 4},
                        {"item": "Iron full helm", "quantity": 1, "slots": 2},
                        {"item": "Steel mace", "quantity": 1, "slots": 1},
                        {"item": "Mithril arrows", "quantity": 3, "slots": 4},
                        {"item": "Body rune", "quantity": 9, "slots": 3},
                        {"item": "Chaos rune", "quantity": 6, "slots": 3},
                        {"item": "Earth rune", "quantity": 10, "slots": 3},
                        {"item": "Death rune", "quantity": 2, "slots": 2},
                        {"item": "Law rune", "quantity": 3, "slots": 2},
                        {"item": "Cosmic rune", "quantity": 7, "slots": 1},
                        {"item": "Mind rune", "quantity": 2, "slots": 1},
                        {"item": "Steel bar", "quantity": 1, "slots": 6},
                        {"item": "Tin ore", "quantity": 1, "slots": 1},
                        {"item": "Pot of flour", "quantity": 1, "slots": 1},
                        {"item": "Coins", "quantity": 35, "slots": 21},
                        {"item": "Coins", "quantity": 6, "slots": 11},
                        {"item": "Coins", "quantity": 58, "slots": 10},
                        {"item": "Coins", "quantity": 12, "slots": 9},
                        {"item": "Coins", "quantity": 80, "slots": 2},
                        {"item": "Coins", "quantity": 1, "slots": 1},
                        {"item": "Coins", "quantity": 13, "slots": 1},
                        {"item": "Bread", "quantity": 1, "slots": 1},
                        {"table": COMBAT_MINOR_HERB_DROP_TABLE, "slots": 3},
                        {"table": COMBAT_ALLOTMENT_SEED_DROP_TABLE, "slots": 18},
                        {"table": COMBAT_GEM_DROP_TABLE, "slots": 3},
                        {"slots": 2},
                    ),
                },
                {
                    "name": "Charms",
                    "total": 1000,
                    "slots": (
                        {"item": "Gold charm", "quantity": 1, "slots": 30},
                        {"item": "Green charm", "quantity": 1, "slots": 10},
                        {"item": "Crimson charm", "quantity": 1, "slots": 8},
                        {"item": "Blue charm", "quantity": 1, "slots": 8},
                        {"slots": 944},
                    ),
                },
            ),
        },
        "source": (
            f"{BLACK_KNIGHT_SOURCE_PATH}: id Npcs.BLACK_KNIGHT; "
            "main table declares total(128), active source slots sum to 116"
        ),
    },
    "outlaw": {
        "display_name": "Outlaw",
        "level": 35,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 2,
        "xp_multiplier": 0.025,
        "stats": {
            "hitpoints": 200,
            "attack": 35,
            "strength": 30,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": -21,
            "defence_stab": 0,
            "defence_slash": 0,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 0,
            "melee_strength": 0,
        },
        "drops": OUTLAW_DROPS,
        "source": (
            f"{OUTLAW_SOURCE_PATH}: ids Npcs.OUTLAW through Npcs.OUTLAW_5851; "
            "xpMultiplier 0.025; aggro radius 4; "
            "main table declares total(128), active source slots sum to 127"
        ),
    },
    "chaos_dwarf": {
        "display_name": "Chaos dwarf",
        "level": 48,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "slayer_xp": 61.0,
        "stats": {
            "hitpoints": 610,
            "attack": 38,
            "strength": 42,
            "defence": 28,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 13,
            "attack_slash": 0,
            "attack_crush": 9,
            "defence_stab": 40,
            "defence_slash": 34,
            "defence_crush": 25,
            "defence_magic": 10,
            "defence_ranged": 35,
            "melee_strength": 0,
        },
        "drops": CHAOS_DWARF_DROPS,
        "source": (
            f"{CHAOS_DWARF_SOURCE_PATH}: id Npcs.CHAOS_DWARF; "
            "SlayerAssignment.DWARF level 1 xp 61.0; aggro radius 4"
        ),
    },
    "haakon_the_champion": {
        "display_name": "Haakon the Champion",
        "level": 29,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 6,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 350,
            "attack": 22,
            "strength": 22,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 8,
            "attack_slash": 0,
            "attack_crush": 9,
            "defence_stab": 12,
            "defence_slash": 14,
            "defence_crush": 10,
            "defence_magic": -1,
            "defence_ranged": 11,
            "melee_strength": 0,
        },
        "drops": HAAKON_DROPS,
        "source": f"{HAAKON_SOURCE_PATH}: id Npcs.HAAKON_THE_CHAMPION; no Charms table in source",
    },
    "ham_guard_level_12": {
        "display_name": "H.A.M. guard",
        "level": 12,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 150,
            "attack": 8,
            "strength": 12,
            "defence": 8,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 5,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": HAM_GUARD_DROPS,
        "source": (
            f"{HAM_GUARD_SOURCE_PATH}: id Npcs.HAM_GUARD; "
            "main table declares total(660), active source slots sum to 648"
        ),
    },
    "ham_guard_level_18": {
        "display_name": "H.A.M. guard",
        "level": 18,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 200,
            "attack": 14,
            "strength": 18,
            "defence": 12,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 6,
            "defence_slash": 6,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 6,
            "melee_strength": 0,
        },
        "drops": HAM_GUARD_DROPS,
        "source": (
            f"{HAM_GUARD_SOURCE_PATH}: id Npcs.HAM_GUARD_1711; "
            "main table declares total(660), active source slots sum to 648"
        ),
    },
    "ham_guard_level_22": {
        "display_name": "H.A.M. guard",
        "level": 22,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 25,
        "stats": {
            "hitpoints": 300,
            "attack": 16,
            "strength": 20,
            "defence": 12,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 7,
            "defence_slash": 7,
            "defence_crush": 0,
            "defence_magic": 0,
            "defence_ranged": 7,
            "melee_strength": 0,
        },
        "drops": HAM_GUARD_DROPS,
        "source": (
            f"{HAM_GUARD_SOURCE_PATH}: id Npcs.HAM_GUARD_1712; "
            "main table declares total(660), active source slots sum to 648"
        ),
    },
    "white_knight_level_36": {
        "display_name": "White knight",
        "level": 36,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 27,
            "strength": 29,
            "defence": 21,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_36_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_36_SOURCE_PATH}: id Npcs.WHITE_KNIGHT; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses"
        ),
    },
    "white_knight_level_38": {
        "display_name": "White knight",
        "level": 38,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 30,
            "strength": 29,
            "defence": 25,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_38_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_38_SOURCE_PATH}: id Npcs.WHITE_KNIGHT_3348; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses; "
            "main table declares total(128), active source slots sum to 130"
        ),
    },
    "white_knight_level_39": {
        "display_name": "White knight",
        "level": 39,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 32,
            "strength": 29,
            "defence": 27,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_39_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_39_SOURCE_PATH}: id Npcs.WHITE_KNIGHT_3349; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses; "
            "main table declares total(128), active source slots sum to 127"
        ),
    },
    "white_knight_level_42": {
        "display_name": "White knight",
        "level": 42,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 7,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 520,
            "attack": 32,
            "strength": 29,
            "defence": 27,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 30,
            "attack_slash": 30,
            "attack_crush": 30,
            "defence_stab": 83,
            "defence_slash": 76,
            "defence_crush": 70,
            "defence_magic": -11,
            "defence_ranged": 74,
            "melee_strength": 31,
        },
        "drops": WHITE_KNIGHT_LEVEL_42_DROPS,
        "source": (
            f"{WHITE_KNIGHT_LEVEL_42_SOURCE_PATH}: id Npcs.WHITE_KNIGHT_3350; "
            "source attackBonus/strengthBonus mapped to melee attack/strength bonuses; "
            "main table declares total(128), active source slots sum to 127"
        ),
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
    "barbarian_level_17": {
        "display_name": "Barbarian",
        "level": 17,
        "group": "Humanoids",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 50,
        "stats": {
            "hitpoints": 240,
            "attack": 15,
            "strength": 14,
            "defence": 10,
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
            "definitions/humanoids/barbarian_greataxe_lvl_17.plugin.kts: "
            "ids Npcs.BARBARIAN/Npcs.BARBARIAN_3248; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_spear_lvl_17.plugin.kts: "
            "id Npcs.BARBARIAN_3260; "
            f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/"
            "definitions/humanoids/barbarian_twohand_sword_lvl_17.plugin.kts: "
            "id Npcs.BARBARIAN_3249"
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
        "drops": SCORPION_CHARM_DROPS,
        "source": SCORPION_LEVEL_14_SOURCE_PATH,
    },
    "king_scorpion": {
        "display_name": "King scorpion",
        "level": 32,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 37.0,
        "stats": {
            "hitpoints": 300,
            "attack": 30,
            "strength": 29,
            "defence": 23,
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
        "source": (
            f"{KING_SCORPION_SOURCE_PATH}: Npcs.KING_SCORPION; "
            "SlayerAssignment.SCORPION level 1 xp 37.0; no DropTableFactory registration; aggro radius 4"
        ),
    },
    "pit_scorpion": {
        "display_name": "Pit scorpion",
        "level": 28,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 25,
        "slayer_xp": 32.0,
        "stats": {
            "hitpoints": 320,
            "attack": 20,
            "strength": 25,
            "defence": 28,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {
            "attack_stab": 0,
            "attack_slash": 0,
            "attack_crush": 0,
            "defence_stab": 5,
            "defence_slash": 13,
            "defence_crush": 13,
            "defence_magic": 0,
            "defence_ranged": 5,
            "melee_strength": 0,
        },
        "drops": {"guaranteed": (), "tables": ()},
        "source": (
            f"{PIT_SCORPION_SOURCE_PATH}: Npcs.PIT_SCORPION; "
            "SlayerAssignment.SCORPION level 1 xp 32.0; no DropTableFactory registration; aggro radius 4"
        ),
    },
    "scorpion_level_59": {
        "display_name": "Scorpion",
        "level": 59,
        "group": "Scorpions",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 22,
        "slayer_xp": 55.0,
        "stats": {
            "hitpoints": 550,
            "attack": 50,
            "strength": 52,
            "defence": 50,
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
            "defence_ranged": 55,
            "melee_strength": 0,
        },
        "drops": SCORPION_CHARM_DROPS,
        "source": (
            f"{SCORPION_LEVEL_59_SOURCE_PATH}: ids Npcs.SCORPION_4402/Npcs.SCORPION_4403; "
            "SlayerAssignment.SCORPION level 1 xp 55.0; aggro radius 4"
        ),
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
    "poison_spider_level_64": {
        "display_name": "Poison spider",
        "level": 64,
        "group": "Spiders",
        "attack_style": "melee",
        "attack_speed": 4,
        "respawn_delay": 30,
        "poison_damage": 6,
        "slayer_xp": 64.0,
        "stats": {
            "hitpoints": 640,
            "attack": 50,
            "strength": 58,
            "defence": 52,
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
        "source": (
            f"{POISON_SPIDER_LEVEL_64_SOURCE_PATH}: Npcs.POISON_SPIDER poisonDamage=6; "
            "attackStyle STAB; no DropTableFactory registration; aggro radius 4"
        ),
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
    "Avantoe seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.AVANTOE_SEED"},
    "Banana": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BANANA"},
    "Bat bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BAT_BONES"},
    "Bear fur": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEAR_FUR"},
    "Belladonna seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BELLADONNA_SEED"},
    "Big bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BIG_BONES"},
    "Black kiteshield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_KITESHIELD"},
    "Black sq shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLACK_SQ_SHIELD"},
    "Bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BONES"},
    "Brass necklace": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRASS_NECKLACE"},
    "Bronze javelin": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_JAVELIN"},
    "Bronze spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BRONZE_SPEAR"},
    "Buttons": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BUTTONS"},
    "Cactus seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CACTUS_SEED"},
    "Cape": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CAPE_1019"},
    "Cadantine seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CADANTINE_SEED"},
    "Champion's scroll": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHAMPIONS_SCROLL_6800"},
    "Chef's hat": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CHEFS_HAT"},
    "Cabbage seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CABBAGE_SEED"},
    "Clue scroll (easy)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CLUE_SCROLL_EASY"},
    "Clue scroll (medium)": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CLUE_SCROLL_MEDIUM"},
    "Coins": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COINS_995"},
    "Cowhide": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COWHIDE"},
    "Curved bone": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CURVED_BONE"},
    "Damaged armour": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DAMAGED_ARMOUR"},
    "Beer": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BEER"},
    "Dragon spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DRAGON_SPEAR"},
    "Dwarf weed seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.DWARF_WEED_SEED"},
    "Eye patch": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.EYE_PATCH"},
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
    "Half an apple pie": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HALF_AN_APPLE_PIE"},
    "H.A.M. boots": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_BOOTS"},
    "H.A.M. cloak": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_CLOAK"},
    "H.A.M. gloves": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_GLOVES"},
    "H.A.M. hood": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_HOOD"},
    "H.A.M. logo": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_LOGO"},
    "H.A.M. robe": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_ROBE"},
    "H.A.M. shirt": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HAM_SHIRT"},
    "Harralander seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.HARRALANDER_SEED"},
    "Irit seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.IRIT_SEED"},
    "Jangerberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JANGERBERRY_SEED"},
    "Jug of wine": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.JUG_OF_WINE"},
    "Knife": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KNIFE"},
    "Kwuarm seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.KWUARM_SEED"},
    "Lantadyme seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LANTADYME_SEED"},
    "Limpwurt root": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LIMPWURT_ROOT"},
    "Limpwurt seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LIMPWURT_SEED"},
    "Loop half of a key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LOOP_HALF_OF_A_KEY"},
    "Long bone": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.LONG_BONE"},
    "Magic staff": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MAGIC_STAFF"},
    "Marrentill seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MARRENTILL_SEED"},
    "Mithril spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MITHRIL_SPEAR"},
    "Muddy key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.MUDDY_KEY"},
    "Needle": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.NEEDLE"},
    "Onion seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ONION_SEED"},
    "Poison ivy seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.POISON_IVY_SEED"},
    "Potato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.POTATO_SEED"},
    "Rake": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAKE"},
    "Ranarr seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RANARR_SEED"},
    "Raw rat meat": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAW_RAT_MEAT"},
    "Rusty sword": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUSTY_SWORD"},
    "Rune javelin": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUNE_JAVELIN"},
    "Rune spear": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RUNE_SPEAR"},
    "Secateurs": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SECATEURS"},
    "Seed dibber": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SEED_DIBBER"},
    "Shield left half": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SHIELD_LEFT_HALF"},
    "Sling": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SLING"},
    "Snapdragon seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SNAPDRAGON_SEED"},
    "Spinach roll": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SPINACH_ROLL"},
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
    "Tarromin seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TARROMIN_SEED"},
    "Thread": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.THREAD"},
    "Toadflax seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOADFLAX_SEED"},
    "Tooth half of a key": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOOTH_HALF_OF_A_KEY"},
    "Tomato seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TOMATO_SEED"},
    "Torstol seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TORSTOL_SEED"},
    "Unicorn horn": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.UNICORN_HORN"},
    "Vial": {"category": "crafted", "source": f"{ITEM_ID_SOURCE_PATH}: Items.VIAL"},
    "Vial of water": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.VIAL_OF_WATER"},
    "Watering can (8)": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERING_CAN_8"},
    "Watermelon seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WATERMELON_SEED"},
    "Whiteberry seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WHITEBERRY_SEED"},
    "Wildblood seed": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WILDBLOOD_SEED"},
    "Wooden shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOODEN_SHIELD"},
    "Wolf bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOLF_BONES"},
    "Zamorak robe bottom": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ZAMORAK_ROBE"},
    "Zamorak robe top": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.ZAMORAK_ROBE_1035"},
    "Tinderbox": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TINDERBOX_590"},
    "Gold charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOLD_CHARM"},
    "Green charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GREEN_CHARM"},
    "Crimson charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CRIMSON_CHARM"},
    "Blue charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLUE_CHARM"},
}


COMBAT_TARGET_GROUP_ORDER: Tuple[str, ...] = ("Lumbridge", "Spiders", "Scorpions", "Goblins", "Humanoids", "Coastal")
