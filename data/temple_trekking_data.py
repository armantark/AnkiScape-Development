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
TEMPLE_TREKKING_DESTINATIONS = {
    "trek": "Paterdomus",
    "ramble": "Burgh de Rott",
}
TEMPLE_TREKKING_EVENTS_PER_TREK = 4  # PLACEHOLDER(temple_trekking.events_per_trek): authentic trek node-count distribution
TEMPLE_TREKKING_COMPANION_FOOD_CAP = 28  # Period follower inventory capacity.
# One preparation compresses gathering the minimum three Mort myre fungi; each
# fungus adds one charge, and repeated fills accumulate rather than hitting a cap.
TEMPLE_TREKKING_DRUID_POUCH_PREP_CHARGES = 3
TEMPLE_TREKKING_COMPANION_FOOD_ITEM = "Lobster"
TEMPLE_TREKKING_COMPANION_FOOD_HEAL = 120
TEMPLE_TREKKING_COMPANION_EAT_THRESHOLD_NUMERATOR = 1  # PLACEHOLDER(temple_trekking.companion_eat_threshold): authentic follower food-selection timing
TEMPLE_TREKKING_COMPANION_EAT_THRESHOLD_DENOMINATOR = 2
# Six ticks is the shared live-combat review adapter, not a period trek number.
TEMPLE_TREKKING_COMBAT_TICKS = 6
TEMPLE_TREKKING_SWAMP_CREATURE_STAGES = 2  # PLACEHOLDER(temple_trekking.swamp_creature_stages): authentic multi-stage swamp-creature phase count and transition

TEMPLE_TREKKING_SOURCE = (
    "RuneScape Wiki Temple Trekking oldid=6514712 (2012-11-01T04:27:27Z); "
    "Reward token oldid=6356763 (2012-10-06T13:22:18Z); rev-727 enum 5033/5034; "
    "OpenRS2 cache 309 item/NPC definitions; Darkan c95aca409 quest references; "
    "memory-bank/source-audits/temple-trekking-trek-model-2026-07-18.md"
)

