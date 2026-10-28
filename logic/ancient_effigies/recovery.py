"""Dangerous-death settlement for carried items, effigies and held lamps.

The ordinary carried-pack behavior moved here from the Combat model unchanged.
The additions keep per-copy custody honest across a death: a held lamp is
carried without a Bank count, a lost effigy copy follows its own record to the
gravestone, and a second death moves the older gravestone's copies to Death's
Office before the new losses are marked, so two same-name copies never swap
their requests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...data.ancient_effigies.catalog import DRAGONKIN_LAMP_NAME, ITEM_IDS_BY_NAME
from ..inventory_pure import clamp_carried_view_to_bank
from .custody import INSTANCES_KEY, held_lamp_ids_pure, sorted_instance_ids


def _non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def _active_carried_view(data: Mapping[str, Any], target_id: Any) -> dict[str, int]:
    """What is actually in hand at death ({item: count}) — the carried view of the
    active target, i.e. the items from this trip. Combat defaults to its current
    enemy; other dangerous skills pass their own target explicitly.

    NOT the union of every target's view. `carried_inventory` keeps a saved pack per
    target, so a player who has trained Firemaking, Cooking, and Smithing has a
    dormant ~28-item pack sitting under each of those target ids. Draining all of
    them on a combat death both dropped materials from skills the player was not
    doing and staged more than 28 slots of items — more than one inventory can hold.
    A dormant pack is a loadout resting in the bank, not something you are carrying.
    """
    carried = data.get("carried_inventory")
    if not isinstance(carried, Mapping):
        return {}
    if target_id is None:
        target_id = data.get("current_combat_target")
    view = carried.get(target_id) if isinstance(target_id, str) else None
    if not isinstance(view, Mapping):
        return {}
    # Clamp to what the bank still holds. The view can outlive its items (discard,
    # shop sale, eating looted food), and graving more than existed would mint the
    # difference when the grave is reclaimed.
    return clamp_carried_view_to_bank(view, data.get("inventory"))


def carried_inventory_grave_counts(data: Mapping[str, Any], target_id: Any = None) -> dict[str, int]:
    """The active carried view, plus every held Dragonkin lamp counted once.

    A held lamp has no Bank count for a pack view to point at; its instance
    record is what the player carries, with or without an active pack.
    """
    counts = dict(_active_carried_view(data, target_id))
    counts.pop(DRAGONKIN_LAMP_NAME, None)
    held = len(held_lamp_ids_pure(data))
    if held:
        counts[DRAGONKIN_LAMP_NAME] = held
    return counts


def _rebuilt_instances(data: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    raw = data.get(INSTANCES_KEY)
    if not isinstance(raw, Mapping):
        return {}
    return {key: dict(value) if isinstance(value, Mapping) else value for key, value in raw.items()}


def _move_graved_records_to_office(data: dict[str, Any]) -> None:
    """A new gravestone pushes the old one's copies to Death's Office first."""
    instances = _rebuilt_instances(data)
    moved = False
    for record in instances.values():
        if isinstance(record, dict) and record.get("location") == "grave":
            record["location"] = "death_office"
            moved = True
    if moved:
        data[INSTANCES_KEY] = instances


def _lose_copies(data: dict[str, Any], item_name: str, location: str, lost: int, no_grave: bool) -> None:
    """Mark the first ``lost`` copies at ``location`` (numeric order) as lost."""
    item_id = ITEM_IDS_BY_NAME[item_name]
    instances = _rebuilt_instances(data)
    affected = [
        instance_id
        for instance_id in sorted_instance_ids(instances)
        if isinstance(instances[instance_id], dict)
        and instances[instance_id].get("item_id") == item_id
        and instances[instance_id].get("location") == location
    ][:lost]
    for instance_id in affected:
        if no_grave:
            del instances[instance_id]
        else:
            instances[instance_id]["location"] = "grave"
    if affected:
        data[INSTANCES_KEY] = instances


def _settle_held_lamps(data: dict[str, Any], count: int, protected: int, grave_items: list[str], no_grave: bool) -> None:
    """Held lamps leave custody without a Bank debit, so no zero entry is minted."""
    lost = count - protected
    if lost > 0:
        _lose_copies(data, DRAGONKIN_LAMP_NAME, "held", lost, no_grave)
        if not no_grave:
            grave_items.extend([DRAGONKIN_LAMP_NAME] * lost)


def _debit_carried_losses(data, carried_counts, protected_carried, grave_items, no_grave) -> None:
    # Only the active pack is carried; dormant target views remain bank loadouts.
    # Debit its lost units from the flat store before staging grave recovery.
    inventory = dict(data.get("inventory", {}) or {})
    for item_name, count in carried_counts.items():
        if item_name == DRAGONKIN_LAMP_NAME:
            continue
        lost = count - protected_carried.get(item_name, 0)
        if lost <= 0:
            continue
        inventory[item_name] = max(0, _non_negative_int(inventory.get(item_name, 0)) - lost)
        if item_name in ITEM_IDS_BY_NAME:
            _lose_copies(data, item_name, "bank", lost, no_grave)
        if not no_grave:
            grave_items.extend([item_name] * lost)
    data["inventory"] = inventory


def _drop_zero_lamp_entry(data: dict[str, Any]) -> None:
    """A lamp lives only in its record; a seeded zero Bank entry is removed."""
    inventory = data.get("inventory")
    if isinstance(inventory, Mapping) and DRAGONKIN_LAMP_NAME in inventory and not inventory[DRAGONKIN_LAMP_NAME]:
        data["inventory"] = {name: amount for name, amount in inventory.items() if name != DRAGONKIN_LAMP_NAME}


def _drop_active_carried_views(data: dict[str, Any], active_target: Any) -> None:
    if not isinstance(active_target, str):
        return
    for map_key in ("carried_inventory", "carried_churn"):
        container = data.get(map_key)
        if isinstance(container, Mapping) and active_target in container:
            container = dict(container)
            container.pop(active_target, None)
            data[map_key] = container


def settle_carried_death(data, carried_counts, protected_carried, grave_items, active_target, no_grave) -> None:
    """Debit the lost carried units, stage their recovery and drop the pack view.

    Runs before the Combat death moves the old gravestone's names to Death's
    Office, so the old copies' records move first and the new losses then take
    the gravestone.
    """
    if not no_grave:
        _move_graved_records_to_office(data)
    _drop_zero_lamp_entry(data)
    if carried_counts:
        _debit_carried_losses(data, carried_counts, protected_carried, grave_items, no_grave)
        held = carried_counts.get(DRAGONKIN_LAMP_NAME, 0)
        if held:
            _settle_held_lamps(data, held, protected_carried.get(DRAGONKIN_LAMP_NAME, 0), grave_items, no_grave)
    _drop_active_carried_views(data, active_target)
