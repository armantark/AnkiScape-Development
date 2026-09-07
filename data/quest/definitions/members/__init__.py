from __future__ import annotations

from . import fight_arena as _fight_arena
from .fight_arena import *
from . import witchs_house as _witchs_house
from .witchs_house import *
from . import merlins_crystal as _merlins_crystal
from .merlins_crystal import *
from . import heroes_quest as _heroes_quest
from .heroes_quest import *
from . import family_crest as _family_crest
from .family_crest import *
from . import temple_of_ikov as _temple_of_ikov
from .temple_of_ikov import *
from . import jungle_potion as _jungle_potion
from .jungle_potion import *
from . import shilo_village as _shilo_village
from .shilo_village import *
from . import lost_city as _lost_city
from .lost_city import *
from . import druidic_ritual as _druidic_ritual
from .druidic_ritual import *
from . import priest_in_peril as _priest_in_peril
from .priest_in_peril import *
from . import tai_bwo_wannai_trio as _tai_bwo_wannai_trio
from .tai_bwo_wannai_trio import *
from . import mournings_end_part_ii as _mournings_end_part_ii
from .mournings_end_part_ii import *
from . import swan_song as _swan_song
from .swan_song import *
from . import lunar_diplomacy as _lunar_diplomacy
from .lunar_diplomacy import *
from . import legacy_of_seergaze as _legacy_of_seergaze
from .legacy_of_seergaze import *

_MODULES = (_fight_arena, _witchs_house, _merlins_crystal, _heroes_quest, _family_crest, _temple_of_ikov, _jungle_potion, _shilo_village, _lost_city, _druidic_ritual, _priest_in_peril, _tai_bwo_wannai_trio, _mournings_end_part_ii, _swan_song, _lunar_diplomacy, _legacy_of_seergaze,)
_QUESTS_BY_ID = {module.QUEST.id: module.QUEST for module in _MODULES}
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {
    quest_id: module._STAGE_REQUIREMENT_REPLACEMENTS_BY_ID
    for quest_id, module in (
        ('fight_arena', _fight_arena),
        ('witchs_house', _witchs_house),
        ('jungle_potion', _jungle_potion),
        ('shilo_village', _shilo_village),
        ('lost_city', _lost_city),
        ('druidic_ritual', _druidic_ritual),
        ('priest_in_peril', _priest_in_peril),
        ('tai_bwo_wannai_trio', _tai_bwo_wannai_trio),
    )
}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {
    quest_id: module._REWARD_ITEM_FRAGMENTS
    for quest_id, module in (
        ('fight_arena', _fight_arena),
        ('witchs_house', _witchs_house),
        ('merlins_crystal', _merlins_crystal),
        ('heroes_quest', _heroes_quest),
        ('family_crest', _family_crest),
        ('temple_of_ikov', _temple_of_ikov),
        ('shilo_village', _shilo_village),
        ('lost_city', _lost_city),
        ('druidic_ritual', _druidic_ritual),
        ('tai_bwo_wannai_trio', _tai_bwo_wannai_trio),
        ('legacy_of_seergaze', _legacy_of_seergaze),
    )
}

__all__ = tuple(name for module in _MODULES for name in module.__all__)
