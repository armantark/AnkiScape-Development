"""Pure quiz, specimen, quest-story, and reward mechanics for Varrock Museum."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

try:
    from .varrock_museum_data import (
        KUDOS_THRESHOLD_REWARDS,
        MUSEUM_TOOL_RACK_ITEMS,
        QUEST_KUDOS,
        QUIZ_DISPLAYS,
        SPECIMEN_DISPLAYS,
        VARROCK_MUSEUM_ACTIVITY_ID,
        VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS,
        VARROCK_MUSEUM_SOURCE_MAX_KUDOS,
    )
except ImportError:  # pragma: no cover - flat test imports
    from varrock_museum_data import (  # type: ignore
        KUDOS_THRESHOLD_REWARDS,
        MUSEUM_TOOL_RACK_ITEMS,
        QUEST_KUDOS,
        QUIZ_DISPLAYS,
        SPECIMEN_DISPLAYS,
        VARROCK_MUSEUM_ACTIVITY_ID,
        VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS,
        VARROCK_MUSEUM_SOURCE_MAX_KUDOS,
    )


VARROCK_MUSEUM_STATE_VERSION = 1
_ROUTES = {"quiz", "cleaning"}
_SPECIMEN_IDS = {str(row["id"]) for row in SPECIMEN_DISPLAYS}
_QUEST_IDS = {str(row["id"]) for row in QUEST_KUDOS}
_REWARD_IDS = {str(row["id"]) for row in KUDOS_THRESHOLD_REWARDS}


def _int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return max(0, default)


def _unique_known(raw: Any, known: set[str]) -> list[str]:
    if not isinstance(raw, (tuple, list)):
        return []
    return [value for value in dict.fromkeys(str(item) for item in raw) if value in known]


def default_varrock_museum_state_pure() -> dict[str, Any]:
    return {
        "version": VARROCK_MUSEUM_STATE_VERSION,
        "route": "quiz",
        "quiz_completed": [],
        "specimens_displayed": [],
        "digsite_pendant_unlocked": False,
        "quest_stories_claimed": [],
        "orlando_reward_claimed": False,
        "threshold_rewards_claimed": [],
        "cleaning_reviews": 0,
        "last_result": "Choose the quiz or specimen-cleaning route.",
    }


def sanitize_varrock_museum_state_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    route = str(source.get("route", "quiz"))
    if route not in _ROUTES:
        route = "quiz"
    return {
        "version": VARROCK_MUSEUM_STATE_VERSION,
        "route": route,
        "quiz_completed": _unique_known(source.get("quiz_completed"), set(QUIZ_DISPLAYS)),
        "specimens_displayed": _unique_known(source.get("specimens_displayed"), _SPECIMEN_IDS),
        "digsite_pendant_unlocked": bool(source.get("digsite_pendant_unlocked")),
        "quest_stories_claimed": _unique_known(source.get("quest_stories_claimed"), _QUEST_IDS),
        "orlando_reward_claimed": bool(source.get("orlando_reward_claimed")),
        "threshold_rewards_claimed": _unique_known(
            source.get("threshold_rewards_claimed"), _REWARD_IDS
        ),
        "cleaning_reviews": _int(source.get("cleaning_reviews")),
        "last_result": str(
            source.get("last_result", "Choose the quiz or specimen-cleaning route.")
            or "Choose the quiz or specimen-cleaning route."
        )[:500],
    }


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    state = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return isinstance(state, Mapping) and bool(state.get("completed"))


def _inventory(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    inventory = player_data.get("inventory")
    return inventory if isinstance(inventory, Mapping) else {}


def _carried_pack(player_data: Mapping[str, Any]) -> Mapping[str, Any]:
    carried = player_data.get("carried_inventory")
    pack = (
        carried.get(VARROCK_MUSEUM_ACTIVITY_ID)
        if isinstance(carried, Mapping)
        else None
    )
    return pack if isinstance(pack, Mapping) else {}


def _equipped_items(player_data: Mapping[str, Any]) -> set[str]:
    equipment = player_data.get("equipment")
    return {str(item) for item in equipment.values()} if isinstance(equipment, Mapping) else set()


def varrock_museum_kudos_pure(player_data: Mapping[str, Any]) -> int:
    state = sanitize_varrock_museum_state_pure(player_data.get("varrock_museum"))
    quest_by_id = {str(row["id"]): int(row["kudos"]) for row in QUEST_KUDOS}
    return (
        len(state["quiz_completed"]) * 2
        + len(state["specimens_displayed"]) * 10
        + sum(quest_by_id[quest_id] for quest_id in state["quest_stories_claimed"])
    )


def varrock_museum_cleaning_locked_reasons_pure(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not _quest_complete(player_data, "the_dig_site"):
        reasons.append("complete The Dig Site")
    equipped = _equipped_items(player_data)
    if "Leather gloves" not in equipped:
        reasons.append("wear Leather gloves")
    if "Leather boots" not in equipped:
        reasons.append("wear Leather boots")
    inventory = _carried_pack(player_data)
    for item_name in ("Trowel", "Rock pick", "Specimen brush"):
        if _int(inventory.get(item_name)) < 1:
            reasons.append(f"carry {item_name}")
    return tuple(reasons)


def _claimable_quest_rows(player_data: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    claimed = set(state["quest_stories_claimed"])
    carried = _carried_pack(player_data)
    rows = []
    for row in QUEST_KUDOS:
        quest_id = str(row["id"])
        required_item = str(row.get("required_item", ""))
        if (
            quest_id not in claimed
            and _quest_complete(player_data, quest_id)
            and (not required_item or _int(carried.get(required_item)) > 0)
        ):
            rows.append(dict(row))
    return tuple(rows)


def varrock_museum_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_varrock_museum_state_pure(player_data.get("varrock_museum"))
    kudos = varrock_museum_kudos_pure({**dict(player_data), "varrock_museum": state})
    route = state["route"]
    cleaning_locked = varrock_museum_cleaning_locked_reasons_pure(player_data)
    quiz_remaining = len(QUIZ_DISPLAYS) - len(state["quiz_completed"])
    specimens_remaining = len(SPECIMEN_DISPLAYS) - len(state["specimens_displayed"])
    cleaning_complete = specimens_remaining == 0 and state["digsite_pendant_unlocked"]
    claimable_thresholds = tuple(
        row
        for row in KUDOS_THRESHOLD_REWARDS
        if int(row["kudos"]) <= kudos
        and str(row["id"]) not in state["threshold_rewards_claimed"]
    )
    can_review = quiz_remaining > 0 if route == "quiz" else not cleaning_locked and not cleaning_complete
    return {
        **state,
        "kudos": kudos,
        "source_max_kudos": VARROCK_MUSEUM_SOURCE_MAX_KUDOS,
        "implemented_max_kudos": VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS,
        "quiz_remaining": quiz_remaining,
        "specimens_remaining": specimens_remaining,
        "cleaning_locked_reasons": cleaning_locked,
        "cleaning_complete": cleaning_complete,
        "claimable_quest_stories": _claimable_quest_rows(player_data, state),
        "claimable_thresholds": claimable_thresholds,
        "can_claim_orlando": quiz_remaining == 0 and not state["orlando_reward_claimed"],
        "can_review": can_review,
    }


def apply_varrock_museum_review_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the inventory alias is rebuilt with dict() before any
    # write, and everything else is top-level assignment.
    data = dict(player_data)
    state = sanitize_varrock_museum_state_pure(data.get("varrock_museum"))
    data["varrock_museum"] = state
    route = state["route"]
    if route == "quiz":
        display = next(
            (name for name in QUIZ_DISPLAYS if name not in state["quiz_completed"]),
            "",
        )
        if not display:
            return data, False, {"reason": "The natural history quiz is complete."}
        state["quiz_completed"].append(display)
        state["last_result"] = f"Completed the {display} display · +2 Kudos"
        return data, True, {
            "action_id": "quiz_display",
            "display": display,
            "kudos": 2,
            "status": state["last_result"],
            "terminal": len(state["quiz_completed"]) == len(QUIZ_DISPLAYS),
        }

    locked = varrock_museum_cleaning_locked_reasons_pure(data)
    if locked:
        return data, False, {"reason": ", ".join(locked), "locked_reasons": locked}
    state["cleaning_reviews"] += 1
    specimen = next(
        (row for row in SPECIMEN_DISPLAYS if row["id"] not in state["specimens_displayed"]),
        None,
    )
    if specimen is not None:
        state["specimens_displayed"].append(str(specimen["id"]))
        state["last_result"] = (
            f"Cleaned {specimen['item']} and filled case {specimen['case']} · +10 Kudos"
        )
        return data, True, {
            "action_id": "clean_specimen",
            "specimen_id": str(specimen["id"]),
            "item": str(specimen["item"]),
            "kudos": 10,
            "status": state["last_result"],
            "terminal": False,
        }
    if not state["digsite_pendant_unlocked"]:
        state["digsite_pendant_unlocked"] = True
        state["last_result"] = (
            "Found a Clean necklace; an archaeologist taught Digsite-pendant enchanting."
        )
        return data, True, {
            "action_id": "clean_necklace",
            "unlock": "digsite_pendant",
            "kudos": 0,
            "status": state["last_result"],
            "terminal": True,
        }
    return data, False, {"reason": "Every museum specimen discovery is complete."}


def apply_varrock_museum_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the inventory alias is rebuilt with dict() before any
    # write, and everything else is top-level assignment.
    data = dict(player_data)
    state = sanitize_varrock_museum_state_pure(data.get("varrock_museum"))
    data["varrock_museum"] = state
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "set_route":
        route = str(payload.get("route", ""))
        if route not in _ROUTES:
            return data, False, {"reason": "Choose Quiz or Specimen cleaning."}
        state["route"] = route
        state["last_result"] = "Natural history quiz selected." if route == "quiz" else "Specimen cleaning selected."
        return data, True, {"route": route, "message": state["last_result"]}

    if action_id == "take_cleaning_kit":
        inventory = dict(_inventory(data))
        equipped = _equipped_items(data)
        added: list[str] = []
        for item_name, _item_id in MUSEUM_TOOL_RACK_ITEMS:
            if _int(inventory.get(item_name)) == 0 and item_name not in equipped:
                inventory[item_name] = 1
                added.append(item_name)
        if not added:
            return data, False, {"reason": "You already have the complete museum cleaning kit."}
        data["inventory"] = inventory
        state["last_result"] = "Took from the museum rack: " + ", ".join(added) + "."
        return data, True, {"items": tuple(added), "message": state["last_result"]}

    if action_id == "claim_quest_stories":
        rows = _claimable_quest_rows(data, state)
        if not rows:
            return data, False, {"reason": "No completed quest stories are ready for Minas."}
        state["quest_stories_claimed"].extend(str(row["id"]) for row in rows)
        kudos = sum(int(row["kudos"]) for row in rows)
        state["last_result"] = f"Historian Minas recorded {len(rows)} stories · +{kudos} Kudos"
        return data, True, {
            "quest_ids": tuple(str(row["id"]) for row in rows),
            "kudos": kudos,
            "message": state["last_result"],
        }

    if action_id == "claim_orlando_reward":
        if len(state["quiz_completed"]) != len(QUIZ_DISPLAYS):
            return data, False, {"reason": "Complete all fourteen quiz displays first."}
        if state["orlando_reward_claimed"]:
            return data, False, {"reason": "Orlando's quiz reward is already claimed."}
        state["orlando_reward_claimed"] = True
        xp = {"hunter": 1000.0, "slayer": 1000.0}
        for skill_id, amount in xp.items():
            exp_key = f"{skill_id}_exp"
            data[exp_key] = float(data.get(exp_key, 0.0) or 0.0) + amount
        state["last_result"] = "Orlando awarded 1,000 Hunter XP and 1,000 Slayer XP."
        return data, True, {"xp": xp, "message": state["last_result"]}

    if action_id == "claim_threshold_rewards":
        kudos = varrock_museum_kudos_pure(data)
        rows = [
            row
            for row in KUDOS_THRESHOLD_REWARDS
            if int(row["kudos"]) <= kudos
            and str(row["id"]) not in state["threshold_rewards_claimed"]
        ]
        if not rows:
            return data, False, {"reason": "No unclaimed Kudos milestone reward is ready."}
        xp: dict[str, float] = {}
        for row in rows:
            state["threshold_rewards_claimed"].append(str(row["id"]))
            for skill_id, amount in row["xp"].items():
                xp[skill_id] = xp.get(skill_id, 0.0) + float(amount)
        for skill_id, amount in xp.items():
            exp_key = f"{skill_id}_exp"
            data[exp_key] = float(data.get(exp_key, 0.0) or 0.0) + amount
        state["last_result"] = "Claimed Kudos milestones: " + ", ".join(
            f"{row['kudos']}+" for row in rows
        )
        return data, True, {
            "reward_ids": tuple(str(row["id"]) for row in rows),
            "xp": xp,
            "message": state["last_result"],
        }

    return data, False, {"reason": "Unknown Varrock Museum command."}
