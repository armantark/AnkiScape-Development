"""Source-backed Combat V1 data.

The enabled rows below are intentionally small: they have complete 2011Scape
combat stats and drop behavior, so runtime combat can fail closed for everything
else while the broader enemy audit continues.
"""

from __future__ import annotations

from typing import Dict, Tuple


DEFAULT_COMBAT_TARGET = "chicken"
DEFAULT_COMBAT_ATTACK_STYLE = "accurate"
COMBAT_BURST_TICKS = 50

COMBAT_SOURCE_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main"
MELEE_FORMULA_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MeleeCombatFormula.kt"
)
MELEE_STRATEGY_SOURCE_PATH = (
    f"{COMBAT_SOURCE_ROOT}/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MeleeCombatStrategy.kt"
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
    "Cowhide": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.COWHIDE"},
    "Raw rat meat": {"category": "food", "source": f"{ITEM_ID_SOURCE_PATH}: Items.RAW_RAT_MEAT"},
    "Sling": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.SLING"},
    "Staff of air": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.STAFF_OF_AIR"},
    "Wooden shield": {"category": "equipment", "source": f"{ITEM_ID_SOURCE_PATH}: Items.WOODEN_SHIELD"},
    "Tinderbox": {"category": "tool", "source": f"{ITEM_ID_SOURCE_PATH}: Items.TINDERBOX_590"},
    "Gold charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GOLD_CHARM"},
    "Green charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.GREEN_CHARM"},
    "Crimson charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.CRIMSON_CHARM"},
    "Blue charm": {"category": "material", "source": f"{ITEM_ID_SOURCE_PATH}: Items.BLUE_CHARM"},
}


COMBAT_TARGET_GROUP_ORDER: Tuple[str, ...] = ("Lumbridge", "Spiders", "Coastal")
