"""Completion-only quest payouts, delegated by the stage transaction owner."""

from typing import Mapping

from ...core.skill_registry import get_skill, trainable_skill_definitions
from ...data.soul_wars_data import SOUL_WARS_ZEAL_CAP
from ...logic.treasure_trails_logic import clue_refusal_reason_pure, filter_clue_scroll_outputs_pure
from ..logic_pure_state import _positive_int


def apply_completion_rewards_pure(data, player_data, quest_id, quest, apply_xp_rewards):
    data["quest_points"] = max(0, _positive_int(data.get("quest_points", 0), 0)) + _positive_int(quest.get("point_reward", 0), 0)
    inventory = data["inventory"]
    offered_rewards = quest.get("rewards", {}) or {}
    rewards = filter_clue_scroll_outputs_pure(data, offered_rewards)
    clue_reward_refusal_reason = clue_refusal_reason_pure(
        player_data, offered_rewards, rewards
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
    apply_xp_rewards(data, quest)
    return clue_reward_refusal_reason


def _quest_xp_reward_row_pure(reward):
    if not isinstance(reward, Mapping):
        return None
    skill_id = reward.get('skill_id')
    if not isinstance(skill_id, str):
        return None
    skill = get_skill(skill_id)
    exp_key = skill.exp_key if skill is not None else f'{skill_id}_exp'
    try:
        amount = float(reward.get('amount', 0))
    except (TypeError, ValueError):
        return None
    if amount <= 0:
        return None
    return skill, exp_key, amount


def _apply_quest_xp_rewards(data, quest):
    trainable_exp_keys = {skill.exp_key for skill in trainable_skill_definitions()}
    pending = data.get('pending_skill_exp_rewards', {})
    if not isinstance(pending, Mapping):
        pending = {}
    clean_pending = dict(pending)
    for reward in quest.get('xp_rewards', ()) or ():
        row = _quest_xp_reward_row_pure(reward)
        if row is None:
            continue
        skill, exp_key, amount = row
        if exp_key in trainable_exp_keys and skill is not None and skill.trainable:
            data[exp_key] = data.get(exp_key, 0) + amount
        else:
            clean_pending[exp_key] = float(clean_pending.get(exp_key, 0) or 0) + amount
    data['pending_skill_exp_rewards'] = {
        key: value for key, value in clean_pending.items() if value > 0
    }
