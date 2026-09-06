"""Pure shop services, vendor actions, and potion container exchange."""

from __future__ import annotations

from typing import Any, Dict, Mapping

from ...data.shop_data import (
    SHOP_PLAYER_SELL_PRICES,
    SHOP_SERVICES,
    SHOP_VENDOR_ACTIONS,
)
from ...data.herblore_data import HERBLORE_TARGETS
from ...data.potion_data import (
    EMPTY_FLASK_ITEM,
    POTION_FAMILIES,
    VIAL_ITEM,
    potion_dose_name,
    potion_flask_name,
)
from ...logic_pure.quest_action_proofs import record_runtime_quest_action_proofs_pure
from .state import (
    _add_inventory,
    _append_event,
    _build_event,
    _clean_int,
    _denied,
    _inventory_count,
    ensure_shop_state_pure,
    shop_access_lock_reason_pure,
)


# Bob Barter's ordinary-vial catalog is the live, non-Daemonheim Herblore
# catalog. Barbarian mixes use two-dose bowls rather than four-dose vials.
DECANTABLE_FOUR_DOSE_POTION_BASES = tuple(
    sorted(
        {
            target.output_item[:-4]
            for target in HERBLORE_TARGETS
            if target.group == "finished"
            and target.subgroup != "barbarian"
            and target.output_item.endswith(" (3)")
            and all(
                f"{target.output_item[:-4]} ({dose})" in SHOP_PLAYER_SELL_PRICES
                for dose in range(1, 5)
            )
        }
    )
)
DECANTABLE_FLASK_POTION_BASES = tuple(
    sorted(
        base
        for base, spec in POTION_FAMILIES.items()
        if set(spec.get("doses", {})) == {1, 2, 3, 4}
        and set(spec.get("flask_doses", {})) == {1, 2, 3, 4, 5, 6}
    )
)


def preview_shop_service_pure(player_data: Mapping[str, Any], service_id: str, quantity: int = 1) -> Dict[str, Any]:
    service = SHOP_SERVICES.get(service_id)
    if service is None:
        return _denied("unknown_service", requested_quantity=quantity)
    if service.get("action_type") == "decant_potions_to_dose":
        return _preview_decant_potions(player_data, service, quantity)
    if service.get("action_type") == "fill_potion_flasks":
        return _preview_fill_potion_flasks(player_data, service)
    if service.get("action_type") == "decant_flasks_to_vials":
        return _preview_decant_flasks_to_vials(player_data, service)
    return _preview_service_like(player_data, service, quantity)


