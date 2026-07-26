"""Pure Fish Flingers entry, six-review event, currency, and shop mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.fish_flingers_data import (
    FISH_FLINGERS_ACTIVITY_ID,
    FISH_FLINGERS_COMMUNAL_DEPLETION,
    FISH_FLINGERS_DISCOVERY_LABELS,
    FISH_FLINGERS_EFFICIENCY,
    FISH_FLINGERS_EVENT_REVIEWS,
    FISH_FLINGERS_LOCATIONS,
    FISH_FLINGERS_REWARDS,
    FISH_FLINGERS_ROTATION_ROUTE,
    FISH_FLINGERS_SPECIES,
    FISH_FLINGERS_STOCK_MAX,
    FISH_FLINGERS_TICKET_CAP,
    FISH_FLINGERS_TICKETS_PER_DAY,
    FISH_FLINGERS_TOKEN_CAP,
    FISH_FLINGERS_WORLD_DAY_REVIEWS,
)


FISH_FLINGERS_STATE_VERSION = 2


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _signed_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return int(default)


def _roll(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        parsed = 0.5
    return max(0.0, min(parsed, 0.999999))


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    return _int(clock.get("answered_cards"))


def default_fish_flingers_state_pure() -> dict[str, Any]:
    return {
        "fish_flingers": {},
        "fish_flingers_tickets": 0,
        "fish_flingers_tokens": 0,
        "fish_flingers_medals": 0,
        "fish_flingers_events_completed": 0,
        "fish_flingers_last_ticket_day": -1,
        "fish_flingers_last_result": "",
    }


def sanitize_fish_flingers_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    review = _int(raw.get("review"), maximum=FISH_FLINGERS_EVENT_REVIEWS - 1)
    if "rotation_index" in raw:
        rotation_index = _int(
            raw.get("rotation_index"),
            maximum=len(FISH_FLINGERS_ROTATION_ROUTE) - 1,
        )
    else:
        legacy_location = _int(
            raw.get("location_index"),
            maximum=len(FISH_FLINGERS_LOCATIONS) - 1,
        )
        rotation_index = next(
            (
                index
                for index, (_species_index, location_index) in enumerate(
                    FISH_FLINGERS_ROTATION_ROUTE
                )
                if location_index == legacy_location
            ),
            0,
        )
    default_species, default_location = FISH_FLINGERS_ROTATION_ROUTE[rotation_index]
    return {
        "version": FISH_FLINGERS_STATE_VERSION,
        "review": review,
        "fish_caught": _int(raw.get("fish_caught"), maximum=999),
        "total_weight": _int(raw.get("total_weight"), maximum=99_999),
        "big_fish": _int(raw.get("big_fish"), maximum=3),
        "assists": _int(raw.get("assists"), maximum=6),
        "perfect_tackles": max(0, review - 2),
        "rotation_index": rotation_index,
        "species_index": _int(
            raw.get("species_index"),
            default_species,
            maximum=len(FISH_FLINGERS_SPECIES) - 1,
        ),
        "location_index": _int(
            raw.get("location_index"),
            default_location,
            maximum=len(FISH_FLINGERS_LOCATIONS) - 1,
        ),
        "stock": max(
            1,
            _int(
                raw.get("stock"),
                FISH_FLINGERS_STOCK_MAX,
                maximum=FISH_FLINGERS_STOCK_MAX,
            ),
        ),
    }


def sanitize_fish_flingers_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = dict(player_data or {})
    defaults = default_fish_flingers_state_pure()
    session = sanitize_fish_flingers_session_pure(source.get("fish_flingers"))
    active = source.get("activity_session")
    active_id = (
        str(active.get("active_id", ""))
        if isinstance(active, Mapping)
        else ""
    )
    if session and active_id not in {"", FISH_FLINGERS_ACTIVITY_ID}:
        session = {}
    return {
        "fish_flingers": session,
        "fish_flingers_tickets": _int(
            source.get("fish_flingers_tickets"), maximum=FISH_FLINGERS_TICKET_CAP
        ),
        "fish_flingers_tokens": _int(
            source.get("fish_flingers_tokens"), maximum=FISH_FLINGERS_TOKEN_CAP
        ),
        "fish_flingers_medals": _int(source.get("fish_flingers_medals")),
        "fish_flingers_events_completed": _int(
            source.get("fish_flingers_events_completed")
        ),
        "fish_flingers_last_ticket_day": _signed_int(
            source.get("fish_flingers_last_ticket_day"), -1
        ),
        "fish_flingers_last_result": str(
            source.get(
                "fish_flingers_last_result",
                defaults["fish_flingers_last_result"],
            )
            or defaults["fish_flingers_last_result"]
        )[:320],
    }


def sync_fish_flingers_tickets_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    # Shallow on purpose: sanitize_fish_flingers_state_pure rebuilds every key
    # this writes, and the ticket counters are plain ints.
    data = dict(player_data)
    data.update(sanitize_fish_flingers_state_pure(data))
    current_day = _answered_cards(data) // FISH_FLINGERS_WORLD_DAY_REVIEWS
    previous_day = _signed_int(data.get("fish_flingers_last_ticket_day"), -1)
    if previous_day < 0:
        grants = FISH_FLINGERS_TICKETS_PER_DAY
    elif current_day > previous_day:
        grants = (current_day - previous_day) * FISH_FLINGERS_TICKETS_PER_DAY
    else:
        grants = 0
    if grants:
        data["fish_flingers_tickets"] = min(
            FISH_FLINGERS_TICKET_CAP,
            _int(data.get("fish_flingers_tickets")) + grants,
        )
    if previous_day < 0 or current_day > previous_day:
        data["fish_flingers_last_ticket_day"] = current_day
    return data


def _finish_event(data: dict[str, Any]) -> None:
    data["fish_flingers"] = {}
    active = data.get("activity_session")
    if (
        isinstance(active, Mapping)
        and str(active.get("active_id", "")) == FISH_FLINGERS_ACTIVITY_ID
    ):
        data["activity_session"] = {"active_id": ""}


def enter_fish_flingers_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = sync_fish_flingers_tickets_pure(player_data)
    if data["fish_flingers"]:
        return data, False, {"reason": "A Fish Flingers event is already active."}
    active = data.get("activity_session")
    active_id = (
        str(active.get("active_id", ""))
        if isinstance(active, Mapping)
        else ""
    )
    if active_id and active_id != FISH_FLINGERS_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    tickets = _int(data.get("fish_flingers_tickets"))
    if tickets < 1:
        return data, False, {"reason": "No Fish Flingers entry tickets are available."}
    data["fish_flingers_tickets"] = tickets - 1
    rotation_index = (
        _int(data.get("fish_flingers_events_completed")) * 2
    ) % len(FISH_FLINGERS_ROTATION_ROUTE)
    species_index, location_index = FISH_FLINGERS_ROTATION_ROUTE[rotation_index]
    data["fish_flingers"] = {
        "version": FISH_FLINGERS_STATE_VERSION,
        "review": 0,
        "fish_caught": 0,
        "total_weight": 0,
        "big_fish": 0,
        "assists": 0,
        "perfect_tackles": 0,
        "rotation_index": rotation_index,
        "species_index": species_index,
        "location_index": location_index,
        "stock": FISH_FLINGERS_STOCK_MAX,
    }
    data["activity_session"] = {"active_id": FISH_FLINGERS_ACTIVITY_ID}
    data["current_utility"] = FISH_FLINGERS_ACTIVITY_ID
    data["fish_flingers_last_result"] = (
        "Entered Fish Flingers · bait discovery ready"
    )
    return data, True, {"message": data["fish_flingers_last_result"]}


def _event_xp(fishing_level: Any, fish_caught: int) -> float:
    level = max(1, min(_int(fishing_level, 1), 99))
    # The cutoff page says XP is score/level scaled and roughly 20,000 at the
    # high end, but marks its own table obsolete. This disclosed balance curve
    # reaches 19,800 at level 99 only for a 48-fish maximum event.
    return float(round(level * 200 * min(1.0, fish_caught / 48.0)))


def _stock_label(stock: int) -> str:
    percent = stock * 100 / FISH_FLINGERS_STOCK_MAX
    if percent >= 67:
        return "Rich"
    if percent >= 34:
        return "Fading"
    return "Low"


def apply_fish_flingers_review_pure(
    player_data: Mapping[str, Any],
    catch_roll: Any,
    big_fish_roll: Any,
    assist_roll: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data = sync_fish_flingers_tickets_pure(player_data)
    session = sanitize_fish_flingers_session_pure(data.get("fish_flingers"))
    if not session:
        return data, {"allowed": False, "reason": "Enter Fish Flingers before training."}

    review = int(session["review"])
    efficiency = float(FISH_FLINGERS_EFFICIENCY[review])
    species_index = int(session["species_index"])
    location_index = int(session["location_index"])
    rotation_index = int(session["rotation_index"])
    stock_before = int(session["stock"])
    species = FISH_FLINGERS_SPECIES[species_index]
    location = FISH_FLINGERS_LOCATIONS[location_index]
    # The source establishes the direction of stock pressure, not its hidden
    # rates. These stock bands and the weight span are disclosed AnkiScape
    # balance math backed by the data-module constants.
    stock_percent = stock_before * 100 / FISH_FLINGERS_STOCK_MAX
    stock_penalty = 0 if stock_percent >= 67 else 1 if stock_percent >= 34 else 2
    communal_pressure = FISH_FLINGERS_COMMUNAL_DEPLETION
    raw_catch = 4 + int(_roll(catch_roll) * 5)
    adjusted_catch = (
        raw_catch
        + int(species["catch_modifier"])
        + int(location["catch_modifier"])
        - stock_penalty
    )
    caught = max(1, min(stock_before, round(adjusted_catch * efficiency)))
    weight_each = max(
        1,
        70
        + int(_roll(catch_roll) * 61)
        + int(species["weight_modifier"])
        + int(location["weight_modifier"]),
    )
    weight = caught * weight_each
    big_fish = int(session["big_fish"])
    caught_big = big_fish < 3 and _roll(big_fish_roll) < 0.25
    if caught_big:
        big_fish += 1
    assists = int(session["assists"])
    assisted = assists < 6 and _roll(assist_roll) < 0.50
    if assisted:
        assists += 1

    next_review = review + 1
    fish_total = int(session["fish_caught"]) + caught
    weight_total = int(session["total_weight"]) + weight
    # The third catch completes the automatic discovery ramp, so only that
    # catch and the three that follow count as source-shaped perfect tackles.
    perfect_tackles = max(0, next_review - 2)
    remaining_stock = max(0, stock_before - caught - communal_pressure)
    terminal = next_review >= FISH_FLINGERS_EVENT_REVIEWS
    rotated = remaining_stock == 0 and not terminal
    if rotated:
        rotation_index = (rotation_index + 1) % len(FISH_FLINGERS_ROTATION_ROUTE)
        species_index, location_index = FISH_FLINGERS_ROTATION_ROUTE[rotation_index]
        remaining_stock = FISH_FLINGERS_STOCK_MAX
    xp = 0.0
    tokens = 0
    medals = 0
    medal_labels: list[str] = []
    if terminal:
        tokens = (
            fish_total // 4
            + min(3, big_fish)
            + min(3, assists // 2)
            + min(3, perfect_tackles // 2)
        )
        if perfect_tackles >= 3:
            medals += 1
            medal_labels.append("Junior Angler")
        if perfect_tackles >= 6:
            medals += 1
            medal_labels.append("Master Angler")
        if big_fish >= 3:
            medals += 1
            medal_labels.append("Whopper")
        if assists >= 6:
            medals += 1
            medal_labels.append("Team Player")
        xp = _event_xp(data.get("fishing_level"), fish_total)
        data["fish_flingers_tokens"] = min(
            FISH_FLINGERS_TOKEN_CAP,
            _int(data.get("fish_flingers_tokens")) + tokens,
        )
        data["fish_flingers_medals"] = _int(
            data.get("fish_flingers_medals")
        ) + medals
        data["fish_flingers_events_completed"] = _int(
            data.get("fish_flingers_events_completed")
        ) + 1
        _finish_event(data)
    else:
        data["fish_flingers"] = {
            "version": FISH_FLINGERS_STATE_VERSION,
            "review": next_review,
            "fish_caught": fish_total,
            "total_weight": weight_total,
            "big_fish": big_fish,
            "assists": assists,
            "perfect_tackles": perfect_tackles,
            "rotation_index": rotation_index,
            "species_index": species_index,
            "location_index": location_index,
            "stock": remaining_stock,
        }

    extras = []
    if caught_big:
        extras.append("big fish landed")
    if assisted:
        extras.append("public catch assisted")
    if rotated:
        next_species = FISH_FLINGERS_SPECIES[species_index]["name"]
        next_location = FISH_FLINGERS_LOCATIONS[location_index]["name"]
        extras.append(f"stock rotated to {next_species} at {next_location}")
    if terminal:
        extras.extend((f"{tokens} tokens", f"{medals} medals", f"{xp:g} Fishing XP"))
    suffix = " · " + " · ".join(extras) if extras else ""
    data["fish_flingers_last_result"] = (
        f"Fish Flingers · {species['name']} at {location['name']} · "
        f"{FISH_FLINGERS_DISCOVERY_LABELS[review]} · "
        f"{caught} fish at {efficiency * 100:g}% efficiency · "
        f"{weight_total} total weight · "
        f"stock {remaining_stock}/{FISH_FLINGERS_STOCK_MAX} · "
        f"{next_review}/6 catches{suffix}"
    )
    return data, {
        "allowed": True,
        "action_id": FISH_FLINGERS_ACTIVITY_ID,
        "success": True,
        "expected_success_chance": 1.0,
        "fish_caught": caught,
        "fish_total": fish_total,
        "catch_weight": weight,
        "total_weight": weight_total,
        "species": str(species["name"]),
        "location": str(location["name"]),
        "stock_before": stock_before,
        "stock_after": remaining_stock,
        "stock_label": _stock_label(remaining_stock),
        "rotation_index": rotation_index,
        "rotated": rotated,
        "communal_pressure": communal_pressure,
        "big_fish": big_fish,
        "assists": assists,
        "perfect_tackles": perfect_tackles,
        "efficiency": efficiency,
        "xp": xp,
        "tokens": tokens,
        "medals": medals,
        "medal_labels": tuple(medal_labels),
        "terminal": terminal,
        "completed_activity": terminal,
        "status": data["fish_flingers_last_result"],
    }


def leave_fish_flingers_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = sync_fish_flingers_tickets_pure(player_data)
    session = sanitize_fish_flingers_session_pure(data.get("fish_flingers"))
    if not session:
        return data, False, {"reason": "No Fish Flingers event is active."}
    progress = int(session["review"])
    _finish_event(data)
    data["fish_flingers_last_result"] = (
        f"Left Fish Flingers after {progress}/6 catches · entry ticket forfeited"
    )
    return data, True, {"message": data["fish_flingers_last_result"]}


def buy_fish_flingers_reward_pure(
    player_data: Mapping[str, Any],
    reward_id: Any,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = sync_fish_flingers_tickets_pure(player_data)
    reward = FISH_FLINGERS_REWARDS.get(str(reward_id))
    if reward is None:
        return data, False, {"reason": "Unknown Fish Flingers reward."}
    tokens = _int(data.get("fish_flingers_tokens"))
    medals = _int(data.get("fish_flingers_medals"))
    token_cost = int(reward["tokens"])
    medal_requirement = int(reward["medals"])
    if tokens < token_cost:
        return data, False, {"reason": f"Requires {token_cost} Fishing tokens."}
    if medals < medal_requirement:
        return data, False, {"reason": f"Requires {medal_requirement} cumulative medals."}
    inventory = dict(data.get("inventory") or {})
    previous = str(reward.get("previous", ""))
    if previous and _int(inventory.get(previous)) < 1:
        return data, False, {"reason": f"Requires {previous} to upgrade."}
    item = str(reward["item"])
    data["fish_flingers_tokens"] = tokens - token_cost
    if previous:
        remaining = _int(inventory.get(previous)) - 1
        if remaining:
            inventory[previous] = remaining
        else:
            inventory.pop(previous, None)
    inventory[item] = _int(inventory.get(item)) + 1
    data["inventory"] = inventory
    data["fish_flingers_last_result"] = (
        f"Fish Flingers reward · {item} · {token_cost} tokens"
    )
    return data, True, {
        "message": data["fish_flingers_last_result"],
        "item": item,
        "tokens_spent": token_cost,
    }


def apply_fish_flingers_command_pure(
    player_data: Mapping[str, Any],
    action_id: Any,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    action = str(action_id)
    if action == "enter_fish_flingers":
        return enter_fish_flingers_pure(player_data)
    if action == "leave_fish_flingers":
        return leave_fish_flingers_pure(player_data)
    if action == "buy_fish_flingers_reward":
        return buy_fish_flingers_reward_pure(
            player_data, dict(payload or {}).get("reward_id")
        )
    data = sync_fish_flingers_tickets_pure(player_data)
    return data, False, {"reason": "Unknown Fish Flingers action."}


def fishing_outfit_multiplier_pure(player_data: Mapping[str, Any]) -> float:
    equipment = player_data.get("equipment")
    worn = set(equipment.values()) if isinstance(equipment, Mapping) else set()
    pieces = {
        "Fishing hat",
        "Fishing jacket",
        "Fishing waders",
        "Fishing boots",
    }
    count = len(pieces.intersection(worn))
    return 1.0 + 0.01 * count + (0.01 if count == len(pieces) else 0.0)


def fish_flingers_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    data = sync_fish_flingers_tickets_pure(player_data)
    state = sanitize_fish_flingers_state_pure(data)
    session = state["fish_flingers"]
    review = int(session.get("review", 0))
    stock = int(session.get("stock", 0))
    rotation_index = int(session.get("rotation_index", 0))
    species_index = int(session.get("species_index", 0))
    location_index = int(session.get("location_index", 0))
    inventory = data.get("inventory")
    bank = inventory if isinstance(inventory, Mapping) else {}
    return {
        "active": bool(session),
        "can_review": bool(session),
        "review": review,
        "review_number": review + 1 if session else 0,
        "fish_caught": int(session.get("fish_caught", 0)),
        "total_weight": int(session.get("total_weight", 0)),
        "big_fish": int(session.get("big_fish", 0)),
        "assists": int(session.get("assists", 0)),
        "perfect_tackles": int(session.get("perfect_tackles", 0)),
        "species": (
            str(FISH_FLINGERS_SPECIES[species_index]["name"]) if session else ""
        ),
        "location": (
            str(FISH_FLINGERS_LOCATIONS[location_index]["name"]) if session else ""
        ),
        "stock": stock,
        "stock_max": FISH_FLINGERS_STOCK_MAX,
        "stock_percent": (
            stock * 100 // FISH_FLINGERS_STOCK_MAX if session else 0
        ),
        "stock_label": _stock_label(stock) if session else "No event",
        "rotation_index": rotation_index,
        "rotation": (
            f"{rotation_index + 1}/{len(FISH_FLINGERS_ROTATION_ROUTE)}"
            if session
            else "—"
        ),
        "communal_pressure": FISH_FLINGERS_COMMUNAL_DEPLETION,
        "communal_pressure_label": (
            f"{FISH_FLINGERS_COMMUNAL_DEPLETION} stock per review"
        ),
        "efficiency": float(FISH_FLINGERS_EFFICIENCY[review]) if session else 0.5,
        "next_discovery": str(FISH_FLINGERS_DISCOVERY_LABELS[review]) if session else "Best bait",
        "tickets": state["fish_flingers_tickets"],
        "tokens": state["fish_flingers_tokens"],
        "medals": state["fish_flingers_medals"],
        "events_completed": state["fish_flingers_events_completed"],
        "last_result": state["fish_flingers_last_result"],
        "rewards": tuple(
            {
                "id": reward_id,
                **spec,
                "affordable": (
                    state["fish_flingers_tokens"] >= int(spec["tokens"])
                    and state["fish_flingers_medals"] >= int(spec["medals"])
                    and (
                        not spec.get("previous")
                        or _int(bank.get(str(spec["previous"]))) > 0
                    )
                ),
            }
            for reward_id, spec in FISH_FLINGERS_REWARDS.items()
        ),
    }
