"""Music Log: the period track table and its unlock triggers.

The design contract asks for a passive log under Collections that records track
names, hints, provenance and completion state, unlocks tracks automatically
from the features they belong to, and whose full collection satisfies the
Completionist cape's music requirement.

The catalog is generated — see ``tools/harvest_music_log.py`` for the pinned
source rows and the source-shaped trigger transcription.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


MUSIC_SOURCE = (
    "darkan-world-server c95aca409f397cab12c13b6d5269b73f6cd8abe9"
    " data/music/songs.json"
)

# Trigger kinds. Each live kind names durable state that already exists in the
# save. ``latent`` retains a sourced row whose owning feature has no honest
# AnkiScape predicate yet.
TRIGGER_KINDS: Tuple[str, ...] = (
    "quest",
    "task_count",
    "activity",
    "enemy",
    "latent",
)


@dataclass(frozen=True)
class MusicTrack:
    id: int
    name: str
    hint: str
    trigger_kind: str
    trigger_key: str = ""
    source: str = ""


def music_track_source(track_id: int) -> str:
    return f"{MUSIC_SOURCE}; song id {track_id}"


from .music_log_catalog import MUSIC_TRACKS  # noqa: E402

MUSIC_TRACKS_BY_ID = {track.id: track for track in MUSIC_TRACKS}

__all__ = [
    "MUSIC_SOURCE",
    "MUSIC_TRACKS",
    "MUSIC_TRACKS_BY_ID",
    "MusicTrack",
    "TRIGGER_KINDS",
    "music_track_source",
]
