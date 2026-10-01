from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

SHILO_VILLAGE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Mosol Rei gave me a Wampum belt for Trufitus.",
        "I should deliver the belt to Trufitus in Tai Bwo Wannai.",
    ),
    _simple_stage(
        2,
        "Trufitus believes the lost Temple of Ah Za Rhoon holds the key to Rashiliyia's curse.",
        "I should search the coast east of Tai Bwo Wannai with a lit light source and rope.",
    ),
    _simple_stage(
        3,
        "I entered Ah Za Rhoon.",
        "I should recover and read every clue about Rashiliyia, Bervirius, and Zadimus.",
    ),
    _simple_stage(
        4,
        "I recovered the temple's two scrolls, stone-plaque, and Zadimus corpse.",
        "Trufitus can interpret the evidence and tell me how to lay Zadimus to rest.",
    ),
    _simple_stage(
        5,
        "Zadimus's burial left me a bone shard and pointed toward Bervirius's tomb.",
        "I should search the Cairn Isle dolmen for clues about Rashiliyia.",
    ),
    _simple_stage(
        6,
        "Bervirius's tomb held a sword pommel, locating crystal, and his notes.",
        "I should read the notes and show the evidence to Trufitus.",
    ),
    _simple_stage(
        7,
        "The clues explain how to find Rashiliyia's tomb and protect myself inside.",
        "I must carve Zadimus's Bone key and chisel the Sword pommel into Bone beads.",
    ),
    _simple_stage(
        8,
        "I carved the Bone key and Bone beads.",
        "Bronze wire will turn the beads into the protective Beads of the dead.",
    ),
    _simple_stage(
        9,
        "I have the Bone key and Beads of the dead.",
        "The locating crystal can lead me to Rashiliyia's tomb, where three regular bones open the inner door.",
    ),
    _simple_stage(
        10,
        "I entered Rashiliyia's tomb.",
        "Nazastarool will return as a zombie, skeleton, and ghost before yielding Rashiliyia's corpse.",
    ),
    _simple_stage(
        11,
        "I defeated all three forms of Nazastarool and recovered Rashiliyia's corpse.",
        "I should show it to Trufitus, then place it on Bervirius's dolmen.",
    ),
    _simple_stage(12, "Rashiliyia's spirit is finally at rest and Shilo Village is open.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=SHILO_VILLAGE_ID,
        display_name="Shilo Village",
        stages=len(SHILO_VILLAGE_STAGES),
        point_reward=2,
        rewards=(),
        start_point="Talk to Mosol Rei outside Shilo Village in southern Karamja.",
        requirements=(
            "Jungle Potion",
            "Smithing 4",
            "Crafting 20",
            "Agility 32",
            "Used during quest: Rope x1, lit light source x1, Spade x1, Chisel x1, Bronze wire x1, Bones x3",
        ),
        required_items=(),
        combat="Nazastarool: level 91 Zombie, level 68 Skeleton, then level 93 Ghost.",
        source=(
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; "
            f"{SHILO_VILLAGE_MOSOL_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}; "
            f"{SHILO_VILLAGE_CACHE_SOURCE}"
        ),
        journal_stages=SHILO_VILLAGE_STAGES,
        release_date="2003-01-27",
        members=True,
        difficulty="Experienced",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(JUNGLE_POTION_ID, "Jungle Potion"),),
        required_skills=(
            QuestSkillRequirement("smithing", "Smithing", 4),
            QuestSkillRequirement("crafting", "Crafting", 20),
            QuestSkillRequirement("agility", "Agility", 32),
        ),
        xp_rewards=(QuestXpReward("crafting", 3875),),
        unlocks=(
            "Access to Shilo Village",
            "Access to Shilo Village gem rocks",
            "Access to the Shilo Village cart service",
        ),
        start_inventory=(("Wampum belt", 1),),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    SHILO_VILLAGE_ID: (
        _stage_req(
            1,
            "Deliver Mosol Rei's Wampum belt to Trufitus and agree to search for Ah Za Rhoon.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_MOSOL_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            consumed_inventory=(("Wampum belt", 1),),
            auto_actions=(
                "Accept Mosol Rei's warning and carry the Wampum belt to Trufitus",
                "Ask Trufitus about Ah Za Rhoon and agree to search for the lost temple",
            ),
        ),
        _stage_req(
            2,
            "Find the Ah Za Rhoon fissure, light the drop, secure a rope, and enter the temple.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
            consumed_inventory=(("Rope", 1),),
            consumed_inventory_options=(
                tuple((item_name, 1) for item_name in LIT_LIGHT_SOURCE_ITEMS),
            ),
            required_tools=(("Spade", 1),),
            auto_actions=(
                "Dig into the buried mound east of Tai Bwo Wannai",
                "Lower the lit light source into the fissure and secure the rope",
                "Climb into Ah Za Rhoon",
            ),
        ),
        _stage_req(
            3,
            "Read the temple scrolls, recover the plaque, and take Zadimus's remains.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            produced_inventory=(
                ("Stone-plaque", 1),
                ("Tattered scroll", 1),
                ("Crumpled scroll", 1),
                ("Zadimus corpse", 1),
            ),
            auto_actions=(
                "Include the Stone-plaque in the collapsed temple search",
                "Search past the loose-rock trap and gallows gas",
                "Recover and read both Ah Za Rhoon scrolls, then take Zadimus's corpse",
            ),
        ),
        _stage_req(
            4,
            "Show the Ah Za Rhoon evidence to Trufitus and bury Zadimus on sacred ground.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            required_inventory=(
                ("Tattered scroll", 1),
                ("Crumpled scroll", 1),
            ),
            consumed_inventory=(("Zadimus corpse", 1),),
            produced_inventory=(("Bone shard", 1),),
            auto_actions=(
                "Show both scrolls and Zadimus's corpse; include the plaque if it is still carried",
                "Bury Zadimus beside the tribal statue and receive his Bone shard",
            ),
        ),
        _stage_req(
            5,
            "Search Bervirius's Cairn Isle tomb for the clues left on its dolmen.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            produced_inventory=(
                ("Sword pommel", 1),
                ("Locating crystal", 1),
                ("Bervirius notes", 1),
            ),
            auto_actions=(
                "Cross to Cairn Isle and descend into Bervirius's tomb",
                "Search the dolmen and recover all three clues",
            ),
        ),
        _stage_req(
            6,
            "Read Bervirius's notes and show the tomb evidence to Trufitus.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            required_inventory=(
                ("Sword pommel", 1),
                ("Locating crystal", 1),
                ("Bervirius notes", 1),
            ),
            auto_actions=(
                "Read all three sections of Bervirius's notes",
                "Show the Sword pommel, Locating crystal, and notes to Trufitus",
            ),
        ),
        _stage_req(
            7,
            "Carve Zadimus's Bone key and chisel the Sword pommel into Bone beads.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            required_inventory=(("Bervirius notes", 1),),
            consumed_inventory=(
                ("Bone shard", 1),
                ("Sword pommel", 1),
            ),
            produced_inventory=(("Bone key", 1), ("Bone beads", 1)),
            required_tools=(("Chisel", 1),),
            auto_actions=(
                "Carve the Bone shard into the Bone key",
                "Chisel the Sword pommel into Bone beads",
            ),
        ),
        _stage_req(
            8,
            "String the Bone beads with Bronze wire to make the protective Beads of the dead.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}",
            required_inventory=(("Bervirius notes", 1),),
            consumed_inventory=(("Bone beads", 1), ("Bronze wire", 1)),
            produced_inventory=(("Beads of the dead", 1),),
            auto_actions=("String the Bone beads with Bronze wire",),
        ),
        _stage_req(
            9,
            "Locate Rashiliyia's tomb, wear the Beads of the dead, and open its bone doors.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
            consumed_inventory=(("Bones", 3),),
            required_tools=(
                ("Bone key", 1),
                ("Beads of the dead", 1),
                ("Locating crystal", 1),
            ),
            auto_actions=(
                "Use the Locating crystal to find Rashiliyia's hidden tomb",
                "Wear the Beads of the dead and unlock the ancient door with the Bone key",
                "Fill the skeletal door's three recesses with regular bones",
            ),
        ),
        _stage_req(
            10,
            "Defeat Nazastarool's zombie, skeleton, and ghost forms in order.",
            (
                f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; "
                f"{DARKAN_NAZASTAROOL_91_NPC_SOURCE}; "
                f"{DARKAN_NAZASTAROOL_68_NPC_SOURCE}; "
                f"{DARKAN_NAZASTAROOL_93_NPC_SOURCE}"
            ),
            produced_inventory=(("Rashiliyia corpse", 1),),
            required_tools=(("Bone key", 1), ("Beads of the dead", 1)),
            auto_actions=("Take Rashiliyia's corpse from the dolmen after the final form falls",),
            combat_encounters=(
                QuestCombatEncounter(
                    encounter_id="shilo_village_nazastarool_91",
                    display_name="Nazastarool",
                    level=91,
                    source=SHILO_VILLAGE_WIKI_SOURCE,
                ),
            ),
        ),
        _stage_req(
            11,
            "Show Rashiliyia's corpse to Trufitus, then return it to Bervirius's dolmen.",
            f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}; {SHILO_VILLAGE_TRUFITUS_SOURCE}",
            consumed_inventory=(("Rashiliyia corpse", 1),),
            auto_actions=(
                "Show Rashiliyia's corpse to Trufitus",
                "Return to Cairn Isle and place the corpse on Bervirius's dolmen",
                "Release Rashiliyia's spirit and open Shilo Village",
            ),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Bone shard": {
            "category": "material",
            "item_id": 604,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Bone key": {
            "category": "material",
            "item_id": 605,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Stone-plaque": {
            "category": "material",
            "item_id": 606,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Tattered scroll": {
            "category": "material",
            "item_id": 607,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Crumpled scroll": {
            "category": "material",
            "item_id": 608,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Rashiliyia corpse": {
            "category": "material",
            "item_id": 609,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Zadimus corpse": {
            "category": "material",
            "item_id": 610,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Locating crystal": {
            "category": "material",
            "item_id": 611,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Beads of the dead": {
            "category": "equipment",
            "item_id": 616,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Bone beads": {
            "category": "material",
            "item_id": 618,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Sword pommel": {
            "category": "material",
            "item_id": 623,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Bervirius notes": {
            "category": "material",
            "item_id": 624,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_DARKAN_SOURCE}",
        },
        "Wampum belt": {
            "category": "material",
            "item_id": 625,
            "tradeable": False,
            "stackable": False,
            "source": f"{SHILO_VILLAGE_WIKI_SOURCE}; {SHILO_VILLAGE_CACHE_SOURCE}; {SHILO_VILLAGE_MOSOL_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'SHILO_VILLAGE_STAGES',
)
