"""Cutoff Temple Trekking companions, routes, event graph, and token rewards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TEMPLE_TREKKING_ACTIVITY_ID = "temple_trekking"
TEMPLE_TREKKING_COMBAT_TARGET_ID = "temple_trekking_ambush"
TEMPLE_TREKKING_DIRECTIONS = (
    ("trek", "Temple Trekking · Burgh de Rott to Paterdomus"),
    ("ramble", "Burgh de Rott Ramble · Paterdomus to Burgh de Rott"),
)
TEMPLE_TREKKING_DIRECTION_QUESTS = {
    "trek": "in_aid_of_the_myreque",
    "ramble": "the_darkness_of_hallowvale",
}
TEMPLE_TREKKING_START_POINTS = {
    "trek": "Burgh de Rott",
    "ramble": "Paterdomus",
}
TEMPLE_TREKKING_DESTINATIONS = {
    "trek": "Paterdomus",
    "ramble": "Burgh de Rott",
}
TEMPLE_TREKKING_EVENTS_PER_TREK = 4  # PLACEHOLDER(temple_trekking.events_per_trek): authentic trek node-count distribution
TEMPLE_TREKKING_COMPANION_FOOD_CAP = 28
TEMPLE_TREKKING_COMPANION_FOOD_ITEM = "Lobster"
TEMPLE_TREKKING_COMPANION_FOOD_HEAL = 120
TEMPLE_TREKKING_COMBAT_TICKS = 6

TEMPLE_TREKKING_SOURCE = (
    "RuneScape Wiki Temple Trekking oldid=6514712 (2012-11-01T04:27:27Z); "
    "Reward token oldid=6356763 (2012-10-06T13:22:18Z); rev-742 items "
    "7774-7799 and NPCs 14011-14032; Darkan c95aca409 has quest references only; "
    "memory-bank/source-audits/temple-trekking-trek-model-2026-07-18.md"
)


@dataclass(frozen=True)
class TempleTrekkingCompanion:
    id: str
    display_name: str
    direction: str
    difficulty: str
    npc_ids: tuple[int, ...]


TEMPLE_TREKKING_COMPANIONS = (
    TempleTrekkingCompanion("dean_vellio", "Dean Vellio", "trek", "easy", (14011, 14012, 14057, 14058)),
    TempleTrekkingCompanion("jayene_kliyn", "Jayene Kliyn", "trek", "medium", (14015, 14016, 14061, 14062)),
    TempleTrekkingCompanion("smiddi_ryak", "Smiddi Ryak", "trek", "hard", (14019, 14020, 14065, 14066)),
    TempleTrekkingCompanion("pazuzu", "Pazuzu", "ramble", "easy", (14013, 14014, 14059, 14060)),
    TempleTrekkingCompanion("zachory_bragg", "Zachory Bragg", "ramble", "medium", (14017, 14018, 14063, 14064)),
    TempleTrekkingCompanion("rolayne_twickit", "Rolayne Twickit", "ramble", "hard", (14021, 14022, 14067, 14068)),
)
TEMPLE_TREKKING_COMPANIONS_BY_ID = {
    row.id: row for row in TEMPLE_TREKKING_COMPANIONS
}
TEMPLE_TREKKING_DEFAULT_COMPANIONS = {
    direction: next(row.id for row in TEMPLE_TREKKING_COMPANIONS if row.direction == direction and row.difficulty == "easy")
    for direction, _label in TEMPLE_TREKKING_DIRECTIONS
}


@dataclass(frozen=True)
class TempleTrekkingRoute:
    id: str
    display_name: str
    difficulty: int
    combat_level: int
    enemy_count: int
    companion_pressure: int


# Companion pressure is an Anki review-scale translation of the attested rule
# that ambushes prioritise and can kill the follower.
TEMPLE_TREKKING_ROUTES = (  # PLACEHOLDER(temple_trekking.companion_combat_pressure): authentic follower-targeting attack rolls and damage
    TempleTrekkingRoute("easy", "Easy route", 0, 80, 2, 45),
    TempleTrekkingRoute("medium", "Medium route", 1, 110, 3, 75),
    TempleTrekkingRoute("hard", "Hard route", 2, 140, 4, 105),
)
TEMPLE_TREKKING_ROUTES_BY_ID = {row.id: row for row in TEMPLE_TREKKING_ROUTES}

# Hard companions are the frail, better-paying escort choice. Their exact
# level-one combat definitions are not exposed by the period record.
TEMPLE_TREKKING_COMPANION_BASE_LIFEPOINTS = {  # PLACEHOLDER(temple_trekking.companion_base_stats): authentic level-one companion combat definitions
    "easy": 1_200,
    "medium": 900,
    "hard": 600,
}
TEMPLE_TREKKING_COMPANION_XP_PER_SUCCESS = 1  # PLACEHOLDER(temple_trekking.companion_xp_per_trek): authentic companion experience awards by route and event quality


@dataclass(frozen=True)
class TempleTrekkingEvent:
    id: str
    display_name: str
    kind: str
    required_item: str = ""
    consume_count: int = 0


TEMPLE_TREKKING_EVENTS = (
    TempleTrekkingEvent("abidor_crank", "Abidor Crank", "friendly"),
    TempleTrekkingEvent("bridge", "Broken bridge", "puzzle", "Logs", 3),
    TempleTrekkingEvent("bog", "Bog", "puzzle"),
    TempleTrekkingEvent("river", "River crossing", "puzzle", "Knife", 0),
    TempleTrekkingEvent("ghasts", "Ghast ambush", "combat", "Druid pouch", 0),
    TempleTrekkingEvent("nail_beasts", "Nail beast ambush", "combat"),
    TempleTrekkingEvent("swamp_snakes", "Swamp snake ambush", "combat"),
    TempleTrekkingEvent("shades", "Shade ambush", "combat"),
)
TEMPLE_TREKKING_EVENTS_BY_ID = {row.id: row for row in TEMPLE_TREKKING_EVENTS}
TEMPLE_TREKKING_NONCOMBAT_EVENT_IDS = tuple(
    row.id for row in TEMPLE_TREKKING_EVENTS if row.kind != "combat"
)
TEMPLE_TREKKING_COMBAT_EVENT_IDS = tuple(
    row.id for row in TEMPLE_TREKKING_EVENTS if row.kind == "combat"
)
# Equal deterministic rotations stand in for the unrecovered route event table.
TEMPLE_TREKKING_EVENT_ROTATION = (  # PLACEHOLDER(temple_trekking.event_weights): authentic per-route event selector weights
    TEMPLE_TREKKING_NONCOMBAT_EVENT_IDS,
    TEMPLE_TREKKING_COMBAT_EVENT_IDS,
)

# Levels and several LP/max-hit cells are pinned; the remaining combat stats the
# shared kernel requires are breadth placeholders rather than invented canon.
TEMPLE_TREKKING_EVENT_COMBAT = {  # PLACEHOLDER(temple_trekking.event_combat_stats): complete period server combat definitions for representative ambushes
    "ghasts": {
        "easy": (79, 450, 90, "melee"),
        "medium": (109, 1_070, 120, "melee"),
        "hard": (139, 1_390, 160, "melee"),
    },
    "nail_beasts": {
        "easy": (69, 550, 120, "melee"),
        "medium": (98, 650, 120, "melee"),
        "hard": (141, 750, 120, "melee"),
    },
    "swamp_snakes": {
        "easy": (80, 1_210, 50, "melee"),
        "medium": (109, 1_250, 120, "melee"),
        "hard": (139, 1_300, 180, "melee"),
    },
    "shades": {
        "easy": (80, 900, 90, "melee"),
        "medium": (105, 1_100, 120, "melee"),
        "hard": (130, 1_300, 160, "melee"),
    },
}

TEMPLE_TREKKING_TOKEN_IDS = {  # PLACEHOLDER(temple_trekking.token_color_item_ids): symbolic cache mapping from items 7774/7775/7776 to blue/yellow/red
    "blue": 7774,
    "yellow": 7776,
    "red": 7775,
}
TEMPLE_TREKKING_TOKEN_ITEMS = {
    color: f"Reward token ({color})" for color in TEMPLE_TREKKING_TOKEN_IDS
}
TEMPLE_TREKKING_TOKEN_COLORS = tuple(TEMPLE_TREKKING_TOKEN_IDS)
TEMPLE_TREKKING_TOKEN_SCORE_THRESHOLDS = (1, 3)  # PLACEHOLDER(temple_trekking.token_tier_formula): authentic route/companion/event-quality token award function


@dataclass(frozen=True)
class TempleTrekkingReward:
    id: str
    display_name: str
    ranges: dict[str, tuple[int, int]]
    outputs: tuple[tuple[str, int], ...]


TEMPLE_TREKKING_REWARDS = (
    TempleTrekkingReward(
        "pure_essence",
        "Pure essence",
        {"blue": (50, 150), "yellow": (70, 210), "red": (100, 300)},
        (("Pure essence", 1),),
    ),
    TempleTrekkingReward(
        "bow_string",
        "Bow string",
        {"blue": (30, 90), "yellow": (40, 120), "red": (70, 210)},
        (("Bow string", 1),),
    ),
    TempleTrekkingReward(
        "silver_bar",
        "Silver bar",
        {"blue": (55, 165), "yellow": (75, 225), "red": (120, 360)},
        (("Silver bar", 1),),
    ),
    TempleTrekkingReward(
        "coal_and_iron",
        "Coal and iron ore",
        {"blue": (7, 21), "yellow": (10, 30), "red": (20, 60)},
        (("Coal", 2), ("Iron ore", 1)),
    ),
    TempleTrekkingReward(
        "watermelon_seed",
        "Watermelon seed",
        {"blue": (2, 8), "yellow": (4, 12), "red": (5, 15)},
        (("Watermelon seed", 1),),
    ),
    TempleTrekkingReward(
        "raw_shark",
        "Raw shark",
        {"blue": (8, 24), "yellow": (10, 30), "red": (18, 54)},
        (("Raw shark", 1),),
    ),
)
TEMPLE_TREKKING_REWARDS_BY_ID = {
    row.id: row for row in TEMPLE_TREKKING_REWARDS
}
TEMPLE_TREKKING_DEFAULT_REWARD = "pure_essence"
# The cutoff ranges are exact; the quantity selector inside each range is not.
TEMPLE_TREKKING_REWARD_ROLL_MODE = "uniform"  # PLACEHOLDER(temple_trekking.reward_quantity_distribution): authentic token reward quantity roll and exceptional-reward chance

TEMPLE_TREKKING_ASSET_MANIFEST = tuple(
    {
        "item_name": TEMPLE_TREKKING_TOKEN_ITEMS[color],
        "wiki_title": f"Reward token ({color}).png",
        "output_path": (
            "activityicons/temple_trekking.png"
            if color == "red"
            else f"activityitems/temple_trekking_token_{color}.png"
        ),
        "size": 64,
    }
    for color in TEMPLE_TREKKING_TOKEN_COLORS
)


def temple_trekking_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TEMPLE_TREKKING_ACTIVITY_ID: {
            "display_name": "Temple Trekking",
            "requirements": {},
            "skill_requirements": {},
            "outputs": tuple(TEMPLE_TREKKING_TOKEN_ITEMS.values()),
            "batch_size": 1,
            "group": "minigames",
            "source": TEMPLE_TREKKING_SOURCE,
        }
    }


def temple_trekking_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    rows = {
        "Druid pouch": (2957, False),
        **{
            item_name: (TEMPLE_TREKKING_TOKEN_IDS[color], False)
            for color, item_name in TEMPLE_TREKKING_TOKEN_ITEMS.items()
        },
    }
    return {
        item_name: {
            "category": "material",
            "source_item_id": item_id,
            "stackable": stackable,
            "tradeable": False,
            "source": TEMPLE_TREKKING_SOURCE,
        }
        for item_name, (item_id, stackable) in rows.items()
    }


def temple_trekking_enemy_pure(event_id: str, route_id: str) -> dict[str, Any]:
    level, lifepoints, max_hit, style = TEMPLE_TREKKING_EVENT_COMBAT[event_id][route_id]
    core = max(1, min(99, round(level * 0.72)))
    return {
        "display_name": TEMPLE_TREKKING_EVENTS_BY_ID[event_id].display_name,
        "level": level,
        "group": "Temple Trekking",
        "stats": {
            "attack": core,
            "strength": core,
            "defence": core,
            "hitpoints": lifepoints,
            "magic": core,
            "ranged": core,
        },
        "bonuses": {},
        "attack_style": style,
        "attack_speed": 4,
        "max_hit": max_hit,
        "drops": {"guaranteed": (), "tables": ()},
        "xp_multiplier": 1.0,
        "encounter_only": True,
        "source": TEMPLE_TREKKING_SOURCE,
    }


def temple_trekking_enemy_registry_as_dict() -> dict[str, dict[str, Any]]:
    return {
        TEMPLE_TREKKING_COMBAT_TARGET_ID: temple_trekking_enemy_pure(
            "ghasts", "easy"
        )
    }
