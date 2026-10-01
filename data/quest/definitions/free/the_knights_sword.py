from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

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

QUEST = QuestDefinition(
        id=THE_KNIGHTS_SWORD_ID,
        display_name="The Knight's Sword",
        stage_count=7,
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
    )

__all__ = (
    'KNIGHTS_SWORD_STAGES', 'KNIGHTS_SWORD_STAGE_REQUIREMENTS',
)
