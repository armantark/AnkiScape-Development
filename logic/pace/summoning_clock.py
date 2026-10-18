"""The familiar's short timers, advanced on every answered card (Again included).

Lifetime and its Summoning-point drain, special-move recharge, Bunyip healing,
triple charms, and the reclaim window that a departing familiar's storage drops
into. ``logic/summoning_logic.py`` owns the transactions that start them and
what a familiar's expiry does to the rest of the save.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from ...data.summoning_data import SUMMONING_POUCHES_BY_ID, SUMMONING_RENEWAL_SOURCE_MINUTES
from .short_timers import STEP_TICKS, TICKS_PER_LEGACY_SHORT_REVIEW, TICKS_PER_SOURCE_MINUTE


SPECIAL_MOVE_POINTS_MAX = 60
SPECIAL_MOVE_RECHARGE_TICKS = 50
SPECIAL_MOVE_RECHARGE_POINTS = 15
BUNYIP_HEAL_TICKS = 25
BUNYIP_HEAL_LIFEPOINTS = 20
CARGO_RECLAIM_TICKS = 5 * TICKS_PER_SOURCE_MINUTE
RENEWAL_WINDOW_TICKS = round(SUMMONING_RENEWAL_SOURCE_MINUTES * TICKS_PER_SOURCE_MINUTE)
CARGO_TIMER_KEY = "remaining_ticks"
TRIPLE_CHARM_TIMER_KEY = "triple_charm_ticks_remaining"
# The card counts a save from before ticks still holds, with their tick fields.
_LEGACY_FAMILIAR_FIELDS = (
    ("remaining_reviews", "remaining_ticks"),
    ("max_reviews", "max_ticks"),
    ("summoning_point_drain_residual", "summoning_point_drain_residual"),
)
_LEGACY_CARGO_KEY = "remaining_reviews"
_LEGACY_TRIPLE_CHARM_KEY = "triple_charm_reviews_remaining"


def _clean_int(
    value: Any,
    default: int = 0,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    try:
        clean = int(value)
    except (TypeError, ValueError, OverflowError):
        clean = default
    if minimum is not None:
        clean = max(minimum, clean)
    if maximum is not None:
        clean = min(maximum, clean)
    return clean


def _legacy_ticks(raw: Mapping[str, Any], key: str, legacy_key: str) -> int:
    if key in raw or legacy_key not in raw:
        return _clean_int(raw.get(key), 0, minimum=0)
    return _clean_int(raw.get(legacy_key), 0, minimum=0) * TICKS_PER_LEGACY_SHORT_REVIEW


def familiar_lifetime_ticks(pouch: Any) -> int:
    return pouch.duration_source_minutes * TICKS_PER_SOURCE_MINUTE


def sanitize_familiar_timers(follower: dict[str, Any]) -> None:
    """Clamp an active follower's timer fields to their periods, in place.

    A follower saved before ticks converts its card counts here, so a running
    familiar keeps its remaining time.
    """
    if "remaining_ticks" not in follower:
        for legacy_key, key in _LEGACY_FAMILIAR_FIELDS:
            if legacy_key in follower:
                follower[key] = (
                    _clean_int(follower.pop(legacy_key), 0, minimum=0)
                    * TICKS_PER_LEGACY_SHORT_REVIEW
                )
    pouch = SUMMONING_POUCHES_BY_ID.get(str(follower.get("entity_id", "")))
    remaining = _clean_int(follower.get("remaining_ticks"), 0, minimum=0)
    if pouch is not None:
        remaining = min(remaining, familiar_lifetime_ticks(pouch))
    follower["remaining_ticks"] = remaining
    follower["max_ticks"] = _clean_int(follower.get("max_ticks"), remaining, minimum=0)
    follower["bunyip_heal_residual"] = _clean_int(
        follower.get("bunyip_heal_residual"),
        0,
        minimum=0,
        maximum=BUNYIP_HEAL_TICKS - 1,
    )
    drain_period = (
        familiar_lifetime_ticks(pouch) if pouch is not None else follower["max_ticks"]
    )
    follower["summoning_point_drain_residual"] = _clean_int(
        follower.get("summoning_point_drain_residual"),
        0,
        minimum=0,
        maximum=max(0, drain_period - 1),
    )


def familiar_lifetime(pouch: Any) -> dict[str, int]:
    """A freshly summoned or renewed familiar's whole lifetime."""
    lifetime = familiar_lifetime_ticks(pouch)
    return {
        "remaining_ticks": lifetime,
        "max_ticks": lifetime,
        "summoning_point_drain_residual": 0,
    }


def renewal_window_open(follower: Mapping[str, Any]) -> bool:
    return follower["remaining_ticks"] <= RENEWAL_WINDOW_TICKS


def sanitize_summoning_timers(source: Mapping[str, Any]) -> dict[str, int]:
    """The player-level timer fields of the Summoning state."""
    return {
        "special_move_recharge_residual": _clean_int(
            source.get("special_move_recharge_residual"),
            0,
            minimum=0,
            maximum=SPECIAL_MOVE_RECHARGE_TICKS - 1,
        ),
        TRIPLE_CHARM_TIMER_KEY: _legacy_ticks(
            source, TRIPLE_CHARM_TIMER_KEY, _LEGACY_TRIPLE_CHARM_KEY
        ),
    }


def _clean_inventory(raw: Any) -> dict[str, int]:
    if not isinstance(raw, Mapping):
        return {}
    return {
        str(item_name): _clean_int(amount, 0, minimum=0)
        for item_name, amount in raw.items()
        if isinstance(item_name, str) and _clean_int(amount, 0, minimum=0) > 0
    }


def sanitize_cargo_timer(raw: Mapping[str, Any]) -> int:
    return min(
        CARGO_RECLAIM_TICKS, _legacy_ticks(raw, CARGO_TIMER_KEY, _LEGACY_CARGO_KEY)
    )


