from __future__ import annotations

from . import alfred_grimhands_barcrawl as _alfred_grimhands_barcrawl
from .alfred_grimhands_barcrawl import *
from . import hunt_for_surok as _hunt_for_surok
from .hunt_for_surok import *
from . import lair_of_tarn_razorlor as _lair_of_tarn_razorlor
from .lair_of_tarn_razorlor import *

from . import skippy_and_the_mogres as _skippy_and_the_mogres
from .skippy_and_the_mogres import *

_MODULES = (_alfred_grimhands_barcrawl, _hunt_for_surok, _lair_of_tarn_razorlor, _skippy_and_the_mogres,)
_QUESTS_BY_ID = {module.QUEST.id: module.QUEST for module in _MODULES}
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {
    quest_id: module._STAGE_REQUIREMENT_REPLACEMENTS_BY_ID
    for quest_id, module in (
    )
}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {
    quest_id: module._REWARD_ITEM_FRAGMENTS
    for quest_id, module in (
    )
}

__all__ = tuple(name for module in _MODULES for name in module.__all__)
