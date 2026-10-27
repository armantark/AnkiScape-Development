"""The last action: what the switch to Bankstanding stopped, and the way back.

The switch to Bankstanding saves a record of the running action under
``LAST_ACTION_KEY``. The review HUD's Resume button restarts it, and the action
queue reuses both the record shape and ``start_action``. A record holds every
key its tab's start path needs; ``start_action`` calls that tab's own start
function, so a restart runs the same requirement checks and shows the same
refusal as the tab.
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
)
from .constants import DEFAULT_COMBAT_TARGET, QUEST_DATA, UTILITY_ACTIVITY_DATA
from .skill_registry import get_skill
from ..logic_pure.logic_pure import (
    can_attempt_quest_review_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_state_pure,
)

LAST_ACTION_KEY = "last_action"
_BANKSTANDING = "bankstanding"
_KINDS = frozenset({"skill", "utility", "quest", "combat"})
_HIDDEN = {"visible": False, "text": "", "tooltip": ""}


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
    record = player_data.get(LAST_ACTION_KEY)
    if not isinstance(record, Mapping) or record.get("kind") not in _KINDS:
        return {}
    if record["kind"] == "quest" and record.get("quest_id") not in QUEST_DATA:
        return {}
    if record["kind"] == "skill" and get_skill(str(record.get("skill") or "")) is None:
        return {}
    return dict(record)


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
    """Resume shows only at Bankstanding, for a saved action that can still run."""
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
    return {"visible": True, "text": f"Resume {name}", "tooltip": tooltip}


def quest_blocked_message(quest_name: str, reasons: tuple[str, ...]) -> str:
    """The reason text a quest review and a Resume click both show for a blocked step."""
    return (
        f"{quest_name} is blocked:\n"
        + "\n".join(f"• {reason}" for reason in reasons)
        + "\n\nQuesting has been switched off until this is resolved."
    )


def start_action(addon, record: Mapping[str, Any]) -> bool:
    """Start a record through the start function its tab uses; True when it runs."""
    kind = record.get("kind")
    if kind == "utility":
        return bool(addon.start_activity_for_reviews(record["utility_id"]))
    if kind == "quest":
        return _start_quest(addon, str(record["quest_id"]))
    skill = COMBAT_REVIEW_ACTION_DISPLAY_NAME if kind == "combat" else str(record["skill"])
    return bool(addon.save_skill(skill, None))


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
