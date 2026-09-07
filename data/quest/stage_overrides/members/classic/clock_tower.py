from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

CLOCK_TOWER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Brother Kojo needs the Clock Tower's missing cogs replaced."),
    _simple_stage(2, "I found rat poison in the Clock Tower dungeon and should use it on the rats."),
    _simple_stage(3, "The dungeon rats are dealt with. I need to find the four cogs."),
    _simple_stage(4, "I found the four cogs. They need to be placed on their matching spindles."),
    _simple_stage(5, "The clock is repaired. I should report back to Brother Kojo."),
    _simple_stage(6, "Brother Kojo rewarded me for repairing the tower.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    CLOCK_TOWER_ID: (
        _stage_req(
            1,
            "Find rat poison in the Clock Tower dungeon.",
            f"{DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Pick up rat poison in the Clock Tower dungeon",),
            produced_inventory=(("Rat poison", 1),),
        ),
        _stage_req(
            2,
            "Poison the Clock Tower dungeon rats to open the blocked door.",
            f"{DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Rat poison", 1),),
            auto_actions=("Poison the Clock Tower dungeon rats",),
        ),
        _stage_req(
            3,
            "Find the four Clock Tower cogs.",
            f"{DARKAN_CLOCK_TOWER_SOURCE}; {DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Find the white, black, blue, and red Clock Tower cogs",),
            produced_inventory=(("White cog", 1), ("Black cog", 1), ("Blue cog", 1), ("Red cog", 1)),
        ),
        _stage_req(
            4,
            "Place the four Clock Tower cogs on their matching spindles.",
            f"{DARKAN_CLOCK_TOWER_SOURCE}; {DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory_options=(((("Bucket of water", 1), ("Ice gloves", 1)),)),
            consumed_inventory=(("White cog", 1), ("Black cog", 1), ("Blue cog", 1), ("Red cog", 1)),
            auto_actions=("Place the four Clock Tower cogs",),
        ),
        _stage_req(
            5,
            "Report the repaired clock to Brother Kojo.",
            DARKAN_CLOCK_TOWER_KOJO_SOURCE,
            auto_actions=("Report the repaired clock to Brother Kojo",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "White cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blue cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Red cog": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Rat poison": {
            "category": "material",
            "source": f"{DARKAN_CLOCK_TOWER_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'CLOCK_TOWER_STAGES',
)
