from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

WATERFALL_QUEST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Almera is worried about Hudon.", "I should find Hudon by the waterfall."),
    _simple_stage(
        2,
        "Hudon mentioned treasure inside the waterfall.",
        "A book nearby may explain Baxtorian's treasure.",
    ),
    _simple_stage(
        3,
        "The book points to Golrie under Tree Gnome Village.",
        "I need the old key to free Golrie.",
    ),
    _simple_stage(
        4,
        "Golrie gave me Glarial's pebble.",
        "The pebble should open Glarial's tomb so I can recover her amulet and urn.",
    ),
    _simple_stage(
        5,
        "I recovered Glarial's amulet and urn.",
        "The waterfall tomb needs six water, air, and earth runes plus Glarial's amulet and urn.",
    ),
    _simple_stage(6, "I took Baxtorian's treasure safely.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    WATERFALL_QUEST_ID: (
        _stage_req(
            1,
            "Find Hudon after speaking to Almera.",
            f"{DARKAN_WATERFALL_ALMERA_SOURCE}; {DARKAN_WATERFALL_HUDON_SOURCE}",
            auto_actions=("Speak to Hudon by the waterfall",),
        ),
        _stage_req(
            2,
            "Search for and read the Book on Baxtorian.",
            f"{DARKAN_WATERFALL_SOURCE}; {DARKAN_WATERFALL_BOOK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Book on Baxtorian", 1),),
            auto_actions=("Search the Baxtorian bookcase", "Read the Book on Baxtorian"),
        ),
        _stage_req(
            3,
            "Free Golrie and receive Glarial's pebble.",
            f"{DARKAN_WATERFALL_SOURCE}; {DARKAN_WATERFALL_GOLRIE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Old key", 1), ("Glarial's pebble", 1)),
            auto_actions=(
                "Search the Tree Gnome Village crate for the old key",
                "Unlock Golrie's prison",
                "Reach Golrie under Tree Gnome Village",
            ),
        ),
        _stage_req(
            4,
            "Use Glarial's pebble to enter the tomb and recover Glarial's amulet and urn.",
            f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory=(("Glarial's pebble", 1),),
            produced_inventory=(("Large old key", 1), ("Glarial's amulet", 1), ("Glarial's urn", 1)),
            required_tools=(("Rope", 1),),
            auto_actions=(
                "Search the waterfall crate for the large old key",
                "Use Glarial's pebble on Glarial's tomb",
                "Search Glarial's tomb for the amulet and urn",
            ),
        ),
        _stage_req(
            5,
            "Place the runes and Glarial's amulet, then use Glarial's urn on the chalice.",
            f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(
                ("Glarial's urn", 1),
                ("Water rune", 6),
                ("Air rune", 6),
                ("Earth rune", 6),
                ("Glarial's amulet", 1),
            ),
            required_tools=(("Rope", 1),),
            auto_actions=(
                "Place six water runes on the pillars",
                "Place six air runes on the pillars",
                "Place six earth runes on the pillars",
                "Place Glarial's amulet on Glarial's statue",
                "Use Glarial's urn on the chalice",
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Book on Baxtorian": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_BOOK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Old key": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Large old key": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Glarial's pebble": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_GOLRIE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Glarial's amulet": {
            "category": "equipment",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Glarial's urn": {
            "category": "material",
            "source": f"{DARKAN_WATERFALL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'WATERFALL_QUEST_STAGES',
)
