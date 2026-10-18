"""Pure Gnome Restaurant delivery jobs, punctuality, tips, and the reward token.

One productive review delivers the outstanding order and takes the next job, which
is the cadence settled in `activity-cadence-reconciliation-2026-07-18.md`. Under the
2026-10-14 owner ruling, Again pauses. A successful answer on another target spends
its card's time budget from the persistent order's window, which affects only tip
quality; the window counts game ticks, so it lasts the same play time at every speed.
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from typing import Any

from ..data.gnome_restaurant_data import (
    GNOME_COCKTAIL_ITEMS,
    GNOME_COCKTAIL_TARGET_IDS,
    GNOME_DISH_ITEMS,
    GNOME_DISH_TARGET_IDS,
    GNOME_RESTAURANT_ACTIVITY_ID,
    GNOME_RESTAURANT_BOX_ITEM,
    GNOME_RESTAURANT_CUSTOMERS_BY_ID,
    GNOME_RESTAURANT_DIFFICULTIES,
    GNOME_RESTAURANT_EASY_MINUTES,
    GNOME_RESTAURANT_EASY_POINTS,
    GNOME_RESTAURANT_EASY_TIP_COINS,
    GNOME_RESTAURANT_GOOD_TIP_GROUP,
    GNOME_RESTAURANT_HARD_DECLINE_WAIT_MINUTES,
    GNOME_RESTAURANT_HARD_MINUTES,
    GNOME_RESTAURANT_HARD_POINTS,
    GNOME_RESTAURANT_REQUEST_ITEMS,
    GNOME_RESTAURANT_STARTING_DOUGH,
    GNOME_RESTAURANT_TOKEN_COCKTAIL_WEIGHT,
    GNOME_RESTAURANT_TOKEN_DISH_WEIGHT,
    GNOME_RESTAURANT_TOKEN_ITEM,
    GNOME_RESTAURANT_TOKEN_MEAL_CAP,
    GNOME_RESTAURANT_TOKEN_POINTS,
    GNOME_RESTAURANT_TUTORIAL_COCKTAILS,
    GNOME_RESTAURANT_TUTORIAL_DISHES,
    gnome_restaurant_customers_for_pure,
    gnome_restaurant_tips_for_pure,
)
from .pace.short_timers import (
    STEP_TICKS,
    TICKS_PER_SOURCE_MINUTE,
    minutes_for_ticks_pure,
    steps_for_ticks_pure,
)


GNOME_RESTAURANT_STATE_VERSION = 1
_VALID_DIFFICULTIES = frozenset(row[0] for row in GNOME_RESTAURANT_DIFFICULTIES)
_LIMIT_MINUTES = {
    "easy": GNOME_RESTAURANT_EASY_MINUTES,
    "hard": GNOME_RESTAURANT_HARD_MINUTES,
}
_LIMIT_TICKS = {
    difficulty: minutes * TICKS_PER_SOURCE_MINUTE
    for difficulty, minutes in _LIMIT_MINUTES.items()
}
_HARD_DECLINE_WAIT_TICKS = GNOME_RESTAURANT_HARD_DECLINE_WAIT_MINUTES * TICKS_PER_SOURCE_MINUTE
_DELIVERY_POINTS = {
    "easy": GNOME_RESTAURANT_EASY_POINTS,
    "hard": GNOME_RESTAURANT_HARD_POINTS,
}


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _roll(rng: Callable[[], float] | None) -> float:
    try:
        return max(0.0, min(float((rng or (lambda: 0.0))()), 0.999999999))
    except (TypeError, ValueError, OverflowError):
        return 0.0


def _pick(rows: tuple[Any, ...], rng: Callable[[], float] | None) -> Any:
    return rows[int(_roll(rng) * len(rows))] if rows else None


def _range_roll(low: int, high: int, rng: Callable[[], float] | None) -> int:
    return low + int(_roll(rng) * (high - low + 1))


def _inventory(data: Mapping[str, Any]) -> Mapping[str, Any]:
    value = data.get("inventory")
    return value if isinstance(value, Mapping) else {}


def _grant_item(data: dict[str, Any], item: str, amount: int = 1) -> None:
    inventory = data.get("inventory")
    if not isinstance(inventory, dict):
        inventory = {}
        data["inventory"] = inventory
    inventory[item] = _int(inventory.get(item)) + amount


def _completed_quests(data: Mapping[str, Any]) -> frozenset[str]:
    quests = data.get("quests")
    if not isinstance(quests, Mapping):
        return frozenset()
    return frozenset(
        str(quest_id)
        for quest_id, row in quests.items()
        if isinstance(row, Mapping) and bool(row.get("completed"))
    )


def _cooked_target_ids(data: Mapping[str, Any]) -> frozenset[str]:
    """Cooking targets the player has actually completed at least once.

    The durable production ledger is the only entry gate: ordinary Cooking done
    long before the player walks into the Grand Tree still counts, and the
    Activity never duplicates a recipe.
    """
    telemetry = data.get("action_telemetry")
    actions = telemetry.get("actions") if isinstance(telemetry, Mapping) else None
    if not isinstance(actions, Mapping):
        return frozenset()
    return frozenset(
        str(key).split(":", 1)[1]
        for key, row in actions.items()
        if str(key).startswith("cooking:")
        and isinstance(row, Mapping)
        and _int(row.get("successes")) > 0
    )


def default_gnome_restaurant_state_pure() -> dict[str, Any]:
    return {
        "version": GNOME_RESTAURANT_STATE_VERSION,
        "service_open": False,
        "difficulty_policy": "easy",
        "order": {},
        "points": 0,
        "deliveries": {"easy": 0, "hard": 0},
        "token_claimed": False,
        "token_meals": 0,
        "hard_decline_ticks_left": 0,
        "tips_received": {},
        "last_result": "",
    }


def _order_ticks_left(order_raw: Mapping[str, Any], difficulty: str) -> int:
    if "ticks_left" in order_raw or "minutes_left" not in order_raw:
        return _int(order_raw.get("ticks_left"), _LIMIT_TICKS[difficulty])
    # An order saved before ticks counted its window in whole source minutes.
    return _int(order_raw.get("minutes_left")) * TICKS_PER_SOURCE_MINUTE


def sanitize_gnome_restaurant_state_pure(raw: Any) -> dict[str, Any]:
    defaults = default_gnome_restaurant_state_pure()
    source = raw if isinstance(raw, Mapping) else {}
    policy = str(source.get("difficulty_policy", "easy"))
    order_raw = source.get("order") if isinstance(source.get("order"), Mapping) else {}
    deliveries_raw = (
        source.get("deliveries") if isinstance(source.get("deliveries"), Mapping) else {}
    )
    tips_raw = (
        source.get("tips_received") if isinstance(source.get("tips_received"), Mapping) else {}
    )
    difficulty = str(order_raw.get("difficulty", ""))
    customer = str(order_raw.get("customer", ""))
    item = str(order_raw.get("item", ""))
    order: dict[str, Any] = {}
    if (
        difficulty in _VALID_DIFFICULTIES
        and customer in GNOME_RESTAURANT_CUSTOMERS_BY_ID
        and GNOME_RESTAURANT_CUSTOMERS_BY_ID[customer].difficulty == difficulty
        and item in GNOME_RESTAURANT_REQUEST_ITEMS
    ):
        order = {
            "difficulty": difficulty,
            "customer": customer,
            "item": item,
            "ticks_left": min(_LIMIT_TICKS[difficulty], _order_ticks_left(order_raw, difficulty)),
        }
    return {
        **defaults,
        "service_open": bool(source.get("service_open", False)),
        "difficulty_policy": policy if policy in _VALID_DIFFICULTIES else "easy",
        "order": order,
        "points": _int(source.get("points")),
        "deliveries": {key: _int(deliveries_raw.get(key)) for key in defaults["deliveries"]},
        "token_claimed": bool(source.get("token_claimed", False)),
        "token_meals": min(
            GNOME_RESTAURANT_TOKEN_MEAL_CAP, _int(source.get("token_meals"))
        ),
        # A wait saved as a ready card is forgiven: it spanned at most one card.
        "hard_decline_ticks_left": min(
            _HARD_DECLINE_WAIT_TICKS, _int(source.get("hard_decline_ticks_left"))
        ),
        "tips_received": {
            str(tip_id): _int(count) for tip_id, count in tips_raw.items()
        },
        "last_result": str(source.get("last_result", ""))[:500],
    }


def gnome_restaurant_training_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    """The one-time tutorial checklist, read from durable Cooking production."""
    cooked = _cooked_target_ids(player_data)
    dishes = tuple(
        target_id for target_id in GNOME_DISH_TARGET_IDS if target_id in cooked
    )
    cocktails = tuple(
        target_id for target_id in GNOME_COCKTAIL_TARGET_IDS if target_id in cooked
    )
    return {
        "dishes_prepared": len(dishes),
        "cocktails_prepared": len(cocktails),
        "dishes_required": GNOME_RESTAURANT_TUTORIAL_DISHES,
        "cocktails_required": GNOME_RESTAURANT_TUTORIAL_COCKTAILS,
        "complete": (
            len(dishes) >= GNOME_RESTAURANT_TUTORIAL_DISHES
            and len(cocktails) >= GNOME_RESTAURANT_TUTORIAL_COCKTAILS
        ),
    }


def _entry_reasons(player_data: Mapping[str, Any], state: Mapping[str, Any]) -> tuple[str, ...]:
    training = gnome_restaurant_training_pure(player_data)
    reasons = []
    if not training["complete"]:
        reasons.append(
            f"Prepare {training['dishes_required']} gnome dishes "
            f"({training['dishes_prepared']} done) and "
            f"{training['cocktails_required']} cocktails "
            f"({training['cocktails_prepared']} done)"
        )
    session = player_data.get("activity_session")
    active_id = (
        str(session.get("active_id", "")) if isinstance(session, Mapping) else ""
    )
    if active_id and active_id != GNOME_RESTAURANT_ACTIVITY_ID:
        reasons.append("Finish the active persistent activity")
    return tuple(reasons)


def _accept_reason(
    player_data: Mapping[str, Any], state: Mapping[str, Any], difficulty: str
) -> str:
    if not state["service_open"]:
        return "Ask Aluft Gianne Jr for the job first."
    if state["order"]:
        return "Deliver or decline the outstanding order first."
    session = player_data.get("activity_session")
    active_id = (
        str(session.get("active_id", "")) if isinstance(session, Mapping) else ""
    )
    if active_id and active_id != GNOME_RESTAURANT_ACTIVITY_ID:
        return "Finish the active persistent activity."
    if difficulty == "hard" and state["hard_decline_ticks_left"] > 0:
        waiting = steps_for_ticks_pure(state["hard_decline_ticks_left"])
        return f"Aluft Gianne Jr will hold another hard job for {waiting} more review(s)."
    if not gnome_restaurant_customers_for_pure(
        difficulty,
        _completed_quests(player_data),
        _int(player_data.get("magic_level"), 1),
    ):
        return "No reachable customer wants a delivery at that difficulty."
    return ""


def _assign_order(
    data: dict[str, Any],
    state: dict[str, Any],
    difficulty: str,
    rng: Callable[[], float] | None,
) -> dict[str, Any]:
    customers = gnome_restaurant_customers_for_pure(
        difficulty,
        _completed_quests(data),
        _int(data.get("magic_level"), 1),
    )
    customer = _pick(customers, rng)
    item = _pick(GNOME_RESTAURANT_REQUEST_ITEMS, rng)
    order = {
        "difficulty": difficulty,
        "customer": customer.id,
        "item": str(item),
        "ticks_left": _LIMIT_TICKS[difficulty],
    }
    state["order"] = order
    return order


def _order_text(state: Mapping[str, Any]) -> str:
    order = state["order"]
    if not order:
        return ""
    customer = GNOME_RESTAURANT_CUSTOMERS_BY_ID[str(order["customer"])]
    return (
        f"{str(order['difficulty']).title()} job: 1 {order['item']} "
        f"for {customer.display_name} — {customer.location}"
    )


def gnome_restaurant_can_review_pure(player_data: Mapping[str, Any]) -> bool:
    state = sanitize_gnome_restaurant_state_pure(player_data.get("gnome_restaurant"))
    order = state["order"]
    if not order:
        return False
    return _int(_inventory(player_data).get(str(order["item"]))) > 0


def gnome_restaurant_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    state = sanitize_gnome_restaurant_state_pure(player_data.get("gnome_restaurant"))
    training = gnome_restaurant_training_pure(player_data)
    entry_reasons = _entry_reasons(player_data, state)
    order = state["order"]
    held = _int(_inventory(player_data).get(str(order["item"]))) if order else 0
    limit = _LIMIT_MINUTES[str(order["difficulty"])] if order else 0
    review_reasons: tuple[str, ...] = ()
    if not order:
        review_reasons = ("Take a delivery job",)
    elif held <= 0:
        review_reasons = (f"Cook or bank 1 {order['item']}",)
    difficulty_rows = tuple(
        {
            "id": difficulty,
            "display_name": label,
            "points": _DELIVERY_POINTS[difficulty],
            "limit_minutes": _LIMIT_MINUTES[difficulty],
            "accept_enabled": not _accept_reason(player_data, state, difficulty),
            "accept_reason": _accept_reason(player_data, state, difficulty),
        }
        for difficulty, label in GNOME_RESTAURANT_DIFFICULTIES
    )
    token_held = _int(_inventory(player_data).get(GNOME_RESTAURANT_TOKEN_ITEM)) > 0
    to_next_token = GNOME_RESTAURANT_TOKEN_POINTS - (
        state["points"] % GNOME_RESTAURANT_TOKEN_POINTS
    )
    selected_for_reviews = (
        str(player_data.get("current_utility", "")) == GNOME_RESTAURANT_ACTIVITY_ID
    )
    return {
        **state,
        "training": training,
        "can_open": not entry_reasons and not state["service_open"],
        "entry_reasons": entry_reasons,
        "order_text": _order_text(state),
        "order_item_held": held,
        "order_minutes_left": minutes_for_ticks_pure(order["ticks_left"]) if order else 0,
        "order_limit_minutes": limit,
        "punctuality_pct": int(round(100 * _punctuality(order))) if order else 0,
        "difficulty_options": difficulty_rows,
        "can_review": bool(order) and held > 0,
        "review_reasons": review_reasons,
        "decline_enabled": bool(order),
        "token_held": token_held,
        "token_activate_enabled": token_held and state["token_meals"] > 0,
        "token_activate_reason": (
            ""
            if token_held and state["token_meals"] > 0
            else "Earn 12 delivery points for a free gnome meal."
            if token_held
            else "Reclaim the Reward token from Aluft Gianne Jr."
        ),
        "token_reclaim_enabled": state["token_claimed"] and not token_held,
        "points_to_next_token": to_next_token,
        "policy_controls_enabled": not order,
        "primary_label": (
            "Active for reviews"
            if state["service_open"] and selected_for_reviews
            else "Take a job"
            if state["service_open"]
            else "Ask Gianne Jr for the job"
        ),
        "primary_enabled": (
            (not entry_reasons and not state["service_open"])
            or (
                state["service_open"]
                and (
                    not order
                    and not _accept_reason(
                        player_data, state, str(state["difficulty_policy"])
                    )
                    or (bool(order) and not selected_for_reviews)
                )
            )
        ),
        "leave_visible": state["service_open"] and bool(order),
        "status_text": state["last_result"]
        or (
            "Deliver gnome food for Aluft Aloft Deliveries."
            if state["service_open"]
            else "Aluft Gianne snr. and Blurberry want to see your cooking first."
        ),
        "ledger_text": (
            f"{state['points']:,} points · {to_next_token} to the next reward · "
            f"token holds {state['token_meals']}/{GNOME_RESTAURANT_TOKEN_MEAL_CAP} meals · "
            f"{state['deliveries']['easy']:,} easy / {state['deliveries']['hard']:,} hard delivered"
        ),
    }


def open_gnome_restaurant_service_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    if state["service_open"]:
        return data, False, {"reason": "Aluft Aloft Deliveries already employs you."}
    reasons = _entry_reasons(data, state)
    if reasons:
        return data, False, {"reason": "; ".join(reasons) + "."}
    state["service_open"] = True
    _grant_item(data, GNOME_RESTAURANT_BOX_ITEM)
    _grant_item(data, "Gianne dough", GNOME_RESTAURANT_STARTING_DOUGH)
    state["last_result"] = (
        f"Aluft Gianne Jr hired you and handed over an {GNOME_RESTAURANT_BOX_ITEM} "
        f"and {GNOME_RESTAURANT_STARTING_DOUGH} Gianne dough."
    )
    data["gnome_restaurant"] = state
    return data, True, {"message": state["last_result"]}


def set_gnome_restaurant_policy_pure(
    player_data: Mapping[str, Any], payload: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    policy = str(payload.get("difficulty_policy", state["difficulty_policy"]))
    if policy not in _VALID_DIFFICULTIES:
        return data, False, {"reason": "Unknown Gnome Restaurant job difficulty."}
    if state["order"]:
        return data, False, {"reason": "Deliver or decline the outstanding order first."}
    state["difficulty_policy"] = policy
    state["last_result"] = f"Aluft Gianne Jr will hand out {policy} jobs."
    data["gnome_restaurant"] = state
    return data, True, {"message": state["last_result"]}


def accept_gnome_restaurant_order_pure(
    player_data: Mapping[str, Any],
    payload: Mapping[str, Any] | None = None,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    body = payload if isinstance(payload, Mapping) else {}
    difficulty = str(body.get("difficulty", state["difficulty_policy"]))
    if difficulty not in _VALID_DIFFICULTIES:
        return data, False, {"reason": "Unknown Gnome Restaurant job difficulty."}
    reason = _accept_reason(data, state, difficulty)
    if reason:
        return data, False, {"reason": reason}
    state["difficulty_policy"] = difficulty
    _assign_order(data, state, difficulty, rng)
    state["last_result"] = _order_text(state)
    data["gnome_restaurant"] = state
    data["activity_session"] = {"active_id": GNOME_RESTAURANT_ACTIVITY_ID}
    data["current_utility"] = GNOME_RESTAURANT_ACTIVITY_ID
    return data, True, {"message": state["last_result"], **state["order"]}


def decline_gnome_restaurant_order_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    order = state["order"]
    if not order:
        return data, False, {"reason": "There is no order to decline."}
    difficulty = str(order["difficulty"])
    state["order"] = {}
    waited = False
    if difficulty == "hard":
        state["hard_decline_ticks_left"] = _HARD_DECLINE_WAIT_TICKS
        waited = True
    replacement_reason = _accept_reason(data, state, state["difficulty_policy"])
    if replacement_reason:
        state["last_result"] = f"Declined the {difficulty} job. {replacement_reason}"
    else:
        _assign_order(data, state, str(state["difficulty_policy"]), rng)
        state["last_result"] = f"Declined the {difficulty} job. {_order_text(state)}"
    data["gnome_restaurant"] = state
    return data, True, {"message": state["last_result"], "hard_wait": waited}


def leave_gnome_restaurant_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    if not state["order"]:
        return data, False, {"reason": "No delivery is outstanding."}
    state["order"] = {}
    state["last_result"] = "Handed the delivery box back; your points are safe."
    data["gnome_restaurant"] = state
    data["activity_session"] = {"active_id": ""}
    return data, True, {"message": state["last_result"]}


def reclaim_gnome_restaurant_token_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    if not state["token_claimed"]:
        return data, False, {"reason": "You have not earned a Reward token yet."}
    if _int(_inventory(data).get(GNOME_RESTAURANT_TOKEN_ITEM)) > 0:
        return data, False, {"reason": "You are already carrying the Reward token."}
    _grant_item(data, GNOME_RESTAURANT_TOKEN_ITEM)
    state["last_result"] = (
        "Aluft Gianne Jr replaced your Reward token for free; "
        f"it still holds {state['token_meals']} meal(s)."
    )
    data["gnome_restaurant"] = state
    return data, True, {"message": state["last_result"]}


def activate_gnome_restaurant_token_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    if _int(_inventory(data).get(GNOME_RESTAURANT_TOKEN_ITEM)) <= 0:
        return data, False, {"reason": "Reclaim the Reward token from Aluft Gianne Jr."}
    meals = state["token_meals"]
    if meals <= 0:
        return data, False, {"reason": "The Reward token holds no meals yet."}
    weighted = tuple(GNOME_DISH_ITEMS) * GNOME_RESTAURANT_TOKEN_DISH_WEIGHT + tuple(
        GNOME_COCKTAIL_ITEMS
    ) * GNOME_RESTAURANT_TOKEN_COCKTAIL_WEIGHT
    delivered: dict[str, int] = {}
    for _meal in range(meals):
        item = str(_pick(weighted, rng))
        delivered[item] = delivered.get(item, 0) + 1
        _grant_item(data, item)
    state["token_meals"] = 0
    state["last_result"] = "A mounted terrorchick delivered " + ", ".join(
        f"{count} {item}" for item, count in sorted(delivered.items())
    )
    data["gnome_restaurant"] = state
    return data, True, {"message": state["last_result"], "delivered": delivered}


def apply_gnome_restaurant_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    rng: Callable[[], float] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    body = payload if isinstance(payload, Mapping) else {}
    if action_id == "open_service":
        return open_gnome_restaurant_service_pure(player_data, rng)
    if action_id == "set_policy":
        return set_gnome_restaurant_policy_pure(player_data, body)
    if action_id == "accept_order":
        return accept_gnome_restaurant_order_pure(player_data, body, rng)
    if action_id == "decline_order":
        return decline_gnome_restaurant_order_pure(player_data, rng)
    if action_id == "leave":
        return leave_gnome_restaurant_pure(player_data)
    if action_id == "reclaim_token":
        return reclaim_gnome_restaurant_token_pure(player_data)
    if action_id == "activate_token":
        return activate_gnome_restaurant_token_pure(player_data, rng)
    return (
        copy.deepcopy(dict(player_data)),
        False,
        {"reason": "Unknown Gnome Restaurant command."},
    )


def _punctuality(order: Mapping[str, Any]) -> float:
    return _int(order.get("ticks_left")) / _LIMIT_TICKS[str(order["difficulty"])]


def _roll_tip(
    data: dict[str, Any],
    state: dict[str, Any],
    order: Mapping[str, Any],
    rng: Callable[[], float] | None,
) -> dict[str, Any]:
    """One delivery's tip. Punctuality is the chance of the good-tip group."""
    punctuality = _punctuality(order)
    if str(order["difficulty"]) == "easy":
        low, high = GNOME_RESTAURANT_EASY_TIP_COINS
        best = low + int(round((high - low) * punctuality))
        coins = _range_roll(low, best, rng)
        _grant_item(data, "Coins", coins)
        return {"tip_items": {"Coins": coins}, "good_tip": False}
    good = _roll(rng) < punctuality
    group = GNOME_RESTAURANT_GOOD_TIP_GROUP if good else ""
    rows = (
        gnome_restaurant_tips_for_pure(str(order["customer"]), group)
        if group
        else tuple(
            row
            for ordinary in ("herb", "gem", "rune", "bolt", "other")
            for row in gnome_restaurant_tips_for_pure(str(order["customer"]), ordinary)
        )
    )
    row = _pick(rows, rng)
    quantity = _range_roll(row.low, row.high, rng)
    _grant_item(data, row.item, quantity)
    state["tips_received"][row.id] = _int(state["tips_received"].get(row.id)) + 1
    return {"tip_items": {row.item: quantity}, "good_tip": good, "tip_id": row.id}


