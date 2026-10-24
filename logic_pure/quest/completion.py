"""Completion rewards shared by the existing quest transaction."""

from ...data.soul_wars_data import SOUL_WARS_ZEAL_CAP
from ...logic.treasure_trails_logic import clue_refusal_reason_pure, filter_clue_scroll_outputs_pure
from ..logic_pure_state import _positive_int


def apply_quest_completion_rewards_pure(data, previous_data, quest_id, quest, award_xp):
    data["quest_points"] = max(0, _positive_int(data.get("quest_points", 0), 0)) + _positive_int(quest.get("point_reward", 0), 0)
    inventory = data["inventory"]
    offered_rewards = quest.get("rewards", {}) or {}
    rewards = filter_clue_scroll_outputs_pure(data, offered_rewards)
    clue_reward_refusal_reason = clue_refusal_reason_pure(
        previous_data, offered_rewards, rewards
    )
    for item_name, amount in rewards.items():
        inventory[item_name] = inventory.get(item_name, 0) + _positive_int(amount, 1)
    if quest_id == "family_crest":
        data["family_gauntlet_enchantment"] = "family"
    if quest_id == "nomads_requiem":
        # Nomad's Requiem pays 70 Zeal points, a Soul Wars currency, not an
        # inventory item (RuneScape Wiki Nomad's Requiem oldid=6386610).
        data["soul_wars_zeal"] = min(
            SOUL_WARS_ZEAL_CAP,
            max(0, int(data.get("soul_wars_zeal") or 0)) + 70,
        )
    award_xp(data, quest)
    return clue_reward_refusal_reason
