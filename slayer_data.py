"""Source-backed Slayer family identities and master-specific assignment rows.

Only certified masters are runtime-enabled. Hidden master pools remain complete
data contracts so readiness can be derived from live Combat dependencies rather
than maintained as a stale prose checklist.
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
MAZCHNA_AUDIT_SOURCE = (
    "memory-bank/source-audits/slayer-mazchna-achtryn-pool-2026-07-17.md"
)
VANNAKA_AUDIT_SOURCE = (
    "memory-bank/source-audits/slayer-vannaka-pool-2026-07-17.md"
)
CHAELDAR_AUDIT_SOURCE = (
    "memory-bank/source-audits/slayer-chaeldar-pool-2026-07-17.md"
)
SUMONA_AUDIT_SOURCE = (
    "memory-bank/source-audits/slayer-sumona-pool-2026-07-17.md"
)


@dataclass(frozen=True)
class SlayerFamily:
    """Stable family identity shared by every master that assigns it."""

    id: str
    display_name: str
    target_ids: Tuple[str, ...]
    required_slayer_level: int = 1
    required_quest_id: str = ""
    required_skill_levels: Tuple[Tuple[str, int], ...] = ()
    required_skill_totals: Tuple[Tuple[Tuple[str, ...], int], ...] = ()
    readiness_features: Tuple[str, ...] = ()
    source: str = TURAEL_AUDIT_SOURCE


@dataclass(frozen=True)
class SlayerMasterFamilyRow:
    """A family's weight and count range for one specific master."""

    family_id: str
    weight: int
    count_min: int
    count_max: int
    source: str


@dataclass(frozen=True)
class SlayerAssignmentFamily:
    """Runtime view combining a stable family with one master's roll row."""

    family: SlayerFamily
    row: SlayerMasterFamilyRow

    @property
    def id(self) -> str:
        return self.family.id

    @property
    def display_name(self) -> str:
        return self.family.display_name

    @property
    def target_ids(self) -> Tuple[str, ...]:
        return self.family.target_ids

    @property
    def required_slayer_level(self) -> int:
        return self.family.required_slayer_level

    @property
    def required_quest_id(self) -> str:
        return self.family.required_quest_id

    @property
    def required_skill_levels(self) -> Tuple[Tuple[str, int], ...]:
        return self.family.required_skill_levels

    @property
    def required_skill_totals(self) -> Tuple[Tuple[Tuple[str, ...], int], ...]:
        return self.family.required_skill_totals

    @property
    def readiness_features(self) -> Tuple[str, ...]:
        return self.family.readiness_features

    @property
    def weight(self) -> int:
        return self.row.weight

    @property
    def count_min(self) -> int:
        return self.row.count_min

    @property
    def count_max(self) -> int:
        return self.row.count_max

    @property
    def source(self) -> str:
        return self.row.source


@dataclass(frozen=True)
class SlayerMaster:
    id: str
    display_name: str
    assignments: Tuple[SlayerAssignmentFamily, ...]
    required_slayer_level: int = 1
    required_combat_level: int = 1
    required_quest_id: str = ""
    runtime_enabled: bool = False
    alternate_display_name: str = ""
    alternate_display_condition: str = ""
    expected_weight_total: int = 0
    source: str = TURAEL_AUDIT_SOURCE

    @property
    def family_ids(self) -> Tuple[str, ...]:
        return tuple(assignment.id for assignment in self.assignments)


