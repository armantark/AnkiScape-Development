from __future__ import annotations

from . import stolen_hearts as _stolen_hearts
from .stolen_hearts import *

_MODULES = (_stolen_hearts,)
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {
    quest_id: module._STAGE_REQUIREMENT_REPLACEMENTS_BY_ID
    for quest_id, module in (
        ('stolen_hearts', _stolen_hearts),
    )
}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {
    quest_id: module._REWARD_ITEM_FRAGMENTS
    for quest_id, module in (
        ('stolen_hearts', _stolen_hearts),
    )
}

__all__ = tuple(name for module in _MODULES for name in module.__all__)
