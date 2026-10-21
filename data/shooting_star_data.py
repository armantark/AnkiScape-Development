"""Period Shooting Star tables and disclosed review-clock abstractions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


SHOOTING_STAR_SOURCE = (
    "RuneScape Wiki Shooting Star oldid=6556329 "
    "(2012-11-15T09:20:35Z)"
)
SHOOTING_STAR_AUDIT = (
    "memory-bank/source-audits/"
    "shooting-star-implementation-harvest-2026-07-20.md"
)
SHOOTING_STAR_ACTIVITY_ID = "shooting_stars"
SHOOTING_STAR_STARDUST = "Stardust"
SHOOTING_STAR_STARDUST_ITEM_ID = 13727

# Owner-settled translations onto AnkiScape's answered-card clocks.
SHOOTING_STAR_INTERVAL_REVIEWS = 20

# World-day-phased calendar durations, in 0.6-second ticks.
SHOOTING_STAR_INTERVAL_TICKS = 120 * 100
SHOOTING_STAR_SPRITE_TICKS = 12 * 100

SHOOTING_STAR_SPRITE_REVIEWS = 2

# Fifteen source minutes at one RuneScape tick per 0.6 seconds. The live
# temporary-effect clock consumes the same ticks used by Charge and combat.
SHOOTING_STAR_ORE_BONUS_TICKS = 1_500
SHOOTING_STAR_ORE_BONUS_CHANCE = 0.25
SHOOTING_STAR_STARDUST_CAP = 200

# Hidden initial-size and first-finder distributions are source-blocked. These
# values preserve the former Normal profile's observed baseline while the shared
# event-seeded fuzziness remains active.
SHOOTING_STAR_POPULATION_BASE_CEILING = 0.92
SHOOTING_STAR_FIRST_FINDER_CHANCE = 0.16


@dataclass(frozen=True)
class ShootingStarLayer:
    size: int
    mining_level: int
    xp_per_dust: float
    dust: int


SHOOTING_STAR_LAYERS: Tuple[ShootingStarLayer, ...] = (
    ShootingStarLayer(9, 90, 210.0, 15),
    ShootingStarLayer(8, 80, 145.0, 25),
    ShootingStarLayer(7, 70, 114.0, 40),
    ShootingStarLayer(6, 60, 71.0, 80),
    ShootingStarLayer(5, 50, 47.0, 175),
    ShootingStarLayer(4, 40, 32.0, 250),
    ShootingStarLayer(3, 30, 29.0, 439),
    ShootingStarLayer(2, 20, 25.0, 700),
    ShootingStarLayer(1, 10, 14.0, 1_200),
)
SHOOTING_STAR_LAYERS_BY_SIZE: Dict[int, ShootingStarLayer] = {
    layer.size: layer for layer in SHOOTING_STAR_LAYERS
}

SHOOTING_STAR_REWARD_MAXIMA = {
    "Cosmic rune": 152,
    "Astral rune": 52,
    "Gold ore": 20,
    "Coins": 50_002,
}

# The complete crash-site table in oldid 6556329. Locations are flavour only;
# AnkiScape deliberately has no telescope, travel, or map phase.
SHOOTING_STAR_LOCATIONS: Tuple[str, ...] = (
    "Crafting Guild mining site",
    "Falador east bank",
    "Rimmington mining site",
    "Falador mining site",
    "Karamja north-western mining site",
    "Brimhaven mining site",
    "South Crandor mining site",
    "Karamja mining site",
    "Shilo Village mining site",
    "Keldagrim entrance mining site",
    "Jatizso mine",
    "Lunar Isle mine",
    "Managing Miscellania mining site",
    "Central Fremennik Isles mining site",
    "Rellekka mining site",
    "Legends' Guild mining site",
    "South-east Ardougne mining site",
    "Coal Trucks",
    "Yanille Bank",
    "Fight Arena mining site",
    "Al Kharid bank",
    "Al Kharid mining site",
    "Duel Arena bank chest",
    "Uzer mining site",
    "Nardah mining site",
    "Nardah bank",
    "Western desert mining site",
    "South-east Varrock mining site",
    "Lumbridge Swamp training mining site",
    "South-west Varrock mining site",
    "Varrock east bank",
    "Burgh de Rott Bank",
    "Canifis Bank",
    "Gnome Stronghold Bank",
    "Lletya bank",
    "Piscatoris mining site",
    "Bandit camp mining site",
    "Mage Arena bank",
    "Pirates' Hideout mining site",
    "North Edgeville mining site",
    "Lava Maze runite mining site",
    "Southern wilderness mining site",
    "Wilderness Volcano",
)

SHOOTING_STAR_LEGACY_LOCATION_ALIASES = {
    "Crafting Guild mine": "Crafting Guild mining site",
    "Falador east mine": "Falador east bank",
    "Rimmington mine": "Rimmington mining site",
    "Varrock south-east mine": "South-east Varrock mining site",
    "Al Kharid mine": "Al Kharid mining site",
    "Lumbridge Swamp mine": "Lumbridge Swamp training mining site",
}


def shooting_star_activity_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        SHOOTING_STAR_ACTIVITY_ID: {
            "display_name": "Shooting Stars",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": SHOOTING_STAR_SOURCE,
        }
    }


def shooting_star_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        SHOOTING_STAR_STARDUST: {
            "category": "mining",
            "tradeable": False,
            "stackable": True,
            "item_id": SHOOTING_STAR_STARDUST_ITEM_ID,
            "source": SHOOTING_STAR_SOURCE,
            "status": "implemented",
        }
    }
