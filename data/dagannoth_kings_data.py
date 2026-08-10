"""Period-pinned minimum data for the Dagannoth Kings room."""

from __future__ import annotations

from typing import Any


DAGANNOTH_KINGS_ACTIVITY_ID = "dagannoth_kings"
DAGANNOTH_KINGS_REVIEW_TICKS = 6
DAGANNOTH_KINGS_RESPAWN_TICKS = 59
DAGANNOTH_KING_IDS = (
    "dagannoth_prime",
    "dagannoth_supreme",
    "dagannoth_rex",
)

DAGANNOTH_KINGS_SOURCE = (
    "RuneScape Wiki Dagannoth Rex oldid=6505723, Dagannoth Prime "
    "oldid=6457675, and Dagannoth Supreme oldid=6535937; Darkan NPC "
    "combat definitions and boss drop tables"
)

# PLACEHOLDER(dagannoth_kings.dragon_hatchet_drop_rate): The cutoff pages prove
# that all three kings drop the Dragon hatchet but give only qualitative rarity.
# Darkan's executable lineage uses one independent 1/128 row for each king.
_MINIMUM_DROPS = {
    "guaranteed": (("Dagannoth bones", 1), ("Dagannoth hide", 1)),
    "tables": (
        {
            "name": "Dragon hatchet",
            "total": 128,
            "slots": (
                {"item": "Dragon hatchet", "quantity": 1, "slots": 1},
                {"slots": 127},
            ),
        },
    ),
}


def _king(
    display_name: str,
    npc_id: int,
    attack_style: str,
    hitpoints: int,
    max_hit: int,
    *,
    attack: int,
    strength: int,
    defence: int,
    magic: int,
    ranged: int,
    slayer_xp: float,
    priority: int,
    oldid: int,
) -> dict[str, Any]:
    return {
        "display_name": display_name,
        "npc_id": npc_id,
        "level": 303,
        "group": "Dagannoth Kings",
        "attack_style": attack_style,
        # PLACEHOLDER(dagannoth_kings.attack_speed): Prime and Rex lack a
        # period-qualified interval; four ticks preserves Darkan's ordinary
        # NPC attack cadence and Supreme's sourced value.
        "attack_speed": 4,
        # PLACEHOLDER(dagannoth_kings.respawn_ticks): Darkan's executable
        # lineage uses 59 ticks; the cutoff pages prove respawning but not its
        # exact interval.
        "respawn_delay": DAGANNOTH_KINGS_RESPAWN_TICKS,
        "max_hit": max_hit,
        "slayer_xp": slayer_xp,
        "stats": {
            "hitpoints": hitpoints,
            "attack": attack,
            "strength": strength,
            "defence": defence,
            "magic": magic,
            "ranged": ranged,
        },
        "bonuses": {},
        "drops": _MINIMUM_DROPS,
        "priority": priority,
        "source": (
            f"https://runescape.wiki/w/{display_name.replace(' ', '_')}?oldid={oldid}; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            f"darkan-world-server/data/npcs/combatdefs/uncategorized/{display_name.lower().replace(' ', '_')}.json; "
            "/Users/ArmanTarkhanian1/Documents/2012scape with bots/"
            f"darkan-world-server/data/npcs/drops/{display_name.lower().replace(' ', '_')}.json"
        ),
    }


DAGANNOTH_KINGS_ENEMY_DATA: dict[str, dict[str, Any]] = {
    "dagannoth_prime": _king(
        "Dagannoth Prime",
        2882,
        "magic",
        2550,
        610,
        attack=255,
        strength=255,
        defence=255,
        magic=255,
        ranged=0,
        slayer_xp=255.0,
        priority=0,
        oldid=6457675,
    ),
    "dagannoth_supreme": _king(
        "Dagannoth Supreme",
        2881,
        "ranged",
        2560,
        300,
        attack=255,
        strength=255,
        defence=128,
        magic=255,
        ranged=255,
        slayer_xp=255.0,
        priority=1,
        oldid=6535937,
    ),
    "dagannoth_rex": _king(
        "Dagannoth Rex",
        2883,
        "melee",
        2550,
        280,
        attack=255,
        strength=255,
        defence=255,
        magic=0,
        ranged=255,
        slayer_xp=334.0,
        priority=2,
        oldid=6505723,
    ),
}


def dagannoth_kings_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        DAGANNOTH_KINGS_ACTIVITY_ID: {
            "display_name": "Dagannoth Kings",
            "requirements": {},
            "batch_size": 1,
            "group": "bosses",
            "outputs": {
                "Dragon hatchet": 1,
                "Dagannoth bones": 1,
                "Dagannoth hide": 1,
            },
            "source": DAGANNOTH_KINGS_SOURCE,
        }
    }
