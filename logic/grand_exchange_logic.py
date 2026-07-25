"""Pure Grand Exchange state, offer-lifecycle, and market reducers."""

from __future__ import annotations

import copy
import hashlib
import math
from typing import Any, Callable, Dict, Mapping, Optional


GE_STATE_VERSION = 1
GE_SLOT_COUNT = 6
DEFAULT_HIGH_VALUE_CONFIRMATION = 1_000_000
DEFAULT_LOW_PRICE_MULTIPLIER = 0.1
DEFAULT_HIGH_PRICE_MULTIPLIER = 10.0
GE_MARKET_HOUR_CARDS = 10
GE_BUY_LIMIT_WINDOW_CARDS = 40
GE_MARKET_DAY_CARDS = 240
GE_MAX_PLAYER_IMPACT_BPS = 1_500
GE_MIN_FILL_IMPACT_BPS = 25
GE_MAX_FILL_IMPACT_BPS = 300
GE_IMPACT_DECAY_BPS_PER_HOUR = 30
GE_IMPACT_LIQUIDITY_GP = 50_000
GE_MAX_TRADE_PRICE = 2_147_483_647
GE_MAX_OFFER_QUANTITY = 2_147_483_647
GE_SHOCK_ROLL_ONE_IN = 240
GE_SHOCK_MIN_BPS = 500
GE_SHOCK_MAX_BPS = 4_000
GE_FILL_LOG_LIMIT = 40
GE_SHOCK_MIN_TICKS = 5
GE_SHOCK_MAX_TICKS = 40
GE_MAX_ALCHEMY_PRESSURE_BPS = 1_500
_ORDER_SIDES = frozenset({"buy", "sell"})
_ORDER_STATUSES = frozenset({"open", "partial", "complete", "cancelled"})


def _clean_int(value: object, default: int = 0, *, minimum: int = 0) -> int:
    try:
        cleaned = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return max(minimum, cleaned)


def _clean_float(value: object, default: float, *, minimum: float) -> float:
    try:
        cleaned = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    if not math.isfinite(cleaned) or cleaned < minimum:
        return default
    return cleaned


def _clean_bounded_int(
    value: object,
    default: int,
    *,
    lower: int,
    upper: int,
) -> int:
    try:
        cleaned = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return max(lower, min(upper, cleaned))


def default_ge_state_pure() -> Dict[str, Any]:
    return {
        "ge_state_version": GE_STATE_VERSION,
        "ironman_mode": False,
        "ge_settings": {
            "high_value_confirmation": DEFAULT_HIGH_VALUE_CONFIRMATION,
            "low_price_multiplier": DEFAULT_LOW_PRICE_MULTIPLIER,
            "high_price_multiplier": DEFAULT_HIGH_PRICE_MULTIPLIER,
        },
        "ge_market_state": {
            "version": GE_STATE_VERSION,
            "last_processed_tick": 0,
            "rng_seed": 1,
            "rng_cursor": 0,
            "rotating_item_index": 0,
            "items": {},
        },
        "ge_player_orders": [],
        "ge_next_order_id": 1,
        "ge_buy_limit_usage": {},
        "ge_trade_history": {},
        "ge_fill_log": [],
    }


