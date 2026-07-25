"""logic_pure_telemetry.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..logic_pure.logic_pure_state import (  # noqa: F401  (re-export)
    COMBAT_BANK_RUN_REVIEWS,
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
    _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
    _COMBAT_STAT_POTION_BY_DOSE,
    _COMBAT_STAT_POTION_ITEM_NAMES,
    _build_combat_potion_dose_lookup,
    _combat_grave_items,
    _combat_stored_loadout,
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
    _positive_int,
    _requirements_from_spec,
    _sanitize_combat_bank_run,
    _sanitize_combat_grave_state,
    _sanitize_combat_supply_loadout,
    _sanitize_death_office_state,
    _signed_int,
    default_combat_supply_loadout_pure,
    quest_completed_pure,
    quest_state_pure,
    sanitize_quest_combat_active_encounters_pure,
)

from ..logic_pure.logic_pure_state import (
    _non_negative_float,
    _non_negative_int,
    _positive_int,
)


def default_action_telemetry_pure():
    return {"version": 1, "actions": {}}


def default_achievement_progress_pure():
    """Durable action-owner progress used by cumulative achievements."""
    return {"version": 1, "skills": {}}


def sanitize_achievement_progress_pure(progress):
    sanitized = default_achievement_progress_pure()
    if not isinstance(progress, Mapping):
        return sanitized
    raw_skills = progress.get("skills", {})
    if not isinstance(raw_skills, Mapping):
        return sanitized
    skills = {}
    for skill_id, raw_record in raw_skills.items():
        if not isinstance(skill_id, str) or not isinstance(raw_record, Mapping):
            continue
        actions = raw_record.get("actions", {})
        outputs = raw_record.get("outputs", {})
        skills[skill_id] = {
            "actions": {
                str(action_id): _non_negative_int(amount, 0)
                for action_id, amount in actions.items()
                if isinstance(action_id, str)
            } if isinstance(actions, Mapping) else {},
            "outputs": {
                str(item_name): _non_negative_int(amount, 0)
                for item_name, amount in outputs.items()
                if isinstance(item_name, str)
            } if isinstance(outputs, Mapping) else {},
        }
    sanitized["skills"] = skills
    return sanitized


def record_achievement_progress_pure(
    player_data,
    skill_id,
    action_id,
    success,
    *,
    output_item=None,
    output_qty=1,
    output_items=None,
):
    """Record cumulative credit under the explicit action-owning skill."""
    progress = sanitize_achievement_progress_pure(player_data.get("achievement_progress"))
    player_data["achievement_progress"] = progress
    skills = progress.setdefault("skills", {})
    owner = str(skill_id)
    record = skills.setdefault(owner, {"actions": {}, "outputs": {}})
    if not bool(success):
        return record

    actions = dict(record.get("actions", {}) or {})
    action_key = str(action_id)
    actions[action_key] = _non_negative_int(actions.get(action_key, 0), 0) + 1
    record["actions"] = actions

    outputs = dict(record.get("outputs", {}) or {})
    if isinstance(output_items, Mapping):
        for item_name, amount in output_items.items():
            if not item_name:
                continue
            qty = _non_negative_int(amount, 0)
            if qty <= 0:
                continue
            key = str(item_name)
            outputs[key] = _non_negative_int(outputs.get(key, 0), 0) + qty
    elif output_item:
        qty = _non_negative_int(output_qty, 0)
        if qty > 0:
            key = str(output_item)
            outputs[key] = _non_negative_int(outputs.get(key, 0), 0) + qty
    record["outputs"] = outputs
    return record


def sanitize_action_telemetry_pure(telemetry):
    sanitized = default_action_telemetry_pure()
    if not isinstance(telemetry, Mapping):
        return sanitized
    raw_actions = telemetry.get("actions", {})
    if not isinstance(raw_actions, Mapping):
        return sanitized
    actions = {}
    for key, raw_record in raw_actions.items():
        if not isinstance(key, str) or not isinstance(raw_record, Mapping):
            continue
        record = dict(raw_record)
        record.setdefault("skill_id", key.split(":", 1)[0])
        record.setdefault("action_id", key.split(":", 1)[1] if ":" in key else key)
        record["attempts"] = _non_negative_int(record.get("attempts", 0), 0)
        record["successes"] = _non_negative_int(record.get("successes", 0), 0)
        record["failures"] = _non_negative_int(record.get("failures", 0), 0)
        if "cadence_waits" in record:
            record["cadence_waits"] = _non_negative_int(
                record.get("cadence_waits", 0),
                0,
            )
        record["expected_successes"] = _non_negative_float(record.get("expected_successes", 0.0), 0.0)
        record["current_dry_streak"] = _non_negative_int(record.get("current_dry_streak", 0), 0)
        record["longest_dry_streak"] = _non_negative_int(record.get("longest_dry_streak", 0), 0)
        if not isinstance(record.get("outputs"), Mapping):
            record["outputs"] = {}
        if not isinstance(record.get("failure_kinds"), Mapping):
            record["failure_kinds"] = {}
        actions[key] = record
    sanitized["actions"] = actions
    return sanitized


def action_telemetry_key_pure(skill_id, action_id):
    return f"{str(skill_id)}:{str(action_id)}"


def record_action_telemetry_pure(
    player_data,
    skill_id,
    action_id,
    success,
    *,
    expected_success_chance=None,
    output_item=None,
    output_qty=1,
    output_items=None,
    failure_kind=None,
):
    """Record one started review action and return its action telemetry row."""
    telemetry = sanitize_action_telemetry_pure(player_data.get("action_telemetry"))
    player_data["action_telemetry"] = telemetry
    actions = telemetry.setdefault("actions", {})
    key = action_telemetry_key_pure(skill_id, action_id)
    record = actions.setdefault(
        key,
        {
            "skill_id": str(skill_id),
            "action_id": str(action_id),
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "expected_successes": 0.0,
            "current_dry_streak": 0,
            "longest_dry_streak": 0,
            "outputs": {},
            "failure_kinds": {},
        },
    )
    record["attempts"] = _non_negative_int(record.get("attempts", 0), 0) + 1
    is_success = bool(success)
    record["last_success"] = is_success

    if expected_success_chance is not None:
        try:
            expected = float(expected_success_chance)
        except (TypeError, ValueError):
            expected = 0.0
        expected = max(0.0, min(expected, 1.0))
        record["expected_successes"] = _non_negative_float(record.get("expected_successes", 0.0), 0.0) + expected
        record["last_expected_success_chance"] = expected

    if is_success:
        record["successes"] = _non_negative_int(record.get("successes", 0), 0) + 1
        record["current_dry_streak"] = 0
        record.pop("last_failure_kind", None)
    else:
        record["failures"] = _non_negative_int(record.get("failures", 0), 0) + 1
        dry_streak = _non_negative_int(record.get("current_dry_streak", 0), 0) + 1
        record["current_dry_streak"] = dry_streak
        record["longest_dry_streak"] = max(_non_negative_int(record.get("longest_dry_streak", 0), 0), dry_streak)
        kind = str(failure_kind or "dry")
        failure_kinds = dict(record.get("failure_kinds", {}) or {})
        failure_kinds[kind] = _non_negative_int(failure_kinds.get(kind, 0), 0) + 1
        record["failure_kinds"] = failure_kinds
        record["last_failure_kind"] = kind

    outputs = dict(record.get("outputs", {}) or {})
    if isinstance(output_items, Mapping):
        for item_name, amount in output_items.items():
            if not item_name:
                continue
            qty = _positive_int(amount, 1)
            outputs[str(item_name)] = _non_negative_int(outputs.get(str(item_name), 0), 0) + qty
            record["last_output_item"] = str(item_name)
    elif output_item:
        qty = _positive_int(output_qty, 1)
        outputs[str(output_item)] = _non_negative_int(outputs.get(str(output_item), 0), 0) + qty
        record["last_output_item"] = str(output_item)
    record["outputs"] = outputs
    return record


def record_cadence_wait_telemetry_pure(player_data, skill_id, action_id):
    """Record admission delay without fabricating an attempted action or dry streak."""
    telemetry = sanitize_action_telemetry_pure(player_data.get("action_telemetry"))
    player_data["action_telemetry"] = telemetry
    key = action_telemetry_key_pure(skill_id, action_id)
    record = telemetry.setdefault("actions", {}).setdefault(
        key,
        {
            "skill_id": str(skill_id),
            "action_id": str(action_id),
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "expected_successes": 0.0,
            "current_dry_streak": 0,
            "longest_dry_streak": 0,
            "outputs": {},
            "failure_kinds": {},
        },
    )
    record["cadence_waits"] = _non_negative_int(record.get("cadence_waits", 0), 0) + 1
    record["last_outcome"] = "cadence_wait"
    return record


def summarize_action_telemetry_pure(player_data):
    telemetry = sanitize_action_telemetry_pure(player_data.get("action_telemetry"))
    rows = []
    for key, record in sorted(telemetry.get("actions", {}).items()):
        attempts = _non_negative_int(record.get("attempts", 0), 0)
        successes = _non_negative_int(record.get("successes", 0), 0)
        expected_successes = _non_negative_float(record.get("expected_successes", 0.0), 0.0)
        rows.append(
            {
                "key": key,
                "skill_id": record.get("skill_id", key.split(":", 1)[0]),
                "action_id": record.get("action_id", key.split(":", 1)[1] if ":" in key else key),
                "attempts": attempts,
                "successes": successes,
                "failures": _non_negative_int(record.get("failures", 0), 0),
                "cadence_waits": _non_negative_int(record.get("cadence_waits", 0), 0),
                "observed_success_rate": (successes / attempts) if attempts else 0.0,
                "expected_success_rate": (expected_successes / attempts) if attempts else 0.0,
                "current_dry_streak": _non_negative_int(record.get("current_dry_streak", 0), 0),
                "longest_dry_streak": _non_negative_int(record.get("longest_dry_streak", 0), 0),
                "outputs": dict(record.get("outputs", {}) or {}),
                "failure_kinds": dict(record.get("failure_kinds", {}) or {}),
            }
        )
    return tuple(rows)
