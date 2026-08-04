"""Source-backed data for the pre-EOC Dungeoneering substrate.

This module contains the independently proven tables and the owner-approved
starter-expedition shape used by the live skill and its floor runtime.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Literal, Mapping, Optional


RoomFamily = Literal["start", "guardian", "key", "skill", "resource", "boss"]

SOURCE_REVISIONS: Mapping[str, tuple[int, str]] = MappingProxyType(
    {
        "dungeoneering": (6579699, "2012-11-19T02:31:37Z"),
        "floors": (6542025, "2012-11-08T00:49:39Z"),
        "prestige": (6516987, "2012-11-01T21:57:13Z"),
        "complexity": (6555542, "2012-11-14T19:37:17Z"),
        "kinship_classes": (6521933, "2012-11-03T01:29:00Z"),
        "coal_bag": (6283103, "2012-09-22T22:36:07Z"),
        "bosses": (6398065, "2012-10-14T01:46:52Z"),
        "doors": (6325508, "2012-09-30T17:22:57Z"),
        "skills": (4632782, "2011-08-15T21:54:34Z"),
        "fishing": (5812989, "2012-06-23T16:17:51Z"),
        "cooking": (6457563, "2012-10-23T01:30:20Z"),
        "herblore": (6555616, "2012-11-14T20:45:41Z"),
        "rewards": (6297239, "2012-09-25T21:01:33Z"),
        "smuggler": (6564954, "2012-11-17T04:36:56Z"),
    }
)

DUNGEONEERING_ACTIVITY_ID = "dungeoneering"
DUNGEONEERING_COMBAT_TARGET_ID = "dungeoneering_boss"
DUNGEONEERING_COMBAT_TICKS_PER_REVIEW = 6
DUNGEONEERING_STATE_VERSION = 3
DUNGEONEERING_MAX_LEVEL = 120
DUNGEONEERING_MAX_FLOOR = 60
COAL_BAG_CAPACITY = 27
DUNGEONEERING_ITEM_IMAGES: Mapping[str, str] = MappingProxyType(
    {
        "Ring of kinship": "activityitems/ring_of_kinship.png",
        "Coal bag": "activityitems/coal_bag.png",
    }
)
COLLECTED_BIND_LIMIT = 10
BIND_LOADOUT_COUNT = 3
AMMO_BIND_CAPACITY = 125
SALT_IN_THE_WOUND_AMMO_BIND_CAPACITY = 225
STARTER_SMALL_REVIEW_BUDGET = 8
STARTER_SMALL_GRAPH_ROOM_COUNT = 10
STARTER_ROOM_BUDGET_SOURCE_STATUS = "provisional/owner-approved-review-translation"
# AnkiScape starter translation: the period requirement generator is not sourced,
# so proof-floor skill doors use the universal minimum instead of copying the
# player's entry level and presenting that player-dependent value as historical.
STARTER_SKILL_DOOR_REQUIREMENT = 1
# PLACEHOLDER(dungeoneering.skill_door_failure): a period door handler that states both the failure roll and true-damage formula
SKILL_DOOR_FAILURE_CHANCE = 0.11
SKILL_DOOR_FAILURE_DAMAGE_MULTIPLIER = 4
# PLACEHOLDER(dungeoneering.smuggler_sellback_rate): rev-742 CS2/server shop logic or a dated guide stating the sell-back fraction
SMUGGLER_SELLBACK_RATE = 0.30


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

# Exact rev-727 and rev-742 NPC definition series: 9912-10057, excluding the
# two non-boss rows 10022-10023. Astea has three NPC forms at every level.
FROZEN_BOSS_COMBAT_LEVEL_LADDERS: Mapping[str, tuple[int, ...]] = MappingProxyType(
    {
        "gluttonous_behemoth": (5, 25, 41, 63, 91, 132, 170, 199, 238, 278, 299, 334, 362, 389, 437, 476, 518),
        "astea_frostweb": (3, 5, 8, 16, 26, 43, 71, 97, 116, 134, 155, 189, 221, 253, 287, 331, 378, 435, 496),
        "icy_bones": (5, 14, 23, 32, 41, 56, 71, 95, 124, 154, 188, 220, 258, 297, 340, 384, 429, 474),
        "luminescent_icefiend": (3, 7, 19, 40, 61, 77, 95, 124, 162, 197, 235, 274, 314, 362, 393, 423, 456),
        "plane_freezer_lakhrahnaz": (7, 17, 25, 35, 57, 76, 104, 140, 174, 203, 233, 262, 293, 329, 362, 393, 424, 455, 491),
        "tokash_bloodchiller": (8, 22, 49, 67, 104, 127, 159, 188, 216, 255, 292, 355, 408, 442, 477, 512),
    }
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


@dataclass(frozen=True)
class FrozenSkillDoor:
    id: str
    display_name: str
    skill_id: str
    frozen_object_id: int


FROZEN_SKILL_DOORS = (
    FrozenSkillDoor("runed_door", "Runed door", "runecrafting", 50278),
    FrozenSkillDoor("barred_door", "Barred door", "strength", 50272),
    FrozenSkillDoor("pile_of_rocks", "Pile of rocks", "mining", 50305),
    FrozenSkillDoor("flammable_debris", "Flammable debris", "firemaking", 50314),
    FrozenSkillDoor("magical_barrier", "Magical barrier", "magic", 50329),
    FrozenSkillDoor("dark_spirit", "Dark spirit", "prayer", 50332),
    FrozenSkillDoor("wooden_barricade", "Wooden barricade", "woodcutting", 50317),
    FrozenSkillDoor("broken_key_door", "Broken key door", "smithing", 50308),
    FrozenSkillDoor("broken_pulley_door", "Broken pulley door", "crafting", 50299),
)
FROZEN_SKILL_DOORS_BY_ID: Mapping[str, FrozenSkillDoor] = MappingProxyType(
    {door.id: door for door in FROZEN_SKILL_DOORS}
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
class SmugglerItem:
    id: str
    item_name: str
    source_item_id: int
    buy_price: int
    minimum_complexity: int
    equipment_slot: str = ""
    ammo_bind: bool = False


# Rev-727 and rev-742 enums 2987-2994 decode to the same item order.
# Prices are truncated cache value × the item's Dungeoneering multiplier.
SMUGGLER_ITEMS = (
    SmugglerItem("novite_ore", "Novite ore", 17630, 525, 3),
    SmugglerItem("bathus_ore", "Bathus ore", 17632, 1700, 3),
    SmugglerItem("marmaros_ore", "Marmaros ore", 17634, 4000, 3),
    SmugglerItem("kratonium_ore", "Kratonium ore", 17636, 6600, 5),
    SmugglerItem("fractite_ore", "Fractite ore", 17638, 12200, 5),
    SmugglerItem("zephyrium_ore", "Zephyrium ore", 17640, 17750, 5),
    SmugglerItem("argonite_ore", "Argonite ore", 17642, 26700, 5),
    SmugglerItem("katagon_ore", "Katagon ore", 17644, 35350, 5),
    SmugglerItem("gorgonite_ore", "Gorgonite ore", 17646, 57500, 5),
    SmugglerItem("promethium_ore", "Promethium ore", 17648, 102000, 5),
    SmugglerItem("salve_nettles", "Salve nettles", 17448, 420, 4),
    SmugglerItem("wildercress", "Wildercress", 17450, 1360, 4),
    SmugglerItem("blightleaf", "Blightleaf", 17452, 3200, 4),
    SmugglerItem("roseblood", "Roseblood", 17454, 5280, 5),
    SmugglerItem("bryll", "Bryll", 17456, 9760, 5),
    SmugglerItem("duskweed", "Duskweed", 17458, 14200, 5),
    SmugglerItem("soulbell", "Soulbell", 17460, 21360, 5),
    SmugglerItem("ectograss", "Ectograss", 17462, 28280, 5),
    SmugglerItem("runeleaf", "Runeleaf", 17464, 46000, 5),
    SmugglerItem("spiritbloom", "Spiritbloom", 17466, 81600, 5),
    SmugglerItem("protomastyx_hide", "Protomastyx hide", 17424, 420, 4),
    SmugglerItem("submastyx_hide", "Submastyx hide", 17426, 1360, 4),
    SmugglerItem("paramastyx_hide", "Paramastyx hide", 17428, 3200, 4),
    SmugglerItem("archaemastyx_hide", "Archaemastyx hide", 17430, 5280, 5),
    SmugglerItem("dromomastyx_hide", "Dromomastyx hide", 17432, 9760, 5),
    SmugglerItem("spinomastyx_hide", "Spinomastyx hide", 17434, 14200, 5),
    SmugglerItem("gallimastyx_hide", "Gallimastyx hide", 17436, 21360, 5),
    SmugglerItem("stegomastyx_hide", "Stegomastyx hide", 17438, 28280, 5),
    SmugglerItem("megamastyx_hide", "Megamastyx hide", 17440, 46000, 5),
    SmugglerItem("tyrannomastyx_hide", "Tyrannomastyx hide", 17442, 81600, 5),
    SmugglerItem("raw_heim_crab", "Raw heim crab", 17797, 200, 2),
    SmugglerItem("raw_red_eye", "Raw red-eye", 17799, 550, 3),
    SmugglerItem("raw_dusk_eel", "Raw dusk eel", 17801, 840, 3),
    SmugglerItem("raw_giant_flatfish", "Raw giant flatfish", 17803, 1400, 5),
    SmugglerItem("raw_short_finned_eel", "Raw short-finned eel", 17805, 1920, 5),
    SmugglerItem("raw_web_snipper", "Raw web snipper", 17807, 2700, 5),
    SmugglerItem("raw_bouldabass", "Raw bouldabass", 17809, 3400, 5),
    SmugglerItem("raw_salve_eel", "Raw salve eel", 17811, 4500, 5),
    SmugglerItem("raw_blue_crab", "Raw blue crab", 17813, 5500, 5),
    SmugglerItem("raw_cave_moray", "Raw cave moray", 17815, 7500, 5),
    SmugglerItem("tangle_gum_branches", "Tangle gum branches", 17682, 225, 2),
    SmugglerItem("seeping_elm_branches", "Seeping elm branches", 17684, 600, 3),
    SmugglerItem("blood_spindle_branches", "Blood spindle branches", 17686, 1650, 3),
    SmugglerItem("utuku_branches", "Utuku branches", 17688, 3750, 5),
    SmugglerItem("spinebeam_branches", "Spinebeam branches", 17690, 7875, 5),
    SmugglerItem("bovistrangler_branches", "Bovistrangler branches", 17692, 12500, 5),
    SmugglerItem("thigat_branches", "Thigat branches", 17694, 22500, 5),
    SmugglerItem("corpsethorn_branches", "Corpsethorn branches", 17696, 35000, 5),
    SmugglerItem("entgallow_branches", "Entgallow branches", 17698, 60000, 5),
    SmugglerItem("grave_creeper_branches", "Grave creeper branches", 17700, 117500, 5),
    SmugglerItem("sagewort_seed", "Sagewort seed", 17826, 2250, 5),
    SmugglerItem("valerian_seed", "Valerian seed", 17827, 3000, 5),
    SmugglerItem("aloe_seed", "Aloe seed", 17828, 4050, 5),
    SmugglerItem("wormwood_seed", "Wormwood seed", 17829, 4500, 5),
    SmugglerItem("magebane_seed", "Magebane seed", 17830, 6000, 5),
    SmugglerItem("featherfoil_seed", "Featherfoil seed", 17831, 8100, 5),
    SmugglerItem("winters_grip_seed", "Winter's grip seed", 17832, 9000, 5),
    SmugglerItem("lycopus_seed", "Lycopus seed", 17833, 10500, 5),
    SmugglerItem("buckthorn_seed", "Buckthorn seed", 17834, 13500, 5),
    SmugglerItem("cave_potato_seed", "Cave potato seed", 17823, 540, 5),
    SmugglerItem("gissel_mushroom_spore", "Gissel mushroom spore", 17824, 900, 5),
    SmugglerItem("edicap_mushroom_spore", "Edicap mushroom spore", 17825, 3000, 5),
    SmugglerItem("rune_essence", "Rune essence", 17776, 50, 3),
    SmugglerItem("novite_arrows", "Novite arrows", 16427, 40, 3, ammo_bind=True),
    SmugglerItem("bathus_arrows", "Bathus arrows", 16432, 96, 5, ammo_bind=True),
    SmugglerItem("marmaros_arrows", "Marmaros arrows", 16437, 182, 5, ammo_bind=True),
    SmugglerItem("kratonite_arrows", "Kratonite arrows", 16442, 289, 5, ammo_bind=True),
    SmugglerItem("fractite_arrows", "Fractite arrows", 16447, 440, 5, ammo_bind=True),
    SmugglerItem("void_dust", "Void dust", 17530, 1000, 5),
    SmugglerItem("firebreath_whiskey", "Firebreath whiskey", 17536, 1000, 5),
    SmugglerItem("red_moss", "Red moss", 17534, 1000, 5),
    SmugglerItem("misshapen_claw", "Misshapen claw", 17532, 1000, 5),
    SmugglerItem("tangle_gum_shortbow", "Tangle gum shortbow", 16867, 687, 3, "weapon"),
    SmugglerItem("tangle_gum_longbow", "Tangle gum longbow", 16317, 562, 3, "weapon"),
    SmugglerItem("tangle_gum_staff", "Tangle gum staff", 16977, 612, 3, "weapon"),
    SmugglerItem("novite_rapier", "Novite rapier", 16935, 875, 3, "weapon"),
    SmugglerItem("novite_kiteshield", "Novite kiteshield", 17341, 1312, 3, "shield"),
    SmugglerItem("bathus_pickaxe", "Bathus pickaxe", 16297, 1062, 5, "weapon"),
    SmugglerItem("marmaros_pickaxe", "Marmaros pickaxe", 16299, 2000, 5, "weapon"),
    SmugglerItem("bathus_hatchet", "Bathus hatchet", 16363, 1062, 5, "weapon"),
    SmugglerItem("marmaros_hatchet", "Marmaros hatchet", 16365, 2000, 5, "weapon"),
    SmugglerItem("bow_string", "Bow string", 17752, 60, 3),
    SmugglerItem("thread", "Thread", 17447, 10, 4),
    SmugglerItem("vial", "Vial", 17490, 10, 5),
    SmugglerItem("feather", "Feather", 17796, 6, 2),
    SmugglerItem("antipoison", "Antipoison", 17566, 200, 2),
)
SMUGGLER_ITEMS_BY_ID: Mapping[str, SmugglerItem] = MappingProxyType(
    {item.id: item for item in SMUGGLER_ITEMS}
)
SMUGGLER_ITEMS_BY_SOURCE_ID: Mapping[int, SmugglerItem] = MappingProxyType(
    {item.source_item_id: item for item in SMUGGLER_ITEMS}
)


@dataclass(frozen=True)
class SmugglerStockBand:
    complexity: int
    enum_ids: tuple[int, ...]
    source_item_ids: tuple[int, ...]

    @property
    def source_row_count(self) -> int:
        return len(self.source_item_ids)

    @property
    def item_ids(self) -> tuple[str, ...]:
        return tuple(
            SMUGGLER_ITEMS_BY_SOURCE_ID[item_id].id
            for item_id in self.source_item_ids
        )


_C2_SMUGGLER_SOURCE_IDS = (17797, 17682, 17796, 17566)
_C3_SMUGGLER_SOURCE_IDS = (
    17630, 17632, 17634, 17797, 17799, 17801, 17682, 17684, 17686,
    17776, 16867, 16317, 16977, 16935, 17341, 16427, 17752, 17796, 17566,
)
_C4_SMUGGLER_SOURCE_IDS = (
    17630, 17632, 17634, 17448, 17450, 17452, 17424, 17426, 17428,
    17797, 17799, 17801, 17682, 17684, 17686, 17776, 16427, 16867,
    16317, 16977, 16935, 17341, 17752, 17447, 17796, 17566,
)
_C5_SMUGGLER_SOURCE_IDS = tuple(item.source_item_id for item in SMUGGLER_ITEMS)
SMUGGLER_STOCK_BANDS: Mapping[int, SmugglerStockBand] = MappingProxyType(
    {
        1: SmugglerStockBand(1, (), ()),
        2: SmugglerStockBand(2, (2989, 2990), _C2_SMUGGLER_SOURCE_IDS),
        3: SmugglerStockBand(3, (2991, 2992), _C3_SMUGGLER_SOURCE_IDS),
        4: SmugglerStockBand(4, (2993, 2994), _C4_SMUGGLER_SOURCE_IDS),
        5: SmugglerStockBand(5, (2987, 2988), _C5_SMUGGLER_SOURCE_IDS),
        6: SmugglerStockBand(6, (2987, 2988), _C5_SMUGGLER_SOURCE_IDS),
    }
)


@dataclass(frozen=True)
class DungeoneeringReward:
    id: str
    display_name: str
    token_cost: int
    dungeoneering_level: int
    other_skill_requirements: tuple[tuple[str, int], ...] = ()
    source_item_id: Optional[int] = None
    fully_functional: bool = False
    notes: str = "Catalogued only; its mechanic is not implemented yet."


DUNGEONEERING_REWARDS = (
    DungeoneeringReward("dungeoneering_xp_lamp", "Dungeoneering XP lamp", 1, 0),
    DungeoneeringReward("gem_bag", "Gem bag", 2000, 25),
    DungeoneeringReward(
        "coal_bag",
        "Coal bag",
        4000,
        35,
        (("Mining", 35),),
        18339,
        True,
        "One owned; holds 27 Coal; manual Bank/carried fill; smelting consumes bag Coal first.",
    ),
    DungeoneeringReward("arcane_pulse_necklace", "Arcane pulse necklace", 6500, 30),
    DungeoneeringReward("twisted_bird_skull_necklace", "Twisted bird skull necklace", 8500, 30),
    DungeoneeringReward("scroll_of_life", "Scroll of life", 10000, 25),
    DungeoneeringReward("longbow_sight", "Longbow sight", 10000, 45),
    DungeoneeringReward("law_staff", "Law staff", 10000, 45, (("Magic", 45),)),
    DungeoneeringReward("nature_staff", "Nature staff", 12500, 53, (("Magic", 53),)),
    DungeoneeringReward("arcane_blast_necklace", "Arcane blast necklace", 15500, 50),
    DungeoneeringReward("split_dragontooth_necklace", "Split dragontooth necklace", 17000, 60),
    DungeoneeringReward("scroll_of_cleansing", "Scroll of cleansing", 20000, 49),
    DungeoneeringReward("scroll_of_efficiency", "Scroll of efficiency", 20000, 55),
    DungeoneeringReward("arcane_stream_necklace", "Arcane stream necklace", 30500, 70),
    DungeoneeringReward("bonecrusher", "Bonecrusher", 34000, 21),
    DungeoneeringReward("herbicide", "Herbicide", 34000, 21),
    DungeoneeringReward("demon_horn_necklace", "Demon horn necklace", 35000, 90),
    DungeoneeringReward("amulet_of_zealots", "Amulet of zealots", 40000, 48),
    DungeoneeringReward("gravite_rapier", "Gravite rapier", 40000, 45),
    DungeoneeringReward("gravite_longsword", "Gravite longsword", 40000, 45),
    DungeoneeringReward("gravite_two_handed_sword", "Gravite two-handed sword", 40000, 45),
    DungeoneeringReward("gravite_staff", "Gravite staff", 40000, 45),
    DungeoneeringReward("gravite_shortbow", "Gravite shortbow", 40000, 45),
    DungeoneeringReward(
        "magical_blastbox",
        "Magical blastbox",
        40000,
        30,
        (("Magic", 30), ("Runecrafting", 30)),
    ),
    DungeoneeringReward("tome_of_frost", "Tome of frost", 43000, 48),
    DungeoneeringReward("anti_poison_totem", "Anti-poison totem", 44000, 60),
    DungeoneeringReward("spirit_cape", "Spirit cape", 45000, 50),
    DungeoneeringReward("mercenarys_gloves", "Mercenary's gloves", 48500, 73),
    DungeoneeringReward("ring_of_vigour", "Ring of vigour", 50000, 62),
    DungeoneeringReward(
        "celestial_surgebox",
        "Celestial surgebox",
        65000,
        70,
        (("Magic", 70), ("Runecrafting", 70)),
    ),
    DungeoneeringReward("sneakerpeeper", "Sneakerpeeper", 85000, 80),
    DungeoneeringReward("scroll_of_renewal", "Scroll of renewal", 107000, 65),
    DungeoneeringReward("scroll_of_rigour", "Scroll of rigour", 140000, 74),
    DungeoneeringReward("scroll_of_augury", "Scroll of augury", 153000, 77),
    DungeoneeringReward("chaotic_rapier", "Chaotic rapier", 200000, 80),
    DungeoneeringReward("chaotic_longsword", "Chaotic longsword", 200000, 80),
    DungeoneeringReward("chaotic_maul", "Chaotic maul", 200000, 80),
    DungeoneeringReward("chaotic_staff", "Chaotic staff", 200000, 80),
    DungeoneeringReward("chaotic_crossbow", "Chaotic crossbow", 200000, 80),
    DungeoneeringReward("chaotic_kiteshield", "Chaotic kiteshield", 200000, 80),
    DungeoneeringReward("eagle_eye_kiteshield", "Eagle-eye kiteshield", 200000, 80),
    DungeoneeringReward("farseer_kiteshield", "Farseer kiteshield", 200000, 80),
)
DUNGEONEERING_REWARDS_BY_ID: Mapping[str, DungeoneeringReward] = MappingProxyType(
    {reward.id: reward for reward in DUNGEONEERING_REWARDS}
)
COAL_BAG_REWARD = DUNGEONEERING_REWARDS_BY_ID["coal_bag"]

RING_OF_KINSHIP_ITEM_ID = 15707
RING_OF_KINSHIP_CLASS_ITEM_IDS: Mapping[str, int] = MappingProxyType(
    {
        kinship_class.id: 18817 + index
        for index, kinship_class in enumerate(KINSHIP_CLASSES)
    }
)


def dungeoneering_extra_items_as_dict() -> dict[str, dict[str, object]]:
    return {
        "Ring of kinship": {
            "category": "tool",
            "source_item_id": RING_OF_KINSHIP_ITEM_ID,
            "stackable": False,
            "tradeable": False,
            "source": "period/wiki-oldid-6521933",
        },
        "Coal bag": {
            "category": "tool",
            "source_item_id": COAL_BAG_REWARD.source_item_id,
            "stackable": False,
            "tradeable": False,
            "source": "period/wiki-oldid-6283103",
        },
    }
