"""Pure shared brawling-glove charge, XP, and Wilderness-risk behavior."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.brawling_gloves_data import BRAWLING_GLOVE_DATA
from ..data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from .equipment_instance_logic import sanitize_equipment_instance_state_pure
from ..logic_pure.logic_pure_thieving import apply_thieving_damage_pure


BRAWLING_WILDERNESS_AMBUSH_CHANCE = 0.01
BRAWLING_WILDERNESS_MAX_HIT_LP = 250


def default_brawling_gloves_state_pure() -> dict[str, object]:
    return {"brawling_wilderness_targets": {}}


def sanitize_brawling_gloves_state_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    data = dict(player_data)
    cleaned: dict[str, dict[str, bool]] = {}
    raw = player_data.get("brawling_wilderness_targets", {})
    if isinstance(raw, Mapping):
        for skill_id in BRAWLING_GLOVE_DATA:
            targets = raw.get(skill_id, {})
            if not isinstance(targets, Mapping):
                continue
            enabled = {
                str(target_id): True
                for target_id, value in targets.items()
                if isinstance(target_id, str) and target_id and value is True
            }
            if enabled:
                cleaned[skill_id] = enabled
    data["brawling_wilderness_targets"] = cleaned
    return data


def set_brawling_wilderness_target_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    target_id: str,
    enabled: bool,
) -> dict[str, Any]:
    data = sanitize_brawling_gloves_state_pure(player_data)
    if skill_id not in BRAWLING_GLOVE_DATA or not isinstance(target_id, str) or not target_id:
        return data
    policies = {
        key: dict(value)
        for key, value in data["brawling_wilderness_targets"].items()
    }
    targets = policies.setdefault(skill_id, {})
    if enabled:
        targets[target_id] = True
    else:
        targets.pop(target_id, None)
        if not targets:
            policies.pop(skill_id, None)
    data["brawling_wilderness_targets"] = policies
    return data


def brawling_wilderness_enabled_pure(
    player_data: Mapping[str, Any], skill_id: str, target_id: str
) -> bool:
    policies = player_data.get("brawling_wilderness_targets", {})
    if not isinstance(policies, Mapping):
        return False
    targets = policies.get(skill_id, {})
    return isinstance(targets, Mapping) and targets.get(target_id) is True


def brawling_glove_state_pure(
    player_data: Mapping[str, Any], skill_id: str
) -> dict[str, Any]:
    spec = BRAWLING_GLOVE_DATA.get(skill_id)
    if spec is None:
        return {"active": False}
    data = sanitize_equipment_instance_state_pure(
        player_data, EQUIPMENT_CONDITION_DATA
    )
    item_name = spec["item_name"]
    if (data.get("equipment", {}) or {}).get("hands") != item_name:
        return {
            "active": False,
            "item_name": item_name,
            "max_actions": spec["max_actions"],
        }
    family_id = f"brawling_{skill_id}"
    for instance_id, record in data.get("equipment_instances", {}).items():
        if (
            record.get("family_id") == family_id
            and record.get("location") == "equipped:hands"
        ):
            return {
                "active": True,
                "instance_id": instance_id,
                "item_name": item_name,
                "remaining_actions": int(record.get("condition", 0) or 0),
                "max_actions": spec["max_actions"],
                "outside_multiplier": spec["outside_multiplier"],
                "wilderness_multiplier": spec["wilderness_multiplier"],
            }
    return {"active": False, "item_name": item_name, "max_actions": spec["max_actions"]}


def apply_brawling_gloves_xp_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    target_id: str,
    base_xp: float,
) -> tuple[dict[str, Any], float, dict[str, Any]]:
    data = sanitize_equipment_instance_state_pure(
        sanitize_brawling_gloves_state_pure(player_data),
        EQUIPMENT_CONDITION_DATA,
    )
    try:
        xp = max(0.0, float(base_xp))
    except (TypeError, ValueError, OverflowError):
        xp = 0.0
    state = brawling_glove_state_pure(data, skill_id)
    if xp <= 0 or not state.get("active"):
        return data, xp, {"applied": False}

    wilderness = brawling_wilderness_enabled_pure(data, skill_id, target_id)
    multiplier_key = "wilderness_multiplier" if wilderness else "outside_multiplier"
    multiplier = float(state[multiplier_key])
    instance_id = str(state["instance_id"])
    instances = {
        key: dict(value)
        for key, value in data.get("equipment_instances", {}).items()
    }
    record = instances[instance_id]
    remaining = max(0, int(record.get("condition", 0) or 0) - 1)
    disintegrated = remaining == 0
    if disintegrated:
        instances.pop(instance_id, None)
        equipment = dict(data.get("equipment", {}) or {})
        equipment.pop("hands", None)
        data["equipment"] = equipment
    else:
        record["condition"] = remaining
        instances[instance_id] = record
    data["equipment_instances"] = instances
    return data, xp * multiplier, {
        "applied": True,
        "item_name": state["item_name"],
        "multiplier": multiplier,
        "wilderness": wilderness,
        "remaining_actions": remaining,
        "disintegrated": disintegrated,
    }


def apply_brawling_wilderness_risk_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    target_id: str,
    trigger_roll: float,
    damage_roll: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = sanitize_brawling_gloves_state_pure(player_data)
    if not brawling_wilderness_enabled_pure(data, skill_id, target_id):
        return data, {"triggered": False}
    try:
        triggered = float(trigger_roll) < BRAWLING_WILDERNESS_AMBUSH_CHANCE
    except (TypeError, ValueError, OverflowError):
        triggered = False
    if not triggered:
        return data, {"triggered": False}
    try:
        normalized_damage = max(0.0, min(float(damage_roll), 0.999999999))
    except (TypeError, ValueError, OverflowError):
        normalized_damage = 0.0
    damage = 1 + int(normalized_damage * BRAWLING_WILDERNESS_MAX_HIT_LP)
    damaged, result = apply_thieving_damage_pure(
        data,
        damage,
        source="brawling_wilderness_pker",
        carried_target_id=target_id,
    )
    return damaged, {"triggered": True, **result}
