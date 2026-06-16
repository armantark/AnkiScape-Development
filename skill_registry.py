"""Backend skill catalog for AnkiScape.

The registry preserves today's display-name based save behavior while giving
future skills stable IDs and categories. Keeping this pure avoids importing
Anki/Qt during tests and lets storage migrations share the same source of truth
as review dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Literal, Optional, Tuple


SkillCategory = Literal["combat", "gathering", "artisan", "support"]
ActionKind = Literal["gather", "process", "combat", "support"]


@dataclass(frozen=True)
class SkillDefinition:
    id: str
    display_name: str
    category: SkillCategory
    implemented: bool
    participates_in_review: bool
    action_kind: ActionKind
    level_key: str
    exp_key: str
    current_target_key: Optional[str] = None
    default_target: Optional[str] = None
    review_handler_key: Optional[str] = None
    visible_in_skill_hub: bool = True


CURRENT_SKILLS: Tuple[SkillDefinition, ...] = (
    SkillDefinition(
        id="mining",
        display_name="Mining",
        category="gathering",
        implemented=True,
        participates_in_review=True,
        action_kind="gather",
        level_key="mining_level",
        exp_key="mining_exp",
        current_target_key="current_ore",
        default_target="rune_essence",
        review_handler_key="mining",
    ),
    SkillDefinition(
        id="woodcutting",
        display_name="Woodcutting",
        category="gathering",
        implemented=True,
        participates_in_review=True,
        action_kind="gather",
        level_key="woodcutting_level",
        exp_key="woodcutting_exp",
        current_target_key="current_tree",
        default_target="tree",
        review_handler_key="woodcutting",
    ),
    SkillDefinition(
        id="fishing",
        display_name="Fishing",
        category="gathering",
        implemented=True,
        participates_in_review=True,
        action_kind="gather",
        level_key="fishing_level",
        exp_key="fishing_exp",
        current_target_key="current_fishing",
        default_target="catch_crayfish",
        review_handler_key="fishing",
    ),
    SkillDefinition(
        id="smithing",
        display_name="Smithing",
        category="artisan",
        implemented=True,
        participates_in_review=True,
        action_kind="process",
        level_key="smithing_level",
        exp_key="smithing_exp",
        current_target_key="current_smith",
        default_target="smelt_bronze_bar",
        review_handler_key="smithing",
    ),
    SkillDefinition(
        id="crafting",
        display_name="Crafting",
        category="artisan",
        implemented=True,
        participates_in_review=True,
        action_kind="process",
        level_key="crafting_level",
        exp_key="crafting_exp",
        current_target_key="current_craft",
        default_target="form_pot_unfired",
        review_handler_key="crafting",
    ),
    SkillDefinition(
        id="fletching",
        display_name="Fletching",
        category="artisan",
        implemented=True,
        participates_in_review=True,
        action_kind="process",
        level_key="fletching_level",
        exp_key="fletching_exp",
        current_target_key="current_fletch",
        default_target="arrow_shafts",
        review_handler_key="fletching",
        visible_in_skill_hub=True,
    ),
    SkillDefinition(
        id="firemaking",
        display_name="Firemaking",
        category="artisan",
        implemented=True,
        participates_in_review=True,
        action_kind="process",
        level_key="firemaking_level",
        exp_key="firemaking_exp",
        current_target_key="current_firemaking",
        default_target="logs",
        review_handler_key="firemaking",
        visible_in_skill_hub=True,
    ),
)


PLANNED_SKILLS: Tuple[SkillDefinition, ...] = (
    SkillDefinition("attack", "Attack", "combat", False, False, "combat", "attack_level", "attack_exp"),
    SkillDefinition("constitution", "Constitution", "combat", False, False, "combat", "constitution_level", "constitution_exp"),
    SkillDefinition("defense", "Defense", "combat", False, False, "combat", "defense_level", "defense_exp"),
    SkillDefinition("magic", "Magic", "combat", False, False, "combat", "magic_level", "magic_exp"),
    SkillDefinition("prayer", "Prayer", "combat", False, False, "combat", "prayer_level", "prayer_exp"),
    SkillDefinition("ranged", "Ranged", "combat", False, False, "combat", "ranged_level", "ranged_exp"),
    SkillDefinition("strength", "Strength", "combat", False, False, "combat", "strength_level", "strength_exp"),
    SkillDefinition("summoning", "Summoning", "combat", False, False, "combat", "summoning_level", "summoning_exp"),
    SkillDefinition("construction", "Construction", "artisan", False, False, "process", "construction_level", "construction_exp"),
    SkillDefinition("cooking", "Cooking", "artisan", False, False, "process", "cooking_level", "cooking_exp"),
    SkillDefinition("herblore", "Herblore", "artisan", False, False, "process", "herblore_level", "herblore_exp"),
    SkillDefinition("runecrafting", "Runecrafting", "artisan", False, False, "process", "runecrafting_level", "runecrafting_exp"),
    SkillDefinition("farming", "Farming", "gathering", False, False, "gather", "farming_level", "farming_exp"),
    SkillDefinition("hunter", "Hunter", "gathering", False, False, "gather", "hunter_level", "hunter_exp"),
    SkillDefinition("agility", "Agility", "support", False, False, "support", "agility_level", "agility_exp"),
    SkillDefinition("dungeoneering", "Dungeoneering", "support", False, False, "support", "dungeoneering_level", "dungeoneering_exp"),
    SkillDefinition("slayer", "Slayer", "support", False, False, "support", "slayer_level", "slayer_exp"),
    SkillDefinition("thieving", "Thieving", "support", False, False, "support", "thieving_level", "thieving_exp"),
)


ALL_SKILLS: Tuple[SkillDefinition, ...] = CURRENT_SKILLS + PLANNED_SKILLS


def _index_by_id(skills: Iterable[SkillDefinition]) -> Dict[str, SkillDefinition]:
    return {skill.id: skill for skill in skills}


def _index_by_display_name(skills: Iterable[SkillDefinition]) -> Dict[str, SkillDefinition]:
    return {skill.display_name.lower(): skill for skill in skills}


_SKILLS_BY_ID = _index_by_id(ALL_SKILLS)
_SKILLS_BY_DISPLAY_NAME = _index_by_display_name(ALL_SKILLS)


def get_skill(identifier: str) -> Optional[SkillDefinition]:
    key = identifier.strip().lower()
    return _SKILLS_BY_ID.get(key) or _SKILLS_BY_DISPLAY_NAME.get(key)


def implemented_review_skill_names() -> Tuple[str, ...]:
    return tuple(skill.display_name for skill in ALL_SKILLS if skill.implemented and skill.participates_in_review)


def implemented_skill_definitions() -> Tuple[SkillDefinition, ...]:
    return tuple(skill for skill in ALL_SKILLS if skill.implemented)


def planned_skill_definitions() -> Tuple[SkillDefinition, ...]:
    return tuple(skill for skill in ALL_SKILLS if not skill.implemented)


def is_review_skill(identifier: str) -> bool:
    skill = get_skill(identifier)
    return bool(skill and skill.implemented and skill.participates_in_review)


def is_skill_hub_visible(identifier: str) -> bool:
    skill = get_skill(identifier)
    return bool(skill and skill.visible_in_skill_hub)


def review_handler_key(identifier: str) -> Optional[str]:
    skill = get_skill(identifier)
    if skill is None or not skill.implemented or not skill.participates_in_review:
        return None
    return skill.review_handler_key


def skill_level_exp_keys(identifier: str) -> Optional[Tuple[str, str]]:
    skill = get_skill(identifier)
    if skill is None:
        return None
    return skill.level_key, skill.exp_key


def default_skill_state() -> Dict[str, int]:
    defaults: Dict[str, int] = {}
    for skill in implemented_skill_definitions():
        defaults[skill.level_key] = 1
        defaults[skill.exp_key] = 0
    return defaults


def default_target_state() -> Dict[str, str]:
    defaults: Dict[str, str] = {}
    for skill in implemented_skill_definitions():
        if skill.current_target_key is not None and skill.default_target is not None:
            defaults[skill.current_target_key] = skill.default_target
    return defaults
