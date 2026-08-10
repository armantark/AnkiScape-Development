"""Persistent Dagannoth Kings room on the shared boss-room substrate."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..data.dagannoth_kings_data import (
    DAGANNOTH_KING_IDS,
    DAGANNOTH_KINGS_ACTIVITY_ID,
    DAGANNOTH_KINGS_ENEMY_DATA,
    DAGANNOTH_KINGS_REVIEW_TICKS,
)
from .boss_room_logic import (
    apply_boss_room_command_pure,
    apply_boss_room_review_pure,
    boss_room_view_pure,
    default_boss_room_state_pure,
    sanitize_boss_room_state_pure,
)


DAGANNOTH_KINGS_STATE_KEY = "dagannoth_kings"


def default_dagannoth_kings_state_pure() -> dict[str, Any]:
    return default_boss_room_state_pure()


def sanitize_dagannoth_kings_state_pure(raw: Any) -> dict[str, Any]:
    return sanitize_boss_room_state_pure(
        raw, DAGANNOTH_KINGS_ENEMY_DATA, DAGANNOTH_KING_IDS
    )


def dagannoth_kings_view_pure(player_data: Mapping[str, Any]) -> dict[str, Any]:
    return boss_room_view_pure(
        player_data,
        state_key=DAGANNOTH_KINGS_STATE_KEY,
        enemy_data=DAGANNOTH_KINGS_ENEMY_DATA,
        enemy_ids=DAGANNOTH_KING_IDS,
        review_ticks=DAGANNOTH_KINGS_REVIEW_TICKS,
    )


def apply_dagannoth_kings_command_pure(
    player_data: Mapping[str, Any],
    action_id: str,
    payload: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    return apply_boss_room_command_pure(
        player_data,
        action_id,
        payload,
        activity_id=DAGANNOTH_KINGS_ACTIVITY_ID,
        display_name="the Dagannoth Kings room",
        state_key=DAGANNOTH_KINGS_STATE_KEY,
        enemy_data=DAGANNOTH_KINGS_ENEMY_DATA,
        enemy_ids=DAGANNOTH_KING_IDS,
    )


def apply_dagannoth_kings_review_pure(
    player_data: Mapping[str, Any],
    rng,
    *,
    equipment_data: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], bool, dict[str, Any]]:
    return apply_boss_room_review_pure(
        player_data,
        rng,
        activity_id=DAGANNOTH_KINGS_ACTIVITY_ID,
        display_name="the Dagannoth Kings room",
        state_key=DAGANNOTH_KINGS_STATE_KEY,
        enemy_data=DAGANNOTH_KINGS_ENEMY_DATA,
        enemy_ids=DAGANNOTH_KING_IDS,
        review_ticks=DAGANNOTH_KINGS_REVIEW_TICKS,
        equipment_data=equipment_data,
    )
