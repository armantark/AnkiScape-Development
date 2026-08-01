"""Music Log: a passive collection that unlocks itself from durable state.

There is no audio. The log records the complete named cutoff catalog and keeps
feature-owned rows visible as latent until AnkiScape has durable evidence for
their unlock.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..data.music_log_data import MUSIC_TRACKS, MusicTrack
from .achievement_diary_logic import MUSIC_UNLOCK_TASK_COUNT, diary_totals_pure


MUSIC_LOG_STATE_VERSION = 1
_EVALUATABLE_TRACKS = tuple(
    track for track in MUSIC_TRACKS if track.trigger_kind != "latent"
)

_ACTIVITY_EVIDENCE_KEYS: dict[str, tuple[str, ...]] = {
    "barbarian_assault": ("barbarian_assault_runs_completed",),
    "castle_wars": ("castle_wars_games_played",),
    "conquest": ("conquest_matches_started",),
    "fist_of_guthix": ("fist_of_guthix.matches_started",),
    "gnome_ball": ("gnome_ball_runs_completed",),
    "mobilising_armies": ("mobilising_armies_games_played",),
    "pyramid_plunder": ("pyramid_plunder_runs_completed",),
    "soul_wars": ("soul_wars_games_played",),
    "troll_invasion": ("troll_invasion_completions",),
}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _int(value: Any) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def _value_at(player_data: Mapping[str, Any], dotted_key: str) -> Any:
    value: Any = player_data
    for part in dotted_key.split("."):
        if not isinstance(value, Mapping) or part not in value:
            return None
        value = value[part]
    return value


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

    "The Task at Hand" needs 350 completed tasks. Latent diary rows reserve the
    cutoff denominator but cannot complete, so the track activates only when at
    least 350 task predicates are obtainable. Tracks whose own trigger is
    explicitly latent stay excluded until their owning feature ships.
    """

    if track.trigger_kind == "latent":
        return True
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


def _activity_started_pure(player_data: Mapping[str, Any], activity_id: str) -> bool:
    session = _mapping(player_data.get("activity_session"))
    if session.get("active_id") == activity_id:
        return True
    if player_data.get("current_utility") == activity_id:
        return True
    return any(
        _int(_value_at(player_data, key)) > 0
        for key in _ACTIVITY_EVIDENCE_KEYS.get(activity_id, ())
    )


def track_unlocked_now_pure(player_data: Mapping[str, Any], track: MusicTrack) -> bool:
    """Whether the track's own source-shaped trigger is satisfied now."""

    if track.trigger_kind == "quest":
        state = _mapping(_mapping(player_data.get("quests")).get(track.trigger_key))
        return bool(state.get("completed"))
    if track.trigger_kind == "task_count":
        return diary_totals_pure(player_data)["completed"] >= MUSIC_UNLOCK_TASK_COUNT
    if track.trigger_kind == "activity":
        return _activity_started_pure(player_data, track.trigger_key)
    if track.trigger_kind == "enemy":
        return _int(
            _mapping(player_data.get("combat_kill_counts")).get(track.trigger_key)
        ) > 0
    return False


def refresh_music_log_pure(
    player_data: Mapping[str, Any]
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Unlock every newly earned track and return the names that just landed."""

    data = dict(player_data)
    state = sanitize_music_log_state_pure(data)["music_log"]
    unlocked = list(state["unlocked_tracks"])
    known = set(unlocked)
    newly: list[str] = []
    for track in _EVALUATABLE_TRACKS:
        if track.id in known or track_is_latent_pure(track):
            continue
        if track_unlocked_now_pure(data, track):
            unlocked.append(track.id)
            known.add(track.id)
            newly.append(track.name)
    state["unlocked_tracks"] = sorted(unlocked)
    data["music_log"] = state
    return data, tuple(newly)


def music_log_totals_pure(player_data: Mapping[str, Any]) -> dict[str, int]:
    """Return full-cutoff totals; latent rows remain in the denominator."""

    state = sanitize_music_log_state_pure(player_data)["music_log"]
    return {
        "unlocked": len(state["unlocked_tracks"]),
        "total": len(MUSIC_TRACKS),
        "latent": sum(track_is_latent_pure(track) for track in MUSIC_TRACKS),
    }


def music_log_view_pure(
    player_data: Mapping[str, Any],
    *,
    search: str = "",
    completion_filter: str = "",
) -> dict[str, Any]:
    """Everything the Collections Music Log renders, including filter decisions."""

    state = sanitize_music_log_state_pure(player_data)["music_log"]
    unlocked = set(state["unlocked_tracks"])
    needle = search.strip().lower()
    rows: list[dict[str, Any]] = []
    for track in MUSIC_TRACKS:
        done = track.id in unlocked
        latent = track_is_latent_pure(track)
        if completion_filter == "unlocked" and not done:
            continue
        if completion_filter == "locked" and done:
            continue
        if completion_filter == "latent" and not latent:
            continue
        if needle and needle not in f"{track.name} {track.hint} {track.source}".lower():
            continue
        rows.append(
            {
                "track_id": track.id,
                "name": track.name,
                "hint": track.hint,
                "source": track.source,
                "unlocked": done,
                "latent": latent,
                "status": "Unlocked" if done else ("Latent" if latent else "Locked"),
                "trigger": track.trigger_kind,
            }
        )
    totals = music_log_totals_pure(player_data)
    return {"tracks": tuple(rows), **totals}
