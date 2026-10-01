"""Pure NPC shop logic for stock, events, rollback, and the review-card clock."""

from __future__ import annotations

import copy
import random
from typing import Any, Dict, Iterable, Mapping, Optional

from ..data.shop_data import (
    SHOP_DATA,
    SHOP_DATA_VERSION,
    SHOP_ID_ALIASES,
    SHOP_PLAYER_BUY_PRICES,
    SHOP_PLAYER_SELL_PRICES,
    SHOP_SERVICES,
    SHOP_VENDOR_ACTIONS,
)

from .inventory_pure import CARRIED_CAPACITY

from ..data.herblore_data import HERBLORE_TARGETS

from ..data.crafting_data import LEGACY_CRAFTING_ITEM_MIGRATIONS

from ..core.constants import EXTRA_ITEM_DATA

from ..logic_pure.quest_action_proofs import record_runtime_quest_action_proofs_pure, retract_shop_event_quest_action_proofs_pure
from ..logic_pure.shop_diary_transactions import (
    SHOP_DIARY_TRANSACTION_KEYS,
    shop_diary_transaction_counter_key_pure,
)
from ..data.potion_data import (
    EMPTY_FLASK_ITEM,
    POTION_FAMILIES,
    VIAL_ITEM,
    potion_dose_name,
    potion_flask_name,
)
from .shop.state import (
    MAX_SHOP_EVENT_HISTORY,
    _CANONICAL_SHOP_ROW_NAMES,
    default_shop_state_pure as default_shop_state_pure,
    sanitize_shop_state_pure as sanitize_shop_state_pure,
    ensure_shop_state_pure,
    migrate_shop_diary_transaction_counts_pure as migrate_shop_diary_transaction_counts_pure,
    advance_shop_market_clock_pure as advance_shop_market_clock_pure,
    shop_access_lock_reason_pure,
    resolve_shop_id,
    _clean_int,
    _clean_optional_int,
    _canonical_saved_shop_item_name,
    _migrate_item_delta_names,
    _migrate_saved_stock_set_names,
    _migrate_saved_shop_event_item_names,
    _sanitize_market_clock as _sanitize_market_clock,
    _sanitize_stock_state as _sanitize_stock_state,
    _sanitize_stock_rows as _sanitize_stock_rows,
    _sanitize_stock_row as _sanitize_stock_row,
    _sanitize_shop_events as _sanitize_shop_events,
    _sanitize_transaction_counts as _sanitize_transaction_counts,
    _quest_access_lock_reason as _quest_access_lock_reason,
    _quest_points_access_lock_reason as _quest_points_access_lock_reason,
    _skill_access_lock_reason as _skill_access_lock_reason,
    _skill_total_access_lock_reason as _skill_total_access_lock_reason,
    _shop_or_none,
    _row_definition,
    _temporary_row_definition_from_group,
    _temporary_row_definition,
    _state_row_from_definition,
    _view_group_state,
    _transaction_group_state,
    _compress_group_state,
    _apply_restock_to_group_state,
    _set_stock_quantity,
    _row_view,
    _denied,
    _inventory_count,
    _add_inventory,
    _stocked_row_for_item,
    _item_tradeable,
    _sell_price_for_item,
    _temporary_stock_row,
    _item_slug,
    _build_event,
    _event_display,
    _next_event_id,
    _diary_transaction_key,
    _adjust_diary_transaction_count,
    _append_event,
    _event_by_id,
    _last_rollbackable_event,
)
from .shop.services import (
    DECANTABLE_FOUR_DOSE_POTION_BASES,
    DECANTABLE_FLASK_POTION_BASES,
    preview_shop_service_pure as preview_shop_service_pure,
    apply_shop_service_pure,
    preview_shop_vendor_action_pure as preview_shop_vendor_action_pure,
    apply_shop_vendor_action_pure,
    _preview_service_like,
    _decant_potion_family,
    _decant_potions_delta,
    _preview_decant_potions,
    _apply_decant_potions,
    _consume_potion_doses,
    _fill_potion_flasks_delta,
    _preview_fill_potion_flasks,
    _decant_flask_family_to_vials,
    _decant_flasks_to_vials_delta,
    _preview_decant_flasks_to_vials,
    _apply_inventory_wide_service,
    _apply_fill_potion_flasks,
    _apply_decant_flasks_to_vials,
    _apply_service_like,
    _service_requirement_rows,
)


