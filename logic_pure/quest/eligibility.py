"""Quest start requirements, shared with performed opening eligibility checks."""

from collections.abc import Mapping

from ...core.skill_registry import get_skill
from ...data.quest.elemental_workshop_iii import QUEST_ID
from ..logic_pure_combat_engine import player_combat_level_pure
from ..logic_pure_state import _positive_int, quest_completed_pure, quest_state_pure


def _skill_requirement_reason(player_data, requirement):
    if not isinstance(requirement, Mapping):
        return None
    skill_id = requirement.get("skill_id")
    display_name = requirement.get("display_name")
    if not isinstance(skill_id, str):
        return None
    skill = get_skill(skill_id)
    label = str(display_name or (skill.display_name if skill is not None else skill_id.replace("_", " ").title()))
    level_required = _positive_int(requirement.get("level", 1), 1)
    if skill_id == "combat":
        return None if player_combat_level_pure(player_data) >= level_required else f"{label} {level_required}"
    if skill is None or not skill.trainable:
        return f"{label} {level_required} (not implemented)"
    level_key = skill.level_key
    if level_key not in player_data:
        return f"{label} {level_required} (not implemented)"
    if _positive_int(player_data.get(level_key, 1), 1) < level_required:
        return f"{label} {level_required}"
    return None


def _prerequisite_reasons(player_data, quest, quest_data):
    reasons = []
    for requirement in quest.get("required_quests", ()) or ():
        if not isinstance(requirement, Mapping):
            continue
        required_id = requirement.get("quest_id")
        if not isinstance(required_id, str):
            continue
        label = requirement.get("display_name") or required_id.replace("_", " ").title()
        if not isinstance(quest_data.get(required_id), Mapping):
            reasons.append(f"{label} (not implemented)")
        elif not quest_completed_pure(player_data, required_id):
            reasons.append(str(label))
    return reasons


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
        reason = _skill_requirement_reason(view, requirement)
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
    reasons = _prerequisite_reasons(player_data, quest, quest_data)
    reasons.extend(_skill_reasons(player_data, quest_id, quest))
    reasons.extend(_point_and_item_reasons(player_data, quest))
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
