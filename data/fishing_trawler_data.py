"""Pinned pre-EOC Fishing Trawler activity and compressed pressure data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


FISHING_TRAWLER_ACTIVITY_ID = "fishing_trawler"
FISHING_TRAWLER_SOURCE = (
    "RuneScape Wiki Fishing Trawler oldid=6288357 "
    "(2012-09-24T04:51:16Z); Tiger shark oldid=6448339 "
    "(2012-10-21T04:48:57Z)"
)

# The source trip lasted twelve minutes but did not publish a discrete event
# count. The owner-settled event-scaled contract compresses the consequential
# leak, net, and bailing junctures into this disclosed ten-review schedule.
FISHING_TRAWLER_EVENT_REVIEWS = 10
FISHING_TRAWLER_SINK_WATER = 100
FISHING_TRAWLER_CREW_WATER_OFFSET = 6
FISHING_TRAWLER_PASTE_PER_LEAK = 10
FISHING_TRAWLER_BAIL_AMOUNT = 28
FISHING_TRAWLER_LAYOUT_CAPACITY = 28


@dataclass(frozen=True)
class TrawlerPressureEvent:
    label: str
    water: int
    leaks: int = 0
    tears_net: bool = False


FISHING_TRAWLER_PRESSURE_EVENTS = (
    TrawlerPressureEvent("Open water", 8),
    TrawlerPressureEvent("First leak cluster", 12, leaks=1),
    TrawlerPressureEvent("Heavy swell", 14),
    TrawlerPressureEvent("Net snag", 14, tears_net=True),
    TrawlerPressureEvent("Cross-sea leaks", 16, leaks=1),
    TrawlerPressureEvent("Deep-water swell", 18),
    TrawlerPressureEvent("Hull strain", 16, leaks=1),
    TrawlerPressureEvent("Second net snag", 14, tears_net=True),
    TrawlerPressureEvent("Breaking wave", 22, leaks=2),
    TrawlerPressureEvent("Final run home", 20),
)

FISHING_TRAWLER_DEFAULT_LAYOUT = {
    "Swamp paste": 60,
    "Rope": 4,
    "Bailing bucket": 1,
}

FISHING_TRAWLER_DUTIES = (
    ("balanced", "Balanced"),
    ("water_first", "Bail early"),
    ("maintenance_first", "Repair first"),
    ("catch_first", "Fish aggressively"),
)


@dataclass(frozen=True)
class TrawlerCatch:
    item: str
    level: int
    ordinary_xp: float
    source_item_id: int


# The period Trawler page names tuna through manta ray and says rewards are any
# saltwater fish the player can catch. Anchovies provide the smallest existing
# period-backed level-15 row needed to make the source entry gate productive.
FISHING_TRAWLER_COMMON_CATCHES = (
    TrawlerCatch("Raw anchovies", 15, 40.0, 321),
    TrawlerCatch("Raw tuna", 35, 80.0, 359),
    TrawlerCatch("Raw lobster", 40, 90.0, 377),
    TrawlerCatch("Raw swordfish", 50, 100.0, 371),
    TrawlerCatch("Raw shark", 76, 110.0, 383),
    TrawlerCatch("Raw sea turtle", 79, 38.0, 395),
    TrawlerCatch("Raw manta ray", 81, 46.0, 389),
)

FISHING_TRAWLER_TIGER_SHARK = TrawlerCatch("Raw tiger shark", 95, 80.0, 21520)
# oldid 6448339 says players "typically" receive one every five trips. This is
# the period article's approximate frequency, not a claim about the hidden
# server roll; the exact selector remains data-depth work.
FISHING_TRAWLER_TIGER_SHARK_TRIP_CHANCE = 1.0 / 5.0
FISHING_TRAWLER_CATCHES = (
    *FISHING_TRAWLER_COMMON_CATCHES,
    FISHING_TRAWLER_TIGER_SHARK,
)


def fishing_trawler_activity_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        FISHING_TRAWLER_ACTIVITY_ID: {
            "display_name": "Fishing Trawler",
            "requirements": {},
            "skill_requirements": {"fishing": 15},
            "outputs": tuple(catch.item for catch in FISHING_TRAWLER_CATCHES),
            "batch_size": 1,
            "group": "minigames",
            "source": FISHING_TRAWLER_SOURCE,
        }
    }
