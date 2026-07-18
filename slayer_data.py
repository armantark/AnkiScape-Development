"""Source-backed Slayer master and assignment-family data.

The live runtime begins with the complete Turael/Spria pool. Other masters stay
out of player surfaces until their full baseline pools satisfy the repository's
readiness contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


TURAEL_SOURCE = "https://runescape.wiki/w/Turael?oldid=6585248"
SPRIA_SOURCE = "https://runescape.wiki/w/Spria?oldid=6538791"
SLAYER_ASSIGNMENT_SOURCE = (
    "https://runescape.wiki/w/Slayer_assignment?oldid=6303852"
)
TURAEL_AUDIT_SOURCE = (
    "memory-bank/source-audits/slayer-turael-spria-pool-2026-07-17.md"
)


@dataclass(frozen=True)
class SlayerFamily:
    id: str
    display_name: str
    weight: int
    count_min: int
    count_max: int
    target_ids: Tuple[str, ...]
    required_slayer_level: int = 1
    required_quest_id: str = ""
    source: str = TURAEL_AUDIT_SOURCE


@dataclass(frozen=True)
class SlayerMaster:
    id: str
    display_name: str
    family_ids: Tuple[str, ...]
    required_slayer_level: int = 1
    required_combat_level: int = 1
    required_quest_id: str = ""
    source: str = TURAEL_AUDIT_SOURCE


TURAEL_FAMILIES: Tuple[SlayerFamily, ...] = (
    SlayerFamily(
        "banshees",
        "Banshees",
        30,
        15,
        50,
        ("banshee",),
        required_slayer_level=15,
        required_quest_id="priest_in_peril",
    ),
    SlayerFamily("bats", "Bats", 10, 15, 50, ("giant_bat",)),
    SlayerFamily("bears", "Bears", 10, 15, 50, ("black_bear",)),
    SlayerFamily("birds", "Birds", 10, 15, 50, ("seagull",)),
    SlayerFamily(
        "cave_bugs",
        "Cave bugs",
        10,
        15,
        50,
        ("cave_bug",),
        required_slayer_level=7,
    ),
    SlayerFamily(
        "cave_slimes",
        "Cave slimes",
        30,
        15,
        50,
        ("cave_slime",),
        required_slayer_level=17,
    ),
    SlayerFamily("cows", "Cows", 10, 15, 50, ("cow", "cow_calf")),
    SlayerFamily(
        "crawling_hands",
        "Crawling hands",
        30,
        15,
        50,
        ("crawling_hand",),
        required_slayer_level=5,
    ),
    SlayerFamily(
        "desert_lizards",
        "Desert lizards",
        30,
        15,
        50,
        ("desert_lizard",),
        required_slayer_level=22,
    ),
    SlayerFamily("dogs", "Dogs", 15, 15, 50, ("jackal",)),
    SlayerFamily(
        "dwarves",
        "Dwarves",
        10,
        15,
        50,
        ("dwarf_level_10", "dwarf_level_11"),
    ),
    SlayerFamily("ghosts", "Ghosts", 15, 15, 50, ("ghost",)),
    SlayerFamily(
        "goblins",
        "Goblins",
        10,
        15,
        50,
        (
            "goblin_level_2_unarmed",
            "goblin_level_2_armed",
            "goblin_level_5",
            "goblin_level_11",
            "goblin_level_13",
            "goblin_level_16",
            "goblin_level_25",
        ),
    ),
    SlayerFamily(
        "gelatinous_abominations",
        "Gelatinous abominations",
        30,
        15,
        50,
        ("gelatinous_abomination",),
    ),
    SlayerFamily(
        "grotworms",
        "Grotworms",
        15,
        15,
        30,
        ("young_grotworm",),
    ),
    SlayerFamily("icefiends", "Icefiends", 10, 10, 20, ("icefiend",)),
    SlayerFamily(
        "minotaurs",
        "Minotaurs",
        10,
        15,
        50,
        ("minotaur_level_12", "minotaur_level_27"),
    ),
    SlayerFamily("monkeys", "Monkeys", 10, 15, 50, ("monkey",)),
    SlayerFamily("scorpions", "Scorpions", 10, 15, 50, ("scorpion",)),
    SlayerFamily(
        "skeletons",
        "Skeletons",
        15,
        15,
        50,
        (
            "skeleton_level_21",
            "skeleton_level_22",
            "skeleton_level_25",
            "skeleton_level_45",
            "skeleton_level_60",
            "skeleton_level_68",
            "skeleton_level_85",
        ),
    ),
    SlayerFamily(
        "spiders",
        "Spiders",
        10,
        15,
        50,
        ("spider", "giant_spider"),
    ),
    SlayerFamily(
        "wolves",
        "Wolves",
        15,
        15,
        50,
        ("wolf", "white_wolf_level_25", "white_wolf_level_38", "big_wolf"),
    ),
    SlayerFamily(
        "zombies",
        "Zombies",
        10,
        15,
        50,
        (
            "zombie_level_13",
            "zombie_level_18",
            "zombie_level_24",
            "zombie_level_25",
            "zombie_level_30",
            "zombie_level_44",
            "zombie_level_53",
        ),
    ),
)

SLAYER_FAMILIES_BY_ID: Dict[str, SlayerFamily] = {
    family.id: family for family in TURAEL_FAMILIES
}

TURAEL_MASTER = SlayerMaster(
    id="turael_spria",
    display_name="Turael",
    family_ids=tuple(family.id for family in TURAEL_FAMILIES),
)

SLAYER_MASTERS_BY_ID: Dict[str, SlayerMaster] = {
    TURAEL_MASTER.id: TURAEL_MASTER,
}

DEFAULT_SLAYER_MASTER_ID = TURAEL_MASTER.id
