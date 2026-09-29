"""What a combat target threatens, and the risk band its preview shows."""

from typing import Mapping

from ..data.combat_data import COMBAT_ENEMY_DATA
from .logic_pure_combat_food import _combat_preview_food_available
from .logic_pure_combat_model import (
    COMBAT_POISON_NPC_ATTACK_CHANCE,
    _combat_banked_hazard_count,
    _combat_enemy_max_hit_old_hp,
    _combat_environmental_hazard_spec,
    _combat_loaded_hazard_count,
    _combat_protective_equipment_state,
    _combat_unprotected_damage_lifepoints,
    _combat_weakening_equipment_state,
    combat_enemy_current_lifepoints_pure,
    combat_finisher_state_pure,
    combat_max_lifepoints_pure,
    combat_target_locked_reasons_pure,
    combat_wilderness_equipment_risk_pure,
)
from .logic_pure_combat_supplies import (
    combat_dragonfire_protection_pure,
    combat_poison_damage_for_ticks_pure,
    combat_poison_immunity_ticks_pure,
    combat_poison_ticks_for_initial_damage_pure,
)
from .logic_pure_equipment import _equipment_bonus_value
from .logic_pure_state import _non_negative_int, _positive_int


def _combat_preview_target_context(player_data, target_id, enemy_data, equipment_data):
    enemy_data = enemy_data or COMBAT_ENEMY_DATA
    enemy = enemy_data.get(target_id)
    if enemy is None:
        return enemy_data, enemy, equipment_data, ("unknown enemy",)
    equipment_data = equipment_data or {}
    reasons = combat_target_locked_reasons_pure(
        player_data, target_id, enemy_data, equipment_data=equipment_data
    )
    return enemy_data, enemy, equipment_data, reasons


def _combat_preview_incoming_damage(player_data, enemy, enemy_totals, combat_class):
    """The enemy's largest hit after the player's weakening, protective and
    dragonfire gear, against the player's lifepoints."""
    enemy_max_hit = _combat_enemy_max_hit_old_hp(
        enemy,
        _positive_int(enemy.get("stats", {}).get("strength", 1), 1) + 8,
        _equipment_bonus_value(enemy_totals, "melee_strength"),
        enemy_totals,
    )
    weakening_equipment, weakening_active = _combat_weakening_equipment_state(
        player_data, enemy
    )
    if weakening_active:
        enemy_max_hit *= max(
            0.0,
            float(weakening_equipment.get("enemy_damage_multiplier", 1.0)),
        )
    protective_equipment, protection_active = _combat_protective_equipment_state(
        player_data, enemy, combat_class
    )
    unprotected_effect = (
        protective_equipment.get("unprotected_effect")
        if isinstance(protective_equipment, Mapping) and not protection_active
        else None
    )
    max_lp = combat_max_lifepoints_pure(player_data)
    current_lp = max(0, min(_positive_int(player_data.get("combat_lifepoints", max_lp), max_lp), max_lp))
    enemy_max_lp_hit = (
        _combat_unprotected_damage_lifepoints(unprotected_effect, max_lp)
        + (
            int(enemy_max_hit * 10)
            if isinstance(unprotected_effect, Mapping)
            and bool(unprotected_effect.get("additive_to_attack"))
            else 0
        )
        if isinstance(unprotected_effect, Mapping)
        else int(enemy_max_hit * 10)
    )
    dragonfire_state = combat_dragonfire_protection_pure(player_data, enemy)
    if dragonfire_state:
        dragonfire_spec = enemy.get("dragonfire", {})
        dragonfire_state = {
            **dragonfire_state,
            "chance_numerator": _positive_int(
                dragonfire_spec.get("chance_numerator", 1), 1
            ),
            "chance_denominator": _positive_int(
                dragonfire_spec.get("chance_denominator", 1), 1
            ),
        }
        enemy_max_lp_hit = max(
            enemy_max_lp_hit,
            _non_negative_int(dragonfire_state.get("max_hit", 0), 0),
        )
    return {
        "enemy_max_hit": enemy_max_lp_hit,
        "player_lifepoints": current_lp,
        "player_max_lifepoints": max_lp,
        "protection_warning": (
            str(protective_equipment.get("warning", ""))
            if isinstance(protective_equipment, Mapping) and not protection_active
            else ""
        ),
        "weakening_equipment": {
            "display_name": str(
                weakening_equipment.get("display_name", "Weakening equipment")
            ),
            "active": weakening_active,
            "enemy_accuracy_multiplier": float(
                weakening_equipment.get("enemy_accuracy_multiplier", 1.0)
            ),
            "enemy_damage_multiplier": float(
                weakening_equipment.get("enemy_damage_multiplier", 1.0)
            ),
        }
        if isinstance(weakening_equipment, Mapping)
        else {},
        "dragonfire": dragonfire_state,
    }


