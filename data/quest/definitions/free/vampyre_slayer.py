from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

VAMPYRE_SLAYER_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "Morgan asked me to find Dr Harlow at the Blue Moon Inn in Varrock."),
    _simple_stage(2, "Dr Harlow agreed to help, but he wants a beer first."),
    _simple_stage(3, "Dr Harlow gave me a stake and stake hammer for Count Draynor."),
    _simple_stage(4, "Count Draynor is dead. I should tell Morgan that Draynor is safe."),
    _simple_stage(5, "Morgan rewarded me for slaying Count Draynor.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=VAMPYRE_SLAYER_ID,
        display_name="Vampyre Slayer",
        stage_count=5,
        point_reward=3,
        rewards=(),
        start_point="Speak to Morgan in Draynor Village.",
        requirements=(),
        required_items=(),
        combat="Count Draynor (level 37); garlic is optional and weakens him.",
        source=(
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MORGAN_SOURCE_PATH}; "
            f"{VAMPYRE_SLAYER_DR_HARLOW_SOURCE_PATH}; {VAMPYRE_SLAYER_MANOR_SOURCE_PATH}; "
            f"{COUNT_DRAYNOR_NPC_SOURCE_PATH}"
        ),
        journal_stages=VAMPYRE_SLAYER_STAGES,
        release_date="2001-01-28",
        members=False,
        difficulty="Novice",
        length="Short",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("attack", 4825),),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    VAMPYRE_SLAYER_ID: (
        _stage_req(
            1,
            "Speak to Dr Harlow at the Blue Moon Inn.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_DR_HARLOW_SOURCE_PATH}",
            auto_actions=("Speak to Dr Harlow at the Blue Moon Inn",),
        ),
        _stage_req(
            2,
            "Buy Dr Harlow a beer at the Blue Moon Inn and receive vampyre-slaying gear.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_DR_HARLOW_SOURCE_PATH}",
            produced_inventory=(("Stake", 1), ("Stake hammer", 1)),
            auto_actions=("Buy Dr Harlow a beer at the Blue Moon Inn",),
        ),
        _stage_req(
            3,
            "Open Count Draynor's coffin with a stake and stake hammer, then defeat him.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MANOR_SOURCE_PATH}; {COUNT_DRAYNOR_NPC_SOURCE_PATH}",
            required_inventory=(("Stake", 1),),
            consumed_inventory=(("Stake", 1),),
            required_tools=(("Stake hammer", 1),),
            combat_encounters=(
                _combat(
                    VAMPYRE_SLAYER_ID,
                    "count_draynor_37",
                    "Count Draynor",
                    37,
                    f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MANOR_SOURCE_PATH}; {COUNT_DRAYNOR_NPC_SOURCE_PATH}",
                    "2011Scape removes the stake when the coffin is opened, spawns Count Draynor, and treats garlic as an optional stat weakening item.",
                    npc_stats=(
                        ("hitpoints", 350),
                        ("attack", 30),
                        ("strength", 25),
                        ("defence", 30),
                        ("magic", 1),
                        ("ranged", 1),
                    ),
                    npc_bonuses=(
                        ("defenceStab", 2),
                        ("defenceSlash", 1),
                        ("defenceCrush", 3),
                        ("defenceMagic", 0),
                        ("defenceRanged", 0),
                    ),
                    npc_configs=(("attack_speed", 4), ("attack_style", "melee")),
                    npc_stats_source=COUNT_DRAYNOR_NPC_SOURCE_PATH,
                ),
            ),
        ),
        _stage_req(
            4,
            "Tell Morgan that Count Draynor is dead.",
            f"{VAMPYRE_SLAYER_SOURCE_PATH}; {VAMPYRE_SLAYER_MORGAN_SOURCE_PATH}; {COUNT_DRAYNOR_NPC_SOURCE_PATH}",
            auto_actions=("Tell Morgan that Count Draynor is dead",),
        ),
    ),
}

__all__ = (
    'VAMPYRE_SLAYER_STAGES',
)
