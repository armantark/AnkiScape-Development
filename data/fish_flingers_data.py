"""Pinned pre-EOC Fish Flingers activity and reward data."""

from __future__ import annotations

from typing import Any, Dict

from .equipment_data import EquipmentBonuses, EquipmentItem


FISH_FLINGERS_ACTIVITY_ID = "fish_flingers"
FISH_FLINGERS_SOURCE = (
    "RuneScape Wiki Fish Flingers oldid=6529096 "
    "(2012-11-03T16:37:15Z)"
)

# Eight catches, not six. The medal table is sourced (three perfect tackles for
# Junior Angler, six for Master Angler, oldid 6529096); the catch count is our own
# abstraction of the competition's many casts, as this family's audit says
# outright. Six catches fix perfect tackles at exactly four forever, which made
# Master Angler permanently unearnable and Team Player nearly so. At eight a
# flawless event yields exactly six perfect tackles, so all four sourced medals
# are reachable and no sourced number moved.
FISH_FLINGERS_EVENT_CATCHES = 8
# The competition lasts its 2012 ten minutes (Darkan ACTIVE_MILLIS; oldid 6529096
# wikitext lines 9, 40 and 435), in 0.6-second game ticks, and the eight catches
# land at even intervals across it (owner, Q4, 2026-10-18).
FISH_FLINGERS_EVENT_TICKS = 1_000
FISH_FLINGERS_CATCH_TICKS = FISH_FLINGERS_EVENT_TICKS // FISH_FLINGERS_EVENT_CATCHES
FISH_FLINGERS_TICKETS_PER_DAY = 2
FISH_FLINGERS_TICKET_CAP = 10
FISH_FLINGERS_TOKEN_CAP = 2000

# Oldid 6529096 establishes these six species, four locations, and the
# one/one/two/two location distribution. The integer modifiers, stock maximum,
# rotation route, and communal depletion amount below are disclosed AnkiScape
# balance values because the period source does not preserve exact catch rates,
# individual weight ranges, or a quantified multiplayer pressure multiplier.
FISH_FLINGERS_SPECIES = (
    {"name": "Bass", "catch_modifier": 0},
    {"name": "Cod", "catch_modifier": 1},
    {"name": "Herring", "catch_modifier": -1},
    {"name": "Pike", "catch_modifier": 2},
    {"name": "Salmon", "catch_modifier": 1},
    {"name": "Trout", "catch_modifier": -1},
)
FISH_FLINGERS_LOCATIONS = (
    {"name": "Lake", "catch_modifier": 0},
    {"name": "River", "catch_modifier": -1},
    {"name": "Beach", "catch_modifier": 0},
    {"name": "Docks", "catch_modifier": 1},
)
FISH_FLINGERS_ROTATION_ROUTE = (
    (0, 0),  # Bass at Lake
    (1, 1),  # Cod at River
    (2, 2),  # Herring at Beach
    (3, 2),  # Pike at Beach
    (4, 3),  # Salmon at Docks
    (5, 3),  # Trout at Docks
)
FISH_FLINGERS_STOCK_MAX = 24
FISH_FLINGERS_COMMUNAL_DEPLETION = 3

# These are disclosed AnkiScape pacing values. The source proves that each
# correct tackle component contributes one third of the rating, while the
# owner-settled contract compresses automatic discovery into the first three
# catches. One entry per catch, so the ramp scales with the game: bait, hook and
# weight land at ticks 125, 250 and 375, three eighths of the ten minutes at
# every speed, and the last five catches run at full efficiency.
FISH_FLINGERS_EFFICIENCY = (0.50, 0.75, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00)
FISH_FLINGERS_DISCOVERY_LABELS = (
    "Best bait discovered",
    "Best hook discovered",
    "Best weight discovered",
    "Perfect tackle retained",
    "Perfect tackle retained",
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
