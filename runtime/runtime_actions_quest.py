"""Quest stages and consecutive battles, and the notice when a quest completes."""

from __future__ import annotations

from textwrap import fill
from typing import Any

from ..core.constants import CLAIM_DATA, EQUIPMENT_DATA, QUEST_DATA
from ..core.last_action import quest_blocked_message
from ..core.equipment_change import prepare_quest_equipment_pure, release_quest_equipment_pure
from ..logic.bar_crawl_logic import apply_bar_crawl_drink_effects_pure
from ..logic_pure.logic_pure import (
    _quest_current_stage_selected_requirements,
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    can_start_quest_pure,
    can_attempt_quest_review_pure,
    quest_current_stage_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_current_stage_blockers_pure,
    quest_current_stage_resolvable_combat_blockers_pure,
    quest_lamps_waiting_text_pure,
)
from ..data.quest.grand_tree import PHASE_NOTICES
from ..logic_pure.quest.eligibility import quest_eligibility_reasons_pure
from ..logic_pure.quest.elder_kiln import elder_kiln_opening_applies_pure
from ..logic_pure.quest.grand_tree import grand_tree_phase_pure
from ..logic_pure.quest.review_services import quest_review_service_phase_pure
from ..logic_pure.quest.hazeel_journal import hazeel_opening_announcement_pure
from ..data.quest.hazeel_opening import OpeningAction
from ..logic_pure.quest.murder_mystery import (
    murder_mystery_silver_review_phase_pure, murder_mystery_silver_action_pure,
    murder_mystery_silver_refusal_reason_pure, INVALID_CUSTODY,
)
from ..logic_pure.quest.review_steps import quest_review_phase_pure, quest_review_feedback_pure
from ..logic_pure.quest.toktz_opening import toktz_opening_review_ready_pure, toktz_opening_message_pure
from ..logic_pure.quest.another_cook import (
    another_cook_phase_pure, another_cook_progress_message_pure,
)
from .elder_kiln_review import answer_elder_kiln_opening
from .runtime_actions_context import RuntimeActionContext, _step_with_danger_stop
from .runtime_actions_shared import (
    _combat_review_ticks,
    _record_action,
    _refresh_combat_levels,
    _switch_material_failure_to_bankstanding,
)


def _switch_off_blocked_quest(ctx: RuntimeActionContext, quest_name: str, reasons: tuple[str, ...]) -> None:
    # The review HUD shows this short reason beside Resume in a fixed-height
    # box, so it names the first blocker; the dialog below lists them all.
    more = f" (+{len(reasons) - 1} more)" if len(reasons) > 1 else ""
    ctx.deactivate_current_skill(f"{reasons[0]}{more}")
    ctx.show_error_message("Quest blocked", quest_blocked_message(quest_name, reasons))


def _answer_quest_fight(ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], encounter_id: Any) -> dict[str, Any] | None:
    player_data = ctx.player_data
    new_data, ok, result = apply_quest_combat_encounter_pure(
        player_data,
        quest_id,
        QUEST_DATA,
        encounter_id,
        rng=ctx.random_random,
        equipment_data=EQUIPMENT_DATA,
        ticks=_combat_review_ticks(ctx),
        live_cadence=ctx.cadence_live_enabled,
        stop_after_first_kill=ctx.cadence_live_enabled,
    )
    if not ok:
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest combat blocked",
            f"{quest.get('display_name', quest_id)} cannot resolve this battle yet.",
        )
        return None
    ctx.card.ammo_fired += sum(result.get("ammo_used", {}).values())
    ctx.card.ammo_broken += result.get("ammo_broken", 0)
    ctx.card.ammo_landed += result.get("ammo_landed", 0)
    player_data.update(release_quest_equipment_pure(new_data, quest_id, QUEST_DATA))
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
    _announce_quest_combat(ctx, result)
    return result