def _sanitize_fill_log_entry(raw: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    side = str(raw.get("side", ""))
    item_name = str(raw.get("item_name", "")).strip()
    if side not in _ORDER_SIDES or not item_name:
        return None
    return {
        "card": _clean_int(raw.get("card"), 0),
        "side": side,
        "item_name": item_name,
        "completed_quantity": _clean_int(raw.get("completed_quantity"), 0),
        "original_quantity": _clean_int(raw.get("original_quantity"), 0),
    }


def _sanitize_order(raw: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    side = str(raw.get("side", ""))
    item_name = str(raw.get("item_name", "")).strip()
    status = str(raw.get("status", "open"))
    if side not in _ORDER_SIDES or not item_name or status not in _ORDER_STATUSES:
        return None

    original_quantity = _clean_int(raw.get("original_quantity"), 0)
    if original_quantity <= 0:
        return None
    remaining_quantity = min(
        original_quantity,
        _clean_int(raw.get("remaining_quantity"), 0),
    )
    completed_quantity = min(
        original_quantity - remaining_quantity,
        _clean_int(raw.get("completed_quantity"), 0),
    )
    if status in {"complete", "cancelled"}:
        remaining_quantity = 0

    order_id = _clean_int(raw.get("id"), 0)
    if order_id <= 0:
        return None
    submitted_unit_price = _clean_int(
        raw.get("submitted_unit_price"),
        0,
        minimum=0,
    )
    if submitted_unit_price <= 0:
        return None
    if (
        original_quantity > GE_MAX_OFFER_QUANTITY
        or submitted_unit_price > GE_MAX_TRADE_PRICE
    ):
        return None

    if status in {"open", "partial"}:
        if remaining_quantity <= 0:
            status = "complete"
        elif completed_quantity > 0:
            status = "partial"
        else:
            status = "open"

    if side == "buy":
        escrow_coins = min(
            _clean_int(raw.get("escrow_coins"), 0),
            remaining_quantity * submitted_unit_price,
        )
        escrow_items = 0
        collectible_coins = min(
            _clean_int(raw.get("collectible_coins"), 0),
            (
                original_quantity * submitted_unit_price
                if status == "cancelled"
                else completed_quantity * submitted_unit_price
            ),
        )
        collectible_items = min(
            _clean_int(raw.get("collectible_items"), 0),
            completed_quantity,
        )
    else:
        escrow_coins = 0
        escrow_items = min(
            _clean_int(raw.get("escrow_items"), 0),
            remaining_quantity,
        )
        collectible_coins = min(
            _clean_int(raw.get("collectible_coins"), 0),
            completed_quantity * GE_MAX_TRADE_PRICE,
        )
        collectible_items = min(
            _clean_int(raw.get("collectible_items"), 0),
            original_quantity if status == "cancelled" else 0,
        )

    if status in {"open", "partial"}:
        backing_is_complete = (
            escrow_coins == remaining_quantity * submitted_unit_price
            if side == "buy"
            else escrow_items == remaining_quantity
        )
        if not backing_is_complete:
            if side == "buy":
                collectible_coins += escrow_coins
                escrow_coins = 0
            else:
                collectible_items += escrow_items
                escrow_items = 0
            remaining_quantity = 0
            status = "cancelled"
    if (
        status in {"complete", "cancelled"}
        and collectible_coins <= 0
        and collectible_items <= 0
    ):
        return None

    return {
        "id": order_id,
        "side": side,
        "item_name": item_name,
        "original_quantity": original_quantity,
        "remaining_quantity": remaining_quantity,
        "completed_quantity": completed_quantity,
        "submitted_unit_price": submitted_unit_price,
        "escrow_coins": escrow_coins,
        "escrow_items": escrow_items,
        "collectible_coins": collectible_coins,
        "collectible_items": collectible_items,
        "status": status,
        "created_market_tick": _clean_int(raw.get("created_market_tick"), 0),
        "last_updated_market_tick": _clean_int(
            raw.get("last_updated_market_tick"),
            0,
        ),
    }


def sanitize_ge_state_pure(raw: Mapping[str, Any] | None) -> Dict[str, Any]:
    defaults = default_ge_state_pure()
    data = dict(raw or {})

    raw_settings = data.get("ge_settings")
    settings = dict(defaults["ge_settings"])
    if isinstance(raw_settings, Mapping):
        settings["high_value_confirmation"] = _clean_int(
            raw_settings.get("high_value_confirmation"),
            DEFAULT_HIGH_VALUE_CONFIRMATION,
            minimum=1,
        )
        settings["low_price_multiplier"] = _clean_float(
            raw_settings.get("low_price_multiplier"),
            DEFAULT_LOW_PRICE_MULTIPLIER,
            minimum=0.000001,
        )
        settings["high_price_multiplier"] = _clean_float(
            raw_settings.get("high_price_multiplier"),
            DEFAULT_HIGH_PRICE_MULTIPLIER,
            minimum=1.0,
        )

    raw_market = data.get("ge_market_state")
    market = dict(defaults["ge_market_state"])
    if isinstance(raw_market, Mapping):
        market["last_processed_tick"] = _clean_int(
            raw_market.get("last_processed_tick"),
            0,
        )
        market["rng_seed"] = _clean_int(raw_market.get("rng_seed"), 1, minimum=1)
        market["rng_cursor"] = _clean_int(raw_market.get("rng_cursor"), 0)
        market["rotating_item_index"] = _clean_int(
            raw_market.get("rotating_item_index"),
            0,
        )
        raw_items = raw_market.get("items")
        market["items"] = (
            copy.deepcopy(dict(raw_items))
            if isinstance(raw_items, Mapping)
            else {}
        )

    orders = []
    seen_ids = set()
    raw_orders = data.get("ge_player_orders")
    if isinstance(raw_orders, (list, tuple)):
        for raw_order in raw_orders:
            if not isinstance(raw_order, Mapping):
                continue
            order = _sanitize_order(raw_order)
            if order is None or order["id"] in seen_ids:
                continue
            seen_ids.add(order["id"])
            orders.append(order)
            if len(orders) == GE_SLOT_COUNT:
                break

    next_order_id = max(
        _clean_int(data.get("ge_next_order_id"), 1, minimum=1),
        max(seen_ids, default=0) + 1,
    )
    raw_buy_usage = data.get("ge_buy_limit_usage")
    buy_usage = (
        copy.deepcopy(dict(raw_buy_usage))
        if isinstance(raw_buy_usage, Mapping)
        else {}
    )
    raw_history = data.get("ge_trade_history")
    trade_history = (
        copy.deepcopy(dict(raw_history))
        if isinstance(raw_history, Mapping)
        else {}
    )
    raw_fill_log = data.get("ge_fill_log")
    fill_log = []
    if isinstance(raw_fill_log, (list, tuple)):
        for raw_entry in raw_fill_log:
            if not isinstance(raw_entry, Mapping):
                continue
            entry = _sanitize_fill_log_entry(raw_entry)
            if entry is not None:
                fill_log.append(entry)

    return {
        "ge_state_version": GE_STATE_VERSION,
        "ironman_mode": bool(data.get("ironman_mode", False)),
        "ge_settings": settings,
        "ge_market_state": market,
        "ge_player_orders": orders,
        "ge_next_order_id": next_order_id,
        "ge_buy_limit_usage": buy_usage,
        "ge_trade_history": trade_history,
        "ge_fill_log": fill_log[-GE_FILL_LOG_LIMIT:],
    }


def ensure_ge_state_pure(player_data: Mapping[str, Any] | None) -> Dict[str, Any]:
    # Shallow on purpose: sanitize_ge_state_pure rebuilds every key it returns.
    # The inventory copy below stays deep — GE mutates inventory in place.
    data = dict(player_data or {})
    data.update(sanitize_ge_state_pure(data))
    inventory = data.get("inventory")
    data["inventory"] = copy.deepcopy(dict(inventory)) if isinstance(inventory, Mapping) else {}
    return data


def ge_access_lock_reason_pure(player_data: Mapping[str, Any]) -> Optional[str]:
    if bool(player_data.get("ironman_mode", False)):
        return "Grand Exchange is disabled while Ironman mode is enabled."
    return None


def _offer_confirmation_reason(
    settings: Mapping[str, Any],
    *,
    total_value: int,
    unit_price: int,
    guide_price: int,
) -> Optional[str]:
    if total_value >= _clean_int(
        settings.get("high_value_confirmation"),
        DEFAULT_HIGH_VALUE_CONFIRMATION,
        minimum=1,
    ):
        return "high_total_value"
    if unit_price < guide_price * _clean_float(
        settings.get("low_price_multiplier"),
        DEFAULT_LOW_PRICE_MULTIPLIER,
        minimum=0.000001,
    ):
        return "extreme_low_price"
    if unit_price > guide_price * _clean_float(
        settings.get("high_price_multiplier"),
        DEFAULT_HIGH_PRICE_MULTIPLIER,
        minimum=1.0,
    ):
        return "extreme_high_price"
    return None


def _current_guide_price_pure(
    data: Mapping[str, Any],
    *,
    item_name: str,
    item_spec: Mapping[str, Any],
) -> int:
    market = data.get("ge_market_state")
    items = market.get("items") if isinstance(market, Mapping) else None
    item_state = items.get(item_name) if isinstance(items, Mapping) else None
    stored = _clean_int(
        item_state.get("guide_price") if isinstance(item_state, Mapping) else None,
        0,
    )
    return stored if stored > 0 else _clean_int(item_spec.get("guide_price"), 0)


def preview_ge_offer_pure(
    player_data: Mapping[str, Any],
    *,
    side: str,
    item_name: str,
    quantity: int,
    unit_price: int,
    item_spec: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    data = ensure_ge_state_pure(player_data)
    lock_reason = ge_access_lock_reason_pure(data)
    if lock_reason:
        return {"ok": False, "reason": "ironman_mode", "message": lock_reason}
    if side not in _ORDER_SIDES:
        return {"ok": False, "reason": "invalid_side"}
    item_name = str(item_name).strip()
    if not item_name or not isinstance(item_spec, Mapping):
        return {"ok": False, "reason": "unknown_item"}
    if not bool(item_spec.get("tradeable", False)):
        return {"ok": False, "reason": "untradeable_item"}
    if not bool(item_spec.get("exchangeable", False)):
        return {"ok": False, "reason": "not_exchangeable"}
    quantity = _clean_int(quantity, 0)
    unit_price = _clean_int(unit_price, 0)
    if (
        quantity <= 0
        or quantity > GE_MAX_OFFER_QUANTITY
        or unit_price <= 0
        or unit_price > GE_MAX_TRADE_PRICE
    ):
        return {"ok": False, "reason": "invalid_offer"}
    if len(data["ge_player_orders"]) >= GE_SLOT_COUNT:
        return {"ok": False, "reason": "no_offer_slot"}

    guide_price = _current_guide_price_pure(
        data,
        item_name=item_name,
        item_spec=item_spec,
    )
    if guide_price <= 0:
        return {"ok": False, "reason": "guide_price_unavailable"}
    if side == "buy" and _clean_int(item_spec.get("buy_limit"), 0) <= 0:
        return {"ok": False, "reason": "buy_limit_unavailable"}

    total_value = quantity * unit_price
    inventory = data["inventory"]
    if side == "buy" and _clean_int(inventory.get("Coins"), 0) < total_value:
        return {
            "ok": False,
            "reason": "insufficient_coins",
            "required": total_value,
            "owned": _clean_int(inventory.get("Coins"), 0),
        }
    if side == "sell" and _clean_int(inventory.get(item_name), 0) < quantity:
        return {
            "ok": False,
            "reason": "insufficient_items",
            "required": quantity,
            "owned": _clean_int(inventory.get(item_name), 0),
        }

    confirmation_reason = _offer_confirmation_reason(
        data["ge_settings"],
        total_value=total_value,
        unit_price=unit_price,
        guide_price=guide_price,
    )
    return {
        "ok": True,
        "side": side,
        "item_name": item_name,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_value": total_value,
        "guide_price": guide_price,
        "confirmation_required": confirmation_reason is not None,
        "confirmation_reason": confirmation_reason,
    }


def place_ge_offer_pure(
    player_data: Mapping[str, Any],
    *,
    side: str,
    item_name: str,
    quantity: int,
    unit_price: int,
    item_spec: Mapping[str, Any] | None,
    confirmed: bool = False,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_ge_state_pure(player_data)
    preview = preview_ge_offer_pure(
        data,
        side=side,
        item_name=item_name,
        quantity=quantity,
        unit_price=unit_price,
        item_spec=item_spec,
    )
    if not preview.get("ok"):
        return data, preview
    if preview["confirmation_required"] and not confirmed:
        return data, {
            **preview,
            "ok": False,
            "reason": "confirmation_required",
        }

    inventory = data["inventory"]
    total_value = int(preview["total_value"])
    quantity = int(preview["quantity"])
    if side == "buy":
        inventory["Coins"] = _clean_int(inventory.get("Coins"), 0) - total_value
        escrow_coins = total_value
        escrow_items = 0
    else:
        inventory[item_name] = _clean_int(inventory.get(item_name), 0) - quantity
        escrow_coins = 0
        escrow_items = quantity

    order_id = data["ge_next_order_id"]
    market_tick = _clean_int(
        data.get("shop_market_clock", {}).get("market_tick")
        if isinstance(data.get("shop_market_clock"), Mapping)
        else 0,
        0,
    )
    order = {
        "id": order_id,
        "side": side,
        "item_name": item_name,
        "original_quantity": quantity,
        "remaining_quantity": quantity,
        "completed_quantity": 0,
        "submitted_unit_price": int(preview["unit_price"]),
        "escrow_coins": escrow_coins,
        "escrow_items": escrow_items,
        "collectible_coins": 0,
        "collectible_items": 0,
        "status": "open",
        "created_market_tick": market_tick,
        "last_updated_market_tick": market_tick,
    }
    data["ge_player_orders"].append(order)
    data["ge_next_order_id"] = order_id + 1
    return data, {"ok": True, "reason": "offer_placed", "order": copy.deepcopy(order)}


def edit_ge_offer_pure(
    player_data: Mapping[str, Any],
    order_id: int,
    *,
    remaining_quantity: int,
    unit_price: int,
    item_spec: Mapping[str, Any] | None,
    confirmed: bool = False,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_ge_state_pure(player_data)
    lock_reason = ge_access_lock_reason_pure(data)
    if lock_reason:
        return data, {"ok": False, "reason": "ironman_mode", "message": lock_reason}
    order = next(
        (
            candidate
            for candidate in data["ge_player_orders"]
            if candidate["id"] == _clean_int(order_id, 0)
        ),
        None,
    )
    if order is None:
        return data, {"ok": False, "reason": "unknown_order"}
    if order["status"] not in {"open", "partial"}:
        return data, {"ok": False, "reason": "order_not_open"}
    if not isinstance(item_spec, Mapping):
        return data, {"ok": False, "reason": "unknown_item"}

    remaining_quantity = _clean_int(remaining_quantity, 0)
    unit_price = _clean_int(unit_price, 0)
    completed_quantity = _clean_int(order.get("completed_quantity"), 0)
    if (
        remaining_quantity <= 0
        or completed_quantity + remaining_quantity > GE_MAX_OFFER_QUANTITY
        or unit_price <= 0
        or unit_price > GE_MAX_TRADE_PRICE
    ):
        return data, {"ok": False, "reason": "invalid_offer"}

    guide_price = _current_guide_price_pure(
        data,
        item_name=str(order["item_name"]),
        item_spec=item_spec,
    )
    if guide_price <= 0:
        return data, {"ok": False, "reason": "guide_price_unavailable"}
    total_value = remaining_quantity * unit_price
    confirmation_reason = _offer_confirmation_reason(
        data["ge_settings"],
        total_value=total_value,
        unit_price=unit_price,
        guide_price=guide_price,
    )
    if confirmation_reason is not None and not confirmed:
        return data, {
            "ok": False,
            "reason": "confirmation_required",
            "confirmation_required": True,
            "confirmation_reason": confirmation_reason,
            "total_value": total_value,
        }

    inventory = data["inventory"]
    if order["side"] == "buy":
        old_escrow = _clean_int(order.get("escrow_coins"), 0)
        new_escrow = total_value
        delta = new_escrow - old_escrow
        available = _clean_int(inventory.get("Coins"), 0)
        if delta > available:
            return data, {
                "ok": False,
                "reason": "insufficient_coins",
                "required": delta,
                "owned": available,
            }
        inventory["Coins"] = available - max(delta, 0) + max(-delta, 0)
        order["escrow_coins"] = new_escrow
    else:
        old_escrow = _clean_int(order.get("escrow_items"), 0)
        delta = remaining_quantity - old_escrow
        item_name = str(order["item_name"])
        available = _clean_int(inventory.get(item_name), 0)
        if delta > available:
            return data, {
                "ok": False,
                "reason": "insufficient_items",
                "required": delta,
                "owned": available,
            }
        inventory[item_name] = available - max(delta, 0) + max(-delta, 0)
        order["escrow_items"] = remaining_quantity

    market_tick = _clean_int(
        data.get("shop_market_clock", {}).get("market_tick")
        if isinstance(data.get("shop_market_clock"), Mapping)
        else 0,
        0,
    )
    order["original_quantity"] = completed_quantity + remaining_quantity
    order["remaining_quantity"] = remaining_quantity
    order["submitted_unit_price"] = unit_price
    order["status"] = "partial" if completed_quantity > 0 else "open"
    order["created_market_tick"] = market_tick
    order["last_updated_market_tick"] = market_tick
    return data, {
        "ok": True,
        "reason": "offer_edited",
        "order": copy.deepcopy(order),
    }


def cancel_ge_offer_pure(
    player_data: Mapping[str, Any],
    order_id: int,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_ge_state_pure(player_data)
    order = next(
        (candidate for candidate in data["ge_player_orders"] if candidate["id"] == order_id),
        None,
    )
    if order is None:
        return data, {"ok": False, "reason": "unknown_order"}
    if order["status"] not in {"open", "partial"}:
        return data, {"ok": False, "reason": "order_not_open"}

    if order["side"] == "buy":
        order["collectible_coins"] += order["escrow_coins"]
        order["escrow_coins"] = 0
    else:
        order["collectible_items"] += order["escrow_items"]
        order["escrow_items"] = 0
    order["remaining_quantity"] = 0
    order["status"] = "cancelled"
    order["last_updated_market_tick"] = _clean_int(
        data.get("shop_market_clock", {}).get("market_tick")
        if isinstance(data.get("shop_market_clock"), Mapping)
        else 0,
        0,
    )
    return data, {"ok": True, "reason": "offer_cancelled", "order_id": order_id}


def collect_ge_offer_pure(
    player_data: Mapping[str, Any],
    order_id: int,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_ge_state_pure(player_data)
    order = next(
        (candidate for candidate in data["ge_player_orders"] if candidate["id"] == order_id),
        None,
    )
    if order is None:
        return data, {"ok": False, "reason": "unknown_order"}

    coins = _clean_int(order.get("collectible_coins"), 0)
    items = _clean_int(order.get("collectible_items"), 0)
    if coins <= 0 and items <= 0:
        return data, {"ok": False, "reason": "nothing_to_collect"}
    inventory = data["inventory"]
    if coins:
        inventory["Coins"] = _clean_int(inventory.get("Coins"), 0) + coins
    if items:
        item_name = str(order["item_name"])
        inventory[item_name] = _clean_int(inventory.get(item_name), 0) + items
    order["collectible_coins"] = 0
    order["collectible_items"] = 0
    if order["status"] in {"complete", "cancelled"}:
        data["ge_player_orders"] = [
            candidate
            for candidate in data["ge_player_orders"]
            if candidate["id"] != order_id
        ]
    return data, {
        "ok": True,
        "reason": "offer_collected",
        "order_id": order_id,
        "coins": coins,
        "items": items,
    }


def collect_all_ge_offers_pure(
    player_data: Mapping[str, Any],
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_ge_state_pure(player_data)
    collected_coins = 0
    collected_items: Dict[str, int] = {}
    order_ids = [
        order["id"]
        for order in data["ge_player_orders"]
        if order["collectible_coins"] > 0 or order["collectible_items"] > 0
    ]
    for order_id in order_ids:
        order = next(order for order in data["ge_player_orders"] if order["id"] == order_id)
        item_name = str(order["item_name"])
        data, result = collect_ge_offer_pure(data, order_id)
        collected_coins += _clean_int(result.get("coins"), 0)
        amount = _clean_int(result.get("items"), 0)
        if amount:
            collected_items[item_name] = collected_items.get(item_name, 0) + amount
    if not order_ids:
        return data, {"ok": False, "reason": "nothing_to_collect"}
    return data, {
        "ok": True,
        "reason": "all_offers_collected",
        "coins": collected_coins,
        "items": collected_items,
    }


def _stable_unit_interval(*parts: object) -> float:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:8], "big") / float(1 << 64)


def _next_market_draw(
    market: Dict[str, Any],
    random_draw: Callable[[], float] | None,
) -> float:
    cursor = _clean_int(market.get("rng_cursor"), 0)
    market["rng_cursor"] = cursor + 1
    if random_draw is None:
        return _stable_unit_interval(
            _clean_int(market.get("rng_seed"), 1, minimum=1),
            cursor,
        )
    try:
        draw = float(random_draw())
    except (TypeError, ValueError, OverflowError):
        draw = 0.5
    if not math.isfinite(draw):
        return 0.5
    return min(math.nextafter(1.0, 0.0), max(0.0, draw))


def _move_toward_zero(value: int, amount: int) -> int:
    if value > 0:
        return max(0, value - amount)
    if value < 0:
        return min(0, value + amount)
    return 0


def _market_liquidity_pure(
    *,
    anchor_price: int,
    item_seed: int,
    market_tick: int,
    item_spec: Mapping[str, Any],
) -> float:
    base = 1.0 - math.log(max(1, anchor_price)) / math.log(2_000_000_000)
    base = min(1.0, max(0.18, base))
    category_factor = {
        "ore": 1.08,
        "log": 1.08,
        "fish": 1.05,
        "runecrafting": 1.05,
        "gem": 0.82,
        "equipment": 0.80,
        "hunter": 0.85,
    }.get(str(item_spec.get("category", "")), 1.0)
    role_factor = {
        "raw_material": 1.08,
        "processed_good": 0.92,
        "rare_or_dependency": 0.80,
    }.get(str(item_spec.get("source_role", "")), 1.0)
    required_level = _clean_int(item_spec.get("required_level"), 1, minimum=1)
    level_factor = 1.0 - min(0.30, (required_level - 1) / 326.0)
    day_index = market_tick // GE_MARKET_DAY_CARDS
    day_phase = (market_tick % GE_MARKET_DAY_CARDS) / GE_MARKET_DAY_CARDS
    day_envelope = 1.0 - 0.25 * math.cos(2.0 * math.pi * day_phase)
    weekend = 1.10 if day_index % 7 in {5, 6} else 1.0
    item_jitter = 0.95 + 0.10 * _stable_unit_interval(item_seed, "item_liquidity")
    day_jitter = 0.90 + 0.20 * _stable_unit_interval(
        item_seed,
        day_index,
        "day_liquidity",
    )
    return min(
        1.5,
        max(
            0.10,
            base
            * category_factor
            * role_factor
            * level_factor
            * day_envelope
            * weekend
            * item_jitter
            * day_jitter,
        ),
    )


def _shock_bps_at_tick(item_state: Mapping[str, Any], market_tick: int) -> int:
    start = _clean_int(item_state.get("shock_start_tick"), 0)
    end = _clean_int(item_state.get("shock_end_tick"), 0)
    peak = _clean_bounded_int(
        item_state.get("shock_peak_bps"),
        0,
        lower=-GE_SHOCK_MAX_BPS,
        upper=GE_SHOCK_MAX_BPS,
    )
    if end <= start or market_tick <= start or market_tick >= end or peak == 0:
        return 0
    phase = (market_tick - start) / (end - start)
    return int(round(peak * math.sin(math.pi * phase)))


def _market_item_state_pure(
    market: Dict[str, Any],
    *,
    item_name: str,
    item_spec: Mapping[str, Any],
    market_tick: int,
    random_draw: Callable[[], float] | None,
) -> Dict[str, Any]:
    raw_items = market.get("items")
    items = copy.deepcopy(dict(raw_items)) if isinstance(raw_items, Mapping) else {}
    raw_state = items.get(item_name)
    state = dict(raw_state) if isinstance(raw_state, Mapping) else {}
    catalog_price = _clean_int(item_spec.get("guide_price"), 1, minimum=1)
    stored_anchor = _clean_int(state.get("anchor_price"), 0)
    anchor_price = stored_anchor if stored_anchor > 0 else catalog_price
    stored_guide = _clean_int(state.get("guide_price"), 0)
    guide_price = stored_guide if stored_guide > 0 else catalog_price
    last_tick = min(
        market_tick,
        _clean_int(state.get("last_processed_tick"), market_tick),
    )
    elapsed = max(0, market_tick - last_tick)
    item_seed = _clean_int(
        state.get("item_seed"),
        int(_stable_unit_interval(market.get("rng_seed", 1), item_name) * (1 << 31))
        + 1,
        minimum=1,
    )
    impact_bps = _clean_bounded_int(
        state.get("player_impact_bps"),
        0,
        lower=-GE_MAX_PLAYER_IMPACT_BPS,
        upper=GE_MAX_PLAYER_IMPACT_BPS,
    )
    ambient_bps = _clean_bounded_int(
        state.get("ambient_bps"),
        0,
        lower=-1_500,
        upper=1_500,
    )

    if elapsed > 0:
        decay = (
            elapsed * GE_IMPACT_DECAY_BPS_PER_HOUR
        ) // GE_MARKET_HOUR_CARDS
        impact_bps = _move_toward_zero(impact_bps, decay)
        ambient_bps = int(round(ambient_bps * math.pow(0.5, elapsed / 600.0)))
        liquidity = _market_liquidity_pure(
            anchor_price=anchor_price,
            item_seed=item_seed,
            market_tick=market_tick,
            item_spec=item_spec,
        )
        volatility = min(3.0, max(0.5, 1.0 / liquidity))
        noise_step = (
            (_next_market_draw(market, random_draw) * 2.0 - 1.0)
            * 15.0
            * volatility
            * math.sqrt(elapsed)
        )
        ambient_bps = max(-1_500, min(1_500, int(round(ambient_bps + noise_step))))

        shock_end = _clean_int(state.get("shock_end_tick"), 0)
        if shock_end and market_tick >= shock_end:
            state["shock_start_tick"] = 0
            state["shock_end_tick"] = 0
            state["shock_peak_bps"] = 0
            state["shock_cooldown_until_tick"] = market_tick + GE_MARKET_HOUR_CARDS
        if (
            _clean_int(state.get("shock_end_tick"), 0) <= 0
            and market_tick >= _clean_int(state.get("shock_cooldown_until_tick"), 0)
        ):
            start_probability = 1.0 - math.pow(
                1.0 - 1.0 / GE_SHOCK_ROLL_ONE_IN,
                elapsed,
            )
            if _next_market_draw(market, random_draw) < start_probability:
                direction = -1 if _next_market_draw(market, random_draw) < 0.5 else 1
                magnitude_draw = _next_market_draw(market, random_draw)
                duration_draw = _next_market_draw(market, random_draw)
                magnitude = GE_SHOCK_MIN_BPS + int(
                    magnitude_draw * (GE_SHOCK_MAX_BPS - GE_SHOCK_MIN_BPS + 1)
                )
                duration = GE_SHOCK_MIN_TICKS + int(
                    duration_draw * (GE_SHOCK_MAX_TICKS - GE_SHOCK_MIN_TICKS + 1)
                )
                state["shock_start_tick"] = market_tick
                state["shock_end_tick"] = market_tick + duration
                state["shock_peak_bps"] = direction * magnitude

    shock_bps = _shock_bps_at_tick(state, market_tick)
    total_bps = max(-9_000, min(9_000, ambient_bps + impact_bps + shock_bps))
    true_price = max(
        1,
        min(
            GE_MAX_TRADE_PRICE,
            int(round(anchor_price * (10_000 + total_bps) / 10_000)),
        ),
    )
    high_alchemy_value = _clean_int(item_spec.get("high_alchemy_value"), 0)
    alchemy_pressure_bps = 0
    if high_alchemy_value > true_price:
        gap_bps = int(
            round(
                (high_alchemy_value - true_price)
                / max(1, anchor_price)
                * 10_000
            )
        )
        alchemy_pressure_bps = min(
            GE_MAX_ALCHEMY_PRESSURE_BPS,
            max(0, int(round(gap_bps * 0.25))),
        )
        total_bps = max(-9_000, min(9_000, total_bps + alchemy_pressure_bps))
        true_price = max(
            1,
            min(
                GE_MAX_TRADE_PRICE,
                int(round(anchor_price * (10_000 + total_bps) / 10_000)),
            ),
        )
    state.update(
        {
            "anchor_price": anchor_price,
            "guide_price": guide_price,
            "true_price": true_price,
            "player_impact_bps": impact_bps,
            "ambient_bps": ambient_bps,
            "current_shock_bps": shock_bps,
            "current_alchemy_pressure_bps": alchemy_pressure_bps,
            "last_processed_tick": market_tick,
            "item_seed": item_seed,
        }
    )
    items[item_name] = state
    market["items"] = items
    return state


def _buy_limit_remaining_pure(
    data: Dict[str, Any],
    *,
    item_name: str,
    buy_limit: int,
    market_tick: int,
) -> int:
    usage_map = copy.deepcopy(dict(data.get("ge_buy_limit_usage") or {}))
    raw_usage = usage_map.get(item_name)
    usage = dict(raw_usage) if isinstance(raw_usage, Mapping) else {}
    window_start = _clean_int(usage.get("window_start_tick"), market_tick)
    bought = _clean_int(usage.get("bought"), 0)
    if market_tick - window_start >= GE_BUY_LIMIT_WINDOW_CARDS:
        window_start = market_tick
        bought = 0
    usage_map[item_name] = {
        "window_start_tick": window_start,
        "bought": bought,
    }
    data["ge_buy_limit_usage"] = usage_map
    return max(0, buy_limit - bought)


def _record_buy_limit_usage_pure(
    data: Dict[str, Any],
    *,
    item_name: str,
    quantity: int,
    market_tick: int,
) -> None:
    usage_map = copy.deepcopy(dict(data.get("ge_buy_limit_usage") or {}))
    raw_usage = usage_map.get(item_name)
    usage = dict(raw_usage) if isinstance(raw_usage, Mapping) else {}
    usage_map[item_name] = {
        "window_start_tick": _clean_int(
            usage.get("window_start_tick"),
            market_tick,
        ),
        "bought": _clean_int(usage.get("bought"), 0) + quantity,
    }
    data["ge_buy_limit_usage"] = usage_map


def _record_trade_pure(
    data: Dict[str, Any],
    *,
    item_name: str,
    market_tick: int,
    quantity: int,
    unit_price: int,
) -> None:
    history_map = copy.deepcopy(dict(data.get("ge_trade_history") or {}))
    window_start = (market_tick // GE_MARKET_DAY_CARDS) * GE_MARKET_DAY_CARDS
    raw_history = history_map.get(item_name)
    history = dict(raw_history) if isinstance(raw_history, Mapping) else {}
    if _clean_int(history.get("window_start_tick"), window_start) != window_start:
        history = {}
    history_map[item_name] = {
        "window_start_tick": window_start,
        "quantity": _clean_int(history.get("quantity"), 0) + quantity,
        "notional": _clean_int(history.get("notional"), 0) + quantity * unit_price,
    }
    data["ge_trade_history"] = history_map


def _fill_order_for_tick_pure(
    data: Dict[str, Any],
    order: Dict[str, Any],
    *,
    item_spec: Mapping[str, Any],
    item_state: Dict[str, Any],
    market_tick: int,
    elapsed: int,
    random_draw: Callable[[], float] | None,
) -> Dict[str, Any] | None:
    market = data["ge_market_state"]
    true_price = _clean_int(item_state.get("true_price"), 1, minimum=1)
    submitted = _clean_int(order.get("submitted_unit_price"), 1, minimum=1)
    side = str(order["side"])
    buy_limit_remaining = None
    if side == "buy":
        buy_limit = _clean_int(item_spec.get("buy_limit"), 0)
        if buy_limit <= 0:
            return None
        buy_limit_remaining = _buy_limit_remaining_pure(
            data,
            item_name=str(order["item_name"]),
            buy_limit=buy_limit,
            market_tick=market_tick,
        )
        if buy_limit_remaining <= 0:
            return None
    generosity_bps = (
        (true_price - submitted) / true_price * 10_000
        if side == "sell"
        else (submitted - true_price) / true_price * 10_000
    )
    logistic_x = max(-60.0, min(60.0, -0.006 * (generosity_bps - 40.0)))
    base_probability = 0.9 / (1.0 + math.exp(logistic_x))
    liquidity = _market_liquidity_pure(
        anchor_price=_clean_int(item_state.get("anchor_price"), 1, minimum=1),
        item_seed=_clean_int(item_state.get("item_seed"), 1, minimum=1),
        market_tick=market_tick,
        item_spec=item_spec,
    )
    probability_noise = 1.0 + (
        _next_market_draw(market, random_draw) * 2.0 - 1.0
    ) * 0.35
    one_tick_probability = min(
        0.98,
        max(
            0.0,
            base_probability
            * (0.55 + 0.45 * min(1.0, liquidity))
            * probability_noise,
        ),
    )
    fill_probability = 1.0 - math.pow(1.0 - one_tick_probability, max(1, elapsed))
    if _next_market_draw(market, random_draw) >= fill_probability:
        return None

    aggression = min(1.5, max(0.0, generosity_bps / 500.0))
    size_factor = 0.5 + _next_market_draw(market, random_draw)
    base_quantity = (
        _clean_int(order.get("original_quantity"), 1, minimum=1)
        * 0.12
        * (0.5 + 0.5 * min(1.0, liquidity))
        * (1.0 + aggression * 1.5)
        * size_factor
        * math.sqrt(max(1, elapsed))
    )
    if _next_market_draw(market, random_draw) < 0.1:
        base_quantity *= 2.5
    quantity = min(
        _clean_int(order.get("remaining_quantity"), 0),
        max(1, int(math.ceil(base_quantity))),
    )
    if side == "buy":
        quantity = min(quantity, int(buy_limit_remaining or 0))
    if quantity <= 0:
        return None

    execution_price = (
        min(submitted, true_price)
        if side == "buy"
        else max(submitted, true_price)
    )
    if side == "buy":
        reserved = quantity * submitted
        order["escrow_coins"] = max(
            0,
            _clean_int(order.get("escrow_coins"), 0) - reserved,
        )
        order["collectible_items"] = (
            _clean_int(order.get("collectible_items"), 0) + quantity
        )
        order["collectible_coins"] = (
            _clean_int(order.get("collectible_coins"), 0)
            + quantity * (submitted - execution_price)
        )
        _record_buy_limit_usage_pure(
            data,
            item_name=str(order["item_name"]),
            quantity=quantity,
            market_tick=market_tick,
        )
    else:
        order["escrow_items"] = max(
            0,
            _clean_int(order.get("escrow_items"), 0) - quantity,
        )
        order["collectible_coins"] = (
            _clean_int(order.get("collectible_coins"), 0)
            + quantity * execution_price
        )

    order["remaining_quantity"] = max(
        0,
        _clean_int(order.get("remaining_quantity"), 0) - quantity,
    )
    order["completed_quantity"] = min(
        _clean_int(order.get("original_quantity"), 0),
        _clean_int(order.get("completed_quantity"), 0) + quantity,
    )
    order["status"] = "complete" if order["remaining_quantity"] == 0 else "partial"
    order["last_updated_market_tick"] = market_tick

    fill_value = quantity * execution_price
    impact = int(
        round(
            fill_value
            / max(1.0, GE_IMPACT_LIQUIDITY_GP * liquidity)
            * 100.0
        )
    )
    impact = min(
        GE_MAX_FILL_IMPACT_BPS,
        max(GE_MIN_FILL_IMPACT_BPS, impact),
    )
    signed_impact = impact if side == "buy" else -impact
    item_state["player_impact_bps"] = max(
        -GE_MAX_PLAYER_IMPACT_BPS,
        min(
            GE_MAX_PLAYER_IMPACT_BPS,
            int(item_state.get("player_impact_bps", 0) or 0) + signed_impact,
        ),
    )
    total_bps = max(
        -9_000,
        min(
            9_000,
            int(item_state.get("ambient_bps", 0) or 0)
            + int(item_state.get("player_impact_bps", 0) or 0)
            + int(item_state.get("current_shock_bps", 0) or 0)
            + int(item_state.get("current_alchemy_pressure_bps", 0) or 0),
        ),
    )
    item_state["true_price"] = max(
        1,
        min(
            GE_MAX_TRADE_PRICE,
            int(round(item_state["anchor_price"] * (10_000 + total_bps) / 10_000)),
        ),
    )
    _record_trade_pure(
        data,
        item_name=str(order["item_name"]),
        market_tick=market_tick,
        quantity=quantity,
        unit_price=execution_price,
    )
    return {
        "order_id": int(order["id"]),
        "side": side,
        "item_name": str(order["item_name"]),
        "quantity": quantity,
        "unit_price": execution_price,
        "price_improvement": abs(submitted - execution_price),
        "impact_bps": signed_impact,
        "completed_quantity": int(order["completed_quantity"]),
        "original_quantity": int(order["original_quantity"]),
    }


def _update_guide_price_if_due_pure(
    data: Dict[str, Any],
    *,
    item_name: str,
    item_state: Dict[str, Any],
    item_spec: Mapping[str, Any],
    market_tick: int,
) -> None:
    day_start = (market_tick // GE_MARKET_DAY_CARDS) * GE_MARKET_DAY_CARDS
    last_update = _clean_int(item_state.get("last_guide_update_tick"), 0)
    if day_start <= last_update:
        return
    history_map = copy.deepcopy(dict(data.get("ge_trade_history") or {}))
    raw_history = history_map.get(item_name)
    history = dict(raw_history) if isinstance(raw_history, Mapping) else {}
    history_start = _clean_int(history.get("window_start_tick"), 0)
    quantity = (
        _clean_int(history.get("quantity"), 0)
        if history_start < day_start
        else 0
    )
    notional = (
        _clean_int(history.get("notional"), 0)
        if history_start < day_start
        else 0
    )
    old_guide = _clean_int(item_state.get("guide_price"), 1, minimum=1)
    if quantity > 0 and notional > 0:
        vwap = notional / quantity
        liquidity = _market_liquidity_pure(
            anchor_price=_clean_int(item_state.get("anchor_price"), 1, minimum=1),
            item_seed=_clean_int(item_state.get("item_seed"), 1, minimum=1),
            market_tick=market_tick,
            item_spec=item_spec,
        )
        matched_weight = 0.20 + 0.50 * min(1.0, liquidity)
        target = int(round(old_guide + (vwap - old_guide) * matched_weight))
        lower = max(1, int(math.floor(old_guide * 0.95)))
        upper = max(1, int(math.ceil(old_guide * 1.05)))
        item_state["guide_price"] = min(upper, max(lower, target))
    item_state["last_guide_update_tick"] = day_start
    history_map[item_name] = {
        "window_start_tick": day_start,
        "quantity": 0,
        "notional": 0,
    }
    data["ge_trade_history"] = history_map


def advance_ge_market_tick_pure(
    player_data: Mapping[str, Any],
    *,
    item_catalog: Mapping[str, Mapping[str, Any]],
    random_draw: Callable[[], float] | None = None,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Advance the local GE to the shared answered-card market clock.

    Work is bounded by the six player offer slots. A skipped interval is
    collapsed into one price/fill draw rather than replayed tick by tick.
    """

    data = ensure_ge_state_pure(player_data)
    clock = data.get("shop_market_clock")
    market_tick = _clean_int(
        clock.get("market_tick") if isinstance(clock, Mapping) else 0,
        0,
    )
    # The fill log is keyed by answered cards, not by market_tick: market_tick
    # is also the buy-limit window clock and the two are clamped separately.
    answered_cards = _clean_int(
        clock.get("answered_cards") if isinstance(clock, Mapping) else 0,
        0,
    )
    market = copy.deepcopy(dict(data["ge_market_state"]))
    previous_tick = min(
        market_tick,
        _clean_int(market.get("last_processed_tick"), 0),
    )
    elapsed = market_tick - previous_tick
    if elapsed <= 0:
        return data, {
            "ok": True,
            "reason": "market_current",
            "market_tick": market_tick,
            "fills": [],
        }
    data["ge_market_state"] = market
    fills = []
    open_orders = [
        order
        for order in data["ge_player_orders"]
        if order["status"] in {"open", "partial"}
        and _clean_int(order.get("remaining_quantity"), 0) > 0
    ]
    item_names = tuple(dict.fromkeys(str(order["item_name"]) for order in open_orders))
    item_states: Dict[str, Dict[str, Any]] = {}
    for item_name in item_names:
        item_spec = item_catalog.get(item_name)
        if not isinstance(item_spec, Mapping):
            continue
        item_states[item_name] = _market_item_state_pure(
            market,
            item_name=item_name,
            item_spec=item_spec,
            market_tick=market_tick,
            random_draw=random_draw,
        )
        _update_guide_price_if_due_pure(
            data,
            item_name=item_name,
            item_state=item_states[item_name],
            item_spec=item_spec,
            market_tick=market_tick,
        )
        for order in sorted(
            (candidate for candidate in open_orders if candidate["item_name"] == item_name),
            key=lambda candidate: (
                _clean_int(candidate.get("created_market_tick"), 0),
                _clean_int(candidate.get("id"), 0),
            ),
        ):
            order_elapsed = market_tick - max(
                previous_tick,
                _clean_int(order.get("created_market_tick"), previous_tick),
            )
            if order_elapsed <= 0:
                continue
            fill = _fill_order_for_tick_pure(
                data,
                order,
                item_spec=item_spec,
                item_state=item_states[item_name],
                market_tick=market_tick,
                elapsed=order_elapsed,
                random_draw=random_draw,
            )
            if fill is not None:
                fills.append(fill)

    market["last_processed_tick"] = market_tick
    market["rotating_item_index"] = _clean_int(
        market.get("rotating_item_index"),
        0,
    )
    data["ge_market_state"] = market
    if fills:
        # Rebuild the list rather than appending in place: ensure_ge_state_pure
        # is shallow, so mutating the saved list would write through.
        log = list(data.get("ge_fill_log") or [])
        log.extend(
            {
                "card": answered_cards,
                "side": fill["side"],
                "item_name": fill["item_name"],
                "completed_quantity": fill["completed_quantity"],
                "original_quantity": fill["original_quantity"],
            }
            for fill in fills
        )
        data["ge_fill_log"] = log[-GE_FILL_LOG_LIMIT:]
    return data, {
        "ok": True,
        "reason": "market_advanced",
        "market_tick": market_tick,
        "elapsed_ticks": elapsed,
        "fills": fills,
    }


def ge_frontend_projection_pure(
    player_data: Mapping[str, Any],
    *,
    item_catalog: Mapping[str, Mapping[str, Any]],
) -> Dict[str, Any]:
    data = ensure_ge_state_pure(player_data)
    item_rows = []
    for item_name, item_spec in item_catalog.items():
        if not isinstance(item_spec, Mapping):
            continue
        item_rows.append(
            {
                "item_name": str(item_name),
                "guide_price": _current_guide_price_pure(
                    data,
                    item_name=str(item_name),
                    item_spec=item_spec,
                ),
                "buy_limit": _clean_int(item_spec.get("buy_limit"), 0) or None,
                "owned": _clean_int(data["inventory"].get(item_name), 0),
                "asset_path": str(item_spec.get("asset_path") or ""),
                "category": str(item_spec.get("category") or ""),
            }
        )
    item_rows.sort(key=lambda row: row["item_name"].casefold())
    orders = [copy.deepcopy(order) for order in data["ge_player_orders"]]
    has_collectible = any(
        _clean_int(order.get("collectible_coins"), 0) > 0
        or _clean_int(order.get("collectible_items"), 0) > 0
        for order in orders
    )
    slots = tuple(
        orders[index] if index < len(orders) else None
        for index in range(GE_SLOT_COUNT)
    )
    clock = data.get("shop_market_clock")
    return {
        "ironman_mode": bool(data["ironman_mode"]),
        "lock_reason": ge_access_lock_reason_pure(data),
        "coins": _clean_int(data["inventory"].get("Coins"), 0),
        "settings": copy.deepcopy(data["ge_settings"]),
        "has_collectible": has_collectible,
        "slots": slots,
        "items": tuple(item_rows),
        # Newest first: reverse-chronological order is decided here so every
        # frontend renders the same way.
        "fill_log": tuple(reversed(copy.deepcopy(data["ge_fill_log"]))),
        "answered_cards": _clean_int(
            clock.get("answered_cards") if isinstance(clock, Mapping) else 0,
            0,
        ),
    }


def apply_ge_frontend_action_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None,
    *,
    item_catalog: Mapping[str, Mapping[str, Any]],
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    payload = dict(payload or {})
    item_name = str(payload.get("item_name", ""))
    item_spec = item_catalog.get(item_name)
    if action_id == "preview_offer":
        data = ensure_ge_state_pure(player_data)
        result = preview_ge_offer_pure(
            data,
            side=str(payload.get("side", "")),
            item_name=item_name,
            quantity=_clean_int(payload.get("quantity"), 0),
            unit_price=_clean_int(payload.get("unit_price"), 0),
            item_spec=item_spec,
        )
        return data, result
    if action_id == "place_offer":
        return place_ge_offer_pure(
            player_data,
            side=str(payload.get("side", "")),
            item_name=item_name,
            quantity=_clean_int(payload.get("quantity"), 0),
            unit_price=_clean_int(payload.get("unit_price"), 0),
            item_spec=item_spec,
            confirmed=bool(payload.get("confirmed", False)),
        )
    if action_id == "edit_offer":
        order_id = _clean_int(payload.get("order_id"), 0)
        data = ensure_ge_state_pure(player_data)
        order = next(
            (
                candidate
                for candidate in data["ge_player_orders"]
                if candidate["id"] == order_id
            ),
            None,
        )
        order_item_name = str((order or {}).get("item_name", ""))
        return edit_ge_offer_pure(
            data,
            order_id,
            remaining_quantity=_clean_int(payload.get("remaining_quantity"), 0),
            unit_price=_clean_int(payload.get("unit_price"), 0),
            item_spec=item_catalog.get(order_item_name),
            confirmed=bool(payload.get("confirmed", False)),
        )
    if action_id == "cancel_offer":
        return cancel_ge_offer_pure(
            player_data,
            _clean_int(payload.get("order_id"), 0),
        )
    if action_id == "collect_offer":
        return collect_ge_offer_pure(
            player_data,
            _clean_int(payload.get("order_id"), 0),
        )
    if action_id == "collect_all":
        return collect_all_ge_offers_pure(player_data)
    if action_id == "set_ironman":
        return set_ironman_mode_pure(
            player_data,
            bool(payload.get("enabled", False)),
        )
    if action_id == "set_offer_safety":
        return set_ge_offer_safety_pure(
            player_data,
            high_value_confirmation=_clean_int(
                payload.get("high_value_confirmation"),
                0,
            ),
            low_price_percent=_clean_int(payload.get("low_price_percent"), 0),
            high_price_multiplier=_clean_int(
                payload.get("high_price_multiplier"),
                0,
            ),
        )
    return ensure_ge_state_pure(player_data), {
        "ok": False,
        "reason": "unknown_action",
    }


def set_ironman_mode_pure(
    player_data: Mapping[str, Any],
    enabled: bool,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_ge_state_pure(player_data)
    enabled = bool(enabled)
    if enabled and data["ge_player_orders"]:
        return data, {"ok": False, "reason": "offers_must_be_cleared"}
    data["ironman_mode"] = enabled
    return data, {"ok": True, "reason": "ironman_mode_updated", "enabled": enabled}


def set_ge_offer_safety_pure(
    player_data: Mapping[str, Any],
    *,
    high_value_confirmation: int,
    low_price_percent: int,
    high_price_multiplier: int,
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_ge_state_pure(player_data)
    high_value_confirmation = _clean_int(high_value_confirmation, 0)
    low_price_percent = _clean_int(low_price_percent, 0)
    high_price_multiplier = _clean_int(high_price_multiplier, 0)
    if (
        high_value_confirmation <= 0
        or not 1 <= low_price_percent <= 100
        or not 1 <= high_price_multiplier <= 100
    ):
        return data, {"ok": False, "reason": "invalid_settings"}
    data["ge_settings"] = {
        "high_value_confirmation": high_value_confirmation,
        "low_price_multiplier": low_price_percent / 100.0,
        "high_price_multiplier": float(high_price_multiplier),
    }
    return data, {
        "ok": True,
        "reason": "offer_safety_updated",
        "settings": copy.deepcopy(data["ge_settings"]),
    }
