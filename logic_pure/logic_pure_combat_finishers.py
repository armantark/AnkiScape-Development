"""Charged combat finisher reload consumption."""

from .logic_pure_state import _non_negative_int, _positive_int


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
