"""Skill-level gates without importing the Combat engine or quest controllers."""

from typing import Mapping

from ...core.skill_registry import get_skill
from ..logic_pure_state import _positive_int


def skill_level_requirement_reason_pure(player_data, requirement, *, level_override=None):
    if not isinstance(requirement, Mapping):
        return None
    skill_id = requirement.get("skill_id")
    if not isinstance(skill_id, str):
        return None
    skill = get_skill(skill_id)
    label = str(requirement.get("display_name") or (skill.display_name if skill else skill_id.replace("_", " ").title()))
    level_required = _positive_int(requirement.get("level", 1), 1)
    if skill is None or not skill.trainable or skill.level_key not in player_data:
        return f"{label} {level_required} (not implemented)"
    level = _positive_int(player_data.get(skill.level_key, 1), 1) if level_override is None else level_override
    return f"{label} {level_required}" if level < level_required else None
