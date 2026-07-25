"""Typed freeze-date pet definitions and review-native care calibration."""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

try:
    from .pet_data_generated import PET_CATALOG, PET_OLDID
except ImportError:
    from pet_data_generated import PET_CATALOG, PET_OLDID


PET_GROWTH_REVIEWS_PER_STAGE = 25
PET_BABY_HUNGER_PER_REVIEW = 6.0
PET_ADULT_HUNGER_PER_REVIEW = 3.0
PET_FEED_HUNGER_REDUCTION = 30.0


@dataclass(frozen=True)
class PetDefinition:
    id: str
    display_name: str
    summoning_level: int
    requirements: str
    stage_images: tuple[str, ...]
    stage_count: int
    foods: tuple[str, ...]
    food_summary: str
    acquisition: str
    colour_count: int
    summoning_related: bool
    obtainable: bool
    legacy_compatibility_only: bool
    release_source_blocked: bool
    source: str

    @property
    def asset_path(self) -> str:
        return f"petitems/{self.id}_0.png"


def _row_to_pet(row: Mapping[str, object]) -> PetDefinition:
    return PetDefinition(
        id=str(row["id"]),
        display_name=str(row["display_name"]),
        summoning_level=int(row["summoning_level"]),
        requirements=str(row["requirements"]),
        stage_images=tuple(str(value) for value in row["stage_images"]),
        stage_count=int(row["stage_count"]),
        foods=tuple(str(value) for value in row["foods"]),
        food_summary=str(row["food_summary"]),
        acquisition=str(row["acquisition"]),
        colour_count=int(row["colour_count"]),
        summoning_related=bool(row["summoning_related"]),
        obtainable=bool(row["obtainable"]),
        legacy_compatibility_only=bool(row["legacy_compatibility_only"]),
        release_source_blocked=bool(row["release_source_blocked"]),
        source=str(row["source"]),
    )


PETS = tuple(_row_to_pet(row) for row in PET_CATALOG)
PETS_BY_ID: Mapping[str, PetDefinition] = MappingProxyType(
    {pet.id: pet for pet in PETS}
)
OBTAINABLE_PETS = tuple(pet for pet in PETS if pet.obtainable)


def pet_asset_manifest() -> tuple[tuple[str, str, str], ...]:
    rows = []
    for pet in PETS:
        for index, wiki_title in enumerate(pet.stage_images):
            rows.append(
                (
                    f"{pet.display_name} stage {index + 1}",
                    wiki_title,
                    f"petitems/{pet.id}_{index}.png",
                )
            )
    return tuple(rows)


def pet_display_foods(pet: PetDefinition) -> tuple[str, ...]:
    """Return explicit storage keys when the period table names real items."""

    ignored = {
        "fish",
        "raw meat",
        "raw fish",
        "chicken",
        "kitten",
        "runecrafting altar",
    }
    return tuple(
        food
        for food in pet.foods
        if food.casefold() not in ignored and re.search(r"[a-z]", food, re.I)
    )


assert PET_OLDID == 6579897
assert len(PETS) == 47
assert len(OBTAINABLE_PETS) == 44
