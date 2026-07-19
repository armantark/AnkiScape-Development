"""Pure Grand Exchange state and offer-lifecycle reducers.

The market simulation itself is intentionally separate from this module's
escrow boundary. Offers can be placed, cancelled, collected, and migrated
without importing Qt or Anki; later market ticks only need to update the same
sanitized order records.
"""

from __future__ import annotations

import copy
import math
from typing import Any, Dict, Mapping, Optional


GE_STATE_VERSION = 1
GE_SLOT_COUNT = 8
DEFAULT_HIGH_VALUE_CONFIRMATION = 1_000_000
DEFAULT_LOW_PRICE_MULTIPLIER = 0.1
DEFAULT_HIGH_PRICE_MULTIPLIER = 10.0
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

    return {
        "id": order_id,
        "side": side,
        "item_name": item_name,
        "original_quantity": original_quantity,
        "remaining_quantity": remaining_quantity,
        "completed_quantity": completed_quantity,
        "submitted_unit_price": submitted_unit_price,
        "escrow_coins": _clean_int(raw.get("escrow_coins"), 0),
        "escrow_items": _clean_int(raw.get("escrow_items"), 0),
        "collectible_coins": _clean_int(raw.get("collectible_coins"), 0),
        "collectible_items": _clean_int(raw.get("collectible_items"), 0),
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

    return {
        "ge_state_version": GE_STATE_VERSION,
        "ironman_mode": bool(data.get("ironman_mode", False)),
        "ge_settings": settings,
        "ge_market_state": market,
        "ge_player_orders": orders,
        "ge_next_order_id": next_order_id,
        "ge_buy_limit_usage": buy_usage,
        "ge_trade_history": trade_history,
    }


def ensure_ge_state_pure(player_data: Mapping[str, Any] | None) -> Dict[str, Any]:
    data = copy.deepcopy(dict(player_data or {}))
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
    if quantity <= 0 or unit_price <= 0:
        return {"ok": False, "reason": "invalid_offer"}
    if len(data["ge_player_orders"]) >= GE_SLOT_COUNT:
        return {"ok": False, "reason": "no_offer_slot"}

    guide_price = _clean_int(item_spec.get("guide_price"), 0)
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
