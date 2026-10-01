from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

SHIELD_OF_ARRAV_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Reldo says the Shield of Arrav book in the Varrock palace library explains where to begin.",
    ),
    _simple_stage(
        2,
        "I read about the Shield of Arrav and should ask Reldo where the Phoenix Gang is hiding.",
    ),
    _simple_stage(
        3,
        "Reldo sent me to Baraek at Varrock market for information about the Phoenix Gang.",
    ),
    _simple_stage(
        4,
        "Baraek revealed the Phoenix hideout after I bribed him.",
        "I must choose whether to join the Phoenix Gang or the Black Arm Gang.",
    ),
    _simple_stage(
        5,
        "My chosen gang needs proof of loyalty.",
        "The Phoenix route needs Jonny the beard's intelligence report; the Black Arm route needs two Phoenix crossbows.",
    ),
    _simple_stage(
        6,
        "I have the proof item for my chosen gang and should hand it in.",
    ),
    _simple_stage(
        7,
        "I joined a gang and can retrieve that gang's half of the shield.",
    ),
    _simple_stage(
        8,
        "I found a shield half and should show it to King Roald.",
    ),
    _simple_stage(
        9,
        "King Roald sent me to Curator Haig Halen to authenticate the shield half.",
    ),
    _simple_stage(
        10,
        "The curator made duplicate half certificates.",
        "My route contact can trade a duplicate half certificate so I can make the full certificate.",
    ),
    _simple_stage(
        11,
        "I have the full certificate and should give it to King Roald.",
    ),
    _simple_stage(12, "King Roald accepted the certificate and paid the reward.", "Quest complete!"),
)


