"""Quest skill gates, including the attested consumable boost at Horror's start."""

from typing import Mapping

from ...core.skill_registry import get_skill
from .skill_levels import skill_level_requirement_reason_pure
from ..logic_pure_combat_engine import player_combat_level_pure
from ..logic_pure_state import _non_negative_int, _positive_int


def _quest_requirement_level(player_data, skill_id, level_key, quest_id):
    level = _positive_int(player_data.get(level_key, 1), 1)
    if quest_id == "horror_from_the_deep" and skill_id == "agility":
        if _non_negative_int(player_data.get("agility_boost_actions_remaining", 0), 0) > 0:
            level += min(20, _non_negative_int(player_data.get("agility_effective_boost", 0), 0))
    return level


def _skill_requirement_reason(player_data, requirement, *, quest_id=""):
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
    level_override = _quest_requirement_level(player_data, skill_id, skill.level_key, quest_id) if skill else None
    return skill_level_requirement_reason_pure(player_data, requirement, level_override=level_override)
