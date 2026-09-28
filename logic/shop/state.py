"""Pure shop state, stock, inventory, and transaction history operations."""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Mapping, Optional

from ...data.shop_data import (
    SHOP_DATA,
    SHOP_DATA_VERSION,
    SHOP_ID_ALIASES,
    SHOP_PLAYER_BUY_PRICES,
    SHOP_PLAYER_SELL_PRICES,
    SHOP_SERVICES,
    SHOP_VENDOR_ACTIONS,
)
from ...data.crafting_data import LEGACY_CRAFTING_ITEM_MIGRATIONS
from ...core.constants import EXTRA_ITEM_DATA
from ...logic_pure.shop_diary_transactions import (
    SHOP_DIARY_TRANSACTION_KEYS,
    shop_diary_transaction_counter_key_pure,
)


MAX_SHOP_EVENT_HISTORY = 200
_CANONICAL_SHOP_ROW_NAMES = {
    str(row["id"]): str(row["item_name"])
    for shop in SHOP_DATA.values()
    for row in shop.get("stock", ())
}


def default_shop_state_pure() -> Dict[str, Any]:
    return {
        "shop_data_version": SHOP_DATA_VERSION,
        "shop_market_clock": {"version": 1, "answered_cards": 0, "market_tick": 0},
        "shop_stock_state": {},
        "shop_events": [],
        "shop_transaction_counts": {},
        "shop_next_event_id": 1,
        "wilderness_shop_slots": 0,
    }


def sanitize_shop_state_pure(raw: Mapping[str, Any] | None) -> Dict[str, Any]:
    data = dict(raw or {})
    clean_clock = _sanitize_market_clock(data.get("shop_market_clock"))
    return {
        "shop_data_version": SHOP_DATA_VERSION,
        "shop_market_clock": clean_clock,
        "shop_stock_state": _sanitize_stock_state(data.get("shop_stock_state"), clean_clock["market_tick"]),
        "shop_events": _sanitize_shop_events(data.get("shop_events")),
        "shop_transaction_counts": _sanitize_transaction_counts(data.get("shop_transaction_counts")),
        "shop_next_event_id": _clean_int(data.get("shop_next_event_id"), 1, minimum=1),
        "wilderness_shop_slots": _clean_int(data.get("wilderness_shop_slots"), 0, minimum=0),
    }


def ensure_shop_state_pure(player_data: Mapping[str, Any] | None) -> Dict[str, Any]:
    # Deep copy is load-bearing: the vendor/buy paths mutate data["inventory"]
    # and nested stock rows in place, so a shallow copy would write through to
    # the caller's live save. Do not "optimize" this one.
    data = copy.deepcopy(dict(player_data or {}))
    data.update(sanitize_shop_state_pure(data))
    return data


def migrate_shop_diary_transaction_counts_pure(
    player_data: Mapping[str, Any] | None,
) -> Dict[str, Any]:
    """Seed narrow counters from retained events without erasing durable totals."""

    data = ensure_shop_state_pure(player_data)
    events = data["shop_events"]
    rolled_back = {
        str(event.get("rolled_back_event_id", ""))
        for event in events
        if event.get("type") == "rollback"
    }
    retained_counts: Dict[str, int] = {}
    for event in events:
        if str(event.get("event_id", "")) in rolled_back:
            continue
        key = _diary_transaction_key(event)
        if key:
            retained_counts[key] = retained_counts.get(key, 0) + 1
    counts = dict(data.get("shop_transaction_counts", {}) or {})
    for key, retained in retained_counts.items():
        counts[key] = max(_clean_int(counts.get(key), 0, minimum=0), retained)
    data["shop_transaction_counts"] = counts
    return data


def advance_shop_market_clock_pure(player_data: Mapping[str, Any], answered_cards: int = 1) -> Dict[str, Any]:
    # This path mutates only the clock. Sanitizing returns fresh shop-owned nested
    # state, so the full save does not need the vendor paths' load-bearing deepcopy.
    data = dict(player_data or {})
    data.update(sanitize_shop_state_pure(data))
    increment = max(0, int(answered_cards))
    clock = dict(data["shop_market_clock"])
    clock["answered_cards"] += increment
    clock["market_tick"] += increment
    data["shop_market_clock"] = clock
    return data


