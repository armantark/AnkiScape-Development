"""Pure Shooting Star lifecycle, mining, preferences, and reward exchange."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Sequence

from ..data.shooting_star_data import (
    SHOOTING_STAR_FIRST_FINDER_CHANCE,
    SHOOTING_STAR_POPULATION_BASE_CEILING,
    SHOOTING_STAR_INTERVAL_REVIEWS,
    SHOOTING_STAR_LAYERS_BY_SIZE,
    SHOOTING_STAR_LEGACY_LOCATION_ALIASES,
    SHOOTING_STAR_LOCATIONS,
    SHOOTING_STAR_ORE_BONUS_TICKS,
    SHOOTING_STAR_REWARD_MAXIMA,
    SHOOTING_STAR_SPRITE_REVIEWS,
    SHOOTING_STAR_STARDUST,
    SHOOTING_STAR_STARDUST_CAP,
)
from .pace.world_clock import DEFAULT_WORLD_DAY_CARDS, world_day_index_pure
from .world_population_logic import (
    naturalized_population_target_bps_pure,
    seeded_unit_pure,
)


SHOOTING_STAR_STATE_VERSION = 2


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _signed_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return int(default)


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    return _int(clock.get("answered_cards"))


def _current_slot_card(answered_cards: int) -> int:
    return (
        answered_cards // SHOOTING_STAR_INTERVAL_REVIEWS
    ) * SHOOTING_STAR_INTERVAL_REVIEWS


def _next_slot_card(answered_cards: int) -> int:
    return (
        answered_cards // SHOOTING_STAR_INTERVAL_REVIEWS + 1
    ) * SHOOTING_STAR_INTERVAL_REVIEWS


def _event_seed(slot_card: int) -> int:
    return (int(slot_card) * 1_664_525 + 1_013_904_223) & 0x7FFFFFFF


def _layer_mass(starting_size: int) -> int:
    return sum(
        layer.dust
        for size, layer in SHOOTING_STAR_LAYERS_BY_SIZE.items()
        if size <= int(starting_size)
    )


def default_shooting_star_state_pure() -> dict[str, Any]:
    return {
        "version": SHOOTING_STAR_STATE_VERSION,
        "active_event": {},
        "last_resolved_slot_card": 0,
        "last_exchange_day": -1,
        "ore_bonus_ticks_remaining": 0,
        "last_result": "",
        "event_log": [],
        "notice": {},
        "watched_event_id": "",
    }


def _sanitize_event(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    slot_card = _int(raw.get("slot_card"))
    starting_size = min(9, _int(raw.get("starting_size"), 1, minimum=1))
    current_size = min(
        starting_size,
        _int(raw.get("current_size"), starting_size),
    )
    location = str(raw.get("location", ""))
    location = SHOOTING_STAR_LEGACY_LOCATION_ALIASES.get(location, location)
    event_id = str(raw.get("event_id", ""))
    sprite_released = bool(raw.get("sprite_released", False))
    if (
        slot_card < SHOOTING_STAR_INTERVAL_REVIEWS
        or not event_id
        or location not in SHOOTING_STAR_LOCATIONS
    ):
        return {}
    if not sprite_released and current_size <= 0:
        current_size = starting_size
    layer_remaining = 0
    if not sprite_released and current_size > 0:
        layer_remaining = min(
            SHOOTING_STAR_LAYERS_BY_SIZE[current_size].dust,
            _int(
                raw.get(
                    "layer_remaining",
                    SHOOTING_STAR_LAYERS_BY_SIZE[current_size].dust,
                )
            ),
        )
        if layer_remaining <= 0:
            layer_remaining = SHOOTING_STAR_LAYERS_BY_SIZE[current_size].dust
    total_mass = _layer_mass(starting_size)
    return {
        "event_id": event_id,
        "slot_card": slot_card,
        "seed": _int(raw.get("seed"), _event_seed(slot_card)),
        "location": location,
        "starting_size": starting_size,
        "current_size": 0 if sprite_released else current_size,
        "layer_remaining": layer_remaining,
        "total_mass": total_mass,
        "crowd_dust_removed": min(
            total_mass, _int(raw.get("crowd_dust_removed"))
        ),
        "player_dust_mined": min(
            total_mass, _int(raw.get("player_dust_mined"))
        ),
        "player_attempted": bool(raw.get("player_attempted", False)),
        "tag_candidate": bool(raw.get("tag_candidate", False)),
        "tag_awarded": bool(raw.get("tag_awarded", False)),
        "sprite_released": sprite_released,
        "sprite_expires_card": (
            _int(raw.get("sprite_expires_card"))
            if sprite_released
            else 0
        ),
    }


def sanitize_shooting_star_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_shooting_star_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    event_log = source.get("event_log")
    raw_notice = source.get("notice")
    notice: dict[str, Any] = {}
    if isinstance(raw_notice, Mapping):
        kind = str(raw_notice.get("kind", ""))
        event_id = str(raw_notice.get("event_id", ""))[:80]
        if kind in {"unminable", "ready"} and event_id:
            notice = {
                "kind": kind,
                "event_id": event_id,
                "current_size": min(
                    9,
                    _int(raw_notice.get("current_size"), minimum=0),
                ),
                "required_level": min(
                    90,
                    _int(raw_notice.get("required_level"), minimum=0),
                ),
                "sprite_available": bool(
                    raw_notice.get("sprite_available", False)
                ),
            }
    return {
        **defaults,
        "active_event": _sanitize_event(source.get("active_event")),
        "last_resolved_slot_card": _int(
            source.get("last_resolved_slot_card")
        ),
        "last_exchange_day": max(
            -1,
            _signed_int(source.get("last_exchange_day"), -1),
        ),
        "ore_bonus_ticks_remaining": _int(
            source.get("ore_bonus_ticks_remaining")
        ),
        "last_result": str(source.get("last_result", ""))[:240],
        "event_log": (
            [dict(row) for row in event_log if isinstance(row, Mapping)][-20:]
            if isinstance(event_log, list)
            else []
        ),
        "notice": notice,
        "watched_event_id": str(
            source.get("watched_event_id", "") or ""
        )[:80],
    }


def ensure_shooting_star_state_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    # Shallow on purpose: every key written below is rebuilt from scratch, and a
    # whole-save deep copy here cost 2.07 ms on every review.
    data = dict(player_data)
    data["shooting_star"] = sanitize_shooting_star_state_pure(
        data.get("shooting_star")
    )
    return data


def _spawn_event(*, slot_card: int) -> dict[str, Any]:
    seed = _event_seed(slot_card)
    sizes = tuple(range(1, 10))
    starting_size = sizes[
        min(
            len(sizes) - 1,
            int(seeded_unit_pure(seed, 6) * len(sizes)),
        )
    ]
    location = SHOOTING_STAR_LOCATIONS[
        min(
            len(SHOOTING_STAR_LOCATIONS) - 1,
            int(
                seeded_unit_pure(seed, 0)
                * len(SHOOTING_STAR_LOCATIONS)
            ),
        )
    ]
    return {
        "event_id": f"shooting-star-{slot_card}",
        "slot_card": slot_card,
        "seed": seed,
        "location": location,
        "starting_size": starting_size,
        "current_size": starting_size,
        "layer_remaining": SHOOTING_STAR_LAYERS_BY_SIZE[
            starting_size
        ].dust,
        "total_mass": _layer_mass(starting_size),
        "crowd_dust_removed": 0,
        "player_dust_mined": 0,
        "player_attempted": False,
        "tag_candidate": (
            seeded_unit_pure(seed, 7) < SHOOTING_STAR_FIRST_FINDER_CHANCE
        ),
        "tag_awarded": False,
        "sprite_released": False,
        "sprite_expires_card": 0,
    }


def _release_sprite(event: dict[str, Any], answered_cards: int) -> None:
    event["current_size"] = 0
    event["layer_remaining"] = 0
    event["sprite_released"] = True
    event["sprite_expires_card"] = (
        answered_cards + SHOOTING_STAR_SPRITE_REVIEWS
    )


def _remove_dust(
    event: dict[str, Any],
    quantity: int,
    *,
    answered_cards: int,
) -> int:
    removed = 0
    remaining = max(0, int(quantity))
    while remaining > 0 and not event.get("sprite_released"):
        available = _int(event.get("layer_remaining"))
        take = min(available, remaining)
        event["layer_remaining"] = available - take
        removed += take
        remaining -= take
        if event["layer_remaining"] > 0:
            break
        current_size = _int(event.get("current_size"))
        if current_size <= 1:
            _release_sprite(event, answered_cards)
            break
        next_size = current_size - 1
        event["current_size"] = next_size
        event["layer_remaining"] = SHOOTING_STAR_LAYERS_BY_SIZE[
            next_size
        ].dust
    return removed


def _apply_crowd_target(
    event: dict[str, Any],
    *,
    answered_cards: int,
) -> None:
    if event.get("sprite_released"):
        return
    phase = (
        answered_cards - _int(event.get("slot_card"))
    ) / SHOOTING_STAR_INTERVAL_REVIEWS
    target_bps = naturalized_population_target_bps_pure(
        phase=phase,
        day_phase=(_int(event.get("slot_card")) % DEFAULT_WORLD_DAY_CARDS)
        / DEFAULT_WORLD_DAY_CARDS,
        seed=_int(event.get("seed")),
        base_ceiling=SHOOTING_STAR_POPULATION_BASE_CEILING,
    )
    total_mass = _int(event.get("total_mass"))
    target_removed = (total_mass * target_bps) // 10_000
    current_removed = _int(event.get("crowd_dust_removed"))
    quantity = max(0, target_removed - current_removed)
    if quantity <= 0:
        return
    removed = _remove_dust(
        event,
        quantity,
        answered_cards=answered_cards,
    )
    event["crowd_dust_removed"] = current_removed + removed


def _refresh_watched_star_notice(
    state: dict[str, Any],
    *,
    mining_level: int,
) -> None:
    watched_event_id = str(state.get("watched_event_id", "") or "")
    if not watched_event_id:
        return
    event = state.get("active_event")
    if not isinstance(event, Mapping) or str(event.get("event_id", "")) != watched_event_id:
        notice = state.get("notice")
        if (
            isinstance(notice, Mapping)
            and notice.get("kind") == "ready"
            and str(notice.get("event_id", "")) == watched_event_id
        ):
            state["notice"] = {}
        state["watched_event_id"] = ""
        return
    sprite_available = bool(event.get("sprite_released", False))
    current_size = 0 if sprite_available else _int(event.get("current_size"))
    required_level = (
        SHOOTING_STAR_LAYERS_BY_SIZE[current_size].mining_level
        if current_size in SHOOTING_STAR_LAYERS_BY_SIZE
        else 0
    )
    if not sprite_available and mining_level < required_level:
        return
    state["notice"] = {
        "kind": "ready",
        "event_id": watched_event_id,
        "current_size": current_size,
        "required_level": required_level,
        "sprite_available": sprite_available,
    }


def _resolve_event(
    state: dict[str, Any],
    *,
    reason: str,
) -> dict[str, Any]:
    event = dict(state.get("active_event") or {})
    if not event:
        return state
    row = {
        "kind": "resolved",
        "event_id": event.get("event_id", ""),
        "slot_card": _int(event.get("slot_card")),
        "reason": str(reason),
        "player_dust_mined": _int(event.get("player_dust_mined")),
        "tag_awarded": bool(event.get("tag_awarded", False)),
    }
    state["last_resolved_slot_card"] = max(
        _int(state.get("last_resolved_slot_card")),
        _int(event.get("slot_card")),
    )
    state["active_event"] = {}
    state["event_log"] = (
        list(state.get("event_log", [])) + [row]
    )[-20:]
    return state


def advance_shooting_star_world_clock_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    """Advance one lazy star boundary without reading wall-clock time."""

    data = ensure_shooting_star_state_pure(player_data)
    answered = _answered_cards(data)
    current_slot = _current_slot_card(answered)
    state = dict(data["shooting_star"])
    event = dict(state.get("active_event") or {})
    events: list[dict[str, Any]] = []

    if event:
        event_slot = _int(event.get("slot_card"))
        sprite_expired = bool(event.get("sprite_released")) and (
            answered >= _int(event.get("sprite_expires_card"))
        )
        superseded = current_slot > event_slot
        if sprite_expired or superseded:
            reason = "sprite_expired" if sprite_expired else "next_star"
            state = _resolve_event(state, reason=reason)
            events.append({"kind": "resolved", "reason": reason})
            event = {}
        else:
            was_sprite_released = bool(event.get("sprite_released"))
            _apply_crowd_target(
                event,
                answered_cards=answered,
            )
            state["active_event"] = event
            if not was_sprite_released and event.get("sprite_released"):
                events.append(
                    {
                        "kind": "sprite_released",
                        "event_id": event["event_id"],
                    }
                )

    if (
        not event
        and current_slot >= SHOOTING_STAR_INTERVAL_REVIEWS
        and current_slot > _int(state.get("last_resolved_slot_card"))
    ):
        event = _spawn_event(slot_card=current_slot)
        _apply_crowd_target(
            event,
            answered_cards=answered,
        )
        state["active_event"] = event
        state["event_log"] = (
            list(state.get("event_log", []))
            + [{"kind": "spawned", **event}]
        )[-20:]
        events.append({"kind": "spawned", **event})

    _refresh_watched_star_notice(
        state,
        mining_level=_int(data.get("mining_level"), 1, minimum=1),
    )

    data["shooting_star"] = sanitize_shooting_star_state_pure(state)
    return data, tuple(events)


def shooting_star_event_mineable_pure(
    player_data: Mapping[str, Any],
) -> bool:
    data = ensure_shooting_star_state_pure(player_data)
    event = data["shooting_star"]["active_event"]
    return bool(event and not event.get("sprite_released"))


def _stop_for_unminable_layer(
    data: dict[str, Any],
    state: dict[str, Any],
    event: dict[str, Any],
    *,
    current_size: int,
    tag_xp: float = 0.0,
) -> tuple[dict[str, Any], dict[str, Any]]:
    layer = SHOOTING_STAR_LAYERS_BY_SIZE[current_size]
    existing_notice = state.get("notice")
    notice_created = not (
        isinstance(existing_notice, Mapping)
        and existing_notice.get("kind") == "unminable"
        and str(existing_notice.get("event_id", ""))
        == str(event.get("event_id", ""))
    )
    state["active_event"] = event
    state["notice"] = {
        "kind": "unminable",
        "event_id": str(event.get("event_id", "")),
        "current_size": current_size,
        "required_level": layer.mining_level,
        "sprite_available": False,
    }
    state["watched_event_id"] = ""
    state["last_result"] = "Star unminable at your level"
    data["current_utility"] = "bankstanding"
    data["shooting_star"] = sanitize_shooting_star_state_pure(state)
    return data, {
        "unminable": True,
        "tag_xp": tag_xp,
        "mining_xp": tag_xp,
        "current_size": current_size,
        "required_level": layer.mining_level,
        "notice_created": notice_created,
        "event_log_text": (
            "Star unminable at your level · "
            f"Size {current_size} needs Mining {layer.mining_level}"
        ),
    }


def apply_shooting_star_join_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_shooting_star_state_pure(player_data)
    state = dict(data["shooting_star"])
    event = dict(state.get("active_event") or {})
    if not event or event.get("sprite_released"):
        return data, False, {"reason": "No mineable Shooting Star is active."}
    current_size = _int(event.get("current_size"))
    layer = SHOOTING_STAR_LAYERS_BY_SIZE[current_size]
    mining_level = _int(data.get("mining_level"), 1, minimum=1)
    if mining_level < layer.mining_level:
        stopped, info = _stop_for_unminable_layer(
            data,
            state,
            event,
            current_size=current_size,
        )
        return stopped, False, info
    data["current_utility"] = "shooting_stars"
    return data, True, {"joined": True}


def _pick_gem(
    gem_drop_table: Sequence[Mapping[str, Any]],
    roll: float,
) -> str:
    total = sum(max(0, _int(row.get("weight"))) for row in gem_drop_table)
    if total <= 0:
        return ""
    target = max(0.0, min(0.999999999, float(roll))) * total
    cursor = 0
    for row in gem_drop_table:
        cursor += max(0, _int(row.get("weight")))
        if target < cursor:
            return str(row.get("item", ""))
    return ""


def apply_shooting_star_review_pure(
    player_data: Mapping[str, Any],
    *,
    has_usable_pickaxe: bool,
    gem_roll: float = 1.0,
    gem_pick_roll: float = 0.0,
    gem_drop_chance: float = 0.0,
    gem_drop_table: Sequence[Mapping[str, Any]] = (),
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_shooting_star_state_pure(player_data)
    state = dict(data["shooting_star"])
    event = dict(state.get("active_event") or {})
    if not event or event.get("sprite_released"):
        return data, False, {"reason": "No mineable Shooting Star is active."}

    mining_level = _int(data.get("mining_level"), 1, minimum=1)
    current_size = _int(event.get("current_size"))
    layer = SHOOTING_STAR_LAYERS_BY_SIZE[current_size]
    tag_xp = 0.0
    first_attempt = not bool(event.get("player_attempted", False))
    if first_attempt:
        event["player_attempted"] = True
        if (
            event.get("tag_candidate")
            and _int(event.get("crowd_dust_removed")) <= 0
        ):
            event["tag_awarded"] = True
            tag_xp = float(75 * mining_level)

    if mining_level < layer.mining_level:
        stopped, info = _stop_for_unminable_layer(
            data,
            state,
            event,
            current_size=current_size,
            tag_xp=tag_xp,
        )
        return stopped, True, info

    if not has_usable_pickaxe:
        state["active_event"] = event
        data["shooting_star"] = sanitize_shooting_star_state_pure(state)
        if tag_xp > 0:
            return data, True, {
                "tag_only": True,
                "tag_xp": tag_xp,
                "mining_xp": tag_xp,
                "current_size": _int(event.get("current_size")),
            }
        return data, False, {"reason": "A usable pickaxe is required."}

    removed = _remove_dust(
        event,
        1,
        answered_cards=_answered_cards(data),
    )
    if removed <= 0:
        return data, False, {"reason": "The star has already been depleted."}
    event["player_dust_mined"] = (
        _int(event.get("player_dust_mined")) + removed
    )

    inventory = dict(data.get("inventory", {}) or {})
    dust_before = _int(inventory.get(SHOOTING_STAR_STARDUST))
    dust_added = min(
        removed,
        max(0, SHOOTING_STAR_STARDUST_CAP - dust_before),
    )
    inventory[SHOOTING_STAR_STARDUST] = dust_before + dust_added
    gem = ""
    if (
        gem_drop_table
        and float(gem_roll) < max(0.0, min(1.0, float(gem_drop_chance)))
    ):
        gem = _pick_gem(gem_drop_table, gem_pick_roll)
        if gem:
            inventory[gem] = _int(inventory.get(gem)) + 1
    data["inventory"] = inventory

    state["active_event"] = event
    state["last_result"] = (
        f"Mined size {current_size} stardust."
        if not event.get("sprite_released")
        else "Released the Star sprite."
    )
    data["shooting_star"] = sanitize_shooting_star_state_pure(state)
    mining_xp = layer.xp_per_dust + tag_xp
    return data, True, {
        "tag_xp": tag_xp,
        "dust_xp": layer.xp_per_dust,
        "mining_xp": mining_xp,
        "dust_added": dust_added,
        "dust_total": dust_before + dust_added,
        "dust_cap_reached": dust_before + dust_added
        >= SHOOTING_STAR_STARDUST_CAP,
        "gem": gem,
        "mined_size": current_size,
        "current_size": _int(event.get("current_size")),
        "layer_remaining": _int(event.get("layer_remaining")),
        "sprite_released": bool(event.get("sprite_released", False)),
    }


def shooting_star_notice_view_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    data = ensure_shooting_star_state_pure(player_data)
    notice = data["shooting_star"]["notice"]
    if not notice:
        return {"visible": False, "kind": "", "actions": ()}
    kind = str(notice.get("kind", ""))
    current_size = _int(notice.get("current_size"))
    required_level = _int(notice.get("required_level"))
    if kind == "unminable":
        return {
            "visible": True,
            "kind": kind,
            "label": "Star unminable at your level",
            "detail": (
                f"Size {current_size} needs Mining {required_level}. "
                "Activity stopped and selection cleared."
            ),
            "actions": (
                {"id": "watch", "label": "Watch this star"},
                {"id": "dismiss", "label": "Dismiss"},
            ),
            "event_id": str(notice.get("event_id", "")),
        }
    sprite_available = bool(notice.get("sprite_available", False))
    return {
        "visible": True,
        "kind": kind,
        "label": (
            "Star sprite available"
            if sprite_available
            else "Star ready to mine"
        ),
        "detail": (
            "Rejoin whenever you like. Nothing auto-switched."
            if sprite_available
            else f"Size {current_size} needs Mining {required_level}. "
            "Rejoin whenever you like."
        ),
        "actions": ({"id": "mine", "label": "Mine star"},),
        "event_id": str(notice.get("event_id", "")),
    }


def apply_shooting_star_notice_action_pure(
    player_data: Mapping[str, Any],
    action_id: str,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_shooting_star_state_pure(player_data)
    state = dict(data["shooting_star"])
    notice = dict(state.get("notice") or {})
    action = str(action_id or "")
    if action == "dismiss" and notice:
        state["notice"] = {}
        state["watched_event_id"] = ""
        data["shooting_star"] = sanitize_shooting_star_state_pure(state)
        return data, True, {"dismissed": True}
    if action == "watch" and notice.get("kind") == "unminable":
        state["watched_event_id"] = str(notice.get("event_id", ""))
        state["notice"] = {}
        data["shooting_star"] = sanitize_shooting_star_state_pure(state)
        return data, True, {"watching": True}
    if action == "mine" and notice.get("kind") == "ready":
        event = state.get("active_event")
        if (
            not isinstance(event, Mapping)
            or str(event.get("event_id", "")) != str(notice.get("event_id", ""))
        ):
            return data, False, {"reason": "That Shooting Star is no longer active."}
        state["notice"] = {}
        state["watched_event_id"] = ""
        data["current_utility"] = "shooting_stars"
        data["shooting_star"] = sanitize_shooting_star_state_pure(state)
        return data, True, {
            "rejoin": True,
            "sprite_available": bool(event.get("sprite_released", False)),
        }
    return data, False, {"reason": "That Shooting Star action is unavailable."}


def apply_shooting_star_exchange_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = ensure_shooting_star_state_pure(player_data)
    state = dict(data["shooting_star"])
    event = dict(state.get("active_event") or {})
    if not event or not event.get("sprite_released"):
        return data, False, {"reason": "No Star sprite is available."}

    reward_day = world_day_index_pure(data)
    if _signed_int(state.get("last_exchange_day"), -1) == reward_day:
        return data, False, {
            "reason": "The Star sprite has already rewarded this review day."
        }
    inventory = dict(data.get("inventory", {}) or {})
    dust = min(
        SHOOTING_STAR_STARDUST_CAP,
        _int(inventory.get(SHOOTING_STAR_STARDUST)),
    )
    if dust <= 0:
        return data, False, {"reason": "You have no stardust to exchange."}

    rewards = {
        item_name: (maximum * dust) // SHOOTING_STAR_STARDUST_CAP
        for item_name, maximum in SHOOTING_STAR_REWARD_MAXIMA.items()
    }
    inventory[SHOOTING_STAR_STARDUST] = max(
        0,
        _int(inventory.get(SHOOTING_STAR_STARDUST)) - dust,
    )
    for item_name, quantity in rewards.items():
        if quantity > 0:
            inventory[item_name] = _int(inventory.get(item_name)) + quantity
    data["inventory"] = inventory

    state["last_exchange_day"] = reward_day
    state["ore_bonus_ticks_remaining"] = SHOOTING_STAR_ORE_BONUS_TICKS
    state["last_result"] = (
        f"Exchanged {dust} stardust with the Star sprite."
    )
    state = _resolve_event(state, reason="exchanged")
    data["shooting_star"] = sanitize_shooting_star_state_pure(state)
    return data, True, {
        "dust": dust,
        "rewards": rewards,
        "ore_bonus_ticks": SHOOTING_STAR_ORE_BONUS_TICKS,
    }


def shooting_star_view_pure(
    player_data: Mapping[str, Any],
    *,
    has_usable_pickaxe: bool = True,
) -> dict[str, Any]:
    data = ensure_shooting_star_state_pure(player_data)
    answered = _answered_cards(data)
    state = data["shooting_star"]
    event = state["active_event"]
    sprite = bool(event and event.get("sprite_released"))
    mineable = bool(event and not sprite)
    current_size = _int(event.get("current_size")) if mineable else 0
    layer = (
        SHOOTING_STAR_LAYERS_BY_SIZE[current_size]
        if current_size
        else None
    )
    mining_level = _int(data.get("mining_level"), 1, minimum=1)
    dust = _int(
        (data.get("inventory") or {}).get(SHOOTING_STAR_STARDUST)
    )
    reward_day = world_day_index_pure(data)
    tag_available = bool(
        mineable
        and not event.get("player_attempted")
        and event.get("tag_candidate")
        and _int(event.get("crowd_dust_removed")) <= 0
    )
    return {
        "active": mineable,
        "sprite_available": sprite,
        "location": str(event.get("location", "")) if event else "",
        "starting_size": _int(event.get("starting_size")) if event else 0,
        "current_size": current_size,
        "required_level": layer.mining_level if layer else 0,
        "xp_per_dust": layer.xp_per_dust if layer else 0.0,
        "layer_remaining": _int(event.get("layer_remaining")) if event else 0,
        "player_dust_mined": _int(event.get("player_dust_mined")) if event else 0,
        "dust": dust,
        "dust_cap": SHOOTING_STAR_STARDUST_CAP,
        "tag_available": tag_available,
        "can_select": bool(
            mineable and (has_usable_pickaxe or tag_available)
        ),
        "waiting_for_layer": bool(
            mineable and layer and mining_level < layer.mining_level
        ),
        "has_usable_pickaxe": bool(has_usable_pickaxe),
        "next_reviews": (
            0 if event else max(0, _next_slot_card(answered) - answered)
        ),
        "sprite_reviews_remaining": (
            max(0, _int(event.get("sprite_expires_card")) - answered)
            if sprite
            else 0
        ),
        "can_exchange": bool(
            sprite
            and dust > 0
            and _signed_int(state.get("last_exchange_day"), -1) != reward_day
        ),
        "last_exchange_day": _signed_int(
            state.get("last_exchange_day"), -1
        ),
        "ore_bonus_ticks_remaining": _int(
            state.get("ore_bonus_ticks_remaining")
        ),
        "last_result": str(state.get("last_result", "")),
    }
