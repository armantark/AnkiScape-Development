"""The last action: what the switch to Bankstanding stopped, and the way back.

The switch to Bankstanding saves a record of the running action under
``LAST_ACTION_KEY``. The review HUD's Resume button restarts it, and the action
queue keeps its entries in the same record shape. A record holds every key its
tab's start path needs, plus the reason it stopped for the HUD's status line;
``start_action`` runs the requirement checks that tab's Start runs and shows
the same refusal, then starts the record's own selection.
"""

from __future__ import annotations

from typing import Any, Mapping

from .action_registry import (
    COMBAT_REVIEW_ACTION_DISPLAY_NAME,
    QUEST_REVIEW_ACTION_DISPLAY_NAME,
    is_combat_review_action,
    is_quest_review_action,
    is_utility_review_action,
    landmark_activity_name,
    utility_review_surface_for_target,
)
from .constants import DEFAULT_COMBAT_TARGET, QUEST_DATA, UTILITY_ACTIVITY_DATA
from .menu_cooking import with_cooking_target
from .skill_registry import get_skill
from ..data.shooting_star_data import SHOOTING_STAR_ACTIVITY_ID
from ..logic.shooting_star_logic import apply_shooting_star_join_pure
from ..logic_pure.logic_pure import (
    can_attempt_quest_review_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_state_pure,
    start_quest_pure,
)

LAST_ACTION_KEY = "last_action"
_BANKSTANDING = "bankstanding"
# The keys each kind's start path needs; a record holds these and its stop reason.
_RECORD_KEYS = {
    "skill": ("skill", "target"),
    "utility": ("utility_id",),
    "quest": ("quest_id",),
    "combat": ("target", "combat_action"),
}
_IDLE_AT_BANK = "idle at the Bank"
_HIDDEN = {"visible": False, "text": "", "tooltip": "", "bank_status": _IDLE_AT_BANK}


def last_action_record_pure(player_data: Mapping[str, Any], current_skill: Any) -> dict[str, Any]:
    """The record of the action running now; empty when nothing resumable runs."""
    if is_combat_review_action(current_skill):
        return {
            "kind": "combat",
            "target": str(player_data.get("current_combat_target") or DEFAULT_COMBAT_TARGET),
            "combat_action": str(player_data.get("combat_action") or "attack"),
        }
    if is_quest_review_action(current_skill):
        quest_id = player_data.get("current_quest")
        return {"kind": "quest", "quest_id": quest_id} if quest_id in QUEST_DATA else {}
    if is_utility_review_action(current_skill):
        utility_id = str(player_data.get("current_utility") or "")
        if utility_id in {"", _BANKSTANDING}:
            return {}
        return {"kind": "utility", "utility_id": utility_id}
    skill = get_skill(str(current_skill or ""))
    if skill is None:
        return {}
    return {
        "kind": "skill",
        "skill": skill.display_name,
        "target": player_data.get(skill.current_target_key) if skill.current_target_key else None,
    }


