from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    DEADLIEST_CATCH_ID: (
        _stage_req(
            1,
            "Pickpocket the Master fisher for the sea chart.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            auto_actions=("Pickpocket the Master fisher for the sea chart",),
        ),
        _stage_req(
            2,
            "Recruit Linza and prepare the giant harpoon.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            auto_actions=("Recruit Linza", "Prepare the giant harpoon"),
        ),
        _stage_req(
            3,
            "Track the Thalassus and rescue Jones.",
            DEADLIEST_CATCH_WIKI_SOURCE,
            auto_actions=("Track the Thalassus", "Rescue Jones"),
        ),
    ),
}

__all__: tuple[str, ...] = ()
