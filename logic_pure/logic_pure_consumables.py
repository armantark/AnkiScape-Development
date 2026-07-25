"""logic_pure_consumables.py - split out of logic_pure.py; see that module's header."""

from math import comb, floor, sqrt

from ..data.pack_data import ITEM_PACK_DATA

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

from ..logic_pure.logic_pure_combat_supplies import (  # noqa: F401  (re-export)
    _combat_advance_dragonfire_effects,
    _combat_advance_status_effects,
    _combat_apply_poison_effect_to_data,
    _combat_auto_drink_potions,
    _combat_auto_eat_food_available,
    _combat_bank_has_runes,
    _combat_bank_run_needed,
    _combat_bank_run_result,
    _combat_banked_antipoison_count,
    _combat_banked_auto_food_count,
    _combat_banked_dragonfire_potion_count,
    _combat_banked_finisher_count,
    _combat_banked_ranged_ammo_count,
    _combat_carried_slot_counts,
    _combat_consume_antipoison_if_needed,
    _combat_consume_dragonfire_if_needed,
    _combat_consume_loaded_rune_cost,
    _combat_consume_magic_runes,
    _combat_consume_ranged_ammo,
    _combat_custom_layout_view,
    _combat_deposit_loot,
    _combat_loaded_antipoison_count,
    _combat_loaded_dragonfire_potion_count,
    _combat_loaded_food_count,
    _combat_loaded_ranged_ammo,
    _combat_locks_can_bank_run,
    _combat_missing_loaded_runes,
    _combat_pick_potion_for_skill,
    _combat_progress_or_start_bank_run,
    _combat_ranged_strength_bonus,
    _combat_recover_current_levels,
    _combat_refill_antipoison_loadout,
    _combat_refill_context_supplies,
    _combat_refill_dragonfire_loadout,
    _combat_refill_finisher_loadout,
    _combat_refill_food_loadout,
    _combat_refill_hazard_loadout,
    _combat_refill_magic_rune_loadout,
    _combat_refill_ranged_ammo_loadout,
    _combat_refill_stat_potions,
    _combat_regenerate_special_attack_energy,
    _combat_relevant_potion_items,
    _combat_relevant_potion_skills,
    _combat_should_auto_flee,
    _combat_supply_slots_used,
    _combat_trim_food_to_capacity,
    _combat_try_pack_yak_winter_storage,
    _combat_void_shifter_escape_ready,
    _potion_boost_amount,
    apply_combat_poison_effect_pure,
    apply_combat_stat_boost_to_pure,
    combat_dragonfire_protection_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_immunity_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
    combat_status_summary_pure,
    prayer_potion_restore_amount_pure,
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

from ..logic_pure.logic_pure_combat_supplies import (
    _potion_boost_amount,
    apply_combat_stat_boost_to_pure,
    prayer_potion_restore_amount_pure,
)

from ..logic_pure.logic_pure_combat_model import (
    _combat_base_skill_level,
    _combat_effective_skill_level,
    apply_combat_stat_delta_pure,
    combat_max_lifepoints_pure,
)

from ..logic_pure.logic_pure_state import (
    _copy_player_data_with_nested,
    _non_negative_int,
    _positive_int,
)


def _consumable_heal(data, amount):
    max_lp = combat_max_lifepoints_pure(data)
    current = _non_negative_int(data.get("combat_lifepoints", max_lp), max_lp)
    healed = min(max_lp, current + max(0, int(amount)))
    data["combat_lifepoints"] = healed
    return healed - current


def apply_item_pack_open_pure(inventory, item_name, open_all=False):
    """Open one or every owned shop supply pack without mutating the input."""
    updated = dict(inventory or {})
    spec = ITEM_PACK_DATA.get(item_name)
    owned = _non_negative_int(updated.get(item_name, 0), 0)
    if spec is None or owned <= 0:
        return updated, {"allowed": False, "reason": "missing_pack", "item_name": item_name}
    packs_opened = owned if open_all else 1
    remaining = owned - packs_opened
    if remaining:
        updated[item_name] = remaining
    else:
        updated.pop(item_name, None)
    content_item = str(spec["content_item"])
    content_quantity = packs_opened * int(spec["content_quantity"])
    updated[content_item] = _non_negative_int(updated.get(content_item, 0), 0) + content_quantity
    return updated, {
        "allowed": True,
        "item_name": item_name,
        "packs_opened": packs_opened,
        "content_item": content_item,
        "content_quantity": content_quantity,
    }


def apply_consumable_pure(player_data, item_name, rng=None):
    """Consume one edible or potion and return its state/result without mutation."""
    rng = rng or (lambda: 0.0)
    spec = CONSUMABLE_DATA.get(item_name)
    if spec is None:
        return dict(player_data), {"allowed": False, "reason": "not_a_consumable"}
    data = _copy_player_data_with_nested(player_data)
    inventory = dict(data.get("inventory", {}) or {})
    if _non_negative_int(inventory.get(item_name, 0), 0) <= 0:
        return dict(player_data), {"allowed": False, "reason": "missing_item", "item_name": item_name}
    inventory[item_name] = _non_negative_int(inventory.get(item_name, 0), 0) - 1
    if inventory[item_name] <= 0:
        inventory.pop(item_name, None)
    data["inventory"] = inventory

    healed = 0
    boosts = {}
    drains = {}
    stats_restored = {}
    prayer_points_restored = 0.0
    summoning_points_restored = 0
    special_move_points_restored = 0
    run_energy_restored_pct = 0
    message = str(spec.get("message", ""))

    def _restore_run_energy_credit() -> int:
        restored = _non_negative_int(spec.get("run_energy_pct", 0), 0)
        if restored <= 0:
            return 0
        data["agility_run_energy_credit_pct"] = min(
            100,
            _non_negative_int(
                data.get("agility_run_energy_credit_pct", 0),
                0,
            )
            + restored,
        )
        return restored

    if spec["kind"] == "kebab_random":
        roll = max(0.0, min(float(rng()) * 100.0, 99.999999))
        outcome = next(o for o in spec["effect_table"] if roll < float(o["upto"]))
        message = str(outcome.get("message", message))
        if "heal_max_pct" in outcome:
            healed = _consumable_heal(data, int(combat_max_lifepoints_pure(data) * float(outcome["heal_max_pct"])))
        elif "heal_range" in outcome:
            lo, hi = outcome["heal_range"]
            healed = _consumable_heal(data, lo + int(max(0.0, min(float(rng()), 0.999999999)) * (hi - lo)))
        elif "heal" in outcome:
            healed = _consumable_heal(data, int(outcome["heal"]))
        for skill_id, (lo, hi) in (outcome.get("boost_levels", {}) or {}).items():
            amount = lo + int(max(0.0, min(float(rng()), 0.999999999)) * (hi - lo))
            apply_combat_stat_delta_pure(data, skill_id, amount)
            boosts[skill_id] = amount
        if "drain_random_skill" in outcome:
            lo, hi = outcome["drain_random_skill"]
            amount = lo + int(max(0.0, min(float(rng()), 0.999999999)) * (hi - lo))
            index = min(len(KEBAB_DRAINABLE_SKILLS) - 1, int(max(0.0, min(float(rng()), 0.999999999)) * len(KEBAB_DRAINABLE_SKILLS)))
            skill_id = KEBAB_DRAINABLE_SKILLS[index]
            apply_combat_stat_delta_pure(data, skill_id, -amount)
            drains[skill_id] = amount
    elif spec["kind"] == "beer":
        healed = _consumable_heal(data, _positive_int(spec.get("heal_constitution_ticks", 1), 1) * 10)
        current_strength = _combat_effective_skill_level(data, "strength", 1)
        current_attack = _combat_effective_skill_level(data, "attack", 1)
        str_boost = int(floor(current_strength * float(spec.get("strength_boost_pct", 0.0))))
        atk_drain = int(floor(current_attack * float(spec.get("attack_drain_pct", 0.0))))
        if str_boost > 0:
            apply_combat_stat_delta_pure(data, "strength", str_boost)
            boosts["strength"] = str_boost
        if atk_drain > 0:
            apply_combat_stat_delta_pure(data, "attack", -atk_drain)
            drains["attack"] = atk_drain
    elif spec["kind"] == "run_energy_food":
        healed = _consumable_heal(
            data,
            _non_negative_int(spec.get("heal", 0), 0),
        )
        run_energy_restored_pct = _restore_run_energy_credit()
    elif spec["kind"] == "skill_boost_run_energy":
        skill_id = str(spec.get("skill_id", ""))
        boost = _non_negative_int(spec.get("boost", 0), 0)
        if skill_id and boost > 0:
            apply_combat_stat_boost_to_pure(data, skill_id, boost)
            boosts[skill_id] = boost
        run_energy_restored_pct = _restore_run_energy_credit()
        leaves = str(spec.get("leaves", ""))
        if leaves:
            inv = dict(data.get("inventory", {}) or {})
            inv[leaves] = _non_negative_int(inv.get(leaves, 0), 0) + 1
            data["inventory"] = inv
    elif spec["kind"] == "potion":
        strategy = str(spec.get("strategy", "r"))
        if strategy in {"antifire", "super_antifire"}:
            effect_key = (
                "combat_super_antifire_ticks_remaining"
                if strategy == "super_antifire"
                else "combat_antifire_ticks_remaining"
            )
            data[effect_key] = max(
                _non_negative_int(data.get(effect_key, 0), 0),
                _positive_int(spec.get("duration_ticks", 600), 600),
            )
        for skill_id in spec.get("skills", ()):
            base = _combat_base_skill_level(data, skill_id, 1)
            if skill_id == "prayer":
                before = _non_negative_int(data.get("combat_prayer_points", base * 10), base * 10)
                restored = (
                    (base // 4 + 8) * 10
                    if strategy == "super_restore"
                    else prayer_potion_restore_amount_pure(base, strategy) * 10
                )
                after = min(base * 10, before + restored)
                data["combat_prayer_points"] = after
                prayer_points_restored = max(0, after - before) / 10.0
                continue
            if skill_id == "summoning":
                base = _positive_int(data.get("summoning_level", 1), 1)
                state = dict(data.get("summoning_state", {}) or {})
                before = _non_negative_int(
                    state.get("summoning_points_current", base), base
                )
                restore = base // 4 + (
                    8 if strategy == "super_restore" else 7
                )
                after = min(base, before + restore)
                state["summoning_points_current"] = after
                data["summoning_state"] = state
                summoning_points_restored = max(0, after - before)
                continue
            if strategy == "super_restore":
                before = _combat_effective_skill_level(
                    data, skill_id, base
                )
                if before < base:
                    after = min(base, before + base // 4 + 8)
                    apply_combat_stat_delta_pure(
                        data, skill_id, after - before
                    )
                    stats_restored[skill_id] = after - before
                continue
            amount = _potion_boost_amount(base, strategy)
            apply_combat_stat_boost_to_pure(data, skill_id, amount)
            boosts[skill_id] = amount
        special_points = _non_negative_int(
            spec.get("special_points", 0), 0
        )
        if special_points:
            state = dict(data.get("summoning_state", {}) or {})
            before = _non_negative_int(
                state.get("special_move_points_current", 60), 60
            )
            after = min(60, before + special_points)
            state["special_move_points_current"] = after
            data["summoning_state"] = state
            special_move_points_restored = after - before
        # Leave the next-lower dose (or an empty Vial at dose 1) in inventory.
        leaves = str(spec.get("leaves", ""))
        if leaves:
            inv = dict(data.get("inventory", {}) or {})
            inv[leaves] = _non_negative_int(inv.get(leaves, 0), 0) + 1
            data["inventory"] = inv
    elif spec["kind"] == "farming_juju":
        leaves = str(spec.get("leaves", ""))
        if leaves:
            inv = dict(data.get("inventory", {}) or {})
            inv[leaves] = _non_negative_int(inv.get(leaves, 0), 0) + 1
            data["inventory"] = inv
        data["farm_juju_active_until"] = _non_negative_int(data.get("farm_clock_minutes", 0), 0) + int(spec["farm_minutes"])
    elif spec["kind"] == "agility_boost":
        boost = _positive_int(spec.get("boost", 1), 1)
        healed = _consumable_heal(data, _non_negative_int(spec.get("heal", 0), 0))
        data["agility_effective_boost"] = max(
            _non_negative_int(data.get("agility_effective_boost", 0), 0),
            boost,
        )
        data["agility_boost_actions_remaining"] = max(
            _non_negative_int(data.get("agility_boost_actions_remaining", 0), 0),
            _positive_int(spec.get("action_budget", 10), 10),
        )
        boosts["agility"] = boost
        run_energy_restored_pct = _restore_run_energy_credit()
        leaves = str(spec.get("leaves", ""))
        if leaves:
            inv = dict(data.get("inventory", {}) or {})
            inv[leaves] = _non_negative_int(inv.get(leaves, 0), 0) + 1
            data["inventory"] = inv

    return data, {
        "allowed": True,
        "item_name": item_name,
        "healed": healed,
        "boosts": boosts,
        "drains": drains,
        "stats_restored": stats_restored,
        "prayer_points_restored": prayer_points_restored,
        "summoning_points_restored": summoning_points_restored,
        "special_move_points_restored": special_move_points_restored,
        "run_energy_restored_pct": run_energy_restored_pct,
        "message": message,
    }
