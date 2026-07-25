"""Pinned Pyramid Plunder values and disclosed AnkiScape abstractions."""

from __future__ import annotations

from typing import Any, Dict


PYRAMID_PLUNDER_ACTIVITY_ID = "pyramid_plunder"
PYRAMID_PLUNDER_SOURCE = (
    "RuneScape Wiki Pyramid Plunder oldid=6529238 "
    "(2012-11-03T18:18:22Z)"
)
PYRAMID_PLUNDER_DARKAN_SOURCE = (
    "Darkan ff5b18aaf62d231123f947f3fc13cdcd9e4d2b7d "
    "PyramidPlunder.kt and data/npcs/drops/pyramid_plunder"
)

PYRAMID_PLUNDER_PRIORITIES = {
    "max_xp": "Max XP",
    "balanced": "Balanced",
    "treasure": "Treasure",
}

PYRAMID_PLUNDER_ROOM_DATA = {
    1: {"level": 21, "urns": 13, "urn_xp": 60.0, "chest_xp": 40.0, "base_xp": 20.0, "door_xp": 40.0, "urn_chance": (73, 213), "sarc_chance": (62, 256), "sceptre_denominator": 3500},
    2: {"level": 31, "urns": 13, "urn_xp": 90.0, "chest_xp": 60.0, "base_xp": 30.0, "door_xp": 60.0, "urn_chance": (55, 207), "sarc_chance": (30, 226), "sceptre_denominator": 2250},
    3: {"level": 41, "urns": 12, "urn_xp": 150.0, "chest_xp": 100.0, "base_xp": 50.0, "door_xp": 100.0, "urn_chance": (32, 203), "sarc_chance": (20, 196), "sceptre_denominator": 1250},
    # The period page says 215 XP. Darkan computes 3 * 70 = 210; the pinned
    # period row wins while the conflict stays visible in the source audit.
    4: {"level": 51, "urns": 13, "urn_xp": 215.0, "chest_xp": 140.0, "base_xp": 70.0, "door_xp": 140.0, "urn_chance": (-21, 197), "sarc_chance": (0, 166), "sceptre_denominator": 750},
    5: {"level": 61, "urns": 13, "urn_xp": 300.0, "chest_xp": 200.0, "base_xp": 100.0, "door_xp": 200.0, "urn_chance": (-72, 193), "sarc_chance": (-50, 136), "sceptre_denominator": 650},
    6: {"level": 71, "urns": 13, "urn_xp": 450.0, "chest_xp": 300.0, "base_xp": 150.0, "door_xp": 300.0, "urn_chance": (-150, 187), "sarc_chance": (-90, 106), "sceptre_denominator": 650},
    7: {"level": 81, "urns": 13, "urn_xp": 675.0, "chest_xp": 450.0, "base_xp": 225.0, "door_xp": 450.0, "urn_chance": (-300, 183), "sarc_chance": (-120, 76), "sceptre_denominator": 650},
    8: {"level": 91, "urns": 13, "urn_xp": 825.0, "chest_xp": 550.0, "base_xp": 275.0, "door_xp": 0.0, "urn_chance": (-900, 177), "sarc_chance": (-200, 46), "sceptre_denominator": 650},
}

PYRAMID_PLUNDER_ARTIFACT_TIERS = {
    "pottery": ("Pottery scarab", "Pottery statuette", "Ivory comb"),
    "stone": ("Stone seal", "Stone scarab", "Stone statuette"),
    "gold": ("Gold seal", "Golden scarab", "Golden statuette"),
}
PYRAMID_PLUNDER_ARTIFACT_VALUES = {
    "Ivory comb": 50,
    "Pottery scarab": 75,
    "Pottery statuette": 100,
    "Stone seal": 150,
    "Stone scarab": 175,
    "Stone statuette": 200,
    "Gold seal": 750,
    "Golden scarab": 1_000,
    "Golden statuette": 1_250,
    "Jewelled golden statuette": 7_500,
    "Jewelled diamond statuette": 12_500,
}

