"""Music Log: a passive collection that unlocks itself from durable state.

The design contract puts this under Collections and gives it three jobs: record
every period track with its name, hint and provenance; unlock a track the
moment the feature it belongs to is finished; and, when the whole log is
collected, satisfy the Completionist cape's music requirement.

There is no audio. A track is a record, and the log is the record of records —
which is exactly what the period's own music interface was for a player who had
muted the game.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..data.music_log_data import MUSIC_TRACKS, MusicTrack
from .achievement_diary_logic import MUSIC_UNLOCK_TASK_COUNT, diary_totals_pure


MUSIC_LOG_STATE_VERSION = 1


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int_list(value: Any) -> list[int]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    known = {track.id for track in MUSIC_TRACKS}
    seen: dict[int, None] = {}
    for entry in value:
        try:
            track_id = int(entry)
        except (TypeError, ValueError):
            continue
        if track_id in known:
            seen.setdefault(track_id, None)
    return sorted(seen)


def default_music_log_state_pure() -> dict[str, Any]:
    return {
        "music_log": {
            "version": MUSIC_LOG_STATE_VERSION,
            "unlocked_tracks": [],
        }
    }


def sanitize_music_log_state_pure(
    player_data: Mapping[str, Any] | None,
) -> dict[str, Any]:
    source = _mapping(_mapping(player_data).get("music_log"))
    return {
        "music_log": {
            "version": MUSIC_LOG_STATE_VERSION,
            "unlocked_tracks": _int_list(source.get("unlocked_tracks")),
        }
    }


def track_is_latent_pure(track: MusicTrack) -> bool:
    """Whether the feature this track belongs to has not shipped yet.

    The design contract: "tracks owned by unfinished features remain latent and
    activate with those features". A latent track still appears in the log, so
    the player can see what is coming, but it is left out of the log's own
    denominator — otherwise the Completionist cape's music requirement would be
    gated on content that does not exist, which is how a reward becomes an
    ornament.

    Today there is exactly one: "The Task at Hand" needs 350 completed tasks.
    Latent diary rows reserve the cutoff denominator but cannot complete, so the
    track activates only when at least 350 task predicates are obtainable.
    """

    if track.trigger_kind != "task_count":
        return False
    from ..data.achievement_diary_data import ACHIEVEMENT_DIARY_CATALOG

    obtainable = sum(
        1
        for family in ACHIEVEMENT_DIARY_CATALOG
        for tier in family.tiers
        for task in tier.tasks
        if not task.latent
    )
    return obtainable < MUSIC_UNLOCK_TASK_COUNT


def track_unlocked_now_pure(player_data: Mapping[str, Any], track: MusicTrack) -> bool:
    """Whether the track's own trigger is satisfied by durable state right now."""

    if track.trigger_kind == "quest":
        state = _mapping(_mapping(player_data.get("quests")).get(track.trigger_key))
        return bool(state.get("completed"))
    if track.trigger_kind == "task_count":
        # The one place `MUSIC_UNLOCK_TASK_COUNT` is read: the period achievement
        # system gave "The Task at Hand" at 350 completed tasks, and songs.json
        # carries that same figure in the track's own hint.
        return diary_totals_pure(player_data)["completed"] >= MUSIC_UNLOCK_TASK_COUNT
    if track.trigger_kind == "activity":
        return bool(
            track.trigger_key == "conquest"
            and int(player_data.get("conquest_matches_started", 0) or 0) > 0
        )
    return False


def refresh_music_log_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Unlock every newly earned track and return the names that just landed.

    Unlocks are sticky for the same reason completed achievement names are: the
    track was heard, and nothing later can un-hear it.
    """

    data = dict(player_data)
    state = sanitize_music_log_state_pure(data)["music_log"]
    unlocked = list(state["unlocked_tracks"])
    known = set(unlocked)
    newly: list[str] = []
    for track in MUSIC_TRACKS:
        if track.id in known:
            continue
        if track_unlocked_now_pure(data, track):
            unlocked.append(track.id)
            known.add(track.id)
            newly.append(track.name)
    state["unlocked_tracks"] = sorted(unlocked)
    data["music_log"] = state
    return data, tuple(newly)


def music_log_totals_pure(player_data: Mapping[str, Any]) -> dict[str, int]:
    """``total`` counts only the tracks a player can currently reach."""

    state = sanitize_music_log_state_pure(player_data)["music_log"]
    live = tuple(track for track in MUSIC_TRACKS if not track_is_latent_pure(track))
    return {
        "unlocked": len(state["unlocked_tracks"]),
        "total": len(live),
        "latent": len(MUSIC_TRACKS) - len(live),
    }


def music_log_view_pure(
    player_data: Mapping[str, Any],
    *,
    search: str = "",
    completion_filter: str = "",
) -> dict[str, Any]:
    """Everything the Music Log renders, including its own filter decisions."""

    state = sanitize_music_log_state_pure(player_data)["music_log"]
    unlocked = set(state["unlocked_tracks"])
    needle = search.strip().lower()
    rows: list[dict[str, Any]] = []
    for track in MUSIC_TRACKS:
        done = track.id in unlocked
        if completion_filter == "unlocked" and not done:
            continue
        if completion_filter == "locked" and done:
            continue
        if needle and needle not in f"{track.name} {track.hint}".lower():
            continue
        rows.append(
            {
                "track_id": track.id,
                "name": track.name,
                "hint": track.hint,
                "unlocked": done,
                "latent": track_is_latent_pure(track),
                "trigger": track.trigger_kind,
            }
        )
    totals = music_log_totals_pure(player_data)
    return {"tracks": tuple(rows), **totals}
