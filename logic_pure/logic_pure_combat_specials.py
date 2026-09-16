"""Enemy special-attack damage and event payloads."""

from typing import Mapping

from .logic_pure_combat_model import (
    COMBAT_POISON_NPC_ATTACK_CHANCE,
    _combat_cap_damage_for_finisher,
    _combat_unprotected_damage_lifepoints,
)
from .logic_pure_combat_supplies import (
    _combat_apply_poison_effect_to_data,
    _combat_consume_antipoison_if_needed,
    combat_dragonfire_protection_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
)
from .logic_pure_state import _non_negative_int, _positive_int


def _combat_death_prayer_damage(data, selected_prayers, finisher, enemy_lp, rng):
    cap_multiplier = 2.5 if "wrath" in selected_prayers else .25
    # Death prayers include 1.0; special-attack damage rolls exclude it.
    try:
        death_roll = max(0.0, min(1.0, float(rng())))
    except (TypeError, ValueError):
        death_roll = 0.0
    death_burst, automatic_finisher = _combat_cap_damage_for_finisher(
        data,
        finisher,
        enemy_lp,
        int(
            _positive_int(data.get("prayer_level", 1), 1)
            * cap_multiplier
            * death_roll
        ),
        allow_automatic=False,
    )
    return death_burst, automatic_finisher


def _combat_enemy_poison_application(data, poison_damage, rng, status_applied):
    if poison_damage > 0:
        try:
            poison_roll = float(rng())
        except (TypeError, ValueError):
            poison_roll = 1.0
        if poison_roll < COMBAT_POISON_NPC_ATTACK_CHANCE:
            applied, _reason = _combat_apply_poison_effect_to_data(data, poison_damage)
            if applied:
                status_applied["poison"] = combat_poison_damage_for_ticks_pure(
                    combat_poison_ticks_for_initial_damage_pure(poison_damage)
                )
                return _combat_consume_antipoison_if_needed(data)
    return None


def _combat_enemy_prayer_drain(enemy, raw_enemy_damage, prayer_points_after):
    prayer_drain_base = _non_negative_int(enemy.get("prayer_drain_base", 0), 0)
    if prayer_drain_base <= 0:
        return None
    prayer_drain = prayer_drain_base
    if bool(enemy.get("prayer_drain_damage", False)):
        prayer_drain += max(0, raw_enemy_damage)
    return min(prayer_points_after, prayer_drain)


def _combat_wyvern_breath_damage_event(
    data, breath_spec, protective_equipment, protection_active, max_player_lp, rng,
):
    equipped_shield = str((data.get("equipment", {}) or {}).get("shield", ""))
    if protection_active:
        breath_max_hit = _non_negative_int(
            breath_spec.get("shielded_max_hit", 0), 0
        )
        try:
            breath_roll = max(0.0, min(float(rng()), 0.999999999999))
        except (TypeError, ValueError):
            breath_roll = 0.0
        damage = int(breath_roll * (breath_max_hit + 1))
    else:
        breath_effect = (
            protective_equipment.get("unprotected_effect")
            if isinstance(protective_equipment, Mapping)
            else None
        )
        damage = _combat_unprotected_damage_lifepoints(
            breath_effect, max_player_lp, rng
        )
        breath_max_hit = _non_negative_int(
            ((breath_effect or {}).get("damage") or {}).get("max", 0), 0,
        )
    delay = _non_negative_int(breath_spec.get("player_delay_ticks", 0), 0)
    return damage, {
        "kind": "wyvern_breath",
        "protected": bool(protection_active),
        "shield_item": equipped_shield,
        "max_hit": breath_max_hit,
        "delay_ticks": delay,
    }


def _combat_dragonfire_damage_lifepoints(
    data, enemy, magic_prayer_active, rng,
):
    dragonfire_state = combat_dragonfire_protection_pure(
        data,
        enemy,
        magic_prayer_active=magic_prayer_active,
    )
    dragonfire_max_hit = _non_negative_int(
        dragonfire_state.get("max_hit", 0), 0
    )
    try:
        dragonfire_roll = max(
            0.0, min(float(rng()), 0.999999999999)
        )
    except (TypeError, ValueError):
        dragonfire_roll = 0.0
    return int(dragonfire_roll * (dragonfire_max_hit + 1))
