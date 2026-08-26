"""logic_pure_claims.py - split out of logic_pure.py; see that module's header."""

from typing import Iterable, Mapping, Optional

from ..core.skill_registry import get_skill, trainable_skill_definitions

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

from .logic_pure_quest import (
    _apply_skill_xp_reward,
)

from .logic_pure_state import (
    _copy_player_data_with_nested,
    _positive_int,
    quest_completed_pure,
)


def claim_locked_reasons_pure(player_data, claim_id, claim_data):
    claim = claim_data.get(claim_id)
    if not claim:
        return ("unknown claim",)
    state = (player_data.get("claims", {}) or {}).get(claim_id, {})
    if isinstance(state, Mapping) and state.get("claimed"):
        return ("claimed",)
    reasons = []
    required_quest = claim.get("required_quest")
    if required_quest and not quest_completed_pure(player_data, str(required_quest)):
        reasons.append("quest")
    required_tools = claim.get("required_tools", ()) or ()
    if isinstance(required_tools, Mapping):
        required_tools = required_tools.items()
    for tool in required_tools:
        if not isinstance(tool, (tuple, list)) or len(tool) < 2:
            continue
        tool_name, quantity = tool[0], _positive_int(tool[1], 0)
        if (
            isinstance(tool_name, str)
            and quantity > 0
            and not _has_quest_tool(player_data, tool_name, quantity)
        ):
            reasons.append(tool_name)
    required_level = _positive_int(claim.get("required_runecrafting_level", 1), 1)
    if required_level > 1 and _positive_int(player_data.get("runecrafting_level", 1), 1) < required_level:
        reasons.append(f"Runecrafting level {required_level}")
    if str(claim.get("claim_type", "item")) == "skill_reward":
        skill_options = tuple(claim.get("skill_options", ()) or ())
        if len(skill_options) == 1:
            skill_id = str(skill_options[0])
            minimum_level = _positive_int(claim.get("minimum_level", 1), 1)
            if _skill_level_for_reward(player_data, skill_id) < minimum_level:
                skill = get_skill(skill_id)
                display_name = skill.display_name if skill is not None else skill_id.replace("_", " ").title()
                reasons.append(f"{display_name} level {minimum_level}")
    required_diary_tier = claim.get("required_diary_tier")
    if isinstance(required_diary_tier, str) and required_diary_tier:
        diary_state = player_data.get("achievement_diaries", {})
        claimed_tiers = (
            diary_state.get("claimed_tiers", ()) if isinstance(diary_state, Mapping) else ()
        )
        if not isinstance(claimed_tiers, Iterable):
            claimed_tiers = ()
        if required_diary_tier not in claimed_tiers:
            reasons.append("diary tier")
    return tuple(reasons)


def _claim_bundle_items(claim):
    raw_items = claim.get("items", ()) if isinstance(claim, Mapping) else ()
    if isinstance(raw_items, Mapping):
        candidates = raw_items.items()
    elif isinstance(raw_items, Iterable) and not isinstance(raw_items, (str, bytes)):
        candidates = raw_items
    else:
        candidates = ()
    items = []
    for raw_item in candidates:
        if isinstance(raw_item, Mapping):
            name = raw_item.get("item_name", raw_item.get("item"))
            quantity = raw_item.get("quantity", raw_item.get("amount", 1))
        elif isinstance(raw_item, (tuple, list)) and len(raw_item) >= 2:
            name, quantity = raw_item[0], raw_item[1]
        else:
            continue
        if not isinstance(name, str) or not name:
            continue
        quantity = _positive_int(quantity, 0)
        if quantity <= 0:
            continue
        items.append((name, quantity))
    return tuple(items)


def _claim_skill_options(claim):
    configured = tuple(claim.get("skill_options", ()) or ())
    if configured:
        return configured
    return tuple(skill.id for skill in trainable_skill_definitions())


def claim_rows_pure(player_data, claim_data):
    rows = []
    for claim_id, claim in claim_data.items():
        reasons = claim_locked_reasons_pure(player_data, claim_id, claim_data)
        claimed = reasons == ("claimed",)
        eligible = not reasons
        items = _claim_bundle_items(claim)
        rows.append(
            {
                "claim_id": claim_id,
                "display_name": claim.get("display_name", claim_id),
                "claim_type": claim.get("claim_type", "item"),
                "item_name": claim.get("item_name", claim_id),
                "quantity": _positive_int(claim.get("quantity", 1), 1),
                "items": items,
                "xp_amount": float(claim.get("xp_amount", 0) or 0),
                "skill_options": (
                    _claim_skill_options(claim)
                    if claim.get("claim_type") in {"xp_lamp", "skill_reward"}
                    else ()
                ),
                "minimum_level": _positive_int(claim.get("minimum_level", 1), 1),
                "eligible": eligible,
                "claimed": claimed,
                "locked_reasons": reasons,
            }
        )
    return tuple(rows)


def _skill_level_for_reward(player_data, skill_id):
    skill = get_skill(skill_id)
    level_key = skill.level_key if skill is not None else f"{skill_id}_level"
    return _positive_int(player_data.get(level_key, 1), 1)


def apply_claim_pure(player_data, claim_id, claim_data, selected_skill_id=None):
    if claim_locked_reasons_pure(player_data, claim_id, claim_data):
        return player_data, False
    claim = claim_data.get(claim_id)
    if not claim:
        return player_data, False
    data = _copy_player_data_with_nested(player_data)
    claim_type = str(claim.get("claim_type", "item"))
    if claim_type in {"xp_lamp", "skill_reward"}:
        if claim_type == "xp_lamp":
            skill_id = selected_skill_id
            skill_options = _claim_skill_options(claim)
            if not isinstance(skill_id, str) or skill_id not in skill_options:
                return player_data, False
        else:
            skill_options = tuple(claim.get("skill_options", ()) or ())
            if len(skill_options) != 1:
                return player_data, False
            skill_id = str(skill_options[0])
        minimum_level = _positive_int(claim.get("minimum_level", 1), 1)
        if _skill_level_for_reward(player_data, skill_id) < minimum_level:
            return player_data, False
        amount = float(claim.get("xp_amount", 0) or 0)
        if amount <= 0:
            return player_data, False
        _apply_skill_xp_reward(data, skill_id, amount)
        if claim_type == "skill_reward":
            inventory = data.setdefault("inventory", {})
            for item_name, quantity in _claim_bundle_items(claim):
                inventory[item_name] = inventory.get(item_name, 0) + quantity
    elif claim_type == "item_bundle":
        bundle_items = _claim_bundle_items(claim)
        if not bundle_items:
            return player_data, False
        inventory = data.setdefault("inventory", {})
        for item_name, quantity in bundle_items:
            inventory[item_name] = inventory.get(item_name, 0) + quantity
    else:
        item_name = str(claim.get("item_name", claim_id))
        quantity = _positive_int(claim.get("quantity", 1), 1)
        data["inventory"][item_name] = data["inventory"].get(item_name, 0) + quantity
    data.setdefault("claims", {}).setdefault(claim_id, {})["claimed"] = True
    return data, True