def advance_gnome_restaurant_clock_pure(
    player_data: Mapping[str, Any],
    *,
    successful_answer: bool,
    delivering: bool,
    card_ticks: int = STEP_TICKS,
) -> dict[str, Any]:
    """Spend one answered card's time budget from the restaurant's timers.

    Every answer spends the hard-decline wait; only a successful answer on
    another target spends the order's window.
    """
    data = dict(player_data)
    if not isinstance(data.get("gnome_restaurant"), Mapping):
        return data
    state = sanitize_gnome_restaurant_state_pure(data["gnome_restaurant"])
    state["hard_decline_ticks_left"] = max(0, state["hard_decline_ticks_left"] - card_ticks)
    if (order := state["order"]) and successful_answer and not delivering:
        order["ticks_left"] = max(0, order["ticks_left"] - card_ticks)
    data["gnome_restaurant"] = state
    return data


def apply_gnome_restaurant_review_pure(
    player_data: Mapping[str, Any],
    rng: Callable[[], float] | None = None,
    *,
    productive: bool = True,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    data = copy.deepcopy(dict(player_data))
    state = sanitize_gnome_restaurant_state_pure(data.get("gnome_restaurant"))
    order = state["order"]
    if not order:
        return data, False, {"reason": "Take a delivery job from Aluft Gianne Jr."}
    if not productive:
        minutes_left = minutes_for_ticks_pure(order["ticks_left"])
        state["last_result"] = (
            f"Again paused the delivery window; {minutes_left} of "
            f"{_LIMIT_MINUTES[str(order['difficulty'])]} minute(s) left."
        )
        data["gnome_restaurant"] = state
        return data, True, {
            "advanced": False,
            "terminal": False,
            "minutes_left": minutes_left,
            "message": state["last_result"],
        }
    item = str(order["item"])
    if _int(_inventory(data).get(item)) <= 0:
        return data, False, {"reason": f"Cook or bank 1 {item} for this delivery."}
    inventory = dict(_inventory(data))
    inventory[item] = _int(inventory.get(item)) - 1
    if inventory[item] <= 0:
        inventory.pop(item, None)
    data["inventory"] = inventory

    difficulty = str(order["difficulty"])
    customer = GNOME_RESTAURANT_CUSTOMERS_BY_ID[str(order["customer"])]
    tip = _roll_tip(data, state, order, rng)
    points = _DELIVERY_POINTS[difficulty]
    before = state["points"]
    state["points"] = before + points
    state["deliveries"][difficulty] += 1
    thresholds = (state["points"] // GNOME_RESTAURANT_TOKEN_POINTS) - (
        before // GNOME_RESTAURANT_TOKEN_POINTS
    )
    crossed_first_threshold = before < GNOME_RESTAURANT_TOKEN_POINTS <= state["points"]
    meal_thresholds = thresholds - int(crossed_first_threshold)
    token_granted = False
    if thresholds > 0:
        if not state["token_claimed"]:
            state["token_claimed"] = True
            token_granted = True
            _grant_item(data, GNOME_RESTAURANT_TOKEN_ITEM)
        state["token_meals"] = min(
            GNOME_RESTAURANT_TOKEN_MEAL_CAP,
            state["token_meals"] + meal_thresholds,
        )
    state["order"] = {}
    tip_text = ", ".join(
        f"{count:,} {tip_item}" for tip_item, count in tip["tip_items"].items()
    )
    message = (
        f"Delivered 1 {item} to {customer.display_name} · +{points} point(s) · "
        f"tip {tip_text}"
    )
    if token_granted:
        message += f" · {GNOME_RESTAURANT_TOKEN_ITEM} earned"
    elif thresholds > 0:
        message += f" · token now holds {state['token_meals']} meal(s)"
    replacement_reason = _accept_reason(data, state, str(state["difficulty_policy"]))
    if not replacement_reason:
        _assign_order(data, state, str(state["difficulty_policy"]), rng)
        message += f" · next: {_order_text(state)}"
    state["last_result"] = message
    data["gnome_restaurant"] = state
    return data, True, {
        "advanced": True,
        "terminal": not state["order"],
        "delivered_item": item,
        "difficulty": difficulty,
        "customer": customer.id,
        "points_gained": points,
        "token_granted": token_granted,
        "token_meals": state["token_meals"],
        "output_items": tip["tip_items"],
        "message": message,
        **tip,
    }
