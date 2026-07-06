"""Pure NPC shop runtime logic.

The UI should call these functions through a thin adapter. They own source
disposition checks, stock mutation, event history, rollback, and the review-card
market clock without importing Anki.
"""

from __future__ import annotations

import copy
from typing import Any, Dict, Iterable, Mapping, Optional

try:
    from .shop_data import (
        SHOP_DATA,
        SHOP_DATA_VERSION,
        SHOP_ID_ALIASES,
        SHOP_SERVICES,
        SHOP_VENDOR_ACTIONS,
    )
except ImportError:
    from shop_data import (
        SHOP_DATA,
        SHOP_DATA_VERSION,
        SHOP_ID_ALIASES,
        SHOP_SERVICES,
        SHOP_VENDOR_ACTIONS,
    )


MAX_SHOP_EVENT_HISTORY = 200


def default_shop_state_pure() -> Dict[str, Any]:
    return {
        "shop_data_version": SHOP_DATA_VERSION,
        "shop_market_clock": {"version": 1, "answered_cards": 0, "market_tick": 0},
        "shop_stock_state": {},
        "shop_events": [],
        "shop_next_event_id": 1,
    }


def sanitize_shop_state_pure(raw: Mapping[str, Any] | None) -> Dict[str, Any]:
    defaults = default_shop_state_pure()
    data = dict(raw or {})

    clock = data.get("shop_market_clock")
    clean_clock = dict(defaults["shop_market_clock"])
    if isinstance(clock, Mapping):
        clean_clock["version"] = _clean_int(clock.get("version"), 1, minimum=1)
        clean_clock["answered_cards"] = _clean_int(clock.get("answered_cards"), 0, minimum=0)
        clean_clock["market_tick"] = _clean_int(clock.get("market_tick"), 0, minimum=0)

    clean_stock: Dict[str, Any] = {}
    raw_stock = data.get("shop_stock_state")
    if isinstance(raw_stock, Mapping):
        for group_id, group_state in raw_stock.items():
            if not isinstance(group_id, str) or not isinstance(group_state, Mapping):
                continue
            clean_rows: Dict[str, Any] = {}
            raw_rows = group_state.get("rows")
            if isinstance(raw_rows, Mapping):
                for row_id, row_state in raw_rows.items():
                    if not isinstance(row_id, str) or not isinstance(row_state, Mapping):
                        continue
                    current_quantity = _clean_int(row_state.get("current_quantity"), 0, minimum=0)
                    default_quantity = _clean_int(row_state.get("default_quantity"), 0, minimum=0)
                    if current_quantity == default_quantity and not bool(row_state.get("temporary")):
                        continue
                    clean_rows[row_id] = {
                        "item_id": _clean_int(row_state.get("item_id"), -1, minimum=-1),
                        "item_name": str(row_state.get("item_name", "")),
                        "current_quantity": current_quantity,
                        "default_quantity": default_quantity,
                        "restock_ticks": _clean_int(row_state.get("restock_ticks"), 50, minimum=1),
                        "restock_amount": _clean_int(row_state.get("restock_amount"), 1, minimum=1),
                        "buy_price": _clean_optional_int(row_state.get("buy_price")),
                        "sell_price": _clean_optional_int(row_state.get("sell_price")),
                        "tradeable": bool(row_state.get("tradeable", True)),
                        "temporary": bool(row_state.get("temporary", False)),
                    }
            if clean_rows:
                clean_stock[group_id] = {
                    "shop_id": str(group_state.get("shop_id", "")),
                    "last_market_tick": _clean_int(group_state.get("last_market_tick"), clean_clock["market_tick"], minimum=0),
                    "rows": clean_rows,
                }

    raw_events = data.get("shop_events")
    clean_events = [dict(event) for event in raw_events if isinstance(event, Mapping)] if isinstance(raw_events, list) else []
    return {
        "shop_data_version": SHOP_DATA_VERSION,
        "shop_market_clock": clean_clock,
        "shop_stock_state": clean_stock,
        "shop_events": clean_events[-MAX_SHOP_EVENT_HISTORY:],
        "shop_next_event_id": _clean_int(data.get("shop_next_event_id"), 1, minimum=1),
    }


def ensure_shop_state_pure(player_data: Mapping[str, Any] | None) -> Dict[str, Any]:
    data = copy.deepcopy(dict(player_data or {}))
    data.update(sanitize_shop_state_pure(data))
    return data


