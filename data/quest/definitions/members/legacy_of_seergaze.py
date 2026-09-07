from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

LEGACY_OF_SEERGAZE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "A mercenary near Paterdomus reported suspicious activity in Morytania."),
    _simple_stage(2, "Drezel's discovery beneath Paterdomus pointed toward the columbarium."),
    _simple_stage(3, "I helped the Myreque investigate the Vyrewatch and Meiyerditch."),
    _simple_stage(4, "I created the Ivandis flail to fight the Vyrewatch."),
    _simple_stage(5, "I performed a cremation rite and recovered a key to the hidden storage."),
    _simple_stage(6, "I found the blood talisman and reported back to the Myreque."),
    _simple_stage(7, "The blood altar and columbarium rewards are now available.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=LEGACY_OF_SEERGAZE_ID,
        display_name="Legacy of Seergaze",
        stages=7,
        point_reward=2,
        rewards=(("Blood talisman", 1), ("Ivandis flail", 1), ("Tome of xp 2nd ed (3)", 1)),
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
        source=f"{LEGACY_OF_SEERGAZE_SOURCE}; {LEGACY_OF_SEERGAZE_REWARD_SOURCE}",
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
    )

_REWARD_ITEM_FRAGMENT_0 = {
        "Ivandis flail": {"category": "equipment", "source": LEGACY_OF_SEERGAZE_SOURCE},
        "Tome of xp 2nd ed (3)": {
            "category": "material",
            "item_id": 13160,
            "stackable": False,
            "tradeable": False,
            "source": LEGACY_OF_SEERGAZE_REWARD_SOURCE,
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'LEGACY_OF_SEERGAZE_STAGES',
)
