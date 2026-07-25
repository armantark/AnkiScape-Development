"""Pure Sorceress's Garden state, review action, and direct commands."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..data.sorceress_garden_data import (
    SORCERESS_GARDEN_HERB_POOL,
    SORCERESS_GARDEN_SEASONS,
    SORCERESS_GARDEN_SEASONS_BY_ID,
)


SORCERESS_GARDEN_STATE_VERSION = 1
HARVEST_MODES = ("fruit", "herbs", "alternate")
JUICE_MODES = ("osman", "keep")


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _quest_complete(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    if not isinstance(quests, Mapping):
        return False
    state = quests.get(quest_id)
    return isinstance(state, Mapping) and bool(state.get("completed", False))


def effective_thieving_level_pure(player_data: Mapping[str, Any]) -> int:
    base = _int(player_data.get("thieving_level"), 1, minimum=1)
    current = player_data.get("combat_current_levels")
    if not isinstance(current, Mapping) or "thieving" not in current:
        return base
    return max(1, _int(current.get("thieving"), base, minimum=1))


def default_sorceress_garden_state_pure() -> dict[str, Any]:
    return {
        "version": SORCERESS_GARDEN_STATE_VERSION,
        "introduced": False,
        "season_id": "winter",
        "harvest_mode": "fruit",
        "juice_mode": "osman",
        "alternate_next": "fruit",
        "successful_trips": 0,
        "last_result": "",
    }


def sanitize_sorceress_garden_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_sorceress_garden_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    season_id = str(source.get("season_id", defaults["season_id"]))
    harvest_mode = str(source.get("harvest_mode", defaults["harvest_mode"]))
    juice_mode = str(source.get("juice_mode", defaults["juice_mode"]))
    alternate_next = str(source.get("alternate_next", defaults["alternate_next"]))
    return {
        **defaults,
        "introduced": bool(source.get("introduced", False)),
        "season_id": (
            season_id if season_id in SORCERESS_GARDEN_SEASONS_BY_ID else "winter"
        ),
        "harvest_mode": harvest_mode if harvest_mode in HARVEST_MODES else "fruit",
        "juice_mode": juice_mode if juice_mode in JUICE_MODES else "osman",
        "alternate_next": alternate_next if alternate_next in {"fruit", "herbs"} else "fruit",
        "successful_trips": _int(source.get("successful_trips")),
        "last_result": str(source.get("last_result", ""))[:240],
    }


def sorceress_garden_locked_reasons_pure(
    player_data: Mapping[str, Any],
    season_id: str | None = None,
) -> tuple[str, ...]:
    state = sanitize_sorceress_garden_state_pure(
        player_data.get("sorceress_garden")
    )
    selected = str(season_id or state["season_id"])
    season = SORCERESS_GARDEN_SEASONS_BY_ID.get(selected)
    reasons: list[str] = []
    if not _quest_complete(player_data, "diamond_in_the_rough"):
        reasons.append("Diamond in the Rough")
    elif not state["introduced"]:
        reasons.append("the Osman introduction")
    if season is None:
        reasons.append("valid seasonal garden")
    elif effective_thieving_level_pure(player_data) < season.thieving_level:
        reasons.append(f"Thieving {season.thieving_level}")
    return tuple(reasons)


def sorceress_garden_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_sorceress_garden_state_pure(
        player_data.get("sorceress_garden")
    )
    quest_complete = _quest_complete(player_data, "diamond_in_the_rough")
    selected_season = SORCERESS_GARDEN_SEASONS_BY_ID[state["season_id"]]
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    return {
        **state,
        "quest_complete": quest_complete,
        "effective_thieving_level": effective_thieving_level_pure(player_data),
        "locked_reasons": sorceress_garden_locked_reasons_pure(player_data),
        "selected_fruit": selected_season.fruit,
        "fruit_progress": min(
            _int(inventory.get(selected_season.fruit)),
            selected_season.fruit_per_juice,
        ),
        "fruit_per_juice": selected_season.fruit_per_juice,
        "seasons": tuple(
            {
                "id": season.id,
                "display_name": season.display_name,
                "thieving_level": season.thieving_level,
                "fruit_per_juice": season.fruit_per_juice,
                "locked_reasons": sorceress_garden_locked_reasons_pure(
                    player_data, season.id
                ),
            }
            for season in SORCERESS_GARDEN_SEASONS
        ),
    }


def _roll_item(pool: Sequence[str], roll: Any) -> str:
    try:
        bounded = max(0.0, min(float(roll), 0.999999999))
    except (TypeError, ValueError, OverflowError):
        bounded = 0.0
    return pool[min(len(pool) - 1, int(bounded * len(pool)))]


def apply_sorceress_garden_review_pure(
    player_data: Mapping[str, Any],
    herb_rolls: Sequence[float] = (0.0, 0.5),
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: this only assigns top-level keys on the working copy;
    # the locked-reason helpers are read-only.
    data = dict(player_data)
    state = sanitize_sorceress_garden_state_pure(data.get("sorceress_garden"))
    data["sorceress_garden"] = state
    season = SORCERESS_GARDEN_SEASONS_BY_ID[state["season_id"]]
    locked = sorceress_garden_locked_reasons_pure(data, season.id)
    if locked:
        return data, {"allowed": False, "locked_reasons": locked}

    harvest = state["harvest_mode"]
    if harvest == "alternate":
        harvest = state["alternate_next"]
    inventory = dict(data.get("inventory", {}) or {})
    outputs: dict[str, int] = {}
    thieving_xp = 0.0
    juices_completed = 0

    if harvest == "herbs":
        rolls = tuple(herb_rolls) or (0.0, 0.5)
        for index in range(2):
            item = _roll_item(
                SORCERESS_GARDEN_HERB_POOL,
                rolls[index % len(rolls)],
            )
            inventory[item] = _int(inventory.get(item)) + 1
            outputs[item] = outputs.get(item, 0) + 1
        farming_xp = season.herb_farming_xp
        result_text = " and ".join(
            f"{quantity} {item}" for item, quantity in outputs.items()
        )
    else:
        inventory[season.fruit] = _int(inventory.get(season.fruit)) + 1
        outputs[season.fruit] = 1
        farming_xp = season.fruit_farming_xp
        while _int(inventory.get(season.fruit)) >= season.fruit_per_juice:
            inventory[season.fruit] -= season.fruit_per_juice
            if inventory[season.fruit] <= 0:
                inventory.pop(season.fruit, None)
            outputs[season.fruit] = outputs.get(season.fruit, 0) - season.fruit_per_juice
            juices_completed += 1
            if state["juice_mode"] == "osman":
                thieving_xp += season.osman_thieving_xp
            else:
                inventory[season.juice] = _int(inventory.get(season.juice)) + 1
                outputs[season.juice] = outputs.get(season.juice, 0) + 1
        outputs = {name: qty for name, qty in outputs.items() if qty > 0}
        result_text = season.fruit
        if juices_completed:
            result_text += (
                f" · {juices_completed} juice handed to Osman"
                if state["juice_mode"] == "osman"
                else f" · {juices_completed} juice kept"
            )

    data["inventory"] = inventory
    if state["harvest_mode"] == "alternate":
        state["alternate_next"] = "herbs" if harvest == "fruit" else "fruit"
    state["successful_trips"] += 1
    state["last_result"] = (
        f"{season.display_name} garden · {result_text} · "
        f"+{int(farming_xp)} Farming XP"
        + (f" · +{int(thieving_xp)} Thieving XP" if thieving_xp else "")
    )
    data["sorceress_garden"] = state
    return data, {
        "allowed": True,
        "success": True,
        "action_id": f"{season.id}_{harvest}",
        "season_id": season.id,
        "harvest": harvest,
        "farming_xp": farming_xp,
        "thieving_xp": thieving_xp,
        "outputs": outputs,
        "juices_completed": juices_completed,
        "status": state["last_result"],
    }


def apply_sorceress_garden_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: this only assigns top-level keys on the working copy;
    # the locked-reason helpers are read-only.
    data = dict(player_data)
    state = sanitize_sorceress_garden_state_pure(data.get("sorceress_garden"))
    payload = payload if isinstance(payload, Mapping) else {}

    if action_id == "introduce":
        if not _quest_complete(data, "diamond_in_the_rough"):
            return data, False, {"reason": "Complete Diamond in the Rough first."}
        if state["introduced"]:
            return data, False, {"reason": "The Garden introduction is already complete."}
        state["introduced"] = True
        state["last_result"] = "Osman and the apprentice introduced the Sorceress's Garden."
    elif action_id == "set_preferences":
        season_id = str(payload.get("season_id", state["season_id"]))
        harvest_mode = str(payload.get("harvest_mode", state["harvest_mode"]))
        juice_mode = str(payload.get("juice_mode", state["juice_mode"]))
        if season_id not in SORCERESS_GARDEN_SEASONS_BY_ID:
            return data, False, {"reason": "Unknown seasonal garden."}
        if harvest_mode not in HARVEST_MODES or juice_mode not in JUICE_MODES:
            return data, False, {"reason": "Unknown Garden preference."}
        state.update({
            "season_id": season_id,
            "harvest_mode": harvest_mode,
            "juice_mode": juice_mode,
        })
    else:
        return data, False, {"reason": "Unknown Sorceress's Garden command."}

    data["sorceress_garden"] = state
    return data, True, {"message": state.get("last_result", "Preferences saved.")}