def apply_shop_service_pure(player_data: Mapping[str, Any], service_id: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    service = SHOP_SERVICES.get(service_id)
    data = ensure_shop_state_pure(player_data)
    if service is None:
        return data, _denied("unknown_service", requested_quantity=quantity)
    if service.get("action_type") == "decant_potions_to_dose":
        return _apply_decant_potions(data, service, quantity)
    if service.get("action_type") == "fill_potion_flasks":
        return _apply_fill_potion_flasks(data, service)
    if service.get("action_type") == "decant_flasks_to_vials":
        return _apply_decant_flasks_to_vials(data, service)
    return _apply_service_like(data, service, "service", quantity)


def preview_shop_vendor_action_pure(player_data: Mapping[str, Any], action_id: str, quantity: int = 1) -> Dict[str, Any]:
    action = SHOP_VENDOR_ACTIONS.get(action_id)
    if action is None:
        return _denied("unknown_vendor_action", requested_quantity=quantity)
    # Dialogue parity (owner decision 2026-07-07): every vendor action is one
    # interaction per use — Karim hands over exactly one kebab per
    # conversation. The quantity spinner was an AnkiScape invention.
    return _preview_service_like(player_data, action, 1)


def apply_shop_vendor_action_pure(player_data: Mapping[str, Any], action_id: str, quantity: int = 1) -> tuple[Dict[str, Any], Dict[str, Any]]:
    action = SHOP_VENDOR_ACTIONS.get(action_id)
    data = ensure_shop_state_pure(player_data)
    if action is None:
        return data, _denied("unknown_vendor_action", requested_quantity=quantity)
    # Dialogue parity: one interaction per use regardless of requested qty.
    return _apply_service_like(data, action, "vendor_action", 1)


def _preview_service_like(player_data: Mapping[str, Any], service: Mapping[str, Any], quantity: int) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    requested = max(1, int(quantity))
    if service.get("visibility") != "visible":
        return _denied(service.get("lock_reason") or "service_not_visible", requested_quantity=requested, service_id=service["id"])
    access_lock = shop_access_lock_reason_pure(data, service)
    if access_lock:
        return _denied(
            access_lock,
            requested_quantity=requested,
            service_id=service["id"],
        )
    required_skill = str(service.get("required_skill", ""))
    required_level = _clean_int(service.get("required_level"), 0, minimum=0)
    if required_skill and required_level:
        current_level = _clean_int(
            data.get(f"{required_skill}_level"), 1, minimum=1
        )
        if current_level < required_level:
            return _denied(
                "skill_level",
                requested_quantity=requested,
                service_id=service["id"],
                skill_id=required_skill,
                required_level=required_level,
                current_level=current_level,
            )
    currency_name = str(service.get("currency_item_name", "Coins"))
    unit_price = _clean_int(service.get("price"), 0, minimum=0)
    requested_requirements = _service_requirement_rows(data, service, requested, unit_price, currency_name)
    max_quantity = requested
    if unit_price:
        max_quantity = min(max_quantity, _inventory_count(data, currency_name) // unit_price)
    for item in service.get("inputs", []):
        max_quantity = min(max_quantity, _inventory_count(data, item["item_name"]) // max(1, int(item["quantity"])))
    if max_quantity <= 0:
        return _denied(
            "missing_requirements",
            requested_quantity=requested,
            service_id=service["id"],
            unit_price=unit_price,
            currency_item_name=currency_name,
            requirements=requested_requirements,
            missing_requirements=[row for row in requested_requirements if int(row.get("shortfall", 0) or 0) > 0],
        )
    return {
        "allowed": True,
        "transaction_type": "service_like",
        "id": service["id"],
        "display_name": service["display_name"],
        "requested_quantity": requested,
        "quantity": max_quantity,
        "clamped": max_quantity != requested,
        "unit_price": unit_price,
        "total_price": unit_price * max_quantity,
        "currency_item_name": currency_name,
        "requirements": _service_requirement_rows(data, service, max_quantity, unit_price, currency_name),
        "requested_requirements": requested_requirements,
    }


def _decant_potions_delta(
    data: Mapping[str, Any], target_dose: int
) -> tuple[Dict[str, int], list[str], int, int, int]:
    inventory_delta: Dict[str, int] = {}
    changed_families: list[str] = []
    total_doses = 0
    vial_balance = 0
    for base in DECANTABLE_FOUR_DOSE_POTION_BASES:
        counts = {dose: _inventory_count(data, f"{base} ({dose})") for dose in range(1, 5)}
        family_doses = sum(dose * count for dose, count in counts.items())
        if not family_doses:
            continue
        full_vials, remainder = divmod(family_doses, target_dose)
        result_counts = {dose: 0 for dose in range(1, 5)}
        result_counts[target_dose] = full_vials
        if remainder:
            result_counts[remainder] += 1
        family_delta = {
            f"{base} ({dose})": result_counts[dose] - counts[dose]
            for dose in range(1, 5)
            if result_counts[dose] != counts[dose]
        }
        if not family_delta:
            continue
        inventory_delta.update(family_delta)
        changed_families.append(base)
        total_doses += family_doses
        vial_balance += sum(counts.values()) - sum(result_counts.values())
    if vial_balance:
        inventory_delta["Vial"] = vial_balance
    return (
        inventory_delta,
        changed_families,
        total_doses,
        max(0, vial_balance),
        max(0, -vial_balance),
    )


def _preview_decant_potions(
    player_data: Mapping[str, Any], service: Mapping[str, Any], target_dose: int
) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    requested = int(target_dose)
    if requested not in (2, 3, 4):
        return _denied(
            "unsupported_decant_dose",
            requested_quantity=requested,
            service_id=service["id"],
        )
    if service.get("visibility") != "visible":
        return _denied(
            service.get("lock_reason") or "service_not_visible",
            requested_quantity=requested,
            service_id=service["id"],
        )
    access_lock = shop_access_lock_reason_pure(data, service)
    if access_lock:
        return _denied(
            access_lock,
            requested_quantity=requested,
            service_id=service["id"],
        )
    inventory_delta, changed_families, total_doses, returned_vials, required_vials = (
        _decant_potions_delta(data, requested)
    )
    if not inventory_delta:
        return _denied("no_potions_to_decant", requested_quantity=requested, service_id=service["id"])
    owned_vials = _inventory_count(data, "Vial")
    if required_vials > owned_vials:
        return _denied(
            "missing_decant_vials",
            requested_quantity=requested,
            service_id=service["id"],
            target_dose=requested,
            required_vials=required_vials,
            owned_vials=owned_vials,
        )
    return {
        "allowed": True,
        "transaction_type": "service_like",
        "id": service["id"],
        "display_name": service["display_name"],
        "requested_quantity": 1,
        "quantity": 1,
        "clamped": False,
        "unit_price": 0,
        "total_price": 0,
        "currency_item_name": str(service.get("currency_item_name", "Coins")),
        "requirements": [],
        "requested_requirements": [],
        "inventory_delta": inventory_delta,
        "decanted_families": changed_families,
        "family_count": len(changed_families),
        "target_dose": requested,
        "total_doses": total_doses,
        "returned_vials": returned_vials,
        "required_vials": required_vials,
    }


def _apply_decant_potions(
    data: Dict[str, Any], service: Mapping[str, Any], target_dose: int
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    preview = _preview_decant_potions(data, service, target_dose)
    if not preview["allowed"]:
        return data, preview
    inventory_delta = preview["inventory_delta"]
    for item_name, delta in inventory_delta.items():
        _add_inventory(data, item_name, delta)
    event = _build_event(
        data,
        "service",
        {"id": "", "display_name": service["display_name"], "shared_stock_group": ""},
        quantity=1,
        service_id=service["id"],
        item_name=service["display_name"],
        total_price=0,
        inventory_delta=inventory_delta,
        stock_set={},
        stock_delta={},
    )
    _append_event(data, event)
    result = dict(preview)
    result["event_id"] = event["event_id"]
    return data, result


def _consume_potion_doses(
    inventory_delta: Dict[str, int],
    counts: Mapping[int, int],
    *,
    base: str,
    doses_to_move: int,
    flask: bool,
) -> tuple[int, int]:
    remaining = doses_to_move
    emptied_containers = 0
    name_for_dose = potion_flask_name if flask else potion_dose_name
    for dose in range(4, 0, -1):
        for _ in range(counts.get(dose, 0)):
            if remaining <= 0:
                return doses_to_move, emptied_containers
            source_name = name_for_dose(base, dose)
            moved = min(dose, remaining)
            inventory_delta[source_name] = inventory_delta.get(source_name, 0) - 1
            if moved < dose:
                remainder_name = name_for_dose(base, dose - moved)
                inventory_delta[remainder_name] = inventory_delta.get(remainder_name, 0) + 1
            else:
                emptied_containers += 1
                if not flask:
                    inventory_delta[VIAL_ITEM[0]] = (
                        inventory_delta.get(VIAL_ITEM[0], 0) + 1
                    )
            remaining -= moved
    return doses_to_move - remaining, emptied_containers


def _fill_potion_flasks_delta(
    data: Mapping[str, Any],
) -> tuple[Dict[str, int], list[str], int, int, int, int]:
    inventory_delta: Dict[str, int] = {}
    changed_families: list[str] = []
    total_doses = 0
    returned_vials = 0
    destroyed_flasks = 0
    empty_flasks = _inventory_count(data, EMPTY_FLASK_ITEM[0])
    for base in DECANTABLE_FLASK_POTION_BASES:
        if empty_flasks <= 0:
            break
        vial_counts = {
            dose: _inventory_count(data, potion_dose_name(base, dose))
            for dose in range(1, 5)
        }
        flask_counts = {
            dose: _inventory_count(data, potion_flask_name(base, dose))
            for dose in range(1, 5)
        }
        eligible_doses = sum(
            dose * (vial_counts[dose] + flask_counts[dose])
            for dose in range(1, 5)
        )
        flask_count = min(empty_flasks, eligible_doses // 6)
        if flask_count <= 0:
            continue

        doses_to_move = flask_count * 6
        moved_from_vials, emptied_vials = _consume_potion_doses(
            inventory_delta,
            vial_counts,
            base=base,
            doses_to_move=doses_to_move,
            flask=False,
        )
        moved_from_flasks, emptied_partial_flasks = _consume_potion_doses(
            inventory_delta,
            flask_counts,
            base=base,
            doses_to_move=doses_to_move - moved_from_vials,
            flask=True,
        )
        if moved_from_vials + moved_from_flasks != doses_to_move:
            raise ValueError(f"Could not conserve {base} doses while filling flasks")

        inventory_delta[EMPTY_FLASK_ITEM[0]] = (
            inventory_delta.get(EMPTY_FLASK_ITEM[0], 0) - flask_count
        )
        full_flask_name = potion_flask_name(base, 6)
        inventory_delta[full_flask_name] = inventory_delta.get(full_flask_name, 0) + flask_count
        changed_families.append(base)
        total_doses += doses_to_move
        returned_vials += emptied_vials
        destroyed_flasks += emptied_partial_flasks
        empty_flasks -= flask_count

    return (
        inventory_delta,
        changed_families,
        total_doses,
        len(changed_families),
        returned_vials,
        max(0, destroyed_flasks),
    )


def _preview_fill_potion_flasks(
    player_data: Mapping[str, Any], service: Mapping[str, Any]
) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    if service.get("visibility") != "visible":
        return _denied(
            service.get("lock_reason") or "service_not_visible",
            requested_quantity=1,
            service_id=service["id"],
        )
    access_lock = shop_access_lock_reason_pure(data, service)
    if access_lock:
        return _denied(access_lock, requested_quantity=1, service_id=service["id"])
    if _inventory_count(data, EMPTY_FLASK_ITEM[0]) <= 0:
        return _denied(
            "missing_empty_potion_flask",
            requested_quantity=1,
            service_id=service["id"],
        )
    (
        inventory_delta,
        changed_families,
        total_doses,
        family_count,
        returned_vials,
        destroyed_flasks,
    ) = _fill_potion_flasks_delta(data)
    if not inventory_delta:
        return _denied(
            "insufficient_flask_doses",
            requested_quantity=1,
            service_id=service["id"],
        )
    flasks_created = sum(
        delta
        for item_name, delta in inventory_delta.items()
        if item_name.endswith(" flask (6)") and delta > 0
    )
    return {
        "allowed": True,
        "transaction_type": "service_like",
        "id": service["id"],
        "display_name": service["display_name"],
        "requested_quantity": 1,
        "quantity": 1,
        "clamped": False,
        "unit_price": 0,
        "total_price": 0,
        "currency_item_name": str(service.get("currency_item_name", "Coins")),
        "requirements": [],
        "requested_requirements": [],
        "inventory_delta": inventory_delta,
        "decanted_families": changed_families,
        "family_count": family_count,
        "total_doses": total_doses,
        "flasks_created": flasks_created,
        "returned_vials": returned_vials,
        "destroyed_flasks": destroyed_flasks,
    }


def _decant_flasks_to_vials_delta(
    data: Mapping[str, Any],
) -> tuple[Dict[str, int], list[str], int, int, int]:
    inventory_delta: Dict[str, int] = {}
    changed_families: list[str] = []
    total_doses = 0
    destroyed_flasks = 0
    created_vials = 0
    for base in DECANTABLE_FLASK_POTION_BASES:
        counts = {
            dose: _inventory_count(data, potion_flask_name(base, dose))
            for dose in range(1, 5)
        }
        family_doses = sum(dose * count for dose, count in counts.items())
        if family_doses <= 0:
            continue
        for dose, count in counts.items():
            if count:
                inventory_delta[potion_flask_name(base, dose)] = -count
        full_vials, remainder = divmod(family_doses, 4)
        if full_vials:
            inventory_delta[potion_dose_name(base, 4)] = full_vials
        if remainder:
            inventory_delta[potion_dose_name(base, remainder)] = (
                inventory_delta.get(potion_dose_name(base, remainder), 0) + 1
            )
        changed_families.append(base)
        total_doses += family_doses
        destroyed_flasks += sum(counts.values())
        created_vials += full_vials + bool(remainder)
    return (
        inventory_delta,
        changed_families,
        total_doses,
        destroyed_flasks,
        created_vials,
    )


def _preview_decant_flasks_to_vials(
    player_data: Mapping[str, Any], service: Mapping[str, Any]
) -> Dict[str, Any]:
    data = ensure_shop_state_pure(player_data)
    if service.get("visibility") != "visible":
        return _denied(
            service.get("lock_reason") or "service_not_visible",
            requested_quantity=1,
            service_id=service["id"],
        )
    access_lock = shop_access_lock_reason_pure(data, service)
    if access_lock:
        return _denied(access_lock, requested_quantity=1, service_id=service["id"])
    (
        inventory_delta,
        changed_families,
        total_doses,
        destroyed_flasks,
        created_vials,
    ) = _decant_flasks_to_vials_delta(data)
    if not inventory_delta:
        return _denied(
            "no_partial_flasks_to_decant",
            requested_quantity=1,
            service_id=service["id"],
        )
    return {
        "allowed": True,
        "transaction_type": "service_like",
        "id": service["id"],
        "display_name": service["display_name"],
        "requested_quantity": 1,
        "quantity": 1,
        "clamped": False,
        "unit_price": 0,
        "total_price": 0,
        "currency_item_name": str(service.get("currency_item_name", "Coins")),
        "requirements": [],
        "requested_requirements": [],
        "inventory_delta": inventory_delta,
        "decanted_families": changed_families,
        "family_count": len(changed_families),
        "total_doses": total_doses,
        "destroyed_flasks": destroyed_flasks,
        "created_vials": created_vials,
    }


def _apply_inventory_wide_service(
    data: Dict[str, Any],
    service: Mapping[str, Any],
    preview: Mapping[str, Any],
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    if not preview["allowed"]:
        return data, dict(preview)
    inventory_delta = dict(preview["inventory_delta"])
    for item_name, delta in inventory_delta.items():
        _add_inventory(data, item_name, delta)
    event = _build_event(
        data,
        "service",
        {"id": "", "display_name": service["display_name"], "shared_stock_group": ""},
        quantity=1,
        service_id=service["id"],
        item_name=service["display_name"],
        total_price=0,
        inventory_delta=inventory_delta,
        stock_set={},
        stock_delta={},
    )
    _append_event(data, event)
    result = dict(preview)
    result["event_id"] = event["event_id"]
    return data, result


def _apply_fill_potion_flasks(
    data: Dict[str, Any], service: Mapping[str, Any]
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    return _apply_inventory_wide_service(
        data,
        service,
        _preview_fill_potion_flasks(data, service),
    )


def _apply_decant_flasks_to_vials(
    data: Dict[str, Any], service: Mapping[str, Any]
) -> tuple[Dict[str, Any], Dict[str, Any]]:
    return _apply_inventory_wide_service(
        data,
        service,
        _preview_decant_flasks_to_vials(data, service),
    )


def _apply_service_like(data: Dict[str, Any], service: Mapping[str, Any], event_type: str, quantity: int) -> tuple[Dict[str, Any], Dict[str, Any]]:
    preview = _preview_service_like(data, service, quantity)
    if not preview["allowed"]:
        return data, preview
    amount = preview["quantity"]
    inventory_delta: Dict[str, int] = {}
    currency_name = preview["currency_item_name"]
    if preview["total_price"]:
        inventory_delta[currency_name] = inventory_delta.get(currency_name, 0) - preview["total_price"]
    for item in service.get("inputs", []):
        inventory_delta[item["item_name"]] = inventory_delta.get(item["item_name"], 0) - int(item["quantity"]) * amount
    for item in service.get("outputs", []):
        inventory_delta[item["item_name"]] = inventory_delta.get(item["item_name"], 0) + int(item["quantity"]) * amount
    for item_name, delta in inventory_delta.items():
        _add_inventory(data, item_name, delta)
    event = _build_event(
        data,
        event_type,
        {"id": "", "display_name": service["display_name"], "shared_stock_group": ""},
        quantity=amount,
        service_id=service["id"],
        item_name=service["display_name"],
        total_price=preview["total_price"],
        inventory_delta=inventory_delta,
        stock_set={},
        stock_delta={},
    )
    _append_event(data, event)
    record_runtime_quest_action_proofs_pure(data, f"shop_{event_type}", str(service["id"]))
    result = dict(preview)
    result["event_id"] = event["event_id"]
    return data, result


def _service_requirement_rows(
    data: Mapping[str, Any],
    service: Mapping[str, Any],
    quantity: int,
    unit_price: int,
    currency_name: str,
) -> list[Dict[str, Any]]:
    rows: list[Dict[str, Any]] = []
    if unit_price:
        owned = _inventory_count(data, currency_name)
        required = unit_price * quantity
        rows.append(
            {
                "item_name": currency_name,
                "required_quantity": required,
                "owned_quantity": owned,
                "shortfall": max(0, required - owned),
                "kind": "currency",
            }
        )
    for item in service.get("inputs", []):
        item_name = str(item.get("item_name", ""))
        if not item_name:
            continue
        required = _clean_int(item.get("quantity"), 1, minimum=1) * quantity
        owned = _inventory_count(data, item_name)
        rows.append(
            {
                "item_name": item_name,
                "required_quantity": required,
                "owned_quantity": owned,
                "shortfall": max(0, required - owned),
                "kind": "item",
            }
        )
    return rows
