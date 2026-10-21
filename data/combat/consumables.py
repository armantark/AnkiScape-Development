from __future__ import annotations

from typing import Dict

from .mechanics import (
    FOOD_SOURCE_PATH,
    POTION_SOURCE_PATH,
    POTION_TYPE_SOURCE_PATH,
)

# Stat-affecting consumables (edible, but excluded from COMBAT_FOOD_DATA so
# combat auto-eat never picks them by default — owner decision 2026-07-07:
# eligible only if the player explicitly opts in). Effects are applied by
# logic_pure.apply_consumable_pure; the tables below are source-audited in
# memory-bank/source-audits/kebab-beer-consumables-2026-07-07.md.
KEBAB_SOURCE = f"{FOOD_SOURCE_PATH}: calculateKebabEffect (wiki oldid 4868155)"
BEER_SOURCE = f"{POTION_TYPE_SOURCE_PATH}: BEER beerHealth/beerStrength/beerDrain"

CONSUMABLE_DATA: Dict[str, dict] = {
    # Kebab: roll nextDouble(100) over the source effect table. Heal amounts
    # are lifepoints (AnkiScape level*10 model); boosts/drains are levels.
    "Kebab": {
        "kind": "kebab_random",
        "verb": "Eat",
        "source": KEBAB_SOURCE,
        "effect_table": (
            {"upto": 8.71, "message": "That kebab didn't seem to do a lot."},
            {"upto": 69.95, "heal_max_pct": 0.10, "message": "It restores some health."},
            {"upto": 91.07, "heal_range": (100, 200), "message": "That was a good kebab. You feel a lot better."},
            {"upto": 94.72, "heal": 300, "boost_levels": {"attack": (2, 3), "strength": (2, 3), "defense": (2, 3)},
             "message": "Wow, that was an amazing kebab! You feel really invigorated."},
            {"upto": 100.0, "drain_random_skill": (2, 4), "message": "That kebab tasted a bit dodgy."},
        ),
    },
    # Beer: engine potion. +1 Constitution tick (10 LP), +4% current Strength,
    # -7% current Attack (floored).
    "Beer": {
        "kind": "beer",
        "source": BEER_SOURCE,
        "heal_constitution_ticks": 1,
        "strength_boost_pct": 0.04,
        "attack_drain_pct": 0.07,
        "message": "You drink the beer. You feel slightly reinvigorated... and slightly dizzy.",
    },
    "White tree fruit": {
        "kind": "run_energy_food",
        "verb": "Eat",
        "heal": 30,
        "run_energy_pct": 17,
        "message": "You eat the White tree fruit. It restores 30 LP and 17% run energy.",
        "source": "White tree fruit oldid 5838367, 2012-06-26T04:41:55Z",
    },
}

from ..potion_data import potion_consumables_as_dict
CONSUMABLE_DATA.update(potion_consumables_as_dict())
from ..sorceress_garden_data import sorceress_garden_consumables_as_dict
CONSUMABLE_DATA.update(sorceress_garden_consumables_as_dict())

# Agility boosts are deliberately action-budgeted. RuneScape's minute-based
# decay cannot use the wall clock in AnkiScape, so one dose holds for ten
# answered Agility actions and then expires atomically.
for _dose in range(1, 5):
    CONSUMABLE_DATA[f"Agility potion ({_dose})"] = {
        "kind": "agility_boost",
        "boost": 3,
        "action_budget": 10,
        "leaves": f"Agility potion ({_dose - 1})" if _dose > 1 else "Vial",
        "message": "You drink the agility potion. Your next Agility actions use a +3 boost.",
        "source": "Agility potion oldid 6288977; action budget is an AnkiScape abstraction",
    }
for _dose in range(1, 3):
    CONSUMABLE_DATA[f"Agility mix ({_dose})"] = {
        "kind": "agility_boost",
        "boost": 3,
        "action_budget": 10,
        "heal": 60,
        "leaves": f"Agility mix ({_dose - 1})" if _dose > 1 else "Vial",
        "message": "You drink the agility mix. It restores 60 LP and grants a +3 Agility boost.",
        "source": "Agility mix oldid 6288968; action budget is an AnkiScape abstraction",
    }
CONSUMABLE_DATA["Summer pie"] = {
    "kind": "agility_boost",
    "verb": "Eat",
    "boost": 5,
    "action_budget": 10,
    "heal": 110,
    "run_energy_pct": 20,
    "leaves": "Half a summer pie",
    "message": "You eat half the summer pie. It restores 110 LP and grants a +5 Agility boost.",
    "source": "Summer pie oldid 6358590; action budget is an AnkiScape abstraction",
}
CONSUMABLE_DATA["Half a summer pie"] = {
    "kind": "agility_boost",
    "verb": "Eat",
    "boost": 5,
    "action_budget": 10,
    "heal": 110,
    "run_energy_pct": 20,
    "leaves": "Pie dish",
    "message": "You finish the summer pie. It restores 110 LP and grants a +5 Agility boost.",
    "source": "Summer pie oldid 6358590; action budget is an AnkiScape abstraction",
}
for _dose in range(1, 5):
    CONSUMABLE_DATA[f"Juju farming potion ({_dose})"] = {
        "kind": "farming_juju",
        "farm_minutes": 5,
        "leaves": f"Juju farming potion ({_dose - 1})" if _dose > 1 else "Vial",
        "message": "You drink the juju farming potion. Its harvest effect lasts for 5 farm minutes.",
        "source": "Juju farming potion oldid 6439645; farming-skill contract section 23",
    }

