"""Pure carried-inventory helpers for AnkiScape.

The flat inventory remains the bank. This module models the 28-slot carried
overlay and the pouch-only coin balance without importing Anki or UI code.

Why this sits in ``logic/`` and not ``logic_pure/`` despite the name: the
``logic_pure/`` package is not "the pure code", it is the pieces of the former
12,710-line ``logic_pure.py`` monolith, kept together so that split stays
reviewable. Everything else that is pure domain logic lives in ``logic/``,
whether or not its filename says ``pure``. Both packages are Qt-free; the
distinction is provenance, not purity.
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


def set_carried_layout_quantity_pure(
    layout: Mapping[str, int],
    item_name: str,
    quantity: int,
    stackable_names: set[str] | frozenset[str],
    capacity: int = CARRIED_CAPACITY,
) -> tuple[dict[str, int], bool]:
    """Set one desired pack quantity without disturbing its queue position."""
    current = dict(layout) if isinstance(layout, Mapping) else {}
    if not isinstance(item_name, str) or not item_name:
        return current, False
    try:
        desired = int(quantity)
    except (TypeError, ValueError, OverflowError):
        return current, False
    if desired < 0:
        return current, False

    candidate = dict(current)
    if desired:
        candidate[item_name] = desired
    else:
        candidate.pop(item_name, None)
    capacity = _clean_int(capacity, CARRIED_CAPACITY, minimum=1)
    if carried_slots_used(candidate, stackable_names) > capacity:
        return current, False
    return candidate, True


def discard_inventory_quantity_pure(
    inventory: Mapping[str, int],
    item_name: str,
    quantity: int,
) -> tuple[dict[str, int], bool]:
    """Discard an exact positive bank quantity while preserving the remainder."""
    current = dict(inventory) if isinstance(inventory, Mapping) else {}
    if not isinstance(item_name, str) or not item_name:
        return current, False
    try:
        discard_count = int(quantity)
    except (TypeError, ValueError, OverflowError):
        return current, False
    available = _clean_int(current.get(item_name, 0), 0, minimum=0)
    if discard_count <= 0 or discard_count > available:
        return current, False
    current[item_name] = available - discard_count
    return current, True


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
    overrides: Any = None,
) -> tuple[dict[str, int], dict[str, int]]:
    """Split rolled drops into ``(kept, left)``.

    ``overrides`` ({item: "keep"|"leave"}) is the advanced per-drop control and
    wins first: an explicit "keep" is picked up even below the threshold, an
    explicit "leave" is dropped even if valuable (coins are exempt — they are the
    money pouch and always kept). Otherwise the casual rule applies: do not
    auto-hoard tiny drops — a drop is **left** only when its value is known *and*
    below the high-alch threshold *and* it is not a stackable; unknown-value items
    are kept (never leave a possibly-valuable drop for lack of a price), and
    stackables and coins are always kept.
    """
    kept: dict[str, int] = {}
    left: dict[str, int] = {}
    if not isinstance(drops, Mapping):
        return kept, left
    value_map = values if isinstance(values, Mapping) else {}
    override_map = overrides if isinstance(overrides, Mapping) else {}
    for item_name, count in drops.items():
        if not isinstance(item_name, str):
            continue
        amount = _clean_int(count, 0, minimum=0)
        if amount <= 0:
            continue
        override = override_map.get(item_name)
        if item_name == COIN_ITEM_NAME or override == "keep":
            kept[item_name] = amount
            continue
        if override == "leave":
            left[item_name] = amount
            continue
        value = value_map.get(item_name)
        if value is None or loot_should_pick_up(item_name, value, threshold, stackable_names):
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


def _processing_pack_slots(
    actions: int,
    requirements: Mapping[str, int],
    stackable_names: set[str] | frozenset[str],
    bags: Mapping[str, int],
) -> int:
    """Slots a pack holding ``actions`` worth of a recipe's inputs would occupy."""
    total = 0
    for item_name, need in requirements.items():
        units = _clean_int(need, 0, minimum=0) * actions
        if units <= 0:
            continue
        if item_name in stackable_names:
            total += 1
        elif item_name in bags:
            # The bag holds its capacity in one slot; the overflow rides loose.
            total += 1 + max(0, units - _clean_int(bags.get(item_name), 0, minimum=0))
        else:
            total += units
    return total


