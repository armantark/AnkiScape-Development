from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

MONKS_FRIEND_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Brother Omad needs the child's blanket recovered from the thieves' hideout."),
    _simple_stage(2, "I recovered the child's blanket and should return it to Brother Omad."),
    _simple_stage(3, "Brother Omad can tell me what else is needed for the birthday party."),
    _simple_stage(4, "Brother Cedric is lost outside the monastery and needs a jug of water."),
    _simple_stage(5, "Brother Cedric needs logs to repair his cart."),
    _simple_stage(6, "Brother Cedric is returning. I should tell Brother Omad and join the party."),
    _simple_stage(7, "Brother Omad's party is underway.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    MONKS_FRIEND_ID: (
        _stage_req(
            1,
            "Recover the child's blanket from the thieves' hideout.",
            f"{DARKAN_MONKS_FRIEND_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Child's blanket", 1),),
            auto_actions=("Recover the child's blanket from the thieves' hideout",),
        ),
        _stage_req(
            2,
            "Return the child's blanket to Brother Omad.",
            f"{DARKAN_MONKS_FRIEND_SOURCE}; {DARKAN_MONKS_FRIEND_OMAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Child's blanket", 1),),
        ),
        _stage_req(
            3,
            "Ask Brother Omad about Brother Cedric and the party.",
            DARKAN_MONKS_FRIEND_OMAD_SOURCE,
            auto_actions=("Ask Brother Omad about Brother Cedric and the party",),
        ),
        _stage_req(
            4,
            "Give Brother Cedric a jug of water.",
            f"{DARKAN_MONKS_FRIEND_CEDRIC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Jug of water", 1),),
        ),
        _stage_req(
            5,
            "Give Brother Cedric logs to repair his cart.",
            f"{DARKAN_MONKS_FRIEND_CEDRIC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Logs", 1),),
        ),
        _stage_req(
            6,
            "Return to Brother Omad and join the birthday party.",
            DARKAN_MONKS_FRIEND_OMAD_SOURCE,
            auto_actions=("Return to Brother Omad and join the birthday party",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Child's blanket": {
            "category": "material",
            "source": f"{DARKAN_MONKS_FRIEND_OMAD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Jug of water": {
            "category": "material",
            "source": f"{DARKAN_MONKS_FRIEND_CEDRIC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'MONKS_FRIEND_STAGES',
)
