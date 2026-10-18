"""The per-card runtime context and the time budget a successful card buys.

Decision 4: a card buys six game ticks per unit of game speed. Combat receives
the whole budget in one call and spends it inside its own tick loop; every other
handler takes one six-tick kernel step per call until the card is spent, the
action stops, or a step ends the card through ``stop_card``. Split out of
runtime_actions.py; see that module's header.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Any, Callable, Mapping, Optional

from ..logic.cadence_live import LIVE_COMBAT_TICKS_PER_REVIEW


@dataclass
class CardBudget:
    """The game ticks left on one successful card.

    Scoped copies of a context (``dataclasses.replace``) share this object, so a
    step that ends the card inside the carried overlay ends it for the
    dispatcher too.
    """

    ticks_remaining: int
    stop_reason: str = ""


@dataclass
class RuntimeActionContext:
    player_data: dict[str, Any]
    random_random: Callable[[], float]
    show_error_message: Callable[[str, str], None]
    deactivate_current_skill: Callable[..., None]
    award_skill_exp: Callable[[str, float], float]
    award_hidden_skill_exp: Callable[[str, str, float], None]
    level_up_check: Callable[[str, dict[str, Any]], None]
    check_achievements: Callable[[dict[str, Any]], None]
    save_player_data: Callable[[], None]
    refresh_skill_availability: Callable[[], None]
    show_exp: Callable[[float], None]
    show_activity_gain: Callable[[str], None]
    implemented_exp_keys_snapshot: Callable[[], dict[str, float]]
    show_quest_exp_delta: Callable[[dict[str, float]], None]
    review_action_multiplier: int = 1
    cadence_shadow_enabled: bool = False
    cadence_live_enabled: bool = False
    cadence_forced_opportunity: bool = False
    # Fired once when the Stronghold of Security is finished, so the UI can pop
    # the boot-choice reward dialog. Optional so older call sites keep working.
    prompt_stronghold_reward: Optional[Callable[[], None]] = None
    # Fired when a review is refused because the player is near death with no
    # food and nothing bankable to fetch. The UI asks whether to leave; the
    # handler has already stopped the review either way.
    prompt_near_death: Optional[Callable[[str], None]] = None
    prompt_slayer_completion: Optional[Callable[[int, str], None]] = None
    switch_to_bankstanding: Optional[Callable[..., None]] = None
    select_review_action: Optional[Callable[[str], bool]] = None
    refresh_carried_inventory: Optional[Callable[[], None]] = None
    card: Optional[CardBudget] = None

    def __post_init__(self) -> None:
        if self.card is None:
            speed = max(1, int(self.review_action_multiplier or 1))
            self.card = CardBudget(LIVE_COMBAT_TICKS_PER_REVIEW * speed)


def stop_card(ctx: RuntimeActionContext, reason: str) -> None:
    """End the card after this step; its unspent ticks lapse."""
    ctx.card.stop_reason = reason


def activity_session_cleared(
    before: Optional[Mapping[str, Any]],
    after: Optional[Mapping[str, Any]],
) -> bool:
    """True when an active activity session ended (active_id -> empty).

    The shared transition predicate for every boundary that finalizes an undo
    snapshot after a session completes: the surface must land on Bankstanding
    before the snapshot is taken so undo restores the former activity whole.
    """
    before_active = str((before or {}).get("active_id", "") or "")
    after_active = str((after or {}).get("active_id", "") or "")
    return bool(before_active) and not after_active


def spend_card_budget(
    ctx: RuntimeActionContext,
    handler_key: str,
    step: Callable[[RuntimeActionContext], Any],
    *,
    one_per_card: bool,
    can_continue: Callable[[], bool],
) -> bool:
    """Spend the card on the selected action; return whether any step progressed.

    ``can_continue`` reports, before every step after the first, whether the
    same action is still selected and can start again.
    """
    budget = ctx.card
    progressed = False
    while budget.ticks_remaining >= LIVE_COMBAT_TICKS_PER_REVIEW and not budget.stop_reason:
        if progressed and not can_continue():
            break
        before_session = dict(ctx.player_data.get("activity_session") or {})
        result = step(ctx)
        budget.ticks_remaining = (
            0
            if one_per_card or handler_key == "combat"
            else budget.ticks_remaining - LIVE_COMBAT_TICKS_PER_REVIEW
        )
        if result is False:
            break
        progressed = True
        if activity_session_cleared(before_session, ctx.player_data.get("activity_session")):
            break
    return progressed
