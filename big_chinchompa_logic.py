"""Pure Big Chinchompa world-event, reward, and private-ground logic."""

from __future__ import annotations

import copy
import math
from typing import Any, Mapping, Sequence

try:
    from .big_chinchompa_data import (
        BIG_CHINCHOMPA_COMPETENCE_CAP,
        BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW,
        BIG_CHINCHOMPA_EVENT_INTERVAL_REVIEWS,
        BIG_CHINCHOMPA_EVENT_MINUTES,
        BIG_CHINCHOMPA_JAR_CAPACITY,
        BIG_CHINCHOMPA_LOCATIONS,
        BIG_CHINCHOMPA_MOTH_TIERS,
        BIG_CHINCHOMPA_PERSONAL_POINT_CAP,
        BIG_CHINCHOMPA_PLAYER_FULLNESS_BPS_PER_CIRCUIT,
        BIG_CHINCHOMPA_REWARDS_BY_ID,
        BIG_CHINCHOMPA_TICKET_BY_TARGET,
        BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW,
        WORLD_POPULATION_BASE_CEILINGS,
        WORLD_POPULATION_PROFILES,
    )
except ImportError:  # pragma: no cover - flat test imports
    from big_chinchompa_data import (  # type: ignore
        BIG_CHINCHOMPA_COMPETENCE_CAP,
        BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW,
        BIG_CHINCHOMPA_EVENT_INTERVAL_REVIEWS,
        BIG_CHINCHOMPA_EVENT_MINUTES,
        BIG_CHINCHOMPA_JAR_CAPACITY,
        BIG_CHINCHOMPA_LOCATIONS,
        BIG_CHINCHOMPA_MOTH_TIERS,
        BIG_CHINCHOMPA_PERSONAL_POINT_CAP,
        BIG_CHINCHOMPA_PLAYER_FULLNESS_BPS_PER_CIRCUIT,
        BIG_CHINCHOMPA_REWARDS_BY_ID,
        BIG_CHINCHOMPA_TICKET_BY_TARGET,
        BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW,
        WORLD_POPULATION_BASE_CEILINGS,
        WORLD_POPULATION_PROFILES,
    )


BIG_CHINCHOMPA_STATE_VERSION = 1
DEFAULT_WORLD_POPULATION_PROFILE = "normal"


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    return _int(clock.get("answered_cards"))


