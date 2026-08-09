"""Review-driven temporary levels and target-local skilling potion policy."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


SKILLING_STAT_RESTORE_TICKS = 100
SKILLING_POTION_BOOST = 3
SKILLING_POTION_SKILLS = frozenset({"crafting", "fletching"})


def default_skilling_boost_state_pure() -> dict[str, Any]:
    return {
        "skilling_current_levels": {},
        "skilling_level_decay_ticks": 0,
        "skilling_potion_targets": {},
    }


def _base_level(player_data: Mapping[str, Any], skill_id: str) -> int:
    try:
        return max(1, int(player_data.get(f"{skill_id}_level", 1) or 1))
    except (TypeError, ValueError):
        return 1


def sanitize_skilling_boost_state_pure(
    player_data: Mapping[str, Any],
) -> dict[str, Any]:
    raw_levels = player_data.get("skilling_current_levels", {})
    levels: dict[str, int] = {}
    if isinstance(raw_levels, Mapping):
        for raw_skill, raw_level in raw_levels.items():
            skill_id = str(raw_skill)
            if f"{skill_id}_level" not in player_data:
                continue
            try:
                current = max(1, min(120, int(raw_level)))
            except (TypeError, ValueError):
                continue
            if current != _base_level(player_data, skill_id):
                levels[skill_id] = current

    raw_targets = player_data.get("skilling_potion_targets", {})
    targets: dict[str, dict[str, bool]] = {}
    if isinstance(raw_targets, Mapping):
        for raw_skill, raw_skill_targets in raw_targets.items():
            skill_id = str(raw_skill)
            if skill_id not in SKILLING_POTION_SKILLS or not isinstance(
                raw_skill_targets, Mapping
            ):
                continue
            enabled = {
                str(target_id): True
                for target_id, value in raw_skill_targets.items()
                if isinstance(target_id, str) and bool(value)
            }
            if enabled:
                targets[skill_id] = enabled

    try:
        decay_ticks = max(
            0,
            min(
                SKILLING_STAT_RESTORE_TICKS - 1,
                int(player_data.get("skilling_level_decay_ticks", 0) or 0),
            ),
        )
    except (TypeError, ValueError):
        decay_ticks = 0
    if not levels:
        decay_ticks = 0

    return {
        "skilling_current_levels": levels,
        "skilling_level_decay_ticks": decay_ticks,
        "skilling_potion_targets": targets,
    }


def skilling_effective_level_pure(
    player_data: Mapping[str, Any], skill_id: str
) -> int:
    base = _base_level(player_data, skill_id)
    raw_levels = player_data.get("skilling_current_levels", {})
    if not isinstance(raw_levels, Mapping):
        return base
    try:
        return max(1, int(raw_levels.get(skill_id, base) or base))
    except (TypeError, ValueError):
        return base


def skilling_potion_target_enabled_pure(
    player_data: Mapping[str, Any], skill_id: str, target_id: str
) -> bool:
    policies = player_data.get("skilling_potion_targets", {})
    if not isinstance(policies, Mapping):
        return False
    skill_targets = policies.get(skill_id, {})
    return bool(
        isinstance(skill_targets, Mapping) and skill_targets.get(target_id, False)
    )


def skilling_potion_item_pure(
    inventory: Mapping[str, Any], skill_id: str
) -> str:
    from ..data.potion_data import skilling_potion_items_for_skill

    return next(
        (
            item_name
            for item_name in skilling_potion_items_for_skill(skill_id)
            if int(inventory.get(item_name, 0) or 0) > 0
        ),
        "",
    )


def skilling_target_level_available_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    target_id: str,
    required_level: int,
) -> bool:
    required = max(1, int(required_level))
    if skilling_effective_level_pure(player_data, skill_id) >= required:
        return True
    base = _base_level(player_data, skill_id)
    if (
        required > base + SKILLING_POTION_BOOST
        or not skilling_potion_target_enabled_pure(
            player_data, skill_id, target_id
        )
    ):
        return False
    inventory = player_data.get("inventory", {})
    if not isinstance(inventory, Mapping):
        return False
    advanced_targets = player_data.get("carried_advanced_targets", {})
    if isinstance(advanced_targets, Mapping) and advanced_targets.get(target_id):
        layouts = player_data.get("carried_layout", {})
        layout = layouts.get(target_id, {}) if isinstance(layouts, Mapping) else {}
        if not isinstance(layout, Mapping):
            return False
        allowed_inventory = {
            item_name: inventory.get(item_name, 0)
            for item_name in layout
            if isinstance(item_name, str)
            if int(layout.get(item_name, 0) or 0) > 0
        }
        return bool(skilling_potion_item_pure(allowed_inventory, skill_id))
    return bool(skilling_potion_item_pure(inventory, skill_id))


def set_skilling_potion_target_enabled_pure(
    player_data: Mapping[str, Any],
    skill_id: str,
    target_id: str,
    enabled: bool,
) -> tuple[dict[str, Any], bool]:
    if skill_id not in SKILLING_POTION_SKILLS or not target_id:
        return dict(player_data), False
    data = dict(player_data)
    raw_policies = player_data.get("skilling_potion_targets", {})
    if not isinstance(raw_policies, Mapping):
        raw_policies = {}
    policies = {
        str(key): dict(value)
        for key, value in raw_policies.items()
        if isinstance(key, str) and isinstance(value, Mapping)
    }
    skill_targets = dict(policies.get(skill_id, {}))
    if enabled:
        skill_targets[target_id] = True
    else:
        skill_targets.pop(target_id, None)
    if skill_targets:
        policies[skill_id] = skill_targets
    else:
        policies.pop(skill_id, None)
    data["skilling_potion_targets"] = policies
    return data, True


def apply_skilling_stat_boost_pure(
    player_data: Mapping[str, Any], skill_id: str, boost: int
) -> dict[str, Any]:
    data = dict(player_data)
    levels = dict(data.get("skilling_current_levels", {}) or {})
    base = _base_level(data, skill_id)
    current = skilling_effective_level_pure(data, skill_id)
    levels[skill_id] = max(current, base + max(0, int(boost)))
    data["skilling_current_levels"] = levels
    data.setdefault("skilling_level_decay_ticks", 0)
    return data


def advance_skilling_temporary_levels_pure(
    player_data: Mapping[str, Any], elapsed_ticks: int
) -> dict[str, Any]:
    data = dict(player_data)
    state = sanitize_skilling_boost_state_pure(data)
    levels = dict(state["skilling_current_levels"])
    if not levels:
        data.update(state)
        return data

    total_ticks = state["skilling_level_decay_ticks"] + max(
        0, int(elapsed_ticks)
    )
    restore_steps, residual = divmod(total_ticks, SKILLING_STAT_RESTORE_TICKS)
    if restore_steps:
        for skill_id, current in tuple(levels.items()):
            base = _base_level(data, skill_id)
            if current > base:
                current = max(base, current - restore_steps)
            elif current < base:
                current = min(base, current + restore_steps)
            if current == base:
                levels.pop(skill_id, None)
            else:
                levels[skill_id] = current
    data["skilling_current_levels"] = levels
    data["skilling_level_decay_ticks"] = residual if levels else 0
    data["skilling_potion_targets"] = state["skilling_potion_targets"]
    return data
