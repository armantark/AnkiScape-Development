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
ITEM_ID_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt"
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
        "compatible_ammo": ("Bronze arrows",),
        "source": f"{RANGED_BOW_SOURCE_PATH}: SHORTBOW accepts BRONZE_ARROWS + IRON_ARROWS",
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
}


COMBAT_EXTRA_ITEM_DATA: Dict[str, dict] = {
    "Bones": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BONES"},
    "Cape": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CAPE_1019"},
    "Cowhide": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COWHIDE"},
    "Raw rat meat": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAW_RAT_MEAT"},
    "Sling": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SLING"},
    "Staff of air": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_AIR"},
    "Staff of water": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_WATER"},
    "Staff of earth": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_EARTH"},
    "Staff of fire": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_FIRE"},
    "Wooden shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOODEN_SHIELD"},
    "Tinderbox": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TINDERBOX_590"},
    "Gold charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOLD_CHARM"},
    "Green charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GREEN_CHARM"},
    "Crimson charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CRIMSON_CHARM"},
    "Blue charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLUE_CHARM"},
}


COMBAT_TARGET_GROUP_ORDER: Tuple[str, ...] = ("Lumbridge", "Spiders", "Humanoids", "Coastal")
