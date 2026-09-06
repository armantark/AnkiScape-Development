from __future__ import annotations

from .dependencies import *
from .ids import *


@dataclass(frozen=True)
class QuestStage:
    stage: int
    journal: Tuple[str, ...]


@dataclass(frozen=True)
class QuestCombatEncounter:
    encounter_id: str
    display_name: str
    level: int = 0
    quantity: int = 1
    source: str = ""
    source_text: str = ""
    npc_stats: Tuple[Tuple[str, object], ...] = ()
    npc_bonuses: Tuple[Tuple[str, object], ...] = ()
    npc_configs: Tuple[Tuple[str, object], ...] = ()
    guaranteed_drops: Tuple[Tuple[str, int], ...] = ()
    npc_stats_source: str = ""


@dataclass(frozen=True)
class QuestStageRequirement:
    stage: int
    description: str
    variant: str = ""
    required_inventory: Tuple[Tuple[str, int], ...] = ()
    required_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = ()
    consumed_inventory: Tuple[Tuple[str, int], ...] = ()
    consumed_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = ()
    produced_inventory: Tuple[Tuple[str, int], ...] = ()
    repeatable_until_consumed: bool = False
    required_skills: Tuple[QuestSkillRequirement, ...] = ()
    required_tools: Tuple[Tuple[str, int], ...] = ()
    required_actions: Tuple[str, ...] = ()
    auto_actions: Tuple[str, ...] = ()
    required_routes: Tuple[str, ...] = ()
    combat_encounters: Tuple[QuestCombatEncounter, ...] = ()
    source: str = ""


@dataclass(frozen=True)
class QuestChoiceOption:
    label: str
    route_id: str
    description: str = ""


@dataclass(frozen=True)
class QuestChoice:
    stage: int
    prompt: str
    options: Tuple[QuestChoiceOption, ...]
    source: str = ""


@dataclass(frozen=True)
class QuestPrerequisite:
    quest_id: str
    display_name: str


@dataclass(frozen=True)
class QuestSkillRequirement:
    skill_id: str
    display_name: str
    level: int


@dataclass(frozen=True)
class QuestXpReward:
    skill_id: str
    amount: float


@dataclass(frozen=True)
class QuestLampReward:
    display_name: str
    amount: float
    skill_options: Tuple[str, ...]
    minimum_level: int
    source: str
    source_text: str = ""
    quantity: int = 1


@dataclass(frozen=True)
class QuestDefinition:
    id: str
    display_name: str
    stages: int
    point_reward: int
    rewards: Tuple[Tuple[str, int], ...]
    start_point: str
    requirements: Tuple[str, ...]
    required_items: Tuple[Tuple[str, int], ...]
    combat: str
    source: str
    journal_stages: Tuple[QuestStage, ...]
    release_date: str
    members: bool
    difficulty: str
    length: str
    timeline: str
    required_quests: Tuple[QuestPrerequisite, ...] = ()
    required_skills: Tuple[QuestSkillRequirement, ...] = ()
    required_quest_points: int = 0
    xp_rewards: Tuple[QuestXpReward, ...] = ()
    lamp_rewards: Tuple[QuestLampReward, ...] = ()
    unlocks: Tuple[str, ...] = ()
    release_order: int = 0
    stage_requirements: Tuple[QuestStageRequirement, ...] = ()
    start_inventory: Tuple[Tuple[str, int], ...] = ()
    choices: Tuple[QuestChoice, ...] = ()
    # Miniquests are ordinary ledger rows that award no quest points; the flag
    # only tells the Quests tab to group them separately.
    miniquest: bool = False


@dataclass(frozen=True)
class ClaimDefinition:
    id: str
    display_name: str
    source: str
    claim_type: str = "item"
    item_name: str = ""
    quantity: int = 1
    items: Tuple[Tuple[str, int], ...] = ()
    required_quest: str = RUNE_MYSTERIES_ID
    required_tools: Tuple[Tuple[str, int], ...] = ()
    required_runecrafting_level: int = 0
    xp_amount: float = 0.0
    skill_options: Tuple[str, ...] = ()
    minimum_level: int = 1
    delivery_required: bool = False


@dataclass(frozen=True)
class QuestReference:
    id: str
    display_name: str
    source: str
    note: str


@dataclass(frozen=True)
class QuestUnlockRule:
    quest_id: str
    gate_kind: str
    skill_id: str
    target_ids: Tuple[str, ...]
    reason: str
    source: str


@dataclass(frozen=True)
class TargetUnlockRequirement:
    kind: str
    reason: str
    source: str
    quest_id: str = ""
    ability_id: str = ""


@dataclass(frozen=True)
class TargetUnlockRule:
    gate_kind: str
    skill_id: str
    target_ids: Tuple[str, ...]
    requirements: Tuple[TargetUnlockRequirement, ...]


def _clean_journal(*lines: str) -> Tuple[str, ...]:
    cleaned = []
    for line in lines:
        stripped = re.sub(r"</?col(?:=[^>]*)?>", "", line)
        stripped = stripped.replace("<str>", "").strip()
        if stripped:
            cleaned.append(stripped)
    return tuple(cleaned)


def _simple_stage(stage: int, *lines: str) -> QuestStage:
    return QuestStage(stage, _clean_journal(*lines))


