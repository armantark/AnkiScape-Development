"""Shadow foreground upkeep before the carried overlay replaces Bank inventory."""

from ..core.constants import HUNTER_DATA, QUEST_UNLOCK_RULES
from ..data.habitat import SHADOW_TARGET
from ..logic.farming_logic import apply_shadow_setup_step_pure
from ..logic_pure.logic_pure_gathering import (
    has_hunter_materials_pure, has_hunter_tools_pure,
)
from ..logic_pure.logic_pure import quest_unlock_locked_reasons_pure
from .runtime_actions_context import stop_card
from .runtime_actions_shared import _apply_farming_queue_result, _farming_levels_before_answer


def run_shadow_upkeep(ctx, handler_key):
    """None proceeds to hunting; True consumes this existing handler step."""
    data = ctx.player_data
    if handler_key != "hunter" or data.get("current_hunter") != SHADOW_TARGET:
        return None
    spec = HUNTER_DATA[SHADOW_TARGET]
    inventory = data.get("inventory", {})
    if (data.get("hunter_level", 1) < spec["level"]
            or not has_hunter_tools_pure(SHADOW_TARGET, inventory, HUNTER_DATA)
            or not has_hunter_materials_pure(SHADOW_TARGET, inventory, HUNTER_DATA)
            or quest_unlock_locked_reasons_pure(data, "hunter", SHADOW_TARGET, QUEST_UNLOCK_RULES)):
        stop_card(ctx, "habitat_blocked")
        ctx.show_activity_gain("Shadow hunting requires Hunter 71, its tools and quest access.")
        return True
    old_levels = _farming_levels_before_answer(ctx)
    updated, info = apply_shadow_setup_step_pure(data, ctx.random_random)
    if info["status"] == "field":
        field = info["field_result"]
        _apply_farming_queue_result(ctx, old_levels, updated, True, field)
        ctx.show_activity_gain(field["message"])
        return True
    if info["status"] == "ready":
        data.clear()
        data.update(updated)
        return None
    stop_card(ctx, "habitat_" + info["status"])
    ctx.show_activity_gain(info["reason"])
    return True
