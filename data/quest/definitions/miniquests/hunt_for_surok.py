from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

# ---- Miniquests -----------------------------------------------------------
# The pre-EOC quest catalog is built from the wiki's quest release list, which
# does not carry miniquests. These rows are written by hand from the pinned
# period record and join the same ledger, storage and unlock engine; only the
# Quests tab groups them apart. Miniquests award no quest points, which
# `Miniquests` oldid 6020341 states outright.

HUNT_FOR_SUROK_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I can start this miniquest by speaking to Surok after mining the",
        "statue of Saradomin to gain access to the Tunnels of Chaos.",
    ),
    _simple_stage(2, "I confronted Surok outside the statue and he fled into the tunnels beneath."),
    _simple_stage(
        3,
        "I found Surok fleeing from the Tunnels of Chaos and into a portal",
        "leading into the Chaos Tunnels.",
    ),
    _simple_stage(4, "I found Surok again near the fire giants but he fled off to the south."),
    _simple_stage(
        5,
        "I found Surok again near the skeletons next to the moss giant room",
        "but he got away again fleeing to the west.",
    ),
    _simple_stage(
        6,
        "I managed to defeat Bork but Surok managed to escape somewhere unknown.",
        "Miniquest complete!",
    ),
)


HUNT_FOR_SUROK_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    _stage_req(
        1,
        "Excavate the statue of Saradomin and confront Surok, who flees into the tunnel below.",
        f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_DARKAN_SOURCE}",
        required_tools=(("Pickaxe", 1),),
        auto_actions=(
            "Ask Anna Jones to let you at the statue, then excavate it with a pickaxe",
            "Attempt to arrest Surok and watch him slip into the Tunnel of Chaos",
        ),
    ),
    _stage_req(
        2,
        "Follow Surok through the Tunnel of Chaos, past Dakh'thoulan Aegis, into the Chaos Tunnels.",
        f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_DARKAN_SOURCE}",
        auto_actions=(
            "Enter the opening under the statue and head north through the Tunnel of Chaos",
            "Take the footprinted portal in Dakh'thoulan Aegis's room",
        ),
    ),
    _stage_req(
        3,
        "Catch Surok in the red spider room, where he kills two fire giants outright, and follow him south.",
        HUNT_FOR_SUROK_WIKI_SOURCE,
        auto_actions=(
            "Cross the multi-combat caverns by their footprinted portals",
            "Watch Surok destroy two fire giants and take the southern portal after him",
        ),
    ),
    _stage_req(
        4,
        "Catch Surok in the skeleton room and get past the two wolves he summons.",
        HUNT_FOR_SUROK_WIKI_SOURCE,
        auto_actions=(
            "Confront Surok among the skeletons beside the moss giant room",
            "Run past the two summoned wolves to the western portal",
        ),
    ),
    _stage_req(
        5,
        "Enter the last portal in the Dagannoth chamber and defeat Bork.",
        (
            f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_BORK_SOURCE}; "
            f"{HUNT_FOR_SUROK_BORK_DARKAN_SOURCE}"
        ),
        auto_actions=(
            "Take the western footprinted portal out of the Dagannoth chamber",
            "Grab Bork's drops and leave before the cave collapses",
        ),
        combat_encounters=(
            _combat(
                HUNT_FOR_SUROK_ID,
                "bork",
                "Bork",
                267,
                (
                    f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {HUNT_FOR_SUROK_BORK_SOURCE}; "
                    f"{HUNT_FOR_SUROK_BORK_DARKAN_SOURCE}; {HUNT_FOR_SUROK_BORK_HANDLER_SOURCE}"
                ),
                (
                    "Bork is a level 267 aggressive Ork immune to poison, with 3,000 life points, "
                    "crush attacks at speed 6 and a maximum hit of 254. At 2,000 life points he "
                    "calls three to nine level 70 orks of the Ork legion, and Surok bombards the "
                    "fight for up to 350 every fifteen seconds. A quest stage resolves one "
                    "attacker, so both pressures stay narration here; the walkthrough tells the "
                    "player to ignore the legions, and the repeatable Bork context is where every "
                    "attacker in the room is fought review by review."
                ),
                # PLACEHOLDER(dominion_tower.unsourced_boss_stat_blocks): Darkan's
                # Bork row is a "nostats" file whose combat levels are all zero, so
                # the core stats use the registered conversion exactly — 72% of the
                # combat level capped at 99, in all four stats. Copying the composite
                # level 267 straight into the stats would make him unhittable and
                # unsurvivable.
                npc_stats=(
                    ("hitpoints", 3000),
                    ("attack", 99),
                    ("strength", 99),
                    ("defence", 99),
                    ("magic", 99),
                ),
                npc_configs=(
                    ("max_hit", 254),
                    ("attack_speed", 6),
                    ("attack_style", "melee"),
                    ("attack_bonus", "crush_att"),
                    ("aggressiveness_type", "aggressive"),
                    # `Bork` oldid 6565904 prints `immune to poison = Yes`, and
                    # Darkan's `Bork.processEntity()` resets poison every tick.
                    ("poison_immune", True),
                    # The period states no player combat requirement for Bork — his own
                    # Slayer requirement is level 1 — so the miniquest gate is the only
                    # gate, and the enemy level must not become an invented one.
                    ("minimum_player_combat", 1),
                ),
                npc_stats_source=(
                    "Period life points, maximum hit, attack speed and crush style, matched by "
                    "Darkan's combat definition; hidden combat stats use the settled "
                    "72%-of-combat-level conversion, capped at 99"
                ),
            ),
        ),
    ),
)

