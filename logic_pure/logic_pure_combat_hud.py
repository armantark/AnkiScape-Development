"""The combat HUD's health, prayer and summoning bars, last-fight summary and
finisher text."""

from typing import Mapping

from .logic_pure_combat_finishers import (
    combat_finisher_notice_pure,
    combat_finisher_tooltip_pure,
)
from .logic_pure_combat_model import combat_max_lifepoints_pure
from .logic_pure_state import _non_negative_int, _positive_int


def _combat_hud_pct(value, ceiling):
    return int((min(value, ceiling) / ceiling) * 100) if ceiling > 0 else 0


def _combat_hud_player_bars(player_data):
    """Lifepoints, prayer and summoning, each clamped to its maximum."""
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = max(0, min(_non_negative_int(player_data.get("combat_lifepoints", max_lp), max_lp), max_lp))
    prayer_max = _positive_int(player_data.get("prayer_level", 1), 1)
    prayer_current = min(
        prayer_max * 10,
        _non_negative_int(
            player_data.get("combat_prayer_points", prayer_max * 10),
            prayer_max * 10,
        ),
    ) // 10
    summoning_max = _positive_int(player_data.get("summoning_level", 1), 1)
    summoning_state = player_data.get("summoning_state", {}) or {}
    summoning_current = min(
        summoning_max,
        _non_negative_int(
            summoning_state.get("summoning_points_current", summoning_max)
            if isinstance(summoning_state, Mapping)
            else summoning_max,
            summoning_max,
        ),
    )
    return {
        "player_lifepoints": current_lp,
        "player_max_lifepoints": max_lp,
        "player_pct": _combat_hud_pct(current_lp, max_lp),
        "prayer_points": prayer_current,
        "prayer_max_points": prayer_max,
        "summoning_points": summoning_current,
        "summoning_max_points": summoning_max,
    }


def _combat_hud_enemy_bar(player_data, target_id, enemy_data):
    """The target's health, carried over only from an unfinished encounter with
    that same target."""
    enemy = enemy_data.get(target_id) if isinstance(target_id, str) else None
    if isinstance(enemy, Mapping):
        enemy_name = str(enemy.get("display_name", target_id))
        enemy_max_lp = _positive_int(enemy.get("stats", {}).get("hitpoints", 1), 1)
    else:
        enemy_name = "Enemy"
        enemy_max_lp = 0
    encounter = player_data.get("combat_encounter", {}) or {}
    carried = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id and enemy_max_lp > 0
    if carried:
        enemy_lp = max(0, min(_positive_int(encounter.get("enemy_lifepoints", enemy_max_lp), enemy_max_lp), enemy_max_lp))
    else:
        enemy_lp = enemy_max_lp
    return {
        "enemy_name": enemy_name,
        "enemy_lifepoints": enemy_lp,
        "enemy_max_lifepoints": enemy_max_lp,
        "enemy_pct": _combat_hud_pct(enemy_lp, enemy_max_lp),
        "enemy_carried": bool(carried),
    }


def _combat_hud_last_fight(player_data, target_id):
    """The target's kill count and how the last burst ended."""
    kills_total = _non_negative_int((player_data.get("combat_kill_counts", {}) or {}).get(target_id, 0), 0)
    last = player_data.get("combat_last_result", {}) or {}
    last = last if isinstance(last, Mapping) else {}
    last_kills = _non_negative_int(last.get("kills", 0), 0)
    if last.get("died"):
        last_outcome = "died"
    elif last.get("fled"):
        last_outcome = "fled"
    else:
        last_outcome = ""
    return {
        "kills_total": kills_total,
        "last_kills": last_kills,
        "last_outcome": last_outcome,
    }


def _combat_hud_finisher_text(finisher):
    """The strip's finisher prompt, and the combat menu's tooltip for the
    finisher option, which reads the same HUD state."""
    return {
        "finisher_notice": combat_finisher_notice_pure(finisher),
        "finisher_tooltip": combat_finisher_tooltip_pure(finisher),
    }
