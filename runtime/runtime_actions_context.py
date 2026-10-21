"""The per-card runtime context and the time budget a successful card buys.

Owner decision 4 (2026-10-15): a card buys six game ticks per unit of game
speed. Combat receives the whole budget in one call and spends it inside its own
tick loop; every other handler takes one six-tick kernel step per call until the
card is spent, the action stops, or a step ends the card through ``stop_card``.
A stun owes its ticks to the running budget, and the next card pays them first.
Split out of runtime_actions.py; see that module's header.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Any, Callable, Mapping, Optional

from ..logic.cadence_live import LIVE_COMBAT_TICKS_PER_REVIEW
from ..logic.pace.short_timers import STEP_TICKS, card_ticks_pure
from ..logic.pace.world_clock import calendar_ticks_pure
from ..logic.pace.danger_stops import card_danger_state_pure, card_danger_stop_pure

# Quests and Dungeoneering already run faster than 2012 at speed 1, so they keep
# one stage or one room per card at every speed (owner-accepted).
ONE_PER_CARD_HANDLER_KEYS = frozenset({"quest", "dungeoneering"})

# Ticks the running budget owes the next card: a stun's length, or the part of a
# step that started with fewer than six ticks left.
CARD_TICK_DEBT_KEY = "card_tick_debt"


@dataclass
class CardBudget:
    """The game ticks left on one successful card.

    Scoped copies of a context (``dataclasses.replace``) share this object, so a
    step that ends the card inside the carried overlay ends it for the
    dispatcher too.
    """

    ticks_remaining: int
    stop_reason: str = ""
    exhaustion_reason: str = ""

    def record_tick_stop(self, ticks_elapsed: int, reason: str) -> str:
        self.stop_reason = reason
        if not reason and ticks_elapsed >= self.ticks_remaining:
            self.stop_reason = self.exhaustion_reason
        return self.stop_reason

    def record_step_stop(self, handler_key: str = "") -> None:
        if handler_key != "combat" and self.ticks_remaining == 0 and not self.stop_reason:
            self.stop_reason = self.exhaustion_reason


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
    calendar_ticks_for_answer: Optional[int] = None
    familiar_ticks_before: Optional[int] = None

    def __post_init__(self) -> None:
        if self.card is None:
            self.card = CardBudget(card_ticks_pure(self.review_action_multiplier))
        if self.familiar_ticks_before is not None and 0 < self.familiar_ticks_before < self.card.ticks_remaining:
            self.card.ticks_remaining = self.familiar_ticks_before
            self.card.exhaustion_reason = "familiar_ended"

    def step_calendar_tick(self) -> int:
        """The end of this step, before the card's remaining time and daily gap."""
        now = calendar_ticks_pure(self.player_data)
        if self.calendar_ticks_for_answer is None:
            return now
        budget = card_ticks_pure(self.review_action_multiplier)
        available = budget
        if self.familiar_ticks_before is not None and self.familiar_ticks_before > 0:
            available = min(available, self.familiar_ticks_before)
        spent = min(budget, available - self.card.ticks_remaining + STEP_TICKS)
        return now - self.calendar_ticks_for_answer + spent


def stop_card(ctx: RuntimeActionContext, reason: str) -> None:
    """End the card after this step; its unspent ticks lapse."""
    ctx.card.stop_reason = reason


_DANGER_STOP_TEXTS = {"died": "<<COPY:danger_stop_died>>", "fled": "<<COPY:danger_stop_fled>>"}


def danger_stop_suffix(reason: str) -> str:
    """Why a death or flee ended the card early, for the end of the line that reports it.

    With no XP gained, the review popup keeps only the card's last line, so a
    line of its own would hide the death or flee it explains.
    """
    text = _DANGER_STOP_TEXTS.get(reason)
    return f" · {text}" if text else ""


def _card_tick_debt(player_data: Mapping[str, Any]) -> int:
    debt = player_data.get(CARD_TICK_DEBT_KEY, 0)
    return debt if type(debt) is int and debt > 0 else 0


def stun_card(ctx: RuntimeActionContext, ticks: int) -> None:
    """A stun ends the card and owes its ticks to the running budget (decision 5).

    Once the stunning step is charged, the card's unspent ticks pay the stun
    first; only the rest carries to the next card.
    """
    ctx.player_data[CARD_TICK_DEBT_KEY] = _card_tick_debt(ctx.player_data) + ticks
    stop_card(ctx, "stun")


def _settle_card_tick_debt(ctx: RuntimeActionContext) -> bool:
    """Pay the tick debt from the card, then report whether a step may start.

    A step starts once the debt is paid, even with fewer than six ticks left, and
    its overrun becomes the next card's debt, so no tick is forfeited.
    """
    budget = ctx.card
    balance = budget.ticks_remaining - _card_tick_debt(ctx.player_data)
    budget.ticks_remaining = max(balance, 0)
    if balance < 0:
        ctx.player_data[CARD_TICK_DEBT_KEY] = -balance
    else:
        ctx.player_data.pop(CARD_TICK_DEBT_KEY, None)
    return budget.ticks_remaining > 0 and not budget.stop_reason


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


def _step_with_danger_stop(ctx: RuntimeActionContext, step: Callable[[RuntimeActionContext], Any]) -> Any:
    before = card_danger_state_pure(ctx.player_data)
    result = step(ctx)
    danger = card_danger_stop_pure(before, card_danger_state_pure(ctx.player_data))
    if danger and not ctx.card.stop_reason:
        stop_card(ctx, danger)
    return result


def spend_card_on_farm_queue(
    ctx: RuntimeActionContext,
    first_step: Callable[[RuntimeActionContext], Any],
    next_step: Callable[[RuntimeActionContext], Any],
) -> bool:
    """Queued Farming steps take the card's first six-tick steps.

    ``first_step`` also carries the card's one background farm-clock tick, so
    the return value says whether it ran: a card the tick debt holds whole must
    still move the farm clock. The rest of the budget falls to the selected
    action in the same transaction, unless a step ended the card.
    """
    step = first_step
    while ctx.player_data.get("farm_queue") and _settle_card_tick_debt(ctx):
        _step_with_danger_stop(ctx, step)
        ctx.card.ticks_remaining -= LIVE_COMBAT_TICKS_PER_REVIEW
        step = next_step
    _settle_card_tick_debt(ctx)
    ctx.card.record_step_stop()
    return step is next_step


def spend_card_budget(
    ctx: RuntimeActionContext,
    handler_key: str,
    step: Callable[[RuntimeActionContext], Any],
    *,
    can_continue: Callable[[], bool],
) -> bool:
    """Spend the card on the selected action; return whether any step progressed.

    ``can_continue`` reports, before every step after the first, whether the
    same action is still selected and can start again.
    """
    budget = ctx.card
    progressed = False
    while _settle_card_tick_debt(ctx):
        if progressed and not can_continue():
            break
        before_session = dict(ctx.player_data.get("activity_session") or {})
        result = _step_with_danger_stop(ctx, step)
        budget.ticks_remaining = (
            0
            if handler_key == "combat" or handler_key in ONE_PER_CARD_HANDLER_KEYS
            else budget.ticks_remaining - LIVE_COMBAT_TICKS_PER_REVIEW
        )
        if result is False:
            break
        progressed = True
        if activity_session_cleared(before_session, ctx.player_data.get("activity_session")):
            break
    _settle_card_tick_debt(ctx)
    budget.record_step_stop(handler_key)
    return progressed
