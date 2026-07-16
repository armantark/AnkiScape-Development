"""Pure NPC shop runtime logic.

The UI should call these functions through a thin adapter. They own source
disposition checks, stock mutation, event history, rollback, and the review-card
market clock without importing Anki.
"""

from __future__ import annotations

import copy
import random
from typing import Any, Dict, Iterable, Mapping, Optional

try:
    from .shop_data import (
        SHOP_DATA,
        SHOP_DATA_VERSION,
        SHOP_ID_ALIASES,
        SHOP_PLAYER_BUY_PRICES,
        SHOP_PLAYER_SELL_PRICES,
        SHOP_SERVICES,
        SHOP_VENDOR_ACTIONS,
    )
except ImportError:
    from shop_data import (
        SHOP_DATA,
        SHOP_DATA_VERSION,
        SHOP_ID_ALIASES,
        SHOP_PLAYER_BUY_PRICES,
        SHOP_PLAYER_SELL_PRICES,
        SHOP_SERVICES,
        SHOP_VENDOR_ACTIONS,
    )

try:
    from .inventory_pure import CARRIED_CAPACITY
except ImportError:
    from inventory_pure import CARRIED_CAPACITY

try:
    from .herblore_data import HERBLORE_TARGETS
except ImportError:
    from herblore_data import HERBLORE_TARGETS


MAX_SHOP_EVENT_HISTORY = 200

# Bob Barter's ordinary-vial catalog is the live, non-Daemonheim Herblore
# catalog. Barbarian mixes use two-dose bowls rather than four-dose vials.
DECANTABLE_FOUR_DOSE_POTION_BASES = tuple(
    sorted(
        {
            target.output_item[:-4]
            for target in HERBLORE_TARGETS
            if target.group == "finished"
            and target.subgroup != "barbarian"
            and target.output_item.endswith(" (3)")
            and all(
                f"{target.output_item[:-4]} ({dose})" in SHOP_PLAYER_SELL_PRICES
                for dose in range(1, 5)
            )
        }
    )
)


