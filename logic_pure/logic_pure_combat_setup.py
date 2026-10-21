"""How a combat burst sets up both sides before its first tick: the enemy's
lifepoints and whether it still fights back, the prayers the player asked for
and the prayer points they drain, and where a carried live fight resumes its
attack clocks."""

from ..data.prayer_data import PRAYER_UPTIME_POLICIES
from .logic_pure_prayer import (
    _castle_wars_halo_drain_multipliers,
    active_prayer_selection_pure,
    automatic_protection_prayer_pure,
    prayer_drain_and_effective_uptime_pure,
    prayer_effect_state_pure,
    prayer_uptime_fraction_pure,
)
from .logic_pure_state import _non_negative_float, _non_negative_int, _positive_int


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


def _combat_prayer_request(data, live_cadence, automatic_protection_prayer=None):
    """The selected prayers, the Saradomin halo's slower drain on the ones it
    covers, and the uptime the player asked for. A live burst reads the uptime
    policy directly because each tick then drains and reports its own uptime."""
    selected_prayers = tuple(active_prayer_selection_pure(data, automatic_protection_prayer=automatic_protection_prayer))
    halo_drain_multipliers = _castle_wars_halo_drain_multipliers(data, selected_prayers)
    requested_uptime = (
        float(PRAYER_UPTIME_POLICIES.get(str(data.get("combat_prayer_uptime", "off")), 0.0))
        if live_cadence and selected_prayers
        else prayer_uptime_fraction_pure(data)
    )
    automatic = automatic_protection_prayer_pure(data, automatic_protection_prayer)
    if automatic:
        if not bool(data.get("combat_prayers_enabled", True)):
            requested_uptime = 0.0
        requested_uptime = requested_uptime or 1.0
        halo_drain_multipliers[automatic] = halo_drain_multipliers.get(automatic, 1.0) / requested_uptime
    return selected_prayers, halo_drain_multipliers, requested_uptime


def _combat_start_prayer(
    data, selected_prayers, prayer_bonus, ticks, requested_uptime,
    halo_drain_multipliers, live_cadence,
    automatic_protection_prayer=None,
):
    """Prayer at the start of a burst. An ordinary burst drains its whole tick
    budget up front and switches spent prayers off; a live burst drains in each
    tick instead, so it starts at the uptime asked for. Returns the points
    before, the points and drain counter now, the uptime and prayer effects."""
    points_before = _non_negative_int(data.get("combat_prayer_points", 0), 0)
    counter = data.get("combat_prayer_drain_counter", 0.0)
    points, counter, uptime = (
        (points_before, counter, requested_uptime)
        if live_cadence
        else prayer_drain_and_effective_uptime_pure(
            points_before,
            counter,
            selected_prayers,
            prayer_bonus,
            ticks,
            requested_uptime,
            halo_drain_multipliers,
        )
    )
    data["combat_prayer_points"] = points
    data["combat_prayer_drain_counter"] = counter
    prayer_effects = prayer_effect_state_pure(data, uptime, automatic_protection_prayer=automatic_protection_prayer)
    if not live_cadence:
        _combat_switch_off_spent_prayers(data, points, selected_prayers)
    return points_before, points, counter, uptime, prayer_effects


def _combat_prayer_tick(
    data, live_cadence, points, counter, burst_uptime, selected_prayers,
    prayer_bonus, requested_uptime, halo_drain_multipliers,
):
    """One tick's prayer. A live burst drains the tick; an ordinary burst
    already drained up front, so every tick keeps the burst's uptime. Returns
    the points, drain counter, this tick's uptime and its share of the burst's
    uptime, which scales prayer against the enemy's hit this tick."""
    if not live_cadence:
        return points, counter, burst_uptime, 1.0
    points, counter, tick_uptime = prayer_drain_and_effective_uptime_pure(
        points,
        counter,
        selected_prayers,
        prayer_bonus,
        1,
        requested_uptime,
        halo_drain_multipliers,
    )
    data["combat_prayer_points"] = points
    data["combat_prayer_drain_counter"] = counter
    return points, counter, tick_uptime, (
        tick_uptime / burst_uptime if burst_uptime > 0 else 1.0
    )


def _combat_switch_off_spent_prayers(data, points, selected_prayers):
    if points <= 0 and selected_prayers:
        data["combat_selected_prayers"] = []


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


def _combat_spell_factor(encounter, key):
    return max(0.01, min(1.0, _non_negative_float(encounter.get(key, 1.0), 1.0)))


def _combat_spell_enemy_state(encounter, resumed, live_cadence, effect, value):
    """Resume this enemy's spell drains, or apply the spell to a fresh enemy."""
    applied = {str(name) for name in encounter.get("magic_effects_applied", ()) if isinstance(name, str)} if resumed else set()
    attack = _combat_spell_factor(encounter, "spell_enemy_attack_factor") if resumed else 1.0
    defence = _combat_spell_factor(encounter, "spell_enemy_defence_factor") if resumed else 1.0
    if live_cadence and effect in applied:
        return applied, True, attack, defence
    if effect in {"attack_drain", "strength_drain", "magic_drain"}:
        attack *= max(0.0, 1.0 - value)
    elif effect == "defence_drain":
        defence *= max(0.0, 1.0 - value)
    else:
        return applied, False, attack, defence
    if live_cadence:
        applied.add(effect)
    return applied, effect in applied, attack, defence
