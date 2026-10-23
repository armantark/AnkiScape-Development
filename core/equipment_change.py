"""Save changes behind the Equipment panel's Equip and Unequip actions."""

from ..data.equipment_condition_data import EQUIPMENT_CONDITION_DATA
from ..logic.equipment_instance_logic import (
    sanitize_equipment_instance_state_pure,
    sync_equipment_instances_pure,
)
from ..logic_pure.logic_pure import (
    can_equip_item_pure,
    equip_item_pure,
    reconcile_combat_method_pure,
    unequip_item_pure,
)
from .constants import EQUIPMENT_DATA


def _save_after_move(current, move):
    new_inventory, new_equipment, moved = move
    if not moved:
        return dict(current), False
    before_equipment = dict(current.get("equipment", {}) or {})
    updated = dict(current)
    updated["inventory"] = new_inventory
    updated["equipment"] = new_equipment
    updated.update(
        sync_equipment_instances_pure(updated, before_equipment, EQUIPMENT_CONDITION_DATA)
    )
    if before_equipment.get("weapon") != new_equipment.get("weapon"):
        updated, _ok, _reason = reconcile_combat_method_pure(current, updated, EQUIPMENT_DATA)
    return updated, moved


def equip_item_save_pure(player_data, item_name):
    """Return `(save, equipped)` after moving one Bank item into its slot."""
    if item_name == 'Spirit shield' and can_equip_item_pure(item_name, EQUIPMENT_DATA, player_data)[0] is False:
        return dict(player_data), False
    return _save_after_move(
        player_data,
        equip_item_pure(
            item_name,
            player_data.get("inventory", {}) or {},
            player_data.get("equipment", {}) or {},
            EQUIPMENT_DATA,
        ),
    )


def unequip_slot_save_pure(player_data, slot):
    """Return `(save, unequipped)` after moving one slot's item back to the Bank."""
    return _save_after_move(
        player_data,
        unequip_item_pure(
            slot,
            player_data.get("inventory", {}) or {},
            player_data.get("equipment", {}) or {},
        ),
    )


def return_ineligible_spirit_shield_save_pure(player_data):
    """Return an ineligible worn Spirit shield to the Bank exactly once."""
    equipment = player_data.get("equipment", {}) or {}
    if equipment.get("shield") != 'Spirit shield':
        return dict(player_data), False
    if can_equip_item_pure('Spirit shield', EQUIPMENT_DATA, player_data)[0]:
        return dict(player_data), False
    inventory, equipment, changed = unequip_item_pure(
        'shield', player_data.get("inventory", {}) or {}, equipment,
    )
    updated = dict(player_data)
    updated["inventory"] = inventory
    updated["equipment"] = equipment
    return updated, changed


def sanitize_equipment_conditions_save_pure(player_data):
    """Normalize loaded per-copy conditions using the equipment condition catalog."""
    updated = dict(player_data)
    updated.update(sanitize_equipment_instance_state_pure(player_data, EQUIPMENT_CONDITION_DATA))
    return updated
