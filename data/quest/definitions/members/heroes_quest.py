from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

HEROES_QUEST_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Achietties accepted my application and set three proof tasks.",
        "I need an Entranan Firebird feather, a Master Thieves' armband, and a cooked Lava eel.",
    ),
    _simple_stage(2, "Gerrant in Port Sarim can explain how to catch lava eels."),
    _simple_stage(3, "Gerrant gave me Blamish snail slime for a lava-proof rod."),
    _simple_stage(4, "I made Blamish oil from the slime and unfinished harralander."),
    _simple_stage(5, "I coated an ordinary fishing rod with Blamish oil."),
    _simple_stage(6, "I caught a raw Lava eel with the oily fishing rod."),
    _simple_stage(
        7,
        "I cooked the Lava eel.",
        "I still need Ice gloves before I can safely collect the firebird feather.",
    ),
    _simple_stage(8, "I defeated the Ice Queen and obtained Ice gloves.", "The Entranan Firebird feather remains."),
    _simple_stage(
        9,
        "I collected the Entranan Firebird feather.",
        "Now I need the Master Thieves' armband through my Shield of Arrav gang contacts.",
    ),
    _simple_stage(10, "My gang contacts can get me into Scarface Pete's mansion for Pete's candlestick."),
    _simple_stage(11, "I have Pete's candlestick and can trade it for the Master Thieves' armband."),
    _simple_stage(12, "I have the cooked Lava eel, Fire feather, and Thieves' armband for Achietties."),
    _simple_stage(13, "Achietties accepted my proof items and opened the Heroes' Guild.", "Quest complete!"),
)


