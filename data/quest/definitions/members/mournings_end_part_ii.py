from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

MOURNINGS_END_PART_II_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The head mourner has opened the route toward the excavation below West Ardougne."),
    _simple_stage(2, "I entered the Temple of Light beneath Arandar."),
    _simple_stage(3, "I worked through the temple mirrors and coloured light beams."),
    _simple_stage(4, "I reached the death altar deep in the temple."),
    _simple_stage(5, "I uncovered the mourners' plan and secured a death talisman."),
    _simple_stage(6, "I escaped the temple and returned with news of what I found."),
    _simple_stage(7, "The path to the death altar is open.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=MOURNINGS_END_PART_II_ID,
        display_name="Mourning's End Part II",
        stage_count=7,
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
    )

__all__ = (
    'MOURNINGS_END_PART_II_STAGES',
)
