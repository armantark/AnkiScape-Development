"""How a combat burst sets up both sides before its first tick: the enemy's
lifepoints and whether it still fights back, the prayers the player asked for,
and where a carried live fight resumes its attack clocks."""

from ..data.prayer_data import PRAYER_UPTIME_POLICIES
from .logic_pure_prayer import (
    _castle_wars_halo_drain_multipliers,
    active_prayer_selection_pure,
    prayer_uptime_fraction_pure,
)
from .logic_pure_state import _non_negative_int, _positive_int


def _combat_enemy_start_lifepoints(enemy, encounter, active_encounter):
    """The enemy's maximum and current lifepoints, resumed from a carried
    encounter, and the lifepoints at or below which it stops fighting back.
    Returns those three and whether it has already stopped."""
    enemy_max_lp = _positive_int(enemy.get("stats", {}).get("hitpoints", 1), 1)
    enemy_lp = (
        max(0, min(_positive_int(encounter.get("enemy_lifepoints", enemy_max_lp), enemy_max_lp), enemy_max_lp))
        if active_encounter
        else enemy_max_lp
    )
    stop_lifepoints = _non_negative_int(enemy.get("retaliation_stop_lifepoints", 0), 0)
    stopped = bool(
        stop_lifepoints > 0
        and (
            enemy_lp <= stop_lifepoints
            or (active_encounter and encounter.get("retaliation_stopped", False))
        )
    )
    return enemy_max_lp, enemy_lp, stop_lifepoints, stopped


def _combat_prayer_request(data, live_cadence):
    """The selected prayers, the Saradomin halo's slower drain on the ones it
    covers, and the uptime the player asked for. A live burst reads the uptime
    policy directly because each tick then drains and reports its own uptime."""
    selected_prayers = tuple(active_prayer_selection_pure(data))
    halo_drain_multipliers = _castle_wars_halo_drain_multipliers(data, selected_prayers)
    requested_uptime = (
        float(PRAYER_UPTIME_POLICIES.get(str(data.get("combat_prayer_uptime", "off")), 0.0))
        if live_cadence and selected_prayers
        else prayer_uptime_fraction_pure(data)
    )
    return selected_prayers, halo_drain_multipliers, requested_uptime


def _combat_resume_attack_clocks(encounter, resumed, enemy_attack_speed):
    """The ticks until each side attacks and the Curse ramp's attack count: a
    carried live fight resumes them, anything else starts fresh."""
    if not resumed:
        return 0, enemy_attack_speed, 0
    return (
        _non_negative_int(encounter.get("player_attack_ticks_remaining", 0), 0),
        _non_negative_int(
            encounter.get("enemy_attack_ticks_remaining", enemy_attack_speed),
            enemy_attack_speed,
        ),
        _non_negative_int(encounter.get("curse_attack_count", 0), 0),
    )
