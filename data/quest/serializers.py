from __future__ import annotations

from .dependencies import *
from .contract import *
from .ledger import *


def _quest_requirement_dict(requirement: QuestPrerequisite) -> Dict[str, object]:
    return {"quest_id": requirement.quest_id, "display_name": requirement.display_name}


def _skill_requirement_dict(requirement: QuestSkillRequirement) -> Dict[str, object]:
    return {"skill_id": requirement.skill_id, "display_name": requirement.display_name, "level": requirement.level}


def _xp_reward_dict(reward: QuestXpReward) -> Dict[str, object]:
    return {"skill_id": reward.skill_id, "amount": reward.amount}


def _lamp_reward_dict(reward: QuestLampReward) -> Dict[str, object]:
    return {
        "display_name": reward.display_name,
        "amount": reward.amount,
        "skill_options": reward.skill_options,
        "minimum_level": reward.minimum_level,
        "source": reward.source,
        "source_text": reward.source_text,
        "quantity": reward.quantity,
    }


def _quest_choice_option_dict(option: QuestChoiceOption) -> Dict[str, object]:
    return {"label": option.label, "route_id": option.route_id, "description": option.description}


def _quest_choice_dict(choice: QuestChoice) -> Dict[str, object]:
    return {
        "stage": choice.stage,
        "prompt": choice.prompt,
        "options": tuple(_quest_choice_option_dict(option) for option in choice.options),
        "source": choice.source,
    }


def _combat_encounter_dict(encounter: QuestCombatEncounter) -> Dict[str, object]:
    return {
        "encounter_id": encounter.encounter_id,
        "display_name": encounter.display_name,
        "level": encounter.level,
        "quantity": encounter.quantity,
        "source": encounter.source,
        "source_text": encounter.source_text,
        "npc_stats": dict(encounter.npc_stats),
        "npc_bonuses": dict(encounter.npc_bonuses),
        "npc_configs": dict(encounter.npc_configs),
        "guaranteed_drops": dict(encounter.guaranteed_drops),
        "npc_stats_source": encounter.npc_stats_source,
        "required_encounters": encounter.required_encounters,
    }


def _stage_requirement_dict(requirement: QuestStageRequirement) -> Dict[str, object]:
    return {
        "stage": requirement.stage,
        "description": requirement.description,
        "variant": requirement.variant,
        "required_inventory": dict(requirement.required_inventory),
        "required_inventory_options": tuple(
            tuple({item_name: amount} for item_name, amount in option_group)
            for option_group in requirement.required_inventory_options
        ),
        "consumed_inventory": dict(requirement.consumed_inventory),
        "consumed_inventory_options": tuple(
            tuple({item_name: amount} for item_name, amount in option_group)
            for option_group in requirement.consumed_inventory_options
        ),
        "produced_inventory": dict(requirement.produced_inventory),
        "repeatable_until_consumed": requirement.repeatable_until_consumed,
        "required_skills": tuple(
            _skill_requirement_dict(skill) for skill in requirement.required_skills
        ),
        "required_tools": dict(requirement.required_tools),
        "required_actions": requirement.required_actions,
        "auto_actions": requirement.auto_actions,
        "required_routes": requirement.required_routes,
        "combat_encounters": tuple(_combat_encounter_dict(encounter) for encounter in requirement.combat_encounters),
        "source": requirement.source,
    }


def quests_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {
            "id": quest.id,
            "display_name": quest.display_name,
            "stages": quest.stages,
            "point_reward": quest.point_reward,
            "rewards": dict(quest.rewards),
            "start_point": quest.start_point,
            "requirements": quest.requirements,
            "required_items": dict(quest.required_items),
            "start_inventory": dict(quest.start_inventory),
            "required_quests": tuple(_quest_requirement_dict(req) for req in quest.required_quests),
            "required_skills": tuple(_skill_requirement_dict(req) for req in quest.required_skills),
            "required_quest_points": quest.required_quest_points,
            "xp_rewards": tuple(_xp_reward_dict(reward) for reward in quest.xp_rewards),
            "lamp_rewards": tuple(_lamp_reward_dict(reward) for reward in quest.lamp_rewards),
            "combat": quest.combat,
            "source": quest.source,
            "release_date": quest.release_date,
            "release_order": quest.release_order,
            "members": quest.members,
            "difficulty": quest.difficulty,
            "length": quest.length,
            "timeline": quest.timeline,
            "unlocks": quest.unlocks,
            "miniquest": quest.miniquest,
            "journal_stages": {stage.stage: stage.journal for stage in quest.journal_stages},
            "stage_requirements": tuple(_stage_requirement_dict(req) for req in quest.stage_requirements),
            "choices": tuple(_quest_choice_dict(choice) for choice in quest.choices),
        }
        for quest in QUESTS
    }


def quest_references_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        quest.id: {"id": quest.id, "display_name": quest.display_name, "source": quest.source, "note": quest.note}
        for quest in QUEST_REFERENCES
    }


def target_unlock_rules_as_dict() -> Tuple[Dict[str, object], ...]:
    return tuple(
        {
            "gate_kind": rule.gate_kind,
            "skill_id": rule.skill_id,
            "target_ids": rule.target_ids,
            "requirements": tuple(
                {
                    "kind": requirement.kind,
                    "quest_id": requirement.quest_id,
                    "ability_id": requirement.ability_id,
                    "stage": requirement.stage,
                    "reason": requirement.reason,
                    "source": requirement.source,
                }
                for requirement in rule.requirements
            ),
        }
        for rule in TARGET_UNLOCK_RULES
    )


def quest_unlock_rules_as_dict() -> Tuple[Dict[str, object], ...]:
    return target_unlock_rules_as_dict()


quests_as_dict.__module__ = "ankiscape.data.quest_data"
quest_references_as_dict.__module__ = "ankiscape.data.quest_data"
target_unlock_rules_as_dict.__module__ = "ankiscape.data.quest_data"
quest_unlock_rules_as_dict.__module__ = "ankiscape.data.quest_data"

__all__ = (
    'quests_as_dict', 'quest_references_as_dict', 'target_unlock_rules_as_dict', 'quest_unlock_rules_as_dict',
)
