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
# A drop is left only if its high-alch value is under this many coins, so the
# default leaves near-worthless junk (feathers, ashes) while keeping a monster's
# real drops (raw meat ~high-alch 35). Tunable; owner may raise it for a harsher
# no-hoarding penalty or lower it toward keep-everything.
DEFAULT_LOOT_VALUE_THRESHOLD = 10

_DEFAULT_PACK_MODE = "balanced"
_VALID_PACK_MODES = frozenset({"balanced", "max_output", "max_safety"})

# Bags pack an otherwise-unstackable material into one slot, so a carried bag is
# worth exactly the extra capacity it grants — fewer bank runs. {bag: (material,
# extra_capacity)}. The Coal bag is present in the Oct-2011 cache but has no
# in-game source yet (Dungeoneering), so it ships live-but-inert: owning one is
# impossible today, but the mechanic lights up with zero further changes.
BAG_DEFINITIONS: dict[str, tuple[str, int]] = {
    "Coal bag": ("Coal", 27),
}


def effective_carried_capacity(view: Any, owned_bags: Any) -> int:
    """Slots before a bank-run, raised by any owned bag whose material is carried.

    A bag replaces up to ``extra_capacity`` one-slot items with a single slot, so
    the trip holds that many more of the material — i.e. the churn threshold rises
    by the bag's capacity while that material is what's being carried.
    """
    capacity = CARRIED_CAPACITY
    if not isinstance(view, Mapping) or not isinstance(owned_bags, (set, frozenset, dict, Mapping)):
        return capacity
    for bag_name, (material, extra) in BAG_DEFINITIONS.items():
        if bag_name in owned_bags and _clean_int(view.get(material, 0), 0) > 0:
            capacity += max(0, int(extra))
    return capacity


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


def filter_loot_pure(
    drops: Any,
    values: Any,
    threshold: Any,
    stackable_names: set[str] | frozenset[str],
) -> tuple[dict[str, int], dict[str, int]]:
    """Split rolled drops into ``(kept, left)`` by the high-alch value filter.

    The owner's rule: do not auto-hoard every tiny drop. A drop is **left** only
    when its value is known *and* below the high-alch threshold *and* it is not a
    stackable — everything else is **kept**. Unknown-value items are kept (never
    leave a possibly-valuable drop for lack of a price); stackables and coins are
    always kept (a stackable costs at most one slot; coins are the money pouch).
    """
    kept: dict[str, int] = {}
    left: dict[str, int] = {}
    if not isinstance(drops, Mapping):
        return kept, left
    value_map = values if isinstance(values, Mapping) else {}
    for item_name, count in drops.items():
        if not isinstance(item_name, str):
            continue
        amount = _clean_int(count, 0, minimum=0)
        if amount <= 0:
            continue
        value = value_map.get(item_name)
        if value is None or item_name == COIN_ITEM_NAME or loot_should_pick_up(item_name, value, threshold, stackable_names):
            kept[item_name] = amount
        else:
            left[item_name] = amount
    return kept, left


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


def inventory_delta_gains(inv_before: Any, inv_after: Any) -> dict[str, int]:
    """The positive per-item delta between two flat-inventory snapshots.

    This is how the overlay learns what an action produced without knowing any
    skill's internals: a tick's gains are whatever went up in the flat store.
    Coins are excluded — they are the money pouch, never carried.
    """
    if not isinstance(inv_after, Mapping):
        return {}
    before = inv_before if isinstance(inv_before, Mapping) else {}
    gains: dict[str, int] = {}
    for item_name, after_count in inv_after.items():
        if not isinstance(item_name, str) or item_name == COIN_ITEM_NAME:
            continue
        gained = _clean_int(after_count, 0) - _clean_int(before.get(item_name, 0), 0)
        if gained > 0:
            gains[item_name] = gained
    return gains


def carried_action_churn_pure(
    inv_before: Any,
    inv_after: Any,
    stackable_names: set[str] | frozenset[str],
) -> int:
    """The slots one action churned = max(slots gained, slots consumed).

    This is the unified teeth signal: gathering churns its output slots,
    consumption churns its input slots, 1:1 processing churns one. Accumulated,
    it forces a bank-run every ``CARRIED_CAPACITY`` slots regardless of skill.
    Coins are excluded (they are the money pouch).
    """
    gains = inventory_delta_gains(inv_before, inv_after)
    before = inv_before if isinstance(inv_before, Mapping) else {}
    after = inv_after if isinstance(inv_after, Mapping) else {}
    losses: dict[str, int] = {}
    for item_name, before_count in before.items():
        if not isinstance(item_name, str) or item_name == COIN_ITEM_NAME:
            continue
        lost = _clean_int(before_count, 0) - _clean_int(after.get(item_name, 0), 0)
        if lost > 0:
            losses[item_name] = lost
    return max(carried_slots_used(gains, stackable_names), carried_slots_used(losses, stackable_names))


