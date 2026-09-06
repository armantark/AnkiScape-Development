from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

FIGHT_ARENA_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "Lady Servil asked me to rescue her husband and son from General Khazard's arena.",
        "I need a Khazard disguise before entering the jail.",
    ),
    _simple_stage(2, "I borrowed the Khazard helmet and armour and should wear them to enter the jail."),
    _simple_stage(3, "Jeremy says the bald, fat, lazy guard with a goatee keeps the cell keys."),
    _simple_stage(4, "The Khazard barman Angor sells Khali brew for 5 coins."),
    _simple_stage(5, "I have Khali brew and can offer it to the lazy guard."),
    _simple_stage(6, "The lazy guard is asleep. I can steal the Khazard cell keys."),
    _simple_stage(7, "I have the cell keys and can open Jeremy's cell to reach the arena."),
    _simple_stage(8, "Sir Servil is trapped in the arena with a Khazard ogre."),
    _simple_stage(9, "General Khazard sent a Khazard scorpion against me."),
    _simple_stage(10, "Bouncer is General Khazard's final mandatory arena beast."),
    _simple_stage(11, "General Khazard offered an optional fight. I can leave and return to Lady Servil."),
    _simple_stage(12, "Lady Servil rewarded me for rescuing her family.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=FIGHT_ARENA_ID,
        display_name="Fight Arena",
        stages=12,
        point_reward=2,
        rewards=(("Coins", 1000),),
        start_point="Talk to Lady Servil north of the Khazard fight arena town, south of Ardougne.",
        requirements=(
            "Used during quest: Coins x5.",
            "The Khazard helmet and armour are borrowed during the quest rather than required to start it.",
        ),
        required_items=(),
        combat=(
            "Mandatory arena fights: Khazard ogre (level 63), Khazard scorpion (level 44), and Bouncer (level 137). "
            "General Khazard is optional after Bouncer."
        ),
        source=(
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; "
            f"{DARKAN_FIGHT_ARENA_LADY_SOURCE}; {DARKAN_FIGHT_ARENA_JEREMY_SOURCE}; "
            f"{DARKAN_FIGHT_ARENA_LAZY_GUARD_SOURCE}; {DARKAN_FIGHT_ARENA_ANGOR_SOURCE}; "
            f"{SCAPE_2011_ITEM_IDENTITY_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}"
        ),
        journal_stages=FIGHT_ARENA_STAGES,
        release_date="2002-07-23",
        members=True,
        difficulty="Experienced",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("attack", 12175), QuestXpReward("thieving", 2175)),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    FIGHT_ARENA_ID: (
        _stage_req(
            1,
            "Borrow the Khazard disguise from the armour stand.",
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            produced_inventory=(("Khazard helmet", 1), ("Khazard armour", 1)),
        ),
        _stage_req(
            2,
            "Wear the Khazard helmet and armour to enter the jail.",
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Khazard helmet", 1), ("Khazard armour", 1)),
        ),
        _stage_req(
            3,
            "Talk to Jeremy and learn which lazy guard has the cell keys.",
            f"{DARKAN_FIGHT_ARENA_JEREMY_SOURCE}; {DARKAN_FIGHT_ARENA_SOURCE}",
            auto_actions=("Talk to Jeremy about the key holder",),
        ),
        _stage_req(
            4,
            "Buy a Khali brew from Angor for the lazy guard.",
            f"{DARKAN_FIGHT_ARENA_ANGOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Coins", 5),),
            produced_inventory=(("Khali brew", 1),),
        ),
        _stage_req(
            5,
            "Give the Khali brew to the lazy guard.",
            f"{DARKAN_FIGHT_ARENA_LAZY_GUARD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Khali brew", 1),),
        ),
        _stage_req(
            6,
            "Steal the Khazard cell keys from the sleeping lazy guard.",
            f"{DARKAN_FIGHT_ARENA_LAZY_GUARD_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            auto_actions=("Steal the Khazard cell keys from the lazy guard",),
            produced_inventory=(("Khazard cell keys", 1),),
        ),
        _stage_req(
            7,
            "Use the Khazard cell keys on Jeremy's cell to begin the arena sequence.",
            f"{DARKAN_FIGHT_ARENA_SOURCE}; {DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            required_tools=(("Khazard cell keys", 1),),
            auto_actions=("Use the Khazard cell keys on Jeremy's cell",),
        ),
        _stage_req(
            8,
            "Defeat the Khazard ogre threatening Sir Servil.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_KHAZARD_OGRE_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    FIGHT_ARENA_ID,
                    "khazard_ogre_63",
                    "Khazard ogre",
                    63,
                    f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_KHAZARD_OGRE_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
                    "Darkan's Fight Arena cutscene targets the Khazard ogre before Sir Servil is freed; the combatdef supplies hitpoints/max-hit only, so resolver stats remain incomplete.",
                    npc_stats=(("hitpoints", 600),),
                    npc_configs=(
                        ("max_hit", 1),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_FIGHT_ARENA_KHAZARD_OGRE_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            9,
            "Defeat General Khazard's Khazard scorpion.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_KHAZARD_SCORPION_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    FIGHT_ARENA_ID,
                    "khazard_scorpion_44",
                    "Khazard scorpion",
                    44,
                    (
                        f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; "
                        f"{DARKAN_FIGHT_ARENA_KHAZARD_SCORPION_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}"
                    ),
                    "Darkan's Fight Arena cutscene spawns the Khazard scorpion after the ogre; the combatdef supplies hitpoints/max-hit only, so resolver stats remain incomplete.",
                    npc_stats=(("hitpoints", 400),),
                    npc_configs=(
                        ("max_hit", 50),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_FIGHT_ARENA_KHAZARD_SCORPION_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            10,
            "Defeat Bouncer in the arena.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_BOUNCER_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    FIGHT_ARENA_ID,
                    "bouncer_137",
                    "Bouncer",
                    137,
                    f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_BOUNCER_NPC_SOURCE}; {FIGHT_ARENA_WIKI_SOURCE}",
                    "Darkan's Fight Arena cutscene requires Bouncer before the player may leave; General Khazard is optional afterward.",
                    npc_stats=(
                        ("hitpoints", 1160),
                        ("attack", 120),
                        ("strength", 120),
                        ("defence", 120),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 140),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=DARKAN_FIGHT_ARENA_BOUNCER_NPC_SOURCE,
                ),
            ),
        ),
        _stage_req(
            11,
            "Leave the arena and return to Lady Servil for the reward.",
            f"{DARKAN_FIGHT_ARENA_CUTSCENE_SOURCE}; {DARKAN_FIGHT_ARENA_LADY_SOURCE}",
            auto_actions=("Return to Lady Servil for the reward",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Khazard helmet": {
            "category": "equipment",
            "source": f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Khazard armour": {
            "category": "equipment",
            "source": f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Khali brew": {
            "category": "material",
            "source": f"{DARKAN_FIGHT_ARENA_ANGOR_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Khazard cell keys": {
            "category": "tool",
            "source": f"{DARKAN_FIGHT_ARENA_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'FIGHT_ARENA_STAGES',
)
