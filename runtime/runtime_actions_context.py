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

from ..core.activity_feedback import fish_flingers_card_feedback
from ..logic.cadence_live import LIVE_COMBAT_TICKS_PER_REVIEW
from ..logic.pace.short_timers import STEP_TICKS, card_ticks_pure
from ..logic.pace.world_clock import calendar_ticks_pure
from ..logic.pace.danger_stops import card_danger_state_pure, card_danger_stop_pure

# Non-fight quest steps and Dungeoneering rooms keep one card at every speed;
# the quest handler carries consecutive fights within its own tick budget.
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
    # A kill can leave ticks for a bank trip or the queue's next entry.
    # Record elapsed Combat time across those bursts for pace verification.
    burst_ticks_left: int = 0
    combat_ticks_spent: int = 0

    def record_tick_stop(self, ticks_elapsed: int, reason: str) -> str:
        self.stop_reason = reason
        if not reason and ticks_elapsed >= self.ticks_remaining:
            self.stop_reason = self.exhaustion_reason
        return self.stop_reason

    def charge_step(self, handler_key: str) -> None:
        """Charge the step that ran: six ticks, a quest stage or room's whole card, or a burst's ticks."""
        if handler_key == "combat":
            self.ticks_remaining, self.burst_ticks_left = self.burst_ticks_left, 0
        elif handler_key in ONE_PER_CARD_HANDLER_KEYS:
            self.ticks_remaining = 0
        else:
            self.ticks_remaining -= LIVE_COMBAT_TICKS_PER_REVIEW

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
    # The queue entry that counts this step: what it still needs in its unit
    # (items made, inputs used or kills), and how many of its input one action
    # uses when it counts uses. The remainder is None when no entry counts the step.
    queue_remainder: Optional[int] = None
    queue_use_size: int = 0
    queue_wilderness_fingerprint: str = ""
    stop_notice: Optional[Callable[..., bool]] = None

    def show_stop_notice(self, title: str, message: str, queue_message: str, detail: str = "") -> bool:
        """True when the continuing queue received the notice without a dialog."""
        if self.stop_notice is not None:
            return self.stop_notice(title, message, queue_message, detail)
        self.show_error_message(title, message)
        return False

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

    def queue_action_limit(self) -> Optional[int]:
        """The most actions a step that takes several may take before the queue entry counting it is full.

        Each action counts as one item, or as the inputs it uses. An action that
        can only make a whole lot keeps the whole lot, and the entry still ends
        at its count. None when no entry counts the step.
        """
        if self.queue_remainder is None:
            return None
        return self.queue_remainder // self.queue_use_size if self.queue_use_size else self.queue_remainder


def stop_card(ctx: RuntimeActionContext, reason: str) -> None:
    """End the card after this step; its unspent ticks lapse."""
    ctx.card.stop_reason = reason


def _card_tick_debt(player_data: Mapping[str, Any]) -> int:
    debt = player_data.get(CARD_TICK_DEBT_KEY, 0)
    return debt if type(debt) is int and debt > 0 else 0


def stun_card(ctx: RuntimeActionContext, ticks: int, *, source: str = "") -> None:
    """A stun ends the card and owes its ticks to the running budget (decision 5).

    Once the stunning step is charged, the card's unspent ticks pay the stun
    first; only the rest carries to the next card.
    """
    ctx.player_data[CARD_TICK_DEBT_KEY] = _card_tick_debt(ctx.player_data) + ticks
    if source:
        ctx.player_data["card_tick_debt_source"] = source
    else:
        ctx.player_data.pop("card_tick_debt_source", None)
    stop_card(ctx, "stun")


def _settle_card_tick_debt(ctx: RuntimeActionContext) -> bool:
    """Pay the tick debt from the card, then report whether a step may start.

    A step starts once the debt is paid, even with fewer than six ticks left, and
    its overrun becomes the next card's debt, so no tick is forfeited.
    """
    budget = ctx.card
    balance = budget.ticks_remaining - _card_tick_debt(ctx.player_data)
    if (
        budget.ticks_remaining > 0 and balance <= 0 and not budget.stop_reason
        and ctx.player_data.get("card_tick_debt_source") == "thieving"
    ):
        ctx.show_activity_gain("Stun recovery took this card")
    budget.ticks_remaining = max(balance, 0)
    if balance < 0:
        ctx.player_data[CARD_TICK_DEBT_KEY] = -balance
    else:
        ctx.player_data.pop(CARD_TICK_DEBT_KEY, None)
        ctx.player_data.pop("card_tick_debt_source", None)
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
    fish_before = dict(ctx.player_data.get("fish_flingers") or {})
    while _settle_card_tick_debt(ctx):
        if progressed and not can_continue():
            break
        before_session = dict(ctx.player_data.get("activity_session") or {})
        result = _step_with_danger_stop(ctx, step)
        budget.charge_step(handler_key)
        if result is False:
            break
        progressed = True
        if activity_session_cleared(before_session, ctx.player_data.get("activity_session")):
            break
    _settle_card_tick_debt(ctx)
    budget.record_step_stop(handler_key)
    waiting = fish_flingers_card_feedback(fish_before, ctx.player_data.get("fish_flingers"))
    if waiting:
        ctx.show_activity_gain(waiting)
    return progressed


_COMBAT_RECOVERY_STATE_KEYS = (
    "combat_lifepoints",
    "combat_special_attack_energy",
    "combat_current_levels",
    "combat_status_effects",
    "combat_supply_loadout",
    "equipment_ammunition_count",
    "combat_ava_incidental_items",
    "combat_ava_incidental_ticks",
    "combat_grave",
)


def apply_review_recovery(addon, save_callback=None, *, ticks=None) -> None:
    if not any(key in addon._state.player_data for key in _COMBAT_RECOVERY_STATE_KEYS):
        return
    if ticks is None:
        ticks = addon.runtime_actions.card_ticks_pure(addon._review_action_multiplier())
    recovered = addon.apply_safe_combat_recovery_pure(addon._state.player_data, addon.EQUIPMENT_DATA, ticks)
    if recovered == addon._state.player_data:
        return
    addon._state.player_data.clear()
    addon._state.player_data.update(recovered)
    (save_callback or addon.save_player_data)()
    addon._refresh_skill_availability()
    try:
        addon.update_review_hud(addon._state.player_data, addon._state.current_skill)
    except Exception:
        pass
