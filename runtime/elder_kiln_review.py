"""The Elder Kiln's egg-hatching exercise, played inside one successful quest Answer.

The presenter's controls act only on a detached copy. Nothing is published until
the presenter returns, so an exception leaves the attempt and proof uncommitted
and the enclosing Answer's own rollback in charge. The controls never save,
record direct actions, advance the shared clock or apply the review multiplier.
"""

from __future__ import annotations

from typing import Any

from ..core import logic as core_logic
from ..core.constants import QUEST_DATA
from ..data.quest.elder_kiln import ATTEMPT_EVENT_ID, FAILURE_COPY, FAILURE_EVENT_ID, HATCH_EVENT_ID
from ..logic_pure.logic_pure import apply_quest_progress_pure, start_quest_pure
from ..logic_pure.quest.eligibility import quest_eligibility_reasons_pure
from ..logic_pure.quest.elder_kiln import (
    apply_elder_kiln_command_pure, elder_kiln_admission_reasons_pure, elder_kiln_attempt_pure,
    elder_kiln_observation_pure,
)
from .runtime_actions_context import RuntimeActionContext
from .runtime_actions_shared import _record_action


class _HatchingSession:
    """The Answer's working copy; each command replaces it with the reducer's result."""

    def __init__(self, player_data: dict[str, Any], quest_id: str, rng) -> None:
        self.data = player_data
        self.quest_id = quest_id
        self.rng = rng

    def observation(self, events=(), accepted=True) -> dict[str, Any]:
        return elder_kiln_observation_pure(self.data, events, accepted)

    def command(self, name: str) -> dict[str, Any]:
        self.data, accepted, events = apply_elder_kiln_command_pure(self.data, self.quest_id, name, self.rng)
        return self.observation(events, accepted)


def _refuse(ctx: RuntimeActionContext, quest: dict[str, Any], reasons: tuple[str, ...]) -> bool:
    ctx.deactivate_current_skill()
    reason_lines = "\n".join(f"• {reason}" for reason in reasons)
    ctx.show_error_message(
        "Quest blocked",
        f"{quest.get('display_name', 'The Elder Kiln')} is blocked:\n{reason_lines}\n\n"
        "Questing has been switched off until this is resolved.",
    )
    return False


def _finish_answer(ctx: RuntimeActionContext, message: str) -> None:
    ctx.check_achievements(ctx.player_data)
    ctx.save_player_data()
    ctx.refresh_skill_availability()
    ctx.show_activity_gain(message)


def _commit_attempt(ctx: RuntimeActionContext, quest: dict[str, Any], data: dict[str, Any]) -> bool:
    """An offer, pause or failure: the attempt is saved and the stage stays open."""
    attempt = elder_kiln_attempt_pure(data)
    failed = attempt["phase"] == "failed"
    ctx.player_data.update(data)
    _record_action(
        ctx, "quest", FAILURE_EVENT_ID if failed else ATTEMPT_EVENT_ID, False,
        failure_kind="failed" if failed else "paused",
    )
    display_name = quest.get("display_name", "The Elder Kiln")
    if failed:
        message = f"{display_name}: {FAILURE_COPY}"
    elif attempt["phase"] == "request":
        message = f"{display_name}: TzHaar-Mej-Jeh is waiting at the Birthing Pool"
    else:
        message = f"{display_name}: hatching paused at {attempt['progress']}%"
    _finish_answer(ctx, message)
    return True


def _commit_hatch(ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], data: dict[str, Any]) -> bool:
    """The real hatch proof completes stage 1 once; stage 2 waits for another Answer."""
    advanced, ok, completed_now = apply_quest_progress_pure(data, quest_id, QUEST_DATA)
    if not ok or completed_now:
        ctx.show_error_message("Quest progress not saved", "The hatching could not be recorded. No progress changed.")
        return False
    ctx.player_data.update(advanced)
    _record_action(ctx, "quest", HATCH_EVENT_ID, True, expected_success_chance=1.0)
    progress = ctx.player_data["quests"][quest_id]["progress"]
    _finish_answer(ctx, f"{quest.get('display_name', quest_id)}: the egg hatched ({progress}/{quest.get('stages', 1)})")
    return True


def answer_elder_kiln_opening(
    ctx: RuntimeActionContext, quest_id: str, quest: dict[str, Any], stage_blockers: tuple[dict[str, Any], ...],
) -> bool:
    reasons = elder_kiln_admission_reasons_pure(
        ctx.player_data, quest_id, QUEST_DATA, stage_blockers, quest_eligibility_reasons_pure,
    )
    if reasons:
        return _refuse(ctx, quest, reasons)
    working, started = start_quest_pure(ctx.player_data, quest_id, QUEST_DATA)
    if not started:
        return _refuse(ctx, quest, ("The quest cannot be started",))
    session = _HatchingSession(working, quest_id, ctx.random_random)
    core_logic.present_elder_kiln_hatching(session.command, session.observation())
    if elder_kiln_attempt_pure(session.data)["phase"] == "hatched":
        return _commit_hatch(ctx, quest_id, quest, session.data)
    return _commit_attempt(ctx, quest, session.data)
