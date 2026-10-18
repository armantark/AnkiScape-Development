"""Pure Fish Flingers entry, ten-minute eight-catch event, currency, and shop mechanics."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from math import floor
from typing import Any

from ..data.fish_flingers_data import (
    FISH_FLINGERS_ACTIVITY_ID,
    FISH_FLINGERS_CATCH_TICKS,
    FISH_FLINGERS_COMMUNAL_DEPLETION,
    FISH_FLINGERS_DISCOVERY_LABELS,
    FISH_FLINGERS_EFFICIENCY,
    FISH_FLINGERS_EVENT_CATCHES,
    FISH_FLINGERS_EVENT_TICKS,
    FISH_FLINGERS_LOCATIONS,
    FISH_FLINGERS_REWARDS,
    FISH_FLINGERS_ROTATION_ROUTE,
    FISH_FLINGERS_SPECIES,
    FISH_FLINGERS_STOCK_MAX,
    FISH_FLINGERS_TICKET_CAP,
    FISH_FLINGERS_TICKETS_PER_DAY,
    FISH_FLINGERS_TOKEN_CAP,
)
from .pace.short_timers import STEP_TICKS
from .pace.world_clock import world_day_index_pure


FISH_FLINGERS_STATE_VERSION = 3


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


def _catches_landed(session: Mapping[str, Any]) -> int:
    return int(session["ticks_elapsed"]) // FISH_FLINGERS_CATCH_TICKS


def default_fish_flingers_state_pure() -> dict[str, Any]:
    return {
        "fish_flingers": {},
        "fish_flingers_tickets": 0,
        "fish_flingers_tokens": 0,
        "fish_flingers_medals": 0,
        "fish_flingers_events_completed": 0,
        "fish_flingers_last_ticket_day": -1,
        "fish_flingers_last_result": "",
        "fish_flingers_game_log": [],
    }


def sanitize_fish_flingers_session_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    if "ticks_elapsed" in raw:
        ticks_elapsed = _int(
            raw.get("ticks_elapsed"), maximum=FISH_FLINGERS_EVENT_TICKS - 1
        )
    else:
        # Version 2 counted landed catches, one per step. Each keeps its place on
        # the ten-minute line, so no catch is lost or played twice.
        ticks_elapsed = FISH_FLINGERS_CATCH_TICKS * _int(
            raw.get("review"), maximum=FISH_FLINGERS_EVENT_CATCHES - 1
        )
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
        "ticks_elapsed": ticks_elapsed,
        "fish_caught": _int(raw.get("fish_caught"), maximum=999),
        "big_fish": _int(raw.get("big_fish"), maximum=3),
        "assists": _int(raw.get("assists"), maximum=6),
        "perfect_tackles": max(0, ticks_elapsed // FISH_FLINGERS_CATCH_TICKS - 2),
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


FISH_FLINGERS_GAME_LOG_RETAINED = 50


def sanitize_fish_flingers_game_log_pure(value: Any) -> list[dict[str, Any]]:
    """Normalize the settled-game ledger, oldest first, newest 50 kept."""

    if not isinstance(value, (list, tuple)):
        return []
    rows: list[dict[str, Any]] = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        rows.append(
            {
                "score": _int(raw.get("score"), maximum=48),
                "xp": _int(raw.get("xp")),
                "fishing_level": _int(raw.get("fishing_level"), maximum=99),
                "review_index": _int(raw.get("review_index")),
                "medals": _int(raw.get("medals"), maximum=4),
            }
        )
    return rows[-FISH_FLINGERS_GAME_LOG_RETAINED:]


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
        "fish_flingers_game_log": sanitize_fish_flingers_game_log_pure(
            source.get("fish_flingers_game_log")
        ),
    }


def sync_fish_flingers_tickets_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    # Shallow on purpose: sanitize_fish_flingers_state_pure rebuilds every key
    # this writes, and the ticket counters are plain ints.
    data = dict(player_data)
    data.update(sanitize_fish_flingers_state_pure(data))
    current_day = world_day_index_pure(data)
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
        "ticks_elapsed": 0,
        "fish_caught": 0,
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


def fish_flingers_score_pure(session: Mapping[str, Any]) -> int:
    """Translate the bounded session statistics to Darkan's 48-point score."""
    fish_caught = _int(session.get("fish_caught"))
    big_fish = _int(session.get("big_fish"), maximum=3)
    assists = _int(session.get("assists"), maximum=6)
    perfect_tackles = _int(session.get("perfect_tackles"), maximum=6)

    # Darkan commit bf9c0f0894e05a592826c6e3e622d1b9538c4e88,
    # FishFlingersDomain.kt:98-114: score combines catch bands, large fish,
    # assists, total/heaviest weight, and the perfect-tackle table. The local
    # eight-catch session does not retain weights, so one tracked catch is the
    # closest proxy for 500 kg and one tracked large fish for 60 kg.
    catch_points = (
        5
        if fish_caught >= 130
        else 4
        if fish_caught >= 110
        else 3
        if fish_caught >= 90
        else 2
        if fish_caught >= 80
        else 1
        if fish_caught >= 70
        else 0
    )
    # Eight local catches cannot exceed 47 fish, so the session never reaches
    # Darkan's 70-catch band, which counts every cast of the live event.
    perfect_points = (0, 1, 2, 4, 5, 6, 8)[perfect_tackles]
    return (
        catch_points
        + big_fish * 2
        + assists
        + min(20, fish_caught)
        + min(3, big_fish)
        + perfect_points
    )


