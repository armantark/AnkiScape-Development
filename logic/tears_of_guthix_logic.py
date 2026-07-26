"""Pure, review-driven Tears of Guthix eligibility, collection, and payout."""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

from ..core.skill_registry import get_skill, trainable_skill_definitions
from ..data.tears_of_guthix_data import (
    ORNATE_BOWL_CRAFTING_LEVEL,
    ORNATE_BOWL_MINING_LEVEL,
    ORNATE_BOWL_TOOL,
    TEARS_OF_GUTHIX_ACTIVITY_ID,
    TEARS_OF_GUTHIX_ENTRY_CAP,
    TEARS_OF_GUTHIX_GREEN_TEAR_CHANCE,
    TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS,
    TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP,
    TEARS_OF_GUTHIX_PROGRESS_EXP,
    TEARS_OF_GUTHIX_PROGRESS_QUEST_POINTS,
    TEARS_OF_GUTHIX_QUEST_ID,
    TEARS_OF_GUTHIX_STONE_BOWL_XP_CAP,
    TEARS_OF_GUTHIX_TEARS_PER_TICK,
    TEARS_OF_GUTHIX_TICKS_PER_QUEST_POINT,
    TEARS_OF_GUTHIX_TICKS_PER_REVIEW,
    TEARS_OF_GUTHIX_WEEK_REVIEWS,
    TEARS_OF_GUTHIX_XP_PER_LEVEL,
)


TEARS_OF_GUTHIX_STATE_VERSION = 1


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return default


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def _world_week(player_data: Mapping[str, Any]) -> int:
    return _answered_cards(player_data) // TEARS_OF_GUTHIX_WEEK_REVIEWS


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    quest = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def total_experience_pure(player_data: Mapping[str, Any]) -> float:
    """"100,000 XP. This can be shared across any number of skills.\""""
    return sum(
        _float(player_data.get(skill.exp_key))
        for skill in trainable_skill_definitions()
    )


def reward_skill_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """"The experience is added to the skill with the least experience.\"

    Least *experience*, not lowest displayed level — the period article calls
    that out explicitly against the common Dungeoneering misreading. Eligibility
    is AnkiScape's trainable set, the same one Penguin Hide and Seek redeems
    into; the period exclusion for skills a player cannot yet train has no
    general rule to port.
    """
    skills = trainable_skill_definitions()
    chosen = min(
        skills,
        key=lambda skill: (_float(player_data.get(skill.exp_key)), skill.id),
    )
    return {
        "id": chosen.id,
        "display_name": chosen.display_name,
        "level_key": chosen.level_key,
        "exp_key": chosen.exp_key,
        "level": max(1, _int(player_data.get(chosen.level_key), 1, minimum=1)),
        "exp": _float(player_data.get(chosen.exp_key)),
    }


def collection_ticks_pure(player_data: Mapping[str, Any]) -> int:
    """"The time a player has is the player's Quest Points in Ticks.\""""
    return min(
        TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS,
        _int(player_data.get("quest_points"))
        * TEARS_OF_GUTHIX_TICKS_PER_QUEST_POINT,
    )


def xp_per_tear_pure(level: int, ornate_bowl: bool) -> int:
    cap = (
        TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP
        if ornate_bowl
        else TEARS_OF_GUTHIX_STONE_BOWL_XP_CAP
    )
    return min(cap, max(1, int(level)) * TEARS_OF_GUTHIX_XP_PER_LEVEL)


def _beats(ticks: int) -> int:
    return math.ceil(max(0, int(ticks)) / TEARS_OF_GUTHIX_TICKS_PER_REVIEW)


def default_tears_of_guthix_state_pure() -> dict[str, Any]:
    return {
        "version": TEARS_OF_GUTHIX_STATE_VERSION,
        "ornate_bowl": False,
        "active": False,
        "remaining_ticks": 0,
        "session_ticks": 0,
        "tears": 0,
        "visits": 0,
        "allowance_week_index": -1,
        "available_entries": 0,
        "last_visit_exp": 0.0,
        "last_visit_quest_points": 0,
        "last_result": "",
    }


