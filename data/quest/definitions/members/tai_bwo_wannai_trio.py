from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

TAI_BWO_WANNAI_TRIO_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Timfraku wants his three sons to return to Tai Bwo Wannai."),
    _simple_stage(2, "I helped Tiadeche learn the way to catch karambwan."),
    _simple_stage(3, "I helped Tamayu prepare for his fight with the Shaikahan."),
    _simple_stage(4, "I helped Tinsay gather and prepare unusual food for the village."),
    _simple_stage(5, "The three sons are ready to return to Tai Bwo Wannai."),
    _simple_stage(6, "I reported back to Timfraku and restored the family.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=TAI_BWO_WANNAI_TRIO_ID,
        display_name="Tai Bwo Wannai Trio",
        stages=6,
        point_reward=2,
        rewards=(("Coins", 2000), ("Rune spear (kp)", 1)),
        start_point="Speak to Timfraku in Tai Bwo Wannai Village.",
        requirements=("Jungle Potion", "Agility 15", "Cooking 30", "Fishing 5"),
        required_items=(),
        combat="Must be able to defeat level 48 jogres.",
        source=TAI_BWO_WANNAI_TRIO_SOURCE,
        journal_stages=TAI_BWO_WANNAI_TRIO_STAGES,
        release_date="2004-09-14",
        members=True,
        difficulty="Intermediate",
        length="Long",
        timeline="Fifth Age",
        required_quests=(QuestPrerequisite(JUNGLE_POTION_ID, "Jungle Potion"),),
        required_skills=(
            QuestSkillRequirement("agility", "Agility", 15),
            QuestSkillRequirement("cooking", "Cooking", 30),
            QuestSkillRequirement("fishing", "Fishing", 5),
        ),
        xp_rewards=(
            QuestXpReward("cooking", 5000),
            QuestXpReward("fishing", 5000),
            QuestXpReward("attack", 2500),
            QuestXpReward("strength", 2500),
        ),
        unlocks=("Ability to catch karambwanji and karambwan",),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    TAI_BWO_WANNAI_TRIO_ID: (
        _stage_req(
            2,
            "Help Tiadeche with the karambwan catching setup.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Raw karambwan", 2),),
            required_tools=(("Small fishing net", 1),),
            auto_actions=("Catch karambwanji for Tiadeche",),
        ),
        _stage_req(
            3,
            "Prepare Tamayu to fight the Shaikahan.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Agility potion (4)", 1), ("Steel spear", 1)),
            auto_actions=("Repair and poison Tamayu's spear",),
            combat_encounters=(
                _combat(
                    TAI_BWO_WANNAI_TRIO_ID,
                    "monkey",
                    "Monkey",
                    3,
                    "https://runescape.wiki/w/Tai_Bwo_Wannai_Trio?oldid=6529797",
                    "Quest details require killing a level 3 monkey.",
                ),
                _combat(
                    TAI_BWO_WANNAI_TRIO_ID,
                    "jogre",
                    "Jogre",
                    53,
                    f"https://runescape.wiki/w/Tai_Bwo_Wannai_Trio?oldid=6529797; {TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE}",
                    "Jogre bones can be obtained during the quest by fighting a level 53 jogre.",
                    npc_stats=(
                        ("hitpoints", 600),
                        ("attack", 43),
                        ("strength", 43),
                        ("defence", 43),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 73),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=TAI_BWO_WANNAI_TRIO_JOGRE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            4,
            "Prepare Tinsay's unusual food requests.",
            TAI_BWO_WANNAI_TRIO_SOURCE,
            required_inventory=(("Karamjan rum", 1), ("Seaweed", 1), ("Banana", 1), ("Jogre bones", 1)),
            required_tools=(("Knife", 1), ("Tinderbox", 1), ("Pestle and mortar", 1)),
            auto_actions=("Prepare the sliced banana in rum", "Burn and grind the jogre bones"),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Rune spear (kp)": {"category": "equipment", "source": TAI_BWO_WANNAI_TRIO_SOURCE},
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'TAI_BWO_WANNAI_TRIO_STAGES',
)
