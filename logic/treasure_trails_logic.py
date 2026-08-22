"""Pure Easy Treasure Trails: clue ownership, step resolution and casket rewards.

The one rule this family must never let anyone copy is clue ownership. A player
may hold one clue scroll across every tier, and the check has to look at the
inventory *and* at the trail already in progress, while deliberately ignoring
caskets so a finished trail can still be opened. It lives here, in
`clue_ownership_reason_pure`, and every other surface — the drop filter, the
panel, the activity handler — asks this module rather than deciding for itself.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.treasure_trails_data import (
    CASKET_ITEMS,
    CLUE_SCROLL_ITEMS,
    EASY_TIER,
    IMPLEMENTED_CLUE_TIERS,
    TREASURE_TRAILS_ACTIVITY_ID,
    TREASURE_TRAILS_EASY_MAX_STEPS,
    TREASURE_TRAILS_EASY_MIN_STEPS,
    TREASURE_TRAILS_EASY_RARE_CHANCE,
    TREASURE_TRAILS_EASY_RARE_REWARDS,
    TREASURE_TRAILS_EASY_REWARD_SPOTS,
    TREASURE_TRAILS_EASY_STANDARD_REWARDS,
    TREASURE_TRAILS_EASY_STEPS,
    TREASURE_TRAILS_SOURCE,
)


TREASURE_TRAILS_STATE_VERSION = 1
TREASURE_TRAILS_BANK_START_LOCK = (
    "Right-click the clue in the Bank and choose Start trail."
)


def _int(value: Any, default: int = 0, *, minimum: int = 0, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(minimum, min(parsed, maximum))


def default_treasure_trails_state_pure() -> dict[str, Any]:
    return {
        "treasure_trail": {},
        # An abandoned trail is only put away, not torn up: the retained trail
        # waits here so starting the same scroll again picks it back up mid-trail.
        "treasure_trail_retained": {},
        "treasure_trails_started": 0,
        "treasure_trails_completed": 0,
        "treasure_trails_caskets_opened": 0,
        "treasure_trails_last_result": "",
    }


def sanitize_treasure_trail_pure(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, Mapping) or not raw:
        return {}
    tier = str(raw.get("tier", ""))
    if tier not in IMPLEMENTED_CLUE_TIERS:
        return {}
    steps = [
        str(step_id)
        for step_id in (raw.get("steps") or ())
        if str(step_id) in TREASURE_TRAILS_EASY_STEPS
    ]
    if not steps:
        return {}
    steps = steps[:TREASURE_TRAILS_EASY_MAX_STEPS]
    return {
        "version": TREASURE_TRAILS_STATE_VERSION,
        "tier": tier,
        "steps": steps,
        "index": _int(raw.get("index"), maximum=len(steps) - 1),
    }


def sanitize_treasure_trails_state_pure(player_data: Mapping[str, Any] | None) -> dict[str, Any]:
    source = dict(player_data or {})
    trail = sanitize_treasure_trail_pure(source.get("treasure_trail"))
    active = source.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if trail and active_id not in {"", TREASURE_TRAILS_ACTIVITY_ID}:
        trail = {}
    return {
        **default_treasure_trails_state_pure(),
        "treasure_trail": trail,
        "treasure_trail_retained": sanitize_treasure_trail_pure(
            source.get("treasure_trail_retained")
        ),
        "treasure_trails_started": _int(source.get("treasure_trails_started")),
        "treasure_trails_completed": _int(source.get("treasure_trails_completed")),
        "treasure_trails_caskets_opened": _int(source.get("treasure_trails_caskets_opened")),
        "treasure_trails_last_result": str(source.get("treasure_trails_last_result", ""))[:500],
    }


def held_clue_tiers_pure(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    """Every tier of clue the player currently holds, trail included.

    Caskets are deliberately absent: the period keeps them outside the ownership
    check so a completed trail opens normally.
    """
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    held = [
        tier
        for tier, item_name in CLUE_SCROLL_ITEMS.items()
        if _int(inventory.get(item_name)) > 0
    ]
    trail = sanitize_treasure_trail_pure(player_data.get("treasure_trail"))
    if trail and trail["tier"] not in held:
        held.append(str(trail["tier"]))
    return tuple(held)


def clue_ownership_reason_pure(player_data: Mapping[str, Any]) -> str:
    """Why no new clue may arrive, or "" when one may.

    "Players will only be able to receive a new clue scroll if they do not
    already have one in their inventory or bank (or in their Kingdom Management
    resources)." AnkiScape has one item container and Miscellania pays its
    collections straight into it, so the inventory is all three places at once.
    """
    held = held_clue_tiers_pure(player_data)
    if not held:
        return ""
    return (
        "You already have a clue scroll: "
        + ", ".join(CLUE_SCROLL_ITEMS[tier] for tier in sorted(held))
    )


def filter_clue_scroll_outputs_pure(
    player_data: Mapping[str, Any], outputs: Mapping[str, Any]
) -> dict[str, int]:
    """Drop the clue out of a reward payload the player may not receive."""
    filtered = {
        str(item): _int(amount) for item, amount in outputs.items() if _int(amount) > 0
    }
    clue_items = {name: tier for tier, name in CLUE_SCROLL_ITEMS.items()}
    offered = [item for item in filtered if item in clue_items]
    if not offered:
        return filtered
    if clue_ownership_reason_pure(player_data):
        for item in offered:
            filtered.pop(item, None)
        return filtered
    # One clue in total. A period drop never offered two at once, so which one
    # survives has no source: AnkiScape keeps the highest tier, the choice that
    # cannot cost the player anything.
    tier_order = list(CLUE_SCROLL_ITEMS.values())
    kept = max(offered, key=tier_order.index)
    for item in offered:
        filtered.pop(item, None)
    filtered[kept] = 1
    return filtered


def clue_refusal_reason_pure(
    player_data: Mapping[str, Any],
    offered_outputs: Mapping[str, Any],
    granted_outputs: Mapping[str, Any],
) -> str:
    """Explain a clue removed by the filter, including one kept from this event."""
    clue_items = tuple(CLUE_SCROLL_ITEMS.values())
    if all(
        _int(granted_outputs.get(item_name)) >= _int(offered_outputs.get(item_name))
        for item_name in clue_items
    ):
        return ""
    ownership_reason = clue_ownership_reason_pure(player_data)
    if ownership_reason:
        return ownership_reason
    kept = [
        item_name
        for item_name in clue_items
        if _int(granted_outputs.get(item_name))
    ]
    return "You already have a clue scroll: " + ", ".join(kept)


def _roll(rng: Callable[[], float], low: int, high: int) -> int:
    span = max(1, high - low + 1)
    return low + min(int(rng() * span), span - 1)


def _pick(rng: Callable[[], float], rows):
    rows = tuple(rows)
    return rows[min(int(rng() * len(rows)), len(rows) - 1)]


def _equipped_items(player_data: Mapping[str, Any]) -> dict[str, str]:
    equipment = player_data.get("equipment")
    if not isinstance(equipment, Mapping):
        return {}
    worn = {}
    for slot, value in equipment.items():
        if isinstance(value, Mapping):
            value = value.get("item_name") or value.get("name")
        if value:
            worn[str(slot)] = str(value)
    return worn


def emote_step_blocked_reason_pure(player_data: Mapping[str, Any], step_id: str) -> str:
    """Why an emote step cannot resolve, or "" when it can.

    The settled flattening drops the emote animation but keeps the gear gate,
    because acquiring the listed equipment is the part of the step the player
    actually plays.
    """
    step = TREASURE_TRAILS_EASY_STEPS.get(str(step_id))
    if step is None or str(step["kind"]) != "emote":
        return ""
    worn = set(_equipped_items(player_data).values())
    if step["bare"]:
        return "Uri wants you wearing nothing at all." if worn else ""
    missing = [item for item in step["equipment"] if item not in worn]
    if missing:
        return "Equip " + ", ".join(missing) + " first."
    return ""


def read_clue_scroll_pure(
    player_data: Mapping[str, Any],
    tier: str = EASY_TIER,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Start a trail from a clue the player is holding."""
    # Shallow on purpose: the trail is rebuilt fresh and inventory is copied
    # before any item moves.
    data = dict(player_data)
    state = sanitize_treasure_trails_state_pure(data)
    data.update(state)
    tier = str(tier)
    if tier not in CLUE_SCROLL_ITEMS:
        return data, False, {"reason": "That is not a clue scroll."}
    if state["treasure_trail"]:
        return data, False, {"reason": "You are already following a Treasure Trail."}
    inventory = data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    if _int(inventory.get(CLUE_SCROLL_ITEMS[tier])) <= 0:
        return data, False, {"reason": f"You have no {CLUE_SCROLL_ITEMS[tier]}."}
    if tier not in IMPLEMENTED_CLUE_TIERS:
        return data, False, {
            "reason": (
                f"{CLUE_SCROLL_ITEMS[tier]} trails are not built yet — only the "
                "easy tier is. Keep the scroll; it will start when they land."
            ),
            "tier_locked": tier,
        }
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if active_id and active_id != TREASURE_TRAILS_ACTIVITY_ID:
        return data, False, {"reason": "Finish the active persistent activity first."}
    retained = state["treasure_trail_retained"]
    resumed = bool(retained) and str(retained["tier"]) == tier
    if resumed:
        trail = dict(retained)
    else:
        draw = rng or (lambda: 0.0)
        # PLACEHOLDER(treasure_trails.easy_step_count_distribution): the period
        # page states the 1-to-5 range but not the shape inside it, and Darkan's
        # 1 + random(3) cannot reach five, so it cannot settle this either.
        length = _roll(
            draw, TREASURE_TRAILS_EASY_MIN_STEPS, TREASURE_TRAILS_EASY_MAX_STEPS
        )
        pool = list(TREASURE_TRAILS_EASY_STEPS)
        steps = []
        for _index in range(length):
            # Darkan draws each clue detail uniformly from the rows at or below
            # the trail's difficulty, so a uniform draw over the easy pool is
            # sourced.
            steps.append(str(_pick(draw, pool)))
        trail = {
            "version": TREASURE_TRAILS_STATE_VERSION,
            "tier": tier,
            "steps": steps,
            "index": 0,
        }
    steps = list(trail["steps"])
    data["treasure_trail"] = trail
    # A retained trail of another tier belongs to a scroll the player no longer
    # holds, so either way nothing is left waiting once a trail is under way.
    data["treasure_trail_retained"] = {}
    data["activity_session"] = {"active_id": TREASURE_TRAILS_ACTIVITY_ID}
    data["current_utility"] = TREASURE_TRAILS_ACTIVITY_ID
    if not resumed:
        data["treasure_trails_started"] = int(state["treasure_trails_started"]) + 1
    message = (
        f"Treasure Trail resumed · {trail['index']}/{len(steps)} solved"
        if resumed
        else (
            f"Treasure Trail started · {len(steps)} clue"
            f"{'s' if len(steps) != 1 else ''} to follow"
        )
    )
    data["treasure_trails_last_result"] = message
    return data, True, {"message": message, "steps": tuple(steps)}