def saved_last_action_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The saved record, or empty when the save holds none this game can start."""
    return valid_action_record_pure(player_data.get(LAST_ACTION_KEY))


def valid_action_record_pure(record: Any) -> dict[str, Any]:
    """An action record this game can start, cut to its shape, else empty."""
    if not isinstance(record, Mapping) or record.get("kind") not in _RECORD_KEYS:
        return {}
    keys = ("kind", *_RECORD_KEYS[record["kind"]])
    if any(key not in record for key in keys):
        return {}
    if record["kind"] == "quest" and record.get("quest_id") not in QUEST_DATA:
        return {}
    if record["kind"] == "skill" and get_skill(str(record.get("skill") or "")) is None:
        return {}
    return {key: record[key] for key in (*keys, "reason") if key in record}


def last_action_name_pure(record: Mapping[str, Any]) -> str:
    """The name the player picked the action by: quest, activity, skill or Combat."""
    kind = record.get("kind")
    if kind == "quest":
        return str(QUEST_DATA[record["quest_id"]].get("display_name", record["quest_id"]))
    if kind == "utility":
        utility_id = str(record["utility_id"])
        spec = UTILITY_ACTIVITY_DATA.get(utility_id, {})
        return str(
            spec.get("display_name")
            or landmark_activity_name(utility_id)
            or utility_id.replace("_", " ").title()
        )
    if kind == "combat":
        return COMBAT_REVIEW_ACTION_DISPLAY_NAME
    return str(record.get("skill") or "")


def resume_button_view_pure(player_data: Mapping[str, Any], current_skill: Any) -> dict[str, Any]:
    """Resume shows only at Bankstanding, for a saved action that can still run.

    ``bank_status`` is the Bankstanding line under the HUD title: why the saved
    action stopped while Resume is offered, else the plain idle line.
    """
    at_bank = (
        is_utility_review_action(current_skill)
        and player_data.get("current_utility") == _BANKSTANDING
    )
    record = saved_last_action_pure(player_data) if at_bank else {}
    if not record:
        return dict(_HIDDEN)
    name = last_action_name_pure(record)
    tooltip = f"Restart {name}."
    if record["kind"] == "quest":
        state = quest_state_pure(player_data, record["quest_id"])
        if state.get("completed"):
            return dict(_HIDDEN)
        stages = QUEST_DATA[record["quest_id"]].get("stages", 1)
        tooltip = f"Restart {name} at stage {int(state.get('progress', 0) or 0)}/{stages}."
    reason = str(record.get("reason") or "")
    return {
        "visible": True,
        "text": f"Resume {name}",
        "tooltip": tooltip,
        "bank_status": f"stopped: {reason}" if reason else _IDLE_AT_BANK,
    }


def quest_blocked_message(quest_name: str, reasons: tuple[str, ...]) -> str:
    """The reason text a quest review and a Resume click both show for a blocked step."""
    return (
        f"{quest_name} is blocked:\n"
        + "\n".join(f"• {reason}" for reason in reasons)
        + "\n\nQuesting has been switched off until this is resolved."
    )


def start_values(addon, current: Mapping[str, Any], record: Mapping[str, Any]) -> tuple[dict[str, Any], str] | None:
    """The save and review action that start ``record`` with its own target; None when it cannot start.

    Each selection goes through the rule that owns it, such as the gauntlets a
    Cooking target swaps or the Warriors' Guild room a fight target leaves.
    """
    kind = record["kind"]
    if kind == "quest":
        updated, ok = start_quest_pure(current, record["quest_id"], QUEST_DATA)
        return (updated, QUEST_REVIEW_ACTION_DISPLAY_NAME) if ok else None
    if kind == "utility":
        utility_id = record["utility_id"]
        updated, joined = dict(current), True
        if utility_id == SHOOTING_STAR_ACTIVITY_ID:
            updated, joined, _info = apply_shooting_star_join_pure(current)
        updated["current_utility"] = utility_id
        return (updated, utility_review_surface_for_target(utility_id)) if joined else None
    if kind == "combat":
        values = {**addon._combat_target_values(current, record["target"]), "combat_action": record["combat_action"]}
        return {**current, **values}, COMBAT_REVIEW_ACTION_DISPLAY_NAME
    skill = get_skill(record["skill"])
    updated = dict(current)
    if skill.current_target_key and record.get("target") is not None:
        updated[skill.current_target_key] = record["target"]
        if skill.id == "cooking":
            updated = with_cooking_target(addon, updated, record["target"])
    return updated, skill.display_name


def start_action(addon, record: Mapping[str, Any]) -> bool:
    """Start a record with the checks its tab's Start runs; True when it runs.

    A skill or fight restarts on the record's own target, so a target picked in
    the tab since the stop never runs under the record's name, and the
    selection and the start are one undo step.
    """
    kind = record.get("kind")
    if kind == "utility":
        return bool(addon.start_activity_for_reviews(record["utility_id"]))
    if kind == "quest":
        return _start_quest(addon, str(record["quest_id"]))
    refusal = addon.skill_start_refusal(record.get("skill"))
    if refusal:
        addon.show_error_message(*refusal)
        return False
    updated, review_action = start_values(addon, addon._state.player_data, record)
    committed = addon.commit_direct_action(lambda _current: (updated, True), selected_skill=review_action)
    if committed:
        addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
    return committed


def _start_quest(addon, quest_id: str) -> bool:
    # The Quests tab refuses a blocked step without a word because its card
    # already lists the blocker; from the HUD the player needs the review's text.
    player_data = addon._state.player_data
    reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
    if reasons and not can_attempt_quest_review_pure(player_data, quest_id, QUEST_DATA):
        name = str(QUEST_DATA[quest_id].get("display_name", quest_id))
        addon.show_error_message("Quest blocked", quest_blocked_message(name, tuple(reasons)))
        return False
    return bool(addon.on_set_quest(quest_id)) and bool(
        addon.save_skill(QUEST_REVIEW_ACTION_DISPLAY_NAME, None)
    )


def resume_last_action(addon) -> bool:
    """The Resume click: restart the saved action, or refuse with its tab's reason."""
    if not resume_button_view_pure(addon._state.player_data, addon._state.current_skill)["visible"]:
        return False
    return start_action(addon, saved_last_action_pure(addon._state.player_data))
