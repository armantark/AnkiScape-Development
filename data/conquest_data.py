"""Sourced Conquest roster, commands, rewards, and disclosed translations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .equipment_data import EquipmentBonuses, EquipmentItem


CONQUEST_ACTIVITY_ID = "conquest"
CONQUEST_SOURCE = "memory-bank/source-audits/conquest-harvest-2026-07-28.md"
CONQUEST_COMBAT_REQUIREMENT = 40
CONQUEST_SETUP_BUDGET = 1_000
CONQUEST_MAX_COMMANDS = 4
CONQUEST_DEPLOYMENT_ROWS = 3
CONQUEST_RATING_START = 1_000
CONQUEST_RATING_FLOOR = 0
CONQUEST_DEFLECTOR_RATING = 1_250
CONQUEST_DEFLECTOR_COST = 150
CONQUEST_DEFLECTOR_ITEM = "Void knight deflector"

CONQUEST_BOARD_SIZE = 20  # PLACEHOLDER(conquest.board_size)
CONQUEST_UNIT_CAP = 10  # PLACEHOLDER(conquest.squad_unit_cap)
CONQUEST_STARTING_COMMAND_POINTS = 0  # PLACEHOLDER(conquest.starting_command_points)
CONQUEST_PASSIVE_COMMAND_POINTS = 25  # PLACEHOLDER(conquest.passive_command_points)
CONQUEST_EARLY_GAME_THRESHOLD = 4  # PLACEHOLDER(conquest.early_game_eligibility_threshold)

# PLACEHOLDER(conquest.turn_ratio_curve): monotone, ratio 7 around round 19,
# while five turns each remains below the maximum.
CONQUEST_TURN_RATIO_CURVE = (
    (1, 1),
    (4, 2),
    (7, 3),
    (10, 4),
    (13, 5),
    (16, 6),
    (19, 7),
    (22, 8),
    (25, 9),
    (28, 10),
)

# PLACEHOLDER(conquest.rating_formula): a symmetric opponent-sensitive Elo
# translation. K=46 and divisor 2360 preserve 2500 defeating 1311 at ±11.
CONQUEST_RATING_K = 46
CONQUEST_RATING_DIVISOR = 2_360

# PLACEHOLDER(conquest.battlefield_layouts): small seeded symmetric layout pool.
CONQUEST_BATTLEFIELD_LAYOUTS = (
    (),
    (
        (8, 8),
        (8, 9),
        (8, 10),
        (8, 11),
        (11, 8),
        (11, 9),
        (11, 10),
        (11, 11),
    ),
    (
        (6, 9),
        (6, 10),
        (9, 6),
        (9, 13),
        (10, 6),
        (10, 13),
        (13, 9),
        (13, 10),
    ),
)

# The ordinary review loop has no wall-clock timer. If one is added later, the
# sourced behavior is to end the current turn, not forfeit the match.
CONQUEST_TIMEOUT_RESOLUTION = "end_turn"  # PLACEHOLDER(conquest.turn_timeout_resolution)


@dataclass(frozen=True)
class ConquestUnit:
    id: str
    display_name: str
    cost: int
    lifepoints: int
    damage: int
    movement: int
    attack_range: int


CONQUEST_UNITS = (
    ConquestUnit("scout", "Scout", 25, 100, 100, 6, 1),
    # The cutoff wikitext says 50; a release-era in-game image says 30.
    ConquestUnit("foot_soldier", "Foot Soldier", 50, 300, 100, 4, 1),  # PLACEHOLDER(conquest.foot_soldier_cost)
    ConquestUnit("halberdier", "Halberdier", 75, 200, 200, 4, 2),
    ConquestUnit("archer", "Archer", 100, 100, 100, 3, 6),
    ConquestUnit("mage", "Mage", 100, 100, 200, 4, 4),
    ConquestUnit("knight", "Knight", 100, 300, 300, 4, 1),
    ConquestUnit("champion", "Champion", 200, 500, 400, 4, 1),
)
CONQUEST_UNITS_BY_ID = {unit.id: unit for unit in CONQUEST_UNITS}

# Reconstructed from the sourced full default squad and the guide's documented
# one-Archer alternative (replace both Foot Soldiers with a second Archer).
CONQUEST_DEFAULT_SQUAD = {
    "scout": 2,
    "foot_soldier": 2,
    "halberdier": 2,
    "archer": 1,
    "mage": 1,
    "knight": 1,
    "champion": 1,
}


@dataclass(frozen=True)
class ConquestCommand:
    id: str
    display_name: str
    cost: int
    cooldown: int
    effect: str


CONQUEST_COMMANDS = (
    ConquestCommand(
        "battle_cry",
        "Battle Cry",
        75,
        5,
        "+200 damage and +200 health until the owner's next turn",
    ),
    ConquestCommand(
        "stoicism",
        "Stoicism",
        75,
        5,
        "+400 health until the owner's next turn",
    ),
    ConquestCommand("regenerate", "Regenerate", 150, 4, "Fully restore one troop"),
    ConquestCommand(
        "bombard",
        "Bombard",
        200,
        2,
        "Deal 100 damage to one enemy; kills award no command points",
    ),
    ConquestCommand(
        "winds_of_fate",
        "Winds of Fate",
        150,
        2,
        "Complete one selected command's cooldown",
    ),
    ConquestCommand("charge", "Charge", 75, 5, "Double one troop's movement this turn"),
    ConquestCommand(
        "chastise",
        "Chastise",
        50,
        3,
        "One enemy cannot move or attack next turn; never targets the last troop",
    ),
    ConquestCommand(
        "vigilance",
        "Vigilance",
        50,
        3,
        "One troop strikes first when defending until the owner's next turn",
    ),
    ConquestCommand(
        "shield_wall",
        "Shield Wall",
        50,
        5,
        "Damage to one troop is reduced to 100 until the owner's next turn",
    ),
)
CONQUEST_COMMANDS_BY_ID = {command.id: command for command in CONQUEST_COMMANDS}
CONQUEST_DEFAULT_COMMANDS = (
    "battle_cry",
    "charge",
    "chastise",
    "vigilance",
)
CONQUEST_DOCTRINES = (
    ("balanced", "Balanced"),
    ("aggressive", "Aggressive"),
    ("defensive", "Defensive"),
)

CONQUEST_ASSET_MANIFEST = (
    {
        "item_name": "Conquest",
        "wiki_title": "Conquest icon.jpg",
        "output_path": "activityicons/conquest.png",
        "size": 64,
    },
    {
        "item_name": CONQUEST_DEFLECTOR_ITEM,
        "wiki_title": "Void knight deflector detail old.png",
        "output_path": "activityitems/conquest_void_knight_deflector.png",
        "size": 48,
    },
)


def conquest_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CONQUEST_ACTIVITY_ID: {
            "display_name": "Conquest",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "source": CONQUEST_SOURCE,
        }
    }


def conquest_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {
        CONQUEST_DEFLECTOR_ITEM: {
            "display_name": CONQUEST_DEFLECTOR_ITEM,
            "stackable": False,
            "tradeable": False,
            "source": (
                "RuneScape Wiki Void knight deflector oldid=6441661; "
                "2011Scape rev-667 item 19711; " + CONQUEST_SOURCE
            ),
        }
    }


def conquest_equipment_data_as_dict() -> dict[str, EquipmentItem]:
    return {
        CONQUEST_DEFLECTOR_ITEM: EquipmentItem(
            item_name=CONQUEST_DEFLECTOR_ITEM,
            slot="shield",
            combat_skill=None,
            required_level=1,
            two_handed=False,
            equipment_type="void_knight",
            bonuses=EquipmentBonuses(
                defence_stab=30,
                defence_slash=30,
                defence_crush=30,
                defence_magic=10,
                defence_ranged=30,
                prayer=0,
            ),
            attack_speed=4,
            source_item_id=19712,
            source=(
                "2011Scape rev-667 items.yml item 19712; RuneScape Wiki "
                "Void knight deflector oldid=6441661"
            ),
            source_status="period item identity and equipment block",
        )
    }


def conquest_units_as_dicts() -> tuple[dict[str, Any], ...]:
    return tuple(asdict(unit) for unit in CONQUEST_UNITS)


__all__ = [
    name
    for name in globals()
    if name.startswith("CONQUEST_") or name.startswith("conquest_")
]
