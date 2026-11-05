"""Reclaim worn equipment while preserving ammunition stack quantities."""


def reclaim_items(data, items, loadout, stack_extras=None):
    remaining = list(items)
    equipment = dict(data.get("equipment") or {})
    for slot, name in loadout.items():
        if not equipment.get(slot) and name in remaining:
            remaining.remove(name)
            equipment[slot] = name
            if slot == "ammunition":
                data["equipment_ammunition_count"] = 1
    inventory = dict(data.get("inventory") or {})
    for name in remaining:
        inventory[name] = inventory.get(name, 0) + 1
    for name, count in (stack_extras or {}).items():
        if equipment.get("ammunition") == name:
            data["equipment_ammunition_count"] = int(data.get("equipment_ammunition_count", 1)) + count
        else:
            inventory[name] = inventory.get(name, 0) + count
    data.update(inventory=inventory, equipment=equipment)


def lost_ammo_extras(data, lost_equipment):
    name = lost_equipment.get("ammunition")
    if not name:
        return {}
    count = max(0, int(data.get("equipment_ammunition_count", 1)))
    data["equipment_ammunition_count"] = 0
    return {name: count - 1} if count > 1 else {}


def merge_stack_extras(*stores):
    result = {}
    for store in stores:
        for name, count in (store or {}).items():
            result[name] = result.get(name, 0) + count
    return result
