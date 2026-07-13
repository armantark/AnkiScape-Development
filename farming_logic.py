"""Pure persistent-state and action mechanics for Farming."""

from __future__ import annotations

import copy
import math
from typing import Any, Callable, Mapping, Optional

try:
    from .constants import EXP_TABLE, TREE_DATA, WOODCUTTING_AXE_DATA
    from .farming_data import (
        COMPOST_BIN_CAPACITY,
        COMPOST_TIERS,
        FARM_MINUTES_PER_ANSWER,
        FARMING_COMPOST_BINS,
        FARMING_COMPOST_BINS_BY_ID,
        FARMING_CROPS_BY_ID,
        FARMING_PATCHES,
        FARMING_PATCHES_BY_ID,
        FLOWER_PROTECTION,
        REGULAR_COMPOST_INPUTS,
        SAPLING_RECIPES,
        SUPERCOMPOST_INPUTS,
    )
    from .logic_pure import best_woodcutting_axe_pure, calculate_new_level, quest_completed_pure
except ImportError:  # pragma: no cover - flat imports used by tests
    from constants import EXP_TABLE, TREE_DATA, WOODCUTTING_AXE_DATA  # type: ignore
    from farming_data import (  # type: ignore
        COMPOST_BIN_CAPACITY,
        COMPOST_TIERS,
        FARM_MINUTES_PER_ANSWER,
        FARMING_COMPOST_BINS,
        FARMING_COMPOST_BINS_BY_ID,
        FARMING_CROPS_BY_ID,
        FARMING_PATCHES,
        FARMING_PATCHES_BY_ID,
        FLOWER_PROTECTION,
        REGULAR_COMPOST_INPUTS,
        SAPLING_RECIPES,
        SUPERCOMPOST_INPUTS,
    )
    from logic_pure import best_woodcutting_axe_pure, calculate_new_level, quest_completed_pure  # type: ignore


FIELD_STEP_KINDS = frozenset({"plant", "harvest", "check_health", "cure", "clear", "chop"})
FARM_EVENT_LOG_LIMIT = 200
MORYTANIA_MEDIUM_TASK_KEYS = ("morytania_medium", "medium_morytania_tasks")
FARM_COUNTER_DEFAULTS = {
    "plants": 0,
    "harvests": 0,
    "produce_harvested": 0,
    "health_checks": 0,
    "tree_health_checks": 0,
    "cures": 0,
    "clears": 0,
    "chops": 0,
    "full_runs": 0,
    "queue_steps_executed": 0,
    "queue_steps_skipped": 0,
    "saplings_started": 0,
    "compost_bins_filled": 0,
    "compost_bins_collected": 0,
}


def _int(value: Any, default: int = 0, minimum: int = 0) -> int:
    try:
        number = float(value)
        if not math.isfinite(number):
            return default
        return max(minimum, int(number))
    except (TypeError, ValueError, OverflowError):
        return default


def _number(value: Any, default: float = 0.0, minimum: float = 0.0) -> float:
    try:
        number = float(value)
        if not math.isfinite(number):
            return default
        return max(minimum, number)
    except (TypeError, ValueError, OverflowError):
        return default


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
        "watered": False,
        "health_checked": False,
        "stump": False,
        "produce_count": 0,
        "last_regrowth_at": 0,
        "next_regrowth_at": 0,
        "jade_state": None,
        "jade_prunes": 0,
        "plan": None,
    }


def _default_bin_record() -> dict[str, Any]:
    return {
        "status": "empty",
        "tier": None,
        "input_item": None,
        "filled_at": 0,
        "ready_at": 0,
        "amount": 0,
    }