# Rev-727 enum 5034 maps companion level to cumulative companion XP exactly.
TEMPLE_TREKKING_COMPANION_XP_THRESHOLDS = (
    0, 4, 5, 6, 7, 9, 10, 13, 15, 18, 22, 27, 32, 38, 46, 56, 67,
    80, 96, 116, 139, 167, 200, 241, 289, 347, 416, 500, 600, 720, 806,
    896, 990, 1_088, 1_190, 1_296, 1_406, 1_520, 1_638, 1_760, 1_886,
    2_016, 2_150, 2_288, 2_430, 2_576, 2_726, 2_880, 3_038, 3_200,
    3_366, 3_536, 3_710, 3_888, 4_070, 4_256, 4_446, 4_640, 4_838,
    5_040, 5_246, 5_456, 5_670, 5_888, 6_110, 6_336, 6_566, 6_800,
    7_038, 7_280, 7_526, 7_776, 8_030, 8_288, 8_550, 8_816, 9_086,
    9_360, 9_638, 9_920, 10_206, 10_496, 10_790, 11_088, 11_390,
    11_696, 12_006, 12_320, 12_638, 12_960, 13_286, 13_616, 13_950,
    14_288, 14_630, 14_976, 15_326, 15_680, 16_000,
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
    enemy_count: int
    companion_pressure: int


# Enemy count and companion pressure are review-scale translations of the attested
# rule that ambushes prioritise and can kill the follower.
# PLACEHOLDER(temple_trekking.route_enemy_counts): authentic per-event enemy counts by route
TEMPLE_TREKKING_ROUTES = (  # PLACEHOLDER(temple_trekking.companion_combat_pressure): authentic follower-targeting attack rolls and damage
    TempleTrekkingRoute("easy", "Easy route", 0, 2, 45),
    TempleTrekkingRoute("medium", "Medium route", 1, 3, 75),
    TempleTrekkingRoute("hard", "Hard route", 2, 4, 80),
)
TEMPLE_TREKKING_ROUTES_BY_ID = {row.id: row for row in TEMPLE_TREKKING_ROUTES}

# Hard companions are the frail, better-paying escort choice. Client parameters
# exist, but a complete level-one server combat definition is not yet recovered.
TEMPLE_TREKKING_COMPANION_BASE_LIFEPOINTS = {  # PLACEHOLDER(temple_trekking.companion_base_stats): authentic level-one companion combat definitions
    "easy": 1_200,
    "medium": 900,
    "hard": 600,
}
TEMPLE_TREKKING_COMPANION_LIFEPOINTS_PER_LEVEL = 10  # PLACEHOLDER(temple_trekking.companion_lifepoints_per_level): authentic companion stat growth by level
TEMPLE_TREKKING_COMPANION_XP_PER_SUCCESS = 4  # PLACEHOLDER(temple_trekking.companion_xp_per_trek): authentic companion experience awards by route and event quality


@dataclass(frozen=True)
class TempleTrekkingEvent:
    id: str
    display_name: str
    kind: str
    required_item: str = ""
    consume_count: int = 0
    direction: str = ""
    required_quest: str = ""


# Breadth one keeps the smallest set that exercises friendly, consumable puzzle,
# trial puzzle, tool puzzle, hybrid, ordinary combat, direction-specific and
# quest-gated edges. Each node is attested; unresolved branch internals remain
# explicit abstractions or placeholders in the pure resolver.
TEMPLE_TREKKING_EVENTS = (
    TempleTrekkingEvent("abidor_crank", "Abidor Crank", "friendly"),
    # PLACEHOLDER(temple_trekking.bridge_log_cost): authentic logs/planks and tool costs for all bridge sections
    TempleTrekkingEvent("bridge", "Broken bridge", "puzzle", "Logs", 3),
    TempleTrekkingEvent("bog", "Bog", "puzzle"),
    TempleTrekkingEvent("river", "River crossing", "puzzle", "Knife", 0),
    TempleTrekkingEvent("campsite", "Starving adventurers' campsite", "hybrid"),
    TempleTrekkingEvent("ghasts", "Ghast ambush", "combat"),
    TempleTrekkingEvent("swamp_snakes", "Swamp snake ambush", "combat"),
    TempleTrekkingEvent("swamp_creature", "Swamp creature", "combat", direction="ramble"),
    TempleTrekkingEvent(
        "vyrewatch",
        "Vyrewatch ambush",
        "combat",
        required_quest="legacy_of_seergaze",
    ),
)
TEMPLE_TREKKING_EVENTS_BY_ID = {row.id: row for row in TEMPLE_TREKKING_EVENTS}
TEMPLE_TREKKING_NONCOMBAT_EVENT_IDS = tuple(
    row.id for row in TEMPLE_TREKKING_EVENTS if row.kind != "combat"
)
TEMPLE_TREKKING_COMBAT_EVENT_IDS = tuple(
    row.id for row in TEMPLE_TREKKING_EVENTS if row.kind == "combat"
)
# Levels and several LP/max-hit cells are pinned; the remaining combat stats the
# shared kernel requires are breadth placeholders rather than invented canon.
TEMPLE_TREKKING_EVENT_COMBAT = {  # PLACEHOLDER(temple_trekking.event_combat_stats): complete period server combat definitions for representative ambushes
    "ghasts": {
        "easy": (79, 450, 90, "melee"),
        "medium": (109, 1_070, 120, "melee"),
        "hard": (139, 1_390, 160, "melee"),
    },
    "swamp_snakes": {
        "easy": (80, 1_210, 50, "melee"),
        "medium": (109, 1_250, 120, "melee"),
        "hard": (139, 1_300, 180, "melee"),
    },
    "swamp_creature": {
        "easy": (80, 900, 90, "melee"),
        "medium": (110, 1_100, 120, "melee"),
        "hard": (140, 1_300, 160, "melee"),
    },
    "vyrewatch": {
        "easy": (80, 900, 90, "melee"),
        "medium": (110, 1_100, 120, "melee"),
        "hard": (140, 1_300, 160, "melee"),
    },
}

TEMPLE_TREKKING_TOKEN_IDS = {
    "blue": 7776,
    "yellow": 7774,
    "red": 7775,
}
TEMPLE_TREKKING_TOKEN_ITEMS = {
    color: f"Reward token ({color})" for color in TEMPLE_TREKKING_TOKEN_IDS
}
TEMPLE_TREKKING_TOKEN_COLORS = tuple(TEMPLE_TREKKING_TOKEN_IDS)
TEMPLE_TREKKING_TOKEN_SCORE_THRESHOLDS = (0, 2)  # PLACEHOLDER(temple_trekking.token_tier_formula): authentic route/companion/event-quality/follower-damage token award function

# Combat-kernel adapters fill fields the cache identity rows do not source.
TEMPLE_TREKKING_ENEMY_CORE_STAT_RATIO = 0.72
TEMPLE_TREKKING_ENEMY_ATTACK_SPEED = 4


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
        # The dedicated Reward token page wins the conflicting aggregate table.
        {"blue": (56, 165), "yellow": (75, 225), "red": (120, 360)},
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
        # The dedicated Reward token page wins the conflicting aggregate table.
        {"blue": (2, 6), "yellow": (4, 12), "red": (5, 15)},
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

TEMPLE_TREKKING_ASSET_MANIFEST = (
    {
        "item_name": "Temple Trekking",
        "wiki_title": "Reward token (red).png",
        "output_path": "activityicons/temple_trekking.png",
        "size": 64,
    },
    {
        "item_name": "Druid pouch",
        "wiki_title": "Druid pouch.png",
        "output_path": "activityitems/temple_trekking_druid_pouch.png",
        "size": 64,
    },
    *(
        {
            "item_name": TEMPLE_TREKKING_TOKEN_ITEMS[color],
            "wiki_title": f"Reward token ({color}).png",
            "output_path": f"activityitems/temple_trekking_token_{color}.png",
            "size": 64,
        }
        for color in TEMPLE_TREKKING_TOKEN_COLORS
    ),
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
    core = max(1, min(99, round(level * TEMPLE_TREKKING_ENEMY_CORE_STAT_RATIO)))
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
        "attack_speed": TEMPLE_TREKKING_ENEMY_ATTACK_SPEED,
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
