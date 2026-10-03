"""Charged combat finisher consumption, and the finisher wording the
review HUD, the combat menu and the target row share."""

from .logic_pure_state import _non_negative_int, _positive_int


def _combat_consume_finisher_charge(data, finisher, charge_items, loadout, finishers):
    for index, (charged_item, _charges) in enumerate(charge_items):
        current = _non_negative_int(finishers.get(charged_item, 0), 0)
        if current <= 0:
            continue
        if current == 1:
            finishers.pop(charged_item, None)
        else:
            finishers[charged_item] = current - 1
        replacement = (
            charge_items[index + 1][0]
            if index + 1 < len(charge_items)
            else str(finisher.get("empty_item", "") or "")
        )
        if replacement:
            finishers[replacement] = (
                _non_negative_int(finishers.get(replacement, 0), 0) + 1
            )
        loadout["finishers"] = finishers
        data["combat_supply_loadout"] = loadout
        return True
    return _combat_reload_and_consume_finisher(
        data, finisher, charge_items, loadout, finishers
    )


def _combat_reload_and_consume_finisher(data, finisher, charge_items, loadout, finishers):
    empty_item = str(finisher.get("empty_item", "") or "")
    reload_item = str(finisher.get("reload_item", "") or "")
    empty_count = _non_negative_int(finishers.get(empty_item, 0), 0)
    reload_count = _non_negative_int(finishers.get(reload_item, 0), 0)
    if empty_count <= 0 or reload_count <= 0:
        return False
    if empty_count == 1:
        finishers.pop(empty_item, None)
    else:
        finishers[empty_item] = empty_count - 1
    if reload_count == 1:
        finishers.pop(reload_item, None)
    else:
        finishers[reload_item] = reload_count - 1
    replacement_charges = max(
        0, _positive_int(finisher.get("reload_charges", 0), 0) - 1
    )
    replacement = next(
        (
            charged_item
            for charged_item, charges in charge_items
            if charges == replacement_charges
        ),
        empty_item,
    )
    if replacement:
        finishers[replacement] = (
            _non_negative_int(finishers.get(replacement, 0), 0) + 1
        )
    loadout["finishers"] = finishers
    data["combat_supply_loadout"] = loadout
    return True


def combat_finisher_notice_pure(finisher):
    """The finisher prompt once the target is low enough for it. A worn
    finisher asks to be worn, not loaded: Gelatinous abomination oldid 6079671,
    "The gauntlets must be worn, not just in inventory"."""
    if not finisher["ready"]:
        return ""
    if finisher["available"]:
        return f"Finisher ready: {finisher['action_label']}"
    if finisher["worn"]:
        return f"Wear {finisher['item']} to finish"
    return f"Finisher blocked: no loaded {finisher['item']}"


def combat_finisher_tooltip_pure(finisher):
    if finisher["available"]:
        if finisher["charged"]:
            return (
                "Spends one Fungicide spray charge and preserves the remaining "
                "dose. A loaded Fungicide canister automatically refills an "
                "empty spray."
            )
        verb = "Consumes one" if finisher["consumable"] else "Uses the reusable"
        return f"{verb} {finisher['item']} and finishes the enemy."
    if finisher["ready"]:
        return (
            f"Wear {finisher['item']} to finish the enemy."
            if finisher["worn"]
            else f"No {finisher['item']} is loaded in the combat pack."
        )
    return f"Available at 1–{finisher['threshold_lifepoints']} enemy LP."


def combat_finisher_supply_pure(finisher):
    if finisher["charged"]:
        return (
            f"{finisher['charges']} spray charges + "
            f"{finisher['reloads']} canister reloads"
        )
    if finisher["worn"]:
        return "worn" if finisher["item_count"] else "not worn"
    return f"{finisher['item_count']} loaded"