def default_shop_state_pure() -> Dict[str, Any]:
    return {
        "shop_data_version": SHOP_DATA_VERSION,
        "shop_market_clock": {"version": 1, "answered_cards": 0, "market_tick": 0},
        "shop_stock_state": {},
        "shop_events": [],
        "shop_next_event_id": 1,
        "wilderness_shop_slots": 0,
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
        "wilderness_shop_slots": _clean_int(data.get("wilderness_shop_slots"), 0, minimum=0),
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


def shop_access_lock_reason_pure(player_data: Mapping[str, Any], shop: Mapping[str, Any]) -> Optional[str]:
    """Owner-grilled access gates (2026-07-07): quest/route walls, guild
    skill walls, and quest-point walls evaluated against the save. Wilderness
    is access-open (its cost is the ambush risk, not a lock)."""
    rule = shop.get("access")
    if not isinstance(rule, Mapping):
        return None
    kind = rule.get("kind")
    label = str(rule.get("label", "access requirement"))
    if kind == "quest":
        quests = player_data.get("quests", {}) or {}
        state = quests.get(str(rule.get("quest_id", "")), {}) or {}
        if str(rule.get("stage", "completed")) == "started":
            if bool(state.get("started")) or bool(state.get("completed")):
                return None
            return f"Requires starting {label}"
        if bool(state.get("completed")):
            return None
        return f"Requires {label}"
    if kind == "quest_points":
        required = int(rule.get("quest_points", 0) or 0)
        if int(player_data.get("quest_points", 0) or 0) >= required:
            return None
        return f"Requires {label}"
    if kind == "skill":
        skill = str(rule.get("skill", ""))
        required = int(rule.get("level", 1) or 1)
        if int(player_data.get(f"{skill}_level", 1) or 1) >= required:
            return None
        return f"Requires {label}"
    if kind == "skill_total":
        total = sum(int(player_data.get(f"{skill}_level", 1) or 1) for skill in rule.get("skills", ()))
        if total >= int(rule.get("total", 0) or 0):
            return None
        return f"Requires {label}"
    return None



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
    access_lock = shop_access_lock_reason_pure(data, shop)
    if access_lock:
        for row_view in rows:
            row_view["can_buy"] = False
            row_view["can_sell_to_shop"] = False
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
        "lock_reason": access_lock or shop["lock_reason"],
        "wilderness": (shop.get("access") or {}).get("kind") == "wilderness",
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


# Owner-declared Wilderness ambush (grill 2026-07-07): every completed block
# of 28 purchase-slots from a Wilderness shop rolls 1% for one PKer-style hit.
# Stackables occupy one slot per purchase; unstackables one slot per item.
# The damage roll reuses the engine's landed-hit semantics (uniform
# 1..maxHit-1) with a declared max hit of 250 lifepoints; death routes through
# the normal PvM grave path. This is an AnkiScape invention, ledger-declared.
# The "trip" is one carried inventory's worth of purchases, so it shares the
# single 28-slot constant with the carry model (2g: one source of truth for 28;
# the accumulators stay distinct because shop-purchase volume and skilling churn
# measure different things).
_WILDERNESS_SLOTS_PER_TRIP = CARRIED_CAPACITY
_WILDERNESS_AMBUSH_CHANCE = 0.01
_WILDERNESS_AMBUSH_MAX_HIT_LP = 250
_WILDERNESS_RESTORE_KEYS = (
    "combat_lifepoints",
    "combat_grave",
    "death_office",
    "combat_encounter",
    "combat_status_effects",
    "equipment",
)


def _apply_wilderness_ambush(data: Dict[str, Any], shop: Mapping[str, Any], row: Mapping[str, Any], amount: int, rng) -> Optional[Dict[str, Any]]:
    if (shop.get("access") or {}).get("kind") != "wilderness":
        return None
    from logic_pure import _combat_apply_pvm_death, combat_max_lifepoints_pure

    slots = 1 if bool(row.get("stackable")) else max(1, int(amount))
    before_slots = _clean_int(data.get("wilderness_shop_slots"), 0, minimum=0)
    total_slots = before_slots + slots
    data["wilderness_shop_slots"] = total_slots
    blocks = (total_slots // _WILDERNESS_SLOTS_PER_TRIP) - (before_slots // _WILDERNESS_SLOTS_PER_TRIP)
    if blocks <= 0:
        return {"slots": slots, "slots_before": before_slots, "triggered": False}

    max_lp = combat_max_lifepoints_pure(data)
    lp_before = max(0, _clean_int(data.get("combat_lifepoints"), max_lp, minimum=0)) or max_lp
    damage = 0
    for _ in range(blocks):
        if float(rng()) < _WILDERNESS_AMBUSH_CHANCE:
            roll = max(0.0, min(float(rng()), 0.999999999))
            damage += 1 + int(roll * (_WILDERNESS_AMBUSH_MAX_HIT_LP - 1))
    if damage <= 0:
        return {"slots": slots, "slots_before": before_slots, "triggered": False}

    restore = {key: copy.deepcopy(data.get(key)) for key in _WILDERNESS_RESTORE_KEYS}
    lp_after = lp_before - damage
    died = lp_after <= 0
    if died:
        _combat_apply_pvm_death(data, max_lp, grave_source="wilderness_shop_ambush")
    else:
        data["combat_lifepoints"] = lp_after
    return {
        "slots": slots,
        "slots_before": before_slots,
        "triggered": True,
        "damage": damage,
        "lifepoints_before": lp_before,
        "lifepoints_after": max(0, lp_after),
        "died": died,
        "restore": restore,
    }



def apply_shop_buy_pure(player_data: Mapping[str, Any], shop_id: str, row_id: str, quantity: int = 1, rng=None) -> tuple[Dict[str, Any], Dict[str, Any]]:
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
    ambush = _apply_wilderness_ambush(data, shop, row, amount, rng or random.random)
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
    if ambush is not None:
        event["wilderness_ambush"] = copy.deepcopy(ambush)
    _append_event(data, event)
    result = dict(preview)
    result["event_id"] = event["event_id"]
    if ambush is not None:
        result["wilderness_ambush"] = {k: v for k, v in ambush.items() if k != "restore"}
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
        stocked_row = _stocked_row_for_item(shop, item_name)
        if stocked_row is not None and stocked_row["id"] == row_id:
            # Sold-into-main-stock overstock decays toward the row's default
            # (ShopItem.capStock), not toward zero like player-sold slots.
            group_state["rows"][row_id] = _state_row_from_definition(stocked_row)
        else:
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
    if service.get("action_type") == "decant_potions_to_four":
        return _preview_decant_potions_to_four(player_data, service, quantity)
    return _preview_service_like(player_data, service, quantity)


def apply_shop_service_pure(player_data: Mapping[str, Any], service_id: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    service = SHOP_SERVICES.get(service_id)
    data = ensure_shop_state_pure(player_data)
    if service is None:
        return data, _denied("unknown_service", requested_quantity=quantity)
    if service.get("action_type") == "decant_potions_to_four":
        return _apply_decant_potions_to_four(data, service, quantity)
    return _apply_service_like(data, service, "service", quantity)


def preview_shop_vendor_action_pure(player_data: Mapping[str, Any], action_id: str, quantity: int = 1) -> Dict[str, Any]:
    action = SHOP_VENDOR_ACTIONS.get(action_id)
    if action is None:
        return _denied("unknown_vendor_action", requested_quantity=quantity)
    # Dialogue parity (owner decision 2026-07-07): every vendor action is one
    # interaction per use — Karim hands over exactly one kebab per
    # conversation. The quantity spinner was an AnkiScape invention.
    return _preview_service_like(player_data, action, 1)


def apply_shop_vendor_action_pure(player_data: Mapping[str, Any], action_id: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    action = SHOP_VENDOR_ACTIONS.get(action_id)
    data = ensure_shop_state_pure(player_data)
    if action is None:
        return data, _denied("unknown_vendor_action", requested_quantity=quantity)
    # Dialogue parity: one interaction per use regardless of requested qty.
    return _apply_service_like(data, action, "vendor_action", 1)


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
    ambush = event.get("wilderness_ambush")
    if isinstance(ambush, Mapping):
        # Undo the slot accounting; restore combat/death state if it triggered.
        slots_before = _clean_int(ambush.get("slots_before"), 0, minimum=0)
        data["wilderness_shop_slots"] = slots_before
        restore = ambush.get("restore")
        if ambush.get("triggered") and isinstance(restore, Mapping):
            for key in _WILDERNESS_RESTORE_KEYS:
                if key in restore:
                    if restore[key] is None:
                        data.pop(key, None)  # the key did not exist pre-ambush
                    else:
                        data[key] = copy.deepcopy(restore[key])
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
        "price_policy": row.get("price_policy", ""),
        "price_source": row.get("price_source", ""),
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
    access_lock = shop_access_lock_reason_pure(data, shop)
    if access_lock:
        return _denied(access_lock, requested_quantity=requested, shop_id=shop["id"], row_id=row["id"])
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
    currency_owned = _inventory_count(data, currency_name)
    affordable = currency_owned // max(1, unit_price)
    quantity_allowed = min(requested, current_quantity, affordable)
    if quantity_allowed <= 0:
        required_currency = unit_price * min(requested, current_quantity)
        return _denied(
            "insufficient_currency",
            requested_quantity=requested,
            shop_id=shop["id"],
            row_id=row["id"],
            unit_price=unit_price,
            required_currency=required_currency,
            currency_owned=currency_owned,
            currency_shortfall=max(0, required_currency - currency_owned),
            currency_item_name=currency_name,
            stock_available=current_quantity,
        )
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
        "currency_owned": currency_owned,
        "required_currency": unit_price * quantity_allowed,
        "stock_available": current_quantity,
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
    access_lock = shop_access_lock_reason_pure(data, shop)
    if access_lock:
        return _denied(access_lock, requested_quantity=requested, shop_id=shop["id"])
    owned_quantity = _inventory_count(data, item_name)
    if owned_quantity <= 0:
        return _denied("missing_item", requested_quantity=requested, shop_id=shop["id"], item_name=item_name, owned_quantity=0)

    if item_name == shop["currency_item_name"]:
        # Shop.java: item.getId() == currency -> "You can't sell this item."
        return _denied("currency_item", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)
    stocked_row = _stocked_row_for_item(shop, item_name)
    if not shop["general_store"] and stocked_row is None:
        return _denied("specialist_shop_stock_only", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)
    if not _item_tradeable(item_name):
        return _denied("item_not_tradeable", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)

    row_id = f"{shop['id']}:temporary:{_item_slug(item_name)}"
    if stocked_row is not None:
        row_id = stocked_row["id"]
    elif row_id not in group_state.get("rows", {}):
        # Shop.java: general stock is MAX_SHOP_ITEMS(40) minus the main stock;
        # a sale needing a new slot fails when the pool is full.
        temporary_rows = sum(
            1 for state in group_state.get("rows", {}).values() if bool(state.get("temporary"))
        )
        if temporary_rows >= max(0, 40 - len(shop["stock"])):
            return _denied("shop_full", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)
    # Darkan getSellPrice depends only on the item, never the shop.
    unit_price = _sell_price_for_item(item_name)
    if unit_price is None:
        return _denied("sell_price_unresolved", requested_quantity=requested, shop_id=shop["id"], item_name=item_name)
    amount = min(requested, owned_quantity)
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
        "owned_quantity": owned_quantity,
    }


def _preview_service_like(player_data: Mapping[str, Any], service: Mapping[str, Any], quantity: int) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    requested = max(1, int(quantity))
    if service.get("visibility") != "visible":
        return _denied(service.get("lock_reason") or "service_not_visible", requested_quantity=requested, service_id=service["id"])
    currency_name = str(service.get("currency_item_name", "Coins"))
    unit_price = _clean_int(service.get("price"), 0, minimum=0)
    requested_requirements = _service_requirement_rows(data, service, requested, unit_price, currency_name)
    max_quantity = requested
    if unit_price:
        max_quantity = min(max_quantity, _inventory_count(data, currency_name) // unit_price)
    for item in service.get("inputs", []):
        max_quantity = min(max_quantity, _inventory_count(data, item["item_name"]) // max(1, int(item["quantity"])))
    if max_quantity <= 0:
        return _denied(
            "missing_requirements",
            requested_quantity=requested,
            service_id=service["id"],
            unit_price=unit_price,
            currency_item_name=currency_name,
            requirements=requested_requirements,
            missing_requirements=[row for row in requested_requirements if int(row.get("shortfall", 0) or 0) > 0],
        )
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
        "requirements": _service_requirement_rows(data, service, max_quantity, unit_price, currency_name),
        "requested_requirements": requested_requirements,
    }


def _decant_potions_to_four_delta(
    data: Mapping[str, Any],
) -> tuple[Dict[str, int], list[str], int, int]:
    inventory_delta: Dict[str, int] = {}
    changed_families: list[str] = []
    total_doses = 0
    returned_vials = 0
    for base in DECANTABLE_FOUR_DOSE_POTION_BASES:
        counts = {dose: _inventory_count(data, f"{base} ({dose})") for dose in range(1, 5)}
        family_doses = sum(dose * count for dose, count in counts.items())
        if not family_doses:
            continue
        full_vials, remainder = divmod(family_doses, 4)
        result_counts = {dose: 0 for dose in range(1, 5)}
        result_counts[4] = full_vials
        if remainder:
            result_counts[remainder] += 1
        family_delta = {
            f"{base} ({dose})": result_counts[dose] - counts[dose]
            for dose in range(1, 5)
            if result_counts[dose] != counts[dose]
        }
        if not family_delta:
            continue
        inventory_delta.update(family_delta)
        changed_families.append(base)
        total_doses += family_doses
        returned_vials += sum(counts.values()) - sum(result_counts.values())
    if returned_vials:
        inventory_delta["Vial"] = returned_vials
    return inventory_delta, changed_families, total_doses, returned_vials


def _preview_decant_potions_to_four(
    player_data: Mapping[str, Any], service: Mapping[str, Any], quantity: int
) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    requested = max(1, int(quantity))
    if service.get("visibility") != "visible":
        return _denied(
            service.get("lock_reason") or "service_not_visible",
            requested_quantity=requested,
            service_id=service["id"],
        )
    inventory_delta, changed_families, total_doses, returned_vials = (
        _decant_potions_to_four_delta(data)
    )
    if not inventory_delta:
        return _denied("no_potions_to_decant", requested_quantity=requested, service_id=service["id"])
    return {
        "allowed": True,
        "transaction_type": "service_like",
        "id": service["id"],
        "display_name": service["display_name"],
        "requested_quantity": requested,
        "quantity": 1,
        "clamped": requested != 1,
        "unit_price": 0,
        "total_price": 0,
        "currency_item_name": str(service.get("currency_item_name", "Coins")),
        "requirements": [],
        "requested_requirements": [],
        "inventory_delta": inventory_delta,
        "decanted_families": changed_families,
        "family_count": len(changed_families),
        "total_doses": total_doses,
        "returned_vials": returned_vials,
    }


def _apply_decant_potions_to_four(
    data: Dict[str, Any], service: Mapping[str, Any], quantity: int
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    preview = _preview_decant_potions_to_four(data, service, quantity)
    if not preview["allowed"]:
        return data, preview
    inventory_delta = preview["inventory_delta"]
    for item_name, delta in inventory_delta.items():
        _add_inventory(data, item_name, delta)
    event = _build_event(
        data,
        "service",
        {"id": "", "display_name": service["display_name"], "shared_stock_group": ""},
        quantity=1,
        service_id=service["id"],
        item_name=service["display_name"],
        total_price=0,
        inventory_delta=inventory_delta,
        stock_set={},
        stock_delta={},
    )
    _append_event(data, event)
    result = dict(preview)
    result["event_id"] = event["event_id"]
    return data, result


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


def _service_requirement_rows(
    data: Mapping[str, Any],
    service: Mapping[str, Any],
    quantity: int,
    unit_price: int,
    currency_name: str,
) -> list[Dict[str, Any]]:
    rows: list[Dict[str, Any]] = []
    if unit_price:
        owned = _inventory_count(data, currency_name)
        required = unit_price * quantity
        rows.append(
            {
                "item_name": currency_name,
                "required_quantity": required,
                "owned_quantity": owned,
                "shortfall": max(0, required - owned),
                "kind": "currency",
            }
        )
    for item in service.get("inputs", []):
        item_name = str(item.get("item_name", ""))
        if not item_name:
            continue
        required = _clean_int(item.get("quantity"), 1, minimum=1) * quantity
        owned = _inventory_count(data, item_name)
        rows.append(
            {
                "item_name": item_name,
                "required_quantity": required,
                "owned_quantity": owned,
                "shortfall": max(0, required - owned),
                "kind": "item",
            }
        )
    return rows


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
