from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    SOME_LIKE_IT_COLD_ID: (
        _stage_req(
            1,
            "Reach the seals and learn how to enter the Iceberg.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Speak to Chuck again for teleport", "Entertain the seal", "Travel to the Iceberg"),
        ),
        _stage_req(
            2,
            "Build Ping and Pong's rock costumes.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Build Ping and Pong's rock costumes", "Give Ping and Pong their costumes"),
        ),
        _stage_req(
            3,
            "Infiltrate the Walrus camp and recover the egg.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Distract the Walrus", "Steal the egg from the table"),
        ),
        _stage_req(
            4,
            "Defeat Astoria and repair the submarine engine.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=(
                "Defeat Astoria in Battlefish",
                "Collect camp repair supplies",
                "Repair the submarine engine",
            ),
        ),
        _stage_req(
            5,
            "Defeat the seals in Battlefish.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Defeat the seals in Battlefish",),
        ),
        _stage_req(
            6,
            "Escape the Walrus camp.",
            SOME_LIKE_IT_COLD_WIKI_SOURCE,
            auto_actions=("Escape in the submarine",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Rock costume": {
            "category": "material",
            "item_id": 24863,
            "tradeable": False,
            "stackable": False,
            "source": f"{SOME_LIKE_IT_COLD_WIKI_SOURCE}; {SOME_LIKE_IT_COLD_CACHE_SOURCE}",
        },
        "Pop costume": {
            "category": "material",
            "item_id": 24864,
            "tradeable": False,
            "stackable": False,
            "source": f"{SOME_LIKE_IT_COLD_WIKI_SOURCE}; {SOME_LIKE_IT_COLD_CACHE_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__: tuple[str, ...] = ()
