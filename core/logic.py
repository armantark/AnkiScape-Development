"""Anki-aware game logic orchestrators (no direct persistence here)."""

from .constants import (
    EXP_TABLE,
    ACHIEVEMENTS,
    BASE_WOODCUTTING_PROBABILITY,
    BASE_MINING_PROBABILITY,
    LEVEL_BONUS_FACTOR,
)
from ..ui.ui import show_level_up_dialog, show_achievement_dialog
from .skill_registry import skill_level_exp_keys


def get_exp_to_next_level(player_data, exp_table):
    current_level = player_data["mining_level"]
    if current_level >= 99:
        return 0
    return exp_table[current_level] - player_data["total_exp"]

from ..logic_pure.logic_pure import calculate_new_level, calculate_probability_with_level

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

from ..logic_pure.logic_pure import get_newly_completed_achievements
from ..logic.achievement_diary_logic import (
    diary_task_by_id_pure,
    refresh_achievement_diaries_pure,
)


def _popups_enabled():
    """Whether a completion popup can and should be shown.

    Diary tasks receive retroactive credit, so a single review can complete
    several at once in an environment that has no Qt at all — a headless test,
    or an Anki build whose Qt import failed. `ui.ui` degrades to no-ops in that
    case, so ask it for the dialog's own symbol before promising a dialog.
    """
    from ..ui import ui as ui_module

    if getattr(ui_module, "QDialog", None) is None:
        return False
    try:
        from aqt import mw  # type: ignore
        return bool(mw.col.get_config("ankiscape_popups_enabled", True)) if getattr(mw, 'col', None) else True
    except Exception:
        return True


def check_achievements(player_data):
    """Advance both achievement ledgers after a review.

    The 168-row catalog is no longer a player-facing list — the Achievement
    Cabinet replaced it — but it stays live here as the history substrate the
    2026-07-16 semantics contract defines, so completed names keep their sticky
    meaning and no save loses its recorded past. The popup now belongs to the
    diary task that actually names a period feat.
    """
    newly_completed = get_newly_completed_achievements(player_data, ACHIEVEMENTS)
    if newly_completed:
        player_data.setdefault("completed_achievements", []).extend(newly_completed)

    updated, newly_tasks = refresh_achievement_diaries_pure(player_data)
    player_data.clear()
    player_data.update(updated)
    if not newly_tasks or not _popups_enabled():
        return
    for task_id in newly_tasks:
        found = diary_task_by_id_pure(task_id)
        if found is None:
            continue
        family, tier, task = found
        show_achievement_dialog(
            task.name,
            {
                "description": task.description,
                "difficulty": f"{family.name} — {tier.name}",
            },
        )


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
