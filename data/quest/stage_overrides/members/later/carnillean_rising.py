from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    CARNILLEAN_RISING_ID: (
        _stage_req(
            1,
            "Accept Xenia's request and speak to Ceril Carnillean.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Speak to Xenia", "Speak to Ceril Carnillean"),
        ),
        _stage_req(
            2,
            "Gather the mansion props for Philipe's quest.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Collect the Carnillean family book", "Gather the mansion props"),
        ),
        _stage_req(
            3,
            "Build the cellar quest scene.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Build the cave quest hotspots", "Recruit Sarsaparilla and Claus"),
        ),
        _stage_req(
            4,
            "Guide Philipe through the staged quest.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Guide Philipe through the cellar quest",),
        ),
        _stage_req(
            5,
            "Report back to Philipe, Ceril, and Xenia.",
            CARNILLEAN_RISING_WIKI_SOURCE,
            auto_actions=("Report back to Philipe", "Report back to Ceril and Xenia"),
        ),
    ),
}

__all__: tuple[str, ...] = ()
