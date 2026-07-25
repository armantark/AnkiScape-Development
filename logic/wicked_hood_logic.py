"""Pure Wicked hood state, daily allowances, and direct operations."""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any

from .inventory_pure import CARRIED_CAPACITY, carried_slots_used
from ..data.item_values import STACKABLE_ITEM_NAMES
from ..data.runecrafting_data import ALTARS_BY_ID, STANDARD_RUNE_TARGETS_BY_ID


WICKED_HOOD_ITEM = "Wicked hood"
WICKED_HOOD_WORLD_DAY_REVIEWS = 240
WICKED_HOOD_OUTFIT_UPGRADES = (
    "Wicked cape",
    "Wicked robe top",
    "Wicked legs",
)
WICKED_HOOD_F2P_ALTARS = frozenset(
    {"air", "mind", "water", "earth", "fire", "body"}
)
WICKED_HOOD_ELEMENTAL_ALTARS = frozenset({"air", "water", "earth", "fire"})


def runecrafting_route_phases_pure(
    reviews_total: int, *, skip_outbound: bool = False
) -> tuple[dict[str, Any], ...]:
    """Partition an existing route cost without changing its baseline total.

    The source-rate model supplies one whole-cycle review count. Until its
    constituent timings are separately sourced, one review represents banking
    and the remaining reviews are split as evenly as possible between the
    return and outbound legs. A hood teleport removes only the latter.
    """
    total = _non_negative_int(reviews_total)
    if total <= 0:
        return ()
    bank_reviews = 1
    travel_reviews = max(0, total - bank_reviews)
    return_reviews = travel_reviews // 2
    outbound_reviews = travel_reviews - return_reviews
    phases = (
        {"id": "return", "label": "Returning to the bank", "reviews": return_reviews},
        {"id": "bank", "label": "Banking and loading essence", "reviews": bank_reviews},
        {"id": "outbound", "label": "Travelling to the altar", "reviews": outbound_reviews},
    )
    return tuple(
        phase
        for phase in phases
        if phase["reviews"] > 0 and not (skip_outbound and phase["id"] == "outbound")
    )


def wicked_hood_skip_active_outbound_pure(
    raw_bank_run: Any,
) -> tuple[dict[str, Any], bool]:
    """Remove the unspent outbound tail from an active altar route."""
    if not isinstance(raw_bank_run, Mapping):
        return {}, False
    remaining = _non_negative_int(raw_bank_run.get("reviews_remaining"))
    total = _non_negative_int(raw_bank_run.get("reviews_total"), remaining)
    raw_phases = raw_bank_run.get("route_phases")
    phases = (
        tuple(dict(phase) for phase in raw_phases if isinstance(phase, Mapping))
        if isinstance(raw_phases, (list, tuple))
        else runecrafting_route_phases_pure(total)
    )
    outbound = sum(
        _non_negative_int(phase.get("reviews"))
        for phase in phases
        if phase.get("id") == "outbound"
    )
    if remaining <= 0 or outbound <= 0:
        return dict(raw_bank_run), False
    reduced_remaining = max(0, remaining - min(remaining, outbound))
    kept_phases = [phase for phase in phases if phase.get("id") != "outbound"]
    if reduced_remaining <= 0:
        return {}, True
    state = dict(raw_bank_run)
    state["reviews_remaining"] = reduced_remaining
    state["reviews_total"] = max(
        reduced_remaining,
        sum(_non_negative_int(phase.get("reviews")) for phase in kept_phases),
    )
    state["route_phases"] = kept_phases
    state["outbound_teleport_used"] = True
    return state, True


def bank_run_phase_label_pure(raw_bank_run: Any) -> str:
    if not isinstance(raw_bank_run, Mapping):
        return "Running to the bank"
    phases = raw_bank_run.get("route_phases")
    if not isinstance(phases, (list, tuple)):
        return str(raw_bank_run.get("route_label", "Running to the bank"))
    remaining = _non_negative_int(raw_bank_run.get("reviews_remaining"))
    cursor = remaining
    for phase in reversed(phases):
        if not isinstance(phase, Mapping):
            continue
        reviews = _non_negative_int(phase.get("reviews"))
        if cursor <= reviews:
            return str(phase.get("label", phase.get("id", "Bank run")))
        cursor -= reviews
    return str(raw_bank_run.get("route_label", "Running to the bank"))


