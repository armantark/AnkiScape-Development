"""Shared stage item parsing and tool custody for quest admission."""

from typing import Iterable, Mapping

from ...core.tool_belt import tool_on_belt
from ..logic_pure_state import _positive_int
from ..quest_action_proofs import record_quest_stage_action_proofs_pure
from ...data.quest.stage_overrides.members.later.creature_of_fenkenstrain import (
    CREATURE_OF_FENKENSTRAIN_STAGE_ADDITIONS,
    CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION,
)


def _quest_stage_item_pairs(requirement, key):
    raw_items = requirement.get(key, {}) if isinstance(requirement, Mapping) else {}
    if isinstance(raw_items, Mapping):
        return tuple((str(name), _positive_int(amount, 1)) for name, amount in raw_items.items())
    if isinstance(raw_items, Iterable) and not isinstance(raw_items, str):
        pairs = []
        for item in raw_items:
            if isinstance(item, Mapping):
                name = item.get("item_name") or item.get("display_name")
                amount = item.get("quantity", item.get("amount", 1))
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                name, amount = item[0], item[1]
            else:
                continue
            if isinstance(name, str):
                pairs.append((name, _positive_int(amount, 1)))
        return tuple(pairs)
    return tuple()

def _quest_stage_item_option_groups(requirement, key):
    raw_groups = requirement.get(key, ()) if isinstance(requirement, Mapping) else ()
    if isinstance(raw_groups, Mapping):
        return (_quest_stage_item_pairs({key: raw_groups}, key),)
    if not isinstance(raw_groups, Iterable) or isinstance(raw_groups, str):
        return tuple()
    raw_groups = tuple(raw_groups)
    if raw_groups and all(isinstance(raw_group, Mapping) for raw_group in raw_groups):
        pairs = tuple(
            (str(name), _positive_int(amount, 1))
            for raw_group in raw_groups
            for name, amount in raw_group.items()
        )
        return (pairs,) if pairs else tuple()
    groups = []
    for raw_group in raw_groups:
        if isinstance(raw_group, Mapping):
            pairs = tuple((str(name), _positive_int(amount, 1)) for name, amount in raw_group.items())
        elif isinstance(raw_group, Iterable) and not isinstance(raw_group, str):
            pairs = []
            for option in raw_group:
                if isinstance(option, Mapping):
                    pairs.extend((str(name), _positive_int(amount, 1)) for name, amount in option.items())
                elif isinstance(option, (tuple, list)) and len(option) >= 2:
                    pairs.append((str(option[0]), _positive_int(option[1], 1)))
            pairs = tuple(pairs)
        else:
            pairs = tuple()
        if pairs:
            groups.append(pairs)
    return tuple(groups)

def _quest_stage_strings(requirement, key):
    raw_values = requirement.get(key, ()) if isinstance(requirement, Mapping) else ()
    if isinstance(raw_values, str):
        return (raw_values,)
    if isinstance(raw_values, Iterable):
        return tuple(str(value) for value in raw_values if str(value))
    return tuple()

_GENERIC_TOOL_SUFFIXES = {"pickaxe": ("pickaxe",), "hatchet": ("hatchet", " axe"), "axe": ("hatchet", " axe")}

def _has_quest_tool(player_data, tool_name, amount):
    inventory = player_data.get("inventory", {}) or {}
    # The belt holds one of each tool; a stage asking for several wants stock.
    if inventory.get(tool_name, 0) >= amount or (amount == 1 and tool_on_belt(player_data, tool_name)):
        return True
    equipment = player_data.get("equipment", {}) or {}
    if isinstance(equipment, Mapping) and tool_name in {str(item_name) for item_name in equipment.values()}:
        return True
    suffixes = _GENERIC_TOOL_SUFFIXES.get(tool_name.lower())
    return bool(suffixes) and any(
        str(name).lower().endswith(suffixes) and count >= amount for name, count in inventory.items()
    )


def apply_fenkenstrain_stage_two_items_pure(data):
    """Validate every ordered step privately before installing inventory or deeds."""
    inventory = dict(data["inventory"])
    for step in CREATURE_OF_FENKENSTRAIN_STAGE_TWO_TRANSACTION:
        needed = step["required_inventory"] + step["consumed_inventory"]
        if any(_positive_int(inventory.get(name, 0), 0) < amount for name, amount in needed):
            return False
        for name, amount in step["consumed_inventory"]:
            inventory[name] = _positive_int(inventory.get(name, 0), 0) - amount
        for name, amount in step["produced_inventory"]:
            inventory[name] = _positive_int(inventory.get(name, 0), 0) + amount
    data["inventory"] = inventory
    record_quest_stage_action_proofs_pure(
        data, "creature_of_fenkenstrain", CREATURE_OF_FENKENSTRAIN_STAGE_ADDITIONS[0].auto_actions,
    )
    return True


def consume_stage_rows_pure(data, quest_id, requirements, item_pairs, option_groups, stage_strings, positive_int):
    """Commit ordinary rows with their existing option, repeatable and proof semantics."""
    inventory = data["inventory"]
    for requirement in requirements:
        record_quest_stage_action_proofs_pure(data, quest_id, stage_strings(requirement, "auto_actions"))
        for item_name, amount in item_pairs(requirement, "consumed_inventory"):
            inventory[item_name] = max(0, positive_int(inventory.get(item_name, 0), 0) - amount)
        for options in option_groups(requirement, "consumed_inventory_options"):
            selected = next(filter(lambda pair: positive_int(inventory.get(pair[0], 0), 0) >= pair[1], options), None)
            if selected is not None:
                item_name, amount = selected
                inventory[item_name] = max(0, positive_int(inventory.get(item_name, 0), 0) - amount)
        if bool(requirement.get("repeatable_until_consumed")):
            continue
        for item_name, amount in item_pairs(requirement, "produced_inventory"):
            inventory[item_name] = positive_int(inventory.get(item_name, 0), 0) + amount
    return True
