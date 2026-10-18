"""Period-pinned Evil Tree tables and disclosed review-scale abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


EVIL_TREE_SOURCE = (
    "RuneScape Wiki Evil Tree oldid=6569638 "
    "(2012-11-17T22:22:59Z)"
)
EVIL_TREE_AUDIT = (
    "memory-bank/source-audits/"
    "evil-tree-implementation-harvest-2026-07-19.md"
)
EVIL_TREE_UTILITY_ID = "evil_tree"
EVIL_TREE_KINDLING = "Evil tree kindling"
EVIL_TREE_KINDLING_ITEM_ID = 14666

# Owner-settled review-clock translations. These are intentionally named
# abstractions rather than presented as recovered RuneScape formulas.
EVIL_TREE_SPAWN_REVIEWS = 20
EVIL_TREE_ACTIVE_REVIEWS = 5
EVIL_TREE_DAILY_INTERACTIONS = 2
EVIL_TREE_NEST_MULTIPLIER = 2.0
EVIL_TREE_REWARD_MINIMUM_SHARE = 0.5

EVIL_TREE_ELIGIBLE_BLESSING_TARGETS = frozenset(
    {"tree", "oak", "willow", "maple", "yew", "magic"}
)


@dataclass(frozen=True)
class EvilTreeTier:
    id: str
    display_name: str
    woodcutting_level: int
    farming_level: int
    firemaking_level: int
    nurture_xp: float
    root_xp: float
    tree_xp: float
    firemaking_xp: float
    max_logs: Tuple[Tuple[str, int], ...]
    max_coins: int
    blessing_reviews: int
    reward_seed: str
    source: str = EVIL_TREE_SOURCE


EVIL_TREE_TIERS: Tuple[EvilTreeTier, ...] = (
    EvilTreeTier(
        "normal",
        "Normal evil tree",
        1,
        1,
        1,
        20.0,
        3.0,
        15.1,
        200.0,
        (("Logs", 12),),
        185,
        1,
        "Acorn",
    ),
    EvilTreeTier(
        "oak",
        "Evil oak tree",
        15,
        7,
        15,
        45.0,
        6.4,
        32.4,
        300.0,
        (("Oak logs", 24),),
        326,
        2,
        "Acorn",
    ),
    EvilTreeTier(
        "willow",
        "Willow evil tree",
        30,
        15,
        30,
        66.0,
        9.1,
        45.7,
        450.0,
        (("Willow logs", 226),),
        1_127,
        2,
        "Willow seed",
    ),
    EvilTreeTier(
        "maple",
        "Maple evil tree",
        45,
        22,
        45,
        121.5,
        11.1,
        55.8,
        675.0,
        (("Maple logs", 131),),
        1_280,
        3,
        "Maple seed",
    ),
    EvilTreeTier(
        "yew",
        "Yew evil tree",
        60,
        30,
        60,
        172.5,
        12.8,
        64.4,
        1_012.5,
        (("Yew logs", 17),),
        2_334,
        4,
        "Yew seed",
    ),
    EvilTreeTier(
        "magic",
        "Magic evil tree",
        75,
        37,
        75,
        311.0,
        14.1,
        70.9,
        1_517.5,
        (("Magic logs", 10),),
        4_737,
        4,
        "Magic seed",
    ),
    EvilTreeTier(
        "elder",
        "Elder evil tree",
        85,
        42,
        85,
        687.5,
        15.5,
        77.8,
        2_000.5,
        (
            ("Teak logs", 375),
            ("Mahogany logs", 102),
            ("Yew logs", 59),
            ("Magic logs", 18),
        ),
        8_694,
        5,
        "Magic seed",
    ),
)

EVIL_TREE_TIERS_BY_ID: Dict[str, EvilTreeTier] = {
    tier.id: tier for tier in EVIL_TREE_TIERS
}

# Unrestricted labels only. Quest-gated locations are deliberately excluded;
# the owning contract treats the location as sourced event flavor, not travel.
EVIL_TREE_LOCATIONS: Tuple[str, ...] = (
    "south of Seers' Village",
    "east of Rimmington",
    "north of Falador",
    "west of Catherby",
    "Draynor Village",
    "west of Falador",
    "Edgeville",
    "near Yanille",
)


def evil_tree_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        EVIL_TREE_KINDLING: {
            "category": "material",
            "tradeable": False,
            "item_id": EVIL_TREE_KINDLING_ITEM_ID,
            "source": EVIL_TREE_SOURCE,
            "status": "implemented",
        }
    }

