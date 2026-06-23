"""Pure review-action dispatch metadata.

Skill identity stays in ``skill_registry``. This module only answers the runtime
question "which review handler should this active training name use?", including
no-XP Utility/Activities without pretending it is a levelled skill.
"""

from __future__ import annotations

from typing import Optional, Tuple

try:
    from .skill_registry import implemented_review_skill_names, review_handler_key
except ImportError:  # pragma: no cover - flat import path used by the test runner
    from skill_registry import implemented_review_skill_names, review_handler_key  # type: ignore


UTILITY_REVIEW_ACTION_ID = "utility"
UTILITY_REVIEW_ACTION_DISPLAY_NAME = "Utility / Activities"
UTILITY_REVIEW_ACTION_ALIASES: Tuple[str, ...] = ("Utility", UTILITY_REVIEW_ACTION_DISPLAY_NAME)
QUEST_REVIEW_ACTION_ID = "quest"
QUEST_REVIEW_ACTION_DISPLAY_NAME = "Quests"
QUEST_REVIEW_ACTION_ALIASES: Tuple[str, ...] = ("Quest", QUEST_REVIEW_ACTION_DISPLAY_NAME)
COMBAT_REVIEW_ACTION_ID = "combat"
COMBAT_REVIEW_ACTION_DISPLAY_NAME = "Combat"
COMBAT_REVIEW_ACTION_ALIASES: Tuple[str, ...] = (COMBAT_REVIEW_ACTION_DISPLAY_NAME,)

_UTILITY_REVIEW_ACTION_KEYS = {name.strip().lower() for name in UTILITY_REVIEW_ACTION_ALIASES}
_QUEST_REVIEW_ACTION_KEYS = {name.strip().lower() for name in QUEST_REVIEW_ACTION_ALIASES}
_COMBAT_REVIEW_ACTION_KEYS = {name.strip().lower() for name in COMBAT_REVIEW_ACTION_ALIASES}


def is_utility_review_action(identifier: str) -> bool:
    """Return True for the canonical Utility label and its legacy alias."""
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


def is_review_action(identifier: str) -> bool:
    """Return True when an active name can produce review rewards."""
    return review_action_handler_key(identifier) is not None


def review_action_display_names() -> Tuple[str, ...]:
    """Display names that may run from the review-answer hook."""
    return implemented_review_skill_names() + (
        COMBAT_REVIEW_ACTION_DISPLAY_NAME,
        QUEST_REVIEW_ACTION_DISPLAY_NAME,
        UTILITY_REVIEW_ACTION_DISPLAY_NAME,
    )
