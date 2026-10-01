from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

# (drink, bar, place, coins) from Bar Crawl oldid 6304383. That page allows any
# order; ruling 4.28 item 5 fixes this one because each bar is an automatic
# review step, and a free order means nothing once nobody chooses it.
BAR_CRAWL_DRINKS: Tuple[Tuple[str, str, str, int], ...] = (
    ("Uncle Humphrey's Gutrot", "Blue Moon Inn", "Varrock", 50),
    ("Fire Toad Blast", "Blurberry's Bar", "the Grand Tree", 10),
    ("Supergrog", "Dead Man's Chest", "Brimhaven", 15),
    ("Fire Brandy", "Dragon Inn", "Yanille", 12),
    ("Heart Stopper", "Flying Horse Inn", "Ardougne", 8),
    ("Liverbane Ale", "Forester's Arms", "Seers' Village", 18),
    ("Olde Suspiciouse", "Jolly Boar Inn", "Varrock", 10),
    ("Ape Bite Liqueur", "Karamja Wines, Spirits, and Beers", "Musa Point", 7),
    ("Hand of Death Cocktail", "Rising Sun", "Falador", 70),
    ("Black Skull Ale", "Rusty Anchor", "Port Sarim", 8),
)
_RETURN_STAGE = len(BAR_CRAWL_DRINKS) + 2

BAR_CRAWL_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(
        1,
        "I should speak to a Barbarian guard at the Barbarian Outpost",
        "and take a Barcrawl card.",
    ),
    *(
        _simple_stage(
            stage,
            f"My Barcrawl card has {stage - 2} of 10 signatures.",
            f"Next I should drink {drink} at {bar}, {place}, for {coins} coins.",
        )
        for stage, (drink, bar, place, coins) in enumerate(BAR_CRAWL_DRINKS, start=2)
    ),
    _simple_stage(
        _RETURN_STAGE,
        "My Barcrawl card has all 10 signatures.",
        "I should bring it back to a Barbarian guard.",
    ),
    _simple_stage(
        _RETURN_STAGE + 1,
        "I returned the completed Barcrawl card to a Barbarian guard.",
        "I can now enter the Barbarian Outpost.",
        "Miniquest complete!",
    ),
)

_BAR_CRAWL_STAGE_SOURCE = f"{BAR_CRAWL_WIKI_SOURCE}; {BAR_CRAWL_CARD_SOURCE}; {BAR_CRAWL_HARVEST_SOURCE}"

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
    *(
        _stage_req(
            stage,
            f"Pay {coins} coins for {drink} at {bar} and get the Barcrawl card signed.",
            _BAR_CRAWL_STAGE_SOURCE,
            required_inventory=(("Barcrawl card", 1),),
            consumed_inventory=(("Coins", coins),),
            auto_actions=(f"Drink {drink} at {bar}",),
        )
        for stage, (drink, bar, _place, coins) in enumerate(BAR_CRAWL_DRINKS, start=2)
    ),
    # As in Tarn, entering the final journal stage writes completion.
    _stage_req(
        _RETURN_STAGE,
        "Return the signed Barcrawl card to a Barbarian guard.",
        _BAR_CRAWL_STAGE_SOURCE,
        required_inventory=(("Barcrawl card", 1),),
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
