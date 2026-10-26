"""Shared Farming maturity and automatic watering calculations."""

from __future__ import annotations

import math
from typing import Any, Mapping

from ...data.habitat import RED_BLOSSOM_WATERING_FACTOR
from .materials import _int


def _is_mature(record: Mapping[str, Any], crop: Any) -> bool:
    return bool(crop.stages is not None and _int(record.get("stage", 0)) >= crop.stages and not record.get("dead"))


def automatic_watering_applies(crop, inventory, watering_intent):
    return (
        watering_intent
        and (crop.patch_type in {"allotment", "flower", "hops"} or crop.id == "red_blossom")
        and any(_int(inventory.get(item)) > 0 for item in ("Watering can", "Watering can (8)"))
    )


def watered_disease_slots(crop, record, compost_tier):
    watering_factor = RED_BLOSSOM_WATERING_FACTOR if crop.id == "red_blossom" else 0.9
    if not record.get("watered"):
        watering_factor = 1.0
    return math.floor(crop.disease_slots * compost_tier.disease_factor * watering_factor)
