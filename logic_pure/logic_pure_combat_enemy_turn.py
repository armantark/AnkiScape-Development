"""The enemy's attack inside a combat burst tick: whether a dragon breathes
fire, what a special the player is not protected from costs, how prayers cut
the hit, what a vampyre bite takes back, and when Redemption saves the player.
The attack selection and the ordinary hit roll stay in the burst because tests
patch them on the engine module; Vengeance stays with the burst's Magic code."""

from typing import Mapping

from .logic_pure_combat_model import (
    _combat_apply_unprotected_stat_drains,
    _combat_enemy_protection_class,
    _combat_unprotected_damage_lifepoints,
)
from .logic_pure_combat_specials import _combat_enemy_prayer_drain
from .logic_pure_combat_supplies import (
    _combat_advance_dragonfire_effects,
    _combat_consume_dragonfire_if_needed,
)
from .logic_pure_state import _non_negative_int, _positive_int


def _combat_enemy_breathes_dragonfire(data, enemy, elapsed_ticks, rng, potions_used):
    """Bring dragonfire protection up to this attack, drink a carried potion if
    it ran out, and roll whether the enemy breathes fire."""
    _combat_advance_dragonfire_effects(data, elapsed_ticks)
    potion_event = _combat_consume_dragonfire_if_needed(data, enemy)
    if potion_event:
        potions_used.append(potion_event)
    dragonfire_spec = (
        enemy.get("dragonfire")
        if isinstance(enemy.get("dragonfire"), Mapping)
        else None
    )
    if dragonfire_spec is None:
        return False
    try:
        return float(rng()) < (
            _positive_int(dragonfire_spec.get("chance_numerator", 1), 1)
            / _positive_int(dragonfire_spec.get("chance_denominator", 1), 1)
        )
    except (TypeError, ValueError):
        return False


def _combat_unprotected_special_damage(
    data, unprotected_effect, prayer_effects, tick_prayer_uptime, max_player_lp, rng, stat_drains,
):
    """Damage from a special the player's missing protective equipment lets
    through, draining stats unless the named prayer is up. Returns the damage
    and whether a stat was drained."""
    damage = _combat_unprotected_damage_lifepoints(unprotected_effect, max_player_lp)
    stat_drain_prayer = unprotected_effect.get("stat_drain_protection_prayer")
    stat_drain_blocked = (
        isinstance(stat_drain_prayer, str)
        and tick_prayer_uptime > 0
        and float(prayer_effects.get(stat_drain_prayer, 0.0)) > 0.0
    )
    attack_drains = (
        {}
        if stat_drain_blocked
        else _combat_apply_unprotected_stat_drains(data, unprotected_effect, rng)
    )
    for skill_id, amount in attack_drains.items():
        stat_drains[skill_id] = _non_negative_int(stat_drains.get(skill_id, 0), 0) + amount
    return damage, bool(attack_drains)


def _combat_enemy_damage_after_prayers(
    data,
    enemy,
    attack_enemy,
    combat_class,
    raw_damage,
    ignores_protection,
    unprotected_effect,
    prayer_effects,
    prayer_scale,
    player_lp,
    max_player_lp,
    prayer_points,
    rng,
    enemy_counts,
):
    """Drain prayer by the raw hit, cut the hit by the matching protection
    prayer unless the attack ignores it, add a special that stacks on the
    attack, and cap the damage at the player's lifepoints. Returns the damage
    and the prayer points left."""
    prayer_drain = _combat_enemy_prayer_drain(enemy, raw_damage, prayer_points)
    if prayer_drain is not None:
        prayer_points -= prayer_drain
        enemy_counts["enemy_prayer_drain"] += prayer_drain
        data["combat_prayer_points"] = prayer_points
    damage = raw_damage
    if not ignores_protection and (
        not isinstance(unprotected_effect, Mapping)
        or bool(unprotected_effect.get("protection_prayer_applies"))
    ):
        protection_class = _combat_enemy_protection_class(attack_enemy, combat_class)
        protection_key = {
            "magic": "protect_magic",
            "ranged": "protect_ranged",
        }.get(protection_class, "protect_melee")
        damage = int(
            damage
            * (1.0 - float(prayer_effects.get(protection_key, 0.0)) * prayer_scale)
        )
    if (
        isinstance(unprotected_effect, Mapping)
        and bool(unprotected_effect.get("additive_to_attack"))
    ):
        damage += _combat_unprotected_damage_lifepoints(
            unprotected_effect, max_player_lp, rng
        )
        enemy_counts["unprotected_attacks"] += 1
    return min(player_lp, damage), prayer_points


