"""Pure carried-inventory helpers for AnkiScape.

The flat inventory remains the bank. This module models the 28-slot carried
overlay and the pouch-only coin balance without importing Anki or UI code.
"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any


CARRIED_CAPACITY = 28
# Coins are the money pouch: canonical in the flat bank, never carried, never
# dropped on death. Kept as a name so the overlay/death/loot paths can exclude it.
COIN_ITEM_NAME = "Coins"
HIGH_ALCH_VALUE_FACTOR = 0.6
# Declared AnkiScape balance knob for automatic loot pickup, not a source value.
DEFAULT_LOOT_VALUE_THRESHOLD = 50

_DEFAULT_PACK_MODE = "balanced"
_VALID_PACK_MODES = frozenset({"balanced", "max_output", "max_safety"})


def carried_slots_used(carried: Mapping[str, int], stackable_names: set[str] | frozenset[str]) -> int:
    """Return occupied carried slots using RuneScape stackability semantics."""
    if not isinstance(carried, Mapping):
        return 0
    slots = 0
    for item_name, raw_count in carried.items():
        count = _clean_int(raw_count, 0)
        if count <= 0:
            continue
        # Stackable item names consume one slot because quantity is stored on
        # the stack, not by duplicating carried slots.
        slots += 1 if item_name in stackable_names else count
    return slots


def carried_capacity_remaining(carried: Mapping[str, int], stackable_names: set[str] | frozenset[str]) -> int:
    return max(0, CARRIED_CAPACITY - carried_slots_used(carried, stackable_names))


def carried_has_room_for(
    carried: Mapping[str, int],
    item_name: str,
    count: int,
    stackable_names: set[str] | frozenset[str],
) -> bool:
    add_count = _clean_int(count, 0)
    used = carried_slots_used(carried, stackable_names)
    if add_count <= 0:
        return used <= CARRIED_CAPACITY
    if item_name in stackable_names:
        current_count = _clean_int(carried.get(item_name, 0), 0) if isinstance(carried, Mapping) else 0
        extra_slots = 0 if current_count > 0 else 1
    else:
        extra_slots = add_count
    return used + extra_slots <= CARRIED_CAPACITY


def high_alch_value(cache_value: Any) -> int:
    try:
        value = float(cache_value)
        alch_value = int(HIGH_ALCH_VALUE_FACTOR * value)
    except (TypeError, ValueError, OverflowError):
        alch_value = 0
    return max(0, alch_value)


def loot_should_pick_up(
    item_name: str,
    item_cache_value: Any,
    threshold: Any,
    stackable_names: set[str] | frozenset[str],
) -> bool:
    if item_name in stackable_names:
        return True
    clean_threshold = _clean_int(threshold, DEFAULT_LOOT_VALUE_THRESHOLD, minimum=0)
    return high_alch_value(item_cache_value) >= clean_threshold


def money_pouch_balance(player_data: Mapping[str, Any]) -> int:
    """The money-pouch balance: the coin count surfaced from the flat bank.

    Coins are the money pouch. They live canonically in ``inventory[COIN_ITEM_NAME]``
    (the same store shops, quests, and crafting already transact through) and are
    simply never placed in a carried slot and never dropped on death. There is no
    separate coin store, so nothing to repoint and no way to strand a balance.
    """
    if not isinstance(player_data, Mapping):
        return 0
    inventory = player_data.get("inventory")
    if not isinstance(inventory, Mapping):
        return 0
    return _clean_int(inventory.get(COIN_ITEM_NAME), 0, minimum=0)


def default_carried_state() -> dict[str, Any]:
    return {
        "carried_inventory": {},
        "carried_pack_mode": _DEFAULT_PACK_MODE,
        "loot_value_threshold": DEFAULT_LOOT_VALUE_THRESHOLD,
    }


def sanitize_carried_state(player_data: MutableMapping[str, Any]) -> None:
    defaults = default_carried_state()
    player_data["carried_inventory"] = _sanitize_carried_inventory(player_data.get("carried_inventory"))

    pack_mode = player_data.get("carried_pack_mode", defaults["carried_pack_mode"])
    player_data["carried_pack_mode"] = pack_mode if pack_mode in _VALID_PACK_MODES else defaults["carried_pack_mode"]

    player_data["loot_value_threshold"] = _clean_int(
        player_data.get("loot_value_threshold"),
        defaults["loot_value_threshold"],
        minimum=0,
    )


def _sanitize_carried_inventory(raw_inventory: Any) -> dict[str, dict[str, int]]:
    if not isinstance(raw_inventory, Mapping):
        return {}
    clean_inventory: dict[str, dict[str, int]] = {}
    for target_id, target_items in raw_inventory.items():
        if not isinstance(target_id, str) or not isinstance(target_items, Mapping):
            continue
        clean_items: dict[str, int] = {}
        for item_name, count in target_items.items():
            if not isinstance(item_name, str):
                continue
            clean_count = _clean_int(count, 0, minimum=0)
            if clean_count > 0:
                clean_items[item_name] = clean_count
        if clean_items:
            clean_inventory[target_id] = clean_items
    return clean_inventory


def _clean_int(value: Any, default: int, *, minimum: int | None = None) -> int:
    try:
        out = int(value)
    except (TypeError, ValueError):
        out = default
    if minimum is not None:
        out = max(minimum, out)
    return out
