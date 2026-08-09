"""Period-pinned brawling-glove identities and action limits."""

from __future__ import annotations

from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


BRAWLING_GLOVES_SOURCE = (
    "RuneScape Wiki Brawling gloves oldid=6472676 and six skill pages pinned "
    "in memory-bank/source-audits/skilling-brawling-gloves-source-closure-2026-08-09.md"
)

BRAWLING_GLOVE_DATA: dict[str, dict[str, Any]] = {
    "woodcutting": {
        "item_name": "Brawling gloves (wc)",
        "item_id": 13850,
        "max_actions": 732,
        "outside_multiplier": 1.5,
        "wilderness_multiplier": 4.0,
    },
    "firemaking": {
        "item_name": "Brawling gloves (fm)",
        "item_id": 13851,
        "max_actions": 1200,
        "outside_multiplier": 1.5,
        "wilderness_multiplier": 5.0,
    },
    "mining": {
        "item_name": "Brawling gloves (mining)",
        "item_id": 13852,
        # PLACEHOLDER(brawling_gloves.mining_action_limit): deterministic review-action midpoint for the sourced 350-800 ore estimate.
        "max_actions": 575,
        "outside_multiplier": 1.5,
        "wilderness_multiplier": 4.0,
    },
    "smithing": {
        "item_name": "Brawling gloves (smithing)",
        "item_id": 13855,
        "max_actions": 434,
        "outside_multiplier": 1.5,
        "wilderness_multiplier": 4.0,
    },
    "fishing": {
        "item_name": "Brawling gloves (fishing)",
        "item_id": 13856,
        "max_actions": 400,
        "outside_multiplier": 1.5,
        "wilderness_multiplier": 5.0,
    },
    "cooking": {
        "item_name": "Brawling gloves (cooking)",
        "item_id": 13857,
        "max_actions": 1109,
        "outside_multiplier": 1.5,
        "wilderness_multiplier": 4.0,
    },
}


def brawling_gloves_condition_data_as_dict() -> dict[str, dict[str, Any]]:
    return {
        f"brawling_{skill_id}": {
            "display_name": spec["item_name"],
            "full_name": spec["item_name"],
            "max_condition": spec["max_actions"],
            "names_by_percent": {100: spec["item_name"], 0: spec["item_name"]},
            "degrade_during_combat": False,
            "unsafe_death_percent": None,
            "source": BRAWLING_GLOVES_SOURCE,
        }
        for skill_id, spec in BRAWLING_GLOVE_DATA.items()
    }


def brawling_gloves_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    zero_bonuses = EquipmentBonuses()
    return {
        spec["item_name"]: EquipmentItem(
            item_name=spec["item_name"],
            slot="hands",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type=f"brawling_{skill_id}",
            bonuses=zero_bonuses,
            attack_speed=4,
            source_item_id=spec["item_id"],
            source=BRAWLING_GLOVES_SOURCE,
            source_status="period item definition and cutoff wiki",
        )
        for skill_id, spec in BRAWLING_GLOVE_DATA.items()
    }


def brawling_gloves_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        spec["item_name"]: {
            "category": "equipment",
            "item_id": spec["item_id"],
            "stackable": False,
            "tradeable": False,
            "source": BRAWLING_GLOVES_SOURCE,
        }
        for spec in BRAWLING_GLOVE_DATA.values()
    }
