"""Best-available item store values, derived from committed shop buy prices.

The loot filter (`inventory_pure.loot_should_pick_up`) needs an item's store value
to decide whether a drop is worth carrying. A complete value table would come from
a full Darkan-cache dump of every item's `ItemDefinitions.getValue()`, but that
extractor needs JDK 24 (the core jar is class-file v68) and is a later slice.

Until then the shop **buy price** is the closest already-committed proxy: for coin
shops `getBuyPrice` returns the cache `value` (or an enum override), so an item's
buy price is its store value. Items that appear in no shop are simply absent here,
and callers treat an unknown value as "keep" (never leave a possibly-valuable drop
just because we lack a price).
"""

from typing import Dict, FrozenSet, Optional

try:
    from .shop_data import SHOP_DATA
except ImportError:  # flat imports in tests
    from shop_data import SHOP_DATA


def _build_item_tables() -> "tuple[Dict[str, int], FrozenSet[str]]":
    values: Dict[str, int] = {}
    stackable: set = set()
    for shop in SHOP_DATA.values():
        for row in shop.get("stock", ()) or ():
            name = row.get("item_name")
            if not isinstance(name, str):
                continue
            price = row.get("buy_price")
            if isinstance(price, int) and price > 0:
                # A few items sell in multiple shops; keep the highest listed price.
                values[name] = max(values.get(name, 0), price)
            # The cache `stackable` flag rides along on shop stock rows (the item
            # registry's own flag is unpopulated). It is the reliable source.
            if row.get("stackable"):
                stackable.add(name)
    return values, frozenset(stackable)


ITEM_VALUES, STACKABLE_ITEM_NAMES = _build_item_tables()


def item_store_value(item_name: str) -> Optional[int]:
    """The item's store value, or ``None`` when no committed price is known."""
    return ITEM_VALUES.get(item_name)
