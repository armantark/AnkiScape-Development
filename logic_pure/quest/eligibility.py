"""Quest start requirements, shared with performed opening eligibility checks."""

from ...data.quest.elemental_workshop_iii import QUEST_ID
from ..logic_pure_state import _positive_int, quest_state_pure
from .skill_requirements import _skill_requirement_reason
from .start_requirements import _quest_prerequisite_reasons_pure, _quest_museum_claim_reasons_pure


def _skill_evaluation_view(player_data, quest_id):
    if quest_id != QUEST_ID:
        return player_data
    from ...logic.skilling_boost_logic import skilling_effective_level_pure
    from ..logic_pure_combat_model import _combat_effective_skill_level

    view = dict(player_data)
    for skill_id in ("mining", "smithing"):
        view[f"{skill_id}_level"] = skilling_effective_level_pure(player_data, skill_id)
    view["defense_level"] = _combat_effective_skill_level(player_data, "defense", 1)
    return view


def _skill_reasons(player_data, quest_id, quest):
    view = _skill_evaluation_view(player_data, quest_id)
    reasons = []
    for requirement in quest.get("required_skills", ()) or ():
        reason = _skill_requirement_reason(view, requirement, quest_id=quest_id)
        if reason:
            reasons.append(reason)
    return reasons


def _point_and_item_reasons(player_data, quest):
    reasons = []
    required_points = _positive_int(quest.get("required_quest_points", 0), 0)
    if required_points and _positive_int(player_data.get("quest_points", 0), 0) < required_points:
        reasons.append(f"{required_points} quest points")
    inventory = player_data.get("inventory", {}) or {}
    for item_name, amount in (quest.get("required_items", {}) or {}).items():
        if inventory.get(item_name, 0) < amount:
            reasons.append(f"{item_name} x{amount}")
    return reasons


def quest_eligibility_reasons_pure(player_data, quest_id, quest_data):
    """Recheck real requirements even when a quest was already selected."""
    quest = quest_data.get(quest_id)
    if not quest:
        return ("unknown quest",)
    reasons = _quest_prerequisite_reasons_pure(player_data, quest, quest_data)
    reasons.extend(_skill_reasons(player_data, quest_id, quest))
    reasons.extend(_point_and_item_reasons(player_data, quest))
    reasons.extend(_quest_museum_claim_reasons_pure(player_data, quest_id))
    return tuple(dict.fromkeys(reasons))


def quest_locked_reasons_pure(player_data, quest_id, quest_data):
    if not quest_data.get(quest_id):
        return ("unknown quest",)
    state = quest_state_pure(player_data, quest_id)
    if state["completed"]:
        return ("completed",)
    if state["started"]:
        return tuple()
    return quest_eligibility_reasons_pure(player_data, quest_id, quest_data)