def _non_negative_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return max(0, int(default))


def wicked_hood_review_day_pure(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    answered = (
        _non_negative_int(clock.get("answered_cards"))
        if isinstance(clock, Mapping)
        else 0
    )
    return answered // WICKED_HOOD_WORLD_DAY_REVIEWS


def wicked_hood_caps_pure(state: Mapping[str, Any]) -> dict[str, int]:
    upgrades = {
        str(item)
        for item in state.get("outfit_upgrades", ())
        if isinstance(item, str) and item in WICKED_HOOD_OUTFIT_UPGRADES
    }
    pieces = len(upgrades)
    return {
        "essence": 100 + (25 * pieces),
        "runes": 1 + pieces + int(bool(state.get("elemental_fed"))),
        "teleports": 2 + int(pieces == len(WICKED_HOOD_OUTFIT_UPGRADES)),
    }


def default_wicked_hood_state_pure(review_day: int = 0) -> dict[str, Any]:
    state = {
        "fed_altars": [],
        "omni_fed": False,
        "elemental_fed": False,
        "outfit_upgrades": [],
        "allowance_day": _non_negative_int(review_day),
        "essence_remaining": 100,
        "rune_withdrawals_remaining": 1,
        "teleports_remaining": 2,
        "pending_altar_teleport": "",
    }
    return state


def sanitize_wicked_hood_state_pure(
    raw_state: Any,
    review_day: int = 0,
    *,
    initialize_allowances: bool = False,
) -> dict[str, Any]:
    raw = raw_state if isinstance(raw_state, Mapping) else {}
    raw_fed = raw.get("fed_altars", ())
    if isinstance(raw_fed, str):
        raw_fed = (raw_fed,)
    fed = sorted(
        {
            str(altar)
            for altar in raw_fed
            if isinstance(altar, str) and altar in ALTARS_BY_ID
        }
    ) if isinstance(raw_fed, (list, tuple, set, frozenset)) else []
    raw_upgrades = raw.get("outfit_upgrades", ())
    if isinstance(raw_upgrades, str):
        raw_upgrades = (raw_upgrades,)
    upgrades = [
        item
        for item in WICKED_HOOD_OUTFIT_UPGRADES
        if item in raw_upgrades
    ] if isinstance(raw_upgrades, (list, tuple, set, frozenset)) else []
    day = _non_negative_int(review_day)
    state = {
        "fed_altars": fed,
        "omni_fed": bool(raw.get("omni_fed")),
        "elemental_fed": bool(raw.get("elemental_fed")),
        "outfit_upgrades": upgrades,
        "allowance_day": _non_negative_int(raw.get("allowance_day"), day),
        "essence_remaining": _non_negative_int(raw.get("essence_remaining")),
        "rune_withdrawals_remaining": _non_negative_int(
            raw.get("rune_withdrawals_remaining")
        ),
        "teleports_remaining": _non_negative_int(raw.get("teleports_remaining")),
        "pending_altar_teleport": (
            str(raw.get("pending_altar_teleport", "") or "")
            if str(raw.get("pending_altar_teleport", "") or "") in ALTARS_BY_ID
            else ""
        ),
    }
    caps = wicked_hood_caps_pure(state)
    if initialize_allowances and not {
        "essence_remaining",
        "rune_withdrawals_remaining",
        "teleports_remaining",
    }.issubset(raw):
        state["allowance_day"] = day
        state["essence_remaining"] = caps["essence"]
        state["rune_withdrawals_remaining"] = caps["runes"]
        state["teleports_remaining"] = caps["teleports"]
    else:
        state["essence_remaining"] = min(state["essence_remaining"], caps["essence"])
        state["rune_withdrawals_remaining"] = min(
            state["rune_withdrawals_remaining"], caps["runes"]
        )
        state["teleports_remaining"] = min(
            state["teleports_remaining"], caps["teleports"]
        )
    if state["allowance_day"] != day:
        state["allowance_day"] = day
        state["essence_remaining"] = caps["essence"]
        state["rune_withdrawals_remaining"] = caps["runes"]
        state["teleports_remaining"] = caps["teleports"]
    return state


def ensure_wicked_hood_state_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    # Shallow on purpose: sanitize_ below rebuilds the one key this owns, and a
    # whole-save deep copy here cost 2.07 ms on every review.
    data = dict(player_data)
    day = wicked_hood_review_day_pure(data)
    data["wicked_hood"] = sanitize_wicked_hood_state_pure(
        data.get("wicked_hood"), review_day=day, initialize_allowances=True
    )
    return data


def advance_wicked_hood_review_day_pure(
    player_data: Mapping[str, Any]
) -> dict[str, Any]:
    """Refill fixed allowances at a shared 240-answer day boundary."""
    return ensure_wicked_hood_state_pure(player_data)


def wicked_hood_owned_pure(player_data: Mapping[str, Any]) -> bool:
    inventory = player_data.get("inventory")
    if isinstance(inventory, Mapping) and _non_negative_int(inventory.get(WICKED_HOOD_ITEM)):
        return True
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping) and WICKED_HOOD_ITEM in equipment.values():
        return True
    for key in ("combat_grave", "death_office"):
        state = player_data.get(key)
        if not isinstance(state, Mapping):
            continue
        items = state.get("items", ())
        if isinstance(items, Mapping) and _non_negative_int(items.get(WICKED_HOOD_ITEM)):
            return True
        if isinstance(items, (list, tuple, set)) and WICKED_HOOD_ITEM in items:
            return True
    return False


