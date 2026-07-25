"""Pure weekly roster, spying, and redemption for Penguin Hide and Seek."""

from __future__ import annotations

from typing import Any, Mapping

from ..data.penguin_hide_and_seek_data import (
    PENGUIN_COINS_PER_POINT,
    PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID,
    PENGUIN_ONE_POINT_SPAWNS,
    PENGUIN_POINT_CAP,
    PENGUIN_POLAR_BEAR_LOCATIONS,
    PENGUIN_TWO_POINT_SPAWNS,
    PENGUIN_WEEK_REVIEWS,
    PENGUIN_XP_PER_LEVEL_POINT,
    PenguinSpawn,
)
from ..core.skill_registry import get_skill, trainable_skill_definitions


PENGUIN_STATE_VERSION = 1
_VALID_SPAWN_IDS = {
    spawn.id for spawn in (*PENGUIN_ONE_POINT_SPAWNS, *PENGUIN_TWO_POINT_SPAWNS)
} | {"polar_bear", "invisible_penguin"}


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _quest_state(player_data: Mapping[str, Any], quest_id: str) -> Mapping[str, Any]:
    quests = player_data.get("quests")
    if not isinstance(quests, Mapping):
        return {}
    state = quests.get(quest_id)
    return state if isinstance(state, Mapping) else {}


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    return bool(_quest_state(player_data, quest_id).get("completed", False))


def _quest_started(player_data: Mapping[str, Any], quest_id: str) -> bool:
    state = _quest_state(player_data, quest_id)
    return bool(
        state.get("completed", False)
        or state.get("started", False)
        or _int(state.get("progress")) > 0
    )


def _has_ring_of_visibility(player_data: Mapping[str, Any]) -> bool:
    inventory = player_data.get("inventory")
    carried_by_target = player_data.get("carried_inventory")
    carried = (
        carried_by_target.get(PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID)
        if isinstance(carried_by_target, Mapping)
        else None
    )
    equipment = player_data.get("equipment")
    return bool(
        isinstance(inventory, Mapping)
        and isinstance(carried, Mapping)
        and _int(inventory.get("Ring of visibility")) > 0
        and _int(carried.get("Ring of visibility")) > 0
    ) or bool(
        isinstance(equipment, Mapping)
        and "Ring of visibility" in {str(item) for item in equipment.values()}
    )


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    return _int(clock.get("answered_cards"))


def penguin_week_index_pure(player_data: Mapping[str, Any]) -> int:
    return _answered_cards(player_data) // PENGUIN_WEEK_REVIEWS


def default_penguin_state_pure() -> dict[str, Any]:
    return {
        "version": PENGUIN_STATE_VERSION,
        "week_index": -1,
        "spotted_ids": [],
        "selected_id": "",
        "points": 0,
        "lifetime_spotted": 0,
        "last_result": "",
    }


def sanitize_penguin_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_penguin_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    spotted = source.get("spotted_ids")
    spotted_ids = (
        [
            spawn_id
            for spawn_id in dict.fromkeys(str(value) for value in spotted)
            if spawn_id in _VALID_SPAWN_IDS
        ]
        if isinstance(spotted, (list, tuple))
        else []
    )
    selected_id = str(source.get("selected_id", ""))
    return {
        **defaults,
        "week_index": max(-1, _int(source.get("week_index"), -1, minimum=-1)),
        "spotted_ids": spotted_ids,
        "selected_id": selected_id if selected_id in _VALID_SPAWN_IDS else "",
        "points": min(PENGUIN_POINT_CAP, _int(source.get("points"))),
        "lifetime_spotted": _int(source.get("lifetime_spotted")),
        "last_result": str(source.get("last_result", ""))[:280],
    }


def _sync_week(player_data: Mapping[str, Any], state: Mapping[str, Any]) -> dict[str, Any]:
    synced = dict(state)
    week_index = penguin_week_index_pure(player_data)
    if synced.get("week_index") != week_index:
        synced.update({"week_index": week_index, "spotted_ids": [], "selected_id": ""})
    return synced