def apply_treasure_trail_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Resolve one step of the active trail."""
    # Shallow on purpose: see read_clue_scroll_pure.
    data = dict(player_data)
    state = sanitize_treasure_trails_state_pure(data)
    trail = state["treasure_trail"]
    active = data.get("activity_session")
    active_id = str(active.get("active_id", "")) if isinstance(active, Mapping) else ""
    if not trail or active_id != TREASURE_TRAILS_ACTIVITY_ID:
        return data, False, {
            "reason": "Start a trail from the clue scroll in the Bank before following it."
        }
    data.update(state)
    step_id = trail["steps"][int(trail["index"])]
    step = TREASURE_TRAILS_EASY_STEPS[step_id]
    blocked = emote_step_blocked_reason_pure(data, step_id)
    if blocked:
        data["treasure_trails_last_result"] = f"{step['text']} · {blocked}"
        return data, True, {
            "terminal": False,
            "blocked": True,
            "step": dict(step),
            "message": data["treasure_trails_last_result"],
        }

    trail = dict(trail)
    trail["index"] = int(trail["index"]) + 1
    if trail["index"] < len(trail["steps"]):
        data["treasure_trail"] = trail
        message = (
            f"You've found another clue! · "
            f"{trail['index']}/{len(trail['steps'])} solved"
        )
        data["treasure_trails_last_result"] = message
        return data, True, {
            "terminal": False,
            "blocked": False,
            "step": dict(step),
            "message": message,
        }

    inventory = copy.deepcopy(dict(data.get("inventory") or {}))
    clue_item = CLUE_SCROLL_ITEMS[str(trail["tier"])]
    held = _int(inventory.get(clue_item))
    if held <= 1:
        inventory.pop(clue_item, None)
    else:
        inventory[clue_item] = held - 1
    casket = CASKET_ITEMS[str(trail["tier"])]
    inventory[casket] = _int(inventory.get(casket)) + 1
    data["inventory"] = inventory
    data["treasure_trail"] = {}
    data["activity_session"] = {"active_id": ""}
    data["treasure_trails_completed"] = int(state["treasure_trails_completed"]) + 1
    message = f"Well done! You've completed the Treasure Trail · {casket} received"
    data["treasure_trails_last_result"] = message
    return data, True, {
        "terminal": True,
        "blocked": False,
        "step": dict(step),
        "casket": casket,
        "message": message,
    }


def abandon_treasure_trail_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Stop following the trail without destroying the scroll."""
    # Shallow on purpose: see read_clue_scroll_pure.
    data = dict(player_data)
    state = sanitize_treasure_trails_state_pure(data)
    if not state["treasure_trail"]:
        return data, False, {"reason": "You are not following a Treasure Trail."}
    data.update(state)
    data["treasure_trail_retained"] = dict(state["treasure_trail"])
    data["treasure_trail"] = {}
    data["activity_session"] = {"active_id": ""}
    message = "You put the clue scroll away. Start it again from the Bank to pick the trail back up."
    data["treasure_trails_last_result"] = message
    return data, True, {"message": message}


