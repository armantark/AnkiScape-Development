"""Registered-item Grand Exchange catalog construction.

The committed cache flags decide eligibility. Period guide-price and buy-limit
harvests may override the cache-value fallback without widening the catalog to
items AnkiScape cannot otherwise display or store.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Iterable, Mapping

from ..core.constants import ITEM_DEFINITIONS
from ..core.item_registry import ItemDefinition
from .item_values import EXCHANGEABLE_ITEM_NAMES, ITEM_VALUES

try:
    from ..generated.grand_exchange_period_generated import (
        PERIOD_GE_BUY_LIMIT_SOURCE,
        PERIOD_GE_BUY_LIMITS,
        PERIOD_GE_GUIDE_PRICES,
        PERIOD_GE_PRICE_PROVENANCE,
    )
except ImportError:
    PERIOD_GE_BUY_LIMIT_SOURCE = {}
    PERIOD_GE_BUY_LIMITS = {}
    PERIOD_GE_GUIDE_PRICES = {}
    PERIOD_GE_PRICE_PROVENANCE = {}


def _market_source_role(category: str) -> str:
    if category in {"ore", "log", "fish", "runecrafting"}:
        return "raw_material"
    if category in {"bar", "food", "crafted", "fletched", "smithed"}:
        return "processed_good"
    if category in {"gem", "equipment", "hunter"}:
        return "rare_or_dependency"
    return "general"


def build_ge_item_catalog_pure(
    item_definitions: Iterable[ItemDefinition],
    *,
    item_values: Mapping[str, int],
    exchangeable_names: frozenset[str] | set[str],
    period_guide_prices: Mapping[str, int] | None = None,
    period_buy_limits: Mapping[str, int] | None = None,
    period_price_provenance: Mapping[str, Mapping[str, object]] | None = None,
    period_buy_limit_source: Mapping[str, object] | None = None,
) -> dict[str, dict[str, object]]:
    period_guide_prices = period_guide_prices or {}
    period_buy_limits = period_buy_limits or {}
    period_price_provenance = period_price_provenance or {}
    period_buy_limit_source = period_buy_limit_source or {}
    catalog: dict[str, dict[str, object]] = {}
    for item in item_definitions:
        item_name = item.storage_key
        if (
            item_name == "Coins"
            or not item.tradeable
            or item_name not in exchangeable_names
        ):
            continue
        period_price = int(period_guide_prices.get(item_name, 0) or 0)
        cache_value = int(item_values.get(item_name, 0) or 0)
        guide_price = period_price if period_price > 0 else cache_value
        if guide_price <= 0:
            continue
        buy_limit = int(period_buy_limits.get(item_name, 0) or 0)
        catalog[item_name] = {
            "item_name": item_name,
            "item_id": item.id,
            "source_item_id": item.source_item_id,
            "category": item.category,
            "required_level": item.required_level,
            "source_role": _market_source_role(item.category),
            "asset_path": item.asset_path,
            "tradeable": True,
            "exchangeable": True,
            "guide_price": guide_price,
            "guide_price_source": (
                "period_grand_exchange_database"
                if period_price > 0
                else "cache_value_fallback"
            ),
            "guide_price_provenance": dict(
                period_price_provenance.get(item_name, {})
            ),
            "cache_value": cache_value if cache_value > 0 else None,
            "low_alchemy_value": int(cache_value * 0.4) if cache_value > 0 else None,
            "high_alchemy_value": int(cache_value * 0.6) if cache_value > 0 else None,
            "buy_limit": buy_limit if buy_limit > 0 else None,
            "buy_limit_source": (
                dict(period_buy_limit_source) if buy_limit > 0 else None
            ),
        }
    return catalog


GE_ITEM_CATALOG = MappingProxyType(
    build_ge_item_catalog_pure(
        ITEM_DEFINITIONS,
        item_values=ITEM_VALUES,
        exchangeable_names=EXCHANGEABLE_ITEM_NAMES,
        period_guide_prices=PERIOD_GE_GUIDE_PRICES,
        period_buy_limits=PERIOD_GE_BUY_LIMITS,
        period_price_provenance=PERIOD_GE_PRICE_PROVENANCE,
        period_buy_limit_source=PERIOD_GE_BUY_LIMIT_SOURCE,
    )
)
