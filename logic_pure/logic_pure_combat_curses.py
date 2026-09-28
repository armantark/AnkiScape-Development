"""How Curses change a burst's rolls at the burst's prayer uptime: Sap and Leech
drain the enemy's attack and defence by their expected ramp and each Leech
boosts its own stat, and Turmoil boosts the player from the enemy's levels."""

from .logic_pure_combat_model import _combat_base_skill_level
from .logic_pure_prayer import curse_expected_ramp_pure
from .logic_pure_state import _positive_int

_LEECH_ATTACK_DRAINS = frozenset(("leech_attack", "leech_ranged", "leech_magic", "leech_strength"))
_LEECH_SELF_EFFECTS = {
    "leech_attack": "attack", "leech_strength": "strength",
    "leech_defence": "defence", "leech_ranged": "ranged",
    "leech_magic": "magic",
}


def _combat_curse_drains(
    selected_prayers,
    expected_attacks,
    prayer_uptime,
    prayer_effects,
    enemy_attack_factor,
    enemy_defence_factor,
):
    """Apply each selected Sap and Leech curse. Returns the enemy's attack and
    defence factors; Leech boosts are raised in prayer_effects in place."""
    sap_drain = curse_expected_ramp_pure(expected_attacks, "sap")["enemy_drain"] * prayer_uptime
    leech_ramp = curse_expected_ramp_pure(expected_attacks, "leech")
    leech_drain = leech_ramp["enemy_drain"] * prayer_uptime
    self_effect = 1.0 + leech_ramp["self_boost"] * prayer_uptime
    for prayer_id in selected_prayers:
        if prayer_id.startswith("sap_"):
            enemy_attack_factor *= 1.0 - sap_drain
            if prayer_id != "sap_spirit":
                enemy_defence_factor *= 1.0 - sap_drain
        elif prayer_id in _LEECH_ATTACK_DRAINS:
            enemy_attack_factor *= 1.0 - leech_drain
        elif prayer_id == "leech_defence":
            enemy_defence_factor *= 1.0 - leech_drain
        effect_key = _LEECH_SELF_EFFECTS.get(prayer_id)
        if effect_key:
            prayer_effects[effect_key] = max(float(prayer_effects.get(effect_key, 1.0)), self_effect)
    return enemy_attack_factor, enemy_defence_factor


def _combat_turmoil_boosts(data, enemy, prayer_uptime, prayer_effects):
    """Raise the attack, defence and strength effects to Turmoil's boost over
    the player's base level, which adds a share of the enemy's same level."""
    enemy_stats = enemy.get("stats", {}) or {}
    for key, base_bonus, enemy_bonus in (
        ("attack", .15, .15),
        ("defence", .15, .15),
        ("strength", .23, .10),
    ):
        player_base = max(1, _combat_base_skill_level(data, "defense" if key == "defence" else key, 1))
        enemy_level = _positive_int(enemy_stats.get(key, 1), 1)
        turmoil_level = player_base * (1.0 + base_bonus * prayer_uptime) + enemy_bonus * enemy_level * prayer_uptime
        prayer_effects[key] = max(float(prayer_effects.get(key, 1.0)), turmoil_level / player_base)
