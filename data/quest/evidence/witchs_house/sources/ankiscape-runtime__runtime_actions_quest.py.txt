"""Quest reviews, split out of runtime_actions_production.py: one quest stage or
battle per review, and the notice when the quest completes."""

from __future__ import annotations

from typing import Any

from ..core.constants import CLAIM_DATA, EQUIPMENT_DATA, QUEST_DATA
from ..logic.bar_crawl_logic import apply_bar_crawl_drink_effects_pure
from ..logic_pure.logic_pure import (
    apply_quest_combat_encounter_pure,
    apply_quest_progress_pure,
    can_start_quest_pure,
    quest_current_stage_pure,
    quest_current_stage_blocker_reasons_pure,
    quest_current_stage_blockers_pure,
    quest_current_stage_resolvable_combat_blockers_pure,
    quest_lamps_waiting_text_pure,
)
from ..logic_pure.quest.oronwen import oronwen_phase_pure, oronwen_review_ready_pure
from .runtime_actions_context import RuntimeActionContext
from .runtime_actions_shared import (
    _combat_review_ticks,
    _record_action,
    _refresh_combat_levels,
    _switch_material_failure_to_bankstanding,
)


def _switch_off_blocked_quest(ctx: RuntimeActionContext, quest_name: str, reasons: tuple[str, ...]) -> None:
    ctx.deactivate_current_skill()
    reason_lines = "\n".join(f"• {reason}" for reason in reasons)
    ctx.show_error_message("Quest blocked", f"{quest_name} is blocked:\n{reason_lines}\n\nQuesting has been switched off until this is resolved.")


def _answer_quest_combat(ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], encounter_id: Any) -> bool:
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
        ctx.show_activity_gain(f"☠ YOU DIED — killed by {display_name}; gear moved to grave")
    elif result.get("killed"):
        ctx.show_activity_gain(f"Defeated {display_name}{quantity_text}")
    else:
        ctx.show_activity_gain(
            f"{display_name}: {int(result.get('player_damage', 0) or 0)} damage dealt, "
            f"{int(result.get('enemy_lifepoints', 0) or 0)} LP left"
        )
    return True


def _announce_quest_completion(ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], clue_reward_refusal_reason: Any) -> None:
    display_name = str(quest.get("display_name", quest_id))
    ctx.show_activity_gain(f"{display_name} complete")
    if clue_reward_refusal_reason:
        ctx.show_activity_gain(clue_reward_refusal_reason)
    # Quest lamps wait silently in Bank Claims, so the one modal the player
    # reads at completion is where they learn the lamps exist.
    lamps_waiting = quest_lamps_waiting_text_pure(ctx.player_data, quest_id, CLAIM_DATA)
    ctx.show_error_message(
        "Quest complete",
        f"{display_name} is complete, so questing has been switched off. "
        + (f"{lamps_waiting} " if lamps_waiting else "")
        + "Open the AnkiScape menu to pick another quest.",
    )


def _announce_quest_progress(ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], repair_phase: Any) -> None:
    if repair_phase == "hand_in":
        ctx.show_activity_gain("Oronwen took the damaged trousers, 2 Silk and 1 Bear fur. Review one more card to collect the repaired trousers.")
        return
    if repair_phase == "collect":
        ctx.show_activity_gain("Oronwen returned the repaired mourner trousers.")
    state = ctx.player_data.get("quests", {}).get(quest_id, {})
    ctx.show_activity_gain(f"{quest.get('display_name', quest_id)} {state.get('progress', 0)}/{quest.get('stages', 1)}")


def handle_quest_answer(ctx: RuntimeActionContext) -> bool:
    player_data = ctx.player_data
    quest_id = player_data.get("current_quest", "rune_mysteries")
    if quest_id not in QUEST_DATA:
        _switch_material_failure_to_bankstanding(ctx)
        return False
    quest = QUEST_DATA[quest_id]
    combat_blockers = quest_current_stage_resolvable_combat_blockers_pure(player_data, quest_id, QUEST_DATA)
    if combat_blockers:
        return _answer_quest_combat(ctx, quest_id, quest, combat_blockers[0].get("encounter_id"))
    stage_blockers = quest_current_stage_blockers_pure(player_data, quest_id, QUEST_DATA)
    stage_blocker_reasons = tuple(str(blocker.get("reason")) for blocker in stage_blockers)
    if stage_blocker_reasons and not oronwen_review_ready_pure(player_data, quest_id, stage_blockers):
        _switch_off_blocked_quest(ctx, quest.get("display_name", quest_id), stage_blocker_reasons)
        return False
    if not can_start_quest_pure(player_data, quest_id, QUEST_DATA):
        ctx.deactivate_current_skill()
        ctx.show_error_message(
            "Quest unavailable",
            f"{quest.get('display_name', quest_id)} cannot progress right now, so questing has been switched off.",
        )
        return False

    repair_phase = oronwen_phase_pure(player_data, quest_id)
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
        stage_blocker_reasons = quest_current_stage_blocker_reasons_pure(player_data, quest_id, QUEST_DATA)
        if stage_blocker_reasons:
            _switch_off_blocked_quest(ctx, quest.get("display_name", quest_id), stage_blocker_reasons)
        return False
    if quest_id == "bar_crawl":
        new_data = apply_bar_crawl_drink_effects_pure(
            new_data,
            quest_current_stage_pure(player_data, quest_id, QUEST_DATA),
            rng=ctx.random_random,
        )
    player_data.update(new_data)
    _record_action(ctx, "quest", quest_id, True, expected_success_chance=1.0)
    if completed_now:
        ctx.show_quest_exp_delta(exp_before)
        ctx.deactivate_current_skill()
    ctx.check_achievements(player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    if completed_now:
        _announce_quest_completion(ctx, quest_id, quest, clue_reward_refusal_reason)
    else:
        _announce_quest_progress(ctx, quest_id, quest, repair_phase)
    return True