def open_casket_pure(
    player_data: Mapping[str, Any],
    tier: str = EASY_TIER,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Roll the casket. Deliberately outside the clue-ownership check."""
    # Shallow on purpose: see read_clue_scroll_pure.
    data = dict(player_data)
    state = sanitize_treasure_trails_state_pure(data)
    data.update(state)
    tier = str(tier)
    if tier not in IMPLEMENTED_CLUE_TIERS:
        return data, False, {"reason": f"{tier.title()} caskets are not built yet."}
    casket = CASKET_ITEMS[tier]
    inventory = copy.deepcopy(dict(data.get("inventory") or {}))
    if _int(inventory.get(casket)) <= 0:
        return data, False, {"reason": f"You have no {casket}."}
    held = _int(inventory.get(casket))
    if held <= 1:
        inventory.pop(casket, None)
    else:
        inventory[casket] = held - 1

    draw = rng or (lambda: 0.0)
    spots = _roll(draw, *TREASURE_TRAILS_EASY_REWARD_SPOTS)
    rare_numerator, rare_denominator = TREASURE_TRAILS_EASY_RARE_CHANCE
    rewards: dict[str, int] = {}
    rare_hits = 0
    for _spot in range(spots):
        rare = draw() * rare_denominator < rare_numerator
        table = TREASURE_TRAILS_EASY_RARE_REWARDS if rare else TREASURE_TRAILS_EASY_STANDARD_REWARDS
        rare_hits += 1 if rare else 0
        row = _pick(draw, table)
        quantity = _roll(draw, int(row["minimum"]), int(row["maximum"]))
        rewards[str(row["item"])] = rewards.get(str(row["item"]), 0) + quantity
    for item_name, quantity in rewards.items():
        inventory[item_name] = _int(inventory.get(item_name)) + quantity
    data["inventory"] = inventory
    data["treasure_trails_caskets_opened"] = int(state["treasure_trails_caskets_opened"]) + 1
    message = "The casket held " + ", ".join(
        f"{quantity:,} {item_name}" for item_name, quantity in sorted(rewards.items())
    )
    data["treasure_trails_last_result"] = message
    return data, True, {
        "message": message,
        "rewards": dict(rewards),
        "reward_spots": spots,
        "rare_hits": rare_hits,
    }


def apply_treasure_trails_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    tier = str(body.get("tier", EASY_TIER)) or EASY_TIER
    if action_id == "start_from_bank":
        return read_clue_scroll_pure(player_data, tier, rng)
    if action_id == "read":
        return dict(player_data), False, {"reason": TREASURE_TRAILS_BANK_START_LOCK}
    if action_id == "abandon":
        return abandon_treasure_trail_pure(player_data)
    if action_id == "open_casket":
        return open_casket_pure(player_data, tier, rng)
    # Shallow: an unrecognised action changes nothing, and the caller discards
    # this save because ok is False.
    return dict(player_data), False, {"reason": "Unknown Treasure Trails command."}


def treasure_trails_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """Everything a panel needs, with every rule already decided here."""
    state = sanitize_treasure_trails_state_pure(player_data)
    trail = state["treasure_trail"]
    inventory = player_data.get("inventory")
    inventory = inventory if isinstance(inventory, Mapping) else {}
    active_session = player_data.get("activity_session")
    active_id = (
        str(active_session.get("active_id", ""))
        if isinstance(active_session, Mapping)
        else ""
    )
    session_available = active_id in {"", TREASURE_TRAILS_ACTIVITY_ID}
    step = None
    if trail:
        step_id = trail["steps"][int(trail["index"])]
        row = TREASURE_TRAILS_EASY_STEPS[step_id]
        step = {
            **row,
            "number": int(trail["index"]) + 1,
            "total": len(trail["steps"]),
            "blocked_reason": emote_step_blocked_reason_pure(player_data, step_id),
        }
    clue_rows = []
    for tier, item_name in CLUE_SCROLL_ITEMS.items():
        held = _int(inventory.get(item_name))
        if held <= 0:
            continue
        clue_rows.append(
            {
                "tier": tier,
                "item": item_name,
                "implemented": tier in IMPLEMENTED_CLUE_TIERS,
                "locked_reason": ""
                if tier in IMPLEMENTED_CLUE_TIERS
                else (
                    f"{item_name} trails are not built yet — only the easy tier is. "
                    "The scroll keeps, and it still blocks a new clue from dropping."
                ),
                "can_read": False,
                "can_start_from_bank": (
                    tier in IMPLEMENTED_CLUE_TIERS and not trail and session_available
                ),
                "bank_start_locked_reason": (
                    ""
                    if tier in IMPLEMENTED_CLUE_TIERS and not trail and session_available
                    else (
                        "Finish the active persistent activity first."
                        if not session_available
                        else "You are already following a Treasure Trail."
                    )
                ),
            }
        )
    ownership_reason = clue_ownership_reason_pure(player_data)
    return {
        **state,
        "active": bool(trail),
        "step": step,
        "clue_rows": tuple(clue_rows),
        "activity_start_locked_reason": (
            TREASURE_TRAILS_BANK_START_LOCK
            if any(row["implemented"] for row in clue_rows) and not trail
            else ""
        ),
        # The single ownership rule, published so no panel re-derives it.
        "can_receive_clue": not ownership_reason,
        "clue_blocked_reason": ownership_reason,
        "caskets": tuple(
            {
                "tier": tier,
                "item": item_name,
                "held": _int(inventory.get(item_name)),
                "implemented": tier in IMPLEMENTED_CLUE_TIERS,
            }
            for tier, item_name in CASKET_ITEMS.items()
            if _int(inventory.get(item_name)) > 0
        ),
        "implemented_tiers": IMPLEMENTED_CLUE_TIERS,
        "source": TREASURE_TRAILS_SOURCE,
    }