# Skills a kebab's dodgy roll can drain (source: any non-Constitution skill id).
KEBAB_DRAINABLE_SKILLS = (
    "attack", "strength", "defense", "ranged", "magic", "prayer", "mining",
    "smithing", "fishing", "cooking", "woodcutting", "firemaking", "crafting",
    "fletching", "runecrafting", "hunter",
)

COMBAT_FOOD_DATA: Dict[str, dict] = {
    "Crayfish": {"heal_lifepoints": 20, "source": FOOD_SOURCE_PATH},
    "Shrimps": {"heal_lifepoints": 30, "source": FOOD_SOURCE_PATH},
    "Sardine": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Cooked chicken": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Cooked meat": {"heal_lifepoints": 40, "source": FOOD_SOURCE_PATH},
    "Herring": {"heal_lifepoints": 50, "source": FOOD_SOURCE_PATH},
    "Mackerel": {"heal_lifepoints": 60, "source": FOOD_SOURCE_PATH},
    "Half an apple pie": {"heal_lifepoints": 70, "source": f"{FOOD_SOURCE_PATH}: HALF_AN_APPLE_PIE"},
    "Trout": {"heal_lifepoints": 70, "source": FOOD_SOURCE_PATH},
    "Cod": {"heal_lifepoints": 70, "source": FOOD_SOURCE_PATH},
    "Pike": {"heal_lifepoints": 80, "source": FOOD_SOURCE_PATH},
    "Salmon": {"heal_lifepoints": 90, "source": FOOD_SOURCE_PATH},
    "Tuna": {"heal_lifepoints": 100, "source": FOOD_SOURCE_PATH},
    "Lobster": {"heal_lifepoints": 120, "source": FOOD_SOURCE_PATH},
    "Bass": {"heal_lifepoints": 130, "source": FOOD_SOURCE_PATH},
    "Chilli potato": {"heal_lifepoints": 140, "source": f"{FOOD_SOURCE_PATH}: CHILLI_POTATO"},
    "Swordfish": {"heal_lifepoints": 140, "source": FOOD_SOURCE_PATH},
    "Monkfish": {"heal_lifepoints": 160, "source": FOOD_SOURCE_PATH},
    "Shark": {"heal_lifepoints": 200, "source": FOOD_SOURCE_PATH},
    "Tiger shark": {
        "heal_lifepoints": 250,
        "max_overheal_lifepoints": 100,
        "source": "RuneScape Wiki Tiger shark oldid=6448339 (2012-10-21T04:48:57Z)",
    },
}

# Gnome dishes. Heals come from 2011Scape Food.kt, which lists the live 21xx/22xx
# ids, and each one agrees with its dedicated cutoff item page. The seven cocktails
# are deliberately absent: five of them move Strength and Attack, so they belong in
# CONSUMABLE_DATA under the 2026-07-07 rule that keeps stat-affecting edibles out of
# combat auto-eat.
GNOME_FOOD_SOURCE = (
    f"{FOOD_SOURCE_PATH}: gnome food block; "
    "memory-bank/source-audits/gnome-restaurant-harvest-2026-07-28.md"
)
COMBAT_FOOD_DATA.update({
    item_name: {"heal_lifepoints": heal, "source": GNOME_FOOD_SOURCE}
    for item_name, heal in (
        ("Toad crunchies", 120),
        ("Spicy crunchies", 70),
        ("Worm crunchies", 80),
        ("Chocchip crunchies", 70),
        ("Fruit batta", 110),
        ("Toad batta", 110),
        ("Worm batta", 110),
        ("Vegetable batta", 110),
        ("Cheese+tom batta", 110),
        ("Worm hole", 120),
        ("Veg ball", 120),
        ("Tangled toads' legs", 150),
        ("Chocolate bomb", 150),
    )
})

