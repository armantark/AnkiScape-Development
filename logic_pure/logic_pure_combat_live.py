"""Live-cadence rolls: a live burst resolves one tick at a time, so prayers
count only for the share of the tick they were up and the curse ramp grows with
each player attack. Both sides' accuracy and the player's max hit scale here."""

from .logic_pure_combat_model import _combat_accuracy
from .logic_pure_prayer import curse_expected_ramp_pure


def _combat_live_curse_adjustments(selected_prayers, curse_attack_count, tick_uptime):
    enemy_drain = 0.0
    self_boost = 0.0
    if any(prayer_id.startswith("sap_") for prayer_id in selected_prayers):
        enemy_drain = max(
            enemy_drain,
            curse_expected_ramp_pure(curse_attack_count, "sap")["enemy_drain"],
        )
    if any(prayer_id.startswith("leech_") for prayer_id in selected_prayers):
        ramp = curse_expected_ramp_pure(curse_attack_count, "leech")
        enemy_drain = max(enemy_drain, ramp["enemy_drain"])
        self_boost = max(self_boost, ramp["self_boost"])
    return enemy_drain * tick_uptime, self_boost * tick_uptime


def _combat_live_prayer_factor(prayer_effects, prayer_uptime, effect_key, tick_uptime):
    fallback_key = "ranged" if effect_key.startswith("ranged_") else effect_key
    full = float(prayer_effects.get(effect_key, prayer_effects.get(fallback_key, 1.0)))
    if prayer_uptime <= 0:
        return 1.0
    ratio = max(0.0, min(float(tick_uptime) / prayer_uptime, 1.0))
    return 1.0 + (full - 1.0) * ratio


def _combat_live_player_rolls(
    combat_class,
    player_attack_roll,
    player_max_hit,
    enemy_defence_roll,
    enemy_defence_factor,
    spell_enemy_defence_factor,
    prayer_effects,
    prayer_uptime,
    tick_prayer_uptime,
    selected_prayers,
    curse_attack_count,
):
    """Rescale the burst's full-uptime player accuracy and max hit to this
    tick's prayer uptime and curse ramp."""
    live_enemy_drain, live_self_boost = _combat_live_curse_adjustments(
        selected_prayers, curse_attack_count, tick_prayer_uptime
    )
    attack_effect_key = {
        "ranged": "ranged_attack",
        "magic": "magic",
    }.get(combat_class, "attack")
    strength_effect_key = {
        "ranged": "ranged_strength",
        "magic": "magic",
    }.get(combat_class, "strength")
    full_attack_factor = max(
        0.000001,
        float(
            prayer_effects.get(
                attack_effect_key,
                prayer_effects.get(
                    "ranged" if combat_class == "ranged" else attack_effect_key,
                    1.0,
                ),
            )
        ),
    )
    full_strength_factor = max(
        0.000001,
        float(
            prayer_effects.get(
                strength_effect_key,
                prayer_effects.get(
                    "ranged" if combat_class == "ranged" else strength_effect_key,
                    1.0,
                ),
            )
        ),
    )
    current_attack_factor = _combat_live_prayer_factor(
        prayer_effects, prayer_uptime, attack_effect_key, tick_prayer_uptime
    )
    current_strength_factor = _combat_live_prayer_factor(
        prayer_effects, prayer_uptime, strength_effect_key, tick_prayer_uptime
    )
    current_enemy_defence_factor = max(
        0.01,
        spell_enemy_defence_factor * (1.0 - live_enemy_drain),
    )
    live_player_accuracy = _combat_accuracy(
        player_attack_roll / full_attack_factor * current_attack_factor,
        enemy_defence_roll
        / max(enemy_defence_factor, 0.000001)
        * current_enemy_defence_factor,
    )
    live_player_max_hit = max(
        0,
        int(
            player_max_hit
            / full_strength_factor
            * current_strength_factor
            * (1.0 + live_self_boost)
        ),
    )
    return live_player_accuracy, live_player_max_hit


def _combat_live_enemy_accuracy(
    enemy_attack_roll,
    player_defence_roll,
    enemy_attack_factor,
    spell_enemy_attack_factor,
    prayer_effects,
    prayer_uptime,
    tick_prayer_uptime,
    selected_prayers,
    curse_attack_count,
):
    """Rescale the burst's full-uptime enemy accuracy to this tick's prayer
    uptime and curse drain."""
    live_enemy_drain, _live_self_boost = _combat_live_curse_adjustments(
        selected_prayers, curse_attack_count, tick_prayer_uptime
    )
    full_defence_factor = max(
        0.000001, float(prayer_effects.get("defence", 1.0))
    )
    current_defence_factor = _combat_live_prayer_factor(
        prayer_effects, prayer_uptime, "defence", tick_prayer_uptime
    )
    current_enemy_attack_factor = max(
        0.01,
        spell_enemy_attack_factor * (1.0 - live_enemy_drain),
    )
    return _combat_accuracy(
        enemy_attack_roll
        / max(enemy_attack_factor, 0.000001)
        * current_enemy_attack_factor,
        player_defence_roll
        / full_defence_factor
        * current_defence_factor,
    )