def carried_bank_run_gate_pure(
    view: Any,
    churn: Any,
    keep: bool,
    stackable_names: set[str] | frozenset[str],
    target_id: Any,
    bank_run_state: Any,
    reviews_cost: int = SKILLING_BANK_RUN_REVIEWS,
    capacity: int = CARRIED_CAPACITY,
) -> tuple[dict[str, Any], dict[str, int], int, dict[str, Any], bool]:
    """Decide, **before** an action tick, whether the tick is spent banking.

    The teeth: once accumulated ``churn`` reaches ``capacity`` slots the player
    must bank before acting again, so the next answer buys the bank-run instead of
    skill XP — exactly how combat spends answers when supplies run out. ``capacity``
    defaults to ``CARRIED_CAPACITY`` but a bag raises it (see
    ``effective_carried_capacity``).

    Returns ``(new_bank_run_state, new_view, new_churn, event, act)``. ``act=False``
    means skip the action this tick (it went to banking); on a completed run the
    view clears and churn resets (items stay banked in the flat store). Under
    **Drop** nothing is carried and nothing banks, so the tick always acts.
    """
    view = dict(view) if isinstance(view, Mapping) else {}
    churn = _clean_int(churn, 0, minimum=0)
    capacity = _clean_int(capacity, CARRIED_CAPACITY, minimum=1)
    idle = {"active": False, "started": False, "completed": False, "reviews_remaining": 0}
    if not keep:
        return {}, view, churn, idle, True
    active = bool(sanitize_bank_run_state(bank_run_state, reviews_cost))
    full = churn >= capacity
    if not (active or full):
        return sanitize_bank_run_state(bank_run_state, reviews_cost), view, churn, idle, True
    new_state, event = bank_run_progress_pure(bank_run_state, True, target_id, reviews_cost)
    if event.get("completed"):
        view = {}
        churn = 0
    return new_state, view, churn, event, False


def carried_fold_gains_pure(
    view: Any,
    produced: Any,
    stackable_names: set[str] | frozenset[str],
) -> dict[str, int]:
    """Fold a Keep action tick's gains into the carried view (coins excluded).

    Called **after** a tick that acted, so the produced items accumulate in the
    pack until the next gate spends a tick banking them. ``stackable_names`` is
    accepted for symmetry with the rest of the overlay API.
    """
    view = dict(view) if isinstance(view, Mapping) else {}
    if isinstance(produced, Mapping):
        for item_name, qty in produced.items():
            if not isinstance(item_name, str) or item_name == COIN_ITEM_NAME:
                continue
            gained = _clean_int(qty, 0, minimum=0)
            if gained > 0:
                view[item_name] = view.get(item_name, 0) + gained
    return view


def default_carried_state() -> dict[str, Any]:
    return {
        "carried_inventory": {},           # {target_id: {item: count}} — death/loot content
        "carried_churn": {},               # {target_id: int} — slots churned since last bank
        "carried_keep_drop": {},           # {target_id: "keep"|"drop"} — default keep
        "skilling_bank_run": {},           # active {reviews_remaining, target_id} run
        "carried_pack_mode": _DEFAULT_PACK_MODE,
        "loot_value_threshold": DEFAULT_LOOT_VALUE_THRESHOLD,
    }


def carried_keep_for(player_data: Mapping[str, Any], target_id: str) -> bool:
    """Whether a gathering target keeps its product (default) or drops it."""
    if not isinstance(player_data, Mapping):
        return True
    keep_drop = player_data.get("carried_keep_drop")
    if not isinstance(keep_drop, Mapping):
        return True
    return keep_drop.get(target_id, "keep") != "drop"


def sanitize_carried_state(player_data: MutableMapping[str, Any]) -> None:
    defaults = default_carried_state()
    player_data["carried_inventory"] = _sanitize_carried_inventory(player_data.get("carried_inventory"))

    raw_churn = player_data.get("carried_churn")
    player_data["carried_churn"] = (
        {
            str(target_id): _clean_int(value, 0, minimum=0)
            for target_id, value in raw_churn.items()
            if isinstance(target_id, str) and _clean_int(value, 0, minimum=0) > 0
        }
        if isinstance(raw_churn, Mapping)
        else {}
    )

    raw_keep_drop = player_data.get("carried_keep_drop")
    player_data["carried_keep_drop"] = (
        {
            str(target_id): "drop"
            for target_id, value in raw_keep_drop.items()
            if isinstance(target_id, str) and value == "drop"
        }
        if isinstance(raw_keep_drop, Mapping)
        else {}
    )

    player_data["skilling_bank_run"] = sanitize_bank_run_state(
        player_data.get("skilling_bank_run"), SKILLING_BANK_RUN_REVIEWS
    )

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
