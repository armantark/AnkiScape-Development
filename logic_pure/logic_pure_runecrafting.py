"""logic_pure_runecrafting.py - split out of logic_pure.py; see that module's header."""

from __future__ import annotations

from typing import Iterable, Mapping, Optional

try:
    from .wicked_hood_logic import (
        apply_wicked_hood_upgrade_pure,
        wicked_hood_fed_altars_pure,
        wicked_hood_operable_pure,
    )
except ImportError:
    from wicked_hood_logic import (  # type: ignore
        apply_wicked_hood_upgrade_pure,
        wicked_hood_fed_altars_pure,
        wicked_hood_operable_pure,
    )

try:
    from .logic_pure_quest import (  # noqa: F401  (re-export)
        QUEST_COMBAT_CONFIG_VERSION,
        QUEST_COMBAT_DEFAULT_BURST_TICKS,
        QUEST_COMBAT_RESOLVER_ENABLED_KEY,
        _QUEST_COMBAT_BONUS_ALIASES,
        _QUEST_COMBAT_PREREQUISITE_BLOCKER_KINDS,
        _QUEST_NONCOMBAT_STAGE_BLOCKER_KINDS,
        _QUEST_ROUTE_INHERITANCE,
        _apply_quest_xp_rewards,
        _apply_skill_xp_reward,
        _consume_quest_current_stage_items,
        _dedupe_quest_blockers,
        _has_quest_tool,
        _mark_quest_stage_actions,
        _quest_blocker,
        _quest_choice_current_stage,
        _quest_choice_options,
        _quest_choice_selected,
        _quest_choice_stage,
        _quest_choices_for_stage,
        _quest_combat_attack_style,
        _quest_combat_bonuses,
        _quest_combat_completed_count,
        _quest_combat_configs,
        _quest_combat_default_rng,
        _quest_combat_display,
        _quest_combat_enemy_spec,
        _quest_combat_normalized_bonuses,
        _quest_combat_remaining_count,
        _quest_combat_required_stat_keys,
        _quest_combat_stats,
        _quest_combat_target_id,
        _quest_combat_total_quantity,
        _quest_current_stage_choice_blockers,
        _quest_current_stage_encounter_by_id,
        _quest_current_stage_rows,
        _quest_current_stage_selected_requirements,
        _quest_flag_completed,
        _quest_item_option_reason,
        _quest_item_requirement_text,
        _quest_requirement_blockers,
        _quest_route_completed,
        _quest_stage_item_option_groups,
        _quest_stage_item_pairs,
        _quest_stage_requirement_variant,
        _quest_stage_strings,
        _requirements_for_unlock_rule,
        _skill_requirement_reason,
        _target_ids_for_unlock_rule,
        _trainable_exp_keys,
        ability_unlocked_pure,
        apply_quest_combat_encounter_pure,
        apply_quest_progress_pure,
        apply_quest_route_choice_pure,
        can_attempt_quest_review_pure,
        can_progress_quest_pure,
        can_start_quest_pure,
        default_quest_combat_active_encounters_pure,
        default_quest_combat_config_pure,
        normalize_xp_rewards_pure,
        primary_xp_reward_amount_pure,
        quest_availability_state_pure,
        quest_combat_encounter_has_stats_pure,
        quest_combat_encounter_ready_pure,
        quest_combat_resolver_enabled_pure,
        quest_current_stage_blocker_reasons_pure,
        quest_current_stage_blockers_pure,
        quest_current_stage_choices_pure,
        quest_current_stage_pure,
        quest_current_stage_resolvable_combat_blockers_pure,
        quest_journal_rows_pure,
        quest_locked_reasons_pure,
        quest_unlock_locked_reasons_pure,
        sanitize_quest_combat_config_pure,
        start_quest_pure,
        target_unlock_locked_reasons_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_quest import (  # type: ignore  # noqa: F401
        QUEST_COMBAT_CONFIG_VERSION,
        QUEST_COMBAT_DEFAULT_BURST_TICKS,
        QUEST_COMBAT_RESOLVER_ENABLED_KEY,
        _QUEST_COMBAT_BONUS_ALIASES,
        _QUEST_COMBAT_PREREQUISITE_BLOCKER_KINDS,
        _QUEST_NONCOMBAT_STAGE_BLOCKER_KINDS,
        _QUEST_ROUTE_INHERITANCE,
        _apply_quest_xp_rewards,
        _apply_skill_xp_reward,
        _consume_quest_current_stage_items,
        _dedupe_quest_blockers,
        _has_quest_tool,
        _mark_quest_stage_actions,
        _quest_blocker,
        _quest_choice_current_stage,
        _quest_choice_options,
        _quest_choice_selected,
        _quest_choice_stage,
        _quest_choices_for_stage,
        _quest_combat_attack_style,
        _quest_combat_bonuses,
        _quest_combat_completed_count,
        _quest_combat_configs,
        _quest_combat_default_rng,
        _quest_combat_display,
        _quest_combat_enemy_spec,
        _quest_combat_normalized_bonuses,
        _quest_combat_remaining_count,
        _quest_combat_required_stat_keys,
        _quest_combat_stats,
        _quest_combat_target_id,
        _quest_combat_total_quantity,
        _quest_current_stage_choice_blockers,
        _quest_current_stage_encounter_by_id,
        _quest_current_stage_rows,
        _quest_current_stage_selected_requirements,
        _quest_flag_completed,
        _quest_item_option_reason,
        _quest_item_requirement_text,
        _quest_requirement_blockers,
        _quest_route_completed,
        _quest_stage_item_option_groups,
        _quest_stage_item_pairs,
        _quest_stage_requirement_variant,
        _quest_stage_strings,
        _requirements_for_unlock_rule,
        _skill_requirement_reason,
        _target_ids_for_unlock_rule,
        _trainable_exp_keys,
        ability_unlocked_pure,
        apply_quest_combat_encounter_pure,
        apply_quest_progress_pure,
        apply_quest_route_choice_pure,
        can_attempt_quest_review_pure,
        can_progress_quest_pure,
        can_start_quest_pure,
        default_quest_combat_active_encounters_pure,
        default_quest_combat_config_pure,
        normalize_xp_rewards_pure,
        primary_xp_reward_amount_pure,
        quest_availability_state_pure,
        quest_combat_encounter_has_stats_pure,
        quest_combat_encounter_ready_pure,
        quest_combat_resolver_enabled_pure,
        quest_current_stage_blocker_reasons_pure,
        quest_current_stage_blockers_pure,
        quest_current_stage_choices_pure,
        quest_current_stage_pure,
        quest_current_stage_resolvable_combat_blockers_pure,
        quest_journal_rows_pure,
        quest_locked_reasons_pure,
        quest_unlock_locked_reasons_pure,
        sanitize_quest_combat_config_pure,
        start_quest_pure,
        target_unlock_locked_reasons_pure,
    )

try:
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
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_state import (  # type: ignore  # noqa: F401
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

try:
    from .logic_pure_quest import (
        quest_unlock_locked_reasons_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_quest import (  # type: ignore
        quest_unlock_locked_reasons_pure,
    )

try:
    from .logic_pure_state import (
        _copy_player_data_with_nested,
        _positive_int,
        quest_completed_pure,
    )
except ImportError:  # pragma: no cover - flat test imports
    from logic_pure_state import (  # type: ignore
        _copy_player_data_with_nested,
        _positive_int,
        quest_completed_pure,
    )


def _altar_for_target(target, runecrafting_data):
    altar_id = target.get("altar_id")
    for candidate in runecrafting_data.values():
        if candidate.get("kind") == "standard" and candidate.get("altar_id") == altar_id:
            return candidate
    return None


def runecrafting_unlocked_pure(player_data):
    return quest_completed_pure(player_data, "rune_mysteries")


def _fed_altars(player_data):
    return set(wicked_hood_fed_altars_pure(player_data))


def _altar_access_item_names(altar_id, runecrafting_data):
    talisman = None
    tiara = None
    for target in runecrafting_data.values():
        if target.get("kind") == "tiara" and target.get("altar_id") == altar_id:
            talisman = target.get("talisman_item")
            tiara = target.get("output_item")
            break
    if talisman is None:
        standard = _altar_for_target({"altar_id": altar_id}, runecrafting_data)
        if standard:
            rune_item = str(standard.get("output_item", "")).replace(" rune", "")
            talisman = f"{rune_item} talisman" if rune_item else None
            tiara = f"{rune_item} tiara" if rune_item else None
    return talisman, tiara


def runecrafting_altar_access_source_pure(player_data, altar_id, runecrafting_data):
    inventory = player_data.get("inventory", {}) or {}
    equipment = player_data.get("equipment", {}) or {}
    talisman_item, tiara_item = _altar_access_item_names(altar_id, runecrafting_data)
    if tiara_item and equipment.get("head") == tiara_item:
        return "tiara"
    if altar_id in _fed_altars(player_data) and wicked_hood_operable_pure(player_data):
        return "hood"
    if talisman_item and inventory.get(talisman_item, 0) > 0:
        return "talisman"
    return ""


def runecrafting_standard_base_capacity_pure(player_data, target, runecrafting_data):
    source = runecrafting_altar_access_source_pure(player_data, target.get("altar_id"), runecrafting_data)
    if source in {"tiara", "hood"}:
        return 28
    if source == "talisman":
        return 27
    return 0


def _pouch_capacity_after_degradation(pouch, degradation):
    threshold = pouch.get("degradation_threshold")
    capacity = _positive_int(pouch.get("capacity", 0), 0)
    if threshold is None:
        return capacity
    try:
        threshold_int = int(threshold)
    except (TypeError, ValueError):
        threshold_int = 0
    loss = max(0, int(degradation) - threshold_int)
    return max(0, capacity - loss)


def _repair_degraded_pouches(data, pouch_data):
    inventory = data["inventory"]
    pouch_state = data.setdefault("runecrafting_pouches", {})
    for pouch_id, pouch in pouch_data.items():
        degraded_item = pouch.get("degraded_item")
        display_name = pouch.get("display_name")
        if degraded_item and display_name and inventory.get(degraded_item, 0) > 0:
            count = inventory.get(degraded_item, 0)
            inventory[degraded_item] = 0
            inventory[display_name] = inventory.get(display_name, 0) + count
            pouch_state[pouch_id] = {"degradation": 0}


def runecrafting_pouch_capacity_pure(player_data, pouch_data):
    level = _positive_int(player_data.get("runecrafting_level", 1), 1)
    inventory = player_data.get("inventory", {}) or {}
    pouch_state = player_data.get("runecrafting_pouches", {}) or {}
    total = 0
    for pouch_id, pouch in pouch_data.items():
        display_name = pouch.get("display_name")
        if not display_name or inventory.get(display_name, 0) <= 0:
            continue
        if level < _positive_int(pouch.get("required_level", 1), 1):
            continue
        state = pouch_state.get(pouch_id, {}) if isinstance(pouch_state, Mapping) else {}
        degradation = _positive_int(state.get("degradation", 0), 0) if isinstance(state, Mapping) else 0
        total += _pouch_capacity_after_degradation(pouch, degradation)
    return total


def _degrade_used_pouches(data, pouch_data, extra_essence_used):
    level = _positive_int(data.get("runecrafting_level", 1), 1)
    inventory = data["inventory"]
    pouch_state = data.setdefault("runecrafting_pouches", {})
    remaining_extra = max(0, int(extra_essence_used))
    for pouch_id, pouch in pouch_data.items():
        if remaining_extra <= 0:
            break
        display_name = pouch.get("display_name")
        if not display_name or inventory.get(display_name, 0) <= 0:
            continue
        if level < _positive_int(pouch.get("required_level", 1), 1):
            continue
        state = pouch_state.setdefault(pouch_id, {"degradation": 0})
        degradation_before = _positive_int(state.get("degradation", 0), 0)
        capacity_before = _pouch_capacity_after_degradation(pouch, degradation_before)
        if capacity_before <= 0:
            continue
        remaining_extra -= min(remaining_extra, capacity_before)
        threshold = pouch.get("degradation_threshold")
        if threshold is None:
            continue
        degradation = degradation_before + 1
        state["degradation"] = degradation
        if _pouch_capacity_after_degradation(pouch, degradation) <= 0 and pouch.get("degraded_item"):
            inventory[display_name] = max(0, inventory.get(display_name, 0) - 1)
            degraded_item = str(pouch["degraded_item"])
            inventory[degraded_item] = inventory.get(degraded_item, 0) + 1
            state["degradation"] = 0


def _available_essence_count(inventory, essence_items):
    return sum(_positive_int(inventory.get(item, 0), 0) for item in essence_items)


def _consume_essence_ordered(inventory, essence_items, amount):
    remaining = amount
    consumed = {}
    for item in essence_items:
        if remaining <= 0:
            break
        take = min(remaining, _positive_int(inventory.get(item, 0), 0))
        if take > 0:
            inventory[item] = inventory.get(item, 0) - take
            consumed[item] = take
            remaining -= take
    return amount - remaining, consumed


def _runecrafting_multiplier_info(target, level):
    output_item = str(target.get("output_item", ""))
    divisors = {
        "Air rune": 11,
        "Mind rune": 14,
        "Water rune": 19,
        "Earth rune": 26,
        "Fire rune": 35,
        "Body rune": 46,
        "Cosmic rune": 59,
        "Chaos rune": 74,
        "Nature rune": 91,
    }
    divisor = divisors.get(output_item)
    if divisor is None:
        return 1, 0.0, 1
    base = int(level) // divisor + 1
    max_base = 99 // divisor + 1
    if base >= max_base:
        return base, 0.0, max_base
    current_start = divisor * (base - 1)
    next_start = divisor * base
    span = max(1, next_start - current_start)
    chance = max(0.0, min(((float(level) - current_start) / span) * 0.60, 0.60))
    return base, chance, max_base


def _standard_output_count(target, level, essence_used, rolls):
    base, chance, max_base = _runecrafting_multiplier_info(target, level)
    if base >= max_base or chance <= 0:
        return base * essence_used
    total = 0
    roll_iter = iter(rolls or ())
    for _ in range(essence_used):
        try:
            roll = float(next(roll_iter))
        except (StopIteration, TypeError, ValueError):
            roll = 1.0
        total += base + 1 if roll < chance else base
    return total


def binding_necklace_charges_pure(player_data):
    if (player_data.get("equipment", {}) or {}).get("neck") != "Binding necklace":
        return 0
    charges = (player_data.get("item_charges", {}) or {}).get("Binding necklace")
    if charges is None:
        return 15
    return max(0, _positive_int(charges, 0))


def runecrafting_locked_reasons_pure(player_data, target_id, runecrafting_data, pouch_data, quest_unlock_rules=()):
    target = runecrafting_data.get(target_id)
    if not target:
        return ("unknown target",)
    reasons = []
    if not runecrafting_unlocked_pure(player_data):
        reasons.append("Rune Mysteries")
    reasons.extend(
        quest_unlock_locked_reasons_pure(
            player_data,
            "runecrafting",
            target_id,
            quest_unlock_rules,
        )
    )
    level = _positive_int(player_data.get("runecrafting_level", 1), 1)
    required_level = _positive_int(target.get("level", 1), 1)
    if level < required_level:
        reasons.append(f"Runecrafting level {required_level}")
    inventory = player_data.get("inventory", {}) or {}
    kind = target.get("kind")
    if kind == "standard":
        if runecrafting_standard_base_capacity_pure(player_data, target, runecrafting_data) <= 0:
            reasons.append("altar access")
        if _available_essence_count(inventory, tuple(target.get("essence_items", ()))) <= 0:
            reasons.append("essence")
    elif kind == "combination":
        if runecrafting_altar_access_source_pure(player_data, target.get("altar_id"), runecrafting_data) == "":
            reasons.append("altar access")
        required_items = ["Pure essence", target.get("component_rune")]
        if not bool(player_data.get("magic_imbue_active", False)):
            required_items.append(target.get("consumed_talisman"))
        for item_name in required_items:
            if item_name and inventory.get(item_name, 0) <= 0:
                reasons.append(str(item_name))
    elif kind == "tiara":
        for item_name in ("Tiara", target.get("talisman_item")):
            if item_name and inventory.get(item_name, 0) <= 0:
                reasons.append(str(item_name))
    elif kind == "hood_feed":
        equipment = player_data.get("equipment", {}) or {}
        has_hood = inventory.get("Wicked hood", 0) > 0 or equipment.get("head") == "Wicked hood"
        if not has_hood:
            reasons.append("Wicked hood")
        hood = player_data.get("wicked_hood", {}) or {}
        altar_id = target.get("altar_id")
        already_fed = (
            bool(hood.get("elemental_fed"))
            if altar_id == "elemental"
            else bool(hood.get("omni_fed"))
            if altar_id == "omni"
            else altar_id in _fed_altars(player_data)
        )
        if already_fed:
            reasons.append("already fed")
        input_item = target.get("input_item")
        if input_item and inventory.get(input_item, 0) <= 0:
            reasons.append(str(input_item))
    return tuple(dict.fromkeys(reasons))


def can_runecraft_target_pure(player_data, target_id, runecrafting_data, pouch_data, quest_unlock_rules=()):
    return not runecrafting_locked_reasons_pure(
        player_data,
        target_id,
        runecrafting_data,
        pouch_data,
        quest_unlock_rules,
    )


def can_runecraft_any_pure(player_data, runecrafting_data, pouch_data, quest_unlock_rules=()):
    return any(
        can_runecraft_target_pure(
            player_data,
            target_id,
            runecrafting_data,
            pouch_data,
            quest_unlock_rules,
        )
        for target_id in runecrafting_data
    )


def apply_runecrafting_action_pure(player_data, target_id, runecrafting_data, pouch_data, rolls=(), quest_unlock_rules=()):
    target = runecrafting_data.get(target_id)
    if not target:
        return player_data, 0, False, "Unknown Runecrafting target"
    locked_reasons = runecrafting_locked_reasons_pure(
        player_data,
        target_id,
        runecrafting_data,
        pouch_data,
        quest_unlock_rules,
    )
    if locked_reasons:
        return player_data, 0, False, "Runecrafting target is locked: " + ", ".join(locked_reasons)

    data = _copy_player_data_with_nested(player_data)
    _repair_degraded_pouches(data, pouch_data)
    inventory = data["inventory"]
    level = _positive_int(data.get("runecrafting_level", 1), 1)
    kind = target.get("kind")
    roll_iter = iter(rolls or ())

    if kind == "standard":
        base_capacity = runecrafting_standard_base_capacity_pure(data, target, runecrafting_data)
        capacity = base_capacity + runecrafting_pouch_capacity_pure(data, pouch_data)
        essence_items = tuple(target.get("essence_items", ()))
        essence_item = next((item for item in essence_items if _positive_int(inventory.get(item, 0), 0) > 0), "")
        essence_to_use = min(capacity, _positive_int(inventory.get(essence_item, 0), 0))
        inventory[essence_item] = inventory.get(essence_item, 0) - essence_to_use
        used = essence_to_use
        if used <= 0:
            return player_data, 0, False, "No essence available"
        output_count = _standard_output_count(target, level, used, roll_iter)
        output_item = str(target.get("output_item"))
        inventory[output_item] = inventory.get(output_item, 0) + output_count
        if used > base_capacity:
            _degrade_used_pouches(data, pouch_data, used - base_capacity)
        return data, float(target.get("base_exp", 0.0)) * used, True, f"+{output_count} {output_item}"

    if kind == "combination":
        base_capacity = 26
        capacity = base_capacity + runecrafting_pouch_capacity_pure(data, pouch_data)
        pure_count = _positive_int(inventory.get("Pure essence", 0), 0)
        component_rune = str(target.get("component_rune"))
        consumed_talisman = str(target.get("consumed_talisman"))
        craft_count = min(capacity, pure_count, _positive_int(inventory.get(component_rune, 0), 0))
        imbued = bool(data.get("magic_imbue_active", False))
        if craft_count <= 0 or (not imbued and inventory.get(consumed_talisman, 0) <= 0):
            return player_data, 0, False, "Missing combination materials"
        inventory["Pure essence"] = inventory.get("Pure essence", 0) - craft_count
        inventory[component_rune] = inventory.get(component_rune, 0) - craft_count
        if imbued:
            data["magic_imbue_active"] = False
        else:
            inventory[consumed_talisman] = inventory.get(consumed_talisman, 0) - 1
        output_item = str(target.get("output_item"))
        charges = binding_necklace_charges_pure(data)
        if charges > 0:
            output_count = craft_count
            remaining = charges - 1
            if remaining > 0:
                data.setdefault("item_charges", {})["Binding necklace"] = remaining
            else:
                data.setdefault("item_charges", {}).pop("Binding necklace", None)
                data.setdefault("equipment", {}).pop("neck", None)
        else:
            try:
                roll = float(next(roll_iter))
            except (StopIteration, TypeError, ValueError):
                roll = 0.0
            output_count = min(craft_count, int(max(0.0, min(roll, 0.999999999)) * craft_count) + 1)
        inventory[output_item] = inventory.get(output_item, 0) + output_count
        if craft_count > base_capacity:
            _degrade_used_pouches(data, pouch_data, craft_count - base_capacity)
        return data, float(target.get("base_exp", 0.0)) * craft_count, True, f"+{output_count} {output_item}"

    if kind == "tiara":
        talisman = str(target.get("talisman_item"))
        inventory["Tiara"] = inventory.get("Tiara", 0) - 1
        inventory[talisman] = inventory.get(talisman, 0) - 1
        output_item = str(target.get("output_item"))
        inventory[output_item] = inventory.get(output_item, 0) + 1
        return data, float(target.get("base_exp", 0.0)), True, f"+1 {output_item}"

    if kind == "hood_feed":
        input_item = str(target.get("input_item"))
        altar_id = str(target.get("altar_id"))
        inventory[input_item] = inventory.get(input_item, 0) - 1
        if altar_id == "elemental":
            data = apply_wicked_hood_upgrade_pure(
                data, elemental_fed=True
            )
        elif altar_id == "omni":
            data = apply_wicked_hood_upgrade_pure(data, omni_fed=True)
        else:
            data = apply_wicked_hood_upgrade_pure(
                data, fed_altars=(altar_id,)
            )
        return data, 0, True, f"{input_item} fed"

    return player_data, 0, False, "Unsupported Runecrafting target"
