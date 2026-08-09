"""Period Shades of Mort'ton values and disclosed review abstractions."""

from __future__ import annotations

from typing import Any


SHADES_OF_MORTTON_ACTIVITY_ID = "shades_of_mortton"
SHADES_OF_MORTTON_COMBAT_TARGET_ID = "shades_of_mortton_loar_shade"
SHADES_OF_MORTTON_SOURCE = (
    "RuneScape Wiki Shades of Mort'ton (minigame) oldid=6449451 "
    "(2012-10-21T17:37:46Z); rev-742 item definitions"
)
SHADES_BRONZE_CHEST_SOURCE = (
    "RuneScape Wiki Shades of Mort'ton (minigame) oldid=6449451; "
    "Darkan shade_bronze_chest.json at 4d72f80f3e7ad56a712b4e38653f01cedaeeb289"
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
SHADES_BRONZE_KEY_ROLL_MODIFIERS = {
    key_name: 1.0 - (index * 0.05)
    for index, key_name in enumerate(SHADES_BRONZE_KEYS)
}

# The period page fixes the bronze chest's reward families but not its hidden
# selection probabilities. Darkan's four 128-slot groups therefore remain a
# provisional reconstruction; their complete item identities and quantities
# replace the former one-item-per-group breadth sample.
SHADES_BRONZE_CHEST_REWARD_GROUPS = (
    {
        "slots": 55,
        "rewards": (
            # Rev 742 calls item 1141 "Steel helm"; AnkiScape's owning
            # Smithing row uses its established storage name, Steel med helm.
            ("Steel med helm", 1, 1, 1141),
            ("Magic staff", 1, 1, 1389),
            ("Steel spear", 1, 1, 1241),
            ("Steel mace", 1, 1, 1424),
            ("Steel scimitar", 1, 1, 1325),
            ("Steel sword", 1, 1, 1281),
            ("Steel longsword", 1, 1, 1295),
            ("Black hatchet", 1, 1, 1361),
            ("Black dagger", 1, 1, 1217),
            ("Black spear", 1, 1, 4580),
            ("Black mace", 1, 1, 1426),
            ("Mithril dagger", 1, 1, 1209),
            ("Silver bar", 1, 3, 2355),
            ("Adamant bar", 1, 3, 2362),
            # Darkan awards rev-742 Scroll box (easy) 19005. Treasure Trails'
            # settled flattening stores the usable clue directly and enforces
            # the period one-clue-total rule at award time.
            ("Clue scroll (easy)", 1, 1, 19005),
        ),
    },
    {
        "slots": 59,
        "rewards": (
            ("Steel hatchet", 1, 1, 1353),
            ("Black dagger (p)", 1, 1, 1233),
            ("Mithril dagger (p)", 1, 1, 1225),
            ("Amulet of defence", 1, 1, 1729),
        ),
    },
    {
        "slots": 10,
        "rewards": (
            ("Chaos rune", 12, 28, 562),
            ("Sapphire ring", 1, 1, 1637),
            ("Mithril bar", 1, 3, 2359),
        ),
    },
    {
        "slots": 4,
        "rewards": (("Fine cloth", 1, 1, 3470),),
    },
)
SHADES_BRONZE_CHEST_OUTPUTS = tuple(
    reward[0]
    for group in SHADES_BRONZE_CHEST_REWARD_GROUPS
    for reward in group["rewards"]
)

SHADES_ITEM_IDS = {
    "Olive oil (4)": 3422,
    "Olive oil (3)": 3424,
    "Olive oil (2)": 3426,
    "Olive oil (1)": 3428,
    "Sacred oil (4)": 3430,
    "Sacred oil (3)": 3432,
    "Sacred oil (2)": 3434,
    "Sacred oil (1)": 3436,
    "Pyre logs": 3438,
    "Loar remains": 3396,
    "Bronze key red": 3450,
    "Bronze key brown": 3451,
    "Bronze key crimson": 3452,
    "Black dagger (p)": 1233,
    "Mithril dagger (p)": 1225,
    "Fine cloth": 3470,
}


def shades_of_mortton_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SHADES_OF_MORTTON_ACTIVITY_ID: {
            "display_name": "Shades of Mort'ton",
            "requirements": {},
            "quest_requirements": ("shades_of_mortton",),
            "skill_requirements": {},
            "outputs": (
                "Sacred oil (4)",
                "Serum 208 (4)",
                "Loar remains",
                *SHADES_BRONZE_KEYS,
                *SHADES_BRONZE_CHEST_OUTPUTS,
            ),
            "batch_size": 1,
            "group": "minigames",
            "source": SHADES_OF_MORTTON_SOURCE,
        }
    }


def shades_of_mortton_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    item_names = (
        *(f"Olive oil ({dose})" for dose in range(1, 5)),
        *(f"Sacred oil ({dose})" for dose in range(1, 5)),
        *(f"Serum 207 ({dose})" for dose in range(1, 5)),
        *(f"Serum 208 ({dose})" for dose in range(1, 5)),
        "Loar remains",
        *SHADES_BRONZE_KEYS,
        "Black dagger (p)",
        "Mithril dagger (p)",
        "Fine cloth",
        *SHADES_PYRE_LOGS,
    )
    return {
        item_name: {
            "category": (
                "equipment"
                if item_name in {"Black dagger (p)", "Mithril dagger (p)"}
                else "activity_material"
            ),
            "stackable": False,
            "tradeable": item_name not in SHADES_BRONZE_KEYS,
            "source": (
                SHADES_BRONZE_CHEST_SOURCE
                if item_name in {"Black dagger (p)", "Mithril dagger (p)"}
                else SHADES_OF_MORTTON_SOURCE
            ),
            **(
                {"source_item_id": SHADES_ITEM_IDS[item_name]}
                if item_name in SHADES_ITEM_IDS
                else {}
            ),
        }
        for item_name in item_names
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
