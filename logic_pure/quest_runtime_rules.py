"""Quest-specific runtime rules backed by period source evidence."""

from typing import Iterable, Mapping

from .logic_pure_state import (
    _non_negative_int,
    quest_completed_pure,
    quest_state_pure,
)


_COUNT_DRAYNOR_GARLIC_ENCOUNTER = (
    "vampyre_slayer",
    "vampyre_slayer_count_draynor_37",
)


def quest_combat_inventory_adjusted_stats_pure(
    quest_id, encounter_id, stats, player_data
):
    if (quest_id, encounter_id) != _COUNT_DRAYNOR_GARLIC_ENCOUNTER:
        return stats
    inventory = player_data.get("inventory", {}) if isinstance(player_data, Mapping) else {}
    if not isinstance(inventory, Mapping) or _non_negative_int(inventory.get("Garlic", 0), 0) <= 0:
        return stats
    # Quest items use the flat owned-supply store. Target-local carried views are
    # overlays on that store, and Count Draynor has no configurable target pack.
    adjusted = dict(stats)
    adjusted["strength"] = max(1, adjusted["strength"] - 5)
    adjusted["defence"] = max(1, adjusted["defence"] - 5)
    return adjusted


def ability_unlocked_pure(player_data, ability_id):
    abilities = player_data.get("unlocked_abilities", ())
    if isinstance(abilities, str):
        return abilities == ability_id
    if isinstance(abilities, Iterable):
        return ability_id in {ability for ability in abilities if isinstance(ability, str)}
    return False


def _target_ids_for_unlock_rule(rule):
    target_ids = rule.get("target_ids", ())
    if isinstance(target_ids, str):
        return (target_ids,)
    if isinstance(target_ids, Iterable):
        return tuple(item for item in target_ids if isinstance(item, str))
    return tuple()


def _requirements_for_unlock_rule(rule):
    requirements = rule.get("requirements")
    if isinstance(requirements, Mapping):
        return (requirements,)
    if isinstance(requirements, Iterable) and not isinstance(requirements, str):
        return tuple(requirement for requirement in requirements if isinstance(requirement, Mapping))
    quest_id = rule.get("quest_id")
    if isinstance(quest_id, str):
        return (
            {
                "kind": "quest_completed",
                "quest_id": quest_id,
                "reason": rule.get("reason") or quest_id.replace("_", " ").title(),
                "source": rule.get("source", ""),
            },
        )
    return tuple()


_TARGET_UNLOCK_RULE_INDEX_CACHE = {}


def _normalized_target_unlock_rule_index(target_unlock_rules):
    rules = target_unlock_rules or ()
    if not isinstance(rules, tuple):
        return _build_normalized_target_unlock_rule_index(rules)
    cache_key = id(rules)
    cached = _TARGET_UNLOCK_RULE_INDEX_CACHE.get(cache_key)
    if cached is not None and cached[0] is rules:
        return cached[1]
    index = _build_normalized_target_unlock_rule_index(rules)
    _TARGET_UNLOCK_RULE_INDEX_CACHE[cache_key] = (rules, index)
    return index


def _build_normalized_target_unlock_rule_index(target_unlock_rules):
    index = {}
    for rule in target_unlock_rules or ():
        if not isinstance(rule, Mapping) or rule.get("gate_kind", "target") != "target":
            continue
        skill_id = rule.get("skill_id")
        if not isinstance(skill_id, str):
            continue
        requirements = tuple(
            (
                str(requirement.get("kind", "quest_completed")),
                requirement.get("quest_id"),
                requirement.get("ability_id"),
                _non_negative_int(requirement.get("stage", 0), 0),
                requirement.get("reason"),
            )
            for requirement in _requirements_for_unlock_rule(rule)
        )
        for target_id in _target_ids_for_unlock_rule(rule):
            index.setdefault((skill_id, target_id), []).extend(requirements)
    return {key: tuple(requirements) for key, requirements in index.items()}


def _target_unlock_requirement_satisfied_pure(
    player_data, kind, quest_id, ability_id, stage
):
    valid_quest_id = isinstance(quest_id, str)
    state = quest_state_pure(player_data, quest_id) if valid_quest_id else {}
    satisfied_by_kind = {
        "quest_completed": not valid_quest_id or quest_completed_pure(player_data, quest_id),
        "quest_started": state.get("started") or state.get("completed"),
        "quest_stage": state.get("completed")
        or (state.get("started") and state.get("progress", 0) >= max(stage, 1)),
        "ability_unlocked": not isinstance(ability_id, str)
        or ability_unlocked_pure(player_data, ability_id),
    }
    return bool(satisfied_by_kind.get(kind, True))


def target_unlock_locked_reasons_pure(player_data, skill_id, target_id, target_unlock_rules):
    reasons = []
    requirements = _normalized_target_unlock_rule_index(target_unlock_rules).get(
        (skill_id, target_id), ()
    )
    for kind, quest_id, ability_id, stage, reason in requirements:
        if _target_unlock_requirement_satisfied_pure(
            player_data, kind, quest_id, ability_id, stage
        ):
            continue
        requirement_id = ability_id if kind == "ability_unlocked" else quest_id
        reasons.append(str(reason or str(requirement_id).replace("_", " ").title()))
    return tuple(dict.fromkeys(reasons))


def quest_unlock_locked_reasons_pure(player_data, skill_id, target_id, quest_unlock_rules):
    return target_unlock_locked_reasons_pure(player_data, skill_id, target_id, quest_unlock_rules)