def pack_processing_inputs_pure(
    bank: Mapping[str, int],
    requirements: Mapping[str, int],
    capacity: int,
    stackable_names: set[str] | frozenset[str],
    bags: Mapping[str, int] | None = None,
) -> dict[str, int]:
    """Fill a processing target's carried pack with its recipe inputs.

    Packs the most *actions* the 28 slots can carry, honouring the recipe's ratio.
    An even split across materials is wrong: Steel needs 1 iron : 2 coal, so an even
    14/14 runs out of coal after 7 smelts and wastes 7 iron slots. Solving for the
    largest whole number of actions the budget allows gives 9 iron + 18 coal, i.e.
    9 smelts — and with a Coal bag (27 coal in one slot) it frees the slots to reach
    18, which is exactly what a coal bag buys you in the real game.

    Never invents materials: the action count is also capped by what the bank holds.
    """
    if not isinstance(bank, Mapping) or not isinstance(requirements, Mapping):
        return {}
    needs = {
        name: _clean_int(need, 0, minimum=0)
        for name, need in requirements.items()
        if isinstance(name, str) and _clean_int(need, 0, minimum=0) > 0
    }
    if not needs:
        return {}
    bags = bags if isinstance(bags, Mapping) else {}
    capacity = _clean_int(capacity, CARRIED_CAPACITY, minimum=1)

    # Never pack more trips than the bank can supply of the scarcest material.
    max_actions = min(_clean_int(bank.get(name), 0, minimum=0) // need for name, need in needs.items())
    # For stackable-only recipes, every complete batch fits whenever one does.
    step = max_actions if needs.keys() <= stackable_names else 1
    actions = 0
    while actions < max_actions and _processing_pack_slots(actions + 1, needs, stackable_names, bags) <= capacity:
        actions += step
    if actions <= 0:
        return {}
    return {name: need * actions for name, need in needs.items()}


def apply_carried_layout_pure(
    bank: Mapping[str, int],
    layout: Mapping[str, int],
    capacity: int,
    stackable_names: set[str] | frozenset[str],
) -> dict[str, int]:
    """Apply an advanced player's saved layout, capped by the bank and capacity.

    The layout is the arrangement the player set once in the 4x7 grid; this caps
    each entry by what the bank actually holds (never invents materials) and by
    the slot budget (in case a bag was removed and capacity shrank since saving).
    Entries are applied in the saved order, first-come-first-served on capacity.
    """
    if not isinstance(bank, Mapping) or not isinstance(layout, Mapping):
        return {}
    capacity = _clean_int(capacity, CARRIED_CAPACITY, minimum=1)
    carried: dict[str, int] = {}
    for item_name, desired_count in layout.items():
        if not isinstance(item_name, str):
            continue
        want = min(_clean_int(desired_count, 0, minimum=0), _clean_int(bank.get(item_name), 0, minimum=0))
        if want <= 0:
            continue
        if item_name in stackable_names:
            already_present = item_name in carried
            if already_present or carried_slots_used(carried, stackable_names) < capacity:
                carried[item_name] = carried.get(item_name, 0) + want
        else:
            placed = 0
            while placed < want and carried_slots_used(carried, stackable_names) < capacity:
                carried[item_name] = carried.get(item_name, 0) + 1
                placed += 1
    return carried


# Skilling banks at one review (combat keeps its own two); tunable.
SKILLING_BANK_RUN_REVIEWS = 1


def request_carried_bank_run_now_pure(
    player_data: Mapping[str, Any], target_id: Any
) -> tuple[dict[str, Any], bool, str]:
    """Request that the target's next review starts its normal bank route."""
    data = dict(player_data) if isinstance(player_data, Mapping) else {}
    if not isinstance(target_id, str) or not target_id:
        return data, False, "No active target can make a bank run."
    data["skilling_bank_run_requested"] = target_id
    return data, True, ""


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
    total = _clean_int(raw.get("reviews_total"), 0, minimum=0)
    if total > 0:
        state["reviews_total"] = max(remaining, min(total, max_reviews))
    route_label = raw.get("route_label")
    if isinstance(route_label, str) and route_label:
        state["route_label"] = route_label
    raw_phases = raw.get("route_phases")
    if isinstance(raw_phases, (list, tuple)):
        phases = []
        for raw_phase in raw_phases:
            if not isinstance(raw_phase, Mapping):
                continue
            phase_id = raw_phase.get("id")
            label = raw_phase.get("label")
            reviews = _clean_int(raw_phase.get("reviews"), 0, minimum=0)
            if not isinstance(phase_id, str) or not phase_id or reviews <= 0:
                continue
            phases.append(
                {
                    "id": phase_id,
                    "label": label if isinstance(label, str) and label else phase_id,
                    "reviews": reviews,
                }
            )
        if phases and sum(phase["reviews"] for phase in phases) == state.get(
            "reviews_total", remaining
        ):
            state["route_phases"] = phases
    if raw.get("outbound_teleport_used") is True:
        state["outbound_teleport_used"] = True
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
    for key in (
        "reviews_total",
        "route_label",
        "route_phases",
        "outbound_teleport_used",
    ):
        if key in state:
            new_state[key] = state[key]
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
    force: bool = False,
) -> tuple[dict[str, Any], dict[str, int], int, dict[str, Any], bool]:
    """Decide, **before** an action tick, whether the tick is spent banking.

    The teeth: once accumulated ``churn`` reaches ``capacity`` slots the player
    must bank before acting again, so the next answer buys the bank-run instead of
    skill XP — exactly how combat spends answers when supplies run out. ``capacity``
    defaults to ``CARRIED_CAPACITY`` but a bag raises it (see
    ``effective_carried_capacity``). ``force`` is an additional, more precise
    trigger: processing targets pass it when the carried pack has run out of a
    required input even though churn hasn't reached capacity yet (a lopsided
    recipe can run dry early) — the pack literally cannot supply the next action.

    Returns ``(new_bank_run_state, new_view, new_churn, event, act)``. ``act=False``
    means skip the action this tick (it went to banking); on a completed run the
    view clears and churn resets (the caller repacks both from the bank). Under
    **Drop** nothing is carried and nothing banks, so the tick always acts.
    """
    view = dict(view) if isinstance(view, Mapping) else {}
    churn = _clean_int(churn, 0, minimum=0)
    capacity = _clean_int(capacity, CARRIED_CAPACITY, minimum=1)
    idle = {"active": False, "started": False, "completed": False, "reviews_remaining": 0}
    if not keep:
        return {}, view, churn, idle, True
    active = bool(sanitize_bank_run_state(bank_run_state, reviews_cost))
    full = churn >= capacity or bool(force)
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


