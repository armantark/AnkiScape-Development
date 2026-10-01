from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

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

QUEST = QuestDefinition(
        id=LUNAR_DIPLOMACY_ID,
        display_name="Lunar Diplomacy",
        stage_count=8,
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
    )

__all__ = (
    'LUNAR_DIPLOMACY_STAGES',
)
