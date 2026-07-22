"""Period Shades of Mort'ton values and disclosed review abstractions."""

from __future__ import annotations

from typing import Any


SHADES_OF_MORTTON_ACTIVITY_ID = "shades_of_mortton"
SHADES_OF_MORTTON_COMBAT_TARGET_ID = "shades_of_mortton_loar_shade"
SHADES_OF_MORTTON_SOURCE = (
    "RuneScape Wiki Shades of Mort'ton (minigame) oldid=6449451 "
    "(2012-10-21T17:37:46Z); rev-742 item definitions"
)

SHADES_SANCTITY_MAX_TENTHS = 1_000
SHADES_REPAIR_MAX = 100
SHADES_REPAIR_UNLOCK = 99
SHADES_RESOURCE_PACK = {
    "Timber beam": 1,
    "Limestone brick": 1,
    "Swamp paste": 5,
}
SHADES_RESOURCE_PACK_POINTS = 5
SHADES_REPAIR_PROGRESS = 4
SHADES_REPAIR_SANCTITY_TENTHS = 50
SHADES_SHADE_KILL_SANCTITY_TENTHS = 20
SHADES_OIL_SANCTITY_PER_DOSE_TENTHS = 9
SHADES_SERUM_SANCTITY_TENTHS = 200
SHADES_SANCTITY_DECAY_REVIEWS = 10

# The period page says the Flamtaer hammer is much faster and that altar
# lighting can fail. Darkan supplies these hidden rolls; they remain explicitly
# provisional until a second implementation or period rate is recovered.
SHADES_REPAIR_CHANCE_BY_HAMMER = {"Hammer": 1.0 / 6.0, "Flamtaer hammer": 0.5}
SHADES_ALTAR_LIGHT_CHANCE = 0.5

# Crowd pressure is an owner-approved AnkiScape abstraction. It moves only the
# communal repair meter and can never grant personal resources, sanctity, XP,
# keys, or loot.
SHADES_CROWD_REPAIR = {"quiet": 0, "normal": 1, "busy": 2}
SHADES_SHADE_DAMAGE = 1

SHADES_DUTIES = (
    ("repair", "Repair the Temple of Mort'ton"),
    ("combat", "Fight Loar shades"),
    ("cremate", "Cremate Loar remains"),
)
SHADES_DUTY_IDS = tuple(duty_id for duty_id, _label in SHADES_DUTIES)

SHADES_PYRE_LOGS = {
    "Pyre logs": {
        "base_log": "Logs",
        "level": 5,
        "oil_doses": 2,
        "creation_xp": 12.0,
        "cremation_xp": 50.0,
    },
    "Oak pyre logs": {
        "base_log": "Oak logs",
        "level": 20,
        "oil_doses": 2,
        "creation_xp": 12.0,
        "cremation_xp": 70.0,
    },
    "Willow pyre logs": {
        "base_log": "Willow logs",
        "level": 35,
        "oil_doses": 3,
        "creation_xp": 12.0,
        "cremation_xp": 100.0,
    },
    "Teak pyre logs": {
        "base_log": "Teak logs",
        "level": 40,
        "oil_doses": 3,
        "creation_xp": 14.0,
        "cremation_xp": 120.0,
    },
    "Arctic pyre logs": {
        "base_log": "Arctic pine logs",
        "level": 47,
        "oil_doses": 3,
        "creation_xp": 14.0,
        "cremation_xp": 158.0,
    },
    "Maple pyre logs": {
        "base_log": "Maple logs",
        "level": 50,
        "oil_doses": 3,
        "creation_xp": 14.0,
        "cremation_xp": 175.0,
    },
    "Mahogany pyre logs": {
        "base_log": "Mahogany logs",
        "level": 55,
        "oil_doses": 3,
        "creation_xp": 14.0,
        "cremation_xp": 210.0,
    },
    "Eucalyptus pyre logs": {
        "base_log": "Eucalyptus logs",
        "level": 63,
        "oil_doses": 4,
        "creation_xp": 16.0,
        "cremation_xp": 246.0,
    },
    "Yew pyre logs": {
        "base_log": "Yew logs",
        "level": 65,
        "oil_doses": 4,
        "creation_xp": 16.0,
        "cremation_xp": 255.0,
    },
    "Magic pyre logs": {
        "base_log": "Magic logs",
        "level": 80,
        "oil_doses": 4,
        "creation_xp": 16.0,
        "cremation_xp": 404.5,
    },
}

SHADES_LOAR_PRAYER_XP = {
    "Pyre logs": 25.0,
    "Oak pyre logs": 33.0,
    "Willow pyre logs": 33.5,
    "Teak pyre logs": 33.7,
    "Arctic pyre logs": 33.9,
    "Maple pyre logs": 34.0,
    "Mahogany pyre logs": 34.3,
    "Eucalyptus pyre logs": 34.4,
    "Yew pyre logs": 34.5,
    "Magic pyre logs": 35.0,
}

SHADES_BRONZE_KEYS = (
    "Bronze key red",
    "Bronze key brown",
    "Bronze key crimson",
)


def shades_of_mortton_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SHADES_OF_MORTTON_ACTIVITY_ID: {
            "display_name": "Shades of Mort'ton",
            "requirements": {"quest": "shades_of_mortton"},
            "skill_requirements": {},
            "outputs": (
                "Sacred oil (4)",
                "Serum 208 (4)",
                "Loar remains",
                *SHADES_BRONZE_KEYS,
                "Fine cloth",
            ),
            "batch_size": 1,
            "group": "activities",
            "source": SHADES_OF_MORTTON_SOURCE,
        }
    }


def shades_of_mortton_loar_enemy_pure() -> dict[str, Any]:
    return {
        "display_name": "Loar Shade",
        "level": 40,
        "group": "Shades of Mort'ton",
        "stats": {
            "attack": 45,
            "strength": 30,
            "defence": 26,
            "magic": 42,
            "ranged": 0,
            "hitpoints": 380,
        },
        "bonuses": {},
        "attack_style": "melee",
        "attack_speed": 4,
        "max_hit": 40,
        "xp_multiplier": 1.0,
        "drops": {"guaranteed": (("Loar remains", 1),), "tables": ()},
        "source": SHADES_OF_MORTTON_SOURCE,
    }
