"""One worn ammunition stack and Bank-backed rune packing."""

from ...data.combat.mechanics import COMBAT_RANGED_AMMO_DATA, COMBAT_RANGED_WEAPON_DATA
from ...logic.inventory_pure import carried_slots_used, clamp_carried_view_to_bank
from ...data.item_values import STACKABLE_ITEM_NAMES
from ...data.equipment_data import EQUIPMENT_DATA
from ..logic_pure_state import _non_negative_int


# PLACEHOLDER(ava_recovery_split): corroborate Darkan Ranged.kt with a period split.
AVA_RECOVERY = {"Ava's attractor": 0.60, "Ava's accumulator": 0.72, "Ava's alerter": 0.72}
AMMO_PICKUP_WITHOUT_AVA = 0.50  # Owner's Pass 21 balance rule, all fired shots.
# PLACEHOLDER(ava_incidental_interval): recover the exact period generation timer.
AVA_INCIDENTAL_TICKS = 300  # Period wiki estimate: one arrow per 180 seconds.


def equipped_ammo(data):
    name = (data.get("equipment") or {}).get("ammunition")
    return {name: max(0, int(data.get("equipment_ammunition_count", 1)))} if name else {}


def carried_items(data, target_id=None):
    target_id = target_id or data.get("current_combat_target", "chicken")
    view = (data.get("carried_inventory") or {}).get(target_id, {})
    return clamp_carried_view_to_bank(view, data.get("inventory") or {})


def carried_runes(data, target_id=None):
    return {name: count for name, count in carried_items(data, target_id).items() if name.endswith(" rune")}


def best_ammo(data, compatible, equipment_data, *, check_levels=True):
    def allowed(name):
        spec = equipment_data[name]
        requirements = spec.skill_requirements or ((spec.combat_skill, spec.required_level),)
        return all(int(data.get(f"{skill}_level", 1)) >= level for skill, level in requirements)
    inventory = data.get("inventory") or {}
    return max((name for name in compatible if inventory.get(name, 0) > 0 and (not check_levels or allowed(name))),
               key=lambda name: (COMBAT_RANGED_AMMO_DATA.get(name, {}).get("ranged_strength", 0), name), default=None)


def refill_ammo(data, weapon_spec, equipment_data):
    if not weapon_spec:
        return
    equipment = dict(data.get("equipment") or {})
    inventory = dict(data.get("inventory") or {})
    compatible = weapon_spec.get("compatible_ammo", ())
    current = equipment.get("ammunition")
    count = equipped_ammo(data).get(current, 0)
    stock = dict(inventory)
    if current:
        stock[current] = stock.get(current, 0) + count
    available = {**data, "inventory": stock}
    manual = data.get("equipment_ammunition_manual", "")
    name = best_ammo(available, (manual,) if manual in compatible else (), equipment_data)
    if not name:
        data["equipment_ammunition_manual"] = ""
        name = best_ammo(available, compatible, equipment_data)
    if not name:
        return
    if current and current != name:
        inventory[current] = inventory.get(current, 0) + count
        count = 0
    count += inventory.get(name, 0)
    inventory[name] = 0
    equipment["ammunition"] = name
    data.update(inventory=inventory, equipment=equipment, equipment_ammunition_count=count)


def pack_runes(data, rune_cost, supply_slots):
    target = data.get("current_combat_target", "chicken")
    view = carried_items(data, target)
    inventory = data.get("inventory") or {}
    custom = (data.get("carried_advanced_targets") or {}).get(target)
    layout = (data.get("carried_layout") or {}).get(target, {})
    for name in rune_cost:
        if custom and name not in layout:
            continue
        if name not in view and carried_slots_used(view, STACKABLE_ITEM_NAMES) + supply_slots >= 28:
            break
        if inventory.get(name, 0) > 0:
            view[name] = min(inventory[name], layout.get(name, inventory[name])) if custom else inventory[name]
    data["carried_inventory"] = {**(data.get("carried_inventory") or {}), target: view}


def consume_runes(data, rune_cost):
    view = carried_items(data)
    if any(view.get(name, 0) < amount for name, amount in rune_cost.items()):
        return None
    inventory = dict(data.get("inventory") or {})
    for name, amount in rune_cost.items():
        inventory[name] -= amount
        view[name] -= amount
        if view[name] <= 0:
            view.pop(name)
    target = data.get("current_combat_target", "chicken")
    data.update(inventory=inventory, carried_inventory={**(data.get("carried_inventory") or {}), target: view})
    return dict(rune_cost)


