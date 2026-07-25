"""logic_pure_combat_supplies.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..logic.inventory_pure import CARRIED_CAPACITY, apply_carried_layout_pure, carried_slots_used, clamp_carried_view_to_bank

try:
    from ..data.item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
except ImportError:  # values not generated in this checkout
    ITEM_VALUES = {}
    STACKABLE_ITEM_NAMES = frozenset()

from ..data.potion_data import POTION_FAMILIES, potion_dose_name, potion_flask_name

from ..data.prayer_passive_data import (
    BONECRUSHER_ITEM_NAME,
    ECTOPLASMATOR_ITEM_NAME,
    ECTOPLASMATOR_XP_BY_ENEMY_ID,
)
from ..data.urn_data import (
    MAX_NONEMPTY_URNS_PER_SKILL,
    URN_CARRIED_TARGET_KEYS,
    URN_TIERS_BY_FULL_ITEM,
    URN_TIERS_BY_ID,
    URN_TIERS_BY_SKILL,
    materialize_urn_layout_pure,
    sanitize_urn_state_pure,
    urn_action_event_pure,
    urn_tier_accepts_event_pure,
)

from ..data.combat_data import (
    COMBAT_ATTACK_STYLE_DATA,
    COMBAT_ANTIPOISON_POTION_DATA,
    COMBAT_BURST_TICKS,
    COMBAT_ENEMY_DATA,
    COMBAT_FOOD_DATA,
    CONSUMABLE_DATA,
    KEBAB_DRAINABLE_SKILLS,
    COMBAT_MAGIC_STAFF_DATA,
    COMBAT_MAGIC_SPELL_DATA,
    COMBAT_RANGED_AMMO_DATA,
    COMBAT_RANGED_WEAPON_DATA,
    DEFAULT_COMBAT_ATTACK_STYLE,
    DEFAULT_COMBAT_SPELL,
    DEFAULT_COMBAT_TARGET,
    MAGIC_FORMULA_SOURCE_PATH,
    MAGIC_STRATEGY_SOURCE_PATH,
    MELEE_FORMULA_SOURCE_PATH,
    MELEE_STRATEGY_SOURCE_PATH,
    POTION_TYPE_SOURCE_PATH,
    RANGED_FORMULA_SOURCE_PATH,
    RANGED_STRATEGY_SOURCE_PATH,
    WEAPON_TYPE_ATTACK_STYLES,
    WEAPON_TYPE_UNARMED_STYLES,
)

from ..logic_pure.logic_pure_combat_model import (  # noqa: F401  (re-export)
    COMBAT_DEATH_OFFICE_RECLAIM_COINS_PER_ITEM,
    COMBAT_ENEMY_ATTACK_STYLES,
    COMBAT_FOOD_LOADOUT_CAPACITY,
    COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
    COMBAT_POISON_NPC_ATTACK_CHANCE,
    COMBAT_POISON_SOURCE_PATH,
    COMBAT_POISON_TICK_DELAY,
    COMBAT_POISON_TIMER_SOURCE_PATH,
    COMBAT_PRESET_FIELDS,
    COMBAT_REST_FULL_HEAL_REVIEWS,
    COMBAT_SPECIAL_ATTACK_MAX_ENERGY,
    COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS,
    COMBAT_STAT_DRAIN_RECOVERY_TICKS,
    NATURAL_COMBAT_RECOVERY_LIFEPOINTS,
    SAFE_COMBAT_RECOVERY_LIFEPOINTS,
    SAFE_COMBAT_RECOVERY_TICKS,
    _COMBAT_AFFECTABLE_SKILLS,
    _COMBAT_ANTIPOISON_SLOT_CAP,
    _COMBAT_DEFAULT_PACK_MODE,
    _COMBAT_DRAGONFIRE_POTION_SLOT_CAP,
    _COMBAT_DRAINABLE_SKILLS,
    _COMBAT_FOOD_CAP_BY_MODE,
    _COMBAT_MAGIC_EQUIPMENT_TYPES,
    _COMBAT_MELEE_STYLE_IDS,
    _COMBAT_MELEE_STYLE_TYPES,
    _COMBAT_POTION_FLASK_CAP_BY_MODE,
    _COMBAT_RANGED_STYLE_IDS,
    _COMBAT_VALID_PACK_MODES,
    _COMBAT_XP_MODE_TO_STYLE_ID,
    _DEFAULT_COMBAT_AUTO_EAT_FOOD,
    _carried_inventory_grave_counts,
    _combat_accuracy,
    _combat_apply_follower_death,
    _combat_apply_magic_xp,
    _combat_apply_pvm_death,
    _combat_apply_triple_charm_reward,
    _combat_apply_unprotected_stat_drains,
    _combat_apply_wilderness_ambush,
    _combat_apply_wilderness_death,
    _combat_apply_xp,
    _combat_attack_bonus_from_totals,
    _combat_banked_hazard_count,
    _combat_base_skill_level,
    _combat_cap_damage_for_finisher,
    _combat_coerce_pack_mode,
    _combat_consume_auto_food,
    _combat_consume_hazard_dose,
    _combat_consume_loaded_finisher,
    _combat_death_office_items,
    _combat_defence_bonus_from_totals,
    _combat_drop_requirements_met,
    _combat_effective_player_attack_level,
    _combat_effective_player_defence_level,
    _combat_effective_player_magic_level,
    _combat_effective_player_ranged_level,
    _combat_effective_player_strength_level,
    _combat_effective_rune_cost_pure,
    _combat_effective_skill_level,
    _combat_enemy_attack_class,
    _combat_enemy_attack_style,
    _combat_enemy_bonuses,
    _combat_enemy_max_hit_old_hp,
    _combat_enemy_protection_class,
    _combat_environmental_hazard_spec,
    _combat_equipped_item_count,
    _combat_equipped_weapon_name,
    _combat_finisher_charge_items,
    _combat_finisher_spec,
    _combat_food_slot_cap,
    _combat_hazard_dose_items,
    _combat_loaded_finisher_charge_state,
    _combat_loaded_finisher_count,
    _combat_loaded_hazard_count,
    _combat_magic_locked_reasons,
    _combat_magic_max_hit_old_hp,
    _combat_magic_missing_runes,
    _combat_magic_rune_count,
    _combat_melee_max_hit_old_hp,
    _combat_npc_xp_multiplier,
    _combat_pending_supplemental_magic_costs_pure,
    _combat_potion_flask_cap,
    _combat_preset_snapshot,
    _combat_protective_equipment_state,
    _combat_ranged_ammo_count,
    _combat_ranged_locked_reasons,
    _combat_ranged_max_hit_old_hp,
    _combat_ranged_weapon_spec,
    _combat_reclaim_items_to_player,
    _combat_required_rune_cost_pure,
    _combat_resolve_melee_slot,
    _combat_restricted_weapon_locked_reasons,
    _combat_roll_drop_table,
    _combat_roll_drops,
    _combat_selected_magic_spell,
    _combat_selected_ranged_ammo,
    _combat_slot_drop_quantity,
    _combat_spellbook_swap_applies_pure,
    _combat_start_equipment_state,
    _combat_supplemental_rune_cost_pure,
    _combat_unprotected_damage_lifepoints,
    _combat_weakening_equipment_state,
    _combat_weapon_equipment_type,
    _combat_weapon_is_magic,
    _combat_weapon_is_ranged,
    _combat_weapon_type_id,
    _sanitize_combat_current_levels,
    _sanitize_combat_recovery_progress,
    _sanitize_combat_status_effects,
    _set_combat_death_office_items,
    apply_combat_finisher_pure,
    apply_combat_preset_pure,
    apply_combat_stat_delta_pure,
    apply_combat_target_overrides_pure,
    charged_god_spell_max_hit_bonus_pure,
    combat_attack_style_for_equipment_pure,
    combat_enemy_current_lifepoints_pure,
    combat_enemy_drop_item_names_pure,
    combat_finisher_state_pure,
    combat_magic_preset_locked_reasons_pure,
    combat_max_lifepoints_pure,
    combat_melee_attack_type_pure,
    combat_staff_covered_runes_pure,
    combat_target_locked_reasons_pure,
    combat_weapon_attack_style_slots_pure,
    combat_wilderness_equipment_risk_pure,
    default_combat_state_pure,
    derive_casual_combat_magic_pure,
    sanitize_combat_state_pure,
    save_combat_preset_pure,
)

from ..logic_pure.logic_pure_prayer import (  # noqa: F401  (re-export)
    CASTLE_WARS_HALO_DRAIN_PRAYERS,
    _highest_legal_prayer_candidate_pure,
    active_prayer_selection_pure,
    apply_prayer_action_pure,
    apply_prayer_selection_pure,
    clear_prayer_gilded_stint_pure,
    curse_expected_ramp_pure,
    prayer_drain_and_effective_uptime_pure,
    prayer_drain_for_ticks_pure,
    prayer_effect_state_pure,
    prayer_gilded_search_step_pure,
    prayer_selection_locked_reasons_pure,
    prayer_target_locked_reasons_pure,
    prayer_uptime_fraction_pure,
    sanitize_prayer_selection_pure,
)

from ..logic_pure.logic_pure_equipment import (  # noqa: F401  (re-export)
    _combat_level_key,
    _combat_skill_label,
    _equipment_bonus_value,
    _equipment_bonuses,
    _equipment_skill_requirements,
    _equipment_value,
    _mage_arena_god_for_item,
    _normalized_equipment_slot,
    _toolbelt_ids,
    best_mining_pickaxe_pure,
    best_woodcutting_axe_pure,
    can_equip_item_pure,
    equip_item_pure,
    equipment_bonus_state_pure,
    equipment_stat_totals_pure,
    unequip_item_pure,
)

from ..logic_pure.logic_pure_state import (  # noqa: F401  (re-export)
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

from ..logic_pure.logic_pure_combat_model import (
    COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
    COMBAT_POISON_SOURCE_PATH,
    COMBAT_POISON_TICK_DELAY,
    COMBAT_SPECIAL_ATTACK_MAX_ENERGY,
    COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS,
    COMBAT_STAT_DRAIN_RECOVERY_TICKS,
    _COMBAT_ANTIPOISON_SLOT_CAP,
    _COMBAT_DRAGONFIRE_POTION_SLOT_CAP,
    _combat_banked_hazard_count,
    _combat_base_skill_level,
    _combat_effective_rune_cost_pure,
    _combat_effective_skill_level,
    _combat_environmental_hazard_spec,
    _combat_finisher_charge_items,
    _combat_finisher_spec,
    _combat_food_slot_cap,
    _combat_hazard_dose_items,
    _combat_loaded_finisher_count,
    _combat_loaded_hazard_count,
    _combat_potion_flask_cap,
    _combat_required_rune_cost_pure,
    _combat_selected_ranged_ammo,
    _sanitize_combat_current_levels,
    _sanitize_combat_recovery_progress,
    _sanitize_combat_status_effects,
    apply_combat_stat_delta_pure,
    combat_max_lifepoints_pure,
    sanitize_combat_state_pure,
)

from ..logic_pure.logic_pure_prayer import (
    active_prayer_selection_pure,
    prayer_effect_state_pure,
)

from ..logic_pure.logic_pure_equipment import (
    _equipment_bonus_value,
)

from ..logic_pure.logic_pure_state import (
    COMBAT_BANK_RUN_REVIEWS,
    _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
    _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
    _COMBAT_STAT_POTION_BY_DOSE,
    _copy_player_data_with_nested,
    _non_negative_int,
    _positive_int,
    _sanitize_combat_bank_run,
    _sanitize_combat_supply_loadout,
)


def _combat_void_shifter_escape_ready(data, lifepoints, maximum):
    state = data.get("summoning_state", {}) or {}
    follower = state.get("active_follower", {}) or {}
    return bool(
        follower.get("kind") == "familiar"
        and follower.get("entity_id") == "voidshifter"
        and 0 < lifepoints < maximum * 0.10
    )


def _combat_refill_food_loadout(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = dict(loadout.get("food", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    # Food is capped by the packing mode's slot allocation (food is unstackable,
    # so count == slots); the freed slots leave room for damage potions.
    food_cap = _combat_food_slot_cap(data)
    loaded_food = sum(_non_negative_int(amount, 0) for amount in food_loadout.values())
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if loaded_food >= food_cap:
            break
        if item_name not in COMBAT_FOOD_DATA:
            continue
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0:
            continue
        take = min(available, food_cap - loaded_food)
        inventory[item_name] = available - take
        food_loadout[item_name] = _non_negative_int(food_loadout.get(item_name, 0), 0) + take
        loaded_food += take
    loadout["food"] = {item: amount for item, amount in food_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


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


def _combat_loaded_ranged_ammo(data, weapon_spec):
    if not isinstance(weapon_spec, Mapping):
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    ammo_loadout = loadout.get("ammo", {}) or {}
    for ammo_name in weapon_spec.get("compatible_ammo", ()) or ():
        if isinstance(ammo_name, str) and _non_negative_int(ammo_loadout.get(ammo_name, 0), 0) > 0:
            return ammo_name
    return None


def _combat_banked_ranged_ammo_count(data, weapon_spec):
    if not isinstance(weapon_spec, Mapping):
        return 0
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    total = 0
    for ammo_name in weapon_spec.get("compatible_ammo", ()) or ():
        if isinstance(ammo_name, str):
            total += _non_negative_int(inventory.get(ammo_name, 0), 0)
    return total


def _combat_missing_loaded_runes(data, rune_cost):
    if not isinstance(rune_cost, Mapping) or not rune_cost:
        return {}
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    rune_loadout = loadout.get("runes", {}) or {}
    missing = {}
    for rune_name, amount in rune_cost.items():
        if not isinstance(rune_name, str):
            continue
        required = _positive_int(amount, 0)
        loaded = _non_negative_int(rune_loadout.get(rune_name, 0), 0)
        if required > loaded:
            missing[rune_name] = required - loaded
    return missing


def _combat_bank_has_runes(data, missing_runes):
    if not missing_runes:
        return False
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return False
    return all(_non_negative_int(inventory.get(rune_name, 0), 0) >= amount for rune_name, amount in missing_runes.items())


def _combat_loaded_antipoison_count(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    return sum(
        _non_negative_int(amount, 0)
        for item_name, amount in (loadout.get("potions", {}) or {}).items()
        if item_name in COMBAT_ANTIPOISON_POTION_DATA
    )


def _combat_banked_antipoison_count(data):
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    return sum(_non_negative_int(inventory.get(item_name, 0), 0) for item_name in COMBAT_ANTIPOISON_POTION_DATA)


def _combat_loaded_dragonfire_potion_count(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    return sum(
        _non_negative_int(amount, 0)
        for item_name, amount in (loadout.get("potions", {}) or {}).items()
        if item_name in _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES
    )


def _combat_banked_dragonfire_potion_count(data):
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        return 0
    return sum(
        _non_negative_int(inventory.get(item_name, 0), 0)
        for item_name in _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES
    )


def _combat_custom_layout_view(data, target_id):
    if not isinstance(target_id, str):
        return {}
    advanced = data.get("carried_advanced_targets")
    layouts = data.get("carried_layout")
    if not isinstance(advanced, Mapping) or not advanced.get(target_id) or not isinstance(layouts, Mapping):
        return {}
    layout = layouts.get(target_id)
    if not isinstance(layout, Mapping):
        return {}
    return apply_carried_layout_pure(
        data.get("inventory", {}) or {},
        materialize_urn_layout_pure(data.get("inventory", {}) or {}, layout),
        CARRIED_CAPACITY,
        STACKABLE_ITEM_NAMES,
    )


def _combat_refill_finisher_loadout(data, enemy):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    inventory = dict(data.get("inventory", {}) or {})
    for loaded_item, amount in (loadout.get("finishers", {}) or {}).items():
        inventory[loaded_item] = (
            _non_negative_int(inventory.get(loaded_item, 0), 0)
            + _non_negative_int(amount, 0)
        )
    finishers = {}
    finisher = _combat_finisher_spec(enemy)
    if finisher is not None and finisher.get("must_be_worn"):
        loadout["finishers"] = finishers
        data["inventory"] = inventory
        data["combat_supply_loadout"] = loadout
        return
    item_name = (
        str(finisher.get("item", "") or "")
        if finisher is not None
        else ""
    )
    charge_items = _combat_finisher_charge_items(finisher)
    if charge_items:
        selected_item = ""
        for charged_item, _charges in charge_items:
            available = _non_negative_int(inventory.get(charged_item, 0), 0)
            if available <= 0:
                continue
            inventory[charged_item] = available - 1
            selected_item = charged_item
            break
        empty_item = str(finisher.get("empty_item", "") or "")
        reload_item = str(finisher.get("reload_item", "") or "")
        if (
            not selected_item
            and empty_item
            and reload_item
            and _non_negative_int(inventory.get(empty_item, 0), 0) > 0
            and _non_negative_int(inventory.get(reload_item, 0), 0) > 0
        ):
            inventory[empty_item] = _non_negative_int(
                inventory.get(empty_item, 0), 0
            ) - 1
            inventory[reload_item] = _non_negative_int(
                inventory.get(reload_item, 0), 0
            ) - 1
            reload_charges = _positive_int(finisher.get("reload_charges", 0), 0)
            selected_item = next(
                (
                    charged_item
                    for charged_item, charges in charge_items
                    if charges == reload_charges
                ),
                "",
            )
        if selected_item:
            finishers[selected_item] = 1
        loadout["finishers"] = finishers
        data["inventory"] = inventory
        data["combat_supply_loadout"] = loadout
        if selected_item and reload_item:
            remaining_slots = max(
                0, CARRIED_CAPACITY - _combat_supply_slots_used(data)
            )
            available_reloads = _non_negative_int(
                inventory.get(reload_item, 0), 0
            )
            take_reloads = min(available_reloads, remaining_slots)
            if take_reloads > 0:
                inventory[reload_item] = available_reloads - take_reloads
                finishers[reload_item] = take_reloads
                loadout["finishers"] = finishers
                data["inventory"] = inventory
                data["combat_supply_loadout"] = loadout
        return
    available = _non_negative_int(inventory.get(item_name, 0), 0)
    if available > 0:
        take = available if bool(finisher.get("consume", False)) else 1
        inventory[item_name] = available - take
        finishers[item_name] = take
    loadout["finishers"] = finishers
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_banked_finisher_count(data, enemy):
    finisher = _combat_finisher_spec(enemy)
    if finisher is None:
        return 0
    item_name = str(finisher.get("item", "") or "")
    inventory = data.get("inventory", {}) or {}
    charge_items = _combat_finisher_charge_items(finisher)
    if charge_items and isinstance(inventory, Mapping):
        charges = sum(
            _non_negative_int(inventory.get(charged_item, 0), 0) * charge_count
            for charged_item, charge_count in charge_items
        )
        empty_item = str(finisher.get("empty_item", "") or "")
        reload_item = str(finisher.get("reload_item", "") or "")
        banked_tools = sum(
            _non_negative_int(inventory.get(charged_item, 0), 0)
            for charged_item, _charges in charge_items
        ) + _non_negative_int(inventory.get(empty_item, 0), 0)
        loadout = _sanitize_combat_supply_loadout(
            data.get("combat_supply_loadout")
        )
        loaded_finishers = loadout.get("finishers", {}) or {}
        loaded_tools = sum(
            _non_negative_int(loaded_finishers.get(charged_item, 0), 0)
            for charged_item, _charges in charge_items
        ) + _non_negative_int(loaded_finishers.get(empty_item, 0), 0)
        reloads = (
            _non_negative_int(inventory.get(reload_item, 0), 0)
            if reload_item and banked_tools + loaded_tools > 0
            else 0
        )
        return charges + reloads * _positive_int(
            finisher.get("reload_charges", 0), 0
        )
    return (
        _non_negative_int(inventory.get(item_name, 0), 0)
        if isinstance(inventory, Mapping)
        else 0
    )


def _combat_refill_hazard_loadout(data, enemy):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    inventory = dict(data.get("inventory", {}) or {})
    for item_name, amount in (loadout.get("hazards", {}) or {}).items():
        inventory[item_name] = (
            _non_negative_int(inventory.get(item_name, 0), 0)
            + _non_negative_int(amount, 0)
        )
    supplies = {}
    hazard = _combat_environmental_hazard_spec(enemy)
    dose_items = _combat_hazard_dose_items(hazard)
    remaining_slots = (
        _positive_int(hazard.get("loadout_cap", 1), 1)
        if hazard is not None
        else 0
    )
    for item_name in dose_items:
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0 or remaining_slots <= 0:
            continue
        take = min(available, remaining_slots)
        supplies[item_name] = take
        inventory[item_name] = available - take
        remaining_slots -= take
    loadout["hazards"] = supplies
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_trim_food_to_capacity(data):
    """Keep mandatory supplies while returning excess food to the bank."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    excess_slots = max(0, _combat_supply_slots_used(data) - CARRIED_CAPACITY)
    if excess_slots <= 0:
        return
    food = dict(loadout.get("food", {}) or {})
    inventory = dict(data.get("inventory", {}) or {})
    preferred = [
        item_name
        for item_name in data.get("combat_auto_eat_food", ()) or ()
        if isinstance(item_name, str)
    ]
    removal_order = list(reversed(preferred))
    removal_order.extend(
        item_name for item_name in reversed(tuple(food)) if item_name not in preferred
    )
    for item_name in removal_order:
        if excess_slots <= 0:
            break
        loaded = _non_negative_int(food.get(item_name, 0), 0)
        if loaded <= 0:
            continue
        returned = min(loaded, excess_slots)
        remaining = loaded - returned
        if remaining > 0:
            food[item_name] = remaining
        else:
            food.pop(item_name, None)
        inventory[item_name] = (
            _non_negative_int(inventory.get(item_name, 0), 0) + returned
        )
        excess_slots -= returned
    loadout["food"] = food
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_carried_slot_counts(data, target_id):
    """Return ``(all carried slots, depositable loot slots)`` for one target."""
    if not isinstance(target_id, str):
        return 0, 0
    carried = data.get("carried_inventory")
    view = carried.get(target_id) if isinstance(carried, Mapping) else None
    if not isinstance(view, Mapping):
        return 0, 0
    view = clamp_carried_view_to_bank(view, data.get("inventory"))
    depositable = dict(view)
    for item_name, baseline_count in _combat_custom_layout_view(data, target_id).items():
        remaining = _non_negative_int(depositable.get(item_name, 0), 0) - _non_negative_int(baseline_count, 0)
        if remaining > 0:
            depositable[item_name] = remaining
        else:
            depositable.pop(item_name, None)
    return (
        carried_slots_used(view, STACKABLE_ITEM_NAMES),
        carried_slots_used(depositable, STACKABLE_ITEM_NAMES),
    )


