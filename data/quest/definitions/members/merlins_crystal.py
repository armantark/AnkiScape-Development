from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

MERLINS_CRYSTAL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "King Arthur asked me to find out how Merlin was trapped.",
        "The knights of the round table may know how to reach Morgan Le Faye's stronghold and free Merlin.",
    ),
    _simple_stage(
        2,
        "Sir Lancelot says Morgan Le Faye's stronghold can be entered by sea.",
        "I should hide in a delivery crate near the Catherby candle-maker.",
    ),
    _simple_stage(
        3,
        "I reached Keep Le Faye.",
        "Sir Mordred guards the stronghold, and Morgan may reveal how to break Merlin's crystal if he is defeated.",
    ),
    _simple_stage(
        4,
        "Morgan Le Faye told me the ritual needs bat bones, a lit black candle, the binding words, and Excalibur.",
        "I need wax for the candle-maker before I can get a black candle.",
    ),
    _simple_stage(
        5,
        "The candle-maker made a black candle.",
        "The Lady of the Lake has Excalibur and wants me to prove I am worthy.",
    ),
    _simple_stage(
        6,
        "The Lady of the Lake gave me Excalibur after I helped the beggar.",
        "I must summon and bind Thrantax at the chaos altar with bat bones and a lit black candle.",
    ),
    _simple_stage(
        7,
        "Thrantax is bound.",
        "Merlin's crystal can now be shattered with Excalibur.",
    ),
    _simple_stage(8, "I freed Merlin and King Arthur made me a knight of the round table.", "Quest complete!"),
)


MERLINS_CRYSTAL_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    QuestStageRequirement(
        stage=1,
        description="Investigate Merlin's crystal with the relevant round-table knights.",
        auto_actions=("Complete the round-table investigation with Sir Gawain, Sir Lucan, and Sir Lancelot",),
        source=(
            f"{MERLINS_CRYSTAL_SOURCE}; {MERLINS_CRYSTAL_SIR_GAWAIN_SOURCE}; "
            f"{MERLINS_CRYSTAL_SIR_LUCAN_SOURCE}; {MERLINS_CRYSTAL_SIR_LANCELOT_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=2,
        description="Hide in the Catherby delivery crate to enter Keep Le Faye.",
        auto_actions=("Reach Keep Le Faye through the Catherby crate delivery",),
        source=f"{MERLINS_CRYSTAL_KEEP_SOURCE}; {MERLINS_CRYSTAL_CRATE_SCENE_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Defeat Sir Mordred in Keep Le Faye.",
        combat_encounters=(
            QuestCombatEncounter(
                encounter_id=f"{MERLINS_CRYSTAL_ID}_sir_mordred_39",
                display_name="Sir Mordred",
                level=39,
                source=f"{MERLINS_CRYSTAL_KEEP_SOURCE}; {MERLINS_CRYSTAL_MORDRED_SOURCE}; {MERLINS_CRYSTAL_MORDRED_NPC_SOURCE}",
                source_text="Sir Mordred is attacked in Keep Le Faye and Morgan appears after he is defeated.",
                npc_stats=(
                    ("hitpoints", 500),
                    ("attack", 33),
                    ("strength", 33),
                    ("defence", 33),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 57),
                    ("attack_range", -1),
                    ("attack_style", "melee"),
                    ("attack_bonus", "slash_att"),
                    ("aggressiveness_type", "aggressive"),
                ),
                npc_stats_source=MERLINS_CRYSTAL_MORDRED_NPC_SOURCE,
            ),
        ),
        source=(
            f"{MERLINS_CRYSTAL_KEEP_SOURCE}; {MERLINS_CRYSTAL_MORDRED_SOURCE}; "
            f"{MERLINS_CRYSTAL_MORGAN_SOURCE}; {MERLINS_CRYSTAL_MORDRED_NPC_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=4,
        description="Question Morgan Le Faye and collect wax safely from a beehive.",
        required_inventory=(("Bucket", 1), ("Insect repellent", 1)),
        consumed_inventory=(("Bucket", 1),),
        produced_inventory=(("Bucket of wax", 1),),
        auto_actions=("Question Morgan Le Faye about Excalibur and the binding words",),
        source=(
            f"{MERLINS_CRYSTAL_MORGAN_SOURCE}; {MERLINS_CRYSTAL_BEEHIVE_SOURCE}; {MERLINS_CRYSTAL_BEEKEEPER_SOURCE}; "
            f"{MERLINS_CRYSTAL_2011SCAPE_CATHERBY_SPAWN_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}"
        ),
    ),
    QuestStageRequirement(
        stage=5,
        description="Exchange the bucket of wax for a black candle.",
        consumed_inventory=(("Bucket of wax", 1),),
        produced_inventory=(("Black candle", 1),),
        auto_actions=("Ask the Catherby candle-maker for a black candle",),
        source=f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=6,
        description="Pass the Lady of the Lake's Port Sarim test and receive Excalibur.",
        consumed_inventory=(("Bread", 1),),
        produced_inventory=(("Excalibur", 1),),
        auto_actions=("Accept the Lady of the Lake's test in Taverley", "Give bread to the Port Sarim beggar"),
        source=f"{MERLINS_CRYSTAL_LADY_SOURCE}; {MERLINS_CRYSTAL_BEGGAR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
    ),
    QuestStageRequirement(
        stage=7,
        description="Bind Thrantax, shatter Merlin's crystal with Excalibur, and report to King Arthur.",
        required_inventory=(("Bat bones", 1), ("Black candle", 1)),
        consumed_inventory=(("Bat bones", 1), ("Black candle", 1)),
        produced_inventory=(("Lit black candle", 1),),
        required_tools=(("Tinderbox", 1), ("Excalibur", 1)),
        auto_actions=(
            "Read the chaos altar inscription",
            "Bind Thrantax with Snarthon Candtrick Termanto",
            "Shatter Merlin's crystal with Excalibur",
            "Report Merlin's freedom to King Arthur",
        ),
        source=(
            f"{MERLINS_CRYSTAL_SOURCE}; {MERLINS_CRYSTAL_RITUAL_SCENE_SOURCE}; "
            f"{MERLINS_CRYSTAL_THRANTAX_SOURCE}; {MERLINS_CRYSTAL_THRANTAX_NPC_SOURCE}; "
            f"{MERLINS_CRYSTAL_KING_ARTHUR_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {MERLINS_CRYSTAL_WIKI_SOURCE}"
        ),
    ),
)