def shop_view_model_pure(player_data: Mapping[str, Any], shop_id: str) -> Dict[str, Any]:
    return _shop_view_model_from_state(ensure_shop_state_pure(player_data), shop_id)


def shop_view_models_pure(player_data: Mapping[str, Any], shop_ids) -> Dict[str, Dict[str, Any]]:
    """View models for many shops built from a single sanitized snapshot.

    ``ensure_shop_state_pure`` deep-copies the whole save, so asking for every
    shop one at a time copied it once per shop (~270 times) and dominated the
    main-menu open. The read path never mutates the snapshot, so one copy is
    enough for the whole batch.
    """
    data = ensure_shop_state_pure(player_data)
    return {shop_id: _shop_view_model_from_state(data, shop_id) for shop_id in shop_ids}


def _shop_view_model_from_state(data: Mapping[str, Any], shop_id: str) -> Dict[str, Any]:
    """Read-only view model over an already sanitized save snapshot."""
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


def shop_selector_entries_pure(player_data: Mapping[str, Any], shop_ids) -> list[Dict[str, Any]]:
    """Shop-list entries in browse order.

    A shop locked against this save (any access wall, or a static currency
    lock) sorts after every open shop and its label names only the reason, so
    the list never advertises a shop the player cannot use yet. It still opens
    read-only.
    """
    views = shop_view_models_pure(player_data, shop_ids)
    keyed = []
    for shop_id in shop_ids:
        shop = SHOP_DATA[shop_id]
        view = views[shop_id]
        locked = bool(view["lock_reason"])
        # Live stock from the data, not the current stock level, so a shop
        # does not jump around the list as it sells out.
        has_live_stock = any(row.get("disposition") == "live" for row in shop["stock"])
        entry = {
            "shop_id": shop_id,
            "label": _shop_selector_label(shop, view),
            "locked": locked,
            "rows": view["rows"],
        }
        keyed.append(((locked, not has_live_stock, shop["display_name"]), entry))
    return [entry for _key, entry in sorted(keyed, key=lambda pair: pair[0])]


def _shop_selector_label(shop: Mapping[str, Any], view: Mapping[str, Any]) -> str:
    lock_reason = str(view["lock_reason"])
    if lock_reason:
        return f"{shop['display_name']} · {lock_reason[:1].upper()}{lock_reason[1:].replace('_', ' ')}"
    live_count = sum(1 for row in view["rows"] if row["can_buy"])
    locked_count = sum(1 for row in view["rows"] if row["lock_reason"])
    parts = [
        f"{live_count} live" if live_count else "",
        f"{locked_count} locked" if locked_count else "",
        "general store" if shop["general_store"] else "",
    ]
    return f"{shop['display_name']} · " + (" · ".join(part for part in parts if part) or "read-only")


def search_shop_catalog_pure(
    player_data: Mapping[str, Any],
    query: str,
    *,
    include_locked: bool = True,
    include_hidden: bool = False,
    limit: int = 50,
) -> Dict[str, Any]:
    normalized = query.strip().lower()
    results = _search_stock_rows(
        ensure_shop_state_pure(player_data),
        normalized,
        include_locked=include_locked,
        include_hidden=include_hidden,
    )
    results.extend(_search_services(normalized))
    # Locked rows go last before the cut, so a common word ("fish") cannot fill
    # the limit with shops the save cannot buy from and push open ones out.
    results.sort(key=lambda result: bool(result["lock_reason"]))
    return {"query": query, "results": results[: max(0, limit)]}


def _search_stock_rows(
    data: Mapping[str, Any],
    normalized: str,
    *,
    include_locked: bool,
    include_hidden: bool,
) -> list[Dict[str, Any]]:
    results = []
    for shop in SHOP_DATA.values():
        if shop["visibility"] == "hidden" and not include_hidden:
            continue
        if shop["visibility"] == "visible_locked" and not include_locked:
            continue
        view = _shop_view_model_from_state(data, shop["id"])
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
                    "lock_reason": row["lock_reason"] or view["lock_reason"],
                }
            )
    return results


def _search_services(normalized: str) -> list[Dict[str, Any]]:
    results = []
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
    return results


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
    from ..logic_pure.logic_pure import _combat_apply_pvm_death, combat_max_lifepoints_pure

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


