"""logic_pure_construction.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from .achievement_diary_events import record_direct_diary_event_pure

from .logic_pure_state import (  # noqa: F401  (re-export)
    COMBAT_BANK_RUN_REVIEWS,
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
    _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
    _COMBAT_STAT_POTION_BY_DOSE,
    _COMBAT_STAT_POTION_ITEM_NAMES,
    _build_combat_potion_dose_lookup,
    _combat_grave_items,
    _combat_stored_loadout,
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
    _positive_int,
    _requirements_from_spec,
    _sanitize_combat_bank_run,
    _sanitize_combat_grave_state,
    _sanitize_combat_supply_loadout,
    _sanitize_death_office_state,
    _signed_int,
    default_combat_supply_loadout_pure,
    quest_completed_pure,
    quest_state_pure,
    sanitize_quest_combat_active_encounters_pure,
)

from .logic_pure_state import (
    _copy_player_data_with_nested,
    _non_negative_int,
    _positive_int,
    quest_completed_pure,
)


_LECTERN_SLOTS = {
    "oak_lecturn": {11, 15},
    "eagle_lecturn": {11, 12, 13, 15},
    "demon_lecturn": {3, 8, 11, 15},
    "teak_eagle_lecturn": {2, 5, 11, 12, 13, 15},
    "teak_demon_lecturn": {3, 6, 7, 8, 10, 11, 15},
    "mahogany_eagle_lecturn": {2, 5, 12, 13, 14, 15, 16},
    "mahogany_demon_lecturn": {3, 4, 6, 7, 8, 9, 10, 11, 15},
}


def _construction_nail_stock(inventory, nail_data):
    return sum(_non_negative_int(inventory.get(name, 0), 0) for name in nail_data)


def _construction_has_workbench(flags, required_level, workbench_tiers):
    return any(level >= required_level and bool(flags.get(target_id)) for level, target_id in workbench_tiers)


def construction_target_locked_reasons_pure(player_data, target_id, construction_data, room_data, servant_data, nail_data, workbench_tiers):
    spec = construction_data.get(target_id)
    if not isinstance(spec, Mapping):
        return ("Unknown Construction target",)
    reasons = []
    if not bool(player_data.get("house_owned", False)):
        reasons.append("Purchase a house")
    rooms = player_data.get("house_rooms_bought", {}) or {}
    room = str(spec.get("room", ""))
    if room and not bool(rooms.get(room)):
        reasons.append(f"Buy {room_data.get(room, {}).get('display_name', room)}")
    inventory = player_data.get("inventory", {}) or {}
    flags = player_data.get("house_built_flags", {}) or {}
    if target_id.startswith("tablet_"):
        required_level = _positive_int(spec.get("magic_level", 1), 1)
        if _positive_int(player_data.get("magic_level", 1), 1) < required_level:
            reasons.append(f"Magic level {required_level}")
        slot = _positive_int(spec.get("lectern_component", 0), 0)
        if not any(bool(flags.get(lectern)) and slot in slots for lectern, slots in _LECTERN_SLOTS.items()):
            reasons.append("Build a compatible lectern")
    else:
        required_level = _positive_int(spec.get("level", 1), 1)
        effective_level = _positive_int(player_data.get("construction_level", 1), 1)
        if (not bool(spec.get("water")) and _non_negative_int(inventory.get("Crystal saw", 0), 0) > 0
                and quest_completed_pure(player_data, "the_eyes_of_glouphrie")):
            effective_level += 3
        if effective_level < required_level:
            reasons.append(f"Construction level {required_level}")
        if target_id.startswith("flatpack_") and not _construction_has_workbench(
            flags, _positive_int(spec.get("workbench_level", 17), 17), workbench_tiers
        ):
            reasons.append("Build the required workbench tier")
    for item, amount in (spec.get("requirements", {}) or {}).items():
        have = _construction_nail_stock(inventory, nail_data) if item == "Nails" else _non_negative_int(inventory.get(item, 0), 0)
        if have < _positive_int(amount, 1):
            reasons.append(f"{item} x{amount}")
    servant = str(player_data.get("house_servant", ""))
    if servant and bool(spec.get("requirements")) and not target_id.startswith("tablet_"):
        # Wages are paid once per servant-assisted review stint.
        wage = _positive_int(servant_data.get(servant, {}).get("wage", 0), 0)
        if _non_negative_int(inventory.get("Coins", 0), 0) < wage:
            reasons.append(f"Coins x{wage} servant wage")
    return tuple(reasons)


def _consume_construction_nails(inventory, amount, nail_data, rng):
    remaining = amount
    while remaining > 0:
        choice = next((name for name in reversed(tuple(nail_data)) if _non_negative_int(inventory.get(name, 0), 0) > 0), None)
        if choice is None:
            return False
        inventory[choice] = _non_negative_int(inventory.get(choice, 0), 0) - 1
        bend_rate = _positive_int(nail_data[choice].get("bend_rate", 1), 1)
        try:
            bent = float(rng()) < (1.0 / float(bend_rate + 1))
        except (TypeError, ValueError):
            bent = False
        if not bent:
            remaining -= 1
    return True


def apply_construction_action_pure(player_data, target_id, construction_data, servant_data, nail_data, rng):
    spec = construction_data.get(target_id)
    if not isinstance(spec, Mapping):
        return player_data, {}, False
    data = _copy_player_data_with_nested(player_data)
    inventory = dict(data.get("inventory", {}) or {})
    servant = str(data.get("house_servant", ""))
    requirements = spec.get("requirements", {}) or {}
    servant_assisted = bool(servant and requirements) and not target_id.startswith("tablet_")
    batch_size = _positive_int(servant_data.get(servant, {}).get("batch_size", 1), 1) if servant_assisted else 1
    if servant_assisted:
        wage = _positive_int(servant_data.get(servant, {}).get("wage", 0), 0)
        if _non_negative_int(inventory.get("Coins", 0), 0) < wage:
            return player_data, {}, False
        inventory["Coins"] = _non_negative_int(inventory.get("Coins", 0), 0) - wage
    completed = 0
    for _ in range(batch_size):
        enough = all(
            (_construction_nail_stock(inventory, nail_data) if item == "Nails" else _non_negative_int(inventory.get(item, 0), 0)) >= _positive_int(amount, 1)
            for item, amount in requirements.items()
        )
        if not enough:
            break
        before = dict(inventory)
        ok = True
        for item, amount in requirements.items():
            amount = _positive_int(amount, 1)
            if item == "Nails":
                ok = _consume_construction_nails(inventory, amount, nail_data, rng)
                if not ok: break
            else:
                inventory[item] = _non_negative_int(inventory.get(item, 0), 0) - amount
        if not ok:
            inventory = before
            break
        completed += 1
    if completed <= 0:
        return player_data, {}, False
    output_item = spec.get("output_item")
    outputs = {}
    if isinstance(output_item, str):
        inventory[output_item] = _non_negative_int(inventory.get(output_item, 0), 0) + completed
        outputs[output_item] = completed
        data["construction_outputs_created"] = _non_negative_int(data.get("construction_outputs_created", 0), 0) + completed
    data["inventory"] = inventory
    data["construction_actions_completed"] = _non_negative_int(data.get("construction_actions_completed", 0), 0) + completed
    if bool(spec.get("stateful")) and not target_id.startswith("flatpack_"):
        flags = dict(data.get("house_built_flags", {}) or {})
        flags[target_id] = True
        data["house_built_flags"] = flags
    skill = "magic" if target_id.startswith("tablet_") else "construction"
    return data, {skill: float(spec.get("xp", 0.0) or 0.0) * completed, "count": completed, "outputs": outputs}, True


def purchase_house_pure(player_data, price=1000):
    if bool(player_data.get("house_owned")):
        return player_data, False
    data = _copy_player_data_with_nested(player_data)
    inventory = dict(data.get("inventory", {}) or {})
    if _non_negative_int(inventory.get("Coins", 0), 0) < price:
        return player_data, False
    inventory["Coins"] -= price
    data["inventory"] = inventory
    data["house_owned"] = True
    data["house_rooms_bought"] = {**dict(data.get("house_rooms_bought", {}) or {}), "garden": True, "parlour": True}
    record_direct_diary_event_pure(data, True, "construction_command", action_id="purchase_house")
    return data, True


def purchase_house_option_pure(player_data, option_id, options, *, kind):
    spec = options.get(option_id)
    if not isinstance(spec, Mapping) or not bool(player_data.get("house_owned")):
        return player_data, False
    level = _positive_int(player_data.get("construction_level", 1), 1)
    if level < _positive_int(spec.get("level", 1), 1):
        return player_data, False
    quest_gate = spec.get("quest_gate")
    if quest_gate and not quest_completed_pure(player_data, str(quest_gate)):
        return player_data, False
    data = _copy_player_data_with_nested(player_data)
    inventory = dict(data.get("inventory", {}) or {})
    price = _positive_int(spec.get("price", 0), 0)
    if _non_negative_int(inventory.get("Coins", 0), 0) < price:
        return player_data, False
    inventory["Coins"] -= price
    data["inventory"] = inventory
    if kind == "room":
        rooms = dict(data.get("house_rooms_bought", {}) or {})
        if rooms.get(option_id): return player_data, False
        rooms[option_id] = True
        data["house_rooms_bought"] = rooms
        record_direct_diary_event_pure(data, True, "construction_command", action_id="purchase_room")
    elif kind == "servant":
        data["house_servant"] = option_id
    elif kind == "style":
        data["house_style"] = option_id
    return data, True


# Darkan BoneAltar.java Altar enum @ 3b47cfdf: base multipliers Oak 1.0,
# Teak 1.1, Cloth 1.25, Mahogany 1.5, Limestone 1.75, Marble 2.0, Gilded 2.5,
# +0.5 per lit burner capped at two. A chapel holds one altar; the highest
# tier built is the one standing.
_OWNED_ALTAR_TIERS = (
    "oak_altar", "teak_altar", "cloth_altar",
    "mahogany_altar", "limestone_altar", "marble_altar", "guilded_altar",
)

_OWNED_ALTAR_BASE_MULTIPLIERS = {
    "oak_altar": 1.0, "teak_altar": 1.1, "cloth_altar": 1.25,
    "mahogany_altar": 1.5, "limestone_altar": 1.75,
    "marble_altar": 2.0, "guilded_altar": 2.5,
}


def owned_altar_id_pure(player_data):
    flags = player_data.get("house_built_flags", {}) or {}
    return next((name for name in reversed(_OWNED_ALTAR_TIERS) if bool(flags.get(name))), None)


def owned_gilded_altar_burner_count_pure(player_data):
    rooms = player_data.get("house_rooms_bought", {}) or {}
    flags = player_data.get("house_built_flags", {}) or {}
    if not bool(player_data.get("house_owned")) or not bool(rooms.get("chapel")) or owned_altar_id_pure(player_data) is None:
        return 0
    return min(2, sum(bool(flags.get(name)) for name in ("inscence_burner", "mahogany_burner", "marble_burner")))


def owned_gilded_altar_effective_burners_pure(player_data, target_id=None):
    stint = player_data.get("prayer_owned_altar_stint", {}) or {}
    if isinstance(stint, Mapping) and target_id and stint.get("target_id") == target_id:
        return min(2, _non_negative_int(stint.get("burners_lit", 0), 0))
    return owned_gilded_altar_burner_count_pure(player_data)


def owned_gilded_altar_marrentill_required_pure(player_data, target_id):
    stint = player_data.get("prayer_owned_altar_stint", {}) or {}
    if isinstance(stint, Mapping) and stint.get("target_id") == target_id:
        return 0
    return owned_gilded_altar_burner_count_pure(player_data)


_OWNED_ALTAR_REASON_NAMES = {
    "oak_altar": "an oak altar",
    "teak_altar": "a teak altar",
    "cloth_altar": "a cloth-covered altar",
    "mahogany_altar": "a mahogany altar",
    "limestone_altar": "a limestone altar",
    "marble_altar": "a marble altar",
    "guilded_altar": "a gilded altar",
}


def owned_gilded_altar_access_reasons_pure(player_data, target_id):
    reasons = []
    rooms = player_data.get("house_rooms_bought", {}) or {}
    altar_id = owned_altar_id_pure(player_data)
    if not bool(player_data.get("house_owned")):
        reasons.append("a player-owned house")
    if not bool(rooms.get("chapel")):
        reasons.append("a Chapel")
    if altar_id is None:
        reasons.append(_OWNED_ALTAR_REASON_NAMES["oak_altar"])
    marrentill_required = owned_gilded_altar_marrentill_required_pure(player_data, target_id)
    if marrentill_required > 0:
        inventory = player_data.get("inventory", {}) or {}
        if _non_negative_int(inventory.get("Clean marrentill", 0), 0) < marrentill_required:
            reasons.append(f"Clean marrentill x{marrentill_required}")
    return tuple(reasons)


def effective_gilded_altar_multiplier_pure(player_data, mode, target_id=None):
    if mode == "hosted":
        return 3.5
    if mode == "owned":
        base = _OWNED_ALTAR_BASE_MULTIPLIERS.get(owned_altar_id_pure(player_data), 1.0)
        return base + 0.5 * owned_gilded_altar_effective_burners_pure(player_data, target_id)
    return 0.0