def _rotate(pool: tuple[PenguinSpawn, ...], week_index: int) -> tuple[PenguinSpawn, ...]:
    offset = week_index % len(pool)
    ordered = pool[offset:] + pool[:offset]
    return ordered[:5]


def _ordinary_roster(player_data: Mapping[str, Any], week_index: int) -> list[dict[str, Any]]:
    cold_war = _quest_complete(player_data, "cold_war")
    rows: list[dict[str, Any]] = []
    for spawn in _rotate(PENGUIN_ONE_POINT_SPAWNS, week_index):
        rows.append({
            "id": spawn.id,
            "location": spawn.location,
            "disguise": spawn.disguise,
            "detail": spawn.detail,
            "points": 1,
            "kind": "ordinary",
        })
    for spawn in _rotate(PENGUIN_TWO_POINT_SPAWNS, week_index):
        rows.append({
            "id": spawn.id,
            "location": spawn.location,
            "disguise": spawn.disguise,
            "detail": spawn.detail,
            "points": 2 if cold_war else 1,
            "kind": "ordinary",
        })
    return rows


def penguin_roster_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    state = _sync_week(
        player_data,
        sanitize_penguin_state_pure(player_data.get("penguin_hide_and_seek")),
    )
    week_index = int(state["week_index"])
    rows = _ordinary_roster(player_data, week_index)
    if _quest_complete(player_data, "hunt_for_red_raktuber"):
        rows.append({
            "id": "polar_bear",
            "location": PENGUIN_POLAR_BEAR_LOCATIONS[
                week_index % len(PENGUIN_POLAR_BEAR_LOCATIONS)
            ],
            "disguise": "Well",
            "detail": "the stationary PBJ polar-bear agent",
            "points": 1,
            "kind": "polar_bear",
        })
    if (
        _quest_complete(player_data, "some_like_it_cold")
        and _quest_started(player_data, "desert_treasure")
        and _has_ring_of_visibility(player_data)
    ):
        ghost_spawn = PENGUIN_ONE_POINT_SPAWNS[
            (week_index + 3) % len(PENGUIN_ONE_POINT_SPAWNS)
        ]
        rows.append({
            "id": "invisible_penguin",
            "location": ghost_spawn.location,
            "disguise": "Invisible",
            "detail": "visible through the Ring of visibility",
            "points": 3,
            "kind": "invisible",
        })
    spotted = set(state["spotted_ids"])
    return tuple({**row, "spotted": row["id"] in spotted} for row in rows)


def penguin_reward_skills_pure() -> tuple[dict[str, str], ...]:
    return tuple(
        {
            "id": skill.id,
            "display_name": skill.display_name,
            "level_key": skill.level_key,
            "exp_key": skill.exp_key,
        }
        for skill in trainable_skill_definitions()
    )


def penguin_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = _sync_week(
        player_data,
        sanitize_penguin_state_pure(player_data.get("penguin_hide_and_seek")),
    )
    roster = penguin_roster_pure({**dict(player_data), "penguin_hide_and_seek": state})
    spotted = sum(1 for row in roster if row["spotted"])
    selected = next(
        (row for row in roster if row["id"] == state["selected_id"] and not row["spotted"]),
        None,
    )
    return {
        **state,
        "roster": roster,
        "spotted_count": spotted,
        "roster_count": len(roster),
        "selected": selected,
        "can_review": selected is not None,
        "cold_war_bonus": _quest_complete(player_data, "cold_war"),
        "polar_bear_unlocked": _quest_complete(player_data, "hunt_for_red_raktuber"),
        "invisible_unlocked": any(row["kind"] == "invisible" for row in roster),
    }