def shop_access_lock_reason_pure(player_data: Mapping[str, Any], shop: Mapping[str, Any]) -> Optional[str]:
    """Owner-grilled access gates (2026-07-07): quest/route walls, guild
    skill walls, and quest-point walls evaluated against the save. Wilderness
    is access-open (its cost is the ambush risk, not a lock)."""
    rule = shop.get("access")
    if not isinstance(rule, Mapping):
        return None
    kind = rule.get("kind")
    label = str(rule.get("label", "access requirement"))
    lock_reason = _ACCESS_LOCK_REASONS.get(kind)
    if lock_reason is None:
        return None
    return lock_reason(player_data, rule, label)


def resolve_shop_id(shop_id: str) -> str:
    return SHOP_ID_ALIASES.get(shop_id, shop_id)


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


def _canonical_saved_shop_item_name(item_name: str, row_id: str = "", temporary: bool = False) -> str:
    if not temporary and row_id in _CANONICAL_SHOP_ROW_NAMES:
        return _CANONICAL_SHOP_ROW_NAMES[row_id]
    return LEGACY_CRAFTING_ITEM_MIGRATIONS.get(item_name, item_name)


def _migrate_item_delta_names(raw: Any) -> Any:
    if not isinstance(raw, Mapping):
        return raw
    migrated: Dict[str, Any] = {}
    for item_name, delta in raw.items():
        if not isinstance(item_name, str):
            continue
        canonical_name = _canonical_saved_shop_item_name(item_name)
        if isinstance(delta, int) and isinstance(migrated.get(canonical_name), int):
            migrated[canonical_name] += delta
        else:
            migrated[canonical_name] = delta
    return migrated


def _migrate_saved_stock_set_names(raw: Any) -> Any:
    if not isinstance(raw, Mapping):
        return raw
    migrated = copy.deepcopy(dict(raw))
    for rows in migrated.values():
        if not isinstance(rows, dict):
            continue
        for row_id, row_state in rows.items():
            if not isinstance(row_id, str) or not isinstance(row_state, dict):
                continue
            row_state["item_name"] = _canonical_saved_shop_item_name(
                str(row_state.get("item_name", "")), row_id, bool(row_state.get("temporary"))
            )
    return migrated


def _migrate_saved_shop_event_item_names(raw: Mapping[str, Any]) -> Dict[str, Any]:
    event = copy.deepcopy(dict(raw))
    row_id = str(event.get("row_id", "") or "")
    event["item_name"] = _canonical_saved_shop_item_name(str(event.get("item_name", "")), row_id)
    event["inventory_delta"] = _migrate_item_delta_names(event.get("inventory_delta"))
    inverse = event.get("inverse")
    if isinstance(inverse, dict):
        inverse["inventory_delta"] = _migrate_item_delta_names(inverse.get("inventory_delta"))
        inverse["stock_set"] = _migrate_saved_stock_set_names(inverse.get("stock_set"))
    return event


def _sanitize_market_clock(raw_clock: Any) -> Dict[str, int]:
    clean_clock = dict(default_shop_state_pure()["shop_market_clock"])
    if isinstance(raw_clock, Mapping):
        clean_clock["version"] = _clean_int(raw_clock.get("version"), 1, minimum=1)
        clean_clock["answered_cards"] = _clean_int(raw_clock.get("answered_cards"), 0, minimum=0)
        clean_clock["market_tick"] = _clean_int(raw_clock.get("market_tick"), 0, minimum=0)
    return clean_clock


def _sanitize_stock_state(raw_stock: Any, market_tick: int) -> Dict[str, Any]:
    clean_stock: Dict[str, Any] = {}
    if not isinstance(raw_stock, Mapping):
        return clean_stock
    for group_id, group_state in raw_stock.items():
        if not isinstance(group_id, str) or not isinstance(group_state, Mapping):
            continue
        clean_rows = _sanitize_stock_rows(group_state.get("rows"))
        if clean_rows:
            clean_stock[group_id] = {
                "shop_id": str(group_state.get("shop_id", "")),
                "last_market_tick": _clean_int(group_state.get("last_market_tick"), market_tick, minimum=0),
                "rows": clean_rows,
            }
    return clean_stock