def carried_fold_gains_with_overflow_pure(
    view: Any,
    produced: Any,
    stackable_names: set[str] | frozenset[str],
    capacity: int = CARRIED_CAPACITY,
) -> tuple[dict[str, int], dict[str, int]]:
    """Fill remaining carried slots and return the excess sent to the Bank.

    The flat inventory already owns every produced item; this helper only
    projects which gains still fit in the physical carried view. It is used by
    the Evil Tree blessing's source behavior when eligible logs are banked from
    a full pack.
    """

    carried = dict(view) if isinstance(view, Mapping) else {}
    overflow: dict[str, int] = {}
    remaining_slots = max(
        0,
        _clean_int(capacity, CARRIED_CAPACITY, minimum=1)
        - carried_slots_used(carried, stackable_names),
    )
    if not isinstance(produced, Mapping):
        return carried, overflow

    for item_name, raw_quantity in produced.items():
        if not isinstance(item_name, str) or item_name == COIN_ITEM_NAME:
            continue
        quantity = _clean_int(raw_quantity, 0, minimum=0)
        if quantity <= 0:
            continue
        if item_name in stackable_names:
            fits = quantity if item_name in carried or remaining_slots > 0 else 0
            if fits and item_name not in carried:
                remaining_slots -= 1
        else:
            fits = min(quantity, remaining_slots)
            remaining_slots -= fits
        if fits:
            carried[item_name] = carried.get(item_name, 0) + fits
        if quantity > fits:
            overflow[item_name] = quantity - fits
    return carried, overflow


def layout_to_grid_cells_pure(
    layout: Any,
    stackable_names: set[str] | frozenset[str],
    capacity: int = CARRIED_CAPACITY,
) -> list[tuple[str | None, int]]:
    """Expand a ``{item: count}`` layout into exactly ``capacity`` grid cells.

    Each cell is ``(item_name, display_count)``; an empty cell is ``(None, 0)``.
    A stackable item takes one cell showing its full count; an unstackable item
    takes one cell per unit (each showing count 1). Overflow beyond ``capacity``
    is simply not shown — this is a display of the *saved* layout, and
    ``apply_carried_layout_pure`` is what actually caps it at bank-run time.
    """
    capacity = _clean_int(capacity, CARRIED_CAPACITY, minimum=1)
    cells: list[tuple[str | None, int]] = []
    if isinstance(layout, Mapping):
        for item_name, raw_count in layout.items():
            if not isinstance(item_name, str) or len(cells) >= capacity:
                continue
            count = _clean_int(raw_count, 0, minimum=0)
            if count <= 0:
                continue
            if item_name in stackable_names:
                cells.append((item_name, count))
            else:
                for _ in range(count):
                    if len(cells) >= capacity:
                        break
                    cells.append((item_name, 1))
    while len(cells) < capacity:
        cells.append((None, 0))
    return cells[:capacity]