def apply_penguin_review_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the week state is rebuilt rather than written
    # through, and the quest state alias is only read.
    data = dict(player_data)
    state = _sync_week(data, sanitize_penguin_state_pure(data.get("penguin_hide_and_seek")))
    data["penguin_hide_and_seek"] = state
    view = penguin_view_pure(data)
    selected = view.get("selected")
    if not isinstance(selected, Mapping):
        return data, False, {"reason": "Select an unspotted penguin first."}

    points_before = int(state["points"])
    possible = _int(selected.get("points"))
    awarded = min(possible, PENGUIN_POINT_CAP - points_before)
    lost = possible - awarded
    state["points"] = points_before + awarded
    state["spotted_ids"] = [*state["spotted_ids"], str(selected["id"])]
    state["selected_id"] = ""
    state["lifetime_spotted"] += 1
    state["last_result"] = (
        f"Spied the {str(selected['disguise']).lower()} penguin at "
        f"{selected['location']} · +{awarded} point"
        + ("s" if awarded != 1 else "")
        + (f" · {lost} lost at the 50-point cap" if lost else "")
    )
    data["penguin_hide_and_seek"] = state
    return data, True, {
        "action_id": str(selected["id"]),
        "location": str(selected["location"]),
        "disguise": str(selected["disguise"]),
        "points_awarded": awarded,
        "points_lost": lost,
        "status": state["last_result"],
    }


def apply_penguin_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the week state is rebuilt rather than written
    # through, and the quest state alias is only read.
    data = dict(player_data)
    state = _sync_week(data, sanitize_penguin_state_pure(data.get("penguin_hide_and_seek")))
    data["penguin_hide_and_seek"] = state
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "select_spy":
        spawn_id = str(payload.get("spawn_id", ""))
        row = next((row for row in penguin_roster_pure(data) if row["id"] == spawn_id), None)
        if row is None or row["spotted"]:
            return data, False, {"reason": "Choose an unspotted penguin from this week's roster."}
        state["selected_id"] = spawn_id
        data["penguin_hide_and_seek"] = state
        return data, True, {"selected_id": spawn_id, "message": f"Selected {row['location']}."}

    points = int(state["points"])
    if action_id == "redeem_coins":
        if points <= 0:
            return data, False, {"reason": "You have no Penguin Points to redeem."}
        coins = points * PENGUIN_COINS_PER_POINT
        inventory = dict(data.get("inventory", {}) or {})
        inventory["Coins"] = _int(inventory.get("Coins")) + coins
        data["inventory"] = inventory
        state["points"] = 0
        state["last_result"] = f"Redeemed {points} Penguin Points for {coins:,} coins."
        data["penguin_hide_and_seek"] = state
        return data, True, {"coins": coins, "points_spent": points, "message": state["last_result"]}

    if action_id == "redeem_xp":
        skill_id = str(payload.get("skill_id", ""))
        skill = get_skill(skill_id)
        valid_ids = {row["id"] for row in penguin_reward_skills_pure()}
        if skill is None or skill_id not in valid_ids:
            return data, False, {"reason": "Choose a trainable skill for the XP reward."}
        if points <= 0:
            return data, False, {"reason": "You have no Penguin Points to redeem."}
        level = max(1, _int(data.get(skill.level_key), 1, minimum=1))
        xp = float(level * PENGUIN_XP_PER_LEVEL_POINT * points)
        data[skill.exp_key] = float(data.get(skill.exp_key, 0.0) or 0.0) + xp
        state["points"] = 0
        state["last_result"] = (
            f"Redeemed {points} Penguin Points for {xp:,.0f} {skill.display_name} XP."
        )
        data["penguin_hide_and_seek"] = state
        return data, True, {
            "skill_id": skill.id,
            "skill_name": skill.display_name,
            "exp_key": skill.exp_key,
            "xp": xp,
            "points_spent": points,
            "message": state["last_result"],
        }

    return data, False, {"reason": "Unknown Penguin Hide and Seek command."}
