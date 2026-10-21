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

# Saved packet: 0270-barcrawl-drink-effects; owner answers 2026-10-21 10:44 PDT.
# Tip.It 20120419060910 (2012-04-19T06:09:10Z), bar_crawl.htm:271,292,
# 310-314,332-346,373-391,400-403 gives averages, NOT level-50 formulas.
# Body SHA-256: a44b5d84b4574b6e685d7b780ac65f43cde93af05b33f03aa8b73da66e874271.
# Wiki Bar_Crawl_(miniquest) oldid 6269519 (2012-09-20T04:35:56Z):
# 23,36,43,49,55,61,67,73,79,85,91 supplies affected skills/health descriptions.
# Body SHA-256: 32e617e947b6c317ff5d71500bb64ac26c0a5b0dc04b5e4470e129bbe02b0a2d.
# Owner includes Smithing using oldid 5882004 (2012-07-04T04:25:50Z):72,
# versus repeated Mining at 6269519:73; this is not a historical resolution.
# Body SHA-256: d17e01157e6ecbe5f5c5af897766fbe4b39ca66a15df669d89bce594c4ad7e50.
# Tip.It says Ape Bite has no damage; the wiki names Attack/Defence. Owner
# chooses those losses, including wholly provisional 8/7 reference amounts.
# Olde Suspiciouse Strength/Smithing 6/6 are also wholly provisional.
# Originals 6304383/5575732 remain unrecovered; these hashes are NOT theirs.
# Darkan's 2024 restoration supplies no historical authority here.
# PLACEHOLDER(bar_crawl.stat_drain_magnitudes): needs per-skill formulas, units and rounding.
BAR_CRAWL_STAT_REFERENCE_LEVEL = 50
BAR_CRAWL_STAT_DRAIN_REFERENCES = {
    "Uncle Humphrey's Gutrot": {"attack": 8, "defense": 7, "strength": 7, "smithing": 6},
    "Fire Toad Blast": {},
    "Supergrog": {"attack": 8, "defense": 7, "herblore": 6, "cooking": 7, "prayer": 60},
    "Fire Brandy": {"attack": 11, "defense": 10},
    "Heart Stopper": {},
    "Liverbane Ale": {"attack": 8, "defense": 6, "fletching": 5, "firemaking": 5, "woodcutting": 5},
    "Olde Suspiciouse": {"attack": 8, "defense": 7, "mining": 6, "crafting": 6, "magic": 6, "strength": 6, "smithing": 6},
    "Ape Bite Liqueur": {"attack": 8, "defense": 7},
    "Hand of Death Cocktail": {"attack": 8, "defense": 6, "ranged": 6, "fishing": 6},
    "Black Skull Ale": {},
}
# PLACEHOLDER(bar_crawl.drink_damage_transaction): needs scaling, bounds, rounding and protection/death semantics.
BAR_CRAWL_DAMAGE_REFERENCE_LIFEPOINTS = 500
# Gutrot 20 (6269519:36) conflicts with 200 at oldid 5575745
# (2012-05-07T07:33:35Z):36; owner selects 20 without resolving history.
# 5575745 body SHA-256: 119304aa8a26b7758ca5a1f81d36d4e387db9991fe751992098722485685f46f.
# PLACEHOLDER(bar_crawl.gutrot_damage_formula): needs maximum conflict resolved and actual damage transaction.
# PLACEHOLDER(bar_crawl.drink_damage_transaction): needs actual Fire Toad/Hand scaling and roll bounds.
BAR_CRAWL_DAMAGE_CAPS = {
    "Uncle Humphrey's Gutrot": 20,
    "Fire Toad Blast": 47,
    "Hand of Death Cocktail": 200,
}
# PLACEHOLDER(bar_crawl.drink_damage_transaction): needs exact Heart Stopper bounds and arithmetic; floor is owner policy.
BAR_CRAWL_HEART_STOPPER_PERCENT_BOUNDS = (20, 30)

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
