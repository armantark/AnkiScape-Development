from __future__ import annotations

from .dependencies import *
from .contract import *
from .ids import *
from .sources import *
from .item_names import *
from .choices import *
from .catalog_overrides import *
from .catalog_overrides import QUEST_REQUIREMENT_TEXT_REPLACEMENTS_BY_ID
from .stage_requirements import *
from .stage_additions import *
from .stage_cleanups import *
from .combat_replacements import *
from .combat_relocation import relocate_combat_encounters as _relocate_combat_encounters
from ...core.tool_belt import QUEST_STAGES_NEEDING_HELD_TOOLS, TOOL_BELT_TOOLS

_STAGE_COUNT_BY_LENGTH = {
    "Short": 3,
    "Short to Medium": 4,
    "Medium": 5,
    "Medium to Long": 6,
    "Long": 7,
    "Long to Very Long": 8,
    "Very Long": 9,
    "Very, Very Long": 10,
}


def _generated_stage_count(length: str) -> int:
    return _STAGE_COUNT_BY_LENGTH.get(length, 5)


def _generated_journal_stages(display_name: str, stages: int) -> Tuple[QuestStage, ...]:
    if stages <= 1:
        return (_simple_stage(1, f"I completed {display_name}.", "Quest complete!"),)
    rows = [_simple_stage(1, f"I started {display_name}.")]
    for stage in range(2, stages):
        rows.append(_simple_stage(stage, f"I made progress on {display_name}."))
    rows.append(_simple_stage(stages, f"I completed {display_name}.", "Quest complete!"))
    return tuple(rows)


def _catalog_journal_stages(row: Dict[str, object], display_name: str, stages: int) -> Tuple[QuestStage, ...]:
    raw_stages = row.get("journal_stages", ()) or ()
    rows = []
    for raw_stage in raw_stages:
        if not isinstance(raw_stage, dict):
            continue
        try:
            stage = int(raw_stage.get("stage", 0))
        except (TypeError, ValueError):
            continue
        raw_lines = raw_stage.get("journal", ()) or ()
        lines = tuple(str(line) for line in raw_lines if str(line).strip())
        if stage > 0 and lines:
            rows.append(QuestStage(stage, lines))
    if rows:
        return tuple(sorted(rows, key=lambda stage: stage.stage))
    return _generated_journal_stages(display_name, stages)


def _quest_reward_item_name(name: object) -> str:
    raw_name = str(name)
    if raw_name in QUEST_REWARD_NON_ITEM_NAMES:
        return ""
    return QUEST_REWARD_ITEM_NAME_OVERRIDES.get(raw_name, raw_name)


def _catalog_int(row: Dict[str, object], key: str, default: int = 0) -> int:
    try:
        return int(row.get(key, default))
    except (TypeError, ValueError):
        return default


def _catalog_bool(row: Dict[str, object], key: str, default: bool = False) -> bool:
    value = row.get(key, default)
    return bool(value)


_CATALOG_ITEM_ENTRY_KEYS = frozenset({"item_name", "display_name", "quantity", "amount"})


def _catalog_item_mapping_entry_pairs(entry: Mapping) -> Tuple[Tuple[str, int], ...]:
    name = entry.get("item_name") or entry.get("display_name")
    if isinstance(name, str) and name:
        return ((name, _catalog_int({"value": entry.get("quantity", entry.get("amount", 1))}, "value", 1)),)
    # An unnamed entry is itself a name-to-amount mapping, minus any stray entry keys.
    return tuple(
        (str(item_name), _catalog_int({"value": amount}, "value", 1))
        for item_name, amount in entry.items()
        if item_name not in _CATALOG_ITEM_ENTRY_KEYS
    )


def _catalog_item_entry_pairs(entry: object) -> Tuple[Tuple[str, int], ...]:
    if isinstance(entry, Mapping):
        return _catalog_item_mapping_entry_pairs(entry)
    if isinstance(entry, (tuple, list)) and len(entry) >= 2 and isinstance(entry[0], str) and entry[0]:
        return ((entry[0], _catalog_int({"value": entry[1]}, "value", 1)),)
    return ()