def advance_shop_market_clock_pure(player_data: Mapping[str, Any], answered_cards: int = 1) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    increment = max(0, int(answered_cards))
    clock = dict(data["shop_market_clock"])
    clock["answered_cards"] += increment
    clock["market_tick"] += increment
    data["shop_market_clock"] = clock
    return data


def resolve_shop_id(shop_id: str) -> str:
    return SHOP_ID_ALIASES.get(shop_id, shop_id)


def shop_view_model_pure(player_data: Mapping[str, Any], shop_id: str) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    shop = _shop_or_none(shop_id)
    if shop is None:
        return {"exists": False, "shop_id": shop_id, "rows": []}
    group_state = _view_group_state(data, shop)
    rows = []
    seen_row_ids = set()
    for row in shop["stock"]:
        row_state = group_state["rows"].get(row["id"], _state_row_from_definition(row))
        rows.append(_row_view(row, row_state, shop))
        seen_row_ids.add(row["id"])
    for row_id, row_state in sorted(group_state["rows"].items()):
        if row_id in seen_row_ids or not bool(row_state.get("temporary")):
            continue
        rows.append(_row_view(_temporary_row_definition(row_id, row_state), row_state, shop))
    return {
        "exists": True,
        "shop_id": shop["id"],
        "display_name": shop["display_name"],
        "currency_item_name": shop["currency_item_name"],
        "currency_implemented": shop["currency_implemented"],
        "general_store": shop["general_store"],
        "buy_only": shop["buy_only"],
        "shared_stock_group": shop["shared_stock_group"],
        "visibility": shop["visibility"],
        "lock_reason": shop["lock_reason"],
        "market_tick": data["shop_market_clock"]["market_tick"],
        "rows": rows,
    }


def search_shop_catalog_pure(
    player_data: Mapping[str, Any],
    query: str,
    *,
    include_locked: bool = True,
    include_hidden: bool = False,
    limit: int = 50,
) -> Dict[str, Any]:
    normalized = query.strip().lower()
    data = ensure_shop_state_pure(player_data)
    results = []
    for shop in SHOP_DATA.values():
        if shop["visibility"] == "hidden" and not include_hidden:
            continue
        if shop["visibility"] == "visible_locked" and not include_locked:
            continue
        view = shop_view_model_pure(data, shop["id"])
        for row in view["rows"]:
            haystack = f"{row['item_name']} {shop['display_name']}".lower()
            if normalized and normalized not in haystack:
                continue
            results.append(
                {
                    "kind": "stock",
                    "shop_id": shop["id"],
                    "shop_name": shop["display_name"],
                    "row_id": row["id"],
                    "item_name": row["item_name"],
                    "current_quantity": row["current_quantity"],
                    "default_quantity": row["default_quantity"],
                    "buy_price": row["buy_price"],
                    "sell_price": row["sell_price"],
                    "visibility": row["visibility"],
                    "lock_reason": row["lock_reason"],
                }
            )
    for service in list(SHOP_SERVICES.values()) + list(SHOP_VENDOR_ACTIONS.values()):
        haystack = " ".join(
            [service["display_name"], service.get("provider", "")]
            + [item["item_name"] for item in service.get("inputs", [])]
            + [item["item_name"] for item in service.get("outputs", [])]
        ).lower()
        if normalized and normalized not in haystack:
            continue
        results.append(
            {
                "kind": "service" if service["id"] in SHOP_SERVICES else "vendor_action",
                "id": service["id"],
                "display_name": service["display_name"],
                "provider": service.get("provider", ""),
                "price": service.get("price", 0),
                "currency_item_name": service.get("currency_item_name", "Coins"),
                "visibility": service.get("visibility", "visible"),
                "lock_reason": service.get("lock_reason", ""),
            }
        )
    return {"query": query, "results": results[: max(0, limit)]}


def preview_shop_buy_pure(player_data: Mapping[str, Any], shop_id: str, row_id: str, quantity: int = 1) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    shop = _shop_or_none(shop_id)
    if shop is None:
        return _denied("unknown_shop", requested_quantity=quantity)
    group_state = _view_group_state(data, shop)
    row = _row_definition(shop, row_id)
    if row is None:
        row = _temporary_row_definition_from_group(row_id, group_state)
    if row is None:
        return _denied("unknown_stock_row", requested_quantity=quantity, shop_id=shop["id"])
    return _preview_buy_from_state(data, shop, row, group_state, quantity)


