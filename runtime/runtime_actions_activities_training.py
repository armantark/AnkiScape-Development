from __future__ import annotations

from ..logic_pure.achievement_diary_events import (
    record_direct_diary_event_pure,
)
from ..logic_pure.logic_pure import (
    apply_stronghold_step_pure,
    apply_knight_waves_step_pure,
    apply_mage_arena_step_pure,
    attune_mage_arena_spell_pure,
    record_cadence_wait_telemetry_pure,
    apply_thieving_damage_pure,
    STRONGHOLD_STEP_NAMES,
    STRONGHOLD_TOTAL_STEPS,
)
from ..data.agility_data import (
    AGILITY_TARGETS_BY_ID,
    DEFAULT_AGILITY_TARGET,
)
from ..logic.agility_logic import (
    agility_maximum_failure_damage_pure,
    agility_target_locked_reasons_pure,
    apply_agility_command_pure,
    apply_agility_review_pure,
    sanitize_agility_state_pure,
)
from ..data.flash_powder_factory_data import FLASH_POWDER_FACTORY_ACTIVITY_ID
from ..logic.flash_powder_factory_logic import apply_flash_powder_factory_review_pure
from ..data.pyramid_plunder_data import PYRAMID_PLUNDER_ACTIVITY_ID
from ..logic.pyramid_plunder_logic import apply_pyramid_plunder_review_pure
from ..data.werewolf_skullball_data import WEREWOLF_SKULLBALL_ACTIVITY_ID
from ..logic.werewolf_skullball_logic import apply_werewolf_skullball_review_pure
from ..data.gnome_ball_data import GNOME_BALL_ACTIVITY_ID
from ..logic.gnome_ball_logic import apply_gnome_ball_review_pure
from ..data.fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
from ..logic.fish_flingers_logic import (
    apply_fish_flingers_review_pure,
    fishing_outfit_multiplier_pure,
)
from ..data.fishing_trawler_data import FISHING_TRAWLER_ACTIVITY_ID
from ..logic.fishing_trawler_logic import apply_fishing_trawler_review_pure
from ..data.great_orb_project_data import GREAT_ORB_PROJECT_ACTIVITY_ID
from ..logic.great_orb_project_logic import apply_great_orb_project_review_pure
from ..data.mage_training_arena_data import MAGE_TRAINING_ARENA_ACTIVITY_ID
from ..logic.mage_training_arena_logic import apply_mage_training_arena_review_pure
from ..data.ranging_guild_data import RANGING_GUILD_ACTIVITY_ID
from ..logic.ranging_guild_logic import apply_ranging_guild_review_pure
from ..logic.agility_travel import (
    agility_travel_profile_pure,
    scheduled_travel_reviews_pure,
)
from ..data.livid_farm_data import LIVID_FARM_ACTIVITY_ID
from ..logic.livid_farm_logic import apply_livid_farm_reviews_pure
from .runtime_actions_shared import (
    _award_action_xp_rewards,
    _record_action,
    _refresh_combat_levels,
    _switch_material_failure_to_bankstanding,
)
from .runtime_actions_context import RuntimeActionContext
from .runtime_actions_activities_shared import (
    STRONGHOLD_UTILITY_KEY,
    KNIGHT_WAVES_UTILITY_KEY,
    MAGE_ARENA_UTILITY_KEY,
    MAGE_ARENA_ATTUNE_PREFIX,
)


def _handle_stronghold_answer(ctx: RuntimeActionContext) -> bool:
    """One review = one Stronghold level. Awards nothing en route; the final
    level flips the state to complete and pops the boot-choice reward dialog."""
    player_data = ctx.player_data
    info = apply_stronghold_step_pure(player_data)
    if not info["advanced"]:
        # Already cleared — nothing left to do, so switch off the activity.
        ctx.deactivate_current_skill()
        return False

    _record_action(ctx, "utility", STRONGHOLD_UTILITY_KEY, True, expected_success_chance=1.0)
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()

    step = info["step"]
    if info["just_completed"]:
        ctx.deactivate_current_skill()
        ctx.show_activity_gain("Stronghold of Security cleared — claim your reward!")
        if callable(ctx.prompt_stronghold_reward):
            ctx.prompt_stronghold_reward()
    else:
        level_name = STRONGHOLD_STEP_NAMES[step - 1]
        ctx.show_activity_gain(f"Cleared the {level_name} ({step}/{STRONGHOLD_TOTAL_STEPS})")
    return True


