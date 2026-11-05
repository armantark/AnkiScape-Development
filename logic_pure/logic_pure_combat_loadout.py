"""Prepare a target's pack, preset and starting ammunition, then gate its bank travel.

This module can read the combat model and supplies together while the engine
keeps encounter rolls separate from target preparation.
"""

from typing import Mapping

from .logic_pure_combat_model import apply_combat_preset_pure, apply_combat_target_overrides_pure
from .logic_pure_combat_supplies import (
    _combat_custom_layout_view, _combat_refill_ranged_ammo_loadout,
    _combat_locks_can_bank_run, _combat_progress_or_start_bank_run, _combat_relevant_potion_items,
)
from .logic_pure_combat_model import (
    _combat_ranged_weapon_spec, combat_target_locked_reasons_pure,
    _positive_int, COMBAT_BURST_TICKS, COMBAT_ATTACK_STYLE_DATA, DEFAULT_COMBAT_ATTACK_STYLE,
    combat_attack_style_for_equipment_pure, _sanitize_combat_supply_loadout,
)
from .combat.ammunition import equipped_ammo, carried_runes, EQUIPMENT_DATA


def _combat_prepare_target_loadout(data, target_id):
    """Restore an empty carried pack before applying the target's preset, so
    overrides see the same pack as an already active encounter."""
    carried = data.get("carried_inventory")
    current_view = carried.get(target_id) if isinstance(carried, Mapping) else None
    if not isinstance(current_view, Mapping) or not current_view:
        repacked = _combat_custom_layout_view(data, target_id)
        if repacked:
            carried = dict(carried) if isinstance(carried, Mapping) else {}
            carried[target_id] = repacked
            data["carried_inventory"] = carried
    return _combat_target_loadout(data, target_id)


def _combat_target_loadout(data, target_id):
    pinned_preset = (data.get("combat_target_presets", {}) or {}).get(target_id)
    if isinstance(pinned_preset, str):
        return apply_combat_preset_pure(data, pinned_preset, target_id)[0]
    return apply_combat_target_overrides_pure(data, target_id)


def combat_start_ammo_values_pure(player_data, target_id, *, allow_bank_run=True):
    """Ready an empty slot at target selection, without bypassing a fight's bank trip."""
    if not allow_bank_run or equipped_ammo(player_data) or player_data.get("combat_bank_run"):
        return {}
    encounter = player_data.get("combat_encounter") or {}
    if encounter.get("target_id") == target_id:
        return {}
    data = {**player_data, "current_combat_target": target_id}
    _name, _equipment, weapon = _combat_ranged_weapon_spec(data, EQUIPMENT_DATA)
    _combat_refill_ranged_ammo_loadout(data, weapon)
    if not equipped_ammo(data):
        return {}
    return {key: data[key] for key in ("inventory", "equipment", "equipment_ammunition_count", "equipment_ammunition_manual")}


def _combat_bank_window(
    data, target_id, combat_class, ranged_weapon_spec, spell_spec,
    equipment_data, enemy_data, ticks, allow_bank_run, locked_reasons,
):
    ticks = _positive_int(ticks, COMBAT_BURST_TICKS)
    if not allow_bank_run or not _combat_locks_can_bank_run(locked_reasons):
        return 0, ticks, None, locked_reasons
    result = _combat_progress_or_start_bank_run(
        data, target_id, combat_class, ranged_weapon_spec, spell_spec,
        equipment_data, enemy_data, ticks=ticks,
    )
    if result is None:
        return 0, ticks, None, locked_reasons
    spent = result["ticks_elapsed"]
    if not result["bank_run_completed"] or spent >= ticks:
        return spent, ticks, result, ()
    reasons = combat_target_locked_reasons_pure(data, target_id, enemy_data, equipment_data=equipment_data)
    return spent, ticks - spent, None, reasons


def combat_supply_loadout_summary_pure(player_data, equipment_data=None):
    loadout = _sanitize_combat_supply_loadout(player_data.get("combat_supply_loadout"))
    style = COMBAT_ATTACK_STYLE_DATA.get(
        combat_attack_style_for_equipment_pure(player_data, equipment_data or {}),
        COMBAT_ATTACK_STYLE_DATA[DEFAULT_COMBAT_ATTACK_STYLE],
    )
    combat_class = str(style.get("combat_class", "melee"))
    relevant_stat_potions = set(_combat_relevant_potion_items(combat_class))
    stat_potions = {
        item_name: amount
        for item_name, amount in loadout["stat_potions"].items()
        if item_name in relevant_stat_potions
    }
    return {
        "food_loaded_items": dict(loadout["food"]),
        "potions_loaded": sum(loadout["potions"].values()),
        "potions_loaded_items": dict(loadout["potions"]),
        "stat_potions_loaded": sum(stat_potions.values()),
        "stat_potions_loaded_items": stat_potions,
        "ammo_equipped": equipped_ammo(player_data),
        "runes_carried": {name: count for name, count in carried_runes(player_data).items() if name.endswith(" rune")} if combat_class == "magic" else {},
        "finishers_loaded": dict(loadout["finishers"]),
        "hazards_loaded": dict(loadout["hazards"]),
        "cannonballs_loaded": loadout["cannonballs"],
    }