def fish_flingers_xp_payout_pure(fishing_level: Any, score: Any) -> int:
    # PLACEHOLDER(fish_flingers.xp_payout): period settlement source or a
    # qualified cutoff-era payout table would retire the Darkan reconstruction.
    # Darkan commit bf9c0f0894e05a592826c6e3e622d1b9538c4e88,
    # FishFlingersDomain.kt:130-134: the event pays this once at settlement.
    level = max(1, min(_int(fishing_level, 1), 99))
    bounded_score = max(0, min(_int(score), 48))
    maximum = max(162, 235 * level - 73)
    return floor(maximum * bounded_score / 48)


def _stock_label(stock: int) -> str:
    percent = stock * 100 / FISH_FLINGERS_STOCK_MAX
    if percent >= 67:
        return "Rich"
    if percent >= 34:
        return "Fading"
    return "Low"


def apply_fish_flingers_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Play one six-tick step of the competition.

    Catch k lands on the step whose ticks cross k x 125, and only that step
    draws its catch, big-fish and assist rolls, so the same rolls play the same
    game at every game speed.
    """
    data = sync_fish_flingers_tickets_pure(player_data)
    session = sanitize_fish_flingers_session_pure(data.get("fish_flingers"))
    if not session:
        return data, {"allowed": False, "reason": "Enter Fish Flingers before training."}
    ticks_elapsed = int(session["ticks_elapsed"]) + STEP_TICKS
    if ticks_elapsed // FISH_FLINGERS_CATCH_TICKS == _catches_landed(session):
        data["fish_flingers"] = {**session, "ticks_elapsed": ticks_elapsed}
        return data, {
            "allowed": True,
            "action_id": FISH_FLINGERS_ACTIVITY_ID,
            "catch_landed": False,
            "terminal": False,
        }
    return _land_catch(data, session, ticks_elapsed, (rng(), rng(), rng()))


def _stock_penalty(stock: int) -> int:
    return {"Rich": 0, "Fading": 1, "Low": 2}[_stock_label(stock)]


def _settle_event(
    data: dict[str, Any],
    fish_total: int,
    big_fish: int,
    assists: int,
    perfect_tackles: int,
) -> dict[str, Any]:
    """Pay the finished event's tokens, medals and XP, and close it."""
    tokens = (
        fish_total // 4
        + min(3, big_fish)
        + min(3, assists // 2)
        + min(3, perfect_tackles // 2)
    )
    medal_labels = tuple(
        label
        for label, earned in (
            ("Junior Angler", perfect_tackles >= 3),
            ("Master Angler", perfect_tackles >= 6),
            ("Whopper", big_fish >= 3),
            ("Team Player", assists >= 6),
        )
        if earned
    )
    medals = len(medal_labels)
    score = fish_flingers_score_pure(
        {
            "fish_caught": fish_total,
            "big_fish": big_fish,
            "assists": assists,
            "perfect_tackles": perfect_tackles,
        }
    )
    xp = fish_flingers_xp_payout_pure(data.get("fishing_level"), score)
    data["fish_flingers_tokens"] = min(
        FISH_FLINGERS_TOKEN_CAP,
        _int(data.get("fish_flingers_tokens")) + tokens,
    )
    data["fish_flingers_medals"] = _int(data.get("fish_flingers_medals")) + medals
    data["fish_flingers_events_completed"] = _int(
        data.get("fish_flingers_events_completed")
    ) + 1
    data["fish_flingers_game_log"] = (
        sanitize_fish_flingers_game_log_pure(data.get("fish_flingers_game_log"))
        + [
            {
                "score": score,
                "xp": xp,
                "fishing_level": max(1, min(_int(data.get("fishing_level"), 1), 99)),
                "review_index": FISH_FLINGERS_EVENT_CATCHES,
                "medals": medals,
            }
        ]
    )[-FISH_FLINGERS_GAME_LOG_RETAINED:]
    _finish_event(data)
    return {
        "tokens": tokens,
        "medals": medals,
        "medal_labels": medal_labels,
        "score": score,
        "xp": xp,
    }


_NO_SETTLEMENT = {"tokens": 0, "medals": 0, "medal_labels": (), "score": 0, "xp": 0.0}


def _land_catch(
    data: dict[str, Any],
    session: Mapping[str, Any],
    ticks_elapsed: int,
    rolls: tuple[float, float, float],
) -> tuple[dict[str, Any], dict[str, Any]]:
    catch_roll, big_fish_roll, assist_roll = rolls
    catch_index = _catches_landed(session)
    efficiency = float(FISH_FLINGERS_EFFICIENCY[catch_index])
    species_index = int(session["species_index"])
    location_index = int(session["location_index"])
    rotation_index = int(session["rotation_index"])
    stock_before = int(session["stock"])
    species = FISH_FLINGERS_SPECIES[species_index]
    location = FISH_FLINGERS_LOCATIONS[location_index]
    # The source establishes the direction of stock pressure, not its hidden
    # rates. These stock bands and the weight span are disclosed AnkiScape
    # balance math backed by the data-module constants.
    communal_pressure = FISH_FLINGERS_COMMUNAL_DEPLETION
    raw_catch = 4 + int(_roll(catch_roll) * 5)
    adjusted_catch = (
        raw_catch
        + int(species["catch_modifier"])
        + int(location["catch_modifier"])
        - _stock_penalty(stock_before)
    )
    caught = max(1, min(stock_before, round(adjusted_catch * efficiency)))
    big_fish = int(session["big_fish"])
    caught_big = big_fish < 3 and _roll(big_fish_roll) < 0.25
    big_fish += int(caught_big)
    assists = int(session["assists"])
    assisted = assists < 6 and _roll(assist_roll) < 0.50
    assists += int(assisted)

    catches = catch_index + 1
    fish_total = int(session["fish_caught"]) + caught
    # The third catch completes the automatic discovery ramp, so only that
    # catch and the ones that follow count as source-shaped perfect tackles.
    perfect_tackles = max(0, catches - 2)
    remaining_stock = max(0, stock_before - caught - communal_pressure)
    terminal = catches >= FISH_FLINGERS_EVENT_CATCHES
    rotated = remaining_stock == 0 and not terminal
    if rotated:
        rotation_index = (rotation_index + 1) % len(FISH_FLINGERS_ROTATION_ROUTE)
        species_index, location_index = FISH_FLINGERS_ROTATION_ROUTE[rotation_index]
        remaining_stock = FISH_FLINGERS_STOCK_MAX
    if terminal:
        settlement = _settle_event(data, fish_total, big_fish, assists, perfect_tackles)
    else:
        settlement = _NO_SETTLEMENT
        data["fish_flingers"] = {
            "version": FISH_FLINGERS_STATE_VERSION,
            "ticks_elapsed": ticks_elapsed,
            "fish_caught": fish_total,
            "big_fish": big_fish,
            "assists": assists,
            "perfect_tackles": perfect_tackles,
            "rotation_index": rotation_index,
            "species_index": species_index,
            "location_index": location_index,
            "stock": remaining_stock,
        }

    extras = [
        text
        for text, shown in (
            ("big fish landed", caught_big),
            ("public catch assisted", assisted),
            (
                f"stock rotated to {FISH_FLINGERS_SPECIES[species_index]['name']} "
                f"at {FISH_FLINGERS_LOCATIONS[location_index]['name']}",
                rotated,
            ),
        )
        if shown
    ]
    if terminal:
        extras.extend(
            (
                f"{settlement['tokens']} tokens",
                f"{settlement['medals']} medals",
                f"{settlement['xp']:g} Fishing XP",
            )
        )
    suffix = " · " + " · ".join(extras) if extras else ""
    data["fish_flingers_last_result"] = (
        f"Fish Flingers · {species['name']} at {location['name']} · "
        f"{FISH_FLINGERS_DISCOVERY_LABELS[catch_index]} · "
        f"{caught} fish at {efficiency * 100:g}% efficiency · "
        f"stock {remaining_stock}/{FISH_FLINGERS_STOCK_MAX} · "
        f"{catches}/{FISH_FLINGERS_EVENT_CATCHES} catches{suffix}"
    )
    return data, {
        "allowed": True,
        "action_id": FISH_FLINGERS_ACTIVITY_ID,
        "catch_landed": True,
        "success": True,
        "expected_success_chance": 1.0,
        "fish_caught": caught,
        "fish_total": fish_total,
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
        **settlement,
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
    progress = _catches_landed(session)
    _finish_event(data)
    data["fish_flingers_last_result"] = (
        f"Left Fish Flingers after {progress}/{FISH_FLINGERS_EVENT_CATCHES} catches · entry ticket forfeited"
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
    catches = int(session.get("ticks_elapsed", 0)) // FISH_FLINGERS_CATCH_TICKS
    stock = int(session.get("stock", 0))
    rotation_index = int(session.get("rotation_index", 0))
    species_index = int(session.get("species_index", 0))
    location_index = int(session.get("location_index", 0))
    inventory = data.get("inventory")
    bank = inventory if isinstance(inventory, Mapping) else {}
    return {
        "active": bool(session),
        "can_review": bool(session),
        "catches": catches,
        "catch_number": catches + 1 if session else 0,
        "fish_caught": int(session.get("fish_caught", 0)),
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
        "efficiency": float(FISH_FLINGERS_EFFICIENCY[catches]) if session else 0.5,
        "next_discovery": str(FISH_FLINGERS_DISCOVERY_LABELS[catches]) if session else "Best bait",
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
