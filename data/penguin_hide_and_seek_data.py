"""Period-pinned compact data for Penguin Hide and Seek."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID = "penguin_hide_and_seek"
PENGUIN_WEEK_REVIEWS = 1_680
PENGUIN_POINT_CAP = 50
PENGUIN_COINS_PER_POINT = 6_500
PENGUIN_XP_PER_LEVEL_POINT = 25

PENGUIN_HIDE_AND_SEEK_SOURCE = (
    "RuneScape Wiki Penguin Hide and Seek oldid=6569778 "
    "(2012-11-17T23:47:37Z); Spawn locations oldid=6566231 "
    "(2012-11-17T15:09:05Z); 1-point spawn locations oldid=6208449"
)


@dataclass(frozen=True)
class PenguinSpawn:
    id: str
    location: str
    disguise: str
    point_tier: int
    detail: str


# Breadth-one uses a compact period-qualified rotation: six locations for each
# ordinary tier, from which five spawn each answered-card week. The remaining
# cutoff pool is data-depth work; the weekly roster mechanic is not flattened.
PENGUIN_ONE_POINT_SPAWNS = (
    PenguinSpawn("al_kharid_cactus", "Al Kharid", "Cactus", 1, "south-west of Ranael's shop"),
    PenguinSpawn("castle_wars_bush", "Castle Wars", "Bush", 1, "on the island east of the arena"),
    PenguinSpawn("draynor_manor_crate", "Draynor Manor", "Crate", 1, "inside the manor yard"),
    PenguinSpawn("gnome_maze_bush", "Gnome Maze", "Bush", 1, "in the south-western maze"),
    PenguinSpawn("ice_mountain_rock", "Ice Mountain", "Rock", 1, "south-west of the Oracle's tent"),
    PenguinSpawn("lumbridge_swamp_toadstool", "Lumbridge Swamp", "Toadstool", 1, "north of the Water altar"),
)

PENGUIN_TWO_POINT_SPAWNS = (
    PenguinSpawn("castle_wars_rock", "Castle Wars", "Rock", 2, "between the lakes south-west of the arena"),
    PenguinSpawn("haunted_woods_crate", "Haunted Woods", "Crate", 2, "by the first lake west of Port Phasmatys"),
    PenguinSpawn("nardah_cactus", "Nardah", "Cactus", 2, "north of Nardah"),
    PenguinSpawn("piscatoris_crate", "Piscatoris", "Crate", 2, "among the dead trees south of the colony"),
    PenguinSpawn("port_phasmatys_barrel", "Port Phasmatys", "Barrel", 2, "south-west of the southern market stall"),
    PenguinSpawn("outer_sophanem_cactus", "Outer Sophanem", "Cactus", 2, "beside the river west of the north entrance"),
)

PENGUIN_POLAR_BEAR_LOCATIONS = (
    "Ardougne well",
    "Falador well",
    "Musa Point well",
    "Rellekka well",
    "Rimmington well",
    "Varrock well",
)


def penguin_hide_and_seek_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID: {
            "display_name": "Penguin Hide and Seek",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": PENGUIN_HIDE_AND_SEEK_SOURCE,
        }
    }
