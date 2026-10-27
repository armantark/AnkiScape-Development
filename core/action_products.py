"""The product of an action: the item its queue entry counts and its XP popup shows.

A review's item changes list everything it moved, loot, drunk potions and
emptied vials included. The product is the item the player picked the action
for, read from the action's target data, so "+1 Vial" from a potion or a
fight's loot never reaches the popup or a queue count.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .constants import UTILITY_ACTIVITY_DATA
from .skill_registry import get_skill
from ..logic.cadence_coverage import FOREGROUND_ROUTE_TABLES


def _field(spec: Any, name: str) -> Any:
    return spec.get(name) if isinstance(spec, Mapping) else getattr(spec, name, None)


def action_target_spec_pure(action: Mapping[str, Any]) -> Any:
    """The data row of a skill or combat action's target; None for other kinds."""
    if action.get("kind") == "combat":
        return FOREGROUND_ROUTE_TABLES["combat"].get(action.get("target"))
    skill = get_skill(str(action.get("skill") or "")) if action.get("kind") == "skill" else None
    if skill is None:
        return None
    return FOREGROUND_ROUTE_TABLES.get(skill.review_handler_key or "", {}).get(action.get("target"))


def action_product_items_pure(action: Mapping[str, Any]) -> tuple[str, ...]:
    """The items an action makes; empty for fights, quests and actions that make none."""
    if action.get("kind") == "utility":
        # A minigame's ``outputs`` lists its reward shop, not what one review makes.
        spec = UTILITY_ACTIVITY_DATA.get(action.get("utility_id"), {})
        return _item_names((spec.get("output_item"),))
    spec = action_target_spec_pure(action) if action.get("kind") == "skill" else None
    if spec is None:
        return ()
    names = [_field(spec, "output_item")]
    if _field(spec, "alternate_output_level"):
        # Mining's level-gated second product: Rune essence becomes Pure essence.
        names.append(_field(spec, "alternate_output_item"))
    names += [_field(row, "item") for row in _field(spec, "weighted_outputs") or ()]
    names += [_field(fish, "output_item") for fish in _field(spec, "fish") or ()]
    if not any(names):
        names += list(_field(spec, "outputs") or ())
    return _item_names(names)


def action_used_input_pure(action: Mapping[str, Any]) -> str:
    """The one item an action that makes nothing uses up, such as Bones for burying; empty otherwise.

    The player plans such an action by that item ("bury 100 bones"), so its
    queue entry counts it instead of reviews.
    """
    if action.get("kind") == "utility":
        spec = UTILITY_ACTIVITY_DATA.get(action.get("utility_id"), {})
    elif action.get("kind") == "skill":
        spec = action_target_spec_pure(action)
    else:
        return ""
    needs = tuple(_field(spec, "requirements") or ()) if spec else ()
    return needs[0] if len(needs) == 1 and not action_product_items_pure(action) else ""


def product_gains_pure(action: Mapping[str, Any], changes: Mapping[str, int]) -> dict[str, int]:
    """The review's gains of the action's product items, from its item changes."""
    products = action_product_items_pure(action)
    return {item: count for item, count in changes.items() if item in products and count > 0}


def _item_names(values: Iterable[Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(value for value in values if isinstance(value, str) and value))