def wicked_hood_operable_pure(
    player_data: Mapping[str, Any], target_id: str | None = None
) -> bool:
    equipment = player_data.get("equipment")
    if isinstance(equipment, Mapping) and equipment.get("head") == WICKED_HOOD_ITEM:
        return True
    target = str(target_id or player_data.get("current_runecrafting", "") or "")
    carried = player_data.get("carried_inventory")
    view = carried.get(target) if isinstance(carried, Mapping) else None
    inventory = player_data.get("inventory")
    return bool(
        isinstance(view, Mapping)
        and _non_negative_int(view.get(WICKED_HOOD_ITEM))
        and isinstance(inventory, Mapping)
        and _non_negative_int(inventory.get(WICKED_HOOD_ITEM))
    )


def wicked_hood_accessible_altars_pure(
    state: Mapping[str, Any], altar_ids: tuple[str, ...] | list[str]
) -> tuple[str, ...]:
    available = {str(altar) for altar in state.get("fed_altars", ()) if isinstance(altar, str)}
    if state.get("omni_fed"):
        available.update(str(altar) for altar in altar_ids)
    if state.get("elemental_fed"):
        available.update(WICKED_HOOD_ELEMENTAL_ALTARS)
    return tuple(altar for altar in altar_ids if altar in available)


def wicked_hood_fed_altars_pure(player_data: Mapping[str, Any]) -> tuple[str, ...]:
    data = ensure_wicked_hood_state_pure(player_data)
    return wicked_hood_accessible_altars_pure(
        data["wicked_hood"], list(ALTARS_BY_ID)
    )


