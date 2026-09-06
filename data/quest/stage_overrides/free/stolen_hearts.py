from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    "stolen_hearts": (
        _stage_req(
            1,
            "Join the Skulls and earn Khnum's trust.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            auto_actions=(
                "Threaten the Skullery bouncer and enter the gang cellar",
                "Pass Khnum's recruitment questions",
            ),
        ),
        _stage_req(
            2,
            "Tail Khnum to Draynor jail and uncover the kidnapping plot.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            auto_actions=(
                "Report the Skullery to Ozan and tail Khnum",
                "Interrogate Khnum with Ozan and Leela",
            ),
        ),
        _stage_req(
            3,
            "Confront Lady Keli and recover the ransom note.",
            (
                f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}; "
                f"{STOLEN_HEARTS_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
            ),
            produced_inventory=(("Ransom note", 1),),
            auto_actions=("Confront Lady Keli near the Wizards' Tower bridge",),
            combat_encounters=(
                _combat(
                    "stolen_hearts",
                    "mercenary_joe",
                    "Mercenary Joe",
                    2,
                    (
                        f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                        f"{DARKAN_BEASTS_SOURCE}"
                    ),
                    "Defeat Mercenary Joe and two Skulls mercenaries before collecting the ransom note.",
                    npc_stats=(
                        ("hitpoints", 500),
                        ("attack", 1),
                        ("strength", 1),
                        ("defence", 1),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=f"{DARKAN_BEASTS_SOURCE}:4959",
                ),
                _combat(
                    "stolen_hearts",
                    "skulls_mercenary",
                    "Skulls mercenary",
                    2,
                    (
                        f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                        f"{DARKAN_BEASTS_SOURCE}"
                    ),
                    "Defeat Mercenary Joe and two Skulls mercenaries before collecting the ransom note.",
                    quantity=2,
                    npc_stats=(
                        ("hitpoints", 400),
                        ("attack", 1),
                        ("strength", 1),
                        ("defence", 1),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=f"{DARKAN_BEASTS_SOURCE}:4960-4961",
                ),
            ),
        ),
        _stage_req(
            4,
            "Carry the ransom warning to Al Kharid and cross the rooftops with Ozan.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            required_inventory=(("Ransom note", 1),),
            produced_inventory=(("History of the Kharid-ib", 1),),
            auto_actions=(
                "Travel with Ozan to Al Kharid",
                "Cross the Al Kharid rooftops and enter the palace treasury",
                "Read the History of the Kharid-ib",
            ),
        ),
        _stage_req(
            5,
            "Solve Het's scales, take the Kharid-ib, and identify yourself to Osman.",
            f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_QUICK_GUIDE_SOURCE}",
            consumed_inventory=(
                ("Ransom note", 1),
                ("History of the Kharid-ib", 1),
            ),
            auto_actions=(
                "Find the heavy weight in two weighings",
                "Take the Kharid-ib and give Leela's passphrase to Osman",
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Ransom note": {
            "category": "material",
            "item_id": 25127,
            "tradeable": False,
            "source": (
                f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "History of the Kharid-ib": {
            "category": "material",
            "item_id": 25128,
            "tradeable": False,
            "source": (
                f"{STOLEN_HEARTS_WIKI_SOURCE}; {STOLEN_HEARTS_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__: tuple[str, ...] = ()
