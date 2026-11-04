"""Utility/Activity runs: no-XP recipes that turn bank materials into products.

They sit below logic_pure_production so quest supply steps can run a Utility
row without importing production logic, which imports quest logic.
"""

from __future__ import annotations

from typing import Mapping

from ..logic_pure_state import _at_most, _positive_int


def _max_batches_for_requirements(requirements, inventory, batch_size):
    if not requirements:
        return batch_size
    possible = batch_size
    for material, amount in requirements.items():
        per_batch = _positive_int(amount)
        possible = min(possible, inventory.get(material, 0) // per_batch)
    return possible


def utility_activity_material_requirements_pure(activity_key, inventory, utility_activity_data):
    """Resolve the exact consumable materials for a no-XP Utility/Activity."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return None
    requirements = dict(spec.get("requirements", {}))
    for material, alternatives in spec.get("material_options", {}).items():
        amount = requirements.get(material)
        if amount is None:
            continue
        selected = next(
            (option for option in alternatives if inventory.get(option, 0) >= amount),
            None,
        )
        if selected is None:
            return None
        del requirements[material]
        requirements[selected] = amount
    return requirements


def can_perform_utility_activity_pure(inventory, activity_key, utility_activity_data):
    """Return True if a no-XP Utility/Activity can run for at least one batch."""
    spec = utility_activity_data.get(activity_key)
    if not spec:
        return False
    for option_group in spec.get("required_item_options", ()):
        if not any(inventory.get(item_name, 0) > 0 for item_name in option_group):
            return False
    openable_items = spec.get("openable_items")
    if openable_items:
        return any(inventory.get(item_name, 0) > 0 for item_name in openable_items)
    requirements = utility_activity_material_requirements_pure(
        activity_key, inventory, utility_activity_data
    )
    if requirements is None:
        return False
    batch_size = _positive_int(spec.get("batch_size", 1))
    if _max_batches_for_requirements(requirements, inventory, batch_size) <= 0:
        return False
    any_requirements = spec.get("any_requirements")
    if isinstance(any_requirements, (list, tuple, set)) and any_requirements:
        return any(inventory.get(str(item_name), 0) > 0 for item_name in any_requirements)
    return True


def _utility_outputs_from_spec(spec):
    outputs = spec.get("outputs")
    if isinstance(outputs, Mapping):
        return {
            str(item): _positive_int(amount, 1)
            for item, amount in outputs.items()
            if isinstance(item, str) and item
        }
    output_item = spec.get("output_item")
    if isinstance(output_item, str) and output_item:
        return {output_item: _positive_int(spec.get("output_qty", 1), 1)}
    return {}


def apply_utility_activity_pure(
    activity_key, inventory, utility_activity_data, r_output=None, batch_limit=None
):
    """Apply a no-XP Utility/Activity, at most ``batch_limit`` batches, and return (inventory, exp, success, processed)."""
    spec = utility_activity_data.get(activity_key)
    if not spec or not can_perform_utility_activity_pure(
        inventory,
        activity_key,
        utility_activity_data,
    ):
        return inventory, 0, False, 0
    if spec.get("no_op"):
        return dict(inventory), 0, True, 1
    requirements = utility_activity_material_requirements_pure(
        activity_key, inventory, utility_activity_data
    )
    batch_size = _at_most(_positive_int(spec.get("batch_size", 1)), batch_limit)
    batch_count = _max_batches_for_requirements(requirements, inventory, batch_size)
    if batch_count <= 0:
        return inventory, 0, False, 0

    new_inv = dict(inventory)
    for material, amount in requirements.items():
        new_inv[material] = new_inv.get(material, 0) - (_positive_int(amount) * batch_count)
    outputs = _utility_outputs_from_spec(spec)
    weighted_outputs = spec.get("weighted_outputs", ())
    if weighted_outputs:
        total_weight = sum(
            _positive_int(row.get("weight", 0), 0)
            for row in weighted_outputs
            if isinstance(row, Mapping)
        ) + _positive_int(spec.get("non_bone_output_weight", 0), 0)
        roll = max(0.0, min(float(0.0 if r_output is None else r_output), 0.999999999))
        slot = int(roll * total_weight) if total_weight else 0
        cursor = 0
        outputs = {}
        for row in weighted_outputs:
            if not isinstance(row, Mapping):
                continue
            cursor += _positive_int(row.get("weight", 0), 0)
            if slot < cursor:
                item_name = row.get("item")
                if isinstance(item_name, str) and item_name:
                    outputs[item_name] = _positive_int(row.get("quantity", 1), 1)
                break
    elif not outputs:
        outputs = {activity_key: 1}
    for output_item, output_qty in outputs.items():
        new_inv[output_item] = new_inv.get(output_item, 0) + (output_qty * batch_count)
    return new_inv, 0, True, batch_count
