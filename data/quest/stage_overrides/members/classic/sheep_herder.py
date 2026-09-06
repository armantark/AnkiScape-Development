from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

SHEEP_HERDER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Councillor Halgrive gave me poisoned sheep feed and asked me to dispose of four infected sheep.",
        "Doctor Orbon in the Ardougne chapel can sell protective clothing.",
    ),
    _simple_stage(
        2,
        "Doctor Orbon sold me a plague jacket and plague trousers.",
        "I need a cattleprod from the Ardougne sheep enclosure before handling the infected sheep.",
    ),
    _simple_stage(
        3,
        "I found the cattleprod. I need to herd and poison the red, green, blue, and yellow sheep.",
    ),
    _simple_stage(
        4,
        "The infected sheep bones need to be incinerated.",
    ),
    _simple_stage(
        5,
        "I incinerated the red, green, blue, and yellow sheep bones.",
        "Councillor Halgrive should hear that the infected sheep are gone.",
    ),
    _simple_stage(6, "Councillor Halgrive paid me for clearing the infected sheep.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    SHEEP_HERDER_ID: (
        _stage_req(
            1,
            "Accept poisoned sheep feed from Councillor Halgrive.",
            f"{DARKAN_SHEEP_HERDER_COUNCILLOR_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Accept poisoned sheep feed from Councillor Halgrive",),
            produced_inventory=(("Sheep feed", 1),),
        ),
        _stage_req(
            2,
            "Buy protective clothing from Doctor Orbon.",
            f"{DARKAN_SHEEP_HERDER_DOCTOR_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Coins", 100),),
            produced_inventory=(("Plague jacket", 1), ("Plague trousers", 1)),
        ),
        _stage_req(
            3,
            "Pick up the cattleprod from the Ardougne sheep enclosure.",
            (
                f"{DARKAN_SHEEP_HERDER_SOURCE}; {DARKAN_SHEEP_HERDER_FARMER_SOURCE}; "
                f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            auto_actions=(
                "Reach the Ardougne sheep enclosure",
                "Pick up the cattleprod from the sheep enclosure barn",
            ),
            produced_inventory=(("Cattleprod", 1),),
        ),
        _stage_req(
            4,
            "Herd and poison all four infected sheep.",
            (
                f"{DARKAN_SHEEP_HERDER_SOURCE}; {DARKAN_SHEEP_HERDER_FARMER_SOURCE}; "
                f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            required_inventory=(("Sheep feed", 1),),
            required_tools=(("Plague jacket", 1), ("Plague trousers", 1), ("Cattleprod", 1)),
            auto_actions=(
                "Reach the Ardougne sheep enclosure",
                "Herd and poison the red sheep",
                "Herd and poison the green sheep",
                "Herd and poison the blue sheep",
                "Herd and poison the yellow sheep",
            ),
            produced_inventory=(
                ("Red sheep bones", 1),
                ("Green sheep bones", 1),
                ("Blue sheep bones", 1),
                ("Yellow sheep bones", 1),
            ),
        ),
        _stage_req(
            5,
            "Incinerate the sheep bones and report all four infected sheep.",
            (
                f"{DARKAN_SHEEP_HERDER_SOURCE}; {DARKAN_SHEEP_HERDER_FARMER_SOURCE}; "
                f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {DARKAN_SHEEP_HERDER_CONSTANTS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
            consumed_inventory=(
                ("Red sheep bones", 1),
                ("Green sheep bones", 1),
                ("Blue sheep bones", 1),
                ("Yellow sheep bones", 1),
            ),
            auto_actions=(
                "Reach the Ardougne sheep enclosure",
                "Incinerate the red sheep bones",
                "Incinerate the green sheep bones",
                "Incinerate the blue sheep bones",
                "Incinerate the yellow sheep bones",
                "Report the incinerated sheep to Councillor Halgrive",
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Sheep feed": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_COUNCILLOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plague jacket": {
            "category": "equipment",
            "source": f"{DARKAN_SHEEP_HERDER_DOCTOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Plague trousers": {
            "category": "equipment",
            "source": f"{DARKAN_SHEEP_HERDER_DOCTOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Cattleprod": {
            "category": "tool",
            "source": f"{DARKAN_SHEEP_HERDER_FARMER_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Red sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Green sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blue sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Yellow sheep bones": {
            "category": "material",
            "source": f"{DARKAN_SHEEP_HERDER_UTILS_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'SHEEP_HERDER_STAGES',
)
