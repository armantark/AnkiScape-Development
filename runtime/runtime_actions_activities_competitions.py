from __future__ import annotations

from ..core.constants import EQUIPMENT_DATA
from ..data.trouble_brewing_data import TROUBLE_BREWING_ACTIVITY_ID
from ..logic.trouble_brewing_logic import (
    apply_trouble_brewing_review_pure,
    trouble_brewing_view_pure,
)
from ..data.pest_control_data import PEST_CONTROL_ACTIVITY_ID
from ..logic.pest_control_logic import (
    apply_pest_control_review_pure,
    pest_control_view_pure,
)
from ..data.conquest_data import CONQUEST_ACTIVITY_ID
from ..logic.conquest_logic import apply_conquest_review_pure
from ..data.barbarian_assault_data import BARBARIAN_ASSAULT_ACTIVITY_ID
from ..logic.barbarian_assault_logic import apply_barbarian_assault_review_pure
from ..data.soul_wars_data import SOUL_WARS_ACTIVITY_ID
from ..logic.soul_wars_logic import apply_soul_wars_review_pure
from ..data.duel_arena_data import DUEL_ARENA_ACTIVITY_ID
from ..logic.duel_arena_logic import apply_duel_arena_review_pure
from ..data.clan_wars_data import CLAN_WARS_ACTIVITY_ID
from ..data.troll_invasion_data import TROLL_INVASION_ACTIVITY_ID
from ..data.crucible_data import CRUCIBLE_ACTIVITY_ID
from ..logic.clan_wars_logic import apply_clan_wars_review_pure
from ..logic.troll_invasion_logic import apply_troll_invasion_review_pure
from ..data.mobilising_armies_data import MOBILISING_ARMIES_ACTIVITY_ID
from ..logic.mobilising_armies_logic import apply_mobilising_armies_review_pure
from ..logic.crucible_logic import apply_crucible_review_pure
from ..data.stealing_creation_data import STEALING_CREATION_ACTIVITY_ID
from ..logic.stealing_creation_logic import apply_stealing_creation_review_pure
from .runtime_actions_shared import (
    _award_skill_xp_rows,
    _record_action,
    _refresh_combat_levels,
    _stop_card_at_slice_boundary,
)
from .runtime_actions_context import RuntimeActionContext