def _handle_knight_waves_answer(ctx: RuntimeActionContext) -> bool:
    new_data, ok, info = apply_knight_waves_step_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message("Knight Waves locked", ", ".join(info.get("locked_reasons", ())))
        return False
    ctx.player_data.update(new_data)
    _record_action(ctx, "utility", KNIGHT_WAVES_UTILITY_KEY, True, expected_success_chance=1.0)
    for skill in ("Attack", "Strength", "Defence", "Constitution") if info.get("completed") else ():
        ctx.level_up_check(skill, ctx.player_data)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if info.get("completed"):
        ctx.deactivate_current_skill()
        ctx.show_activity_gain("Knight Waves complete — Chivalry and Piety unlocked")
    else:
        ctx.show_activity_gain(f"Knight Waves: {info.get('step', 0)}/8 knights defeated")
    return True


def _handle_mage_arena_answer(ctx: RuntimeActionContext) -> bool:
    new_data, ok, info = apply_mage_arena_step_pure(ctx.player_data)
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message("Mage Arena locked", ", ".join(info.get("locked_reasons", ())))
        return False
    ctx.player_data.update(new_data)
    _record_action(ctx, "utility", MAGE_ARENA_UTILITY_KEY, True, expected_success_chance=1.0)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if info.get("completed"):
        ctx.deactivate_current_skill()
        ctx.show_activity_gain(
            f"Mage Arena complete — {str(info.get('alignment', '')).title()} cape, staff, and spell attunement claimed"
        )
    else:
        ctx.show_activity_gain(f"Mage Arena: {info.get('step', 0)}/5 Kolodion forms defeated")
    return True