QUEST = QuestDefinition(
        id=HUNT_FOR_SUROK_ID,
        display_name="The Hunt for Surok",
        stage_count=len(HUNT_FOR_SUROK_STAGES),
        point_reward=0,
        rewards=(),
        start_point="Speak to Surok by the statue of Saradomin, east of Varrock.",
        requirements=("What Lies Below", "Mining 42"),
        required_items=(),
        combat="Bork: level 267, 3,000 life points, maximum hit 254.",
        source=(
            f"{HUNT_FOR_SUROK_WIKI_SOURCE}; {MINIQUEST_LIST_SOURCE}; "
            f"{HUNT_FOR_SUROK_DARKAN_SOURCE}; {HUNT_FOR_SUROK_MINIQUEST_ENUM_SOURCE}"
        ),
        journal_stages=HUNT_FOR_SUROK_STAGES,
        release_date="2008-03-04",
        members=True,
        # PLACEHOLDER(hunt_for_surok.difficulty_label): the pinned page's quest
        # details block carries `wdifficulty=4` and no difficulty word, and the
        # miniquest list carries no difficulty column at all.
        difficulty="Special",
        length="Short to Medium",
        timeline="Fifth Age",
        # The release list the catalog is built from carries no miniquests, so
        # they take the catalog's own unknown-order value and sort last.
        release_order=9999,
        required_quests=(QuestPrerequisite(WHAT_LIES_BELOW_ID, "What Lies Below"),),
        # What Lies Below already demands Mining 42, so this row can never be the
        # binding gate. It is kept because it is the miniquest's own stated
        # requirement and stage 1 spends it on the statue; the prerequisite quest
        # is a separate fact that happens to cover it today. Its unannotated
        # sibling Slayer 44 is dropped instead — see the source audit, which
        # records both readings.
        required_skills=(QuestSkillRequirement("mining", "Mining", 42),),
        xp_rewards=(QuestXpReward("slayer", 5000),),
        unlocks=(
            "Ability to fight Bork in the Chaos Tunnels once per day",
            "Ability to wear Dagon'hai robes",
        ),
        stage_requirements=HUNT_FOR_SUROK_STAGE_REQUIREMENTS,
        miniquest=True,
    )

__all__ = (
    'HUNT_FOR_SUROK_STAGES', 'HUNT_FOR_SUROK_STAGE_REQUIREMENTS',
)
