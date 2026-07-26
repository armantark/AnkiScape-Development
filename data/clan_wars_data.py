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
    "RuneScape Wiki Clan Wars oldid=6288405 (2012-09-24T05:10:06Z); Darkan "
    "clanwars/FFAController.java, Potions.kt checkPVPPotionBoosts and "
    "Player.sendPVPItemsOnDeath at d14face35aa5c851b7d3c48df79f619ef399a366"
)


@dataclass(frozen=True)
class ClanWarsMode:
    id: str
    display_name: str
    description: str
    dangerous: bool
    entry_warning: str


CLAN_WARS_MODES = (
    ClanWarsMode(
        CLAN_WARS_WHITE_MODE,
        "White portal · safe free-for-all",
        "Fight the surrounding free-for-all without losing items on death.",
        False,
        "",
    ),
    ClanWarsMode(
        CLAN_WARS_RED_MODE,
        "Red portal · dangerous free-for-all",
        "Death destroys carried and worn items; Protect Item saves one.",
        True,
        "On death, every carried and worn item is destroyed except the one "
        "that Protect Item saves. There is no gravestone and no Death's "
        "Office recovery, teleport escape is forbidden, and extreme or "
        "Overload boosts are clamped on entry.",
    ),
    ClanWarsMode(
        CLAN_WARS_PURPLE_MODE,
        "Purple portal · team score race",
        "A bounded team-score race; the opposing clan also scores elsewhere.",
        False,
        "",
    ),
)
CLAN_WARS_MODES_BY_ID = {mode.id: mode for mode in CLAN_WARS_MODES}
CLAN_WARS_MODE_IDS = tuple(mode.id for mode in CLAN_WARS_MODES)

# Match shape. A period free-for-all is a crowd, not a duel: rivals are worn
# down by combatants other than the player, and the player is worn down by
# combatants other than the engaged rival. These divisors are the same kind of
# disclosed review-scale abstraction that TzHaar Fight Pit ships for its
# roster attrition and late-round pressure, and they carry no claim about a
# period rate. They exist so that a kill, a death, a win, a loss and a draw are
# all reachable inside the bounded match instead of only a 0-0 draw.
CLAN_WARS_OPPONENT_OFFSETS = (-6, 2, 8)
CLAN_WARS_RIVAL_CROSSFIRE_DIVISOR = 3
CLAN_WARS_PLAYER_CROSSFIRE_DIVISOR = 6
CLAN_WARS_CROSSFIRE_START_REVIEW = 3
CLAN_WARS_TEAM_SCORE_INTERVAL = 3

# Exact, from Darkan `Potions.kt` `checkPVPPotionBoosts`, which the dangerous
# free-for-all controller calls on entry: each combat skill is lowered to
# `base + flat + base * multiplier` whenever a boost has carried it higher.
CLAN_WARS_RED_BOOST_CAPS = (
    ("attack", 5, 0.15),
    ("strength", 5, 0.15),
    ("defense", 5, 0.15),
    ("ranged", 5, 0.10),
    ("magic", 5, 0.0),
)


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


def clan_wars_enemy_pure() -> dict[str, Any]:
    """Hidden registry row; live rival stats are persisted per match."""
    return {
        "display_name": "Clan Wars rival",
        "level": 3,
        "group": "Clan Wars",
        "stats": {
            "attack": 1,
            "strength": 1,
            "defence": 1,
            "hitpoints": 100,
            "magic": 1,
            "ranged": 1,
        },
        "bonuses": {},
        "attack_style": "melee",
        "attack_speed": 4,
        "drops": {"guaranteed": (), "tables": ()},
        "xp_multiplier": 1.0,
        "source": CLAN_WARS_SOURCE + "; hidden dynamic-opponent registry row",
    }
