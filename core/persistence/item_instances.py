"""Per-copy item custody: equipment condition instances and Ancient Effigies.

Storage defaults and load sanitation compose both ledgers here, so the
oversized migration body only calls one name for each.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from copy import deepcopy
from typing import Any

from ...data.ancient_effigies.catalog import DRAGONKIN_LAMP_NAME
from ...logic.ancient_effigies.custody import (
    INSTANCES_KEY,
    NEXT_ID_KEY,
    default_effigy_custody_state_pure,
    synchronize_effigy_custody_pure,
)
from ...logic.bank_layout_logic import reconcile_bank_layout_for_player_pure
from ...logic.equipment_instance_logic import (
    default_equipment_instance_state_pure,
    sanitize_equipment_instance_state_pure,
)


_SYNCHRONIZED_KEYS = ("inventory", "carried_inventory", INSTANCES_KEY, NEXT_ID_KEY)


def bank_storage_keys_pure(item_definitions: Iterable[Any]) -> list[str]:
    """Registered storage keys a new or loaded Bank seeds at zero.

    A Dragonkin lamp is only ever a custody record, so no Bank is seeded with
    a lamp entry that custody would then have to remove on every load.
    """
    return [item.storage_key for item in item_definitions if item.storage_key != DRAGONKIN_LAMP_NAME]


def default_item_instance_state_pure() -> dict[str, Any]:
    return {**default_equipment_instance_state_pure(), **default_effigy_custody_state_pure()}


def sanitize_item_instance_state_pure(
    data: Mapping[str, Any], condition_data: Mapping[str, Mapping[str, Any]]
) -> dict[str, Any]:
    """Reconcile equipment instances, then effigy and lamp custody.

    Adopting a legacy lamp unit empties its Bank count, so the Bank layout is
    reconciled again and a reload finds no slot left for it.
    """
    synchronized = synchronize_effigy_custody_pure(
        sanitize_equipment_instance_state_pure(data, condition_data)
    )
    if synchronized.get("inventory") != data.get("inventory"):
        synchronized = reconcile_bank_layout_for_player_pure(synchronized)
    return synchronized


def synchronize_live_item_instances(player_data: dict[str, Any]) -> None:
    """Bring the live save's effigy custody up to date before it is written.

    Any producer that credited an effigy by name gets its copy identity here,
    through the ordinary save. Only the custody keys of the live record change.
    """
    synchronized = synchronize_effigy_custody_pure(player_data)
    for key in _SYNCHRONIZED_KEYS:
        if key in synchronized and synchronized[key] != player_data.get(key):
            player_data[key] = synchronized[key]


def persist_adopted_item_instances(
    latest_record: Any,
    player_data: Mapping[str, Any],
    save: Callable[[dict[str, Any]], None],
) -> bool:
    """Save identities and seeds adopted on load before any window can show them.

    Patches only the two custody keys, and the removal of an adopted lamp's
    Bank unit, into a copy of the latest stored record. Every other raw field
    keeps its stored form.
    """
    if not isinstance(latest_record, Mapping) or not latest_record:
        return False
    patch: dict[str, Any] = {}
    defaults = default_effigy_custody_state_pure()
    for key in (INSTANCES_KEY, NEXT_ID_KEY):
        if latest_record.get(key, defaults[key]) != player_data.get(key):
            patch[key] = deepcopy(player_data.get(key))
    raw_inventory = latest_record.get("inventory")
    live_inventory = player_data.get("inventory")
    if (
        isinstance(raw_inventory, Mapping)
        and raw_inventory.get(DRAGONKIN_LAMP_NAME, 0) != 0
        and isinstance(live_inventory, Mapping)
        and not live_inventory.get(DRAGONKIN_LAMP_NAME, 0)
    ):
        patch["inventory"] = {
            name: deepcopy(amount) for name, amount in raw_inventory.items() if name != DRAGONKIN_LAMP_NAME
        }
    if not patch:
        return False
    record = deepcopy(dict(latest_record))
    record.update(patch)
    save(record)
    return True
