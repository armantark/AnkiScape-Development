from __future__ import annotations

from ...dependencies import *
from ...ids import *
from ...sources import *
from ...item_names import *
from ...contract import *
from ...choices import *

GOBLIN_DIPLOMACY_STAGES: Tuple[QuestStage, ...] = (
    _simple_stage(1, "The goblin generals want to try orange goblin mail."),
    _simple_stage(2, "The generals rejected orange goblin mail and now want blue goblin mail."),
    _simple_stage(3, "The generals rejected blue goblin mail and now want regular brown goblin mail."),
    _simple_stage(4, "The generals chose brown armour and rewarded me.", "Quest complete!"),
)

QUEST = QuestDefinition(
        id=GOBLIN_DIPLOMACY_ID,
        display_name="Goblin Diplomacy",
        stages=4,
        point_reward=5,
        rewards=(("Gold bar", 1),),
        start_point="Talk to General Bentnoze or General Wartface in Goblin Village.",
        requirements=("Used during quest: Orange goblin mail x1, Blue goblin mail x1, Goblin mail x1",),
        required_items=(),
        combat="None.",
        source=f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
        journal_stages=GOBLIN_DIPLOMACY_STAGES,
        release_date="2001-05-08",
        members=False,
        difficulty="Novice",
        length="Short to Medium",
        timeline="Fifth Age",
        xp_rewards=(QuestXpReward("crafting", 200),),
    )

_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID: Dict[str, Tuple[QuestStageRequirement, ...]] = {
    GOBLIN_DIPLOMACY_ID: (
        _stage_req(
            1,
            "Give the goblin generals orange goblin mail.",
            f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Orange goblin mail", 1),),
        ),
        _stage_req(
            2,
            "Give the goblin generals blue goblin mail.",
            f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Blue goblin mail", 1),),
        ),
        _stage_req(
            3,
            "Give the goblin generals regular brown goblin mail.",
            f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; {SCAPE_2011_ITEM_IDENTITY_SOURCE}",
            consumed_inventory=(("Goblin mail", 1),),
        ),
    ),
}

_REWARD_ITEM_FRAGMENT_0 = {
        "Red dye": {
            "category": "material",
            "item_id": 1763,
            "tradeable": True,
            "stackable": False,
            "source": (
                f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; OpenRS2 cache rev 742 item 1763; "
                "src/main/java/com/rs/game/content/skills/construction/playerOwnedHouse/"
                "HouseObjects.kt:485 @ 7e7d67b481f1b94599de38a98c470419ab7c96b3"
            ),
        },
        "Orange goblin mail": {
            "category": "material",
            "item_id": 286,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {ORANGE_GOBLIN_MAIL_WIKI_SOURCE}; "
                f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; OpenRS2 cache rev 742 item 286"
            ),
        },
        "Blue goblin mail": {
            "category": "material",
            "item_id": 287,
            "tradeable": False,
            "stackable": False,
            "source": (
                f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {BLUE_GOBLIN_MAIL_WIKI_SOURCE}; "
                f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; OpenRS2 cache rev 742 item 287"
            ),
        },
        "Goblin mail": {
            "category": "material",
            "item_id": 288,
            "tradeable": True,
            "stackable": False,
            "source": (
                f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {GOBLIN_MAIL_WIKI_SOURCE}; "
                f"{DARKAN_GOBLIN_DIPLOMACY_SOURCE}; OpenRS2 cache rev 742 item 288"
            ),
        },
}

_REWARD_ITEM_FRAGMENTS = (_REWARD_ITEM_FRAGMENT_0,)

__all__ = (
    'GOBLIN_DIPLOMACY_STAGES',
)
