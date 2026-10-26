"""Shared Farming patch defaults and plan sanitation, below orchestration."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ...data.farming_data import COMPOST_TIERS, FARMING_CROPS_BY_ID

PLANT_CURE_ITEM_FIRST = "plant_cure_item_first"
CURE_PLANT_SPELL_FIRST = "cure_plant_spell_first"
CURE_ROUTE_PREFERENCES = frozenset({
    PLANT_CURE_ITEM_FIRST,
    CURE_PLANT_SPELL_FIRST,
})


def _default_patch_record() -> dict[str, Any]:
    return {
        "crop_id": None,
        "last_crop_id": None,
        "planted_at": 0,
        "stage": 0,
        "compost_tier": "none",
        "lives": 0,
        "diseased": False,
        "dead": False,
        "protected": False,
        "livid_protected": False,
        "watered": False,
        "health_checked": False,
        "stump": False,
        "produce_count": 0,
        "last_regrowth_at": 0,
        "next_regrowth_at": 0,
        "jade_state": None,
        "jade_prunes": 0,
        "jade_combat_encounter": {},
        "jade_attack_style_index": 0,
        "plan": None,
    }


def _sanitize_plan(raw: Any) -> Optional[dict[str, Any]]:
    if not isinstance(raw, Mapping):
        return None
    plan = dict(raw)
    crop_id = plan.get("crop_id")
    if not isinstance(crop_id, str) or crop_id not in FARMING_CROPS_BY_ID:
        return None
    tier = plan.get("compost_tier", "none")
    plan["crop_id"] = crop_id
    plan["compost_tier"] = tier if tier in COMPOST_TIERS else "none"
    plan["protection_intent"] = bool(
        plan.get("protection_intent", False)
        and FARMING_CROPS_BY_ID[crop_id].protection is not None
    )
    plan["watering_intent"] = bool(plan.get("watering_intent", True))
    plan["cure_intent"] = bool(plan.get("cure_intent", True))
    preference = str(
        plan.get("cure_route_preference", PLANT_CURE_ITEM_FIRST) or ""
    )
    plan["cure_route_preference"] = (
        preference
        if preference in CURE_ROUTE_PREFERENCES
        else PLANT_CURE_ITEM_FIRST
    )
    plan["protection_paid"] = bool(plan.get("protection_paid", False))
    plan["fertile_soil_applied"] = bool(plan.get("fertile_soil_applied", False))
    return plan