def _next_slot_card(answered_cards: int) -> int:
    if answered_cards < BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW:
        return BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW
    elapsed = answered_cards - BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW
    return (
        BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW
        + (elapsed // BIG_CHINCHOMPA_EVENT_INTERVAL_REVIEWS + 1)
        * BIG_CHINCHOMPA_EVENT_INTERVAL_REVIEWS
    )


def _current_slot_card(answered_cards: int) -> int:
    if answered_cards < BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW:
        return 0
    elapsed = answered_cards - BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW
    return (
        BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW
        + (elapsed // BIG_CHINCHOMPA_EVENT_INTERVAL_REVIEWS)
        * BIG_CHINCHOMPA_EVENT_INTERVAL_REVIEWS
    )


def _world_minutes(answered_cards: int) -> int:
    return answered_cards * BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW


def _has_future_review_window(answered_cards: int, end_world_minute: int) -> bool:
    return (
        _world_minutes(answered_cards)
        + BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW
        <= end_world_minute
    )


def _event_seed(slot_card: int) -> int:
    return (slot_card * 1_103_515_245 + 12_345) & 0x7FFFFFFF


def _seed_unit(seed: int, stream: int) -> float:
    value = (seed ^ (stream * 0x9E3779B9)) & 0xFFFFFFFF
    value = (value * 1_664_525 + 1_013_904_223) & 0xFFFFFFFF
    return value / 0xFFFFFFFF


def _profile(player_data: Mapping[str, Any]) -> str:
    value = str(
        player_data.get(
            "world_population_profile",
            DEFAULT_WORLD_POPULATION_PROFILE,
        )
    ).lower()
    return value if value in WORLD_POPULATION_PROFILES else DEFAULT_WORLD_POPULATION_PROFILE


def default_big_chinchompa_state_pure() -> dict[str, Any]:
    return {
        "version": BIG_CHINCHOMPA_STATE_VERSION,
        "active_event": {},
        "competence_points": 0,
        "last_resolved_slot_card": 0,
        "last_result": "",
        "event_log": [],
    }


def sanitize_big_chinchompa_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_big_chinchompa_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    active: dict[str, Any] = {}
    raw_event = source.get("active_event")
    if isinstance(raw_event, Mapping):
        slot_card = _int(raw_event.get("slot_card"))
        event_id = str(raw_event.get("event_id", ""))
        location = str(raw_event.get("location", ""))
        if (
            slot_card >= BIG_CHINCHOMPA_EVENT_FIRST_SLOT_REVIEW
            and event_id
            and location in BIG_CHINCHOMPA_LOCATIONS
        ):
            active = {
                "event_id": event_id,
                "slot_card": slot_card,
                "end_world_minute": slot_card
                * BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW
                + BIG_CHINCHOMPA_EVENT_MINUTES,
                "location": location,
                "seed": _int(raw_event.get("seed"), _event_seed(slot_card)),
                "crowd_fullness_bps": min(
                    10_000, _int(raw_event.get("crowd_fullness_bps"))
                ),
                "player_fullness_bps": min(
                    10_000, _int(raw_event.get("player_fullness_bps"))
                ),
                "event_points": min(
                    BIG_CHINCHOMPA_PERSONAL_POINT_CAP,
                    _int(raw_event.get("event_points")),
                ),
                "circuits_completed": _int(raw_event.get("circuits_completed")),
            }
    event_log = source.get("event_log")
    return {
        **defaults,
        "active_event": active,
        "competence_points": min(
            BIG_CHINCHOMPA_COMPETENCE_CAP,
            _int(source.get("competence_points")),
        ),
        "last_resolved_slot_card": _int(
            source.get("last_resolved_slot_card")
        ),
        "last_result": str(source.get("last_result", ""))[:240],
        "event_log": (
            [dict(row) for row in event_log if isinstance(row, Mapping)][-20:]
            if isinstance(event_log, list)
            else []
        ),
    }


def ensure_big_chinchompa_state_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    data = copy.deepcopy(dict(player_data))
    data["world_population_profile"] = _profile(data)
    data["big_chinchompa"] = sanitize_big_chinchompa_state_pure(
        data.get("big_chinchompa")
    )
    private = data.get("hunter_private_ground_targets")
    data["hunter_private_ground_targets"] = (
        [
            target_id
            for target_id in dict.fromkeys(str(value) for value in private)
            if target_id in BIG_CHINCHOMPA_TICKET_BY_TARGET
        ]
        if isinstance(private, (list, tuple))
        else []
    )
    return data


def _event_total_fullness_bps(event: Mapping[str, Any]) -> int:
    return min(
        10_000,
        _int(event.get("crowd_fullness_bps"))
        + _int(event.get("player_fullness_bps")),
    )


def _normalized_logistic(phase: float, midpoint: float, steepness: float) -> float:
    phase = max(0.0, min(1.0, phase))

    def sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-value))

    start = sigmoid(-steepness * midpoint)
    end = sigmoid(steepness * (1.0 - midpoint))
    current = sigmoid(steepness * (phase - midpoint))
    if end <= start:
        return phase
    return max(0.0, min(1.0, (current - start) / (end - start)))