_FAMILIES: Tuple[SlayerFamily, ...] = (
    SlayerFamily(
        "banshees",
        "Banshees",
        ("banshee",),
        required_slayer_level=15,
        required_quest_id="priest_in_peril",
        readiness_features=("protective_equipment",),
    ),
    SlayerFamily("bats", "Bats", ("giant_bat",)),
    SlayerFamily("bears", "Bears", ("black_bear",)),
    SlayerFamily("birds", "Birds", ("seagull",)),
    SlayerFamily("cave_bugs", "Cave bugs", ("cave_bug",), required_slayer_level=7),
    SlayerFamily(
        "cave_crawlers",
        "Cave crawlers",
        ("cave_crawler",),
        required_slayer_level=10,
        readiness_features=("poison_damage",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "cave_slimes",
        "Cave slimes",
        ("cave_slime",),
        required_slayer_level=17,
        readiness_features=("poison_damage",),
    ),
    SlayerFamily(
        "catablepon",
        "Catablepon",
        ("catablepon_level_49", "catablepon_level_64", "catablepon_level_68"),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "cockatrice",
        "Cockatrice",
        ("cockatrice",),
        required_slayer_level=25,
        readiness_features=("protective_equipment",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily("cows", "Cows", ("cow", "cow_calf")),
    SlayerFamily(
        "crawling_hands",
        "Crawling hands",
        ("crawling_hand",),
        required_slayer_level=5,
    ),
    SlayerFamily(
        "cyclopes",
        "Cyclopes",
        ("cyclops", "cyclossus"),
        required_skill_totals=((("attack", "strength"), 130),),
        readiness_features=("warriors_guild_gate",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "desert_lizards",
        "Desert lizards",
        ("desert_lizard",),
        required_slayer_level=22,
        readiness_features=("finisher",),
    ),
    SlayerFamily("dogs", "Dogs", ("jackal",)),
    SlayerFamily("dwarves", "Dwarves", ("dwarf_level_10", "dwarf_level_11")),
    SlayerFamily(
        "flesh_crawlers",
        "Flesh crawlers",
        ("flesh_crawler_level_28", "flesh_crawler_level_35", "flesh_crawler_level_41"),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily("ghosts", "Ghosts", ("ghost",)),
    SlayerFamily("ghouls", "Ghouls", ("ghoul",), source=MAZCHNA_AUDIT_SOURCE),
    SlayerFamily(
        "gelatinous_abominations",
        "Gelatinous abominations",
        ("gelatinous_abomination",),
    ),
    SlayerFamily(
        "goblins",
        "Goblins",
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
    SlayerFamily("grotworms", "Grotworms", ("young_grotworm",)),
    SlayerFamily(
        "hill_giants",
        "Hill giants",
        ("hill_giant",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "hobgoblins",
        "Hobgoblins",
        ("hobgoblin_unarmed", "hobgoblin_armed"),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "ice_warriors",
        "Ice warriors",
        ("ice_warrior",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily("icefiends", "Icefiends", ("icefiend",)),
    SlayerFamily(
        "kalphites",
        "Kalphites",
        ("kalphite_soldier",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "minotaurs",
        "Minotaurs",
        ("minotaur_level_12", "minotaur_level_27"),
    ),
    SlayerFamily(
        "mogres",
        "Mogres",
        ("mogre",),
        required_slayer_level=32,
        required_quest_id="skippy_and_the_mogres",
        readiness_features=("lure",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily("monkeys", "Monkeys", ("monkey",)),
    SlayerFamily(
        "pyrefiends",
        "Pyrefiends",
        ("pyrefiend",),
        required_slayer_level=30,
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "rock_slugs",
        "Rock slugs",
        ("rockslug",),
        required_slayer_level=20,
        readiness_features=("finisher",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily("scorpions", "Scorpions", ("scorpion",)),
    SlayerFamily(
        "skeletons",
        "Skeletons",
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
    SlayerFamily("spiders", "Spiders", ("spider", "giant_spider")),
    SlayerFamily(
        "vampyres",
        "Vampyres",
        ("vampyre",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "wall_beasts",
        "Wall beasts",
        ("wall_beast",),
        required_slayer_level=35,
        required_skill_levels=(("defence", 5),),
        readiness_features=("start_equipment",),
        source=MAZCHNA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "wolves",
        "Wolves",
        ("wolf", "white_wolf_level_25", "white_wolf_level_38", "big_wolf"),
    ),
    SlayerFamily(
        "zombies",
        "Zombies",
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
    SlayerFamily(
        "aberrant_spectres",
        "Aberrant spectres",
        ("aberrant_spectre",),
        required_slayer_level=60,
        required_quest_id="priest_in_peril",
        readiness_features=("protective_equipment",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "ankou",
        "Ankou",
        ("ankou_level_75", "ankou_level_82", "ankou_level_86"),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "basilisks",
        "Basilisks",
        ("basilisk",),
        required_slayer_level=40,
        required_skill_levels=(("defence", 20),),
        readiness_features=("protective_equipment",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "bloodveld",
        "Bloodveld",
        ("bloodveld",),
        required_slayer_level=50,
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "brine_rats",
        "Brine rats",
        ("brine_rat",),
        required_slayer_level=47,
        readiness_features=("partial_quest_access",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "crocodiles",
        "Crocodiles",
        ("crocodile",),
        readiness_features=("desert_context",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "dust_devils",
        "Dust devils",
        ("dust_devil",),
        required_slayer_level=65,
        readiness_features=("start_equipment",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "earth_warriors",
        "Earth warriors",
        ("earth_warrior",),
        readiness_features=("wilderness_risk",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "green_dragons",
        "Green dragons",
        ("green_dragon",),
        readiness_features=("dragonfire", "wilderness_risk"),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "harpie_bug_swarms",
        "Harpie bug swarms",
        ("harpie_bug_swarm",),
        required_slayer_level=33,
        readiness_features=("start_equipment",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "ice_giants",
        "Ice giants",
        ("ice_giant",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "infernal_mages",
        "Infernal mages",
        ("infernal_mage",),
        required_slayer_level=45,
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "jellies",
        "Jellies",
        ("jelly",),
        required_slayer_level=52,
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "jungle_horrors",
        "Jungle horrors",
        ("jungle_horror",),
        required_quest_id="cabin_fever",
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "killerwatts",
        "Killerwatts",
        ("killerwatt",),
        required_slayer_level=37,
        required_quest_id="ernest_the_chicken",
        readiness_features=("protective_equipment",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "lesser_demons",
        "Lesser demons",
        ("lesser_demon",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "molanisks",
        "Molanisks",
        ("molanisk",),
        required_slayer_level=39,
        required_quest_id="death_to_the_dorgeshuun",
        readiness_features=("lure", "light_source"),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "moss_giants",
        "Moss giants",
        ("moss_giant",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "ogres",
        "Ogres",
        ("ogre",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "otherworldly_beings",
        "Otherworldly beings",
        ("otherworldly_being",),
        required_quest_id="lost_city",
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "sea_snakes",
        "Sea snakes",
        ("sea_snake_hatchling", "sea_snake_young"),
        required_quest_id="royal_trouble",
        readiness_features=("poison_damage",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "shades",
        "Shades",
        ("shade",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "shadow_warriors",
        "Shadow warriors",
        ("shadow_warrior",),
        required_quest_id="legends_quest",
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "turoth",
        "Turoth",
        ("turoth",),
        required_slayer_level=55,
        readiness_features=("restricted_weapon",),
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "werewolves",
        "Werewolves",
        ("werewolf",),
        required_quest_id="priest_in_peril",
        source=VANNAKA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "blue_dragons",
        "Blue dragons",
        ("blue_dragon", "baby_blue_dragon"),
        readiness_features=("dragonfire",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "bronze_dragons",
        "Bronze dragons",
        ("bronze_dragon",),
        readiness_features=("dragonfire",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "cave_horrors",
        "Cave horrors",
        ("cave_horror",),
        required_slayer_level=58,
        required_quest_id="cabin_fever",
        readiness_features=("light_source", "protective_equipment"),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "dagannoths",
        "Dagannoths",
        ("dagannoth", "dagannoth_level_92"),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "elves",
        "Elves",
        ("elf_warrior", "elf_warrior_level_108"),
        required_quest_id="regicide",
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "fever_spiders",
        "Fever spiders",
        ("fever_spider",),
        required_slayer_level=42,
        readiness_features=("protective_equipment", "disease_damage"),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "fire_giants",
        "Fire giants",
        ("fire_giant",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "fungal_magi",
        "Fungal magi",
        ("fungal_mage",),
        required_skill_levels=(("magic", 50),),
        readiness_features=("neem_oil",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "gargoyles",
        "Gargoyles",
        ("gargoyle",),
        required_slayer_level=75,
        readiness_features=("finisher",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "grifolapines",
        "Grifolapines",
        ("grifolapine",),
        required_slayer_level=88,
        required_skill_levels=(("magic", 60),),
        readiness_features=("neem_oil",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "grifolaroos",
        "Grifolaroos",
        ("grifolaroo",),
        required_slayer_level=82,
        required_skill_levels=(("magic", 60),),
        readiness_features=("neem_oil",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "jungle_strykewyrms",
        "Jungle strykewyrms",
        ("jungle_strykewyrm",),
        required_slayer_level=73,
        readiness_features=("assignment_only", "poison_damage"),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "kurasks",
        "Kurasks",
        ("kurask",),
        required_slayer_level=70,
        readiness_features=("restricted_weapon",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "mutated_zygomites",
        "Mutated zygomites",
        ("mutated_zygomite_level_74", "mutated_zygomite_level_86"),
        required_slayer_level=57,
        required_quest_id="lost_city",
        readiness_features=("finisher",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "trolls",
        "Trolls",
        ("troll",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "vyrewatch",
        "Vyrewatch",
        ("vyrewatch",),
        required_slayer_level=67,
        required_quest_id="the_branches_of_darkmeyer",
        readiness_features=("restricted_weapon",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "warped_tortoises",
        "Warped tortoises",
        ("warped_tortoise",),
        required_slayer_level=56,
        required_quest_id="the_path_of_glouphrie",
        readiness_features=("crystal_chime",),
        source=CHAELDAR_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "abyssal_demons",
        "Abyssal demons",
        ("abyssal_demon",),
        required_slayer_level=85,
        readiness_features=("teleport_interruption",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "aquanites",
        "Aquanites",
        ("aquanite",),
        required_slayer_level=78,
        readiness_features=("prayer_negation",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "black_demons",
        "Black demons",
        ("black_demon",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "desert_strykewyrms",
        "Desert strykewyrms",
        ("desert_strykewyrm",),
        required_slayer_level=77,
        readiness_features=("assignment_only", "strykewyrm_special"),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "greater_demons",
        "Greater demons",
        ("greater_demon",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "hellhounds",
        "Hellhounds",
        ("hellhound",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "iron_dragons",
        "Iron dragons",
        ("iron_dragon",),
        readiness_features=("dragonfire",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "mutated_jadinkos",
        "Mutated jadinkos",
        ("mutated_jadinko_baby",),
        required_slayer_level=80,
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "nechryael",
        "Nechryael",
        ("nechryael",),
        required_slayer_level=80,
        readiness_features=("death_spawn",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "red_dragons",
        "Red dragons",
        ("red_dragon", "baby_red_dragon"),
        readiness_features=("dragonfire",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "scabarites",
        "Scabarites",
        ("scabaras_lancer",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "spiritual_mages",
        "Spiritual mages",
        ("spiritual_mage_saradomin",),
        required_slayer_level=83,
        readiness_features=("god_wars_context",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "spiritual_warriors",
        "Spiritual warriors",
        ("spiritual_warrior_saradomin",),
        required_slayer_level=68,
        readiness_features=("god_wars_context",),
        source=SUMONA_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "terror_dogs",
        "Terror dogs",
        ("terror_dog",),
        required_slayer_level=40,
        readiness_features=("prayer_drain_context",),
        source=SUMONA_AUDIT_SOURCE,
    ),
)

SLAYER_FAMILIES_BY_ID: Dict[str, SlayerFamily] = {
    family.id: family for family in _FAMILIES
}


def _assignment(
    family_id: str,
    weight: int,
    count_min: int,
    count_max: int,
    source: str,
) -> SlayerAssignmentFamily:
    return SlayerAssignmentFamily(
        family=SLAYER_FAMILIES_BY_ID[family_id],
        row=SlayerMasterFamilyRow(
            family_id=family_id,
            weight=weight,
            count_min=count_min,
            count_max=count_max,
            source=source,
        ),
    )


TURAEL_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = (
    _assignment("banshees", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("bats", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("bears", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("birds", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("cave_bugs", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("cave_slimes", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("cows", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("crawling_hands", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("desert_lizards", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("dogs", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("dwarves", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("ghosts", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("goblins", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("gelatinous_abominations", 30, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("grotworms", 15, 15, 30, TURAEL_AUDIT_SOURCE),
    _assignment("icefiends", 10, 10, 20, TURAEL_AUDIT_SOURCE),
    _assignment("minotaurs", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("monkeys", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("scorpions", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("skeletons", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("spiders", 10, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("wolves", 15, 15, 50, TURAEL_AUDIT_SOURCE),
    _assignment("zombies", 10, 15, 50, TURAEL_AUDIT_SOURCE),
)

MAZCHNA_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, MAZCHNA_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("banshees", 20, 40, 70),
        ("bats", 10, 40, 70),
        ("bears", 10, 40, 70),
        ("catablepon", 10, 40, 70),
        ("cave_crawlers", 20, 40, 70),
        ("cave_slimes", 10, 40, 70),
        ("cockatrice", 20, 40, 70),
        ("crawling_hands", 20, 40, 70),
        ("cyclopes", 10, 30, 60),
        ("desert_lizards", 10, 40, 70),
        ("dogs", 10, 40, 70),
        ("flesh_crawlers", 10, 40, 70),
        ("ghouls", 10, 40, 70),
        ("ghosts", 10, 40, 70),
        ("grotworms", 10, 40, 70),
        ("hill_giants", 10, 40, 70),
        ("hobgoblins", 10, 40, 70),
        ("ice_warriors", 10, 40, 70),
        ("kalphites", 10, 40, 70),
        ("mogres", 10, 40, 70),
        ("pyrefiends", 20, 40, 70),
        ("rock_slugs", 15, 40, 70),
        ("skeletons", 10, 40, 70),
        ("vampyres", 10, 40, 70),
        ("wall_beasts", 10, 10, 20),
        ("wolves", 10, 40, 70),
        ("zombies", 10, 40, 70),
    )
)

VANNAKA_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, VANNAKA_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("aberrant_spectres", 25, 60, 120),
        ("ankou", 10, 60, 120),
        ("banshees", 15, 60, 120),
        ("basilisks", 10, 60, 120),
        ("bloodveld", 20, 60, 120),
        ("brine_rats", 20, 60, 120),
        ("cockatrice", 10, 60, 120),
        ("crocodiles", 10, 30, 60),
        ("cyclopes", 10, 60, 120),
        ("dust_devils", 25, 60, 120),
        ("earth_warriors", 15, 30, 60),
        ("ghouls", 10, 60, 120),
        ("green_dragons", 10, 30, 60),
        ("grotworms", 15, 60, 120),
        ("harpie_bug_swarms", 20, 60, 120),
        ("hill_giants", 10, 60, 120),
        ("ice_giants", 10, 60, 120),
        ("ice_warriors", 10, 60, 120),
        ("infernal_mages", 10, 60, 120),
        ("jellies", 20, 60, 120),
        ("jungle_horrors", 10, 60, 120),
        ("killerwatts", 20, 60, 120),
        ("lesser_demons", 10, 60, 120),
        ("mogres", 10, 60, 120),
        ("molanisks", 10, 60, 120),
        ("moss_giants", 10, 60, 120),
        ("ogres", 10, 60, 120),
        ("otherworldly_beings", 10, 60, 120),
        ("pyrefiends", 10, 60, 120),
        ("sea_snakes", 10, 30, 60),
        ("shades", 10, 60, 120),
        ("shadow_warriors", 10, 60, 120),
        ("turoth", 20, 60, 120),
        ("vampyres", 15, 60, 120),
        ("werewolves", 10, 60, 120),
    )
)

CHAELDAR_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, CHAELDAR_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("aberrant_spectres", 15, 110, 170),
        ("banshees", 5, 110, 170),
        ("basilisks", 15, 110, 170),
        ("bloodveld", 15, 110, 170),
        ("blue_dragons", 10, 110, 170),
        ("brine_rats", 10, 110, 170),
        ("bronze_dragons", 10, 30, 60),
        ("cave_crawlers", 5, 110, 170),
        ("cave_horrors", 15, 110, 170),
        ("crawling_hands", 5, 110, 170),
        ("dagannoths", 10, 110, 170),
        ("dust_devils", 15, 110, 170),
        ("elves", 10, 60, 90),
        ("fever_spiders", 10, 110, 170),
        ("fire_giants", 10, 110, 170),
        ("fungal_magi", 10, 83, 136),
        ("gargoyles", 15, 110, 170),
        ("grifolapines", 8, 60, 100),
        ("grifolaroos", 8, 60, 100),
        ("grotworms", 15, 72, 109),
        ("harpie_bug_swarms", 20, 110, 170),
        ("jungle_strykewyrms", 12, 80, 110),
        ("infernal_mages", 10, 110, 170),
        ("jellies", 15, 110, 170),
        ("jungle_horrors", 15, 110, 170),
        ("kalphites", 10, 110, 170),
        ("kurasks", 15, 110, 170),
        ("lesser_demons", 10, 110, 170),
        ("mutated_zygomites", 10, 30, 60),
        ("shadow_warriors", 10, 110, 170),
        ("trolls", 10, 110, 170),
        ("turoth", 15, 110, 170),
        ("vyrewatch", 10, 89, 106),
        ("warped_tortoises", 10, 110, 170),
    )
)

SUMONA_FAMILIES: Tuple[SlayerAssignmentFamily, ...] = tuple(
    _assignment(family_id, weight, count_min, count_max, SUMONA_AUDIT_SOURCE)
    for family_id, weight, count_min, count_max in (
        ("aberrant_spectres", 15, 120, 185),
        ("abyssal_demons", 10, 120, 185),
        ("aquanites", 10, 120, 185),
        ("banshees", 15, 120, 185),
        ("basilisks", 15, 120, 185),
        ("black_demons", 10, 120, 185),
        ("bloodveld", 10, 120, 185),
        ("blue_dragons", 8, 120, 189),
        ("cave_crawlers", 15, 120, 185),
        ("cave_horrors", 15, 120, 185),
        ("dagannoths", 10, 120, 192),
        ("desert_strykewyrms", 14, 90, 110),
        ("dust_devils", 15, 120, 185),
        ("elves", 10, 60, 90),
        ("fire_giants", 10, 120, 185),
        ("fungal_magi", 10, 90, 150),
        ("gargoyles", 10, 120, 185),
        ("greater_demons", 10, 120, 185),
        ("grifolapines", 8, 55, 75),
        ("grifolaroos", 8, 55, 75),
        ("grotworms", 15, 70, 115),
        ("hellhounds", 10, 120, 185),
        ("iron_dragons", 7, 30, 85),
        ("jungle_strykewyrms", 12, 90, 120),
        ("kalphites", 10, 120, 189),
        ("kurasks", 15, 120, 185),
        ("mutated_jadinkos", 10, 80, 130),
        ("nechryael", 10, 120, 185),
        ("red_dragons", 5, 30, 79),
        ("scabarites", 10, 30, 60),
        ("spiritual_mages", 10, 120, 185),
        ("spiritual_warriors", 10, 120, 185),
        ("terror_dogs", 10, 30, 60),
        ("trolls", 10, 120, 191),
        ("turoth", 15, 120, 185),
        ("vyrewatch", 10, 96, 105),
        ("warped_tortoises", 10, 120, 185),
    )
)

TURAEL_MASTER = SlayerMaster(
    id="turael_spria",
    display_name="Turael",
    assignments=TURAEL_FAMILIES,
    runtime_enabled=True,
    expected_weight_total=355,
)

MAZCHNA_MASTER = SlayerMaster(
    id="mazchna_achtryn",
    display_name="Mazchna",
    assignments=MAZCHNA_FAMILIES,
    required_combat_level=20,
    required_quest_id="priest_in_peril",
    alternate_display_name="Achtryn",
    alternate_display_condition="while_guthix_sleeps_in_progress",
    expected_weight_total=325,
    source=MAZCHNA_AUDIT_SOURCE,
)

VANNAKA_MASTER = SlayerMaster(
    id="vannaka",
    display_name="Vannaka",
    assignments=VANNAKA_FAMILIES,
    required_combat_level=40,
    expected_weight_total=460,
    source=VANNAKA_AUDIT_SOURCE,
)

CHAELDAR_MASTER = SlayerMaster(
    id="chaeldar",
    display_name="Chaeldar",
    assignments=CHAELDAR_FAMILIES,
    required_combat_level=70,
    required_quest_id="lost_city",
    expected_weight_total=388,
    source=CHAELDAR_AUDIT_SOURCE,
)

SUMONA_MASTER = SlayerMaster(
    id="sumona",
    display_name="Sumona",
    assignments=SUMONA_FAMILIES,
    required_slayer_level=35,
    required_combat_level=85,
    required_quest_id="smoking_kills",
    expected_weight_total=407,
    source=SUMONA_AUDIT_SOURCE,
)

SLAYER_MASTERS_BY_ID: Dict[str, SlayerMaster] = {
    master.id: master
    for master in (
        TURAEL_MASTER,
        MAZCHNA_MASTER,
        VANNAKA_MASTER,
        CHAELDAR_MASTER,
        SUMONA_MASTER,
    )
}
LIVE_SLAYER_MASTERS_BY_ID: Dict[str, SlayerMaster] = {
    master_id: master
    for master_id, master in SLAYER_MASTERS_BY_ID.items()
    if master.runtime_enabled
}

TURAEL_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in TURAEL_FAMILIES
}
MAZCHNA_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in MAZCHNA_FAMILIES
}
VANNAKA_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in VANNAKA_FAMILIES
}
CHAELDAR_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in CHAELDAR_FAMILIES
}
SUMONA_FAMILIES_BY_ID: Dict[str, SlayerAssignmentFamily] = {
    family.id: family for family in SUMONA_FAMILIES
}

DEFAULT_SLAYER_MASTER_ID = TURAEL_MASTER.id
