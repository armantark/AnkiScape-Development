"""Generate ``data/music_log_catalog.py`` from Darkan's period song table.

Source, top of the project's evidence order:
``darkan-world-server/data/music/songs.json`` — the Nov-2012 song table, one
row per music archive with the period ``name`` and ``hint``. Blank-name archive
rows are not tracks the source can identify and are omitted rather than given
invented names. Every named row is retained.

Trigger transcription is deliberately narrow. Quest rows use the shipped quest
named by a completion/participation hint. Activity and enemy rows use the exact
source ids listed below, whose hints name a shipped feature. The remaining
source rows stay latent until their owning world feature has a durable
AnkiScape predicate.

Run:

    python3 tools/harvest_music_log.py
"""

from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pkg_alias  # noqa: E402,F401

from ankiscape.data.quest_data import QUESTS  # noqa: E402

SONGS_JSON = (
    "/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server"
    "/data/music/songs.json"
)
DARKAN_COMMIT = "c95aca409f397cab12c13b6d5269b73f6cd8abe9"
OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "music_log_catalog.py",
)

COMPLETION_HINT = re.compile(
    r"^(during|on completion of|on completing|after completing|upon completing|by completing)\b"
)
TASK_TRACK_ID = 941

# Exact source rows whose hints name a shipped activity rather than only a map
# location. The activity id is the same stable id used by the utility surface.
_ACTIVITY_TRACK_IDS = {
    38: "fishing_trawler",
    47: "duel_arena",
    51: "fishing_trawler",
    112: "gnome_ball",
    211: "barbarian_assault",
    228: "sorceress_garden",
    229: "sorceress_garden",
    230: "sorceress_garden",
    231: "sorceress_garden",
    309: "varrock_museum",
    314: "castle_wars",
    317: "castle_wars",
    318: "castle_wars",
    380: "barrows",
    381: "barrows",
    442: "clan_wars",
    463: "tzhaar_fight_pit",
    473: "fight_caves",
    487: "vinesweeper",
    492: "stronghold_player_safety",
    493: "stronghold_player_safety",
    494: "stronghold_player_safety",
    503: "fist_of_guthix",
    507: "fist_of_guthix",
    533: "mage_training_arena",
    534: "mage_training_arena",
    535: "mage_training_arena",
    541: "mage_training_arena",
    562: "circus",
    578: "stealing_creation",
    587: "pest_control",
    588: "pest_control",
    591: "pyramid_plunder",
    597: "soul_wars",
    598: "soul_wars",
    601: "evil_tree",
    604: "barbarian_assault",
    610: "trouble_brewing",
    611: "trouble_brewing",
    668: "mobilising_armies",
    669: "mobilising_armies",
    670: "mobilising_armies",
    729: "mage_training_arena",
    730: "familiarisation",
    734: "fish_flingers",
    735: "fish_flingers",
    736: "fish_flingers",
    845: "castle_wars",
    846: "court_cases",
    893: "conquest",
    895: "conquest",
    971: "troll_invasion",
    1014: "dominion_tower",
    1015: "dominion_tower",
    1016: "dominion_tower",
    1017: "dominion_tower",
    1018: "dominion_tower",
    1021: "dominion_tower",
    1022: "dominion_tower",
    1023: "dominion_tower",
    1047: "flash_powder_factory",
    1082: "fight_caves",
    1086: "fight_caves",
    1088: "fight_caves",
}

# These source hints name a shipped enemy or its lair. A first recorded kill is
# the durable AnkiScape translation of encountering that enemy-owned track.
_ENEMY_TRACK_IDS = {
    19: "hellhound",
    568: "killerwatt",
    632: "cave_horror",
}


def _quest_trigger(hint: str) -> str:
    lowered = hint.lower()
    if not COMPLETION_HINT.match(lowered):
        return ""
    for quest in sorted(QUESTS, key=lambda q: -len(q.display_name)):
        if quest.display_name.lower() in lowered:
            return quest.id
    return ""


def _trigger(track_id: int, hint: str) -> tuple[str, str]:
    if track_id == TASK_TRACK_ID:
        return "task_count", ""
    if track_id in _ACTIVITY_TRACK_IDS:
        return "activity", _ACTIVITY_TRACK_IDS[track_id]
    if track_id in _ENEMY_TRACK_IDS:
        return "enemy", _ENEMY_TRACK_IDS[track_id]
    quest_id = _quest_trigger(hint)
    if quest_id:
        return "quest", quest_id
    return "latent", "world_map"


def build() -> str:
    songs = json.load(open(SONGS_JSON, encoding="utf-8"))
    rows: list[str] = []
    seen: set[int] = set()
    for song in sorted(songs, key=lambda row: int(row["id"])):
        track_id = int(song["id"])
        hint = str(song.get("hint", "")).strip()
        name = str(song.get("name", "")).strip()
        if not name or track_id in seen:
            continue
        seen.add(track_id)
        kind, key = _trigger(track_id, hint)
        rows.append(
            "    MusicTrack(%d, %r, %r, %r, %r, music_track_source(%d)),"
            % (track_id, name, hint, kind, key, track_id)
        )
    body = "\n".join(rows)
    return (
        '"""Generated by ``tools/harvest_music_log.py``. Do not hand-edit.\n\n'
        "Source: darkan-world-server %s data/music/songs.json — every named row\n"
        "from the period table, with its own name and unlock hint. Blank-name\n"
        "archive rows are omitted rather than assigned invented track names.\n\n"
        "Named tracks kept: %d.\n\"\"\"\n\n"
        "from __future__ import annotations\n\n"
        "from .music_log_data import MusicTrack, music_track_source\n\n\n"
        "MUSIC_TRACKS: tuple[MusicTrack, ...] = (\n%s\n)\n"
    ) % (DARKAN_COMMIT, len(rows), body)


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(build())
    print(f"wrote {OUT}")