def _announce_quest_combat(ctx: RuntimeActionContext, result: dict[str, Any]) -> None:
    display_name = str(result.get("display_name") or "combat encounter")
    quantity_text = str(result.get("quantity_text") or "")
    if result.get("reason") == "quest_combat_bank_run":
        remaining = -(-int(result.get("bank_run_ticks_remaining", 0) or 0) // (6 * ctx.review_action_multiplier))
        ctx.show_activity_gain(f"{display_name}: bank run ({remaining} review{'s' if remaining != 1 else ''} remaining)")
    elif result.get("died"):
        ctx.show_activity_gain(f"☠ YOU DIED — killed by {display_name}; gear moved to grave")
    elif result.get("killed"):
        ctx.show_activity_gain(f"Defeated {display_name}{quantity_text}")
    else:
        ctx.show_activity_gain(
            f"{display_name}: {int(result.get('player_damage', 0) or 0)} damage dealt, "
            f"{int(result.get('enemy_lifepoints', 0) or 0)} LP left"
        )


def _next_quest_fight(ctx: RuntimeActionContext, quest_id: str) -> str | None:
    fights = quest_current_stage_resolvable_combat_blockers_pure(ctx.player_data, quest_id, QUEST_DATA)
    if fights:
        return fights[0]["encounter_id"]
    rows, blockers = _quest_current_stage_selected_requirements(ctx.player_data, quest_id, QUEST_DATA)
    # Item work and automatic deeds keep their own card, even when their
    # prerequisites are already held. Only a fight-only stage can collapse.
    deeds = ("consumed_inventory", "consumed_inventory_options", "produced_inventory", "auto_actions", "repeatable_until_consumed")
    if blockers or not any(row.get("combat_encounters") for row in rows):
        return None
    if any(row.get(key) for row in rows for key in deeds):
        return None
    candidate, ok, completed = apply_quest_progress_pure(ctx.player_data, quest_id, QUEST_DATA)
    fights = quest_current_stage_resolvable_combat_blockers_pure(candidate, quest_id, QUEST_DATA)
    if not ok or completed or not fights:
        return None
    ctx.player_data.update(candidate)
    return fights[0]["encounter_id"]


def _answer_quest_combat(ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], encounter_id: Any) -> bool:
    while encounter_id:
        result = _step_with_danger_stop(ctx, lambda scoped: _answer_quest_fight(scoped, quest_id, quest, encounter_id))
        if result is None:
            return False
        if not ctx.cadence_live_enabled:
            break
        elapsed = int(result.get("ticks_elapsed", 0))
        ctx.card.combat_ticks_spent += elapsed
        ctx.card.record_tick_stop(elapsed, ctx.card.stop_reason or result.get("stop_reason", ""))
        ctx.card.ticks_remaining = max(0, ctx.card.ticks_remaining - elapsed)
        if ctx.card.stop_reason or not result.get("killed"):
            break
        encounter_id = _next_quest_fight(ctx, quest_id)
        if not ctx.card.ticks_remaining:
            break
    return True


def _announce_quest_completion(ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], clue_reward_refusal_reason: Any) -> None:
    display_name = str(quest.get("display_name", quest_id))
    lamps_waiting = quest_lamps_waiting_text_pure(ctx.player_data, quest_id, CLAIM_DATA)
    continued = ctx.show_stop_notice(
        "Quest complete",
        f"{display_name} is complete, so questing has been switched off. "
        + (f"{lamps_waiting} " if lamps_waiting else "")
        + "Open the AnkiScape menu to pick another quest.",
        f"{display_name} complete.", lamps_waiting,
    )
    if not continued:
        ctx.show_activity_gain(f"{display_name} complete")
    if clue_reward_refusal_reason:
        ctx.show_activity_gain(clue_reward_refusal_reason)


def _announce_hazeel_step(ctx, action):
    lines = hazeel_opening_announcement_pure(ctx.player_data, action)
    for line in lines:
        ctx.show_activity_gain(line)
    return len(lines) < 2


def _announce_watchtower_progress(ctx, phase):
    messages = {
        "commission": "The Watchtower Wizard asked you to investigate the missing power crystals. You can now use the ladder.",
        "search": "You searched the bushes outside the Watchtower and found Fingernails. Return them to the Wizard.",
        "present": "The Wizard took the Fingernails and identified the thieves as Skavids, servants of the ogres. He asked you to recover the four crystals.",
    }
    # The shared floating label sizes to its text without automatic wrapping.
    # Keep the full explanation readable within a laptop reviewer window.
    ctx.show_activity_gain(fill(messages[phase], width=48))


