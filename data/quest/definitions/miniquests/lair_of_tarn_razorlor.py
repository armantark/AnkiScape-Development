from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

LAIR_OF_TARN_RAZORLOR_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Odovacar the banker told me that Tarn Razorlor still haunts the",
        "abandoned mine west of Burgh de Rott. I should climb down into",
        "his lair and see what became of him.",
    ),
    _simple_stage(
        2,
        "I am inside Tarn's Lair. Odovacar keeps a bank at the end of the",
        "northern hall, behind two wall traps I will have to search out.",
    ),
    _simple_stage(
        3,
        "I reached Odovacar's bank. Beyond it the lair is a maze of floor",
        "traps, swinging logs and pillars I must jump between.",
    ),
    _simple_stage(
        4,
        "I crossed the trapped halls. The last pillar room is watched by two",
        "skeleton mages; past it a stairway leads down to Tarn's chamber.",
    ),
    _simple_stage(
        5,
        "Tarn transformed into a lashing green mutant and set two terror dogs",
        "on me.",
    ),
    _simple_stage(
        6,
        "The mutant fell, but Tarn rose again as a ghost. This form is the",
        "weaker of the two.",
    ),
    _simple_stage(
        7,
        "Tarn is dead and the room beyond his chamber has opened. His diary",
        "is on the table inside.",
    ),
    _simple_stage(
        8,
        "I took Tarn's diary from his bedroom. Reading it over a salve amulet",
        "would enchant the amulet against the undead.",
        "Miniquest complete!",
    ),
)


LAIR_OF_TARN_RAZORLOR_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    _stage_req(
        1,
        "Climb into the abandoned mine west of Burgh de Rott and follow the path north into Tarn's Lair.",
        f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {MINIQUEST_LIST_SOURCE}",
        auto_actions=(
            "Climb over the mine cart and crawl down the cart tunnel",
            "Follow the first level of the mine north to its end",
        ),
    ),
    _stage_req(
        2,
        "Search out the two wall traps on the northern hall and reach Odovacar's bank room.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Pass the floor traps east to the end of the entrance passage",
            "Disarm the southern and northern wall traps by searching them",
        ),
    ),
    _stage_req(
        3,
        "Take the D-S-T route through the floor traps to the western pillar room and drop the log swing.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Cross the six-trap room through Doorway S and the three-trap room through Doorway T",
            "Jump the southern pillars and search the flagstone to deactivate the log swing",
        ),
    ),
    _stage_req(
        4,
        "Time the pit room's walls, cross the second pillar room past two level 94 skeleton mages, and take Doorway U.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Time the shifting walls so the pit never takes you",
            "Zigzag the pillars while the skeleton mages fire, then descend Doorway U",
        ),
    ),
    _stage_req(
        5,
        "Defeat Tarn's mutant form with two level 110 terror dogs loose in the chamber.",
        (
            f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TERROR_DOG_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_MUTANT_TARN_DARKAN_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TERROR_DOG_DARKAN_SOURCE}"
        ),
        combat_encounters=(
            _combat(
                LAIR_OF_TARN_RAZORLOR_ID,
                "mutant_tarn",
                "Mutant tarn",
                69,
                (
                    f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
                    f"{LAIR_OF_TARN_RAZORLOR_MUTANT_TARN_DARKAN_SOURCE}"
                ),
                (
                    "The cutscene turns Tarn into a level 69 mutant with 650 life points, attacks "
                    "at speed 5 and an approximate maximum hit of 190. The infobox lists melee and "
                    "magic, but the same revision's strategy section says he \"attacks solely with "
                    "melee if approached\" — which is every AnkiScape battle — so this fight is "
                    "melee, exactly as Darkan's file has it. Two level 110 terror dogs enter with "
                    "him. A quest stage resolves one attacker, so they stay narration on the same "
                    "terms as Bork's legions; the source says Tarn is the only monster that must "
                    "die, and the period lets a player manoeuvre the dogs behind him to escape "
                    "them entirely."
                ),
                # PLACEHOLDER(lair_of_tarn_razorlor.mutant_tarn_stat_block): Darkan's
                # mutant file is a "nostats" row with every combat level zeroed, so
                # the ghost form's block stands in for the mutant's. The two forms
                # share a level, life-point total, maximum hit and attack speed in the
                # period record, which is why the substitution is the same body twice.
                npc_stats=(
                    ("hitpoints", 650),
                    ("attack", 40),
                    ("strength", 80),
                    ("defence", 40),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 190),
                    ("attack_speed", 5),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                    # Slayer 40 is the period gate and it is already a quest requirement,
                    # so the enemy level must not add a second, unsourced one.
                    ("minimum_player_combat", 1),
                ),
                npc_stats_source=(
                    f"Period level, life points, maximum hit and attack speed from "
                    f"{LAIR_OF_TARN_RAZORLOR_MUTANT_TARN_DARKAN_SOURCE}, which states no combat "
                    f"levels; the block stands in from the ghost form's "
                    f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
                ),
            ),
        ),
    ),
    _stage_req(
        6,
        "Defeat the ghost Tarn rises as when his mutant form falls.",
        (
            f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
        ),
        combat_encounters=(
            _combat(
                LAIR_OF_TARN_RAZORLOR_ID,
                "tarn_ghost",
                "Tarn",
                69,
                (
                    f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}; "
                    f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
                ),
                (
                    "Tarn's ghost keeps level 69, 650 life points and the approximate 190 maximum "
                    "hit, but attacks with melee alone, which is why the source calls it the easier "
                    "form. Poison carried over from the mutant form persists."
                ),
                npc_stats=(
                    ("hitpoints", 650),
                    ("attack", 40),
                    ("strength", 80),
                    ("defence", 40),
                    ("magic", 1),
                    ("ranged", 1),
                ),
                npc_configs=(
                    ("max_hit", 190),
                    ("attack_speed", 5),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                    ("minimum_player_combat", 1),
                ),
                npc_stats_source=(
                    f"Period level, life points, maximum hit and attack speed; combat levels from "
                    f"{LAIR_OF_TARN_RAZORLOR_TARN_DARKAN_SOURCE}"
                ),
            ),
        ),
    ),
    _stage_req(
        7,
        "Take Tarn's diary from the table in the room his death opens.",
        LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE,
        auto_actions=(
            "Enter Tarn's bedroom once the wall opens",
            "Take Tarn's diary from the table",
        ),
    ),
)

