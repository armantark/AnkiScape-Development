from __future__ import annotations

from . import a_fairy_tale_i_growing_pains as _a_fairy_tale_i_growing_pains
from .a_fairy_tale_i_growing_pains import *
from . import a_souls_bane as _a_souls_bane
from .a_souls_bane import *
from . import carnillean_rising as _carnillean_rising
from .carnillean_rising import *
from . import deadliest_catch as _deadliest_catch
from .deadliest_catch import *
from . import diamond_in_the_rough as _diamond_in_the_rough
from .diamond_in_the_rough import *
from . import dwarf_cannon as _dwarf_cannon
from .dwarf_cannon import *
from . import gertrudes_cat as _gertrudes_cat
from .gertrudes_cat import *
from . import icthlarins_little_helper as _icthlarins_little_helper
from .icthlarins_little_helper import *
from . import nature_spirit as _nature_spirit
from .nature_spirit import *
from . import smoking_kills as _smoking_kills
from .smoking_kills import *
from . import some_like_it_cold as _some_like_it_cold
from .some_like_it_cold import *
from . import song_from_the_depths as _song_from_the_depths
from .song_from_the_depths import *
from . import the_fremennik_isles as _the_fremennik_isles
from .the_fremennik_isles import *
from . import wolf_whistle as _wolf_whistle
from .wolf_whistle import *

_MODULES = (_a_fairy_tale_i_growing_pains, _a_souls_bane, _carnillean_rising, _deadliest_catch, _diamond_in_the_rough, _dwarf_cannon, _gertrudes_cat, _icthlarins_little_helper, _nature_spirit, _smoking_kills, _some_like_it_cold, _song_from_the_depths, _the_fremennik_isles, _wolf_whistle,)
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {
    module_name: module._STAGE_REQUIREMENT_REPLACEMENTS_BY_ID
    for module_name, module in (
        ('a_fairy_tale_i_growing_pains', _a_fairy_tale_i_growing_pains),
        ('a_souls_bane', _a_souls_bane),
        ('carnillean_rising', _carnillean_rising),
        ('deadliest_catch', _deadliest_catch),
        ('diamond_in_the_rough', _diamond_in_the_rough),
        ('dwarf_cannon', _dwarf_cannon),
        ('gertrudes_cat', _gertrudes_cat),
        ('icthlarins_little_helper', _icthlarins_little_helper),
        ('nature_spirit', _nature_spirit),
        ('smoking_kills', _smoking_kills),
        ('some_like_it_cold', _some_like_it_cold),
        ('song_from_the_depths', _song_from_the_depths),
        ('the_fremennik_isles', _the_fremennik_isles),
        ('wolf_whistle', _wolf_whistle),
    )
}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {
    module_name: module._REWARD_ITEM_FRAGMENTS
    for module_name, module in (
        ('diamond_in_the_rough', _diamond_in_the_rough),
        ('dwarf_cannon', _dwarf_cannon),
        ('gertrudes_cat', _gertrudes_cat),
        ('icthlarins_little_helper', _icthlarins_little_helper),
        ('smoking_kills', _smoking_kills),
        ('some_like_it_cold', _some_like_it_cold),
    )
}

__all__ = tuple(name for module in _MODULES for name in module.__all__)
