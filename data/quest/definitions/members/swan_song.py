from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

SWAN_SONG_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Herman Caranos needs help defending the Piscatoris Fishing Colony."),
    _simple_stage(2, "I recruited the Wise Old Man for one last adventure."),
    _simple_stage(3, "We repaired the colony and prepared for the sea troll attack."),
    _simple_stage(4, "I fought through the sea trolls attacking the colony."),
    _simple_stage(5, "The Sea Troll Queen was defeated and the colony was saved."),
    _simple_stage(6, "Piscatoris is secure and the monkfish grounds are available.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=SWAN_SONG_ID,
        display_name="Swan Song",
        stage_count=6,
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
    )

__all__ = (
    'SWAN_SONG_STAGES',
)
