from ...data.quest.another_cook import OPENING_ITEM_DATA
from ...data.quest.toktz_opening import OPENING_ITEMS as _TOKTZ_OPENING_ITEMS
from ...data.quest_data import quest_reward_items_as_dict
from ...data.quest_item_acquisition_data import quest_item_acquisition_extra_items_as_dict


QUEST_REWARD_ITEM_DATA = {**OPENING_ITEM_DATA, **quest_reward_items_as_dict(), **quest_item_acquisition_extra_items_as_dict()}

QUEST_REWARD_ITEM_DATA.update({name: dict(metadata) for name, metadata in _TOKTZ_OPENING_ITEMS.items()})

__all__ = ["QUEST_REWARD_ITEM_DATA"]
