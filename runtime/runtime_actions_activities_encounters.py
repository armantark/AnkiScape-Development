from __future__ import annotations

from collections.abc import Mapping
from ..core.constants import (
    COMBAT_ENEMY_DATA,
    EQUIPMENT_DATA,
)
from ..data.shades_of_mortton_data import SHADES_OF_MORTTON_ACTIVITY_ID
from ..logic.shades_of_mortton_logic import apply_shades_of_mortton_review_pure
from ..data.goblin_raids_data import GOBLIN_RAIDS_ACTIVITY_ID
from ..logic.goblin_raids_logic import apply_goblin_raids_review_pure
from ..data.fight_caves_data import FIGHT_CAVES_ACTIVITY_ID
from ..logic.fight_caves_logic import apply_fight_caves_review_pure
from ..data.dungeoneering_data import DUNGEONEERING_ACTIVITY_ID
from ..logic.dungeoneering_logic import apply_dungeoneering_review_pure
from ..data.phoenix_lair_data import PHOENIX_LAIR_ACTIVITY_ID
from ..logic.phoenix_lair_logic import apply_phoenix_lair_review_pure
from ..data.bork_data import BORK_ACTIVITY_ID
from ..data.skeletal_horror_data import SKELETAL_HORROR_ACTIVITY_ID
from ..logic.bork_logic import apply_bork_review_pure
from ..logic.skeletal_horror_logic import apply_skeletal_horror_review_pure
from ..data.barrows_data import BARROWS_ACTIVITY_ID
from ..logic.barrows_logic import apply_barrows_review_pure
from .runtime_actions_shared import (
    _award_action_xp_rewards,
    _record_action,
    _refresh_combat_levels,
    _switch_material_failure_to_bankstanding,
)
from .runtime_actions_context import RuntimeActionContext
from .runtime_actions_activities_shared import (
    _activity_session_is_current,
)


def _handle_fight_caves_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_fight_caves_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fight Cave unavailable",
            str(result.get("reason", "Enter the Fight Cave before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        FIGHT_CAVES_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Fight Cave review complete")))
    return True


