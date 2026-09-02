from __future__ import annotations

from collections.abc import Mapping

from .runtime_actions_context import RuntimeActionContext


STRONGHOLD_UTILITY_KEY = "stronghold_of_security"


KNIGHT_WAVES_UTILITY_KEY = "knight_waves"


MAGE_ARENA_UTILITY_KEY = "mage_arena"


MAGE_ARENA_ATTUNE_PREFIX = "mage_arena_attune:"


def _activity_session_is_current(
    ctx: RuntimeActionContext,
    activity_id: str,
) -> bool:
    active = ctx.player_data.get("activity_session")
    return isinstance(active, Mapping) and str(active.get("active_id", "")) == activity_id


_activity_session_is_current.__module__ = f"{__package__}.runtime_actions_activities"
