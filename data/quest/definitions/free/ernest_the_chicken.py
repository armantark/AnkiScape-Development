from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

ERNEST_THE_CHICKEN_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Veronica asked me to find Ernest inside Draynor Manor."),
    _simple_stage(2, "Professor Oddenstein says Ernest has been turned into a chicken."),
    _simple_stage(3, "Oddenstein needs his pressure gauge, rubber tube, and oil can to repair the machine."),
    _simple_stage(4, "I poisoned the fish food and can use it on the manor fountain."),
    _simple_stage(5, "I recovered the pressure gauge from the fountain."),
    _simple_stage(6, "A grimy key from the compost heap should open the room with the rubber tube."),
    _simple_stage(7, "I recovered the rubber tube from the locked room."),
    _simple_stage(8, "I recovered the oil can from the basement puzzle and should return all three parts to Oddenstein."),
    _simple_stage(9, "Professor Oddenstein restored Ernest and rewarded me.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=ERNEST_THE_CHICKEN_ID,
        display_name="Ernest the Chicken",
        stages=9,
        point_reward=4,
        rewards=(("Coins", 3000), ("Egg", 10), ("Feather", 300)),
        start_point="Talk to Veronica south of Draynor Manor's gates.",
        requirements=(
            "Used during quest: Fish food x1, Poison x1, Spade x1",
        ),
        required_items=(),
        combat="None required; dangerous manor enemies are avoidable.",
        source=f"{DARKAN_ERNEST_SOURCE}; {DARKAN_ERNEST_ODDENSTEIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        journal_stages=ERNEST_THE_CHICKEN_STAGES,
        release_date="2001-01-21",
        members=False,
        difficulty="Novice",
        length="Medium",
        timeline="Fifth Age",
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    ERNEST_THE_CHICKEN_ID: (
        _stage_req(
            1,
            "Find Professor Oddenstein and learn what happened to Ernest.",
            f"{DARKAN_ERNEST_SOURCE}; {DARKAN_ERNEST_ODDENSTEIN_SOURCE}",
            auto_actions=("Ask Professor Oddenstein about Ernest",),
        ),
        _stage_req(
            2,
            "Agree to retrieve Oddenstein's missing machine parts.",
            f"{DARKAN_ERNEST_ODDENSTEIN_SOURCE}",
            auto_actions=("Agree to retrieve Oddenstein's machine parts",),
        ),
        _stage_req(
            3,
            "Mix fish food with poison for the manor fountain.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Fish food", 1), ("Poison", 1)),
            produced_inventory=(("Poisoned fish food", 1),),
        ),
        _stage_req(
            4,
            "Use poisoned fish food on the fountain and recover the pressure gauge.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Poisoned fish food", 1),),
            produced_inventory=(("Pressure gauge", 1),),
        ),
        _stage_req(
            5,
            "Dig in the compost heap with a spade to find the grimy key.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Spade", 1),),
            produced_inventory=(("Grimy key", 1),),
        ),
        _stage_req(
            6,
            "Use the grimy key to reach and recover the rubber tube.",
            f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Grimy key", 1),),
            produced_inventory=(("Rubber tube", 1),),
        ),
        _stage_req(
            7,
            "Solve the basement lever puzzle and recover the oil can.",
            (
                f"{DARKAN_ERNEST_SOURCE}; {DARKAN_ERNEST_SOURCE_ROOT}/PuzzleRoom.java; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=("Solve the Draynor Manor basement lever puzzle",),
            produced_inventory=(("Oil can", 1),),
        ),
        _stage_req(
            8,
            "Give Oddenstein the pressure gauge, rubber tube, and oil can.",
            f"{DARKAN_ERNEST_ODDENSTEIN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Pressure gauge", 1), ("Rubber tube", 1), ("Oil can", 1)),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Fish food": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Poison": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Poisoned fish food": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pressure gauge": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Grimy key": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Rubber tube": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Oil can": {
            "category": "material",
            "source": f"{DARKAN_ERNEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'ERNEST_THE_CHICKEN_STAGES',
)
