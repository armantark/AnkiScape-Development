"""Pure review-clock lifecycle and finite-session logic for Evil Trees."""

from __future__ import annotations

import copy
import math
from typing import Any, Mapping, Sequence

from ..data.evil_tree_data import (
    EVIL_TREE_ACTIVE_REVIEWS,
    EVIL_TREE_DAILY_INTERACTIONS,
    EVIL_TREE_KINDLING,
    EVIL_TREE_LOCATIONS,
    EVIL_TREE_REVIEW_DAY,
    EVIL_TREE_REWARD_MINIMUM_SHARE,
    EVIL_TREE_SPAWN_REVIEWS,
    EVIL_TREE_TIERS,
    EVIL_TREE_TIERS_BY_ID,
)


EVIL_TREE_STATE_VERSION = 1
EVIL_TREE_PHASES = ("nurture", "prepare", "fell")


def _int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, parsed)


def _roll(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    if not math.isfinite(parsed):
        return 0.0
    return max(0.0, min(parsed, math.nextafter(1.0, 0.0)))


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    if not isinstance(clock, Mapping):
        return 0
    return _int(clock.get("answered_cards"))


def default_evil_tree_state_pure() -> dict[str, Any]:
    return {
        "version": EVIL_TREE_STATE_VERSION,
        "last_world_card": 0,
        "next_spawn_card": EVIL_TREE_SPAWN_REVIEWS,
        "active_event": {},
        "session": {},
        "participation_day": 0,
        "participations_today": 0,
        "participated_event_ids": [],
        "blessing_reviews_remaining": 0,
        "blessing_tier": "",
        "blessing_granted_card": 0,
        "last_result": "",
        "event_log": [],
    }


def sanitize_evil_tree_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_evil_tree_state_pure()
    source = raw if isinstance(raw, Mapping) else {}

    event: dict[str, Any] = {}
    raw_event = source.get("active_event")
    if isinstance(raw_event, Mapping):
        tier_id = str(raw_event.get("tier_id", ""))
        location = str(raw_event.get("location", ""))
        event_id = str(raw_event.get("event_id", ""))
        remaining = _int(raw_event.get("reviews_remaining"))
        if (
            tier_id in EVIL_TREE_TIERS_BY_ID
            and location in EVIL_TREE_LOCATIONS
            and event_id
            and remaining > 0
        ):
            event = {
                "event_id": event_id,
                "tier_id": tier_id,
                "location": location,
                "spawn_card": _int(raw_event.get("spawn_card")),
                "reviews_remaining": min(remaining, EVIL_TREE_ACTIVE_REVIEWS),
            }

    session: dict[str, Any] = {}
    raw_session = source.get("session")
    if isinstance(raw_session, Mapping) and event:
        phase = str(raw_session.get("phase", ""))
        mode = str(raw_session.get("mode", ""))
        if (
            str(raw_session.get("event_id", "")) == event["event_id"]
            and phase in EVIL_TREE_PHASES
            and mode in {"full", "nurture_only"}
        ):
            session = {
                "event_id": event["event_id"],
                "tier_id": event["tier_id"],
                "phase": phase,
                "mode": mode,
                "contribution_percent": min(
                    100, _int(raw_session.get("contribution_percent"))
                ),
            }

    day = _int(source.get("participation_day"))
    participated = source.get("participated_event_ids")
    participated_ids = (
        [str(value) for value in participated if isinstance(value, str) and value]
        if isinstance(participated, (list, tuple))
        else []
    )
    event_log = source.get("event_log")
    return {
        **defaults,
        "last_world_card": _int(source.get("last_world_card")),
        "next_spawn_card": max(
            1,
            _int(
                source.get("next_spawn_card"),
                EVIL_TREE_SPAWN_REVIEWS,
                minimum=1,
            ),
        ),
        "active_event": event,
        "session": session,
        "participation_day": day,
        "participations_today": min(
            EVIL_TREE_DAILY_INTERACTIONS,
            _int(source.get("participations_today")),
        ),
        "participated_event_ids": list(dict.fromkeys(participated_ids))[-8:],
        "blessing_reviews_remaining": min(
            5, _int(source.get("blessing_reviews_remaining"))
        ),
        "blessing_tier": (
            str(source.get("blessing_tier", ""))
            if str(source.get("blessing_tier", "")) in EVIL_TREE_TIERS_BY_ID
            else ""
        ),
        "blessing_granted_card": _int(source.get("blessing_granted_card")),
        "last_result": str(source.get("last_result", ""))[:240],
        "event_log": (
            [dict(row) for row in event_log if isinstance(row, Mapping)][-20:]
            if isinstance(event_log, list)
            else []
        ),
    }


def ensure_evil_tree_state_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    # Shallow on purpose: sanitize_ below rebuilds the one key this owns, and a
    # whole-save deep copy here cost 2.07 ms on every review.
    data = dict(player_data)
    data["evil_tree"] = sanitize_evil_tree_state_pure(data.get("evil_tree"))
    return data


def evil_tree_spawn_due_pure(player_data: Mapping[str, Any]) -> bool:
    data = ensure_evil_tree_state_pure(player_data)
    state = data["evil_tree"]
    return (
        not state["active_event"]
        and _answered_cards(data) >= int(state["next_spawn_card"])
    )


def advance_evil_tree_world_clock_pure(
    player_data: Mapping[str, Any],
    *,
    tier_roll: Any = 0.0,
    location_roll: Any = 0.0,
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    """Advance expiry, daily allowance, blessing, and the next event.

    The host calls this once after every answered card. No wall-clock state is
    read, and a newly earned blessing is not consumed on its grant card.
    """

    data = ensure_evil_tree_state_pure(player_data)
    state = dict(data["evil_tree"])
    answered = _answered_cards(data)
    previous = min(answered, int(state["last_world_card"]))
    elapsed = answered - previous
    events: list[dict[str, Any]] = []

    day = answered // EVIL_TREE_REVIEW_DAY
    if day != int(state["participation_day"]):
        state["participation_day"] = day
        state["participations_today"] = 0
        state["participated_event_ids"] = []

    event = dict(state["active_event"])
    if event and elapsed > 0:
        event["reviews_remaining"] = max(
            0, int(event["reviews_remaining"]) - elapsed
        )
        if event["reviews_remaining"] <= 0:
            expired_id = event["event_id"]
            if (
                state["session"]
                and state["session"].get("event_id") == expired_id
            ):
                state["session"] = {}
                state["last_result"] = "The Evil Tree withered before the session finished."
            state["active_event"] = {}
            state["next_spawn_card"] = answered + EVIL_TREE_SPAWN_REVIEWS
            events.append({"kind": "expired", "event_id": expired_id})
        else:
            state["active_event"] = event

    blessing_elapsed = max(
        0,
        answered
        - max(previous, int(state.get("blessing_granted_card", 0) or 0)),
    )
    if blessing_elapsed and int(state["blessing_reviews_remaining"]) > 0:
        remaining = max(
            0, int(state["blessing_reviews_remaining"]) - blessing_elapsed
        )
        state["blessing_reviews_remaining"] = remaining
        if remaining <= 0:
            state["blessing_tier"] = ""
            state["blessing_granted_card"] = 0
            events.append({"kind": "blessing_expired"})

    if (
        not state["active_event"]
        and answered >= int(state["next_spawn_card"])
    ):
        tier_index = min(
            len(EVIL_TREE_TIERS) - 1,
            int(_roll(tier_roll) * len(EVIL_TREE_TIERS)),
        )
        location_index = min(
            len(EVIL_TREE_LOCATIONS) - 1,
            int(_roll(location_roll) * len(EVIL_TREE_LOCATIONS)),
        )
        tier = EVIL_TREE_TIERS[tier_index]
        event = {
            "event_id": f"evil-tree-{answered}",
            "tier_id": tier.id,
            "location": EVIL_TREE_LOCATIONS[location_index],
            "spawn_card": answered,
            "reviews_remaining": EVIL_TREE_ACTIVE_REVIEWS,
        }
        state["active_event"] = event
        events.append({"kind": "spawned", **event})

    state["last_world_card"] = answered
    state["event_log"] = (
        list(state.get("event_log", [])) + events
    )[-20:]
    data["evil_tree"] = sanitize_evil_tree_state_pure(state)
    return data, tuple(events)


def evil_tree_entry_mode_pure(
    player_data: Mapping[str, Any],
    *,
    has_usable_hatchet: bool,
) -> tuple[str, tuple[str, ...]]:
    data = ensure_evil_tree_state_pure(player_data)
    state = data["evil_tree"]
    event = state["active_event"]
    if not event:
        return "locked", ("No Evil Tree is active.",)
    if event["event_id"] in state["participated_event_ids"]:
        return "locked", ("Already interacted with this Evil Tree.",)
    if int(state["participations_today"]) >= EVIL_TREE_DAILY_INTERACTIONS:
        return "locked", ("Two Evil Tree interactions used this review day.",)

    tier = EVIL_TREE_TIERS_BY_ID[event["tier_id"]]
    farming = _int(data.get("farming_level"), 1, minimum=1)
    woodcutting = _int(data.get("woodcutting_level"), 1, minimum=1)
    firemaking = _int(data.get("firemaking_level"), 1, minimum=1)
    if farming < tier.farming_level:
        return "locked", (
            f"Requires {tier.farming_level} Farming to nurture.",
        )

    full_reasons: list[str] = []
    if woodcutting < tier.woodcutting_level:
        full_reasons.append(f"{tier.woodcutting_level} Woodcutting")
    if firemaking < tier.firemaking_level:
        full_reasons.append(f"{tier.firemaking_level} Firemaking")
    if not has_usable_hatchet:
        full_reasons.append("a usable hatchet")
    if int(event["reviews_remaining"]) < len(EVIL_TREE_PHASES):
        full_reasons.append("three remaining event reviews")
    if full_reasons:
        return "nurture_only", tuple(full_reasons)
    return "full", ()


def evil_tree_view_pure(
    player_data: Mapping[str, Any],
    *,
    has_usable_hatchet: bool,
) -> dict[str, Any]:
    data = ensure_evil_tree_state_pure(player_data)
    state = data["evil_tree"]
    event = state["active_event"]
    session = state["session"]
    answered = _answered_cards(data)
    if not event:
        return {
            "active": False,
            "session_active": False,
            "next_reviews": max(0, int(state["next_spawn_card"]) - answered),
            "participations_today": int(state["participations_today"]),
            "interaction_limit": EVIL_TREE_DAILY_INTERACTIONS,
            "blessing_reviews_remaining": int(
                state["blessing_reviews_remaining"]
            ),
            "blessing_tier": str(state["blessing_tier"]),
            "last_result": str(state["last_result"]),
        }

    tier = EVIL_TREE_TIERS_BY_ID[event["tier_id"]]
    mode, reasons = evil_tree_entry_mode_pure(
        data, has_usable_hatchet=has_usable_hatchet
    )
    if session:
        mode = str(session["mode"])
        reasons = ()
    return {
        "active": True,
        "event_id": event["event_id"],
        "tier_id": tier.id,
        "tier_name": tier.display_name,
        "location": event["location"],
        "reviews_remaining": int(event["reviews_remaining"]),
        "requirements": {
            "Farming": tier.farming_level,
            "Woodcutting": tier.woodcutting_level,
            "Firemaking": tier.firemaking_level,
        },
        "entry_mode": mode,
        "entry_reasons": reasons,
        "session_active": bool(session),
        "phase": str(session.get("phase", "")),
        "contribution_percent": int(
            session.get("contribution_percent", 0) or 0
        ),
        "participations_today": int(state["participations_today"]),
        "interaction_limit": EVIL_TREE_DAILY_INTERACTIONS,
        "blessing_reviews_remaining": int(
            state["blessing_reviews_remaining"]
        ),
        "blessing_tier": str(state["blessing_tier"]),
        "last_result": str(state["last_result"]),
    }


def _add_xp(data: dict[str, Any], key: str, amount: float) -> None:
    try:
        current = float(data.get(key, 0.0) or 0.0)
    except (TypeError, ValueError, OverflowError):
        current = 0.0
    data[key] = max(0.0, current) + float(amount)


def _bounded_reward_amount(maximum: int, roll: Any) -> int:
    share = EVIL_TREE_REWARD_MINIMUM_SHARE + (
        1.0 - EVIL_TREE_REWARD_MINIMUM_SHARE
    ) * _roll(roll)
    return max(1, min(maximum, int(math.floor(maximum * share))))


def apply_evil_tree_review_pure(
    player_data: Mapping[str, Any],
    *,
    has_usable_hatchet: bool,
    reward_rolls: Sequence[Any] = (),
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Perform exactly one Nurture, Prepare, or Fell phase action."""

    data = ensure_evil_tree_state_pure(player_data)
    state = dict(data["evil_tree"])
    event = dict(state["active_event"])
    if not event:
        return data, False, {
            "reason": (
                str(state.get("last_result", "") or "")
                or "No Evil Tree is active."
            )
        }

    session = dict(state["session"])
    started = False
    if not session:
        mode, reasons = evil_tree_entry_mode_pure(
            data, has_usable_hatchet=has_usable_hatchet
        )
        if mode == "locked":
            return data, False, {"reason": reasons[0] if reasons else "Unavailable."}
        session = {
            "event_id": event["event_id"],
            "tier_id": event["tier_id"],
            "phase": "nurture",
            "mode": mode,
            "contribution_percent": 0,
        }
        state["participations_today"] = min(
            EVIL_TREE_DAILY_INTERACTIONS,
            int(state["participations_today"]) + 1,
        )
        state["participated_event_ids"] = (
            list(state["participated_event_ids"]) + [event["event_id"]]
        )[-8:]
        started = True

    tier = EVIL_TREE_TIERS_BY_ID[event["tier_id"]]
    phase = session["phase"]
    result: dict[str, Any] = {
        "phase": phase,
        "tier_id": tier.id,
        "tier_name": tier.display_name,
        "started": started,
        "mode": session["mode"],
        "completed": False,
        "partial": False,
        "xp": {},
        "outputs": {},
    }

    if phase == "nurture":
        _add_xp(data, "farming_exp", tier.nurture_xp)
        result["xp"] = {"Farming": tier.nurture_xp}
        session["contribution_percent"] = 33
        if session["mode"] == "nurture_only":
            result["completed"] = True
            result["partial"] = True
            state["session"] = {}
            state["last_result"] = (
                f"Nurtured {tier.display_name}; the remaining skill gates "
                "prevented felling."
            )
            data["current_utility"] = "bankstanding"
        else:
            session["phase"] = "prepare"
            state["session"] = session
            state["last_result"] = f"Nurtured {tier.display_name}."

    elif phase == "prepare":
        inventory = dict(data.get("inventory", {}) or {})
        inventory[EVIL_TREE_KINDLING] = (
            _int(inventory.get(EVIL_TREE_KINDLING)) + 1
        )
        data["inventory"] = inventory
        _add_xp(data, "woodcutting_exp", tier.root_xp)
        result["xp"] = {"Woodcutting": tier.root_xp}
        result["outputs"] = {EVIL_TREE_KINDLING: 1}
        session["phase"] = "fell"
        session["contribution_percent"] = 67
        state["session"] = session
        state["last_result"] = (
            f"Chopped an evil root and gathered {EVIL_TREE_KINDLING}."
        )

    elif phase == "fell":
        inventory = dict(data.get("inventory", {}) or {})
        if _int(inventory.get(EVIL_TREE_KINDLING)) <= 0:
            return data, False, {
                "reason": f"{EVIL_TREE_KINDLING} is required to finish the tree."
            }
        inventory[EVIL_TREE_KINDLING] = (
            _int(inventory.get(EVIL_TREE_KINDLING)) - 1
        )

        rolls = [_roll(value) for value in reward_rolls]
        while len(rolls) < 4:
            rolls.append(0.0)
        log_options = tier.max_logs
        log_index = min(len(log_options) - 1, int(rolls[0] * len(log_options)))
        log_name, max_logs = log_options[log_index]
        logs = _bounded_reward_amount(max_logs, rolls[1])
        coins = _bounded_reward_amount(tier.max_coins, rolls[2])
        ordinary_item = (
            tier.reward_seed if rolls[3] < 0.5 else "Bird's nest (seeds)"
        )

        inventory[log_name] = _int(inventory.get(log_name)) + logs
        inventory["Coins"] = _int(inventory.get("Coins")) + coins
        inventory[ordinary_item] = _int(inventory.get(ordinary_item)) + 1
        data["inventory"] = inventory
        _add_xp(data, "woodcutting_exp", tier.tree_xp)
        _add_xp(data, "firemaking_exp", tier.firemaking_xp)
        result["xp"] = {
            "Woodcutting": tier.tree_xp,
            "Firemaking": tier.firemaking_xp,
        }
        result["outputs"] = {
            log_name: logs,
            "Coins": coins,
            ordinary_item: 1,
        }
        result["completed"] = True
        result["contribution_percent"] = 100
        result["blessing_reviews"] = tier.blessing_reviews

        answered = _answered_cards(data)
        state["session"] = {}
        state["active_event"] = {}
        state["next_spawn_card"] = answered + EVIL_TREE_SPAWN_REVIEWS
        state["blessing_reviews_remaining"] = max(
            int(state["blessing_reviews_remaining"]),
            tier.blessing_reviews,
        )
        state["blessing_tier"] = tier.id
        state["blessing_granted_card"] = answered
        state["last_result"] = (
            f"Felled {tier.display_name}: {logs} {log_name}, "
            f"{coins:,} coins, and {ordinary_item}."
        )
        data["current_utility"] = "bankstanding"

    data["evil_tree"] = sanitize_evil_tree_state_pure(state)
    return data, True, result
