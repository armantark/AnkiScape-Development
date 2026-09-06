from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

BLACK_KNIGHTS_FORTRESS_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Sir Amik Varze asked me to infiltrate the Black Knights' Fortress."),
    _simple_stage(2, "I entered the fortress in disguise and need to learn the Black Knights' plan."),
    _simple_stage(3, "The Black Knights' potion can be ruined by dropping the wrong cabbage into the cauldron."),
    _simple_stage(4, "The potion is ruined. I should report back to Sir Amik Varze."),
    _simple_stage(5, "Sir Amik Varze rewarded me for stopping the Black Knights.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=BLACK_KNIGHTS_FORTRESS_ID,
        display_name="Black Knights' Fortress",
        stages=5,
        point_reward=3,
        rewards=(("Coins", 2500),),
        start_point="Speak to Sir Amik Varze on the 3rd floor of the White Knights' Castle's western tower.",
        requirements=("12 Quest Points", "Used during quest: Iron chainbody x1, Bronze med helm x1, Cabbage x1"),
        required_items=(),
        combat="Ability to evade level 33 Black Knights; no required kill.",
        source=f"{DARKAN_BLACK_KNIGHTS_SOURCE}; {DARKAN_BLACK_KNIGHTS_SIR_AMIK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        journal_stages=BLACK_KNIGHTS_FORTRESS_STAGES,
        release_date="2001-04-06",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        required_quest_points=12,
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    BLACK_KNIGHTS_FORTRESS_ID: (
        _stage_req(
            1,
            "Enter the Black Knights' Fortress in disguise.",
            f"{DARKAN_BLACK_KNIGHTS_SOURCE}; {DARKAN_BLACK_KNIGHTS_SIR_AMIK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Iron chainbody", 1), ("Bronze med helm", 1)),
            auto_actions=("Infiltrate the Black Knights' Fortress",),
        ),
        _stage_req(
            2,
            "Listen at the grill and learn about the invincibility potion.",
            DARKAN_BLACK_KNIGHTS_SOURCE,
            auto_actions=("Listen at the grill above the Black Knights' meeting",),
        ),
        _stage_req(
            3,
            "Drop a non-Draynor cabbage into the cauldron through the floor hole.",
            DARKAN_BLACK_KNIGHTS_SOURCE,
            consumed_inventory=(("Cabbage", 1),),
        ),
        _stage_req(
            4,
            "Report the ruined potion to Sir Amik Varze.",
            DARKAN_BLACK_KNIGHTS_SIR_AMIK_SOURCE,
            auto_actions=("Report the ruined potion to Sir Amik Varze",),
        ),
    ),
}

__all__ = (
    'BLACK_KNIGHTS_FORTRESS_STAGES',
)
