"""Cutoff TzHaar Fight Pit facts and disclosed review-scale abstractions."""

from __future__ import annotations

from typing import Any


TZHAAR_FIGHT_PIT_ACTIVITY_ID = "tzhaar_fight_pit"
TZHAAR_FIGHT_PIT_COMBAT_TARGET_ID = "tzhaar_fight_pit_opponent"
TZHAAR_FIGHT_PIT_TOKKUL_ITEM = "Tokkul"
TZHAAR_FIGHT_PIT_FIRE_CAPE_ITEM = "Fire cape"
TZHAAR_FIGHT_PIT_COMBAT_TICKS_PER_REVIEW = 6
TZHAAR_FIGHT_PIT_ROSTER_SIZE = 3

TZHAAR_FIGHT_PIT_SOURCE = (
    "RuneScape Wiki TzHaar Fight Pit oldid=6516239 "
    "(2012-11-01T16:20:05Z); Events Team Fight Pits oldid=4764019 "
    "(2011-09-24T17:09:08Z); OpenRS2 cache rev 742"
)

# The period source names late monster pressure and unavoidable damage without
# recovering exact timing. Reviews are the only AnkiScape progress clock.
TZHAAR_FIGHT_PIT_PRESSURE_START_REVIEW = 12
TZHAAR_FIGHT_PIT_PRESSURE_DAMAGE_DIVISOR = 10
TZHAAR_FIGHT_PIT_ATTRITION_DIVISOR = 8

TZHAAR_FIGHT_PIT_POLICIES = (
    ("casual", "Casual · engage the weakest survivor"),
    ("aggressive", "Advanced · engage the strongest survivor"),
    ("defensive", "Advanced · engage the weakest survivor"),
)


def tzhaar_fight_pit_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TZHAAR_FIGHT_PIT_ACTIVITY_ID: {
            "display_name": "TzHaar Fight Pit",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (TZHAAR_FIGHT_PIT_TOKKUL_ITEM,),
            "batch_size": 1,
            "group": "minigames",
            "source": TZHAAR_FIGHT_PIT_SOURCE,
        }
    }


def tzhaar_fight_pit_enemy_pure() -> dict[str, Any]:
    """Hidden registry row; live opponent stats are persisted per match."""
    return {
        "display_name": "Fight Pit rival",
        "level": 3,
        "group": "TzHaar Fight Pit",
        "stats": {
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "hitpoints": 100,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {},
        "attack_speed": 4,
        "drops": {"guaranteed": (), "tables": ()},
        "xp_multiplier": 1.0,
        "source": TZHAAR_FIGHT_PIT_SOURCE + "; hidden dynamic-opponent registry row",
    }
