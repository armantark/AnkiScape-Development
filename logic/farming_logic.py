"""Pure persistent-state and action mechanics for Farming."""

from __future__ import annotations

import copy
import math
from typing import Any, Callable, Iterable, Mapping, Optional

from ..core.constants import EQUIPMENT_DATA, EXP_TABLE, TREE_DATA, WOODCUTTING_AXE_DATA
from ..data.farming_data import (
    COMPOST_BIN_CAPACITY,
    COMPOST_TIERS,
    FARM_MINUTES_PER_ANSWER,
    FARMING_COMPOST_BINS,
    FARMING_COMPOST_BINS_BY_ID,
    FARMING_CROPS_BY_ID,
    FARMING_PATCHES,
    FARMING_PATCHES_BY_ID,
    FLOWER_PROTECTION,
    LIVID_FARM_ALLOTMENT_PATCH_ID,
    LIVID_FARM_PROTECTION_SCROLL,
    REGULAR_COMPOST_INPUTS,
    SAPLING_RECIPES,
    SUPERCOMPOST_INPUTS,
)
from ..logic_pure.logic_pure import apply_combat_burst_pure, apply_consumable_pure, best_woodcutting_axe_pure, calculate_new_level, quest_completed_pure
from ..data.quest_data import QUEST_DISPLAY_NAMES


