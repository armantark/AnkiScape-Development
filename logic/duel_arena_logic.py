"""Pure, bounded Duel Arena challenge lifecycle."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..data.duel_arena_data import (
    DUEL_ARENA_ACTIVITY_ID,
    DUEL_ARENA_MAX_COMBAT_LEVEL,
    DUEL_ARENA_MAX_REVIEWS,
    DUEL_ARENA_MIN_COMBAT_LEVEL,
    DUEL_ARENA_OPPONENT_OFFSETS,
    DUEL_ARENA_POINTS_TO_WIN,
    DUEL_ARENA_RULE_IDS,
    DUEL_ARENA_RULES_BY_ID,
    DUEL_ARENA_SOURCE,
    DUELLISTS_CAP_TIERS,
)
from ..logic_pure.logic_pure import (
    combat_max_lifepoints_pure,
    player_combat_level_pure,
)


DUEL_ARENA_STATE_VERSION = 1
_RULE_ID_SET = frozenset(DUEL_ARENA_RULE_IDS)
_CAP_ITEM_NAMES = tuple(tier.item_name for tier in DUELLISTS_CAP_TIERS)


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


def _normalized_rule_ids(raw: Any) -> tuple[str, ...]:
    if not isinstance(raw, (list, tuple, set, frozenset)):
        return ()
    selected = {str(value) for value in raw if str(value) in _RULE_ID_SET}
    return tuple(rule_id for rule_id in DUEL_ARENA_RULE_IDS if rule_id in selected)


def _rules_failure(rule_ids: tuple[str, ...]) -> str:
    selected = set(rule_ids)
    if {"no_ranged", "no_melee", "no_magic"} <= selected:
        return "At least one combat style must remain available."
    if {"no_movement", "obstacles"} <= selected:
        return "No Movement and Obstacles cannot be enabled together."
    return ""


def default_duel_arena_state_pure() -> dict[str, Any]:
    return {
        "duel_arena": {},
        "duel_arena_rule_ids": (),
        "duel_arena_matches": 0,
        "duel_arena_wins": 0,
        "duel_arena_losses": 0,
        "duel_arena_abandons": 0,
        "duel_arena_last_result": "",
    }


def duellists_cap_tier_pure(wins: Any) -> dict[str, Any]:
    win_count = _int(wins)
    current = DUELLISTS_CAP_TIERS[0]
    for tier in DUELLISTS_CAP_TIERS:
        if win_count >= tier.minimum_wins:
            current = tier
    next_tier = next(
        (tier for tier in DUELLISTS_CAP_TIERS if tier.minimum_wins > win_count),
        None,
    )
    return {
        "tier": current.tier,
        "minimum_wins": current.minimum_wins,
        "item_name": current.item_name,
        "asset_filename": current.asset_filename,
        "next_tier": next_tier.tier if next_tier else None,
        "next_wins": next_tier.minimum_wins if next_tier else None,
        "wins_remaining": max(0, next_tier.minimum_wins - win_count)
        if next_tier
        else 0,
    }


def _owned_cap_item(player_data: Mapping[str, Any]) -> tuple[str, str]:
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping):
        for slot, item_name in equipment.items():
            if str(item_name) in _CAP_ITEM_NAMES:
                return str(item_name), f"equipment:{slot}"
    inventory = player_data.get("inventory")
    if isinstance(inventory, Mapping):
        for item_name in reversed(_CAP_ITEM_NAMES):
            if _int(inventory.get(item_name)) > 0:
                return item_name, "inventory"
    return "", ""


def _set_owned_cap_tier(data: dict[str, Any], item_name: str) -> bool:
    owned_item, location = _owned_cap_item(data)
    if not owned_item:
        return False
    inventory = (
        dict(data.get("inventory"))
        if isinstance(data.get("inventory"), Mapping)
        else {}
    )
    equipment = (
        dict(data.get("equipment"))
        if isinstance(data.get("equipment"), Mapping)
        else {}
    )
    for cap_name in _CAP_ITEM_NAMES:
        inventory.pop(cap_name, None)
    equipped_slot = ""
    if location.startswith("equipment:"):
        equipped_slot = location.split(":", 1)[1]
    for slot, equipped_item in tuple(equipment.items()):
        if str(equipped_item) in _CAP_ITEM_NAMES:
            equipment.pop(slot, None)
    if equipped_slot:
        equipment[equipped_slot] = item_name
    else:
        inventory[item_name] = 1
    data["inventory"] = inventory
    data["equipment"] = equipment
    return owned_item != item_name


def claim_duellists_cap_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_duel_arena_state_pure(data)
    if state["duel_arena"]:
        return data, False, {"reason": "Finish or abandon the active duel first."}
    target = duellists_cap_tier_pure(state["duel_arena_wins"])
    owned_item, _location = _owned_cap_item(data)
    if owned_item == target["item_name"]:
        return data, False, {"reason": "You already own the current Duellist's cap."}
    if owned_item:
        _set_owned_cap_tier(data, target["item_name"])
        verb = "Changed"
    else:
        inventory = (
            dict(data.get("inventory"))
            if isinstance(data.get("inventory"), Mapping)
            else {}
        )
        inventory[target["item_name"]] = 1
        data["inventory"] = inventory
        verb = "Claimed"
    data.update(state)
    message = f"{verb} Duellist's cap to tier {target['tier']}."
    data["duel_arena_last_result"] = message
    return data, True, {"message": message, "cap": target}


def _opponent_for(
    player_data: Mapping[str, Any],
    duel_number: int,
    opponent_level: int | None = None,
) -> dict[str, Any]:
    player_level = player_combat_level_pure(player_data)
    if opponent_level is None:
        offset = DUEL_ARENA_OPPONENT_OFFSETS[
            (max(1, duel_number) - 1) % len(DUEL_ARENA_OPPONENT_OFFSETS)
        ]
        opponent_level = player_level + offset
    level = _int(
        opponent_level,
        player_level,
        minimum=DUEL_ARENA_MIN_COMBAT_LEVEL,
        maximum=DUEL_ARENA_MAX_COMBAT_LEVEL,
    )
    return {
        "opponent_id": f"duel-arena-{duel_number}-{level}",
        "display_name": f"Simulated duellist (level {level})",
        "combat_level": level,
    }


def _sanitize_session(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    opponent = raw.get("opponent")
    if not isinstance(opponent, Mapping):
        return {}
    opponent_id = str(opponent.get("opponent_id", ""))[:100]
    if not opponent_id:
        return {}
    rules = _normalized_rule_ids(raw.get("rule_ids"))
    if _rules_failure(rules):
        return {}
    return {
        "version": DUEL_ARENA_STATE_VERSION,
        "duel_number": _int(raw.get("duel_number"), 1, minimum=1),
        "review": _int(raw.get("review"), maximum=DUEL_ARENA_MAX_REVIEWS),
        "rule_ids": rules,
        "opponent": {
            "opponent_id": opponent_id,
            "display_name": str(
                opponent.get("display_name", "Simulated duellist")
            )[:120],
            "combat_level": _int(
                opponent.get("combat_level"),
                DUEL_ARENA_MIN_COMBAT_LEVEL,
                minimum=DUEL_ARENA_MIN_COMBAT_LEVEL,
                maximum=DUEL_ARENA_MAX_COMBAT_LEVEL,
            ),
        },
        "player_points": _int(
            raw.get("player_points"), maximum=DUEL_ARENA_POINTS_TO_WIN
        ),
        "opponent_points": _int(
            raw.get("opponent_points"), maximum=DUEL_ARENA_POINTS_TO_WIN
        ),
        "previous_combat_target": str(
            raw.get("previous_combat_target", "")
        )[:120],
    }


def sanitize_duel_arena_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_duel_arena_state_pure()
    session = _sanitize_session(source.get("duel_arena"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if session and active_id not in {"", DUEL_ARENA_ACTIVITY_ID}:
        session = {}
    rule_ids = _normalized_rule_ids(source.get("duel_arena_rule_ids"))
    if _rules_failure(rule_ids):
        rule_ids = ()
    return {
        **defaults,
        "duel_arena": session,
        "duel_arena_rule_ids": rule_ids,
        "duel_arena_matches": _int(source.get("duel_arena_matches")),
        "duel_arena_wins": _int(source.get("duel_arena_wins")),
        "duel_arena_losses": _int(source.get("duel_arena_losses")),
        "duel_arena_abandons": _int(source.get("duel_arena_abandons")),
        "duel_arena_last_result": str(
            source.get("duel_arena_last_result", "")
        )[:500],
    }


def _restore_stats(data: dict[str, Any]) -> None:
    # "The ending restores stats, health, run energy, poison, and other stat
    # effects", so every bar goes back to its own engine maximum rather than to a
    # figure of this family's own: Prayer points are `prayer_level * 10` as
    # everywhere else in the engine, and 100 is both
    # `COMBAT_SPECIAL_ATTACK_MAX_ENERGY` and the ceiling the Agility run-energy
    # credit is clamped to.
    data["combat_lifepoints"] = combat_max_lifepoints_pure(data)
    data["combat_prayer_points"] = max(
        1, _int(data.get("prayer_level"), 1, minimum=1)
    ) * 10
    data["combat_special_attack_energy"] = 100
    data["combat_current_levels"] = {}
    data["combat_status_effects"] = {}
    data["agility_run_energy_credit_pct"] = 100


def _finish(
    data: dict[str, Any],
    session: Mapping[str, Any],
    message: str,
) -> None:
    data["duel_arena"] = {}
    data["activity_session"] = _empty_activity_session()
    data["combat_encounter"] = {}
    data["current_combat_target"] = str(
        session.get("previous_combat_target", "")
    )
    data["duel_arena_last_result"] = message
    _restore_stats(data)


def set_duel_arena_rules_pure(
    player_data: Mapping[str, Any],
    rule_ids: Any,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_duel_arena_state_pure(data)
    if state["duel_arena"]:
        return data, False, {"reason": "Finish or abandon the active duel first."}
    if not isinstance(rule_ids, (list, tuple, set, frozenset)):
        return data, False, {"reason": "Duel rules must be a collection."}
    requested = tuple(str(value) for value in rule_ids)
    unknown = tuple(value for value in requested if value not in _RULE_ID_SET)
    if unknown:
        return data, False, {"reason": f"Unknown Duel Arena rule: {unknown[0]}."}
    normalized = _normalized_rule_ids(requested)
    failure = _rules_failure(normalized)
    if failure:
        return data, False, {"reason": failure}
    data.update(state)
    data["duel_arena_rule_ids"] = normalized
    return data, True, {
        "message": f"Saved {len(normalized)} Duel Arena rules.",
        "rule_ids": normalized,
    }


def enter_duel_arena_pure(
    player_data: Mapping[str, Any],
    rule_ids: Any = None,
    *,
    opponent_level: int | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_duel_arena_state_pure(data)
    if state["duel_arena"]:
        return data, False, {"reason": "A Duel Arena challenge is already active."}
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != DUEL_ARENA_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    encounter = data.get("combat_encounter")
    if isinstance(encounter, Mapping) and encounter:
        return data, False, {"reason": "Finish or leave the current Combat encounter first."}
    selected = (
        state["duel_arena_rule_ids"]
        if rule_ids is None
        else _normalized_rule_ids(rule_ids)
    )
    if rule_ids is not None:
        if not isinstance(rule_ids, (list, tuple, set, frozenset)):
            return data, False, {"reason": "Duel rules must be a collection."}
        unknown = [str(value) for value in rule_ids if str(value) not in _RULE_ID_SET]
        if unknown:
            return data, False, {"reason": f"Unknown Duel Arena rule: {unknown[0]}."}
    failure = _rules_failure(selected)
    if failure:
        return data, False, {"reason": failure}
    duel_number = state["duel_arena_matches"] + 1
    opponent = _opponent_for(data, duel_number, opponent_level)
    session = {
        "version": DUEL_ARENA_STATE_VERSION,
        "duel_number": duel_number,
        "review": 0,
        "rule_ids": selected,
        "opponent": opponent,
        "player_points": 0,
        "opponent_points": 0,
        "previous_combat_target": str(
            data.get("current_combat_target", "")
        )[:120],
    }
    data.update(state)
    data["duel_arena_rule_ids"] = selected
    data["duel_arena_matches"] = duel_number
    data["duel_arena"] = session
    data["activity_session"] = {"active_id": DUEL_ARENA_ACTIVITY_ID}
    data["current_utility"] = DUEL_ARENA_ACTIVITY_ID
    data["combat_encounter"] = {}
    _restore_stats(data)
    data["duel_arena_last_result"] = (
        f"Free challenge accepted against {opponent['display_name']}."
    )
    return data, True, {
        "message": data["duel_arena_last_result"],
        "opponent": dict(opponent),
        "rule_ids": selected,
    }


def _player_exchange_chance(
    player_data: Mapping[str, Any],
    opponent_level: int,
) -> float:
    # AnkiScape abstraction, declared in the family's audit: a period duel was
    # two real players fighting, so nothing here converts a recovered value. This
    # turns the combat-level gap into one review's chance of taking an exchange.
    # The divisor sets how fast the gap tells: 0.25 / (1 / 270) is a gap of about
    # 67 combat levels, roughly half the level range, so only a badly mismatched
    # pairing reaches the bound and duels between nearby levels stay near even.
    player_level = player_combat_level_pure(player_data)
    return max(0.25, min(0.75, 0.5 + (player_level - opponent_level) / 270.0))


def apply_duel_arena_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_duel_arena_state_pure(data)
    session = state["duel_arena"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not session or active_id != DUEL_ARENA_ACTIVITY_ID:
        return data, False, {"reason": "Enter a Duel Arena challenge before training it."}
    if not productive:
        return data, True, {
            "advanced": False,
            "terminal": False,
            "message": "The duel advances only on an eligible successful review.",
        }
    data.update(state)
    chance = _player_exchange_chance(
        data, int(session["opponent"]["combat_level"])
    )
    draw = max(0.0, min(1.0, float((rng or (lambda: 0.5))())))
    if draw < chance:
        session["player_points"] += 1
        exchange_winner = "player"
    else:
        session["opponent_points"] += 1
        exchange_winner = "opponent"
    session["review"] += 1
    maximum = combat_max_lifepoints_pure(data)
    data["combat_lifepoints"] = max(
        1,
        maximum
        - (
            maximum
            * int(session["opponent_points"])
            // DUEL_ARENA_POINTS_TO_WIN
        ),
    )
    terminal = (
        session["player_points"] >= DUEL_ARENA_POINTS_TO_WIN
        or session["opponent_points"] >= DUEL_ARENA_POINTS_TO_WIN
        or session["review"] >= DUEL_ARENA_MAX_REVIEWS
    )
    if terminal:
        won = session["player_points"] > session["opponent_points"]
        before_tier = duellists_cap_tier_pure(state["duel_arena_wins"])
        if won:
            data["duel_arena_wins"] = state["duel_arena_wins"] + 1
            after_tier = duellists_cap_tier_pure(data["duel_arena_wins"])
            message = (
                f"Duel won {session['player_points']}-{session['opponent_points']} "
                f"against {session['opponent']['display_name']}."
            )
            if after_tier["tier"] > before_tier["tier"]:
                message += f" Duellist's cap reached tier {after_tier['tier']}."
                if _set_owned_cap_tier(data, after_tier["item_name"]):
                    message += " Your owned cap changed to the new tier."
            outcome = "win"
        else:
            data["duel_arena_losses"] = state["duel_arena_losses"] + 1
            after_tier = before_tier
            message = (
                f"Safe duel defeat {session['player_points']}-{session['opponent_points']} "
                f"against {session['opponent']['display_name']}."
            )
            outcome = "loss"
        _finish(data, session, message)
        return data, True, {
            "advanced": True,
            "terminal": True,
            "outcome": outcome,
            "exchange_winner": exchange_winner,
            "player_points": session["player_points"],
            "opponent_points": session["opponent_points"],
            "cap": after_tier,
            "message": message,
        }
    data["duel_arena"] = session
    data["duel_arena_last_result"] = (
        f"Duel in progress · {session['player_points']}-"
        f"{session['opponent_points']} after {session['review']} reviews."
    )
    return data, True, {
        "advanced": True,
        "terminal": False,
        "exchange_winner": exchange_winner,
        "player_points": session["player_points"],
        "opponent_points": session["opponent_points"],
        "chance": chance,
        "message": data["duel_arena_last_result"],
    }


def abandon_duel_arena_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = dict(player_data)
    state = sanitize_duel_arena_state_pure(data)
    session = state["duel_arena"]
    if not session:
        return data, False, {"reason": "No Duel Arena challenge is active."}
    if "no_forfeit" in session["rule_ids"]:
        return data, False, {
            "reason": "No Forfeit is enabled; finish the bounded duel through reviews."
        }
    data.update(state)
    data["duel_arena_abandons"] += 1
    message = (
        f"Safely abandoned the duel at {session['player_points']}-"
        f"{session['opponent_points']}."
    )
    _finish(data, session, message)
    return data, True, {"message": message, "outcome": "abandon"}


def apply_duel_arena_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "set_rules":
        return set_duel_arena_rules_pure(player_data, body.get("rule_ids", ()))
    if action_id == "enter":
        return enter_duel_arena_pure(
            player_data,
            body.get("rule_ids"),
        )
    if action_id == "claim_cap":
        return claim_duellists_cap_pure(player_data)
    if action_id == "abandon":
        return abandon_duel_arena_pure(player_data)
    return dict(player_data), False, {"reason": "Unknown Duel Arena command."}


def duel_arena_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_duel_arena_state_pure(player_data)
    session = state["duel_arena"]
    active = player_data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    encounter = player_data.get("combat_encounter")
    reasons = []
    if active_id and active_id != DUEL_ARENA_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity.")
    if not session and isinstance(encounter, Mapping) and encounter:
        reasons.append("Finish or leave the current Combat encounter.")
    selected = (
        tuple(session["rule_ids"])
        if session
        else tuple(state["duel_arena_rule_ids"])
    )
    cap = duellists_cap_tier_pure(state["duel_arena_wins"])
    owned_cap_item, owned_cap_location = _owned_cap_item(player_data)
    return {
        **state,
        "active": bool(session),
        "can_forfeit": bool(session) and "no_forfeit" not in selected,
        "can_enter": not reasons and not session,
        "entry_reasons": tuple(reasons),
        "selected_rule_ids": selected,
        "selected_rules": tuple(
            DUEL_ARENA_RULES_BY_ID[rule_id].display_name for rule_id in selected
        ),
        "cap": cap,
        "owned_cap_item": owned_cap_item,
        "owned_cap_location": owned_cap_location,
        "can_claim_cap": not session and owned_cap_item != cap["item_name"],
        "points_to_win": DUEL_ARENA_POINTS_TO_WIN,
        "maximum_reviews": DUEL_ARENA_MAX_REVIEWS,
        "source": DUEL_ARENA_SOURCE,
    }
