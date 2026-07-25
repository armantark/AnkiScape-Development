"""Pinned pre-EOC Fish Flingers activity and reward data."""

from __future__ import annotations

from typing import Any, Dict

from .equipment_data import EquipmentBonuses, EquipmentItem


FISH_FLINGERS_ACTIVITY_ID = "fish_flingers"
FISH_FLINGERS_SOURCE = (
    "RuneScape Wiki Fish Flingers oldid=6529096 "
    "(2012-11-03T19:53:36Z)"
)

FISH_FLINGERS_EVENT_REVIEWS = 6
FISH_FLINGERS_TICKETS_PER_DAY = 2
FISH_FLINGERS_TICKET_CAP = 10
FISH_FLINGERS_TOKEN_CAP = 2000
FISH_FLINGERS_WORLD_DAY_REVIEWS = 240

# These are disclosed AnkiScape pacing values. The source proves that each
# correct tackle component contributes one third of the rating, while the
# owner-settled contract compresses automatic discovery into three reviews.
FISH_FLINGERS_EFFICIENCY = (0.50, 0.75, 1.00, 1.00, 1.00, 1.00)
FISH_FLINGERS_DISCOVERY_LABELS = (
    "Best bait discovered",
    "Best hook discovered",
    "Best weight discovered",
    "Perfect tackle retained",
    "Perfect tackle retained",
    "Perfect tackle retained",
)

# The 24 July 2012 reward table is literal in oldid 6529096. Medal thresholds
# are cumulative and the previous tackle box is upgraded in place.
FISH_FLINGERS_REWARDS: Dict[str, Dict[str, Any]] = {
    "fishing_hat": {"item": "Fishing hat", "tokens": 140, "medals": 0},
    "fishing_jacket": {"item": "Fishing jacket", "tokens": 140, "medals": 0},
    "fishing_waders": {"item": "Fishing waders", "tokens": 140, "medals": 0},
    "fishing_boots": {"item": "Fishing boots", "tokens": 140, "medals": 0},
    "beginner_tackle_box": {
        "item": "Beginner's tackle box",
        "tokens": 110,
        "medals": 20,
    },
    "basic_tackle_box": {
        "item": "Basic tackle box",
        "tokens": 230,
        "medals": 50,
        "previous": "Beginner's tackle box",
    },
    "standard_tackle_box": {
        "item": "Standard tackle box",
        "tokens": 470,
        "medals": 110,
        "previous": "Basic tackle box",
    },
    "professional_tackle_box": {
        "item": "Professional tackle box",
        "tokens": 900,
        "medals": 230,
        "previous": "Standard tackle box",
    },
    "champion_tackle_box": {
        "item": "Champion's tackle box",
        "tokens": 1860,
        "medals": 500,
        "previous": "Professional tackle box",
    },
}


def fish_flingers_activity_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        FISH_FLINGERS_ACTIVITY_ID: {
            "display_name": "Fish Flingers",
            "requirements": {},
            "skill_requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": FISH_FLINGERS_SOURCE,
        }
    }


def fish_flingers_extra_items_as_dict() -> Dict[str, Dict[str, Any]]:
    slots = {
        "Fishing hat": "head",
        "Fishing jacket": "body",
        "Fishing waders": "legs",
        "Fishing boots": "feet",
    }
    source_ids = {
        "Beginner's tackle box": 15666,
        "Basic tackle box": 15667,
        "Standard tackle box": 15668,
        "Professional tackle box": 15669,
        "Champion's tackle box": 15670,
        "Fishing hat": 24427,
        "Fishing jacket": 24428,
        "Fishing waders": 24429,
        "Fishing boots": 24430,
    }
    return {
        str(spec["item"]): {
            "category": "equipment" if str(spec["item"]) in slots else "tool",
            "stackable": False,
            "tradeable": False,
            "source": FISH_FLINGERS_SOURCE,
            "source_item_id": source_ids[str(spec["item"])],
            **(
                {
                    "equipment_slot": slots[str(spec["item"])],
                    "equipment_type": slots[str(spec["item"])],
                }
                if str(spec["item"]) in slots
                else {}
            ),
        }
        for spec in FISH_FLINGERS_REWARDS.values()
    }


def fish_flingers_equipment_data_as_dict() -> Dict[str, EquipmentItem]:
    slots = {
        "Fishing hat": ("head", 24427),
        "Fishing jacket": ("body", 24428),
        "Fishing waders": ("legs", 24429),
        "Fishing boots": ("feet", 24430),
    }
    return {
        item_name: EquipmentItem(
            item_name=item_name,
            slot=slot,
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="fishing_outfit",
            bonuses=EquipmentBonuses(),
            attack_speed=4,
            source_item_id=source_item_id,
            source=(
                "OpenRS2 cache rev 742 item definition; " + FISH_FLINGERS_SOURCE
            ),
            source_status="period cache identity and wear option",
            skill_requirements=(),
            weapon_type=-1,
        )
        for item_name, (slot, source_item_id) in slots.items()
    }
