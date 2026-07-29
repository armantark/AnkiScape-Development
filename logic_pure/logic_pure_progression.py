"""logic_pure_progression.py - split out of logic_pure.py; see that module's header."""

from math import comb, floor, sqrt

from typing import Iterable, Mapping, Optional

from ..data.mining_data import MINING_REVIEW_DAY_CARDS, RED_SANDSTONE_DAILY_CAP

from .logic_pure_state import (  # noqa: F401  (re-export)
    COMBAT_BANK_RUN_REVIEWS,
    COMBAT_GRAVE_RECOVERY_REVIEWS,
    _COMBAT_DRAGONFIRE_POTION_BY_DOSE,
    _COMBAT_DRAGONFIRE_POTION_ITEM_NAMES,
    _COMBAT_STAT_POTION_BY_DOSE,
    _COMBAT_STAT_POTION_ITEM_NAMES,
    _build_combat_potion_dose_lookup,
    _combat_grave_items,
    _combat_stored_loadout,
    _copy_player_data_with_nested,
    _non_negative_float,
    _non_negative_int,
    _positive_int,
    _requirements_from_spec,
    _sanitize_combat_bank_run,
    _sanitize_combat_grave_state,
    _sanitize_combat_supply_loadout,
    _sanitize_death_office_state,
    _signed_int,
    default_combat_supply_loadout_pure,
    quest_completed_pure,
    quest_state_pure,
    sanitize_quest_combat_active_encounters_pure,
)

from .logic_pure_state import (
    _non_negative_int,
    _positive_int,
)


REVIEW_SUCCESS_MINIMUM = 0.20


REVIEW_SUCCESS_SCALE = 0.72


REVIEW_SUCCESS_CAP = 0.95


def get_exp_to_next_level(player_data, EXP_TABLE):
    """Return exp needed to reach the next level for Mining.
    Supports EXP_TABLE as list or dict. Uses mining_exp, falls back to legacy total_exp.
    When at or beyond max level or threshold missing, returns 0.
    """
    current_level = player_data.get("mining_level", player_data.get("level", 1))
    max_level = 99 if isinstance(EXP_TABLE, dict) else len(EXP_TABLE)
    if current_level >= max_level:
        return 0
    # Determine threshold for next level from EXP_TABLE
    if isinstance(EXP_TABLE, dict):
        threshold = EXP_TABLE.get(current_level)
    else:
        try:
            threshold = EXP_TABLE[current_level]
        except (IndexError, TypeError):
            threshold = None
    if threshold is None:
        return 0
    skill_exp = player_data.get("mining_exp", player_data.get("total_exp", 0))
    needed = threshold - skill_exp
    return needed if needed > 0 else 0


def compute_level_progress(level: int, exp: float, exp_table: list) -> tuple[int, float, int]:
    """Pure helper for computing percent, remaining XP, and target level.
    Returns (percent, xp_remaining, target_level). Clamps values sensibly.
    - At the table's maximum level, always return 100% and 0 remaining.
    """
    try:
        lvl = max(1, int(level))
        xp = float(exp or 0)
        max_level = len(exp_table)

        if lvl >= max_level:
            return 100, 0.0, max_level

        # Compute thresholds for the current level segment
        prev = float(exp_table[lvl - 1])
        nxt = float(exp_table[lvl])

        # If thresholds are degenerate (e.g., at end), treat as maxed
        if nxt <= prev:
            return 100, 0.0, max_level

        # Clamp percent to [0, 100] and remaining to >= 0
        span = nxt - prev
        pct_float = ((xp - prev) / span) * 100.0
        if xp >= nxt:
            pct = 100
            remain = 0.0
        else:
            pct = int(max(0.0, min(100.0, pct_float)))
            remain = max(0.0, nxt - xp)

        target_lv = min(lvl + 1, max_level)
        return pct, remain, target_lv
    except Exception:
        # Fallback on error: show safe defaults and a reasonable next target
        try:
            safe_lvl = max(1, int(level))
        except Exception:
            safe_lvl = 1
        try:
            max_level = max(1, len(exp_table))
        except Exception:
            max_level = 99
        return 0, 0.0, min(safe_lvl + 1, max_level)


def calculate_new_level(skill_exp, current_level, EXP_TABLE):
    """
    Calculate the new level for a skill given experience, current level, and EXP_TABLE.
    Supports EXP_TABLE as a dict (level -> threshold) or a list where index (level-1) stores threshold.
    Returns the new level (int).
    """
    new_level = current_level
    if isinstance(EXP_TABLE, dict):
        try:
            max_level = max(int(level) for level in EXP_TABLE)
        except (TypeError, ValueError):
            max_level = new_level
    else:
        try:
            max_level = len(EXP_TABLE)
        except TypeError:
            max_level = new_level
    while new_level < max_level:
        # Determine threshold to reach next level (new_level+1)
        if isinstance(EXP_TABLE, dict):
            threshold = EXP_TABLE.get(new_level + 1)
        else:
            try:
                # In list form, index equals current level (new_level) for threshold to reach next level
                threshold = EXP_TABLE[new_level]
            except (IndexError, TypeError):
                threshold = None

        if threshold is None or skill_exp < threshold:
            break
        new_level += 1
    return new_level