# Darkan's room tables are exact local-emulator evidence for ordinary loot.
PYRAMID_PLUNDER_URN_TIER_WEIGHTS = {
    1: (("pottery", 20), ("stone", 30)),
    2: (("gold", 5), ("pottery", 10), ("stone", 35)),
    3: (("gold", 10), ("pottery", 5), ("stone", 35)),
    4: (("gold", 10), ("stone", 40)),
    5: (("gold", 15), ("stone", 35)),
    6: (("gold", 20), ("stone", 30)),
    7: (("gold", 25), ("stone", 25)),
    8: (("gold", 30), ("stone", 20)),
}
PYRAMID_PLUNDER_SARC_TIER_WEIGHTS = {
    1: (("pottery", 5), ("stone", 45)),
    2: (("gold", 15), ("stone", 35)),
    3: (("gold", 20), ("stone", 30)),
    4: (("gold", 30), ("stone", 20)),
    5: (("gold", 34), ("stone", 15), ("jewelled_gold", 1)),
    6: (("gold", 39), ("stone", 10), ("jewelled_gold", 1)),
    7: (("gold", 40), ("stone", 6), ("jewelled_gold", 3), ("jewelled_diamond", 1)),
    8: (("gold", 45), ("jewelled_gold", 3), ("jewelled_diamond", 2)),
}
PYRAMID_PLUNDER_ENGRAVED_TIER_WEIGHTS = (
    ("gold", 39),
    ("jewelled_gold", 7),
    ("jewelled_diamond", 4),
)

PYRAMID_PLUNDER_BLACK_IBIS = (
    "Black ibis body",
    "Black ibis legs",
    "Black ibis mask",
    "Black ibis boots",
)
PYRAMID_PLUNDER_PHARAOH_SCEPTRES = (
    "Pharaoh's sceptre (3)",
    "Pharaoh's sceptre (2)",
    "Pharaoh's sceptre (1)",
)
PYRAMID_PLUNDER_PROTECTED_REWARDS = frozenset(
    (*PYRAMID_PLUNDER_BLACK_IBIS, *PYRAMID_PLUNDER_PHARAOH_SCEPTRES, "Sceptre of the gods")
)

# Hidden trigger rates and NPC damage are not published by the pinned page.
# These bounded values are deliberately named and surfaced in the audit rather
# than being passed off as period facts.
PYRAMID_PLUNDER_FALLBACKS = {
    "snake_poison_chance": 0.25,
    "scarab_trigger_chance": 0.20,
    "scarab_damage": 40,
    "mummy_trigger_chance": 0.20,
    "mummy_damage": 60,
    "chest_loot_profile": "same-room Darkan sarcophagus ordinary table",
}
PYRAMID_PLUNDER_AUTO_FOOD_SLOTS = 8


def pyramid_plunder_activity_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        PYRAMID_PLUNDER_ACTIVITY_ID: {
            "display_name": "Pyramid Plunder",
            "requirements": {},
            "skill_requirements": {"thieving": 21},
            "batch_size": 1,
            "group": "minigames",
            "source": PYRAMID_PLUNDER_SOURCE,
        }
    }


def pyramid_plunder_extra_items_as_dict() -> Dict[str, Dict[str, Any]]:
    item_ids = {
        "Ivory comb": 9026,
        "Golden scarab": 9028,
        "Stone scarab": 9030,
        "Pottery scarab": 9032,
        "Golden statuette": 9034,
        "Pottery statuette": 9036,
        "Stone statuette": 9038,
        "Gold seal": 9040,
        "Stone seal": 9042,
        "Pharaoh's sceptre (3)": 9044,
        "Pharaoh's sceptre (2)": 9046,
        "Pharaoh's sceptre (1)": 9048,
        "Pharaoh's sceptre": 9050,
        "Jewelled golden statuette": 20661,
        "Black ibis body": 21532,
        "Black ibis legs": 21533,
        "Black ibis mask": 21534,
        "Black ibis boots": 21535,
        "Sceptre of the gods": 21536,
        "Jewelled diamond statuette": 21570,
    }
    untradeable = {
        "Jewelled diamond statuette",
        *PYRAMID_PLUNDER_BLACK_IBIS,
        "Sceptre of the gods",
    }
    return {
        name: {
            "category": "equipment" if name in PYRAMID_PLUNDER_PROTECTED_REWARDS else "material",
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": name not in untradeable,
            "source": f"{PYRAMID_PLUNDER_SOURCE}; {PYRAMID_PLUNDER_DARKAN_SOURCE}",
        }
        for name, item_id in item_ids.items()
    }