def _combat_deposit_loot(data, target_id):
    """Deposit loot, then repack the target's saved Custom carried layout."""
    if not isinstance(target_id, str):
        return
    carried = dict(data.get("carried_inventory", {}) or {})
    repacked = _combat_custom_layout_view(data, target_id)
    if repacked:
        carried[target_id] = repacked
    else:
        carried.pop(target_id, None)
    data["carried_inventory"] = carried


def _combat_refill_context_supplies(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data=None, enemy_data=None):
    # Owner-settled AnkiScape rule: every completed bank run includes a free
    # altar stop, restoring the internal level*10 Prayer point pool.
    data["combat_prayer_points"] = _positive_int(data.get("prayer_level", 1), 1) * 10
    data["combat_prayer_drain_counter"] = 0.0
    summoning_state = dict(data.get("summoning_state", {}) or {})
    summoning_state["summoning_points_current"] = _positive_int(
        data.get("summoning_level", 1), 1
    )
    data["summoning_state"] = summoning_state
    _combat_refill_food_loadout(data)
    _combat_refill_stat_potions(data, combat_class)
    enemy_lookup = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_lookup.get(target_id, {}) if isinstance(target_id, str) and isinstance(enemy_lookup, Mapping) else {}
    _combat_refill_finisher_loadout(data, enemy)
    _combat_refill_dragonfire_loadout(data, enemy)
    target_poison = _positive_int(enemy.get("poison_damage", 0), 0) if isinstance(enemy, Mapping) else 0
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if target_poison > 0 or "poison" in effects:
        _combat_refill_antipoison_loadout(data)
    if combat_class == "ranged":
        _combat_refill_ranged_ammo_loadout(data, ranged_weapon_spec)
    rune_cost = _combat_required_rune_cost_pure(data, combat_class, spell_spec, equipment_data)
    if rune_cost:
        _combat_refill_magic_rune_loadout(data, rune_cost)
    _combat_refill_hazard_loadout(data, enemy)
    _combat_trim_food_to_capacity(data)
    # The same bank trip deposits accumulated loot (owner: loot banks alongside
    # supply depletion).
    _combat_deposit_loot(data, target_id)