def get_newly_completed_achievements(player_data, ACHIEVEMENTS):
    """
    Returns a list of achievement names that are newly completed (not yet in player_data["completed_achievements"])
    """
    completed_names = list(player_data.get("completed_achievements", []))
    completed = set(completed_names)
    newly_completed = []
    projected_data = dict(player_data)
    while True:
        added = False
        projected_data["completed_achievements"] = completed_names + newly_completed
        for name, data in ACHIEVEMENTS.items():
            if name in completed or name in newly_completed:
                continue
            if data["condition"](projected_data):
                newly_completed.append(name)
                projected_data["completed_achievements"] = completed_names + newly_completed
                added = True
        if not added:
            break
    return newly_completed


def calculate_probability_with_level(player_level, base_probability, level_bonus_factor, source_probability, cap=0.95):
    """
    Compute success probability given a player's level and base probabilities.
    Probability = min(base_probability + player_level * level_bonus_factor, cap) * source_probability
    """
    level_bonus = player_level * level_bonus_factor
    return min(base_probability + level_bonus, cap) * source_probability


def pick_gem(gem_data, r):
    """
    Deterministically pick a gem given gem_data and a random draw r in [0, 1).
    gem_data: { name: { "probability": float }, ... }
    Returns the gem name, or None if r exceeds the total probability mass.
    """
    cumulative = 0.0
    for gem, data in gem_data.items():
        cumulative += data.get("probability", 0.0)
        if r < cumulative:
            return gem
    return None


def pick_weighted_item_pure(weighted_items, r, total_weight=None):
    """Pick an item from source-style weighted slots using a [0, 1) roll."""
    if total_weight is None:
        total_weight = sum(_positive_int(item.get("weight", 0), 0) for item in weighted_items)
    if total_weight <= 0:
        return None
    threshold = max(0.0, min(float(r), 0.999999999)) * total_weight
    cumulative = 0
    for item in weighted_items:
        cumulative += _positive_int(item.get("weight", 0), 0)
        if threshold < cumulative:
            return item.get("item")
    last = weighted_items[-1] if weighted_items else {}
    return last.get("item")


def sanitize_review_action_multiplier(value, default=1, minimum=1, maximum=10):
    """Return the integer number of game action ticks one review can run."""
    if isinstance(value, bool):
        return default
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        return default
    if multiplier != multiplier:
        return default
    if multiplier < minimum:
        return minimum
    if multiplier > maximum:
        return maximum
    return int(multiplier)


def sanitize_xp_multiplier(value, default=1.0, minimum=0.0, maximum=100.0):
    """Compatibility wrapper for old configs/tests; review rewards no longer use it."""
    if isinstance(value, bool):
        return default
    try:
        multiplier = float(value)
    except (TypeError, ValueError):
        return default
    if multiplier != multiplier:
        return default
    if multiplier < minimum:
        return minimum
    if multiplier > maximum:
        return maximum
    return multiplier


def default_red_sandstone_daily_state_pure():
    return {"review_day": 0, "mined": 0}


def red_sandstone_review_day_pure(player_data):
    clock = player_data.get("shop_market_clock")
    answered = (
        _non_negative_int(clock.get("answered_cards"), 0)
        if isinstance(clock, Mapping)
        else 0
    )
    return answered // MINING_REVIEW_DAY_CARDS


def sanitize_red_sandstone_daily_state_pure(raw_state, current_review_day=0):
    current_day = _non_negative_int(current_review_day, 0)
    source = raw_state if isinstance(raw_state, Mapping) else {}
    saved_day = _non_negative_int(source.get("review_day"), 0)
    mined = (
        min(_non_negative_int(source.get("mined"), 0), RED_SANDSTONE_DAILY_CAP)
        if saved_day == current_day
        else 0
    )
    return {"review_day": current_day, "mined": mined}


def red_sandstone_daily_state_pure(player_data):
    return sanitize_red_sandstone_daily_state_pure(
        player_data.get("red_sandstone_daily"),
        red_sandstone_review_day_pure(player_data),
    )


def red_sandstone_daily_remaining_pure(player_data):
    state = red_sandstone_daily_state_pure(player_data)
    return max(RED_SANDSTONE_DAILY_CAP - int(state["mined"]), 0)


def normalize_review_success_probability_pure(
    source_chance,
    minimum=REVIEW_SUCCESS_MINIMUM,
    scale=REVIEW_SUCCESS_SCALE,
    cap=REVIEW_SUCCESS_CAP,
):
    """Adapt source tick odds to one AnkiScape review-action roll."""
    try:
        source = float(source_chance)
    except (TypeError, ValueError):
        source = 0.0
    source = max(0.0, min(source, 1.0))
    return max(0.0, min(float(minimum) + (sqrt(source) * float(scale)), float(cap)))
