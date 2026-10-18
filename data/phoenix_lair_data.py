"""Period-pinned Phoenix Lair activity and encounter data."""

from __future__ import annotations

from typing import Any


PHOENIX_LAIR_ACTIVITY_ID = "phoenix_lair"
PHOENIX_LAIR_GUARDIAN_TARGET_ID = "phoenix_lair_guardians"
PHOENIX_LAIR_PHOENIX_TARGET_ID = "phoenix_lair_phoenix"
PHOENIX_LAIR_GUARDIAN_COUNT = 5
PHOENIX_LAIR_EGG_CHANCE = 1.0 / 1000.0
PHOENIX_EGG_CONTEXT_ID = "phoenix_egg"

PHOENIX_QUILL_ITEM = "Phoenix quill"
PHOENIX_EGG_ITEM = "Phoenix egg"
CRACKED_PHOENIX_EGG_ITEM = "Cracked phoenix egg"

PHOENIX_LAIR_SOURCE = (
    "RuneScape Wiki Phoenix Lair oldid=6574295 (2012-11-18); "
    "Phoenix oldid=6588809 (2012-11-19); Darkan Phoenix lifecycle commit 7907f0b5f"
)


def _guardian(
    display_name: str,
    npc_id: int,
    level: int,
    lifepoints: int,
    max_hit: int,
    attack_style: str,
    oldid: int,
) -> dict[str, Any]:
    # The period pages expose level, LP, style, and approximate max hit but not
    # the full combat-stat block. Level-shaped attack/defence values are a
    # labeled bounded abstraction used only to drive the shared Combat reducer.
    return {
        "display_name": display_name,
        "npc_id": npc_id,
        "level": level,
        "stats": {
            "attack": level if attack_style == "melee" else 1,
            "strength": level if attack_style == "melee" else 1,
            "defence": level,
            "magic": level if attack_style == "magic" else 1,
            "ranged": level if attack_style == "ranged" else 1,
            "hitpoints": lifepoints,
        },
        "bonuses": {},
        "attack_style": attack_style,
        "attack_speed": 6,
        "max_hit": max_hit,
        "source": (
            f"RuneScape Wiki {display_name} oldid={oldid}; "
            "full combat stats are a level-shaped bounded abstraction"
        ),
    }


PHOENIX_LAIR_GUARDIANS: dict[str, dict[str, Any]] = {
    "lesser_reborn_warrior": _guardian(
        "Lesser reborn warrior", 8557, 100, 960, 100, "melee", 5882751
    ),
    "greater_reborn_warrior": _guardian(
        "Greater reborn warrior", 8559, 128, 1350, 120, "melee", 5929109
    ),
    "lesser_reborn_ranger": _guardian(
        "Lesser reborn ranger", 8561, 87, 800, 110, "ranged", 6352235
    ),
    "greater_reborn_ranger": _guardian(
        "Greater reborn ranger", 8563, 107, 1000, 130, "ranged", 6352812
    ),
    "lesser_reborn_mage": _guardian(
        "Lesser reborn mage", 8565, 82, 800, 90, "magic", 6049792
    ),
    "greater_reborn_mage": _guardian(
        "Greater reborn mage", 8567, 112, 1100, 120, "magic", 6351801
    ),
}
PHOENIX_LAIR_GUARDIANS["lesser_reborn_warrior"]["source"] += (
    "; source max hit is unknown, so 100 LP is a bounded placeholder"
)

PHOENIX_LAIR_GUARDIAN_IDS = tuple(PHOENIX_LAIR_GUARDIANS)

PHOENIX_LAIR_PHOENIX = {
    "display_name": "Phoenix",
    "npc_id": 8549,
    "level": 235,
    "stats": {
        "attack": 1,
        "strength": 1,
        "defence": 235,
        "magic": 235,
        "ranged": 1,
        "hitpoints": 2550,
    },
    "bonuses": {},
    "attack_style": "magic",
    "attack_speed": 6,
    "max_hit": 290,
    "drops": {"guaranteed": (), "tables": ()},
    "slayer_xp": 0.0,
    "source": (
        "RuneScape Wiki Phoenix oldid=6588809; full combat stats are a "
        "level-shaped bounded abstraction"
    ),
}

PHOENIX_LAIR_FIXED_REWARDS = {
    "firemaking_exp": 7500.0,
    "fletching_exp": 3000.0,
    "crafting_exp": 1000.0,
}


def phoenix_lair_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        PHOENIX_LAIR_ACTIVITY_ID: {
            "display_name": "Phoenix Lair",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "outputs": (PHOENIX_QUILL_ITEM,),
            "source": PHOENIX_LAIR_SOURCE,
        }
    }


def phoenix_lair_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        PHOENIX_EGG_ITEM: {
            "category": "pet",
            "item_id": 14629,
            "stackable": False,
            "tradeable": False,
            "source": "RuneScape Wiki Phoenix egg oldid=4364298; OpenRS2 rev-742",
        },
        CRACKED_PHOENIX_EGG_ITEM: {
            "category": "pet",
            "item_id": 14630,
            "stackable": False,
            "tradeable": False,
            "source": (
                "RuneScape Wiki Cracked phoenix egg oldid=4362222; OpenRS2 rev-742"
            ),
        },
    }