def _combat_apply_vampyre_bite(
    data, bite_spec, damage, enemy_lp, enemy_max_lp, rng, enemy_counts, stat_drains,
):
    """Roll a vampyre's bite after its hit lands: it drains one of its listed
    stats and heals the vampyre by up to the damage dealt. Returns the
    vampyre's lifepoints."""
    bite_numerator = _positive_int(bite_spec.get("chance_numerator", 1), 1)
    bite_denominator = _positive_int(bite_spec.get("chance_denominator", 1), 1)
    try:
        bite_triggered = float(rng()) < bite_numerator / bite_denominator
    except (TypeError, ValueError):
        bite_triggered = False
    if not bite_triggered:
        return enemy_lp
    enemy_counts["vampyre_bites"] += 1
    bite_skills = tuple(
        skill_id
        for skill_id in (bite_spec.get("stat_drain_skills", ()) or ())
        if isinstance(skill_id, str)
    )
    if bite_skills:
        try:
            skill_roll = max(0.0, min(float(rng()), 0.999999999999))
        except (TypeError, ValueError):
            skill_roll = 0.0
        drained_skill = bite_skills[int(skill_roll * len(bite_skills))]
        bite_drains = _combat_apply_unprotected_stat_drains(
            data,
            {
                "stat_drain": {
                    "kind": "flat_to_floor",
                    "amount": _positive_int(bite_spec.get("stat_drain_amount", 1), 1),
                    "floor": _positive_int(bite_spec.get("stat_drain_floor", 1), 1),
                    "skills": (drained_skill,),
                },
            },
        )
        for skill_id, amount in bite_drains.items():
            stat_drains[skill_id] = _non_negative_int(stat_drains.get(skill_id, 0), 0) + amount
    bite_healing = min(
        max(0, damage),
        _positive_int(bite_spec.get("max_heal", 1), 1),
        max(0, enemy_max_lp - enemy_lp),
    )
    if bite_healing > 0:
        enemy_lp += bite_healing
        enemy_counts["enemy_healing"] += bite_healing
        enemy_counts["vampyre_bite_healing"] += bite_healing
    return enemy_lp


def _combat_apply_redemption(
    data, player_lp, max_player_lp, prayer_effects, tick_prayer_uptime,
    prayer_points, prayer_counter,
):
    """Let Redemption, while it is up this tick, save a player left below 10%
    lifepoints. Returns the lifepoints, prayer points and prayer drain counter."""
    if not (
        0 < player_lp < max_player_lp * .10
        and tick_prayer_uptime > 0
        and float(prayer_effects.get("redemption", 0.0)) > 0
    ):
        return player_lp, prayer_points, prayer_counter
    # RuneScape Wiki Redemption oldid=6292830: heal 250% of Prayer
    # level below 10% LP, then consume every remaining prayer point.
    player_lp = min(
        max_player_lp,
        player_lp
        + int(
            _positive_int(data.get("prayer_level", 1), 1)
            * 2.5
            * tick_prayer_uptime
        ),
    )
    data["combat_prayer_points"] = 0
    data["combat_prayer_drain_counter"] = 0.0
    data["combat_selected_prayers"] = []
    return player_lp, 0, 0.0
