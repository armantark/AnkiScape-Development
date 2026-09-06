from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

FISHING_CONTEST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Austri or Vestri can give me a pass for the Hemenster Fishing Contest."),
    _simple_stage(2, "I have a fishing pass and need to enter the contest."),
    _simple_stage(3, "The contest has started. I need to move the stranger away from the best fishing spot."),
    _simple_stage(4, "The stranger left the best spot. I need to catch the winning fish."),
    _simple_stage(5, "I caught a raw giant carp and should claim the trophy from Bonzo."),
    _simple_stage(6, "I have the fishing trophy and should return it to the dwarf brothers."),
    _simple_stage(7, "The dwarf brothers opened the White Wolf Mountain shortcut.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    FISHING_CONTEST_ID: (
        _stage_req(
            1,
            "Receive a fishing pass from Austri or Vestri.",
            f"{DARKAN_FISHING_CONTEST_SOURCE}; {DARKAN_FISHING_CONTEST_DWARF_BROTHERS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Receive a fishing pass from Austri or Vestri",),
            produced_inventory=(("Fishing pass", 1),),
        ),
        _stage_req(
            2,
            "Show the fishing pass and pay Bonzo's contest entry fee.",
            f"{DARKAN_FISHING_CONTEST_MORRIS_SOURCE}; {DARKAN_FISHING_CONTEST_BONZO_SOURCE}",
            required_inventory=(("Fishing pass", 1),),
            consumed_inventory=(("Coins", 5),),
        ),
        _stage_req(
            3,
            "Put garlic in the pipe beside the stranger's fishing spot.",
            f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Garlic", 1),),
        ),
        _stage_req(
            4,
            "Catch the winning giant carp at Hemenster.",
            (
                f"{DARKAN_FISHING_CONTEST_SOURCE}; {DARKAN_FISHING_CONTEST_GRANDPA_JACK_SOURCE}; "
                f"{DARKAN_FISHING_SKILL_SOURCE}; {DARKAN_FISHING_FISH_SOURCE}; "
                f"{DARKAN_FISHING_SPOT_SOURCE}; {DARKAN_FISHING_CONTEST_WIKI_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory_options=((("Red vine worm", 1), ("Fishing bait", 1)),),
            produced_inventory=(("Raw giant carp", 1),),
            required_tools=(("Fishing rod", 1),),
            auto_actions=("Catch the winning giant carp",),
        ),
        _stage_req(
            5,
            "Claim the Hemenster fishing trophy from Bonzo.",
            f"{DARKAN_FISHING_CONTEST_BONZO_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Raw giant carp", 1),),
            produced_inventory=(("Fishing trophy", 1),),
        ),
        _stage_req(
            6,
            "Give the fishing trophy to Austri or Vestri.",
            f"{DARKAN_FISHING_CONTEST_DWARF_BROTHERS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Fishing trophy", 1),),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Fishing pass": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Red vine worm": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Raw giant carp": {
            "category": "fish",
            "source": f"{DARKAN_FISHING_FISH_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Fishing trophy": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_BONZO_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Garlic": {
            "category": "material",
            "source": f"{DARKAN_FISHING_CONTEST_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Fishing rod": {
            "category": "tool",
            "source": f"{DARKAN_FISHING_SPOT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'FISHING_CONTEST_STAGES',
)
