"""Pure Livid Farm cadence, cycle, and progression helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

try:
    from .livid_farm_data import (
        LIVID_FARM_BORROWED_POWER_COST,
        LIVID_FARM_DISTRACTION_INTERVAL,
        LIVID_FARM_DISTRACTIONS,
        LIVID_FARM_DUTIES,
        LIVID_FARM_ENTRY_LEVELS,
        LIVID_FARM_MORE_PLANKS_REVIEWS,
        LIVID_FARM_UNLOCKS,
        LIVID_FARM_WALLET_CAP,
        LIVID_FARM_WISHES,
    )
except ImportError:  # pragma: no cover - flat imports used by tests
    from livid_farm_data import (  # type: ignore
        LIVID_FARM_BORROWED_POWER_COST,
        LIVID_FARM_DISTRACTION_INTERVAL,
        LIVID_FARM_DISTRACTIONS,
        LIVID_FARM_DUTIES,
        LIVID_FARM_ENTRY_LEVELS,
        LIVID_FARM_MORE_PLANKS_REVIEWS,
        LIVID_FARM_UNLOCKS,
        LIVID_FARM_WALLET_CAP,
        LIVID_FARM_WISHES,
    )


def _non_negative_int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _finite_non_negative_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0
    if number < 0.0 or number != number or number == float("inf"):
        return 0.0
    return number


def default_livid_farm_state_pure() -> dict[str, Any]:
    return {
        "farm_routine": "complete",
        "cadence_credit": 0,
        "distraction_credit": 0,
        "cycles_completed": 0,
        "produce_points": 0,
        "lifetime_produce_points": 0,
        "unlocked_spells": [],
        "borrowed_power_claimed": False,
        "lunar_lumber_residual": 0,
        "more_planks_reviews_remaining": 0,
        "more_planks_active_this_review": False,
    }


def sanitize_livid_farm_state_pure(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    state = default_livid_farm_state_pure()
    routine = str(source.get("farm_routine", "complete"))
    state["farm_routine"] = routine if routine in {"complete", "conserve"} else "complete"
    state["cadence_credit"] = _non_negative_int(source.get("cadence_credit", 0)) % 5
    state["distraction_credit"] = (
        _non_negative_int(source.get("distraction_credit", 0))
        % LIVID_FARM_DISTRACTION_INTERVAL
    )
    state["cycles_completed"] = _non_negative_int(source.get("cycles_completed", 0))
    state["lifetime_produce_points"] = _non_negative_int(
        source.get("lifetime_produce_points", 0)
    )
    source_unlocks = source.get("unlocked_spells", ())
    if not isinstance(source_unlocks, (list, tuple, set, frozenset)):
        source_unlocks = ()
    claimed = bool(
        source.get("borrowed_power_claimed", False)
        or "borrowed_power" in set(map(str, source_unlocks))
    )
    wallet = _non_negative_int(source.get("produce_points", 0))
    state["produce_points"] = min(wallet, LIVID_FARM_WALLET_CAP) if claimed else wallet
    valid_unlocks = {row[0] for row in LIVID_FARM_UNLOCKS}
    unlocked = source_unlocks
    state["unlocked_spells"] = [
        unlock_id
        for unlock_id, _name, _threshold in LIVID_FARM_UNLOCKS
        if unlock_id in valid_unlocks and unlock_id in set(map(str, unlocked))
    ]
    state["borrowed_power_claimed"] = claimed
    state["lunar_lumber_residual"] = (
        _non_negative_int(source.get("lunar_lumber_residual", 0)) % 28
    )
    state["more_planks_reviews_remaining"] = min(
        LIVID_FARM_MORE_PLANKS_REVIEWS,
        _non_negative_int(source.get("more_planks_reviews_remaining", 0)),
    )
    state["more_planks_active_this_review"] = bool(
        source.get("more_planks_active_this_review", False)
    )
    if claimed:
        state["unlocked_spells"] = [
            unlock_id for unlock_id, _name, _threshold in LIVID_FARM_UNLOCKS
        ]
    return state


def _quest_completed(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quest_state = (player_data.get("quests", {}) or {}).get(quest_id, {})
    return bool(isinstance(quest_state, Mapping) and quest_state.get("completed"))


def livid_farm_locked_reasons_pure(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not _quest_completed(player_data, "lunar_diplomacy"):
        reasons.append("Lunar Diplomacy")
    for skill_id, required in LIVID_FARM_ENTRY_LEVELS.items():
        level = _non_negative_int(player_data.get(f"{skill_id}_level", 1), 1)
        if level < required:
            reasons.append(f"{skill_id.title()} {required}")
    return tuple(reasons)


def livid_farm_effective_magic_level_pure(
    player_data: Mapping[str, Any],
) -> int:
    base = _non_negative_int(player_data.get("magic_level", 1), 1)
    current_levels = player_data.get("combat_current_levels", {}) or {}
    if not isinstance(current_levels, Mapping):
        return base
    return _non_negative_int(current_levels.get("magic", base), base)


def livid_farm_cycles_for_steps_pure(
    cadence_credit: Any,
    successful_steps: Any,
) -> tuple[int, int]:
    credit = _non_negative_int(cadence_credit) % 5
    steps = _non_negative_int(successful_steps)
    total_credit = credit + (6 * steps)
    return total_credit // 5, total_credit % 5


def _effective_rune_cost(
    player_data: Mapping[str, Any],
    rune_cost: Mapping[str, int],
) -> dict[str, int]:
    try:
        from .logic_pure import effective_magic_rune_cost_pure
    except ImportError:  # pragma: no cover - flat imports used by tests
        from logic_pure import effective_magic_rune_cost_pure  # type: ignore
    return effective_magic_rune_cost_pure(player_data, rune_cost)


def livid_farm_cycle_projection_pure(
    player_data: Mapping[str, Any],
    routine: str | None = None,
) -> dict[str, Any]:
    state = sanitize_livid_farm_state_pure(player_data.get("livid_farm"))
    selected_routine = routine or state["farm_routine"]
    if selected_routine not in {"complete", "conserve"}:
        selected_routine = "complete"
    magic_level = livid_farm_effective_magic_level_pure(player_data)
    rune_cost: dict[str, int] = {}
    xp_rewards: dict[str, float] = {}
    points = 0
    duty_rows: list[dict[str, Any]] = []
    for duty in LIVID_FARM_DUTIES:
        eligible = magic_level >= int(duty["magic_level"])
        included = eligible or selected_routine == "complete"
        if not included:
            duty_rows.append(
                {
                    "id": duty["id"],
                    "display_name": duty["display_name"],
                    "included": False,
                    "eligible": False,
                }
            )
            continue
        count = int(duty["count"])
        duty_points = count * int(duty["points_each"])
        if not eligible:
            duty_points //= 2
        points += duty_points
        for rune_name, amount in duty["rune_cost"].items():
            rune_cost[rune_name] = rune_cost.get(rune_name, 0) + count * int(amount)
        if eligible:
            xp_rewards["magic"] = xp_rewards.get("magic", 0.0) + (
                count * float(duty["magic_xp_each"])
            )
        secondary = str(duty["secondary_skill"])
        xp_rewards[secondary] = xp_rewards.get(secondary, 0.0) + (
            count * float(duty["secondary_xp_each"])
        )
        duty_rows.append(
            {
                "id": duty["id"],
                "display_name": duty["display_name"],
                "included": True,
                "eligible": eligible,
                "points": duty_points,
            }
        )
    effective_cost = _effective_rune_cost(player_data, rune_cost)
    return {
        "routine": selected_routine,
        "magic_level": magic_level,
        "points": points,
        "xp_rewards": xp_rewards,
        "rune_cost": effective_cost,
        "duties": tuple(duty_rows),
    }


def livid_farm_missing_runes_pure(
    player_data: Mapping[str, Any],
    rune_cost: Mapping[str, int],
) -> dict[str, int]:
    inventory = player_data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        inventory = {}
    return {
        rune_name: amount - _non_negative_int(inventory.get(rune_name, 0))
        for rune_name, amount in rune_cost.items()
        if _non_negative_int(inventory.get(rune_name, 0)) < int(amount)
    }


def _consume_runes(
    inventory: dict[str, Any],
    rune_cost: Mapping[str, int],
) -> None:
    for rune_name, amount in rune_cost.items():
        inventory[rune_name] = _non_negative_int(inventory.get(rune_name, 0)) - int(amount)


def _add_runes(
    inventory: dict[str, Any],
    runes: Mapping[str, int],
) -> None:
    for rune_name, amount in runes.items():
        inventory[rune_name] = _non_negative_int(inventory.get(rune_name, 0)) + int(amount)


def _claim_crossed_unlocks(state: dict[str, Any]) -> list[dict[str, Any]]:
    unlocked = set(map(str, state["unlocked_spells"]))
    claimed: list[dict[str, Any]] = []
    lifetime = _non_negative_int(state["lifetime_produce_points"])
    for unlock_id, display_name, threshold in LIVID_FARM_UNLOCKS:
        if unlock_id in unlocked or lifetime < threshold:
            continue
        if unlock_id == "borrowed_power":
            if _non_negative_int(state["produce_points"]) < LIVID_FARM_BORROWED_POWER_COST:
                continue
            state["produce_points"] -= LIVID_FARM_BORROWED_POWER_COST
            state["borrowed_power_claimed"] = True
        state["unlocked_spells"].append(unlock_id)
        unlocked.add(unlock_id)
        claimed.append(
            {
                "id": unlock_id,
                "display_name": display_name,
                "threshold": threshold,
            }
        )
    return claimed


def _apply_distraction(
    player_data: Mapping[str, Any],
    inventory: dict[str, Any],
    magic_level: int,
    roll: float,
) -> dict[str, Any]:
    safe_roll = max(0.0, min(_finite_non_negative_float(roll), 1.0))
    index = min(int(safe_roll * len(LIVID_FARM_DISTRACTIONS)), len(LIVID_FARM_DISTRACTIONS) - 1)
    spec = LIVID_FARM_DISTRACTIONS[index]
    rune_cost = _effective_rune_cost(player_data, spec["rune_cost"])
    missing = {
        rune_name: amount - _non_negative_int(inventory.get(rune_name, 0))
        for rune_name, amount in rune_cost.items()
        if _non_negative_int(inventory.get(rune_name, 0)) < int(amount)
    }
    if missing:
        return {
            "id": spec["id"],
            "display_name": spec["display_name"],
            "completed": False,
            "missing_runes": missing,
            "magic_xp": 0.0,
            "rune_delta": {},
        }
    _consume_runes(inventory, rune_cost)
    _add_runes(inventory, spec["rune_reward"])
    rune_delta = dict(spec["rune_reward"])
    for rune_name, amount in rune_cost.items():
        rune_delta[rune_name] = rune_delta.get(rune_name, 0) - int(amount)
    return {
        "id": spec["id"],
        "display_name": spec["display_name"],
        "completed": True,
        "missing_runes": {},
        "magic_xp": (
            float(spec["magic_xp"])
            if magic_level >= int(spec["magic_level"])
            else 0.0
        ),
        "rune_delta": {name: amount for name, amount in rune_delta.items() if amount},
    }


def apply_livid_farm_reviews_pure(
    player_data: Mapping[str, Any],
    successful_steps: Any = 1,
    *,
    rng: Callable[[], float] = lambda: 0.0,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    """Apply exact review cadence and as many complete source cycles as funded."""
    data = dict(player_data)
    locked_reasons = livid_farm_locked_reasons_pure(data)
    if locked_reasons:
        return data, False, {
            "reason": "locked",
            "locked_reasons": locked_reasons,
            "cycles": 0,
        }
    state = sanitize_livid_farm_state_pure(data.get("livid_farm"))
    requested_cycles, next_credit = livid_farm_cycles_for_steps_pure(
        state["cadence_credit"],
        successful_steps,
    )
    if requested_cycles <= 0:
        state["cadence_credit"] = next_credit
        data["livid_farm"] = state
        return data, True, {
            "reason": "cadence_wait",
            "cycles": 0,
            "cadence_credit": next_credit,
            "xp_rewards": {},
            "points": 0,
            "new_unlocks": (),
            "distractions": (),
        }

    inventory = dict(data.get("inventory", {}) or {})
    projection = livid_farm_cycle_projection_pure(data, state["farm_routine"])
    review_rune_cost = {
        rune_name: int(amount) * requested_cycles
        for rune_name, amount in projection["rune_cost"].items()
    }
    blocked_missing = livid_farm_missing_runes_pure(
        {"inventory": inventory},
        review_rune_cost,
    )
    if blocked_missing:
        data["livid_farm"] = state
        return data, False, {
            "reason": "missing_runes",
            "cycles": 0,
            "requested_cycles": requested_cycles,
            "cadence_credit": state["cadence_credit"],
            "xp_rewards": {},
            "points": 0,
            "rune_cost_per_cycle": dict(projection["rune_cost"]),
            "missing_runes": blocked_missing,
            "new_unlocks": (),
            "distractions": (),
            "routine": state["farm_routine"],
        }
    xp_rewards: dict[str, float] = {}
    points = 0
    completed_cycles = 0
    distractions: list[dict[str, Any]] = []
    new_unlocks: list[dict[str, Any]] = []
    magic_level = int(projection["magic_level"])

    for _cycle in range(requested_cycles):
        _consume_runes(inventory, projection["rune_cost"])
        completed_cycles += 1
        cycle_points = int(projection["points"])
        points += cycle_points
        for skill_id, amount in projection["xp_rewards"].items():
            xp_rewards[skill_id] = xp_rewards.get(skill_id, 0.0) + float(amount)
        state["cycles_completed"] += 1
        state["lifetime_produce_points"] += cycle_points
        state["produce_points"] += cycle_points
        if state["borrowed_power_claimed"]:
            state["produce_points"] = min(
                state["produce_points"],
                LIVID_FARM_WALLET_CAP,
            )
        new_unlocks.extend(_claim_crossed_unlocks(state))
        state["distraction_credit"] += 1
        if state["distraction_credit"] >= LIVID_FARM_DISTRACTION_INTERVAL:
            state["distraction_credit"] -= LIVID_FARM_DISTRACTION_INTERVAL
            distraction = _apply_distraction(
                data,
                inventory,
                magic_level,
                rng(),
            )
            distractions.append(distraction)
            if distraction["completed"] and distraction["magic_xp"] > 0:
                xp_rewards["magic"] = xp_rewards.get("magic", 0.0) + float(
                    distraction["magic_xp"]
                )

    state["cadence_credit"] = next_credit
    data["inventory"] = inventory
    data["livid_farm"] = state
    ok = completed_cycles > 0
    return data, ok, {
        "reason": "cycles" if ok else "missing_runes",
        "cycles": completed_cycles,
        "requested_cycles": requested_cycles,
        "cadence_credit": state["cadence_credit"],
        "points": points,
        "xp_rewards": xp_rewards,
        "rune_cost_per_cycle": dict(projection["rune_cost"]),
        "missing_runes": {},
        "new_unlocks": tuple(new_unlocks),
        "distractions": tuple(distractions),
        "routine": state["farm_routine"],
    }


def set_livid_farm_routine_pure(
    player_data: Mapping[str, Any],
    routine: Any,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    selected = str(routine)
    if selected not in {"complete", "conserve"}:
        return dict(player_data), False, {"reason": "invalid_routine"}
    data = dict(player_data)
    state = sanitize_livid_farm_state_pure(data.get("livid_farm"))
    state["farm_routine"] = selected
    data["livid_farm"] = state
    return data, True, {"routine": selected}


def _livid_carried_inventory(
    player_data: Mapping[str, Any],
) -> dict[str, int]:
    carried_root = player_data.get("carried_inventory", {}) or {}
    raw = (
        carried_root.get("livid_farm", {})
        if isinstance(carried_root, Mapping)
        else {}
    )
    inventory = player_data.get("inventory", {}) or {}
    if not isinstance(raw, Mapping) or not isinstance(inventory, Mapping):
        return {}
    return {
        str(item_name): min(
            _non_negative_int(amount),
            _non_negative_int(inventory.get(item_name, 0)),
        )
        for item_name, amount in raw.items()
        if isinstance(item_name, str)
        and _non_negative_int(amount) > 0
        and _non_negative_int(inventory.get(item_name, 0)) > 0
    }


def _unfinished_herb_outputs() -> dict[str, str]:
    try:
        from .herblore_data import HERBLORE_TARGETS
    except ImportError:  # pragma: no cover - flat imports used by tests
        from herblore_data import HERBLORE_TARGETS  # type: ignore
    outputs: dict[str, str] = {}
    for target in HERBLORE_TARGETS:
        if target.group != "unf" or target.subgroup == "dungeoneering":
            continue
        requirements = dict(target.requirements)
        clean_herbs = [
            item_name
            for item_name in requirements
            if item_name.startswith("Clean ") and item_name != "Cave nightshade"
        ]
        if len(clean_herbs) == 1:
            outputs[clean_herbs[0]] = target.output_item
    return outputs


def _wish_material_reason(
    player_data: Mapping[str, Any],
    wish_id: str,
) -> str:
    carried = _livid_carried_inventory(player_data)
    if wish_id == "vial_my_herbs":
        if not any(
            _non_negative_int(carried.get(herb, 0)) > 0
            for herb in _unfinished_herb_outputs()
        ):
            return "Carry a clean herb in the Livid Farm pack"
    elif wish_id == "lunar_lumber":
        if _non_negative_int(carried.get("Lunar lumber", 0)) <= 0:
            return "Carry Lunar lumber in the Livid Farm pack"
    return ""


def livid_farm_wish_rows_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    state = sanitize_livid_farm_state_pure(player_data.get("livid_farm"))
    rows = []
    for wish in LIVID_FARM_WISHES:
        status = str(wish["status"])
        reason = ""
        if not state["borrowed_power_claimed"]:
            reason = "Unlock Borrowed Power first"
        elif status == "source_blocked":
            reason = str(wish["summary"])
        elif status == "dependency_blocked":
            reason = str(wish["summary"])
        elif state["produce_points"] < int(wish["cost"]):
            reason = f"Need {int(wish['cost']):,} Produce"
        else:
            reason = _wish_material_reason(player_data, str(wish["id"]))
        rows.append(
            {
                **wish,
                "enabled": not reason,
                "locked_reason": reason,
            }
        )
    return tuple(rows)


def _replace_livid_carried(
    data: dict[str, Any],
    carried: Mapping[str, int],
) -> None:
    carried_root = dict(data.get("carried_inventory", {}) or {})
    clean = {
        item_name: _non_negative_int(amount)
        for item_name, amount in carried.items()
        if _non_negative_int(amount) > 0
    }
    if clean:
        carried_root["livid_farm"] = clean
    else:
        carried_root.pop("livid_farm", None)
    data["carried_inventory"] = carried_root


def _add_inventory_items(
    inventory: dict[str, Any],
    outputs: Mapping[str, int],
) -> None:
    for item_name, amount in outputs.items():
        quantity = _non_negative_int(amount)
        if quantity <= 0:
            continue
        inventory[item_name] = (
            _non_negative_int(inventory.get(item_name, 0)) + quantity
        )


def apply_livid_farm_wish_pure(
    player_data: Mapping[str, Any],
    wish_id: Any,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    selected = str(wish_id)
    row = next(
        (
            wish
            for wish in livid_farm_wish_rows_pure(player_data)
            if wish["id"] == selected
        ),
        None,
    )
    if row is None:
        return dict(player_data), False, {"reason": "unknown_wish"}
    if not row["enabled"]:
        return dict(player_data), False, {
            "reason": "locked",
            "message": row["locked_reason"],
        }

    data = dict(player_data)
    inventory = dict(data.get("inventory", {}) or {})
    carried = _livid_carried_inventory(data)
    state = sanitize_livid_farm_state_pure(data.get("livid_farm"))
    outputs: dict[str, int] = {}

    if selected == "vial_my_herbs":
        for herb, unfinished in _unfinished_herb_outputs().items():
            amount = min(50, _non_negative_int(carried.get(herb, 0)))
            if amount <= 0:
                continue
            herb_remaining = (
                _non_negative_int(inventory.get(herb, 0)) - amount
            )
            if herb_remaining > 0:
                inventory[herb] = herb_remaining
            else:
                inventory.pop(herb, None)
            carried[herb] = _non_negative_int(carried.get(herb, 0)) - amount
            inventory[unfinished] = (
                _non_negative_int(inventory.get(unfinished, 0)) + amount
            )
            carried[unfinished] = (
                _non_negative_int(carried.get(unfinished, 0)) + amount
            )
            outputs[unfinished] = amount
    elif selected == "lunar_lumber":
        amount = _non_negative_int(carried.get("Lunar lumber", 0))
        prior = state["lunar_lumber_residual"]
        total = prior + amount
        outputs["Astral rune"] = (total * 25 // 28) - (prior * 25 // 28)
        for rune_name in (
            "Nature rune",
            "Death rune",
            "Earth rune",
            "Cosmic rune",
            "Water rune",
        ):
            outputs[rune_name] = (total * 10 // 28) - (prior * 10 // 28)
        outputs = {
            item_name: quantity
            for item_name, quantity in outputs.items()
            if quantity > 0
        }
        state["lunar_lumber_residual"] = total % 28
        lumber_remaining = (
            _non_negative_int(inventory.get("Lunar lumber", 0)) - amount
        )
        if lumber_remaining > 0:
            inventory["Lunar lumber"] = lumber_remaining
        else:
            inventory.pop("Lunar lumber", None)
        carried.pop("Lunar lumber", None)
        _add_inventory_items(inventory, outputs)
        _add_inventory_items(carried, outputs)
    elif selected == "more_planks":
        state["more_planks_reviews_remaining"] = (
            LIVID_FARM_MORE_PLANKS_REVIEWS
        )
        state["more_planks_active_this_review"] = False
    elif selected == "gimme_herbs":
        outputs = {
            "Grimy kwuarm": 3,
            "Grimy irit": 3,
            "Grimy cadantine": 2,
            "Grimy avantoe": 2,
            "Grimy lantadyme": 1,
        }
        _add_inventory_items(inventory, outputs)
    elif selected == "awesome_seeds":
        outputs = {
            "Ranarr seed": 4,
            "Watermelon seed": 4,
            "Curry tree seed": 6,
            "Pineapple seed": 2,
            "Papaya tree seed": 2,
            "Willow seed": 4,
        }
        _add_inventory_items(inventory, outputs)
    else:  # The projection must keep incomplete rows disabled.
        return dict(player_data), False, {"reason": "unavailable_wish"}

    state["produce_points"] -= int(row["cost"])
    data["inventory"] = inventory
    data["livid_farm"] = state
    _replace_livid_carried(data, carried)
    return data, True, {
        "reason": "wish_applied",
        "wish_id": selected,
        "display_name": row["display_name"],
        "cost": int(row["cost"]),
        "outputs": outputs,
    }


def advance_livid_farm_wish_effects_pure(
    player_data: Mapping[str, Any],
    answered_cards: Any = 1,
) -> dict[str, Any]:
    data = dict(player_data)
    state = sanitize_livid_farm_state_pure(data.get("livid_farm"))
    cards = _non_negative_int(answered_cards)
    remaining = state["more_planks_reviews_remaining"]
    state["more_planks_active_this_review"] = cards > 0 and remaining > 0
    state["more_planks_reviews_remaining"] = max(0, remaining - cards)
    data["livid_farm"] = state
    return data