def _combat_bank_run_needed(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data=None, enemy_data=None):
    # One 28-slot inventory: supplies (food/potions/ammo/runes) and loot share it,
    # so a bank run is forced when together they fill it. As food is eaten the
    # freed slots become loot room, exactly like a real inventory.
    #
    # Guard: only *loot* is deposited by a bank run, so with nothing to deposit a
    # full inventory cannot be relieved by banking. Requiring loot here means an
    # over-budget supply loadout can never softlock combat into a permanent
    # bank-run loop (it would refill the same supplies and re-trigger forever).
    carried_slots, loot_slots = _combat_carried_slot_counts(data, target_id)
    if loot_slots > 0 and _combat_supply_slots_used(data) + carried_slots >= CARRIED_CAPACITY:
        return True
    if _combat_loaded_food_count(data) <= 0 and _combat_banked_auto_food_count(data) > 0:
        return True
    enemy_lookup = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_lookup.get(target_id, {}) if isinstance(target_id, str) and isinstance(enemy_lookup, Mapping) else {}
    if (
        isinstance(enemy, Mapping)
        and isinstance(enemy.get("dragonfire"), Mapping)
        and _combat_loaded_dragonfire_potion_count(data) <= 0
        and _combat_banked_dragonfire_potion_count(data) > 0
        and _non_negative_int(
            data.get("combat_antifire_ticks_remaining", 0), 0
        )
        <= 0
        and _non_negative_int(
            data.get("combat_super_antifire_ticks_remaining", 0), 0
        )
        <= 0
    ):
        return True
    finisher = _combat_finisher_spec(enemy)
    if finisher is not None:
        item_name = str(finisher.get("item", "") or "")
        if (
            not finisher.get("must_be_worn")
            and _combat_loaded_finisher_count(data, item_name, finisher) <= 0
            and _combat_banked_finisher_count(data, enemy) > 0
        ):
            return True
    hazard = _combat_environmental_hazard_spec(enemy)
    if (
        hazard is not None
        and _combat_loaded_hazard_count(data, hazard) <= 0
        and _combat_banked_hazard_count(data, hazard) > 0
    ):
        return True
    target_poison = _positive_int(enemy.get("poison_damage", 0), 0) if isinstance(enemy, Mapping) else 0
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if (target_poison > 0 or "poison" in effects) and _combat_loaded_antipoison_count(data) <= 0:
        if _combat_banked_antipoison_count(data) > 0:
            return True
    if combat_class == "ranged":
        return _combat_loaded_ranged_ammo(data, ranged_weapon_spec) is None and _combat_banked_ranged_ammo_count(data, ranged_weapon_spec) > 0
    rune_cost = _combat_required_rune_cost_pure(data, combat_class, spell_spec, equipment_data)
    if rune_cost:
        missing_runes = _combat_missing_loaded_runes(data, rune_cost)
        return _combat_bank_has_runes(data, missing_runes)
    return False


