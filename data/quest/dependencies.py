from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Dict, Mapping, Tuple, Union

from ...generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG

from .. import cabin_fever_data, chompy_hunting_data, rum_deal_data, zogre_flesh_eaters_data
from ..runecrafting_data import RUNEMYSTERIES_SOURCE_PATH, WICKED_HOOD_ITEM
from ..stronghold_player_safety_data import (
    STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS,
    STRONGHOLD_PLAYER_SAFETY_LAMP_SOURCE,
)
from ..summoning_data import SUMMONING_POUCHES
from ..firemaking_data import LIT_LIGHT_SOURCE_ITEMS
from ..herblore_data import (
    DARKAN_HERB_CLEANING_SOURCE_PATH,
    JUNGLE_POTION_CACHE_SOURCE,
    JUNGLE_POTION_POST_QUEST_SEARCH_SOURCE,
    JUNGLE_POTION_SEARCH_ACTIVITY_IDS,
)
from ..varrock_museum_data import varrock_museum_quest_reward_additions_as_dict

__all__ = (
    're', 'dataclass', 'replace', 'Dict', 'Mapping', 'Tuple', 'Union', 'PRE_EOC_QUEST_CATALOG', 'cabin_fever_data', 'chompy_hunting_data', 'rum_deal_data', 'zogre_flesh_eaters_data', 'RUNEMYSTERIES_SOURCE_PATH',
    'WICKED_HOOD_ITEM', 'STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS', 'STRONGHOLD_PLAYER_SAFETY_LAMP_SOURCE', 'SUMMONING_POUCHES', 'LIT_LIGHT_SOURCE_ITEMS', 'DARKAN_HERB_CLEANING_SOURCE_PATH', 'JUNGLE_POTION_CACHE_SOURCE',
    'JUNGLE_POTION_POST_QUEST_SEARCH_SOURCE', 'JUNGLE_POTION_SEARCH_ACTIVITY_IDS', 'varrock_museum_quest_reward_additions_as_dict',
)
