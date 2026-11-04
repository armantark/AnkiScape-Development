from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *
from ...witchs_house import (
    DIARY, TAKE_DIARY, READ_DIARY, ENTER_BASEMENT, TAKE_GLOVES, PASS_GATE,
    TAKE_MAGNET, TAKE_KEY, TAKE_BALL, ROUTE_SOURCE, DIARY_SOURCE, HANDLER_SOURCE, INSULATING_GLOVES,
)

WITCHS_HOUSE_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Harvey asked me to get his ball back. I need to search the potted plant outside the Witch's house."),
    _simple_stage(2, 'I found the front door key under a potted plant. I can use it to enter the house.'),
    _simple_stage(3, "I entered the Witch's house. There is a diary on the table."),
    _simple_stage(4, "Read the Witch's diary before continuing."),
    _simple_stage(5, "I read the Witch's diary. I should prepare gloves before entering the basement gate."),
    _simple_stage(6, 'I entered the basement. Wear insulating gloves before passing the electric gate.'),
    _simple_stage(7, 'I passed the electric gate wearing insulating gloves. Search the cupboard for the magnet.'),
    _simple_stage(8, 'I found the magnet. Use cheese on the mouse hole and attach the magnet to the mouse.'),
    _simple_stage(9, "The mouse mechanism opened the garden door. Avoid the witch's patrol."),
    _simple_stage(10, "I passed the witch's patrol. Search the fountain for the shed key."),
    _simple_stage(11, 'I found the backroom key. Use it to unlock the shed.'),
    _simple_stage(12, "I unlocked the shed. Defeat all four forms of the Witch's experiment."),
    _simple_stage(13, "All four experiment forms are defeated. Pick up Harvey's ball."),
    _simple_stage(14, "I picked up Harvey's ball. Return it to Harvey."),
    _simple_stage(15, 'Harvey got his ball back.', "Quest complete!"),
)