def _handle_mage_arena_attunement_answer(
    ctx: RuntimeActionContext,
    activity_key: str,
) -> bool:
    god_id = activity_key.removeprefix(MAGE_ARENA_ATTUNE_PREFIX)
    new_data, ok, info = attune_mage_arena_spell_pure(ctx.player_data, god_id)
    if not ok:
        ctx.deactivate_current_skill()
        reason = str(info.get("reason", "attunement unavailable")).replace("_", " ")
        ctx.show_error_message("Mage Arena attunement locked", reason)
        return False
    ctx.player_data.clear()
    ctx.player_data.update(new_data)
    _record_action(
        ctx,
        "utility",
        activity_key,
        True,
        expected_success_chance=1.0,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.deactivate_current_skill()
    ctx.show_activity_gain(
        f"{info.get('spell_name', 'God spell')} attuned for use outside the Mage Arena"
    )
    return True


def _handle_livid_farm_answer(ctx: RuntimeActionContext) -> bool:
    updated, ok, result = apply_livid_farm_reviews_pure(
        ctx.player_data,
        ctx.review_action_multiplier,
        rng=ctx.random_random,
    )
    if not ok:
        locked = tuple(result.get("locked_reasons", ()))
        missing = dict(result.get("missing_runes", {}) or {})
        if locked:
            ctx.deactivate_current_skill()
            ctx.show_error_message(
                "Livid Farm locked",
                "Livid Farm requires " + ", ".join(map(str, locked)) + ".",
            )
        elif missing:
            _switch_material_failure_to_bankstanding(ctx)
            missing_text = ", ".join(
                f"{amount} {rune_name}"
                for rune_name, amount in missing.items()
            )
            ctx.show_error_message(
                "Out of Livid Farm runes",
                f"The next atomic review needs {missing_text}. "
                "Nothing was consumed, and AnkiScape switched to Bankstanding.",
            )
        return False

    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp_rewards = dict(result.get("xp_rewards", {}) or {})
    xp_reward_rows = tuple(
        {"skill_id": skill_id, "amount": amount}
        for skill_id, amount in xp_rewards.items()
    )
    primary_xp = _award_action_xp_rewards(ctx, xp_reward_rows, "magic")
    _record_action(
        ctx,
        "utility",
        LIVID_FARM_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=primary_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    cycles = int(result.get("cycles", 0) or 0)
    points = int(result.get("points", 0) or 0)
    parts = [
        f"Livid Farm · {cycles} cycle{'s' if cycles != 1 else ''}",
        f"+{points:,} Produce",
    ]
    distractions = tuple(result.get("distractions", ()))
    completed_distractions = [
        row for row in distractions if row.get("completed")
    ]
    skipped_distractions = [
        row for row in distractions if not row.get("completed")
    ]
    if completed_distractions:
        parts.append(
            "distraction: "
            + ", ".join(str(row.get("display_name", "")) for row in completed_distractions)
        )
    if skipped_distractions:
        parts.append(
            "skipped unfunded "
            + ", ".join(str(row.get("display_name", "")) for row in skipped_distractions)
        )
    unlocks = tuple(result.get("new_unlocks", ()))
    if unlocks:
        parts.append(
            "unlocked "
            + ", ".join(str(row.get("display_name", "")) for row in unlocks)
        )
    ctx.show_activity_gain(" · ".join(parts))
    return True


def handle_flash_powder_factory_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, result = apply_flash_powder_factory_review_pure(
        ctx.player_data,
        tuple(ctx.random_random() for _ in range(4)) if productive else (),
        productive=productive,
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Flash Powder Factory unavailable",
            str(result.get("reason", "Enter the factory before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    _record_action(
        ctx,
        "utility",
        FLASH_POWDER_FACTORY_ACTIVITY_ID,
        bool(result.get("success", False)),
        expected_success_chance=1.0,
        output_items=result.get("outputs") or {},
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(
        str(result.get("status", "Flash powder circuit complete"))
    )
    if result.get("completed_activity"):
        _switch_material_failure_to_bankstanding(ctx)
    return True


def _handle_pyramid_plunder_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_pyramid_plunder_review_pure(
        ctx.player_data,
        ctx.random_random,
        rooms=max(1, int(ctx.review_action_multiplier or 1)),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Pyramid Plunder unavailable",
            str(result.get("reason", "Enter Pyramid Plunder before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp = result.get("xp") or {}
    gained = 0.0
    for skill_id, label in (
        ("thieving", "Thieving"),
        ("strength", "Strength"),
        ("runecrafting", "Runecrafting"),
    ):
        amount = float(xp.get(skill_id, 0.0) or 0.0)
        if amount > 0:
            gained += ctx.award_skill_exp(f"{skill_id}_exp", amount)
            ctx.level_up_check(label, ctx.player_data)
    _record_action(
        ctx,
        "utility",
        PYRAMID_PLUNDER_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=float(xp.get("thieving", 0.0) or 0.0),
        output_items=result.get("outputs") or {},
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Pyramid Plunder room resolved")))
    if result.get("died"):
        ctx.show_activity_gain("☠ YOU DIED — Pyramid Plunder hazard; carried pack and gear moved to grave")
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_werewolf_skullball_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_werewolf_skullball_review_pure(ctx.player_data)
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Werewolf Skullball unavailable",
            str(result.get("reason", "Enter Werewolf Skullball before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    xp = float(result.get("xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("agility_exp", xp) if xp > 0 else 0.0
    if xp > 0:
        ctx.level_up_check("Agility", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        WEREWOLF_SKULLBALL_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Werewolf Skullball run complete")))
    ctx.deactivate_current_skill()
    return True


def _handle_gnome_ball_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_gnome_ball_review_pure(
        ctx.player_data,
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Gnome Ball unavailable",
            str(result.get("reason", "Enter Gnome Ball before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    agility_xp = float(result.get("agility_xp", 0.0) or 0.0)
    ranged_xp = float(result.get("ranged_xp", 0.0) or 0.0)
    gained = 0.0
    if agility_xp > 0:
        gained += ctx.award_skill_exp("agility_exp", agility_xp)
        ctx.level_up_check("Agility", ctx.player_data)
    if ranged_xp > 0:
        gained += ctx.award_skill_exp("ranged_exp", ranged_xp)
        ctx.level_up_check("Ranged", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        GNOME_BALL_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 1.0) or 0.0
        ),
        output_items=result.get("outputs") or {},
        failure_kind="death" if result.get("died") else None,
        primary_xp=agility_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", "Gnome Ball beat resolved")))
    if result.get("died"):
        ctx.show_activity_gain("☠ YOU DIED — Gnome Ball tackle; carried pack and gear moved to grave")
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_fish_flingers_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_fish_flingers_review_pure(
        ctx.player_data,
        ctx.random_random(),
        ctx.random_random(),
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fish Flingers unavailable",
            str(result.get("reason", "Enter Fish Flingers before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    # Fish Flingers' event payout is already settled by the Darkan formula.
    # The Fishing outfit remains relevant to other Fishing activities, but
    # Darkan's FishFlingers.settle path applies no outfit multiplier here.
    awarded_xp = float(result.get("xp", 0.0) or 0.0)
    gained = 0.0
    if awarded_xp > 0:
        gained = ctx.award_skill_exp("fishing_exp", awarded_xp)
        ctx.level_up_check("Fishing", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        FISH_FLINGERS_ACTIVITY_ID,
        True,
        expected_success_chance=1.0,
        primary_xp=awarded_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Fish Flingers catch resolved"))
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_fishing_trawler_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_fishing_trawler_review_pure(
        ctx.player_data,
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Fishing Trawler unavailable",
            str(result.get("reason", "Board the trawler before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    awarded_xp = base_xp * fishing_outfit_multiplier_pure(ctx.player_data)
    gained = 0.0
    if awarded_xp > 0:
        gained = ctx.award_skill_exp("fishing_exp", awarded_xp)
        ctx.level_up_check("Fishing", ctx.player_data)
    _record_action(
        ctx,
        "utility",
        FISHING_TRAWLER_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=1.0,
        output_items=result.get("outputs") or {},
        failure_kind="sunk" if result.get("sunk") else None,
        primary_xp=awarded_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Fishing Trawler duty resolved"))
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def _handle_great_orb_project_answer(ctx: RuntimeActionContext) -> bool:
    updated, result = apply_great_orb_project_review_pure(
        ctx.player_data,
        ctx.random_random(),
        ctx.random_random(),
    )
    if not result.get("allowed"):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Great Orb Project unavailable",
            str(result.get("reason", "Enter the Great Orb Project before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = 0.0
    if base_xp > 0:
        gained = ctx.award_skill_exp("runecrafting_exp", base_xp)
        ctx.level_up_check("Runecrafting", ctx.player_data)
    output_item = str(result.get("output_item", ""))
    output_quantity = int(result.get("output_quantity", 0) or 0)
    outputs = {output_item: output_quantity} if output_item and output_quantity else {}
    _record_action(
        ctx,
        "utility",
        GREAT_ORB_PROJECT_ACTIVITY_ID,
        bool(result.get("success")),
        expected_success_chance=float(
            result.get("expected_success_chance", 0.5) or 0.0
        ),
        output_items=outputs,
        primary_xp=base_xp,
    )
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(
        str(result.get("status", "Great Orb Project round resolved"))
    )
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_mage_training_arena_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_mage_training_arena_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Mage Training Arena unavailable",
            str(result.get("reason", "Enter the Arena before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    magic_xp = float(result.get("magic_xp", 0.0) or 0.0)
    if productive and result.get("checkpoint") is False:
        record_cadence_wait_telemetry_pure(
            ctx.player_data,
            "utility",
            MAGE_TRAINING_ARENA_ACTIVITY_ID,
        )
    elif result.get("advanced"):
        _record_action(
            ctx,
            "utility",
            MAGE_TRAINING_ARENA_ACTIVITY_ID,
            not result.get("died"),
            expected_success_chance=1.0,
            failure_kind="safe_death" if result.get("died") else None,
            primary_xp=magic_xp,
        )
    if magic_xp:
        _refresh_combat_levels(ctx, {"magic_exp": magic_xp})
        ctx.show_exp(magic_xp)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("message") or "Arena checkpoint resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_ranging_guild_answer(
    ctx: RuntimeActionContext,
    *,
    productive: bool = True,
) -> bool:
    updated, ok, result = apply_ranging_guild_review_pure(
        ctx.player_data,
        ctx.random_random,
        productive=productive,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Ranging Guild unavailable",
            str(result.get("reason", "Enter the competition before training.")),
        )
        return False
    ctx.player_data.clear()
    ctx.player_data.update(updated)
    ranged_xp = float(result.get("ranged_xp", 0.0) or 0.0)
    if result.get("advanced"):
        _record_action(
            ctx,
            "utility",
            RANGING_GUILD_ACTIVITY_ID,
            result.get("outcome_id") != "miss",
            expected_success_chance=None,
            failure_kind="miss" if result.get("outcome_id") == "miss" else None,
            primary_xp=ranged_xp,
        )
    if ranged_xp:
        _refresh_combat_levels(ctx, {"ranged_exp": ranged_xp})
        ctx.show_exp(ranged_xp)
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(str(result.get("message") or "Competition shot resolved"))
    if result.get("terminal"):
        ctx.deactivate_current_skill()
    return True


def handle_agility_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    target_id = str(player_data.get("current_agility", DEFAULT_AGILITY_TARGET))
    if target_id == FLASH_POWDER_FACTORY_ACTIVITY_ID:
        return handle_flash_powder_factory_answer(ctx)
    if target_id not in AGILITY_TARGETS_BY_ID:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    locked = agility_target_locked_reasons_pure(player_data, target_id)
    if locked:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Agility target locked",
            f"{AGILITY_TARGETS_BY_ID[target_id].display_name} requires {', '.join(locked)}, so Agility has been switched off.",
        )
        return False

    lap_counts_before = dict(sanitize_agility_state_pure(player_data)["agility_lap_counts"])
    pit_offer_before = bool(player_data.get("agility_pit_offer", False))
    pit_origin_before = str(player_data.get("agility_pit_origin_course", "") or "")
    current_agility_before = str(player_data.get("current_agility", target_id) or target_id)
    equipment_before = dict(player_data.get("equipment", {}) or {})
    inventory_before = dict(player_data.get("inventory", {}) or {})
    xp_charges_before = dict(player_data.get("agility_effect_charges", {}) or {})
    updated, result = apply_agility_review_pure(
        player_data,
        tuple(ctx.random_random() for _ in range(4)),
    )
    if not result.get("allowed"):
        return False
    player_data.clear()
    player_data.update(updated)

    damage = int(result.get("damage", 0) or 0)
    safety_stop_message = ""
    if damage > 0:
        wilderness_ambush = bool((result.get("wilderness_ambush") or {}).get("triggered"))
        deferred_pit_accept = bool(
            wilderness_ambush
            and result.get("completed_lap")
            and player_data.get("current_agility") == "the_pit"
            and player_data.get("agility_pit_offer")
        )
        if deferred_pit_accept:
            # The Wilderness ambush resolves before the lap reward. Restore the
            # pre-entry carried state so a fatal hit cannot bank-protect hand
            # equipment by auto-accepting The Pit one transaction too early.
            player_data["current_agility"] = current_agility_before
            player_data["agility_pit_origin_course"] = pit_origin_before
            player_data["equipment"] = equipment_before
            player_data["inventory"] = inventory_before
        damaged, damage_result = apply_thieving_damage_pure(
            player_data,
            damage,
            source="agility_wilderness_pker" if wilderness_ambush else "agility_failure",
            carried_target_id=target_id,
        )
        player_data.clear()
        player_data.update(damaged)
        result["damage_result"] = damage_result
        if deferred_pit_accept and not damage_result.get("died"):
            accepted, accept_result = apply_agility_command_pure(
                player_data,
                "accept_pit_offer",
                {},
            )
            if accept_result.get("allowed"):
                player_data.clear()
                player_data.update(accepted)
        if damage_result.get("died"):
            grave = dict(player_data.get("combat_grave", {}) or {})
            travel_profile = agility_travel_profile_pure(
                "agility",
                target_id,
                int(player_data.get("agility_level", 1) or 1),
                inventory_before,
                equipment_before,
            )
            travel_reviews = max(
                1, scheduled_travel_reviews_pure(travel_profile, ctx.random_random())
            )
            grave.update({
                "target_id": target_id,
                "travel_reviews": travel_reviews,
                "reviews_remaining": travel_reviews + 1,
            })
            player_data["combat_grave"] = grave
            ctx.deactivate_current_skill()
            if wilderness_ambush and result.get("completed_lap"):
                player_data["agility_lap_counts"] = lap_counts_before
                player_data["agility_pit_offer"] = pit_offer_before
                player_data["agility_pit_origin_course"] = pit_origin_before
                player_data["current_agility"] = current_agility_before
                charges = dict(player_data.get("agility_effect_charges", {}) or {})
                for modifier in result.get("xp_modifiers", ()) or ():
                    item_name = modifier.get("item") if isinstance(modifier, dict) else None
                    if not isinstance(item_name, str):
                        continue
                    if item_name in xp_charges_before:
                        charges[item_name] = xp_charges_before[item_name]
                    else:
                        charges.pop(item_name, None)
                player_data["agility_effect_charges"] = charges
                result.update({
                    "xp": 0.0,
                    "base_xp": 0.0,
                    "xp_modifiers": (),
                    "success": False,
                    "completed_lap": False,
                    "failure_kind": "wilderness_pker_death",
                    "reward_forfeited": True,
                })
                death_status = "Wilderness PKer ambush · died before the lap reward"
                player_data["agility_status"] = death_status
                result["status"] = death_status
        elif (
            not result.get("success")
            and player_data.get("activity_auto_stop_on_danger", True)
        ):
            maximum_failure_damage = agility_maximum_failure_damage_pure(
                player_data, target_id
            )
            lifepoints = int(player_data.get("combat_lifepoints", 0) or 0)
            if maximum_failure_damage > 0 and lifepoints <= maximum_failure_damage:
                ctx.deactivate_current_skill()
                safety_stop_message = (
                    f"Safety stop — {lifepoints} LP left; "
                    f"{AGILITY_TARGETS_BY_ID[target_id].display_name} can hit "
                    f"up to {maximum_failure_damage} LP on a failure"
                )

    outputs = {
        str(item): int(quantity)
        for item, quantity in (result.get("outputs") or {}).items()
        if int(quantity) > 0
    }
    if outputs:
        inventory = dict(player_data.get("inventory", {}) or {})
        for item, quantity in outputs.items():
            inventory[item] = int(inventory.get(item, 0) or 0) + quantity
        player_data["inventory"] = inventory

    base_xp = float(result.get("xp", 0.0) or 0.0)
    gained = ctx.award_skill_exp("agility_exp", base_xp) if base_xp > 0 else 0.0
    if base_xp > 0:
        ctx.level_up_check("Agility", player_data)
    cross_rewards = tuple(
        {"skill_id": str(skill_id), "amount": float(amount)}
        for skill_id, amount in (result.get("cross_skill_rewards") or ())
        if float(amount) > 0
    )
    if cross_rewards:
        _award_action_xp_rewards(ctx, cross_rewards, str(cross_rewards[0]["skill_id"]))
    achievement_outputs = dict(outputs)
    tickets = int(result.get("tickets", 0) or 0)
    if tickets > 0:
        achievement_outputs["Agility arena ticket"] = tickets
    record_direct_diary_event_pure(
        player_data,
        True,
        "agility_result",
        action_id=str(result.get("action_id", target_id)),
        target_id=str(result.get("target_id", target_id)),
        completed_lap=bool(result.get("completed_lap")),
    )
    _record_action(
        ctx,
        "agility",
        str(result.get("action_id", target_id)),
        bool(result.get("success")),
        expected_success_chance=result.get("expected_success_chance"),
        output_items=outputs,
        achievement_output_items=achievement_outputs,
        failure_kind=result.get("failure_kind"),
        primary_xp=base_xp,
    )
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if gained > 0:
        ctx.show_exp(gained)
    ctx.show_activity_gain(str(result.get("status", player_data.get("agility_status", "Agility action complete"))))
    damage_result = result.get("damage_result") or {}
    if damage_result.get("died"):
        cause = "Wilderness PKer ambush" if (result.get("wilderness_ambush") or {}).get("triggered") else "Agility failure"
        ctx.show_activity_gain(
            f"☠ YOU DIED — {cause}; carried pack and gear moved to grave. "
            "Training stopped — click the Gravestone banner to walk back."
        )
    elif damage_result.get("food_used"):
        food = damage_result["food_used"]
        ctx.show_activity_gain(f"Auto-ate {food['item']} (+{food['healed_by']} LP)")
    if safety_stop_message:
        ctx.show_activity_gain(safety_stop_message)
    return True


_handle_stronghold_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_knight_waves_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_mage_arena_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_mage_arena_attunement_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_livid_farm_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_flash_powder_factory_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_pyramid_plunder_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_werewolf_skullball_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_gnome_ball_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_fish_flingers_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_fishing_trawler_answer.__module__ = f"{__package__}.runtime_actions_activities"
_handle_great_orb_project_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_mage_training_arena_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_ranging_guild_answer.__module__ = f"{__package__}.runtime_actions_activities"
handle_agility_answer.__module__ = f"{__package__}.runtime_actions_activities"