def _stage_req(
    stage: int,
    description: str,
    source: str,
    *,
    variant: str = "",
    required_inventory: Tuple[Tuple[str, int], ...] = (),
    required_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = (),
    consumed_inventory: Tuple[Tuple[str, int], ...] = (),
    consumed_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = (),
    produced_inventory: Tuple[Tuple[str, int], ...] = (),
    repeatable_until_consumed: bool = False,
    required_skills: Tuple[QuestSkillRequirement, ...] = (),
    required_tools: Tuple[Tuple[str, int], ...] = (),
    required_actions: Tuple[str, ...] = (),
    auto_actions: Tuple[str, ...] = (),
    required_routes: Tuple[str, ...] = (),
    combat_encounters: Tuple[QuestCombatEncounter, ...] = (),
) -> QuestStageRequirement:
    return QuestStageRequirement(
        stage=stage,
        description=description,
        variant=variant,
        required_inventory=required_inventory,
        required_inventory_options=required_inventory_options,
        consumed_inventory=consumed_inventory,
        consumed_inventory_options=consumed_inventory_options,
        produced_inventory=produced_inventory,
        repeatable_until_consumed=repeatable_until_consumed,
        required_skills=required_skills,
        required_tools=required_tools,
        required_actions=required_actions,
        auto_actions=auto_actions,
        required_routes=required_routes,
        combat_encounters=combat_encounters,
        source=source,
    )


def _combat(
    quest_id: str,
    encounter_id: str,
    display_name: str,
    level: int,
    source: str,
    source_text: str,
    *,
    quantity: int = 1,
    npc_stats: Tuple[Tuple[str, object], ...] = (),
    npc_bonuses: Tuple[Tuple[str, object], ...] = (),
    npc_configs: Tuple[Tuple[str, object], ...] = (),
    guaranteed_drops: Tuple[Tuple[str, int], ...] = (),
    npc_stats_source: str = "",
) -> QuestCombatEncounter:
    return QuestCombatEncounter(
        encounter_id=f"{quest_id}_{encounter_id}",
        display_name=display_name,
        level=level,
        quantity=quantity,
        source=source,
        source_text=source_text,
        npc_stats=npc_stats,
        npc_bonuses=npc_bonuses,
        npc_configs=npc_configs,
        guaranteed_drops=guaranteed_drops,
        npc_stats_source=npc_stats_source,
    )


QuestCombatEncounterReplacement = Union[QuestCombatEncounter, Tuple[QuestCombatEncounter, ...]]


@dataclass(frozen=True)
class QuestStageRequirementCleanup:
    stage: int
    variant: str = ""
    remove_required_inventory: Tuple[str, ...] = ()
    remove_required_inventory_options: Tuple[str, ...] = ()
    remove_consumed_inventory: Tuple[str, ...] = ()
    remove_consumed_inventory_options: Tuple[str, ...] = ()
    remove_required_tools: Tuple[str, ...] = ()
    add_required_tools: Tuple[Tuple[str, int], ...] = ()
    add_required_skills: Tuple[QuestSkillRequirement, ...] = ()
    remove_required_actions: Tuple[str, ...] = ()
    add_required_inventory: Tuple[Tuple[str, int], ...] = ()
    add_required_inventory_options: Tuple[Tuple[Tuple[str, int], ...], ...] = ()
    add_required_actions: Tuple[str, ...] = ()
    add_auto_actions: Tuple[str, ...] = ()
    remove_required_routes: Tuple[str, ...] = ()
    add_required_routes: Tuple[str, ...] = ()
    add_consumed_inventory: Tuple[Tuple[str, int], ...] = ()
    add_produced_inventory: Tuple[Tuple[str, int], ...] = ()
    source: str = ""


QuestStage.__module__ = "ankiscape.data.quest_data"
QuestCombatEncounter.__module__ = "ankiscape.data.quest_data"
QuestStageRequirement.__module__ = "ankiscape.data.quest_data"
QuestChoiceOption.__module__ = "ankiscape.data.quest_data"
QuestChoice.__module__ = "ankiscape.data.quest_data"
QuestPrerequisite.__module__ = "ankiscape.data.quest_data"
QuestSkillRequirement.__module__ = "ankiscape.data.quest_data"
QuestXpReward.__module__ = "ankiscape.data.quest_data"
QuestLampReward.__module__ = "ankiscape.data.quest_data"
QuestDefinition.__module__ = "ankiscape.data.quest_data"
ClaimDefinition.__module__ = "ankiscape.data.quest_data"
QuestReference.__module__ = "ankiscape.data.quest_data"
QuestUnlockRule.__module__ = "ankiscape.data.quest_data"
TargetUnlockRequirement.__module__ = "ankiscape.data.quest_data"
TargetUnlockRule.__module__ = "ankiscape.data.quest_data"
QuestStageRequirementCleanup.__module__ = "ankiscape.data.quest_data"

__all__ = (
    'QuestStage', 'QuestCombatEncounter', 'QuestStageRequirement', 'QuestChoiceOption', 'QuestChoice', 'QuestPrerequisite', 'QuestSkillRequirement', 'QuestXpReward', 'QuestLampReward', 'QuestDefinition',
    'ClaimDefinition', 'QuestReference', 'QuestUnlockRule', 'TargetUnlockRequirement', 'TargetUnlockRule', '_clean_journal', '_simple_stage', '_stage_req', '_combat', 'QuestCombatEncounterReplacement',
    'QuestStageRequirementCleanup',
)
