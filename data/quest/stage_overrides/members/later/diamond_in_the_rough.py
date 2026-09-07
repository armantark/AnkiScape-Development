from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    "diamond_in_the_rough": (
        _stage_req(
            1,
            "Take the Kharid-ib's heavy container and leave Al Kharid with Ozan.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}"
            ),
            produced_inventory=(("Heavy weight", 1),),
            auto_actions=(
                "Receive Osman's rescue mission and collect the Heavy weight",
                "Leave the palace by Ozan's rooftop route and reach Shantay Pass",
            ),
        ),
        _stage_req(
            2,
            "Follow Het's sundial and survive the Apmeken bandit ambush.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
            ),
            required_inventory=(("Heavy weight", 1),),
            produced_inventory=(
                ("Sundial gnomon", 1),
                ("Waterskin (4)", 4),
            ),
            auto_actions=(
                "Accept Shantay's four waterskins and align Het's sundial",
                "Recover the Sundial gnomon from the final bandit",
            ),
            combat_encounters=(
                _combat(
                    "diamond_in_the_rough",
                    "bandit",
                    "Bandit (Diamond in the Rough)",
                    2,
                    (
                        "https://runescape.wiki/w/Bandit_(Diamond_in_the_Rough)?oldid=6343462; "
                        f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Five level-2 bandits and their king make up the six-enemy sundial ambush.",
                    quantity=5,
                    npc_stats=(
                        ("hitpoints", 200),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 5),
                        ("ranged", 5),
                    ),
                    npc_stats_source=(
                        "https://runescape.wiki/w/Bandit_(Diamond_in_the_Rough)?oldid=6343462; "
                        f"{DARKAN_BEASTS_SOURCE}:4953-4957; "
                        "Strength 1 is the AnkiScape minimum resolver adapter"
                    ),
                ),
                _combat(
                    "diamond_in_the_rough",
                    "bandit_king",
                    "Bandit king",
                    3,
                    (
                        "https://runescape.wiki/w/Bandit_king?oldid=6538856; "
                        f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Defeat the Bandit king before repairing Apmeken's sundial.",
                    npc_stats=(
                        ("hitpoints", 300),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 5),
                        ("ranged", 5),
                    ),
                    npc_stats_source=(
                        "https://runescape.wiki/w/Bandit_king?oldid=6538856; "
                        f"{DARKAN_BEASTS_SOURCE}:4952; "
                        "Strength 1 is the AnkiScape minimum resolver adapter"
                    ),
                ),
            ),
        ),
        _stage_req(
            3,
            "Escape the quicksand and recover the Kharid-ib from the Kalphite nursery.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}"
            ),
            consumed_inventory=(
                ("Heavy weight", 1),
                ("Sundial gnomon", 1),
            ),
            produced_inventory=(
                ("Sapphire", 1),
                ("Emerald", 1),
                ("Ruby", 1),
            ),
            auto_actions=(
                "Repair Apmeken's sundial and lose the Kharid-ib in the quicksand",
                "Find Crondis's gnomon beneath Ozan and follow the crocodile sunbeam",
                "Slice sparkling Dung kalphites until the sapphire, emerald, ruby, and Kharid-ib are recovered",
                "Align the nursery sundial with the scarab",
            ),
        ),
        _stage_req(
            4,
            "Defeat Apep and Heru, then rescue Prince Ali.",
            (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_QUICK_GUIDE_SOURCE}; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
            ),
            auto_actions=(
                "Move clear of Apep's Whirling Dervish and turn away from Heru's blinding shield",
                "Rescue Prince Ali and return to Osman",
            ),
            combat_encounters=(
                _combat(
                    "diamond_in_the_rough",
                    "apep",
                    "Apep",
                    5,
                    (
                        "https://runescape.wiki/w/Apep?oldid=6488383; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Apep attacks first and uses Whirling Dervish before Heru joins the fight.",
                    npc_stats=(
                        ("hitpoints", 500),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=(
                        f"{DARKAN_BEASTS_SOURCE}:4958; "
                        "Strength 1 is the AnkiScape minimum resolver adapter"
                    ),
                ),
                _combat(
                    "diamond_in_the_rough",
                    "heru",
                    "Heru",
                    5,
                    (
                        "https://runescape.wiki/w/Heru?oldid=6471439; "
                        f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; {DARKAN_BEASTS_SOURCE}"
                    ),
                    "Heru attacks after Apep and can interrupt the player with his blinding shield.",
                    npc_stats=(
                        ("hitpoints", 500),
                        ("attack", 5),
                        ("strength", 1),
                        ("defence", 5),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_stats_source=(
                        "https://runescape.wiki/w/Heru?oldid=6471439; "
                        f"{DARKAN_BEASTS_SOURCE}:4949; "
                        "HP and resolver stats use the explicit equal-level Apep adapter"
                    ),
                ),
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Heavy weight": {
            "category": "material",
            "item_id": 25116,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Heavy_weight?oldid=6320315; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Sundial gnomon": {
            "category": "material",
            "item_id": 25118,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Sundial_gnomon?oldid=6360192; "
                f"{DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Apmeken mask": {
            "category": "equipment",
            "equipment_slot": "head",
            "item_id": 25122,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Ankh": {
            "category": "equipment",
            "equipment_slot": "shield",
            "item_id": 25123,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Scabaras mask": {
            "category": "equipment",
            "equipment_slot": "head",
            "item_id": 25124,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Was": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 25125,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{DIAMOND_IN_THE_ROUGH_WIKI_SOURCE}; {DIAMOND_IN_THE_ROUGH_CACHE_SOURCE}; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__: tuple[str, ...] = ()