def _announce_quest_progress(
    ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], repair_phase: Any,
    opening_message: str = "", cook_phase: Any = None, opening_phase=None, silver_action="",
) -> None:
    if silver_action:
        ctx.show_activity_gain(silver_action)
        return
    if opening_phase in PHASE_NOTICES:
        # ExpPopup sizes to its text, so wrap the full notice for laptop windows.
        ctx.show_activity_gain(fill(PHASE_NOTICES[opening_phase], width=48))
        return
    if repair_phase == "recover_key":
        ctx.show_activity_gain("Recovered the backroom key from the fountain.")
        return
    if repair_phase == "recover_ball":
        ctx.show_activity_gain("Recovered Harvey's ball from the shed.")
        return
    if quest_id == "watchtower" and repair_phase:
        _announce_watchtower_progress(ctx, repair_phase)
        return
    if isinstance(repair_phase, OpeningAction) and _announce_hazeel_step(ctx, repair_phase):
        return
    if opening_message:
        ctx.show_activity_gain(opening_message)
        return
    deed_message = another_cook_progress_message_pure(cook_phase)
    state = ctx.player_data.get("quests", {}).get(quest_id, {})
    if quest_id == "the_slug_menace" and state.get('progress') == 2:
        deed_message = "Scanned Mayor Hobb with Commorb v2: two life forms. Savant is unsure what it means."
    progress_notice = f"{quest.get('display_name', quest_id)} {state.get('progress', 0)}/{quest.get('stages', 1)}"
    if deed_message:
        # The collector keeps the last mixed activity message, so send the
        # performed deed and counter together, wrapped for the existing popup.
        ctx.show_activity_gain('\n'.join((fill(deed_message, width=40), progress_notice)))
        return
    for message in quest_review_feedback_pure(repair_phase, progress_notice):
        ctx.show_activity_gain(message)


def _report_quest_progress_refusal(ctx, quest_id, quest):
    if murder_mystery_silver_review_phase_pure(ctx.player_data, quest_id, QUEST_DATA):
        reason = murder_mystery_silver_refusal_reason_pure(
            ctx.player_data, quest_id, QUEST_DATA, quest_eligibility_reasons_pure,
        )
        ctx.show_error_message('Bedroom search refused', reason or INVALID_CUSTODY)
        return
    blockers = quest_current_stage_blockers_pure(ctx.player_data, quest_id, QUEST_DATA)
    if toktz_opening_review_ready_pure(ctx.player_data, quest_id, blockers):
        ctx.show_error_message("Quest item not received", "The quest item could not be added. No opening progress was saved.")
        return
    stage_blocker_reasons = quest_current_stage_blocker_reasons_pure(ctx.player_data, quest_id, QUEST_DATA)
    if stage_blocker_reasons:
        _switch_off_blocked_quest(ctx, quest.get("display_name", quest_id), stage_blocker_reasons)
    elif quest_id == "the_slug_menace" and quest_current_stage_pure(ctx.player_data, quest_id, QUEST_DATA) == 1:
        ctx.show_error_message(
            "Investigation not completed",
            "The mayor's scan could not be completed. No items or quest progress changed.",
        )
    elif quest_id == "murder_mystery" and quest_current_stage_pure(ctx.player_data, quest_id, QUEST_DATA) == 1:
        ctx.show_error_message(
            "Evidence not collected",
            "The evidence could not be collected. No items or quest progress changed.",
        )


def _show_quest_review_exp(ctx: RuntimeActionContext, exp_before: dict[str, float], completed_now: bool, cook_phase: Any, phase: Any) -> None:
    if completed_now or cook_phase == 'prepare' or (isinstance(phase, dict) and phase.get('xp_rewards')):
        ctx.show_quest_exp_delta(exp_before)