def _handle_stealing_creation_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_stealing_creation_review_pure(
        ctx.player_data,
        ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Stealing Creation unavailable",
            str(result.get("reason", "Enter Stealing Creation before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        STEALING_CREATION_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if result.get("complete"):
        ctx.deactivate_current_skill()
    ctx.show_activity_gain(
        str(result.get("status", "Stealing Creation duty complete"))
    )
    return True


def handle_trouble_brewing_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    view = trouble_brewing_view_pure(ctx.player_data)
    duty = str(view.get("policy", {}).get("duty", "water"))
    session = view.get("session")
    if isinstance(session, dict):
        duty = str(session.get("duty", duty))
    updated, result = apply_trouble_brewing_review_pure(
        ctx.player_data,
        productive=productive,
        duty=duty,
        opponent_roll=ctx.random_random(),
        sabotage_roll=ctx.random_random(),
    )
    if result.get("reason"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Trouble Brewing unavailable",
            str(result["reason"]),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    skill_rows = {
        "agility": ("agility_exp", "Agility"),
        "cooking": ("cooking_exp", "Cooking"),
        "crafting": ("crafting_exp", "Crafting"),
        "firemaking": ("firemaking_exp", "Firemaking"),
        "woodcutting": ("woodcutting_exp", "Woodcutting"),
    }
    skill_xp = dict(result.get("skill_xp") or {})
    total_gained = _award_skill_xp_rows(ctx, skill_xp, skill_rows)
    _record_action(
        ctx,
        "utility",
        TROUBLE_BREWING_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        primary_xp=sum(float(value or 0.0) for value in skill_xp.values()),
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if total_gained > 0:
        ctx.show_exp(total_gained)
    ctx.show_activity_gain(str(result.get("message", "Trouble Brewing beat resolved")))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_pest_control_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    view = pest_control_view_pure(ctx.player_data)
    duty: str | None = None
    session = view.get("pest_control")
    if isinstance(session, dict) and session.get("automation_mode") == "advanced":
        duty = str(session.get("duty", duty))
    updated, ok, result = apply_pest_control_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        duty=duty,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Pest Control unavailable",
            str(result.get("reason", "Enter Pest Control before training.")),
        )
        return False
    xp_rewards = dict(result.get("xp_rewards") or {})
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        PEST_CONTROL_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("died") else None,
        primary_xp=sum(float(amount or 0.0) for amount in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    xp_total = sum(float(amount or 0.0) for amount in xp_rewards.values())
    if xp_total > 0:
        ctx.show_exp(xp_total)
    ctx.show_activity_gain(
        str(result.get("message") or result.get("status") or "Pest Control beat resolved")
    )
    _stop_card_at_slice_boundary(ctx, result)
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_conquest_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_conquest_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
    )
    if not ok:
        if productive:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Conquest unavailable",
                str(result.get("reason", "Enter Conquest before training.")),
            )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        CONQUEST_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        failure_kind="safe_loss" if result.get("terminal") and not result.get("won") else None,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("message") or "Conquest turn exchange resolved")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_barbarian_assault_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_barbarian_assault_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Barbarian Assault unavailable",
            str(result.get("reason", "Enter Barbarian Assault before training.")),
        )
        return False
    xp_rewards = dict(result.get("xp_rewards") or {})
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        BARBARIAN_ASSAULT_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("died") else None,
        primary_xp=sum(float(amount or 0.0) for amount in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    xp_total = sum(float(amount or 0.0) for amount in xp_rewards.values())
    if xp_total > 0:
        ctx.show_exp(xp_total)
    ctx.show_activity_gain(
        str(
            result.get("message")
            or result.get("status")
            or "Barbarian Assault beat resolved"
        )
    )
    _stop_card_at_slice_boundary(ctx, result, "wave_completed", "queen_started")
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_soul_wars_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_soul_wars_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
        equipment_data=EQUIPMENT_DATA,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Soul Wars unavailable",
            str(result.get("reason", "Enter Soul Wars before training.")),
        )
        return False
    xp_rewards = dict(result.get("xp_rewards") or {})
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        SOUL_WARS_ACTIVITY_ID,
        productive,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("died") else None,
        primary_xp=sum(float(amount or 0.0) for amount in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    xp_total = sum(float(amount or 0.0) for amount in xp_rewards.values())
    if xp_total > 0:
        ctx.show_exp(xp_total)
    ctx.show_activity_gain(
        str(result.get("message") or "Soul Wars beat resolved")
    )
    _stop_card_at_slice_boundary(ctx, result)
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_duel_arena_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_duel_arena_review_pure(
        ctx.player_data,
        ctx.random_random,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Duel Arena unavailable",
            str(result.get("reason", "Enter a free challenge duel before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        DUEL_ARENA_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        failure_kind="safe_death" if result.get("outcome") == "loss" else None,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("message") or "Duel exchange resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_clan_wars_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_clan_wars_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
        productive=productive,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Clan Wars unavailable",
            str(result.get("reason", "Enter a Clan Wars portal before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    combat = dict(result.get("combat") or {})
    xp_rewards = dict(combat.get("xp_rewards") or {})
    # A death is this activity's failure mode, so it must be recorded as one.
    # Telemetry only keeps a failure kind on an unsuccessful action.
    died = bool(combat.get("died"))
    _record_action(
        ctx,
        "utility",
        CLAN_WARS_ACTIVITY_ID,
        productive and not died,
        expected_success_chance=1.0,
        failure_kind=(
            "dangerous_death"
            if died and not combat.get("safe_death")
            else "safe_death"
            if died
            else None
        ),
        primary_xp=sum(float(value or 0.0) for value in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("message") or "Clan Wars combat beat resolved")
    )
    _stop_card_at_slice_boundary(ctx, result)
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_troll_invasion_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_troll_invasion_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
        productive=productive,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Troll Invasion unavailable",
            str(result.get("reason", "Enter Troll Invasion before training it.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    combat = result.get("combat") or {}
    combat_xp = result.get("xp_rewards") or combat.get("xp_rewards") or {}
    skill_xp = result.get("skill_xp") or {}
    skill_rows = {
        "construction": ("construction_exp", "Construction"),
        "crafting": ("crafting_exp", "Crafting"),
        "firemaking": ("firemaking_exp", "Firemaking"),
    }
    awarded_skill_xp = _award_skill_xp_rows(ctx, skill_xp, skill_rows)
    died = bool(combat.get("died"))
    actions_resolved = max(0, int(result.get("actions_resolved", 1)))
    primary_xp = awarded_skill_xp + sum(
        float(value or 0.0) for value in combat_xp.values()
    )
    # Like Clan Wars, an Again answer records a non-productive attempt even
    # though the activity state does not advance.
    recorded_actions = max(1, actions_resolved)
    for _ in range(recorded_actions):
        _record_action(
            ctx,
            "utility",
            TROLL_INVASION_ACTIVITY_ID,
            productive and not died,
            expected_success_chance=1.0,
            failure_kind="safe_death" if died else None,
            primary_xp=primary_xp / max(1, actions_resolved),
        )
    _refresh_combat_levels(ctx, combat_xp)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if awarded_skill_xp > 0:
        ctx.show_exp(awarded_skill_xp)
    ctx.show_activity_gain(str(result.get("message") or "Troll Invasion beat resolved"))
    _stop_card_at_slice_boundary(ctx, result)
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_mobilising_armies_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_mobilising_armies_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Mobilising Armies unavailable",
            str(result.get("reason", "Enter a scenario before commanding it.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        MOBILISING_ARMIES_ACTIVITY_ID,
        productive and not result.get("stalled"),
        expected_success_chance=1.0,
        failure_kind="squad_lost" if result.get("squad_lost") else None,
        output_items={str(result["loot"]): 1} if result.get("loot") else None,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("message") or "Mobilising Armies order resolved")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_crucible_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_crucible_review_pure(
        ctx.player_data,
        ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
        productive=productive,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "The Crucible unavailable",
            str(result.get("reason", "Enter the Crucible arena before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    combat = dict(result.get("combat") or {})
    xp_rewards = dict(combat.get("xp_rewards") or {})
    # A death is this activity's failure mode, so it must be recorded as one.
    # Outside the Supreme Champion event every death is a dangerous one.
    died = bool(combat.get("died"))
    _record_action(
        ctx,
        "utility",
        CRUCIBLE_ACTIVITY_ID,
        productive and not died,
        expected_success_chance=1.0,
        failure_kind=(
            "dangerous_death"
            if died and not combat.get("safe_death")
            else "safe_death"
            if died
            else None
        ),
        primary_xp=sum(float(value or 0.0) for value in xp_rewards.values()),
    )
    _refresh_combat_levels(ctx, xp_rewards)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("message") or "Crucible arena beat resolved")
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


_handle_stealing_creation_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_trouble_brewing_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_pest_control_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_conquest_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_barbarian_assault_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_soul_wars_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_duel_arena_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_clan_wars_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_troll_invasion_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_mobilising_armies_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_crucible_answer.__module__ = f"{__package__}.runtime_actions_activities"
