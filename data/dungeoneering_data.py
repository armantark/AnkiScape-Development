"""Source-backed data for the pre-EOC Dungeoneering substrate.

The live Skills surface remains parked until the floor-XP curve and death
coefficient are source-closed.  This module contains the independently proven
tables and the owner-approved starter-expedition shape so later runtime work
does not have to rediscover them.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping


RoomFamily = Literal["start", "guardian", "key", "skill", "resource", "boss"]

SOURCE_REVISIONS: Mapping[str, tuple[int, str]] = MappingProxyType(
    {
        "dungeoneering": (6579699, "2012-11-19T02:31:37Z"),
        "floors": (6542025, "2012-11-08T00:49:39Z"),
        "prestige": (6516987, "2012-11-01T21:57:13Z"),
        "complexity": (6555542, "2012-11-14T19:37:17Z"),
        "kinship_classes": (6190515, "2012-09-03T19:30:40Z"),
        "coal_bag": (6283103, "2012-09-22T22:36:07Z"),
        "bosses": (6398065, "2012-10-14T01:46:52Z"),
        "doors": (6325508, "2012-09-30T17:22:57Z"),
        "skills": (4632782, "2011-08-15T21:54:34Z"),
        "fishing": (5812989, "2012-06-23T16:17:51Z"),
        "cooking": (6457563, "2012-10-23T01:30:20Z"),
        "herblore": (6555616, "2012-11-14T20:45:41Z"),
        "rewards": (6297239, "2012-09-25T21:01:33Z"),
    }
)

DUNGEONEERING_MAX_LEVEL = 120
DUNGEONEERING_MAX_FLOOR = 60
COLLECTED_BIND_LIMIT = 10
BIND_LOADOUT_COUNT = 3
AMMO_BIND_CAPACITY = 125
SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY = 225
STARTER_SMALL_ROOM_BUDGET = 8
STARTER_ROOM_BUDGET_SOURCE_STATUS = "provisional/owner-approved-review-translation"


@dataclass(frozen=True)
class FloorTheme:
    id: str
    display_name: str
    first_floor: int
    last_floor: int
    minimum_level: int
    maximum_level: int
    members_only: bool


FLOOR_THEMES = (
    FloorTheme("frozen", "Frozen", 1, 11, 1, 21, False),
    FloorTheme("abandoned_i", "Abandoned I", 12, 17, 23, 33, False),
    FloorTheme("furnished", "Furnished", 18, 29, 35, 57, False),
    FloorTheme("abandoned_ii", "Abandoned II", 30, 35, 59, 69, False),
    FloorTheme("occult", "Occult", 36, 47, 71, 93, True),
    FloorTheme("warped", "Warped", 48, 60, 95, 119, True),
)
FLOOR_THEMES_BY_ID: Mapping[str, FloorTheme] = MappingProxyType(
    {theme.id: theme for theme in FLOOR_THEMES}
)


@dataclass(frozen=True)
class FloorSize:
    id: str
    display_name: str
    grid_width: int
    grid_height: int
    maximum_rooms: int
    minimum_party_size: int


FLOOR_SIZES = (
    FloorSize("small", "Small", 4, 4, 16, 1),
    FloorSize("medium", "Medium", 4, 8, 32, 1),
    FloorSize("large", "Large", 8, 8, 64, 3),
)
FLOOR_SIZES_BY_ID: Mapping[str, FloorSize] = MappingProxyType(
    {size.id: size for size in FLOOR_SIZES}
)


@dataclass(frozen=True)
class Complexity:
    level: int
    xp_penalty_percent: int
    enabled_skills: tuple[str, ...]
    skill_doors: bool
    forced_guide_mode: bool


_COMBAT_SKILLS = (
    "Attack",
    "Constitution",
    "Defence",
    "Magic",
    "Prayer",
    "Ranged",
    "Strength",
)
_C2_SKILLS = _COMBAT_SKILLS + (
    "Cooking",
    "Firemaking",
    "Fishing",
    "Woodcutting",
)
_C3_SKILLS = _C2_SKILLS + ("Mining", "Runecrafting", "Smithing")
_C4_SKILLS = _C3_SKILLS + ("Farming textiles", "Hunter", "Smithing armour")
_C5_SKILLS = _C4_SKILLS + (
    "Construction",
    "Farming seeds",
    "Herblore",
    "Summoning",
    "Thieving",
)

COMPLEXITIES = (
    Complexity(1, 50, _COMBAT_SKILLS, False, True),
    Complexity(2, 45, _C2_SKILLS, False, False),
    Complexity(3, 40, _C3_SKILLS, False, False),
    Complexity(4, 35, _C4_SKILLS, False, False),
    Complexity(5, 30, _C5_SKILLS, True, False),
    Complexity(6, 0, _C5_SKILLS, True, False),
)
COMPLEXITIES_BY_LEVEL: Mapping[int, Complexity] = MappingProxyType(
    {complexity.level: complexity for complexity in COMPLEXITIES}
)

BIND_SLOTS_BY_LEVEL = (
    (1, 1),
    (20, 2),
    (50, 3),
    (90, 4),
    (120, 5),
)


@dataclass(frozen=True)
class KinshipClass:
    id: str
    display_name: str
    category: str
    effect: str
    tier_values_percent: tuple[int, ...]


_STANDARD_11_TO_20 = tuple(range(11, 21))
_STANDARD_20_TO_50 = (20, 23, 27, 30, 33, 37, 40, 43, 47, 50)

KINSHIP_TIER_COSTS = (135, 175, 335, 660, 1360, 3400, 6800, 18750, 58600, 233000)
KINSHIP_CLASSES = (
    KinshipClass("tank", "Tank", "Melee", "Shield damage reduction", tuple(range(6, 16))),
    KinshipClass("tactician", "Tactician", "Melee", "Accurate-stance hit chance", _STANDARD_11_TO_20),
    KinshipClass("berserker", "Berserker", "Melee", "Aggressive-stance Strength level", _STANDARD_11_TO_20),
    KinshipClass("sniper", "Sniper", "Ranged", "Longrange maximum-hit chance", _STANDARD_20_TO_50),
    KinshipClass("keen_eye", "Keen-eye", "Ranged", "Accurate-stance Defence reduction chance", (40, 47, 53, 60, 67, 73, 80, 87, 93, 100)),
    KinshipClass("desperado", "Desperado", "Ranged", "Rapid-stance Ranged level", _STANDARD_11_TO_20),
    KinshipClass("blazer", "Blazer", "Magic", "Elemental damage-over-time chance", tuple(range(5, 51, 5))),
    KinshipClass("blaster", "Blaster", "Magic", "Elemental slow/snare chance", tuple(range(12, 31, 2))),
    KinshipClass("blitzer", "Blitzer", "Magic", "Faster elemental-cast chance", tuple(range(10, 101, 10))),
    KinshipClass("medic", "Medic", "Skiller", "Extra health healed to another player", _STANDARD_20_TO_50),
    KinshipClass("gatherer", "Gatherer", "Skiller", "Extra-resource chance and failed-task damage reduction", _STANDARD_20_TO_50),
    KinshipClass("artisan", "Artisan", "Skiller", "Resource-save chance and failed-task damage reduction", _STANDARD_20_TO_50),
)
KINSHIP_CLASSES_BY_ID: Mapping[str, KinshipClass] = MappingProxyType(
    {kinship_class.id: kinship_class for kinship_class in KINSHIP_CLASSES}
)


@dataclass(frozen=True)
class FrozenBoss:
    id: str
    display_name: str
    minimum_level: int
    first_floor: int
    last_floor: int = 11


FROZEN_BOSSES = (
    FrozenBoss("gluttonous_behemoth", "Gluttonous Behemoth", 1, 1),
    FrozenBoss("astea_frostweb", "Astea Frostweb", 1, 1),
    FrozenBoss("icy_bones", "Icy Bones", 1, 1),
    FrozenBoss("luminescent_icefiend", "Luminescent icefiend", 5, 3),
    FrozenBoss("plane_freezer_lakhrahnaz", "Plane-freezer Lakhrahnaz", 11, 6),
    FrozenBoss("tokash_bloodchiller", "To'Kash the Bloodchiller", 17, 9),
)
FROZEN_BOSSES_BY_ID: Mapping[str, FrozenBoss] = MappingProxyType(
    {boss.id: boss for boss in FROZEN_BOSSES}
)


@dataclass(frozen=True)
class DoorFamily:
    id: str
    display_name: str
    requirement: str
    xp_multiplier: int = 0
    failure_consequence_status: str = "not_applicable"


DOOR_FAMILIES = (
    DoorFamily("basic", "Basic door", "Open"),
    DoorFamily("guardian", "Guardian door", "Defeat every required monster"),
    DoorFamily("key", "Key door", "Use the matching shared key"),
    DoorFamily(
        "skill",
        "Skill door",
        "Meet and perform the door's skill requirement",
        xp_multiplier=5,
        failure_consequence_status="source_blocked/moderate-to-severe-damage",
    ),
)
DOOR_FAMILIES_BY_ID: Mapping[str, DoorFamily] = MappingProxyType(
    {door.id: door for door in DOOR_FAMILIES}
)

STARTER_ROOM_FAMILIES: tuple[RoomFamily, ...] = (
    "start",
    "guardian",
    "key",
    "skill",
    "resource",
    "boss",
)


@dataclass(frozen=True)
class StarterChainStep:
    id: str
    display_name: str
    skill: str
    level: int
    xp: float
    inputs: tuple[tuple[str, int], ...]
    output: tuple[str, int]
    minimum_complexity: int
    source_status: str
    existing_target_id: str = ""


STARTER_RESOURCE_CHAIN = (
    StarterChainStep(
        "catch_heim_crab",
        "Catch Raw heim crab",
        "Fishing",
        1,
        9.0,
        (),
        ("Raw heim crab", 1),
        2,
        "period/wiki-oldid-5812989",
    ),
    StarterChainStep(
        "cook_heim_crab",
        "Cook Heim crab",
        "Cooking",
        1,
        22.0,
        (("Raw heim crab", 1),),
        ("Heim crab", 1),
        2,
        "period/wiki-oldid-6457563",
    ),
)

STARTER_HERBLORE_CHAIN = (
    StarterChainStep(
        "clean_valerian",
        "Clean valerian",
        "Herblore",
        4,
        3.2,
        (("Grimy valerian", 1),),
        ("Clean valerian", 1),
        5,
        "period/wiki-oldid-6555616",
        "clean_valerian",
    ),
    StarterChainStep(
        "mix_valerian_unfinished",
        "Mix Valerian potion (unf)",
        "Herblore",
        4,
        0.0,
        (("Clean valerian", 1), ("Vial of water", 1)),
        ("Valerian potion (unf)", 1),
        5,
        "reconciled/game-main-plus-period-ingredients",
        "unf_valerian",
    ),
    StarterChainStep(
        "mix_weak_ranged",
        "Mix Weak ranged potion",
        "Herblore",
        5,
        34.0,
        (("Valerian potion (unf)", 1), ("Void dust", 1)),
        ("Weak ranged potion", 1),
        5,
        "period/wiki-oldid-6555616",
        "finished_weak_ranged",
    ),
)


@dataclass(frozen=True)
class DungeoneeringReward:
    id: str
    display_name: str
    token_cost: int
    dungeoneering_level: int
    other_skill_requirements: tuple[tuple[str, int], ...]
    source_item_id: int
    fully_functional: bool
    notes: str


COAL_BAG_REWARD = DungeoneeringReward(
    "coal_bag",
    "Coal bag",
    4000,
    35,
    (("Mining", 35),),
    18339,
    True,
    "One owned; holds 27 Coal; manual/bank fill; smelting consumes bag Coal first.",
)

RING_OF_KINSHIP_ITEM_ID = 15707
RING_OF_KINSHIP_CLASS_ITEM_IDS: Mapping[str, int] = MappingProxyType(
    {
        kinship_class.id: 18817 + index
        for index, kinship_class in enumerate(KINSHIP_CLASSES)
    }
)

