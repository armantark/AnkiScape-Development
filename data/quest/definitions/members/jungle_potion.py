from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

JUNGLE_POTION_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Trufitus asked me to find, clean, and return snake weed from the marshy jungle vines."),
    _simple_stage(2, "Trufitus asked me to find, clean, and return ardrigal from the north-east palm trees."),
    _simple_stage(3, "Trufitus asked me to find, clean, and return sito foil from the scorched earth."),
    _simple_stage(4, "Trufitus asked me to find, clean, and return volencia moss from the south-east rocks."),
    _simple_stage(5, "Trufitus asked me to find, clean, and return rogue's purse from the northern caves."),
    _simple_stage(
        6,
        "I collected five jungle herbs for Trufitus and he rewarded me with Herblore training.",
        "Quest complete!",
    ),
)

QUEST = QuestDefinition(
        id=JUNGLE_POTION_ID,
        display_name="Jungle Potion",
        stages=len(JUNGLE_POTION_STAGES),
        point_reward=1,
        rewards=(),
        start_point="Speak to Trufitus near Tai Bwo Wannai.",
        requirements=(
            "Druidic Ritual",
            "Herblore 3",
            "Used during quest: the five jungle herbs found and cleaned in strict order",
        ),
        required_items=(),
        combat="None required; the jungle contains environmental dangers.",
        source=(
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; "
            f"{DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_CACHE_SOURCE}; "
            f"{JUNGLE_POTION_WIKI_SOURCE}"
        ),
        journal_stages=JUNGLE_POTION_STAGES,
        release_date="2002-10-23",
        members=True,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(DRUIDIC_RITUAL_ID, "Druidic Ritual"),),
        required_skills=(QuestSkillRequirement("herblore", "Herblore", 3),),
        xp_rewards=(QuestXpReward("herblore", 775),),
        supply_recipes=(
            QuestSupplyRecipe(step="search marshy jungle vines", product="Grimy snake weed", source=JUNGLE_POTION_WIKI_SOURCE),
            QuestSupplyRecipe(step="clean snake weed", herblore_id="clean_snake_weed"),
            QuestSupplyRecipe(step="search jungle palm trees", product="Grimy ardrigal", source=JUNGLE_POTION_WIKI_SOURCE),
            QuestSupplyRecipe(step="clean ardrigal", herblore_id="clean_ardrigal"),
            QuestSupplyRecipe(step="search scorched earth", product="Grimy sito foil", source=JUNGLE_POTION_WIKI_SOURCE),
            QuestSupplyRecipe(step="clean sito foil", herblore_id="clean_sito_foil"),
            QuestSupplyRecipe(step="search jungle mine rocks", product="Grimy volencia moss", source=JUNGLE_POTION_WIKI_SOURCE),
            QuestSupplyRecipe(step="clean volencia moss", herblore_id="clean_volencia_moss"),
            QuestSupplyRecipe(step="search fungus-covered cavern wall", product="Grimy rogue's purse", source=JUNGLE_POTION_WIKI_SOURCE),
            QuestSupplyRecipe(step="clean rogue's purse", herblore_id="clean_rogues_purse"),
        ),
        unlocks=(
            "Access to Tai Bwo Wannai Cleanup",
            "Access to Rionasta's parcel service",
            "Access to the Calquat gardener",
            "Eligibility to start Shilo Village",
        ),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    JUNGLE_POTION_ID: (
        _stage_req(
            1,
            "Find, clean, and give Trufitus snake weed from the south-west marshy jungle vines.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean snake weed", 1),),
            required_skills=(QuestSkillRequirement("herblore", "Herblore", 3),),
            auto_actions=(
                "Give Trufitus clean snake weed",
            ),
        ),
        _stage_req(
            2,
            "Find, clean, and give Trufitus ardrigal from the north-east palm trees.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean ardrigal", 1),),
            required_skills=(QuestSkillRequirement("herblore", "Herblore", 3),),
            auto_actions=(
                "Give Trufitus clean ardrigal",
            ),
        ),
        _stage_req(
            3,
            "Find, clean, and give Trufitus sito foil from the scorched earth south of the village.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean sito foil", 1),),
            required_skills=(QuestSkillRequirement("herblore", "Herblore", 3),),
            auto_actions=(
                "Give Trufitus clean sito foil",
            ),
        ),
        _stage_req(
            4,
            "Find, clean, and give Trufitus volencia moss from the rocks south-east of the village.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean volencia moss", 1),),
            required_skills=(QuestSkillRequirement("herblore", "Herblore", 3),),
            auto_actions=(
                "Give Trufitus clean volencia moss",
            ),
        ),
        _stage_req(
            5,
            "Find, clean, and give Trufitus rogue's purse from the fungus-covered northern cavern wall.",
            f"{DARKAN_JUNGLE_POTION_SOURCE}; {DARKAN_JUNGLE_POTION_TRUFITUS_SOURCE}; {DARKAN_HERB_CLEANING_SOURCE_PATH}; {JUNGLE_POTION_CACHE_SOURCE}; {JUNGLE_POTION_WIKI_SOURCE}",
            consumed_inventory=(("Clean rogue's purse", 1),),
            required_skills=(QuestSkillRequirement("herblore", "Herblore", 3),),
            auto_actions=(
                "Give Trufitus clean rogue's purse",
            ),
        ),
    ),
}

__all__ = (
    'JUNGLE_POTION_STAGES',
)
