"""Pure review-clock kingdom management and collection mechanics."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

try:
    from .managing_miscellania_data import (
        MANAGING_MISCELLANIA_ACTIVITY_ID,
        MANAGING_MISCELLANIA_QUEST_ID,
        MISCELLANIA_APPROVAL_CHORES,
        MISCELLANIA_CREDIT_SCALE,
        MISCELLANIA_RESOURCE_BY_ID,
        MISCELLANIA_RESOURCE_FAMILIES,
        MISCELLANIA_REVIEWS_PER_DAY,
        ROYAL_TROUBLE_QUEST_ID,
    )
except ImportError:  # pragma: no cover - flat test imports
    from managing_miscellania_data import (  # type: ignore
        MANAGING_MISCELLANIA_ACTIVITY_ID,
        MANAGING_MISCELLANIA_QUEST_ID,
        MISCELLANIA_APPROVAL_CHORES,
        MISCELLANIA_CREDIT_SCALE,
        MISCELLANIA_RESOURCE_BY_ID,
        MISCELLANIA_RESOURCE_FAMILIES,
        MISCELLANIA_REVIEWS_PER_DAY,
        ROYAL_TROUBLE_QUEST_ID,
    )


MISCELLANIA_STATE_VERSION = 1


def _int(value: Any, default: int = 0, *, maximum: int = 2_147_483_647) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        parsed = default
    return max(0, min(parsed, maximum))


def _quest_completed(player_data: Mapping[str, Any], quest_id: str) -> bool:
    quests = player_data.get("quests")
    quest = quests.get(quest_id) if isinstance(quests, Mapping) else None
    return isinstance(quest, Mapping) and bool(quest.get("completed"))


def _answered_cards(player_data: Mapping[str, Any]) -> int:
    clock = player_data.get("shop_market_clock")
    return _int(clock.get("answered_cards")) if isinstance(clock, Mapping) else 0


def miscellania_limits_pure(player_data: Mapping[str, Any]) -> dict[str, int]:
    royal = _quest_completed(player_data, ROYAL_TROUBLE_QUEST_ID)
    return {
        "subjects": 15 if royal else 10,
        "coffer_cap": 7_500_000 if royal else 5_000_000,
        "salary_cap": 75_000 if royal else 50_000,
        "approval_decay_bp": 100 if royal else 250,
    }


def default_managing_miscellania_state_pure(
    answered_cards: int = 0,
) -> dict[str, Any]:
    return {
        "managing_miscellania": {
            "version": MISCELLANIA_STATE_VERSION,
            "approval_basis_points": 10000,
            "coffer": 0,
            "production_credit": 0,
            "last_world_day": _int(answered_cards) // MISCELLANIA_REVIEWS_PER_DAY,
            "allocations": {family.id: 0 for family in MISCELLANIA_RESOURCE_FAMILIES},
            "variants": {
                family.id: family.variants[0].id
                for family in MISCELLANIA_RESOURCE_FAMILIES
            },
            "approval_chore": str(MISCELLANIA_APPROVAL_CHORES[0]["id"]),
            "collections": 0,
            "days_funded": 0,
        },
        "managing_miscellania_last_result": "",
    }


def sanitize_managing_miscellania_state_pure(
    raw: Any,
    *,
    answered_cards: int = 0,
) -> dict[str, Any]:
    source = raw if isinstance(raw, Mapping) else {}
    allocations_raw = source.get("allocations")
    allocations_source = allocations_raw if isinstance(allocations_raw, Mapping) else {}
    variants_raw = source.get("variants")
    variants_source = variants_raw if isinstance(variants_raw, Mapping) else {}
    allocations = {
        family.id: min(10, _int(allocations_source.get(family.id)))
        for family in MISCELLANIA_RESOURCE_FAMILIES
    }
    variants: dict[str, str] = {}
    for family in MISCELLANIA_RESOURCE_FAMILIES:
        valid = {variant.id for variant in family.variants}
        selected = str(variants_source.get(family.id, family.variants[0].id))
        variants[family.id] = selected if selected in valid else family.variants[0].id
    chore_ids = {str(row["id"]) for row in MISCELLANIA_APPROVAL_CHORES}
    chore = str(source.get("approval_chore", MISCELLANIA_APPROVAL_CHORES[0]["id"]))
    current_day = _int(answered_cards) // MISCELLANIA_REVIEWS_PER_DAY
    return {
        "version": MISCELLANIA_STATE_VERSION,
        "approval_basis_points": min(
            10000, _int(source.get("approval_basis_points"), 10000)
        ),
        "coffer": _int(source.get("coffer"), maximum=7_500_000),
        "production_credit": _int(source.get("production_credit")),
        "last_world_day": min(
            current_day,
            _int(source.get("last_world_day"), current_day),
        ),
        "allocations": allocations,
        "variants": variants,
        "approval_chore": chore if chore in chore_ids else str(MISCELLANIA_APPROVAL_CHORES[0]["id"]),
        "collections": _int(source.get("collections")),
        "days_funded": _int(source.get("days_funded")),
    }


def sanitize_managing_miscellania_player_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    data = dict(player_data or {})
    state = sanitize_managing_miscellania_state_pure(
        data.get("managing_miscellania"),
        answered_cards=_answered_cards(data),
    )
    limits = miscellania_limits_pure(data)
    remaining = limits["subjects"]
    for family in MISCELLANIA_RESOURCE_FAMILIES:
        assigned = min(int(state["allocations"][family.id]), remaining)
        state["allocations"][family.id] = assigned
        remaining -= assigned
    state["coffer"] = min(int(state["coffer"]), limits["coffer_cap"])
    return {
        "managing_miscellania": state,
        "managing_miscellania_last_result": str(
            data.get("managing_miscellania_last_result", "") or ""
        )[:500],
    }


def managing_miscellania_locked_reasons_pure(
    player_data: Mapping[str, Any],
) -> tuple[str, ...]:
    if not _quest_completed(player_data, MANAGING_MISCELLANIA_QUEST_ID):
        return ("Throne of Miscellania",)
    return ()


def _eligible_chore(player_data: Mapping[str, Any], chore_id: str) -> dict[str, Any] | None:
    for row in MISCELLANIA_APPROVAL_CHORES:
        if str(row["id"]) != chore_id:
            continue
        skill = str(row["skill"])
        if _int(player_data.get(f"{skill}_level"), 1, maximum=99) >= int(row["level"]):
            return dict(row)
    return None


def managing_miscellania_can_train_pure(player_data: Mapping[str, Any]) -> bool:
    if managing_miscellania_locked_reasons_pure(player_data):
        return False
    state = sanitize_managing_miscellania_player_state_pure(player_data)[
        "managing_miscellania"
    ]
    return (
        state["approval_basis_points"] < 10000
        and _eligible_chore(player_data, state["approval_chore"]) is not None
    )


def advance_managing_miscellania_world_clock_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    # Shallow on purpose: the sanitized state below is a fresh object and is the
    # only key written back. A whole-save deep copy cost 2.07 ms on every review.
    data = dict(player_data)
    sanitized = sanitize_managing_miscellania_player_state_pure(data)
    state = sanitized["managing_miscellania"]
    current_day = _answered_cards(data) // MISCELLANIA_REVIEWS_PER_DAY
    events: list[dict[str, Any]] = []
    if current_day <= state["last_world_day"]:
        data.update(sanitized)
        return data, ()
    unlocked = not managing_miscellania_locked_reasons_pure(data)
    for day in range(state["last_world_day"] + 1, current_day + 1):
        state["last_world_day"] = day
        if not unlocked:
            continue
        limits = miscellania_limits_pure(data)
        state["approval_basis_points"] = max(
            0,
            state["approval_basis_points"] - limits["approval_decay_bp"],
        )
        salary = min(state["coffer"] // 10, limits["salary_cap"])
        state["coffer"] -= salary
        effective_salary = salary * state["approval_basis_points"] // 10000
        credit = (
            effective_salary * MISCELLANIA_CREDIT_SCALE // limits["salary_cap"]
            if limits["salary_cap"]
            else 0
        )
        state["production_credit"] += credit
        if salary:
            state["days_funded"] += 1
        events.append(
            {
                "kind": "daily_salary",
                "day": day,
                "salary": salary,
                "credit": credit,
                "approval_basis_points": state["approval_basis_points"],
            }
        )
    data.update(sanitized)
    data["managing_miscellania"] = state
    if events:
        latest = events[-1]
        data["managing_miscellania_last_result"] = (
            f"Kingdom day {latest['day']}: {latest['salary']:,} coins paid · "
            f"approval {latest['approval_basis_points'] / 100:.1f}%"
        )
    return data, tuple(events)


def _selected_variant(state: Mapping[str, Any], family_id: str):
    family = MISCELLANIA_RESOURCE_BY_ID[family_id]
    selected = str((state.get("variants") or {}).get(family_id, family.variants[0].id))
    return next(
        (variant for variant in family.variants if variant.id == selected),
        family.variants[0],
    )


def miscellania_collection_outputs_pure(
    state: Mapping[str, Any],
) -> dict[str, int]:
    credit = _int(state.get("production_credit"))
    allocations = state.get("allocations")
    workers_by_family = allocations if isinstance(allocations, Mapping) else {}
    outputs: dict[str, int] = {}
    for family in MISCELLANIA_RESOURCE_FAMILIES:
        workers = min(10, _int(workers_by_family.get(family.id)))
        if not workers or not credit:
            continue
        variant = _selected_variant(state, family.id)
        for item, daily_quantity in variant.outputs_per_full_day:
            quantity = daily_quantity * credit * workers // (
                MISCELLANIA_CREDIT_SCALE * 10
            )
            if quantity:
                outputs[item] = outputs.get(item, 0) + quantity
    maple_logs = outputs.get("Maple logs", 0)
    if maple_logs:
        outputs["Bird's nest (seeds)"] = maple_logs // 100
    return outputs


def apply_managing_miscellania_review_pure(
    player_data: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    # Shallow on purpose: the sanitized kingdom state is a fresh object and is
    # the only key written back.
    data = dict(player_data)
    locked = managing_miscellania_locked_reasons_pure(data)
    if locked:
        return data, {"allowed": False, "reason": f"Requires {locked[0]}."}
    sanitized = sanitize_managing_miscellania_player_state_pure(data)
    state = sanitized["managing_miscellania"]
    if state["approval_basis_points"] >= 10000:
        return data, {"allowed": False, "reason": "Approval is already 100%."}
    chore = _eligible_chore(data, state["approval_chore"])
    if chore is None:
        return data, {
            "allowed": False,
            "reason": "No eligible approval chore is available.",
        }
    gained = min(
        int(chore["approval_basis_points"]),
        10000 - state["approval_basis_points"],
    )
    state["approval_basis_points"] += gained
    status = (
        f"{chore['label']} · +{gained / 100:g}% approval · "
        f"{float(chore['xp']):g} {chore['skill_label']} XP"
    )
    data.update(sanitized)
    data["managing_miscellania"] = state
    data["managing_miscellania_last_result"] = status
    return data, {
        "allowed": True,
        "success": True,
        "status": status,
        "skill": chore["skill"],
        "skill_label": chore["skill_label"],
        "xp": float(chore["xp"]),
        "approval_basis_points": gained,
    }


def _coffer_target_for_days(salary_cap: int, days: int) -> int:
    return min((max(1, days) + 9) * salary_cap, salary_cap * 100)


def apply_managing_miscellania_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    # Shallow on purpose: the sanitized kingdom state is a fresh object and is
    # the only key written back.
    data = dict(player_data)
    locked = managing_miscellania_locked_reasons_pure(data)
    if locked:
        return data, False, {"reason": f"Requires {locked[0]}."}
    sanitized = sanitize_managing_miscellania_player_state_pure(data)
    state = sanitized["managing_miscellania"]
    limits = miscellania_limits_pure(data)
    body = dict(payload or {})
    inventory = dict(data.get("inventory") or {})

    if action_id in {"deposit", "withdraw"}:
        quantity = _int(body.get("quantity"))
        if quantity <= 0:
            return data, False, {"reason": "Enter a positive coin quantity."}
        if action_id == "deposit":
            quantity = min(
                quantity,
                _int(inventory.get("Coins")),
                limits["coffer_cap"] - state["coffer"],
            )
            if quantity <= 0:
                return data, False, {"reason": "No coins can be deposited."}
            inventory["Coins"] = _int(inventory.get("Coins")) - quantity
            state["coffer"] += quantity
            message = f"Deposited {quantity:,} coins into the kingdom coffer."
        else:
            quantity = min(quantity, state["coffer"])
            if quantity <= 0:
                return data, False, {"reason": "The kingdom coffer is empty."}
            state["coffer"] -= quantity
            inventory["Coins"] = _int(inventory.get("Coins")) + quantity
            message = f"Withdrew {quantity:,} coins from the kingdom coffer."
        data["inventory"] = inventory
    elif action_id in {"fund_days", "deposit_maximum"}:
        target = (
            limits["coffer_cap"]
            if action_id == "deposit_maximum"
            else _coffer_target_for_days(limits["salary_cap"], _int(body.get("days"), 1))
        )
        quantity = min(
            max(0, target - state["coffer"]),
            _int(inventory.get("Coins")),
            limits["coffer_cap"] - state["coffer"],
        )
        if quantity <= 0:
            return data, False, {"reason": "No coins are available for that target balance."}
        inventory["Coins"] = _int(inventory.get("Coins")) - quantity
        state["coffer"] += quantity
        data["inventory"] = inventory
        message = f"Funded the kingdom coffer to {state['coffer']:,} coins."
    elif action_id == "set_workers":
        family_id = str(body.get("family_id", ""))
        if family_id not in MISCELLANIA_RESOURCE_BY_ID:
            return data, False, {"reason": "Unknown kingdom resource family."}
        requested = min(10, _int(body.get("workers")))
        current = int(state["allocations"].get(family_id, 0))
        assigned_elsewhere = sum(state["allocations"].values()) - current
        if assigned_elsewhere + requested > limits["subjects"]:
            return data, False, {"reason": "Not enough unassigned subjects."}
        state["allocations"][family_id] = requested
        message = (
            f"Assigned {requested} subject{'s' if requested != 1 else ''} "
            f"to {MISCELLANIA_RESOURCE_BY_ID[family_id].label}."
        )
    elif action_id == "set_variant":
        family_id = str(body.get("family_id", ""))
        variant_id = str(body.get("variant_id", ""))
        family = MISCELLANIA_RESOURCE_BY_ID.get(family_id)
        if family is None or variant_id not in {variant.id for variant in family.variants}:
            return data, False, {"reason": "Unknown kingdom resource option."}
        state["variants"][family_id] = variant_id
        message = f"{family.label} output set to {_selected_variant(state, family_id).label}."
    elif action_id == "set_approval_chore":
        chore_id = str(body.get("chore_id", ""))
        chore = next(
            (
                row
                for row in MISCELLANIA_APPROVAL_CHORES
                if str(row["id"]) == chore_id
            ),
            None,
        )
        if chore is None:
            return data, False, {"reason": "Unknown approval chore."}
        if _eligible_chore(data, chore_id) is None:
            return data, False, {"reason": "That approval chore is not eligible."}
        state["approval_chore"] = chore_id
        message = f"Approval work set to {chore['label']}."
    elif action_id == "collect":
        outputs = miscellania_collection_outputs_pure(state)
        if not state["production_credit"]:
            return data, False, {"reason": "The kingdom has no unclaimed production."}
        if not outputs:
            return data, False, {
                "reason": "No whole resources are ready yet. Keep the coffer funded."
            }
        for item, quantity in outputs.items():
            inventory[item] = _int(inventory.get(item)) + quantity
        data["inventory"] = inventory
        state["production_credit"] = 0
        state["collections"] += 1
        summary = ", ".join(f"{item} ×{quantity:,}" for item, quantity in outputs.items())
        message = f"Advisor Ghrim banked {summary}."
    else:
        return data, False, {"reason": "Unknown Managing Miscellania action."}

    data.update(sanitized)
    data["managing_miscellania"] = state
    data["managing_miscellania_last_result"] = message
    return data, True, {"message": message}


def managing_miscellania_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = sanitize_managing_miscellania_player_state_pure(player_data)
    state = sanitized["managing_miscellania"]
    limits = miscellania_limits_pure(player_data)
    locked = managing_miscellania_locked_reasons_pure(player_data)
    assigned = sum(state["allocations"].values())
    resources = []
    for family in MISCELLANIA_RESOURCE_FAMILIES:
        resources.append(
            {
                "id": family.id,
                "label": family.label,
                "workers": state["allocations"][family.id],
                "variant": state["variants"][family.id],
                "variants": tuple(
                    {"id": variant.id, "label": variant.label}
                    for variant in family.variants
                ),
            }
        )
    chore = next(
        row
        for row in MISCELLANIA_APPROVAL_CHORES
        if str(row["id"]) == state["approval_chore"]
    )
    chore_eligible = _eligible_chore(player_data, state["approval_chore"]) is not None
    preview = miscellania_collection_outputs_pure(state)
    answered_cards = _answered_cards(player_data)
    reviews_into_day = answered_cards % MISCELLANIA_REVIEWS_PER_DAY
    return {
        "eligible": not locked,
        "locked_reasons": locked,
        "approval_percent": state["approval_basis_points"] / 100,
        "coffer": state["coffer"],
        "coffer_cap": limits["coffer_cap"],
        "salary_cap": limits["salary_cap"],
        "subjects": limits["subjects"],
        "assigned_subjects": assigned,
        "idle_subjects": limits["subjects"] - assigned,
        "production_credit": state["production_credit"],
        "production_days": state["production_credit"] / MISCELLANIA_CREDIT_SCALE,
        "reviews_to_next_day": MISCELLANIA_REVIEWS_PER_DAY - reviews_into_day,
        "approval_decay_percent": limits["approval_decay_bp"] / 100,
        "royal_trouble_completed": _quest_completed(
            player_data, ROYAL_TROUBLE_QUEST_ID
        ),
        "bank_coins": _int((player_data.get("inventory") or {}).get("Coins"))
        if isinstance(player_data.get("inventory"), Mapping)
        else 0,
        "resources": tuple(resources),
        "preview": preview,
        "can_collect": bool(preview),
        "can_train": managing_miscellania_can_train_pure(player_data),
        "approval_chore": dict(chore),
        "approval_chores": tuple(
            dict(row)
            for row in MISCELLANIA_APPROVAL_CHORES
            if _eligible_chore(player_data, str(row["id"])) is not None
        ),
        "approval_chore_eligible": chore_eligible,
        "collections": state["collections"],
        "days_funded": state["days_funded"],
        "last_result": sanitized["managing_miscellania_last_result"],
    }