def sanitize_cargo_events(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, (list, tuple)):
        return []
    events: list[dict[str, Any]] = []
    seen: set[int] = set()
    for candidate in raw:
        if not isinstance(candidate, Mapping):
            continue
        event_id = _clean_int(candidate.get("event_id"), 0, minimum=1)
        items = _clean_inventory(candidate.get("items"))
        remaining = sanitize_cargo_timer(candidate)
        if event_id in seen or not items or remaining <= 0:
            continue
        seen.add(event_id)
        events.append(
            {
                "event_id": event_id,
                "familiar_id": str(candidate.get("familiar_id", "")),
                "items": items,
                CARGO_TIMER_KEY: remaining,
                "source": str(candidate.get("source", "expiry")),
            }
        )
    return sorted(events, key=lambda event: event["event_id"])[-20:]


def drop_familiar_storage(
    state: dict[str, Any],
    follower: Mapping[str, Any],
    *,
    source: str,
) -> Optional[dict[str, Any]]:
    storage = _clean_inventory(follower.get("storage"))
    if not storage:
        return None
    event = {
        "event_id": state["cargo_next_event_id"],
        "familiar_id": str(follower.get("entity_id", "")),
        "items": storage,
        CARGO_TIMER_KEY: CARGO_RECLAIM_TICKS,
        "source": source,
    }
    state["cargo_next_event_id"] += 1
    state["cargo_events"].append(event)
    state["cargo_events"] = state["cargo_events"][-20:]
    return event


def triple_charm_duration(shards: int) -> int:
    """Triple charm drops for 40 seconds per raw shard, rounded to the minute."""
    return round(shards * 40.0 / 60.0) * TICKS_PER_SOURCE_MINUTE


def _advance_bunyip_heal(
    player_data: dict[str, Any], follower: dict[str, Any], ticks: int
) -> int:
    # An ordinary familiar stays summoned through a Frozen floor, but its heal
    # must not reach Daemonheim, where survival rests on floor supplies alone.
    dungeon = player_data.get("dungeoneering")
    in_floor = isinstance(dungeon, Mapping) and bool(dungeon.get("active"))
    if follower.get("entity_id") != "bunyip" or in_floor:
        return 0
    heal_steps, follower["bunyip_heal_residual"] = divmod(
        _clean_int(follower.get("bunyip_heal_residual"), 0, minimum=0) + ticks,
        BUNYIP_HEAL_TICKS,
    )
    maximum = max(
        10, _clean_int(player_data.get("constitution_level"), 10, minimum=1) * 10
    )
    before = _clean_int(
        player_data.get("combat_lifepoints"), maximum, minimum=0, maximum=maximum
    )
    player_data["combat_lifepoints"] = min(
        maximum, before + heal_steps * BUNYIP_HEAL_LIFEPOINTS
    )
    return player_data["combat_lifepoints"] - before


def _advance_familiar_lifetime(
    state: dict[str, Any], follower: dict[str, Any], ticks: int
) -> None:
    remaining = max(0, _clean_int(follower.get("remaining_ticks"), 0))
    lived = min(ticks, remaining)
    follower["remaining_ticks"] = remaining - lived
    pouch = SUMMONING_POUCHES_BY_ID.get(str(follower["entity_id"]))
    if pouch is None:
        return
    # The drain spreads over the ticks the familiar actually lives, so a card
    # that outlasts it cannot drain past the source total.
    lifetime = max(1, familiar_lifetime_ticks(pouch))
    drain_per_lifetime = max(0, pouch.level - pouch.summoning_point_cost)
    drain_steps, follower["summoning_point_drain_residual"] = divmod(
        _clean_int(
            follower.get("summoning_point_drain_residual"),
            0,
            minimum=0,
            maximum=lifetime - 1,
        )
        + drain_per_lifetime * lived,
        lifetime,
    )
    state["summoning_points_current"] = max(
        0, state["summoning_points_current"] - drain_steps
    )


def advance_summoning_timers(
    player_data: dict[str, Any], state: dict[str, Any], ticks: int = STEP_TICKS
) -> dict[str, Any]:
    """Advance every timer of a sanitized Summoning state by one card's ticks.

    Returns the cargo events whose window closed, the Bunyip's healing, and
    the familiar whose lifetime ran out, still in ``state`` for its owner to
    retire.
    """
    retained: list[dict[str, Any]] = []
    lost: list[dict[str, Any]] = []
    for event in state["cargo_events"]:
        event = dict(event)
        event[CARGO_TIMER_KEY] -= ticks
        (retained if event[CARGO_TIMER_KEY] > 0 else lost).append(event)
    state["cargo_events"] = retained

    recharge_steps, state["special_move_recharge_residual"] = divmod(
        state["special_move_recharge_residual"] + ticks,
        SPECIAL_MOVE_RECHARGE_TICKS,
    )
    state["special_move_points_current"] = min(
        SPECIAL_MOVE_POINTS_MAX,
        state["special_move_points_current"]
        + recharge_steps * SPECIAL_MOVE_RECHARGE_POINTS,
    )
    state[TRIPLE_CHARM_TIMER_KEY] = max(0, state[TRIPLE_CHARM_TIMER_KEY] - ticks)

    healing = 0
    expired = None
    follower = state["active_follower"]
    if follower.get("kind") == "familiar":
        follower = dict(follower)
        healing = _advance_bunyip_heal(player_data, follower, ticks)
        _advance_familiar_lifetime(state, follower, ticks)
        state["active_follower"] = follower
        if follower["remaining_ticks"] <= 0:
            expired = follower
    return {"lost_cargo_events": lost, "passive_healing": healing, "expired": expired}