def apply_shop_buy_pure(player_data: Mapping[str, Any], shop_id: str, row_id: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_shop_state_pure(player_data)
    shop = _shop_or_none(shop_id)
    if shop is None:
        return data, _denied("unknown_shop", requested_quantity=quantity)
    group_state = _transaction_group_state(data, shop)
    row = _row_definition(shop, row_id)
    if row is None:
        row = _temporary_row_definition_from_group(row_id, group_state)
    if row is None:
        return data, _denied("unknown_stock_row", requested_quantity=quantity, shop_id=shop["id"])
    preview = _preview_buy_from_state(data, shop, row, group_state, quantity)
    if not preview["allowed"]:
        data["shop_stock_state"][shop["shared_stock_group"]] = _compress_group_state(group_state)
        return data, preview

    item_name = row["item_name"]
    currency_name = shop["currency_item_name"]
    before_row = copy.deepcopy(group_state["rows"][row["id"]])
    amount = preview["quantity"]
    total_price = preview["total_price"]
    _add_inventory(data, currency_name, -total_price)
    _add_inventory(data, item_name, amount)
    group_state["rows"][row["id"]]["current_quantity"] = max(0, before_row["current_quantity"] - amount)
    after_row = copy.deepcopy(group_state["rows"][row["id"]])
    data["shop_stock_state"][shop["shared_stock_group"]] = _compress_group_state(group_state)
    event = _build_event(
        data,
        "buy",
        shop,
        quantity=amount,
        row_id=row["id"],
        item_name=item_name,
        total_price=total_price,
        inventory_delta={currency_name: -total_price, item_name: amount},
        stock_set={shop["shared_stock_group"]: {row["id"]: before_row}},
        stock_delta={shop["shared_stock_group"]: {row["id"]: {"before": before_row, "after": after_row}}},
    )
    _append_event(data, event)
    result = dict(preview)
    result["event_id"] = event["event_id"]
    return data, result


def preview_shop_sell_pure(player_data: Mapping[str, Any], shop_id: str, item_name: str, quantity: int = 1) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    shop = _shop_or_none(shop_id)
    if shop is None:
        return _denied("unknown_shop", requested_quantity=quantity)
    group_state = _view_group_state(data, shop)
    return _preview_sell_from_state(data, shop, group_state, item_name, quantity)


def apply_shop_sell_pure(player_data: Mapping[str, Any], shop_id: str, item_name: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_shop_state_pure(player_data)
    shop = _shop_or_none(shop_id)
    if shop is None:
        return data, _denied("unknown_shop", requested_quantity=quantity)
    group_state = _transaction_group_state(data, shop)
    preview = _preview_sell_from_state(data, shop, group_state, item_name, quantity)
    if not preview["allowed"]:
        data["shop_stock_state"][shop["shared_stock_group"]] = _compress_group_state(group_state)
        return data, preview

    amount = preview["quantity"]
    currency_name = shop["currency_item_name"]
    total_price = preview["total_price"]
    row_id = preview["row_id"]
    before_row = copy.deepcopy(group_state["rows"].get(row_id)) if row_id in group_state["rows"] else None
    if row_id not in group_state["rows"]:
        group_state["rows"][row_id] = _temporary_stock_row(item_name, preview["unit_price"])
    group_state["rows"][row_id]["current_quantity"] += amount
    after_row = copy.deepcopy(group_state["rows"][row_id])
    _add_inventory(data, item_name, -amount)
    _add_inventory(data, currency_name, total_price)
    data["shop_stock_state"][shop["shared_stock_group"]] = _compress_group_state(group_state)
    event = _build_event(
        data,
        "sell",
        shop,
        quantity=amount,
        row_id=row_id,
        item_name=item_name,
        total_price=total_price,
        inventory_delta={item_name: -amount, currency_name: total_price},
        stock_set={shop["shared_stock_group"]: {row_id: before_row}},
        stock_delta={shop["shared_stock_group"]: {row_id: {"before": before_row, "after": after_row}}},
    )
    _append_event(data, event)
    result = dict(preview)
    result["event_id"] = event["event_id"]
    return data, result


def preview_shop_service_pure(player_data: Mapping[str, Any], service_id: str, quantity: int = 1) -> Dict[str, Any]:
    service = SHOP_SERVICES.get(service_id)
    if service is None:
        return _denied("unknown_service", requested_quantity=quantity)
    return _preview_service_like(player_data, service, quantity)


def apply_shop_service_pure(player_data: Mapping[str, Any], service_id: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    service = SHOP_SERVICES.get(service_id)
    data = ensure_shop_state_pure(player_data)
    if service is None:
        return data, _denied("unknown_service", requested_quantity=quantity)
    return _apply_service_like(data, service, "service", quantity)


def preview_shop_vendor_action_pure(player_data: Mapping[str, Any], action_id: str, quantity: int = 1) -> Dict[str, Any]:
    action = SHOP_VENDOR_ACTIONS.get(action_id)
    if action is None:
        return _denied("unknown_vendor_action", requested_quantity=quantity)
    return _preview_service_like(player_data, action, quantity)


def apply_shop_vendor_action_pure(player_data: Mapping[str, Any], action_id: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    action = SHOP_VENDOR_ACTIONS.get(action_id)
    data = ensure_shop_state_pure(player_data)
    if action is None:
        return data, _denied("unknown_vendor_action", requested_quantity=quantity)
    return _apply_service_like(data, action, "vendor_action", quantity)


def apply_shop_transaction_pure(player_data: Mapping[str, Any], transaction_type: str, **kwargs: Any) -> tuple[Dict[str, Any], Dict[str, Any]]:
    if transaction_type == "buy":
        return apply_shop_buy_pure(player_data, str(kwargs.get("shop_id", "")), str(kwargs.get("row_id", "")), int(kwargs.get("quantity", 1)))
    if transaction_type == "sell":
        return apply_shop_sell_pure(player_data, str(kwargs.get("shop_id", "")), str(kwargs.get("item_name", "")), int(kwargs.get("quantity", 1)))
    if transaction_type == "service":
        return apply_shop_service_pure(player_data, str(kwargs.get("service_id", "")), int(kwargs.get("quantity", 1)))
    if transaction_type == "vendor_action":
        return apply_shop_vendor_action_pure(player_data, str(kwargs.get("action_id", "")), int(kwargs.get("quantity", 1)))
    return ensure_shop_state_pure(player_data), _denied("unknown_transaction_type", transaction_type=transaction_type)


def rollback_shop_event_pure(player_data: Mapping[str, Any], event_id: Optional[str] = None) -> tuple[Dict[str, Any], Dict[str, Any]]:
    data = ensure_shop_state_pure(player_data)
    event = _event_by_id(data, event_id) if event_id else _last_rollbackable_event(data)
    if event is None:
        return data, _denied("unknown_shop_event")
    inverse = event.get("inverse", {})
    inventory_delta = inverse.get("inventory_delta", {})
    if isinstance(inventory_delta, Mapping):
        for item_name, delta in inventory_delta.items():
            if isinstance(item_name, str):
                _add_inventory(data, item_name, _clean_int(delta, 0))
    stock_set = inverse.get("stock_set", {})
    if isinstance(stock_set, Mapping):
        for group_id, rows in stock_set.items():
            if not isinstance(group_id, str) or not isinstance(rows, Mapping):
                continue
            group_state = copy.deepcopy(data.get("shop_stock_state", {}).get(group_id, {"shop_id": "", "last_market_tick": data["shop_market_clock"]["market_tick"], "rows": {}}))
            group_state.setdefault("rows", {})
            for row_id, before_row in rows.items():
                if not isinstance(row_id, str):
                    continue
                if before_row is None:
                    group_state["rows"].pop(row_id, None)
                elif isinstance(before_row, Mapping):
                    group_state["rows"][row_id] = copy.deepcopy(dict(before_row))
            compressed = _compress_group_state(group_state)
            if compressed["rows"]:
                data["shop_stock_state"][group_id] = compressed
            else:
                data["shop_stock_state"].pop(group_id, None)
    rollback_event = {
        "event_id": _next_event_id(data),
        "type": "rollback",
        "rolled_back_event_id": event["event_id"],
        "market_tick": data["shop_market_clock"]["market_tick"],
        "display": f"Rolled back {event.get('display', event['event_id'])}",
    }
    _append_event(data, rollback_event)
    return data, {"allowed": True, "event_id": rollback_event["event_id"], "rolled_back_event_id": event["event_id"]}


def shop_history_rows_pure(player_data: Mapping[str, Any], shop_id: Optional[str] = None, limit: int = 20) -> list[Dict[str, Any]]:
    data = ensure_shop_state_pure(player_data)
    events = data.get("shop_events", [])
    if shop_id:
        canonical = resolve_shop_id(shop_id)
        events = [event for event in events if event.get("shop_id") == canonical]
    return [dict(event) for event in events[-max(0, limit):]][::-1]


def _clean_int(value: Any, default: int, *, minimum: int | None = None) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError):
        out = default
    if minimum is not None:
        out = max(minimum, out)
    return out


def _clean_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _shop_or_none(shop_id: str) -> Optional[Dict[str, Any]]:
    return SHOP_DATA.get(resolve_shop_id(shop_id))


def _row_definition(shop: Mapping[str, Any], row_id: str) -> Optional[Dict[str, Any]]:
    for row in shop.get("stock", []):
        if row.get("id") == row_id:
            return row
    return None


def _temporary_row_definition_from_group(row_id: str, group_state: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    row_state = group_state.get("rows", {}).get(row_id)
    if not isinstance(row_state, Mapping) or not bool(row_state.get("temporary")):
        return None
    return _temporary_row_definition(row_id, row_state)


def _temporary_row_definition(row_id: str, row_state: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "id": row_id,
        "item_id": _clean_int(row_state.get("item_id"), -1, minimum=-1),
        "item_name": str(row_state.get("item_name", "")),
        "default_quantity": _clean_int(row_state.get("default_quantity"), 0, minimum=0),
        "current_quantity": _clean_int(row_state.get("current_quantity"), 0, minimum=0),
        "restock_ticks": _clean_int(row_state.get("restock_ticks"), 50, minimum=1),
        "restock_amount": _clean_int(row_state.get("restock_amount"), 1, minimum=1),
        "buy_price": _clean_optional_int(row_state.get("buy_price")),
        "sell_price": _clean_optional_int(row_state.get("sell_price")),
        "tradeable": bool(row_state.get("tradeable", True)),
        "visibility": "visible",
        "lock_reason": "",
        "disposition": "live",
        "source": "player_sold_temp_stock",
        "source_path": "",
    }


def _state_row_from_definition(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "item_id": row["item_id"],
        "item_name": row["item_name"],
        "current_quantity": _clean_int(row.get("current_quantity", row.get("default_quantity", 0)), 0, minimum=0),
        "default_quantity": _clean_int(row.get("default_quantity"), 0, minimum=0),
        "restock_ticks": _clean_int(row.get("restock_ticks"), 50, minimum=1),
        "restock_amount": _clean_int(row.get("restock_amount"), 1, minimum=1),
        "buy_price": _clean_optional_int(row.get("buy_price")),
        "sell_price": _clean_optional_int(row.get("sell_price")),
        "tradeable": bool(row.get("tradeable", True)),
        "temporary": False,
    }


def _view_group_state(data: Mapping[str, Any], shop: Mapping[str, Any]) -> Dict[str, Any]:
    group_id = shop["shared_stock_group"]
    existing = data.get("shop_stock_state", {}).get(group_id)
    if isinstance(existing, Mapping):
        group_state = copy.deepcopy(dict(existing))
        group_state.setdefault("rows", {})
    else:
        group_state = {"shop_id": shop["id"], "last_market_tick": data["shop_market_clock"]["market_tick"], "rows": {}}
    for row in shop["stock"]:
        group_state["rows"].setdefault(row["id"], _state_row_from_definition(row))
    _apply_restock_to_group_state(group_state, data["shop_market_clock"]["market_tick"])
    return group_state


def _transaction_group_state(data: Dict[str, Any], shop: Mapping[str, Any]) -> Dict[str, Any]:
    group_state = _view_group_state(data, shop)
    data.setdefault("shop_stock_state", {})
    data["shop_stock_state"][shop["shared_stock_group"]] = _compress_group_state(group_state)
    return group_state


def _compress_group_state(group_state: Mapping[str, Any]) -> Dict[str, Any]:
    rows = {}
    for row_id, row in group_state.get("rows", {}).items():
        if not isinstance(row_id, str) or not isinstance(row, Mapping):
            continue
        current_quantity = _clean_int(row.get("current_quantity"), 0, minimum=0)
        default_quantity = _clean_int(row.get("default_quantity"), 0, minimum=0)
        temporary = bool(row.get("temporary", False))
        if not temporary and current_quantity == default_quantity:
            continue
        if temporary and current_quantity <= 0:
            continue
        clean_row = dict(row)
        clean_row["current_quantity"] = current_quantity
        clean_row["default_quantity"] = default_quantity
        rows[row_id] = clean_row
    return {
        "shop_id": str(group_state.get("shop_id", "")),
        "last_market_tick": _clean_int(group_state.get("last_market_tick"), 0, minimum=0),
        "rows": rows,
    }


def _apply_restock_to_group_state(group_state: Dict[str, Any], market_tick: int) -> None:
    last_market_tick = _clean_int(group_state.get("last_market_tick"), market_tick, minimum=0)
    elapsed = max(0, market_tick - last_market_tick)
    if elapsed <= 0:
        return
    for row_id in list(group_state.get("rows", {})):
        row = group_state["rows"][row_id]
        current = _clean_int(row.get("current_quantity"), 0, minimum=0)
        default = _clean_int(row.get("default_quantity"), 0, minimum=0)
        if current == default:
            continue
        steps = elapsed // _clean_int(row.get("restock_ticks"), 50, minimum=1)
        if steps <= 0:
            continue
        delta = steps * _clean_int(row.get("restock_amount"), 1, minimum=1)
        if current < default:
            row["current_quantity"] = min(default, current + delta)
        else:
            row["current_quantity"] = max(default, current - delta)
        if bool(row.get("temporary")) and row["current_quantity"] <= 0:
            group_state["rows"].pop(row_id, None)
    group_state["last_market_tick"] = market_tick


def _row_view(row: Mapping[str, Any], row_state: Mapping[str, Any], shop: Mapping[str, Any]) -> Dict[str, Any]:
    can_buy = row["disposition"] == "live" and shop["visibility"] == "visible" and bool(shop["currency_implemented"])
    return {
        "id": row["id"],
        "item_id": row["item_id"],
        "item_name": row["item_name"],
        "current_quantity": _clean_int(row_state.get("current_quantity"), 0, minimum=0),
        "default_quantity": row["default_quantity"],
        "buy_price": row["buy_price"],
        "sell_price": row["sell_price"],
        "visibility": row["visibility"],
        "lock_reason": row["lock_reason"],
        "disposition": row["disposition"],
        "can_buy": can_buy,
        "can_sell_to_shop": not bool(shop["buy_only"]) and (bool(shop["general_store"]) or row["disposition"] == "live"),
        "source": row["source"],
        "source_path": row["source_path"],
    }


def _preview_buy_from_state(
    data: Mapping[str, Any],
    shop: Mapping[str, Any],
    row: Mapping[str, Any],
    group_state: Mapping[str, Any],
    quantity: int,
) -> Dict[str, Any]:
    requested = max(1, int(quantity))
    if shop["visibility"] != "visible":
        return _denied(shop.get("lock_reason") or "shop_not_visible", requested_quantity=requested, shop_id=shop["id"], row_id=row["id"])
    if row["disposition"] != "live":
        return _denied(row.get("lock_reason") or "stock_row_not_live", requested_quantity=requested, shop_id=shop["id"], row_id=row["id"])
    unit_price = _clean_optional_int(row.get("buy_price"))
    if unit_price is None:
        return _denied("price_policy_unresolved", requested_quantity=requested, shop_id=shop["id"], row_id=row["id"])
    row_state = group_state["rows"].get(row["id"], _state_row_from_definition(row))
    current_quantity = _clean_int(row_state.get("current_quantity"), 0, minimum=0)
    if current_quantity <= 0:
        return _denied("out_of_stock", requested_quantity=requested, shop_id=shop["id"], row_id=row["id"])
    currency_name = shop["currency_item_name"]
    affordable = _inventory_count(data, currency_name) // max(1, unit_price)
    quantity_allowed = min(requested, current_quantity, affordable)
    if quantity_allowed <= 0:
        return _denied("insufficient_currency", requested_quantity=requested, shop_id=shop["id"], row_id=row["id"], unit_price=unit_price)
    return {
        "allowed": True,
        "transaction_type": "buy",
        "shop_id": shop["id"],
        "row_id": row["id"],
        "item_name": row["item_name"],
        "requested_quantity": requested,
        "quantity": quantity_allowed,
        "clamped": quantity_allowed != requested,
        "unit_price": unit_price,
        "total_price": unit_price * quantity_allowed,
        "currency_item_name": currency_name,
    }


def _preview_sell_from_state(
    data: Mapping[str, Any],
    shop: Mapping[str, Any],
    group_state: Mapping[str, Any],
    item_name: str,
    quantity: int,
) -> Dict[str, Any]:
    requested = max(1, int(quantity))
    if shop["visibility"] != "visible":
        return _denied(shop.get("lock_reason") or "shop_not_visible", requested_quantity=requested, shop_id=shop["id"])
    if shop["buy_only"]:
        return _denied("shop_buy_only", requested_quantity=requested, shop_id=shop["id"])
    if _inventory_count(data, item_name) <= 0:
        return _denied("missing_item", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)

    stocked_row = _stocked_row_for_item(shop, item_name)
    if not shop["general_store"] and stocked_row is None:
        return _denied("specialist_shop_stock_only", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)
    if not _item_tradeable(item_name):
        return _denied("item_not_tradeable", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)

    unit_price = None
    row_id = f"{shop['id']}:temporary:{_item_slug(item_name)}"
    if stocked_row is not None:
        row_id = stocked_row["id"]
        unit_price = _clean_optional_int(stocked_row.get("sell_price"))
    if unit_price is None:
        unit_price = _sell_price_for_item(item_name)
    if unit_price is None:
        return _denied("sell_price_unresolved", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)
    amount = min(requested, _inventory_count(data, item_name))
    return {
        "allowed": True,
        "transaction_type": "sell",
        "shop_id": shop["id"],
        "row_id": row_id,
        "item_name": item_name,
        "requested_quantity": requested,
        "quantity": amount,
        "clamped": amount != requested,
        "unit_price": unit_price,
        "total_price": unit_price * amount,
        "currency_item_name": shop["currency_item_name"],
        "temporary_stock": row_id not in group_state.get("rows", {}),
    }


def _preview_service_like(player_data: Mapping[str, Any], service: Mapping[str, Any], quantity: int) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    requested = max(1, int(quantity))
    if service.get("visibility") != "visible":
        return _denied(service.get("lock_reason") or "service_not_visible", requested_quantity=requested, service_id=service["id"])
    currency_name = str(service.get("currency_item_name", "Coins"))
    unit_price = _clean_int(service.get("price"), 0, minimum=0)
    max_quantity = requested
    if unit_price:
        max_quantity = min(max_quantity, _inventory_count(data, currency_name) // unit_price)
    for item in service.get("inputs", []):
        max_quantity = min(max_quantity, _inventory_count(data, item["item_name"]) // max(1, int(item["quantity"])))
    if max_quantity <= 0:
        return _denied("missing_requirements", requested_quantity=requested, service_id=service["id"], unit_price=unit_price)
    return {
        "allowed": True,
        "transaction_type": "service_like",
        "id": service["id"],
        "display_name": service["display_name"],
        "requested_quantity": requested,
        "quantity": max_quantity,
        "clamped": max_quantity != requested,
        "unit_price": unit_price,
        "total_price": unit_price * max_quantity,
        "currency_item_name": currency_name,
    }


def _apply_service_like(data: Dict[str, Any], service: Mapping[str, Any], event_type: str, quantity: int) -> tuple[Dict[str, Any], Dict[str, Any]]:
    preview = _preview_service_like(data, service, quantity)
    if not preview["allowed"]:
        return data, preview
    amount = preview["quantity"]
    inventory_delta: Dict[str, int] = {}
    currency_name = preview["currency_item_name"]
    if preview["total_price"]:
        inventory_delta[currency_name] = inventory_delta.get(currency_name, 0) - preview["total_price"]
    for item in service.get("inputs", []):
        inventory_delta[item["item_name"]] = inventory_delta.get(item["item_name"], 0) - int(item["quantity"]) * amount
    for item in service.get("outputs", []):
        inventory_delta[item["item_name"]] = inventory_delta.get(item["item_name"], 0) + int(item["quantity"]) * amount
    for item_name, delta in inventory_delta.items():
        _add_inventory(data, item_name, delta)
    event = _build_event(
        data,
        event_type,
        {"id": "", "display_name": service["display_name"], "shared_stock_group": ""},
        quantity=amount,
        service_id=service["id"],
        item_name=service["display_name"],
        total_price=preview["total_price"],
        inventory_delta=inventory_delta,
        stock_set={},
        stock_delta={},
    )
    _append_event(data, event)
    result = dict(preview)
    result["event_id"] = event["event_id"]
    return data, result


def _denied(reason: str, **extra: Any) -> Dict[str, Any]:
    return {"allowed": False, "reason": reason, **extra}


def _inventory_count(data: Mapping[str, Any], item_name: str) -> int:
    inventory = data.get("inventory")
    if not isinstance(inventory, Mapping):
        return 0
    return _clean_int(inventory.get(item_name), 0, minimum=0)


def _add_inventory(data: Dict[str, Any], item_name: str, delta: int) -> None:
    data.setdefault("inventory", {})
    data["inventory"][item_name] = max(0, _inventory_count(data, item_name) + int(delta))


def _stocked_row_for_item(shop: Mapping[str, Any], item_name: str) -> Optional[Dict[str, Any]]:
    for row in shop.get("stock", []):
        if row.get("item_name") == item_name and row.get("disposition") != "blocked":
            return row
    return None


def _item_tradeable(item_name: str) -> bool:
    for shop in SHOP_DATA.values():
        for row in shop.get("stock", []):
            if row.get("item_name") == item_name:
                return bool(row.get("tradeable", False))
    for collection in (SHOP_SERVICES, SHOP_VENDOR_ACTIONS):
        for spec in collection.values():
            for item in list(spec.get("inputs", [])) + list(spec.get("outputs", [])):
                if item.get("item_name") == item_name:
                    return bool(item.get("tradeable", False))
    return True


def _sell_price_for_item(item_name: str) -> Optional[int]:
    prices = []
    for shop in SHOP_DATA.values():
        for row in shop.get("stock", []):
            if row.get("item_name") == item_name:
                sell_price = _clean_optional_int(row.get("sell_price"))
                if sell_price is not None:
                    prices.append(sell_price)
    for action in SHOP_VENDOR_ACTIONS.values():
        for item in action.get("outputs", []):
            if item.get("item_name") == item_name:
                price = _clean_int(action.get("price"), 0, minimum=0)
                if price > 0:
                    prices.append(max(1, price // 3))
    if not prices:
        return None
    return min(prices)


def _temporary_stock_row(item_name: str, unit_price: int) -> Dict[str, Any]:
    return {
        "item_id": -1,
        "item_name": item_name,
        "current_quantity": 0,
        "default_quantity": 0,
        "restock_ticks": 50,
        "restock_amount": 1,
        "buy_price": max(1, unit_price * 3),
        "sell_price": unit_price,
        "tradeable": _item_tradeable(item_name),
        "temporary": True,
    }


def _item_slug(item_name: str) -> str:
    return "_".join(part for part in item_name.lower().replace("'", "").split() if part) or "item"


def _build_event(
    data: Dict[str, Any],
    event_type: str,
    shop: Mapping[str, Any],
    *,
    quantity: int,
    item_name: str,
    total_price: int,
    inventory_delta: Mapping[str, int],
    stock_set: Mapping[str, Mapping[str, Any]],
    stock_delta: Mapping[str, Any],
    row_id: str | None = None,
    service_id: str | None = None,
) -> Dict[str, Any]:
    inverse_inventory = {item_name: -int(delta) for item_name, delta in inventory_delta.items()}
    event = {
        "event_id": _next_event_id(data),
        "type": event_type,
        "shop_id": shop.get("id", ""),
        "row_id": row_id,
        "service_id": service_id,
        "item_name": item_name,
        "quantity": quantity,
        "total_price": total_price,
        "market_tick": data["shop_market_clock"]["market_tick"],
        "inventory_delta": dict(inventory_delta),
        "stock_delta": copy.deepcopy(dict(stock_delta)),
        "inverse": {
            "inventory_delta": inverse_inventory,
            "stock_set": copy.deepcopy(dict(stock_set)),
        },
        "display": _event_display(event_type, shop, item_name, quantity),
    }
    return event


def _event_display(event_type: str, shop: Mapping[str, Any], item_name: str, quantity: int) -> str:
    shop_name = shop.get("display_name") or "NPC shop"
    if event_type == "buy":
        return f"Bought {quantity} x {item_name} from {shop_name}"
    if event_type == "sell":
        return f"Sold {quantity} x {item_name} to {shop_name}"
    if event_type == "service":
        return f"Used {shop_name} {quantity} time(s)"
    if event_type == "vendor_action":
        return f"Completed {shop_name} {quantity} time(s)"
    return f"{event_type}: {item_name}"


def _next_event_id(data: Dict[str, Any]) -> str:
    current = _clean_int(data.get("shop_next_event_id"), 1, minimum=1)
    data["shop_next_event_id"] = current + 1
    return f"shop_evt_{current}"


def _append_event(data: Dict[str, Any], event: Mapping[str, Any]) -> None:
    events = data.setdefault("shop_events", [])
    if not isinstance(events, list):
        events = []
        data["shop_events"] = events
    events.append(copy.deepcopy(dict(event)))
    if len(events) > MAX_SHOP_EVENT_HISTORY:
        del events[:-MAX_SHOP_EVENT_HISTORY]


def _event_by_id(data: Mapping[str, Any], event_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not event_id:
        return None
    for event in data.get("shop_events", []):
        if isinstance(event, Mapping) and event.get("event_id") == event_id:
            return copy.deepcopy(dict(event))
    return None


def _last_rollbackable_event(data: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    for event in reversed(data.get("shop_events", [])):
        if isinstance(event, Mapping) and event.get("type") != "rollback" and isinstance(event.get("inverse"), Mapping):
            return copy.deepcopy(dict(event))
    return None
