"""Quest and one-time claim data for AnkiScape."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Dict, Mapping, Tuple, Union

try:
    from .quest_catalog_generated import PRE_EOC_QUEST_CATALOG
except ImportError:  # pragma: no cover
    from quest_catalog_generated import PRE_EOC_QUEST_CATALOG  # type: ignore

try:
    from .runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM
except ImportError:  # pragma: no cover
    from runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM  # type: ignore


RUNE_MYSTERIES_ID = "rune_mysteries"
THE_RESTLESS_GHOST_ID = "the_restless_ghost"
LOST_CITY_ID = "lost_city"
LUNAR_DIPLOMACY_ID = "lunar_diplomacy"
MOURNINGS_END_PART_II_ID = "mournings_end_part_ii"
LEGACY_OF_SEERGAZE_ID = "legacy_of_seergaze"
SWAN_SONG_ID = "swan_song"
TAI_BWO_WANNAI_TRIO_ID = "tai_bwo_wannai_trio"
DEFAULT_QUEST_TARGET = RUNE_MYSTERIES_ID

THE_FREMENNIK_TRIALS_ID = "the_fremennik_trials"
SHILO_VILLAGE_ID = "shilo_village"
MOURNINGS_END_PART_I_ID = "mournings_end_part_i"
DARKNESS_OF_HALLOWVALE_ID = "the_darkness_of_hallowvale"
ONE_SMALL_FAVOUR_ID = "one_small_favour"
GARDEN_OF_TRANQUILLITY_ID = "garden_of_tranquillity"
JUNGLE_POTION_ID = "jungle_potion"
KENNITHS_CONCERNS_ID = "kenniths_concerns"
DEADLIEST_CATCH_ID = "deadliest_catch"
WOLF_WHISTLE_ID = "wolf_whistle"
SONG_FROM_THE_DEPTHS_ID = "song_from_the_depths"
CARNILLEAN_RISING_ID = "carnillean_rising"
SOME_LIKE_IT_COLD_ID = "some_like_it_cold"
WITCHS_HOUSE_ID = "witchs_house"
EAGLES_PEAK_ID = "eagles_peak"
AS_A_FIRST_RESORT_ID = "as_a_first_resort"
ROCKING_OUT_ID = "rocking_out"
THE_KNIGHTS_SWORD_ID = "the_knights_sword"
HEROES_QUEST_ID = "heroes_quest"
SPIRITS_OF_THE_ELID_ID = "spirits_of_the_elid"
ANOTHER_SLICE_OF_H_A_M_ID = "another_slice_of_h_a_m"

RESTLESS_GHOST_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/TheRestlessGhost.kt"
)
RESTLESS_GHOST_SKULL_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/rock_with_skull.plugin.kts"
)
RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/npcs/definitions/undeads/skeleton_warlock_lvl_11.plugin.kts"
)
LOST_CITY_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/LostCity.kt"
)
LOST_CITY_KB_SOURCE = "https://2011.rs/kb/lost_city_members"
LUNAR_DIPLOMACY_SOURCE = "https://www.2011.rs/kb/sym_lunar_diplomacy_members_a_m"
MOURNINGS_END_PART_II_SOURCE = "https://www.2011.rs/kb/mourning_s_ends_part_ii_the_temple_of_light_members"
LEGACY_OF_SEERGAZE_SOURCE = "https://2011.rs/kb/legacy_of_seergaze_members"
SWAN_SONG_SOURCE = "https://www.2011.rs/kb/swan_song_members"
TAI_BWO_WANNAI_TRIO_SOURCE = "https://www.2011.rs/kb/tai_bwo_wannai_trio_members"
DARKAN_QUEST_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/"
    "com/rs/game/content/quests"
)
DARKAN_NPC_COMBATDEF_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs"
)
DARKAN_DEVELOPER_INFO_ROOT = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information"
)
DARKAN_NPC_LIST_SOURCE = f"{DARKAN_DEVELOPER_INFO_ROOT}/npcList.txt"
DARKAN_BEASTS_SOURCE = f"{DARKAN_DEVELOPER_INFO_ROOT}/beasts.txt"
DARKAN_ENUMS_SOURCE = f"{DARKAN_DEVELOPER_INFO_ROOT}/enums.txt"
DARKAN_LOST_CITY_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/lostcity/LostCity.java"
DARKAN_JUNGLE_POTION_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/junglepotion/JunglePotion.java"
DARKAN_WOLF_WHISTLE_SOURCE = f"{DARKAN_QUEST_SOURCE_ROOT}/wolfwhistle/WolfWhistle.java"
HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/entrana_firebird.json"
TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/jogre/jogre_(53).json"
SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/sea_troll_queen (noanims).json"
PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE = (
    f"{DARKAN_NPC_COMBATDEF_ROOT}/areas/paterdomus/monk_of_zamorak/monk_of_zamorak_(30).json"
)
TROLL_STRONGHOLD_DAD_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/areas/death_plateau/dad.json"
SPIRITS_BLACK_GOLEM_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/black_golem (noanims).json"
SPIRITS_WHITE_GOLEM_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/white_golem (noanims).json"
SPIRITS_GREY_GOLEM_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/grey_golem (noanims).json"
ANOTHER_SLICE_HAM_ARCHER_NPC_SOURCE = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/h.a.m._archer (noanims).json"
WITCHS_HOUSE_WIKI_SOURCE = "https://runescape.wiki/w/Witch's_House?oldid=6474931"
WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT = f"{DARKAN_NPC_COMBATDEF_ROOT}/uncategorized/witch's_experiment"
WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(19) (noanims).json"
)
WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(30) (noanims).json"
)
WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(42) (noanims).json"
)
WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE = (
    f"{WITCHS_HOUSE_EXPERIMENT_NPC_SOURCE_ROOT}/witch's_experiment_(53) (noanims).json"
)
RESTLESS_GHOST_WIKI_SOURCE = "https://runescape.wiki/w/The_Restless_Ghost?oldid=6355778"
HEROES_QUEST_WIKI_SOURCE = "https://runescape.wiki/w/Heroes'_Quest?oldid=6534275"
SPIRITS_OF_THE_ELID_WIKI_SOURCE = "https://runescape.wiki/w/Spirits_of_the_Elid?oldid=6326193"
ANOTHER_SLICE_OF_H_A_M_WIKI_SOURCE = "https://runescape.wiki/w/Another_Slice_of_H.A.M.?oldid=6548739"
JUNGLE_POTION_WIKI_SOURCE = "https://runescape.wiki/w/Jungle_Potion?oldid=6555418"
KENNITHS_CONCERNS_WIKI_SOURCE = "https://runescape.wiki/w/Kennith%27s_Concerns?oldid=6549837"
DEADLIEST_CATCH_WIKI_SOURCE = "https://runescape.wiki/w/Deadliest_Catch?oldid=6295312"
WOLF_WHISTLE_WIKI_SOURCE = "https://runescape.wiki/w/Wolf_Whistle?oldid=6327531"
SONG_FROM_THE_DEPTHS_WIKI_SOURCE = "https://runescape.wiki/w/Song_from_the_Depths?oldid=6467675"
CARNILLEAN_RISING_WIKI_SOURCE = "https://runescape.wiki/w/Carnillean_Rising?oldid=6534490"
SOME_LIKE_IT_COLD_WIKI_SOURCE = "https://runescape.wiki/w/Some_Like_It_Cold?oldid=6545099"
SWAN_SONG_WIKI_SOURCE = "https://runescape.wiki/w/Swan_Song?oldid=6548264"
RUNE_MYSTERIES_RELEASE_SOURCE = "https://runescape.salmoneus.net/runescape-2007/quests/rune-mysteries.html"
RUNECRAFTING_BASICS_SOURCE = "https://www.2011.rs/kb/runecrafting_the_basics"
RUNECRAFTING_ALTARS_SOURCE = "https://www.2011.rs/kb/runecrafting_locating_the_altars"
RUNE_ESSENCE_MINE_SOURCE = "https://www.2011.rs/kb/mining_the_rune_essence_mine"
RAW_MONKFISH_SOURCE = "https://runescape.fandom.com/wiki/Raw_monkfish"
RAW_KARAMBWAN_SOURCE = "https://runescape.fandom.com/wiki/Raw_karambwan"
GEM_ROCK_SOURCE = "https://runescape.wiki/w/Gem_rock?oldid=37044944"
PRIEST_IN_PERIL_ID = "priest_in_peril"
PRIEST_IN_PERIL_SOURCE = "https://runescape.wiki/w/Priest_in_Peril?oldid=6487728"
TROLL_STRONGHOLD_ID = "troll_stronghold"
THE_FREMENNIK_ISLES_ID = "the_fremennik_isles"
THE_FREMENNIK_ISLES_SOURCE = "https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919"
BROAD_FLETCHING_ABILITY = "broad_fletching"
BARBARIAN_FISHING_ABILITY = "barbarian_fishing"
BROAD_FLETCHING_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/inter/slayer/slayer_rewards.plugin.kts"
)
BARBARIAN_FISHING_SOURCE = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/fishing/Fishing.kt"
)
HUNTER_EAGLES_PEAK_SOURCE = "https://www.2011.rs/kb/hunter_box_trapping_level_27"
HUNTER_AS_A_FIRST_RESORT_SOURCE = "https://www.2011.rs/kb/hunter_locations"
HUNTER_ROCKING_OUT_SOURCE = "https://www.2011.rs/kb/hunter_butterfly_netting_level_15"
KNIGHTS_SWORD_QUEST_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/quests/impl/TheKnightsSword.kt"
)
KNIGHTS_SWORD_THURGO_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/asgarnia/thurgo.plugin.kts"
)
KNIGHTS_SWORD_SQUIRE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/falador/squire.plugin.kts"
)
HUNTER_PRIEST_IN_PERIL_SOURCE = "https://www.2011.rs/kb/hunter_net_trapping_level_29"

QUEST_REWARD_ITEM_NAME_OVERRIDES = {
    "Ring of charos": "Ring of Charos",
}


@dataclass(frozen=True)
class QuestStage:
    stage: int
    journal: Tuple[str, ...]


@dataclass(frozen=True)
class QuestCombatEncounter:
    encounter_id: str
    display_name: str
    level: int = 0
    quantity: int = 1
    source: str = ""
    source_text: str = ""
    npc_stats: Tuple[Tuple[str, object], ...] = ()
    npc_bonuses: Tuple[Tuple[str, object], ...] = ()
    npc_configs: Tuple[Tuple[str, object], ...] = ()
    npc_stats_source: str = ""


@dataclass(frozen=True)
class QuestStageRequirement:
    stage: int
    description: str
    required_inventory: Tuple[Tuple[str, int], ...] = ()
    required_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = ()
    consumed_inventory: Tuple[Tuple[str, int], ...] = ()
    required_tools: Tuple[Tuple[str, int], ...] = ()
    required_actions: Tuple[str, ...] = ()
    required_routes: Tuple[str, ...] = ()
    combat_encounters: Tuple[QuestCombatEncounter, ...] = ()
    source: str = ""


@dataclass(frozen=True)
class QuestPrerequisite:
    quest_id: str
    display_name: str


@dataclass(frozen=True)
class QuestSkillRequirement:
    skill_id: str
    display_name: str
    level: int


@dataclass(frozen=True)
class QuestXpReward:
    skill_id: str
    amount: float


@dataclass(frozen=True)
class QuestLampReward:
    display_name: str
    amount: float
    skill_options: Tuple[str, ...]
    minimum_level: int
    source: str
    source_text: str = ""
    quantity: int = 1


@dataclass(frozen=True)
class QuestDefinition:
    id: str
    display_name: str
    stages: int
    point_reward: int
    rewards: Tuple[Tuple[str, int], ...]
    start_point: str
    requirements: Tuple[str, ...]
    required_items: Tuple[Tuple[str, int], ...]
    combat: str
    source: str
    journal_stages: Tuple[QuestStage, ...]
    release_date: str
    members: bool
    difficulty: str
    length: str
    timeline: str
    required_quests: Tuple[QuestPrerequisite, ...] = ()
    required_skills: Tuple[QuestSkillRequirement, ...] = ()
    required_quest_points: int = 0
    xp_rewards: Tuple[QuestXpReward, ...] = ()
    lamp_rewards: Tuple[QuestLampReward, ...] = ()
    unlocks: Tuple[str, ...] = ()
    release_order: int = 0
    stage_requirements: Tuple[QuestStageRequirement, ...] = ()


@dataclass(frozen=True)
class ClaimDefinition:
    id: str
    display_name: str
    source: str
    claim_type: str = "item"
    item_name: str = ""
    quantity: int = 1
    required_quest: str = RUNE_MYSTERIES_ID
    required_runecrafting_level: int = 0
    xp_amount: float = 0.0
    skill_options: Tuple[str, ...] = ()
    minimum_level: int = 1


@dataclass(frozen=True)
class QuestReference:
    id: str
    display_name: str
    source: str
    note: str


@dataclass(frozen=True)
class QuestUnlockRule:
    quest_id: str
    gate_kind: str
    skill_id: str
    target_ids: Tuple[str, ...]
    reason: str
    source: str


@dataclass(frozen=True)
class TargetUnlockRequirement:
    kind: str
    reason: str
    source: str
    quest_id: str = ""
    ability_id: str = ""


@dataclass(frozen=True)
class TargetUnlockRule:
    gate_kind: str
    skill_id: str
    target_ids: Tuple[str, ...]
    requirements: Tuple[TargetUnlockRequirement, ...]


def _clean_journal(*lines: str) -> Tuple[str, ...]:
    cleaned = []
    for line in lines:
        stripped = re.sub(r"</?col(?:=[^>]*)?>", "", line)
        stripped = stripped.replace("<str>", "").strip()
        if stripped:
            cleaned.append(stripped)
    return tuple(cleaned)


def _simple_stage(stage: int, *lines: str) -> QuestStage:
    return QuestStage(stage, _clean_journal(*lines))


RUNE_MYSTERIES_STAGES: Tuple[QuestStage, ...] = (
    QuestStage(
        1,
        _clean_journal(
            "I spoke to Duke Horacio in Lumbridge Castle. He told me",
            "that he'd found a Strange Talisman in the Castle which",
            "might be of use to the Order of Wizards at the Wizards'",
            "Tower. He asked me to take it there and give it to a wizard",
            "called Sedridor. I can find the Wizards' Tower south west of",
            "Lumbridge, across the bridge from Draynor Village.",
        ),
    ),
    QuestStage(2, _clean_journal("I travelled toward the Wizards' Tower with the strange talisman.")),
    QuestStage(
        3,
        _clean_journal(
            "I delivered the Strange Talisman to Sedridor in the",
            "basement of the Wizards' Tower. He believes it might be",
            "key to discovering a Teleportation Incantation to the lost",
            "Rune Essence Mine. He asked me to help confirm this by",
            "delivering a Package to Aubury, an expert on",
            "Runecrafting. I can find him in his Rune Shop in south east",
            "Varrock.",
        ),
    ),
    QuestStage(4, _clean_journal("I carried Sedridor's package toward Aubury's Rune Shop in Varrock.")),
    QuestStage(
        5,
        _clean_journal(
            "I delivered the Package to Aubury at his Rune Shop in",
            "south east Varrock. He confirmed Sedridor's suspicions",
            "and asked me to take some Research Notes back to him. I",
            "can find Sedridor in the basement of the Wizards' Tower.",
        ),
    ),
    QuestStage(
        6,
        _clean_journal(
            "I spoke to Duke Horacio and he showed me a strange",
            "talisman that had been found by one of his subjects.",
            "I agreed to take it to the Wizards' Tower, South West of",
            "Lumbridge for further examination by the wizards.",
            "I gave the Talisman to the Head of the Tower and",
            "agreed to help him with his research into rune stones.",
            "I took the research package to Varrock and delivered it.",
            "Aubury was interested in the research package and gave",
            "me his own research notes to deliver to Sedridor.",
            "I brought Sedridor the research notes that Aubury had",
            "compiled so that he could compare their research. They",
            "discovered that it was now possible to create new rune",
            "stones, a skill that had been thought lost forever.",
            "In return for all of my help they taught me how to do this,",
            "and will teleport me to mine blank runes anytime.",
            "Quest complete!",
        ),
    ),
)

LOST_CITY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The adventurers in Lumbridge Swamp are searching for Zanaris.", "I should find out what they know."),
    _simple_stage(2, "I found Shamus hiding in a swamp tree.", "He says Zanaris is reached through the shed while carrying a dramen staff."),
    _simple_stage(3, "I travelled to Entrana to find the dramen tree.", "The tree is protected by a dangerous spirit."),
    _simple_stage(4, "I defeated the tree spirit and cut a dramen branch."),
    _simple_stage(5, "I crafted a dramen staff from the branch.", "The shed in Lumbridge Swamp should now open the way."),
    _simple_stage(6, "I entered Zanaris through the swamp shed.", "Quest complete!"),
)

TAI_BWO_WANNAI_TRIO_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Timfraku wants his three sons to return to Tai Bwo Wannai."),
    _simple_stage(2, "I helped Tiadeche learn the way to catch karambwan."),
    _simple_stage(3, "I helped Tamayu prepare for his fight with the Shaikahan."),
    _simple_stage(4, "I helped Tinsay gather and prepare unusual food for the village."),
    _simple_stage(5, "The three sons are ready to return to Tai Bwo Wannai."),
    _simple_stage(6, "I reported back to Timfraku and restored the family.", "Quest complete!"),
)

MOURNINGS_END_PART_II_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The head mourner has opened the route toward the excavation below West Ardougne."),
    _simple_stage(2, "I entered the Temple of Light beneath Arandar."),
    _simple_stage(3, "I worked through the temple mirrors and coloured light beams."),
    _simple_stage(4, "I reached the death altar deep in the temple."),
    _simple_stage(5, "I uncovered the mourners' plan and secured a death talisman."),
    _simple_stage(6, "I escaped the temple and returned with news of what I found."),
    _simple_stage(7, "The path to the death altar is open.", "Quest complete!"),
)

SWAN_SONG_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Herman Caranos needs help defending the Piscatoris Fishing Colony."),
    _simple_stage(2, "I recruited the Wise Old Man for one last adventure."),
    _simple_stage(3, "We repaired the colony and prepared for the sea troll attack."),
    _simple_stage(4, "I fought through the sea trolls attacking the colony."),
    _simple_stage(5, "The Sea Troll Queen was defeated and the colony was saved."),
    _simple_stage(6, "Piscatoris is secure and the monkfish grounds are available.", "Quest complete!"),
)

LUNAR_DIPLOMACY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Lokar Searunner offered passage toward the Moon Clan."),
    _simple_stage(2, "I sailed from Rellekka through Pirates' Cove toward Lunar Isle."),
    _simple_stage(3, "I met the Moon Clan and learned why they distrust the Fremennik."),
    _simple_stage(4, "I prepared a waking sleep potion for the Oneiromancer."),
    _simple_stage(5, "I made a lunar staff and gathered ceremonial lunar clothing."),
    _simple_stage(6, "I entered the dream world and faced the Moon Clan's trials."),
    _simple_stage(7, "I defeated myself in the dream world."),
    _simple_stage(8, "The Moon Clan accepted me and the astral altar is open.", "Quest complete!"),
)

LEGACY_OF_SEERGAZE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "A mercenary near Paterdomus reported suspicious activity in Morytania."),
    _simple_stage(2, "Drezel's discovery beneath Paterdomus pointed toward the columbarium."),
    _simple_stage(3, "I helped the Myreque investigate the Vyrewatch and Meiyerditch."),
    _simple_stage(4, "I created the Ivandis flail to fight the Vyrewatch."),
    _simple_stage(5, "I performed a cremation rite and recovered a key to the hidden storage."),
    _simple_stage(6, "I found the blood talisman and reported back to the Myreque."),
    _simple_stage(7, "The blood altar and columbarium rewards are now available.", "Quest complete!"),
)

KNIGHTS_SWORD_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I told the Squire I would help replace the sword he lost.",
        "Reldo in Varrock Palace library may know where to find Imcando dwarves.",
    ),
    _simple_stage(
        2,
        "Reldo said some Imcando dwarves live on the southern peninsula of Asgarnia.",
        "They dislike strangers and love redberry pies.",
    ),
    _simple_stage(
        3,
        "I found Thurgo and gave him a Redberry pie.",
        "He will help now that he trusts me.",
    ),
    _simple_stage(4, "Thurgo needs a picture of the sword before he can make a replacement."),
    _simple_stage(5, "The Squire told me about a portrait in Sir Vyvin's room that shows the sword."),
    _simple_stage(
        6,
        "Thurgo needs two Iron bars and some Blurite ore to make the replica sword.",
        "Blurite ore is found below the cliff near Thurgo's house.",
    ),
    _simple_stage(
        7,
        "Thurgo made a replica of Sir Vyvin's sword and I returned it to the Squire.",
        "Quest complete!",
    ),
)

KNIGHTS_SWORD_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=2,
        description="Give Thurgo a Redberry pie.",
        consumed_inventory=(("Redberry pie", 1),),
        source=f"{KNIGHTS_SWORD_QUEST_SOURCE_PATH}; {KNIGHTS_SWORD_THURGO_SOURCE_PATH}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Give Thurgo the materials for the replica sword.",
        consumed_inventory=(("Blurite ore", 1), ("Iron bar", 2)),
        source=f"{KNIGHTS_SWORD_QUEST_SOURCE_PATH}; {KNIGHTS_SWORD_THURGO_SOURCE_PATH}",
    ),
)


QUEST_OVERRIDES: Tuple[QuestDefinition, ...] = (
    QuestDefinition(
        id=LOST_CITY_ID,
        display_name="Lost City",
        stages=6,
        point_reward=3,
        rewards=(("Dramen staff", 1),),
        start_point="Talk to the warrior adventurer in Lumbridge Swamp.",
        requirements=("Crafting 31", "Woodcutting 36"),
        required_items=(),
        combat="Must be able to kill a level 63 Tree spirit.",
        source=f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_KB_SOURCE}",
        journal_stages=LOST_CITY_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Experienced",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(
            QuestSkillRequirement("crafting", "Crafting", 31),
            QuestSkillRequirement("woodcutting", "Woodcutting", 36),
        ),
        unlocks=("Access to Zanaris", "Ability to craft cosmic runes"),
    ),
    QuestDefinition(
        id=RUNE_MYSTERIES_ID,
        display_name="Rune Mysteries",
        stages=6,
        point_reward=1,
        rewards=(("Air talisman", 1),),
        start_point="Speak to Duke Horacio, upstairs in Lumbridge Castle.",
        requirements=(),
        required_items=(),
        combat="None.",
        source=f"{RUNEMYSTERIES_SOURCE_PATH}; {RUNE_MYSTERIES_RELEASE_SOURCE}",
        journal_stages=RUNE_MYSTERIES_STAGES,
        release_date="2003-12-01",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(
            QuestXpReward("magic", 250),
            QuestXpReward("runecrafting", 250),
        ),
        unlocks=("Ability to craft runes", "Ability to mine rune essence"),
    ),
    QuestDefinition(
        id=THE_KNIGHTS_SWORD_ID,
        display_name="The Knight's Sword",
        stages=7,
        point_reward=1,
        rewards=(),
        start_point="Speak to the Squire in the courtyard of the White Knights' Castle in southern Falador.",
        requirements=("Mining 10", "Used during quest: Redberry pie x1, Blurite ore x1, Iron bar x2"),
        required_items=(),
        combat="Ability to evade level 54 Ice Warriors and level 53 Ice Giants.",
        source=f"{KNIGHTS_SWORD_QUEST_SOURCE_PATH}; {KNIGHTS_SWORD_SQUIRE_SOURCE_PATH}; {KNIGHTS_SWORD_THURGO_SOURCE_PATH}",
        journal_stages=KNIGHTS_SWORD_STAGES,
        release_date="2001-04-06",
        members=False,
        difficulty="Intermediate",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(QuestSkillRequirement("mining", "Mining", 10),),
        xp_rewards=(QuestXpReward("smithing", 12725),),
        stage_requirements=KNIGHTS_SWORD_STAGE_REQUIREMENTS,
    ),
    QuestDefinition(
        id=TAI_BWO_WANNAI_TRIO_ID,
        display_name="Tai Bwo Wannai Trio",
        stages=6,
        point_reward=2,
        rewards=(("Coins", 2000), ("Rune spear (kp)", 1)),
        start_point="Speak to Timfraku in Tai Bwo Wannai Village.",
        requirements=("Jungle Potion", "Agility 15", "Cooking 30", "Fishing 5"),
        required_items=(),
        combat="Must be able to defeat level 48 jogres.",
        source=TAI_BWO_WANNAI_TRIO_SOURCE,
        journal_stages=TAI_BWO_WANNAI_TRIO_STAGES,
        release_date="2004-09-14",
        members=True,
        difficulty="Intermediate",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(JUNGLE_POTION_ID, "Jungle Potion"),),
        required_skills=(
            QuestSkillRequirement("agility", "Agility", 15),
            QuestSkillRequirement("cooking", "Cooking", 30),
            QuestSkillRequirement("fishing", "Fishing", 5),
        ),
        xp_rewards=(
            QuestXpReward("cooking", 5000),
            QuestXpReward("fishing", 5000),
            QuestXpReward("attack", 2500),
            QuestXpReward("strength", 2500),
        ),
        unlocks=("Ability to catch karambwanji and karambwan",),
    ),
    QuestDefinition(
        id=MOURNINGS_END_PART_II_ID,
        display_name="Mourning's End Part II",
        stages=7,
        point_reward=2,
        rewards=(("Death talisman", 1),),
        start_point="Speak to the head mourner in West Ardougne.",
        requirements=("Mourning's End Part I",),
        required_items=(),
        combat="No direct boss fight; the Temple of Light is dangerous.",
        source=MOURNINGS_END_PART_II_SOURCE,
        journal_stages=MOURNINGS_END_PART_II_STAGES,
        release_date="2005-10-17",
        members=True,
        difficulty="Master",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(MOURNINGS_END_PART_I_ID, "Mourning's End Part I"),),
        xp_rewards=(QuestXpReward("agility", 20000),),
        unlocks=("Access to the Death Altar",),
    ),
    QuestDefinition(
        id=SWAN_SONG_ID,
        display_name="Swan Song",
        stages=6,
        point_reward=2,
        rewards=(("Coins", 25000),),
        start_point="Speak to Herman Caranos at the Piscatoris Fishing Colony.",
        requirements=(
            "One Small Favour",
            "Garden of Tranquillity",
            "101 Quest Points",
            "Magic 66",
            "Cooking 62",
            "Fishing 62",
            "Smithing 45",
            "Firemaking 42",
            "Crafting 40",
        ),
        required_items=(),
        combat="Must be able to fight a powerful level 170 monster.",
        source=SWAN_SONG_SOURCE,
        journal_stages=SWAN_SONG_STAGES,
        release_date="2006-05-02",
        members=True,
        difficulty="Master",
        length="Medium",
        timeline="Fifth Age",
        required_quests=(
            QuestPrerequisite(ONE_SMALL_FAVOUR_ID, "One Small Favour"),
            QuestPrerequisite(GARDEN_OF_TRANQUILLITY_ID, "Garden of Tranquillity"),
        ),
        required_skills=(
            QuestSkillRequirement("magic", "Magic", 66),
            QuestSkillRequirement("cooking", "Cooking", 62),
            QuestSkillRequirement("fishing", "Fishing", 62),
            QuestSkillRequirement("smithing", "Smithing", 45),
            QuestSkillRequirement("firemaking", "Firemaking", 42),
            QuestSkillRequirement("crafting", "Crafting", 40),
        ),
        required_quest_points=101,
        xp_rewards=(
            QuestXpReward("magic", 15000),
            QuestXpReward("fishing", 10000),
            QuestXpReward("prayer", 10000),
        ),
        unlocks=("Access to the Piscatoris Fishing Colony", "Ability to fish monkfish"),
    ),
    QuestDefinition(
        id=LUNAR_DIPLOMACY_ID,
        display_name="Lunar Diplomacy",
        stages=8,
        point_reward=2,
        rewards=(("Astral rune", 50),),
        start_point="Talk to Lokar Searunner at the docks of Rellekka.",
        requirements=(
            "The Fremennik Trials",
            "Lost City",
            "Rune Mysteries",
            "Shilo Village",
            "Crafting 61",
            "Defence 40",
            "Firemaking 49",
            "Herblore 5",
            "Magic 65",
            "Mining 60",
            "Woodcutting 55",
        ),
        required_items=(),
        combat="Must be able to defeat Suqahs and the player's dream self.",
        source=LUNAR_DIPLOMACY_SOURCE,
        journal_stages=LUNAR_DIPLOMACY_STAGES,
        release_date="2006-07-24",
        members=True,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quests=(
            QuestPrerequisite(THE_FREMENNIK_TRIALS_ID, "The Fremennik Trials"),
            QuestPrerequisite(LOST_CITY_ID, "Lost City"),
            QuestPrerequisite(RUNE_MYSTERIES_ID, "Rune Mysteries"),
            QuestPrerequisite(SHILO_VILLAGE_ID, "Shilo Village"),
        ),
        required_skills=(
            QuestSkillRequirement("crafting", "Crafting", 61),
            QuestSkillRequirement("defense", "Defence", 40),
            QuestSkillRequirement("firemaking", "Firemaking", 49),
            QuestSkillRequirement("herblore", "Herblore", 5),
            QuestSkillRequirement("magic", "Magic", 65),
            QuestSkillRequirement("mining", "Mining", 60),
            QuestSkillRequirement("woodcutting", "Woodcutting", 55),
        ),
        xp_rewards=(QuestXpReward("magic", 5000), QuestXpReward("runecrafting", 5000)),
        unlocks=("Access to the Lunar Spellbook", "Access to the Astral Altar"),
    ),
    QuestDefinition(
        id=LEGACY_OF_SEERGAZE_ID,
        display_name="Legacy of Seergaze",
        stages=7,
        point_reward=2,
        rewards=(("Blood talisman", 1), ("Ivandis flail", 1), ("Tome of Experience, 2nd Ed.", 1)),
        start_point="Talk to the Mercenary Adventurer at the Burgh de Rott Ramble start point east of Paterdomus.",
        requirements=(
            "Darkness of Hallowvale",
            "Construction 20",
            "Agility 29",
            "Slayer 31",
            "Mining 35",
            "Firemaking 40",
            "Crafting 47",
            "Magic 49",
        ),
        required_items=(),
        combat="Two different combat styles are useful against level 80 guards and Vyrewatch.",
        source=LEGACY_OF_SEERGAZE_SOURCE,
        journal_stages=LEGACY_OF_SEERGAZE_STAGES,
        release_date="2008-04-22",
        members=True,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(DARKNESS_OF_HALLOWVALE_ID, "Darkness of Hallowvale"),),
        required_skills=(
            QuestSkillRequirement("construction", "Construction", 20),
            QuestSkillRequirement("agility", "Agility", 29),
            QuestSkillRequirement("slayer", "Slayer", 31),
            QuestSkillRequirement("mining", "Mining", 35),
            QuestSkillRequirement("firemaking", "Firemaking", 40),
            QuestSkillRequirement("crafting", "Crafting", 47),
            QuestSkillRequirement("magic", "Magic", 49),
        ),
        xp_rewards=(
            QuestXpReward("agility", 2000),
            QuestXpReward("construction", 1000),
            QuestXpReward("crafting", 4000),
            QuestXpReward("magic", 3000),
            QuestXpReward("mining", 2000),
            QuestXpReward("slayer", 2000),
        ),
        unlocks=("Access to the Blood Altar", "Paterdomus Columbarium rewards"),
    ),
)
QUEST_OVERRIDES_BY_ID: Dict[str, QuestDefinition] = {quest.id: quest for quest in QUEST_OVERRIDES}


def _stage_req(
    stage: int,
    description: str,
    source: str,
    *,
    required_inventory: Tuple[Tuple[str, int], ...] = (),
    required_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = (),
    consumed_inventory: Tuple[Tuple[str, int], ...] = (),
    required_tools: Tuple[Tuple[str, int], ...] = (),
    required_actions: Tuple[str, ...] = (),
    required_routes: Tuple[str, ...] = (),
    combat_encounters: Tuple[QuestCombatEncounter, ...] = (),
) -> QuestStageRequirement:
    return QuestStageRequirement(
        stage=stage,
        description=description,
        required_inventory=required_inventory,
        required_inventory_options=required_inventory_options,
        consumed_inventory=consumed_inventory,
        required_tools=required_tools,
        required_actions=required_actions,
        required_routes=required_routes,
        combat_encounters=combat_encounters,
        source=source,
    )


def _combat(
    quest_id: str,
    encounter_id: str,
    display_name: str,
    level: int,
    source: str,
    source_text: str,
    *,
    quantity: int = 1,
    npc_stats: Tuple[Tuple[str, object], ...] = (),
    npc_bonuses: Tuple[Tuple[str, object], ...] = (),
    npc_configs: Tuple[Tuple[str, object], ...] = (),
    npc_stats_source: str = "",
) -> QuestCombatEncounter:
    return QuestCombatEncounter(
        encounter_id=f"{quest_id}_{encounter_id}",
        display_name=display_name,
        level=level,
        quantity=quantity,
        source=source,
        source_text=source_text,
        npc_stats=npc_stats,
        npc_bonuses=npc_bonuses,
        npc_configs=npc_configs,
        npc_stats_source=npc_stats_source,
    )


QuestCombatEncounterReplacement = Union[QuestCombatEncounter, Tuple[QuestCombatEncounter, ...]]


QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    WITCHS_HOUSE_ID: (
        _stage_req(
            1,
            "Gather the gloves and cheese needed to enter the Witch's House safely.",
            WITCHS_HOUSE_WIKI_SOURCE,
            required_inventory=(("Leather gloves", 1), ("Cheese", 1)),
        ),
        _stage_req(
            2,
            "Defeat the Witch's experiment through all four forms before retrieving the ball.",
            WITCHS_HOUSE_WIKI_SOURCE,
            combat_encounters=(
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_first_form",
                    "Witch's experiment (Skavid form)",
                    19,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE}",
                    "Historical quest text says the experiment's first stage is a Skavid level 19; Darkan NPC id 897 supplies the Witch's experiment level 19 stats.",
                    npc_stats=(
                        ("hitpoints", 1130),
                        ("attack", 18),
                        ("strength", 10),
                        ("defence", 19),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 100),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE,
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_second_form",
                    "Witch's experiment (Spider form)",
                    30,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE}",
                    "Historical quest text says the experiment's second stage is a Spider level 30; Darkan NPC id 898 supplies the Witch's experiment level 30 stats.",
                    npc_stats=(
                        ("hitpoints", 1225),
                        ("attack", 28),
                        ("strength", 20),
                        ("defence", 29),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 125),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE,
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_third_form",
                    "Witch's experiment (Bear form)",
                    42,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE}",
                    "Historical quest text says the experiment's third stage is a Bear level 42; Darkan NPC id 899 supplies the Witch's experiment level 42 stats.",
                    npc_stats=(
                        ("hitpoints", 1325),
                        ("attack", 38),
                        ("strength", 30),
                        ("defence", 39),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 135),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE,
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_fourth_form",
                    "Witch's experiment (Wolf form)",
                    53,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE}",
                    "Historical quest text says the experiment's final stage is a Wolf level 53; Darkan NPC id 900 supplies the Witch's experiment level 53 stats.",
                    npc_stats=(
                        ("hitpoints", 1425),
                        ("attack", 48),
                        ("strength", 40),
                        ("defence", 49),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 150),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE,
                ),
            ),
        ),
    ),
    LOST_CITY_ID: (
        _stage_req(
            1,
            "Find Shamus in the Lumbridge Swamp tree.",
            f"{LOST_CITY_SOURCE_PATH}; {DARKAN_LOST_CITY_SOURCE}; {LOST_CITY_KB_SOURCE}",
            required_actions=("Find Shamus in the Lumbridge Swamp tree",),
        ),
        _stage_req(
            3,
            "Reach Entrana, defeat the tree spirit, and prepare to cut the Dramen tree.",
            f"{LOST_CITY_SOURCE_PATH}; {DARKAN_LOST_CITY_SOURCE}; {LOST_CITY_KB_SOURCE}",
            required_tools=(("Hatchet", 1),),
            required_routes=("Reach Entrana without combat gear",),
            combat_encounters=(
                _combat(
                    LOST_CITY_ID,
                    "tree_spirit",
                    "Tree spirit",
                    63,
                    f"{LOST_CITY_SOURCE_PATH}; {DARKAN_LOST_CITY_SOURCE}",
                    "2011Scape and Darkan Lost City quest text describe the required tree-spirit fight as level 63.",
                ),
            ),
        ),
        _stage_req(
            4,
            "Cut a dramen branch from the Dramen tree.",
            f"{LOST_CITY_SOURCE_PATH}; {DARKAN_LOST_CITY_SOURCE}",
            required_tools=(("Hatchet", 1),),
            required_actions=("Cut a dramen branch",),
        ),
        _stage_req(
            5,
            "Craft the dramen staff and enter Zanaris through the Lumbridge Swamp shed.",
            f"{LOST_CITY_SOURCE_PATH}; {DARKAN_LOST_CITY_SOURCE}",
            required_tools=(("Knife", 1),),
            required_actions=("Craft a dramen staff", "Enter Zanaris through the Lumbridge Swamp shed"),
        ),
    ),
    TAI_BWO_WANNAI_TRIO_ID: (
        _stage_req(
            2,
            "Help Tiadeche with the karambwan catching setup.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Raw karambwan", 2),),
            required_tools=(("Small fishing net", 1),),
            required_actions=("Catch karambwanji for Tiadeche",),
        ),
        _stage_req(
            3,
            "Prepare Tamayu to fight the Shaikahan.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Agility potion (4)", 1), ("Steel spear", 1)),
            required_actions=("Repair and poison Tamayu's spear",),
            combat_encounters=(
                _combat(
                    TAI_BWO_WANNAI_TRIO_ID,
                    "monkey",
                    "Monkey",
                    3,
                    "https://runescape.wiki/w/Tai_Bwo_Wannai_Trio?oldid=6529797",
                    "Quest details require killing a level 3 monkey.",
                ),
                _combat(
                    TAI_BWO_WANNAI_TRIO_ID,
                    "jogre",
                    "Jogre",
                    53,
                    f"https://runescape.wiki/w/Tai_Bwo_Wannai_Trio?oldid=6529797; {TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE}",
                    "Jogre bones can be obtained during the quest by fighting a level 53 jogre.",
                    npc_stats=(
                        ("hitpoints", 600),
                        ("attack", 43),
                        ("strength", 43),
                        ("defence", 43),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 73),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            4,
            "Prepare Tinsay's unusual food requests.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Karamjan rum", 1), ("Seaweed", 1), ("Banana", 1), ("Jogre bones", 1)),
            required_tools=(("Knife", 1), ("Tinderbox", 1), ("Pestle and mortar", 1)),
            required_actions=("Prepare the sliced banana in rum", "Burn and grind the jogre bones"),
        ),
    ),
}


QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    THE_RESTLESS_GHOST_ID: (
        _stage_req(
            1,
            "Receive the ghostspeak amulet from Father Urhney.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_WIKI_SOURCE}",
            required_actions=("Receive the ghostspeak amulet from Father Urhney",),
        ),
        _stage_req(
            2,
            "Speak to the restless ghost while wearing the ghostspeak amulet.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_WIKI_SOURCE}",
            required_inventory=(("Ghostspeak amulet", 1),),
            required_actions=("Speak to the restless ghost",),
        ),
        _stage_req(
            3,
            "Search the Lumbridge Swamp mining spot for the muddy skull.",
            (
                f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
                f"{RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}; {RESTLESS_GHOST_WIKI_SOURCE}"
            ),
            required_actions=("Search the mining spot for the ghost's skull",),
            combat_encounters=(
                _combat(
                    THE_RESTLESS_GHOST_ID,
                    "skeleton_warlock",
                    "Skeleton warlock",
                    11,
                    (
                        f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_SKULL_SOURCE_PATH}; "
                        f"{RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH}; {RESTLESS_GHOST_WIKI_SOURCE}"
                    ),
                    (
                        "The 2011Scape quest text requires facing a level 11 skeleton warlock; "
                        "the Lumbridge skull object spawns Npcs.SKELETON_WARLOCK, whose local "
                        "combat definition supplies these stats."
                    ),
                    npc_stats=(
                        ("hitpoints", 180),
                        ("attack", 1),
                        ("strength", 1),
                        ("defence", 1),
                        ("magic", 8),
                    ),
                    npc_bonuses=(
                        ("attackStab", 0),
                        ("attackCrush", 0),
                        ("defenceStab", 0),
                        ("defenceSlash", 0),
                        ("defenceCrush", 0),
                        ("defenceMagic", 5),
                        ("defenceRanged", 0),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "magic")),
                    npc_stats_source=RESTLESS_GHOST_SKELETON_WARLOCK_NPC_SOURCE_PATH,
                ),
            ),
        ),
        _stage_req(
            4,
            "Return the muddy skull to the ghost's coffin.",
            f"{RESTLESS_GHOST_SOURCE_PATH}; {RESTLESS_GHOST_WIKI_SOURCE}",
            consumed_inventory=(("Muddy skull", 1),),
        ),
    ),
    JUNGLE_POTION_ID: (
        _stage_req(
            1,
            "Bring Trufitus clean snake weed.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean snake weed", 1),),
        ),
        _stage_req(
            2,
            "Bring Trufitus clean ardrigal.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean ardrigal", 1),),
        ),
        _stage_req(
            3,
            "Bring Trufitus clean sito foil.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean sito foil", 1),),
        ),
        _stage_req(
            4,
            "Bring Trufitus clean volencia moss and clean rogue's purse.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean volencia moss", 1), ("Clean rogue's purse", 1)),
        ),
    ),
    RUNE_MYSTERIES_ID: (
        _stage_req(
            1,
            "Deliver the strange talisman to Sedridor.",
            RUNEMYSTERIES_SOURCE_PATH,
            required_actions=("Deliver the strange talisman to Sedridor",),
        ),
        _stage_req(
            3,
            "Deliver Sedridor's package to Aubury.",
            RUNEMYSTERIES_SOURCE_PATH,
            required_actions=("Deliver Sedridor's package to Aubury",),
        ),
        _stage_req(
            5,
            "Return Aubury's research notes to Sedridor.",
            RUNEMYSTERIES_SOURCE_PATH,
            required_actions=("Return Aubury's research notes to Sedridor",),
        ),
    ),
    SWAN_SONG_ID: (
        _stage_req(
            5,
            "Defeat the Sea Troll Queen.",
            f"{SWAN_SONG_SOURCE}; {SWAN_SONG_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    SWAN_SONG_ID,
                    "sea_troll_queen",
                    "Sea Troll Queen",
                    170,
                    f"{SWAN_SONG_WIKI_SOURCE}; {SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE}",
                    "Quest details require the level 170 Sea Troll Queen after the sea troll waves.",
                    npc_stats=(
                        ("hitpoints", 2000),
                        ("attack", 100),
                        ("strength", 70),
                        ("defence", 100),
                        ("magic", 150),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 2345),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=SWAN_SONG_SEA_TROLL_QUEEN_NPC_SOURCE,
                ),
            ),
        ),
    ),
    KENNITHS_CONCERNS_ID: (
        _stage_req(
            1,
            "Investigate the Witchaven tunnels and speak to a villager.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_tools=(("Pickaxe", 1),),
            required_routes=("Reach the Witchaven shrine tunnels",),
            required_actions=("Talk to a villager past the rocks",),
        ),
        _stage_req(
            2,
            "Warn Kennith and speak to Kent.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_actions=("Warn Kennith", "Speak to Kent near the Legends' Guild"),
        ),
        _stage_req(
            3,
            "Trap the possessed villagers in the church.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_actions=("Trap the possessed villagers in the church",),
        ),
        _stage_req(
            4,
            "Mine rubium and fill the steam vents.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_tools=(("Pickaxe", 1),),
            required_actions=("Mine rubium and fill the steam vents",),
        ),
        _stage_req(
            5,
            "Find the toy train and rescue Kennith.",
            KENNITHS_CONCERNS_WIKI_SOURCE,
            required_actions=("Find Kennith's toy train", "Use the toy train on Kennith"),
        ),
    ),
    DEADLIEST_CATCH_ID: (
        _stage_req(
            1,
            "Pickpocket the Master fisher for the sea chart.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            required_actions=("Pickpocket the Master fisher for the sea chart",),
        ),
        _stage_req(
            2,
            "Recruit Linza and prepare the giant harpoon.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            required_actions=("Recruit Linza", "Prepare the giant harpoon"),
        ),
        _stage_req(
            3,
            "Track the Thalassus and rescue Jones.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            required_actions=("Track the Thalassus", "Rescue Jones"),
        ),
    ),
    WOLF_WHISTLE_ID: (
        _stage_req(
            1,
            "Find Scalectrix at the Taverley well.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            required_actions=("Find Scalectrix at the Taverley well",),
        ),
        _stage_req(
            2,
            "Collect the wolpertinger pouch materials.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            required_actions=("Collect the ancient wolf bone amulet", "Collect the embroidered pouch", "Collect the white hare meat"),
        ),
        _stage_req(
            3,
            "Infuse the giant wolpertinger pouch and save Bowloftrix.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            required_actions=("Infuse the giant wolpertinger pouch", "Take the pouch to Scalectrix"),
        ),
    ),
    SONG_FROM_THE_DEPTHS_ID: (
        _stage_req(
            1,
            "Drink the restless sleep potion and follow the souls to the cave.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            required_actions=("Drink the restless sleep potion", "Follow the souls to the cave entrance"),
        ),
        _stage_req(
            2,
            "Work through the dream cave puzzles.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            required_actions=("Complete the maze doors", "Solve the symbol rooms", "Move the saplings through the dream rooms"),
        ),
        _stage_req(
            3,
            "Escape the dragon's stomach and return to Lucille.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            required_actions=("Escape the dragon's stomach", "Return to Lucille"),
        ),
    ),
    CARNILLEAN_RISING_ID: (
        _stage_req(
            1,
            "Accept Xenia's request and speak to Ceril Carnillean.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            required_actions=("Speak to Xenia", "Speak to Ceril Carnillean"),
        ),
        _stage_req(
            2,
            "Gather the mansion props for Philipe's quest.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            required_actions=("Collect the Carnillean family book", "Gather the mansion props"),
        ),
        _stage_req(
            3,
            "Build the cellar quest scene.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            required_actions=("Build the cave quest hotspots", "Recruit Sarsaparilla and Claus"),
        ),
        _stage_req(
            4,
            "Guide Philipe through the staged quest.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            required_actions=("Guide Philipe through the cellar quest",),
            combat_encounters=(
                _combat(
                    CARNILLEAN_RISING_ID,
                    "cave_wolf_matriarch",
                    "Cave wolf matriarch",
                    283,
                    CARNILLEAN_RISING_WIKI_SOURCE,
                    "Historical guide text describes dodging a level 283 monster during Philipe's staged quest.",
                ),
            ),
        ),
        _stage_req(
            5,
            "Report back to Philipe, Ceril, and Xenia.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            required_actions=("Report back to Philipe", "Report back to Ceril and Xenia"),
        ),
    ),
    SOME_LIKE_IT_COLD_ID: (
        _stage_req(
            1,
            "Reach the seals and learn how to enter the Iceberg.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            required_actions=("Speak to Chuck again for teleport", "Entertain the seal", "Travel to the Iceberg"),
        ),
        _stage_req(
            2,
            "Build Ping and Pong's rock costumes.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            required_actions=("Build Ping and Pong's rock costumes", "Give Ping and Pong their costumes"),
        ),
        _stage_req(
            3,
            "Infiltrate the Walrus camp and recover the egg.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            required_actions=("Distract the Walrus", "Steal the egg from the table"),
        ),
        _stage_req(
            4,
            "Collect supplies and repair the submarine engine.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            required_actions=("Collect camp repair supplies", "Repair the submarine engine"),
        ),
        _stage_req(
            5,
            "Win the Battlefish games.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            required_actions=("Defeat Astoria in Battlefish", "Defeat the seals in Battlefish"),
        ),
        _stage_req(
            6,
            "Escape the Walrus camp.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            required_actions=("Escape in the submarine",),
        ),
    ),
}


QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID: Dict[str, Dict[str, QuestCombatEncounterReplacement]] = {
    HEROES_QUEST_ID: {
        "heroes_quest_entrana_fire_bird_2": _combat(
            HEROES_QUEST_ID,
            "entrana_fire_bird_2",
            "Entrana Fire Bird",
            2,
            f"{HEROES_QUEST_WIKI_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}",
            "Historical quest details require the Entrana Fire Bird level 2; Darkan NPC id 6108 and the Entrana firebird combatdef supply these stats.",
            npc_stats=(
                ("hitpoints", 50),
                ("attack", 1),
                ("strength", 1),
                ("defence", 1),
                ("magic", 1),
                ("ranged", 1),
            ),
            npc_configs=(
                ("max_hit", 10),
                ("attack_range", -1),
                ("attack_style", "melee"),
                ("attack_bonus", "stab_att"),
                ("aggressiveness_type", "passive"),
            ),
            npc_stats_source=HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE,
        ),
    },
    SPIRITS_OF_THE_ELID_ID: {
        "spirits_of_the_elid_golem_75": (
            _combat(
                SPIRITS_OF_THE_ELID_ID,
                "black_golem_75",
                "Black golem",
                75,
                f"{SPIRITS_OF_THE_ELID_WIKI_SOURCE}; {DARKAN_ENUMS_SOURCE}; {SPIRITS_BLACK_GOLEM_NPC_SOURCE}",
                "Historical quest details require three level 75 golems; Darkan enum 2791 identifies the Black golem for Spirits of the Elid and the Black golem combatdef supplies these stats.",
                npc_stats=(
                    ("hitpoints", 800),
                    ("attack", 80),
                    ("strength", 30),
                    ("defence", 80),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 90),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=SPIRITS_BLACK_GOLEM_NPC_SOURCE,
            ),
            _combat(
                SPIRITS_OF_THE_ELID_ID,
                "white_golem_75",
                "White golem",
                75,
                f"{SPIRITS_OF_THE_ELID_WIKI_SOURCE}; {DARKAN_ENUMS_SOURCE}; {SPIRITS_WHITE_GOLEM_NPC_SOURCE}",
                "Historical quest details require three level 75 golems; Darkan enum 2791 identifies the White golem for Spirits of the Elid and the White golem combatdef supplies these stats.",
                npc_stats=(
                    ("hitpoints", 800),
                    ("attack", 80),
                    ("strength", 30),
                    ("defence", 80),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 40),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=SPIRITS_WHITE_GOLEM_NPC_SOURCE,
            ),
            _combat(
                SPIRITS_OF_THE_ELID_ID,
                "grey_golem_75",
                "Grey golem",
                75,
                f"{SPIRITS_OF_THE_ELID_WIKI_SOURCE}; {DARKAN_ENUMS_SOURCE}; {SPIRITS_GREY_GOLEM_NPC_SOURCE}",
                "Historical quest details require three level 75 golems; Darkan enum 2791 identifies the Grey golem for Spirits of the Elid and the Grey golem combatdef supplies these stats.",
                npc_stats=(
                    ("hitpoints", 800),
                    ("attack", 80),
                    ("strength", 30),
                    ("defence", 80),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 40),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=SPIRITS_GREY_GOLEM_NPC_SOURCE,
            ),
        ),
    },
    ANOTHER_SLICE_OF_H_A_M_ID: {
        "another_slice_of_h_a_m_h_a_m_ranger_30": _combat(
            ANOTHER_SLICE_OF_H_A_M_ID,
            "h_a_m_ranger_30",
            "H.A.M. ranger",
            30,
            f"{ANOTHER_SLICE_OF_H_A_M_WIKI_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {DARKAN_BEASTS_SOURCE}; {ANOTHER_SLICE_HAM_ARCHER_NPC_SOURCE}",
            "Historical quest details name a level 30 H.A.M. ranger; Darkan names the ranged level 30 NPC H.A.M. Archer id 5859 and the archer combatdef supplies the ranged payload.",
            npc_stats=(
                ("hitpoints", 350),
                ("attack", 15),
                ("strength", 0),
                ("defence", 30),
                ("magic", 0),
                ("ranged", 30),
            ),
            npc_configs=(
                ("max_hit", 40),
                ("attack_range", -1),
                ("attack_style", "range"),
                ("aggressiveness_type", "aggressive"),
            ),
            npc_stats_source=f"{ANOTHER_SLICE_HAM_ARCHER_NPC_SOURCE}; {DARKAN_BEASTS_SOURCE}",
        ),
    },
    PRIEST_IN_PERIL_ID: {
        "priest_in_peril_monk_of_zamorak_30": _combat(
            PRIEST_IN_PERIL_ID,
            "monk_of_zamorak_30",
            "Monk of Zamorak",
            30,
            f"{PRIEST_IN_PERIL_SOURCE}; {DARKAN_QUEST_SOURCE_ROOT}/priestinperil/PriestInPeril.java; {PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE}",
            "Priest in Peril kills use the Paterdomus Zamorak monk NPC ids 1044-1046; the level 30 id 1046 combatdef supplies these stats.",
            npc_stats=(
                ("hitpoints", 250),
                ("attack", 25),
                ("strength", 25),
                ("defence", 25),
                ("magic", 40),
                ("ranged", 1),
            ),
            npc_configs=(
                ("max_hit", 20),
                ("attack_range", -1),
                ("attack_style", "magic"),
                ("attack_bonus", "crush_att"),
                ("aggressiveness_type", "aggressive"),
            ),
            npc_stats_source=PRIEST_IN_PERIL_MONK_OF_ZAMORAK_NPC_SOURCE,
        ),
    },
    TROLL_STRONGHOLD_ID: {
        "troll_stronghold_dad_101": _combat(
            TROLL_STRONGHOLD_ID,
            "dad_101",
            "Dad",
            101,
            f"https://runescape.wiki/w/Troll_Stronghold?oldid=6552397; {DARKAN_QUEST_SOURCE_ROOT}/troll_stronghold/TrollStronghold.kt; {TROLL_STRONGHOLD_DAD_NPC_SOURCE}",
            "Darkan Troll Stronghold instantiates DAD for the arena fight; the area-specific Dad combatdef supplies these stats.",
            npc_stats=(
                ("hitpoints", 1200),
                ("attack", 60),
                ("strength", 120),
                ("defence", 50),
                ("magic", 0),
                ("ranged", 0),
            ),
            npc_configs=(
                ("max_hit", 275),
                ("attack_range", -1),
                ("attack_style", "melee"),
                ("attack_bonus", "crush_att"),
                ("aggressiveness_type", "passive"),
            ),
            npc_stats_source=TROLL_STRONGHOLD_DAD_NPC_SOURCE,
        ),
    },
}


_STAGE_COUNT_BY_LENGTH = {
    "Short": 3,
    "Short to Medium": 4,
    "Medium": 5,
    "Medium to Long": 6,
    "Long": 7,
    "Long to Very Long": 8,
    "Very Long": 9,
    "Very, Very Long": 10,
}


def _generated_stage_count(length: str) -> int:
    return _STAGE_COUNT_BY_LENGTH.get(length, 5)


def _generated_journal_stages(display_name: str, stages: int) -> Tuple[QuestStage, ...]:
    if stages <= 1:
        return (_simple_stage(1, f"I completed {display_name}.", "Quest complete!"),)
    rows = [_simple_stage(1, f"I started {display_name}.")]
    for stage in range(2, stages):
        rows.append(_simple_stage(stage, f"I made progress on {display_name}."))
    rows.append(_simple_stage(stages, f"I completed {display_name}.", "Quest complete!"))
    return tuple(rows)


def _catalog_journal_stages(row: Dict[str, object], display_name: str, stages: int) -> Tuple[QuestStage, ...]:
    raw_stages = row.get("journal_stages", ()) or ()
    rows = []
    for raw_stage in raw_stages:
        if not isinstance(raw_stage, dict):
            continue
        try:
            stage = int(raw_stage.get("stage", 0))
        except (TypeError, ValueError):
            continue
        raw_lines = raw_stage.get("journal", ()) or ()
        lines = tuple(str(line) for line in raw_lines if str(line).strip())
        if stage > 0 and lines:
            rows.append(QuestStage(stage, lines))
    if rows:
        return tuple(sorted(rows, key=lambda stage: stage.stage))
    return _generated_journal_stages(display_name, stages)


def _quest_reward_item_name(name: object) -> str:
    raw_name = str(name)
    return QUEST_REWARD_ITEM_NAME_OVERRIDES.get(raw_name, raw_name)


def _catalog_int(row: Dict[str, object], key: str, default: int = 0) -> int:
    try:
        return int(row.get(key, default))
    except (TypeError, ValueError):
        return default


def _catalog_bool(row: Dict[str, object], key: str, default: bool = False) -> bool:
    value = row.get(key, default)
    return bool(value)


def _catalog_item_pairs(value: object) -> Tuple[Tuple[str, int], ...]:
    if isinstance(value, Mapping):
        return tuple((str(name), _catalog_int({"value": amount}, "value", 1)) for name, amount in value.items())
    if isinstance(value, (tuple, list)):
        pairs = []
        for item in value:
            if isinstance(item, Mapping):
                name = item.get("item_name") or item.get("display_name")
                amount = item.get("quantity", item.get("amount", 1))
                if not isinstance(name, str) or not name:
                    for item_name, item_amount in item.items():
                        if item_name in {"item_name", "display_name", "quantity", "amount"}:
                            continue
                        pairs.append((str(item_name), _catalog_int({"value": item_amount}, "value", 1)))
                    continue
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                name, amount = item[0], item[1]
            else:
                continue
            if isinstance(name, str) and name:
                pairs.append((name, _catalog_int({"value": amount}, "value", 1)))
        return tuple(pairs)
    return ()


def _catalog_item_options(value: object) -> Tuple[Tuple[Tuple[str, int], ...], ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    if value and all(isinstance(group, Mapping) for group in value):
        return (_catalog_item_pairs(value),)
    groups = []
    for group in value:
        options = _catalog_item_pairs(group)
        if options:
            groups.append(options)
    return tuple(groups)


def _catalog_object_pairs(value: object) -> Tuple[Tuple[str, object], ...]:
    if isinstance(value, Mapping):
        return tuple((str(key), item) for key, item in value.items())
    return ()


def _catalog_strings(value: object) -> Tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, (tuple, list)):
        return tuple(str(item) for item in value if str(item))
    return ()


def _catalog_combat_encounters(value: object) -> Tuple[QuestCombatEncounter, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    encounters = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        encounter_id = raw.get("encounter_id")
        display_name = raw.get("display_name")
        if not isinstance(encounter_id, str) or not isinstance(display_name, str):
            continue
        encounters.append(
            QuestCombatEncounter(
                encounter_id=encounter_id,
                display_name=display_name,
                level=_catalog_int(dict(raw), "level", 0),
                quantity=_catalog_int(dict(raw), "quantity", 1),
                source=str(raw.get("source", "")),
                source_text=str(raw.get("source_text", "")),
                npc_stats=_catalog_object_pairs(raw.get("npc_stats", {})),
                npc_bonuses=_catalog_object_pairs(raw.get("npc_bonuses", {})),
                npc_configs=_catalog_object_pairs(raw.get("npc_configs", {})),
                npc_stats_source=str(raw.get("npc_stats_source", "")),
            )
        )
    return tuple(encounters)


def _catalog_stage_requirements(value: object) -> Tuple[QuestStageRequirement, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    requirements = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        stage = _catalog_int(dict(raw), "stage", 0)
        if stage <= 0:
            continue
        requirements.append(
            QuestStageRequirement(
                stage=stage,
                description=str(raw.get("description", "Generated quest-stage requirement.")),
                required_inventory=_catalog_item_pairs(raw.get("required_inventory", {})),
                required_inventory_options=_catalog_item_options(raw.get("required_inventory_options", ())),
                consumed_inventory=_catalog_item_pairs(raw.get("consumed_inventory", {})),
                required_tools=_catalog_item_pairs(raw.get("required_tools", {})),
                required_actions=_catalog_strings(raw.get("required_actions", ())),
                required_routes=_catalog_strings(raw.get("required_routes", ())),
                combat_encounters=_catalog_combat_encounters(raw.get("combat_encounters", ())),
                source=str(raw.get("source", "")),
            )
        )
    return tuple(requirements)


def _quest_from_catalog(row: Dict[str, object]) -> QuestDefinition:
    display_name = str(row.get("display_name", row.get("id", "Quest")))
    length = str(row.get("length", "Medium"))
    stages = _catalog_int(row, "stages", _generated_stage_count(length))
    required_quests = tuple(
        QuestPrerequisite(str(req.get("quest_id")), str(req.get("display_name", req.get("quest_id"))))
        for req in row.get("required_quests", ()) or ()
        if isinstance(req, dict) and req.get("quest_id")
    )
    required_skills = tuple(
        QuestSkillRequirement(
            str(req.get("skill_id")),
            str(req.get("display_name", req.get("skill_id"))),
            _catalog_int(req, "level", 1),
        )
        for req in row.get("required_skills", ()) or ()
        if isinstance(req, dict) and req.get("skill_id")
    )
    xp_rewards = tuple(
        QuestXpReward(str(reward.get("skill_id")), float(reward.get("amount", 0) or 0))
        for reward in row.get("xp_rewards", ()) or ()
        if isinstance(reward, dict) and reward.get("skill_id")
    )
    item_rewards = tuple(
        (_quest_reward_item_name(reward.get("item_name")), _catalog_int(reward, "quantity", 1))
        for reward in row.get("item_rewards", ()) or ()
        if isinstance(reward, dict) and reward.get("item_name")
    )
    lamp_rewards = tuple(
        QuestLampReward(
            str(reward.get("display_name", "XP lamp")),
            float(reward.get("amount", 0) or 0),
            tuple(str(skill_id) for skill_id in (reward.get("skill_options", ()) or ()) if str(skill_id)),
            _catalog_int(reward, "minimum_level", 1),
            str(reward.get("source", row.get("reward_source", row.get("source", "")))),
            str(reward.get("source_text", "")),
            _catalog_int(reward, "quantity", 1),
        )
        for reward in row.get("lamp_rewards", ()) or ()
        if isinstance(reward, dict) and reward.get("amount")
    )
    return QuestDefinition(
        id=str(row.get("id")),
        display_name=display_name,
        stages=stages,
        point_reward=_catalog_int(row, "point_reward", 0),
        rewards=item_rewards,
        start_point=str(row.get("start_point", "See the source guide for the start location.")),
        requirements=tuple(str(requirement) for requirement in (row.get("requirements", ()) or ())),
        required_items=(),
        combat=str(row.get("combat", "See the source guide.")),
        source=f"{row.get('source', '')}; {row.get('release_source', '')}",
        journal_stages=_catalog_journal_stages(row, display_name, stages),
        release_date=str(row.get("release_date", "")),
        members=_catalog_bool(row, "members", True),
        difficulty=str(row.get("difficulty", "Novice")),
        length=length,
        timeline=str(row.get("timeline", "Fifth Age")),
        required_quests=required_quests,
        required_skills=required_skills,
        required_quest_points=_catalog_int(row, "required_quest_points", 0),
        xp_rewards=xp_rewards,
        lamp_rewards=lamp_rewards,
        unlocks=tuple(str(unlock) for unlock in (row.get("unlocks", ()) or ())),
        release_order=_catalog_int(row, "release_order", 9999),
        stage_requirements=_catalog_stage_requirements(row.get("stage_requirements", ())),
    )


def _quest_catalog_row_id(row: Dict[str, object]) -> str:
    return str(row.get("id", ""))


def _dedupe_stage_requirements(requirements: Tuple[QuestStageRequirement, ...]) -> Tuple[QuestStageRequirement, ...]:
    seen = set()
    rows = []
    for requirement in sorted(requirements, key=lambda row: (row.stage, row.description, row.source)):
        key = (
            requirement.stage,
            requirement.description,
            requirement.required_inventory,
            requirement.required_inventory_options,
            requirement.consumed_inventory,
            requirement.required_tools,
            requirement.required_actions,
            requirement.required_routes,
            tuple(encounter.encounter_id for encounter in requirement.combat_encounters),
            requirement.source,
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(requirement)
    return tuple(rows)


def _apply_combat_encounter_replacements(
    quest_id: str,
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    replacements = QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID.get(quest_id, {})
    if not replacements:
        return requirements
    changed = False
    rows = []
    for requirement in requirements:
        replacement_rows = []
        for encounter in requirement.combat_encounters:
            replacement = replacements.get(encounter.encounter_id)
            if replacement is None:
                replacement_rows.append(encounter)
            elif isinstance(replacement, tuple):
                replacement_rows.extend(replacement)
            else:
                replacement_rows.append(replacement)
        combat_encounters = tuple(replacement_rows)
        if combat_encounters != requirement.combat_encounters:
            changed = True
            requirement = replace(requirement, combat_encounters=combat_encounters)
        rows.append(requirement)
    return tuple(rows) if changed else requirements


def _quest_with_stage_requirements(quest: QuestDefinition, row: Dict[str, object]) -> QuestDefinition:
    replacements = QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID.get(quest.id)
    if replacements is not None:
        base = replacements
    elif quest.stage_requirements:
        base = quest.stage_requirements
    else:
        base = _catalog_stage_requirements(row.get("stage_requirements", ()))

    additions = QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID.get(quest.id, ())
    requirements = _apply_combat_encounter_replacements(
        quest.id,
        _dedupe_stage_requirements((*base, *additions)),
    )
    if requirements == quest.stage_requirements:
        return quest
    return replace(quest, stage_requirements=requirements)


QUESTS: Tuple[QuestDefinition, ...] = tuple(
    _quest_with_stage_requirements(
        replace(QUEST_OVERRIDES_BY_ID[row_id], release_order=_catalog_int(row, "release_order", 9999))
        if row_id in QUEST_OVERRIDES_BY_ID
        else _quest_from_catalog(row),
        row,
    )
    for row in PRE_EOC_QUEST_CATALOG
    for row_id in (_quest_catalog_row_id(row),)
)
QUESTS_BY_ID: Dict[str, QuestDefinition] = {quest.id: quest for quest in QUESTS}
QUEST_DISPLAY_NAMES: Dict[str, str] = {quest.id: quest.display_name for quest in QUESTS}

# Compatibility export retained for callers that were added during the first
# quest-lock pass. Unlock quest ids now all resolve to playable QuestDefinition
# rows, so there are no state-only references left.
QUEST_REFERENCES: Tuple[QuestReference, ...] = ()
QUEST_REFERENCES_BY_ID: Dict[str, QuestReference] = {}

QUEST_UNLOCK_RULES: Tuple[QuestUnlockRule, ...] = (
    QuestUnlockRule(RUNE_MYSTERIES_ID, "target", "mining", ("rune_essence",), "Rune Mysteries", RUNE_ESSENCE_MINE_SOURCE),
    QuestUnlockRule(
        LOST_CITY_ID,
        "target",
        "runecrafting",
        ("craft_cosmic_runes", "bind_cosmic_tiara", "feed_cosmic_talisman_to_hood", "feed_cosmic_tiara_to_hood"),
        "Lost City",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(LUNAR_DIPLOMACY_ID, "target", "runecrafting", ("craft_astral_runes",), "Lunar Diplomacy", RUNECRAFTING_ALTARS_SOURCE),
    QuestUnlockRule(
        MOURNINGS_END_PART_II_ID,
        "target",
        "runecrafting",
        ("craft_death_runes", "bind_death_tiara", "feed_death_talisman_to_hood", "feed_death_tiara_to_hood"),
        "Mourning's End Part II",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(
        LEGACY_OF_SEERGAZE_ID,
        "target",
        "runecrafting",
        ("craft_blood_runes", "bind_blood_tiara", "feed_blood_talisman_to_hood", "feed_blood_tiara_to_hood"),
        "Legacy of Seergaze",
        RUNECRAFTING_BASICS_SOURCE,
    ),
    QuestUnlockRule(SWAN_SONG_ID, "target", "fishing", ("catch_monkfish",), "Swan Song", RAW_MONKFISH_SOURCE),
    QuestUnlockRule(TAI_BWO_WANNAI_TRIO_ID, "target", "fishing", ("catch_karambwan",), "Tai Bwo Wannai Trio", RAW_KARAMBWAN_SOURCE),
    QuestUnlockRule(SHILO_VILLAGE_ID, "target", "mining", ("gem_rocks",), "Shilo Village", GEM_ROCK_SOURCE),
    QuestUnlockRule(PRIEST_IN_PERIL_ID, "target", "fishing", ("catch_slimy_eel",), "Priest in Peril", PRIEST_IN_PERIL_SOURCE),
    QuestUnlockRule(
        PRIEST_IN_PERIL_ID,
        "target",
        "cooking",
        ("cook_slimy_eel", "cook_thin_snail", "cook_lean_snail", "cook_fat_snail"),
        "Priest in Peril",
        PRIEST_IN_PERIL_SOURCE,
    ),
    QuestUnlockRule(
        PRIEST_IN_PERIL_ID,
        "target",
        "utility",
        ("gather_thin_snails", "gather_lean_snails", "gather_fat_snails"),
        "Priest in Peril",
        PRIEST_IN_PERIL_SOURCE,
    ),
    QuestUnlockRule(THE_FREMENNIK_ISLES_ID, "target", "firemaking", ("arctic_pine_logs",), "The Fremennik Isles", THE_FREMENNIK_ISLES_SOURCE),
    QuestUnlockRule(THE_FREMENNIK_ISLES_ID, "target", "cooking", ("cook_yak",), "The Fremennik Isles", THE_FREMENNIK_ISLES_SOURCE),
    QuestUnlockRule(THE_FREMENNIK_ISLES_ID, "target", "utility", ("scavenge_raw_yak_meat",), "The Fremennik Isles", THE_FREMENNIK_ISLES_SOURCE),
    QuestUnlockRule(EAGLES_PEAK_ID, "target", "hunter", ("catch_ferret",), "Eagles' Peak", HUNTER_EAGLES_PEAK_SOURCE),
    QuestUnlockRule(AS_A_FIRST_RESORT_ID, "target", "hunter", ("catch_wimpy_bird",), "As a First Resort", HUNTER_AS_A_FIRST_RESORT_SOURCE),
    QuestUnlockRule(ROCKING_OUT_ID, "target", "hunter", ("catch_pirate_impling_puro_puro", "catch_pirate_impling_world"), "Rocking Out", HUNTER_ROCKING_OUT_SOURCE),
    QuestUnlockRule(PRIEST_IN_PERIL_ID, "target", "hunter", ("catch_swamp_lizard",), "Priest in Peril", HUNTER_PRIEST_IN_PERIL_SOURCE),
)


def _quest_target_unlock_rule(rule: QuestUnlockRule) -> TargetUnlockRule:
    return TargetUnlockRule(
        gate_kind=rule.gate_kind,
        skill_id=rule.skill_id,
        target_ids=rule.target_ids,
        requirements=(
            TargetUnlockRequirement(
                kind="quest_completed",
                reason=rule.reason,
                source=rule.source,
                quest_id=rule.quest_id,
            ),
        ),
    )


TARGET_UNLOCK_RULES: Tuple[TargetUnlockRule, ...] = tuple(
    _quest_target_unlock_rule(rule) for rule in QUEST_UNLOCK_RULES
) + (
    TargetUnlockRule(
        gate_kind="target",
        skill_id="fletching",
        target_ids=("broad_arrows", "feather_broad_bolts"),
        requirements=(
            TargetUnlockRequirement(
                kind="ability_unlocked",
                reason="Broad Fletching",
                source=BROAD_FLETCHING_SOURCE,
                ability_id=BROAD_FLETCHING_ABILITY,
            ),
        ),
    ),
    TargetUnlockRule(
        gate_kind="target",
        skill_id="fishing",
        target_ids=("catch_leaping_fish",),
        requirements=(
            TargetUnlockRequirement(
                kind="ability_unlocked",
                reason="Barbarian Fishing",
                source=BARBARIAN_FISHING_SOURCE,
                ability_id=BARBARIAN_FISHING_ABILITY,
            ),
        ),
    ),
)


def _lamp_claim_id(quest: QuestDefinition, index: int) -> str:
    return f"{quest.id}_xp_lamp_{index}"


def _quest_lamp_claims() -> Tuple[ClaimDefinition, ...]:
    claims = []
    for quest in QUESTS:
        lamp_index = 1
        for lamp in quest.lamp_rewards:
            if lamp.amount <= 0 or not lamp.skill_options:
                continue
            for _ in range(max(1, int(lamp.quantity))):
                claims.append(
                    ClaimDefinition(
                        id=_lamp_claim_id(quest, lamp_index),
                        display_name=f"{quest.display_name}: {lamp.display_name} ({int(lamp.amount):,} XP)",
                        source=lamp.source or quest.source,
                        claim_type="xp_lamp",
                        required_quest=quest.id,
                        xp_amount=lamp.amount,
                        skill_options=lamp.skill_options,
                        minimum_level=max(1, int(lamp.minimum_level)),
                    )
                )
                lamp_index += 1
    return tuple(claims)


CLAIMS: Tuple[ClaimDefinition, ...] = (
    ClaimDefinition(
        id="wicked_hood",
        display_name="Wicked hood",
        source="https://runescape.wiki/w/Wicked_hood",
        item_name=WICKED_HOOD_ITEM,
        quantity=1,
    ),
    *_quest_lamp_claims(),
)
CLAIMS_BY_ID: Dict[str, ClaimDefinition] = {claim.id: claim for claim in CLAIMS}


def default_quest_states() -> Dict[str, Dict[str, object]]:
    return {quest.id: {"started": False, "progress": 0, "completed": False} for quest in QUESTS}


def default_claim_states() -> Dict[str, Dict[str, object]]:
    return {claim.id: {"claimed": False} for claim in CLAIMS}


def _quest_requirement_dict(requirement: QuestPrerequisite) -> Dict[str, object]:
    return {"quest_id": requirement.quest_id, "display_name": requirement.display_name}


def _skill_requirement_dict(requirement: QuestSkillRequirement) -> Dict[str, object]:
    return {"skill_id": requirement.skill_id, "display_name": requirement.display_name, "level": requirement.level}


def _xp_reward_dict(reward: QuestXpReward) -> Dict[str, object]:
    return {"skill_id": reward.skill_id, "amount": reward.amount}


def _lamp_reward_dict(reward: QuestLampReward) -> Dict[str, object]:
    return {
        "display_name": reward.display_name,
        "amount": reward.amount,
        "skill_options": reward.skill_options,
        "minimum_level": reward.minimum_level,
        "source": reward.source,
        "source_text": reward.source_text,
        "quantity": reward.quantity,
    }


def _combat_encounter_dict(encounter: QuestCombatEncounter) -> Dict[str, object]:
    return {
        "encounter_id": encounter.encounter_id,
        "display_name": encounter.display_name,
        "level": encounter.level,
        "quantity": encounter.quantity,
        "source": encounter.source,
        "source_text": encounter.source_text,
        "npc_stats": dict(encounter.npc_stats),
        "npc_bonuses": dict(encounter.npc_bonuses),
        "npc_configs": dict(encounter.npc_configs),
        "npc_stats_source": encounter.npc_stats_source,
    }


def _stage_requirement_dict(requirement: QuestStageRequirement) -> Dict[str, object]:
    return {
        "stage": requirement.stage,
        "description": requirement.description,
        "required_inventory": dict(requirement.required_inventory),
        "required_inventory_options": tuple(
            tuple({item_name: amount} for item_name, amount in option_group)
            for option_group in requirement.required_inventory_options
        ),
        "consumed_inventory": dict(requirement.consumed_inventory),
        "required_tools": dict(requirement.required_tools),
        "required_actions": requirement.required_actions,
        "required_routes": requirement.required_routes,
        "combat_encounters": tuple(_combat_encounter_dict(encounter) for encounter in requirement.combat_encounters),
        "source": requirement.source,
    }


def quests_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {
            "id": quest.id,
            "display_name": quest.display_name,
            "stages": quest.stages,
            "point_reward": quest.point_reward,
            "rewards": dict(quest.rewards),
            "start_point": quest.start_point,
            "requirements": quest.requirements,
            "required_items": dict(quest.required_items),
            "required_quests": tuple(_quest_requirement_dict(req) for req in quest.required_quests),
            "required_skills": tuple(_skill_requirement_dict(req) for req in quest.required_skills),
            "required_quest_points": quest.required_quest_points,
            "xp_rewards": tuple(_xp_reward_dict(reward) for reward in quest.xp_rewards),
            "lamp_rewards": tuple(_lamp_reward_dict(reward) for reward in quest.lamp_rewards),
            "combat": quest.combat,
            "source": quest.source,
            "release_date": quest.release_date,
            "release_order": quest.release_order,
            "members": quest.members,
            "difficulty": quest.difficulty,
            "length": quest.length,
            "timeline": quest.timeline,
            "unlocks": quest.unlocks,
            "journal_stages": {stage.stage: stage.journal for stage in quest.journal_stages},
            "stage_requirements": tuple(_stage_requirement_dict(req) for req in quest.stage_requirements),
        }
        for quest in QUESTS
    }


def quest_references_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {"id": quest.id, "display_name": quest.display_name, "source": quest.source, "note": quest.note}
        for quest in QUEST_REFERENCES
    }


def target_unlock_rules_as_dict() -> Tuple[Dict[str, object], ...]:
    return tuple(
        {
            "gate_kind": rule.gate_kind,
            "skill_id": rule.skill_id,
            "target_ids": rule.target_ids,
            "requirements": tuple(
                {
                    "kind": requirement.kind,
                    "quest_id": requirement.quest_id,
                    "ability_id": requirement.ability_id,
                    "reason": requirement.reason,
                    "source": requirement.source,
                }
                for requirement in rule.requirements
            ),
        }
        for rule in TARGET_UNLOCK_RULES
    )


def quest_unlock_rules_as_dict() -> Tuple[Dict[str, object], ...]:
    return target_unlock_rules_as_dict()


def quest_reward_items_as_dict() -> Dict[str, Dict[str, object]]:
    generated_items: Dict[str, Dict[str, object]] = {}
    for row in PRE_EOC_QUEST_CATALOG:
        for reward in row.get("item_rewards", ()) or ():
            if not isinstance(reward, dict):
                continue
            item_name = _quest_reward_item_name(reward.get("item_name"))
            if not isinstance(item_name, str) or not item_name:
                continue
            generated_items[item_name] = {
                "category": str(reward.get("category", "material")),
                "source": str(reward.get("source", row.get("reward_source", row.get("source", "")))),
            }
    generated_items.update({
        "Coins": {"category": "material", "source": "RuneScape currency"},
        "Dramen staff": {"category": "material", "source": LOST_CITY_SOURCE_PATH},
        "Rune spear (kp)": {"category": "equipment", "source": TAI_BWO_WANNAI_TRIO_SOURCE},
        "Ivandis flail": {"category": "equipment", "source": LEGACY_OF_SEERGAZE_SOURCE},
        "Tome of Experience, 2nd Ed.": {"category": "material", "source": LEGACY_OF_SEERGAZE_SOURCE},
    })
    return generated_items


def claims_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        claim.id: {
            "id": claim.id,
            "display_name": claim.display_name,
            "claim_type": claim.claim_type,
            "item_name": claim.item_name,
            "quantity": claim.quantity,
            "source": claim.source,
            "required_quest": claim.required_quest,
            "required_runecrafting_level": claim.required_runecrafting_level,
            "xp_amount": claim.xp_amount,
            "skill_options": claim.skill_options,
            "minimum_level": claim.minimum_level,
        }
        for claim in CLAIMS
    }