# Gnome cocktails. Every value is from the drink's own cutoff item page; the two
# non-alcoholic mixes carry no stat effect. Blurberry special's healing comes from
# the Cooking table because its item page only says "a few life points".
_GNOME_COCKTAILS = (
    ("Fruit blast", 80, {}, {}, "Fruit blast oldid 6309046 (2012-09-28T01:45:11Z)"),
    ("Pineapple punch", 90, {}, {}, "Pineapple punch oldid 6071249 (2012-08-10T09:35:30Z)"),
    ("Wizard blizzard", 50, {"strength": 6}, {"attack": 4}, "Wizard blizzard oldid 6071262 (2012-08-10T09:36:55Z)"),
    ("Short green guy", 50, {"strength": 4}, {"attack": 3}, "Short green guy oldid 6248716 (2012-09-16T00:45:18Z)"),
    ("Drunk dragon", 50, {"strength": 7}, {"attack": 4}, "Drunk dragon oldid 6071325 (2012-08-10T09:44:02Z)"),
    ("Choc saturday", 50, {"strength": 7}, {"attack": 4}, "Choc saturday oldid 6071447 (2012-08-10T09:56:50Z)"),
    ("Blurberry special", 70, {"strength": 7}, {"attack": 5}, "Blurberry special oldid 6357080 (2012-10-06T16:18:29Z); healing from Cooking oldid 6548144"),
)
for _name, _heal, _boosts, _drains, _source in _GNOME_COCKTAILS:
    _effect = (
        f" It restores {_heal} LP"
        + (f", raises Strength by {_boosts['strength']}" if _boosts else "")
        + (f" and lowers Attack by {_drains['attack']}" if _drains else "")
        + "."
    )
    CONSUMABLE_DATA[_name] = {
        "kind": "gnome_cocktail",
        "verb": "Drink",
        "heal": _heal,
        "boost_levels": _boosts,
        "drain_levels": _drains,
        "leaves": "Cocktail glass",
        "message": f"You drink the {_name.lower()}.{_effect}",
        "source": _source,
    }


COMBAT_ANTIPOISON_POTION_DATA: Dict[str, dict] = {
    "Antipoison (4)": {
        "replacement": "Antipoison (3)",
        "immunity_ticks": 150,  # PLACEHOLDER(combat.antipoison_immunity_ticks): resolve 150 versus 300 ticks and obtain independent period corroboration
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON4; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON; immunity: Antipoison oldid 5606640 line 22, 90s = 150 ticks; conflicting Herblore oldid 6569702 line 71, 180s = 300 ticks; provisional",
    },
    "Antipoison (3)": {
        "replacement": "Antipoison (2)",
        "immunity_ticks": 150,  # PLACEHOLDER(combat.antipoison_immunity_ticks): resolve 150 versus 300 ticks and obtain independent period corroboration
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON3; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON; immunity: Antipoison oldid 5606640 line 22, 90s = 150 ticks; conflicting Herblore oldid 6569702 line 71, 180s = 300 ticks; provisional",
    },
    "Antipoison (2)": {
        "replacement": "Antipoison (1)",
        "immunity_ticks": 150,  # PLACEHOLDER(combat.antipoison_immunity_ticks): resolve 150 versus 300 ticks and obtain independent period corroboration
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON2; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON; immunity: Antipoison oldid 5606640 line 22, 90s = 150 ticks; conflicting Herblore oldid 6569702 line 71, 180s = 300 ticks; provisional",
    },
    "Antipoison (1)": {
        "replacement": "Vial",
        "immunity_ticks": 150,  # PLACEHOLDER(combat.antipoison_immunity_ticks): resolve 150 versus 300 ticks and obtain independent period corroboration
        "source": f"{POTION_SOURCE_PATH}: ANTIPOISON1; {POTION_TYPE_SOURCE_PATH}: ANTIPOISON; immunity: Antipoison oldid 5606640 line 22, 90s = 150 ticks; conflicting Herblore oldid 6569702 line 71, 180s = 300 ticks; provisional",
    },
    "Super antipoison (4)": {
        "replacement": "Super antipoison (3)",
        "immunity_ticks": 600,  # PLACEHOLDER(combat.super_antipoison_immunity_ticks): obtain independent period corroboration for 600 ticks
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON4; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON; immunity: Super antipoison oldid 5819437 line 22, 360s = 600 ticks; provisional pending independent period corroboration",
    },
    "Super antipoison (3)": {
        "replacement": "Super antipoison (2)",
        "immunity_ticks": 600,  # PLACEHOLDER(combat.super_antipoison_immunity_ticks): obtain independent period corroboration for 600 ticks
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON3; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON; immunity: Super antipoison oldid 5819437 line 22, 360s = 600 ticks; provisional pending independent period corroboration",
    },
    "Super antipoison (2)": {
        "replacement": "Super antipoison (1)",
        "immunity_ticks": 600,  # PLACEHOLDER(combat.super_antipoison_immunity_ticks): obtain independent period corroboration for 600 ticks
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON2; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON; immunity: Super antipoison oldid 5819437 line 22, 360s = 600 ticks; provisional pending independent period corroboration",
    },
    "Super antipoison (1)": {
        "replacement": "Vial",
        "immunity_ticks": 600,  # PLACEHOLDER(combat.super_antipoison_immunity_ticks): obtain independent period corroboration for 600 ticks
        "source": f"{POTION_SOURCE_PATH}: SUPER_ANTIPOISON1; {POTION_TYPE_SOURCE_PATH}: SUPER_ANTIPOISON; immunity: Super antipoison oldid 5819437 line 22, 360s = 600 ticks; provisional pending independent period corroboration",
    },
}
