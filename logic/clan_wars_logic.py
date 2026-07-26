"""Pure Clan Wars portal policies and bounded review combat."""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.clan_wars_data import (
    CLAN_WARS_ACTIVITY_ID,
    CLAN_WARS_COMBAT_TARGET_ID,
    CLAN_WARS_COMBAT_TICKS,
    CLAN_WARS_MAX_REVIEWS,
    CLAN_WARS_MODE_IDS,
    CLAN_WARS_MODES_BY_ID,
    CLAN_WARS_OPPONENT_OFFSETS,
    CLAN_WARS_POLICIES_BY_ID,
    CLAN_WARS_POLICY_DAMAGE_MULTIPLIERS,
    CLAN_WARS_POLICY_IDS,
    CLAN_WARS_PURPLE_MODE,
    CLAN_WARS_RED_MODE,
    CLAN_WARS_SOURCE,
    CLAN_WARS_WHITE_MODE,
)
from ..logic_pure.logic_pure import (
    apply_combat_burst_pure,
    combat_max_lifepoints_pure,
    player_combat_level_pure,
)


CLAN_WARS_STATE_VERSION = 1
_VALID_MODES = frozenset(CLAN_WARS_MODE_IDS)
_VALID_POLICIES = frozenset(CLAN_WARS_POLICY_IDS)


def _int(
    value: Any,
    default: int = 0,
    *,
    minimum: int = 0,
    maximum: int = 2_147_483_647,
) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def _empty_activity_session() -> dict[str, str]:
    return {"active_id": ""}


def default_clan_wars_state_pure() -> dict[str, Any]:
    return {
        "clan_wars": {},
        "clan_wars_policy": {
            "mode": CLAN_WARS_WHITE_MODE,
            "strategy": "balanced",
        },
        "clan_wars_matches": 0,
        "clan_wars_wins": 0,
        "clan_wars_losses": 0,
        "clan_wars_draws": 0,
        "clan_wars_deaths": 0,
        "clan_wars_kills": 0,
        "clan_wars_exits": 0,
        "clan_wars_last_result": "",
    }


def _sanitize_policy(raw: Any) -> dict[str, str]:
    source = raw if isinstance(raw, Mapping) else {}
    mode = str(source.get("mode", CLAN_WARS_WHITE_MODE))
    strategy = str(source.get("strategy", "balanced"))
    return {
        "mode": mode if mode in _VALID_MODES else CLAN_WARS_WHITE_MODE,
        "strategy": strategy if strategy in _VALID_POLICIES else "balanced",
    }


def _opponent_stats(combat_level: int) -> dict[str, int]:
    core = max(1, min(99, round(combat_level * 0.75)))
    constitution = max(10, min(99, round(combat_level * 0.75 + 8)))
    return {
        "attack": core,
        "strength": core,
        "defence": core,
        "hitpoints": constitution * 10,
        "magic": core,
        "ranged": core,
    }


def _new_opponent(
    player_data: Mapping[str, Any],
    match_number: int,
    opponent_number: int,
) -> dict[str, Any]:
    player_level = player_combat_level_pure(player_data)
    offset = CLAN_WARS_OPPONENT_OFFSETS[
        (max(1, opponent_number) - 1) % len(CLAN_WARS_OPPONENT_OFFSETS)
    ]
    level = max(3, min(138, player_level + offset))
    maximum = _opponent_stats(level)["hitpoints"]
    return {
        "opponent_id": f"clan-wars-{match_number}-{opponent_number}",
        "display_name": f"Clan Wars rival {opponent_number} (level {level})",
        "combat_level": level,
        "lifepoints": maximum,
        "maximum_lifepoints": maximum,
        "encounter": {},
    }


