"""How a combat burst stops and settles: the status tick that can end it before
either side attacks, the kill, death and empty-encounter settlement after it,
and the Wilderness ambush that can follow a burst the player survived."""

from .logic_pure_combat_food import _combat_consume_auto_food
from .logic_pure_combat_model import _combat_apply_pvm_death, _combat_apply_wilderness_ambush
from .logic_pure_combat_specials import _combat_death_prayer_damage
from .logic_pure_combat_supplies import (
    _combat_advance_status_effects,
    _combat_consume_antipoison_if_needed,
    _combat_should_auto_flee,
    _combat_void_shifter_escape_ready,
)
from .logic_pure_state import _non_negative_int, _positive_int


def _combat_advance_status_tick(
    data,
    player_lp,
    max_player_lp,
    rng,
    potions_used,
    food_used,
    status_damage,
    status_expired,
):
    """Advance status effects by one tick, eating after status damage. Returns
    the player's lifepoints and why the burst stops before either side attacks:
    "died", "void_shifter", "auto_flee" or ""."""
    potion_event = _combat_consume_antipoison_if_needed(data)
    if potion_event:
        potions_used.append(potion_event)
    status_result = _combat_advance_status_effects(data, 1, player_lp, max_player_lp)
    player_lp = _non_negative_int(data.get("combat_lifepoints", player_lp), player_lp)
    for effect_name, amount in (status_result.get("damage", {}) or {}).items():
        status_damage[effect_name] = _non_negative_int(status_damage.get(effect_name, 0), 0) + _non_negative_int(amount, 0)
    status_expired.extend(status_result.get("expired", ()) or ())
    if status_result.get("died"):
        return player_lp, "died"
    if status_result.get("damage"):
        player_lp, food_event = _combat_consume_auto_food(data, player_lp, max_player_lp, rng)
        if food_event:
            food_used.append(food_event)
        if _combat_void_shifter_escape_ready(data, player_lp, max_player_lp):
            return player_lp, "void_shifter"
    if _combat_should_auto_flee(data, player_lp, max_player_lp):
        return player_lp, "auto_flee"
    return player_lp, ""


def _combat_settle_burst_outcome(
    data,
    target_id,
    kills,
    died,
    fled,
    player_lp,
    max_player_lp,
    enemy_lp,
    enemy_max_lp,
    selected_prayers,
    finisher,
    rng,
    *,
    live_cadence,
    safe_death,
    no_grave,
):
    """Record the burst's kills, then settle a death or drop an encounter that
    has nothing to carry. Returns the player's lifepoints, the death-prayer
    damage dealt to the enemy, and whether the caller carries the encounter."""
    # Chaining means a single burst can defeat several enemies and still end in
    # a partial survivor or a death, so kills, death, and the carried encounter
    # are independent rather than mutually exclusive branches.
    if kills > 0:
        kill_counts = dict(data.get("combat_kill_counts", {}) or {})
        kill_counts[target_id] = _positive_int(kill_counts.get(target_id, 0), 0) + kills
        data["combat_kill_counts"] = kill_counts
    if not died:
        # No partial progress to carry: the player fled, nothing was fought, or the
        # burst ended right after a kill respawned a fresh full-LP enemy.
        if fled or enemy_lp <= 0 or (enemy_lp >= enemy_max_lp and not live_cadence):
            data["combat_encounter"] = {}
            return player_lp, 0, False
        return player_lp, 0, True
    death_burst = 0
    if "wrath" in selected_prayers or "retribution" in selected_prayers:
        # Death prayers cap with allow_automatic=False, so they never count as
        # an automatic finisher.
        death_burst, _automatic_finisher = _combat_death_prayer_damage(
            data, selected_prayers, finisher, enemy_lp, rng
        )
    if safe_death:
        data["combat_encounter"] = {}
        data["combat_status_effects"] = {}
        return max_player_lp, death_burst, False
    return _combat_apply_pvm_death(data, max_player_lp, no_grave=no_grave), death_burst, False


def _combat_settle_wilderness_ambush(
    data,
    enemy,
    player_lp,
    max_player_lp,
    rng,
    equipment_risk,
    food_used,
):
    """Roll the enemy's Wilderness ambush. Returns the ambush record, the
    player's lifepoints and whether the ambush killed them."""
    ambush = _combat_apply_wilderness_ambush(
        data, enemy, player_lp, max_player_lp, rng, equipment_risk
    )
    if not (ambush and ambush.get("triggered")):
        return ambush, player_lp, False
    food_event = ambush.get("food_used")
    if food_event:
        food_used.append(food_event)
    if ambush.get("died"):
        return ambush, max_player_lp, True
    return ambush, _non_negative_int(ambush.get("lifepoints_after", player_lp), player_lp), False
