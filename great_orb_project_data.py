"""Pinned pre-EOC Great Orb Project activity and reward data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


GREAT_ORB_PROJECT_ACTIVITY_ID = "great_orb_project"
GREAT_ORB_PROJECT_SOURCE = (
    "RuneScape Wiki The Great Orb Project oldid=6564759 "
    "(2012-11-17T03:12:07Z)"
)
GREAT_ORB_PROJECT_ROUNDS = 8
GREAT_ORB_PROJECT_TEMP_CAPACITY = 28


@dataclass(frozen=True)
class GreatOrbAltar:
    id: str
    label: str
    rune: str
    base_xp: float
    multiplier_divisor: int


# The period members' game used these eight altars in this order. Base XP and
# deterministic multiple-rune thresholds reuse the sourced ordinary
# Runecrafting table; the activity doubles XP per essence.
GREAT_ORB_PROJECT_ALTARS = (
    GreatOrbAltar("air", "Air altar", "Air rune", 5.0, 11),
    GreatOrbAltar("mind", "Mind altar", "Mind rune", 5.5, 14),
    GreatOrbAltar("water", "Water altar", "Water rune", 6.0, 19),
    GreatOrbAltar("earth", "Earth altar", "Earth rune", 6.5, 26),
    GreatOrbAltar("fire", "Fire altar", "Fire rune", 7.0, 35),
    GreatOrbAltar("body", "Body altar", "Body rune", 7.5, 46),
    GreatOrbAltar("chaos", "Chaos altar", "Chaos rune", 8.5, 74),
    GreatOrbAltar("nature", "Nature altar", "Nature rune", 9.0, 91),
)

GREAT_ORB_PROJECT_DOCTRINES = (
    ("balanced", "Balanced"),
    ("attract", "Attract orbs"),
    ("repel", "Repel rivals"),
    ("barrier", "Barrier control"),
)

GREAT_ORB_PROJECT_CRAFTING_POLICIES = (
    ("craft_each_round", "Craft each round"),
    ("save_for_nature", "Save for Nature"),
)

# This representative horizontal catalog exercises repeatable consumables and
# existing skill inputs. The complete vertical reward catalog remains
# data-depth work.
GREAT_ORB_PROJECT_REWARDS: dict[str, dict[str, Any]] = {
    "pure_essence": {
        "item": "Pure essence",
        "tokens": 1,
        "quantity": 1,
        "source_item_id": 7936,
        "tradeable": True,
        "stackable": False,
        "category": "resource",
    },
    "air_talisman": {
        "item": "Air talisman",
        "tokens": 50,
        "quantity": 1,
        "source_item_id": 1438,
        "tradeable": True,
        "stackable": False,
        "category": "tool",
    },
}


def great_orb_project_activity_as_dict() -> dict[str, dict[str, Any]]:
    outputs = tuple(
        dict.fromkeys(
            tuple(altar.rune for altar in GREAT_ORB_PROJECT_ALTARS)
            + tuple(str(row["item"]) for row in GREAT_ORB_PROJECT_REWARDS.values())
        )
    )
    return {
        GREAT_ORB_PROJECT_ACTIVITY_ID: {
            "display_name": "Great Orb Project",
            "requirements": {},
            "skill_requirements": {"runecrafting": 50},
            "outputs": outputs,
            "batch_size": 1,
            "group": "minigames",
            "source": GREAT_ORB_PROJECT_SOURCE,
        }
    }