def _combat_try_pack_yak_winter_storage(
    data,
    target_id,
    combat_class,
    ranged_weapon_spec,
    spell_spec,
    equipment_data=None,
    enemy_data=None,
):
    state = data.get("summoning_state", {}) or {}
    follower = state.get("active_follower", {}) or {}
    if (
        not isinstance(state, Mapping)
        or follower.get("kind") != "familiar"
        or follower.get("entity_id") != "packyak"
        or _non_negative_int(
            state.get("special_move_points_current", 0), 0
        ) < 12
    ):
        return False
    policy = (state.get("target_policies", {}) or {}).get(target_id, {}) or {}
    priority = policy.get("winter_storage_priority", ())
    if isinstance(priority, str):
        priority = (priority,)
    if not isinstance(priority, Iterable):
        return False
    carried_root = data.get("carried_inventory", {}) or {}
    carried = (
        carried_root.get(target_id, {})
        if isinstance(carried_root, Mapping)
        else {}
    )
    if not isinstance(carried, Mapping):
        return False
    scroll_name = "Winter storage scroll"
    if _non_negative_int(carried.get(scroll_name, 0), 0) <= 0:
        return False
    depositable = dict(carried)
    for item_name, baseline in _combat_custom_layout_view(data, target_id).items():
        remaining = _non_negative_int(
            depositable.get(item_name, 0), 0
        ) - _non_negative_int(baseline, 0)
        if remaining > 0:
            depositable[item_name] = remaining
        else:
            depositable.pop(item_name, None)
    selected = next(
        (
            item_name
            for item_name in priority
            if isinstance(item_name, str)
            and item_name != scroll_name
            and _non_negative_int(depositable.get(item_name, 0), 0) > 0
            and (
                item_name not in STACKABLE_ITEM_NAMES
                or _non_negative_int(carried.get(item_name, 0), 0) == 1
            )
        ),
        None,
    )
    if selected is None:
        return False
    candidate = _copy_player_data_with_nested(data)
    candidate_carried_root = dict(candidate.get("carried_inventory", {}) or {})
    candidate_carried = dict(candidate_carried_root.get(target_id, {}) or {})
    candidate_carried[selected] -= 1
    if candidate_carried[selected] <= 0:
        candidate_carried.pop(selected, None)
    candidate_carried[scroll_name] -= 1
    if candidate_carried[scroll_name] <= 0:
        candidate_carried.pop(scroll_name, None)
    candidate_carried_root[target_id] = candidate_carried
    candidate["carried_inventory"] = candidate_carried_root
    inventory = dict(candidate.get("inventory", {}) or {})
    inventory[scroll_name] = max(
        0, _non_negative_int(inventory.get(scroll_name, 0), 0) - 1
    )
    candidate["inventory"] = inventory
    candidate_state = dict(candidate.get("summoning_state", {}) or {})
    candidate_state["special_move_points_current"] = (
        _non_negative_int(
            candidate_state.get("special_move_points_current", 0), 0
        )
        - 12
    )
    candidate["summoning_state"] = candidate_state
    if _combat_bank_run_needed(
        candidate,
        target_id,
        combat_class,
        ranged_weapon_spec,
        spell_spec,
        equipment_data,
        enemy_data,
    ):
        return False
    candidate["summoning_exp"] = float(
        candidate.get("summoning_exp", 0.0) or 0.0
    ) + 4.8
    candidate_state["event_log"] = (
        list(candidate_state.get("event_log", []))
        + [
            {
                "kind": "winter_storage",
                "target_id": target_id,
                "item": selected,
                "xp": 4.8,
            }
        ]
    )[-50:]
    data.clear()
    data.update(candidate)
    return True