SHIELD_OF_ARRAV_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Find and read the Shield of Arrav book in Reldo's library.",
        auto_actions=("Find and read the Shield of Arrav book",),
        produced_inventory=(("Shield of Arrav book", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_BOOK_SOURCE}; {SCAPE_2011_VARROCK_RELDO_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=2,
        description="Ask Reldo where to find the Phoenix Gang.",
        auto_actions=("Ask Reldo about the Phoenix Gang",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_RELDO_SOURCE}; {SCAPE_2011_VARROCK_RELDO_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Bribe Baraek for the Phoenix hideout location.",
        consumed_inventory=(("Coins", 20),),
        auto_actions=("Bribe Baraek for the Phoenix hideout",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_BARAEK_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Choose the Phoenix Gang route with Straven.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        auto_actions=("Ask Straven for the Phoenix loyalty task",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Choose the Black Arm Gang route with Charlie and Katrine.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        auto_actions=("Ask Charlie and Katrine for the Black Arm loyalty task",),
        source=(
            f"{DARKAN_SHIELD_OF_ARRAV_CHARLIE_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; "
            f"{SHIELD_OF_ARRAV_WIKI_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=5,
        description="Kill Jonny the beard and take his intelligence report.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{SHIELD_OF_ARRAV_ID}_jonny_the_beard_2",
                display_name="Jonny the beard",
                level=2,
                source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_DROPS_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
                source_text="Jonny the beard drops the intelligence report needed to prove Phoenix Gang loyalty.",
                npc_stats=(
                    ("hitpoints", 80),
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
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=DARKAN_SHIELD_OF_ARRAV_JONNY_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Intel report", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_DROPS_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Your Phoenix contact gets you into the weapon store; defeat the Weaponsmaster and steal two Phoenix crossbows.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{SHIELD_OF_ARRAV_ID}_weaponsmaster_23",
                display_name="Weaponsmaster",
                level=23,
                source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_WEAPONSMASTER_NPC_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}",
                source_text="The weapon store is guarded by the Weaponsmaster before the Black Arm proof crossbows can be taken.",
                npc_stats=(
                    ("hitpoints", 200),
                    ("attack", 21),
                    ("strength", 21),
                    ("defence", 21),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 50),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "passive"),
                ),
                npc_stats_source=DARKAN_SHIELD_OF_ARRAV_WEAPONSMASTER_NPC_SOURCE,
            ),
        ),
        produced_inventory=(("Weapon store key", 1), ("Phoenix crossbow", 2),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_WEAPONSMASTER_NPC_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Hand Straven Jonny's intelligence report to join the Phoenix Gang.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        consumed_inventory=(("Intel report", 1),),
        produced_inventory=(("Weapon store key", 1),),
        auto_actions=("Hand Straven Jonny's intelligence report",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Hand Katrine two Phoenix crossbows to join the Black Arm Gang.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Phoenix crossbow", 2),),
        auto_actions=("Hand Katrine two Phoenix crossbows",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Search the Phoenix Gang chest for the right shield half.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        auto_actions=("Search the Phoenix Gang shield chest",),
        produced_inventory=(("Broken shield (Phoenix half)", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Search the Black Arm Gang cupboard for the left shield half.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        auto_actions=("Search the Black Arm Gang cupboard",),
        produced_inventory=(("Broken shield (Black Arm half)", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Show King Roald the Phoenix shield half.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        required_inventory=(("Broken shield (Phoenix half)", 1),),
        auto_actions=("Show King Roald the Phoenix shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=8,
        description="Show King Roald the Black Arm shield half.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        required_inventory=(("Broken shield (Black Arm half)", 1),),
        auto_actions=("Show King Roald the Black Arm shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Have Curator Haig Halen authenticate the Phoenix shield half.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        consumed_inventory=(("Broken shield (Phoenix half)", 1),),
        produced_inventory=(("Half certificate (Phoenix)", 2),),
        auto_actions=("Have Curator Haig Halen authenticate the Phoenix shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=9,
        description="Have Curator Haig Halen authenticate the Black Arm shield half.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Broken shield (Black Arm half)", 1),),
        produced_inventory=(("Half certificate (Black Arm)", 2),),
        auto_actions=("Have Curator Haig Halen authenticate the Black Arm shield half",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Trade one duplicate Phoenix half certificate through your Black Arm contact and combine the certificate.",
        variant=SHIELD_VARIANT_PHOENIX,
        required_routes=(SHIELD_ROUTE_PHOENIX,),
        consumed_inventory=(("Half certificate (Phoenix)", 1),),
        produced_inventory=(("Certificate", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=10,
        description="Trade one duplicate Black Arm half certificate through your Phoenix contact and combine the certificate.",
        variant=SHIELD_VARIANT_BLACK_ARM,
        required_routes=(SHIELD_ROUTE_BLACK_ARM,),
        consumed_inventory=(("Half certificate (Black Arm)", 1),),
        produced_inventory=(("Certificate", 1),),
        source=f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=11,
        description="Give King Roald the full certificate to claim the reward.",
        consumed_inventory=(("Certificate", 1),),
        auto_actions=("Claim the Shield of Arrav reward from King Roald",),
        source=f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_SOURCE}",
    ),
)

QUEST = QuestDefinition(
        id=SHIELD_OF_ARRAV_ID,
        display_name="Shield of Arrav",
        stage_count=12,
        point_reward=1,
        rewards=(("Coins", 600),),
        start_point="Talk to Reldo in the Varrock palace library.",
        requirements=(
            "Used during quest: Coins x20; your route contact supplies the opposite certificate half.",
            f"Route choice: {SHIELD_ROUTE_PHOENIX} or {SHIELD_ROUTE_BLACK_ARM}.",
            "Black Arm route uses a contextual Phoenix contact for the weapon store.",
        ),
        required_items=(),
        combat=(
            "Phoenix route: Jonny the beard (level 2). "
            "Black Arm route: Weaponsmaster (level 23) guards the Phoenix weapon store."
        ),
        source=(
            f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_RELDO_SOURCE}; "
            f"{DARKAN_SHIELD_OF_ARRAV_BARAEK_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; "
            f"{DARKAN_SHIELD_OF_ARRAV_KATRINE_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; "
            f"{DARKAN_SHIELD_OF_ARRAV_KING_SOURCE}; {SCAPE_2011_VARROCK_RELDO_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {SHIELD_OF_ARRAV_WIKI_SOURCE}"
        ),
        journal_stages=SHIELD_OF_ARRAV_STAGES,
        release_date="2001-01-04",
        members=False,
        difficulty="Novice",
        length="Medium",
        timeline="Fifth Age",
        stage_requirements=SHIELD_OF_ARRAV_STAGE_REQUIREMENTS,
        choices=SHIELD_OF_ARRAV_CHOICES,
    )

_REWARD_ITEM_FRAGMENT_0 = {
        "Shield of Arrav book": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_BOOK_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Intel report": {
            "category": "material",
            "source": (
                f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {DARKAN_SHIELD_OF_ARRAV_JONNY_DROPS_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
        },
        "Weapon store key": {
            "category": "tool",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_STRAVEN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Phoenix crossbow": {
            "category": "equipment",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Broken shield (Phoenix half)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Broken shield (Black Arm half)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Half certificate (Phoenix)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Half certificate (Black Arm)": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_CURATOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Certificate": {
            "category": "material",
            "source": f"{DARKAN_SHIELD_OF_ARRAV_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'SHIELD_OF_ARRAV_STAGES', 'SHIELD_OF_ARRAV_STAGE_REQUIREMENTS',
)