def _sanitize_opponent(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    opponent_id = str(raw.get("opponent_id", ""))[:80]
    level = _int(raw.get("combat_level"), 3, minimum=3, maximum=138)
    maximum = _opponent_stats(level)["hitpoints"]
    lifepoints = _int(raw.get("lifepoints"), maximum, maximum=maximum)
    if not opponent_id or lifepoints <= 0:
        return {}
    encounter = raw.get("encounter")
    return {
        "opponent_id": opponent_id,
        "display_name": str(
            raw.get("display_name", f"Clan Wars rival (level {level})")
        )[:100],
        "combat_level": level,
        "lifepoints": lifepoints,
        "maximum_lifepoints": maximum,
        "encounter": (
            copy.deepcopy(dict(encounter))
            if isinstance(encounter, Mapping)
            else {}
        ),
    }


def _sanitize_session(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    policy = _sanitize_policy(raw)
    opponent = _sanitize_opponent(raw.get("opponent"))
    if not opponent:
        return {}
    return {
        "version": CLAN_WARS_STATE_VERSION,
        "match_number": _int(raw.get("match_number"), 1, minimum=1),
        "review": _int(raw.get("review"), maximum=CLAN_WARS_MAX_REVIEWS),
        "mode": policy["mode"],
        "strategy": policy["strategy"],
        "opponent_number": _int(
            raw.get("opponent_number"), 1, minimum=1, maximum=1_000_000
        ),
        "opponent": opponent,
        "player_score": _int(raw.get("player_score")),
        "opponent_score": _int(raw.get("opponent_score")),
        "previous_combat_target": str(
            raw.get("previous_combat_target", "")
        )[:120],
        "boosts_clamped": bool(raw.get("boosts_clamped", False)),
    }


def sanitize_clan_wars_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_clan_wars_state_pure()
    session = _sanitize_session(source.get("clan_wars"))
    active = source.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if session and active_id not in {"", CLAN_WARS_ACTIVITY_ID}:
        session = {}
    return {
        **defaults,
        "clan_wars": session,
        "clan_wars_policy": _sanitize_policy(
            source.get("clan_wars_policy")
        ),
        "clan_wars_matches": _int(source.get("clan_wars_matches")),
        "clan_wars_wins": _int(source.get("clan_wars_wins")),
        "clan_wars_losses": _int(source.get("clan_wars_losses")),
        "clan_wars_draws": _int(source.get("clan_wars_draws")),
        "clan_wars_deaths": _int(source.get("clan_wars_deaths")),
        "clan_wars_kills": _int(source.get("clan_wars_kills")),
        "clan_wars_exits": _int(source.get("clan_wars_exits")),
        "clan_wars_last_result": str(
            source.get("clan_wars_last_result", "")
        )[:500],
    }


def _clamp_red_portal_boosts(data: dict[str, Any]) -> bool:
    current = data.get("combat_current_levels")
    if not isinstance(current, Mapping):
        return False
    clamped = copy.deepcopy(dict(current))
    changed = False
    for skill_id, multiplier in (
        ("attack", 0.15),
        ("strength", 0.15),
        ("defense", 0.15),
        ("ranged", 0.10),
        ("magic", 0.0),
    ):
        base_key = "defense_level" if skill_id == "defense" else f"{skill_id}_level"
        base = max(1, _int(data.get(base_key), 1, minimum=1, maximum=99))
        maximum = base + 5 + int(base * multiplier)
        value = _int(clamped.get(skill_id), base, minimum=1)
        if value > maximum:
            clamped[skill_id] = maximum
            changed = True
    data["combat_current_levels"] = clamped
    return changed


def _copy_active_carried_pack(
    data: dict[str, Any],
    previous_target: str,
) -> None:
    carried = data.get("carried_inventory")
    if not isinstance(carried, Mapping):
        return
    source = carried.get(previous_target)
    if not isinstance(source, Mapping):
        return
    copied = copy.deepcopy(dict(carried))
    copied[CLAN_WARS_COMBAT_TARGET_ID] = copy.deepcopy(dict(source))
    data["carried_inventory"] = copied


def _remove_activity_carried_pack(data: dict[str, Any]) -> None:
    for key in ("carried_inventory", "carried_churn"):
        raw = data.get(key)
        if not isinstance(raw, Mapping) or CLAN_WARS_COMBAT_TARGET_ID not in raw:
            continue
        copied = copy.deepcopy(dict(raw))
        copied.pop(CLAN_WARS_COMBAT_TARGET_ID, None)
        data[key] = copied


def _enemy_for(opponent: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    level = int(opponent["combat_level"])
    return {
        CLAN_WARS_COMBAT_TARGET_ID: {
            "display_name": str(opponent["display_name"]),
            "level": level,
            "group": "Clan Wars",
            "stats": _opponent_stats(level),
            "bonuses": {},
            "attack_speed": 4,
            "drops": {"guaranteed": (), "tables": ()},
            "xp_multiplier": 1.0,
            "source": CLAN_WARS_SOURCE
            + "; disclosed bounded simulated opponent",
        }
    }


def _restore_safe_resources(data: dict[str, Any]) -> None:
    data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
    data["combat_prayer_points"] = max(
        1, _int(data.get("prayer_level"), 1, minimum=1)
    ) * 10
    data["combat_status_effects"] = {}


def _finish(
    data: dict[str, Any],
    session: Mapping[str, Any],
    message: str,
) -> None:
    data["clan_wars"] = {}
    data["activity_session"] = _empty_activity_session()
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(
        session.get("previous_combat_target", "")
    )
    data["clan_wars_last_result"] = message
    _remove_activity_carried_pack(data)


def set_clan_wars_policy_pure(
    player_data: Mapping[str, Any],
    mode: str,
    strategy: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_clan_wars_state_pure(data)
    if state["clan_wars"]:
        return data, False, {
            "reason": "Finish or leave the active Clan Wars match first."
        }
    if mode not in _VALID_MODES:
        return data, False, {"reason": "Unknown Clan Wars portal mode."}
    if strategy not in _VALID_POLICIES:
        return data, False, {"reason": "Unknown Clan Wars combat policy."}
    policy = {"mode": mode, "strategy": strategy}
    data.update(state)
    data["clan_wars_policy"] = policy
    return data, True, {
        "message": "Clan Wars portal plan saved.",
        "policy": dict(policy),
    }


def enter_clan_wars_pure(
    player_data: Mapping[str, Any],
    mode: str | None = None,
    strategy: str | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_clan_wars_state_pure(data)
    if state["clan_wars"]:
        return data, False, {"reason": "A Clan Wars match is already active."}
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if active_id and active_id != CLAN_WARS_ACTIVITY_ID:
        return data, False, {
            "reason": "Finish the active persistent activity first."
        }
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {
            "reason": "Finish or leave the current Combat encounter first."
        }
    selected_mode = str(mode or state["clan_wars_policy"]["mode"])
    selected_strategy = str(
        strategy or state["clan_wars_policy"]["strategy"]
    )
    if selected_mode not in _VALID_MODES:
        return data, False, {"reason": "Unknown Clan Wars portal mode."}
    if selected_strategy not in _VALID_POLICIES:
        return data, False, {"reason": "Unknown Clan Wars combat policy."}

    match_number = state["clan_wars_matches"] + 1
    previous_target = str(data.get("current_combat_target", ""))[:120]
    opponent = _new_opponent(data, match_number, 1)
    boosts_clamped = (
        _clamp_red_portal_boosts(data)
        if selected_mode == CLAN_WARS_RED_MODE
        else False
    )
    session = {
        "version": CLAN_WARS_STATE_VERSION,
        "match_number": match_number,
        "review": 0,
        "mode": selected_mode,
        "strategy": selected_strategy,
        "opponent_number": 1,
        "opponent": opponent,
        "player_score": 0,
        "opponent_score": 0,
        "previous_combat_target": previous_target,
        "boosts_clamped": boosts_clamped,
    }
    data.update(state)
    data["clan_wars_policy"] = {
        "mode": selected_mode,
        "strategy": selected_strategy,
    }
    data["clan_wars_matches"] = match_number
    data["clan_wars"] = session
    data["activity_session"] = {"active_id": CLAN_WARS_ACTIVITY_ID}
    data["current_utility"] = CLAN_WARS_ACTIVITY_ID
    data["combat_encounter"] = {}
    _copy_active_carried_pack(data, previous_target)
    data["current_combat_target"] = CLAN_WARS_COMBAT_TARGET_ID
    mode_name = CLAN_WARS_MODES_BY_ID[selected_mode].display_name
    message = f"Entered {mode_name}."
    if boosts_clamped:
        message += " Extreme or Overload boosts were reduced to super-potion caps."
    data["clan_wars_last_result"] = message
    return data, True, {
        "message": message,
        "mode": selected_mode,
        "strategy": selected_strategy,
        "boosts_clamped": boosts_clamped,
    }


def _settle_match(
    data: dict[str, Any],
    session: Mapping[str, Any],
    *,
    forced_loss: bool = False,
) -> dict[str, Any]:
    player_score = int(session["player_score"])
    opponent_score = int(session["opponent_score"])
    if forced_loss or player_score < opponent_score:
        outcome = "loss"
        data["clan_wars_losses"] = _int(data.get("clan_wars_losses")) + 1
    elif player_score > opponent_score:
        outcome = "win"
        data["clan_wars_wins"] = _int(data.get("clan_wars_wins")) + 1
    else:
        outcome = "draw"
        data["clan_wars_draws"] = _int(data.get("clan_wars_draws")) + 1
    label = "Team race" if session["mode"] == CLAN_WARS_PURPLE_MODE else "Free-for-all"
    suffix = " Items lost in the red portal were destroyed." if forced_loss else ""
    message = (
        f"{label} {outcome} · {player_score}-{opponent_score} "
        f"after {int(session['review'])} reviews.{suffix}"
    )
    _finish(data, session, message)
    return {
        "terminal": True,
        "outcome": outcome,
        "player_score": player_score,
        "opponent_score": opponent_score,
        "message": message,
    }


def apply_clan_wars_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    equipment_data: Mapping[str, Any] | None = None,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_clan_wars_state_pure(data)
    session = state["clan_wars"]
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    if not session or active_id != CLAN_WARS_ACTIVITY_ID:
        return data, False, {
            "reason": "Enter a Clan Wars portal before training it."
        }
    if not productive:
        return data, True, {
            "advanced": False,
            "terminal": False,
            "message": "Clan Wars advances only on an eligible successful review.",
        }

    data.update(state)
    opponent = session["opponent"]
    data["current_combat_target"] = CLAN_WARS_COMBAT_TARGET_ID
    encounter = copy.deepcopy(opponent["encounter"])
    encounter["target_id"] = CLAN_WARS_COMBAT_TARGET_ID
    encounter["enemy_lifepoints"] = int(opponent["lifepoints"])
    data["combat_encounter"] = encounter
    original_auto_flee = bool(data.get("combat_auto_flee", True))
    data["combat_auto_flee"] = False
    dangerous = session["mode"] == CLAN_WARS_RED_MODE
    data, ok, combat = apply_combat_burst_pure(
        data,
        _enemy_for(opponent),
        equipment_data or {},
        ticks=CLAN_WARS_COMBAT_TICKS,
        rng=rng or (lambda: 0.5),
        live_cadence=True,
        stop_after_first_kill=True,
        safe_death=not dangerous,
        no_grave=dangerous,
        allow_bank_run=False,
        player_damage_multiplier=CLAN_WARS_POLICY_DAMAGE_MULTIPLIERS[
            session["strategy"]
        ],
    )
    data["combat_auto_flee"] = original_auto_flee
    if not ok:
        return copy.deepcopy(dict(player_data)), False, {
            "reason": "Clan Wars combat setup is not runnable.",
            "combat": combat,
        }

    session["review"] += 1
    if combat.get("died"):
        data["clan_wars_deaths"] = state["clan_wars_deaths"] + 1
        session["opponent_score"] += 1
        if dangerous:
            data["clan_wars"] = session
            return data, True, {
                "advanced": True,
                "combat": combat,
                **_settle_match(data, session, forced_loss=True),
            }
        _restore_safe_resources(data)
        session["opponent_number"] += 1
        session["opponent"] = _new_opponent(
            data, session["match_number"], session["opponent_number"]
        )
        data["combat_encounter"] = {}
    elif combat.get("killed"):
        data["clan_wars_kills"] = state["clan_wars_kills"] + 1
        session["player_score"] += 1
        session["opponent_number"] += 1
        session["opponent"] = _new_opponent(
            data, session["match_number"], session["opponent_number"]
        )
        data["combat_encounter"] = {}
    else:
        encounter_after = data.get("combat_encounter")
        if isinstance(encounter_after, Mapping):
            opponent["lifepoints"] = _int(
                encounter_after.get("enemy_lifepoints"),
                int(opponent["lifepoints"]),
                maximum=int(opponent["maximum_lifepoints"]),
            )
            opponent["encounter"] = copy.deepcopy(dict(encounter_after))

    # The opposing-team cadence is an explicit review-scale abstraction. It
    # makes the purple portal a bounded score race without inventing a period
    # reward or claiming that RuneScape used review-count scoring.
    if (
        session["mode"] == CLAN_WARS_PURPLE_MODE
        and session["review"] % 2 == 0
    ):
        session["opponent_score"] += 1

    if session["review"] >= CLAN_WARS_MAX_REVIEWS:
        data["clan_wars"] = session
        return data, True, {
            "advanced": True,
            "combat": combat,
            **_settle_match(data, session),
        }

    data["clan_wars"] = session
    data["clan_wars_last_result"] = (
        f"Clan Wars in progress · {session['player_score']}-"
        f"{session['opponent_score']} after {session['review']} reviews."
    )
    return data, True, {
        "advanced": True,
        "terminal": False,
        "combat": combat,
        "player_score": session["player_score"],
        "opponent_score": session["opponent_score"],
        "message": data["clan_wars_last_result"],
    }


def leave_clan_wars_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_clan_wars_state_pure(data)
    session = state["clan_wars"]
    if not session:
        return data, False, {"reason": "No Clan Wars match is active."}
    data.update(state)
    data["clan_wars_exits"] = state["clan_wars_exits"] + 1
    message = (
        f"Left Clan Wars through the portal at "
        f"{session['player_score']}-{session['opponent_score']}."
    )
    _finish(data, session, message)
    return data, True, {"message": message, "outcome": "exit"}


def teleport_escape_clan_wars_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    state = sanitize_clan_wars_state_pure(player_data)
    session = state["clan_wars"]
    if not session:
        return copy.deepcopy(dict(player_data)), False, {
            "reason": "No Clan Wars match is active."
        }
    if session["mode"] == CLAN_WARS_RED_MODE:
        return copy.deepcopy(dict(player_data)), False, {
            "reason": "Teleport escape is forbidden in the dangerous red portal."
        }
    return leave_clan_wars_pure(player_data)


def apply_clan_wars_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "set_policy":
        return set_clan_wars_policy_pure(
            player_data,
            str(body.get("mode", "")),
            str(body.get("strategy", "")),
        )
    if action_id == "enter":
        return enter_clan_wars_pure(
            player_data,
            str(body.get("mode", "")) or None,
            str(body.get("strategy", "")) or None,
        )
    if action_id == "leave":
        return leave_clan_wars_pure(player_data)
    if action_id == "teleport_escape":
        return teleport_escape_clan_wars_pure(player_data)
    return copy.deepcopy(dict(player_data)), False, {
        "reason": "Unknown Clan Wars command."
    }


def clan_wars_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_clan_wars_state_pure(player_data)
    session = state["clan_wars"]
    active = player_data.get("activity_session")
    active_id = (
        str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    )
    encounter = player_data.get("combat_encounter")
    reasons = []
    if active_id and active_id != CLAN_WARS_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    if not session and isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter.")
    policy = (
        {"mode": session["mode"], "strategy": session["strategy"]}
        if session
        else state["clan_wars_policy"]
    )
    mode = CLAN_WARS_MODES_BY_ID[policy["mode"]]
    return {
        **state,
        "active": bool(session),
        "can_enter": not reasons and not session,
        "entry_reasons": tuple(reasons),
        "selected_mode": policy["mode"],
        "selected_strategy": policy["strategy"],
        "mode_display_name": mode.display_name,
        "mode_description": mode.description,
        "dangerous": mode.dangerous,
        "safe_death": not mode.dangerous,
        "teleport_escape_allowed": bool(session)
        and session["mode"] != CLAN_WARS_RED_MODE,
        "extreme_potions_allowed": not (
            bool(session) and session["mode"] == CLAN_WARS_RED_MODE
        ),
        "maximum_reviews": CLAN_WARS_MAX_REVIEWS,
        "source": CLAN_WARS_SOURCE,
    }