def handle_dungeoneering_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_dungeoneering_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
        player_died=int(ctx.player_data.get("combat_lifepoints", 1) or 0) <= 0,
    )
    if not ok:
        state = ctx.player_data.get("dungeoneering")
        if not (
            _activity_session_is_current(ctx, DUNGEONEERING_ACTIVITY_ID)
            and isinstance(state, Mapping)
            and state.get("active")
            and state.get("session")
        ):
            _switch_material_failure_to_bankstanding(ctx)
        ctx.show_error_message(
            "Dungeoneering unavailable",
            str(result.get("reason", "Enter or resume a floor before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = tuple(
        {"skill_id": skill_id, "amount": amount}
        for skill_id, amount in dict(result.get("xp_rewards", {}) or {}).items()
    )
    primary_xp = _award_action_xp_rewards(
        ctx,
        xp_rewards,
        "dungeoneering",
    )
    _refresh_combat_levels(
        ctx,
        dict(result.get("combat_xp_rewards", {}) or {}),
    )
    _record_action(
        ctx,
        "dungeoneering",
        "starter_floor",
        True,
        expected_success_chance=1.0,
        primary_xp=primary_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if primary_xp > 0:
        ctx.show_exp(primary_xp)
    if result.get("complete"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Dungeoneering room resolved.")))
    return True


def _handle_phoenix_lair_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_phoenix_lair_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Phoenix Lair unavailable",
            str(result.get("reason", "Enter the Phoenix Lair before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        PHOENIX_LAIR_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
    )
    _refresh_combat_levels(ctx, xp_rewards)
    for exp_key, skill_name in {
        "firemaking_exp": "Firemaking",
        "fletching_exp": "Fletching",
        "crafting_exp": "Crafting",
        "slayer_exp": "Slayer",
    }.items():
        if float(xp_rewards.get(exp_key, 0.0) or 0.0) > 0:
            ctx.level_up_check(skill_name, ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Phoenix Lair review complete")))
    return True


def _handle_skeletal_horror_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_skeletal_horror_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Skeletal Horror unavailable",
            str(result.get("reason", "Enter the lair before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        SKELETAL_HORROR_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("died") else None,
        primary_xp=total_xp,
        output_items=(
            {"Clue scroll (elite)": 1}
            if result.get("clue_dropped")
            else None
        ),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    for exp_key, skill_name in {
        "slayer_exp": "Slayer",
        "prayer_exp": "Prayer",
    }.items():
        if float(xp_rewards.get(exp_key, 0.0) or 0.0) > 0:
            ctx.level_up_check(skill_name, ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(
        str(result.get("status", "Skeletal Horror review complete"))
    )
    return True


def _handle_bork_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_bork_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Bork unavailable",
            str(result.get("reason", "Enter Bork's chamber before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    output_items = {
        **dict(result.get("drops", {}) or {}),
        **dict(result.get("rare_drops", {}) or {}),
    }
    died = bool(result.get("died"))
    _record_action(
        ctx,
        "utility",
        BORK_ACTIVITY_ID,
        not died,
        expected_success_chance=1.0,
        failure_kind="death" if died else None,
        primary_xp=total_xp,
        output_items=output_items or None,
    )
    _refresh_combat_levels(ctx, xp_rewards)
    if float(xp_rewards.get("slayer_exp", 0.0) or 0.0) > 0:
        ctx.level_up_check("Slayer", ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("outcome"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Bork review complete")))
    return True


def _handle_barrows_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_barrows_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Barrows unavailable",
            str(result.get("reason", "Enter or resume Barrows before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    total_xp = sum(float(amount or 0.0) for amount in xp_rewards.values())
    _record_action(
        ctx,
        "utility",
        BARROWS_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=total_xp,
        output_items=dict(result.get("rewards", {}) or {}),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_xp > 0:
        ctx.show_exp(total_xp)
    if result.get("complete") or result.get("outcome") == "death":
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(str(result.get("status", "Barrows review complete")))
    return True


def handle_shades_of_mortton_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_shades_of_mortton_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        population=str(ctx.player_data.get("world_population_profile", "normal")),
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Shades of Mort'ton unavailable",
            str(result.get("reason", "Enter Shades of Mort'ton before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    skill_rows = {
        "crafting": ("crafting_exp", "Crafting"),
        "firemaking": ("firemaking_exp", "Firemaking"),
        "prayer": ("prayer_exp", "Prayer"),
    }
    total_gained = 0.0
    skill_xp = dict(result.get("skill_xp") or {})
    combat_xp = dict(result.get("xp_rewards") or {})
    for skill_id, amount in skill_xp.items():
        if skill_id not in skill_rows or float(amount or 0.0) <= 0:
            continue
        exp_key, display_name = skill_rows[skill_id]
        total_gained += ctx.award_skill_exp(exp_key, float(amount))
        ctx.level_up_check(display_name, ctx.player_data)
    _record_action(
        ctx,
        "utility",
        SHADES_OF_MORTTON_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        failure_kind="dangerous_combat_death" if result.get("died") else None,
        primary_xp=(
            sum(float(value or 0.0) for value in skill_xp.values())
            + sum(float(value or 0.0) for value in combat_xp.values())
        ),
    )
    _refresh_combat_levels(ctx, combat_xp)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_gained > 0:
        ctx.show_exp(total_gained)
    ctx.show_activity_gain(
        str(result.get("status") or "Shades of Mort'ton beat resolved")
    )
    return True


def handle_goblin_raids_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_goblin_raids_review_pure(
        ctx.player_data,
        ctx.random_random,
        enemy_data=COMBAT_ENEMY_DATA,
        equipment_data=EQUIPMENT_DATA,
        productive=productive,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Goblin Raids unavailable",
            str(result.get("reason", "Join a goblin raid before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    combat = dict(result.get("combat") or {})
    xp_rewards = dict(combat.get("xp_rewards") or {})
    died = bool(combat.get("died"))
    _record_action(
        ctx,
        "utility",
        GOBLIN_RAIDS_ACTIVITY_ID,
        bool(result.get("advanced")) and not died,
        expected_success_chance=1.0,
        failure_kind="death" if died else None,
        primary_xp=sum(float(value or 0.0) for value in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("message") or "Goblin Raids beat resolved")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


_handle_fight_caves_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_dungeoneering_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_phoenix_lair_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_skeletal_horror_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_bork_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_barrows_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_shades_of_mortton_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_goblin_raids_answer.__module__ = f"{__package__}.runtime_actions_activities"
