from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

LOST_CITY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The adventurers in Lumbridge Swamp are searching for Zanaris.", "I should find out what they know."),
    _simple_stage(2, "I found Shamus hiding in a swamp tree.", "He says Zanaris is reached through the shed while carrying a dramen staff."),
    _simple_stage(3, "I travelled to Entrana to find the dramen tree.", "The tree is protected by a dangerous spirit."),
    _simple_stage(4, "I defeated the tree spirit and cut a dramen branch."),
    _simple_stage(5, "I crafted a dramen staff from the branch.", "The shed in Lumbridge Swamp should now open the way."),
    _simple_stage(6, "I entered Zanaris through the swamp shed.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=LOST_CITY_ID,
        display_name="Lost City",
        stage_count=6,
        point_reward=3,
        rewards=(),
        start_point="Talk to the warrior adventurer in Lumbridge Swamp.",
        requirements=("Crafting 31", "Woodcutting 36", "Used during quest: Hatchet x1, Knife x1"),
        required_items=(),
        combat="Must be able to kill a level 63 Tree spirit.",
        source=(
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_WARRIOR_SOURCE_PATH}; {LOST_CITY_TREE_SOURCE_PATH}; "
            f"{LOST_CITY_SHAMUS_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_SHED_SOURCE_PATH}; "
            f"{LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH}"
        ),
        journal_stages=LOST_CITY_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Experienced",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(
            QuestSkillRequirement("crafting", "Crafting", 31),
            QuestSkillRequirement("woodcutting", "Woodcutting", 36),
        ),
        unlocks=("Access to Zanaris", "Ability to craft cosmic runes"),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    LOST_CITY_ID: (
        _stage_req(
            1,
            "Find Shamus in the Lumbridge Swamp tree.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_WARRIOR_SOURCE_PATH}; {LOST_CITY_TREE_SOURCE_PATH}",
            auto_actions=("Find Shamus in the Lumbridge Swamp tree",),
        ),
        _stage_req(
            2,
            "Speak to Shamus about the dramen staff and reach Entrana.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_SHAMUS_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}",
            auto_actions=(
                "Speak to Shamus about the dramen staff",
                "Reach Entrana without combat gear",
            ),
        ),
        _stage_req(
            3,
            "Defeat the tree spirit guarding the Dramen tree.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH}",
            combat_encounters=(
                _combat(
                    LOST_CITY_ID,
                    "tree_spirit",
                    "Tree spirit",
                    63,
                    f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH}",
                    "2011Scape Lost City text requires killing the level 63 Tree spirit; the local NPC definition supplies the melee combat stats.",
                    npc_stats=(
                        ("hitpoints", 220),
                        ("attack", 90),
                        ("strength", 95),
                        ("defence", 80),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 5),
                        ("defenceSlash", 5),
                        ("defenceCrush", 5),
                        ("defenceMagic", 0),
                        ("defenceRanged", 5),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=LOST_CITY_TREE_SPIRIT_NPC_SOURCE_PATH,
                ),
            ),
        ),
        _stage_req(
            4,
            "Cut a dramen branch from the Dramen tree.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}",
            required_tools=(("Hatchet", 1),),
            auto_actions=("Cut a dramen branch",),
            produced_inventory=(("Dramen branch", 1),),
        ),
        _stage_req(
            5,
            "Craft the dramen staff and enter Zanaris through the Lumbridge Swamp shed.",
            f"{LOST_CITY_SOURCE_PATH}; {LOST_CITY_ENTRANA_SOURCE_PATH}; {LOST_CITY_SHED_SOURCE_PATH}",
            required_inventory=(("Dramen branch", 1),),
            consumed_inventory=(("Dramen branch", 1),),
            produced_inventory=(("Dramen staff", 1),),
            required_tools=(("Knife", 1),),
            auto_actions=("Craft a dramen staff", "Enter Zanaris through the Lumbridge Swamp shed"),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Dramen staff": {"category": "material", "source": LOST_CITY_SOURCE_PATH},
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'LOST_CITY_STAGES',
)
