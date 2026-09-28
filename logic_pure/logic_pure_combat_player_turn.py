"""The player's hit inside a combat burst tick once it is rolled: the burst's
damage multiplier, the finisher cap, melee recoil and Soul Split healing. The
landing and damage rolls stay in the engine because tests patch the damage
roller there; spell runes, spell effects and Magic XP stay with the burst's
Magic code."""

from .logic_pure_combat_model import _combat_cap_damage_for_finisher
from .logic_pure_state import _non_negative_int


def _combat_land_player_hit(
    data, enemy, finisher, combat_class, damage, damage_multiplier, enemy_lp, player_lp,
):
    """Scale a rolled hit by the burst's damage multiplier and cap it for the
    enemy's finisher. Returns the damage, whether a loaded finisher was spent,
    and the melee recoil the hit costs the player."""
    try:
        damage = int(damage * max(0.0, float(damage_multiplier)))
    except (TypeError, ValueError, OverflowError):
        pass
    damage, automatic_finisher = _combat_cap_damage_for_finisher(
        data, finisher, enemy_lp, damage
    )
    recoil = (
        min(player_lp, _non_negative_int(enemy.get("melee_recoil_damage", 0), 0))
        if damage > 0 and combat_class == "melee"
        else 0
    )
    return damage, automatic_finisher, recoil


def _combat_soul_split_heal(
    player_lp, max_player_lp, damage, prayer_effects, prayer_uptime, tick_prayer_uptime,
):
    """Heal the player by Soul Split's share of a hit, for the part of this
    tick the prayer was up."""
    uptime_share = tick_prayer_uptime / prayer_uptime if prayer_uptime > 0 else 0.0
    heal = int(damage * float(prayer_effects.get("soul_split", 0.0)) * uptime_share)
    return min(max_player_lp, player_lp + heal) if heal > 0 else player_lp
