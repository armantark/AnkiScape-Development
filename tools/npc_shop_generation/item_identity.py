"""Source item identities for NPC stock and player support-price maps."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ItemMeta:
    id: int
    name: str
    tradeable: bool
    equipment: Any


# Storage-key normalizations where the items.yml cache name differs from the
# storage key another AnkiScape system already registered for the same item.
# 4600: items.yml spells it "Willow-blackjack" but The Feud quest catalog
# registers the identical weapon as "Willow blackjack"; without normalization
# the two keys slug-collide and the shop item silently loses its registry
# entry, icon, and Bank category.
ITEM_NAME_NORMALIZATIONS: dict[int, str] = {
    882: "Bronze arrows",
    884: "Iron arrows",
    886: "Steel arrows",
    888: "Mithril arrows",
    890: "Adamant arrows",
    892: "Rune arrows",
    4160: "Broad arrows",
    4522: "Oil lamp (unlit)",
    4525: "Oil lamp (empty)",
    4535: "Oil lantern (empty)",
    4537: "Oil lantern (unlit)",
    4544: "Bullseye lantern (unf)",
    4546: "Bullseye lantern (empty)",
    4548: "Bullseye lantern (unlit)",
    4600: "Willow blackjack",
    5014: "Mining helmet (unlit)",
    23035: "Spiked gauntlets",
}

# Period items present in the rev-742/Darkan cache but absent from the older
# rev-667 items.yml baseline. These are still real shop stock, not unknown rows.
MANUAL_ITEM_METADATA: dict[int, dict[str, Any]] = {
    23035: {
        "name": "Spiked gauntlets",
        "tradeable": False,
        "source": "RuneScape Wiki Spiked gauntlets oldid 5827717; OpenRS2/Darkan item 23035",
    },
}

# The seven arrow entries in data/crafting_data.py's settled storage migration.
# Other save migrations do not define the player-price namespace.
PLAYER_PRICE_NAME_ALIASES: dict[str, str] = {
    "Bronze arrow": "Bronze arrows",
    "Iron arrow": "Iron arrows",
    "Steel arrow": "Steel arrows",
    "Mithril arrow": "Mithril arrows",
    "Adamant arrow": "Adamant arrows",
    "Rune arrow": "Rune arrows",
    "Broad arrow": "Broad arrows",
}

# Historical first-stock identities retain generic price support separately
# from exact-state stock names. Oil lantern's save alias uses 4537 instead.
HISTORICAL_PLAYER_PRICE_IDS: dict[str, int] = {
    "Bullseye lantern": 4546,
    "Mining helmet": 5014,
    "Oil lamp": 4525,
    "Oil lantern": 4535,
}


PLAYER_PRICE_EMISSION_TAIL = (
    "Bronze arrows", "Iron arrows", "Steel arrows", "Mithril arrows",
    "Adamant arrows", "Rune arrows", "Broad arrows",
    "Oil lamp (empty)", "Oil lamp (unlit)", "Oil lantern (empty)", "Oil lantern (unlit)",
    "Bullseye lantern (empty)", "Bullseye lantern (unlit)", "Mining helmet (unlit)",
)


def order_player_price_map(prices: Mapping[str, int]) -> dict[str, int]:
    # Preserve the catalog's appended storage names without requiring their presence.
    ordered = {name: prices[name] for name in sorted(prices) if name not in PLAYER_PRICE_EMISSION_TAIL}
    ordered.update((name, prices[name]) for name in PLAYER_PRICE_EMISSION_TAIL if name in prices)
    return ordered


def _item_name(items: Mapping[int, ItemMeta], item_id: int, fallback: str | None = None) -> str:
    normalized = ITEM_NAME_NORMALIZATIONS.get(item_id)
    if normalized:
        return normalized
    meta = items.get(item_id)
    if meta:
        return meta.name
    if fallback:
        return fallback
    return f"Item {item_id}"


def _live_player_price_ids(
    items: Mapping[int, ItemMeta],
    shops: Iterable[Mapping[str, Any]],
    manual_metadata: Mapping[int, Mapping[str, Any]],
) -> dict[str, int]:
    stock_id_by_name: dict[str, int] = {}
    for shop in shops:
        for row in shop.get("stock", []):
            name = row.get("item_name", "")
            item_id = row.get("item_id")
            if not name or not isinstance(item_id, int) or row.get("disposition") != "live":
                continue
            if (
                item_id not in items
                and item_id in manual_metadata
                and manual_metadata[item_id].get("tradeable") is False
            ):
                continue
            name = PLAYER_PRICE_NAME_ALIASES.get(name, name)
            stock_id_by_name.setdefault(name, item_id)
    return stock_id_by_name


def select_player_price_ids(
    items: Mapping[int, ItemMeta],
    shops: Iterable[Mapping[str, Any]],
    *,
    manual_metadata: Mapping[int, Mapping[str, Any]],
) -> dict[str, int]:
    """Select original metadata, historical projections, then first live IDs.

    Keep original metadata separate from manual stock metadata: only a manual
    explicit-False identity absent from the original supplier is ineligible.
    """
    canonical: dict[str, int] = {}
    for item_id, meta in sorted(items.items()):
        if not meta.tradeable:
            continue
        name = _item_name(items, item_id)
        if not name or name.startswith("Item ") or name.lower().startswith("null"):
            continue
        name = PLAYER_PRICE_NAME_ALIASES.get(name, name)
        canonical.setdefault(name, item_id)
    canonical.update(HISTORICAL_PLAYER_PRICE_IDS)
    canonical.update(_live_player_price_ids(items, shops, manual_metadata))
    return canonical