def _undo_wilderness_ambush(data: Dict[str, Any], ambush: Any) -> None:
    if not isinstance(ambush, Mapping):
        return
    # Undo the slot accounting; restore combat/death state if it triggered.
    slots_before = _clean_int(ambush.get("slots_before"), 0, minimum=0)
    data["wilderness_shop_slots"] = slots_before
    restore = ambush.get("restore")
    if not (ambush.get("triggered") and isinstance(restore, Mapping)):
        return
    for key in _WILDERNESS_RESTORE_KEYS:
        if key not in restore:
            continue
        if restore[key] is None:
            data.pop(key, None)  # the key did not exist pre-ambush
        else:
            data[key] = copy.deepcopy(restore[key])


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
    _set_stock_quantity(group_state["rows"][row["id"]], max(0, before_row["current_quantity"] - amount))
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
    record_runtime_quest_action_proofs_pure(data, "shop_buy", row["id"])
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
    row_state = group_state["rows"][row_id]
    _set_stock_quantity(row_state, row_state["current_quantity"] + amount)
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
    _rollback_inventory_delta(data, inverse.get("inventory_delta", {}))
    _rollback_stock_set(data, inverse.get("stock_set", {}))
    _undo_wilderness_ambush(data, event.get("wilderness_ambush"))
    retract_shop_event_quest_action_proofs_pure(data, event)
    _adjust_diary_transaction_count(data, event, -1)
    rollback_event = {
        "event_id": _next_event_id(data),
        "type": "rollback",
        "rolled_back_event_id": event["event_id"],
        "market_tick": data["shop_market_clock"]["market_tick"],
        "display": f"Rolled back {event.get('display', event['event_id'])}",
    }
    _append_event(data, rollback_event)
    return data, {"allowed": True, "event_id": rollback_event["event_id"], "rolled_back_event_id": event["event_id"]}


def _rollback_inventory_delta(data: Dict[str, Any], inventory_delta: Any) -> None:
    if not isinstance(inventory_delta, Mapping):
        return
    for item_name, delta in inventory_delta.items():
        if isinstance(item_name, str):
            _add_inventory(data, item_name, _clean_int(delta, 0))


def _rollback_stock_set(data: Dict[str, Any], stock_set: Any) -> None:
    if not isinstance(stock_set, Mapping):
        return
    for group_id, rows in stock_set.items():
        if isinstance(group_id, str) and isinstance(rows, Mapping):
            _restore_stock_group_rows(data, group_id, rows)


def _restore_stock_group_rows(data: Dict[str, Any], group_id: str, before_rows: Mapping[Any, Any]) -> None:
    group_state = copy.deepcopy(data.get("shop_stock_state", {}).get(group_id, {"shop_id": "", "last_market_tick": data["shop_market_clock"]["market_tick"], "rows": {}}))
    group_state.setdefault("rows", {})
    for row_id, before_row in before_rows.items():
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


def shop_history_rows_pure(player_data: Mapping[str, Any], shop_id: Optional[str] = None, limit: int = 20) -> list[Dict[str, Any]]:
    data = ensure_shop_state_pure(player_data)
    events = data.get("shop_events", [])
    if shop_id:
        canonical = resolve_shop_id(shop_id)
        events = [event for event in events if event.get("shop_id") == canonical]
    return [dict(event) for event in events[-max(0, limit):]][::-1]


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

    row_id = _sell_row_id(shop, group_state, stocked_row, item_name)
    if row_id is None:
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


def _sell_row_id(
    shop: Mapping[str, Any],
    group_state: Mapping[str, Any],
    stocked_row: Optional[Mapping[str, Any]],
    item_name: str,
) -> Optional[str]:
    """Stock row a sale lands in, or None when it needs a slot the shop lacks."""
    if stocked_row is not None:
        return stocked_row["id"]
    row_id = f"{shop['id']}:temporary:{_item_slug(item_name)}"
    if row_id in group_state.get("rows", {}):
        return row_id
    # Shop.java: general stock is MAX_SHOP_ITEMS(40) minus the main stock;
    # a sale needing a new slot fails when the pool is full.
    temporary_rows = sum(
        1 for state in group_state.get("rows", {}).values() if bool(state.get("temporary"))
    )
    if temporary_rows >= max(0, 40 - len(shop["stock"])):
        return None
    return row_id
