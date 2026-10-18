"""Item store values and stackable flags, keyed by item name.

The loot filter (`inventory_pure.loot_should_pick_up`) needs an item's store value
to decide whether a drop is worth carrying. The authoritative source is a full
Darkan-cache dump of every item's `ItemDefinitions.getValue()` and stackable flag
(`item_values_generated.py`, produced by `tools/DumpDarkanItemValues.java` +
`tools/gen_item_values.py`, ~10.7k items). The same dump carries the cache's
Grand Exchange eligibility flag. The committed shop buy prices are kept as a
fallback for any name the cache dump lacks. Names with no known value at all are
absent, and callers treat an unknown value as "keep" (never leave a
possibly-valuable drop just because we lack a price).
"""

from typing import Dict, FrozenSet, Optional

from .shop_data import SHOP_DATA
from .summoning_data import SUMMONING_POUCHES as _SUMMONING_POUCHES

try:  # the generated full-cache table is authoritative when present
    from ..generated.item_values_generated import (
        EXCHANGEABLE_ITEM_NAMES_GENERATED,
        ITEM_VALUES_GENERATED,
        STACKABLE_ITEM_NAMES_GENERATED,
    )
except ImportError:  # dump not generated in this checkout
    ITEM_VALUES_GENERATED = {}
    STACKABLE_ITEM_NAMES_GENERATED = frozenset()
    EXCHANGEABLE_ITEM_NAMES_GENERATED = frozenset()


# Multiple cache identities collapse to this display name, including a
# stackable technical variant. The player-facing essence item occupies one
# inventory slot per unit in the period game.
_FORCED_UNSTACKABLE_ITEM_NAMES = frozenset({"Rune essence", "Pure essence"})

# These exact pouch IDs use different names in the period cache and player storage.
_POUCH_CACHE_NAMES_BY_ID = {
    12053: "Vampyre bat pouch",
    12095: "Sp. cockatrice pouch",
    12105: "Sp. coraxatrice pouch",
    12097: "Sp. guthatrice pouch",
    12103: "Sp. pengatrice pouch",
    12099: "Sp. saratrice pouch",
    12107: "Sp. vulatrice pouch",
    12101: "Sp. zamatrice pouch",
}


def _plural_alias(name: str) -> str:
    """AnkiScape names some stacks in the plural where the cache is singular
    ('Arrow shafts' vs 'Arrow shaft', 'Bronze arrows' vs 'Bronze arrow')."""
    return f"{name}s"


def _add_plural_aliases(
    values: Dict[str, int],
    stackable: set,
    exchangeable: set,
) -> None:
    """Register the plural form of each cache name as an alias of the singular.

    Without this the lookup silently misses for every plural-named registry item
    (219 of them), so a stackable item like Arrow shafts is treated as UNSTACKABLE:
    slot accounting then counts 15 shafts as 15 slots, and Fletching forces a bank
    run every other action. Aliases never overwrite a real cache entry, so a genuine
    distinct item whose name happens to be another's plural is left alone.
    """
    for name in list(stackable):
        alias = _plural_alias(name)
        if alias not in stackable and alias not in values:
            stackable.add(alias)
    for name, value in list(values.items()):
        alias = _plural_alias(name)
        if alias not in values:
            values[alias] = value
    for name in list(exchangeable):
        alias = _plural_alias(name)
        if alias not in exchangeable:
            exchangeable.add(alias)


def _add_cache_name_aliases(values: Dict[str, int], exchangeable: set) -> None:
    for pouch in _SUMMONING_POUCHES:
        cache_name = _POUCH_CACHE_NAMES_BY_ID.get(pouch.pouch_item_id)
        if (
            cache_name is not None
            and cache_name in ITEM_VALUES_GENERATED
            and pouch.pouch_name not in ITEM_VALUES_GENERATED
        ):
            values[pouch.pouch_name] = ITEM_VALUES_GENERATED[cache_name]
            if cache_name in exchangeable:
                exchangeable.add(pouch.pouch_name)
    # Rev-727/742 item 5014 uses this state-qualified storage key.
    if "Mining helmet" in exchangeable:
        exchangeable.add("Mining helmet (unlit)")
    # Rev-727/742 worn variants share their cache name and value with the blue hat.
    for name in ("Mystic hat (dark)", "Mystic hat (light)"):
        if "Mystic hat" in ITEM_VALUES_GENERATED and name not in ITEM_VALUES_GENERATED:
            values[name] = ITEM_VALUES_GENERATED["Mystic hat"]
            if "Mystic hat" in exchangeable:
                exchangeable.add(name)


def _build_item_tables() -> "tuple[Dict[str, int], FrozenSet[str], FrozenSet[str]]":
    # Shop-derived tables are the fallback; the generated cache values override.
    values: Dict[str, int] = {}
    stackable: set = set()
    exchangeable: set = set(EXCHANGEABLE_ITEM_NAMES_GENERATED)
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
    # The server dump calls the first degradable tier ``(deg)`` while the
    # period client CS2 names the same item ``100``. Keep both identities
    # valuable so unsafe-death selection does not treat a newly worn item as 0.
    for name, value in list(values.items()):
        if name.endswith(" (deg)"):
            values.setdefault(f"{name.removesuffix(' (deg)')} 100", value)
    stackable |= set(STACKABLE_ITEM_NAMES_GENERATED)
    _add_plural_aliases(values, stackable, exchangeable)
    _add_cache_name_aliases(values, exchangeable)
    stackable.difference_update(_FORCED_UNSTACKABLE_ITEM_NAMES)
    return values, frozenset(stackable), frozenset(exchangeable)


ITEM_VALUES, STACKABLE_ITEM_NAMES, EXCHANGEABLE_ITEM_NAMES = _build_item_tables()


def item_store_value(item_name: str) -> Optional[int]:
    """The item's store value, or ``None`` when no committed price is known."""
    return ITEM_VALUES.get(item_name)
