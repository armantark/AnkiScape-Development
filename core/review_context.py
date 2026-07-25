"""Pure projection and preference helpers for rare reviewer context actions."""

from __future__ import annotations

import copy
from typing import Any, Mapping, Optional

from ..data.phoenix_lair_data import PHOENIX_EGG_CONTEXT_ID


PIT_REWARD_CONTEXT_ID = "pit_reward"
PIT_REWARD_OPTIONS = (
    {"id": "take_xp", "label": "Take XP"},
    {"id": "gamble", "label": "Gamble"},
)
PHOENIX_EGG_OPTIONS = (
    {"id": "clap", "label": "Clap"},
    {"id": "kick", "label": "Kick"},
)
_CONTEXT_OPTIONS = {
    PIT_REWARD_CONTEXT_ID: tuple(option["id"] for option in PIT_REWARD_OPTIONS),
    PHOENIX_EGG_CONTEXT_ID: tuple(option["id"] for option in PHOENIX_EGG_OPTIONS),
}
_CONTEXT_DEFAULTS = {
    PIT_REWARD_CONTEXT_ID: "take_xp",
    PHOENIX_EGG_CONTEXT_ID: "clap",
}


def default_review_context_state_pure() -> dict[str, Any]:
    return {"review_context_preferences": {}}


def sanitize_review_context_state_pure(
    player_data: Optional[Mapping[str, Any]],
) -> dict[str, Any]:
    data = dict(player_data or {})
    raw_preferences = data.get("review_context_preferences")
    raw_preferences = raw_preferences if isinstance(raw_preferences, Mapping) else {}
    data["review_context_preferences"] = {
        family_id: str(raw_preferences.get(family_id))
        for family_id, valid_options in _CONTEXT_OPTIONS.items()
        if str(raw_preferences.get(family_id)) in valid_options
    }
    return data


def remembered_review_context_choice_pure(
    player_data: Mapping[str, Any],
    family_id: str,
) -> Optional[str]:
    preferences = sanitize_review_context_state_pure(player_data)[
        "review_context_preferences"
    ]
    choice = preferences.get(family_id)
    valid_options = _CONTEXT_OPTIONS.get(family_id, ())
    return str(choice) if choice in valid_options else None


def remember_review_context_choice_pure(
    player_data: Mapping[str, Any],
    family_id: str,
    option_id: str,
) -> dict[str, Any]:
    valid_options = _CONTEXT_OPTIONS.get(family_id, ())
    if option_id not in valid_options:
        return copy.deepcopy(dict(player_data))
    data = copy.deepcopy(sanitize_review_context_state_pure(player_data))
    preferences = dict(data["review_context_preferences"])
    preferences[family_id] = option_id
    data["review_context_preferences"] = preferences
    return data


def review_context_projection_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    activities = player_data.get("agility_activity_state")
    reward = activities.get("pit_reward") if isinstance(activities, Mapping) else None
    rows: list[dict[str, Any]] = []
    if isinstance(reward, Mapping):
        try:
            xp = float(reward.get("xp", 0.0) or 0.0)
        except (TypeError, ValueError, OverflowError):
            xp = 0.0
        if xp > 0:
            rows.append(
                {
                    "family_id": PIT_REWARD_CONTEXT_ID,
                    "label": "Pit reward",
                    "detail": f"{xp:,.6g} Agility XP",
                    "options": PIT_REWARD_OPTIONS,
                    "default_option": _CONTEXT_DEFAULTS[PIT_REWARD_CONTEXT_ID],
                    "remembered_option": remembered_review_context_choice_pure(
                        player_data,
                        PIT_REWARD_CONTEXT_ID,
                    ),
                }
            )
    phoenix = player_data.get("phoenix_lair")
    if isinstance(phoenix, Mapping) and bool(phoenix.get("pending_egg", False)):
        rows.append(
            {
                "family_id": PHOENIX_EGG_CONTEXT_ID,
                "label": "Phoenix egg",
                "detail": "Clap for Cute · Kick for Mean",
                "options": PHOENIX_EGG_OPTIONS,
                "default_option": _CONTEXT_DEFAULTS[PHOENIX_EGG_CONTEXT_ID],
                "remembered_option": remembered_review_context_choice_pure(
                    player_data,
                    PHOENIX_EGG_CONTEXT_ID,
                ),
            }
        )
    return {
        "active": rows[0] if rows else None,
        "queued_count": max(0, len(rows) - 1),
    }


def ignored_review_context_choice_pure(
    player_data: Mapping[str, Any],
) -> Optional[tuple[str, str]]:
    active = review_context_projection_pure(player_data)["active"]
    if not isinstance(active, Mapping):
        return None
    family_id = str(active.get("family_id", ""))
    valid_options = _CONTEXT_OPTIONS.get(family_id, ())
    remembered = remembered_review_context_choice_pure(player_data, family_id)
    default = str(active.get("default_option", ""))
    choice = remembered if remembered in valid_options else default
    if choice not in valid_options:
        return None
    return family_id, choice
