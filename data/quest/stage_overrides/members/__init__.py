from __future__ import annotations

from . import classic as _classic
from .classic import *
from . import later as _later
from .later import *

_GROUPS = (_classic, _later)
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {
    quest_id: fragment
    for group in _GROUPS
    for quest_id, fragment in group._STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST.items()
}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {
    quest_id: fragments
    for group in _GROUPS
    for quest_id, fragments in group._REWARD_ITEM_FRAGMENTS_BY_QUEST.items()
}
__all__ = tuple(name for group in _GROUPS for name in group.__all__)
