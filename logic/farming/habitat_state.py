"""Flat Habitat ownership and strict checks against the actual Farming record."""

import copy
from collections.abc import Mapping

from ...data.habitat import (
    SHADOW_FEATURE, SHADOW_FLOWER_PATCH, SHADOW_REQUIRED_CROP,
    SHADOW_REJECTS_DEAD_FLOWER, ABANDONED_HOUSE_LEVEL, ABANDONED_HOUSE_FEE,
)

from ..skilling_boost_logic import skilling_effective_level_pure

HOUSE_REASON = "Build the Abandoned house through Papa Mambo in Shop, or reach Construction 57."


def default_herblore_habitat_state_pure():
    return {"habitat_feature": None}


def sanitize_herblore_habitat_state_pure(player_data):
    feature = player_data.get("habitat_feature")
    return {"habitat_feature": feature if isinstance(feature, str) and feature.strip() else None}


def shadow_attraction_reasons_pure(player_data) -> tuple[str, ...]:
    data = player_data if isinstance(player_data, Mapping) else {}
    reasons = []
    if data.get("habitat_feature") != SHADOW_FEATURE:
        reasons.append("Abandoned house")
    patches = data.get("farm_patches")
    record = patches.get(SHADOW_FLOWER_PATCH) if isinstance(patches, Mapping) else None
    healthy = isinstance(record, Mapping) and (
        record.get("crop_id") == SHADOW_REQUIRED_CROP
        and type(record.get("stage")) is int and record["stage"] >= 0
        and record.get("diseased") is False
        and (not SHADOW_REJECTS_DEAD_FLOWER or record.get("dead") is False)
        and record.get("stump") is False
    )
    if not healthy:
        reasons.append("healthy planted Red blossom")
    return tuple(reasons)


def _can_build(data):
    return skilling_effective_level_pure(data, "construction") >= ABANDONED_HOUSE_LEVEL


def apply_abandoned_house_pure(player_data, paid=False):
    """Construct one active feature atomically; payment never requires a level."""
    updated = copy.deepcopy(dict(player_data))
    if updated.get("habitat_feature") == SHADOW_FEATURE:
        return updated, False, "The Abandoned house is already built."
    if paid:
        inventory = updated.get("inventory", {})
        if inventory.get("Coins", 0) < ABANDONED_HOUSE_FEE:
            return updated, False, "Requires 57,000 Coins."
        updated["inventory"] = dict(inventory)
        updated["inventory"]["Coins"] -= ABANDONED_HOUSE_FEE
    elif not _can_build(updated):
        return updated, False, HOUSE_REASON
    updated["habitat_feature"] = SHADOW_FEATURE
    return updated, True, "Built the Abandoned house."


def hunter_attraction_reasons_pure(player_data, target):
    """Only Shadow has maintained Habitat admission in this bounded route."""
    return shadow_attraction_reasons_pure(player_data) if target == "track_shadow_jadinko" else ()
