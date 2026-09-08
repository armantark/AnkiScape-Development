"""Combat food availability and consumption."""

from typing import Mapping

from ..data.combat_data import COMBAT_FOOD_DATA
from .logic_pure_state import (
    _non_negative_int,
    _positive_int,
    _sanitize_combat_supply_loadout,
)


_DEFAULT_COMBAT_AUTO_EAT_FOOD = (
    "Shark",
    "Monkfish",
    "Swordfish",
    "Bass",
    "Lobster",
    "Tuna",
    "Salmon",
    "Pike",
    "Trout",
    "Cod",
    "Mackerel",
    "Herring",
    "Cooked meat",
    "Cooked chicken",
    "Sardine",
    "Shrimps",
    "Crayfish",
)


def _combat_loaded_food_count(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = loadout.get("food", {}) or {}
    total = 0
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if isinstance(item_name, str):
            total += _non_negative_int(food_loadout.get(item_name, 0), 0)
    return total


def _combat_banked_auto_food_count(data):
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    total = 0
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if isinstance(item_name, str) and item_name in COMBAT_FOOD_DATA:
            total += _non_negative_int(inventory.get(item_name, 0), 0)
    return total


def _combat_auto_eat_food_available(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = loadout.get("food", {}) or {}
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if item_name in COMBAT_FOOD_DATA and _positive_int(food_loadout.get(item_name, 0), 0) > 0:
            return True
    return False


def _combat_preview_food_available(player_data, active_encounter):
    loadout = _sanitize_combat_supply_loadout(
        player_data.get("combat_supply_loadout")
    )
    bank_inventory = player_data.get("inventory", {}) or {}
    for item_name in player_data.get(
        "combat_auto_eat_food", _DEFAULT_COMBAT_AUTO_EAT_FOOD
    ):
        if item_name not in COMBAT_FOOD_DATA:
            continue
        loadout_count = _non_negative_int(
            (loadout.get("food", {}) or {}).get(item_name, 0), 0
        )
        bank_count = (
            0
            if active_encounter
            else _non_negative_int(bank_inventory.get(item_name, 0), 0)
        )
        if loadout_count + bank_count > 0:
            return True
    return False


def _combat_consume_auto_food(data, current_lifepoints, max_lifepoints, rng):
    threshold_percent = _positive_int(data.get("combat_auto_eat_threshold_percent", 40), 40)
    threshold = max(1, int(max_lifepoints * threshold_percent / 100.0))
    if current_lifepoints > threshold or current_lifepoints >= max_lifepoints:
        return current_lifepoints, None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = dict(loadout.get("food", {}) or {})
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        food = COMBAT_FOOD_DATA.get(item_name)
        if not food or _positive_int(food_loadout.get(item_name, 0), 0) <= 0:
            continue
        food_loadout[item_name] = _positive_int(food_loadout.get(item_name, 0), 0) - 1
        if food_loadout[item_name] <= 0:
            food_loadout.pop(item_name, None)
        loadout["food"] = food_loadout
        data["combat_supply_loadout"] = loadout
        healed_by = _positive_int(food.get("heal_lifepoints", 0), 0)
        maximum = max_lifepoints + _positive_int(
            food.get("max_overheal_lifepoints", 0),
            0,
        )
        return min(maximum, current_lifepoints + healed_by), {
            "item": item_name,
            "healed_by": healed_by,
        }
    return current_lifepoints, None