def sanitize_tears_of_guthix_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_tears_of_guthix_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    session_ticks = min(
        TEARS_OF_GUTHIX_MAX_COLLECTION_TICKS,
        _int(source.get("session_ticks")),
    )
    remaining = min(session_ticks, _int(source.get("remaining_ticks")))
    active = bool(source.get("active", False)) and remaining > 0
    if not active:
        remaining = 0
        session_ticks = 0
    return {
        **defaults,
        "ornate_bowl": bool(source.get("ornate_bowl", False)),
        "active": active,
        "remaining_ticks": remaining,
        "session_ticks": session_ticks,
        "tears": _int(source.get("tears")) if active else 0,
        "visits": _int(source.get("visits")),
        "allowance_week_index": max(
            -1,
            _int(source.get("allowance_week_index"), -1, minimum=-1),
        ),
        "available_entries": min(
            TEARS_OF_GUTHIX_ENTRY_CAP,
            _int(source.get("available_entries")),
        ),
        "last_visit_exp": max(0.0, _float(source.get("last_visit_exp"))),
        "last_visit_quest_points": _int(source.get("last_visit_quest_points")),
        "last_result": str(source.get("last_result", ""))[:500],
    }


def _sync_entries(
    state: Mapping[str, Any],
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    """Bank one entry per elapsed simulated week, up to the carryover cap."""
    synced = dict(state)
    if _int(synced.get("visits")) <= 0:
        return synced
    current_week = _world_week(player_data)
    previous_week = _int(
        synced.get("allowance_week_index"),
        current_week,
        minimum=-1,
    )
    if previous_week < 0:
        synced["allowance_week_index"] = current_week
        return synced
    if current_week > previous_week:
        synced["available_entries"] = min(
            TEARS_OF_GUTHIX_ENTRY_CAP,
            _int(synced.get("available_entries")) + current_week - previous_week,
        )
        synced["allowance_week_index"] = current_week
    return synced


def tears_of_guthix_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = _sync_entries(
        sanitize_tears_of_guthix_state_pure(player_data.get("tears_of_guthix")),
        player_data,
    )
    quest_done = _quest_complete(player_data, TEARS_OF_GUTHIX_QUEST_ID)
    ticks = collection_ticks_pure(player_data)
    first_visit = state["visits"] == 0
    exp_gained = total_experience_pure(player_data) - state["last_visit_exp"]
    quest_points_gained = (
        _int(player_data.get("quest_points")) - state["last_visit_quest_points"]
    )
    progress_met = first_visit or (
        exp_gained >= TEARS_OF_GUTHIX_PROGRESS_EXP
        or quest_points_gained >= TEARS_OF_GUTHIX_PROGRESS_QUEST_POINTS
    )
    week_ready = first_visit or state["available_entries"] > 0
    reviews_to_entry = 0
    if not week_ready:
        remainder = _answered_cards(player_data) % TEARS_OF_GUTHIX_WEEK_REVIEWS
        reviews_to_entry = TEARS_OF_GUTHIX_WEEK_REVIEWS - remainder

    missing: list[str] = []
    if not quest_done:
        missing.append("Complete the Tears of Guthix quest")
    if ticks <= 0:
        missing.append("Earn a Quest Point to buy time in the cavern")

    mining_level = _int(player_data.get("mining_level"), 1, minimum=1)
    crafting_level = _int(player_data.get("crafting_level"), 1, minimum=1)
    inventory = player_data.get("inventory")
    has_chisel = (
        isinstance(inventory, Mapping)
        and _int(inventory.get(ORNATE_BOWL_TOOL)) > 0
    )
    ornate_missing: list[str] = []
    if not quest_done:
        ornate_missing.append("Complete the Tears of Guthix quest")
    if mining_level < ORNATE_BOWL_MINING_LEVEL:
        ornate_missing.append(f"Mining level {ORNATE_BOWL_MINING_LEVEL}")
    if crafting_level < ORNATE_BOWL_CRAFTING_LEVEL:
        ornate_missing.append(f"Crafting level {ORNATE_BOWL_CRAFTING_LEVEL}")
    if not has_chisel:
        ornate_missing.append(f"A {ORNATE_BOWL_TOOL} to shape the larger rock")

    reward_skill = reward_skill_pure(player_data)
    return {
        **state,
        "quest_complete": quest_done,
        "requirements_met": not missing,
        "missing_requirements": tuple(missing),
        "first_visit": first_visit,
        "progress_met": progress_met,
        "exp_since_visit": exp_gained,
        "quest_points_since_visit": quest_points_gained,
        "week_ready": week_ready,
        "reviews_to_entry": reviews_to_entry,
        "entry_ready": bool(not missing and progress_met and week_ready),
        "collection_ticks": ticks,
        "entry_beats": _beats(ticks),
        "session_beats": _beats(state["session_ticks"]),
        "remaining_beats": _beats(state["remaining_ticks"]),
        "reward_skill": reward_skill,
        "xp_per_tear": xp_per_tear_pure(
            reward_skill["level"],
            state["ornate_bowl"],
        ),
        "ornate_bowl_ready": not ornate_missing,
        "ornate_bowl_missing": tuple(ornate_missing),
        # The panel renders these and never re-derives them.
        "enter_enabled": bool(
            state["active"]
            or (not missing and progress_met and week_ready)
        ),
        "leave_enabled": bool(state["active"]),
        "craft_ornate_enabled": bool(not state["ornate_bowl"] and not ornate_missing),
        "craft_ornate_visible": not state["ornate_bowl"],
    }


def _end_session(data: dict[str, Any], state: dict[str, Any], message: str) -> None:
    state["active"] = False
    state["remaining_ticks"] = 0
    state["session_ticks"] = 0
    state["tears"] = 0
    state["last_result"] = message[:500]
    data["tears_of_guthix"] = state
    data["activity_session"] = {"active_id": ""}


def apply_tears_of_guthix_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = _sync_entries(
        sanitize_tears_of_guthix_state_pure(data.get("tears_of_guthix")),
        data,
    )
    data["tears_of_guthix"] = state

    if action_id == "craft_ornate_bowl":
        if state["ornate_bowl"]:
            return data, False, {"reason": "Juna already keeps your ornate bowl."}
        view = tears_of_guthix_view_pure(data)
        if not view["ornate_bowl_ready"]:
            return data, False, {
                "reason": "; ".join(view["ornate_bowl_missing"]) + "."
            }
        state["ornate_bowl"] = True
        state["last_result"] = (
            "Chiselled the larger rock into an ornate bowl; Juna keeps it for you. "
            f"Tears now pay up to {TEARS_OF_GUTHIX_ORNATE_BOWL_XP_CAP} XP each."
        )
        return data, True, {"message": state["last_result"]}

    if action_id == "enter":
        if state["active"]:
            data["activity_session"] = {"active_id": TEARS_OF_GUTHIX_ACTIVITY_ID}
            data["current_utility"] = TEARS_OF_GUTHIX_ACTIVITY_ID
            return data, True, {"message": "Tears of Guthix selected for reviews."}
        active_session = data.get("activity_session")
        if isinstance(active_session, Mapping) and active_session.get("active_id"):
            return data, False, {"reason": "Another persistent activity is active."}
        view = tears_of_guthix_view_pure(data)
        if not view["requirements_met"]:
            return data, False, {
                "reason": "; ".join(view["missing_requirements"]) + "."
            }
        if not view["progress_met"]:
            return data, False, {
                "reason": (
                    "Juna wants to hear something new: earn "
                    f"{int(TEARS_OF_GUTHIX_PROGRESS_EXP - view['exp_since_visit']):,}"
                    " more experience or a Quest Point since your last visit."
                )
            }
        if not view["week_ready"]:
            return data, False, {
                "reason": (
                    "No Tears of Guthix visit is banked; "
                    f"{view['reviews_to_entry']:,} reviews remain."
                )
            }
        ticks = view["collection_ticks"]
        if not view["first_visit"]:
            state["available_entries"] = max(0, state["available_entries"] - 1)
        state.update(
            {
                "active": True,
                "session_ticks": ticks,
                "remaining_ticks": ticks,
                "tears": 0,
                "last_result": (
                    f"Juna lets you into the cavern for {ticks} ticks "
                    f"({_beats(ticks)} collection beats)."
                ),
            }
        )
        data["tears_of_guthix"] = state
        data["activity_session"] = {"active_id": TEARS_OF_GUTHIX_ACTIVITY_ID}
        data["current_utility"] = TEARS_OF_GUTHIX_ACTIVITY_ID
        return data, True, {"message": state["last_result"]}

    if action_id == "leave":
        if not state["active"]:
            return data, False, {"reason": "You are not in the cavern."}
        state["last_result"] = (
            f"Left the cavern holding {state['tears']} tears; "
            f"{_beats(state['remaining_ticks'])} collection beats remain."
        )
        data["tears_of_guthix"] = state
        data["activity_session"] = {"active_id": ""}
        return data, True, {"message": state["last_result"]}

    return data, False, {"reason": "Unknown Tears of Guthix command."}


def apply_tears_of_guthix_review_pure(
    player_data: Mapping[str, Any],
    rng,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = _sync_entries(
        sanitize_tears_of_guthix_state_pure(data.get("tears_of_guthix")),
        data,
    )
    if not state["active"]:
        return data, False, {"reason": "Enter Juna's cavern before collecting."}

    ticks = min(TEARS_OF_GUTHIX_TICKS_PER_REVIEW, state["remaining_ticks"])
    blue = 0
    green = 0
    for _ in range(ticks):
        try:
            roll = float(rng())
        except (TypeError, ValueError, OverflowError):
            roll = 1.0
        if roll < TEARS_OF_GUTHIX_GREEN_TEAR_CHANCE:
            green += 1
        else:
            blue += 1
    # Blue tears add and green tears subtract. The period record does not say
    # whether the counter can go below zero, so it floors rather than inventing
    # a debt the sources never describe.
    tears = max(0, state["tears"] + blue * TEARS_OF_GUTHIX_TEARS_PER_TICK - green)
    state["tears"] = tears
    state["remaining_ticks"] = max(0, state["remaining_ticks"] - ticks)
    data["tears_of_guthix"] = state

    if state["remaining_ticks"] > 0:
        state["last_result"] = (
            f"{tears} tears · +{blue} blue, -{green} green · "
            f"{_beats(state['remaining_ticks'])} beats left"
        )
        data["activity_session"] = {"active_id": TEARS_OF_GUTHIX_ACTIVITY_ID}
        return data, True, {
            "blue_tears": blue,
            "green_tears": green,
            "tears": tears,
            "remaining_beats": _beats(state["remaining_ticks"]),
            "status": state["last_result"],
        }

    reward_skill = reward_skill_pure(data)
    per_tear = xp_per_tear_pure(reward_skill["level"], state["ornate_bowl"])
    awarded = float(tears * per_tear)
    data[reward_skill["exp_key"]] = (
        _float(data.get(reward_skill["exp_key"])) + awarded
    )
    # The threshold is experience earned *since* the visit, so the baseline is
    # taken after the payout lands — otherwise the reward itself would count
    # towards the next visit's requirement.
    state["last_visit_exp"] = total_experience_pure(data)
    state["visits"] += 1
    state["allowance_week_index"] = _world_week(data)
    state["last_visit_quest_points"] = _int(data.get("quest_points"))
    message = (
        f"Juna accepts {tears} tears · +{awarded:,.0f} "
        f"{reward_skill['display_name']} XP at {per_tear} XP per tear"
        + (" (ornate bowl)" if state["ornate_bowl"] else "")
    )
    _end_session(data, state, message)
    return data, True, {
        "blue_tears": blue,
        "green_tears": green,
        "tears": tears,
        "remaining_beats": 0,
        "completed": True,
        "outcome": message,
        "status": message,
        "reward_skill_id": reward_skill["id"],
        "reward_skill_name": reward_skill["display_name"],
        "xp_per_tear": per_tear,
        "xp_rewards": {reward_skill["exp_key"]: awarded},
    }
