"""Saved Grand Exchange offers and their stable six-slot positions."""

from typing import Any, Dict, Mapping, Optional

from .profiles import _clean_int

GE_SLOT_COUNT = 6
GE_MAX_TRADE_PRICE = 2_147_483_647
GE_MAX_OFFER_QUANTITY = 2_147_483_647
_ORDER_SIDES = frozenset({"buy", "sell"})
_ORDER_STATUSES = frozenset({"open", "partial", "complete", "cancelled"})


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


def sanitize_orders_pure(raw_orders: object) -> list[Dict[str, Any]]:
    if not isinstance(raw_orders, (list, tuple)):
        return []
    orders = []
    seen_ids = set()
    free_slots = set(range(GE_SLOT_COUNT))
    for raw_order in raw_orders:
        if not isinstance(raw_order, Mapping):
            continue
        order = _sanitize_order(raw_order)
        if order is None or order["id"] in seen_ids:
            continue
        seen_ids.add(order["id"])
        slot = _clean_int(raw_order.get("slot"), -1, minimum=-1)
        if slot not in free_slots:
            # A compact legacy list takes the same positions it displayed before.
            slot = min(free_slots)
        order["slot"] = slot
        free_slots.remove(slot)
        orders.append(order)
        if len(orders) == GE_SLOT_COUNT:
            break
    return orders
