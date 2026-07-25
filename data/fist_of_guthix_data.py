"""Source-backed Fist of Guthix data and bounded AnkiScape abstractions."""

from __future__ import annotations

from typing import Any


FIST_OF_GUTHIX_SOURCE = (
    "RuneScape Wiki Fist of Guthix oldid 6472973; Guide oldid 6538347; "
    "Reward Shop oldid 6392982"
)
FIST_OF_GUTHIX_ACTIVITY_ID = "fist_of_guthix"
FIST_OF_GUTHIX_ROUND_TICKS = 1_000
FIST_OF_GUTHIX_CHARGE_CAP = 5_000
FIST_OF_GUTHIX_COMBAT_TICKS_PER_REVIEW = 6
FIST_OF_GUTHIX_INITIAL_RATING = 1_000
FIST_OF_GUTHIX_INITIAL_SUPPLIES = {
    "Bandages": 5,
    "Catalytic rune": 300,
    "Elemental rune": 1_000,
    "Stone of power": 1,
    "Tele-orb": 1,
}
FIST_OF_GUTHIX_STANCES: dict[str, dict[str, Any]] = {
    "centre": {
        "display_name": "Centre",
        "charges_per_second": 28,
        "exposure_multiplier": 1.0,
        "source_status": "charge sourced; exposure bounded abstraction",
    },
    "hybrid": {
        "display_name": "Hybrid",
        "charges_per_second": 10,
        "exposure_multiplier": 0.72,
        "source_status": "charge sourced; exposure bounded abstraction",
    },
    "evasive": {
        "display_name": "Evasive",
        "charges_per_second": 3,
        "exposure_multiplier": 0.45,
        "source_status": "charge sourced; exposure bounded abstraction",
    },
}
FIST_OF_GUTHIX_REWARDS = {
    "combat_hood": {
        "display_name": "Combat hood",
        "family_id": "combat_hood",
        "buy_tokens": 50,
        "recharge_tokens": 5,
    },
    "bronze_gauntlets": {
        "display_name": "Bronze gauntlets",
        "family_id": "bronze_gauntlets",
        "buy_tokens": 15,
        "recharge_tokens": 3,
    },
}

FIST_OF_GUTHIX_CONDITION_DATA: dict[str, dict[str, Any]] = {
    "combat_hood": {
        "display_name": "Combat hood",
        "max_condition": 90_000,
        "names_by_percent": {
            100: "Combat hood 100",
            80: "Combat hood 80",
            60: "Combat hood 60",
            40: "Combat hood 40",
            20: "Combat hood 20",
            0: "Combat hood 0",
        },
        "degrade_during_combat": True,
        "unsafe_death_percent": None,
        "source": (
            "RuneScape Wiki Combat hood oldid 5827339; Barrows repair "
            "template oldid 6555466"
        ),
    },
    "bronze_gauntlets": {
        "display_name": "Bronze gauntlets",
        "max_condition": 1,
        "names_by_percent": {
            100: "Bronze gauntlets",
            0: "Worn-out bronze gauntlets",
        },
        "degrade_during_combat": False,
        "unsafe_death_percent": 0,
        "source": "RuneScape Wiki Bronze gauntlets oldid 6097062",
    },
}

FIST_OF_GUTHIX_REWARD_ITEMS: dict[str, dict[str, Any]] = {
    "Combat hood 100": {
        "category": "equipment",
        "item_id": 12964,
        "stackable": False,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["combat_hood"]["source"],
    },
    "Combat hood 80": {
        "category": "equipment",
        "item_id": 12965,
        "stackable": False,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["combat_hood"]["source"],
    },
    "Combat hood 60": {
        "category": "equipment",
        "item_id": 12966,
        "stackable": False,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["combat_hood"]["source"],
    },
    "Combat hood 40": {
        "category": "equipment",
        "item_id": 12967,
        "stackable": False,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["combat_hood"]["source"],
    },
    "Combat hood 20": {
        "category": "equipment",
        "item_id": 12968,
        "stackable": False,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["combat_hood"]["source"],
    },
    "Combat hood 0": {
        "category": "equipment",
        "item_id": 12969,
        "stackable": False,
        "tradeable": True,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["combat_hood"]["source"],
    },
    "Bronze gauntlets": {
        "category": "equipment",
        "item_id": 12985,
        "stackable": False,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["bronze_gauntlets"]["source"],
    },
    "Worn-out bronze gauntlets": {
        "category": "equipment",
        "item_id": 12986,
        "stackable": False,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_CONDITION_DATA["bronze_gauntlets"]["source"],
    },
    "Fist of guthix token": {
        "category": "material",
        "item_id": 12852,
        "stackable": True,
        "tradeable": False,
        "source": FIST_OF_GUTHIX_SOURCE,
    },
}


def fist_of_guthix_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {name: dict(spec) for name, spec in FIST_OF_GUTHIX_REWARD_ITEMS.items()}


def fist_of_guthix_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        FIST_OF_GUTHIX_ACTIVITY_ID: {
            "display_name": "Fist of Guthix",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "source": FIST_OF_GUTHIX_SOURCE,
        }
    }
