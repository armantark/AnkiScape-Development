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
DURADEL_AUDIT_SOURCE = (
    "memory-bank/source-audits/slayer-duradel-lapalok-pool-2026-07-17.md"
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
    chathead_asset_path: str = ""
    alternate_display_name: str = ""
    alternate_display_condition: str = ""
    alternate_chathead_asset_path: str = ""
    expected_weight_total: int = 0
    source: str = TURAEL_AUDIT_SOURCE

    @property
    def family_ids(self) -> Tuple[str, ...]:
        return tuple(assignment.id for assignment in self.assignments)


SlayerFamily.__module__ = "ankiscape.data.slayer_data"
SlayerMasterFamilyRow.__module__ = "ankiscape.data.slayer_data"
SlayerAssignmentFamily.__module__ = "ankiscape.data.slayer_data"
SlayerMaster.__module__ = "ankiscape.data.slayer_data"


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
        (
            "dagannoth",
            "dagannoth_level_92",
            "dagannoth_prime",
            "dagannoth_supreme",
            "dagannoth_rex",
        ),
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
        required_slayer_level=42, required_quest_id="cabin_fever",
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
    SlayerFamily(
        "black_dragons",
        "Black dragons",
        ("black_dragon", "baby_black_dragon", "king_black_dragon"),
        readiness_features=("dragonfire",),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "dark_beasts",
        "Dark beasts",
        ("dark_beast", "revenant_dark_beast"),
        required_slayer_level=90,
        readiness_features=("temple_of_light_context",),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "ganodermic_creatures",
        "Ganodermic creatures",
        ("ganodermic_runt", "ganodermic_beast"),
        required_slayer_level=95,
        required_skill_levels=(("magic", 60),),
        readiness_features=("polypore_context",),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "goraks",
        "Goraks",
        ("gorak_fairy_ring", "gorak_god_wars"),
        required_quest_id="a_fairy_tale_ii_cure_a_queen",
        readiness_features=("location_context",),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "ice_strykewyrms",
        "Ice strykewyrms",
        ("ice_strykewyrm",),
        required_slayer_level=93,
        readiness_features=(
            "assignment_only",
            "strykewyrm_special",
            "fire_cape_or_reward",
        ),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "mithril_dragons",
        "Mithril dragons",
        ("mithril_dragon",),
        readiness_features=("dragonfire", "ancient_cavern_context"),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "skeletal_wyverns",
        "Skeletal wyverns",
        ("skeletal_wyvern",),
        required_slayer_level=72,
        readiness_features=("wyvern_breath", "protective_equipment"),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "steel_dragons",
        "Steel dragons",
        ("steel_dragon",),
        readiness_features=("dragonfire",),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "suqahs",
        "Suqahs",
        ("suqah",),
        required_quest_id="lunar_diplomacy",
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "warped_terrorbirds",
        "Warped terrorbirds",
        ("warped_terrorbird",),
        required_slayer_level=56,
        required_quest_id="the_path_of_glouphrie",
        readiness_features=("crystal_chime",),
        source=DURADEL_AUDIT_SOURCE,
    ),
    SlayerFamily(
        "waterfiends",
        "Waterfiends",
        ("waterfiend",),
        readiness_features=("location_context",),
        source=DURADEL_AUDIT_SOURCE,
    ),
)

SLAYER_FAMILIES_BY_ID: Dict[str, SlayerFamily] = {
    family.id: family for family in _FAMILIES
}