FIELD_STEP_KINDS = frozenset({
    "plant",
    "harvest",
    "check_health",
    "cure",
    "clear",
    "dig_up",
    "chop",
    "habitat_traverse",
})
PLANT_CURE_ITEM_FIRST = "plant_cure_item_first"
CURE_PLANT_SPELL_FIRST = "cure_plant_spell_first"
CURE_ROUTE_PREFERENCES = frozenset({
    PLANT_CURE_ITEM_FIRST,
    CURE_PLANT_SPELL_FIRST,
})
HABITAT_EAST_PATCH_ID = "habitat_vine_herb_east"
HABITAT_TRAVERSAL_PHASES = (
    "Climb the vine",
    "Cross the ridge",
    "Drop into the east camp",
)
HABITAT_TRAVERSAL_XP = 10.0
FARM_EVENT_LOG_LIMIT = 200
JADE_VINE_PATCH_ID = "handelmort_jade_vine"
JADE_POLICY_KEEP_TAME = "keep_tame"
JADE_POLICY_TRAIN_SLAYER = "train_slayer"
JADE_POLICY_TRAIN_FARMING = "train_farming"
JADE_VINE_POLICIES = (
    JADE_POLICY_KEEP_TAME,
    JADE_POLICY_TRAIN_SLAYER,
    JADE_POLICY_TRAIN_FARMING,
)
JADE_VINE_COMBAT_TARGET_ID = "wild_jade_vine"
JADE_VINE_COMBAT_TICKS = 6
JADE_VINE_WILD_BRANCH = 6
JADE_VINE_VISIBLE_BRANCHES = 5
JADE_VINE_REPLANT_PAYMENT = {"Coconut": 5, "Watermelon": 5}
JADE_VINE_ENEMY = {
    "display_name": "Wild jade vine",
    "level": 167,
    "attack_style": "melee",
    "attack_speed": 6,
    "respawn_delay": 0,
    "required_slayer_level": 59,
    "slayer_xp": 0.0,
    "stats": {
        "hitpoints": 2500,
        "attack": 120,
        "strength": 120,
        "defence": 120,
        "magic": 120,
        "ranged": 120,
    },
    "bonuses": {
        "attack_stab": 0,
        "attack_slash": 0,
        "attack_crush": 0,
        "defence_stab": 0,
        "defence_slash": 0,
        "defence_crush": 0,
        "defence_magic": 0,
        "defence_ranged": 0,
        "melee_strength": 0,
    },
    "max_hit": 158,
    # The shared Combat engine stores poison in old-HP points; 7 emits the
    # sourced 70-LP opening poison hit.
    "poison_damage": 7,
    "drops": {},
    "source": (
        "Jade vine oldid 6579442; Wild jade vine oldid 6457741; "
        "source_blocked combat stats use a bounded level-120 neutral abstraction"
    ),
}
MORYTANIA_MEDIUM_TASK_KEYS = ("morytania_medium", "medium_morytania_tasks")
FARM_COUNTER_DEFAULTS = {
    "plants": 0,
    "harvests": 0,
    "produce_harvested": 0,
    "health_checks": 0,
    "tree_health_checks": 0,
    "cures": 0,
    "clears": 0,
    "dig_ups": 0,
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
        "jade_bound_reviews_remaining": 0,
        "jade_attack_style_index": 0,
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
        "farming_spell_patch": None,
        "farm_jade_vine_policy": JADE_POLICY_KEEP_TAME,
        "farm_clock_minutes": 0,
        "farm_patches": {patch.id: _default_patch_record() for patch in FARMING_PATCHES},
        "farm_compost_bins": {row.id: _default_bin_record() for row in FARMING_COMPOST_BINS},
        "farm_plans": {},
        "farm_presets": {},
        "farm_preset_order": [],
        "farm_selected_preset": None,
        "farm_next_preset_id": 1,
        "farm_last_full_run_skips": [],
        "farm_livid_patch_active": False,
        "farm_livid_protection_crop_id": None,
        "farm_livid_protection_uses_remaining": 0,
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


def _preset_plan_snapshot(raw: Any) -> Optional[dict[str, Any]]:
    plan = _sanitize_plan(raw)
    if plan is None:
        return None
    return {
        "crop_id": plan["crop_id"],
        "compost_tier": plan["compost_tier"],
        "protection_intent": plan["protection_intent"],
        "watering_intent": plan["watering_intent"],
        "cure_intent": plan["cure_intent"],
        "cure_route_preference": plan["cure_route_preference"],
    }


def _sanitize_preset(raw: Any, preset_id: str) -> Optional[dict[str, Any]]:
    if not isinstance(raw, Mapping):
        return None
    name = str(raw.get("name", "")).strip()[:60]
    if not name:
        return None
    raw_plans = raw.get("plans")
    plans: dict[str, dict[str, Any]] = {}
    if isinstance(raw_plans, Mapping):
        for patch_id, raw_plan in raw_plans.items():
            patch = FARMING_PATCHES_BY_ID.get(patch_id)
            plan = _preset_plan_snapshot(raw_plan)
            crop = FARMING_CROPS_BY_ID.get(plan.get("crop_id")) if plan else None
            if (
                patch is None
                or patch.fixed_crop_id is not None
                or crop is None
                or crop.patch_type != patch.patch_type
                or patch.crop_whitelist and crop.id not in patch.crop_whitelist
            ):
                continue
            plans[patch_id] = plan
    if not plans:
        return None
    preset = dict(raw)
    preset.update({"id": preset_id, "name": name, "plans": plans})
    return preset


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
    for key in ("diseased", "dead", "protected", "livid_protected", "watered", "health_checked", "stump"):
        record[key] = bool(record.get(key, False))
    record["protected"] = bool(
        record["protected"] or record["livid_protected"]
    )
    record["produce_count"] = _int(record.get("produce_count"))
    record["last_regrowth_at"] = _int(record.get("last_regrowth_at"))
    record["next_regrowth_at"] = _int(record.get("next_regrowth_at"))
    record["jade_state"] = record.get("jade_state") if record.get("jade_state") in {None, "prunable", "wild"} else None
    record["jade_prunes"] = _int(record.get("jade_prunes"))
    encounter = record.get("jade_combat_encounter")
    record["jade_combat_encounter"] = dict(encounter) if isinstance(encounter, Mapping) else {}
    record["jade_bound_reviews_remaining"] = _int(record.get("jade_bound_reviews_remaining"))
    record["jade_attack_style_index"] = _int(record.get("jade_attack_style_index")) % 3
    record["plan"] = _sanitize_plan(record.get("plan"))
    if crop_id is None:
        for key in ("diseased", "dead", "protected", "livid_protected", "watered", "health_checked", "stump"):
            record[key] = False
        record["stage"] = 0
        record["lives"] = 0
        record["produce_count"] = 0
        record["next_regrowth_at"] = 0
        record["jade_state"] = None
        record["jade_prunes"] = 0
        record["jade_combat_encounter"] = {}
        record["jade_bound_reviews_remaining"] = 0
        record["jade_attack_style_index"] = 0
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
        if patch.fixed_crop_id is None:
            continue
        record = patches[patch.id]
        if not farming_access_gate_allows_pure(player_data, patch.access_gate):
            record.clear()
            record.update(_default_patch_record())
            continue
        crop = FARMING_CROPS_BY_ID[patch.fixed_crop_id]
        if record.get("crop_id") != crop.id:
            record.clear()
            record.update(_default_patch_record())
            record.update(
                {
                    "crop_id": crop.id,
                    "last_crop_id": crop.id,
                    "stage": crop.stages or 0,
                    "lives": crop.base_lives,
                    "protected": True,
                    "health_checked": True,
                    "produce_count": crop.fixed_yield or 0,
                    "last_regrowth_at": _int(player_data.get("farm_clock_minutes")),
                }
            )
        record["plan"] = None

    raw_bins = player_data.get("farm_compost_bins")
    bins: dict[str, Any] = dict(raw_bins) if isinstance(raw_bins, Mapping) else {}
    for row in FARMING_COMPOST_BINS:
        bins[row.id] = _sanitize_bin_record(bins.get(row.id))

    raw_plans = player_data.get("farm_plans")
    plans: dict[str, Any] = dict(raw_plans) if isinstance(raw_plans, Mapping) else {}
    for patch_id in list(plans):
        if (
            patch_id in FARMING_PATCHES_BY_ID
            and FARMING_PATCHES_BY_ID[patch_id].fixed_crop_id is not None
        ):
            plans.pop(patch_id, None)
            continue
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

    raw_presets = player_data.get("farm_presets")
    presets: dict[str, dict[str, Any]] = {}
    if isinstance(raw_presets, Mapping):
        for preset_id, raw_preset in raw_presets.items():
            if not isinstance(preset_id, str) or not preset_id.startswith("farm_preset_"):
                continue
            preset = _sanitize_preset(raw_preset, preset_id)
            if preset is not None:
                presets[preset_id] = preset
    raw_preset_order = player_data.get("farm_preset_order")
    preset_order = [
        preset_id
        for preset_id in raw_preset_order
        if isinstance(preset_id, str) and preset_id in presets
    ] if isinstance(raw_preset_order, list) else []
    preset_order.extend(preset_id for preset_id in presets if preset_id not in preset_order)
    selected_preset = player_data.get("farm_selected_preset")
    if selected_preset not in presets:
        selected_preset = None
    highest_preset_id = max(
        (
            _int(preset_id.removeprefix("farm_preset_"))
            for preset_id in presets
            if preset_id.startswith("farm_preset_")
        ),
        default=0,
    )
    raw_full_run_skips = player_data.get("farm_last_full_run_skips")
    full_run_skips = tuple(
        {
            "patch_id": str(row.get("patch_id", "")),
            "patch_name": str(row.get("patch_name", "")),
            "reason": str(row.get("reason", "")),
        }
        for row in raw_full_run_skips
        if isinstance(row, Mapping) and row.get("patch_id") in FARMING_PATCHES_BY_ID
    ) if isinstance(raw_full_run_skips, (list, tuple)) else ()

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

    livid_patch_active = bool(player_data.get("farm_livid_patch_active", False))
    livid_protection_crop_id = player_data.get("farm_livid_protection_crop_id")
    livid_protection_crop = FARMING_CROPS_BY_ID.get(livid_protection_crop_id)
    livid_protection_uses = min(
        10,
        _int(player_data.get("farm_livid_protection_uses_remaining"), minimum=0),
    )
    if (
        livid_protection_crop is None
        or livid_protection_crop.patch_type not in {"tree", "fruit_tree"}
        or livid_protection_uses <= 0
    ):
        livid_protection_crop_id = None
        livid_protection_uses = 0
    farming_spell_patch = player_data.get("farming_spell_patch")
    if (
        farming_spell_patch not in FARMING_PATCHES_BY_ID
        or (
            farming_spell_patch == LIVID_FARM_ALLOTMENT_PATCH_ID
            and not livid_patch_active
        )
    ):
        farming_spell_patch = None

    # Unlike its peers, this sanitizer passes some values straight through from
    # the input instead of rebuilding them, so it is not a rebuild boundary: a
    # shallow working copy that relies on it would still alias the caller's
    # save. Anything added here that is not a scalar needs its own copy.
    return {
        "farming_exp": _number(player_data.get("farming_exp", 0.0)),
        "farming_level": _int(player_data.get("farming_level", 1), default=1, minimum=1),
        "farming_spell_patch": farming_spell_patch,
        "farm_jade_vine_policy": (
            player_data.get("farm_jade_vine_policy")
            if player_data.get("farm_jade_vine_policy") in JADE_VINE_POLICIES
            else JADE_POLICY_KEEP_TAME
        ),
        "farm_clock_minutes": _int(player_data.get("farm_clock_minutes", defaults["farm_clock_minutes"])),
        "farm_patches": patches,
        "farm_compost_bins": bins,
        "farm_plans": plans,
        "farm_presets": presets,
        "farm_preset_order": preset_order,
        "farm_selected_preset": selected_preset,
        "farm_next_preset_id": max(
            highest_preset_id + 1,
            _int(player_data.get("farm_next_preset_id", 1), default=1, minimum=1),
        ),
        "farm_last_full_run_skips": list(full_run_skips),
        "farm_livid_patch_active": livid_patch_active,
        "farm_livid_protection_crop_id": livid_protection_crop_id,
        "farm_livid_protection_uses_remaining": livid_protection_uses,
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
    if gate.kind == "state":
        return bool(gate.key and player_data.get(gate.key))
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


def _remove_jade_prune_steps(updated: dict[str, Any]) -> None:
    updated["farm_queue"] = [
        step
        for step in updated.get("farm_queue", ())
        if not (
            step.get("patch_id") == JADE_VINE_PATCH_ID
            and step.get("kind") == "harvest"
            and step.get("jade_auto_prune")
        )
    ]


def _queue_jade_prune(updated: dict[str, Any]) -> None:
    updated["farm_queue"].append({
        "id": _step_id(updated),
        "kind": "harvest",
        "patch_id": JADE_VINE_PATCH_ID,
        "jade_auto_prune": True,
    })


def _jade_replant_plan(updated: Mapping[str, Any], record: Mapping[str, Any]) -> dict[str, Any]:
    return _sanitize_plan(updated.get("farm_plans", {}).get(JADE_VINE_PATCH_ID)) or _sanitize_plan(record.get("plan")) or {
        "crop_id": "jade_vine",
        "compost_tier": "none",
        "protection_intent": False,
        "watering_intent": False,
        "cure_intent": True,
        "cure_route_preference": PLANT_CURE_ITEM_FIRST,
    }


def _try_horacio_replant(updated: dict[str, Any], record: dict[str, Any]) -> bool:
    if not _has_items(updated["inventory"], JADE_VINE_REPLANT_PAYMENT):
        return False
    plan = _jade_replant_plan(updated, record)
    _consume(updated["inventory"], JADE_VINE_REPLANT_PAYMENT)
    _reset_patch(record)
    if not _owns_jade_seed_anywhere(updated):
        updated["inventory"]["Jade vine seed"] = 1
    _append_planned_steps(updated, JADE_VINE_PATCH_ID, ["plant"], plan)
    _log(
        updated,
        "jade_vine_horacio_replant",
        "Horacio removed the Jade vine and queued its Plant step.",
        patch_id=JADE_VINE_PATCH_ID,
    )
    return True


def _process_patch_boundaries(updated: dict[str, Any], patch_id: str, random_random: Callable[[], float]) -> None:
    record = updated["farm_patches"][patch_id]
    crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
    if crop is None:
        return
    clock = updated["farm_clock_minutes"]
    if (
        crop.stages is not None
        and crop.stage_minutes is not None
        and crop.stage_minutes > 0
    ):
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
                # Willow branches begin accumulating only after the one-time
                # health check; elapsed mature time does not backfill them.
                record["produce_count"] = (
                    0 if crop.id in {"willow", "jade_vine"} else crop.fixed_yield or 0
                )
                record["last_regrowth_at"] = boundary
                if crop.regrowth_range_minutes and crop.id != "jade_vine":
                    record["next_regrowth_at"] = boundary + _random_int_inclusive(random_random, *crop.regrowth_range_minutes)
                if crop.id == "jade_vine":
                    record["jade_state"] = "prunable"
                    record["jade_prunes"] = 0
                _log(updated, "crop_ready", f"{crop.display_name} is ready.", patch_id=patch_id, crop_id=crop.id)
                break
            # The first completed growth stage is immune. The settled Farming
            # contract applies GM's one-cycle 0.9 watering factor.
            if record["stage"] > 1 and not _disease_exempt(updated, patch_id, record, crop):
                tier = COMPOST_TIERS[record.get("compost_tier", "none")]
                watering_factor = 0.9 if record.get("watered") else 1.0
                disease_slots = math.floor(crop.disease_slots * tier.disease_factor * watering_factor)
                if random_random() < disease_slots / 128:
                    record["diseased"] = True
                    _log(updated, "crop_diseased", f"{crop.display_name} became diseased.", patch_id=patch_id, crop_id=crop.id)
                    continue

    if (
        not _is_mature(record, crop)
        or crop.fixed_yield is None
        or record.get("jade_state") == "wild"
        or (crop.id == "willow" and not record.get("health_checked"))
    ):
        return
    if crop.id == "jade_vine":
        if not record.get("health_checked") or not record.get("next_regrowth_at"):
            return
        if (
            updated.get("farm_jade_vine_policy") == JADE_POLICY_TRAIN_FARMING
            and _try_horacio_replant(updated, record)
        ):
            return
        while record["next_regrowth_at"] <= clock:
            record["produce_count"] += 1
            record["last_regrowth_at"] = record["next_regrowth_at"]
            if record["produce_count"] >= JADE_VINE_WILD_BRANCH:
                record["jade_state"] = "wild"
                record["produce_count"] = 0
                record["next_regrowth_at"] = 0
                _remove_jade_prune_steps(updated)
                _log(
                    updated,
                    "jade_vine_wild",
                    "The unseen sixth branch turned the Jade vine wild.",
                    patch_id=patch_id,
                    crop_id=crop.id,
                )
                break
            record["next_regrowth_at"] += _random_int_inclusive(
                random_random, *crop.regrowth_range_minutes
            )
            if updated.get("farm_jade_vine_policy") == JADE_POLICY_KEEP_TAME:
                _queue_jade_prune(updated)
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


def _queued_protection_payment(step: Mapping[str, Any]) -> dict[str, int]:
    crop = FARMING_CROPS_BY_ID.get(step.get("crop_id"))
    payment = crop.protection if crop is not None else None
    raw_payment = step.get("protection_payment")
    if (
        not step.get("protection_paid")
        or payment is None
        or not isinstance(raw_payment, Mapping)
    ):
        return {}
    expected = dict(payment.items)
    normalized = {
        str(item): _int(amount, minimum=0)
        for item, amount in raw_payment.items()
        if isinstance(item, str)
    }
    return expected if normalized == expected else {}


def _refund_queued_protection(updated: dict[str, Any], step: Mapping[str, Any]) -> None:
    for item, amount in _queued_protection_payment(step).items():
        updated["inventory"][item] = _int(updated["inventory"].get(item)) + amount


def _reset_patch(record: dict[str, Any]) -> None:
    plan = copy.deepcopy(record.get("plan"))
    last_crop = record.get("crop_id") or record.get("last_crop_id")
    unknown = {key: value for key, value in record.items() if key not in _default_patch_record()}
    record.clear()
    record.update(_default_patch_record())
    record.update(unknown)
    record["plan"] = plan
    record["last_crop_id"] = last_crop


def activate_livid_farm_allotment_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    if updated["farm_livid_patch_active"]:
        return updated, False, "The Livid Farm allotment is already active"
    record = updated["farm_patches"][LIVID_FARM_ALLOTMENT_PATCH_ID]
    record.clear()
    record.update(_default_patch_record())
    updated["farm_plans"].pop(LIVID_FARM_ALLOTMENT_PATCH_ID, None)
    for step in updated["farm_queue"]:
        if step.get("patch_id") == LIVID_FARM_ALLOTMENT_PATCH_ID:
            _refund_queued_protection(updated, step)
    updated["farm_queue"] = [
        step
        for step in updated["farm_queue"]
        if step.get("patch_id") != LIVID_FARM_ALLOTMENT_PATCH_ID
    ]
    if updated.get("farming_spell_patch") == LIVID_FARM_ALLOTMENT_PATCH_ID:
        updated["farming_spell_patch"] = None
    updated["farm_livid_patch_active"] = True
    _log(
        updated,
        "livid_patch_created",
        "The one-use Livid Farm allotment is ready.",
        patch_id=LIVID_FARM_ALLOTMENT_PATCH_ID,
    )
    return updated, True, "Livid Farm allotment created"


def activate_livid_farm_patch_protection_pure(
    player_data: Mapping[str, Any],
    patch_id: str,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    if _int(updated.get("farm_livid_protection_uses_remaining")) > 0:
        return updated, False, "Another Livid Farm patch protection is already active"
    patch = FARMING_PATCHES_BY_ID.get(patch_id)
    if patch is None:
        return updated, False, "Unknown Farming patch"
    if patch.patch_type not in {"tree", "fruit_tree"}:
        return updated, False, "Choose an ordinary tree or fruit-tree patch"
    if not farming_access_gate_allows_pure(updated, patch.access_gate):
        return updated, False, "Patch access is locked"
    record = updated["farm_patches"][patch_id]
    crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
    if crop is None or crop.patch_type not in {"tree", "fruit_tree"}:
        return updated, False, "Plant a tree in this patch first"
    if (
        _is_mature(record, crop)
        or record.get("diseased")
        or record.get("dead")
        or record.get("stump")
    ):
        return updated, False, "Choose a healthy tree that is still growing"
    if record.get("protected"):
        return updated, False, "This tree is already protected"
    if _int(updated["inventory"].get(LIVID_FARM_PROTECTION_SCROLL)) <= 0:
        return updated, False, "No Patch protection scroll is available"

    updated["inventory"][LIVID_FARM_PROTECTION_SCROLL] = (
        _int(updated["inventory"].get(LIVID_FARM_PROTECTION_SCROLL)) - 1
    )
    if updated["inventory"][LIVID_FARM_PROTECTION_SCROLL] <= 0:
        updated["inventory"].pop(LIVID_FARM_PROTECTION_SCROLL, None)
    record["protected"] = True
    record["livid_protected"] = True
    updated["farm_livid_protection_crop_id"] = crop.id
    updated["farm_livid_protection_uses_remaining"] = 9
    _log(
        updated,
        "livid_patch_protection_activated",
        f"Patch protection now covers 9 more {crop.display_name} plantings.",
        patch_id=patch_id,
        crop_id=crop.id,
        uses_remaining=9,
    )
    return updated, True, f"Protected this tree and 9 more {crop.display_name} plantings"


def _expire_livid_farm_allotment(updated: dict[str, Any]) -> None:
    if not updated.get("farm_livid_patch_active"):
        return
    for step in updated["farm_queue"]:
        if step.get("patch_id") == LIVID_FARM_ALLOTMENT_PATCH_ID:
            _refund_queued_protection(updated, step)
    updated["farm_queue"] = [
        step
        for step in updated["farm_queue"]
        if step.get("patch_id") != LIVID_FARM_ALLOTMENT_PATCH_ID
    ]
    updated["farm_plans"].pop(LIVID_FARM_ALLOTMENT_PATCH_ID, None)
    record = updated["farm_patches"][LIVID_FARM_ALLOTMENT_PATCH_ID]
    record["plan"] = None
    updated["farm_livid_patch_active"] = False
    if updated.get("farming_spell_patch") == LIVID_FARM_ALLOTMENT_PATCH_ID:
        updated["farming_spell_patch"] = None
    _log(
        updated,
        "livid_patch_expired",
        "The one-use Livid Farm allotment disappeared after clearing.",
        patch_id=LIVID_FARM_ALLOTMENT_PATCH_ID,
    )


def _plant(updated: dict[str, Any], patch_id: str, patch: Any, crop: Any, step: Mapping[str, Any]) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if patch.fixed_crop_id is not None:
        return False, "the permanent quest patch cannot be replanted", {}
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
    paid = bool(step.get("protection_paid")) or bool(
        matching_plan and matching_plan.get("protection_paid")
    )
    livid_protected = bool(
        not paid
        and updated.get("farm_livid_protection_crop_id") == crop.id
        and _int(updated.get("farm_livid_protection_uses_remaining")) > 0
    )
    watering_intent = True if matching_plan is None else bool(matching_plan.get("watering_intent"))
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
        "protected": paid or livid_protected,
        "livid_protected": livid_protected,
        "watered": (
            watering_intent
            and crop.patch_type in {"allotment", "flower", "hops"}
            and any(_int(inventory.get(item)) > 0 for item in ("Watering can", "Watering can (8)"))
        ),
        "health_checked": False,
        "stump": False,
        "produce_count": 0,
        "last_regrowth_at": 0,
        "next_regrowth_at": 0,
        "jade_state": "prunable" if crop.id == "jade_vine" else None,
        "jade_prunes": 0,
    })
    if livid_protected:
        uses_remaining = (
            _int(updated.get("farm_livid_protection_uses_remaining")) - 1
        )
        updated["farm_livid_protection_uses_remaining"] = uses_remaining
        if uses_remaining <= 0:
            updated["farm_livid_protection_crop_id"] = None
        _log(
            updated,
            "livid_patch_protection_applied",
            (
                f"Patch protection applied to {crop.display_name}; "
                f"{uses_remaining} use{'s' if uses_remaining != 1 else ''} remain."
            ),
            patch_id=patch_id,
            crop_id=crop.id,
            uses_remaining=uses_remaining,
        )
    xp = float(crop.planting_xp or 0.0) + tier.application_xp
    _award_xp(updated, "farming", xp)
    _increment(updated, "plants")
    return True, f"Planted {crop.display_name}.", {
        "farming_xp": xp,
        "outputs": {"Weeds": 3},
        "livid_protected": livid_protected,
        "livid_protection_uses_remaining": _int(
            updated.get("farm_livid_protection_uses_remaining")
        ),
    }


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


def _harvest_tool_options(crop: Any) -> tuple[str, ...]:
    if crop.id in {"willow", "jade_vine"}:
        return ("Secateurs", "Magic secateurs")
    return (crop.harvest_tool,) if crop.harvest_tool else ()


def _missing_harvest_tool_reason(
    inventory: Mapping[str, Any],
    crop: Any,
) -> str:
    options = _harvest_tool_options(crop)
    if not options or any(_int(inventory.get(tool)) > 0 for tool in options):
        return ""
    return f"Needs {' or '.join(options)} in your Bank."


def _harvest(updated: dict[str, Any], patch_id: str, crop: Any, random_random: Callable[[], float]) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    missing_tool = _missing_harvest_tool_reason(updated["inventory"], crop)
    if missing_tool:
        return False, f"missing {' or '.join(_harvest_tool_options(crop))}", {}
    if not _is_mature(record, crop) or record.get("stump") or record.get("jade_state") == "wild":
        return False, "crop is not ready", {}
    if crop.check_health_xp is not None and not record.get("health_checked"):
        return False, "check the crop's health first", {}
    if (not crop.output_item and crop.id != "jade_vine") or crop.harvest_xp is None:
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
    xp = amount * crop.harvest_xp
    _award_xp(updated, "farming", xp)
    _increment(updated, "harvests")
    if crop.id == "jade_vine":
        record["produce_count"] -= 1
        record["jade_prunes"] += 1
        return True, "Pruned one Jade vine branch.", {
            "farming_xp": xp,
            "outputs": {},
            "juju_bonus": 0,
        }
    updated["inventory"][crop.output_item] = _int(updated["inventory"].get(crop.output_item)) + total_output
    _increment(updated, "produce_harvested", total_output)
    if crop.regrowth_minutes or crop.regrowth_range_minutes:
        record["produce_count"] = 0
        record["last_regrowth_at"] = updated["farm_clock_minutes"]
        if crop.regrowth_range_minutes:
            record["next_regrowth_at"] = updated["farm_clock_minutes"] + _random_int_inclusive(random_random, *crop.regrowth_range_minutes)
    else:
        _reset_patch(record)
    outputs = {crop.output_item: total_output}
    return True, f"Harvested {total_output} {crop.output_item}.", {"farming_xp": xp, "outputs": outputs, "juju_bonus": bonus}


def _check_health(
    updated: dict[str, Any],
    patch_id: str,
    crop: Any,
    random_random: Callable[[], float],
) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if not _is_mature(record, crop) or crop.check_health_xp is None or record.get("health_checked"):
        return False, "health cannot be checked", {}
    record["health_checked"] = True
    if crop.id == "willow":
        record["produce_count"] = 0
        record["last_regrowth_at"] = updated["farm_clock_minutes"]
    elif crop.id == "jade_vine":
        record["jade_state"] = "prunable"
        record["produce_count"] = 0
        record["last_regrowth_at"] = updated["farm_clock_minutes"]
        record["next_regrowth_at"] = updated["farm_clock_minutes"] + _random_int_inclusive(
            random_random, *crop.regrowth_range_minutes
        )
    _award_xp(updated, "farming", crop.check_health_xp)
    _increment(updated, "health_checks")
    if crop.patch_type in {"tree", "fruit_tree", "calquat"}:
        _increment(updated, "tree_health_checks")
    message = f"Checked the health of {crop.display_name}."
    if crop.id == "jade_vine" and updated.get("farm_jade_vine_policy") == JADE_POLICY_TRAIN_FARMING:
        if _try_horacio_replant(updated, record):
            message += " Horacio removed it for 5 coconuts and 5 watermelons and queued its Plant step."
        else:
            message += " Replant blocked: Horacio needs 5 coconuts and 5 watermelons; branch growth continues."
    return True, message, {"farming_xp": crop.check_health_xp}


def _cure_spell_locked_reasons(
    updated: Mapping[str, Any],
    patch_id: str,
) -> tuple[str, ...]:
    from ..core.constants import MAGIC_DATA
    from ..logic_pure.logic_pure import magic_target_locked_reasons_pure
    return magic_target_locked_reasons_pure(
        updated,
        "cure_plant",
        MAGIC_DATA,
        {},
        farming_patch_id=patch_id,
    )


def _cure(
    updated: dict[str, Any],
    patch_id: str,
    crop: Any,
    step: Mapping[str, Any],
) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if not record.get("diseased") or record.get("dead"):
        return False, "crop is not diseased", {}

    preference = str(
        step.get("cure_route_preference", PLANT_CURE_ITEM_FIRST) or ""
    )
    if preference not in CURE_ROUTE_PREFERENCES:
        preference = PLANT_CURE_ITEM_FIRST
    routes = (
        ("cure_plant_spell", "plant_cure_item")
        if preference == CURE_PLANT_SPELL_FIRST
        else ("plant_cure_item", "cure_plant_spell")
    )
    failures = []
    for route in routes:
        if route == "plant_cure_item":
            if _int(updated["inventory"].get("Plant cure")) <= 0:
                failures.append("missing Plant cure")
                continue
            updated["inventory"]["Plant cure"] -= 1
            record["diseased"] = False
            _increment(updated, "cures")
            return True, f"Cured {crop.display_name} with Plant cure.", {
                "farming_xp": 0.0,
                "cure_route": route,
            }

        spell_reasons = _cure_spell_locked_reasons(updated, patch_id)
        if spell_reasons:
            failures.append("Cure Plant: " + ", ".join(spell_reasons))
            continue
        from ..core.constants import MAGIC_DATA
        from ..logic_pure.logic_pure import apply_magic_action_pure
        cast, magic_xp, _secondary, _outputs, ok, message = apply_magic_action_pure(
            updated,
            "cure_plant",
            MAGIC_DATA,
            {},
            farming_patch_id=patch_id,
        )
        if not ok:
            failures.append("Cure Plant is unavailable")
            continue
        _award_xp(cast, "magic", magic_xp)
        updated.clear()
        updated.update(cast)
        return True, message, {
            "farming_xp": 0.0,
            "magic_xp": magic_xp,
            "cure_route": route,
        }

    return False, "; ".join(dict.fromkeys(failures)), {}


def _clear(updated: dict[str, Any], patch_id: str, crop: Any) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if FARMING_PATCHES_BY_ID[patch_id].fixed_crop_id is not None:
        return False, "the permanent quest patch cannot be cleared", {}
    if _int(updated["inventory"].get("Spade")) <= 0:
        return False, "missing Spade", {}
    clearable_scarecrow = crop.id == "scarecrow"
    clearable_mature_no_output = bool(
        _is_mature(record, crop)
        and crop.output_item is None
        and crop.check_health_xp is not None
        and record.get("health_checked")
    )
    if (
        not record.get("dead")
        and not record.get("stump")
        and not clearable_scarecrow
        and not clearable_mature_no_output
    ):
        return False, "patch has no clearable crop or stump", {}
    outputs: dict[str, int] = {}
    if record.get("stump") and crop.root_item:
        updated["inventory"][crop.root_item] = _int(updated["inventory"].get(crop.root_item)) + 1
        outputs[crop.root_item] = 1
    if clearable_scarecrow:
        updated["inventory"]["Scarecrow"] = _int(updated["inventory"].get("Scarecrow")) + 1
        outputs["Scarecrow"] = 1
    _reset_patch(record)
    _increment(updated, "clears")
    return True, f"Cleared {FARMING_PATCHES_BY_ID[patch_id].display_name}.", {"outputs": outputs}


def _is_regrowth_crop(crop: Any) -> bool:
    return bool(
        crop.patch_type != "tree"
        and (crop.regrowth_minutes or crop.regrowth_range_minutes)
    )


def _dig_up(updated: dict[str, Any], patch_id: str, crop: Any) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if FARMING_PATCHES_BY_ID[patch_id].fixed_crop_id is not None:
        return False, "the permanent quest patch cannot be dug up", {}
    if _int(updated["inventory"].get("Spade")) <= 0:
        return False, "missing Spade", {}
    if (
        not _is_regrowth_crop(crop)
        or not _is_mature(record, crop)
        or record.get("diseased")
        or record.get("dead")
        or record.get("stump")
        or record.get("jade_state") == "wild"
    ):
        return False, "patch has no healthy mature regrowth crop", {}
    _reset_patch(record)
    _increment(updated, "dig_ups")
    return True, f"Dug up {crop.display_name}.", {"farming_xp": 0.0, "outputs": {}}


def _toolbelt_has_secateurs(toolbelt: Any) -> bool:
    if not isinstance(toolbelt, Mapping):
        return False
    for raw_items in toolbelt.values():
        items = (raw_items,) if isinstance(raw_items, str) else raw_items
        if not isinstance(items, (tuple, list, set)):
            continue
        if any(str(item).replace("_", " ").casefold() in {"secateurs", "magic secateurs"} for item in items):
            return True
    return False


def _equipped_usable_hatchet(updated: Mapping[str, Any]) -> Optional[str]:
    equipment = updated.get("equipment")
    weapon = equipment.get("weapon") if isinstance(equipment, Mapping) else None
    if not isinstance(weapon, str):
        return None
    axe = next(
        (
            row
            for row in WOODCUTTING_AXE_DATA.values()
            if row.get("display_name") == weapon
        ),
        None,
    )
    if not isinstance(axe, Mapping):
        return None
    if _int(updated.get("woodcutting_level", 1), default=1, minimum=1) < _int(axe.get("level", 1), default=1, minimum=1):
        return None
    return weapon


def _jade_vine_combat(
    updated: dict[str, Any],
    patch_id: str,
    step: Mapping[str, Any],
    random_random: Callable[[], float],
) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if _int(updated.get("slayer_level", 1), default=1, minimum=1) < 59:
        return False, "requires Slayer level 59", {}
    if _equipped_usable_hatchet(updated) is None:
        return False, "equip a usable hatchet", {}
    inventory = updated["inventory"]
    if not (
        _int(inventory.get("Secateurs")) > 0
        or _int(inventory.get("Magic secateurs")) > 0
        or _toolbelt_has_secateurs(updated.get("toolbelt"))
    ):
        return False, "requires Secateurs in your Bank or toolbelt", {}
    if _int(record.get("jade_bound_reviews_remaining")) > 0:
        record["jade_bound_reviews_remaining"] -= 1
        return True, "The Wild jade vine's bind holds you for this review.", {
            "repeat_queue_step": True,
            "combat_continuing": True,
            "ticks_elapsed": 0,
            "outputs": {},
        }

    ordinary_target = updated.get("current_combat_target")
    ordinary_encounter = copy.deepcopy(updated.get("combat_encounter", {}))
    updated["current_combat_target"] = JADE_VINE_COMBAT_TARGET_ID
    updated["combat_encounter"] = copy.deepcopy(record.get("jade_combat_encounter", {}))
    style_index = _int(record.get("jade_attack_style_index")) % 3
    enemy = dict(JADE_VINE_ENEMY)
    enemy["attack_style"] = ("melee", "magic", "ranged")[style_index]
    fought, ok, result = apply_combat_burst_pure(
        updated,
        {JADE_VINE_COMBAT_TARGET_ID: enemy},
        EQUIPMENT_DATA,
        ticks=_int(
            step.get("jade_combat_ticks", JADE_VINE_COMBAT_TICKS),
            default=JADE_VINE_COMBAT_TICKS,
            minimum=1,
        ),
        rng=random_random,
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=False,
        allow_bank_run=False,
    )
    if not ok:
        updated["current_combat_target"] = ordinary_target
        updated["combat_encounter"] = ordinary_encounter
        reasons = result.get("locked_reasons", ()) if isinstance(result, Mapping) else ()
        return False, ", ".join(str(reason) for reason in reasons) or "Wild jade vine combat is unavailable", {}

    synthetic_encounter = copy.deepcopy(fought.get("combat_encounter", {}))
    fought["current_combat_target"] = ordinary_target
    fought["combat_encounter"] = ordinary_encounter
    updated.clear()
    updated.update(fought)
    record = updated["farm_patches"][patch_id]
    record["jade_attack_style_index"] = (style_index + 1) % 3
    killed = bool(result.get("killed"))
    died = bool(result.get("died"))
    fled = bool(result.get("fled"))
    details = {
        "combat_result": dict(result),
        "xp_rewards": dict(result.get("xp_rewards", {}) or {}),
        "ticks_elapsed": _int(result.get("ticks_elapsed")),
        "outputs": {},
    }
    if killed:
        _award_xp(updated, "slayer", 2500.0)
        _award_xp(updated, "woodcutting", 202.0)
        updated["inventory"]["Jade vine seed"] = _int(updated["inventory"].get("Jade vine seed")) + 1
        _reset_patch(record)
        if step.get("replant_after"):
            plan = _sanitize_plan(step.get("replant_plan"))
            if plan is not None:
                plant_step = {
                    "id": _step_id(updated),
                    "kind": "plant",
                    "patch_id": patch_id,
                    "crop_id": plan["crop_id"],
                    "compost_tier": plan["compost_tier"],
                }
                updated["farm_queue"].insert(0, plant_step)
        _increment(updated, "chops")
        details.update({
            "slayer_xp": 2500.0,
            "woodcutting_xp": 202.0,
            "outputs": {"Jade vine seed": 1},
        })
        return True, "Killed the Wild jade vine and cut its stump for a replacement seed.", details
    if died:
        updated["combat_encounter"] = {}
        record["jade_combat_encounter"] = {}
        record["jade_bound_reviews_remaining"] = 0
        return True, "You died; the Wild jade vine remains and will be at full health next time.", details
    if fled:
        record["jade_combat_encounter"] = {}
        record["jade_bound_reviews_remaining"] = 0
        return True, "You fled; the Wild jade vine returned to full health.", details

    record["jade_combat_encounter"] = synthetic_encounter
    if _int(result.get("enemy_damage")) > 0 and random_random() < (1.0 / 6.0):
        record["jade_bound_reviews_remaining"] = 1
        details["bound"] = True
    details["repeat_queue_step"] = True
    details["combat_continuing"] = True
    enemy_lp = _int(result.get("enemy_lifepoints"), default=2500)
    return True, f"Fought the Wild jade vine; {enemy_lp}/2500 LP remain.", details


def _chop(
    updated: dict[str, Any],
    patch_id: str,
    crop: Any,
    step: Mapping[str, Any],
    random_random: Callable[[], float],
) -> tuple[bool, str, dict[str, Any]]:
    record = updated["farm_patches"][patch_id]
    if crop.id == "jade_vine":
        if record.get("jade_state") != "wild":
            return False, "jade vine is not wild", {}
        return _jade_vine_combat(updated, patch_id, step, random_random)
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
    if kind == "habitat_traverse":
        if _int(updated.get("agility_level", 1), default=1, minimum=1) < 55:
            return False, {"message": "requires Agility level 55", "kind": kind}
        phase = _int(step.get("phase"), minimum=0)
        if phase >= len(HABITAT_TRAVERSAL_PHASES):
            return False, {"message": "unknown Habitat traversal phase", "kind": kind}
        _award_xp(updated, "agility", HABITAT_TRAVERSAL_XP)
        message = f"{HABITAT_TRAVERSAL_PHASES[phase]} (+{HABITAT_TRAVERSAL_XP:g} Agility XP)."
        _log(updated, "habitat_traversal", message, phase=phase, patch_id=HABITAT_EAST_PATCH_ID)
        return True, {
            "message": message,
            "kind": kind,
            "patch_id": HABITAT_EAST_PATCH_ID,
            "agility_xp": HABITAT_TRAVERSAL_XP,
            "phase": phase,
        }
    patch_id, patch, crop, error = _patch_crop_for_step(updated, step)
    if error:
        return False, {"message": error, "kind": kind}
    handlers = {
        "plant": lambda: _plant(updated, patch_id, patch, crop, step),
        "harvest": lambda: _harvest(updated, patch_id, crop, random_random),
        "check_health": lambda: _check_health(updated, patch_id, crop, random_random),
        "cure": lambda: _cure(updated, patch_id, crop, step),
        "clear": lambda: _clear(updated, patch_id, crop),
        "dig_up": lambda: _dig_up(updated, patch_id, crop),
        "chop": lambda: _chop(updated, patch_id, crop, step, random_random),
    }
    ok, message, details = handlers[kind]()
    livid_patch_expired = bool(
        ok
        and patch_id == LIVID_FARM_ALLOTMENT_PATCH_ID
        and kind in {"harvest", "clear"}
        and updated["farm_patches"][patch_id].get("crop_id") is None
    )
    if livid_patch_expired:
        _expire_livid_farm_allotment(updated)
    info = {"message": message, "kind": kind, "patch_id": patch_id, "crop_id": crop.id}
    info.update(details)
    if livid_patch_expired:
        info["livid_patch_expired"] = True
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
    if patch.fixed_crop_id is not None:
        return ("Permanent quest patches cannot be changed by Farming spells",)
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


def apply_remote_farm_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """View every admitted patch and cure all live diseased crops in one cast."""

    updated = _copy_with_farm_state(player_data)
    active_patch_count = 0
    cured_patch_ids: list[str] = []
    for patch in FARMING_PATCHES:
        if not farming_access_gate_allows_pure(updated, patch.access_gate):
            continue
        record = updated["farm_patches"][patch.id]
        crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
        if crop is None:
            continue
        active_patch_count += 1
        if record.get("dead") or not record.get("diseased"):
            continue
        record["diseased"] = False
        cured_patch_ids.append(patch.id)
        _increment(updated, "cures")
        _log(
            updated,
            "farming_spell",
            f"Remote Farm cured {crop.display_name}.",
            spell_id="remote_farm",
            patch_id=patch.id,
            crop_id=crop.id,
        )
    return updated, {
        "active_patch_count": active_patch_count,
        "cured_patch_ids": tuple(cured_patch_ids),
        "cured_count": len(cured_patch_ids),
    }


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
    if patch_id == HABITAT_EAST_PATCH_ID:
        for phase in range(len(HABITAT_TRAVERSAL_PHASES)):
            updated["farm_queue"].append({
                "id": _step_id(updated),
                "kind": "habitat_traverse",
                "patch_id": patch_id,
                "phase": phase,
            })
    step_id = _step_id(updated)
    step = {"id": step_id, "kind": kind, "patch_id": patch_id}
    step.update(copy.deepcopy(details))
    if kind == "cure" and "cure_route_preference" not in step:
        plan = _sanitize_plan(updated["farm_plans"].get(patch_id))
        step["cure_route_preference"] = (
            plan["cure_route_preference"]
            if plan is not None
            else PLANT_CURE_ITEM_FIRST
        )
    updated["farm_queue"].append(step)
    return updated, step_id, "queued"


def remove_farm_queue_step_pure(player_data: Mapping[str, Any], step_id: str) -> tuple[dict[str, Any], bool]:
    updated = _copy_with_farm_state(player_data)
    index = next(
        (index for index, step in enumerate(updated["farm_queue"]) if step.get("id") == step_id),
        None,
    )
    if index is None:
        return updated, False
    step = updated["farm_queue"].pop(index)
    _refund_queued_protection(updated, step)
    return updated, True


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
    if patch.fixed_crop_id is not None:
        crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
        if crop is None or not _is_mature(record, crop):
            return [], None, "permanent crop is unavailable"
        if _int(record.get("produce_count")) <= 0:
            return [], None, "no produce is ready"
        return (
            ["harvest"],
            {
                "crop_id": crop.id,
                "compost_tier": "none",
                "protection_intent": False,
                "watering_intent": False,
                "cure_intent": False,
                "cure_route_preference": PLANT_CURE_ITEM_FIRST,
            },
            "queued",
        )
    plan = _sanitize_plan(updated["farm_plans"].get(patch_id)) or _sanitize_plan(record.get("plan"))
    if plan is None:
        return [], None, "patch plan is not set"
    planned_crop = FARMING_CROPS_BY_ID[plan["crop_id"]]
    if not planned_crop.runnable:
        return [], None, f"{planned_crop.display_name} has source-blocked mechanics"
    crop = FARMING_CROPS_BY_ID.get(record.get("crop_id"))
    if crop is None:
        return ["plant"], plan, "queued"
    if record.get("dead") or record.get("stump") or crop.id == "scarecrow":
        return ["clear", "plant"], plan, "queued"
    if record.get("jade_state") == "wild":
        return ["chop"], plan, "queued"
    if record.get("diseased"):
        return (
            (["cure"], plan, "queued")
            if plan.get("cure_intent", True)
            else ([], plan, "auto-cure is disabled")
        )
    if not _is_mature(record, crop):
        return [], plan, "crop is still growing"
    if _is_regrowth_crop(crop) and plan["crop_id"] != crop.id:
        return ["dig_up", "plant"], plan, "queued"
    if crop.patch_type == "tree":
        kinds = [] if record.get("health_checked") else ["check_health"]
        if crop.id == "willow":
            kinds.append("harvest")
        kinds.extend(("chop", "clear", "plant"))
        return kinds, plan, "queued"
    kinds: list[str] = []
    if crop.check_health_xp is not None and not record.get("health_checked"):
        kinds.append("check_health")
    if crop.output_item is None and crop.check_health_xp is not None:
        kinds.extend(("clear", "plant"))
        return kinds, plan, "queued"
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


def _append_planned_steps(
    updated: dict[str, Any],
    patch_id: str,
    kinds: list[str],
    plan: dict[str, Any],
    *,
    protection_paid: bool = False,
    protection_payment: Optional[Mapping[str, int]] = None,
) -> list[str]:
    ids = []
    if patch_id == HABITAT_EAST_PATCH_ID:
        for phase in range(len(HABITAT_TRAVERSAL_PHASES)):
            step_id = _step_id(updated)
            updated["farm_queue"].append({
                "id": step_id,
                "kind": "habitat_traverse",
                "patch_id": patch_id,
                "phase": phase,
            })
            ids.append(step_id)
    for kind in kinds:
        step_id = _step_id(updated)
        step = {"id": step_id, "kind": kind, "patch_id": patch_id}
        if kind == "plant":
            step.update({"crop_id": plan["crop_id"], "compost_tier": plan["compost_tier"]})
            if protection_paid:
                step["protection_paid"] = True
            if protection_payment:
                step["protection_payment"] = dict(protection_payment)
        elif kind == "cure":
            step["cure_route_preference"] = plan["cure_route_preference"]
        elif kind == "chop" and patch_id == JADE_VINE_PATCH_ID:
            step["replant_after"] = True
            step["replant_plan"] = copy.deepcopy(plan)
        updated["farm_queue"].append(step)
        ids.append(step_id)
    return ids


def queue_harvest_and_replant_same_pure(player_data: Mapping[str, Any], patch_id: str) -> tuple[dict[str, Any], tuple[str, ...], str]:
    updated = _copy_with_farm_state(player_data)
    if patch_id not in FARMING_PATCHES_BY_ID:
        return updated, (), "unknown patch"
    if FARMING_PATCHES_BY_ID[patch_id].fixed_crop_id is not None:
        return updated, (), "the permanent quest patch cannot be replanted"
    kinds, plan, message = _planned_patch_steps(updated, patch_id)
    if not kinds or plan is None:
        return updated, (), message
    return updated, tuple(_append_planned_steps(updated, patch_id, kinds, plan)), "queued"


def queue_full_run_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]:
    updated = _copy_with_farm_state(player_data)
    ids: list[str] = []
    skips: list[dict[str, str]] = []
    for patch in FARMING_PATCHES:
        kinds, plan, message = _planned_patch_steps(updated, patch.id)
        if kinds and plan is not None:
            protection_paid = bool(plan.get("protection_paid"))
            protection_payment: dict[str, int] = {}
            if "plant" in kinds and plan.get("protection_intent"):
                planned_crop = FARMING_CROPS_BY_ID[plan["crop_id"]]
                payment = planned_crop.protection
                if payment is None:
                    reason = "planned crop has no gardener protection"
                    skips.append({"patch_id": patch.id, "patch_name": patch.display_name, "reason": reason})
                    _log(updated, "full_run_patch_skipped", f"Skipped {patch.display_name}: {reason}.", patch_id=patch.id)
                    continue
                if not protection_paid:
                    requirements = dict(payment.items)
                    if not _has_items(updated["inventory"], requirements):
                        reason = "missing gardener payment"
                        skips.append({"patch_id": patch.id, "patch_name": patch.display_name, "reason": reason})
                        _log(updated, "full_run_patch_skipped", f"Skipped {patch.display_name}: {reason}.", patch_id=patch.id)
                        continue
                    _consume(updated["inventory"], requirements)
                    protection_paid = True
                    protection_payment = requirements
            ids.extend(
                _append_planned_steps(
                    updated,
                    patch.id,
                    kinds,
                    plan,
                    protection_paid=protection_paid,
                    protection_payment=protection_payment,
                )
            )
        elif plan is not None and message not in {
            "crop is still growing",
            "no produce is ready",
            "auto-cure is disabled",
        }:
            skips.append({"patch_id": patch.id, "patch_name": patch.display_name, "reason": message})
    updated["farm_last_full_run_skips"] = skips
    if ids:
        _increment(updated, "full_runs")
    return updated, tuple(ids)