def _sanitize_stock_rows(raw_rows: Any) -> Dict[str, Any]:
    clean_rows: Dict[str, Any] = {}
    if not isinstance(raw_rows, Mapping):
        return clean_rows
    for row_id, row_state in raw_rows.items():
        if not isinstance(row_id, str) or not isinstance(row_state, Mapping):
            continue
        clean_row = _sanitize_stock_row(row_id, row_state)
        if clean_row is not None:
            clean_rows[row_id] = clean_row
    return clean_rows


def _sanitize_stock_row(row_id: str, row_state: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    current_quantity = _clean_int(row_state.get("current_quantity"), 0, minimum=0)
    default_quantity = _clean_int(row_state.get("default_quantity"), 0, minimum=0)
    temporary = bool(row_state.get("temporary"))
    if current_quantity == default_quantity and not temporary:
        return None
    return {
        "item_id": _clean_int(row_state.get("item_id"), -1, minimum=-1),
        "item_name": _canonical_saved_shop_item_name(str(row_state.get("item_name", "")), row_id, temporary),
        "current_quantity": current_quantity,
        "default_quantity": default_quantity,
        "restock_ticks": _clean_int(row_state.get("restock_ticks"), 50, minimum=1),
        "restock_progress": _clean_int(row_state.get("restock_progress"), 0, minimum=0),
        "restock_amount": _clean_int(row_state.get("restock_amount"), 1, minimum=1),
        "buy_price": _clean_optional_int(row_state.get("buy_price")),
        "sell_price": _clean_optional_int(row_state.get("sell_price")),
        "tradeable": bool(row_state.get("tradeable", True)),
        "temporary": temporary,
    }


def _sanitize_shop_events(raw_events: Any) -> List[Dict[str, Any]]:
    if not isinstance(raw_events, list):
        return []
    events = [_migrate_saved_shop_event_item_names(event) for event in raw_events if isinstance(event, Mapping)]
    return events[-MAX_SHOP_EVENT_HISTORY:]


def _sanitize_transaction_counts(raw_counts: Any) -> Dict[str, int]:
    clean_counts: Dict[str, int] = {}
    if not isinstance(raw_counts, Mapping):
        return clean_counts
    for key, value in raw_counts.items():
        count = _clean_int(value, 0, minimum=0)
        if key in SHOP_DIARY_TRANSACTION_KEYS and count > 0:
            clean_counts[key] = count
    return clean_counts


def _quest_access_lock_reason(player_data: Mapping[str, Any], rule: Mapping[str, Any], label: str) -> Optional[str]:
    quests = player_data.get("quests", {}) or {}
    state = quests.get(str(rule.get("quest_id", "")), {}) or {}
    required_stage = rule.get("stage", "completed")
    if str(required_stage) == "started":
        if bool(state.get("started")) or bool(state.get("completed")):
            return None
        return f"Requires starting {label}"
    required_progress = _clean_int(required_stage, 0)
    if required_progress > 0:
        progress = _clean_int(state.get("progress", 0) or 0, 0)
        if bool(state.get("completed")) or (bool(state.get("started")) and progress >= required_progress):
            return None
        return f"Requires {label} stage {required_progress}"
    if bool(state.get("completed")):
        return None
    return f"Requires {label}"


def _quest_points_access_lock_reason(player_data: Mapping[str, Any], rule: Mapping[str, Any], label: str) -> Optional[str]:
    required = int(rule.get("quest_points", 0) or 0)
    if int(player_data.get("quest_points", 0) or 0) >= required:
        return None
    return f"Requires {label}"


def _skill_access_lock_reason(player_data: Mapping[str, Any], rule: Mapping[str, Any], label: str) -> Optional[str]:
    skill = str(rule.get("skill", ""))
    required = int(rule.get("level", 1) or 1)
    if int(player_data.get(f"{skill}_level", 1) or 1) >= required:
        return None
    return f"Requires {label}"


def _skill_total_access_lock_reason(player_data: Mapping[str, Any], rule: Mapping[str, Any], label: str) -> Optional[str]:
    total = sum(int(player_data.get(f"{skill}_level", 1) or 1) for skill in rule.get("skills", ()))
    if total >= int(rule.get("total", 0) or 0):
        return None
    return f"Requires {label}"


_ACCESS_LOCK_REASONS: Dict[str, Callable[[Mapping[str, Any], Mapping[str, Any], str], Optional[str]]] = {
    "quest": _quest_access_lock_reason,
    "quest_points": _quest_points_access_lock_reason,
    "skill": _skill_access_lock_reason,
    "skill_total": _skill_total_access_lock_reason,
}


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
        "restock_progress": 0,
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
        # Transactions checkpoint the group clock, but each row keeps its unfinished interval.
        progress = elapsed + _clean_int(row.get("restock_progress"), 0, minimum=0)
        steps, row["restock_progress"] = divmod(progress, _clean_int(row.get("restock_ticks"), 50, minimum=1))
        if steps <= 0:
            continue
        delta = steps * _clean_int(row.get("restock_amount"), 1, minimum=1)
        if current < default:
            _set_stock_quantity(row, min(default, current + delta))
        else:
            _set_stock_quantity(row, max(default, current - delta))
        if bool(row.get("temporary")) and row["current_quantity"] <= 0:
            group_state["rows"].pop(row_id, None)
    group_state["last_market_tick"] = market_tick


def _set_stock_quantity(row: Dict[str, Any], quantity: int) -> None:
    default = row["default_quantity"]
    # Time earned toward the default from one side must not carry across it.
    if (row["current_quantity"] - default) * (quantity - default) <= 0:
        row["restock_progress"] = 0
    row["current_quantity"] = quantity


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
        "price_policy": row.get("price_policy", ""),
        "price_source": row.get("price_source", ""),
        "can_buy": can_buy,
        "can_sell_to_shop": not bool(shop["buy_only"]) and (bool(shop["general_store"]) or row["disposition"] == "live"),
        "source": row["source"],
        "source_path": row["source_path"],
    }


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
    registry_spec = EXTRA_ITEM_DATA.get(item_name)
    if registry_spec is not None and registry_spec.get("tradeable") is False:
        return False
    stock_rows = (row for shop in SHOP_DATA.values() for row in shop.get("stock", []))
    service_rows = (
        item
        for collection in (SHOP_SERVICES, SHOP_VENDOR_ACTIONS)
        for spec in collection.values()
        for item in list(spec.get("inputs", [])) + list(spec.get("outputs", []))
    )
    # The first catalog row naming the item decides; an item no row names is tradeable.
    for rows in (stock_rows, service_rows):
        for row in rows:
            if row.get("item_name") == item_name:
                return bool(row.get("tradeable", False))
    return True