QUEST = QuestDefinition(
        id=LAIR_OF_TARN_RAZORLOR_ID,
        display_name="The Lair of Tarn Razorlor",
        stages=len(LAIR_OF_TARN_RAZORLOR_STAGES),
        point_reward=0,
        rewards=(),
        start_point=(
            "Talk to Odovacar the banker in the abandoned mine west of Burgh de Rott."
        ),
        requirements=("Haunted Mine", "Slayer 40"),
        required_items=(),
        combat="Tarn Razorlor: a level 69 mutant form, then a level 69 ghost form.",
        source=(
            f"{LAIR_OF_TARN_RAZORLOR_WIKI_SOURCE}; {MINIQUEST_LIST_SOURCE}; "
            f"{LAIR_OF_TARN_RAZORLOR_TARN_SOURCE}"
        ),
        journal_stages=LAIR_OF_TARN_RAZORLOR_STAGES,
        release_date="2007-01-22",
        members=True,
        # PLACEHOLDER(lair_of_tarn_razorlor.difficulty_label): the pinned page
        # carries no quest details block, so it states neither a difficulty word
        # nor the numeric grade its sibling page carries.
        difficulty="Special",
        # PLACEHOLDER(lair_of_tarn_razorlor.length_label): the same missing block
        # is the only place a length would have been stated.
        length="Short",
        timeline="Fifth Age",
        release_order=9999,
        required_quests=(QuestPrerequisite(HAUNTED_MINE_ID, "Haunted Mine"),),
        required_skills=(QuestSkillRequirement("slayer", "Slayer", 40),),
        xp_rewards=(QuestXpReward("slayer", 5000),),
        unlocks=(
            "Tarn's diary",
            "Ability to enchant a salve amulet into a Salve amulet (e)",
        ),
        stage_requirements=LAIR_OF_TARN_RAZORLOR_STAGE_REQUIREMENTS,
        miniquest=True,
    )

__all__ = (
    'LAIR_OF_TARN_RAZORLOR_STAGES', 'LAIR_OF_TARN_RAZORLOR_STAGE_REQUIREMENTS',
)
