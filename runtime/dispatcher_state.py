"""Shared profile and review transaction state for runtime dispatchers."""

from dataclasses import dataclass, field

from ..core.logic import DeferredAchievementDialogs


@dataclass(slots=True, eq=False)
class DispatcherState:
    # A profile load supplies the save; an empty invented save is never usable.
    player_data: dict = field(init=False, repr=False)
    current_skill: str = "None"
    answer_shown: bool = False
    card_turned: bool = False
    exp_awarded: bool = False
    familiar_ticks_before: int | None = None
    calendar_ticks_for_answer: int | None = None
    review_undo_stack: list = field(default_factory=list)
    direct_action_undo_stack: list = field(default_factory=list)
    review_feedback_context: dict | None = None
    review_feedback_initial_xp: float = 0.0
    review_feedback_flushing: bool = False
    pending_bankstanding_notice: dict | None = None
    pending_review_dialogs: DeferredAchievementDialogs = field(
        default_factory=DeferredAchievementDialogs
    )
    skill_availability_cache_fingerprint: tuple | None = None


state = DispatcherState()
