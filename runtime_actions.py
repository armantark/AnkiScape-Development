"""Runtime review-action handlers.

This module owns review action mutations without importing Anki or Qt. The
package entrypoint passes UI/save/achievement callbacks through
``RuntimeActionContext`` so ``__init__.py`` can stay focused on hooks and state
coordination.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

try:
    from .constants import (
        BIRD_NEST_DROP_CHANCE,
        BIRD_NEST_DROP_TABLE,
        BIRD_NEST_OPEN_TABLES,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        DEFAULT_COMBAT_TARGET,
        DEFAULT_COOKING_TARGET,
        DEFAULT_FIREMAKING_TARGET,
        DEFAULT_FLETCHING_TARGET,
        DEFAULT_FISHING_TARGET,
        DEFAULT_HUNTER_TARGET,
        DEFAULT_MINING_TARGET,
        DEFAULT_RUNECRAFTING_TARGET,
        DEFAULT_UTILITY_ACTIVITY,
        DEFAULT_WOODCUTTING_TARGET,
        EQUIPMENT_DATA,
        EXP_TABLE,
        FIREMAKING_DATA,
        FISHING_DATA,
        HUNTER_DATA,
        FLETCHING_DATA,
        GLORY_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_TABLE,
        MINING_BONUS_ITEM_DATA,
        MINING_PICKAXE_DATA,
        ORE_DATA,
        QUEST_DATA,
        QUEST_UNLOCK_RULES,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
        WOODCUTTING_AXE_DATA,
    )
    from .logic_pure import (
        apply_combat_burst_pure,
        apply_cooking_action_pure,
        apply_crafting_pure,
        apply_firemaking_action_pure,
        apply_fishing_action_pure,
        apply_fletching_pure,
        apply_hunter_action_pure,
        apply_quest_combat_encounter_pure,
        apply_mining_action_pure,
        apply_open_bird_nests_pure,
        apply_quest_progress_pure,
        apply_runecrafting_action_pure,
        apply_smithing_action_pure,
        apply_utility_activity_pure,
        apply_woodcutting_action_pure,
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_cooking_success_probability_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        calculate_hunter_success_probability_pure,
        calculate_mining_success_probability_pure,
        calculate_woodcutting_success_probability_pure,
        calculate_new_level,
        can_chop_woodcutting_target_pure,
        can_craft_item_pure,
        can_attempt_quest_review_pure,
        can_progress_quest_pure,
        can_runecraft_target_pure,
        can_smith_item_pure,
        can_start_quest_pure,
        cooking_target_locked_reasons_pure,
        combat_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        equipment_bonus_state_pure,
        firemaking_target_locked_reasons_pure,
        fishing_method_locked_reasons_pure,
        fletching_target_locked_reasons_pure,
        has_cooking_materials_pure,
        has_crafting_materials_pure,
        has_firemaking_materials_pure,
        has_fishing_bait_pure,
        has_hunter_materials_pure,
        has_ring_of_forging_pure,
        hunter_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        normalize_xp_rewards_pure,
        quest_current_stage_blocker_reasons_pure,
        quest_current_stage_blockers_pure,
        quest_current_stage_resolvable_combat_blockers_pure,
        record_action_telemetry_pure,
        consume_ring_of_forging_charge_pure,
        smithing_success_probability_pure,
        utility_activity_locked_reasons_pure,
    )
    from .skill_registry import get_skill
    from .smithing_data import DEFAULT_SMITHING_TARGET
except ImportError:  # pragma: no cover - flat import path used by tests
    from constants import (  # type: ignore
        BIRD_NEST_DROP_CHANCE,
        BIRD_NEST_DROP_TABLE,
        BIRD_NEST_OPEN_TABLES,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COOKING_DATA,
        CRAFTING_DATA,
        DEFAULT_COMBAT_TARGET,
        DEFAULT_COOKING_TARGET,
        DEFAULT_FIREMAKING_TARGET,
        DEFAULT_FLETCHING_TARGET,
        DEFAULT_FISHING_TARGET,
        DEFAULT_HUNTER_TARGET,
        DEFAULT_MINING_TARGET,
        DEFAULT_RUNECRAFTING_TARGET,
        DEFAULT_UTILITY_ACTIVITY,
        DEFAULT_WOODCUTTING_TARGET,
        EQUIPMENT_DATA,
        EXP_TABLE,
        FIREMAKING_DATA,
        FISHING_DATA,
        HUNTER_DATA,
        FLETCHING_DATA,
        GLORY_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_TABLE,
        MINING_BONUS_ITEM_DATA,
        MINING_PICKAXE_DATA,
        ORE_DATA,
        QUEST_DATA,
        QUEST_UNLOCK_RULES,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        SMITHING_DATA,
        TREE_DATA,
        UTILITY_ACTIVITY_DATA,
        WOODCUTTING_AXE_DATA,
    )
    from logic_pure import (  # type: ignore
        apply_combat_burst_pure,
        apply_cooking_action_pure,
        apply_crafting_pure,
        apply_firemaking_action_pure,
        apply_fishing_action_pure,
        apply_fletching_pure,
        apply_hunter_action_pure,
        apply_quest_combat_encounter_pure,
        apply_mining_action_pure,
        apply_open_bird_nests_pure,
        apply_quest_progress_pure,
        apply_runecrafting_action_pure,
        apply_smithing_action_pure,
        apply_utility_activity_pure,
        apply_woodcutting_action_pure,
        best_mining_pickaxe_pure,
        best_woodcutting_axe_pure,
        calculate_cooking_success_probability_pure,
        calculate_firemaking_success_probability_pure,
        calculate_fishing_success_probability_pure,
        calculate_hunter_success_probability_pure,
        calculate_mining_success_probability_pure,
        calculate_woodcutting_success_probability_pure,
        calculate_new_level,
        can_chop_woodcutting_target_pure,
        can_craft_item_pure,
        can_attempt_quest_review_pure,
        can_progress_quest_pure,
        can_runecraft_target_pure,
        can_smith_item_pure,
        can_start_quest_pure,
        cooking_target_locked_reasons_pure,
        combat_target_locked_reasons_pure,
        eligible_fishing_fish_pure,
        equipment_bonus_state_pure,
        firemaking_target_locked_reasons_pure,
        fishing_method_locked_reasons_pure,
        fletching_target_locked_reasons_pure,
        has_cooking_materials_pure,
        has_crafting_materials_pure,
        has_firemaking_materials_pure,
        has_fishing_bait_pure,
        has_hunter_materials_pure,
        has_ring_of_forging_pure,
        hunter_target_locked_reasons_pure,
        mining_target_locked_reasons_pure,
        normalize_xp_rewards_pure,
        quest_current_stage_blocker_reasons_pure,
        quest_current_stage_blockers_pure,
        quest_current_stage_resolvable_combat_blockers_pure,
        record_action_telemetry_pure,
        consume_ring_of_forging_charge_pure,
        smithing_success_probability_pure,
        utility_activity_locked_reasons_pure,
    )
    from skill_registry import get_skill  # type: ignore
    from smithing_data import DEFAULT_SMITHING_TARGET  # type: ignore

try:
    from . import inventory_pure
    from .item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES
except ImportError:  # pragma: no cover - exercised via flat imports in tests
    import inventory_pure
    from item_values import ITEM_VALUES, STACKABLE_ITEM_NAMES


@dataclass
class RuntimeActionContext:
    player_data: dict[str, Any]
    random_random: Callable[[], float]
    show_error_message: Callable[[str, str], None]
    deactivate_current_skill: Callable[[], None]
    award_skill_exp: Callable[[str, float], float]
    award_hidden_skill_exp: Callable[[str, str, float], None]
    level_up_check: Callable[[str, dict[str, Any]], None]
    check_achievements: Callable[[dict[str, Any]], None]
    save_player_data: Callable[[], None]
    refresh_skill_availability: Callable[[], None]
    refresh_skill_availability_partial: Callable[..., None]
    can_smith_any: Callable[[], bool]
    show_exp: Callable[[float], None]
    show_activity_gain: Callable[[str], None]
    implemented_exp_keys_snapshot: Callable[[], dict[str, float]]
    show_quest_exp_delta: Callable[[dict[str, float]], None]
    review_action_multiplier: int = 1


# Handler keys that draw from / fill the 28-slot carried inventory, mapped to the
# player_data key holding their selected target. Utility (no-XP batching) and
# quests do not take carried teeth, so they are absent.
_OVERLAY_TARGET_KEYS = {
    "mining": "current_ore",
    "woodcutting": "current_tree",
    "fishing": "current_fishing",
    "hunter": "current_hunter",
    "cooking": "current_cooking",
    "crafting": "current_craft",
    "fletching": "current_fletch",
    "firemaking": "current_firemaking",
    "smithing": "current_smith",
    "runecrafting": "current_runecrafting",
}
# v1 treats carried outputs as unstackable (one slot each); the real cache
# `stackable` set is wired with the loot/bag slice.
_OVERLAY_STACKABLE_NAMES: frozenset[str] = frozenset()


def _set_carried_target_map(player_data: dict[str, Any], map_key: str, target_id: str, value) -> None:
    container = player_data.get(map_key)
    if not isinstance(container, dict):
        container = {}
    if value:
        container[target_id] = value
    else:
        container.pop(target_id, None)
    player_data[map_key] = container


def run_answer_with_carried_overlay(ctx: RuntimeActionContext, handler_key: str, handler) -> bool:
    """Run one skilling tick through the 28-slot carried overlay.

    Before the tick, `carried_bank_run_gate_pure` decides whether the pack is full
    (``churn`` reached 28): if so, this answer is spent on a bank-run — the handler
    is not called, no XP is awarded, and the run/view/churn reset. Otherwise the
    handler acts, and the tick's churn (max slots gained/consumed) and any kept
    output fold into the per-target view. Handlers without carried teeth (utility,
    quests) run untouched.
    """
    target_key = _OVERLAY_TARGET_KEYS.get(handler_key)
    if target_key is None:
        return handler(ctx)

    player_data = ctx.player_data
    target_id = str(player_data.get(target_key, ""))
    keep = inventory_pure.carried_keep_for(player_data, target_id)
    view = (player_data.get("carried_inventory") or {}).get(target_id, {})
    churn = (player_data.get("carried_churn") or {}).get(target_id, 0)
    bank_run = player_data.get("skilling_bank_run", {})
    # A carried bag raises the bank-run threshold for its material (fewer trips).
    owned_bags = {
        bag for bag in inventory_pure.BAG_DEFINITIONS
        if int((player_data.get("inventory") or {}).get(bag, 0) or 0) > 0
    }
    capacity = inventory_pure.effective_carried_capacity(view, owned_bags)

    new_state, new_view, new_churn, event, act = inventory_pure.carried_bank_run_gate_pure(
        view, churn, keep, _OVERLAY_STACKABLE_NAMES, target_id, bank_run,
        inventory_pure.SKILLING_BANK_RUN_REVIEWS, capacity,
    )

    if not act:
        player_data["skilling_bank_run"] = new_state
        _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
        _set_carried_target_map(player_data, "carried_churn", target_id, new_churn)
        ctx.show_activity_gain("Bank run — restocked supplies (+1 review)")
        ctx.save_player_data()
        return True

    inv_before = dict(player_data.get("inventory", {}) or {})
    result = handler(ctx)
    if result is not False:
        player_data["skilling_bank_run"] = new_state
        # Drop bypasses the pack entirely (no churn, no banking, fastest XP);
        # Keep accrues churn and folds the product in. Consumption skills are Keep
        # with an empty view, so their input churn still bites.
        if keep:
            inv_after = player_data.get("inventory", {}) or {}
            churn_delta = inventory_pure.carried_action_churn_pure(inv_before, inv_after, _OVERLAY_STACKABLE_NAMES)
            gains = inventory_pure.inventory_delta_gains(inv_before, inv_after)
            new_view = inventory_pure.carried_fold_gains_pure(new_view, gains, _OVERLAY_STACKABLE_NAMES)
            _set_carried_target_map(player_data, "carried_inventory", target_id, new_view)
            _set_carried_target_map(player_data, "carried_churn", target_id, new_churn + churn_delta)
        ctx.save_player_data()
    return result


def missing_materials_text(requirements: dict[str, int], inventory: dict[str, Any]) -> str:
    missing = [
        f"{amount} {material}"
        for material, amount in requirements.items()
        if inventory.get(material, 0) < amount
    ]
    return ", ".join(missing) if missing else "materials"


def fishing_materials_text(method_spec: dict[str, Any], inventory: dict[str, Any]) -> str:
    bait_options = tuple(method_spec.get("bait_options") or ())
    if not bait_options:
        return "materials"
    if len(bait_options) == 1:
        bait = bait_options[0]
        return f"1 {bait}"
    return "any of " + ", ".join(f"1 {bait}" for bait in bait_options)


def _award_action_xp_rewards(ctx: RuntimeActionContext, xp_rewards: Any, owner_skill_id: str) -> float:
    rewards = normalize_xp_rewards_pure({"xp_rewards": xp_rewards})
    if not rewards:
        return 0.0
    primary_skill_id = owner_skill_id if any(reward.get("skill_id") == owner_skill_id for reward in rewards) else str(rewards[0].get("skill_id", ""))
    primary_amount = 0.0
    for reward in rewards:
        skill_id = str(reward.get("skill_id", ""))
        try:
            amount = float(reward.get("amount", 0.0) or 0.0)
        except (TypeError, ValueError):
            amount = 0.0
        if not skill_id or amount <= 0:
            continue
        skill = get_skill(skill_id)
        if skill is None:
            continue
        if skill.implemented:
            gained = ctx.award_skill_exp(skill.exp_key, amount)
            ctx.level_up_check(skill.display_name, ctx.player_data)
        else:
            ctx.award_hidden_skill_exp(skill.exp_key, skill.level_key, amount)
            gained = amount
        if skill_id == primary_skill_id:
            primary_amount = gained
    return primary_amount


def _combined_success_probability(probabilities: Any) -> float:
    dry_probability = 1.0
    for probability in probabilities:
        try:
            chance = float(probability)
        except (TypeError, ValueError):
            chance = 0.0
        dry_probability *= 1.0 - max(0.0, min(chance, 1.0))
    return max(0.0, min(1.0 - dry_probability, 1.0))


def _record_action(
    ctx: RuntimeActionContext,
    skill_id: str,
    action_id: str,
    success: bool,
    *,
    expected_success_chance: Optional[float] = None,
    output_item: Optional[str] = None,
    output_qty: int = 1,
    output_items: Optional[dict[str, int]] = None,
    failure_kind: Optional[str] = None,
) -> None:
    record_action_telemetry_pure(
        ctx.player_data,
        skill_id,
        action_id,
        success,
        expected_success_chance=expected_success_chance,
        output_item=output_item,
        output_qty=output_qty,
        output_items=output_items,
        failure_kind=failure_kind,
    )


_COMBAT_EXP_SKILLS = {
    "attack_exp": "attack",
    "strength_exp": "strength",
    "defense_exp": "defense",
    "constitution_exp": "constitution",
    "ranged_exp": "ranged",
    "magic_exp": "magic",
}


def _combat_review_ticks(ctx: RuntimeActionContext) -> int:
    try:
        multiplier = int(ctx.review_action_multiplier)
    except (TypeError, ValueError):
        multiplier = 1
    return COMBAT_BURST_TICKS * max(1, multiplier)


def _refresh_combat_levels(ctx: RuntimeActionContext, xp_rewards: Any) -> None:
    if not isinstance(xp_rewards, dict):
        return
    for exp_key, amount in xp_rewards.items():
        try:
            gained = float(amount or 0.0)
        except (TypeError, ValueError):
            gained = 0.0
        if gained <= 0:
            continue
        skill = get_skill(_COMBAT_EXP_SKILLS.get(str(exp_key), ""))
        if skill is None:
            continue
        ctx.player_data[skill.level_key] = calculate_new_level(
            ctx.player_data.get(skill.exp_key, 0),
            ctx.player_data.get(skill.level_key, 1),
            EXP_TABLE,
        )
        ctx.level_up_check(skill.display_name, ctx.player_data)


def handle_combat_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target_id = player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    if target_id not in COMBAT_ENEMY_DATA:
        target_id = DEFAULT_COMBAT_TARGET
        player_data["current_combat_target"] = target_id

    locked_reasons = combat_target_locked_reasons_pure(
        player_data,
        target_id,
        COMBAT_ENEMY_DATA,
        equipment_data=EQUIPMENT_DATA,
    )
    if locked_reasons:
        enemy = COMBAT_ENEMY_DATA.get(target_id, {})
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Combat unavailable",
            f"{enemy.get('display_name', target_id)} cannot be fought yet: {', '.join(locked_reasons)}.",
        )
        return False

    new_data, ok, result = apply_combat_burst_pure(
        player_data,
        COMBAT_ENEMY_DATA,
        EQUIPMENT_DATA,
        ticks=_combat_review_ticks(ctx),
        rng=ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        reasons = result.get("locked_reasons") if isinstance(result, dict) else None
        reason_text = ", ".join(reasons) if reasons else "the selected target is unavailable"
        ctx.show_error_message("Combat unavailable", f"Combat has been switched off because {reason_text}.")
        return False

    player_data.update(new_data)
    drops = result.get("drops", {}) if isinstance(result, dict) else {}
    if not isinstance(drops, dict):
        drops = {}
    # Loot filter (owner: no auto-hoarding every tiny drop). The burst already
    # added the drops to the flat inventory, so leave below-value junk by removing
    # it again; stackables, coins, and unknown-value items are kept.
    if drops:
        threshold = player_data.get("loot_value_threshold", inventory_pure.DEFAULT_LOOT_VALUE_THRESHOLD)
        drops, left = inventory_pure.filter_loot_pure(drops, ITEM_VALUES, threshold, STACKABLE_ITEM_NAMES)
        if left:
            inventory = player_data.get("inventory", {}) or {}
            for item_name, amount in left.items():
                inventory[item_name] = max(0, int(inventory.get(item_name, 0) or 0) - amount)
            player_data["inventory"] = inventory
    _record_action(
        ctx,
        "combat",
        str(result.get("target_id", target_id)),
        True,
        expected_success_chance=1.0,
        output_items={str(item): int(amount) for item, amount in drops.items() if isinstance(item, str)},
    )
    _refresh_combat_levels(ctx, result.get("xp_rewards", {}))
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()

    xp_total = 0.0
    for amount in (result.get("xp_rewards", {}) or {}).values():
        try:
            xp_total += float(amount or 0.0)
        except (TypeError, ValueError):
            pass
    if xp_total > 0:
        ctx.show_exp(xp_total)

    display_name = str(result.get("display_name") or "enemy")
    if result.get("died"):
        ctx.show_activity_gain(f"Defeated by {display_name}; gear moved to grave")
    elif result.get("killed"):
        ctx.show_activity_gain(f"Defeated {display_name}")
    else:
        ctx.show_activity_gain(
            f"{display_name}: {int(result.get('player_damage', 0) or 0)} damage dealt, "
            f"{int(result.get('enemy_lifepoints', 0) or 0)} LP left"
        )
    return True


def _spec_output_items(spec: dict[str, Any], fallback_item: Optional[str] = None) -> dict[str, int]:
    outputs = spec.get("outputs")
    if isinstance(outputs, dict) and outputs:
        return {str(item): int(amount) for item, amount in outputs.items() if item and isinstance(amount, int) and amount > 0}
    output_item = fallback_item or spec.get("output_item")
    if not output_item:
        return {}
    try:
        output_qty = int(spec.get("output_qty", 1))
    except (TypeError, ValueError):
        output_qty = 1
    return {str(output_item): max(output_qty, 1)}


def _refresh_smithing_and_crafting_availability(ctx: RuntimeActionContext) -> None:
    player_data = ctx.player_data
    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        ctx.refresh_skill_availability_partial(ctx.can_smith_any(), can_craft_any)
    except Exception:
        pass

    ctx.refresh_skill_availability()


def handle_crafting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    item = player_data.get("current_craft", "form_pot_unfired")
    spec = CRAFTING_DATA.get(item)
    display_name = spec.get("display_name", item) if spec else item
    if not spec:
        ctx.show_error_message("Unknown crafting target", "Choose a valid Crafting target before reviewing.")
        return False

    player_level = player_data.get("crafting_level", 1)
    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Crafting to make {display_name}.")
        return False

    if not has_crafting_materials_pure(item, player_data["inventory"], CRAFTING_DATA):
        missing = missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to craft {display_name}, so Crafting has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    new_inv, base_exp, ok = apply_crafting_pure(item, player_data["inventory"], CRAFTING_DATA)
    if not ok:
        missing = missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to craft {display_name}, so Crafting has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    player_data["inventory"] = new_inv
    _record_action(ctx, "crafting", item, True, expected_success_chance=1.0, output_items=_spec_output_items(spec))
    exp_gained = ctx.award_skill_exp("crafting_exp", base_exp)
    ctx.level_up_check("Crafting", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()

    try:
        can_craft_any = any(
            can_craft_item_pure(player_data.get("crafting_level", 1), player_data.get("inventory", {}), item_name, CRAFTING_DATA)
            for item_name in CRAFTING_DATA.keys()
        )
        ctx.refresh_skill_availability_partial(ctx.can_smith_any(), can_craft_any)
    except Exception:
        pass

    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_utility_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    activity_key = player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
    if activity_key not in UTILITY_ACTIVITY_DATA:
        activity_key = DEFAULT_UTILITY_ACTIVITY
        player_data["current_utility"] = activity_key
    spec = UTILITY_ACTIVITY_DATA[activity_key]
    display_name = spec.get("display_name", activity_key)

    locked_reasons = utility_activity_locked_reasons_pure(player_data, activity_key, UTILITY_ACTIVITY_DATA, QUEST_UNLOCK_RULES)
    quest_locked = tuple(reason for reason in locked_reasons if reason != "materials")
    if quest_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Activity locked",
            f"{display_name} requires {', '.join(quest_locked)}, so it's been switched off. "
            "Open the AnkiScape menu to pick another activity.",
        )
        return False

    if locked_reasons:
        requirements = spec.get("requirements", {})
        ctx.deactivate_current_skill()
        if requirements:
            missing = missing_materials_text(requirements, player_data.get("inventory", {}))
            ctx.show_error_message(
                "Out of materials",
                f"You're out of {missing} for {display_name}, so it's been switched off. "
                "Open the AnkiScape menu to pick another activity.",
            )
        else:
            ctx.show_error_message(
                "Activity switched off",
                f"{display_name} can't run right now, so it's been switched off. "
                "Open the AnkiScape menu to pick another activity.",
            )
        return False

    if activity_key == "open_bird_nest":
        batch_size = 28
        try:
            batch_size = max(int(spec.get("batch_size", 28)), 1)
        except (TypeError, ValueError):
            batch_size = 28
        rolls = [ctx.random_random() for _ in range(batch_size)]
        new_inv, ok, processed, _outputs = apply_open_bird_nests_pure(
            player_data.get("inventory", {}),
            BIRD_NEST_OPEN_TABLES,
            rolls=rolls,
            batch_size=batch_size,
        )
        if not ok:
            ctx.show_error_message("Unavailable activity", f"{display_name} is not available right now.")
            return False
        player_data["inventory"] = new_inv
        _record_action(ctx, "utility", activity_key, True, expected_success_chance=1.0, output_items=_outputs)
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        ctx.show_activity_gain(f"Opened {processed} bird nest{'s' if processed != 1 else ''}")
        return True

    new_inv, _exp, ok, processed = apply_utility_activity_pure(
        activity_key,
        player_data.get("inventory", {}),
        UTILITY_ACTIVITY_DATA,
    )
    if not ok:
        ctx.show_error_message("Unavailable activity", f"{display_name} is not available right now.")
        return False

    player_data["inventory"] = new_inv
    output_items = {item: amount * max(int(processed), 0) for item, amount in _spec_output_items(spec).items()}
    _record_action(ctx, "utility", activity_key, True, expected_success_chance=1.0, output_items=output_items)
    if spec.get("deactivate_after_run"):
        ctx.deactivate_current_skill()
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()

    outputs = spec.get("outputs", {})
    if isinstance(outputs, dict) and outputs:
        if spec.get("deactivate_after_run"):
            ctx.show_activity_gain(str(display_name).replace("Buy ", "Bought ", 1))
        else:
            total_outputs = sum(max(int(amount), 1) for amount in outputs.values() if isinstance(amount, int))
            gained = total_outputs * max(int(processed), 0)
            if gained > 0:
                ctx.show_activity_gain(f"+{gained} items")
    else:
        output_item = str(spec.get("output_item", activity_key))
        try:
            output_qty = max(int(spec.get("output_qty", 1)), 1)
        except (TypeError, ValueError):
            output_qty = 1
        gained = output_qty * max(int(processed), 0)
        if gained > 0:
            ctx.show_activity_gain(f"+{gained} {output_item}")
    return True


def handle_fletching_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_fletch", DEFAULT_FLETCHING_TARGET)
    if target not in FLETCHING_DATA:
        target = DEFAULT_FLETCHING_TARGET
        player_data["current_fletch"] = target
    spec = FLETCHING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("fletching_level", 1)
    locked_reasons = fletching_target_locked_reasons_pure(player_data, target, FLETCHING_DATA, QUEST_UNLOCK_RULES)
    unlock_locked = tuple(
        reason
        for reason in locked_reasons
        if reason not in {"materials"} and not str(reason).startswith("Fletching level")
    )
    if unlock_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fletching target locked",
            f"{display_name} requires {', '.join(unlock_locked)}, so Fletching has been switched off.",
        )
        return False

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Fletching to make {display_name}.")
        return False

    new_inv, base_exp, ok = apply_fletching_pure(target, player_data["inventory"], FLETCHING_DATA)
    if not ok:
        missing = missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to make {display_name}, so Fletching has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    player_data["inventory"] = new_inv
    _record_action(ctx, "fletching", target, True, expected_success_chance=1.0, output_items=_spec_output_items(spec))
    xp_rewards = normalize_xp_rewards_pure(spec, "fletching", base_exp)
    exp_gained = _award_action_xp_rewards(ctx, xp_rewards, "fletching")
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_firemaking_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_firemaking", DEFAULT_FIREMAKING_TARGET)
    if target not in FIREMAKING_DATA:
        target = DEFAULT_FIREMAKING_TARGET
        player_data["current_firemaking"] = target
    spec = FIREMAKING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("firemaking_level", 1)
    quest_locked = tuple(
        reason
        for reason in firemaking_target_locked_reasons_pure(player_data, target, FIREMAKING_DATA, QUEST_UNLOCK_RULES)
        if reason not in {"materials"} and not str(reason).startswith("Firemaking level")
    )
    if quest_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Firemaking target locked",
            f"{display_name} requires {', '.join(quest_locked)}, so Firemaking has been switched off.",
        )
        return False

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Firemaking to burn {display_name}.")
        return False

    if not has_firemaking_materials_pure(target, player_data.get("inventory", {}), FIREMAKING_DATA):
        missing = missing_materials_text(spec.get("requirements", {}), player_data.get("inventory", {}))
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to burn {display_name}, so Firemaking has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    expected_success = calculate_firemaking_success_probability_pure(player_level, spec)
    new_inv, base_exp, ok, _output_item = apply_firemaking_action_pure(
        target,
        player_data.get("inventory", {}),
        FIREMAKING_DATA,
        player_level,
        ctx.random_random(),
    )
    if not ok:
        _record_action(ctx, "firemaking", target, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
        return True

    player_data["inventory"] = new_inv
    _record_action(
        ctx,
        "firemaking",
        target,
        True,
        expected_success_chance=expected_success,
        output_item=_output_item,
    )
    exp_gained = ctx.award_skill_exp("firemaking_exp", base_exp)
    ctx.level_up_check("Firemaking", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_fishing_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_fishing", DEFAULT_FISHING_TARGET)
    if target not in FISHING_DATA:
        target = DEFAULT_FISHING_TARGET
        player_data["current_fishing"] = target
    spec = FISHING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("fishing_level", 1)
    strength_level = player_data.get("strength_level", 1)
    agility_level = player_data.get("agility_level", 1)
    inventory = player_data.get("inventory", {})

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Fishing to {str(display_name).lower()}.")
        return False

    if not has_fishing_bait_pure(inventory, spec):
        missing = fishing_materials_text(spec, inventory)
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to {str(display_name).lower()}, so Fishing has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    eligible = eligible_fishing_fish_pure(spec, player_level, strength_level, agility_level)
    if not eligible:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Insufficient level",
            f"You do not meet the side-level requirements for {display_name}, so Fishing has been switched off.",
        )
        return False
    locked_reasons = fishing_method_locked_reasons_pure(player_data, target, FISHING_DATA, QUEST_UNLOCK_RULES)
    if locked_reasons:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fishing target locked",
            f"{display_name} requires {', '.join(locked_reasons)}, so Fishing has been switched off.",
        )
        return False

    expected_success = _combined_success_probability(
        calculate_fishing_success_probability_pure(player_level, fish)
        for fish in eligible
    )
    rolls = [ctx.random_random() for _ in eligible]
    new_inv, base_exp, ok, _output_item, xp_rewards = apply_fishing_action_pure(
        target,
        inventory,
        FISHING_DATA,
        player_level,
        strength_level,
        agility_level,
        rolls=rolls,
    )
    if not ok:
        _record_action(ctx, "fishing", target, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
        return True

    player_data["inventory"] = new_inv
    _record_action(
        ctx,
        "fishing",
        target,
        True,
        expected_success_chance=expected_success,
        output_item=_output_item,
    )
    exp_gained = _award_action_xp_rewards(
        ctx,
        xp_rewards or ({"skill_id": "fishing", "amount": base_exp},),
        "fishing",
    )
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_hunter_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_hunter", DEFAULT_HUNTER_TARGET)
    if target not in HUNTER_DATA:
        target = DEFAULT_HUNTER_TARGET
        player_data["current_hunter"] = target
    spec = HUNTER_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("hunter_level", 1)
    inventory = player_data.get("inventory", {})

    locked_reasons = hunter_target_locked_reasons_pure(player_data, target, HUNTER_DATA, QUEST_UNLOCK_RULES)
    unlock_locked = tuple(
        reason
        for reason in locked_reasons
        if reason not in {"materials"} and not str(reason).startswith("Hunter level")
    )
    if unlock_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Hunter target locked",
            f"{display_name} requires {', '.join(unlock_locked)}, so Hunter has been switched off.",
        )
        return False

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Hunter to {str(display_name).lower()}.")
        return False

    if not has_hunter_materials_pure(target, inventory, HUNTER_DATA):
        missing = missing_materials_text(spec.get("requirements", {}), inventory)
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to {str(display_name).lower()}, so Hunter has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    expected_success = calculate_hunter_success_probability_pure(player_level, spec)
    new_inv, base_exp, ok, _output_item, xp_rewards = apply_hunter_action_pure(
        target,
        inventory,
        HUNTER_DATA,
        player_level,
        ctx.random_random(),
    )
    if not ok:
        _record_action(ctx, "hunter", target, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
        return True

    player_data["inventory"] = new_inv
    _record_action(
        ctx,
        "hunter",
        target,
        True,
        expected_success_chance=expected_success,
        output_items=_spec_output_items(spec, _output_item),
    )
    player_data["hunter_success_count"] = player_data.get("hunter_success_count", 0) + 1
    exp_gained = _award_action_xp_rewards(
        ctx,
        xp_rewards or ({"skill_id": "hunter", "amount": base_exp},),
        "hunter",
    )
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_cooking_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_cooking", DEFAULT_COOKING_TARGET)
    if target not in COOKING_DATA:
        target = DEFAULT_COOKING_TARGET
        player_data["current_cooking"] = target
    spec = COOKING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("cooking_level", 1)
    quest_locked = tuple(
        reason
        for reason in cooking_target_locked_reasons_pure(player_data, target, COOKING_DATA, QUEST_UNLOCK_RULES)
        if reason not in {"materials"} and not str(reason).startswith("Cooking level")
    )
    if quest_locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Cooking target locked",
            f"{display_name} requires {', '.join(quest_locked)}, so Cooking has been switched off.",
        )
        return False

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Cooking to {str(display_name).lower()}.")
        return False

    if not has_cooking_materials_pure(target, player_data.get("inventory", {}), COOKING_DATA):
        missing = missing_materials_text(spec.get("requirements", {}), player_data.get("inventory", {}))
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to {str(display_name).lower()}, so Cooking has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    expected_success = calculate_cooking_success_probability_pure(player_level, spec)
    new_inv, base_exp, ok, output_item, burned = apply_cooking_action_pure(
        target,
        player_data.get("inventory", {}),
        COOKING_DATA,
        player_level,
        ctx.random_random(),
    )
    if not ok:
        return False

    player_data["inventory"] = new_inv
    if burned:
        _record_action(
            ctx,
            "cooking",
            target,
            False,
            expected_success_chance=expected_success,
            output_item=output_item,
            failure_kind="burn",
        )
        player_data["cooking_burn_count"] = player_data.get("cooking_burn_count", 0) + 1
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        if output_item:
            ctx.show_activity_gain(f"+1 {output_item}")
        return True

    _record_action(
        ctx,
        "cooking",
        target,
        True,
        expected_success_chance=expected_success,
        output_item=output_item,
    )
    player_data["cooking_success_count"] = player_data.get("cooking_success_count", 0) + 1
    exp_gained = ctx.award_skill_exp("cooking_exp", base_exp)
    ctx.level_up_check("Cooking", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_exp(exp_gained)
    return True


def handle_runecrafting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_runecrafting", DEFAULT_RUNECRAFTING_TARGET)
    if target not in RUNECRAFTING_DATA:
        target = DEFAULT_RUNECRAFTING_TARGET
        player_data["current_runecrafting"] = target
    spec = RUNECRAFTING_DATA[target]
    display_name = spec.get("display_name", target)
    player_level = player_data.get("runecrafting_level", 1)

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Runecrafting for {display_name}.")
        return False

    rolls = [ctx.random_random() for _ in range(64)]
    new_data, base_exp, ok, message = apply_runecrafting_action_pure(
        player_data,
        target,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        rolls=rolls,
        quest_unlock_rules=QUEST_UNLOCK_RULES,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Runecrafting unavailable",
            f"{display_name} cannot run right now, so Runecrafting has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    player_data.update(new_data)
    _record_action(ctx, "runecrafting", target, True, expected_success_chance=1.0)
    exp_gained = ctx.award_skill_exp("runecrafting_exp", base_exp)
    ctx.level_up_check("Runecrafting", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if exp_gained > 0:
        ctx.show_exp(exp_gained)
    elif message:
        ctx.show_activity_gain(str(message))
    return True


def handle_quest_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    quest_id = player_data.get("current_quest", "rune_mysteries")
    if quest_id not in QUEST_DATA:
        quest_id = "rune_mysteries"
        player_data["current_quest"] = quest_id
    quest = QUEST_DATA[quest_id]
    stage_blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
    combat_blockers = quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, QUEST_DATA)
    if combat_blockers:
        new_data, ok, result = apply_quest_combat_encounter_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            combat_blockers[0].get("encounter_id"),
            ticks=_combat_review_ticks(ctx),
            rng=ctx.random_random,
            equipment_data=EQUIPMENT_DATA,
        )
        if not ok:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Quest combat blocked",
                f"{quest.get('display_name', quest_id)} cannot resolve this battle yet.",
            )
            return False
        player_data.update(new_data)
        _record_action(ctx, "quest", f"{quest_id}:{result.get('encounter_id', 'combat')}", True, expected_success_chance=1.0)
        _refresh_combat_levels(ctx, result.get("xp_rewards", {}))
        ctx.check_achievements(player_data)
        ctx.save_player_data()
        ctx.refresh_skill_availability()
        xp_total = 0.0
        for amount in (result.get("xp_rewards", {}) or {}).values():
            try:
                xp_total += float(amount or 0.0)
            except (TypeError, ValueError):
                pass
        if xp_total > 0:
            ctx.show_exp(xp_total)
        display_name = str(result.get("display_name") or "combat encounter")
        quantity_text = str(result.get("quantity_text") or "")
        if result.get("reason") == "quest_combat_bank_run":
            remaining = int(result.get("bank_run_reviews_remaining", 0) or 0)
            ctx.show_activity_gain(f"{display_name}: bank run ({remaining} reviews remaining)")
        elif result.get("died"):
            ctx.show_activity_gain(f"Defeated by {display_name}; gear moved to grave")
        elif result.get("killed"):
            ctx.show_activity_gain(f"Defeated {display_name}{quantity_text}")
        else:
            ctx.show_activity_gain(
                f"{display_name}: {int(result.get('player_damage', 0) or 0)} damage dealt, "
                f"{int(result.get('enemy_lifepoints', 0) or 0)} LP left"
            )
        return True
    stage_blocker_reasons = tuple(str(blocker.get("reason")) for blocker in stage_blockers)
    if stage_blocker_reasons:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest blocked",
            f"{quest.get('display_name', quest_id)} is blocked: {', '.join(stage_blocker_reasons)}. "
            "Questing has been switched off until the current stage requirements are met.",
        )
        return False
    if not can_start_quest_pure(player_data, quest_id, QUEST_DATA):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest unavailable",
            f"{quest.get('display_name', quest_id)} cannot progress right now, so questing has been switched off.",
        )
        return False

    exp_before = ctx.implemented_exp_keys_snapshot()
    new_data, ok, completed_now = apply_quest_progress_pure(player_data, quest_id, QUEST_DATA)
    if not ok:
        stage_blocker_reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        if stage_blocker_reasons:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Quest blocked",
                f"{quest.get('display_name', quest_id)} is blocked: {', '.join(stage_blocker_reasons)}. "
                "Questing has been switched off until the current stage requirements are met.",
            )
        return False
    player_data.update(new_data)
    _record_action(ctx, "quest", quest_id, True, expected_success_chance=1.0)
    if completed_now:
        ctx.show_quest_exp_delta(exp_before)
        ctx.deactivate_current_skill()
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if completed_now:
        display_name = str(quest.get("display_name", quest_id))
        ctx.show_activity_gain(f"{display_name} complete")
        ctx.show_error_message(
            "Quest complete",
            f"{display_name} is complete, so questing has been switched off. "
            "Open the AnkiScape menu to pick another quest.",
        )
    else:
        state = player_data.get("quests", {}).get(quest_id, {})
        ctx.show_activity_gain(f"{quest.get('display_name', quest_id)} {state.get('progress', 0)}/{quest.get('stages', 1)}")
    return True


def handle_smithing_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target = player_data.get("current_smith", DEFAULT_SMITHING_TARGET)
    if target not in SMITHING_DATA:
        target = DEFAULT_SMITHING_TARGET
        player_data["current_smith"] = target
    spec = SMITHING_DATA[target]
    display_name = spec.get("display_name", spec.get("output_item", target))
    player_level = player_data["smithing_level"]

    if player_level < spec["level"]:
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Smithing to make {display_name}.")
        return False

    has_forging_ring = has_ring_of_forging_pure(player_data)
    expected_success_chance = smithing_success_probability_pure(
        target,
        spec,
        player_level,
        has_ring_of_forging=has_forging_ring,
    )
    roll = ctx.random_random() if expected_success_chance < 1.0 else 0.0
    new_inv, base_exp, processed, output_item, failed = apply_smithing_action_pure(
        target,
        player_data["inventory"],
        SMITHING_DATA,
        player_level,
        roll,
        has_ring_of_forging=has_forging_ring,
    )
    if not processed:
        missing = missing_materials_text(spec.get("requirements", {}), player_data["inventory"])
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Out of materials",
            f"You need {missing} to make {display_name}, so Smithing has been switched off. "
            "Open the AnkiScape menu to pick another target.",
        )
        return False

    player_data["inventory"] = new_inv
    if target == "smelt_iron_bar" and has_forging_ring:
        ring_data = consume_ring_of_forging_charge_pure(player_data)
        player_data["equipment"] = ring_data.get("equipment", {}) or {}
        player_data["item_charges"] = ring_data.get("item_charges", {}) or {}

    if failed:
        _record_action(
            ctx,
            "smithing",
            target,
            False,
            expected_success_chance=expected_success_chance,
            failure_kind="smelt_fail",
        )
        ctx.save_player_data()
        _refresh_smithing_and_crafting_availability(ctx)
        ctx.show_activity_gain("The ore was too impure")
        return True

    _record_action(
        ctx,
        "smithing",
        target,
        True,
        expected_success_chance=expected_success_chance,
        output_items=_spec_output_items(spec, output_item),
    )
    exp_gained = ctx.award_skill_exp("smithing_exp", base_exp)
    ctx.level_up_check("Smithing", player_data)
    ctx.check_achievements(player_data)
    ctx.save_player_data()

    _refresh_smithing_and_crafting_availability(ctx)
    ctx.show_exp(exp_gained)
    return True


def handle_woodcutting_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    tree = player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET)
    if tree not in TREE_DATA:
        tree = DEFAULT_WOODCUTTING_TARGET
        player_data["current_tree"] = tree
    spec = TREE_DATA[tree]
    player_level = player_data.get("woodcutting_level", 1)

    if player_level < spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {spec['level']} Woodcutting to chop {spec.get('display_name', tree)}.")
        return False

    axe_spec = best_woodcutting_axe_pure(
        player_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    )
    if axe_spec is None:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "No usable hatchet",
            "You need a usable hatchet to train Woodcutting. Woodcutting has been switched off.",
        )
        return False

    r_action = ctx.random_random()
    r_nest_drop = ctx.random_random()
    r_nest_type = ctx.random_random()
    expected_success = calculate_woodcutting_success_probability_pure(player_level, spec, axe_spec)
    new_inv, base_exp, ok, output_item, nest_item = apply_woodcutting_action_pure(
        tree,
        player_data.get("inventory", {}),
        TREE_DATA,
        player_level,
        axe_spec,
        r_action,
        r_nest_drop,
        r_nest_type,
        BIRD_NEST_DROP_TABLE,
        BIRD_NEST_DROP_CHANCE,
    )
    if ok:
        if "logs_cut_today" not in player_data:
            player_data["logs_cut_today"] = 0
        player_data["logs_cut_today"] += 1
        player_data["inventory"] = new_inv
        output_items: dict[str, int] = {}
        for item_name in (output_item, nest_item):
            if item_name:
                output_items[item_name] = output_items.get(item_name, 0) + 1
        _record_action(
            ctx,
            "woodcutting",
            tree,
            True,
            expected_success_chance=expected_success,
            output_items=output_items,
        )
        exp_gained = ctx.award_skill_exp("woodcutting_exp", base_exp)
        ctx.level_up_check("Woodcutting", player_data)
        ctx.check_achievements(player_data)
        ctx.save_player_data()
    else:
        _record_action(ctx, "woodcutting", tree, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()

    ctx.show_exp(base_exp if not ok else exp_gained)
    return True


def handle_mining_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    ore = player_data.get("current_ore", DEFAULT_MINING_TARGET)
    if ore not in ORE_DATA:
        ore = DEFAULT_MINING_TARGET
        player_data["current_ore"] = ore
    ore_spec = ORE_DATA[ore]
    player_level = player_data["mining_level"]

    if player_level < ore_spec.get("level", 1):
        ctx.show_error_message("Insufficient level", f"You need level {ore_spec['level']} Mining to mine {ore_spec.get('display_name', ore)}.")
        return False

    pickaxe_spec = best_mining_pickaxe_pure(
        player_level,
        player_data.get("inventory", {}),
        player_data.get("toolbelt", {}),
        MINING_PICKAXE_DATA,
    )
    if pickaxe_spec is None:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Missing pickaxe",
            "You need a usable pickaxe to train Mining. Mining has been switched off.",
        )
        return False
    locked_reasons = mining_target_locked_reasons_pure(player_data, ore, ORE_DATA, MINING_PICKAXE_DATA, QUEST_UNLOCK_RULES)
    if locked_reasons:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Mining target locked",
            f"{ore_spec.get('display_name', ore)} requires {', '.join(locked_reasons)}, so Mining has been switched off.",
        )
        return False

    bonus_state = equipment_bonus_state_pure(player_data.get("equipment", {}) or {}, MINING_BONUS_ITEM_DATA)
    gem_drop_chance = GLORY_GEM_DROP_CHANCE if bonus_state["has_glory"] else INCIDENTAL_GEM_DROP_CHANCE
    r_action = ctx.random_random()
    r_output = ctx.random_random()
    r_gem_chance = ctx.random_random()
    r_gem_pick = ctx.random_random()
    expected_success = calculate_mining_success_probability_pure(player_level, ore_spec, pickaxe_spec)

    new_inv, base_exp, ok, output_item, gem, extra_output = apply_mining_action_pure(
        ore,
        player_data.get("inventory", {}),
        ORE_DATA,
        player_level,
        pickaxe_spec,
        r_action,
        r_output,
        r_gem_chance,
        r_gem_pick,
        INCIDENTAL_GEM_DROP_TABLE,
        gem_drop_chance,
        bonus_state["varrock_armour_tier"],
    )
    if ok:
        if "ores_mined_today" not in player_data:
            player_data["ores_mined_today"] = 0
        player_data["ores_mined_today"] += 1
        player_data["inventory"] = new_inv
        output_items: dict[str, int] = {}
        for item_name in (output_item, gem, extra_output):
            if item_name:
                output_items[item_name] = output_items.get(item_name, 0) + 1
        _record_action(
            ctx,
            "mining",
            ore,
            True,
            expected_success_chance=expected_success,
            output_items=output_items,
        )
        exp_gained = ctx.award_skill_exp("mining_exp", base_exp)
        ctx.level_up_check("Mining", player_data)
        ctx.check_achievements(player_data)
        ctx.save_player_data()

        ctx.refresh_skill_availability()
        ctx.show_exp(exp_gained)
    else:
        _record_action(ctx, "mining", ore, False, expected_success_chance=expected_success, failure_kind="dry")
        ctx.save_player_data()
    return True


def _can_start_fletching_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_fletch", DEFAULT_FLETCHING_TARGET)
    return not fletching_target_locked_reasons_pure(
        ctx.player_data,
        target,
        FLETCHING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_firemaking_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_firemaking", DEFAULT_FIREMAKING_TARGET)
    return not firemaking_target_locked_reasons_pure(
        ctx.player_data,
        target,
        FIREMAKING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_fishing_action(ctx: RuntimeActionContext) -> bool:
    return not fishing_method_locked_reasons_pure(
        ctx.player_data,
        ctx.player_data.get("current_fishing", DEFAULT_FISHING_TARGET),
        FISHING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_hunter_action(ctx: RuntimeActionContext) -> bool:
    return not hunter_target_locked_reasons_pure(
        ctx.player_data,
        ctx.player_data.get("current_hunter", DEFAULT_HUNTER_TARGET),
        HUNTER_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_cooking_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_cooking", DEFAULT_COOKING_TARGET)
    return not cooking_target_locked_reasons_pure(
        ctx.player_data,
        target,
        COOKING_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_runecrafting_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_runecrafting", DEFAULT_RUNECRAFTING_TARGET)
    return can_runecraft_target_pure(
        ctx.player_data,
        target,
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_combat_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_combat_target", DEFAULT_COMBAT_TARGET)
    return not combat_target_locked_reasons_pure(
        ctx.player_data,
        target,
        COMBAT_ENEMY_DATA,
        equipment_data=EQUIPMENT_DATA,
    )


def _can_start_quest_action(ctx: RuntimeActionContext) -> bool:
    quest_id = ctx.player_data.get("current_quest", "rune_mysteries")
    return can_attempt_quest_review_pure(ctx.player_data, quest_id, QUEST_DATA)


def _can_start_crafting_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_craft", "form_pot_unfired")
    return can_craft_item_pure(
        ctx.player_data.get("crafting_level", 1),
        ctx.player_data.get("inventory", {}),
        target,
        CRAFTING_DATA,
    )


def _can_start_smithing_action(ctx: RuntimeActionContext) -> bool:
    target = ctx.player_data.get("current_smith", DEFAULT_SMITHING_TARGET)
    return can_smith_item_pure(
        ctx.player_data.get("smithing_level", 1),
        ctx.player_data.get("inventory", {}),
        target,
        SMITHING_DATA,
    )


def _can_start_utility_action(ctx: RuntimeActionContext) -> bool:
    activity_key = ctx.player_data.get("current_utility", DEFAULT_UTILITY_ACTIVITY)
    return not utility_activity_locked_reasons_pure(
        ctx.player_data,
        activity_key,
        UTILITY_ACTIVITY_DATA,
        QUEST_UNLOCK_RULES,
    )


def _can_start_woodcutting_action(ctx: RuntimeActionContext) -> bool:
    return can_chop_woodcutting_target_pure(
        ctx.player_data.get("woodcutting_level", 1),
        ctx.player_data.get("current_tree", DEFAULT_WOODCUTTING_TARGET),
        TREE_DATA,
        ctx.player_data.get("inventory", {}),
        ctx.player_data.get("toolbelt", {}),
        WOODCUTTING_AXE_DATA,
    )


def _can_start_mining_action(ctx: RuntimeActionContext) -> bool:
    return not mining_target_locked_reasons_pure(
        ctx.player_data,
        ctx.player_data.get("current_ore", DEFAULT_MINING_TARGET),
        ORE_DATA,
        MINING_PICKAXE_DATA,
        QUEST_UNLOCK_RULES,
    )


CAN_START_HANDLERS: dict[str, Callable[[RuntimeActionContext], bool]] = {
    "mining": _can_start_mining_action,
    "woodcutting": _can_start_woodcutting_action,
    "smithing": _can_start_smithing_action,
    "crafting": _can_start_crafting_action,
    "fletching": _can_start_fletching_action,
    "firemaking": _can_start_firemaking_action,
    "fishing": _can_start_fishing_action,
    "hunter": _can_start_hunter_action,
    "cooking": _can_start_cooking_action,
    "runecrafting": _can_start_runecrafting_action,
    "combat": _can_start_combat_action,
    "utility": _can_start_utility_action,
    "quest": _can_start_quest_action,
}


ANSWER_HANDLERS: dict[str, Callable[[RuntimeActionContext], bool]] = {
    "mining": handle_mining_answer,
    "woodcutting": handle_woodcutting_answer,
    "smithing": handle_smithing_answer,
    "crafting": handle_crafting_answer,
    "fletching": handle_fletching_answer,
    "firemaking": handle_firemaking_answer,
    "fishing": handle_fishing_answer,
    "hunter": handle_hunter_answer,
    "cooking": handle_cooking_answer,
    "runecrafting": handle_runecrafting_answer,
    "combat": handle_combat_answer,
    "utility": handle_utility_answer,
    "quest": handle_quest_answer,
}


def can_start_action(ctx: RuntimeActionContext, handler_key: Optional[str]) -> bool:
    checker = CAN_START_HANDLERS.get(str(handler_key or ""))
    return checker(ctx) if checker is not None else True


def answer_handler_for_key(handler_key: Optional[str]) -> Optional[Callable[[RuntimeActionContext], bool]]:
    return ANSWER_HANDLERS.get(str(handler_key or ""))