def consume_ammo(data, weapon_spec, target_id, rng):
    name = (data.get("equipment") or {}).get("ammunition")
    count = equipped_ammo(data).get(name, 0)
    if name not in (weapon_spec or {}).get("compatible_ammo", ()) or count <= 0:
        return None
    cape = (data.get("equipment") or {}).get("cape")
    recovery = AVA_RECOVERY.get(cape, AMMO_PICKUP_WITHOUT_AVA)
    if rng() >= recovery:
        count -= 1
    data["equipment_ammunition_count"] = count
    if count <= 0:
        data["equipment"] = dict(data.get("equipment") or {})
        data["equipment"].pop("ammunition", None)
    return name


def generate_ava_items(data, ticks, supply_slots=0):
    cape = (data.get("equipment") or {}).get("cape")
    if cape not in AVA_RECOVERY or not data.get("combat_ava_incidental_items", True):
        return
    elapsed = int(data.get("combat_ava_incidental_ticks", 0)) + ticks
    count, data["combat_ava_incidental_ticks"] = divmod(elapsed, AVA_INCIDENTAL_TICKS)
    if count:
        name = "Iron arrows" if cape == "Ava's attractor" else "Steel arrows"
        if name in equipped_ammo(data):
            data["equipment_ammunition_count"] += count
            return
        view = carried_items(data)
        if name not in view and carried_slots_used(view, STACKABLE_ITEM_NAMES) + supply_slots >= 28:
            return
        inventory = dict(data.get("inventory") or {})
        inventory[name] = inventory.get(name, 0) + count
        view[name] = view.get(name, 0) + count
        target = data.get("current_combat_target", "chicken")
        data.update(inventory=inventory, carried_inventory={**(data.get("carried_inventory") or {}), target: view})


def migrate_ammunition(data, equipment_data, version):
    """Remove the two retired balances before the normal sanitizer sees them."""
    if version >= 127:
        return
    loadout = dict(data.get("combat_supply_loadout") or {})
    inventory = dict(data.get("inventory") or {})
    ammo = loadout.pop("ammo", {})
    runes = loadout.pop("runes", {})
    for items in (ammo, runes):
        inventory = return_legacy_items(inventory, items)
    data.update(inventory=inventory, combat_supply_loadout=loadout)
    if (data.get("equipment") or {}).get("ammunition") and not data.get("equipment_ammunition_count"):
        data["equipment_ammunition_count"] = 1
    migrate_equipped_ammo(data, ammo, inventory, equipment_data)


def sanitize_ammunition_state(data):
    count = data.get("equipment_ammunition_count", int(bool((data.get("equipment") or {}).get("ammunition"))))
    manual = data.get("equipment_ammunition_manual")
    return {
        "equipment_ammunition_count": _non_negative_int(count, 0),
        "equipment_ammunition_manual": manual if isinstance(manual, str) and manual in COMBAT_RANGED_AMMO_DATA else "",
        "combat_ava_incidental_items": bool(data.get("combat_ava_incidental_items", True)),
        "combat_ava_incidental_ticks": _non_negative_int(data.get("combat_ava_incidental_ticks", 0), 0),
    }


def equipment_slot_text(data, slot, name):
    count = f" ×{equipped_ammo(data).get(name, 0):,}" if slot.id == "ammunition" else ""
    manual = " Manual" if slot.id == "ammunition" and data.get("equipment_ammunition_manual") else ""
    return f"{slot.label}: {name}{count}{manual}"


def return_legacy_items(inventory, items):
    return {**inventory, **{name: inventory.get(name, 0) + max(0, int(count)) for name, count in items.items()}}


def migrate_equipped_ammo(data, ammo, inventory, equipment_data):
    weapon = (data.get("equipment") or {}).get("weapon")
    spec = COMBAT_RANGED_WEAPON_DATA.get(weapon, {})
    name = best_ammo(data, tuple(name for name in ammo if name in spec.get("compatible_ammo", ())), equipment_data)
    if name in spec.get("compatible_ammo", ()):
        # Select using legacy balances only; unrelated Bank stacks stay banked.
        old = (data.get("equipment") or {}).get("ammunition")
        count = equipped_ammo(data).get(old, 0)
        if old:
            inventory[old] = inventory.get(old, 0) + count
        data["equipment"] = {**(data.get("equipment") or {}), "ammunition": name}
        data["equipment_ammunition_count"] = ammo[name] + (count if old == name else 0)
        inventory[name] -= data["equipment_ammunition_count"]


def combat_target_pack_move_pure(data, target):
    packs = dict(data.get("carried_inventory") or {})
    previous = data.get("current_combat_target")
    if previous != target and previous in packs:
        packs[target] = packs.pop(previous)
    return {"current_combat_target": target, "carried_inventory": packs}
