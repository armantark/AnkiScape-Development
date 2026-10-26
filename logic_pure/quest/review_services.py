"""Review service adapters preserve each service's existing result vocabulary."""

from .oronwen import oronwen_phase_pure, oronwen_review_ready_pure, apply_oronwen_review_pure
from .enakhra import (
    enakhra_opening_phase_pure, enakhra_opening_next_action_pure,
    enakhra_opening_blockers_pure, apply_enakhra_opening_action_pure,
)
from ...data.quest.enakhra_opening import QUEST_ID, PROOFS
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


def quest_service_review_ready_pure(player_data, quest_id, blockers):
    if quest_id != QUEST_ID:
        return quest_review_service_ready_pure(player_data, quest_id, blockers)
    if enakhra_opening_phase_pure(player_data) in (None, "placed", "inconsistent"):
        return False
    if any(blocker.get("kind") != "required_action" or blocker.get("action_id") != PROOFS["place_base"] for blocker in blockers):
        return False
    return not enakhra_opening_blockers_pure(player_data)


def apply_quest_service_review_pure(player_data, quest_id, blockers):
    if quest_id != QUEST_ID:
        return apply_quest_review_service_pure(player_data, quest_id, blockers)
    if not quest_service_review_ready_pure(player_data, quest_id, blockers):
        return player_data, "unchanged"
    descriptor = enakhra_opening_next_action_pure(player_data)
    candidate, ok, _ = apply_enakhra_opening_action_pure(player_data, descriptor["action_id"], descriptor["item_id"])
    if not ok:
        return player_data, "unchanged"
    return candidate, "collected" if descriptor["action_id"] == "place_base" else "handed_in"


def quest_service_phase_pure(player_data, quest_id):
    if quest_id == QUEST_ID:
        return enakhra_opening_next_action_pure(player_data)
    return oronwen_phase_pure(player_data, quest_id)
