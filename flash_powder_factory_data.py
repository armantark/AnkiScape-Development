"""Period Flash Powder Factory values and disclosed review abstractions."""

from __future__ import annotations

from typing import Any, Dict


FLASH_POWDER_FACTORY_ACTIVITY_ID = "flash_powder_factory"
FLASH_POWDER_FACTORY_SOURCE = (
    "RuneScape Wiki Flash Powder Factory oldid=6559970 "
    "(2012-11-15T19:17:32Z); Factory outfit oldid=6547053 "
    "(2012-11-10T19:21:03Z); Rogue kit oldid=6293011 "
    "(2012-09-25T01:04:53Z); Fallen rubble oldid=5130308"
)

FLASH_POWDER_FACTORY_BASE_SLOTS = 8
FLASH_POWDER_FACTORY_EXTENDED_SLOTS = 9
FLASH_POWDER_FACTORY_BASE_CATALYST = 6
FLASH_POWDER_FACTORY_TROUSERS_CATALYST = 9
FLASH_POWDER_FACTORY_BASE_APPARATUS = 3
FLASH_POWDER_FACTORY_MAX_APPARATUS = 6
FLASH_POWDER_FACTORY_MAX_BRIANPOINTS = 155
FLASH_POWDER_FACTORY_LONG_STAY_BONUS = 20

FLASH_POWDER_FACTORY_STRATEGIES = {
    "max_points": "Max Brianpoints",
    "rogue_equipment": "Rogue equipment",
    "balanced": "Balanced",
}
FLASH_POWDER_FACTORY_APPARATUS_POLICIES = {
    "ignore": "Ignore contests",
    "opportunistic": "Opportunistic",
}

FLASH_POWDER_FACTORY_REWARD_COSTS = {
    "Factory mask": 2_250,
    "Factory top": 3_500,
    "Factory trousers": 2_750,
    "Factory gloves": 1_750,
    "Factory boots": 1_750,
    "Rogue kit": 35,
}
FLASH_POWDER_FACTORY_XP_PER_POINT = {
    "agility": 95.0,
    "thieving": 120.0,
}
FLASH_POWDER_FACTORY_XP_LOTS = (10, 100, 1_000, 10_000)
FLASH_POWDER_FACTORY_OUTFIT = frozenset(
    {
        "Factory mask",
        "Factory top",
        "Factory trousers",
        "Factory gloves",
        "Factory boots",
    }
)
FLASH_POWDER_FACTORY_ROGUE_OUTFIT = (
    "Rogue mask",
    "Rogue top",
    "Rogue trousers",
    "Rogue gloves",
    "Rogue boots",
)
ROGUE_KIT_OUTPUTS = ("Chisel", "Rope", "Tinderbox", "Spade")

# The period record names every outcome but does not expose its server weights.
# These bounded, disclosed weights keep Rogue armour rare and implement the
# Factory mask's exact 15-point reduction to the nothing outcome.
FLASH_POWDER_FACTORY_RUBBLE_WEIGHTS = (
    ("nothing", 50),
    ("catalyst", 20),
    ("apparatus", 15),
    ("average_powder", 10),
    ("very_nice_powder", 4),
    ("rogue_piece", 1),
)
FLASH_POWDER_FACTORY_MASK_RUBBLE_WEIGHTS = (
    ("nothing", 35),
    ("catalyst", 25),
    ("apparatus", 19),
    ("average_powder", 13),
    ("very_nice_powder", 6),
    ("rogue_piece", 2),
)


def flash_powder_factory_activity_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        FLASH_POWDER_FACTORY_ACTIVITY_ID: {
            "display_name": "Flash Powder Factory",
            "requirements": {},
            "skill_requirements": {
                "agility": 75,
                "thieving": 75,
                "herblore": 50,
            },
            "requires_unskulled": True,
            "batch_size": 1,
            "group": "minigames",
            "source": FLASH_POWDER_FACTORY_SOURCE,
        }
    }


def flash_powder_factory_extra_items_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        "Rogue kit": {
            "category": "utility",
            "tradeable": False,
            "stackable": True,
            "source": FLASH_POWDER_FACTORY_SOURCE,
            "status": "implemented",
        }
    }
