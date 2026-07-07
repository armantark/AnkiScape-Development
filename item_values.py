"""Item store values and stackable flags, keyed by item name.

The loot filter (`inventory_pure.loot_should_pick_up`) needs an item's store value
to decide whether a drop is worth carrying. The authoritative source is a full
Darkan-cache dump of every item's `ItemDefinitions.getValue()` and stackable flag
(`item_values_generated.py`, produced by `tools/DumpDarkanItemValues.java` +
`tools/gen_item_values.py`, ~10.7k items). The committed shop buy prices are kept
as a fallback for any name the cache dump lacks. Names with no known value at all
are absent, and callers treat an unknown value as "keep" (never leave a
possibly-valuable drop just because we lack a price).
"""

from typing import Dict, FrozenSet, Optional

try:
    from .shop_data import SHOP_DATA
except ImportError:  # flat imports in tests
    from shop_data import SHOP_DATA

try:  # the generated full-cache table is authoritative when present
    from .item_values_generated import ITEM_VALUES_GENERATED, STACKABLE_ITEM_NAMES_GENERATED
except ImportError:
    try:
        from item_values_generated import ITEM_VALUES_GENERATED, STACKABLE_ITEM_NAMES_GENERATED
    except ImportError:  # dump not generated in this checkout
        ITEM_VALUES_GENERATED, STACKABLE_ITEM_NAMES_GENERATED = {}, frozenset()


def _build_item_tables() -> "tuple[Dict[str, int], FrozenSet[str]]":
    # Shop-derived tables are the fallback; the generated cache values override.
    values: Dict[str, int] = {}
    stackable: set = set()
    for shop in SHOP_DATA.values():
        for row in shop.get("stock", ()) or ():
            name = row.get("item_name")
            if not isinstance(name, str):
                continue
            price = row.get("buy_price")
            if isinstance(price, int) and price > 0:
                values[name] = max(values.get(name, 0), price)
            if row.get("stackable"):
                stackable.add(name)
    values.update(ITEM_VALUES_GENERATED)  # real cache getValue() wins over the proxy
    stackable |= set(STACKABLE_ITEM_NAMES_GENERATED)
    return values, frozenset(stackable)


ITEM_VALUES, STACKABLE_ITEM_NAMES = _build_item_tables()


def item_store_value(item_name: str) -> Optional[int]:
    """The item's store value, or ``None`` when no committed price is known."""
    return ITEM_VALUES.get(item_name)
