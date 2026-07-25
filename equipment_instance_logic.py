"""Pure per-copy condition state for non-stackable degradable equipment."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any


VALID_INSTANCE_LOCATIONS = {"bank", "grave", "death_office"}


def default_equipment_instance_state_pure() -> dict[str, Any]:
    return {"equipment_instances": {}, "equipment_instance_next_id": 1}


def _clean_int(value: Any, default: int = 0, *, minimum: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _family_for_item(item_name: str, condition_data: Mapping[str, Mapping[str, Any]]) -> str | None:
    for family_id, spec in condition_data.items():
        if item_name == spec.get("full_name"):
            return family_id
        names = spec.get("names_by_percent", {})
        if isinstance(names, Mapping) and item_name in names.values():
            return family_id
    return None


def is_condition_item_pure(
    item_name: str, condition_data: Mapping[str, Mapping[str, Any]]
) -> bool:
    return bool(_family_for_item(item_name, condition_data))


def _condition_for_name(item_name: str, spec: Mapping[str, Any]) -> int:
    maximum = max(1, _clean_int(spec.get("max_condition"), 1, minimum=1))
    if item_name == spec.get("full_name"):
        return maximum
    names = spec.get("names_by_percent", {})
    if isinstance(names, Mapping):
        for raw_percent, name in names.items():
            if name != item_name:
                continue
            percent = min(100, _clean_int(raw_percent, 0))
            return (maximum * percent) // 100
    return maximum


def condition_name_pure(family_id: str, condition: Any, condition_data: Mapping[str, Mapping[str, Any]]) -> str:
    spec = condition_data[family_id]
    maximum = max(1, _clean_int(spec.get("max_condition"), 1, minimum=1))
    remaining = min(maximum, _clean_int(condition, 0))
    names = spec.get("names_by_percent", {})
    if not isinstance(names, Mapping) or not names:
        return str(spec.get("display_name", family_id))
    available = sorted((_clean_int(value, 0), str(name)) for value, name in names.items())
    if remaining == maximum and spec.get("full_name"):
        return str(spec["full_name"])
    percent = (remaining * 100) / maximum
    for threshold, name in available:
        if percent <= threshold:
            return name
    return available[-1][1]


def _clean_location(value: Any) -> str | None:
    if value in VALID_INSTANCE_LOCATIONS:
        return str(value)
    if isinstance(value, str) and value.startswith("equipped:") and value.partition(":")[2]:
        return value
    return None


def _expected_condition_holders(
    data: Mapping[str, Any], condition_data: Mapping[str, Mapping[str, Any]]
) -> Counter[tuple[str, str]]:
    expected: Counter[tuple[str, str]] = Counter()
    inventory = data.get("inventory", {})
    if isinstance(inventory, Mapping):
        for item_name, count in inventory.items():
            if isinstance(item_name, str) and _family_for_item(item_name, condition_data):
                expected[("bank", item_name)] += _clean_int(count, 0)
    equipment = data.get("equipment", {})
    if isinstance(equipment, Mapping):
        for slot, item_name in equipment.items():
            if isinstance(slot, str) and isinstance(item_name, str) and _family_for_item(item_name, condition_data):
                expected[(f"equipped:{slot}", item_name)] += 1
    for state_key, location in (("combat_grave", "grave"), ("death_office", "death_office")):
        state = data.get(state_key, {})
        items = state.get("items", ()) if isinstance(state, Mapping) else ()
        if isinstance(items, (list, tuple)):
            for item_name in items:
                if isinstance(item_name, str) and _family_for_item(item_name, condition_data):
                    expected[(location, item_name)] += 1
    return expected


def sanitize_equipment_instance_state_pure(
    player_data: Mapping[str, Any], condition_data: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    """Reconcile the per-copy ledger with Bank/equipment/grave name holders."""
    # Shallow on purpose: the ledger below is rebuilt as fresh records, and
    # every caller rebuilds inventory before writing to it.
    data = dict(player_data)
    raw_instances = data.get("equipment_instances", {})
    cleaned: dict[str, dict[str, Any]] = {}
    max_seen_id = 0
    if isinstance(raw_instances, Mapping):
        for raw_id, raw_record in raw_instances.items():
            if not isinstance(raw_id, str) or not isinstance(raw_record, Mapping):
                continue
            family_id = raw_record.get("family_id")
            location = _clean_location(raw_record.get("location"))
            if not isinstance(family_id, str) or family_id not in condition_data or location is None:
                continue
            spec = condition_data[family_id]
            maximum = max(1, _clean_int(spec.get("max_condition"), 1, minimum=1))
            condition = min(maximum, _clean_int(raw_record.get("condition"), maximum))
            record = {
                "family_id": family_id,
                "item_name": condition_name_pure(family_id, condition, condition_data),
                "condition": condition,
                "location": location,
            }
            last_slot = raw_record.get("last_slot")
            if isinstance(last_slot, str) and last_slot:
                record["last_slot"] = last_slot
            cleaned[raw_id] = record
            if raw_id.startswith("equipment-"):
                max_seen_id = max(max_seen_id, _clean_int(raw_id.removeprefix("equipment-"), 0))

    next_id = max(
        max_seen_id + 1,
        _clean_int(data.get("equipment_instance_next_id"), 1, minimum=1),
    )
    expected = _expected_condition_holders(data, condition_data)
    assigned: dict[str, dict[str, Any]] = {}
    unused = set(cleaned)

    location_order = {"grave": 1, "death_office": 2, "bank": 3}
    expected_rows = sorted(
        expected.items(),
        key=lambda row: (
            0 if row[0][0].startswith("equipped:") else location_order.get(row[0][0], 4),
            row[0],
        ),
    )
    remaining_expected = Counter(expected)
    for (location, item_name), count in expected_rows:
        matching_location = [
            instance_id
            for instance_id in sorted(
                unused,
                key=lambda value: (
                    -_clean_int(cleaned[value].get("condition"), 0)
                    if location.startswith("equipped:")
                    else 0,
                    value,
                ),
            )
            if cleaned[instance_id]["location"] == location
            and cleaned[instance_id]["item_name"] == item_name
        ]
        for instance_id in matching_location[:count]:
            assigned[instance_id] = dict(cleaned[instance_id])
            unused.discard(instance_id)
            remaining_expected[(location, item_name)] -= 1

    for (location, item_name), _count in expected_rows:
        count = remaining_expected[(location, item_name)]
        candidates = [
            instance_id
            for instance_id in sorted(
                unused,
                key=lambda value: (
                    -_clean_int(cleaned[value].get("condition"), 0)
                    if location.startswith("equipped:")
                    else 0,
                    value,
                ),
            )
            if cleaned[instance_id]["item_name"] == item_name
        ]
        for instance_id in candidates[:count]:
            record = dict(cleaned[instance_id])
            record["location"] = location
            if location.startswith("equipped:"):
                record["last_slot"] = location.partition(":")[2]
            assigned[instance_id] = record
            unused.discard(instance_id)
        missing = count - min(count, len(candidates))
        family_id = _family_for_item(item_name, condition_data)
        for _ in range(missing):
            instance_id = f"equipment-{next_id}"
            next_id += 1
            record = {
                "family_id": family_id,
                "item_name": item_name,
                "condition": _condition_for_name(item_name, condition_data[family_id]),
                "location": location,
            }
            if location.startswith("equipped:"):
                record["last_slot"] = location.partition(":")[2]
            assigned[instance_id] = record

    data["equipment_instances"] = assigned
    data["equipment_instance_next_id"] = next_id
    return data


def add_equipment_instance_pure(
    player_data: Mapping[str, Any], family_id: str, condition_data: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, Any], str | None]:
    data = sanitize_equipment_instance_state_pure(player_data, condition_data)
    if family_id not in condition_data:
        return data, None
    maximum = max(1, _clean_int(condition_data[family_id].get("max_condition"), 1, minimum=1))
    item_name = condition_name_pure(family_id, maximum, condition_data)
    instance_id = f"equipment-{data['equipment_instance_next_id']}"
    data["equipment_instance_next_id"] += 1
    data["equipment_instances"][instance_id] = {
        "family_id": family_id,
        "item_name": item_name,
        "condition": maximum,
        "location": "bank",
    }
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = _clean_int(inventory.get(item_name), 0) + 1
    data["inventory"] = inventory
    return data, instance_id


def sync_equipment_instances_pure(
    player_data: Mapping[str, Any], before_equipment: Mapping[str, str], condition_data: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    """Move condition records after the ordinary slot/name equip reducer runs."""
    data = sanitize_equipment_instance_state_pure(player_data, condition_data)
    after_equipment = data.get("equipment", {})
    if not isinstance(after_equipment, Mapping):
        return data
    instances = data["equipment_instances"]
    for slot in sorted(set(before_equipment) | set(after_equipment)):
        before_name = before_equipment.get(slot)
        after_name = after_equipment.get(slot)
        if before_name == after_name:
            continue
        if isinstance(before_name, str) and _family_for_item(before_name, condition_data):
            for record in instances.values():
                if record.get("location") == f"equipped:{slot}":
                    record["location"] = "bank"
                    record["last_slot"] = slot
                    break
        if isinstance(after_name, str) and _family_for_item(after_name, condition_data):
            candidates = [
                (instance_id, record)
                for instance_id, record in instances.items()
                if record.get("location") == "bank" and record.get("item_name") == after_name
            ]
            if candidates:
                _, record = max(candidates, key=lambda row: (_clean_int(row[1].get("condition"), 0), row[0]))
                record["location"] = f"equipped:{slot}"
                record["last_slot"] = slot
    return sanitize_equipment_instance_state_pure(data, condition_data)


def advance_equipped_condition_pure(
    player_data: Mapping[str, Any], ticks: Any, condition_data: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    data = sanitize_equipment_instance_state_pure(player_data, condition_data)
    elapsed = _clean_int(ticks, 0)
    if elapsed <= 0:
        return data, ()
    equipment = dict(data.get("equipment", {}) or {})
    inventory = dict(data.get("inventory", {}) or {})
    events = []
    for instance_id, record in data["equipment_instances"].items():
        location = record.get("location", "")
        family_id = record.get("family_id")
        spec = condition_data.get(family_id, {})
        if not isinstance(location, str) or not location.startswith("equipped:") or not spec.get("degrade_during_combat"):
            continue
        before_condition = _clean_int(record.get("condition"), 0)
        after_condition = max(0, before_condition - elapsed)
        before_name = str(record.get("item_name", ""))
        after_name = condition_name_pure(family_id, after_condition, condition_data)
        record["condition"] = after_condition
        record["item_name"] = after_name
        slot = location.partition(":")[2]
        if before_name != after_name:
            equipment[slot] = after_name
            events.append(
                {
                    "instance_id": instance_id,
                    "family_id": family_id,
                    "before_name": before_name,
                    "after_name": after_name,
                    "condition": after_condition,
                }
            )
    data["equipment"] = equipment
    data["inventory"] = inventory
    return data, tuple(events)


def discharge_equipped_on_unsafe_death_pure(
    player_data: Mapping[str, Any], condition_data: Mapping[str, Mapping[str, Any]]
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    data = sanitize_equipment_instance_state_pure(player_data, condition_data)
    equipment = dict(data.get("equipment", {}) or {})
    events = []
    for instance_id, record in data["equipment_instances"].items():
        location = record.get("location", "")
        family_id = record.get("family_id")
        spec = condition_data.get(family_id, {})
        raw_percent = spec.get("unsafe_death_percent")
        if not isinstance(location, str) or not location.startswith("equipped:") or raw_percent is None:
            continue
        maximum = max(1, _clean_int(spec.get("max_condition"), 1, minimum=1))
        condition = (maximum * min(100, _clean_int(raw_percent, 0))) // 100
        before_name = str(record.get("item_name", ""))
        after_name = condition_name_pure(family_id, condition, condition_data)
        record["condition"] = condition
        record["item_name"] = after_name
        slot = location.partition(":")[2]
        equipment[slot] = after_name
        if before_name != after_name:
            events.append(
                {
                    "instance_id": instance_id,
                    "family_id": family_id,
                    "before_name": before_name,
                    "after_name": after_name,
                }
            )
    data["equipment"] = equipment
    return data, tuple(events)


def remove_bank_equipment_instances_pure(
    player_data: Mapping[str, Any], item_name: str, count: Any, condition_data: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    data = sanitize_equipment_instance_state_pure(player_data, condition_data)
    amount = _clean_int(count, 0)
    candidates = sorted(
        (
            instance_id
            for instance_id, record in data["equipment_instances"].items()
            if record.get("location") == "bank" and record.get("item_name") == item_name
        ),
        key=lambda instance_id: (
            _clean_int(data["equipment_instances"][instance_id].get("condition"), 0),
            instance_id,
        ),
    )
    if amount <= 0 or len(candidates) < amount:
        return data
    for instance_id in candidates[:amount]:
        data["equipment_instances"].pop(instance_id, None)
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = max(0, _clean_int(inventory.get(item_name), 0) - amount)
    data["inventory"] = inventory
    return data
