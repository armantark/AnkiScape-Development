"""Atomic consumed-lure handling for persistent Combat encounters."""

from __future__ import annotations

from collections.abc import Mapping

from .logic_pure_state import _non_negative_int, _positive_int


def _consumed_lure_item(enemy):
    lure = enemy.get("lure")
    if not isinstance(lure, Mapping) or not lure.get("consumed"):
        return ""
    return str(lure.get("item", "") or "")


def combat_required_item_locked_reasons_pure(player_data, enemy, active_encounter):
    required_items = dict(enemy.get("required_items", {}) or {})
    inventory = dict(player_data.get("inventory", {}) or {})
    ignored_item = _consumed_lure_item(enemy) if active_encounter else ""
    required_items.pop(ignored_item, None)
    missing = tuple(
        str(item_name)
        for item_name, amount in required_items.items()
        if _non_negative_int(inventory.get(item_name, 0), 0) < max(1, _positive_int(amount, 1))
    )
    if not missing:
        return ()
    label = str(enemy.get("required_items_label", "") or "")
    return (label,) if label else tuple(f"{item_name} x1" for item_name in missing)


def consume_combat_lure_on_start_pure(data, enemy, active_encounter):
    item_name = _consumed_lure_item(enemy)
    if not item_name:
        return False
    if active_encounter:
        return True
    inventory = dict(data.get("inventory", {}) or {})
    inventory[item_name] = _non_negative_int(inventory.get(item_name, 0), 0) - 1
    data["inventory"] = inventory
    return True


def prepare_combat_lure_encounter_pure(data, enemy, target_id, stop_after_first_kill):
    encounter = data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    stop_after_first_kill |= consume_combat_lure_on_start_pure(data, enemy, active_encounter)
    return encounter, active_encounter, stop_after_first_kill