def wicked_hood_projection_pure(
    player_data: Mapping[str, Any],
    altars: Mapping[str, Mapping[str, Any]],
    standard_targets: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    data = ensure_wicked_hood_state_pure(player_data)
    state = data["wicked_hood"]
    caps = wicked_hood_caps_pure(state)
    target_id = str(data.get("current_runecrafting", "") or "")
    accessible = wicked_hood_accessible_altars_pure(
        state, list(altars)
    )
    rows = []
    level = _non_negative_int(data.get("runecrafting_level"), 1)
    targets_by_altar = {
        str(spec.get("altar_id")): (target, spec)
        for target, spec in standard_targets.items()
        if isinstance(spec, Mapping)
    }
    for altar_id in accessible:
        altar = altars.get(altar_id, {})
        target, spec = targets_by_altar.get(altar_id, ("", {}))
        rows.append(
            {
                "altar_id": altar_id,
                "display_name": str(altar.get("display_name", altar_id.title())),
                "rune_item": str(altar.get("rune_item", "")),
                "rune_quantity": 100 if altar_id in WICKED_HOOD_F2P_ALTARS else 5,
                "target_id": target,
                "level": _non_negative_int(spec.get("level"), 1),
                "level_met": level >= _non_negative_int(spec.get("level"), 1),
            }
        )
    claims = data.get("claims")
    claimed = bool(
        isinstance(claims, Mapping)
        and isinstance(claims.get("wicked_hood"), Mapping)
        and claims["wicked_hood"].get("claimed")
    )
    return {
        "claimed": claimed,
        "owned": wicked_hood_owned_pure(data),
        "operable": wicked_hood_operable_pure(data, target_id),
        "essence_item": "Pure essence" if state.get("omni_fed") else "Rune essence",
        "essence_remaining": state["essence_remaining"],
        "essence_cap": caps["essence"],
        "rune_withdrawals_remaining": state["rune_withdrawals_remaining"],
        "rune_withdrawals_cap": caps["runes"],
        "teleports_remaining": state["teleports_remaining"],
        "teleports_cap": caps["teleports"],
        "altars": tuple(rows),
        "pending_altar_teleport": state["pending_altar_teleport"],
    }


def wicked_hood_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    projection = wicked_hood_projection_pure(
        player_data,
        {
            altar_id: dict(altar.__dict__)
            for altar_id, altar in ALTARS_BY_ID.items()
        },
        {
            target_id: dict(target.__dict__)
            for target_id, target in STANDARD_RUNE_TARGETS_BY_ID.items()
        },
    )
    return {
        **projection,
        "caps": {
            "essence": projection["essence_cap"],
            "runes": projection["rune_withdrawals_cap"],
            "teleports": projection["teleports_cap"],
        },
        "altar_options": projection["altars"],
    }


def apply_wicked_hood_upgrade_pure(
    player_data: Mapping[str, Any],
    *,
    fed_altars: tuple[str, ...] = (),
    omni_fed: bool = False,
    elemental_fed: bool = False,
    outfit_upgrade: str = "",
) -> dict[str, Any]:
    data = ensure_wicked_hood_state_pure(player_data)
    state = data["wicked_hood"]
    before = wicked_hood_caps_pure(state)
    state["fed_altars"] = sorted(set(state["fed_altars"]) | set(fed_altars))
    state["omni_fed"] = bool(state["omni_fed"] or omni_fed)
    state["elemental_fed"] = bool(state["elemental_fed"] or elemental_fed)
    if outfit_upgrade in WICKED_HOOD_OUTFIT_UPGRADES:
        state["outfit_upgrades"] = [
            item
            for item in WICKED_HOOD_OUTFIT_UPGRADES
            if item in set(state["outfit_upgrades"]) | {outfit_upgrade}
        ]
    after = wicked_hood_caps_pure(state)
    state["essence_remaining"] += after["essence"] - before["essence"]
    state["rune_withdrawals_remaining"] += after["runes"] - before["runes"]
    state["teleports_remaining"] += after["teleports"] - before["teleports"]
    return data


def apply_wicked_hood_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
    altars: Mapping[str, Mapping[str, Any]] | None = None,
    standard_targets: Mapping[str, Mapping[str, Any]] | None = None,
    stackable_items: set[str] | frozenset[str] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    altars = altars or {
        altar_id: dict(altar.__dict__)
        for altar_id, altar in ALTARS_BY_ID.items()
    }
    standard_targets = standard_targets or {
        target_id: dict(target.__dict__)
        for target_id, target in STANDARD_RUNE_TARGETS_BY_ID.items()
    }
    stackable_items = stackable_items or STACKABLE_ITEM_NAMES
    payload = payload if isinstance(payload, Mapping) else {}
    data = ensure_wicked_hood_state_pure(player_data)
    state = data["wicked_hood"]
    target_id = str(data.get("current_runecrafting", "") or "")

    if action_id == "reclaim":
        projection = wicked_hood_projection_pure(data, altars, standard_targets)
        if not projection["claimed"]:
            return data, False, {"reason": "Claim the Wicked hood first."}
        if wicked_hood_owned_pure(data):
            return data, False, {"reason": "You already own a Wicked hood."}
        inventory = data.setdefault("inventory", {})
        inventory[WICKED_HOOD_ITEM] = 1
        return data, True, {"message": "Wicked hood reclaimed; its progress was preserved."}

    if not wicked_hood_operable_pure(data, target_id):
        return data, False, {
            "reason": "Equip the Wicked hood or carry it in this Runecrafting pack."
        }

    carried_root = dict(data.get("carried_inventory", {}) or {})
    view = dict(carried_root.get(target_id, {}) or {})
    inventory = data.setdefault("inventory", {})

    if action_id == "essence":
        remaining = state["essence_remaining"]
        free_slots = max(0, CARRIED_CAPACITY - carried_slots_used(view, stackable_items))
        quantity = min(remaining, free_slots)
        if quantity <= 0:
            return data, False, {"reason": "No carried-pack space or essence allowance remains."}
        item = "Pure essence" if state.get("omni_fed") else "Rune essence"
        inventory[item] = _non_negative_int(inventory.get(item)) + quantity
        view[item] = _non_negative_int(view.get(item)) + quantity
        carried_root[target_id] = view
        data["carried_inventory"] = carried_root
        state["essence_remaining"] -= quantity
        return data, True, {"message": f"Withdrew {quantity} {item}.", "quantity": quantity, "item": item}

    altar_id = str(payload.get("altar_id", "") or "")
    accessible = wicked_hood_accessible_altars_pure(state, list(altars))
    if altar_id not in accessible:
        return data, False, {"reason": "That altar has not been unlocked in the hood."}

    altar = altars.get(altar_id, {})
    if action_id == "runes":
        if state["rune_withdrawals_remaining"] <= 0:
            return data, False, {"reason": "No rune withdrawals remain this review day."}
        rune_item = str(altar.get("rune_item", "") or "")
        if not rune_item:
            return data, False, {"reason": "That altar has no withdrawable rune."}
        if rune_item not in view and carried_slots_used(view, stackable_items) >= CARRIED_CAPACITY:
            return data, False, {"reason": "The carried pack has no room for that rune stack."}
        quantity = 100 if altar_id in WICKED_HOOD_F2P_ALTARS else 5
        inventory[rune_item] = _non_negative_int(inventory.get(rune_item)) + quantity
        view[rune_item] = _non_negative_int(view.get(rune_item)) + quantity
        carried_root[target_id] = view
        data["carried_inventory"] = carried_root
        state["rune_withdrawals_remaining"] -= 1
        return data, True, {"message": f"Withdrew {quantity} {rune_item}.", "quantity": quantity, "item": rune_item}

    if action_id == "teleport":
        if state["teleports_remaining"] <= 0:
            return data, False, {"reason": "No altar teleports remain this review day."}
        pending_altar = str(state.get("pending_altar_teleport", "") or "")
        if pending_altar:
            pending_name = str(
                altars.get(pending_altar, {}).get("display_name", pending_altar.title())
            )
            return data, False, {
                "reason": f"A teleport to {pending_name} is already queued."
            }
        active_run = data.get("skilling_bank_run")
        if (
            isinstance(active_run, Mapping)
            and active_run.get("target_id") in (None, target_id)
            and _non_negative_int(active_run.get("reviews_remaining")) > 0
            and active_run.get("outbound_teleport_used") is True
        ):
            return data, False, {
                "reason": "This route's outbound leg has already been teleported."
            }
        locked_reason = str(payload.get("locked_reason", "") or "")
        if locked_reason:
            return data, False, {"reason": locked_reason}
        target, spec = next(
            (
                (candidate, row)
                for candidate, row in standard_targets.items()
                if str(row.get("altar_id")) == altar_id
            ),
            ("", {}),
        )
        required_level = _non_negative_int(spec.get("level"), 1)
        if not target or _non_negative_int(data.get("runecrafting_level"), 1) < required_level:
            return data, False, {"reason": f"Requires level {required_level} Runecrafting."}
        state["teleports_remaining"] -= 1
        state["pending_altar_teleport"] = altar_id
        data["current_runecrafting"] = target
        return data, True, {
            "message": f"Teleported to {altar.get('display_name', altar_id.title())}; the next outbound route is skipped.",
            "target_id": target,
            "altar_id": altar_id,
        }

    return data, False, {"reason": "Unknown Wicked hood action."}


def consume_wicked_hood_route_teleport_pure(
    player_data: Mapping[str, Any], altar_id: str
) -> tuple[dict[str, Any], bool]:
    data = ensure_wicked_hood_state_pure(player_data)
    state = data["wicked_hood"]
    if state.get("pending_altar_teleport") != str(altar_id):
        return data, False
    state["pending_altar_teleport"] = ""
    return data, True