def _consume_next_farm_queue_step_in_place(
    updated: dict[str, Any],
    random_random: Callable[[], float],
    review_multiplier: int = 1,
) -> tuple[bool, dict[str, Any]]:
    if not updated["farm_queue"]:
        return False, {"status": "empty", "message": "farm queue is empty"}
    step = updated["farm_queue"].pop(0)
    execution_step = step
    if step.get("kind") == "chop" and step.get("patch_id") == JADE_VINE_PATCH_ID:
        execution_step = dict(step)
        execution_step["jade_combat_ticks"] = JADE_VINE_COMBAT_TICKS * max(
            1, _int(review_multiplier, default=1, minimum=1)
        )
    ok, info = _execute_farm_field_step_in_place(updated, execution_step, random_random)
    info["step_id"] = step["id"]
    continuing = bool(ok and info.get("repeat_queue_step"))
    info["status"] = "continuing" if continuing else "executed" if ok else "skipped"
    if continuing:
        updated["farm_queue"].insert(0, step)
    if ok:
        if not continuing:
            _increment(updated, "queue_steps_executed")
    else:
        _refund_queued_protection(updated, step)
        _increment(updated, "queue_steps_skipped")
        _log(updated, "queue_step_skipped", f"Skipped {step.get('kind')}: {info['message']}.", step_id=step["id"], kind=step.get("kind"), patch_id=step.get("patch_id"))
    return True, info


