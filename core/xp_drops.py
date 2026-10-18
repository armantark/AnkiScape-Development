"""Whole-number XP changes for review feedback; awards keep their precision."""

from math import floor

from .skill_registry import trainable_skill_definitions


def whole_number_xp_breakdown(before, after):
    breakdown = []
    for skill in trainable_skill_definitions():
        gained = floor(float(after.get(skill.exp_key, 0) or 0)) - floor(
            float(before.get(skill.exp_key, 0) or 0)
        )
        if gained > 0:
            breakdown.append((skill.display_name, gained))
    return breakdown
