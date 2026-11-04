"""Finite, shared sell demand inside a copied GE item transaction."""

import copy
from collections.abc import Mapping

from ...data.grand_exchange.sell_demand import daily_sell_demand_capacity_pure
from .profiles import GE_MARKET_DAY_CARDS, _clean_int

# Same technical bound as GE_MAX_OFFER_QUANTITY; avoid a circular module import.
_MAX_QUANTITY = 2_147_483_647


def migrate_sell_demand_items_pure(raw_market):
    raw_items = raw_market.get("items")
    items = copy.deepcopy(dict(raw_items)) if isinstance(raw_items, Mapping) else {}
    if _clean_int(raw_market.get("version"), 0) < 2:
        for name, state in items.items():
            if isinstance(state, Mapping) and "sell_demand" not in state:
                items[name] = {**state, "sell_demand": {"uninitialized": True}}
    return items


def _capacity(item_name, item_spec):
    capacity = item_spec.get("sell_demand_daily_quantity")
    if not _integer(capacity) or capacity <= 0:
        capacity = daily_sell_demand_capacity_pure(item_name, item_spec.get("buy_limit"))
    return min(_MAX_QUANTITY, max(1, capacity))


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _valid_record(record, market_tick):
    if not isinstance(record, Mapping):
        return False
    if not all(_integer(record.get(key)) for key in ("capacity", "credit", "last_tick")):
        return False
    return (
        1 <= record["capacity"] <= _MAX_QUANTITY
        and 0 <= record["credit"] <= record["capacity"] * GE_MARKET_DAY_CARDS
        and 0 <= record["last_tick"] <= market_tick
    )


def _legacy_marker(record):
    return isinstance(record, Mapping) and len(record) == 1 and record.get("uninitialized") is True


def advance_sell_demand_pure(state, *, item_name, item_spec, market_tick, new_item):
    capacity = _capacity(item_name, item_spec)
    ceiling = capacity * GE_MARKET_DAY_CARDS
    record = state.get("sell_demand")
    if new_item or _legacy_marker(record):
        credit = ceiling
    elif _valid_record(record, market_tick):
        credit = min(ceiling, record["credit"])
        credit = min(ceiling, credit + capacity * max(0, market_tick - record["last_tick"]))
    else:
        credit = 0
    state["sell_demand"] = {
        "capacity": capacity, "credit": credit, "last_tick": market_tick,
    }


def sell_demand_remaining_pure(state):
    return state["sell_demand"]["credit"] // GE_MARKET_DAY_CARDS


def consume_sell_demand_pure(state, quantity):
    state["sell_demand"]["credit"] -= quantity * GE_MARKET_DAY_CARDS