def big_chinchompa_crowd_target_bps_pure(
    *,
    slot_card: int,
    answered_cards: int,
    seed: int,
    profile: str,
) -> int:
    """Return one deterministic, monotonic aggregate crowd-pressure target."""

    start_minute = slot_card * BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW
    phase = (
        _world_minutes(answered_cards) - start_minute
    ) / BIG_CHINCHOMPA_EVENT_MINUTES
    phase = max(0.0, min(1.0, phase))

    # `phase + a*sin(pi*phase)` remains monotonic for |a| <= .1 because its
    # derivative stays positive. It gives the shared smooth ±10% phase jitter
    # without allowing aggregate hunters to disappear.
    jitter = (_seed_unit(seed, 4) * 0.2) - 0.1
    natural_phase = max(
        0.0,
        min(1.0, phase + jitter * math.sin(math.pi * phase)),
    )
    midpoint = 0.5 + ((_seed_unit(seed, 2) * 0.2) - 0.1)
    steepness = 8.0 * (0.85 + _seed_unit(seed, 3) * 0.3)
    curve = _normalized_logistic(natural_phase, midpoint, steepness)

    day_phase = (slot_card % 240) / 240.0
    day_envelope = 1.0 + 0.25 * math.sin(2.0 * math.pi * day_phase)
    base_ceiling = WORLD_POPULATION_BASE_CEILINGS.get(
        profile,
        WORLD_POPULATION_BASE_CEILINGS[DEFAULT_WORLD_POPULATION_PROFILE],
    )
    seeded_ceiling = base_ceiling * (0.8 + _seed_unit(seed, 1) * 0.4)
    ceiling = seeded_ceiling * day_envelope
    return min(10_000, max(0, int(round(curve * ceiling * 10_000))))


def _spawn_event(slot_card: int) -> dict[str, Any]:
    seed = _event_seed(slot_card)
    location = BIG_CHINCHOMPA_LOCATIONS[
        int(_seed_unit(seed, 0) * len(BIG_CHINCHOMPA_LOCATIONS))
        % len(BIG_CHINCHOMPA_LOCATIONS)
    ]
    return {
        "event_id": f"big-chinchompa-{slot_card}",
        "slot_card": slot_card,
        "end_world_minute": slot_card
        * BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW
        + BIG_CHINCHOMPA_EVENT_MINUTES,
        "location": location,
        "seed": seed,
        "crowd_fullness_bps": 0,
        "player_fullness_bps": 0,
        "event_points": 0,
        "circuits_completed": 0,
    }


def _resolve_active_event(
    data: dict[str, Any],
    *,
    reason: str,
) -> dict[str, Any]:
    state = dict(data["big_chinchompa"])
    event = dict(state.get("active_event") or {})
    if not event:
        return data
    earned = min(
        BIG_CHINCHOMPA_PERSONAL_POINT_CAP,
        _int(event.get("event_points")),
    )
    before = _int(state.get("competence_points"))
    after = min(BIG_CHINCHOMPA_COMPETENCE_CAP, before + earned)
    event_row = {
        "kind": "resolved",
        "event_id": event["event_id"],
        "slot_card": event["slot_card"],
        "reason": reason,
        "event_points": earned,
        "competence_awarded": after - before,
        "circuits_completed": _int(event.get("circuits_completed")),
    }
    state["competence_points"] = after
    state["last_resolved_slot_card"] = _int(event.get("slot_card"))
    state["last_result"] = (
        f"Big Chinchompa ended: {earned:,} event points became "
        f"{after - before:,} Competence points."
    )
    state["active_event"] = {}
    state["event_log"] = (list(state.get("event_log", [])) + [event_row])[-20:]
    data["big_chinchompa"] = sanitize_big_chinchompa_state_pure(state)
    return data