def default_farming_state_pure() -> dict[str, Any]:
    return {
        "farm_clock_minutes": 0,
        "farm_patches": {patch.id: _default_patch_record() for patch in FARMING_PATCHES},
        "farm_compost_bins": {row.id: _default_bin_record() for row in FARMING_COMPOST_BINS},
        "farm_plans": {},
        "farm_queue": [],
        "farm_next_step_id": 1,
        "farm_sapling_jobs": [],
        "farm_next_sapling_job_id": 1,
        "farm_event_log": [],
        "farm_juju_active_until": 0,
        "farming_counters": dict(FARM_COUNTER_DEFAULTS),
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
    plan["protection_intent"] = bool(plan.get("protection_intent", False))
    plan["protection_paid"] = bool(plan.get("protection_paid", False))
    plan["fertile_soil_applied"] = bool(plan.get("fertile_soil_applied", False))
    return plan


def _sanitize_patch_record(raw: Any) -> dict[str, Any]:
    record = dict(raw) if isinstance(raw, Mapping) else {}
    defaults = _default_patch_record()
    for key, value in defaults.items():
        record.setdefault(key, copy.deepcopy(value))
    crop_id = record.get("crop_id")
    if not isinstance(crop_id, str) or crop_id not in FARMING_CROPS_BY_ID:
        crop_id = None
    last_crop_id = record.get("last_crop_id")
    record["crop_id"] = crop_id
    record["last_crop_id"] = last_crop_id if isinstance(last_crop_id, str) and last_crop_id in FARMING_CROPS_BY_ID else crop_id
    record["planted_at"] = _int(record.get("planted_at"))
    record["stage"] = _int(record.get("stage"))
    tier = record.get("compost_tier", "none")
    record["compost_tier"] = tier if tier in COMPOST_TIERS else "none"
    record["lives"] = _int(record.get("lives"))
    for key in ("diseased", "dead", "protected", "watered", "health_checked", "stump"):
        record[key] = bool(record.get(key, False))
    record["produce_count"] = _int(record.get("produce_count"))
    record["last_regrowth_at"] = _int(record.get("last_regrowth_at"))
    record["next_regrowth_at"] = _int(record.get("next_regrowth_at"))
    record["jade_state"] = record.get("jade_state") if record.get("jade_state") in {None, "prunable", "wild", "killed"} else None
    record["jade_prunes"] = _int(record.get("jade_prunes"))
    record["plan"] = _sanitize_plan(record.get("plan"))
    if crop_id is None:
        for key in ("diseased", "dead", "protected", "watered", "health_checked", "stump"):
            record[key] = False
        record["stage"] = 0
        record["lives"] = 0
        record["produce_count"] = 0
        record["next_regrowth_at"] = 0
        record["jade_state"] = None
        record["jade_prunes"] = 0
    return record


def _sanitize_bin_record(raw: Any) -> dict[str, Any]:
    record = dict(raw) if isinstance(raw, Mapping) else {}
    for key, value in _default_bin_record().items():
        record.setdefault(key, value)
    status = record.get("status")
    record["status"] = status if status in {"empty", "filling", "ready"} else "empty"
    tier = record.get("tier")
    record["tier"] = tier if tier in {"compost", "supercompost"} else None
    record["input_item"] = record.get("input_item") if isinstance(record.get("input_item"), str) else None
    for key in ("filled_at", "ready_at", "amount"):
        record[key] = _int(record.get(key))
    if record["status"] == "empty" or record["tier"] is None:
        record.update(_default_bin_record())
    return record


def sanitize_farming_state_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    defaults = default_farming_state_pure()
    raw_patches = player_data.get("farm_patches")
    patches: dict[str, Any] = dict(raw_patches) if isinstance(raw_patches, Mapping) else {}
    for patch in FARMING_PATCHES:
        patches[patch.id] = _sanitize_patch_record(patches.get(patch.id))

    raw_bins = player_data.get("farm_compost_bins")
    bins: dict[str, Any] = dict(raw_bins) if isinstance(raw_bins, Mapping) else {}
    for row in FARMING_COMPOST_BINS:
        bins[row.id] = _sanitize_bin_record(bins.get(row.id))

    raw_plans = player_data.get("farm_plans")
    plans: dict[str, Any] = dict(raw_plans) if isinstance(raw_plans, Mapping) else {}
    for patch_id in list(plans):
        clean_plan = _sanitize_plan(plans[patch_id])
        if clean_plan is None:
            plans.pop(patch_id, None)
        else:
            plans[patch_id] = clean_plan
    for patch_id, record in patches.items():
        if patch_id in FARMING_PATCHES_BY_ID and isinstance(record, Mapping):
            plan = _sanitize_plan(plans.get(patch_id)) or _sanitize_plan(record.get("plan"))
            record["plan"] = plan
            if plan is not None:
                plans[patch_id] = copy.deepcopy(plan)

    raw_queue = player_data.get("farm_queue")
    queue: list[dict[str, Any]] = []
    if isinstance(raw_queue, list):
        for raw_step in raw_queue:
            if not isinstance(raw_step, Mapping):
                continue
            step = dict(raw_step)
            if not isinstance(step.get("id"), str) or not step["id"]:
                continue
            if not isinstance(step.get("kind"), str):
                continue
            queue.append(step)
    highest_step_id = max(
        (_int(step["id"].removeprefix("farm_step_")) for step in queue if step["id"].startswith("farm_step_")),
        default=0,
    )

    raw_jobs = player_data.get("farm_sapling_jobs")
    jobs: list[dict[str, Any]] = []
    if isinstance(raw_jobs, list):
        for raw_job in raw_jobs:
            if not isinstance(raw_job, Mapping):
                continue
            job = dict(raw_job)
            if not isinstance(job.get("id"), str) or not isinstance(job.get("sapling_item"), str):
                continue
            if not isinstance(job.get("seedling_item"), str):
                continue
            job["amount"] = _int(job.get("amount"), minimum=1)
            job["ready_at"] = _int(job.get("ready_at"))
            jobs.append(job)
    highest_job_id = max(
        (_int(job["id"].removeprefix("farm_sapling_")) for job in jobs if job["id"].startswith("farm_sapling_")),
        default=0,
    )

    raw_log = player_data.get("farm_event_log")
    event_log = [dict(row) for row in raw_log if isinstance(row, Mapping)][-FARM_EVENT_LOG_LIMIT:] if isinstance(raw_log, list) else []
    raw_counters = player_data.get("farming_counters")
    counters = dict(raw_counters) if isinstance(raw_counters, Mapping) else {}
    for key, value in FARM_COUNTER_DEFAULTS.items():
        counters[key] = _int(counters.get(key, value))

    return {
        "farming_exp": _number(player_data.get("farming_exp", 0.0)),
        "farming_level": _int(player_data.get("farming_level", 1), default=1, minimum=1),
        "farm_clock_minutes": _int(player_data.get("farm_clock_minutes", defaults["farm_clock_minutes"])),
        "farm_patches": patches,
        "farm_compost_bins": bins,
        "farm_plans": plans,
        "farm_queue": queue,
        "farm_next_step_id": max(
            highest_step_id + 1,
            _int(player_data.get("farm_next_step_id", 1), default=1, minimum=1),
        ),
        "farm_sapling_jobs": jobs,
        "farm_next_sapling_job_id": max(
            highest_job_id + 1,
            _int(player_data.get("farm_next_sapling_job_id", 1), default=1, minimum=1),
        ),
        "farm_event_log": event_log,
        "farm_juju_active_until": _int(player_data.get("farm_juju_active_until", defaults["farm_juju_active_until"])),
        "farming_counters": counters,
    }


def _copy_with_farm_state(player_data: Mapping[str, Any]) -> dict[str, Any]:
    updated = dict(player_data)
    updated.update(sanitize_farming_state_pure(updated))
    inventory = updated.get("inventory")
    updated["inventory"] = dict(inventory) if isinstance(inventory, Mapping) else {}
    return updated


def _log(updated: dict[str, Any], event: str, message: str, **details: Any) -> None:
    row = {"clock": updated["farm_clock_minutes"], "event": event, "message": message}
    row.update(details)
    updated["farm_event_log"].append(row)
    if len(updated["farm_event_log"]) > FARM_EVENT_LOG_LIMIT:
        del updated["farm_event_log"][:-FARM_EVENT_LOG_LIMIT]


def _increment(updated: dict[str, Any], key: str, amount: int = 1) -> None:
    counters = updated["farming_counters"]
    counters[key] = _int(counters.get(key)) + amount


def _award_xp(updated: dict[str, Any], skill: str, amount: float) -> None:
    if amount <= 0:
        return
    exp_key = f"{skill}_exp"
    level_key = f"{skill}_level"
    updated[exp_key] = _number(updated.get(exp_key)) + amount
    current = _int(updated.get(level_key, 1), default=1, minimum=1)
    updated[level_key] = calculate_new_level(updated[exp_key], current, EXP_TABLE)


def _quest_completed(player_data: Mapping[str, Any], quest_id: str) -> bool:
    return quest_completed_pure(player_data, quest_id)


def _flag_enabled(player_data: Mapping[str, Any], key: str, *collections: str) -> bool:
    for collection_key in collections:
        collection = player_data.get(collection_key)
        if isinstance(collection, Mapping) and bool(collection.get(key)):
            return True
        if isinstance(collection, (list, tuple, set, frozenset)) and key in collection:
            return True
    return False


def farming_access_gate_allows_pure(player_data: Mapping[str, Any], gate: Any) -> bool:
    if gate is None:
        return True
    if gate.kind == "quest":
        return bool(gate.key and _quest_completed(player_data, gate.key))
    if gate.kind == "skill":
        return _int(player_data.get(f"{gate.key}_level", 1), default=1, minimum=1) >= gate.minimum
    if gate.kind == "region":
        if _flag_enabled(player_data, str(gate.key), "unlocked_regions", "region_access"):
            return True
        return gate.key == "morytania" and _quest_completed(player_data, "priest_in_peril")
    if gate.kind == "all":
        return all(farming_access_gate_allows_pure(player_data, child) for child in gate.gates)
    return False


def _task_completed(player_data: Mapping[str, Any], keys: tuple[str, ...]) -> bool:
    return any(_flag_enabled(player_data, key, "completed_task_sets", "task_sets", "completed_tasks") for key in keys)


def _is_mature(record: Mapping[str, Any], crop: Any) -> bool:
    return bool(crop.stages is not None and _int(record.get("stage", 0)) >= crop.stages and not record.get("dead"))


def _flower_protected(updated: Mapping[str, Any], patch_id: str, crop_id: str) -> bool:
    patch = FARMING_PATCHES_BY_ID[patch_id]
    for other in FARMING_PATCHES:
        if other.complex_id != patch.complex_id or other.patch_type != "flower":
            continue
        record = updated["farm_patches"].get(other.id, {})
        flower_id = record.get("crop_id")
        flower = FARMING_CROPS_BY_ID.get(flower_id)
        if flower and _is_mature(record, flower) and crop_id in FLOWER_PROTECTION.get(flower_id, ()):
            return True
    return False


def _disease_exempt(updated: Mapping[str, Any], patch_id: str, record: Mapping[str, Any], crop: Any) -> bool:
    patch = FARMING_PATCHES_BY_ID[patch_id]
    return bool(
        record.get("protected")
        or crop.disease_immune
        or patch.disease_free
        or (crop.patch_type == "mushroom" and _task_completed(updated, MORYTANIA_MEDIUM_TASK_KEYS))
        or (crop.disease_slots is not None and crop.disease_slots <= 0)
        or _flower_protected(updated, patch_id, crop.id)
    )


def _random_int_inclusive(random_random: Callable[[], float], low: int, high: int) -> int:
    roll = max(0.0, min(_number(random_random()), math.nextafter(1.0, 0.0)))
    return low + int(roll * (high - low + 1))


def _process_patch_boundaries(updated: dict[str, Any], patch_id: str, random_random: Callable[[], float]) -> None:
    record = updated["farm_patches"][patch_id]
    crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
    if crop is None or crop.stages is None or crop.stage_minutes is None or crop.stage_minutes <= 0:
        return
    clock = updated["farm_clock_minutes"]
    while not record.get("dead") and record["stage"] < crop.stages:
        boundary = record["planted_at"] + (record["stage"] + 1) * crop.stage_minutes
        if boundary > clock:
            break
        if record.get("diseased"):
            record["dead"] = True
            record["diseased"] = False
            _log(updated, "crop_died", f"{crop.display_name} died at {FARMING_PATCHES_BY_ID[patch_id].display_name}.", patch_id=patch_id, crop_id=crop.id)
            break
        record["stage"] += 1
        if record["stage"] == crop.stages:
            record["produce_count"] = crop.fixed_yield or 0
            record["last_regrowth_at"] = boundary
            if crop.regrowth_range_minutes:
                record["next_regrowth_at"] = boundary + _random_int_inclusive(random_random, *crop.regrowth_range_minutes)
            if crop.id == "jade_vine":
                record["jade_state"] = "prunable"
                record["jade_prunes"] = 0
            _log(updated, "crop_ready", f"{crop.display_name} is ready.", patch_id=patch_id, crop_id=crop.id)
            break
        # The first completed growth stage is immune. Watering is recorded but
        # its exact multiplier/yield effect stays source-blocked by the ledger.
        if record["stage"] > 1 and not _disease_exempt(updated, patch_id, record, crop):
            tier = COMPOST_TIERS[record.get("compost_tier", "none")]
            disease_slots = math.floor(crop.disease_slots * tier.disease_factor)
            if random_random() < disease_slots / 128:
                record["diseased"] = True
                _log(updated, "crop_diseased", f"{crop.display_name} became diseased.", patch_id=patch_id, crop_id=crop.id)
                continue

    if not _is_mature(record, crop) or crop.fixed_yield is None or record.get("jade_state") in {"wild", "killed"}:
        return
    if crop.regrowth_range_minutes:
        while record["produce_count"] < crop.fixed_yield and record["next_regrowth_at"] and record["next_regrowth_at"] <= clock:
            record["produce_count"] += 1
            record["last_regrowth_at"] = record["next_regrowth_at"]
            record["next_regrowth_at"] += _random_int_inclusive(random_random, *crop.regrowth_range_minutes)
    elif crop.regrowth_minutes:
        while record["produce_count"] < crop.fixed_yield and record["last_regrowth_at"] + crop.regrowth_minutes <= clock:
            record["produce_count"] += 1
            record["last_regrowth_at"] += crop.regrowth_minutes


def _advance_one_farm_card(updated: dict[str, Any], random_random: Callable[[], float]) -> None:
    updated["farm_clock_minutes"] += FARM_MINUTES_PER_ANSWER
    ready_jobs = []
    pending_jobs = []
    for job in updated["farm_sapling_jobs"]:
        (ready_jobs if job["ready_at"] <= updated["farm_clock_minutes"] else pending_jobs).append(job)
    updated["farm_sapling_jobs"] = pending_jobs
    for job in ready_jobs:
        inventory = updated["inventory"]
        amount = min(job["amount"], _int(inventory.get(job["seedling_item"])))
        if amount:
            inventory[job["seedling_item"]] -= amount
            inventory[job["sapling_item"]] = _int(inventory.get(job["sapling_item"])) + amount
        _log(updated, "saplings_ready", f"{amount} {job['sapling_item']} matured.", amount=amount)
    for bin_id in FARMING_COMPOST_BINS_BY_ID:
        record = updated["farm_compost_bins"][bin_id]
        if record["status"] == "filling" and record["ready_at"] <= updated["farm_clock_minutes"]:
            record["status"] = "ready"
            _log(updated, "compost_ready", f"{FARMING_COMPOST_BINS_BY_ID[bin_id].display_name} is ready.", bin_id=bin_id)
    for patch_id in FARMING_PATCHES_BY_ID:
        _process_patch_boundaries(updated, patch_id, random_random)


def advance_farm_clock_pure(
    player_data: Mapping[str, Any],
    answered_cards: int = 1,
    random_random: Callable[[], float] = lambda: 1.0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    updated = _copy_with_farm_state(player_data)
    cards = _int(answered_cards)
    events: list[dict[str, Any]] = []
    for _ in range(cards):
        _advance_one_farm_card(updated, random_random)
        events.extend(
            dict(row)
            for row in updated["farm_event_log"]
            if _int(row.get("clock")) == updated["farm_clock_minutes"]
        )
    return updated, {"minutes": cards * FARM_MINUTES_PER_ANSWER, "events": events}


def _patch_crop_for_step(updated: Mapping[str, Any], step: Mapping[str, Any]) -> tuple[Optional[str], Any, Any, Optional[str]]:
    patch_id = step.get("patch_id")
    if not isinstance(patch_id, str) or patch_id not in FARMING_PATCHES_BY_ID:
        return None, None, None, "unknown patch"
    patch = FARMING_PATCHES_BY_ID[patch_id]
    if not farming_access_gate_allows_pure(updated, patch.access_gate):
        return patch_id, patch, None, "patch access is locked"
    record = updated["farm_patches"][patch_id]
    crop_id = step.get("crop_id") if step.get("kind") == "plant" else record.get("crop_id")
    crop = FARMING_CROPS_BY_ID.get(crop_id)
    if crop is None:
        return patch_id, patch, None, "no valid crop"
    return patch_id, patch, crop, None


def _has_items(inventory: Mapping[str, Any], requirements: Mapping[str, int]) -> bool:
    return all(_int(inventory.get(item)) >= amount for item, amount in requirements.items())


def _consume(inventory: dict[str, Any], requirements: Mapping[str, int]) -> None:
    for item, amount in requirements.items():
        inventory[item] = _int(inventory.get(item)) - amount


def _reset_patch(record: dict[str, Any]) -> None:
    plan = copy.deepcopy(record.get("plan"))
    last_crop = record.get("crop_id") or record.get("last_crop_id")
    unknown = {key: value for key, value in record.items() if key not in _default_patch_record()}
    record.clear()
    record.update(_default_patch_record())
    record.update(unknown)
    record["plan"] = plan
    record["last_crop_id"] = last_crop


def _plant(updated: dict[str, Any], patch_id: str, patch: Any, crop: Any, step: Mapping[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if record.get("crop_id") is not None:
        return False, "patch is not empty", {}
    if not crop.runnable:
        return False, f"{crop.display_name} has source-blocked mechanics", {}
    if crop.patch_type != patch.patch_type or patch.crop_whitelist and crop.id not in patch.crop_whitelist:
        return False, "crop does not fit this patch", {}
    if _int(updated.get("farming_level", 1), default=1, minimum=1) < crop.level:
        return False, f"requires Farming level {crop.level}", {}
    plan = _sanitize_plan(updated["farm_plans"].get(patch_id)) or _sanitize_plan(record.get("plan"))
    matching_plan = plan if plan and plan["crop_id"] == crop.id else None
    fertile_soil_applied = bool(matching_plan and matching_plan.get("fertile_soil_applied"))
    tier_id = "supercompost" if fertile_soil_applied else step.get(
        "compost_tier", matching_plan.get("compost_tier") if matching_plan else "none"
    )
    if tier_id not in COMPOST_TIERS:
        return False, "unknown compost tier", {}
    tier = COMPOST_TIERS[tier_id]
    requirements = {crop.seed_item: crop.seeds}
    if tier.item and not fertile_soil_applied:
        requirements[tier.item] = requirements.get(tier.item, 0) + 1
    inventory = updated["inventory"]
    tool = "Spade" if crop.patch_type in {"tree", "fruit_tree", "calquat", "spirit_tree"} else "Seed dibber"
    for required_tool in ("Rake", tool):
        if _int(inventory.get(required_tool)) <= 0:
            return False, f"missing {required_tool}", {}
    if not _has_items(inventory, requirements):
        return False, "missing seeds or compost", {}
    _consume(inventory, requirements)
    inventory["Weeds"] = _int(inventory.get("Weeds")) + 3
    paid = bool(matching_plan and matching_plan.get("protection_paid"))
    if matching_plan:
        matching_plan["protection_paid"] = False
        matching_plan["fertile_soil_applied"] = False
        record["plan"] = copy.deepcopy(matching_plan)
        updated["farm_plans"][patch_id] = copy.deepcopy(matching_plan)
    record.update({
        "crop_id": crop.id,
        "last_crop_id": crop.id,
        "planted_at": updated["farm_clock_minutes"],
        "stage": 0,
        "compost_tier": tier_id,
        "lives": crop.base_lives + tier.extra_lives,
        "diseased": False,
        "dead": False,
        "protected": paid,
        "watered": crop.patch_type in {"allotment", "flower", "hops"} and any(_int(inventory.get(item)) > 0 for item in ("Watering can", "Watering can (8)")),
        "health_checked": False,
        "stump": False,
        "produce_count": 0,
        "last_regrowth_at": 0,
        "next_regrowth_at": 0,
        "jade_state": "prunable" if crop.id == "jade_vine" else None,
        "jade_prunes": 0,
    })
    xp = float(crop.planting_xp or 0.0) + tier.application_xp
    _award_xp(updated, "farming", xp)
    _increment(updated, "plants")
    return True, f"Planted {crop.display_name}.", {"farming_xp": xp, "outputs": {"Weeds": 3}}


def harvest_save_slots_pure(crop: Any, farming_level: int, magic_secateurs: bool) -> int:
    slots = min(crop.min_save_slots + max(0, farming_level - crop.level), crop.max_save_slots)
    return math.ceil(slots * (1.1 if magic_secateurs and crop.magic_secateurs_eligible else 1.0))


def roll_variable_harvest_count_pure(lives: int, save_slots: int, random_random: Callable[[], float]) -> int:
    remaining = max(0, lives)
    harvested = 0
    while remaining > 0:
        harvested += 1
        if random_random() >= min(256, max(0, save_slots)) / 256:
            remaining -= 1
    return harvested


def _juju_farming_active(updated: Mapping[str, Any]) -> bool:
    deadline = _int(updated.get("farm_juju_active_until"))
    # Five era-minutes is shorter than one six-minute review tick; preserve the
    # potion's next-action usefulness without extending it to a second review.
    return deadline > 0 and _int(updated.get("farm_clock_minutes")) <= deadline + 1


def _harvest(updated: dict[str, Any], patch_id: str, crop: Any, random_random: Callable[[], float]) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if _int(updated["inventory"].get("Spade")) <= 0:
        return False, "missing Spade", {}
    if not _is_mature(record, crop) or record.get("stump") or record.get("jade_state") in {"wild", "killed"}:
        return False, "crop is not ready", {}
    if crop.check_health_xp is not None and not record.get("health_checked"):
        return False, "check the crop's health first", {}
    if not crop.output_item or crop.harvest_xp is None:
        return False, "crop has no runnable harvest", {}
    if crop.id == "jade_vine":
        if _int(record.get("produce_count")) <= 0:
            return False, "no branches are ready", {}
        amount = 1
    elif crop.id == "limpwurt":
        level_roll = _random_int_inclusive(random_random, 0, max(0, _int(updated.get("farming_level")) - 1))
        amount = 3 + max(0, int((level_roll - 1) / 10))
    elif crop.fixed_yield is not None:
        amount = _int(record.get("produce_count"))
    else:
        secateurs = _int(updated["inventory"].get("Magic secateurs")) > 0
        slots = harvest_save_slots_pure(crop, updated["farming_level"], secateurs)
        amount = roll_variable_harvest_count_pure(_int(record.get("lives")), slots, random_random)
    if amount <= 0:
        return False, "no produce is ready", {}
    bonus = 0
    if crop.patch_type in {"herb", "vine_herb"} and _juju_farming_active(updated):
        bonus = sum(1 for _ in range(amount) if random_random() < (1.0 / 3.0))
    total_output = amount + bonus
    updated["inventory"][crop.output_item] = _int(updated["inventory"].get(crop.output_item)) + total_output
    xp = amount * crop.harvest_xp
    _award_xp(updated, "farming", xp)
    _increment(updated, "harvests")
    _increment(updated, "produce_harvested", total_output)
    if crop.id == "jade_vine":
        record["produce_count"] -= 1
        record["jade_prunes"] += 1
        record["last_regrowth_at"] = updated["farm_clock_minutes"]
        if record["jade_prunes"] >= 6:
            record["jade_state"] = "wild"
            record["produce_count"] = 0
            record["next_regrowth_at"] = 0
        elif crop.regrowth_range_minutes:
            record["next_regrowth_at"] = updated["farm_clock_minutes"] + _random_int_inclusive(random_random, *crop.regrowth_range_minutes)
    elif crop.regrowth_minutes or crop.regrowth_range_minutes:
        record["produce_count"] = 0
        record["last_regrowth_at"] = updated["farm_clock_minutes"]
        if crop.regrowth_range_minutes:
            record["next_regrowth_at"] = updated["farm_clock_minutes"] + _random_int_inclusive(random_random, *crop.regrowth_range_minutes)
    else:
        _reset_patch(record)
    outputs = {crop.output_item: total_output}
    return True, f"Harvested {total_output} {crop.output_item}.", {"farming_xp": xp, "outputs": outputs, "juju_bonus": bonus}


def _check_health(updated: dict[str, Any], patch_id: str, crop: Any) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if not _is_mature(record, crop) or crop.check_health_xp is None or record.get("health_checked"):
        return False, "health cannot be checked", {}
    record["health_checked"] = True
    _award_xp(updated, "farming", crop.check_health_xp)
    _increment(updated, "health_checks")
    if crop.patch_type in {"tree", "fruit_tree", "calquat"}:
        _increment(updated, "tree_health_checks")
    return True, f"Checked the health of {crop.display_name}.", {"farming_xp": crop.check_health_xp}


def _cure(updated: dict[str, Any], patch_id: str, crop: Any) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if not record.get("diseased") or record.get("dead"):
        return False, "crop is not diseased", {}
    if _int(updated["inventory"].get("Plant cure")) <= 0:
        return False, "missing Plant cure", {}
    updated["inventory"]["Plant cure"] -= 1
    record["diseased"] = False
    _increment(updated, "cures")
    return True, f"Cured {crop.display_name}.", {"farming_xp": 0.0}


def _clear(updated: dict[str, Any], patch_id: str, crop: Any) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if _int(updated["inventory"].get("Spade")) <= 0:
        return False, "missing Spade", {}
    clearable_scarecrow = crop.id == "scarecrow"
    clearable_jade = crop.id == "jade_vine" and record.get("jade_state") == "killed"
    if not record.get("dead") and not record.get("stump") and not clearable_scarecrow and not clearable_jade:
        return False, "patch has no clearable crop or stump", {}
    outputs: dict[str, int] = {}
    if record.get("stump") and crop.root_item:
        updated["inventory"][crop.root_item] = _int(updated["inventory"].get(crop.root_item)) + 1
        outputs[crop.root_item] = 1
    if clearable_scarecrow:
        updated["inventory"]["Scarecrow"] = _int(updated["inventory"].get("Scarecrow")) + 1
        outputs["Scarecrow"] = 1
    if clearable_jade:
        updated["inventory"]["Jade vine seed"] = _int(updated["inventory"].get("Jade vine seed")) + 1
        outputs["Jade vine seed"] = 1
    _reset_patch(record)
    _increment(updated, "clears")
    return True, f"Cleared {FARMING_PATCHES_BY_ID[patch_id].display_name}.", {"outputs": outputs}


def _chop(updated: dict[str, Any], patch_id: str, crop: Any) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if crop.id == "jade_vine":
        if record.get("jade_state") != "wild":
            return False, "jade vine is not wild", {}
        record["jade_state"] = "killed"
        _increment(updated, "chops")
        return True, "Killed the wild jade vine.", {"outputs": {}}
    if crop.patch_type != "tree" or not _is_mature(record, crop) or record.get("stump"):
        return False, "tree is not ready to chop", {}
    if crop.check_health_xp is not None and not record.get("health_checked"):
        return False, "check the tree's health first", {}
    target = TREE_DATA.get(crop.tree_id)
    if not isinstance(target, Mapping):
        return False, "tree has no Woodcutting target", {}
    axe = best_woodcutting_axe_pure(
        _int(updated.get("woodcutting_level", 1), default=1, minimum=1),
        updated["inventory"],
        updated.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    )
    if axe is None:
        return False, "no usable hatchet", {}
    if _int(updated.get("woodcutting_level", 1), default=1, minimum=1) < _int(target.get("level", 1), default=1, minimum=1):
        return False, f"requires Woodcutting level {target.get('level', 1)}", {}
    output = target.get("output_item")
    if not isinstance(output, str):
        return False, "tree has no log output", {}
    updated["inventory"][output] = _int(updated["inventory"].get(output)) + 1
    xp = _number(target.get("exp"))
    _award_xp(updated, "woodcutting", xp)
    record["stump"] = True
    _increment(updated, "chops")
    return True, f"Chopped {crop.display_name}.", {"woodcutting_xp": xp, "outputs": {output: 1}}


def _execute_farm_field_step_in_place(
    updated: dict[str, Any],
    step: Mapping[str, Any],
    random_random: Callable[[], float],
) -> tuple[bool, dict[str, Any]]:
    kind = step.get("kind")
    if kind not in FIELD_STEP_KINDS:
        return False, {"message": "unknown field action", "kind": kind}
    patch_id, patch, crop, error = _patch_crop_for_step(updated, step)
    if error:
        return False, {"message": error, "kind": kind}
    handlers = {
        "plant": lambda: _plant(updated, patch_id, patch, crop, step),
        "harvest": lambda: _harvest(updated, patch_id, crop, random_random),
        "check_health": lambda: _check_health(updated, patch_id, crop),
        "cure": lambda: _cure(updated, patch_id, crop),
        "clear": lambda: _clear(updated, patch_id, crop),
        "chop": lambda: _chop(updated, patch_id, crop),
    }
    ok, message, details = handlers[kind]()
    info = {"message": message, "kind": kind, "patch_id": patch_id, "crop_id": crop.id}
    info.update(details)
    if ok:
        _log(updated, "queue_step_executed", message, kind=kind, patch_id=patch_id, crop_id=crop.id)
    return ok, info


def execute_farm_field_step_pure(
    player_data: Mapping[str, Any],
    step: Mapping[str, Any],
    random_random: Callable[[], float] = lambda: 1.0,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    updated = _copy_with_farm_state(player_data)
    ok, info = _execute_farm_field_step_in_place(updated, step, random_random)
    return updated, ok, info


def farming_spell_target_locked_reasons_pure(
    player_data: Mapping[str, Any],
    spell_id: str,
    patch_id: Optional[str] = None,
) -> tuple[str, ...]:
    """Validate the patch-side transaction before a Farming spell spends runes."""

    target_id = patch_id if patch_id is not None else player_data.get("farming_spell_patch")
    if not isinstance(target_id, str) or target_id not in FARMING_PATCHES_BY_ID:
        return ("Choose a Farming patch",)
    updated = _copy_with_farm_state(player_data)
    patch = FARMING_PATCHES_BY_ID[target_id]
    if not farming_access_gate_allows_pure(updated, patch.access_gate):
        return ("Farming patch access is locked",)
    record = updated["farm_patches"][target_id]
    if spell_id == "cure_plant":
        crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
        if crop is None or record.get("dead") or not record.get("diseased"):
            return ("Choose a live diseased crop",)
        return ()
    if spell_id == "fertile_soil":
        if record.get("crop_id") is not None:
            return ("Choose an empty planned patch",)
        plan = _sanitize_plan(updated["farm_plans"].get(target_id)) or _sanitize_plan(record.get("plan"))
        crop = FARMING_CROPS_BY_ID.get(plan.get("crop_id")) if plan else None
        if crop is None or not crop.runnable:
            return ("Choose an empty patch with a runnable plan",)
        if crop.patch_type != patch.patch_type or patch.crop_whitelist and crop.id not in patch.crop_whitelist:
            return ("Planned crop does not fit the patch",)
        return ()
    return ("Unsupported Farming spell",)


def apply_farming_spell_pure(
    player_data: Mapping[str, Any],
    spell_id: str,
    patch_id: Optional[str] = None,
) -> tuple[dict[str, Any], bool, str]:
    """Apply Cure Plant or a one-shot Fertile Soil plan mutation atomically."""

    reasons = farming_spell_target_locked_reasons_pure(player_data, spell_id, patch_id)
    if reasons:
        return _copy_with_farm_state(player_data), False, reasons[0]
    updated = _copy_with_farm_state(player_data)
    target_id = patch_id if patch_id is not None else str(player_data.get("farming_spell_patch"))
    record = updated["farm_patches"][target_id]
    if spell_id == "cure_plant":
        crop = FARMING_CROPS_BY_ID[record["crop_id"]]
        record["diseased"] = False
        _increment(updated, "cures")
        message = f"Cured {crop.display_name} with Cure Plant."
        _log(updated, "farming_spell", message, spell_id=spell_id, patch_id=target_id, crop_id=crop.id)
        return updated, True, message

    plan = _sanitize_plan(updated["farm_plans"].get(target_id)) or _sanitize_plan(record.get("plan"))
    assert plan is not None
    plan["compost_tier"] = "supercompost"
    plan["fertile_soil_applied"] = True
    updated["farm_plans"][target_id] = copy.deepcopy(plan)
    record["plan"] = copy.deepcopy(plan)
    message = f"Fertile Soil prepared {FARMING_PATCHES_BY_ID[target_id].display_name}."
    _log(updated, "farming_spell", message, spell_id=spell_id, patch_id=target_id, crop_id=plan["crop_id"])
    return updated, True, message


def _step_id(updated: dict[str, Any]) -> str:
    value = updated["farm_next_step_id"]
    updated["farm_next_step_id"] = value + 1
    return f"farm_step_{value:08d}"


def add_farm_queue_step_pure(player_data: Mapping[str, Any], kind: str, patch_id: str, **details: Any) -> tuple[dict[str, Any], Optional[str], str]:
    updated = _copy_with_farm_state(player_data)
    if kind not in FIELD_STEP_KINDS:
        return updated, None, "unknown field action"
    patch = FARMING_PATCHES_BY_ID.get(patch_id)
    if patch is None:
        return updated, None, "unknown patch"
    if not farming_access_gate_allows_pure(updated, patch.access_gate):
        return updated, None, "patch access is locked"
    if kind == "plant":
        crop = FARMING_CROPS_BY_ID.get(details.get("crop_id"))
        if crop is None:
            return updated, None, "no valid crop"
        if not crop.runnable:
            return updated, None, f"{crop.display_name} has source-blocked mechanics"
    step_id = _step_id(updated)
    step = {"id": step_id, "kind": kind, "patch_id": patch_id}
    step.update(copy.deepcopy(details))
    updated["farm_queue"].append(step)
    return updated, step_id, "queued"


def remove_farm_queue_step_pure(player_data: Mapping[str, Any], step_id: str) -> tuple[dict[str, Any], bool]:
    updated = _copy_with_farm_state(player_data)
    before = len(updated["farm_queue"])
    updated["farm_queue"] = [step for step in updated["farm_queue"] if step.get("id") != step_id]
    return updated, len(updated["farm_queue"]) != before


def reorder_farm_queue_step_pure(player_data: Mapping[str, Any], step_id: str, new_index: int) -> tuple[dict[str, Any], bool]:
    updated = _copy_with_farm_state(player_data)
    index = next((i for i, step in enumerate(updated["farm_queue"]) if step.get("id") == step_id), None)
    if index is None:
        return updated, False
    step = updated["farm_queue"].pop(index)
    updated["farm_queue"].insert(max(0, min(_int(new_index), len(updated["farm_queue"]))), step)
    return updated, True


def _planned_patch_steps(updated: Mapping[str, Any], patch_id: str) -> tuple[list[str], Optional[dict[str, Any]], str]:
    patch = FARMING_PATCHES_BY_ID[patch_id]
    if not farming_access_gate_allows_pure(updated, patch.access_gate):
        return [], None, "patch access is locked"
    if any(step.get("patch_id") == patch_id for step in updated["farm_queue"]):
        return [], None, "patch already has queued work"
    record = updated["farm_patches"][patch_id]
    plan = _sanitize_plan(updated["farm_plans"].get(patch_id)) or _sanitize_plan(record.get("plan"))
    if plan is None:
        return [], None, "patch plan is not set"
    planned_crop = FARMING_CROPS_BY_ID[plan["crop_id"]]
    if not planned_crop.runnable:
        return [], None, f"{planned_crop.display_name} has source-blocked mechanics"
    crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
    if crop is None:
        return ["plant"], plan, "queued"
    if record.get("dead") or record.get("stump") or record.get("jade_state") == "killed" or crop.id == "scarecrow":
        return ["clear", "plant"], plan, "queued"
    if record.get("jade_state") == "wild":
        return ["chop", "clear", "plant"], plan, "queued"
    if record.get("diseased"):
        return ["cure"], plan, "queued"
    if not _is_mature(record, crop):
        return [], plan, "crop is still growing"
    if crop.patch_type == "tree":
        kinds = [] if record.get("health_checked") else ["check_health"]
        kinds.extend(("chop", "clear", "plant"))
        return kinds, plan, "queued"
    kinds: list[str] = []
    if crop.check_health_xp is not None and not record.get("health_checked"):
        kinds.append("check_health")
    produce_count = _int(record.get("produce_count"))
    if crop.id == "jade_vine":
        kinds.extend("harvest" for _ in range(produce_count))
        return kinds, plan, "queued" if kinds else "no produce is ready"
    if crop.regrowth_minutes or crop.regrowth_range_minutes:
        if produce_count > 0:
            kinds.append("harvest")
        return kinds, plan, "queued" if kinds else "no produce is ready"
    kinds.extend(("harvest", "plant"))
    return kinds, plan, "queued"


def _append_planned_steps(updated: dict[str, Any], patch_id: str, kinds: list[str], plan: dict[str, Any]) -> list[str]:
    ids = []
    for kind in kinds:
        step_id = _step_id(updated)
        step = {"id": step_id, "kind": kind, "patch_id": patch_id}
        if kind == "plant":
            step.update({"crop_id": plan["crop_id"], "compost_tier": plan["compost_tier"]})
        updated["farm_queue"].append(step)
        ids.append(step_id)
    return ids


def queue_harvest_and_replant_same_pure(player_data: Mapping[str, Any], patch_id: str) -> tuple[dict[str, Any], tuple[str, ...], str]:
    updated = _copy_with_farm_state(player_data)
    if patch_id not in FARMING_PATCHES_BY_ID:
        return updated, (), "unknown patch"
    kinds, plan, message = _planned_patch_steps(updated, patch_id)
    if not kinds or plan is None:
        return updated, (), message
    return updated, tuple(_append_planned_steps(updated, patch_id, kinds, plan)), "queued"


def queue_full_run_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
    updated = _copy_with_farm_state(player_data)
    ids: list[str] = []
    for patch in FARMING_PATCHES:
        kinds, plan, _message = _planned_patch_steps(updated, patch.id)
        if kinds and plan is not None:
            ids.extend(_append_planned_steps(updated, patch.id, kinds, plan))
    if ids:
        _increment(updated, "full_runs")
    return updated, tuple(ids)


def _consume_next_farm_queue_step_in_place(
    updated: dict[str, Any],
    random_random: Callable[[], float],
) -> tuple[bool, dict[str, Any]]:
    if not updated["farm_queue"]:
        return False, {"status": "empty", "message": "farm queue is empty"}
    step = updated["farm_queue"].pop(0)
    ok, info = _execute_farm_field_step_in_place(updated, step, random_random)
    info["step_id"] = step["id"]
    info["status"] = "executed" if ok else "skipped"
    if ok:
        _increment(updated, "queue_steps_executed")
    else:
        _increment(updated, "queue_steps_skipped")
        _log(updated, "queue_step_skipped", f"Skipped {step.get('kind')}: {info['message']}.", step_id=step["id"], kind=step.get("kind"), patch_id=step.get("patch_id"))
    return True, info


def consume_next_farm_queue_step_pure(
    player_data: Mapping[str, Any],
    random_random: Callable[[], float] = lambda: 1.0,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    updated = _copy_with_farm_state(player_data)
    consumed, info = _consume_next_farm_queue_step_in_place(updated, random_random)
    return updated, consumed, info


def apply_farming_review_with_queue_pure(
    player_data: Mapping[str, Any],
    random_random: Callable[[], float] = lambda: 1.0,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Advance one successful review and consume its queued detour with one copy."""

    updated = _copy_with_farm_state(player_data)
    queue = updated["farm_queue"]
    cure_first = bool(queue and queue[0].get("kind") == "cure")
    if cure_first:
        consumed, info = _consume_next_farm_queue_step_in_place(updated, random_random)
        _advance_one_farm_card(updated, random_random)
    else:
        _advance_one_farm_card(updated, random_random)
        consumed, info = _consume_next_farm_queue_step_in_place(updated, random_random)
    return updated, consumed, info


def set_farm_plan_pure(
    player_data: Mapping[str, Any],
    patch_id: str,
    crop_id: str,
    compost_tier: str = "none",
    protection_intent: bool = False,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    patch = FARMING_PATCHES_BY_ID.get(patch_id)
    crop = FARMING_CROPS_BY_ID.get(crop_id)
    if patch is None or crop is None or compost_tier not in COMPOST_TIERS:
        return updated, False, "unknown plan value"
    if not farming_access_gate_allows_pure(updated, patch.access_gate):
        return updated, False, "patch access is locked"
    if not crop.runnable:
        return updated, False, f"{crop.display_name} has source-blocked mechanics"
    if crop.patch_type != patch.patch_type or patch.crop_whitelist and crop.id not in patch.crop_whitelist:
        return updated, False, "crop does not fit this patch"
    existing_plan = _sanitize_plan(updated["farm_plans"].get(patch_id)) or _sanitize_plan(updated["farm_patches"][patch_id].get("plan"))
    if existing_plan and existing_plan.get("protection_paid") and existing_plan["crop_id"] != crop_id:
        return updated, False, "paid protection is tied to the existing planned crop"
    plan = {
        "crop_id": crop_id,
        "compost_tier": compost_tier,
        "protection_intent": bool(protection_intent),
        "protection_paid": bool(existing_plan and existing_plan["crop_id"] == crop_id and existing_plan.get("protection_paid")),
        "fertile_soil_applied": bool(existing_plan and existing_plan["crop_id"] == crop_id and existing_plan.get("fertile_soil_applied")),
    }
    updated["farm_plans"][patch_id] = copy.deepcopy(plan)
    updated["farm_patches"][patch_id]["plan"] = copy.deepcopy(plan)
    return updated, True, "plan saved"


def pay_farming_protection_pure(player_data: Mapping[str, Any], patch_id: str) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    patch = FARMING_PATCHES_BY_ID.get(patch_id)
    if patch is None:
        return updated, False, "unknown patch"
    if not farming_access_gate_allows_pure(updated, patch.access_gate):
        return updated, False, "patch access is locked"
    record = updated["farm_patches"][patch_id]
    plan = _sanitize_plan(updated["farm_plans"].get(patch_id)) or _sanitize_plan(record.get("plan"))
    crop_id = record.get("crop_id") or (plan and plan.get("crop_id"))
    crop = FARMING_CROPS_BY_ID.get(crop_id)
    if crop is None or crop.protection is None:
        return updated, False, "crop has no farmer protection payment"
    if not crop.runnable:
        return updated, False, f"{crop.display_name} has source-blocked mechanics"
    if record.get("crop_id"):
        if record.get("crop_id") != crop.id:
            return updated, False, "protection crop does not match"
        if record.get("diseased"):
            return updated, False, "cure the diseased crop before paying protection"
        if record.get("protected"):
            return updated, True, "protection already paid"
    elif plan and plan.get("protection_paid"):
        return updated, True, "protection already paid"
    requirements = dict(crop.protection.items)
    if not _has_items(updated["inventory"], requirements):
        return updated, False, "missing protection payment"
    _consume(updated["inventory"], requirements)
    if record.get("crop_id") == crop.id:
        record["protected"] = True
    elif plan and plan.get("crop_id") == crop.id:
        plan["protection_paid"] = True
        record["plan"] = copy.deepcopy(plan)
        updated["farm_plans"][patch_id] = copy.deepcopy(plan)
    return updated, True, "protection paid"


def activate_juju_farming_potion_pure(player_data: Mapping[str, Any], item_name: str = "Juju farming potion (3)") -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    prefix = "Juju farming potion ("
    if not item_name.startswith(prefix) or not item_name.endswith(")"):
        return updated, False, "not a Juju farming potion"
    try:
        doses = int(item_name[len(prefix):-1])
    except ValueError:
        return updated, False, "not a Juju farming potion"
    if doses < 1 or doses > 4 or _int(updated["inventory"].get(item_name)) <= 0:
        return updated, False, "missing Juju farming potion"
    updated["inventory"][item_name] -= 1
    leaves = f"Juju farming potion ({doses - 1})" if doses > 1 else "Vial"
    updated["inventory"][leaves] = _int(updated["inventory"].get(leaves)) + 1
    updated["farm_juju_active_until"] = updated["farm_clock_minutes"] + 5
    return updated, True, "Juju farming potion active for 5 farm minutes"


def make_saplings_pure(player_data: Mapping[str, Any], crop_id: str, amount: int = 28) -> tuple[dict[str, Any], int, str]:
    updated = _copy_with_farm_state(player_data)
    recipe = SAPLING_RECIPES.get(crop_id)
    crop = FARMING_CROPS_BY_ID.get(crop_id)
    if recipe is None or crop is None:
        return updated, 0, "unknown sapling"
    if not crop.runnable:
        return updated, 0, f"{crop.display_name} has source-blocked mechanics"
    seed, seedling, sapling = recipe
    inventory = updated["inventory"]
    if _int(inventory.get("Gardening trowel")) <= 0:
        return updated, 0, "missing Gardening trowel"
    if not any(_int(inventory.get(item)) > 0 for item in ("Watering can", "Watering can (8)")):
        return updated, 0, "missing Watering can"
    count = min(28, _int(amount), _int(inventory.get(seed)), _int(inventory.get("Plant pot")))
    if count <= 0:
        return updated, 0, "missing seed or Plant pot"
    inventory[seed] -= count
    inventory["Plant pot"] -= count
    inventory[seedling] = _int(inventory.get(seedling)) + count
    job_id_value = updated["farm_next_sapling_job_id"]
    updated["farm_next_sapling_job_id"] = job_id_value + 1
    updated["farm_sapling_jobs"].append({
        "id": f"farm_sapling_{job_id_value:08d}",
        "crop_id": crop_id,
        "seedling_item": seedling,
        "sapling_item": sapling,
        "amount": count,
        "ready_at": updated["farm_clock_minutes"] + 5,
    })
    _increment(updated, "saplings_started", count)
    return updated, count, "saplings started"


def fill_compost_bin_pure(player_data: Mapping[str, Any], bin_id: str, input_item: str, random_random: Callable[[], float] = lambda: 0.5) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    definition = FARMING_COMPOST_BINS_BY_ID.get(bin_id)
    if definition is None:
        return updated, False, "unknown compost bin"
    if not farming_access_gate_allows_pure(updated, definition.access_gate):
        return updated, False, "compost bin access is locked"
    record = updated["farm_compost_bins"][bin_id]
    if record["status"] != "empty":
        return updated, False, "compost bin is not empty"
    if input_item in SUPERCOMPOST_INPUTS:
        tier_id = "supercompost"
    elif input_item in REGULAR_COMPOST_INPUTS:
        tier_id = "compost"
    else:
        return updated, False, "item is not a source-settled compost input"
    if _int(updated["inventory"].get(input_item)) < COMPOST_BIN_CAPACITY:
        return updated, False, f"requires {COMPOST_BIN_CAPACITY} {input_item}"
    updated["inventory"][input_item] -= COMPOST_BIN_CAPACITY
    tier = COMPOST_TIERS[tier_id]
    duration = _random_int_inclusive(random_random, *tier.source_range_minutes) if tier.source_range_minutes else tier.maturation_minutes
    record.update({
        "status": "filling",
        "tier": tier_id,
        "input_item": input_item,
        "filled_at": updated["farm_clock_minutes"],
        "ready_at": updated["farm_clock_minutes"] + duration,
        "amount": COMPOST_BIN_CAPACITY,
    })
    _increment(updated, "compost_bins_filled")
    return updated, True, "compost bin filled"


def collect_compost_bin_pure(player_data: Mapping[str, Any], bin_id: str) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    definition = FARMING_COMPOST_BINS_BY_ID.get(bin_id)
    if definition is None:
        return updated, False, "unknown compost bin"
    if not farming_access_gate_allows_pure(updated, definition.access_gate):
        return updated, False, "compost bin access is locked"
    record = updated["farm_compost_bins"][bin_id]
    if record["status"] != "ready" or record["tier"] not in {"compost", "supercompost"}:
        return updated, False, "compost is not ready"
    amount = min(COMPOST_BIN_CAPACITY, _int(record.get("amount")))
    if _int(updated["inventory"].get("Bucket")) < amount:
        return updated, False, f"requires {amount} buckets"
    output = COMPOST_TIERS[record["tier"]].item
    updated["inventory"]["Bucket"] -= amount
    updated["inventory"][output] = _int(updated["inventory"].get(output)) + amount
    record.clear()
    record.update(_default_bin_record())
    _increment(updated, "compost_bins_collected")
    return updated, True, f"collected {amount} {output}"


def farming_status_projection_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_farming_state_pure(player_data)
    ready = diseased = dead = active = 0
    rows = []
    for patch in FARMING_PATCHES:
        record = state["farm_patches"][patch.id]
        crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
        if crop is None:
            continue
        active += 1
        is_ready = _is_mature(record, crop)
        ready += int(is_ready)
        diseased += int(record.get("diseased", False))
        dead += int(record.get("dead", False))
        rows.append({
            "patch_id": patch.id,
            "crop_id": crop.id,
            "stage": record["stage"],
            "stages": crop.stages,
            "ready": is_ready,
            "diseased": record["diseased"],
            "dead": record["dead"],
        })
    return {
        "clock_minutes": state["farm_clock_minutes"],
        "active": active,
        "ready": ready,
        "diseased": diseased,
        "dead": dead,
        "queue_length": len(state["farm_queue"]),
        "patches": rows,
    }


def _display_location(complex_id: str) -> str:
    overrides = {
        "falador": "South Falador",
        "phasmatys": "Port Phasmatys",
        "catherby": "North Catherby",
        "ardougne": "North Ardougne",
        "south_ardougne": "South Ardougne",
        "gnome_stronghold": "Tree Gnome Stronghold",
        "gnome_village": "Tree Gnome Village",
        "habitat": "Herblore Habitat",
        "spirit_tree": "Spirit tree patches",
        "tai_bwo": "Tai Bwo Wannai",
        "al_kharid": "Al Kharid",
    }
    return overrides.get(complex_id, complex_id.replace("_", " ").title())


def _access_reason(gate: Any) -> str:
    if gate is None:
        return ""
    if gate.kind == "quest":
        return f"Requires {str(gate.key).replace('_', ' ').title()}."
    if gate.kind == "skill":
        return f"Requires {str(gate.key).replace('_', ' ').title()} level {gate.minimum}."
    if gate.kind == "region":
        return f"Requires access to {str(gate.key).replace('_', ' ').title()}."
    if gate.kind == "all":
        return " ".join(reason for reason in (_access_reason(child) for child in gate.gates) if reason)
    return "This patch is locked."


def _missing_items_reason(inventory: Mapping[str, Any], requirements: Mapping[str, int]) -> str:
    missing = [
        f"{amount} {item} ({_int(inventory.get(item))} in Bank)"
        for item, amount in requirements.items()
        if _int(inventory.get(item)) < amount
    ]
    return f"Needs {', '.join(missing)}." if missing else ""


def _patch_status_view(state: Mapping[str, Any], patch: Any, record: Mapping[str, Any], crop: Any) -> tuple[str, str, int]:
    if crop is None:
        return "empty", "Empty", 10**9
    if record.get("dead"):
        return "dead", "Dead — queue clearing", 0
    if record.get("diseased"):
        return "diseased", "Diseased — queue a cure", 0
    if record.get("stump"):
        return "stump", "Stump — queue clearing", 0
    if crop.id == "jade_vine" and record.get("jade_state") == "wild":
        return "ready", "Ready to chop", 0
    mature = _is_mature(record, crop)
    if mature:
        if crop.check_health_xp is not None and not record.get("health_checked"):
            return "ready", "Health check ready", 0
        if crop.patch_type == "tree":
            return "ready", "Ready to chop", 0
        return "ready", "Ready now", 0
    stages = crop.stages or 0
    stage = _int(record.get("stage"))
    if crop.stage_minutes:
        boundary = _int(record.get("planted_at")) + (stage + 1) * crop.stage_minutes
        reviews = max(1, math.ceil(max(0, boundary - _int(state.get("farm_clock_minutes"))) / FARM_MINUTES_PER_ANSWER))
        return "growing", f"Growing · stage {stage + 1}/{stages} · next stage in about {reviews} reviews", reviews
    return "growing", f"Growing · stage {stage + 1}/{stages}", 10**8


def _queue_step_label(step: Mapping[str, Any]) -> str:
    patch = FARMING_PATCHES_BY_ID.get(step.get("patch_id"))
    verb = str(step.get("kind", "work")).replace("_", " ").title()
    crop = FARMING_CROPS_BY_ID.get(step.get("crop_id"))
    crop_suffix = f" {crop.display_name}" if crop is not None and step.get("kind") == "plant" else ""
    return f"{verb}{crop_suffix} · {patch.display_name if patch else 'Unknown patch'}"


def farming_frontend_projection_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Return presentation-ready Farming state; Qt only renders this projection."""

    state = _copy_with_farm_state(player_data)
    inventory = state["inventory"]
    farming_level = _int(state.get("farming_level", 1), default=1, minimum=1)
    queued_patch_ids = {step.get("patch_id") for step in state["farm_queue"]}
    groups: dict[str, dict[str, Any]] = {}
    active = ready = urgent = 0
    compact_rows: list[dict[str, Any]] = []

    for patch in FARMING_PATCHES:
        record = state["farm_patches"][patch.id]
        crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
        status, status_label, reviews = _patch_status_view(state, patch, record, crop)
        access_allowed = farming_access_gate_allows_pure(state, patch.access_gate)
        access_reason = "" if access_allowed else _access_reason(patch.access_gate)
        plan = _sanitize_plan(state["farm_plans"].get(patch.id)) or _sanitize_plan(record.get("plan"))
        planned_crop = FARMING_CROPS_BY_ID.get(plan.get("crop_id")) if plan else None
        queued = sum(1 for step in state["farm_queue"] if step.get("patch_id") == patch.id)
        if crop is not None:
            active += 1
            ready += int(_is_mature(record, crop))
            urgent += int(status in {"diseased", "dead"})
            compact_rows.append({
                "patch_id": patch.id,
                "location_id": patch.complex_id,
                "location_name": _display_location(patch.complex_id),
                "patch_name": patch.display_name,
                "crop_name": crop.display_name,
                "status": status,
                "status_label": status_label,
                "reviews_to_transition": reviews,
            })

        crop_options = []
        for option in FARMING_CROPS_BY_ID.values():
            if not option.runnable or option.patch_type != patch.patch_type:
                continue
            if patch.crop_whitelist and option.id not in patch.crop_whitelist:
                continue
            reason = access_reason
            if not reason and farming_level < option.level:
                reason = f"Requires Farming level {option.level}."
            crop_options.append({
                "id": option.id,
                "label": option.display_name,
                "enabled": not reason,
                "locked_reason": reason,
            })

        primary_kind = None
        if crop is None:
            primary_kind = "plant" if plan else "choose_plan"
        elif status == "diseased":
            primary_kind = "cure"
        elif status in {"dead", "stump"}:
            primary_kind = "clear"
        elif status == "ready":
            if crop.check_health_xp is not None and not record.get("health_checked"):
                primary_kind = "check_health"
            elif crop.patch_type == "tree" or (crop.id == "jade_vine" and record.get("jade_state") == "wild"):
                primary_kind = "chop"
            else:
                primary_kind = "harvest"

        primary_reason = access_reason
        if not primary_reason and patch.id in queued_patch_ids and primary_kind not in {None, "choose_plan"}:
            primary_reason = "This patch already has queued work."
        if not primary_reason and primary_kind == "plant":
            requirements = {planned_crop.seed_item: planned_crop.seeds} if planned_crop else {}
            if plan and not plan.get("fertile_soil_applied") and plan.get("compost_tier") in COMPOST_TIERS:
                compost_item = COMPOST_TIERS[plan["compost_tier"]].item
                if compost_item:
                    requirements[compost_item] = requirements.get(compost_item, 0) + 1
            tool = "Spade" if planned_crop and planned_crop.patch_type in {"tree", "fruit_tree", "calquat", "spirit_tree"} else "Seed dibber"
            requirements.update({"Rake": 1, tool: 1})
            primary_reason = _missing_items_reason(inventory, requirements)
        elif not primary_reason and primary_kind == "cure":
            primary_reason = _missing_items_reason(inventory, {"Plant cure": 1})
        elif not primary_reason and primary_kind in {"harvest", "clear"}:
            primary_reason = _missing_items_reason(inventory, {"Spade": 1})

        primary_labels = {
            "choose_plan": "Choose a crop",
            "plant": "Queue plant",
            "cure": "Queue cure",
            "clear": "Queue clear",
            "check_health": "Queue health check",
            "chop": "Queue chop",
            "harvest": "Queue harvest",
        }
        primary_action = None if primary_kind is None else {
            "id": primary_kind,
            "label": primary_labels[primary_kind],
            "enabled": primary_kind == "choose_plan" or not primary_reason,
            "locked_reason": primary_reason,
        }

        shortcut_reason = access_reason
        if not shortcut_reason and status != "ready":
            shortcut_reason = "This crop is not ready."
        if not shortcut_reason and patch.id in queued_patch_ids:
            shortcut_reason = "This patch already has queued work."
        if not shortcut_reason and plan is not None:
            requirements = {FARMING_CROPS_BY_ID[plan["crop_id"]].seed_item: FARMING_CROPS_BY_ID[plan["crop_id"]].seeds}
            if not plan.get("fertile_soil_applied"):
                compost_item = COMPOST_TIERS[plan["compost_tier"]].item
                if compost_item:
                    requirements[compost_item] = requirements.get(compost_item, 0) + 1
            shortcut_reason = _missing_items_reason(inventory, requirements)

        protection = {"state": "Unavailable", "intent": bool(plan and plan.get("protection_intent")), "action": None}
        payment_crop = crop or planned_crop
        if crop is not None and (record.get("protected") or crop.disease_immune or patch.disease_free):
            protection["state"] = "Protected"
        elif plan and plan.get("protection_paid"):
            protection["state"] = "Protected"
        elif crop is not None and _flower_protected(state, patch.id, crop.id):
            protection["state"] = "Protected by nearby flowers"
        elif payment_crop is not None and payment_crop.protection is not None:
            payment_requirements = dict(payment_crop.protection.items)
            payment_reason = _missing_items_reason(inventory, payment_requirements)
            protection["state"] = "Protection not paid"
            protection["requirements"] = payment_requirements
            protection["action"] = {
                "id": "pay_protection",
                "label": "Pay now",
                "enabled": not payment_reason and access_allowed,
                "locked_reason": access_reason or payment_reason,
            }

        sapling = None
        sapling_crop = planned_crop if planned_crop and planned_crop.id in SAPLING_RECIPES else None
        if sapling_crop is not None:
            seed, _seedling, _sapling = SAPLING_RECIPES[sapling_crop.id]
            amount = min(28, _int(inventory.get(seed)), _int(inventory.get("Plant pot")))
            reason = _missing_items_reason(inventory, {seed: 1, "Plant pot": 1, "Gardening trowel": 1})
            if not reason and not any(_int(inventory.get(item)) > 0 for item in ("Watering can", "Watering can (8)")):
                reason = "Needs a Watering can in your Bank."
            sapling = {
                "crop_id": sapling_crop.id,
                "label": f"Make up to {amount} saplings" if amount else "Make saplings",
                "enabled": amount > 0 and not reason,
                "locked_reason": reason,
            }

        patch_view = {
            "patch_id": patch.id,
            "patch_name": patch.display_name,
            "patch_type": patch.patch_type.replace("_", " ").title(),
            "access_allowed": access_allowed,
            "access_reason": access_reason,
            "crop_id": crop.id if crop else None,
            "crop_name": crop.display_name if crop else "Empty",
            "status": status,
            "status_label": access_reason or status_label,
            "stage_label": status_label,
            "queued_count": queued,
            "current_compost": str(record.get("compost_tier", "none")).replace("_", " ").title(),
            "plan": {
                "crop_id": plan.get("crop_id") if plan else None,
                "crop_name": planned_crop.display_name if planned_crop else "No plan",
                "compost_tier": plan.get("compost_tier", "none") if plan else "none",
                "protection_intent": bool(plan and plan.get("protection_intent")),
            },
            "crop_options": tuple(crop_options),
            "compost_options": tuple({"id": tier_id, "label": tier_id.replace("_", " ").title(), "enabled": True, "locked_reason": ""} for tier_id in COMPOST_TIERS),
            "protection": protection,
            "primary_action": primary_action,
            "shortcut_action": {
                "id": "harvest_replant",
                "label": "Harvest and replant same",
                "enabled": plan is None or not shortcut_reason,
                "locked_reason": shortcut_reason,
                "needs_plan": plan is None,
            },
            "sapling_action": sapling,
        }
        group = groups.setdefault(patch.complex_id, {
            "location_id": patch.complex_id,
            "display_name": _display_location(patch.complex_id),
            "patches": [],
            "compost_bins": [],
        })
        group["patches"].append(patch_view)

    compost_inputs = tuple(sorted(REGULAR_COMPOST_INPUTS | SUPERCOMPOST_INPUTS))
    for definition in FARMING_COMPOST_BINS:
        group = groups.setdefault(definition.complex_id, {
            "location_id": definition.complex_id,
            "display_name": _display_location(definition.complex_id),
            "patches": [],
            "compost_bins": [],
        })
        record = state["farm_compost_bins"][definition.id]
        access_allowed = farming_access_gate_allows_pure(state, definition.access_gate)
        access_reason = "" if access_allowed else _access_reason(definition.access_gate)
        options = []
        for item in compost_inputs:
            reason = _missing_items_reason(inventory, {item: COMPOST_BIN_CAPACITY})
            options.append({"id": item, "label": f"{item} ({_int(inventory.get(item))})", "enabled": not reason, "locked_reason": reason})
        collect_reason = access_reason
        if not collect_reason and record["status"] != "ready":
            collect_reason = "Compost is not ready."
        if not collect_reason:
            collect_reason = _missing_items_reason(inventory, {"Bucket": _int(record.get("amount"))})
        group["compost_bins"].append({
            "bin_id": definition.id,
            "display_name": definition.display_name,
            "status": record["status"],
            "status_label": "Maturing" if record["status"] == "filling" else record["status"].title(),
            "input_options": tuple(options),
            "fill_enabled": access_allowed and record["status"] == "empty" and any(option["enabled"] for option in options),
            "fill_reason": access_reason or ("Compost bin is not empty." if record["status"] != "empty" else "Needs 15 suitable items in your Bank."),
            "collect_enabled": not collect_reason,
            "collect_reason": collect_reason,
        })

    ordered_groups = []
    for group in groups.values():
        group_active = sum(1 for row in group["patches"] if row["crop_id"])
        group_ready = sum(1 for row in group["patches"] if row["status"] == "ready")
        group_urgent = sum(1 for row in group["patches"] if row["status"] in {"diseased", "dead"})
        group["summary"] = f"{group_active} active · {group_ready} ready · {group_urgent} attention"
        group["open_by_default"] = bool(group_ready or group_urgent)
        group["patches"] = tuple(group["patches"])
        group["compost_bins"] = tuple(group["compost_bins"])
        ordered_groups.append(group)

    queue_rows = tuple({
        "step_id": step["id"],
        "label": _queue_step_label(step),
        "can_move_up": index > 0,
        "can_move_down": index + 1 < len(state["farm_queue"]),
    } for index, step in enumerate(state["farm_queue"]))
    preview_state, preview_ids = queue_full_run_pure(state)
    del preview_state
    compact_rows.sort(key=lambda row: (
        0 if row["status"] in {"diseased", "dead"} else 1 if row["status"] == "ready" else 2,
        row["reviews_to_transition"], row["location_name"], row["patch_name"],
    ))
    priority = "alert" if urgent else "ready" if ready else "queue" if queue_rows else "none"
    tooltip = (
        f"Farming — {urgent} patch{'es' if urgent != 1 else ''} need attention"
        if priority == "alert" else
        f"Farming — {ready} patch{'es' if ready != 1 else ''} ready"
        if priority == "ready" else
        f"Farming — {len(queue_rows)} queued step{'s' if len(queue_rows) != 1 else ''}"
        if priority == "queue" else "Farming — no patches need attention"
    )
    return {
        "level": farming_level,
        "xp": _number(state.get("farming_exp")),
        "active_count": active,
        "ready_count": ready,
        "urgent_count": urgent,
        "queued_count": len(queue_rows),
        "locations": tuple(ordered_groups),
        "queue": queue_rows,
        "full_run": {
            "enabled": bool(preview_ids),
            "count": len(preview_ids),
            "preview": f"{len(preview_ids)} steps ready to queue" if preview_ids else "No planned work is ready.",
            "locked_reason": "" if preview_ids else "No planned work is ready.",
        },
        "compact_rows": tuple(compact_rows),
        "hud": {
            "priority": priority,
            "urgent_count": urgent,
            "ready_count": ready,
            "queue_count": len(queue_rows),
            "tooltip": tooltip,
        },
    }


def apply_farming_frontend_action_pure(
    player_data: Mapping[str, Any], action_id: str, payload: Optional[Mapping[str, Any]] = None
) -> tuple[dict[str, Any], bool, str]:
    """Unified pure mutation boundary used by the Farming Qt controller."""

    data = dict(payload or {})
    patch_id = str(data.get("patch_id", ""))
    projection = farming_frontend_projection_pure(player_data)
    patch_view = next(
        (
            patch
            for location in projection["locations"]
            for patch in location["patches"]
            if patch["patch_id"] == patch_id
        ),
        None,
    )
    if action_id == "set_plan":
        crop_id = str(data.get("crop_id", ""))
        option = next((row for row in (patch_view or {}).get("crop_options", ()) if row["id"] == crop_id), None)
        if option is None or not option["enabled"]:
            return _copy_with_farm_state(player_data), False, (option or {}).get("locked_reason") or "That crop is not available for this patch."
        return set_farm_plan_pure(
            player_data, patch_id, crop_id,
            str(data.get("compost_tier", "none")), bool(data.get("protection_intent", False)),
        )
    if action_id == "pay_protection":
        return pay_farming_protection_pure(player_data, patch_id)
    if action_id == "queue_action":
        kind = str(data.get("kind", ""))
        primary = (patch_view or {}).get("primary_action")
        if not primary or primary.get("id") != kind or not primary.get("enabled"):
            return _copy_with_farm_state(player_data), False, (primary or {}).get("locked_reason") or "That action is no longer available."
        details = dict(data.get("details") or {})
        updated, step_id, message = add_farm_queue_step_pure(player_data, kind, patch_id, **details)
        return updated, step_id is not None, "Added 1 step to the queue." if step_id else message
    if action_id == "harvest_replant":
        shortcut = (patch_view or {}).get("shortcut_action", {})
        if not shortcut.get("enabled") or shortcut.get("needs_plan"):
            return _copy_with_farm_state(player_data), False, shortcut.get("locked_reason") or "Choose a crop, compost tier, and protection plan first."
        updated, ids, message = queue_harvest_and_replant_same_pure(player_data, patch_id)
        return updated, bool(ids), f"Added {len(ids)} steps to the queue." if ids else message
    if action_id == "queue_full_run":
        if not projection["full_run"]["enabled"]:
            return _copy_with_farm_state(player_data), False, projection["full_run"]["locked_reason"]
        updated, ids = queue_full_run_pure(player_data)
        return updated, bool(ids), f"Queued {len(ids)} Farming steps." if ids else "Nothing was queued; no planned patches need work."
    if action_id == "queue_remove":
        updated, ok = remove_farm_queue_step_pure(player_data, str(data.get("step_id", "")))
        return updated, ok, "Removed the queued step." if ok else "That queued step is no longer available."
    if action_id == "queue_move":
        updated, ok = reorder_farm_queue_step_pure(player_data, str(data.get("step_id", "")), _int(data.get("new_index")))
        return updated, ok, "Moved the queued step." if ok else "That queued step is no longer available."
    if action_id == "queue_clear":
        updated = _copy_with_farm_state(player_data)
        changed = bool(updated["farm_queue"])
        updated["farm_queue"] = []
        return updated, changed, "Cleared the Farming queue." if changed else "The Farming queue is already empty."
    if action_id == "make_saplings":
        updated, amount, message = make_saplings_pure(player_data, str(data.get("crop_id", "")), _int(data.get("amount", 28), default=28))
        return updated, amount > 0, f"Made {amount} saplings." if amount else message
    if action_id == "fill_compost_bin":
        return fill_compost_bin_pure(player_data, str(data.get("bin_id", "")), str(data.get("input_item", "")))
    if action_id == "collect_compost_bin":
        return collect_compost_bin_pure(player_data, str(data.get("bin_id", "")))
    return _copy_with_farm_state(player_data), False, "That action is no longer available."