HEROES_QUEST_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Accept Achietties' three proof item challenge.",
        auto_actions=("Accept Achietties' three proof item challenge",),
        source=f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ACHIETTIES_SOURCE}",
    ),
    QuestStageRequirement(
        stage=2,
        description="Ask Gerrant how to catch a lava eel and receive Blamish snail slime.",
        auto_actions=("Ask Gerrant how to catch lava eels",),
        produced_inventory=(("Blamish snail slime", 1),),
        source=f"{HEROES_QUEST_PORT_SARIM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Mix Blamish snail slime into unfinished harralander to make Blamish oil.",
        consumed_inventory=(("Blamish snail slime", 1), ("Harralander potion (unf)", 1)),
        produced_inventory=(("Blamish oil", 1),),
        source=f"{HEROES_QUEST_HERBLORE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Coat a fishing rod with Blamish oil.",
        consumed_inventory=(("Blamish oil", 1), ("Fishing rod", 1)),
        produced_inventory=(("Oily fishing rod", 1),),
        source=f"{HEROES_QUEST_DARKAN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Catch a raw Lava eel at a lava eel fishing spot.",
        consumed_inventory=(("Fishing bait", 1),),
        produced_inventory=(("Raw lava eel", 1),),
        required_tools=(("Oily fishing rod", 1),),
        auto_actions=("Reach a lava eel fishing spot in Taverley Dungeon or the Lava Maze",),
        source=(
            f"{HEROES_QUEST_FISH_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; "
            f"{HEROES_QUEST_FISHING_SOURCE}; {HEROES_QUEST_PORT_SARIM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=6,
        description="Cook the raw Lava eel.",
        consumed_inventory=(("Raw lava eel", 1),),
        produced_inventory=(("Lava eel", 1),),
        auto_actions=("Cook the raw Lava eel",),
        source=f"{HEROES_QUEST_COOKING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Clear the Ice Queen lair rockslide and defeat the Ice Queen.",
        required_tools=(("Pickaxe", 1),),
        auto_actions=(
            "Clear the Ice Queen lair rockslide",
            "Reach the Ice Queen lair through a Dusty key or Agility shortcut route",
        ),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{HEROES_QUEST_ID}_ice_queen_111",
                display_name="Ice Queen",
                level=111,
                source=(
                    f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {HEROES_QUEST_ICE_QUEEN_NPC_SOURCE}; "
                    f"{HEROES_QUEST_WIKI_SOURCE}"
                ),
                source_text="The Ice Queen is defeated in her lair to obtain Ice gloves before collecting the Fire feather.",
                npc_stats=(
                    ("hitpoints", 1050),
                    ("attack", 95),
                    ("strength", 94),
                    ("defence", 95),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 100),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=HEROES_QUEST_ICE_QUEEN_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Ice gloves", 1),),
        source=f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {HEROES_QUEST_ICE_QUEEN_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Defeat the Entranan Firebird and pick up its feather with Ice gloves.",
        required_tools=(("Ice gloves", 1),),
        auto_actions=("Reach Entrana without prohibited combat equipment",),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{HEROES_QUEST_ID}_entrana_fire_bird_2",
                display_name="Entrana Fire Bird",
                level=2,
                source=f"{HEROES_QUEST_WIKI_SOURCE}; {DARKAN_NPC_LIST_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}",
                source_text="The Fire feather is obtained by killing an Entranan Firebird and can only be picked up with Ice gloves.",
                npc_stats=(
                    ("hitpoints", 50),
                    ("attack", 1),
                    ("strength", 1),
                    ("defence", 1),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 10),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "stab_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Fire feather", 1),),
        source=f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Use the Black Arm Gang contacts in Brimhaven and receive Id papers from Trobert.",
        variant=HEROES_VARIANT_BLACK_ARM,
        required_routes=(HEROES_ROUTE_BLACK_ARM,),
        auto_actions=(
            "Ask Katrine about the Scarface Pete candlestick mission",
            "Enter the Black Arm Brimhaven hideout with the Four leaved clover password",
            "Accept Trobert's deputy guard impersonation mission",
        ),
        produced_inventory=(("Id papers", 1),),
        source=(
            f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_BRIMHAVEN_SOURCE}; "
            f"{HEROES_QUEST_TROBERT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=9,
        description="Use the Phoenix Gang contacts in Brimhaven and learn about the mansion's secret panel.",
        variant=HEROES_VARIANT_PHOENIX,
        required_routes=(HEROES_ROUTE_PHOENIX,),
        auto_actions=(
            "Ask Straven about the Scarface Pete candlestick mission",
            "Ask Alfonse the waiter for gherkins",
            "Ask Charlie the cook about the Phoenix guard inside Scarface Pete's mansion",
        ),
        source=f"{HEROES_QUEST_STRAVEN_SOURCE}; {HEROES_QUEST_ALFONSO_SOURCE}; {HEROES_QUEST_CHARLIE_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Enter Scarface Pete's mansion as a Black Arm deputy guard and search the candlestick chest.",
        variant=HEROES_VARIANT_BLACK_ARM,
        required_routes=(HEROES_ROUTE_BLACK_ARM,),
        required_tools=(("Black full helm", 1), ("Black platebody", 1), ("Black platelegs", 1)),
        consumed_inventory=(("Id papers", 1),),
        auto_actions=("Show the Id papers to Garv", "Search Scarface Pete's candlestick chest"),
        produced_inventory=(("Pete's candlestick", 1),),
        source=f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {HEROES_QUEST_BRIMHAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description=(
            "Use the Phoenix secret panel and a Black Arm Gang partner's key to attack Grip after "
            "that partner lures him, then receive one of the candlesticks they retrieve."
        ),
        variant=HEROES_VARIANT_PHOENIX,
        required_routes=(HEROES_ROUTE_PHOENIX,),
        auto_actions=(
            "Enter Scarface Pete's mansion through the Phoenix Gang secret panel",
            "Unlock the window room with a Black Arm Gang partner's miscellaneous key",
            "Receive one of Pete's candlesticks after the Black Arm Gang partner opens the chest with Grip's key",
        ),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{HEROES_QUEST_ID}_grip_22",
                display_name="Grip",
                level=22,
                source=f"{HEROES_QUEST_WIKI_SOURCE}; {HEROES_QUEST_TROBERT_SOURCE}; {HEROES_QUEST_GRIP_NPC_SOURCE}",
                source_text=(
                    "The Phoenix Gang member attacks Grip from the window room after a Black Arm Gang partner "
                    "lures him; Grip's death enables that partner to recover Grip's key."
                ),
                npc_stats=(
                    ("hitpoints", 250),
                    ("attack", 18),
                    ("strength", 17),
                    ("defence", 18),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 30),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "slash_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=HEROES_QUEST_GRIP_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Pete's candlestick", 1),),
        source=(
            f"{HEROES_QUEST_BRIMHAVEN_SOURCE}; {HEROES_QUEST_GRIP_NPC_SOURCE}; "
            f"{HEROES_QUEST_WIKI_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=11,
        description="Give Pete's candlestick to Katrine for the Master Thieves' armband.",
        variant=HEROES_VARIANT_BLACK_ARM,
        required_routes=(HEROES_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Pete's candlestick", 1),),
        produced_inventory=(("Thieves' armband", 1),),
        auto_actions=("Give Pete's candlestick to Katrine",),
        source=f"{HEROES_QUEST_KATRINE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=11,
        description="Give Pete's candlestick to Straven for the Master Thieves' armband.",
        variant=HEROES_VARIANT_PHOENIX,
        required_routes=(HEROES_ROUTE_PHOENIX,),
        consumed_inventory=(("Pete's candlestick", 1),),
        produced_inventory=(("Thieves' armband", 1),),
        auto_actions=("Give Pete's candlestick to Straven",),
        source=f"{HEROES_QUEST_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=12,
        description="Give Achietties the cooked Lava eel, Master Thieves' armband, and Fire feather.",
        consumed_inventory=(("Lava eel", 1), ("Thieves' armband", 1), ("Fire feather", 1)),
        auto_actions=("Hand Achietties the Lava eel, Thieves' armband, and Fire feather",),
        source=f"{HEROES_QUEST_ACHIETTIES_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
)

QUEST = QuestDefinition(
        id=HEROES_QUEST_ID,
        display_name="Heroes' Quest",
        stages=13,
        point_reward=1,
        rewards=(),
        start_point="Speak with Achietties at the entrance to the Heroes' Guild in Burthorpe.",
        requirements=(
            "56 Quest Points",
            "Shield of Arrav",
            "Lost City",
            "Dragon Slayer",
            "Merlin's Crystal",
            "Druidic Ritual",
            "Cooking 53",
            "Fishing 53",
            "Herblore 25",
            "Defence 25",
            "Mining 50",
            (
                "Used during quest: Harralander potion (unf) x1, Fishing rod x1, Fishing bait x1, "
                "Pickaxe x1."
            ),
            (
                "Route choice: Phoenix Gang or Black Arm Gang from Shield of Arrav. "
                "Black Arm route uses black armour and Id papers; Phoenix route uses the secret panel and a "
                "contextual Black Arm Gang partner for the key, Grip lure, and candlestick handoff."
            ),
        ),
        required_items=(),
        combat=(
            "Ice Queen (level 111) for Ice gloves; Entranan Firebird (level 2) for Fire feather; "
            "Phoenix route: Grip (level 22). Ice Queen lair access may require the Dusty key route or an alternate shortcut."
        ),
        source=(
            f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ACHIETTIES_SOURCE}; "
            f"{HEROES_QUEST_PORT_SARIM_SOURCE}; {HEROES_QUEST_HERBLORE_SOURCE}; "
            f"{HEROES_QUEST_FISH_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; {HEROES_QUEST_COOKING_SOURCE}; "
            f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {HEROES_QUEST_BRIMHAVEN_SOURCE}; "
            f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_STRAVEN_SOURCE}; {HEROES_QUEST_TROBERT_SOURCE}; "
            f"{HEROES_QUEST_ALFONSO_SOURCE}; {HEROES_QUEST_CHARLIE_SOURCE}; {HEROES_QUEST_MANSION_DOOR_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {HEROES_QUEST_WIKI_SOURCE}"
        ),
        journal_stages=HEROES_QUEST_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Experienced",
        length="Medium to Long",
        timeline="Fifth Age",
        required_quest_points=56,
        required_quests=(
            QuestPrerequisite(SHIELD_OF_ARRAV_ID, "Shield of Arrav"),
            QuestPrerequisite(LOST_CITY_ID, "Lost City"),
            QuestPrerequisite(DRAGON_SLAYER_ID, "Dragon Slayer"),
            QuestPrerequisite(MERLINS_CRYSTAL_ID, "Merlin's Crystal"),
            QuestPrerequisite(DRUIDIC_RITUAL_ID, "Druidic Ritual"),
        ),
        required_skills=(
            QuestSkillRequirement("cooking", "Cooking", 53),
            QuestSkillRequirement("fishing", "Fishing", 53),
            QuestSkillRequirement("herblore", "Herblore", 25),
            QuestSkillRequirement("defense", "Defence", 25),
            QuestSkillRequirement("mining", "Mining", 50),
        ),
        xp_rewards=(
            QuestXpReward("attack", 3075),
            QuestXpReward("defense", 3075),
            QuestXpReward("strength", 3075),
            QuestXpReward("constitution", 3075),
            QuestXpReward("ranged", 2075),
            QuestXpReward("fishing", 2725),
            QuestXpReward("cooking", 2825),
            QuestXpReward("woodcutting", 1575),
            QuestXpReward("firemaking", 1575),
            QuestXpReward("smithing", 2257),
            QuestXpReward("mining", 2575),
            QuestXpReward("herblore", 1325),
        ),
        unlocks=(
            "Access to the Heroes' Guild",
            "Access to another Black Arm Gang hideout in Brimhaven if you are in the Black Arm Gang",
            "Access to the garden beside Scarface Pete's house if you are in the Phoenix Gang",
            "Ability to wield and buy Dragon battleaxe and Dragon mace from the Heroes' Guild weapon shop",
        ),
        stage_requirements=HEROES_QUEST_STAGE_REQUIREMENTS,
        choices=HEROES_QUEST_CHOICES,
    )