def _catalog_item_pairs(value: object) -> Tuple[Tuple[str, int], ...]:
    if isinstance(value, Mapping):
        return tuple((str(name), _catalog_int({"value": amount}, "value", 1)) for name, amount in value.items())
    if isinstance(value, (tuple, list)):
        return tuple(pair for entry in value for pair in _catalog_item_entry_pairs(entry))
    return ()


def _catalog_item_options(value: object) -> Tuple[Tuple[Tuple[str, int], ...], ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    if value and all(isinstance(group, Mapping) for group in value):
        return (_catalog_item_pairs(value),)
    groups = []
    for group in value:
        options = _catalog_item_pairs(group)
        if options:
            groups.append(options)
    return tuple(groups)


def _catalog_object_pairs(value: object) -> Tuple[Tuple[str, object], ...]:
    if isinstance(value, Mapping):
        return tuple((str(key), item) for key, item in value.items())
    return ()


def _catalog_strings(value: object) -> Tuple[str, ...]:
    if isinstance(value, str):
        return (value,) if value else ()
    if isinstance(value, (tuple, list)):
        return tuple(str(item) for item in value if str(item))
    return ()


def _catalog_combat_encounters(value: object) -> Tuple[QuestCombatEncounter, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    encounters = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        encounter_id = raw.get("encounter_id")
        display_name = raw.get("display_name")
        if not isinstance(encounter_id, str) or not isinstance(display_name, str):
            continue
        encounters.append(
            QuestCombatEncounter(
                encounter_id=encounter_id,
                display_name=display_name,
                level=_catalog_int(dict(raw), "level", 0),
                quantity=_catalog_int(dict(raw), "quantity", 1),
                source=str(raw.get("source", "")),
                source_text=str(raw.get("source_text", "")),
                npc_stats=_catalog_object_pairs(raw.get("npc_stats", {})),
                npc_bonuses=_catalog_object_pairs(raw.get("npc_bonuses", {})),
                npc_configs=_catalog_object_pairs(raw.get("npc_configs", {})),
                guaranteed_drops=_catalog_object_pairs(raw.get("guaranteed_drops", {})),
                npc_stats_source=str(raw.get("npc_stats_source", "")),
                required_encounters=_catalog_strings(raw.get("required_encounters", ())),
            )
        )
    return tuple(encounters)


def _catalog_stage_requirements(value: object) -> Tuple[QuestStageRequirement, ...]:
    if not isinstance(value, (tuple, list)):
        return ()
    requirements = []
    for raw in value:
        if not isinstance(raw, Mapping):
            continue
        stage = _catalog_int(dict(raw), "stage", 0)
        if stage <= 0:
            continue
        requirements.append(
            QuestStageRequirement(
                stage=stage,
                description=str(raw.get("description", "Generated quest-stage requirement.")),
                variant=str(raw.get("variant", "")),
                required_inventory=_catalog_item_pairs(raw.get("required_inventory", {})),
                required_inventory_options=_catalog_item_options(raw.get("required_inventory_options", ())),
                consumed_inventory=_catalog_item_pairs(raw.get("consumed_inventory", {})),
                consumed_inventory_options=_catalog_item_options(raw.get("consumed_inventory_options", ())),
                produced_inventory=_catalog_item_pairs(raw.get("produced_inventory", {})),
                repeatable_until_consumed=_catalog_bool(
                    dict(raw), "repeatable_until_consumed"
                ),
                required_skills=tuple(
                    QuestSkillRequirement(
                        str(skill.get("skill_id")),
                        str(skill.get("display_name", skill.get("skill_id"))),
                        _catalog_int(dict(skill), "level", 1),
                    )
                    for skill in raw.get("required_skills", ()) or ()
                    if isinstance(skill, Mapping) and skill.get("skill_id")
                ),
                required_tools=_catalog_item_pairs(raw.get("required_tools", {})),
                required_actions=_catalog_strings(raw.get("required_actions", ())),
                auto_actions=_catalog_strings(raw.get("auto_actions", ())),
                required_routes=_catalog_strings(raw.get("required_routes", ())),
                combat_encounters=_catalog_combat_encounters(raw.get("combat_encounters", ())),
                source=str(raw.get("source", "")),
            )
        )
    return tuple(requirements)


def _catalog_rows_with(value: object, key: str) -> Tuple[Dict[str, object], ...]:
    return tuple(entry for entry in (value or ()) if isinstance(entry, dict) and entry.get(key))


def _catalog_required_quests(row: Dict[str, object], quest_id: str) -> Tuple[QuestPrerequisite, ...]:
    required_quests = tuple(
        QuestPrerequisite(str(req.get("quest_id")), str(req.get("display_name", req.get("quest_id"))))
        for req in _catalog_rows_with(row.get("required_quests", ()), "quest_id")
    )
    return QUEST_REQUIRED_QUEST_REPLACEMENTS_BY_ID.get(quest_id, required_quests)


def _catalog_required_skills(row: Dict[str, object], quest_id: str) -> Tuple[QuestSkillRequirement, ...]:
    required_skills = tuple(
        QuestSkillRequirement(
            str(req.get("skill_id")),
            str(req.get("display_name", req.get("skill_id"))),
            _catalog_int(req, "level", 1),
        )
        for req in _catalog_rows_with(row.get("required_skills", ()), "skill_id")
    )
    return QUEST_REQUIRED_SKILL_REPLACEMENTS_BY_ID.get(quest_id, required_skills)


def _catalog_xp_rewards(row: Dict[str, object], quest_id: str) -> Tuple[QuestXpReward, ...]:
    xp_rewards = tuple(
        QuestXpReward(str(reward.get("skill_id")), float(reward.get("amount", 0) or 0))
        for reward in _catalog_rows_with(row.get("xp_rewards", ()), "skill_id")
    )
    return QUEST_XP_REWARD_REPLACEMENTS_BY_ID.get(quest_id, xp_rewards)


def _catalog_reward_items(rewards: object) -> Tuple[Tuple[str, int], ...]:
    return tuple(
        (_quest_reward_item_name(reward.get("item_name")), _catalog_int(reward, "quantity", 1))
        for reward in _catalog_rows_with(rewards, "item_name")
    )


def _catalog_item_rewards(row: Dict[str, object], quest_id: str) -> Tuple[Tuple[str, int], ...]:
    item_rewards = QUEST_ITEM_REWARD_REPLACEMENTS_BY_ID.get(quest_id)
    if item_rewards is None:
        item_rewards = _catalog_reward_items(row.get("item_rewards", ()))
    item_reward_additions = QUEST_ITEM_REWARD_ADDITIONS_BY_ID.get(quest_id, ())
    if item_reward_additions:
        item_rewards += _catalog_reward_items(item_reward_additions)
    return item_rewards


def _catalog_lamp_rewards(row: Dict[str, object], quest_id: str) -> Tuple[QuestLampReward, ...]:
    lamp_rewards = tuple(
        QuestLampReward(
            str(reward.get("display_name", "XP lamp")),
            float(reward.get("amount", 0) or 0),
            tuple(str(skill_id) for skill_id in (reward.get("skill_options", ()) or ()) if str(skill_id)),
            _catalog_int(reward, "minimum_level", 1),
            str(reward.get("source", row.get("reward_source", row.get("source", "")))),
            str(reward.get("source_text", "")),
            _catalog_int(reward, "quantity", 1),
        )
        for reward in _catalog_rows_with(row.get("lamp_rewards", ()), "amount")
    )
    return QUEST_LAMP_REWARD_REPLACEMENTS_BY_ID.get(quest_id, lamp_rewards)


def _quest_from_catalog(row: Dict[str, object]) -> QuestDefinition:
    display_name = str(row.get("display_name", row.get("id", "Quest")))
    quest_id = str(row.get("id"))
    length = str(row.get("length", "Medium"))
    stages = _catalog_int(row, "stages", _generated_stage_count(length))
    required_quests = _catalog_required_quests(row, quest_id)
    required_skills = _catalog_required_skills(row, quest_id)
    xp_rewards = _catalog_xp_rewards(row, quest_id)
    item_rewards = _catalog_item_rewards(row, quest_id)
    lamp_rewards = _catalog_lamp_rewards(row, quest_id)
    unlocks = tuple(str(unlock) for unlock in (row.get("unlocks", ()) or ()))
    unlocks = QUEST_UNLOCK_REPLACEMENTS_BY_ID.get(quest_id, unlocks)
    if quest_id == "legends_quest":
        row = dict(row)
        row["required_quest_points"] = 108
        row["requirements"] = (
            ("108 quest points",)
            + tuple(requirement.display_name for requirement in required_quests)
            + tuple(requirement for requirement in row.get("requirements", ()) if requirement != "Regicide")
        )
        row["source"] = (
            f"{row.get('source', '')}; https://runescape.wiki/w/index.php?title=Template%3AQuestreq&oldid=6552449"
            "; https://web.archive.org/web/20121018050049id_/http://runescape.salmoneus.net/quests/legends-quest.html"
        )
    return QuestDefinition(
        id=quest_id,
        display_name=display_name,
        stages=stages,
        point_reward=_catalog_int(row, "point_reward", 0),
        rewards=item_rewards,
        start_point=str(row.get("start_point", "See the source guide for the start location.")),
        requirements=QUEST_REQUIREMENT_TEXT_REPLACEMENTS_BY_ID.get(
            quest_id,
            tuple(str(requirement) for requirement in (row.get("requirements", ()) or ())),
        ),
        required_items=(),
        combat=str(row.get("combat", "See the source guide.")),
        source=f"{row.get('source', '')}; {row.get('release_source', '')}",
        journal_stages=_catalog_journal_stages(row, display_name, stages),
        release_date=str(row.get("release_date", "")),
        members=_catalog_bool(row, "members", True),
        difficulty=str(row.get("difficulty", "Novice")),
        length=length,
        timeline=str(row.get("timeline", "Fifth Age")),
        required_quests=required_quests,
        required_skills=required_skills,
        required_quest_points=_catalog_int(row, "required_quest_points", 0),
        xp_rewards=xp_rewards,
        lamp_rewards=lamp_rewards,
        unlocks=unlocks,
        release_order=_catalog_int(row, "release_order", 9999),
        stage_requirements=_catalog_stage_requirements(row.get("stage_requirements", ())),
        start_inventory=_catalog_item_pairs(row.get("start_inventory", {})),
    )


def _quest_catalog_row_id(row: Dict[str, object]) -> str:
    return str(row.get("id", ""))


def _dedupe_stage_requirements(requirements: Tuple[QuestStageRequirement, ...]) -> Tuple[QuestStageRequirement, ...]:
    seen = set()
    rows = []
    for requirement in sorted(requirements, key=lambda row: (row.stage, row.description, row.source)):
        key = (
            requirement.stage,
            requirement.description,
            requirement.variant,
            requirement.required_inventory,
            requirement.required_inventory_options,
            requirement.consumed_inventory,
            requirement.consumed_inventory_options,
            requirement.produced_inventory,
            requirement.required_skills,
            requirement.required_tools,
            requirement.required_actions,
            requirement.required_routes,
            tuple(encounter.encounter_id for encounter in requirement.combat_encounters),
            requirement.source,
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(requirement)
    return tuple(rows)


def _apply_combat_encounter_replacements(
    quest_id: str,
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    replacements = QUEST_COMBAT_ENCOUNTER_REPLACEMENTS_BY_ID.get(quest_id, {})
    if not replacements:
        return requirements
    changed = False
    rows = []
    for requirement in requirements:
        replacement_rows = []
        for encounter in requirement.combat_encounters:
            replacement = replacements.get(encounter.encounter_id)
            if replacement is None:
                replacement_rows.append(encounter)
            elif isinstance(replacement, tuple):
                replacement_rows.extend(replacement)
            else:
                replacement_rows.append(replacement)
        combat_encounters = tuple(replacement_rows)
        if combat_encounters != requirement.combat_encounters:
            changed = True
            requirement = replace(requirement, combat_encounters=combat_encounters)
        rows.append(requirement)
    return tuple(rows) if changed else requirements


def _remove_stage_item_names(
    items: Tuple[Tuple[str, int], ...],
    item_names: Tuple[str, ...],
) -> Tuple[Tuple[str, int], ...]:
    if not item_names:
        return items
    names = set(item_names)
    return tuple((name, amount) for name, amount in items if name not in names)


def _remove_stage_option_item_names(
    option_groups: Tuple[Tuple[Tuple[str, int], ...], ...],
    item_names: Tuple[str, ...],
) -> Tuple[Tuple[Tuple[str, int], ...], ...]:
    if not item_names:
        return option_groups
    names = set(item_names)
    cleaned_groups = []
    for option_group in option_groups:
        cleaned_options = tuple((name, amount) for name, amount in option_group if name not in names)
        if cleaned_options:
            cleaned_groups.append(cleaned_options)
    return tuple(cleaned_groups)


def _append_unique_strings(existing: Tuple[str, ...], additions: Tuple[str, ...]) -> Tuple[str, ...]:
    rows = list(existing)
    for value in additions:
        if value and value not in rows:
            rows.append(value)
    return tuple(rows)


def _append_stage_item_pairs(
    existing: Tuple[Tuple[str, int], ...],
    additions: Tuple[Tuple[str, int], ...],
) -> Tuple[Tuple[str, int], ...]:
    rows = list(existing)
    names = {name for name, _ in rows}
    for name, amount in additions:
        if not name:
            continue
        if name in names:
            rows = [(row_name, max(row_amount, amount) if row_name == name else row_amount) for row_name, row_amount in rows]
            continue
        rows.append((name, amount))
        names.add(name)
    return tuple(rows)


def _append_stage_item_options(
    existing: Tuple[Tuple[Tuple[str, int], ...], ...],
    additions: Tuple[Tuple[Tuple[str, int], ...], ...],
) -> Tuple[Tuple[Tuple[str, int], ...], ...]:
    rows = list(existing)
    for option in additions:
        if option and option not in rows:
            rows.append(option)
    return tuple(rows)


def _override_stage_item_pairs(
    items: Tuple[Tuple[str, int], ...],
) -> Tuple[Tuple[str, int], ...]:
    return _append_stage_item_pairs(
        (),
        tuple((QUEST_STAGE_ITEM_NAME_OVERRIDES.get(name, name), amount) for name, amount in items),
    )


def _apply_stage_item_name_overrides(
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    rows = []
    for requirement in requirements:
        rows.append(
            replace(
                requirement,
                required_inventory=_override_stage_item_pairs(requirement.required_inventory),
                required_inventory_options=tuple(
                    _override_stage_item_pairs(option)
                    for option in requirement.required_inventory_options
                ),
                consumed_inventory=_override_stage_item_pairs(requirement.consumed_inventory),
                consumed_inventory_options=tuple(
                    _override_stage_item_pairs(option)
                    for option in requirement.consumed_inventory_options
                ),
                produced_inventory=_override_stage_item_pairs(requirement.produced_inventory),
                required_tools=_override_stage_item_pairs(requirement.required_tools),
            )
        )
    return tuple(rows)


def _apply_stage_requirement_cleanup(
    requirement: QuestStageRequirement,
    cleanup: QuestStageRequirementCleanup,
) -> QuestStageRequirement:
    required_actions = tuple(
        action for action in requirement.required_actions if action not in set(cleanup.remove_required_actions)
    )
    required_routes = tuple(
        route for route in requirement.required_routes if route not in set(cleanup.remove_required_routes)
    )
    return replace(
        requirement,
        required_inventory=_append_stage_item_pairs(
            _remove_stage_item_names(requirement.required_inventory, cleanup.remove_required_inventory),
            cleanup.add_required_inventory,
        ),
        required_inventory_options=_append_stage_item_options(
            _remove_stage_option_item_names(
                requirement.required_inventory_options,
                cleanup.remove_required_inventory_options,
            ),
            cleanup.add_required_inventory_options,
        ),
        consumed_inventory=_append_stage_item_pairs(
            _remove_stage_item_names(requirement.consumed_inventory, cleanup.remove_consumed_inventory),
            cleanup.add_consumed_inventory,
        ),
        consumed_inventory_options=_remove_stage_option_item_names(
            requirement.consumed_inventory_options,
            cleanup.remove_consumed_inventory_options,
        ),
        produced_inventory=_append_stage_item_pairs(requirement.produced_inventory, cleanup.add_produced_inventory),
        required_skills=tuple(
            dict.fromkeys((*requirement.required_skills, *cleanup.add_required_skills))
        ),
        required_tools=_append_stage_item_pairs(
            _remove_stage_item_names(requirement.required_tools, cleanup.remove_required_tools),
            cleanup.add_required_tools,
        ),
        required_actions=_append_unique_strings(required_actions, cleanup.add_required_actions),
        auto_actions=_append_unique_strings(requirement.auto_actions, cleanup.add_auto_actions),
        required_routes=_append_unique_strings(required_routes, cleanup.add_required_routes),
        source=cleanup.source or requirement.source,
    )


def _apply_stage_requirement_cleanups(
    quest_id: str,
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    cleanups = QUEST_STAGE_REQUIREMENT_CLEANUPS_BY_ID.get(quest_id) or ()
    changed = False
    rows = []
    for requirement in requirements:
        updated = requirement
        for cleanup in cleanups:
            if requirement.stage != cleanup.stage:
                continue
            if cleanup.variant and cleanup.variant != requirement.variant:
                continue
            updated = _apply_stage_requirement_cleanup(updated, cleanup)
        changed = changed or updated != requirement
        rows.append(updated)
    return _relocate_combat_encounters(quest_id, tuple(rows) if changed else requirements)


def _apply_tool_belt(
    quest_id: str,
    requirements: Tuple[QuestStageRequirement, ...],
) -> Tuple[QuestStageRequirement, ...]:
    """Keep ``required_inventory`` for tools that must be held and ``required_tools`` for belt tools."""
    rows = []
    for requirement in requirements:
        held = QUEST_STAGES_NEEDING_HELD_TOOLS.get((quest_id, requirement.stage), ())
        to_belt = tuple(
            (name, amount)
            for name, amount in requirement.required_inventory
            if name in TOOL_BELT_TOOLS and amount == 1 and name not in held
        )
        to_held = tuple((name, amount) for name, amount in requirement.required_tools if name in held)
        rows.append(
            replace(
                requirement,
                required_inventory=_append_stage_item_pairs(
                    _remove_stage_item_names(requirement.required_inventory, tuple(name for name, _ in to_belt)),
                    to_held,
                ),
                required_tools=_append_stage_item_pairs(
                    _remove_stage_item_names(requirement.required_tools, held),
                    to_belt,
                ),
            )
        )
    return tuple(rows)


def _quest_with_stage_requirements(quest: QuestDefinition, row: Dict[str, object]) -> QuestDefinition:
    replacements = QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID.get(quest.id)
    if replacements is not None:
        base = replacements
    elif quest.stage_requirements:
        base = quest.stage_requirements
    else:
        base = _catalog_stage_requirements(row.get("stage_requirements", ()))

    additions = QUEST_STAGE_REQUIREMENT_ADDITIONS_BY_ID.get(quest.id, ())
    requirements = _apply_tool_belt(
        quest.id,
        _apply_stage_item_name_overrides(
            _apply_combat_encounter_replacements(
                quest.id,
                _apply_stage_requirement_cleanups(
                    quest.id,
                    _dedupe_stage_requirements((*base, *additions)),
                ),
            )
        ),
    )
    max_requirement_stage = max((requirement.stage for requirement in requirements), default=0)
    configured_stages = QUEST_STAGE_COUNT_REPLACEMENTS_BY_ID.get(quest.id, quest.stages)
    stages = max(configured_stages, max_requirement_stage + 1)
    journal_stages = QUEST_JOURNAL_STAGE_REPLACEMENTS_BY_ID.get(quest.id, quest.journal_stages)
    combat = QUEST_COMBAT_TEXT_REPLACEMENTS_BY_ID.get(quest.id, quest.combat)
    choices = QUEST_CHOICE_REPLACEMENTS_BY_ID.get(quest.id, quest.choices)
    if (
        requirements == quest.stage_requirements
        and stages == quest.stages
        and journal_stages == quest.journal_stages
        and combat == quest.combat
        and choices == quest.choices
    ):
        return quest
    return replace(
        quest,
        stages=stages,
        journal_stages=journal_stages,
        combat=combat,
        stage_requirements=requirements,
        choices=choices,
    )


__all__: tuple[str, ...] = ()
