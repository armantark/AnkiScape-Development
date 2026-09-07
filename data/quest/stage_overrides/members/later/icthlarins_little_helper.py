from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

ICTHLARINS_LITTLE_HELPER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "The Wanderer hypnotised me and left a canopic jar in my pack.",
        "I should follow the first memory through Sophanem's southern pyramid.",
    ),
    _simple_stage(
        2,
        "The Sphinx recognised the danger in the canopic jar.",
        "Her token will make Sophanem's High Priest hear me out.",
    ),
    _simple_stage(
        3,
        "The Sphinx's token should convince the High Priest to hear my warning.",
        "I must obtain his permission and place the jar in its matching burial chamber.",
    ),
    _simple_stage(
        4,
        "The canopic guardian has risen from the jar's burial chamber.",
        "I must defeat it before the canopic jar can be recovered.",
    ),
    _simple_stage(
        5,
        "The guardian is defeated and the restored canopic jar is back in my pack.",
        "I must return it and bring willow, linen, sap, and salt for the cleansing ceremony.",
    ),
    _simple_stage(
        6,
        "The Carpenter finished the ceremony's holy symbol.",
        "The next memory will reveal how Amascut corrupted it.",
    ),
    _simple_stage(
        7,
        "Amascut transformed the holy symbol into an unholy symbol.",
        "I must hide it in the eastern sarcophagus to expose the possessed priest.",
    ),
    _simple_stage(
        8,
        "Amascut's unholy symbol is hidden in the eastern sarcophagus.",
        "I must defeat the possessed priest before Icthlarin can break the hypnosis.",
    ),
    _simple_stage(
        9,
        "The High Priest rewarded me with a Catspeak amulet and opened Sophanem.",
        "Quest complete!",
    ),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    "icthlarins_little_helper": (
        _stage_req(
            1,
            "Trust the Wanderer, enter Sophanem under hypnosis, and recover the canopic jar.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}"
            ),
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            consumed_inventory=(("Tinderbox", 1), ("Waterskin (4)", 1)),
            produced_inventory=(("Canopic jar", 1),),
            auto_actions=(
                "Pick up the following cat before speaking to the Wanderer",
                "Enter Sophanem through the secret rock and survive the first pyramid memory",
                "Solve the nine-tile sarcophagus puzzle",
            ),
        ),
        _stage_req(
            2,
            "Answer the Sphinx's family riddle and take her token to the High Priest.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Sphinx%27s_token?oldid=6520569"
            ),
            required_inventory=(("Canopic jar", 1),),
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            produced_inventory=(("Sphinx's token", 1),),
            auto_actions=(
                "Answer nine to the Sphinx's riddle",
                "Ask the High Priest how to return the stolen remains",
            ),
        ),
        _stage_req(
            3,
            "Present the Sphinx's token and place the canopic jar in its burial chamber.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}"
            ),
            consumed_inventory=(("Canopic jar", 1), ("Sphinx's token", 1)),
            auto_actions=(
                "Present the Sphinx's token to the High Priest",
                "Match the canopic jar to its burial chamber",
            ),
        ),
        _stage_req(
            4,
            "Defeat the apparition bound to the canopic jar.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}"
            ),
            produced_inventory=(("Canopic jar", 1),),
            auto_actions=("Restore the assigned jar after the guardian falls",),
            combat_encounters=(
                _combat(
                    "icthlarins_little_helper",
                    "canopic_guardian",
                    "Canopic guardian",
                    81,
                    (
                        f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                        "https://runescape.wiki/w/Apmeken_apparition?oldid=5795222; "
                        "https://runescape.wiki/w/Het_apparition?oldid=6178412; "
                        "https://runescape.wiki/w/Crondis_apparition?oldid=6342246; "
                        "https://runescape.wiki/w/Scabaras_apparition?oldid=6378180; "
                        f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
                    ),
                    (
                        "The assigned jar produces exactly one of four guardians. "
                        "The period range is level 75-81, 600-750 LP, and melee and/or magic."
                    ),
                    npc_stats=(
                        ("hitpoints", 750),
                        ("attack", 81),
                        ("strength", 81),
                        ("defence", 81),
                        ("magic", 81),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 90),
                        ("attack_style", "magic"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=(
                        "Period upper-bound resolver adapter across the four possible guardians; "
                        "not claimed as historical hidden combat stats"
                    ),
                ),
            ),
        ),
        _stage_req(
            5,
            "Return the restored jar and prepare the Carpenter's holy symbol and Embalmer's supplies.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Bucket_of_sap?oldid=6288759; "
                "https://runescape.wiki/w/Linen?oldid=5787786"
            ),
            required_tools=(("Knife", 1),),
            consumed_inventory=(
                ("Canopic jar", 1),
                ("Coins", 30),
                ("Willow logs", 1),
                ("Bucket", 1),
            ),
            consumed_inventory_options=((("Pile of salt", 1), ("Bag of salt", 1)),),
            produced_inventory=(("Holy symbol (Icthlarin's Little Helper)", 1),),
            auto_actions=(
                "Return the restored jar to the High Priest",
                "Buy one sheet of linen from Raetul for 30 coins",
                "Collect a bucket of sap from an evergreen tree with the knife",
                "Give the willow log to the Carpenter and the linen, sap, and salt to the Embalmer",
                "Collect the finished holy symbol without a wall-clock wait",
            ),
        ),
        _stage_req(
            6,
            "Relive Amascut's betrayal and recover the transformed unholy symbol.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Holy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6352893; "
                "https://runescape.wiki/w/Unholy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6315484"
            ),
            consumed_inventory=(("Holy symbol (Icthlarin's Little Helper)", 1),),
            produced_inventory=(("Unholy symbol (Icthlarin's Little Helper)", 1),),
            auto_actions=("Watch Amascut invert the holy symbol during the third memory",),
        ),
        _stage_req(
            7,
            "Hide Amascut's unholy symbol in the eastern sarcophagus.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                "https://runescape.wiki/w/Unholy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6315484"
            ),
            consumed_inventory=(("Unholy symbol (Icthlarin's Little Helper)", 1),),
            auto_actions=("Hide the unholy symbol in the eastern sarcophagus",),
        ),
        _stage_req(
            8,
            "Defeat the possessed priest, break Amascut's hypnosis, and report to the High Priest.",
            (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Possessed_Priest?oldid=6032196; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_POSSESSED_PRIEST_SOURCE}"
            ),
            auto_actions=(
                "Relive Icthlarin removing Amascut's hypnosis and report to the High Priest",
            ),
            combat_encounters=(
                _combat(
                    "icthlarins_little_helper",
                    "possessed_priest",
                    "Possessed Priest",
                    126,
                    (
                        "https://runescape.wiki/w/Possessed_Priest?oldid=6032196; "
                        f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}; "
                        f"{ICTHLARINS_LITTLE_HELPER_POSSESSED_PRIEST_SOURCE}"
                    ),
                    "Level 126, 800 LP, aggressive Magic using bolt spells; approximate period max hit 140.",
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 90),
                        ("strength", 90),
                        ("defence", 40),
                        ("magic", 60),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 140),
                        ("attack_style", "magic"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=ICTHLARINS_LITTLE_HELPER_POSSESSED_PRIEST_SOURCE,
                ),
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Canopic jar": {
            "category": "material",
            "item_id": 4678,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                "https://runescape.wiki/w/Canopic_jar?oldid=6315491; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Sphinx's token": {
            "category": "material",
            "item_id": 4691,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Sphinx%27s_token?oldid=6520569; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Holy symbol (Icthlarin's Little Helper)": {
            "category": "material",
            "item_id": 4682,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Holy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6352893; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Unholy symbol (Icthlarin's Little Helper)": {
            "category": "material",
            "item_id": 4683,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Unholy_symbol_%28Icthlarin%27s_Little_Helper%29?oldid=6315484; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Bucket of sap": {
            "category": "material",
            "item_id": 4687,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Bucket_of_sap?oldid=6288759; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Pile of salt": {
            "category": "material",
            "item_id": 4689,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{ICTHLARINS_LITTLE_HELPER_WIKI_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
        "Catspeak amulet": {
            "category": "equipment",
            "item_id": 4677,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Catspeak_amulet?oldid=6357174; "
                f"{ICTHLARINS_LITTLE_HELPER_CACHE_SOURCE}; "
                f"{ICTHLARINS_LITTLE_HELPER_DARKAN_SOURCE}"
            ),
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'ICTHLARINS_LITTLE_HELPER_STAGES',
)