_REWARD_ITEM_FRAGMENT_0 = {
        "Blamish snail slime": {
            "category": "material",
            "source": f"{HEROES_QUEST_PORT_SARIM_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Harralander potion (unf)": {
            "category": "material",
            "source": f"{HEROES_QUEST_HERBLORE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Blamish oil": {
            "category": "material",
            "source": f"{HEROES_QUEST_HERBLORE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Oily fishing rod": {
            "category": "tool",
            "source": f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Raw lava eel": {
            "category": "fish",
            "source": f"{HEROES_QUEST_FISH_SOURCE}; {HEROES_QUEST_FISHING_SPOT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lava eel": {
            "category": "food",
            "source": f"{HEROES_QUEST_COOKING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENT_1 = {
        "Ice gloves": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_ICE_QUEEN_DUNGEON_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Fire feather": {
            "category": "material",
            "source": f"{HEROES_QUEST_DARKAN_SOURCE}; {HEROES_QUEST_ENTRANA_FIREBIRD_NPC_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Id papers": {
            "category": "material",
            "source": f"{HEROES_QUEST_TROBERT_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black full helm": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black platebody": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black platelegs": {
            "category": "equipment",
            "source": f"{HEROES_QUEST_MANSION_DOOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Pete's candlestick": {
            "category": "material",
            "source": f"{HEROES_QUEST_BRIMHAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Thieves' armband": {
            "category": "material",
            "source": f"{HEROES_QUEST_KATRINE_SOURCE}; {HEROES_QUEST_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0, _REWARD_ITEM_FRAGMENT_1,)

__all__ = (
    'HEROES_QUEST_STAGES', 'HEROES_QUEST_STAGE_REQUIREMENTS',
)
