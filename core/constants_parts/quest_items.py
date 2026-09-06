from ...data.quest_data import quest_reward_items_as_dict
from ...data.quest_item_acquisition_data import quest_item_acquisition_extra_items_as_dict


QUEST_REWARD_ITEM_DATA = {**quest_reward_items_as_dict(), **quest_item_acquisition_extra_items_as_dict()}

__all__ = ["QUEST_REWARD_ITEM_DATA"]