def consume_next_farm_queue_step_pure(
    player_data: Mapping[str, Any],
    random_random: Callable[[], float] = lambda: 1.0,
    review_multiplier: int = 1,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    updated = _copy_with_farm_state(player_data)
    consumed, info = _consume_next_farm_queue_step_in_place(
        updated, random_random, review_multiplier
    )
    return updated, consumed, info


def apply_farming_review_with_queue_pure(
    player_data: Mapping[str, Any],
    random_random: Callable[[], float] = lambda: 1.0,
    review_multiplier: int = 1,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Advance one successful review and consume its queued detour with one copy."""

    updated = _copy_with_farm_state(player_data)
    queue = updated["farm_queue"]
    cure_first = bool(queue and queue[0].get("kind") == "cure")
    if cure_first:
        consumed, info = _consume_next_farm_queue_step_in_place(updated, random_random, review_multiplier)
        _advance_one_farm_card(updated, random_random)
    else:
        _advance_one_farm_card(updated, random_random)
        consumed, info = _consume_next_farm_queue_step_in_place(updated, random_random, review_multiplier)
    return updated, consumed, info


def set_farm_plan_pure(
    player_data: Mapping[str, Any],
    patch_id: str,
    crop_id: str,
    compost_tier: str = "none",
    protection_intent: bool = False,
    watering_intent: bool = True,
    cure_intent: bool = True,
    cure_route_preference: str = PLANT_CURE_ITEM_FIRST,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    patch = FARMING_PATCHES_BY_ID.get(patch_id)
    crop = FARMING_CROPS_BY_ID.get(crop_id)
    if (
        patch is None
        or crop is None
        or compost_tier not in COMPOST_TIERS
        or cure_route_preference not in CURE_ROUTE_PREFERENCES
    ):
        return updated, False, "unknown plan value"
    if patch.fixed_crop_id is not None:
        return updated, False, "permanent quest patches do not use crop plans"
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
        "protection_intent": bool(protection_intent and crop.protection is not None),
        "watering_intent": bool(watering_intent),
        "cure_intent": bool(cure_intent),
        "cure_route_preference": cure_route_preference,
        "protection_paid": bool(existing_plan and existing_plan["crop_id"] == crop_id and existing_plan.get("protection_paid")),
        "fertile_soil_applied": bool(existing_plan and existing_plan["crop_id"] == crop_id and existing_plan.get("fertile_soil_applied")),
    }
    updated["farm_plans"][patch_id] = copy.deepcopy(plan)
    updated["farm_patches"][patch_id]["plan"] = copy.deepcopy(plan)
    return updated, True, "plan saved"


def _next_farm_preset_id(updated: dict[str, Any]) -> str:
    value = updated["farm_next_preset_id"]
    updated["farm_next_preset_id"] = value + 1
    return f"farm_preset_{value:08d}"


def _farm_preset_name_available(
    updated: Mapping[str, Any],
    name: str,
    *,
    excluding_id: Optional[str] = None,
) -> bool:
    normalized = name.casefold()
    return all(
        preset_id == excluding_id or str(preset.get("name", "")).casefold() != normalized
        for preset_id, preset in updated["farm_presets"].items()
    )


def save_farm_preset_pure(
    player_data: Mapping[str, Any],
    name: str,
    patch_ids: Iterable[str],
    preset_id: Optional[str] = None,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    clean_name = str(name).strip()[:60]
    if not clean_name:
        return updated, False, "preset name is required"
    if preset_id is not None and preset_id not in updated["farm_presets"]:
        return updated, False, "preset no longer exists"
    if not _farm_preset_name_available(updated, clean_name, excluding_id=preset_id):
        return updated, False, "preset name already exists"
    plans: dict[str, dict[str, Any]] = {}
    for patch_id in dict.fromkeys(patch_ids):
        if patch_id not in FARMING_PATCHES_BY_ID:
            continue
        if FARMING_PATCHES_BY_ID[patch_id].fixed_crop_id is not None:
            continue
        plan = _preset_plan_snapshot(updated["farm_plans"].get(patch_id))
        if plan is not None:
            plans[patch_id] = plan
    if not plans:
        return updated, False, "choose at least one patch with a saved plan"
    target_id = preset_id or _next_farm_preset_id(updated)
    updated["farm_presets"][target_id] = {
        "id": target_id,
        "name": clean_name,
        "plans": plans,
    }
    if target_id not in updated["farm_preset_order"]:
        updated["farm_preset_order"].append(target_id)
    updated["farm_selected_preset"] = target_id
    return updated, True, "preset updated" if preset_id else "preset saved"


def select_farm_preset_pure(
    player_data: Mapping[str, Any],
    preset_id: Optional[str],
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    if preset_id in {None, ""}:
        changed = updated["farm_selected_preset"] is not None
        updated["farm_selected_preset"] = None
        return updated, changed, "preset selection cleared"
    if preset_id not in updated["farm_presets"]:
        return updated, False, "preset no longer exists"
    updated["farm_selected_preset"] = preset_id
    return updated, True, "preset selected"


def apply_farm_preset_pure(
    player_data: Mapping[str, Any],
    preset_id: Optional[str] = None,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    target_id = preset_id or updated["farm_selected_preset"]
    preset = updated["farm_presets"].get(target_id)
    if preset is None:
        return updated, False, "select a preset first"
    for patch_id, snapshot in preset["plans"].items():
        existing = _sanitize_plan(updated["farm_plans"].get(patch_id))
        if (
            existing
            and existing.get("protection_paid")
            and existing["crop_id"] != snapshot["crop_id"]
        ):
            return updated, False, (
                f"{FARMING_PATCHES_BY_ID[patch_id].display_name} has a legacy "
                "gardener payment tied to its current crop; plant it before replacing that plan."
            )
    for patch_id, snapshot in preset["plans"].items():
        existing = _sanitize_plan(updated["farm_plans"].get(patch_id))
        plan = dict(snapshot)
        same_crop = bool(existing and existing["crop_id"] == plan["crop_id"])
        plan["protection_paid"] = bool(same_crop and existing.get("protection_paid"))
        plan["fertile_soil_applied"] = bool(existing and existing.get("fertile_soil_applied"))
        updated["farm_plans"][patch_id] = copy.deepcopy(plan)
        updated["farm_patches"][patch_id]["plan"] = copy.deepcopy(plan)
    updated["farm_selected_preset"] = target_id
    return updated, True, f"Applied {len(preset['plans'])} patch plans."


def rename_farm_preset_pure(
    player_data: Mapping[str, Any],
    preset_id: str,
    name: str,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    preset = updated["farm_presets"].get(preset_id)
    if preset is None:
        return updated, False, "preset no longer exists"
    clean_name = str(name).strip()[:60]
    if not clean_name:
        return updated, False, "preset name is required"
    if not _farm_preset_name_available(updated, clean_name, excluding_id=preset_id):
        return updated, False, "preset name already exists"
    preset["name"] = clean_name
    return updated, True, "preset renamed"


def duplicate_farm_preset_pure(
    player_data: Mapping[str, Any],
    preset_id: str,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    preset = updated["farm_presets"].get(preset_id)
    if preset is None:
        return updated, False, "preset no longer exists"
    suffix_number = 1
    while True:
        suffix = " copy" if suffix_number == 1 else f" copy {suffix_number}"
        name = f"{preset['name'][:60 - len(suffix)]}{suffix}"
        if _farm_preset_name_available(updated, name):
            break
        suffix_number += 1
    new_id = _next_farm_preset_id(updated)
    updated["farm_presets"][new_id] = {
        "id": new_id,
        "name": name,
        "plans": copy.deepcopy(preset["plans"]),
    }
    updated["farm_preset_order"].append(new_id)
    updated["farm_selected_preset"] = new_id
    return updated, True, "preset duplicated"


def delete_farm_preset_pure(
    player_data: Mapping[str, Any],
    preset_id: str,
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    if preset_id not in updated["farm_presets"]:
        return updated, False, "preset no longer exists"
    updated["farm_presets"].pop(preset_id)
    updated["farm_preset_order"] = [
        value for value in updated["farm_preset_order"] if value != preset_id
    ]
    if updated["farm_selected_preset"] == preset_id:
        updated["farm_selected_preset"] = None
    return updated, True, "preset deleted"


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
    if item_name not in {f"Juju farming potion ({dose})" for dose in range(1, 5)}:
        return _copy_with_farm_state(player_data), False, "not a Juju farming potion"
    updated, result = apply_consumable_pure(player_data, item_name)
    if not result.get("allowed"):
        reason = "not a Juju farming potion" if result.get("reason") == "not_a_consumable" else "missing Juju farming potion"
        return updated, False, reason
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
        is_ready = _is_mature(record, crop) and (
            crop.fixed_yield is None or _int(record.get("produce_count")) > 0
        )
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
        quest_id = str(gate.key)
        display_name = QUEST_DISPLAY_NAMES.get(
            quest_id,
            quest_id.replace("_", " ").title(),
        )
        return f"Requires {display_name}."
    if gate.kind == "skill":
        return f"Requires {str(gate.key).replace('_', ' ').title()} level {gate.minimum}."
    if gate.kind == "region":
        return f"Requires access to {str(gate.key).replace('_', ' ').title()}."
    if gate.kind == "state":
        return "This one-use patch is unavailable."
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
        encounter = record.get("jade_combat_encounter")
        enemy_lp = _int(encounter.get("enemy_lifepoints"), default=2500) if isinstance(encounter, Mapping) and encounter else 2500
        return "ready", f"Wild encounter · {enemy_lp}/2500 LP", 0
    mature = _is_mature(record, crop)
    if mature:
        if crop.check_health_xp is not None and not record.get("health_checked"):
            return "ready", "Health check ready", 0
        if crop.id == "jade_vine":
            branches = _int(record.get("produce_count"))
            next_at = _int(record.get("next_regrowth_at"))
            if not next_at:
                return "growing", "Branch clock not armed", 0
            reviews = max(
                1,
                math.ceil(max(0, next_at - _int(state.get("farm_clock_minutes"))) / FARM_MINUTES_PER_ANSWER),
            )
            review_word = "review" if reviews == 1 else "reviews"
            branch_word = "branch" if branches == 1 else "branches"
            warning = " · next branch makes it wild" if branches == JADE_VINE_VISIBLE_BRANCHES else ""
            if branches:
                return "ready", f"{branches}/{JADE_VINE_VISIBLE_BRANCHES} {branch_word} ready{warning} · next in {reviews} {review_word}", 0
            return "growing", f"0/{JADE_VINE_VISIBLE_BRANCHES} branches · next in {reviews} {review_word}", reviews
        if (
            crop.output_item is not None
            and crop.fixed_yield is not None
            and _int(record.get("produce_count")) <= 0
        ):
            elapsed = max(
                0,
                _int(state.get("farm_clock_minutes"))
                - _int(record.get("last_regrowth_at")),
            )
            interval = crop.regrowth_minutes or FARM_MINUTES_PER_ANSWER
            reviews = max(
                1,
                math.ceil(max(0, interval - elapsed) / FARM_MINUTES_PER_ANSWER),
            )
            review_word = "review" if reviews == 1 else "reviews"
            return (
                "growing",
                f"Regrowing · next produce in about {reviews} {review_word}",
                reviews,
            )
        if crop.patch_type == "tree":
            if crop.id == "willow":
                count = _int(record.get("produce_count"))
                branch_word = "branch" if count == 1 else "branches"
                return (
                    "ready",
                    f"{count}/{crop.fixed_yield} {branch_word} ready · Ready to chop",
                    0,
                )
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
    if step.get("kind") == "habitat_traverse":
        phase = _int(step.get("phase"), minimum=0)
        label = HABITAT_TRAVERSAL_PHASES[phase] if phase < len(HABITAT_TRAVERSAL_PHASES) else "Traverse to the east camp"
        return f"{label} · Herblore Habitat"
    patch = FARMING_PATCHES_BY_ID.get(step.get("patch_id"))
    if step.get("kind") == "chop" and step.get("patch_id") == JADE_VINE_PATCH_ID:
        return "Fight Wild jade vine · Handelmort Mansion"
    verb = str(step.get("kind", "work")).replace("_", " ").title()
    crop = FARMING_CROPS_BY_ID.get(step.get("crop_id"))
    crop_suffix = f" {crop.display_name}" if crop is not None and step.get("kind") == "plant" else ""
    return f"{verb}{crop_suffix} · {patch.display_name if patch else 'Unknown patch'}"


def _jade_policy_label(policy: str) -> str:
    return {
        JADE_POLICY_KEEP_TAME: "Keep tame",
        JADE_POLICY_TRAIN_SLAYER: "Train Slayer",
        JADE_POLICY_TRAIN_FARMING: "Train Farming",
    }.get(policy, "Keep tame")


def _owns_jade_seed_anywhere(player_data: Mapping[str, Any]) -> bool:
    def contains(value: Any) -> bool:
        if isinstance(value, Mapping):
            if _int(value.get("Jade vine seed")) > 0:
                return True
            if value.get("item") == "Jade vine seed" and _int(value.get("quantity", value.get("amount", 1))) > 0:
                return True
            return any(contains(child) for child in value.values())
        if isinstance(value, (tuple, list)):
            return any(contains(child) for child in value)
        return False

    return any(
        contains(player_data.get(key))
        for key in (
            "inventory",
            "carried_inventory",
            "combat_grave",
            "death_office",
        )
    )


def set_jade_vine_policy_pure(
    player_data: Mapping[str, Any], policy: str
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    if not farming_access_gate_allows_pure(
        updated, FARMING_PATCHES_BY_ID[JADE_VINE_PATCH_ID].access_gate
    ):
        return updated, False, "Complete Back to my Roots first."
    if policy not in JADE_VINE_POLICIES:
        return updated, False, "Unknown Jade Vine policy."
    changed = updated.get("farm_jade_vine_policy") != policy
    updated["farm_jade_vine_policy"] = policy
    _remove_jade_prune_steps(updated)
    record = updated["farm_patches"][JADE_VINE_PATCH_ID]
    if policy == JADE_POLICY_KEEP_TAME and record.get("jade_state") == "prunable":
        queued = sum(
            1
            for step in updated["farm_queue"]
            if step.get("patch_id") == JADE_VINE_PATCH_ID and step.get("kind") == "harvest"
        )
        for _ in range(max(0, _int(record.get("produce_count")) - queued)):
            _queue_jade_prune(updated)
    elif (
        policy == JADE_POLICY_TRAIN_FARMING
        and record.get("crop_id") == "jade_vine"
        and record.get("health_checked")
        and record.get("jade_state") == "prunable"
        and _try_horacio_replant(updated, record)
    ):
        return updated, True, "Horacio removed the Jade vine and queued its Plant step."
    if (
        policy == JADE_POLICY_TRAIN_FARMING
        and record.get("crop_id") == "jade_vine"
        and record.get("health_checked")
        and record.get("jade_state") == "prunable"
    ):
        return updated, changed, "Replant blocked: Horacio needs 5 coconuts and 5 watermelons."
    return updated, changed, f"Jade Vine policy: {_jade_policy_label(policy)}."


def claim_jade_vine_seed_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, str]:
    updated = _copy_with_farm_state(player_data)
    if not farming_access_gate_allows_pure(
        updated, FARMING_PATCHES_BY_ID[JADE_VINE_PATCH_ID].access_gate
    ):
        return updated, False, "Complete Back to my Roots first."
    record = updated["farm_patches"][JADE_VINE_PATCH_ID]
    if record.get("crop_id") is not None and not record.get("dead"):
        return updated, False, "A living Jade vine already occupies the patch."
    if _owns_jade_seed_anywhere(updated):
        return updated, False, "You already own a Jade vine seed."
    updated["inventory"]["Jade vine seed"] = 1
    return updated, True, "Horacio gave you a replacement Jade vine seed."


def _farm_preset_modified(state: Mapping[str, Any], preset: Mapping[str, Any]) -> bool:
    return any(
        _preset_plan_snapshot(state["farm_plans"].get(patch_id)) != snapshot
        for patch_id, snapshot in preset.get("plans", {}).items()
    )


def farming_frontend_projection_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Return presentation-ready Farming state; Qt only renders this projection."""

    state = _copy_with_farm_state(player_data)
    inventory = state["inventory"]
    farming_level = _int(state.get("farming_level", 1), default=1, minimum=1)
    livid_scroll_count = _int(inventory.get(LIVID_FARM_PROTECTION_SCROLL))
    livid_protection_crop = FARMING_CROPS_BY_ID.get(
        state.get("farm_livid_protection_crop_id")
    )
    livid_protection_uses = _int(
        state.get("farm_livid_protection_uses_remaining")
    )
    queued_patch_ids = {step.get("patch_id") for step in state["farm_queue"]}
    groups: dict[str, dict[str, Any]] = {}
    active = ready = urgent = 0
    compact_rows: list[dict[str, Any]] = []

    for patch in FARMING_PATCHES:
        if (
            patch.id == LIVID_FARM_ALLOTMENT_PATCH_ID
            and not state["farm_livid_patch_active"]
        ):
            continue
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
            if patch.fixed_crop_id is not None:
                break
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
        if patch.fixed_crop_id is not None:
            if access_allowed and crop is not None and _int(record.get("produce_count")) > 0:
                primary_kind = "harvest"
        elif crop is None:
            primary_kind = "plant" if plan else "choose_plan"
        elif status == "diseased":
            primary_kind = "cure"
        elif status in {"dead", "stump"}:
            primary_kind = "clear"
        elif status == "ready":
            if crop.check_health_xp is not None and not record.get("health_checked"):
                primary_kind = "check_health"
            elif crop.output_item is None and crop.check_health_xp is not None:
                primary_kind = "clear"
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
            item_reason = _missing_items_reason(inventory, {"Plant cure": 1})
            spell_reasons = _cure_spell_locked_reasons(state, patch.id)
            if item_reason and spell_reasons:
                primary_reason = (
                    f"{item_reason}; Cure Plant: {', '.join(spell_reasons)}"
                )
        elif not primary_reason and primary_kind in {"harvest", "clear", "dig_up"}:
            if primary_kind == "harvest" and crop:
                primary_reason = _missing_harvest_tool_reason(inventory, crop)
            else:
                primary_reason = _missing_items_reason(inventory, {"Spade": 1})
        elif not primary_reason and primary_kind == "chop" and crop and crop.id == "jade_vine":
            if _int(state.get("slayer_level", 1), default=1, minimum=1) < 59:
                primary_reason = "Requires Slayer level 59."
            elif _equipped_usable_hatchet(state) is None:
                primary_reason = "Equip a usable hatchet."
            elif not (
                _int(inventory.get("Secateurs")) > 0
                or _int(inventory.get("Magic secateurs")) > 0
                or _toolbelt_has_secateurs(state.get("toolbelt"))
            ):
                primary_reason = "Needs Secateurs in your Bank or toolbelt."

        primary_labels = {
            "choose_plan": "Choose a crop",
            "plant": "Queue plant",
            "cure": "Queue cure",
            "clear": "Queue clear",
            "dig_up": "Queue dig up",
            "check_health": "Queue health check",
            "chop": "Queue chop",
            "harvest": "Queue harvest",
        }
        primary_action = None if primary_kind is None else {
            "id": primary_kind,
            "label": (
                "Queue Wild Vine fight"
                if primary_kind == "chop" and crop and crop.id == "jade_vine"
                else "Queue prune branch"
                if primary_kind == "harvest" and crop and crop.id == "jade_vine"
                else primary_labels[primary_kind]
            ),
            "enabled": primary_kind == "choose_plan" or not primary_reason,
            "locked_reason": primary_reason,
        }
        dig_up_action = None
        if (
            patch.fixed_crop_id is None
            and crop is not None
            and _is_regrowth_crop(crop)
            and _is_mature(record, crop)
            and not record.get("diseased")
            and not record.get("dead")
            and not record.get("stump")
            and record.get("jade_state") != "wild"
        ):
            dig_up_reason = access_reason
            if not dig_up_reason and patch.id in queued_patch_ids:
                dig_up_reason = "This patch already has queued work."
            if not dig_up_reason:
                dig_up_reason = _missing_items_reason(inventory, {"Spade": 1})
            dig_up_action = {
                "id": "dig_up",
                "label": "Queue dig up",
                "enabled": not dig_up_reason,
                "locked_reason": dig_up_reason,
            }

        branch_action = None
        if (
            crop is not None
            and crop.id == "willow"
            and _is_mature(record, crop)
            and record.get("health_checked")
            and not record.get("diseased")
            and not record.get("dead")
            and not record.get("stump")
        ):
            branch_count = _int(record.get("produce_count"))
            branch_reason = access_reason
            if not branch_reason and patch.id in queued_patch_ids:
                branch_reason = "This patch already has queued work."
            if not branch_reason and branch_count <= 0:
                branch_reason = "No willow branches are ready."
            if not branch_reason:
                branch_reason = _missing_harvest_tool_reason(inventory, crop)
            branch_action = {
                "id": "harvest",
                "label": (
                    f"Queue prune {branch_count} "
                    f"{'branch' if branch_count == 1 else 'branches'}"
                    if branch_count > 0
                    else "Queue prune branches"
                ),
                "enabled": not branch_reason,
                "locked_reason": branch_reason,
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
        if crop is not None and record.get("livid_protected"):
            protection["state"] = "Livid scroll"
        elif crop is not None and (record.get("protected") or crop.disease_immune or patch.disease_free):
            protection["state"] = "Protected"
        elif plan and plan.get("protection_paid"):
            protection["state"] = "Protected"
        elif crop is not None and _flower_protected(state, patch.id, crop.id):
            protection["state"] = "Protected by nearby flowers"
        elif payment_crop is not None and payment_crop.protection is not None:
            payment_requirements = dict(payment_crop.protection.items)
            payment_reason = _missing_items_reason(inventory, payment_requirements)
            protection["state"] = (
                "Gardener planned for full run"
                if crop is None and plan and plan.get("protection_intent")
                else "Not paid"
            )
            protection["requirements"] = payment_requirements
            if crop is not None:
                protection["action"] = {
                    "id": "pay_protection",
                    "label": "Pay now",
                    "enabled": not payment_reason and access_allowed,
                    "locked_reason": access_reason or payment_reason,
                }

        livid_protection_action = None
        if (
            crop is not None
            and patch.patch_type in {"tree", "fruit_tree"}
            and (livid_scroll_count > 0 or livid_protection_uses > 0)
        ):
            livid_reason = access_reason
            if not livid_reason and livid_protection_uses > 0:
                livid_reason = (
                    f"Protection for {livid_protection_crop.display_name} is already active."
                    if livid_protection_crop is not None
                    else "Another Livid Farm protection is already active."
                )
            if not livid_reason and livid_scroll_count <= 0:
                livid_reason = "No Patch protection scroll is available."
            if not livid_reason and (
                status == "ready"
                or record.get("diseased")
                or record.get("dead")
                or record.get("stump")
            ):
                livid_reason = "Choose a healthy tree that is still growing."
            if not livid_reason and record.get("protected"):
                livid_reason = "This tree is already protected."
            livid_protection_action = {
                "id": "activate_livid_protection",
                "label": (
                    f"Use {LIVID_FARM_PROTECTION_SCROLL}"
                    if livid_scroll_count <= 1
                    else (
                        f"Use {LIVID_FARM_PROTECTION_SCROLL} "
                        f"({livid_scroll_count})"
                    )
                ),
                "enabled": not livid_reason,
                "locked_reason": livid_reason,
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

        fixed_crop = FARMING_CROPS_BY_ID.get(patch.fixed_crop_id)
        jade_policy = str(state.get("farm_jade_vine_policy", JADE_POLICY_KEEP_TAME))
        jade_status = f"{_jade_policy_label(jade_policy)} · {status_label}"
        if (
            patch.id == JADE_VINE_PATCH_ID
            and jade_policy == JADE_POLICY_TRAIN_FARMING
            and record.get("health_checked")
            and record.get("jade_state") == "prunable"
            and not _has_items(inventory, JADE_VINE_REPLANT_PAYMENT)
        ):
            jade_status = f"Train Farming · Replant blocked: needs 5 coconuts and 5 watermelons · {status_label}"
        jade_seed_claim_reason = ""
        if patch.id == JADE_VINE_PATCH_ID:
            if not access_allowed:
                jade_seed_claim_reason = access_reason
            elif record.get("crop_id") is not None and not record.get("dead"):
                jade_seed_claim_reason = "A living Jade vine occupies the patch."
            elif _owns_jade_seed_anywhere(state):
                jade_seed_claim_reason = "You already own a Jade vine seed."
        patch_view = {
            "patch_id": patch.id,
            "patch_name": patch.display_name,
            "patch_type": patch.patch_type.replace("_", " ").title(),
            "access_allowed": access_allowed,
            "access_reason": access_reason,
            "crop_id": crop.id if crop else None,
            "crop_name": (
                crop.display_name
                if crop
                else fixed_crop.display_name
                if fixed_crop
                else "Empty"
            ),
            "status": status,
            "status_label": access_reason or status_label,
            "stage_label": status_label,
            "queued_count": queued,
            "fixed_crop": patch.fixed_crop_id is not None,
            "produce_count": _int(record.get("produce_count")),
            "produce_capacity": crop.fixed_yield if crop else fixed_crop.fixed_yield if fixed_crop else None,
            "fixed_crop_note": (
                "Permanent post-quest tree · Queue full run harvests all ready fruit · One fruit regrows per answered card."
                if patch.fixed_crop_id is not None
                else ""
            ),
            "current_compost": str(record.get("compost_tier", "none")).replace("_", " ").title(),
            "plan": {
                "crop_id": plan.get("crop_id") if plan else None,
                "crop_name": planned_crop.display_name if planned_crop else "No plan",
                "compost_tier": plan.get("compost_tier", "none") if plan else "none",
                "protection_intent": bool(plan and plan.get("protection_intent")),
                "protection_available": bool(planned_crop and planned_crop.protection is not None),
                "watering_intent": True if plan is None else bool(plan.get("watering_intent", True)),
                "watering_available": bool(planned_crop and planned_crop.patch_type in {"allotment", "flower", "hops"}),
                "cure_intent": True if plan is None else bool(plan.get("cure_intent", True)),
                "cure_route_preference": (
                    PLANT_CURE_ITEM_FIRST
                    if plan is None
                    else plan.get(
                        "cure_route_preference",
                        PLANT_CURE_ITEM_FIRST,
                    )
                ),
            },
            "crop_options": tuple(crop_options),
            "compost_options": tuple({"id": tier_id, "label": tier_id.replace("_", " ").title(), "enabled": True, "locked_reason": ""} for tier_id in COMPOST_TIERS),
            "protection": protection,
            "livid_protection_action": livid_protection_action,
            "primary_action": primary_action,
            "branch_action": branch_action,
            "dig_up_action": dig_up_action,
            "shortcut_action": (
                None
                if patch.fixed_crop_id is not None or patch.id == JADE_VINE_PATCH_ID
                else {
                    "id": "harvest_replant",
                    "label": "Harvest and replant same",
                    "enabled": plan is None or not shortcut_reason,
                    "locked_reason": shortcut_reason,
                    "needs_plan": plan is None,
                }
            ),
            "sapling_action": sapling,
            "jade_vine": (
                {
                    "policy": jade_policy,
                    "policy_options": (
                        {"id": JADE_POLICY_KEEP_TAME, "label": "Keep tame — prune branches"},
                        {"id": JADE_POLICY_TRAIN_SLAYER, "label": "Train Slayer — let it grow wild"},
                        {
                            "id": JADE_POLICY_TRAIN_FARMING,
                            "label": "Train Farming — Horacio: 5 coconuts + 5 watermelons",
                        },
                    ),
                    "policy_enabled": access_allowed,
                    "policy_locked_reason": access_reason,
                    "confirm_train_farming": bool(
                        record.get("crop_id") == "jade_vine"
                        and record.get("health_checked")
                        and record.get("jade_state") == "prunable"
                        and _has_items(inventory, JADE_VINE_REPLANT_PAYMENT)
                    ),
                    "status": jade_status,
                    "claim_seed": {} if not jade_seed_claim_reason else None,
                }
                if patch.id == JADE_VINE_PATCH_ID
                else None
            ),
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
    preview_skips = tuple(preview_state.get("farm_last_full_run_skips", ()))
    preset_rows = tuple(
        {
            "id": preset_id,
            "name": state["farm_presets"][preset_id]["name"],
            "patch_count": len(state["farm_presets"][preset_id]["plans"]),
            "selected": preset_id == state["farm_selected_preset"],
            "modified": _farm_preset_modified(state, state["farm_presets"][preset_id]),
            "patch_ids": tuple(state["farm_presets"][preset_id]["plans"]),
        }
        for preset_id in state["farm_preset_order"]
        if preset_id in state["farm_presets"]
    )
    selected_preset = next((row for row in preset_rows if row["selected"]), None)
    juju_item_name = next(
        (
            f"Juju farming potion ({dose})"
            for dose in range(4, 0, -1)
            if _int(inventory.get(f"Juju farming potion ({dose})")) > 0
        ),
        None,
    )
    juju_active = _juju_farming_active(state)
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
        "presets": {
            "rows": preset_rows,
            "selected_id": selected_preset["id"] if selected_preset else None,
            "selected_name": selected_preset["name"] if selected_preset else "No preset",
            "modified": bool(selected_preset and selected_preset["modified"]),
            "can_apply": selected_preset is not None,
            "planned_patch_ids": tuple(
                patch.id for patch in FARMING_PATCHES if patch.id in state["farm_plans"]
            ),
        },
        "full_run": {
            "enabled": bool(preview_ids or preview_skips),
            "count": len(preview_ids),
            "skips": preview_skips,
            "preview": (
                f"{len(preview_ids)} steps ready · {len(preview_skips)} patch"
                f"{'es' if len(preview_skips) != 1 else ''} skipped"
                if preview_skips
                else f"{len(preview_ids)} steps ready to queue"
                if preview_ids
                else "No planned work is ready."
            ),
            "locked_reason": (
                ""
                if preview_ids
                else f"No steps can be queued; {len(preview_skips)} planned patch"
                f"{'es' if len(preview_skips) != 1 else ''} would be skipped."
                if preview_skips
                else "No planned work is ready."
            ),
        },
        "juju_potion": {
            "item_name": juju_item_name,
            "active": juju_active,
            "enabled": juju_item_name is not None and not juju_active,
            "label": (
                "Juju harvest bonus active"
                if juju_active
                else f"Drink {juju_item_name}"
                if juju_item_name
                else "No Juju farming potion"
            ),
            "locked_reason": (
                "The Juju harvest bonus is already active."
                if juju_active
                else "No Juju farming potion doses are available in your Bank."
                if juju_item_name is None
                else ""
            ),
        },
        "livid_protection": {
            "scroll_count": livid_scroll_count,
            "crop_id": livid_protection_crop.id if livid_protection_crop else None,
            "crop_name": (
                livid_protection_crop.display_name
                if livid_protection_crop
                else None
            ),
            "uses_remaining": livid_protection_uses,
            "label": (
                f"Livid protection · {livid_protection_crop.display_name} · "
                f"{livid_protection_uses} planting"
                f"{'s' if livid_protection_uses != 1 else ''} left"
                if livid_protection_crop and livid_protection_uses
                else (
                    f"Patch protection scroll"
                    f"{'s' if livid_scroll_count != 1 else ''} · "
                    f"{livid_scroll_count}"
                )
                if livid_scroll_count
                else ""
            ),
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
    if action_id == "set_jade_vine_policy":
        return set_jade_vine_policy_pure(
            player_data, str(data.get("policy", ""))
        )
    if action_id == "claim_jade_vine_seed":
        return claim_jade_vine_seed_pure(player_data)
    if action_id == "set_plan":
        crop_id = str(data.get("crop_id", ""))
        option = next((row for row in (patch_view or {}).get("crop_options", ()) if row["id"] == crop_id), None)
        if option is None or not option["enabled"]:
            return _copy_with_farm_state(player_data), False, (option or {}).get("locked_reason") or "That crop is not available for this patch."
        return set_farm_plan_pure(
            player_data, patch_id, crop_id,
            str(data.get("compost_tier", "none")), bool(data.get("protection_intent", False)),
            bool(data.get("watering_intent", True)), bool(data.get("cure_intent", True)),
            str(data.get("cure_route_preference", PLANT_CURE_ITEM_FIRST)),
        )
    if action_id == "pay_protection":
        return pay_farming_protection_pure(player_data, patch_id)
    if action_id == "activate_livid_protection":
        action = (patch_view or {}).get("livid_protection_action")
        if not action or not action.get("enabled"):
            return (
                _copy_with_farm_state(player_data),
                False,
                (action or {}).get("locked_reason")
                or "Livid Farm protection is unavailable for this patch.",
            )
        return activate_livid_farm_patch_protection_pure(
            player_data,
            patch_id,
        )
    if action_id == "activate_juju_farming_potion":
        return activate_juju_farming_potion_pure(
            player_data, str(data.get("item_name", "Juju farming potion (3)"))
        )
    if action_id == "queue_action":
        kind = str(data.get("kind", ""))
        primary = (patch_view or {}).get("primary_action")
        action = (
            primary
            if primary and primary.get("id") == kind
            else (patch_view or {}).get("branch_action")
            if kind == "harvest"
            else (patch_view or {}).get("dig_up_action")
            if kind == "dig_up"
            else None
        )
        if not action or action.get("id") != kind or not action.get("enabled"):
            return _copy_with_farm_state(player_data), False, (action or {}).get("locked_reason") or "That action is no longer available."
        details = dict(data.get("details") or {})
        updated, step_id, message = add_farm_queue_step_pure(player_data, kind, patch_id, **details)
        return updated, step_id is not None, "Added 1 step to the queue." if step_id else message
    if action_id == "harvest_replant":
        shortcut = (patch_view or {}).get("shortcut_action") or {}
        if not shortcut.get("enabled") or shortcut.get("needs_plan"):
            return _copy_with_farm_state(player_data), False, shortcut.get("locked_reason") or "Choose a crop, compost tier, and protection plan first."
        updated, ids, message = queue_harvest_and_replant_same_pure(player_data, patch_id)
        return updated, bool(ids), f"Added {len(ids)} steps to the queue." if ids else message
    if action_id == "queue_full_run":
        if not projection["full_run"]["enabled"]:
            return _copy_with_farm_state(player_data), False, projection["full_run"]["locked_reason"]
        updated, ids = queue_full_run_pure(player_data)
        skips = updated.get("farm_last_full_run_skips", ())
        message = f"Queued {len(ids)} Farming steps."
        if skips:
            message += " Skipped " + ", ".join(
                f"{row['patch_name']} ({row['reason']})" for row in skips
            ) + "."
        return (
            updated,
            bool(ids or skips),
            message if ids or skips else "Nothing was queued; no planned patches need work.",
        )
    if action_id == "save_preset":
        return save_farm_preset_pure(
            player_data,
            str(data.get("name", "")),
            tuple(str(value) for value in data.get("patch_ids", ()) if isinstance(value, str)),
            str(data.get("preset_id")) if data.get("preset_id") else None,
        )
    if action_id == "select_preset":
        return select_farm_preset_pure(
            player_data,
            str(data.get("preset_id")) if data.get("preset_id") else None,
        )
    if action_id == "apply_preset":
        return apply_farm_preset_pure(
            player_data,
            str(data.get("preset_id")) if data.get("preset_id") else None,
        )
    if action_id == "rename_preset":
        return rename_farm_preset_pure(
            player_data,
            str(data.get("preset_id", "")),
            str(data.get("name", "")),
        )
    if action_id == "duplicate_preset":
        return duplicate_farm_preset_pure(player_data, str(data.get("preset_id", "")))
    if action_id == "delete_preset":
        return delete_farm_preset_pure(player_data, str(data.get("preset_id", "")))
    if action_id == "queue_remove":
        updated, ok = remove_farm_queue_step_pure(player_data, str(data.get("step_id", "")))
        return updated, ok, "Removed the queued step." if ok else "That queued step is no longer available."
    if action_id == "queue_move":
        updated, ok = reorder_farm_queue_step_pure(player_data, str(data.get("step_id", "")), _int(data.get("new_index")))
        return updated, ok, "Moved the queued step." if ok else "That queued step is no longer available."
    if action_id == "queue_clear":
        updated = _copy_with_farm_state(player_data)
        changed = bool(updated["farm_queue"])
        for step in updated["farm_queue"]:
            _refund_queued_protection(updated, step)
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
