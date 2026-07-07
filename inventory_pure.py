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


def coerce_pack_mode(mode: Any) -> str:
    return mode if mode in _VALID_PACK_MODES else _DEFAULT_PACK_MODE


def pack_carried_inventory_pure(
    bank: Mapping[str, int],
    spec: Mapping[str, Any],
    mode: Any,
    stackable_names: set[str] | frozenset[str],
) -> dict[str, int]:
    """Fill up to ``CARRIED_CAPACITY`` slots from ``bank`` for one target.

    This is the casual preset packer: the player picks a ``mode`` and the loadout
    falls out of it, so no per-depletion micromanagement is needed. It never
    invents materials — every count is capped by what the bank actually holds.

    ``spec`` describes the target's carry needs (all keys optional):
      ``required``: {item: count} held items that must be carried (e.g. a mould),
        one slot each. Packed first; a target cannot run without them.
      ``food``: [item, ...] ordered food candidates (combat); empty for skilling.
      ``food_reserve``: slots to reserve for food under the balanced mode.
      ``primary``: the material that fills the remaining slots.

    ``mode`` shifts only the food reserve: ``max_output`` drops it to zero (every
    free slot to the primary), ``max_safety`` doubles it, ``balanced`` uses it
    as given. Bags (which pack an unstackable material into one slot) land with
    the bag slice; they will apply automatically when owned, under any mode.
    """
    mode = coerce_pack_mode(mode)
    if not isinstance(bank, Mapping):
        bank = {}
    if not isinstance(spec, Mapping):
        spec = {}

    carried: dict[str, int] = {}

    def _bank(name: str) -> int:
        return _clean_int(bank.get(name), 0, minimum=0)

    # 1. Required held items — one slot each, only what the bank can supply.
    required = spec.get("required") or {}
    if isinstance(required, Mapping):
        for item_name, count in required.items():
            if not isinstance(item_name, str):
                continue
            want = min(_clean_int(count, 0, minimum=0), _bank(item_name))
            if want > 0 and carried_has_room_for(carried, item_name, want, stackable_names):
                carried[item_name] = carried.get(item_name, 0) + want

    # 2. Food reserve — mode-scaled, drawn in the target's preferred order.
    reserve = _clean_int(spec.get("food_reserve"), 0, minimum=0)
    if mode == "max_output":
        reserve = 0
    elif mode == "max_safety":
        reserve *= 2
    food = spec.get("food") or ()
    for item_name in food:
        if reserve <= 0:
            break
        if not isinstance(item_name, str):
            continue
        want = min(reserve, _bank(item_name))
        # Food is unstackable; each unit is a slot, so it also draws down reserve.
        placed = 0
        while placed < want and carried_has_room_for(carried, item_name, 1, stackable_names):
            carried[item_name] = carried.get(item_name, 0) + 1
            placed += 1
        reserve -= placed

    # 3. Primary material fills whatever slots remain.
    primary = spec.get("primary")
    if isinstance(primary, str) and primary:
        available = _bank(primary)
        if primary in stackable_names:
            # A stackable takes a single slot for any count.
            if available > 0 and carried_has_room_for(carried, primary, available, stackable_names):
                carried[primary] = carried.get(primary, 0) + available
        else:
            while available > 0 and carried_has_room_for(carried, primary, 1, stackable_names):
                carried[primary] = carried.get(primary, 0) + 1
                available -= 1

    return carried


# Skilling banks at one review (combat keeps its own two); tunable.
SKILLING_BANK_RUN_REVIEWS = 1


def sanitize_bank_run_state(raw: Any, max_reviews: int) -> dict[str, Any]:
    if not isinstance(raw, Mapping):
        return {}
    remaining = min(_clean_int(raw.get("reviews_remaining"), 0, minimum=0), max_reviews)
    if remaining <= 0:
        return {}
    state: dict[str, Any] = {"reviews_remaining": remaining}
    target_id = raw.get("target_id")
    if isinstance(target_id, str):
        state["target_id"] = target_id
    return state


def bank_run_progress_pure(
    state: Any,
    needed: bool,
    target_id: Any,
    reviews_cost: int,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Advance a bank-run state machine one review, mirroring combat's.

    The overlay is empty (or full) and the bank can refill: the caller passes
    ``needed=True`` and this charges ``reviews_cost`` review-answers before the
    refill. Returns ``(new_state, event)``; ``event`` carries ``started``,
    ``completed`` (the caller repacks the carried subset on completion), and the
    remaining review count. A run for a different target is abandoned.
    """
    state = sanitize_bank_run_state(state, reviews_cost)
    if state and state.get("target_id") not in (None, target_id):
        state = {}
    started = False
    if not state and needed:
        state = {"reviews_remaining": max(1, int(reviews_cost))}
        if isinstance(target_id, str):
            state["target_id"] = target_id
        started = True
    if not state:
        return {}, {"active": False, "started": False, "completed": False, "reviews_remaining": 0}
    remaining = _clean_int(state.get("reviews_remaining"), 0, minimum=0) - 1
    if remaining <= 0:
        return {}, {"active": True, "started": started, "completed": True, "reviews_remaining": 0}
    new_state: dict[str, Any] = {"reviews_remaining": remaining}
    if isinstance(target_id, str):
        new_state["target_id"] = target_id
    return new_state, {"active": True, "started": started, "completed": False, "reviews_remaining": remaining}


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