def default_carried_state() -> dict[str, Any]:
    return {
        "carried_inventory": {},           # {target_id: {item: count}} — death/loot content
        "carried_churn": {},               # {target_id: int} — slots churned since last bank
        "carried_keep_drop": {},           # {target_id: "keep"|"drop"} — default keep
        "skilling_bank_run": {},           # active {reviews_remaining, target_id} run
        "skilling_bank_run_requested": "", # target whose next review starts a run
        "agility_last_travel": {},         # last target-local endurance/weight projection
        "loot_value_threshold": DEFAULT_LOOT_VALUE_THRESHOLD,
        "loot_overrides": {},              # {item: "keep"|"leave"} advanced per-drop
        "carried_layout": {},              # {target_id: {item: count}} — advanced saved 4x7 arrangement
        "carried_advanced_targets": {},    # {target_id: True} — targets using advanced mode
        "carried_primed_targets": {},      # {target_id: True} — processing pack seeded at least once, free
    }


def carried_advanced_for(player_data: Mapping[str, Any], target_id: str) -> bool:
    """Whether a target is in advanced (hand-arranged layout) mode."""
    if not isinstance(player_data, Mapping):
        return False
    advanced = player_data.get("carried_advanced_targets")
    return bool(isinstance(advanced, Mapping) and advanced.get(target_id))


def clamp_carried_view_to_bank(view: Any, bank: Any) -> dict[str, int]:
    """A carried view capped by what the bank actually still holds.

    The view is a *view over the flat store*, never a second store — but the bank
    can shrink underneath it without the view knowing (discarding an item, selling
    it to a shop, eating looted food, a quest consuming it, another skill spending
    the same material). Too many mutation sites to defend individually, so the
    invariant `view <= bank` is enforced wherever the view is read for real effect.
    Without this, a view that outlived its items would grave more than existed and
    mint the difference on reclaim.
    """
    if not isinstance(view, Mapping):
        return {}
    bank = bank if isinstance(bank, Mapping) else {}
    clamped: dict[str, int] = {}
    for item_name, count in view.items():
        if not isinstance(item_name, str):
            continue
        amount = min(_clean_int(count, 0, minimum=0), _clean_int(bank.get(item_name), 0, minimum=0))
        if amount > 0:
            clamped[item_name] = amount
    return clamped


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
    carried = _sanitize_carried_inventory(player_data.get("carried_inventory"))
    # Self-heal on load: a view may have outlived its items (an item discarded,
    # sold, or eaten out of the bank between sessions). Clamp every view so no
    # downstream reader ever sees a pack claiming more than the bank holds.
    bank = player_data.get("inventory")
    if isinstance(bank, Mapping):
        carried = {
            target_id: clamped
            for target_id, view in carried.items()
            if (clamped := clamp_carried_view_to_bank(view, bank))
        }
    player_data["carried_inventory"] = carried

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

    raw_bank_run = player_data.get("skilling_bank_run")
    max_bank_reviews = 100 if isinstance(raw_bank_run, Mapping) and raw_bank_run.get("reviews_total") else SKILLING_BANK_RUN_REVIEWS
    player_data["skilling_bank_run"] = sanitize_bank_run_state(raw_bank_run, max_bank_reviews)
    raw_request = player_data.get("skilling_bank_run_requested")
    player_data["skilling_bank_run_requested"] = (
        raw_request[:120] if isinstance(raw_request, str) else ""
    )
    raw_travel = player_data.get("agility_last_travel")
    player_data["agility_last_travel"] = dict(raw_travel) if isinstance(raw_travel, Mapping) else {}

    raw_overrides = player_data.get("loot_overrides")
    player_data["loot_overrides"] = (
        {
            str(item): value
            for item, value in raw_overrides.items()
            if isinstance(item, str) and value in ("keep", "leave")
        }
        if isinstance(raw_overrides, Mapping)
        else {}
    )

    # Legacy no-op preference: skilling packs are inferred (even-split for
    # processing, action-filled for gathering), not player-picked, so any stray
    # carried_pack_mode from an older save is simply dropped.
    player_data.pop("carried_pack_mode", None)

    player_data["loot_value_threshold"] = _clean_int(
        player_data.get("loot_value_threshold"),
        defaults["loot_value_threshold"],
        minimum=0,
    )

    player_data["carried_layout"] = _sanitize_carried_inventory(player_data.get("carried_layout"))

    raw_advanced = player_data.get("carried_advanced_targets")
    player_data["carried_advanced_targets"] = (
        {str(target_id): True for target_id, value in raw_advanced.items() if isinstance(target_id, str) and value}
        if isinstance(raw_advanced, Mapping)
        else {}
    )

    raw_primed = player_data.get("carried_primed_targets")
    player_data["carried_primed_targets"] = (
        {str(target_id): True for target_id, value in raw_primed.items() if isinstance(target_id, str) and value}
        if isinstance(raw_primed, Mapping)
        else {}
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
