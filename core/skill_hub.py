"""Pure view-model helpers for the Qt Skills hub.

The menu historically exposed one top-level tab per skill (Mining, Woodcutting,
Smithing, Crafting). The roadmap moves skill navigation into a single Skills hub
so the top bar can stay limited to global sections. These helpers are kept
Qt-free and registry-backed so the grouping logic can be unit tested without
Anki and reused by ``ui.py`` without duplicating category knowledge.

Normal mode surfaces only playable skills. Developer mode additionally surfaces
hub-visible planned skills so the rest of the 2011-era skill set can be
inspected while its mechanics are still unimplemented.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from ..core.skill_registry import ALL_SKILLS, SkillDefinition


# Display order is fixed so the hub layout stays stable across renders.
# No-XP Utilities and Activities are injected by ``ui.py`` because neither is a
# registry skill. The retained utility slot keeps future registry grouping
# deterministic without merging the two live surfaces.
CATEGORY_ORDER: Tuple[str, ...] = ("combat", "gathering", "artisan", "support", "utility")

CATEGORY_DISPLAY_NAMES: Dict[str, str] = {
    "combat": "Combat",
    "gathering": "Gathering",
    "artisan": "Artisan",
    "support": "Support",
    "utility": "Utilities",
}


@dataclass(frozen=True)
class SkillCardView:
    """One selectable skill entry inside a category."""

    skill_id: str
    display_name: str
    category: str
    implemented: bool
    selectable_for_review: bool
    surface_state: str = "complete"
    training_source: str = ""


@dataclass(frozen=True)
class CategoryView:
    """A category and the skills that should render under it."""

    category_id: str
    display_name: str
    skills: Tuple[SkillCardView, ...]


def _card_from_definition(skill: SkillDefinition) -> SkillCardView:
    return SkillCardView(
        skill_id=skill.id,
        display_name=skill.display_name,
        category=skill.category,
        implemented=bool(skill.implemented and skill.visible_in_skill_hub),
        selectable_for_review=bool(skill.implemented and skill.visible_in_skill_hub and skill.participates_in_review),
        surface_state=skill.surface_state,
        training_source=skill.training_source or "",
    )


def build_skill_hub(*, include_planned: bool) -> Tuple[CategoryView, ...]:
    """Group skills by category for the hub.

    ``include_planned`` mirrors developer mode: when ``False`` only implemented
    skills are returned, and empty categories are omitted entirely so normal
    users never see a category they cannot train in.
    """

    categories: List[CategoryView] = []
    for category_id in CATEGORY_ORDER:
        cards = tuple(
            _card_from_definition(skill)
            for skill in ALL_SKILLS
            if (
                skill.category == category_id
                and skill.visible_in_skill_hub
                and (include_planned or skill.implemented)
            )
        )
        if not cards:
            continue
        categories.append(
            CategoryView(
                category_id=category_id,
                display_name=CATEGORY_DISPLAY_NAMES.get(category_id, category_id.title()),
                skills=cards,
            )
        )
    return tuple(categories)


def first_category_id(hub: Tuple[CategoryView, ...]) -> str:
    """Return the id of the first non-empty category, or ``""`` when none."""

    return hub[0].category_id if hub else ""
