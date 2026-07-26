"""Period-pinned Enchanted key treasure-hunt data.

The eleven sites, their loot and the temperature ladder are all attested. The
site table below is Darkan's reconstruction of the buried-treasure coordinates,
whose site identities and per-site loot the period wiki corroborates row for
row; only the exact tiles are Darkan's rather than a pinned period coordinate,
and they are used solely to space the sites apart for the key's distance
readings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


ENCHANTED_KEY_ACTIVITY_ID = "enchanted_key"
ENCHANTED_KEY_QUEST_ID = "making_history"
ENCHANTED_KEY_ITEM = "Enchanted key"
ENCHANTED_KEY_SPADE = "Spade"
# "another key can be obtained from Erin for 500 coins, if the second quest has
# not been started."
ENCHANTED_KEY_REPLACEMENT_COST = 500
ENCHANTED_KEY_REPLACEMENT_BLOCKING_QUEST_ID = "meeting_history"

ENCHANTED_KEY_SOURCE = (
    "https://runescape.wiki/w/Enchanted_key?oldid=6554980 "
    "(2012-11-14T08:47:10Z); "
    "https://runescape.wiki/w/Making_History?oldid=6493057 "
    "(2012-10-29T15:58:17Z); "
    "darkan-world-server "
    "src/main/java/com/rs/game/content/quests/making_history/MakingHistory.kt"
)

GUTHIX_MJOLNIR = "Guthix mjolnir"
SARADOMIN_MJOLNIR = "Saradomin mjolnir"
ZAMORAK_MJOLNIR = "Zamorak mjolnir"
ENCHANTED_KEY_MJOLNIRS = (GUTHIX_MJOLNIR, SARADOMIN_MJOLNIR, ZAMORAK_MJOLNIR)


@dataclass(frozen=True)
class TreasureSite:
    id: str
    display_name: str
    detail: str
    x: int
    y: int
    rewards: tuple[tuple[str, int], ...]


# "The first treasure site will always be Fremennik Province. After that, all
# other locations are at a random order for each player. There are a total of 11
# treasure sites to be found."
ENCHANTED_KEY_SITES: tuple[TreasureSite, ...] = (
    TreasureSite(
        "fremennik_province",
        "Fremennik Province",
        "north-east of Rellekka",
        2716,
        3607,
        (("Steel arrows", 20), ("Mithril ore", 10), ("Law rune", 15)),
    ),
    TreasureSite(
        "ardougne_monastery",
        "Ardougne Monastery",
        "in the monastery grounds",
        2621,
        3239,
        (("Pure essence", 36), ("Iron ore", 15), ("Fire rune", 20)),
    ),
    TreasureSite(
        "west_ardougne",
        "West Ardougne",
        "near the outpost",
        2417,
        3382,
        (("Pure essence", 40), ("Iron arrowtips", 20), ("Fire rune", 20)),
    ),
    TreasureSite(
        "gnome_stronghold",
        "Gnome Stronghold",
        "inside the stronghold walls",
        2448,
        3443,
        (("Pure essence", 39), ("Iron arrowtips", 20), ("Water rune", 30)),
    ),
    TreasureSite(
        "body_altar",
        "Body altar",
        "outside the Body altar ruin",
        3033,
        3437,
        (("Mithril ore", 10), ("Iron ore", 15), ("Earth rune", 45)),
    ),
    TreasureSite(
        "waynes_chains",
        "Wayne's Chains",
        "behind the Falador chainmail shop",
        2972,
        3304,
        (("Earth rune", 15), ("Iron arrows", 20), (SARADOMIN_MJOLNIR, 1)),
    ),
    TreasureSite(
        "mudskipper_point",
        "Mudskipper Point",
        "on the southern shore",
        3007,
        3161,
        (("Iron ore", 15), ("Mithril arrows", 20), ("Death rune", 15)),
    ),
    TreasureSite(
        "lumbridge_swamp",
        "Lumbridge Swamp Caves",
        "by the swamp cave entrance",
        3161,
        3176,
        (("Pure essence", 29), ("Mind rune", 20), ("Steel arrows", 20)),
    ),
    TreasureSite(
        "al_kharid",
        "Al-Kharid",
        "north of the palace",
        3292,
        3219,
        (("Pure essence", 40), ("Mithril ore", 10), (ZAMORAK_MJOLNIR, 1)),
    ),
    TreasureSite(
        "exam_centre",
        "Exam Centre",
        "outside the Exam Centre",
        3300,
        3350,
        (("Pure essence", 40), ("Iron ore", 15), (GUTHIX_MJOLNIR, 1)),
    ),
    TreasureSite(
        "grand_exchange",
        "Grand Exchange",
        "north of the Varrock centre",
        3160,
        3490,
        (("Pure essence", 39), ("Mithril arrows", 10), ("Law rune", 15)),
    ),
)

ENCHANTED_KEY_SITE_IDS = tuple(site.id for site in ENCHANTED_KEY_SITES)

# "Its temperature is based on the distance of the treasure from the player,
# measured in the number of steps (including diagonal steps) ... this is the
# Chebyshev distance". The messages and thresholds are the article's own table,
# read from the shortest band outwards.
#
# The whole period ladder ships, but the flattened hunt cannot produce every
# band: a search either lands on the treasure ("steaming") or on another site,
# and the closest two sites are 61 steps apart while the furthest are 883. So
# "burning hot", "very hot" and "freezing" never fire, which
# `test_enchanted_key.py` pins rather than leaves for someone to discover. They
# stay in the table because trimming them would misrepresent the source.
ENCHANTED_KEY_TEMPERATURES: tuple[tuple[int, str], ...] = (
    (4, "The key is steaming."),
    (30, "Ouch! It's burning hot."),
    (60, "It's very hot."),
    (100, "It's hot."),
    (400, "It's warm."),
    (700, "It's cold."),
    (1_000, "It's very cold."),
)
ENCHANTED_KEY_COLDEST = "It's freezing."
# "When a player receives the message 'The key is steaming', he or she should
# use a spade to dig up the treasure."
ENCHANTED_KEY_DIG_DISTANCE = ENCHANTED_KEY_TEMPERATURES[0][0]

ENCHANTED_KEY_WARMER = "Warmer than last time."
ENCHANTED_KEY_COLDER = "Colder than last time."
ENCHANTED_KEY_SAME = "Same temperature as last time."


def enchanted_key_temperature_pure(distance: int) -> str:
    for threshold, message in ENCHANTED_KEY_TEMPERATURES:
        if distance <= threshold:
            return message
    return ENCHANTED_KEY_COLDEST


def enchanted_key_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        ENCHANTED_KEY_ACTIVITY_ID: {
            "display_name": "Enchanted Key",
            "requirements": {},
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "outputs": ENCHANTED_KEY_MJOLNIRS,
            "source": ENCHANTED_KEY_SOURCE,
        }
    }


def enchanted_key_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    """The three god mjolnirs, which the hunt is the only way to dig up.

    "This is the only way to obtain these unique weapons, other than trading
    with another player and buying in the Grand Exchange." Nothing else in the
    add-on registers them, so without this seam the three sites that bury them
    would hand out items the save could not hold.
    """
    return {
        name: {
            "category": "material",
            "stackable": False,
            "tradeable": True,
            "source": ENCHANTED_KEY_SOURCE,
        }
        for name in ENCHANTED_KEY_MJOLNIRS
    }
