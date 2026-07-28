"""Period-pinned Skeletal Horror activity and encounter data."""

from __future__ import annotations

import copy
from typing import Any


SKELETAL_HORROR_ACTIVITY_ID = "skeletal_horror"
SKELETAL_HORROR_TARGET_ID = "skeletal_horror"
SKELETAL_HORROR_ELITE_CLUE_ITEM = "Clue scroll (elite)"
SKELETAL_HORROR_WEEK_REVIEWS = 1680
# The source says repeat availability *resets* each simulated week, so a missed
# week is forfeited rather than banked; one entry is the whole allowance.
SKELETAL_HORROR_ENTRY_CAP = 1
SKELETAL_HORROR_ELITE_CLUE_CHANCE = 1.0 / 20.0
SKELETAL_HORROR_MAX_LIFEPOINTS = 3500
SKELETAL_HORROR_LIMBS = ("right arm", "left arm", "tail")
SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL = 78

SKELETAL_HORROR_SOURCE = (
    "memory-bank/source-audits/skeletal-horror-implementation-harvest-2026-07-19.md; "
    "memory-bank/boss-instance-contract-2026-07-18.md"
)

# Darkan rev-727 cache dump, developer-information/npcListBonuses.txt:9178-9182.
# NPCs 9176-9180 share this exact attack, defence, and strength bonus array.
_SHARED_BONUSES: dict[str, int] = {
    "attack_stab": 0,
    "attack_slash": 0,
    "attack_crush": 0,
    "attack_magic": 0,
    "attack_ranged": 0,
    "defence_stab": 100,
    "defence_slash": 110,
    "defence_crush": 50,
    "defence_magic": 0,
    "defence_ranged": 100,
    "melee_strength": 0,
    "ranged_strength": 0,
    "magic_damage": 0,
}

SKELETAL_HORROR_PHASES: tuple[dict[str, Any], ...] = (
    {
        "npc_id": 9176,
        "combat_level": 320,
        "remaining_lifepoints": 3500,
        "max_hit": 334,
        "attack_styles": ("melee", "magic"),
        "stats": {  # PLACEHOLDER(skeletal_horror.phase_320_stats): authentic phase-320 combat-definition stats
            "attack": 320,
            "strength": 320,
            "defence": 320,
            "magic": 320,
            "hitpoints": SKELETAL_HORROR_MAX_LIFEPOINTS,
        },
    },
    {
        "npc_id": 9177,
        "combat_level": 260,
        "remaining_lifepoints": 2750,
        "max_hit": 214,
        "attack_styles": ("melee", "magic"),
        "stats": {  # PLACEHOLDER(skeletal_horror.phase_260_stats): authentic phase-260 combat-definition stats
            "attack": 260,
            "strength": 260,
            "defence": 260,
            "magic": 260,
            "hitpoints": SKELETAL_HORROR_MAX_LIFEPOINTS,
        },
    },
    {
        "npc_id": 9178,
        "combat_level": 180,
        "remaining_lifepoints": 2000,
        "max_hit": 154,
        "attack_styles": ("melee",),
        "stats": {  # PLACEHOLDER(skeletal_horror.phase_180_stats): authentic phase-180 combat-definition stats
            "attack": 180,
            "strength": 180,
            "defence": 180,
            "magic": 180,
            "hitpoints": SKELETAL_HORROR_MAX_LIFEPOINTS,
        },
    },
    {
        "npc_id": 9179,
        "combat_level": 100,
        "remaining_lifepoints": 1250,
        "max_hit": 74,
        "attack_styles": ("melee",),
        "stats": {  # PLACEHOLDER(skeletal_horror.phase_100_stats): authentic phase-100 combat-definition stats
            "attack": 100,
            "strength": 100,
            "defence": 100,
            "magic": 100,
            "hitpoints": SKELETAL_HORROR_MAX_LIFEPOINTS,
        },
    },
)

SKELETAL_HORROR_FIRST_REWARDS = {
    "slayer_exp": 10_000.0,
    "prayer_exp": 7_000.0,
}
SKELETAL_HORROR_REPEAT_REWARDS = {
    "slayer_exp": 1_250.0,
    "prayer_exp": 1_000.0,
}


def skeletal_horror_enemy_pure(
    phase_index: int,
    attack_style: str,
) -> dict[str, Any]:
    phase = SKELETAL_HORROR_PHASES[
        max(0, min(len(SKELETAL_HORROR_PHASES) - 1, int(phase_index)))
    ]
    return {
        "display_name": "Skeletal Horror",
        "npc_id": phase["npc_id"],
        "level": phase["combat_level"],
        "group": "Skeletal Horror",
        "stats": copy.deepcopy(phase["stats"]),
        "bonuses": dict(_SHARED_BONUSES),
        "attack_style": (
            attack_style
            if attack_style in phase["attack_styles"]
            else phase["attack_styles"][0]
        ),
        "attack_speed": 4,
        "max_hit": phase["max_hit"],
        "drops": {"guaranteed": (), "tables": ()},
        "slayer_xp": 0.0,
        "encounter_only": True,
        "source": SKELETAL_HORROR_SOURCE,
    }


def skeletal_horror_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SKELETAL_HORROR_ACTIVITY_ID: {
            "display_name": "Skeletal Horror",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "outputs": (SKELETAL_HORROR_ELITE_CLUE_ITEM,),
            "source": SKELETAL_HORROR_SOURCE,
        }
    }


def skeletal_horror_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SKELETAL_HORROR_ELITE_CLUE_ITEM: {
            "category": "material",
            "stackable": False,
            "tradeable": False,
            "source": (
                "Skeletal Horror harvest: repeat elite clue reward; "
                "RuneScape Wiki Do No Evil oldid=6587790"
            ),
        }
    }
