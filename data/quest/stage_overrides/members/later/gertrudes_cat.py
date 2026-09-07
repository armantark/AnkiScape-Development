from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

GERTRUDES_CAT_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Gertrude asked me to find Shilop and Wilough in Varrock Marketplace."),
    _simple_stage(2, "Shilop and Wilough know where Fluffs is hiding, but they want coins."),
    _simple_stage(3, "Fluffs is in the Lumber Yard and will not come down yet."),
    _simple_stage(4, "Fluffs is thirsty and needs milk."),
    _simple_stage(5, "Fluffs is still hungry. Doogle leaves can season a raw sardine."),
    _simple_stage(6, "I made a doogle sardine and should feed it to Fluffs."),
    _simple_stage(7, "Fluffs is worried about her kittens somewhere in the Lumber Yard."),
    _simple_stage(8, "I found the kittens and need to return them to Fluffs."),
    _simple_stage(9, "Fluffs has gone home. Gertrude should hear what happened."),
    _simple_stage(10, "Gertrude gave me a kitten.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    GERTRUDES_CAT_ID: (
        _stage_req(
            1,
            "Speak to Shilop or Wilough in Varrock Marketplace.",
            DARKAN_GERTRUDES_CAT_GERTRUDE_SOURCE,
            auto_actions=("Speak to Shilop and Wilough in Varrock Marketplace",),
        ),
        _stage_req(
            2,
            "Pay Shilop and Wilough for Fluffs' location.",
            DARKAN_GERTRUDES_CAT_CHILDREN_SOURCE,
            consumed_inventory=(("Coins", 100),),
        ),
        _stage_req(
            3,
            "Find Fluffs in the Lumber Yard and learn she is thirsty.",
            DARKAN_GERTRUDES_CAT_SOURCE,
            auto_actions=(
                "Reach Fluffs in the Varrock Lumber Yard",
                "Try to pick up Fluffs in the Lumber Yard",
            ),
        ),
        _stage_req(
            4,
            "Give Fluffs a bucket of milk.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bucket of milk", 1),),
            produced_inventory=(("Bucket", 1),),
        ),
        _stage_req(
            5,
            "Season a raw sardine with doogle leaves.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Raw sardine", 1), ("Doogle leaves", 1)),
            produced_inventory=(("Doogle sardine", 1),),
        ),
        _stage_req(
            6,
            "Feed Fluffs the doogle sardine.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Doogle sardine", 1),),
        ),
        _stage_req(
            7,
            "Find Fluffs' kittens in the Lumber Yard.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Search the shaking crate for Fluffs' kittens",),
            produced_inventory=(("Three little kittens", 1),),
        ),
        _stage_req(
            8,
            "Return Fluffs' kittens to her.",
            f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Three little kittens", 1),),
        ),
        _stage_req(
            9,
            "Tell Gertrude that Fluffs and the kittens are safe.",
            DARKAN_GERTRUDES_CAT_GERTRUDE_SOURCE,
            auto_actions=("Tell Gertrude that Fluffs and the kittens are safe",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Bucket of milk": {
            "category": "material",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Doogle leaves": {
            "category": "material",
            "item_id": 1573,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{GERTRUDES_CAT_WIKI_SOURCE}; {DARKAN_GERTRUDES_CAT_SOURCE}; "
                f"{DARKAN_GERTRUDES_CAT_GERTRUDE_SOURCE}; "
                "OpenRS2 cache rev 727 and rev-742 item 1573"
            ),
        },
        "Doogle sardine": {
            "category": "food",
            "item_id": 1552,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{GERTRUDES_CAT_WIKI_SOURCE}; {DARKAN_GERTRUDES_CAT_SOURCE}; "
                "OpenRS2 cache rev 727 and rev-742 item 1552"
            ),
        },
        "Three little kittens": {
            "category": "material",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pet kitten": {
            "category": "material",
            "source": f"{DARKAN_GERTRUDES_CAT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'GERTRUDES_CAT_STAGES',
)
