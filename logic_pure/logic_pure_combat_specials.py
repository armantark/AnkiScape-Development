"""Enemy special-attack damage and event payloads."""

from typing import Mapping

from .logic_pure_combat_model import _combat_unprotected_damage_lifepoints
from .logic_pure_combat_supplies import combat_dragonfire_protection_pure
from .logic_pure_state import _non_negative_int


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
