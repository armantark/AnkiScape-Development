"""Anki-aware game logic orchestrators (no direct persistence here)."""

from .constants import (
    EXP_TABLE,
    ACHIEVEMENTS,
    BASE_WOODCUTTING_PROBABILITY,
    BASE_MINING_PROBABILITY,
    LEVEL_BONUS_FACTOR,
)
from .ui import show_level_up_dialog, show_achievement_dialog
try:
    from .skill_registry import skill_level_exp_keys
except ImportError:
    from skill_registry import skill_level_exp_keys


def get_exp_to_next_level(player_data, exp_table):
    current_level = player_data["mining_level"]
    if current_level >= 99:
        return 0
    return exp_table[current_level] - player_data["total_exp"]

from .logic_pure import calculate_new_level, calculate_probability_with_level

def level_up_check(skill, player_data):
    skill_keys = skill_level_exp_keys(skill)
    if skill_keys is not None:
        level_key, exp_key = skill_keys
        old_level = player_data[level_key]
        new_level = calculate_new_level(player_data[exp_key], old_level, EXP_TABLE)
        if new_level > old_level:
            for lvl in range(old_level + 1, new_level + 1):
                player_data[level_key] = lvl
                # Respect user setting for popups
                try:
                    from aqt import mw  # type: ignore
                    enabled = bool(mw.col.get_config("ankiscape_popups_enabled", True)) if getattr(mw, 'col', None) else True
                except Exception:
                    enabled = True
                if enabled:
                    show_level_up_dialog(skill)

from .logic_pure import get_newly_completed_achievements

def check_achievements(player_data):
    newly_completed = get_newly_completed_achievements(player_data, ACHIEVEMENTS)
    for achievement in newly_completed:
        player_data["completed_achievements"].append(achievement)
        # Respect user setting for popups
        try:
            from aqt import mw  # type: ignore
            enabled = bool(mw.col.get_config("ankiscape_popups_enabled", True)) if getattr(mw, 'col', None) else True
        except Exception:
            enabled = True
        if enabled:
            show_achievement_dialog(achievement, ACHIEVEMENTS[achievement])


def calculate_woodcutting_probability(player_level: int, tree_probability: float) -> float:
    return calculate_probability_with_level(
        player_level,
        BASE_WOODCUTTING_PROBABILITY,
        LEVEL_BONUS_FACTOR,
        tree_probability,
        cap=0.95,
    )


def calculate_mining_probability(player_level: int, ore_probability: float) -> float:
    return calculate_probability_with_level(
        player_level,
        BASE_MINING_PROBABILITY,
        LEVEL_BONUS_FACTOR,
        ore_probability,
        cap=0.95,
    )