QUEST = QuestDefinition(
        id=WITCHS_HOUSE_ID,
        display_name="Witch's House",
        stages=15,
        point_reward=4,
        rewards=(),
        start_point="Talk to Harvey, the crying boy west of Falador.",
        requirements=(
            "Used during quest: Cheese x1 and worn insulating gloves.",
            "The diary, keys, magnet, and ball are found during the quest rather than required to start it.",
        ),
        required_items=(),
        combat=(
            "The Witch's experiment must be defeated through four forms: "
            "Skavid level 19, Spider level 30, Bear level 42, and Wolf level 53."
        ),
        source=(
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_BOY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; "
            f"{WITCHS_HOUSE_WITCH_SENTRY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}"
        ),
        journal_stages=WITCHS_HOUSE_STAGES,
        release_date="2002-02-27",
        members=True,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("constitution", 6325),),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    WITCHS_HOUSE_ID: (
        _stage_req(
            1,
            "Search the potted plant outside the Witch's house for the front door key.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}",
            produced_inventory=(("Door key", 1),),
        ),
        _stage_req(
            2,
            "Use the door key to enter the Witch's house.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}",
            required_tools=(("Door key", 1),),
            auto_actions=("Enter the Witch's house with the door key",),
        ),
        _stage_req(
            3,
            "Take the Witch's diary from the table inside the house.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            produced_inventory=((DIARY, 1),),
            auto_actions=(TAKE_DIARY,),
        ),
        _stage_req(
            4,
            "Read the Witch's diary.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            required_inventory=((DIARY, 1),),
            auto_actions=(READ_DIARY,),
        ),
        _stage_req(
            5,
            "Enter the basement and, if needed, search the boxes for leather gloves.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            required_actions=(READ_DIARY,),
            produced_inventory=(("Leather gloves", 1),),
            auto_actions=(ENTER_BASEMENT, TAKE_GLOVES),
        ),
        _stage_req(
            6,
            "Wear insulating gloves and pass the electric gate in the basement.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            required_actions=(READ_DIARY,),
            auto_actions=(PASS_GATE,),
            wear_slot="hands", wear_items=tuple(INSULATING_GLOVES),
        ),
        _stage_req(
            7,
            "Search the cupboard beyond the electric gate for the magnet.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            required_actions=(PASS_GATE,),
            produced_inventory=(("Magnet", 1),),
            auto_actions=(TAKE_MAGNET,),
        ),
        _stage_req(
            8,
            "Use cheese and the magnet to unlock the mouse-hole security mechanism.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            consumed_inventory=(("Cheese", 1),),
            required_tools=(("Magnet", 1),),
            auto_actions=("Use cheese on the mouse hole and attach the magnet to the mouse",),
        ),
        _stage_req(
            9,
            "Pass through the garden without being seen by the witch.",
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_WITCH_SENTRY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            auto_actions=("Avoid the witch's patrol through the house",),
        ),
        _stage_req(
            10,
            "Search the fountain in the garden for the backroom key.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            required_actions=(READ_DIARY,),
            produced_inventory=(("Backroom key", 1),),
            auto_actions=(TAKE_KEY,),
        ),
        _stage_req(
            11,
            "Use the backroom key to unlock the shed door.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {WITCHS_HOUSE_DIARY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            required_tools=(("Backroom key", 1),),
            required_actions=(READ_DIARY,),
            auto_actions=("Unlock the Witch's shed door with the backroom key",),
        ),
        _stage_req(
            12,
            "Defeat the Witch's experiment through all four forms before retrieving the ball.",
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_WIKI_SOURCE}",
            combat_encounters=(
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_first_form",
                    "Witch's experiment (Skavid form)",
                    19,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE}",
                    "Historical quest text says the experiment's first stage is a Skavid level 19; Darkan NPC id 897 supplies the Witch's experiment level 19 stats.",
                    npc_stats=(
                        ("hitpoints", 1130),
                        ("attack", 18),
                        ("strength", 10),
                        ("defence", 19),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 100),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_19_NPC_SOURCE,
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_second_form",
                    "Witch's experiment (Spider form)",
                    30,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE}",
                    "Historical quest text says the experiment's second stage is a Spider level 30; Darkan NPC id 898 supplies the Witch's experiment level 30 stats.",
                    npc_stats=(
                        ("hitpoints", 1225),
                        ("attack", 28),
                        ("strength", 20),
                        ("defence", 29),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 125),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "crush_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_30_NPC_SOURCE,
                    required_encounters=("witchs_house_witchs_experiment_first_form",),
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_third_form",
                    "Witch's experiment (Bear form)",
                    42,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE}",
                    "Historical quest text says the experiment's third stage is a Bear level 42; Darkan NPC id 899 supplies the Witch's experiment level 42 stats.",
                    npc_stats=(
                        ("hitpoints", 1325),
                        ("attack", 38),
                        ("strength", 30),
                        ("defence", 39),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 135),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "slash_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_42_NPC_SOURCE,
                    required_encounters=("witchs_house_witchs_experiment_second_form",),
                ),
                _combat(
                    WITCHS_HOUSE_ID,
                    "witchs_experiment_fourth_form",
                    "Witch's experiment (Wolf form)",
                    53,
                    f"{WITCHS_HOUSE_WIKI_SOURCE}; {WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE}",
                    "Historical quest text says the experiment's final stage is a Wolf level 53; Darkan NPC id 900 supplies the Witch's experiment level 53 stats.",
                    npc_stats=(
                        ("hitpoints", 1425),
                        ("attack", 48),
                        ("strength", 40),
                        ("defence", 49),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_configs=(
                        ("max_hit", 150),
                        ("attack_range", -1),
                        ("attack_style", "melee"),
                        ("attack_bonus", "stab_att"),
                        ("aggressiveness_type", "aggressive"),
                    ),
                    npc_stats_source=WITCHS_HOUSE_EXPERIMENT_53_NPC_SOURCE,
                    required_encounters=("witchs_house_witchs_experiment_third_form",),
                ),
            ),
        ),
        _stage_req(
            13,
            "Pick up Harvey's ball from the shed.",
            f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}; {ROUTE_SOURCE}; {HANDLER_SOURCE}",
            produced_inventory=(("Ball", 1),),
            auto_actions=(TAKE_BALL,),
        ),
        _stage_req(
            14,
            "Return the ball to Harvey.",
            f"{WITCHS_HOUSE_SOURCE}; {WITCHS_HOUSE_BOY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Ball", 1),),
            auto_actions=("Return the ball to Harvey",),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        DIARY: {
            "category": "tool",
            "source_item_id": 2408,
            "stackable": False,
            "tradeable": False,
            "source": DIARY_SOURCE,
        },
        "Door key": {
            "category": "tool",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Magnet": {
            "category": "tool",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Backroom key": {
            "category": "tool",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
        "Ball": {
            "category": "material",
            "source": f"{WITCHS_HOUSE_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'WITCHS_HOUSE_STAGES',
)
