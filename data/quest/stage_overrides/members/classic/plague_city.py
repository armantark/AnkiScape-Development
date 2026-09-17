from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

PLAGUE_CITY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Edmond asked me to help find Elena and sent me to Alrena for plague protection.",
        "Alrena needs dwellberries to finish the gas mask.",
    ),
    _simple_stage(
        2,
        "Alrena made me a gas mask.",
        "Edmond should explain how to dig into the sewers.",
    ),
    _simple_stage(
        3,
        "Edmond said to soften the soil with water.",
        "I need four buckets of water for the mud patch.",
    ),
    _simple_stage(4, "The soil is soft enough to dig.", "I should use a spade on the mud patch."),
    _simple_stage(
        5,
        "I dug into the Ardougne sewers.",
        "The sewer grill blocks the pipe to West Ardougne.",
    ),
    _simple_stage(
        6,
        "The grill is too secure to pull off alone.",
        "Edmond suggested tying rope to the grill.",
    ),
    _simple_stage(7, "I tied rope to the sewer grill.", "Edmond should help pull it off."),
    _simple_stage(
        8,
        "Edmond and I removed the grill.",
        "I should wear the gas mask, enter West Ardougne, and find Jethick.",
    ),
    _simple_stage(
        9,
        "Jethick needs a picture of Elena.",
        "Showing him a picture should point me to the Rehnison family.",
    ),
    _simple_stage(10, "Jethick gave me a book to return.", "Ted Rehnison is expecting the book."),
    _simple_stage(
        11,
        "I returned the book to Ted Rehnison.",
        "The Rehnisons should know what happened to Elena.",
    ),
    _simple_stage(
        12,
        "Martha Rehnison sent me to Milli.",
        "Milli saw Elena taken into a plague-marked house.",
    ),
    _simple_stage(
        13,
        "The mourners refused entry to the prison house.",
        "The Clerk may let me speak to Bravek for permission.",
    ),
    _simple_stage(
        14,
        "Bravek gave me a scruffy note for a hangover cure.",
        "I need to mix a hangover cure from milk, chocolate dust, and snape grass.",
    ),
    _simple_stage(
        15,
        "I made the hangover cure.",
        "Bravek should take the cure and give me a warrant.",
    ),
    _simple_stage(
        16,
        "Bravek gave me a warrant for the plague house.",
        "I need to sneak in, find the small key, unlock Elena's cell, and report to Edmond.",
    ),
    _simple_stage(17, "Edmond rewarded me for rescuing Elena.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    PLAGUE_CITY_ID: (
        _stage_req(
            1,
            "Give Alrena dwellberries so she can finish the gas mask.",
            (
                f"{DARKAN_PLAGUE_CITY_ALRENA_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_PICTURE_SPAWN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=("Pick up the picture of Elena in Alrena's house",),
            consumed_inventory=(("Dwellberries", 1),),
            produced_inventory=(("Gas mask", 1), ("Picture of Elena", 1)),
        ),
        _stage_req(
            2,
            "Talk to Edmond with the gas mask and learn the sewer plan.",
            f"{DARKAN_PLAGUE_CITY_EDMOND_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            required_inventory=(("Gas mask", 1),),
            auto_actions=("Talk to Edmond with the gas mask",),
        ),
        _stage_req(
            3,
            "Pour four buckets of water on the mud patch.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Bucket of water", 4),),
            produced_inventory=(("Bucket", 4),),
            auto_actions=("Soften Edmond's mud patch with four buckets of water",),
        ),
        _stage_req(
            4,
            "Dig through the softened mud patch into the sewers.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Spade", 1),),
            auto_actions=("Dig through Edmond's softened mud patch",),
        ),
        _stage_req(
            5,
            "Pull the sewer grill and learn that Edmond must help.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_EDMOND_SOURCE}",
            auto_actions=("Pull the sewer grill", "Ask Edmond for help with the grill"),
        ),
        _stage_req(
            6,
            "Tie rope to the sewer grill.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Rope", 1),),
            auto_actions=("Tie rope to the sewer grill",),
        ),
        _stage_req(
            7,
            "Ask Edmond to pull the rope and remove the grill.",
            f"{DARKAN_PLAGUE_CITY_EDMOND_SOURCE}; {DARKAN_PLAGUE_CITY_CUTSCENE_SOURCE}",
            auto_actions=("Ask Edmond to pull the sewer grill rope",),
        ),
        _stage_req(
            8,
            "Wear the gas mask, enter West Ardougne through the sewer, and speak to Jethick.",
            f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_JETHICK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            required_tools=(("Gas mask", 1),),
            auto_actions=(
                "Reach West Ardougne through the sewer pipe",
                "Speak to Jethick about Elena",
            ),
        ),
        _stage_req(
            9,
            "Show Jethick a picture of Elena and take the Rehnison book.",
            f"{DARKAN_PLAGUE_CITY_JETHICK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_inventory=(("Picture of Elena", 1),),
            produced_inventory=(("Turnip growing for beginners", 1),),
            auto_actions=("Show Jethick the picture of Elena", "Agree to return Jethick's book"),
        ),
        _stage_req(
            10,
            "Return Jethick's book to Ted Rehnison.",
            f"{DARKAN_PLAGUE_CITY_REHNISON_DOOR_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            consumed_inventory=(("Turnip growing for beginners", 1),),
            auto_actions=("Return Jethick's book to Ted Rehnison",),
        ),
        _stage_req(
            11,
            "Ask Martha Rehnison where Elena went.",
            f"{DARKAN_PLAGUE_CITY_MARTHA_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}",
            auto_actions=("Ask Martha Rehnison about Elena",),
        ),
        _stage_req(
            12,
            "Ask Milli about Elena and challenge the mourners at the prison house.",
            (
                f"{DARKAN_PLAGUE_CITY_MILLI_SOURCE}; {DARKAN_PLAGUE_CITY_PRISON_DOOR_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}"
            ),
            auto_actions=(
                "Ask Milli Rehnison where Elena was taken",
                "Ask the mourners for prison house clearance",
            ),
        ),
        _stage_req(
            13,
            "Convince the Clerk to let you speak to Bravek and take Bravek's scruffy note.",
            (
                f"{DARKAN_PLAGUE_CITY_CLERK_SOURCE}; {DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            produced_inventory=(("Scruffy note", 1),),
            auto_actions=("Convince the Clerk to let you speak to Bravek", "Ask Bravek for his cure recipe"),
        ),
        _stage_req(
            14,
            "Mix Bravek's hangover cure.",
            f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_ALRENA_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Chocolate dust", 1), ("Bucket of milk", 1), ("Snape grass", 1)),
            produced_inventory=(("Hangover cure", 1),),
            required_tools=(("Pestle and mortar", 1),),
            auto_actions=("Mix chocolate dust with milk and snape grass",),
        ),
        _stage_req(
            15,
            "Give Bravek the hangover cure and obtain a warrant.",
            f"{DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Hangover cure", 1),),
            produced_inventory=(("Warrant", 1),),
            auto_actions=("Give Bravek the hangover cure", "Ask Bravek for a prison house warrant"),
        ),
        _stage_req(
            16,
            "Use the warrant, find the small key, free Elena, and report back to Edmond.",
            (
                f"{DARKAN_PLAGUE_CITY_PRISON_DOOR_SOURCE}; {DARKAN_PLAGUE_CITY_UTILS_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_ELENA_DOOR_SOURCE}; {DARKAN_PLAGUE_CITY_ELENA_SOURCE}; "
                f"{DARKAN_PLAGUE_CITY_EDMOND_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_inventory=(("Warrant", 1),),
            produced_inventory=(("A small key", 1),),
            auto_actions=(
                "Enter the prison house with Bravek's warrant",
                "Search the barrel for the small key",
                "Unlock Elena's cell",
                "Free Elena and report to Edmond",
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Dwellberries": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Picture of Elena": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Turnip growing for beginners": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_JETHICK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Scruffy note": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Hangover cure": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {HANGOVER_CURE_WIKI_SOURCE}",
            "source_item_id": 1504,
            "stackable": False,
            "tradeable": False,
        },
        "Warrant": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_BRAVEK_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "A small key": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Chocolate dust": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Snape grass": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_SOURCE}; {DARKAN_PLAGUE_CITY_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Bucket": {
            "category": "material",
            "source": f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pestle and mortar": {
            "category": "tool",
            "source": f"{DARKAN_PLAGUE_CITY_ALRENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Spade": {
            "category": "tool",
            "source": f"{DARKAN_PLAGUE_CITY_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'PLAGUE_CITY_STAGES',
)
