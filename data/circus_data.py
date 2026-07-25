"""Pinned pre-EOC Big Top Bonanza tables and horizontal reward catalog."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CIRCUS_ACTIVITY_ID = "big_top_bonanza"
CIRCUS_WEEK_REVIEWS = 240 * 7
CIRCUS_SOURCE = (
    "RuneScape Wiki Balthazar Beauregard's Big Top Bonanza oldid=6554790 "
    "(2012-11-14T06:58:34Z); OpenRS2 rev-742 items 13663, 13666, "
    "13667, 13672, 13680, and 23003"
)

CIRCUS_STRATEGIES = {
    "max_xp": "Max XP",
    "entertain": "Entertain for costume",
    "balanced": "Balanced",
}


@dataclass(frozen=True)
class CircusTrick:
    id: str
    display_name: str
    level: int
    xp: float
    variant: str


@dataclass(frozen=True)
class CircusPerformance:
    id: str
    display_name: str
    skill_id: str
    max_attempts: int
    tricks: tuple[CircusTrick, ...]
    quest_gate: str = ""


def _trick(
    stable_id: str,
    display_name: str,
    level: int,
    xp: float,
    variant: str,
) -> CircusTrick:
    return CircusTrick(stable_id, display_name, level, xp, variant)


_MAGIC_LOW = (
    (10, 970.0, "Rat", "Book"),
    (20, 2055.0, "Cat", "Tree stump"),
    (30, 2059.0, "Bowl", "Helm"),
    (40, 2133.0, "Penguin", "Shield"),
    (50, 2206.0, "Ork", "Armour"),
)
_MAGIC_HIGH = (
    (60, 2647.0, "Armour"),
    (70, 2794.0, "Stool"),
    (80, 3088.0, "Dumb-bells"),
    (90, 3525.0, "Assistant"),
    (99, 3529.0, "Anvil"),
)

MAGIC_TRICKS = tuple(
    _trick(f"levitate_{level}", f"Levitate {target.lower()}", level, xp, "levitation")
    for level, xp, target, _other in _MAGIC_LOW
) + tuple(
    _trick(f"elemental_{level}", f"Cast at {target.lower()}", level, xp, "elemental")
    for level, xp, _other, target in _MAGIC_LOW
) + tuple(
    trick
    for level, xp, target in _MAGIC_HIGH
    for trick in (
        _trick(f"alchemy_{level}", f"Alchemise {target.lower()}", level, xp, "alchemy"),
        _trick(f"teleport_{level}", f"Teleport {target.lower()}", level, xp, "teleport"),
    )
)

_RANGED_XP = (
    (10, 687.5),
    (20, 1455.0),
    (30, 1458.5),
    (40, 1510.5),
    (50, 1562.5),
    (60, 1875.0),
    (70, 1979.0),
    (80, 2187.5),
    (90, 2495.0),
    (99, 2500.0),
)
RANGED_TRICKS = tuple(
    trick
    for level, xp in _RANGED_XP
    for trick in (
        _trick(f"fixed_target_{level}", f"Fixed target · level {level}", level, xp, "fixed"),
        _trick(f"rotating_target_{level}", f"Rotating target · level {level}", level, xp, "rotating"),
    )
)

_AGILITY_XP = (
    (10, 310.0, "Small hop", "Balls"),
    (20, 419.0, "One-leg balance", "Plates"),
    (30, 830.0, "Twirl", "Eggs"),
    (40, 833.0, "Handstand", "Knives"),
    (50, 1042.0, "Cartwheel", "Spades"),
    (60, 1354.0, "Small leap", "Tuna"),
    (70, 1354.0, "No-hand cartwheel", "Soap"),
    (80, 1354.0, "Forward roll", "Cannon balls"),
    (90, 1354.0, "Large leap", "Torches"),
    (99, 1354.0, "Backflip", "Chinchompas"),
)
AGILITY_TRICKS = tuple(
    _trick(
        f"tightrope_{level}",
        tightrope,
        level,
        xp,
        "tightrope",
    )
    for level, xp, tightrope, _juggle in _AGILITY_XP
) + tuple(
    _trick(f"juggle_{level}", f"Juggle {juggle.lower()}", level, xp, "juggling")
    for level, xp, _tightrope, juggle in _AGILITY_XP
)

_FIREMAKING_XP = (
    (74, 2580.0),
    (78, 2830.0),
    (82, 3080.0),
    (87, 3330.0),
    (91, 3580.0),
    (95, 3830.0),
)
FIRE_BREATHING_TRICKS = tuple(
    _trick(
        f"fire_breath_{level}",
        f"{name} solution",
        level,
        xp,
        "fire_breathing",
    )
    for (level, xp), name in zip(
        _FIREMAKING_XP,
        ("Salt", "Berry", "Copper", "Blurite", "Elemental", "Rubium"),
    )
)
FLAMING_POI_TRICKS = tuple(
    _trick(f"poi_{level}", name, level, xp, "flaming_poi")
    for (level, xp), name in zip(
        _FIREMAKING_XP,
        (
            "Twig's Try",
            "The Lazy Lina",
            "Isis Spiral",
            "The Flint Fling",
            "Spinning Sera",
            "The Big 'E'",
        ),
    )
)

THIEVING_TRICKS = tuple(
    _trick(stable_id, label, level, xp, "magic_tricks")
    for stable_id, label, level, xp in (
        ("pretend_levitate", "Pretend Levitate", 50, 2206.0),
        ("card_trick", "Card Trick", 60, 2647.0),
        ("flowers_from_sleeves", "Flowers from Sleeves", 70, 2794.0),
        ("rabbit_from_hat", "Rabbit from Hat", 80, 3088.0),
        ("water_tank", "Water Tank", 90, 3525.0),
    )
)

CIRCUS_PERFORMANCES: dict[str, CircusPerformance] = {
    row.id: row
    for row in (
        CircusPerformance("magic", "Magic spell casting", "magic", 10, MAGIC_TRICKS),
        CircusPerformance("ranged", "Ranged targets", "ranged", 10, RANGED_TRICKS),
        CircusPerformance("agility", "Agility tightrope", "agility", 10, AGILITY_TRICKS),
        CircusPerformance(
            "fire_breathing",
            "Fire-breathing",
            "firemaking",
            6,
            FIRE_BREATHING_TRICKS,
            "the_firemakers_curse",
        ),
        CircusPerformance(
            "flaming_poi",
            "Flaming poi",
            "firemaking",
            6,
            FLAMING_POI_TRICKS,
            "the_firemakers_curse",
        ),
        CircusPerformance(
            "thieving",
            "Thieving magic tricks",
            "thieving",
            10,
            THIEVING_TRICKS,
            "some_like_it_cold",
        ),
    )
}
CIRCUS_PERFORMANCE_ORDER = tuple(CIRCUS_PERFORMANCES)


# One period-identified representative item per score band is enough to prove
# award, persistence, loss, and free reclaim. The remaining colour/gender and
# set-piece variants are catalog depth, not a different reward mechanic.
CIRCUS_REWARDS: dict[str, dict[str, Any]] = {
    "audience": {
        "display_name": "Giant's hand",
        "item_id": 13666,
        "minimum_score": 1,
        "maximum_score": 500,
    },
    "acrobat": {
        "display_name": "Acrobat hood",
        "item_id": 13680,
        "minimum_score": 501,
        "maximum_score": 1000,
    },
    "firemaker": {
        "display_name": "Firemaker's tabard",
        "item_id": 23003,
        "minimum_score": 501,
        "maximum_score": 1000,
    },
    "clown": {
        "display_name": "Clown hat",
        "item_id": 13667,
        "minimum_score": 1001,
        "maximum_score": 1200,
    },
    "ringmaster": {
        "display_name": "Ringmaster hat",
        "item_id": 13672,
        "minimum_score": 1201,
        "maximum_score": None,
    },
}


def circus_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CIRCUS_ACTIVITY_ID: {
            "display_name": "Big Top Bonanza",
            "requirements": {},
            "outputs": tuple(
                reward["display_name"] for reward in CIRCUS_REWARDS.values()
            ),
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": CIRCUS_SOURCE,
        }
    }


def circus_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        str(spec["display_name"]): {
            "category": "equipment",
            "source_item_id": int(spec["item_id"]),
            "stackable": False,
            "tradeable": False,
            "source": CIRCUS_SOURCE,
        }
        for spec in CIRCUS_REWARDS.values()
    }