def _combat_bank_run_result(data, target_id, started=False, completed=False):
    bank_run = _sanitize_combat_bank_run(data.get("combat_bank_run"))
    return {
        "reason": "combat_bank_run",
        "target_id": target_id,
        "display_name": COMBAT_ENEMY_DATA.get(target_id, {}).get("display_name", target_id)
        if isinstance(target_id, str)
        else "",
        "bank_run_started": bool(started),
        "bank_run_completed": bool(completed),
        "bank_run_reviews_remaining": _non_negative_int(bank_run.get("reviews_remaining", 0), 0),
        "ticks": 0,
        "ticks_elapsed": 0,
        "player_damage": 0,
        "enemy_damage": 0,
        "killed": False,
        "died": False,
        "stop_reason": "bank_run",
        "food_used": tuple(),
        "potions_used": tuple(),
        "ammo_used": {},
        "runes_used": {},
        "status_damage": {},
        "status_applied": {},
        "status_expired": tuple(),
        "drops": {},
        "xp_rewards": {},
    }


def _combat_locks_can_bank_run(locked_reasons):
    if not locked_reasons:
        return True
    return all(
        isinstance(reason, str)
        and (reason == "compatible ammunition" or reason.startswith("runes: "))
        for reason in locked_reasons
    )


def _combat_progress_or_start_bank_run(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data=None, enemy_data=None):
    bank_run = _sanitize_combat_bank_run(data.get("combat_bank_run"))
    if bank_run and bank_run.get("target_id") not in (None, target_id):
        bank_run = {}
    started = False
    if not bank_run and _combat_bank_run_needed(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data):
        if not _combat_try_pack_yak_winter_storage(
            data,
            target_id,
            combat_class,
            ranged_weapon_spec,
            spell_spec,
            equipment_data,
            enemy_data,
        ):
            bank_run = {"reviews_remaining": COMBAT_BANK_RUN_REVIEWS, "target_id": target_id}
            started = True
    if not bank_run:
        data["combat_bank_run"] = {}
        return None
    remaining = _non_negative_int(bank_run.get("reviews_remaining", 0), 0) - 1
    if remaining <= 0:
        data["combat_bank_run"] = {}
        _combat_refill_context_supplies(data, target_id, combat_class, ranged_weapon_spec, spell_spec, equipment_data, enemy_data)
        return _combat_bank_run_result(data, target_id, started=started, completed=True)
    data["combat_bank_run"] = {"reviews_remaining": remaining, "target_id": target_id}
    return _combat_bank_run_result(data, target_id, started=started, completed=False)


