"""Music Log: the period track table and its unlock triggers.

The design contract asks for a passive log under Collections that records track
names, hints, provenance and completion state, unlocks tracks automatically
from the features they belong to, and whose full collection satisfies the
Completionist cape's music requirement.

The catalog is generated — see ``tools/harvest_music_log.py`` for the source
and for the one abstraction the translation makes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


MUSIC_SOURCE = (
    "darkan-world-server c95aca409f397cab12c13b6d5269b73f6cd8abe9"
    " data/music/songs.json; period track names, hints and ids"
)

# Trigger kinds. Each names durable state that already exists in the save.
TRIGGER_KINDS: Tuple[str, ...] = (
    "quest",       # key: quest id — the track's own quest is complete
    "task_count",  # no key: the achievement-task milestone below
)


@dataclass(frozen=True)
class MusicTrack:
    id: int
    name: str
    hint: str
    trigger_kind: str
    trigger_key: str = ""


from .music_log_catalog import MUSIC_TRACKS  # noqa: E402  (avoids a cycle at import)

MUSIC_TRACKS_BY_ID = {track.id: track for track in MUSIC_TRACKS}

__all__ = [
    "MUSIC_SOURCE",
    "MUSIC_TRACKS",
    "MUSIC_TRACKS_BY_ID",
    "MusicTrack",
    "TRIGGER_KINDS",
]
