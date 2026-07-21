"""Pinned Werewolf Skullball route data and AnkiScape translation."""

from __future__ import annotations

from typing import Any, Dict


WEREWOLF_SKULLBALL_ACTIVITY_ID = "werewolf_skullball"
WEREWOLF_SKULLBALL_SOURCE = (
    "RuneScape Wiki Werewolf Skullball oldid=6488093 "
    "(2012-10-28T12:40:39Z)"
)
WEREWOLF_SKULLBALL_RING_SOURCE = (
    "RuneScape Wiki Ring of charos oldid=6359534 "
    "(2012-10-06T21:47:17Z); OpenRS2 caches 727 and 742"
)

WEREWOLF_SKULLBALL_RING_ITEMS = (
    "Ring of Charos",
    "Ring of charos (a)",
    "Ring of charos (a)(i)",
)

WEREWOLF_SKULLBALL_MOVES = {
    "T": {"label": "Tap", "squares": 1},
    "K": {"label": "Kick", "squares": 4},
    "S": {"label": "Shoot", "squares": 9},
}

# The focused cutoff page supplies one complete recommended route and two
# explicit substitutions. These presets keep those real move sequences rather
# than simulating the arena grid. Every listed route remains under four source
# minutes and therefore earns the sourced 750 XP maximum.
WEREWOLF_SKULLBALL_ROUTE_PRESETS = {
    "careful": {
        "label": "Careful",
        "plan": "S K T K T T S T S K T K T T S K S T S S T S S T T T T T S S",
        "character": "measured kick-and-tap finish",
        "notable": "uses the slower kick-and-tap fifth-goal line",
    },
    "balanced": {
        "label": "Balanced",
        "plan": "S K T K T T S T S S K T T S K S T S S T S S T T T T T S S",
        "character": "recommended mixed route",
        "notable": "follows the cutoff recommended route",
    },
    "fast": {
        "label": "Fast",
        "plan": "S K T K T T S T S S K T T S K S T S S T S S S T T S S",
        "character": "long-shot wall-bounce route",
        "notable": "uses the sourced tenth-goal wall bounce",
    },
}

WEREWOLF_SKULLBALL_DEFAULT_ROUTE = "balanced"
WEREWOLF_SKULLBALL_MAX_XP = 750
WEREWOLF_SKULLBALL_FULL_XP_MOVE_BUDGET = 30
WEREWOLF_SKULLBALL_DECAY_PER_EXCESS_MOVE = 8


def werewolf_skullball_activity_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        WEREWOLF_SKULLBALL_ACTIVITY_ID: {
            "display_name": "Werewolf Skullball",
            "requirements": {},
            "skill_requirements": {"agility": 25},
            "batch_size": 1,
            "group": "minigames",
            "source": WEREWOLF_SKULLBALL_SOURCE,
        }
    }


def werewolf_skullball_extra_items_as_dict() -> Dict[str, Dict[str, Any]]:
    return {
        "Ring of Charos": {
            "category": "equipment",
            "source_item_id": 4202,
            "stackable": False,
            "tradeable": False,
            "source": WEREWOLF_SKULLBALL_RING_SOURCE,
        },
        "Ring of charos (a)": {
            "category": "equipment",
            "source_item_id": 6465,
            "stackable": False,
            "tradeable": False,
            "source": WEREWOLF_SKULLBALL_RING_SOURCE,
        },
        "Ring of charos (a)(i)": {
            "category": "equipment",
            "source_item_id": 15016,
            "stackable": False,
            "tradeable": False,
            "source": WEREWOLF_SKULLBALL_RING_SOURCE,
        },
    }
