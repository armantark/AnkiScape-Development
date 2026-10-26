"""Quest review services share the normal single-transaction review boundary."""

from .oronwen import oronwen_phase_pure, oronwen_review_ready_pure, apply_oronwen_review_pure
from .witchs_house import (
    witchs_house_service_phase_pure, witchs_house_service_ready_pure,
    apply_witchs_house_service_pure,
)


def quest_review_service_phase_pure(player_data, quest_id, blockers):
    return oronwen_phase_pure(player_data, quest_id) or witchs_house_service_phase_pure(player_data, quest_id, blockers)


def quest_review_service_ready_pure(player_data, quest_id, blockers):
    return (oronwen_review_ready_pure(player_data, quest_id, blockers)
            or witchs_house_service_ready_pure(player_data, quest_id, blockers))


def apply_quest_review_service_pure(player_data, quest_id, blockers):
    data, result = apply_oronwen_review_pure(player_data, quest_id, blockers)
    if result != "unchanged":
        return data, result
    return apply_witchs_house_service_pure(player_data, quest_id, blockers)
