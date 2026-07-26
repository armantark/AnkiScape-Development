"""Pinned Clan Wars portal modes and AnkiScape match metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CLAN_WARS_ACTIVITY_ID = "clan_wars"
CLAN_WARS_COMBAT_TARGET_ID = "clan_wars_opponent"
CLAN_WARS_WHITE_MODE = "white_ffa"
CLAN_WARS_RED_MODE = "red_ffa"
CLAN_WARS_PURPLE_MODE = "purple_team"
CLAN_WARS_MAX_REVIEWS = 8
CLAN_WARS_COMBAT_TICKS = 6

CLAN_WARS_SOURCE = (
    "RuneScape Wiki Clan Wars oldid=6288405 "
    "(2012-09-24T05:10:06Z); Darkan FFAController.java and Potions.kt at "
    "22c1460e52f8eac453e925586429c8c9ee22c652; OpenRS2 cache revisions "
    "727 and 742 object definitions 38698, 38699, 38700, 49255, and 49256"
)


@dataclass(frozen=True)
class ClanWarsMode:
    id: str
    display_name: str
    description: str
    dangerous: bool
    team_race: bool


CLAN_WARS_MODES = (
    ClanWarsMode(
        CLAN_WARS_WHITE_MODE,
        "White portal · safe free-for-all",
        "Fight simulated opponents without losing items on death.",
        False,
        False,
    ),
    ClanWarsMode(
        CLAN_WARS_RED_MODE,
        "Red portal · dangerous free-for-all",
        "Death destroys carried and worn items; Protect Item saves one slot.",
        True,
        False,
    ),
    ClanWarsMode(
        CLAN_WARS_PURPLE_MODE,
        "Purple portal · team score race",
        "A bounded AnkiScape team-score race against simulated opponents.",
        False,
        True,
    ),
)
CLAN_WARS_MODES_BY_ID = {mode.id: mode for mode in CLAN_WARS_MODES}
CLAN_WARS_MODE_IDS = tuple(mode.id for mode in CLAN_WARS_MODES)


@dataclass(frozen=True)
class ClanWarsPolicy:
    id: str
    display_name: str
    description: str


CLAN_WARS_POLICIES = (
    ClanWarsPolicy(
        "balanced",
        "Balanced",
        "Use the current Combat loadout without an extra damage modifier.",
    ),
    ClanWarsPolicy(
        "pressure",
        "Pressure",
        "Trade defence for a small damage increase during this simulation.",
    ),
    ClanWarsPolicy(
        "survival",
        "Survival",
        "Trade damage for a more conservative simulation.",
    ),
)
CLAN_WARS_POLICIES_BY_ID = {
    policy.id: policy for policy in CLAN_WARS_POLICIES
}
CLAN_WARS_POLICY_IDS = tuple(policy.id for policy in CLAN_WARS_POLICIES)

# Opponent rotation, review cap, and policy modifiers are bounded AnkiScape
# abstractions. They do not claim to reproduce a period Clan Wars match format.
CLAN_WARS_OPPONENT_OFFSETS = (-6, 2, 8)
CLAN_WARS_POLICY_DAMAGE_MULTIPLIERS = {
    "balanced": 1.0,
    "pressure": 1.12,
    "survival": 0.88,
}

CLAN_WARS_ASSET_MANIFEST = (
    {
        "item_name": "Clan Wars",
        "wiki_title": "Clan wars portal.png",
        "output_path": "activityicons/clan_wars.png",
        "size": 64,
    },
)


def clan_wars_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CLAN_WARS_ACTIVITY_ID: {
            "display_name": "Clan Wars",
            "requirements": {},
            "skill_requirements": {},
            "outputs": (),
            "batch_size": 1,
            "group": "minigames",
            "source": CLAN_WARS_SOURCE,
        }
    }


def clan_wars_enemy_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CLAN_WARS_COMBAT_TARGET_ID: {
            "name": "Simulated Clan Wars opponent",
            "lifepoints": 100,
            "attack_level": 10,
            "strength_level": 10,
            "defense_level": 10,
            "ranged_level": 10,
            "magic_level": 10,
            "attack_bonus": 0,
            "strength_bonus": 0,
            "defense_bonus": 0,
            "attack_speed": 4,
            "attack_style": "melee",
            "attack_xp": 0,
            "strength_xp": 0,
            "defense_xp": 0,
            "hitpoints_xp": 0,
            "drops": (),
            "source": CLAN_WARS_SOURCE,
        }
    }
