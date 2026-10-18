from __future__ import annotations

from .dependencies import *
from .ids import *
from .sources import *

QUEST_REWARD_NON_ITEM_NAMES = frozenset({
    "Karamja",
    "Mahjarrat Ritual Site Cavern",
})


QUEST_REWARD_ITEM_NAME_OVERRIDES = {
    "Amulet of ghostspeak": "Ghostspeak amulet",
    "Ring of charos": "Ring of Charos",
    "Sapphires": "Sapphire",
    # Eagles' Peak's pinned revision lists "A box trap." — parser mangling of a
    # real rev-742 item (10008, the placeable trap with the Lay action), not a
    # junk string. Normalise it onto the canonical item instead of prohibiting
    # the name and dropping a genuine reward.
    "A box trap.": "Box trap",
}

# The pinned quest pages often spell one canonical item with link labels,
# plurals, or historical display-name ordering. Keep those source words in the
# generated catalogue, then resolve them onto the storage keys used by actions.
QUEST_STAGE_ITEM_NAME_OVERRIDES = {
    "Amulet of Ghostspeak": "Ghostspeak amulet",
    "Bananas": "Banana",
    "Bat Bones": "Bat bones",
    "Black Candle": "Black candle",
    "Blood runes": "Blood rune",
    "Bronze helm": "Bronze med helm",
    "Body runes": "Body rune",
    "Bowstring": "Bow string",
    "Bronze hatchets": "Bronze hatchet",
    "Buckets": "Bucket",
    "Clean Guam": "Clean guam",
    "Ecto token": "Ecto-token",
    "Ectotokens": "Ecto-token",
    "Emeralds": "Emerald",
    "Empty Pot": "Empty pot",
    "Feathers": "Feather",
    "Fruit Blast": "Fruit blast",
    "Ghostspeak Amulet": "Ghostspeak amulet",
    "Granite rock": "Granite (5kg)",
    "Ground Bat bones": "Ground bat bones",
    "Jade (gem)": "Jade",
    "Jangerberry": "Jangerberries",
    "Lava runes": "Lava rune",
    "Log": "Logs",
    "Magic log": "Magic logs",
    "Maple log": "Maple logs",
    "Mind runes": "Mind rune",
    "Mist runes": "Mist rune",
    "Mithril bars": "Mithril bar",
    "Mithril grapple": "Mith grapple",
    "Mort Myre Fungus": "Mort myre fungus",
    "Oak log": "Oak logs",
    "Oak planks": "Oak plank",
    "Ogre arrows": "Ogre arrow",
    "Pestle and Mortar": "Pestle and mortar",
    "Planks": "Plank",
    "Pot of Flour": "Pot of flour",
    "Potatoes": "Potato",
    "Ring of charos": "Ring of Charos",
    "Rock Climbing boots": "Rock climbing boots",
    "Rogue's purse": "Clean rogue's purse",
    "Rune Pickaxe": "Rune pickaxe",
    "Secateur": "Secateurs",
    "Steam runes": "Steam rune",
    "Steel bars": "Steel bar",
    "Steel nail": "Steel nails",
    "Stripy feathers": "Stripy feather",
    "Tinderboxes": "Tinderbox",
    "Willow branches": "Willow branch",
    "Willow log": "Willow logs",
    "Wolf Bones": "Wolf bones",
}

__all__ = (
    'QUEST_REWARD_NON_ITEM_NAMES', 'QUEST_REWARD_ITEM_NAME_OVERRIDES', 'QUEST_STAGE_ITEM_NAME_OVERRIDES',
)
