"""Pure point-pool projection for the Equipment tab."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..logic_pure.logic_pure_combat_engine import combat_hud_state_pure
from ..logic_pure.logic_pure_combat_model import sanitize_combat_state_pure
from .summoning_logic import sanitize_summoning_state_pure


def equipment_points_view_pure(player_data: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    """Return the live player point pools shown above worn equipment."""

    combat = combat_hud_state_pure(player_data)
    combat_state = sanitize_combat_state_pure(player_data)
    prayer_maximum = max(1, int(player_data.get("prayer_level", 1) or 1))
    # Combat keeps tenths internally for drain cadence; the player-facing pool
    # uses the same whole-point scale as the Prayer level on the Stats surface.
    prayer_current = combat_state["combat_prayer_points"] // 10
    summoning_maximum = max(1, int(player_data.get("summoning_level", 1) or 1))
    summoning_state = sanitize_summoning_state_pure(
        player_data.get("summoning_state"),
        summoning_level=summoning_maximum,
    )
    return (
        {
            "id": "lifepoints",
            "label": "Life points",
            "current": combat["player_lifepoints"],
            "maximum": combat["player_max_lifepoints"],
        },
        {
            "id": "prayer",
            "label": "Prayer points",
            "current": prayer_current,
            "maximum": prayer_maximum,
        },
        {
            "id": "summoning",
            "label": "Summoning points",
            "current": summoning_state["summoning_points_current"],
            "maximum": summoning_maximum,
        },
    )
