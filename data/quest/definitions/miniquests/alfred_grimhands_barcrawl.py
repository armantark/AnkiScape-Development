from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *
from ....quest_action_proof_data import (
    BAR_CRAWL_BLUE_MOON_INN_PROOF,
    BAR_CRAWL_BLURBERRYS_BAR_PROOF,
    BAR_CRAWL_DEAD_MANS_CHEST_PROOF,
    BAR_CRAWL_DRAGON_INN_PROOF,
    BAR_CRAWL_FLYING_HORSE_INN_PROOF,
    BAR_CRAWL_FORESTERS_ARMS_PROOF,
    BAR_CRAWL_JOLLY_BOAR_INN_PROOF,
    BAR_CRAWL_KARAMJA_WINES_SPIRITS_AND_BEERS_PROOF,
    BAR_CRAWL_RISING_SUN_PROOF,
    BAR_CRAWL_RUSTY_ANCHOR_PROOF,
)

BAR_CRAWL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I should speak to a Barbarian guard at the Barbarian Outpost",
        "and take a Barcrawl card.",
    ),
    _simple_stage(
        2,
        "I have a Barcrawl card. I must buy the named speciality drink",
        "at each of the ten bars, in any order, and get every signature.",
        "Then I should bring the completed card back to a guard.",
    ),
    _simple_stage(
        3,
        "I returned the completed Barcrawl card to a Barbarian guard.",
        "I can now enter the Barbarian Outpost.",
        "Miniquest complete!",
    ),
)

BAR_CRAWL_STAGE_REQUIREMENTS: Tuple[QuestStageRequirement, ...] = (
    _stage_req(
        1,
        "Speak to a Barbarian guard at the Barbarian Outpost and take a Barcrawl card.",
        f"{BAR_CRAWL_WIKI_SOURCE}; {BAR_CRAWL_GUARD_SOURCE}; {BAR_CRAWL_CARD_SOURCE}; {BAR_CRAWL_HARVEST_SOURCE}",
        auto_actions=(
            "Speak to a Barbarian guard at the Barbarian Outpost",
            "Take a Barcrawl card",
        ),
        produced_inventory=(("Barcrawl card", 1),),
    ),
    # As in Tarn, entering the final journal stage writes completion. All
    # signatures gate that return transition together, never a prescribed route.
    _stage_req(
        2,
        "Buy all ten speciality drinks in any order, then return the signed card to a Barbarian guard.",
        f"{BAR_CRAWL_WIKI_SOURCE}; {BAR_CRAWL_CARD_SOURCE}; {BAR_CRAWL_HARVEST_SOURCE}",
        required_inventory=(("Barcrawl card", 1),),
        required_actions=(
            BAR_CRAWL_BLUE_MOON_INN_PROOF,
            BAR_CRAWL_BLURBERRYS_BAR_PROOF,
            BAR_CRAWL_DEAD_MANS_CHEST_PROOF,
            BAR_CRAWL_DRAGON_INN_PROOF,
            BAR_CRAWL_FLYING_HORSE_INN_PROOF,
            BAR_CRAWL_FORESTERS_ARMS_PROOF,
            BAR_CRAWL_JOLLY_BOAR_INN_PROOF,
            BAR_CRAWL_KARAMJA_WINES_SPIRITS_AND_BEERS_PROOF,
            BAR_CRAWL_RISING_SUN_PROOF,
            BAR_CRAWL_RUSTY_ANCHOR_PROOF,
        ),
        auto_actions=("Return the signed Barcrawl card to a Barbarian guard",),
    ),
)

QUEST = QuestDefinition(
        id=BAR_CRAWL_ID,
        display_name="Alfred Grimhand's Barcrawl",
        stages=len(BAR_CRAWL_STAGES),
        point_reward=0,
        rewards=(),
        start_point=(
            "Talk to a Barbarian guard at the Barbarian Outpost. "
            "Short if the Grand Tree quest is completed and the Lodestone Network is unlocked."
        ),
        requirements=(),
        required_items=(),
        combat="None",
        source=(
            f"{BAR_CRAWL_WIKI_SOURCE}; {BAR_CRAWL_CARD_SOURCE}; "
            f"{BAR_CRAWL_GUARD_SOURCE}; {BAR_CRAWL_HARVEST_SOURCE}; "
            f"{BAR_CRAWL_RELEASE_SOURCE}"
        ),
        journal_stages=BAR_CRAWL_STAGES,
        # PLACEHOLDER(quests.bar_crawl.release_date): needs a traceable release record.
        release_date="PLACEHOLDER(quests.bar_crawl.release_date)",
        members=True,
        difficulty="Special",
        length="Medium",
        # PLACEHOLDER(quests.bar_crawl.timeline): needs an explicit period timeline.
        timeline="PLACEHOLDER(quests.bar_crawl.timeline)",
        release_order=9999,
        required_quests=(),
        required_skills=(),
        xp_rewards=(),
        unlocks=(
            "Access to the Barbarian Outpost",
            "Barcrawl prerequisite for Horror from the Deep",
            "Barcrawl prerequisite for Scorpion Catcher",
        ),
        stage_requirements=BAR_CRAWL_STAGE_REQUIREMENTS,
        miniquest=True,
    )

__all__ = (
    'BAR_CRAWL_STAGES', 'BAR_CRAWL_STAGE_REQUIREMENTS',
)
