"""Deterministic backend fixtures for the future NPC shop frontend."""

from __future__ import annotations

from typing import Any, Dict, Mapping

try:
    from .shop_data import SHOP_DATA, SHOP_VENDOR_ACTIONS
    from .shop_logic import (
        apply_shop_buy_pure,
        apply_shop_sell_pure,
        apply_shop_vendor_action_pure,
        default_shop_state_pure,
        preview_shop_buy_pure,
        search_shop_catalog_pure,
        shop_history_rows_pure,
        shop_view_model_pure,
    )
except ImportError:
    from shop_data import SHOP_DATA, SHOP_VENDOR_ACTIONS
    from shop_logic import (
        apply_shop_buy_pure,
        apply_shop_sell_pure,
        apply_shop_vendor_action_pure,
        default_shop_state_pure,
        preview_shop_buy_pure,
        search_shop_catalog_pure,
        shop_history_rows_pure,
        shop_view_model_pure,
    )


def build_shop_fixture_player_data() -> Dict[str, Any]:
    data = {
        "inventory": {
            "Coins": 100_000,
            "Beer": 3,
            "Cowhide": 2,
            "Logs": 2,
            "Beer glass": 1,
        }
    }
    data.update(default_shop_state_pure())
    return data


def build_shop_frontend_fixtures() -> Dict[str, Any]:
    player_data = build_shop_fixture_player_data()
    live_shop, live_row = _first_live_stock_row()
    locked_shop, locked_row = _first_locked_stock_row()
    general_store = _first_general_store()
    non_coin_shop = _first_non_coin_shop()
    hidden_shop = _first_hidden_shop()
    vendor_action_id = _first_id(SHOP_VENDOR_ACTIONS)

    after_buy, buy_result = apply_shop_buy_pure(player_data, live_shop["id"], live_row["id"], 2)
    after_sell, sell_result = apply_shop_sell_pure(after_buy, general_store["id"], "Beer", 1)
    after_vendor, vendor_result = apply_shop_vendor_action_pure(after_sell, vendor_action_id, 1)

    return {
        "fixture_player_data": player_data,
        "normal_coin_stock_shop": shop_view_model_pure(player_data, live_shop["id"]),
        "feather_multi_shop_search": search_shop_catalog_pure(player_data, "Feather", include_locked=True, limit=12),
        "locked_read_only_shop": shop_view_model_pure(player_data, locked_shop["id"]),
        "locked_preview_error": preview_shop_buy_pure(player_data, locked_shop["id"], locked_row["id"], 1),
        "non_coin_locked_shop": shop_view_model_pure(player_data, non_coin_shop["id"]) if non_coin_shop else {},
        "hidden_reward_shop": shop_view_model_pure(player_data, hidden_shop["id"]) if hidden_shop else {},
        "shared_stock_shop": {
            "shop_id": live_shop["id"],
            "shared_stock_group": live_shop["shared_stock_group"],
            "after_buy_view": shop_view_model_pure(after_buy, live_shop["id"]),
        },
        "player_sold_stock": {
            "shop_id": general_store["id"],
            "result": sell_result,
            "view": shop_view_model_pure(after_sell, general_store["id"]),
        },
        "vendor_action_transaction": {
            "action_id": vendor_action_id,
            "result": vendor_result,
        },
        "history": shop_history_rows_pure(after_vendor, limit=10),
        "search_after_transactions": search_shop_catalog_pure(after_vendor, "Beer", include_locked=True, limit=12),
    }


def _first_live_stock_row() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    for shop in SHOP_DATA.values():
        for row in shop["stock"]:
            if row["disposition"] == "live" and shop["visibility"] == "visible":
                return shop, row
    raise AssertionError("generated shop catalog has no live stock rows")


def _first_locked_stock_row() -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    for shop in SHOP_DATA.values():
        for row in shop["stock"]:
            if row["visibility"] == "visible_locked":
                return shop, row
    raise AssertionError("generated shop catalog has no locked stock rows")


def _first_general_store() -> Mapping[str, Any]:
    for shop in SHOP_DATA.values():
        if shop["general_store"] and shop["visibility"] == "visible":
            return shop
    raise AssertionError("generated shop catalog has no visible general store")


def _first_non_coin_shop() -> Mapping[str, Any] | None:
    for shop in SHOP_DATA.values():
        if shop["currency_id"] != 995:
            return shop
    return None


def _first_hidden_shop() -> Mapping[str, Any] | None:
    for shop in SHOP_DATA.values():
        if shop["visibility"] == "hidden":
            return shop
    return None


def _first_id(rows: Mapping[str, Any]) -> str:
    return next(iter(rows))
