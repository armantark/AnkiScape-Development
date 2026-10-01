from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

TEMPLE_OF_IKOV_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Lucien gave me the Pendant of lucien and sent me to the Temple of Ikov."),
    _simple_stage(2, "I entered the Temple of Ikov with a light source."),
    _simple_stage(3, "I cut through the temple web and found the Boots of lightness."),
    _simple_stage(4, "I crossed the lava bridge at low weight and picked up the lever."),
    _simple_stage(5, "I placed and pulled the lever near the temple entrance to open the ice-arrow route."),
    _simple_stage(6, "I searched the ice chamber chests and gathered ice arrows."),
    _simple_stage(7, "I disarmed the trapped lever and opened the Fire Warrior route."),
    _simple_stage(8, "I defeated the Fire Warrior of Lesarkus with ice arrows and a suitable bow."),
    _simple_stage(9, "Winelda can teleport me across the lava if I bring twenty Limpwurt roots."),
    _simple_stage(10, "I reached the Staff of Armadyl chamber and must choose whether to aid Lucien or the Guardians."),
    _simple_stage(11, "Lucien or the Guardians accepted my choice.", "Quest complete!"),
)


TEMPLE_OF_IKOV_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Enter the Temple of Ikov with Lucien's pendant and a light source.",
        required_inventory_options=(tuple((item_name, 1) for item_name in LIT_LIGHT_SOURCE_ITEMS),),
        required_tools=(("Pendant of lucien", 1),),
        auto_actions=("Enter the Temple of Ikov",),
        source=(
            f"{TEMPLE_OF_IKOV_DARKAN_SOURCE}; {TEMPLE_OF_IKOV_DUNGEON_SOURCE}; "
            f"{TEMPLE_OF_IKOV_LUCIEN_ARDOUGNE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=2,
        description="Cut through the temple web and take the Boots of lightness.",
        required_tools=(("Knife", 1),),
        auto_actions=("Cut through the Temple of Ikov web", "Pick up the Boots of lightness"),
        produced_inventory=(("Boots of lightness", 1),),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Cross the lava bridge at low weight and pick up the lever.",
        required_tools=(("Pendant of lucien", 1), ("Boots of lightness", 1)),
        auto_actions=(
            "Cross the Temple of Ikov lava bridge at low weight",
            "Pick up the Temple of Ikov lever",
        ),
        produced_inventory=(("Lever", 1),),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Place and pull the lever near the entrance to open the ice-arrow route.",
        consumed_inventory=(("Lever", 1),),
        auto_actions=("Place and pull the Temple of Ikov lever near the entrance",),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Search the ice chamber chests for ice arrows.",
        auto_actions=("Search the Temple of Ikov ice-arrow chests",),
        produced_inventory=(("Ice arrows", 1),),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Search the trapped lever for traps, then pull it to open the Fire Warrior route.",
        auto_actions=(
            "Search and disarm the trapped Fire Warrior lever",
            "Pull the disarmed Fire Warrior lever",
        ),
        source=f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Defeat the Fire Warrior of Lesarkus with ice arrows and a compatible bow.",
        required_tools=(("Ice arrows", 1),),
        required_inventory_options=(TEMPLE_OF_IKOV_BOW_OPTIONS,),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{TEMPLE_OF_IKOV_ID}_fire_warrior_of_lesarkus_84",
                display_name="Fire Warrior of Lesarkus",
                level=84,
                source=f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE}",
                source_text=(
                    "The Fire Warrior can only be damaged by ice arrows fired from a compatible bow."
                ),
                npc_stats=(
                    ("hitpoints", 590),
                    ("attack", 78),
                    ("strength", 78),
                    ("defence", 78),
                    ("magic", 62),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 80),
                    ("attack_range", -1),
                    ("attack_style", "magic"),
                    ("attack_bonus", "magic_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE,
            ),
        ),
        source=f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Pay Winelda twenty Limpwurt roots for a teleport across the lava.",
        consumed_inventory=(("Limpwurt root", 20),),
        auto_actions=("Ask Winelda to teleport across the lava",),
        source=f"{TEMPLE_OF_IKOV_WINELDA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Accept the Guardian offer and receive an Armadyl pendant.",
        variant=TEMPLE_OF_IKOV_VARIANT_GUARDIANS,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_GUARDIANS,),
        auto_actions=("Remove the Pendant of lucien and accept the Guardian cleansing",),
        produced_inventory=(("Armadyl pendant", 1),),
        source=f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {TEMPLE_OF_IKOV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Side with Lucien, defeat a blocking Guardian, and take the Staff of Armadyl.",
        variant=TEMPLE_OF_IKOV_VARIANT_LUCIEN,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_LUCIEN,),
        required_tools=(("Pendant of lucien", 1),),
        auto_actions=("Take the Staff of Armadyl from the guarded chamber",),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{TEMPLE_OF_IKOV_ID}_guardian_of_armadyl_45",
                display_name="Guardian of Armadyl",
                level=45,
                source=(
                    f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {TEMPLE_OF_IKOV_2011SCAPE_SPAWN_SOURCE}; "
                    f"{TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE}"
                ),
                source_text=(
                    "Darkan blocks taking the Staff of Armadyl while a Guardian has line of sight; "
                    "AnkiScape models the blocking chamber fight as one Guardian encounter."
                ),
                npc_stats=(
                    ("hitpoints", 500),
                    ("attack", 37),
                    ("strength", 37),
                    ("defence", 37),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 60),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "stab_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Staff of armadyl", 1),),
        source=(
            f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE}; "
            f"{TEMPLE_OF_IKOV_2011SCAPE_SPAWN_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=10,
        description="Wear the Armadyl pendant and defeat Lucien in Varrock.",
        variant=TEMPLE_OF_IKOV_VARIANT_GUARDIANS,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_GUARDIANS,),
        required_tools=(("Armadyl pendant", 1),),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{TEMPLE_OF_IKOV_ID}_lucien_14",
                display_name="Lucien",
                level=14,
                source=f"{TEMPLE_OF_IKOV_LUCIEN_MOB_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE}",
                source_text="Lucien can be attacked only while wearing the Armadyl pendant.",
                npc_stats=(
                    ("hitpoints", 170),
                    ("attack", 12),
                    ("strength", 11),
                    ("defence", 10),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 20),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "stab_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE,
            ),
        ),
        source=f"{TEMPLE_OF_IKOV_LUCIEN_MOB_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Give the Staff of Armadyl to Lucien in Varrock.",
        variant=TEMPLE_OF_IKOV_VARIANT_LUCIEN,
        required_routes=(TEMPLE_OF_IKOV_ROUTE_LUCIEN,),
        consumed_inventory=(("Staff of armadyl", 1),),
        auto_actions=("Give the Staff of Armadyl to Lucien in Varrock",),
        source=f"{TEMPLE_OF_IKOV_LUCIEN_VARROCK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
)

