"""Period-pinned Big Chinchompa tables and review-clock abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


BIG_CHINCHOMPA_SOURCE = (
    "RuneScape Wiki Big Chinchompa oldid=6538836 "
    "(2012-11-06T10:56:45Z)"
)
BIG_CHINCHOMPA_AUDIT = (
    "memory-bank/source-audits/"
    "big-chinchompa-implementation-harvest-2026-07-19.md"
)
BIG_CHINCHOMPA_UTILITY_ID = "big_chinchompa"

BIG_CHINCHOMPA_REVIEW_DAY = 240
BIG_CHINCHOMPA_EVENT_INTERVAL_REVIEWS = 120
BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW = 60
BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW = 6
BIG_CHINCHOMPA_EVENT_MINUTES = 20
BIG_CHINCHOMPA_JAR_CAPACITY = 15
BIG_CHINCHOMPA_PERSONAL_POINT_CAP = 1_500
BIG_CHINCHOMPA_COMPETENCE_CAP = 20_000
BIG_CHINCHOMPA_PLAYER_FULLNESS_BPS_PER_CIRCUIT = 100

# Each label is independently pinned as a period Hunter area. The source page
# says Nyriki appears at Hunter areas but does not enumerate its complete pool.
BIG_CHINCHOMPA_LOCATIONS: Tuple[str, ...] = (
    "Feldip Hunter area",
    "Piscatoris Hunter area",
    "Rellekka Hunter area",
)

WORLD_POPULATION_PROFILES = ("quiet", "normal", "busy")
WORLD_POPULATION_PROFILE_LABELS = {
    "quiet": "Quiet",
    "normal": "Normal",
    "busy": "Busy",
}
# Disclosed naturalism abstraction. Seeded ±20% variation and the 0.75–1.25
# review-day envelope are applied separately in the pure reducer.
WORLD_POPULATION_BASE_CEILINGS = {
    "quiet": 0.72,
    "normal": 0.92,
    "busy": 1.12,
}


@dataclass(frozen=True)
class SoporithMothTier:
    id: str
    display_name: str
    hunter_level: int
    xp: float
    points: int


BIG_CHINCHOMPA_MOTH_TIERS: Tuple[SoporithMothTier, ...] = (
    SoporithMothTier("red", "Red soporith moth", 1, 15.0, 1),
    SoporithMothTier("orange", "Orange soporith moth", 13, 50.0, 2),
    SoporithMothTier("yellow", "Yellow soporith moth", 26, 150.0, 5),
    SoporithMothTier("green", "Green soporith moth", 39, 250.0, 8),
    SoporithMothTier("blue", "Blue soporith moth", 52, 300.0, 12),
    SoporithMothTier("purple", "Purple soporith moth", 65, 320.0, 15),
    SoporithMothTier("grey", "Grey soporith moth", 78, 400.0, 18),
    SoporithMothTier("black", "Black soporith moth", 91, 450.0, 21),
)


@dataclass(frozen=True)
class BigChinchompaReward:
    id: str
    display_name: str
    competence_cost: int
    hunter_level: int
    item_name: str = ""
    hunter_xp: float = 0.0
    target_id: str = ""
    source_item_id: int = 0


BIG_CHINCHOMPA_REWARDS: Tuple[BigChinchompaReward, ...] = (
    BigChinchompaReward(
        "swamp_lizard_ticket",
        "Swamp lizard quota ticket",
        4,
        29,
        "Swamp lizard quota ticket",
        target_id="catch_swamp_lizard",
        source_item_id=24954,
    ),
    BigChinchompaReward(
        "carnivorous_chinchompa_ticket",
        "Carnivorous chinchompa quota ticket",
        6,
        63,
        "Carnivorous chinchompa quota ticket",
        target_id="catch_red_chinchompa",
        source_item_id=24950,
    ),
    BigChinchompaReward(
        "pawya_ticket",
        "Pawya quota ticket",
        8,
        66,
        "Pawya quota ticket",
        target_id="catch_pawya",
        source_item_id=24951,
    ),
    BigChinchompaReward(
        "polar_kebbit_ticket",
        "Polar kebbit quota ticket",
        15,
        70,
        "Polar kebbit quota ticket",
        target_id="catch_polar_kebbit",
        source_item_id=24953,
    ),
    BigChinchompaReward(
        "grenwall_ticket",
        "Grenwall quota ticket",
        10,
        77,
        "Grenwall quota ticket",
        target_id="catch_grenwall",
        source_item_id=24952,
    ),
    BigChinchompaReward(
        "protea_flower",
        "Protea flower",
        1,
        1,
        "Protea flower",
        source_item_id=24948,
    ),
    BigChinchompaReward("swamp_toad", "Swamp toad", 12, 1, "Swamp toad"),
    BigChinchompaReward("flax", "Flax", 2, 1, "Flax"),
    BigChinchompaReward("swamp_tar", "Swamp tar", 4, 1, "Swamp tar"),
    BigChinchompaReward("hunter_xp", "Hunter XP", 1, 1, hunter_xp=5.0),
)
BIG_CHINCHOMPA_REWARDS_BY_ID: Dict[str, BigChinchompaReward] = {
    reward.id: reward for reward in BIG_CHINCHOMPA_REWARDS
}
BIG_CHINCHOMPA_TICKET_BY_TARGET = {
    reward.target_id: reward.item_name
    for reward in BIG_CHINCHOMPA_REWARDS
    if reward.target_id
}


def big_chinchompa_activity_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        BIG_CHINCHOMPA_UTILITY_ID: {
            "display_name": "Big Chinchompa",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": BIG_CHINCHOMPA_SOURCE,
        }
    }


def big_chinchompa_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    items = {
        "Moth jar": {
            "category": "hunter",
            "tradeable": False,
            "stackable": False,
            "item_id": 24949,
            "source": BIG_CHINCHOMPA_SOURCE,
            "status": "activity_local",
        },
        "Protea flower": {
            "category": "hunter",
            "tradeable": False,
            "stackable": False,
            "item_id": 24948,
            "source": BIG_CHINCHOMPA_SOURCE,
            "status": "implemented",
        },
    }
    for reward in BIG_CHINCHOMPA_REWARDS:
        if not reward.target_id:
            continue
        items[reward.item_name] = {
            "category": "hunter",
            "tradeable": False,
            "stackable": True,
            "item_id": reward.source_item_id,
            "source": BIG_CHINCHOMPA_SOURCE,
            "status": "implemented",
        }
    return items