def _combat_preview_wilderness_risk(player_data, enemy):
    wilderness_spec = enemy.get("wilderness_risk")
    if not isinstance(wilderness_spec, Mapping):
        return {}
    return {
        **combat_wilderness_equipment_risk_pure(player_data, enemy),
        "ambush_chance": max(
            0.0,
            min(
                1.0,
                float(wilderness_spec.get("ambush_chance", 0.0) or 0.0),
            ),
        ),
        "max_hit": _positive_int(wilderness_spec.get("max_hit", 1), 1),
        "source_status": str(
            wilderness_spec.get("source_status", "") or ""
        ),
    }


def _combat_preview_environmental_hazard(player_data, enemy):
    hazard = _combat_environmental_hazard_spec(enemy)
    if hazard is None:
        return {}
    return {
        "display_name": str(
            hazard.get("display_name", "Environmental hazard")
        ),
        "loaded": _combat_loaded_hazard_count(player_data, hazard),
        "banked": _combat_banked_hazard_count(player_data, hazard),
        "reviews_per_dose": _positive_int(
            hazard.get("reviews_per_dose", 1), 1
        ),
        "source_status": str(hazard.get("source_status", "") or ""),
    }


def _combat_preview_with_risk(
    player_data,
    target_id,
    enemy,
    enemy_data,
    enemy_totals,
    combat_class,
    accuracy,
    attack,
):
    """Complete an unblocked target preview from the player's attack
    projection: the enemy's threat, the risk band and the encounter state."""
    incoming = _combat_preview_incoming_damage(
        player_data, enemy, enemy_totals, combat_class
    )
    encounter = player_data.get("combat_encounter", {}) or {}
    active_encounter = isinstance(encounter, Mapping) and encounter.get("target_id") == target_id
    has_food = _combat_preview_food_available(player_data, active_encounter)
    enemy_max_lp_hit = incoming["enemy_max_hit"]
    if enemy_max_lp_hit <= 0 or incoming["player_lifepoints"] > enemy_max_lp_hit * 3:
        risk = "Safe"
    elif has_food:
        risk = "Food advised"
    else:
        risk = "Death possible"
    wilderness_risk = _combat_preview_wilderness_risk(player_data, enemy)
    if wilderness_risk:
        risk = "Wilderness risk"
    poison_damage = _positive_int(enemy.get("poison_damage", 0), 0)
    poison_immunity_ticks = combat_poison_immunity_ticks_pure(player_data)
    poisonable = poison_damage > 0 and poison_immunity_ticks <= 0
    poison_lifepoints = 0
    if poisonable:
        poison_lifepoints = combat_poison_damage_for_ticks_pure(
            combat_poison_ticks_for_initial_damage_pure(poison_damage)
        )
        if risk == "Safe":
            risk = "Food advised"
    state = (
        "Wilderness risk"
        if wilderness_risk
        else "Fighting"
        if active_encounter
        else "Ready"
    )
    return {
        "state": state,
        "risk_band": risk,
        "reasons": tuple(),
        "accuracy": accuracy,
        "enemy_max_hit": enemy_max_lp_hit,
        "player_lifepoints": incoming["player_lifepoints"],
        "player_max_lifepoints": incoming["player_max_lifepoints"],
        "enemy_lifepoints": combat_enemy_current_lifepoints_pure(player_data, target_id, enemy_data),
        "enemy_max_lifepoints": _positive_int(enemy.get("stats", {}).get("hitpoints", 0), 0),
        **attack,
        "poison_damage": poison_lifepoints,
        "poison_chance": COMBAT_POISON_NPC_ATTACK_CHANCE if poisonable else 0.0,
        "poison_immunity_ticks": poison_immunity_ticks,
        "protection_warning": incoming["protection_warning"],
        "weakening_equipment": incoming["weakening_equipment"],
        "finisher": combat_finisher_state_pure(
            player_data, target_id, enemy_data
        ),
        "environmental_hazard": _combat_preview_environmental_hazard(
            player_data, enemy
        ),
        "dragonfire": incoming["dragonfire"],
        "wilderness_risk": wilderness_risk,
        "source": enemy.get("source", ""),
    }
