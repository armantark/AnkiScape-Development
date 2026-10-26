"""Owned-supply Shadow upkeep using ordinary Farming transactions only."""

import copy
from collections.abc import Mapping

from ...data.farming_data import FARMING_CROPS_BY_ID
from ...data.habitat import SHADOW_FEATURE, SHADOW_FLOWER_PATCH, SHADOW_REQUIRED_CROP
from .habitat_state import HOUSE_REASON, _can_build, apply_abandoned_house_pure, shadow_attraction_reasons_pure

from .state import _default_patch_record, _sanitize_plan, PLANT_CURE_ITEM_FIRST
from .care import _is_mature


FLOWER_REASON = "The existing Habitat flower must be harvested or cleared first."


def _decision(status, reason, step=None):
    result = {"status": status, "reason": reason}
    if step:
        result.update(verb=step["kind"], step=step)
    return result


def _matching_plan(data, record, crop_id):
    plans = data.get("farm_plans", {})
    raw = plans.get(SHADOW_FLOWER_PATCH) if isinstance(plans, Mapping) else None
    plan = _sanitize_plan(raw) or _sanitize_plan(record.get("plan"))
    return plan if plan and plan["crop_id"] == crop_id else None


def _planting_preflight(data, execute_field):
    # Hypothetical empty patch only: the returned copy is discarded. Farming
    # validates retained tools, seed count, level and the matching prepaid plan.
    probe = copy.deepcopy(dict(data))
    patches = probe.setdefault("farm_patches", {})
    record = patches.get(SHADOW_FLOWER_PATCH, {})
    empty = _default_patch_record()
    empty["plan"] = copy.deepcopy(record.get("plan"))
    patches[SHADOW_FLOWER_PATCH] = empty
    _, ok, info = execute_field(
        probe, {"kind": "plant", "patch_id": SHADOW_FLOWER_PATCH, "crop_id": SHADOW_REQUIRED_CROP}
    )
    return ok, info["message"]


def _shadow_cure_preview(player_data, record, step, execute_field):
    plan = _matching_plan(player_data, record, record["crop_id"])
    if plan and not plan["cure_intent"]:
        return _decision("waiting", "Waiting for the diseased Habitat flower; automatic cure is disabled.")
    step.update(kind="cure", cure_route_preference=plan["cure_route_preference"] if plan else PLANT_CURE_ITEM_FIRST)
    _, ok, info = execute_field(player_data, step)
    return _decision("field" if ok else "waiting", info["message"], step)


def _shadow_replacement_preview(player_data, step, execute_field):
    ok, reason = _planting_preflight(player_data, execute_field)
    if not ok:
        return _decision("blocked", reason)
    _, ok, info = execute_field(player_data, step)
    return _decision("field" if ok else "blocked", info["message"] if ok else FLOWER_REASON, step)


def _shadow_occupied_flower_preview(player_data, record, execute_field):
    crop_id = record.get("crop_id")
    crop = FARMING_CROPS_BY_ID.get(crop_id) if isinstance(crop_id, str) else None
    if crop is None:
        return _decision("blocked", FLOWER_REASON)
    step = {"patch_id": SHADOW_FLOWER_PATCH}
    if record.get("dead") or record.get("stump"):
        return _shadow_replacement_preview(player_data, {**step, "kind": "clear"}, execute_field)
    if record.get("diseased"):
        return _shadow_cure_preview(player_data, record, step, execute_field)
    if crop_id == SHADOW_REQUIRED_CROP or not crop.runnable or crop.stages is None or crop.stage_minutes is None:
        return _decision("blocked", FLOWER_REASON)
    if not _is_mature(record, crop):
        return _decision("waiting", "Waiting for the existing Habitat flower to mature.")
    return _shadow_replacement_preview(player_data, {**step, "kind": "harvest"}, execute_field)


def preview_shadow_field_setup(player_data, execute_field):
    """One shared next-step decision; isolated probes never draw randomness."""
    player_data = copy.deepcopy(dict(player_data))
    if player_data.get("habitat_feature") != SHADOW_FEATURE and not _can_build(player_data):
        return _decision("blocked", HOUSE_REASON)
    # Inspect the actual record before ordinary Farming sanitation.
    if not shadow_attraction_reasons_pure({**player_data, "habitat_feature": SHADOW_FEATURE}):
        return _decision("ready", "Shadow's Habitat is ready.")
    patches = player_data.get("farm_patches", {})
    if not isinstance(patches, Mapping):
        return _decision("blocked", FLOWER_REASON)
    record = patches.get(SHADOW_FLOWER_PATCH)
    if SHADOW_FLOWER_PATCH in patches and not isinstance(record, Mapping):
        return _decision("blocked", FLOWER_REASON)
    record = record or {}
    if record.get("crop_id") is not None:
        return _shadow_occupied_flower_preview(player_data, record, execute_field)
    ok, reason = _planting_preflight(player_data, execute_field)
    step = {"patch_id": SHADOW_FLOWER_PATCH, "kind": "plant", "crop_id": SHADOW_REQUIRED_CROP}
    return _decision("field" if ok else "blocked", reason, step)


def apply_shadow_field_setup_step(player_data, random_random, execute_field):
    """Commit at most one field step, building freely only on ready/plant success."""
    info = preview_shadow_field_setup(player_data, execute_field)
    unchanged = copy.deepcopy(dict(player_data))
    if info["status"] in {"waiting", "blocked"}:
        return unchanged, info
    if info["status"] == "ready":
        if unchanged.get("habitat_feature") != SHADOW_FEATURE:
            unchanged, _, _ = apply_abandoned_house_pure(unchanged)
        return unchanged, info
    updated, ok, field = execute_field(unchanged, info["step"], random_random)
    if not ok:
        return unchanged, _decision("blocked", field["message"])
    if info["verb"] == "plant" and updated.get("habitat_feature") != SHADOW_FEATURE:
        updated, built, reason = apply_abandoned_house_pure(updated)
        if not built:
            return unchanged, _decision("blocked", reason)
    return updated, {**info, "field_result": {**field, "status": "executed"}}
