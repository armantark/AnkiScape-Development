from __future__ import annotations

from . import free as _free
from .free import *
from . import members as _members
from .members import *
from . import miniquests as _miniquests
from .miniquests import *

_GROUPS = (_free, _members, _miniquests,)
_QUESTS_BY_ID = {quest_id: quest for group in _GROUPS for quest_id, quest in group._QUESTS_BY_ID.items()}
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {quest_id: fragment for group in _GROUPS for quest_id, fragment in group._STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST.items()}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {quest_id: fragments for group in _GROUPS for quest_id, fragments in group._REWARD_ITEM_FRAGMENTS_BY_QUEST.items()}
__all__ = tuple(name for group in _GROUPS for name in group.__all__)
