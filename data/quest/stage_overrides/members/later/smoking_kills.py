from __future__ import annotations

from ....dependencies import *
from ....ids import *
from ....sources import *
from ....item_names import *
from ....contract import *
from ....choices import *

SMOKING_KILLS_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Sumona asked me to rescue Jesmona from beneath the Pollnivneach well.",
        "I should take a cat and wear my Catspeak amulet before I approach the well.",
    ),
    _simple_stage(
        2,
        "Ali Cat warned me that ordinary Slayer protection cannot block both hazards below.",
        "I should follow my cat's guidance into Catolax's tomb and clear the ranged wing.",
    ),
    _simple_stage(
        3,
        "The ranged wing's guardians fell together and awakened a Mummy Warrior.",
        "I must defeat the mummy and take its Ranged path key.",
    ),
    _simple_stage(
        4,
        "I recovered the Ranged path key.",
        "The key opens the wing's inner door, where a lever will disarm its traps.",
    ),
    _simple_stage(
        5,
        "The ranged lever is set and its traps are disabled.",
        "I should break into the magic wing and bring down its four guardians together.",
    ),
    _simple_stage(
        6,
        "The magic wing's guardians awakened a second Mummy Warrior.",
        "I must defeat it and take the Magic path key.",
    ),
    _simple_stage(
        7,
        "I recovered the Magic path key.",
        "Beyond its door, Catolax can teach me how to combine a Face mask with Earmuffs.",
    ),
    _simple_stage(
        8,
        "Catolax's insight let me make Masked earmuffs from the two Slayer protections.",
        "I should wear the Masked earmuffs before climbing down the Pollnivneach well.",
    ),
    _simple_stage(
        9,
        "The Masked earmuffs protect me from the smoke and banshee screams below.",
        "I need a Banshee voice from a Mighty banshee.",
    ),
    _simple_stage(
        10,
        "I defeated a Mighty banshee and recovered its lingering voice.",
        "The Banshee voice should open the mystic barrier.",
    ),
    _simple_stage(
        11,
        "The Banshee voice broke the barrier at the dungeon's heart.",
        "At half health the Banshee Mistress calls four level 141 Insectoid Assassins into the same battle.",
    ),
    _simple_stage(
        12,
        "The Banshee Mistress is dead and Catolax has spoken to me once more.",
        "I should report my victory to Sumona in Pollnivneach.",
    ),
    _simple_stage(13, "Sumona rewarded me and opened the Slayer reward system.", "Quest complete!"),
)

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    SMOKING_KILLS_ID: (
        _stage_req(
            1,
            "Accept Sumona's rescue request and hear Ali Cat's warning at the Pollnivneach well.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            required_tools=(("Catspeak amulet", 1),),
            auto_actions=(
                "Accept Sumona's request to rescue Jesmona",
                "Approach the Pollnivneach well with a cat and hear Ali Cat's warning",
            ),
        ),
        _stage_req(
            2,
            "Break into the ranged wing of Catolax's tomb and bring down all four guardians together.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            required_tools=(("Catspeak amulet", 1), ("Pickaxe", 1)),
            auto_actions=(
                "Follow the cat's guidance through the Ullek swamp to Catolax's tomb",
                "Break the ranged-wing door and disable both trap banks",
                "Bring the four guardians down together before they can recover",
            ),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "ranged_tomb_guardians",
                    "Ranged-wing tomb guardians",
                    20,
                    SMOKING_KILLS_WIKI_SOURCE,
                    (
                        "One grouped resolver wave represents the four roughly 200-LP, level 10-20 "
                        "guardians that must fall together; the pinned infobox and walkthrough disagree "
                        "on their exact identities."
                    ),
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 20),
                        ("strength", 20),
                        ("defence", 20),
                        ("magic", 20),
                        ("ranged", 20),
                    ),
                    npc_configs=(
                        ("attack_style", "ranged"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Review-native grouped upper-bound adapter from Smoking Kills oldid 6548001; "
                        "exact component identities and hidden stats are source_blocked"
                    ),
                ),
            ),
        ),
        _stage_req(
            3,
            "Defeat the Mummy Warrior awakened by the ranged-wing guardians.",
            f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; {SMOKING_KILLS_MUMMY_DARKAN_SOURCE}",
            produced_inventory=(("Ranged path key", 1),),
            auto_actions=("Take the Ranged path key from the fallen Mummy Warrior",),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "ranged_mummy_warrior",
                    "Mummy Warrior",
                    54,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; "
                        f"{SMOKING_KILLS_MUMMY_DARKAN_SOURCE}"
                    ),
                    "The first level 54 Mummy Warrior uses melee and can hit up to 80.",
                    npc_stats=(
                        ("hitpoints", 540),
                        ("attack", 54),
                        ("strength", 54),
                        ("defence", 54),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 80),
                        ("attack_style", "melee"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Bounded level-based resolver adapter; period HP and hidden combat stats are source_blocked, "
                        "while level 54 and max hit 80 are sourced"
                    ),
                ),
            ),
        ),
        _stage_req(
            4,
            "Open the ranged path door and pull its lever to disarm the wing's traps.",
            SMOKING_KILLS_WIKI_SOURCE,
            consumed_inventory=(("Ranged path key", 1),),
            auto_actions=(
                "Open the ranged path door",
                "Pull the ranged-wing lever",
            ),
        ),
        _stage_req(
            5,
            "Break into the magic wing and bring down its four guardians together.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_inventory_options=(
                (
                    ("Kitten", 1),
                    ("Cat", 1),
                    ("Overgrown cat", 1),
                    ("Hellcat", 1),
                ),
            ),
            required_tools=(("Catspeak amulet", 1), ("Pickaxe", 1)),
            auto_actions=(
                "Break the magic-wing door and disable both trap banks",
                "Bring the four guardians down together before they can recover",
            ),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "magic_tomb_guardians",
                    "Magic-wing tomb guardians",
                    20,
                    SMOKING_KILLS_WIKI_SOURCE,
                    (
                        "One grouped resolver wave represents the four roughly 200-LP, level 10-20 "
                        "guardians that must fall together; the pinned infobox and walkthrough disagree "
                        "on their exact identities."
                    ),
                    npc_stats=(
                        ("hitpoints", 800),
                        ("attack", 20),
                        ("strength", 20),
                        ("defence", 20),
                        ("magic", 20),
                        ("ranged", 20),
                    ),
                    npc_configs=(
                        ("attack_style", "magic"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Review-native grouped upper-bound adapter from Smoking Kills oldid 6548001; "
                        "exact component identities and hidden stats are source_blocked"
                    ),
                ),
            ),
        ),
        _stage_req(
            6,
            "Defeat the Mummy Warrior awakened by the magic-wing guardians.",
            f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; {SMOKING_KILLS_MUMMY_DARKAN_SOURCE}",
            produced_inventory=(("Magic path key", 1),),
            auto_actions=("Take the Magic path key from the fallen Mummy Warrior",),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "magic_mummy_warrior",
                    "Mummy Warrior",
                    54,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MUMMY_SOURCE}; "
                        f"{SMOKING_KILLS_MUMMY_DARKAN_SOURCE}"
                    ),
                    "The second level 54 Mummy Warrior uses melee and can hit up to 80.",
                    npc_stats=(
                        ("hitpoints", 540),
                        ("attack", 54),
                        ("strength", 54),
                        ("defence", 54),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 80),
                        ("attack_style", "melee"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Bounded level-based resolver adapter; period HP and hidden combat stats are source_blocked, "
                        "while level 54 and max hit 80 are sourced"
                    ),
                ),
            ),
        ),
        _stage_req(
            7,
            "Unlock the final path, speak to Catolax, and combine the two Slayer protections.",
            SMOKING_KILLS_WIKI_SOURCE,
            consumed_inventory=(
                ("Magic path key", 1),
                ("Face mask", 1),
                ("Earmuffs", 1),
            ),
            produced_inventory=(("Masked earmuffs", 1),),
            required_tools=(("Ghostspeak amulet", 1),),
            auto_actions=(
                "Open the magic path door and pull its lever",
                "Cross the disabled central traps and speak to Catolax",
                "Combine the Face mask and Earmuffs using Catolax's insight",
            ),
        ),
        _stage_req(
            8,
            "Climb down the Pollnivneach well with Masked earmuffs protecting you.",
            SMOKING_KILLS_WIKI_SOURCE,
            required_tools=(("Masked earmuffs", 1),),
            auto_actions=("Enter the Desert Slayer Dungeon through the Pollnivneach well",),
        ),
        _stage_req(
            9,
            "Defeat a Mighty banshee and take its lingering voice.",
            (
                f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MIGHTY_BANSHEE_SOURCE}; "
                f"{SMOKING_KILLS_MIGHTY_BANSHEE_DARKAN_SOURCE}"
            ),
            produced_inventory=(("Banshee voice", 1),),
            required_tools=(("Masked earmuffs", 1),),
            auto_actions=(
                "Recover one Banshee voice after the Mighty banshee falls",
            ),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "mighty_banshee",
                    "Mighty banshee",
                    90,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MIGHTY_BANSHEE_SOURCE}; "
                        f"{SMOKING_KILLS_MIGHTY_BANSHEE_DARKAN_SOURCE}"
                    ),
                    (
                        "A level 90 aggressive Mighty banshee with 850 LP, magical melee, "
                        "attack speed 6, and approximate max hit 90. One deterministic quest kill "
                        "stands in for the source-blocked Banshee voice drop rate."
                    ),
                    npc_stats=(
                        ("hitpoints", 850),
                        ("attack", 90),
                        ("strength", 90),
                        ("defence", 90),
                        ("magic", 90),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 90),
                        ("attack_speed", 6),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Period HP/max hit/style plus Darkan convergence; hidden combat stats use a bounded "
                        "level-based resolver adapter"
                    ),
                ),
            ),
        ),
        _stage_req(
            10,
            "Use the Banshee voice on the mystic barrier.",
            SMOKING_KILLS_WIKI_SOURCE,
            consumed_inventory=(("Banshee voice", 1),),
            required_tools=(("Masked earmuffs", 1),),
            auto_actions=("Release the Banshee voice into the mystic barrier",),
        ),
        _stage_req(
            11,
            "Defeat the Banshee Mistress and survive the assassins she calls at half health.",
            (
                f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MISTRESS_SOURCE}; "
                f"{SMOKING_KILLS_MISTRESS_DARKAN_SOURCE}"
            ),
            required_tools=(("Masked earmuffs", 1),),
            combat_encounters=(
                _combat(
                    SMOKING_KILLS_ID,
                    "banshee_mistress",
                    "Banshee Mistress",
                    111,
                    (
                        f"{SMOKING_KILLS_WIKI_SOURCE}; {SMOKING_KILLS_MISTRESS_SOURCE}; "
                        f"{SMOKING_KILLS_MISTRESS_DARKAN_SOURCE}"
                    ),
                    (
                        "At half health the Mistress cries \"Minions, aid me!\" and her four level 141 "
                        "Insectoid Assassins join her. AnkiScape folds their level-141 ranged pressure, "
                        "up to 200 damage each, into this single boss battle; they are not separate kills."
                    ),
                    npc_stats=(
                        ("hitpoints", 2220),
                        ("attack", 111),
                        ("strength", 111),
                        ("defence", 111),
                        ("magic", 111),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 200),
                        ("attack_style", "magic"),
                        ("aggressiveness_type", "aggressive"),
                        ("minimum_player_combat", 85),
                    ),
                    npc_stats_source=(
                        "Period 2220 LP and mixed melee/Magic boss behavior with an explicitly collapsed "
                        "half-health assassin phase; hidden combat stats use a bounded level-based adapter"
                    ),
                ),
            ),
        ),
        _stage_req(
            12,
            "Report the Banshee Mistress's defeat to Sumona.",
            SMOKING_KILLS_WIKI_SOURCE,
            auto_actions=(
                "Hear Catolax's final message",
                "Return to Pollnivneach and report the victory to Sumona",
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Ghostspeak amulet": {
            "category": "equipment",
            "item_id": 552,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Ghostspeak_amulet?oldid=6358472; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 552; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Kitten": {
            "category": "material",
            "item_id": 1555,
            "tradeable": False,
            "stackable": False,
            "source": (
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 1555; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Ranged path key": {
            "category": "material",
            "item_id": 13259,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{SMOKING_KILLS_WIKI_SOURCE}; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13259; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Magic path key": {
            "category": "material",
            "item_id": 13260,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{SMOKING_KILLS_WIKI_SOURCE}; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13260; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Banshee voice": {
            "category": "material",
            "item_id": 13276,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{SMOKING_KILLS_WIKI_SOURCE}; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13276; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
        "Masked earmuffs": {
            "category": "equipment",
            "item_id": 13277,
            "tradeable": False,
            "stackable": False,
            "source": (
                "https://runescape.wiki/w/Masked_earmuffs?oldid=6283360; "
                "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml item 13277; "
                f"{DARKAN_DEVELOPER_INFO_ROOT}/itemList.txt"
            ),
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'SMOKING_KILLS_STAGES',
)
