"""Shared review seam for quests whose current journal takes several reviews."""

from textwrap import fill

from ...data.quest.one_small_favour import OPENING_DEEDS, REPLACEMENT_EVENT_ID, REPLACEMENT_MESSAGE, QUEST_ID
from ..logic_pure_state import quest_state_pure
from . import one_small_favour as favour
from .oronwen import QUEST_ID as ORONWEN_QUEST_ID
from .hazeel import (
    hazeel_opening_next_action_pure, hazeel_opening_review_ready_pure, apply_hazeel_opening_review_pure,
)
from .supply_steps import (
    apply_supply_step_pure, supply_step_blockers_pure, supply_step_phase_pure, supply_step_pure,
)
from .review_services import (
    quest_review_phase_pure as quest_service_phase_pure,
    quest_review_ready_pure as quest_service_review_ready_pure,
    apply_quest_review_service_pure as apply_quest_service_review_pure,
    quest_review_requirement_pure as _quest_service_requirement_pure,
)


def quest_review_requirement_pure(player_data, quest_id, requirement):
    return _quest_service_requirement_pure(player_data, quest_id, requirement)


def quest_review_blockers_pure(player_data, quest_id, blockers, quest_data=None):
    blockers = supply_step_blockers_pure(player_data, quest_id, quest_data, blockers)
    return (*blockers, *favour.opening_blockers_pure(player_data, quest_id))


def quest_review_ready_pure(player_data, quest_id, blockers, *, quest_data=None, eligibility_reasons=None):
    return (quest_service_review_ready_pure(player_data, quest_id, blockers)
            or favour.opening_review_ready_pure(player_data, quest_id, blockers)
            or supply_step_pure(player_data, quest_id, quest_data, blockers) is not None
            or hazeel_opening_review_ready_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons))


def apply_quest_review_step_pure(player_data, quest_id, blockers, *, quest_data=None, eligibility_reasons=None):
    if favour.opening_applies_pure(player_data, quest_id):
        return favour.apply_opening_review_pure(player_data, quest_id, blockers)
    data, result = apply_quest_service_review_pure(player_data, quest_id, blockers)
    if result != "unchanged":
        pending = "pending" if quest_id == ORONWEN_QUEST_ID else "partial"
        return data, {"handed_in": pending, "collected": "ready", "deed_only": "deed_only"}[result]
    recipe = supply_step_pure(player_data, quest_id, quest_data, blockers)
    if recipe is not None:
        return apply_supply_step_pure(player_data, recipe), "deed_only"
    return apply_hazeel_opening_review_pure(player_data, quest_id, quest_data, blockers, eligibility_reasons)


def quest_review_phase_pure(player_data, quest_id, blockers=(), quest_data=None):
    if quest_id == QUEST_ID:
        state = quest_state_pure(player_data, quest_id)
        if not state['started'] and not state['completed'] and state['progress'] == 0:
            return OPENING_DEEDS[0]['event_id']
        return favour.opening_phase_pure(player_data, quest_id)
    return (quest_service_phase_pure(player_data, quest_id)
            or supply_step_phase_pure(player_data, quest_id, quest_data, blockers)
            or hazeel_opening_next_action_pure(player_data, quest_id))


def quest_review_message_pure(phase):
    if isinstance(phase, dict):
        return (phase["notice"],), False
    if phase == REPLACEMENT_EVENT_ID:
        return (REPLACEMENT_MESSAGE,), False
    for index, deed in enumerate(OPENING_DEEDS):
        if phase == deed['event_id']:
            return (deed['proof'],), index == len(OPENING_DEEDS) - 1
    if phase == 'hand_in':
        return ('Oronwen took the damaged trousers, 2 Silk and 1 Bear fur. Review one more card to collect the repaired trousers.',), False
    if phase == 'collect':
        return ('Oronwen returned the repaired mourner trousers.',), True
    return (), True


def quest_review_feedback_pure(phase, progress_notice):
    """Keep the final deed and counter together inside the laptop popup."""
    messages, show_progress = quest_review_message_pure(phase)
    if not show_progress:
        return messages
    if phase == OPENING_DEEDS[-1]['event_id']:
        return ('\n'.join((fill(messages[0], width=40), progress_notice)),)
    return (*messages, progress_notice)