def _answer_stage_activity(ctx: RuntimeActionContext, quest_id: str, quest: dict, combat_blockers, stage_blockers) -> bool | None:
    """Hand the Answer to the activity that owns the current stage, or return None for ordinary review."""
    if combat_blockers:
        return _answer_quest_combat(ctx, quest_id, quest, combat_blockers[0].get("encounter_id"))
    if elder_kiln_opening_applies_pure(ctx.player_data, quest_id):
        return answer_elder_kiln_opening(ctx, quest_id, quest, stage_blockers)
    return None


def _quest_review_announcement_phase(player_data, quest_id, stage_blockers):
    return (quest_review_service_phase_pure(player_data, quest_id, stage_blockers)
            or quest_review_phase_pure(player_data, quest_id, stage_blockers, QUEST_DATA))


def _quest_review_blockers(player_data, quest_id, silver_phase):
    if silver_phase:
        return (), ()
    combat = quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, QUEST_DATA)
    if combat:
        return combat, ()
    return (), quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)


def handle_quest_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    quest_id = player_data.get("current_quest", "rune_mysteries")
    if quest_id not in QUEST_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    quest = QUEST_DATA[quest_id]
    if can_attempt_quest_review_pure(player_data, quest_id, QUEST_DATA):
        player_data.update(prepare_quest_equipment_pure(player_data, quest_id, QUEST_DATA))
    silver_phase = murder_mystery_silver_review_phase_pure(player_data, quest_id, QUEST_DATA)
    combat_blockers, stage_blockers = _quest_review_blockers(player_data, quest_id, silver_phase)
    activity_answer = _answer_stage_activity(ctx, quest_id, quest, combat_blockers, stage_blockers)
    if activity_answer is not None:
        return activity_answer
    stage_blocker_reasons = tuple(str(blocker.get("reason")) for blocker in stage_blockers)
    review_ready = can_attempt_quest_review_pure(player_data, quest_id, QUEST_DATA)
    if silver_phase and not review_ready:
        _report_quest_progress_refusal(ctx, quest_id, quest)
        return False
    if stage_blocker_reasons and not review_ready:
        _switch_off_blocked_quest(ctx, quest.get("display_name", quest_id), stage_blocker_reasons)
        return False
    if not can_start_quest_pure(player_data, quest_id, QUEST_DATA):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest unavailable",
            f"{quest.get('display_name', quest_id)} cannot progress right now, so questing has been switched off.",
        )
        return False

    silver_action = murder_mystery_silver_action_pure(player_data) if silver_phase else ""
    opening_phase = grand_tree_phase_pure(player_data, quest_id)
    opening_message = toktz_opening_message_pure(player_data, quest_id)
    cook_phase = another_cook_phase_pure(player_data, quest_id)
    repair_phase = _quest_review_announcement_phase(player_data, quest_id, stage_blockers)
    exp_before = ctx.implemented_exp_keys_snapshot()
    new_data, ok, completed_now, clue_reward_refusal_reason = (
        apply_quest_progress_pure(
            player_data,
            quest_id,
            QUEST_DATA,
            include_clue_refusal=True,
        )
    )
    if not ok:
        _report_quest_progress_refusal(ctx, quest_id, quest)
        return False
    if quest_id == "bar_crawl":
        new_data = apply_bar_crawl_drink_effects_pure(
            new_data,
            quest_current_stage_pure(player_data, quest_id, QUEST_DATA),
            rng=ctx.random_random,
        )
    player_data.update(release_quest_equipment_pure(new_data, quest_id, QUEST_DATA))
    _record_action(ctx, "quest", quest_id, True, expected_success_chance=1.0)
    _show_quest_review_exp(ctx, exp_before, completed_now, cook_phase, repair_phase)
    if completed_now:
        ctx.deactivate_current_skill()
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if completed_now:
        _announce_quest_completion(ctx, quest_id, quest, clue_reward_refusal_reason)
    else:
        _announce_quest_progress(
            ctx, quest_id, quest, repair_phase, opening_message,
            cook_phase=cook_phase, opening_phase=opening_phase, silver_action=silver_action,
        )
    return True