def _sell_price_for_item(item_name: str) -> Optional[int]:
    # Darkan Shop.java getSellPrice is a property of the item alone —
    # identical at every shop. The generated table is that math for the
    # name's canonical item id.
    price = SHOP_PLAYER_SELL_PRICES.get(item_name)
    return int(price) if price is not None else None


def _temporary_stock_row(item_name: str, unit_price: int) -> Dict[str, Any]:
    return {
        "item_id": -1,
        "item_name": item_name,
        "current_quantity": 0,
        "default_quantity": 0,
        "restock_ticks": 50,
        "restock_progress": 0,
        "restock_amount": 1,
        "buy_price": max(1, _clean_int(SHOP_PLAYER_BUY_PRICES.get(item_name), unit_price, minimum=1)),
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


def _diary_transaction_key(event: Mapping[str, Any]) -> str:
    event_type = str(event.get("type", ""))
    detail_id = (
        str(event.get("service_id", ""))
        if event_type in {"service", "vendor_action"}
        else str(event.get("row_id", ""))
    )
    return shop_diary_transaction_counter_key_pure(
        event_type,
        str(event.get("shop_id", "")),
        detail_id,
    )


def _adjust_diary_transaction_count(
    data: Dict[str, Any], event: Mapping[str, Any], delta: int
) -> None:
    key = _diary_transaction_key(event)
    if not key:
        return
    counts = dict(data.get("shop_transaction_counts", {}) or {})
    updated = max(0, _clean_int(counts.get(key), 0, minimum=0) + delta)
    if updated:
        counts[key] = updated
    else:
        counts.pop(key, None)
    data["shop_transaction_counts"] = counts


def _append_event(data: Dict[str, Any], event: Mapping[str, Any]) -> None:
    if event.get("type") != "rollback":
        _adjust_diary_transaction_count(data, event, 1)
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
