from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    WOLF_WHISTLE_ID: (
        _stage_req(
            1,
            "Find Scalectrix at the Taverley well.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            auto_actions=("Find Scalectrix at the Taverley well",),
        ),
        _stage_req(
            2,
            "Collect the wolpertinger pouch materials.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            auto_actions=("Collect the ancient wolf bone amulet", "Collect the embroidered pouch", "Collect the white hare meat"),
        ),
        _stage_req(
            3,
            "Infuse the giant wolpertinger pouch and save Bowloftrix.",
            f"{DARKAN_WOLF_WHISTLE_SOURCE}; {WOLF_WHISTLE_WIKI_SOURCE}",
            auto_actions=("Infuse the giant wolpertinger pouch", "Take the pouch to Scalectrix"),
        ),
    ),
}

__all__: tuple[str, ...] = ()
