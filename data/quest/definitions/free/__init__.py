from __future__ import annotations

from . import cooks_assistant as _cooks_assistant
from .cooks_assistant import *
from . import shield_of_arrav as _shield_of_arrav
from .shield_of_arrav import *
from . import demon_slayer as _demon_slayer
from .demon_slayer import *
from . import dragon_slayer as _dragon_slayer
from .dragon_slayer import *
from . import ernest_the_chicken as _ernest_the_chicken
from .ernest_the_chicken import *
from . import black_knights_fortress as _black_knights_fortress
from .black_knights_fortress import *
from . import goblin_diplomacy as _goblin_diplomacy
from .goblin_diplomacy import *
from . import vampyre_slayer as _vampyre_slayer
from .vampyre_slayer import *
from . import the_restless_ghost as _the_restless_ghost
from .the_restless_ghost import *
from . import imp_catcher as _imp_catcher
from .imp_catcher import *
from . import pirates_treasure as _pirates_treasure
from .pirates_treasure import *
from . import rune_mysteries as _rune_mysteries
from .rune_mysteries import *
from . import the_knights_sword as _the_knights_sword
from .the_knights_sword import *

_MODULES = (_cooks_assistant, _shield_of_arrav, _demon_slayer, _dragon_slayer, _ernest_the_chicken, _black_knights_fortress, _goblin_diplomacy, _vampyre_slayer, _the_restless_ghost, _imp_catcher, _pirates_treasure, _rune_mysteries, _the_knights_sword,)
_QUESTS_BY_ID = {module.QUEST.id: module.QUEST for module in _MODULES}
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {
    quest_id: module._STAGE_REQUIREMENT_REPLACEMENTS_BY_ID
    for quest_id, module in (
        ('cooks_assistant', _cooks_assistant),
        ('demon_slayer', _demon_slayer),
        ('dragon_slayer', _dragon_slayer),
        ('ernest_the_chicken', _ernest_the_chicken),
        ('black_knights_fortress', _black_knights_fortress),
        ('goblin_diplomacy', _goblin_diplomacy),
        ('vampyre_slayer', _vampyre_slayer),
        ('the_restless_ghost', _the_restless_ghost),
        ('imp_catcher', _imp_catcher),
        ('pirates_treasure', _pirates_treasure),
        ('rune_mysteries', _rune_mysteries),
    )
}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {
    quest_id: module._REWARD_ITEM_FRAGMENTS
    for quest_id, module in (
        ('shield_of_arrav', _shield_of_arrav),
        ('demon_slayer', _demon_slayer),
        ('dragon_slayer', _dragon_slayer),
        ('ernest_the_chicken', _ernest_the_chicken),
        ('goblin_diplomacy', _goblin_diplomacy),
    )
}

__all__ = tuple(name for module in _MODULES for name in module.__all__)
