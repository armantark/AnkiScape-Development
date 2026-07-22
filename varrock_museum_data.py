"""Period-pinned horizontal data for Varrock Museum Kudos."""

from __future__ import annotations

from typing import Any


VARROCK_MUSEUM_ACTIVITY_ID = "varrock_museum"
VARROCK_MUSEUM_SOURCE_MAX_KUDOS = 183
VARROCK_MUSEUM_IMPLEMENTED_MAX_KUDOS = 163
VARROCK_MUSEUM_SOURCE = (
    "RuneScape Wiki Varrock Museum oldid=6550044 "
    "(2012-11-12T19:18:01Z); Kudos oldid=6514304 "
    "(2012-11-01T00:26:08Z); Natural history quiz oldid=6459188 "
    "(2012-10-23T14:10:49Z); OpenRS2 rev-742 item definitions"
)


QUIZ_DISPLAYS = (
    "Lizard",
    "Battle tortoise",
    "Dragon",
    "Wyvern",
    "Snail",
    "Snake",
    "Sea slug",
    "Monkey",
    "Kalphite Queen",
    "Terrorbird",
    "Penguin",
    "Mole",
    "Camel",
    "Leech",
)


SPECIMEN_DISPLAYS = (
    {"id": "pottery", "item": "Pottery", "case": 22},
    {"id": "old_symbol", "item": "Old symbol", "case": 36},
    {"id": "ancient_symbol", "item": "Ancient symbol", "case": 37},
    {"id": "ancient_coin", "item": "Ancient coin", "case": 44},
    {"id": "old_coin", "item": "Old coin", "case": 45},
)


# Ghostly Robes supplies the remaining ten quest-story Kudos, but AnkiScape has
# no miniquest state for it yet. Keeping it outside this executable ledger makes
# the 85-point live subtotal explicit instead of inventing a completion flag.
QUEST_KUDOS = (
    {"id": "demon_slayer", "name": "Demon Slayer", "kudos": 5},
    {"id": "rune_mysteries", "name": "Rune Mysteries", "kudos": 5},
    {"id": "shield_of_arrav", "name": "Shield of Arrav", "kudos": 5},
    {"id": "making_history", "name": "Making History", "kudos": 5},
    {"id": "meeting_history", "name": "Meeting History", "kudos": 5},
    {"id": "merlins_crystal", "name": "Merlin's Crystal", "kudos": 5},
    {"id": "observatory_quest", "name": "Observatory Quest", "kudos": 5},
    {"id": "priest_in_peril", "name": "Priest in Peril", "kudos": 5},
    {"id": "a_tail_of_two_cats", "name": "A Tail of Two Cats", "kudos": 5},
    {"id": "temple_of_ikov", "name": "Temple of Ikov", "kudos": 5},
    {
        "id": "what_lies_below",
        "name": "What Lies Below",
        "kudos": 5,
        "required_item": "Dagon'hai history",
    },
    {"id": "in_aid_of_the_myreque", "name": "In Aid of the Myreque", "kudos": 5},
    {"id": "hazeel_cult", "name": "Hazeel Cult", "kudos": 5},
    {"id": "defender_of_varrock", "name": "Defender of Varrock", "kudos": 5},
    {
        "id": "glorious_memories",
        "name": "Glorious Memories",
        "kudos": 10,
        "required_item": "Prophecy tablet",
    },
    {"id": "the_grand_tree", "name": "The Grand Tree", "kudos": 5},
)


KUDOS_THRESHOLD_REWARDS = (
    {"id": "kudos_51", "kudos": 51, "xp": {"mining": 1000.0}},
    {
        "id": "kudos_101",
        "kudos": 101,
        "xp": {"crafting": 2500.0, "mining": 2500.0},
    },
    {
        "id": "kudos_151",
        "kudos": 151,
        "xp": {
            "crafting": 4000.0,
            "hunter": 4000.0,
            "prayer": 4000.0,
            "slayer": 4000.0,
            "smithing": 4000.0,
        },
    },
)


MUSEUM_TOOL_RACK_ITEMS = (
    ("Trowel", 676),
    ("Rock pick", 675),
    ("Specimen brush", 670),
    ("Leather gloves", 1059),
    ("Leather boots", 1061),
)


MUSEUM_SPECIMEN_ITEMS = (
    ("Uncleaned find", 11175),
    ("Pottery", 11178),
    ("Old coin", 11179),
    ("Ancient coin", 11180),
    ("Ancient symbol", 11181),
    ("Old symbol", 11182),
    ("Clean necklace", 11195),
)


def varrock_museum_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        VARROCK_MUSEUM_ACTIVITY_ID: {
            "display_name": "Varrock Museum",
            "requirements": {},
            "batch_size": 1,
            "group": "landmarks",
            "source": VARROCK_MUSEUM_SOURCE,
        }
    }


def varrock_museum_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    rows = {
        name: {
            "category": "material",
            "source_item_id": item_id,
            "stackable": False,
            "tradeable": False,
            "source": VARROCK_MUSEUM_SOURCE,
        }
        for name, item_id in (*MUSEUM_TOOL_RACK_ITEMS[:3], *MUSEUM_SPECIMEN_ITEMS)
    }
    return rows