QUEST = QuestDefinition(
        id=TEMPLE_OF_IKOV_ID,
        display_name="Temple of Ikov",
        stage_count=11,
        point_reward=1,
        rewards=(("Shiny key", 1),),
        start_point="Talk to Lucien at the Flying Horse Inn in north-west East Ardougne.",
        requirements=(
            "Thieving 42",
            (
                "Used during quest: Knife x1, Limpwurt root x20, one yew, magic, or dark bow "
                "compatible with ice arrows; bring any valid lit source."
            ),
            (
                "Quest-made items: Pendant of lucien, Boots of lightness, Lever, Ice arrows, "
                "Armadyl pendant, and Staff of armadyl."
            ),
            f"Route choice: {TEMPLE_OF_IKOV_ROUTE_GUARDIANS} or {TEMPLE_OF_IKOV_ROUTE_LUCIEN}.",
        ),
        required_items=(),
        combat=(
            "Fire Warrior of Lesarkus (level 84) must be defeated with ice arrows and a suitable bow. "
            "Guardian route: Lucien (level 14). Lucien route: a blocking Guardian of Armadyl (level 45)."
        ),
        source=(
            f"{TEMPLE_OF_IKOV_DARKAN_SOURCE}; {TEMPLE_OF_IKOV_DUNGEON_SOURCE}; "
            f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_MOB_SOURCE}; "
            f"{TEMPLE_OF_IKOV_LUCIEN_ARDOUGNE_SOURCE}; {TEMPLE_OF_IKOV_LUCIEN_VARROCK_SOURCE}; "
            f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {TEMPLE_OF_IKOV_WINELDA_SOURCE}; "
            f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_NPC_SOURCE}; {TEMPLE_OF_IKOV_GUARDIAN_NPC_SOURCE}; "
            f"{TEMPLE_OF_IKOV_LUCIEN_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {TEMPLE_OF_IKOV_WIKI_SOURCE}"
        ),
        journal_stages=TEMPLE_OF_IKOV_STAGES,
        release_date="2002-06-05",
        members=True,
        difficulty="Intermediate",
        length="Medium",
        timeline="Fifth Age",
        required_skills=(QuestSkillRequirement("thieving", "Thieving", 42),),
        xp_rewards=(QuestXpReward("ranged", 10500), QuestXpReward("fletching", 8000)),
        unlocks=(
            "Access to the Temple of Ikov",
            "Ability to use the Boots of lightness found during the quest",
        ),
        stage_requirements=TEMPLE_OF_IKOV_STAGE_REQUIREMENTS,
        start_inventory=(("Pendant of lucien", 1),),
        choices=TEMPLE_OF_IKOV_CHOICES,
    )

_REWARD_ITEM_FRAGMENT_0 = {
        "Limpwurt root": {
            "category": "material",
            "source": f"{TEMPLE_OF_IKOV_WINELDA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ice arrows": {
            "category": "equipment",
            "equipment_slot": "ammunition",
            "item_id": 78,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lever": {
            "category": "material",
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Staff of armadyl": {
            "category": "material",
            "item_id": 84,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Shiny key": {
            "category": "material",
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_WIKI_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pendant of lucien": {
            "category": "equipment",
            "equipment_slot": "neck",
            "item_id": 86,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_LUCIEN_ARDOUGNE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Armadyl pendant": {
            "category": "equipment",
            "equipment_slot": "neck",
            "item_id": 87,
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_GUARDIAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Boots of lightness": {
            "category": "equipment",
            "equipment_slot": "feet",
            "tradeable": False,
            "source": f"{TEMPLE_OF_IKOV_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Yew comp bow": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 10282,
            "source": f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magic comp bow": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 10284,
            "source": f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Dark bow": {
            "category": "equipment",
            "equipment_slot": "weapon",
            "item_id": 11235,
            "source": f"{TEMPLE_OF_IKOV_FIRE_WARRIOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'TEMPLE_OF_IKOV_STAGES', 'TEMPLE_OF_IKOV_STAGE_REQUIREMENTS',
)
