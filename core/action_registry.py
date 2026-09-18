"""Pure review-action dispatch metadata.

Skill identity stays in ``skill_registry``. This module only answers the runtime
question "which review handler should this active training name use?", including
no-XP Utilities and Activities without pretending either is a levelled skill.
"""

from __future__ import annotations

from typing import Optional, Tuple

from .constants import ACTIVITY_SURFACE_ID, UTILITY_ACTIVITY_DATA
from .skill_registry import (
    CURRENT_SKILLS,
    implemented_review_skill_names,
    review_handler_key,
)
from ..data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID
from ..data.evil_tree_data import EVIL_TREE_UTILITY_ID


UTILITY_REVIEW_ACTION_ID = "utility"
UTILITY_REVIEW_ACTION_DISPLAY_NAME = "Utilities"
ACTIVITY_REVIEW_ACTION_DISPLAY_NAME = "Activities"
_SPECIAL_ACTIVITY_TARGETS = {
    "stronghold_of_security",
    "knight_waves",
    "mage_arena",
    EVIL_TREE_UTILITY_ID,
    BIG_CHINCHOMPA_UTILITY_ID,
}
LEGACY_UTILITY_REVIEW_ACTION_DISPLAY_NAME = "Utility / Activities"
UTILITY_REVIEW_ACTION_ALIASES: Tuple[str, ...] = (
    "Utility",
    UTILITY_REVIEW_ACTION_DISPLAY_NAME,
    ACTIVITY_REVIEW_ACTION_DISPLAY_NAME,
    LEGACY_UTILITY_REVIEW_ACTION_DISPLAY_NAME,
)
QUEST_REVIEW_ACTION_ID = "quest"
QUEST_REVIEW_ACTION_DISPLAY_NAME = "Quests"
QUEST_REVIEW_ACTION_ALIASES: Tuple[str, ...] = ("Quest", QUEST_REVIEW_ACTION_DISPLAY_NAME)
COMBAT_REVIEW_ACTION_ID = "combat"
COMBAT_REVIEW_ACTION_DISPLAY_NAME = "Combat"
COMBAT_REVIEW_ACTION_ALIASES: Tuple[str, ...] = (COMBAT_REVIEW_ACTION_DISPLAY_NAME,)

_UTILITY_REVIEW_ACTION_KEYS = {name.strip().lower() for name in UTILITY_REVIEW_ACTION_ALIASES}
_QUEST_REVIEW_ACTION_KEYS = {name.strip().lower() for name in QUEST_REVIEW_ACTION_ALIASES}
_COMBAT_REVIEW_ACTION_KEYS = {name.strip().lower() for name in COMBAT_REVIEW_ACTION_ALIASES}


def utility_review_surface_for_target(activity_id: str) -> str:
    """Return the review surface that owns a utility/activity target."""
    target = str(activity_id or "")
    if (
        target in _SPECIAL_ACTIVITY_TARGETS
        or target.startswith("mage_arena_attune:")
        or UTILITY_ACTIVITY_DATA.get(target, {}).get("surface")
        == ACTIVITY_SURFACE_ID
    ):
        return ACTIVITY_REVIEW_ACTION_DISPLAY_NAME
    return UTILITY_REVIEW_ACTION_DISPLAY_NAME


def is_utility_review_action(identifier: str) -> bool:
    """Return True for either no-XP surface and their legacy aliases."""
    return str(identifier or "").strip().lower() in _UTILITY_REVIEW_ACTION_KEYS


def is_quest_review_action(identifier: str) -> bool:
    """Return True for the canonical Quest label and its legacy alias."""
    return str(identifier or "").strip().lower() in _QUEST_REVIEW_ACTION_KEYS


def is_combat_review_action(identifier: str) -> bool:
    """Return True for the canonical Combat review action."""
    return str(identifier or "").strip().lower() in _COMBAT_REVIEW_ACTION_KEYS


def review_action_handler_key(identifier: str) -> Optional[str]:
    """Return the registered review handler key for a skill or Utility action."""
    if is_combat_review_action(identifier):
        return COMBAT_REVIEW_ACTION_ID
    if is_utility_review_action(identifier):
        return UTILITY_REVIEW_ACTION_ID
    if is_quest_review_action(identifier):
        return QUEST_REVIEW_ACTION_ID
    return review_handler_key(identifier)


def review_handler_target_key(handler_key: str) -> Optional[str]:
    """The ``player_data`` key that names a review handler's active target."""
    for skill in CURRENT_SKILLS:
        if skill.review_handler_key == handler_key:
            return skill.current_target_key
    return None


def is_review_action(identifier: str) -> bool:
    """Return True when an active name can produce review rewards."""
    return review_action_handler_key(identifier) is not None


def review_action_display_names() -> Tuple[str, ...]:
    """Display names that may run from the review-answer hook."""
    return implemented_review_skill_names() + (
        COMBAT_REVIEW_ACTION_DISPLAY_NAME,
        QUEST_REVIEW_ACTION_DISPLAY_NAME,
        UTILITY_REVIEW_ACTION_DISPLAY_NAME,
        ACTIVITY_REVIEW_ACTION_DISPLAY_NAME,
    )