def advance_big_chinchompa_world_clock_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    """Advance one lazy world boundary without reading wall-clock time."""

    data = ensure_big_chinchompa_state_pure(player_data)
    answered = _answered_cards(data)
    state = dict(data["big_chinchompa"])
    events: list[dict[str, Any]] = []
    event = dict(state.get("active_event") or {})

    if event:
        end_world_minute = _int(event.get("end_world_minute"))
        expired = (
            _world_minutes(answered) >= end_world_minute
            or not _has_future_review_window(answered, end_world_minute)
        )
        already_full = _event_total_fullness_bps(event) >= 10_000
        if expired or already_full:
            reason = "full" if already_full else "expired"
            data = _resolve_active_event(data, reason=reason)
            events.append({"kind": "resolved", "reason": reason})
            state = dict(data["big_chinchompa"])
            event = {}
        else:
            crowd_target = big_chinchompa_crowd_target_bps_pure(
                slot_card=_int(event.get("slot_card")),
                answered_cards=answered,
                seed=_int(event.get("seed")),
                profile=_profile(data),
            )
            event["crowd_fullness_bps"] = max(
                _int(event.get("crowd_fullness_bps")),
                crowd_target,
            )
            state["active_event"] = event
            data["big_chinchompa"] = sanitize_big_chinchompa_state_pure(state)
            if _event_total_fullness_bps(event) >= 10_000:
                data = _resolve_active_event(data, reason="full")
                events.append({"kind": "resolved", "reason": "full"})
                state = dict(data["big_chinchompa"])
                event = {}

    if not event:
        slot_card = _current_slot_card(answered)
        within_window = (
            slot_card > 0
            and _has_future_review_window(
                answered,
                slot_card * BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW
                + BIG_CHINCHOMPA_EVENT_MINUTES,
            )
        )
        if (
            within_window
            and slot_card > _int(state.get("last_resolved_slot_card"))
        ):
            event = _spawn_event(slot_card)
            state["active_event"] = event
            state["event_log"] = (
                list(state.get("event_log", []))
                + [{"kind": "spawned", **event}]
            )[-20:]
            data["big_chinchompa"] = sanitize_big_chinchompa_state_pure(
                state
            )
            events.append({"kind": "spawned", **event})

    return data, tuple(events)


def big_chinchompa_event_active_pure(player_data: Mapping[str, Any]) -> bool:
    data = ensure_big_chinchompa_state_pure(player_data)
    event = data["big_chinchompa"]["active_event"]
    return bool(
        event
        and _world_minutes(_answered_cards(data))
        < _int(event.get("end_world_minute"))
        and _event_total_fullness_bps(event) < 10_000
    )


def best_soporith_moth_tier_pure(hunter_level: int):
    level = _int(hunter_level, 1, minimum=1)
    return max(
        (
            tier
            for tier in BIG_CHINCHOMPA_MOTH_TIERS
            if level >= tier.hunter_level
        ),
        key=lambda tier: tier.hunter_level,
    )