def _combat_refill_ranged_ammo_loadout(data, weapon_spec):
    if not isinstance(weapon_spec, Mapping):
        return
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    ammo_loadout = dict(loadout.get("ammo", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    for ammo_name in weapon_spec.get("compatible_ammo", ()) or ():
        if not isinstance(ammo_name, str):
            continue
        available = _non_negative_int(inventory.get(ammo_name, 0), 0)
        if available <= 0:
            continue
        inventory[ammo_name] = 0
        ammo_loadout[ammo_name] = _non_negative_int(ammo_loadout.get(ammo_name, 0), 0) + available
    loadout["ammo"] = {item: amount for item, amount in ammo_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_refill_magic_rune_loadout(data, rune_cost):
    if not isinstance(rune_cost, Mapping):
        return
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    rune_loadout = dict(loadout.get("runes", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    for rune_name in rune_cost:
        if not isinstance(rune_name, str):
            continue
        available = _non_negative_int(inventory.get(rune_name, 0), 0)
        if available <= 0:
            continue
        inventory[rune_name] = 0
        rune_loadout[rune_name] = _non_negative_int(rune_loadout.get(rune_name, 0), 0) + available
    loadout["runes"] = {item: amount for item, amount in rune_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_consume_ranged_ammo(data, weapon_spec, target_id):
    ammo_name = _combat_selected_ranged_ammo(data, weapon_spec, target_id)
    if not isinstance(ammo_name, str):
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    ammo_loadout = dict(loadout.get("ammo", {}) or {})
    current = _non_negative_int(ammo_loadout.get(ammo_name, 0), 0)
    if current <= 0:
        return None
    ammo_loadout[ammo_name] = current - 1
    if ammo_loadout[ammo_name] <= 0:
        ammo_loadout.pop(ammo_name, None)
    loadout["ammo"] = ammo_loadout
    data["combat_supply_loadout"] = loadout
    return ammo_name


def _combat_consume_loaded_rune_cost(data, rune_cost):
    if not isinstance(rune_cost, Mapping) or not rune_cost:
        return {}
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    rune_loadout = dict(loadout.get("runes", {}) or {})
    if any(
        _non_negative_int(rune_loadout.get(rune_name, 0), 0) < _positive_int(amount, 0)
        for rune_name, amount in rune_cost.items()
        if isinstance(rune_name, str)
    ):
        return None
    used = {}
    for rune_name, amount in rune_cost.items():
        if not isinstance(rune_name, str):
            continue
        required = _positive_int(amount, 0)
        if required <= 0:
            continue
        current = _non_negative_int(rune_loadout.get(rune_name, 0), 0)
        rune_loadout[rune_name] = current - required
        if rune_loadout[rune_name] <= 0:
            rune_loadout.pop(rune_name, None)
        used[rune_name] = required
    loadout["runes"] = rune_loadout
    data["combat_supply_loadout"] = loadout
    return used


def _combat_consume_magic_runes(data, spell_spec, _target_id, equipment_data=None):
    if not isinstance(spell_spec, Mapping):
        return None
    rune_cost = _combat_effective_rune_cost_pure(data, spell_spec.get("rune_cost", {}), equipment_data)
    return _combat_consume_loaded_rune_cost(data, rune_cost)


def _combat_ranged_strength_bonus(player_totals, ammo_name):
    ammo_spec = COMBAT_RANGED_AMMO_DATA.get(ammo_name) if isinstance(ammo_name, str) else None
    ammo_bonus = _positive_int(ammo_spec.get("ranged_strength", 0), 0) if isinstance(ammo_spec, Mapping) else 0
    return _equipment_bonus_value(player_totals, "ranged_strength") + ammo_bonus


def _combat_regenerate_special_attack_energy(data, ticks, *, exact=False):
    energy = _non_negative_int(
        data.get("combat_special_attack_energy", COMBAT_SPECIAL_ATTACK_MAX_ENERGY),
        COMBAT_SPECIAL_ATTACK_MAX_ENERGY,
    )
    elapsed = max(0, _non_negative_int(ticks, 0))
    if exact:
        numerator = (
            min(
                COMBAT_BURST_TICKS - 1,
                _non_negative_int(
                    data.get("combat_special_attack_regen_residual", 0),
                    0,
                ),
            )
            + elapsed * COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS
        )
        regen, residual = divmod(numerator, COMBAT_BURST_TICKS)
        data["combat_special_attack_regen_residual"] = residual
    else:
        regen = int(elapsed * COMBAT_SPECIAL_ATTACK_REGEN_PER_50_TICKS / COMBAT_BURST_TICKS)
    data["combat_special_attack_energy"] = min(COMBAT_SPECIAL_ATTACK_MAX_ENERGY, energy + regen)


def _combat_recover_current_levels(data, ticks):
    """Restore boosted/drained current levels toward base by one level per
    COMBAT_STAT_DRAIN_RECOVERY_TICKS ticks (engine restoreTick cadence:
    +1 toward max every 100 ticks). Boosts decay down, drains recover up."""
    currents = _sanitize_combat_current_levels(data.get("combat_current_levels"))
    progress = _sanitize_combat_recovery_progress(data.get("combat_recovery_progress"))
    if not currents:
        progress.pop("stat_drain_ticks", None)
        data["combat_current_levels"] = {}
        data["combat_recovery_progress"] = progress
        return
    stat_drain_ticks = _non_negative_int(progress.get("stat_drain_ticks", 0), 0) + max(0, _non_negative_int(ticks, 0))
    steps = stat_drain_ticks // COMBAT_STAT_DRAIN_RECOVERY_TICKS
    stat_drain_ticks = stat_drain_ticks % COMBAT_STAT_DRAIN_RECOVERY_TICKS
    if steps > 0:
        effects = prayer_effect_state_pure(data)
        rapid_restore_uptime = float(effects.get("rapid_restore", 0.0)) / 2.0
        berserker_uptime = float(effects.get("berserker", 0.0)) / 1.15
        restored = {}
        for skill_id, current in currents.items():
            base = _combat_base_skill_level(data, skill_id, current)
            if current < base:
                recovery_steps = steps
                if skill_id not in ("constitution", "prayer", "summoning"):
                    recovery_steps = max(steps, int(steps * (1.0 + rapid_restore_uptime)))
                current = min(base, current + recovery_steps)
            elif current > base:
                decay_steps = max(1, int(steps / (1.0 + .15 * berserker_uptime)))
                current = max(base, current - decay_steps)
            if current != base:
                restored[skill_id] = current
        currents = restored
    progress["stat_drain_ticks"] = stat_drain_ticks if currents and stat_drain_ticks > 0 else 0
    data["combat_current_levels"] = currents
    data["combat_recovery_progress"] = {key: value for key, value in progress.items() if value > 0}


def combat_dragonfire_protection_pure(
    player_data,
    enemy,
    *,
    magic_prayer_active=None,
):
    spec = enemy.get("dragonfire") if isinstance(enemy, Mapping) else None
    if not isinstance(spec, Mapping):
        return {}
    equipment = player_data.get("equipment", {}) or {}
    shield_name = (
        equipment.get("shield")
        if isinstance(equipment, Mapping)
        else None
    )
    shield_active = shield_name in tuple(spec.get("shield_items", ()) or ())
    antifire_active = (
        _non_negative_int(
            player_data.get("combat_antifire_ticks_remaining", 0),
            0,
        )
        > 0
    )
    super_antifire_active = (
        _non_negative_int(
            player_data.get("combat_super_antifire_ticks_remaining", 0),
            0,
        )
        > 0
    )
    if magic_prayer_active is None:
        magic_prayer_active = bool(
            prayer_effect_state_pure(player_data).get("protect_magic")
        )
    full = bool(
        super_antifire_active
        or antifire_active and (shield_active or magic_prayer_active)
    )
    partial = bool(
        not full
        and (
            shield_active
            or antifire_active
            or magic_prayer_active
        )
    )
    protection_level = 2 if full else 1 if partial else 0
    max_hit = (
        0
        if full
        else _positive_int(spec.get("partial_max_hit", 50), 50)
        if partial
        else _positive_int(spec.get("unprotected_max_hit", 500), 500)
    )
    return {
        "protection_level": protection_level,
        "state": "Full" if full else "Partial" if partial else "None",
        "max_hit": max_hit,
        "shield_active": shield_active,
        "shield_item": shield_name if shield_active else "",
        "antifire_active": antifire_active,
        "super_antifire_active": super_antifire_active,
        "magic_prayer_active": bool(magic_prayer_active),
    }


def combat_poison_immunity_ticks_pure(player_data):
    effects = _sanitize_combat_status_effects(player_data.get("combat_status_effects"))
    immunity = effects.get("poison_immunity", {})
    return _non_negative_int(immunity.get("ticks_left", 0), 0) if isinstance(immunity, Mapping) else 0


def _combat_refill_antipoison_loadout(data):
    """Load a couple of antipoison doses — one cures the poison, so two cover a
    trip and refill at every bank run. Uncapped, this loaded the player's entire
    antipoison stock into the loadout, which (since each unstackable dose costs a
    slot) could push supplies past the whole 28-slot inventory and softlock combat
    into a permanent bank-run loop."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    potion_loadout = dict(loadout.get("potions", {}) or {})
    inventory = dict(data.get("inventory", {}) or {})
    loaded = sum(
        _non_negative_int(amount, 0)
        for item_name, amount in potion_loadout.items()
        if item_name in COMBAT_ANTIPOISON_POTION_DATA
    )
    for item_name in COMBAT_ANTIPOISON_POTION_DATA:
        if loaded >= _COMBAT_ANTIPOISON_SLOT_CAP:
            break
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0:
            continue
        take = min(available, _COMBAT_ANTIPOISON_SLOT_CAP - loaded)
        potion_loadout[item_name] = _non_negative_int(potion_loadout.get(item_name, 0), 0) + take
        inventory[item_name] = available - take
        loaded += take
    loadout["potions"] = {item_name: amount for item_name, amount in potion_loadout.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_refill_dragonfire_loadout(data, enemy):
    if not isinstance(enemy, Mapping) or not isinstance(
        enemy.get("dragonfire"), Mapping
    ):
        return
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    potion_loadout = dict(loadout.get("potions", {}) or {})
    inventory = dict(data.get("inventory", {}) or {})
    loaded = sum(
        _non_negative_int(amount, 0)
        for item_name, amount in potion_loadout.items()
        if item_name in _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES
    )
    candidates = sorted(
        _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
        key=lambda item_name: (
            1
            if _COMBAT_DRAGONFIRE_POTION_BY_DOSE[item_name][2]
            == "super_antifire"
            else 0,
            _COMBAT_DRAGONFIRE_POTION_BY_DOSE[item_name][3],
        ),
        reverse=True,
    )
    for item_name in candidates:
        if loaded >= _COMBAT_DRAGONFIRE_POTION_SLOT_CAP:
            break
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0:
            continue
        take = min(
            available,
            _COMBAT_DRAGONFIRE_POTION_SLOT_CAP - loaded,
        )
        inventory[item_name] = available - take
        potion_loadout[item_name] = (
            _non_negative_int(potion_loadout.get(item_name, 0), 0) + take
        )
        loaded += take
    loadout["potions"] = {
        item_name: amount
        for item_name, amount in potion_loadout.items()
        if amount > 0
    }
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_consume_dragonfire_if_needed(data, enemy):
    if not isinstance(enemy, Mapping) or not isinstance(
        enemy.get("dragonfire"), Mapping
    ):
        return None
    if (
        _non_negative_int(
            data.get("combat_super_antifire_ticks_remaining", 0),
            0,
        )
        > 0
        or _non_negative_int(
            data.get("combat_antifire_ticks_remaining", 0),
            0,
        )
        > 0
    ):
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    potion_loadout = dict(loadout.get("potions", {}) or {})
    candidates = sorted(
        (
            item_name
            for item_name, amount in potion_loadout.items()
            if item_name in _COMBAT_DRAGONFIRE_POTION_BY_DOSE
            and _non_negative_int(amount, 0) > 0
        ),
        key=lambda item_name: (
            1
            if _COMBAT_DRAGONFIRE_POTION_BY_DOSE[item_name][2]
            == "super_antifire"
            else 0,
            _COMBAT_DRAGONFIRE_POTION_BY_DOSE[item_name][3],
        ),
        reverse=True,
    )
    if not candidates:
        return None
    item_name = candidates[0]
    base_name, _skills, strategy, dose, is_flask = (
        _COMBAT_DRAGONFIRE_POTION_BY_DOSE[item_name]
    )
    potion_loadout[item_name] -= 1
    if potion_loadout[item_name] <= 0:
        potion_loadout.pop(item_name, None)
    if dose > 1:
        lower = (
            potion_flask_name(base_name, dose - 1)
            if is_flask
            else potion_dose_name(base_name, dose - 1)
        )
        potion_loadout[lower] = (
            _non_negative_int(potion_loadout.get(lower, 0), 0) + 1
        )
    else:
        empty_name = "Potion flask" if is_flask else "Vial"
        inventory = dict(data.get("inventory", {}) or {})
        inventory[empty_name] = (
            _non_negative_int(inventory.get(empty_name, 0), 0) + 1
        )
        data["inventory"] = inventory
    loadout["potions"] = potion_loadout
    data["combat_supply_loadout"] = loadout
    effect_key = (
        "combat_super_antifire_ticks_remaining"
        if strategy == "super_antifire"
        else "combat_antifire_ticks_remaining"
    )
    duration = _positive_int(
        POTION_FAMILIES[base_name].get("duration_ticks", 600),
        600,
    )
    data[effect_key] = duration
    return {
        "item": item_name,
        "effect": strategy,
        "ticks": duration,
    }


def _combat_advance_dragonfire_effects(data, ticks):
    ticks = max(0, _non_negative_int(ticks, 0))
    for effect_key in (
        "combat_antifire_ticks_remaining",
        "combat_super_antifire_ticks_remaining",
    ):
        data[effect_key] = max(
            0,
            _non_negative_int(data.get(effect_key, 0), 0) - ticks,
        )


def _combat_consume_antipoison_if_needed(data):
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if "poison" not in effects:
        data["combat_status_effects"] = effects
        return None
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    potion_loadout = dict(loadout.get("potions", {}) or {})
    for item_name, spec in COMBAT_ANTIPOISON_POTION_DATA.items():
        amount = _non_negative_int(potion_loadout.get(item_name, 0), 0)
        if amount <= 0:
            continue
        amount -= 1
        if amount > 0:
            potion_loadout[item_name] = amount
        else:
            potion_loadout.pop(item_name, None)
        replacement = str(spec.get("replacement", ""))
        if replacement in COMBAT_ANTIPOISON_POTION_DATA:
            potion_loadout[replacement] = _non_negative_int(potion_loadout.get(replacement, 0), 0) + 1
        elif replacement:
            inventory = dict(data.get("inventory", {}) or {})
            inventory[replacement] = _non_negative_int(inventory.get(replacement, 0), 0) + 1
            data["inventory"] = inventory
        immunity_ticks = _positive_int(spec.get("immunity_ticks", 0), 0)
        current_immunity = effects.get("poison_immunity", {})
        current_ticks = (
            _non_negative_int(current_immunity.get("ticks_left", 0), 0)
            if isinstance(current_immunity, Mapping)
            else 0
        )
        effects.pop("poison", None)
        effects["poison_immunity"] = {
            "ticks_left": max(current_ticks, immunity_ticks),
            "source": spec.get("source", POTION_TYPE_SOURCE_PATH),
        }
        loadout["potions"] = {potion: qty for potion, qty in potion_loadout.items() if qty > 0}
        data["combat_supply_loadout"] = loadout
        data["combat_status_effects"] = effects
        return {
            "item": item_name,
            "replacement": replacement,
            "effect": "poison_cure",
            "immunity_ticks": immunity_ticks,
        }
    data["combat_status_effects"] = effects
    return None


def combat_poison_ticks_for_initial_damage_pure(initial_damage):
    damage = _positive_int(initial_damage, 0)
    return max(0, damage * 5 - 4)


def combat_poison_damage_for_ticks_pure(ticks_left):
    return ((_non_negative_int(ticks_left, 0) // 5) + 1) * 10


def _combat_apply_poison_effect_to_data(data, initial_damage):
    ticks_left = combat_poison_ticks_for_initial_damage_pure(initial_damage)
    if ticks_left <= 0:
        return False, "invalid poison damage"
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if combat_poison_immunity_ticks_pure({"combat_status_effects": effects}) > 0:
        data["combat_status_effects"] = effects
        return False, "poison immune"
    current_poison = effects.get("poison", {})
    current_damage = combat_poison_damage_for_ticks_pure(current_poison.get("ticks_left", 0)) if current_poison else 0
    new_damage = combat_poison_damage_for_ticks_pure(ticks_left)
    if current_poison and current_damage > new_damage:
        data["combat_status_effects"] = effects
        return False, "existing poison is stronger"
    effects["poison"] = {
        "ticks_left": ticks_left,
        "tick_progress": 0,
        "source": COMBAT_POISON_SOURCE_PATH,
    }
    data["combat_status_effects"] = effects
    return True, ""


def apply_combat_poison_effect_pure(player_data, initial_damage):
    data = _copy_player_data_with_nested(player_data)
    data.update(sanitize_combat_state_pure(data))
    applied, reason = _combat_apply_poison_effect_to_data(data, initial_damage)
    return data, applied, reason


def _combat_advance_status_effects(data, ticks, current_lifepoints=None, max_lifepoints=None):
    effects = _sanitize_combat_status_effects(data.get("combat_status_effects"))
    if current_lifepoints is not None:
        data["combat_lifepoints"] = _non_negative_int(current_lifepoints, 0)
    max_lp = max_lifepoints if max_lifepoints is not None else combat_max_lifepoints_pure(data)
    player_lp = max(
        0,
        min(
            _non_negative_int(data.get("combat_lifepoints", max_lp), max_lp),
            max_lp + COMBAT_MAX_OVERHEAL_BONUS_LIFEPOINTS,
        ),
    )
    result = {"damage": {}, "expired": tuple(), "died": False}
    expired = []
    immunity = effects.get("poison_immunity")
    if immunity:
        ticks_left = max(
            0,
            _non_negative_int(immunity.get("ticks_left", 0), 0) - max(0, _non_negative_int(ticks, 0)),
        )
        if ticks_left > 0:
            effects["poison_immunity"] = {
                "ticks_left": ticks_left,
                "source": immunity.get("source", POTION_TYPE_SOURCE_PATH),
            }
        else:
            effects.pop("poison_immunity", None)
            expired.append("poison_immunity")
    poison = effects.get("poison")
    if poison:
        progress = _non_negative_int(poison.get("tick_progress", 0), 0) + max(0, _non_negative_int(ticks, 0))
        ticks_left = _non_negative_int(poison.get("ticks_left", 0), 0)
        poison_damage = 0
        while ticks_left > 0 and progress >= COMBAT_POISON_TICK_DELAY and player_lp > 0:
            progress -= COMBAT_POISON_TICK_DELAY
            damage = min(player_lp, combat_poison_damage_for_ticks_pure(ticks_left))
            poison_damage += damage
            player_lp -= damage
            ticks_left -= 1
        if poison_damage > 0:
            result["damage"]["poison"] = poison_damage
        if ticks_left > 0 and player_lp > 0:
            effects["poison"] = {
                "ticks_left": ticks_left,
                "tick_progress": min(progress, COMBAT_POISON_TICK_DELAY - 1),
                "source": poison.get("source", COMBAT_POISON_SOURCE_PATH),
            }
        else:
            effects.pop("poison", None)
            if ticks_left <= 0:
                expired.append("poison")
    result["died"] = player_lp <= 0 and bool(result["damage"])
    result["expired"] = tuple(expired)
    data["combat_lifepoints"] = player_lp
    data["combat_status_effects"] = effects
    return result


def combat_status_summary_pure(player_data):
    effects = _sanitize_combat_status_effects(player_data.get("combat_status_effects"))
    poison = effects.get("poison")
    if poison:
        ticks_left = _non_negative_int(poison.get("ticks_left", 0), 0)
        tick_progress = _non_negative_int(poison.get("tick_progress", 0), 0)
        next_damage = combat_poison_damage_for_ticks_pure(ticks_left)
        ticks_until = max(1, COMBAT_POISON_TICK_DELAY - min(tick_progress, COMBAT_POISON_TICK_DELAY - 1))
        return f"Poisoned: {next_damage} LP in {ticks_until} ticks"
    immunity_ticks = combat_poison_immunity_ticks_pure({"combat_status_effects": effects})
    if immunity_ticks > 0:
        return f"Poison immune: {immunity_ticks} ticks"
    return ""


def _combat_auto_eat_food_available(data):
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    food_loadout = loadout.get("food", {}) or {}
    for item_name in data.get("combat_auto_eat_food", ()) or ():
        if item_name in COMBAT_FOOD_DATA and _positive_int(food_loadout.get(item_name, 0), 0) > 0:
            return True
    return False


def _combat_should_auto_flee(data, current_lifepoints, max_lifepoints):
    """Auto-flee bails out of the burst when LP has fallen to the auto-eat
    threshold and there is no food left to recover with — the "dying silently"
    case. Enabled by default; the last-ditch heal has already been attempted by
    the caller, so reaching here means the player genuinely cannot recover."""
    if not data.get("combat_auto_flee", True):
        return False
    threshold_percent = _positive_int(data.get("combat_auto_eat_threshold_percent", 40), 40)
    threshold = max(1, int(max_lifepoints * threshold_percent / 100.0))
    if current_lifepoints > threshold:
        return False
    return not _combat_auto_eat_food_available(data)


def apply_combat_stat_boost_to_pure(data, skill_id, boost):
    """Potion-style boost (shared by all stat potions): sets current to
    base + boost *as a floor* — it cures a drained stat and boosts to the
    ceiling, but never lowers an already-higher boost and never stacks past
    base + boost (engine `boostCap`). Mutates and returns ``data``."""
    base = _combat_base_skill_level(data, skill_id, 1)
    target = base + max(0, int(boost))
    current = _combat_effective_skill_level(data, skill_id, base)
    if target > current:
        apply_combat_stat_delta_pure(data, skill_id, target - current)
    return data


def _potion_boost_amount(base_level, strategy):
    # PotionType.kt: regular = floor(base/10)+3, super = floor(15*base/100)+5.
    base = max(1, int(base_level))
    if strategy == "s":
        return int(15 * base / 100) + 5
    return base // 10 + 3


def prayer_potion_restore_amount_pure(base_level, strategy):
    """Whole Prayer points restored before the stored tenths-of-a-point scale."""
    base = max(1, int(base_level))
    if strategy == "s_prayer":
        return base * 35 // 100 + 7
    return base // 4 + 7


def _combat_relevant_potion_skills(combat_class):
    """The stat(s) a potion should boost for the active combat style — the ones
    that actually raise output (max hit / accuracy). Defence is not an output
    stat, so it is not auto-potioned."""
    if combat_class == "ranged":
        return ("ranged", "prayer")
    if combat_class == "magic":
        return ("magic", "prayer")
    return ("strength", "attack", "prayer")


def _combat_pick_potion_for_skill(stat_potions, skill_id):
    """Choose the loadout stat-potion dose to drink for ``skill_id``: prefer a
    super potion (bigger boost), then the higher dose (drink the fuller flask
    first, RS-style). Returns the dose item name or None."""
    best = None
    best_rank = None
    for item_name, count in stat_potions.items():
        if _non_negative_int(count, 0) <= 0:
            continue
        entry = _COMBAT_STAT_POTION_BY_DOSE.get(item_name)
        if entry is None or skill_id not in entry[1]:
            continue
        _base, _skills, strategy, dose, _is_flask = entry
        rank = (1 if strategy in {"s", "s_prayer"} else 0, dose)
        if best_rank is None or rank > best_rank:
            best, best_rank = item_name, rank
    return best


def _combat_auto_drink_potions(data, combat_class):
    """Drink carried stat potions at burst start to (re)apply the output boosts
    for the active style. Only drinks a stat that has no active boost (effective
    <= base), so one flask lasts until its boost fully decays. Drinking a dose
    consumes it (a (4) leaves a (3); a (1) empties). Returns the drink events."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    stat_potions = dict(loadout.get("stat_potions", {}) or {})
    if not stat_potions:
        return []
    events = []
    for skill_id in _combat_relevant_potion_skills(combat_class):
        base = _combat_base_skill_level(data, skill_id, 1)
        if skill_id == "prayer":
            prayer_max = base * 10
            if not active_prayer_selection_pure(data) or _non_negative_int(data.get("combat_prayer_points", prayer_max), prayer_max) >= prayer_max:
                continue
        elif _combat_effective_skill_level(data, skill_id, base) > base:
            continue  # a boost is already active on this stat
        item_name = _combat_pick_potion_for_skill(stat_potions, skill_id)
        if item_name is None:
            continue
        base_name, skills, strategy, dose, is_flask = _COMBAT_STAT_POTION_BY_DOSE[item_name]
        # Consume one dose: the vial/flask drops to the next-lower dose (dropped at 0/empty).
        stat_potions[item_name] = _non_negative_int(stat_potions.get(item_name, 0), 0) - 1
        if stat_potions[item_name] <= 0:
            stat_potions.pop(item_name, None)
        if dose > 1:
            lower = potion_flask_name(base_name, dose - 1) if is_flask else potion_dose_name(base_name, dose - 1)
            stat_potions[lower] = _non_negative_int(stat_potions.get(lower, 0), 0) + 1
        # Apply the boost to every stat the family covers (Combat potion = both).
        for boosted_skill in skills:
            if boosted_skill == "prayer":
                prayer_level = _combat_base_skill_level(data, "prayer", 1)
                restored = prayer_potion_restore_amount_pure(prayer_level, strategy)
                data["combat_prayer_points"] = min(prayer_level * 10, _non_negative_int(data.get("combat_prayer_points", 0), 0) + restored * 10)
            else:
                boost = _potion_boost_amount(_combat_base_skill_level(data, boosted_skill, 1), strategy)
                apply_combat_stat_boost_to_pure(data, boosted_skill, boost)
        events.append({"item": item_name, "skills": tuple(skills)})
    loadout["stat_potions"] = {name: amount for name, amount in stat_potions.items() if amount > 0}
    data["combat_supply_loadout"] = loadout
    return events


def _combat_relevant_potion_items(combat_class):
    """Style-relevant stat-potion dose items, best-first: supers before regulars,
    a Combat potion (boosts both melee stats from one slot) preferred, fuller
    flasks first. Used so a small potion cap is never wasted on an off-style flask."""
    relevant_skills = set(_combat_relevant_potion_skills(combat_class))
    items = []
    for item_name, (base_name, skills, strategy, dose, _is_flask) in _COMBAT_STAT_POTION_BY_DOSE.items():
        if relevant_skills.intersection(skills):
            covers_two = len(skills) > 1
            # More doses per slot ranks higher, so a full flask (6) beats a vial (4).
            rank = (1 if strategy in {"s", "s_prayer"} else 0, 1 if covers_two else 0, int(dose))
            items.append((rank, item_name))
    items.sort(reverse=True)
    return [item_name for _rank, item_name in items]


def _combat_refill_stat_potions(data, combat_class="melee"):
    """Load style-relevant stat-potion flasks into the loadout, up to the packing
    mode's flask cap (a couple of doses last a whole trip and refill every bank
    run). One flask = one slot; off-style potions are never loaded."""
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    stat_potions = dict(loadout.get("stat_potions", {}) or {})
    inventory = data.get("inventory", {}) or {}
    if not isinstance(inventory, Mapping):
        data["combat_supply_loadout"] = loadout
        return
    inventory = dict(inventory)
    cap = _combat_potion_flask_cap(data)
    loaded = sum(_non_negative_int(amount, 0) for amount in stat_potions.values())
    for item_name in _combat_relevant_potion_items(combat_class):
        if loaded >= cap:
            break
        available = _non_negative_int(inventory.get(item_name, 0), 0)
        if available <= 0:
            continue
        take = min(available, cap - loaded)
        inventory[item_name] = available - take
        stat_potions[item_name] = _non_negative_int(stat_potions.get(item_name, 0), 0) + take
        loaded += take
    loadout["stat_potions"] = {name: amount for name, amount in stat_potions.items() if amount > 0}
    data["inventory"] = inventory
    data["combat_supply_loadout"] = loadout


def _combat_supply_slots_used(data):
    """Slots the combat loadout occupies in the shared 28-slot inventory.

    Food, potions, hazards, and non-stackable finishing tools cost one slot per
    item; ammo, runes, cannonballs, and stackable finishers cost one per stack.
    """
    loadout = _sanitize_combat_supply_loadout(data.get("combat_supply_loadout"))
    slots = 0
    for key in ("food", "potions", "stat_potions", "hazards"):
        slots += sum(_non_negative_int(amount, 0) for amount in (loadout.get(key, {}) or {}).values())
    for key in ("ammo", "runes"):
        slots += sum(1 for amount in (loadout.get(key, {}) or {}).values() if _non_negative_int(amount, 0) > 0)
    for item_name, amount in (loadout.get("finishers", {}) or {}).items():
        count = _non_negative_int(amount, 0)
        if count <= 0:
            continue
        slots += 1 if item_name in STACKABLE_ITEM_NAMES else count
    if _non_negative_int(loadout.get("cannonballs", 0), 0) > 0:
        slots += 1
    return slots
