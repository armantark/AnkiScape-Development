"""Period-pinned Sorceress's Garden tables and compact activity metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SORCERESS_GARDEN_ACTIVITY_ID = "sorceress_garden"
SORCERESS_GARDEN_SOURCE = (
    "RuneScape Wiki Sorceress's Garden oldid=6466752 "
    "(2012-10-24T20:04:59Z); Sq'irkjuice oldid=6520647"
)


@dataclass(frozen=True)
class SorceressGardenSeason:
    id: str
    display_name: str
    thieving_level: int
    fruit: str
    juice: str
    fruit_per_juice: int
    fruit_farming_xp: float
    herb_farming_xp: float
    osman_thieving_xp: float
    thieving_boost: int
    run_energy_pct: int


SORCERESS_GARDEN_SEASONS = (
    SorceressGardenSeason(
        "winter", "Winter", 1, "Winter sq'irk", "Winter sq'irkjuice",
        5, 30.0, 30.0, 350.0, 0, 10,
    ),
    SorceressGardenSeason(
        "spring", "Spring", 25, "Spring sq'irk", "Spring sq'irkjuice",
        4, 40.0, 40.0, 1_350.0, 1, 20,
    ),
    SorceressGardenSeason(
        "autumn", "Autumn", 45, "Autumn sq'irk", "Autumn sq'irkjuice",
        3, 50.0, 50.0, 2_350.0, 2, 30,
    ),
    SorceressGardenSeason(
        "summer", "Summer", 65, "Summer sq'irk", "Summer sq'irkjuice",
        2, 60.0, 50.0, 3_000.0, 3, 40,
    ),
)
SORCERESS_GARDEN_SEASONS_BY_ID = {
    season.id: season for season in SORCERESS_GARDEN_SEASONS
}

# The cutoff page says the two herbs are completely random and may range up to
# dwarf weed, but does not publish weights. The complete ordinary cutoff herb
# range is therefore used with an explicitly equal bounded distribution; rare
# roll precision remains source-harvest work rather than a missing mechanic.
SORCERESS_GARDEN_HERB_POOL = (
    "Grimy guam",
    "Grimy marrentill",
    "Grimy tarromin",
    "Grimy harralander",
    "Grimy ranarr",
    "Grimy toadflax",
    "Grimy irit",
    "Grimy avantoe",
    "Grimy kwuarm",
    "Grimy snapdragon",
    "Grimy cadantine",
    "Grimy lantadyme",
    "Grimy dwarf weed",
)


def sorceress_garden_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SORCERESS_GARDEN_ACTIVITY_ID: {
            "display_name": "Sorceress's Garden",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "source": SORCERESS_GARDEN_SOURCE,
        }
    }


def sorceress_garden_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {}
    for season in SORCERESS_GARDEN_SEASONS:
        items[season.fruit] = {
            "category": "activity",
            "stackable": False,
            "tradeable": False,
            "source": SORCERESS_GARDEN_SOURCE,
            "status": "implemented",
        }
        items[season.juice] = {
            "category": "consumable",
            "stackable": False,
            "tradeable": False,
            "source": SORCERESS_GARDEN_SOURCE,
            "status": "implemented",
        }
    return items


def sorceress_garden_consumables_as_dict() -> dict[str, dict[str, Any]]:
    return {
        season.juice: {
            "kind": "skill_boost_run_energy",
            "skill_id": "thieving",
            "boost": season.thieving_boost,
            "run_energy_pct": season.run_energy_pct,
            "leaves": "Beer glass",
            "message": (
                f"You drink the {season.display_name.lower()} sq'irkjuice. "
                f"It restores {season.run_energy_pct}% run energy"
                + (
                    f" and boosts Thieving by {season.thieving_boost}."
                    if season.thieving_boost
                    else "."
                )
            ),
            "source": SORCERESS_GARDEN_SOURCE,
        }
        for season in SORCERESS_GARDEN_SEASONS
    }
