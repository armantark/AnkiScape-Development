"""Quest and one-time claim data for AnkiScape."""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Dict, Tuple

try:
    from .quest_catalog_generated import PRE_EOC_QUEST_CATALOG
except ImportError:  # pragma: no cover
    from quest_catalog_generated import PRE_EOC_QUEST_CATALOG  # type: ignore

try:
    from .runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM
except ImportError:  # pragma: no cover
    from runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM  # type: ignore


RUNE_MYSTERIES_ID = "rune_mysteries"
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
RUNE_MYSTERIES_RELEASE_SOURCE = "https://runescape.salmoneus.net/runescape-2007/quests/rune-mysteries.html"
RUNECRAFTING_BASICS_SOURCE = "https://www.2011.rs/kb/runecrafting_the_basics"
RUNECRAFTING_ALTARS_SOURCE = "https://www.2011.rs/kb/runecrafting_locating_the_altars"
RUNE_ESSENCE_MINE_SOURCE = "https://www.2011.rs/kb/mining_the_rune_essence_mine"
RAW_MONKFISH_SOURCE = "https://runescape.fandom.com/wiki/Raw_monkfish"
RAW_KARAMBWAN_SOURCE = "https://runescape.fandom.com/wiki/Raw_karambwan"
GEM_ROCK_SOURCE = "https://runescape.wiki/w/Gem_rock?oldid=37044944"
PRIEST_IN_PERIL_ID = "priest_in_peril"
PRIEST_IN_PERIL_SOURCE = "https://runescape.wiki/w/Priest_in_Peril?oldid=6487728"
THE_FREMENNIK_ISLES_ID = "the_fremennik_isles"
THE_FREMENNIK_ISLES_SOURCE = "https://runescape.wiki/w/The_Fremennik_Isles?oldid=6540919"

QUEST_REWARD_ITEM_NAME_OVERRIDES = {
    "Ring of charos": "Ring of Charos",
}


@dataclass(frozen=True)
class QuestStage:
    stage: int
    journal: Tuple[str, ...]


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
        unlocks=("Ability to craft runes", "Ability to mine rune essence"),
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
    )


def _quest_catalog_row_id(row: Dict[str, object]) -> str:
    return str(row.get("id", ""))


QUESTS: Tuple[QuestDefinition, ...] = tuple(
    replace(QUEST_OVERRIDES_BY_ID[row_id], release_order=_catalog_int(row, "release_order", 9999))
    if row_id in QUEST_OVERRIDES_BY_ID
    else _quest_from_catalog(row)
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
        required_runecrafting_level=5,
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
        }
        for quest in QUESTS
    }


def quest_references_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {"id": quest.id, "display_name": quest.display_name, "source": quest.source, "note": quest.note}
        for quest in QUEST_REFERENCES
    }


def quest_unlock_rules_as_dict() -> Tuple[Dict[str, object], ...]:
    return tuple(
        {
            "quest_id": rule.quest_id,
            "gate_kind": rule.gate_kind,
            "skill_id": rule.skill_id,
            "target_ids": rule.target_ids,
            "reason": rule.reason,
            "source": rule.source,
        }
        for rule in QUEST_UNLOCK_RULES
    )


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
