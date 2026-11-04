"""Item names older builds saved, and the load-time rename of every place a save keeps one."""

from typing import Any, Dict

from ..data.cooking_data import LEGACY_COOKING_ITEM_MIGRATIONS
from ..data.crafting_data import LEGACY_CRAFTING_ITEM_MIGRATIONS
from ..data.quest_data import QUEST_REWARD_ITEM_NAME_OVERRIDES

# Saves keep item names from older builds that no stage, action, shop row or
# offer reads any more: quest rewards granted under their source spellings
# ("Amulet of ghostspeak") and items renamed to their 2012 cache names ("Grain").
LEGACY_ITEM_NAME_MIGRATIONS = {
    **LEGACY_CRAFTING_ITEM_MIGRATIONS, **LEGACY_COOKING_ITEM_MIGRATIONS, **QUEST_REWARD_ITEM_NAME_OVERRIDES,
}


def renamed_item(item_name: Any) -> Any:
    return LEGACY_ITEM_NAME_MIGRATIONS.get(item_name, item_name) if isinstance(item_name, str) else item_name


def migrate_legacy_item_inventory(inventory: Any) -> None:
    if not isinstance(inventory, dict):
        return
    for legacy_key, new_key in LEGACY_ITEM_NAME_MIGRATIONS.items():
        if legacy_key not in inventory:
            continue
        try:
            amount = int(inventory.get(legacy_key, 0))
        except (TypeError, ValueError):
            amount = 0
        if amount:
            inventory[new_key] = inventory.get(new_key, 0) + amount
        inventory.pop(legacy_key, None)


def _rename_item_keys(store: Any) -> None:
    if not isinstance(store, dict):
        return
    for old_name, new_name in LEGACY_ITEM_NAME_MIGRATIONS.items():
        if old_name in store:
            store.setdefault(new_name, store.pop(old_name))


def _migrate_grave_item_names(state: Any) -> None:
    if not isinstance(state, dict):
        return
    if isinstance(state.get("items"), list):
        state["items"] = [renamed_item(item_name) for item_name in state["items"]]
    if isinstance(state.get("loadout"), dict):
        state["loadout"] = {slot: renamed_item(item_name) for slot, item_name in state["loadout"].items()}


def _migrate_grand_exchange_item_names(data: Dict[str, Any]) -> None:
    # An offer fills and pays out under its own item name: one left under a
    # retired name would never fill, and would collect an item nothing reads.
    for record_key in ("ge_player_orders", "ge_fill_log"):
        for record in data.get(record_key) or ():
            if isinstance(record, dict):
                record["item_name"] = renamed_item(record.get("item_name"))
    market = data.get("ge_market_state")
    _rename_item_keys(market.get("items") if isinstance(market, dict) else None)
    _rename_item_keys(data.get("ge_buy_limit_usage"))
    _rename_item_keys(data.get("ge_trade_history"))


def migrate_legacy_item_references(data: Dict[str, Any]) -> None:
    for collection_key in ("carried_inventory", "carried_layout"):
        collection = data.get(collection_key)
        for item_store in collection.values() if isinstance(collection, dict) else ():
            migrate_legacy_item_inventory(item_store)

    _rename_item_keys(data.get("loot_overrides"))

    for state_key in ("combat_grave", "death_office"):
        _migrate_grave_item_names(data.get(state_key))

    if "magic_alchemy_item" in data:
        data["magic_alchemy_item"] = renamed_item(data["magic_alchemy_item"])

    _migrate_grand_exchange_item_names(data)
