from __future__ import annotations

from . import biohazard as _biohazard
from .biohazard import *
from . import clock_tower as _clock_tower
from .clock_tower import *
from . import fishing_contest as _fishing_contest
from .fishing_contest import *
from . import hazeel_cult as _hazeel_cult
from .hazeel_cult import *
from . import holy_grail as _holy_grail
from .holy_grail import *
from . import monks_friend as _monks_friend
from .monks_friend import *
from . import plague_city as _plague_city
from .plague_city import *
from . import scorpion_catcher as _scorpion_catcher
from .scorpion_catcher import *
from . import sheep_herder as _sheep_herder
from .sheep_herder import *
from . import tree_gnome_village as _tree_gnome_village
from .tree_gnome_village import *
from . import tribal_totem as _tribal_totem
from .tribal_totem import *
from . import waterfall_quest as _waterfall_quest
from .waterfall_quest import *

_MODULES = (_biohazard, _clock_tower, _fishing_contest, _hazeel_cult, _holy_grail, _monks_friend, _plague_city, _scorpion_catcher, _sheep_herder, _tree_gnome_village, _tribal_totem, _waterfall_quest,)
_STAGE_REQUIREMENT_REPLACEMENTS_BY_QUEST = {
    module_name: module._STAGE_REQUIREMENT_REPLACEMENTS_BY_ID
    for module_name, module in (
        ('biohazard', _biohazard),
        ('clock_tower', _clock_tower),
        ('fishing_contest', _fishing_contest),
        ('hazeel_cult', _hazeel_cult),
        ('holy_grail', _holy_grail),
        ('monks_friend', _monks_friend),
        ('plague_city', _plague_city),
        ('scorpion_catcher', _scorpion_catcher),
        ('sheep_herder', _sheep_herder),
        ('tree_gnome_village', _tree_gnome_village),
        ('tribal_totem', _tribal_totem),
        ('waterfall_quest', _waterfall_quest),
    )
}
_REWARD_ITEM_FRAGMENTS_BY_QUEST = {
    module_name: module._REWARD_ITEM_FRAGMENTS
    for module_name, module in (
        ('biohazard', _biohazard),
        ('clock_tower', _clock_tower),
        ('fishing_contest', _fishing_contest),
        ('holy_grail', _holy_grail),
        ('monks_friend', _monks_friend),
        ('plague_city', _plague_city),
        ('scorpion_catcher', _scorpion_catcher),
        ('sheep_herder', _sheep_herder),
        ('tree_gnome_village', _tree_gnome_village),
        ('tribal_totem', _tribal_totem),
        ('waterfall_quest', _waterfall_quest),
    )
}

__all__ = tuple(name for module in _MODULES for name in module.__all__)