QUEST = QuestDefinition(
        id=MERLINS_CRYSTAL_ID,
        display_name="Merlin's Crystal",
        stage_count=8,
        point_reward=6,
        rewards=(),
        start_point="Talk to King Arthur in Camelot.",
        requirements=(
            "Used during quest: Bucket x1, Insect repellent x1, Bucket of wax x1, Black candle x1, "
            "Bread x1, Bat bones x1, Tinderbox x1, Excalibur x1"
        ),
        required_items=(),
        combat="Sir Mordred (level 39) must be defeated; Thrantax is bound through ritual dialogue rather than killed.",
        source=(
            f"{MERLINS_CRYSTAL_SOURCE}; {MERLINS_CRYSTAL_KING_ARTHUR_SOURCE}; "
            f"{MERLINS_CRYSTAL_SIR_GAWAIN_SOURCE}; {MERLINS_CRYSTAL_SIR_LUCAN_SOURCE}; "
            f"{MERLINS_CRYSTAL_SIR_LANCELOT_SOURCE}; {MERLINS_CRYSTAL_KEEP_SOURCE}; "
            f"{MERLINS_CRYSTAL_CRATE_SCENE_SOURCE}; {MERLINS_CRYSTAL_MORDRED_SOURCE}; "
            f"{MERLINS_CRYSTAL_MORGAN_SOURCE}; {MERLINS_CRYSTAL_LADY_SOURCE}; "
            f"{MERLINS_CRYSTAL_BEGGAR_SOURCE}; {MERLINS_CRYSTAL_RITUAL_SCENE_SOURCE}; "
            f"{MERLINS_CRYSTAL_THRANTAX_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {MERLINS_CRYSTAL_WIKI_SOURCE}"
        ),
        journal_stages=MERLINS_CRYSTAL_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Intermediate",
        length="Medium",
        timeline="Fifth Age",
        unlocks=("Excalibur", "Honorary Knight of the Round Table"),
        stage_requirements=MERLINS_CRYSTAL_STAGE_REQUIREMENTS,
    )

_REWARD_ITEM_FRAGMENT_0 = {
        "Insect repellent": {
            "category": "tool",
            "source": (
                f"{MERLINS_CRYSTAL_BEEKEEPER_SOURCE}; {MERLINS_CRYSTAL_2011SCAPE_CATHERBY_SPAWN_SOURCE}; "
                f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}"
            ),
        },
        "Bucket of wax": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_BEEHIVE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Black candle": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Lit black candle": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Excalibur": {
            "category": "equipment",
            "source": f"{MERLINS_CRYSTAL_LADY_SOURCE}; {MERLINS_CRYSTAL_BEGGAR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENT_1 = {
        "Bat bones": {
            "category": "material",
            "source": f"{MERLINS_CRYSTAL_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0, _REWARD_ITEM_FRAGMENT_1,)

__all__ = (
    'MERLINS_CRYSTAL_STAGES', 'MERLINS_CRYSTAL_STAGE_REQUIREMENTS',
)
