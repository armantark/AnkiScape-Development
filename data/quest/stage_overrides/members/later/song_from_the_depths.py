from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    SONG_FROM_THE_DEPTHS_ID: (
        _stage_req(
            1,
            "Drink the restless sleep potion and follow the souls to the cave.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            auto_actions=("Drink the restless sleep potion", "Follow the souls to the cave entrance"),
        ),
        _stage_req(
            2,
            "Work through the dream cave puzzles.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            auto_actions=("Complete the maze doors", "Solve the symbol rooms", "Move the saplings through the dream rooms"),
        ),
        _stage_req(
            3,
            "Escape the dragon's stomach and return to Lucille.",
            SONG_FROM_THE_DEPTHS_WIKI_SOURCE,
            auto_actions=("Escape the dragon's stomach", "Return to Lucille"),
        ),
    ),
}

__all__: tuple[str, ...] = ()