def apply_big_chinchompa_review_pure(
    player_data: Mapping[str, Any],
    *,
    circuits: int = 1,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_big_chinchompa_state_pure(player_data)
    if not big_chinchompa_event_active_pure(data):
        return data, False, {"reason": "No Big Chinchompa event is active."}

    state = dict(data["big_chinchompa"])
    event = dict(state["active_event"])
    tier = best_soporith_moth_tier_pure(
        _int(data.get("hunter_level"), 1, minimum=1)
    )
    requested = max(1, _int(circuits, 1, minimum=1))
    completed = 0
    hunter_xp = 0.0
    points_awarded = 0

    for _index in range(requested):
        if _event_total_fullness_bps(event) >= 10_000:
            break
        completed += 1
        hunter_xp += tier.xp * BIG_CHINCHOMPA_JAR_CAPACITY
        current_points = _int(event.get("event_points"))
        point_room = max(
            0, BIG_CHINCHOMPA_PERSONAL_POINT_CAP - current_points
        )
        circuit_points = tier.points * BIG_CHINCHOMPA_JAR_CAPACITY
        gained_points = min(point_room, circuit_points)
        points_awarded += gained_points
        event["event_points"] = current_points + gained_points
        event["circuits_completed"] = (
            _int(event.get("circuits_completed")) + 1
        )
        event["player_fullness_bps"] = min(
            10_000,
            _int(event.get("player_fullness_bps"))
            + BIG_CHINCHOMPA_PLAYER_FULLNESS_BPS_PER_CIRCUIT,
        )

    if completed <= 0:
        return data, False, {"reason": "The Big Chinchompa is already full."}

    state["active_event"] = event
    state["last_result"] = (
        f"Released {completed * BIG_CHINCHOMPA_JAR_CAPACITY} "
        f"{tier.display_name.lower()}s."
    )
    data["big_chinchompa"] = sanitize_big_chinchompa_state_pure(state)
    return data, True, {
        "tier_id": tier.id,
        "tier_name": tier.display_name,
        "circuits": completed,
        "moths": completed * BIG_CHINCHOMPA_JAR_CAPACITY,
        "hunter_xp": hunter_xp,
        "event_points": points_awarded,
        "event_points_total": _int(event.get("event_points")),
        "personal_cap_reached": _int(event.get("event_points"))
        >= BIG_CHINCHOMPA_PERSONAL_POINT_CAP,
        "fullness_percent": _event_total_fullness_bps(event) / 100.0,
    }


def set_world_population_profile_pure(
    player_data: Mapping[str, Any],
    profile: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    value = str(profile).lower()
    if value not in WORLD_POPULATION_PROFILES:
        return copy.deepcopy(dict(player_data)), False, {
            "reason": "Unknown world-population profile."
        }
    data = ensure_big_chinchompa_state_pure(player_data)
    data["world_population_profile"] = value
    return data, True, {"profile": value}


def apply_big_chinchompa_reward_purchase_pure(
    player_data: Mapping[str, Any],
    reward_id: str,
    *,
    exp_table: Sequence[int] = (),
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_big_chinchompa_state_pure(player_data)
    reward = BIG_CHINCHOMPA_REWARDS_BY_ID.get(str(reward_id))
    if reward is None:
        return data, False, {"reason": "Unknown Big Chinchompa reward."}
    hunter_level = _int(data.get("hunter_level"), 1, minimum=1)
    if hunter_level < reward.hunter_level:
        return data, False, {
            "reason": f"Requires Hunter level {reward.hunter_level}."
        }
    state = dict(data["big_chinchompa"])
    wallet = _int(state.get("competence_points"))
    if wallet < reward.competence_cost:
        return data, False, {"reason": "Not enough Competence points."}

    state["competence_points"] = wallet - reward.competence_cost
    data["big_chinchompa"] = sanitize_big_chinchompa_state_pure(state)
    if reward.item_name:
        inventory = dict(data.get("inventory", {}) or {})
        inventory[reward.item_name] = (
            _int(inventory.get(reward.item_name)) + 1
        )
        data["inventory"] = inventory
    elif reward.hunter_xp > 0:
        hunter_exp = float(data.get("hunter_exp", 0.0) or 0.0) + reward.hunter_xp
        data["hunter_exp"] = hunter_exp
        if exp_table:
            level = hunter_level
            while level < 99 and level < len(exp_table):
                if hunter_exp < float(exp_table[level]):
                    break
                level += 1
            data["hunter_level"] = level

    return data, True, {
        "reward_id": reward.id,
        "display_name": reward.display_name,
        "cost": reward.competence_cost,
        "item_name": reward.item_name,
        "hunter_xp": reward.hunter_xp,
        "competence_points": state["competence_points"],
    }


def _hunter_carried_inventory_for_target(
    player_data: Mapping[str, Any],
    target_id: str,
) -> Mapping[str, Any]:
    carried = player_data.get("carried_inventory")
    if isinstance(carried, Mapping) and target_id in carried:
        value = carried.get(target_id)
        return value if isinstance(value, Mapping) else {}
    advanced = player_data.get("carried_advanced_targets")
    if isinstance(advanced, Mapping) and bool(advanced.get(target_id)):
        layouts = player_data.get("carried_layout")
        if isinstance(layouts, Mapping):
            value = layouts.get(target_id)
            return value if isinstance(value, Mapping) else {}
    return {}


def set_hunter_private_ground_pure(
    player_data: Mapping[str, Any],
    target_id: str,
    enabled: bool,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_big_chinchompa_state_pure(player_data)
    target = str(target_id)
    ticket = BIG_CHINCHOMPA_TICKET_BY_TARGET.get(target)
    if not ticket:
        return data, False, {"reason": "That target has no private ground."}
    carried = _hunter_carried_inventory_for_target(data, target)
    if enabled and (
        _int((data.get("inventory") or {}).get(ticket)) <= 0
        or _int(carried.get(ticket)) <= 0
    ):
        return data, False, {
            "reason": f"Add {ticket} to this target's carried pack."
        }
    selected = list(data["hunter_private_ground_targets"])
    if enabled and target not in selected:
        selected.append(target)
    if not enabled:
        selected = [value for value in selected if value != target]
    data["hunter_private_ground_targets"] = selected
    return data, True, {
        "target_id": target,
        "enabled": bool(enabled),
        "ticket": ticket,
    }


def hunter_private_ground_status_pure(
    player_data: Mapping[str, Any],
    target_id: str,
    *,
    inventory_override: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    data = ensure_big_chinchompa_state_pure(player_data)
    target = str(target_id)
    ticket = BIG_CHINCHOMPA_TICKET_BY_TARGET.get(target, "")
    inventory = (
        inventory_override
        if isinstance(inventory_override, Mapping)
        else _hunter_carried_inventory_for_target(data, target)
    )
    count = _int(inventory.get(ticket)) if ticket else 0
    configured = target in data["hunter_private_ground_targets"]
    return {
        "available": bool(ticket),
        "ticket": ticket,
        "tickets": count,
        "configured": configured,
        "active": configured and count > 0,
    }


def consume_hunter_quota_ticket_pure(
    player_data: Mapping[str, Any],
    target_id: str,
) -> tuple[dict[str, Any], str]:
    """Consume one configured ticket after a successful ordinary catch."""

    data = ensure_big_chinchompa_state_pure(player_data)
    carried_by_target = data.get("carried_inventory")
    carried = _hunter_carried_inventory_for_target(data, str(target_id))
    status = hunter_private_ground_status_pure(
        data,
        target_id,
        inventory_override=carried,
    )
    if not status["active"]:
        return data, ""
    ticket = str(status["ticket"])
    inventory = dict(data.get("inventory", {}) or {})
    inventory[ticket] = max(0, _int(inventory.get(ticket)) - 1)
    data["inventory"] = inventory
    carried_map = (
        dict(carried_by_target)
        if isinstance(carried_by_target, Mapping)
        else {}
    )
    updated_carried = dict(carried)
    updated_carried[ticket] = max(
        0, _int(updated_carried.get(ticket)) - 1
    )
    remaining = updated_carried[ticket]
    carried_map[str(target_id)] = {
        item_name: amount
        for item_name, amount in updated_carried.items()
        if _int(amount) > 0
    }
    data["carried_inventory"] = carried_map
    if remaining <= 0:
        data["hunter_private_ground_targets"] = [
            value
            for value in data["hunter_private_ground_targets"]
            if value != str(target_id)
        ]
    return data, ticket


def big_chinchompa_view_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    data = ensure_big_chinchompa_state_pure(player_data)
    answered = _answered_cards(data)
    state = data["big_chinchompa"]
    event = state["active_event"]
    active = big_chinchompa_event_active_pure(data)
    tier = best_soporith_moth_tier_pure(
        _int(data.get("hunter_level"), 1, minimum=1)
    )
    if active:
        minutes = max(
            0,
            _int(event.get("end_world_minute")) - _world_minutes(answered),
        )
        reviews = max(
            0,
            minutes // BIG_CHINCHOMPA_WORLD_MINUTES_PER_REVIEW,
        )
        fullness = _event_total_fullness_bps(event) / 100.0
    else:
        minutes = 0
        reviews = max(0, _next_slot_card(answered) - answered)
        fullness = 0.0
    return {
        "active": active,
        "location": str(event.get("location", "")) if active else "",
        "minutes_remaining": minutes,
        "reviews_remaining": reviews if active else 0,
        "next_reviews": reviews if not active else 0,
        "fullness_percent": fullness,
        "event_points": _int(event.get("event_points")) if active else 0,
        "point_cap": BIG_CHINCHOMPA_PERSONAL_POINT_CAP,
        "competence_points": _int(state.get("competence_points")),
        "competence_cap": BIG_CHINCHOMPA_COMPETENCE_CAP,
        "tier_id": tier.id,
        "tier_name": tier.display_name,
        "tier_level": tier.hunter_level,
        "tier_xp_per_jar": tier.xp * BIG_CHINCHOMPA_JAR_CAPACITY,
        "tier_points_per_jar": tier.points * BIG_CHINCHOMPA_JAR_CAPACITY,
        "population_profile": _profile(data),
        "last_result": str(state.get("last_result", "")),
    }
