"""Pure Slayer assignment, progress, and management operations."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Tuple

from ..logic_pure.achievement_diary_events import record_direct_diary_event_pure
from ..data.slayer_data import (
    DEFAULT_SLAYER_MASTER_ID,
    SLAYER_FAMILIES_BY_ID,
    SLAYER_MASTERS_BY_ID,
    SlayerAssignmentFamily,
)
from ..logic_pure.logic_pure_state import quest_completed_pure, quest_state_pure


def _non_negative_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default


def _positive_int(value: Any, default: int = 1) -> int:
    return max(1, _non_negative_int(value, default))


def _roll_unit(rng: Callable[[], float]) -> float:
    try:
        return max(0.0, min(0.999999999999, float(rng())))
    except (TypeError, ValueError):
        return 0.0


def _quest_started(player_data: Mapping[str, Any], quest_id: str) -> bool:
    state = quest_state_pure(player_data, quest_id)
    return bool(state["started"] or state["completed"])


_QUEST_DISPLAY_NAMES = {
    "priest_in_peril": "Priest in Peril",
}


def slayer_master_persona_pure(
    player_data: Mapping[str, Any],
    master_id: str = DEFAULT_SLAYER_MASTER_ID,
) -> Tuple[str, str]:
    master = SLAYER_MASTERS_BY_ID.get(master_id)
    if master is None:
        return str(master_id), ""
    if master.alternate_display_name:
        condition = master.alternate_display_condition
        if condition == "while_guthix_sleeps_completed" and quest_completed_pure(
            player_data, "while_guthix_sleeps"
        ):
            return master.alternate_display_name, master.alternate_chathead_asset_path
        if condition == "while_guthix_sleeps_in_progress" and _quest_started(
            player_data, "while_guthix_sleeps"
        ):
            return master.alternate_display_name, master.alternate_chathead_asset_path
    return master.display_name, master.chathead_asset_path


def slayer_master_display_name_pure(
    player_data: Mapping[str, Any],
    master_id: str = DEFAULT_SLAYER_MASTER_ID,
) -> str:
    return slayer_master_persona_pure(player_data, master_id)[0]


def slayer_family_locked_reasons_pure(
    player_data: Mapping[str, Any],
    family: SlayerAssignmentFamily,
) -> Tuple[str, ...]:
    reasons = []
    slayer_level = _positive_int(player_data.get("slayer_level", 1), 1)
    if slayer_level < family.required_slayer_level:
        reasons.append(f"Slayer level {family.required_slayer_level}")
    if family.required_quest_id and not quest_completed_pure(
        player_data, family.required_quest_id
    ):
        reasons.append(
            "Complete "
            + _QUEST_DISPLAY_NAMES.get(
                family.required_quest_id,
                family.required_quest_id.replace("_", " ").title(),
            )
        )
    for skill_id, required_level in family.required_skill_levels:
        if _positive_int(player_data.get(f"{skill_id}_level", 1), 1) < required_level:
            reasons.append(f"{skill_id.replace('_', ' ').title()} level {required_level}")
    for skill_ids, required_total in family.required_skill_totals:
        current_total = sum(
            _positive_int(player_data.get(f"{skill_id}_level", 1), 1)
            for skill_id in skill_ids
        )
        if current_total < required_total:
            names = " + ".join(skill_id.replace("_", " ").title() for skill_id in skill_ids)
            reasons.append(f"{names} total {required_total}")
    return tuple(reasons)


def eligible_slayer_families_pure(
    player_data: Mapping[str, Any],
    master_id: str = DEFAULT_SLAYER_MASTER_ID,
) -> Tuple[SlayerAssignmentFamily, ...]:
    master = SLAYER_MASTERS_BY_ID.get(master_id)
    if master is None or not master.runtime_enabled:
        return ()
    return tuple(
        family
        for family in master.assignments
        if not slayer_family_locked_reasons_pure(player_data, family)
    )


def sanitize_slayer_state_pure(player_data: Mapping[str, Any]) -> dict:
    # Shallow on purpose: this returns the whole save and rebuilds only the
    # slayer_* keys, so every OTHER nested value stays aliased to the caller's
    # mapping. Callers may assign top-level keys freely, but must never write
    # through a nested value they did not rebuild here.
    data = dict(player_data)
    assignment_raw = data.get("slayer_assignment")
    assignment = dict(assignment_raw) if isinstance(assignment_raw, Mapping) else {}
    family_id = str(assignment.get("family_id", "") or "")
    master_id = str(assignment.get("master_id", "") or "")
    family = SLAYER_FAMILIES_BY_ID.get(family_id)
    master = SLAYER_MASTERS_BY_ID.get(master_id)
    if (
        family is None
        or master is None
        or not master.runtime_enabled
        or family_id not in master.family_ids
    ):
        assignment = {}
    else:
        initial = _positive_int(assignment.get("initial_count", 1), 1)
        remaining = min(
            initial, _non_negative_int(assignment.get("remaining", initial), initial)
        )
        assignment = {
            "master_id": master_id,
            "family_id": family_id,
            "initial_count": initial,
            "remaining": remaining,
            "completed": remaining == 0,
        }
    data["slayer_assignment"] = assignment
    last_family_id = str(data.get("slayer_last_family_id", "") or "")
    data["slayer_last_family_id"] = (
        last_family_id if last_family_id in SLAYER_FAMILIES_BY_ID else ""
    )
    data["slayer_tasks_completed"] = _non_negative_int(
        data.get("slayer_tasks_completed", 0)
    )
    data["slayer_points"] = _non_negative_int(data.get("slayer_points", 0))
    data["slayer_qualifying_streak"] = _non_negative_int(
        data.get("slayer_qualifying_streak", 0)
    )
    data["slayer_combat_filter"] = bool(data.get("slayer_combat_filter", False))
    return data


def slayer_assignment_progress_pure(player_data: Mapping[str, Any]) -> str:
    assignment = sanitize_slayer_state_pure(player_data)["slayer_assignment"]
    if not assignment or assignment["completed"]:
        return ""
    return f"Slayer: {assignment['remaining']} of {assignment['initial_count']} left"


def get_slayer_assignment_pure(
    player_data: Mapping[str, Any],
    *,
    master_id: str = DEFAULT_SLAYER_MASTER_ID,
    rng: Callable[[], float],
) -> tuple[dict, bool, dict]:
    data = sanitize_slayer_state_pure(player_data)
    current = data.get("slayer_assignment") or {}
    if _non_negative_int(current.get("remaining", 0)) > 0:
        return data, False, {"reason": "assignment_active"}

    families = list(eligible_slayer_families_pure(data, master_id))
    if not families:
        return data, False, {"reason": "no_eligible_assignments"}
    previous = str(data.get("slayer_last_family_id", "") or "")
    without_previous = [family for family in families if family.id != previous]
    if without_previous:
        families = without_previous

    total_weight = sum(family.weight for family in families)
    cursor = _roll_unit(rng) * total_weight
    family = families[-1]
    for candidate in families:
        cursor -= candidate.weight
        if cursor < 0:
            family = candidate
            break

    count_span = family.count_max - family.count_min + 1
    count = family.count_min + int(_roll_unit(rng) * count_span)
    assignment = {
        "master_id": master_id,
        "family_id": family.id,
        "initial_count": count,
        "remaining": count,
        "completed": False,
    }
    data["slayer_assignment"] = assignment
    record_direct_diary_event_pure(
        data, True, "slayer_command", action_id="get_assignment", reason="assignment_started"
    )
    return data, True, {
        "reason": "assignment_started",
        "assignment": dict(assignment),
        "family_display_name": family.display_name,
        "master_display_name": slayer_master_display_name_pure(data, master_id),
    }


def slayer_target_ids_for_assignment_pure(
    player_data: Mapping[str, Any],
) -> Tuple[str, ...]:
    data = sanitize_slayer_state_pure(player_data)
    assignment = data.get("slayer_assignment") or {}
    if _non_negative_int(assignment.get("remaining", 0)) <= 0:
        return ()
    family = SLAYER_FAMILIES_BY_ID.get(
        str(assignment.get("family_id", "") or "")
    )
    return family.target_ids if family else ()


def apply_slayer_kills_pure(
    player_data: Mapping[str, Any],
    *,
    target_id: str,
    kills: int,
    enemy_data: Mapping[str, Mapping[str, Any]],
) -> tuple[dict, dict]:
    data = sanitize_slayer_state_pure(player_data)
    assignment = dict(data.get("slayer_assignment") or {})
    remaining = _non_negative_int(assignment.get("remaining", 0))
    if remaining <= 0:
        return data, {"credited_kills": 0, "slayer_xp": 0.0, "completed": False}
    family = SLAYER_FAMILIES_BY_ID.get(
        str(assignment.get("family_id", "") or "")
    )
    if family is None or target_id not in family.target_ids:
        return data, {"credited_kills": 0, "slayer_xp": 0.0, "completed": False}

    credited = min(remaining, _non_negative_int(kills, 0))
    if credited <= 0:
        return data, {"credited_kills": 0, "slayer_xp": 0.0, "completed": False}
    enemy = enemy_data.get(target_id, {}) or {}
    try:
        xp_each = max(0.0, float(enemy.get("slayer_xp", 0.0) or 0.0))
    except (TypeError, ValueError):
        xp_each = 0.0
    xp = xp_each * credited
    assignment["remaining"] = remaining - credited
    completed = assignment["remaining"] == 0
    assignment["completed"] = completed
    data["slayer_assignment"] = assignment
    if xp > 0:
        data["slayer_exp"] = float(data.get("slayer_exp", 0.0) or 0.0) + xp
    if completed:
        data["slayer_tasks_completed"] = _non_negative_int(
            data.get("slayer_tasks_completed", 0)
        ) + 1
        data["slayer_last_family_id"] = family.id
        # Turael/Spria tasks intentionally award no points and do not advance
        # the post-Smoking-Kills qualifying streak.
    return data, {
        "credited_kills": credited,
        "slayer_xp": xp,
        "completed": completed,
        "remaining": assignment["remaining"],
        "family_id": family.id,
        "family_display_name": family.display_name,
        "master_display_name": slayer_master_display_name_pure(
            data, str(assignment.get("master_id", "") or "")
        ),
    }
