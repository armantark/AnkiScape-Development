"""Source-backed passive Prayer items available before the EOC cutoff."""

from __future__ import annotations


BONECRUSHER_PASSIVE_ID = "bonecrusher"
BONECRUSHER_ITEM_NAME = "Bonecrusher"
BONECRUSHER_ITEM_ID = 18337
BONECRUSHER_SOURCE = "RuneScape Wiki Bonecrusher oldid=6589107 (2012-11-19)"

ECTOPLASMATOR_PASSIVE_ID = "ectoplasmator"
ECTOPLASMATOR_ITEM_NAME = "Ectoplasmator"
ECTOPLASMATOR_ITEM_ID = 25354
ECTOPLASMATOR_SOURCE = "RuneScape Wiki Ectoplasmator oldid=6566210 (2012-11-17)"

# Only stable combat targets whose current identity is covered by the pinned
# Ectoplasmator XP table are included.  The generic Shade target is not one of
# the five named shade remains, and Death wings/non-mage spiritual variants do
# not have exact values in the table.
ECTOPLASMATOR_XP_BY_ENEMY_ID = {
    "ghost": 4.5,
    "ghost_level_77": 4.5,
    "banshee": 4.5,
}


def prayer_passive_items_as_dict() -> dict[str, dict]:
    return {
        BONECRUSHER_ITEM_NAME: {
            "category": "tool",
            "tradeable": False,
            "stackable": False,
            "source": BONECRUSHER_SOURCE,
            "source_item_id": BONECRUSHER_ITEM_ID,
        },
        ECTOPLASMATOR_ITEM_NAME: {
            "category": "tool",
            "tradeable": False,
            "stackable": False,
            "source": ECTOPLASMATOR_SOURCE,
            "source_item_id": ECTOPLASMATOR_ITEM_ID,
        },
    }
