from __future__ import annotations

from ...ids import *
from ...sources import *
from ...contract import *

MOGRE_STAGES = (
    QuestStage(1, ("Skippy is too drunk to explain what attacked him. A bucket of water should sober him.",)),
    QuestStage(2, ("Skippy wants hot nettle tea. I should pick nettles and prepare a bowl.",)),
    QuestStage(3, ("I picked nettles. I should mix and boil them, then give Skippy the tea.",)),
    QuestStage(4, ("The tea helped, but Skippy now needs a hangover cure.",)),
    QuestStage(5, ("I made the hangover cure and should give it to Skippy.",)),
    QuestStage(
        6,
        (
            "Skippy described the creatures in the water. I can now lure Mogres with Fishing explosives.",
            "Miniquest complete!",
        ),
    ),
)
MOGRE_STAGE_REQUIREMENTS = (
    QuestStageRequirement(
        stage=1,
        description="Throw a bucket of water over Skippy to sober him.",
        consumed_inventory=(("Bucket of water", 1),),
        auto_actions=("Sober Skippy with a bucket of water",),
        source=f"{MOGRE_MINIQUEST_WIKI_SOURCE}; {SKIPPY_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=2,
        description="Pick nettles near Draynor Village jail for Skippy's tea.",
        # Nettles are a repeatable glove-protected world pickable, so the
        # stage consumes one picked Nettles the way its sibling stages
        # consume theirs; the pick_nettles Utility row is the producer.
        consumed_inventory=(("Nettles", 1),),
        required_tools=(("Leather gloves", 1),),
        auto_actions=(
            "Pick nettles near Draynor Village jail while wearing leather gloves",
        ),
        source=f"{MOGRE_MINIQUEST_WIKI_SOURCE}; {NETTLES_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=3,
        description="Give Skippy a bowl of hot nettle tea.",
        consumed_inventory=(("Nettle tea", 1),),
        auto_actions=("Give Skippy the hot nettle tea",),
        source=f"{MOGRE_MINIQUEST_WIKI_SOURCE}; {NETTLE_TEA_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=4,
        description="Mix the same hangover cure used in Plague City.",
        consumed_inventory=(
            ("Chocolate dust", 1),
            ("Bucket of milk", 1),
            ("Snape grass", 1),
        ),
        produced_inventory=(("Hangover cure", 1),),
        required_tools=(("Pestle and mortar", 1),),
        auto_actions=("Mix Skippy's hangover cure with chocolate dust, milk and snape grass",),
        source=f"{MOGRE_MINIQUEST_WIKI_SOURCE}; {HANGOVER_CURE_WIKI_SOURCE}",
    ),
    QuestStageRequirement(
        stage=5,
        description="Give Skippy the hangover cure so he can explain the Mogres.",
        consumed_inventory=(("Hangover cure", 1),),
        auto_actions=("Give Skippy the hangover cure",),
        source=(
            f"{MOGRE_MINIQUEST_WIKI_SOURCE}; {SKIPPY_WIKI_SOURCE}; "
            f"{HANGOVER_CURE_WIKI_SOURCE}"
        ),
    ),
)
QUEST = QuestDefinition(
    id=SKIPPY_AND_THE_MOGRES_ID,
    display_name="Skippy and the Mogres",
    stage_count=len(MOGRE_STAGES),
    point_reward=0,
    rewards=(),
    start_point="Speak to Skippy on the coast south-east of Rimmington.",
    requirements=("Cooking 20",),
    required_items=(),
    combat="No combat.",
    source=(
        f"{MOGRE_MINIQUEST_WIKI_SOURCE}; {SKIPPY_WIKI_SOURCE}; "
        f"{MINIQUEST_LIST_SOURCE}"
    ),
    journal_stages=MOGRE_STAGES,
    # PLACEHOLDER(skippy_and_the_mogres.release_date): the pinned pages give
    # no release record for the lore activity, so the row takes the
    # catalog's unknown-order value and sorts last without a period date.
    release_date="2005-10-24",
    members=True,
    # PLACEHOLDER(skippy_and_the_mogres.difficulty_label): neither the
    # lore-activity page nor the miniquest list states a difficulty word.
    difficulty="Novice",
    # PLACEHOLDER(skippy_and_the_mogres.length_label): the same missing
    # details block is the only place a length would have been stated.
    length="Very Short",
    timeline="Fifth Age",
    release_order=9999,
    required_skills=(QuestSkillRequirement("cooking", "Cooking", 20),),
    unlocks=(
        "Ability to lure and kill Mogres with Fishing explosives at Slayer 32",
    ),
    stage_requirements=MOGRE_STAGE_REQUIREMENTS,
    miniquest=True,
)

__all__ = ("MOGRE_STAGES", "MOGRE_STAGE_REQUIREMENTS")
