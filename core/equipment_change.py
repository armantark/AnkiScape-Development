"""Save changes behind the Equipment panel's Equip and Unequip actions."""

from ..logic_pure.logic_pure_equipment import (
    equip_item_pure, unequip_item_pure, save_equipment_move_pure,
    prepare_quest_equipment_pure as _prepare_quest_equipment_pure,
    restore_quest_equipment_pure as _restore_quest_equipment_pure,
    release_quest_equipment_pure,
)
from .constants import EQUIPMENT_DATA


def equip_item_save_pure(player_data, item_name):
    """Return `(save, equipped)` after moving a Bank item or ammunition stack into its slot."""
    if item_name == (player_data.get("equipment") or {}).get("ammunition"):
        inventory = dict(player_data.get("inventory") or {})
        count = int(player_data.get("equipment_ammunition_count", 1)) + inventory.get(item_name, 0)
        inventory[item_name] = 0
        return {**player_data, "inventory": inventory, "equipment_ammunition_count": count}, True
    return save_equipment_move_pure(
        player_data,
        equip_item_pure(item_name, player_data.get("inventory", {}) or {},
                        player_data.get("equipment", {}) or {}, EQUIPMENT_DATA),
        EQUIPMENT_DATA,
    )


def unequip_slot_save_pure(player_data, slot):
    """Return `(save, unequipped)` after moving a worn item or ammunition stack back to the Bank."""
    return save_equipment_move_pure(
        player_data,
        unequip_item_pure(slot, player_data.get("inventory", {}) or {},
                          player_data.get("equipment", {}) or {}),
        EQUIPMENT_DATA,
    )


def prepare_quest_equipment_pure(player_data, quest_id, quest_data):
    return _prepare_quest_equipment_pure(player_data, quest_id, quest_data, EQUIPMENT_DATA)


def restore_quest_equipment_pure(player_data, *, force=False):
    return _restore_quest_equipment_pure(player_data, EQUIPMENT_DATA, force=force)
