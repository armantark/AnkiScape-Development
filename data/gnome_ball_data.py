"""Pinned Gnome Ball match, reward, and item data."""

from __future__ import annotations

from typing import Any, Dict


GNOME_BALL_ACTIVITY_ID = "gnome_ball"
GNOME_BALL_SOURCE = (
    "RuneScape Wiki Gnome Ball oldid=6404371 "
    "(2012-10-14T14:19:59Z)"
)
GNOMEBALL_ITEM_SOURCE = (
    "RuneScape Wiki Gnomeball oldid=6151390 "
    "(2012-08-27T00:52:25Z); OpenRS2 rev 742 item 751"
)

GNOME_BALL_GOAL_XP = (4.0, 5.0, 6.0, 7.0, 5.0)
GNOME_BALL_COMPLETION_BONUS_XP = 25.0
GNOME_BALL_BEATS = (
    {"label": "Opening", "goals": (1, 2)},
    {"label": "Middle", "goals": (3, 4)},
    {"label": "Final", "goals": (5,)},
)

# The exact tackle roll remains source_blocked. The owner-approved Agility
# fallback starts at 20% and approaches a 5% residual across levels 1–99.
GNOME_BALL_TACKLE_ENTRY_CHANCE = 0.20
GNOME_BALL_TACKLE_RESIDUAL_CHANCE = 0.05


def gnome_ball_activity_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        GNOME_BALL_ACTIVITY_ID: {
            "display_name": "Gnome Ball",
            "requirements": {},
            "skill_requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "source": GNOME_BALL_SOURCE,
        }
    }


def gnome_ball_extra_items_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        "Gnomeball": {
            "category": "equipment",
            "source_item_id": 751,
            "stackable": False,
            "tradeable": True,
            "source": GNOMEBALL_ITEM_SOURCE,
        }
    }
