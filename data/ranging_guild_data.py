"""Period-pinned Ranging Guild competition and ticket exchange."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RANGING_GUILD_ACTIVITY_ID = "ranging_guild"
RANGING_GUILD_ENTRY_LEVEL = 40
RANGING_GUILD_ENTRY_COINS = 200
RANGING_GUILD_SHOTS = 10
RANGING_GUILD_ENTRY_ARROWS = 10
RANGING_GUILD_TICKET_ITEM = "Archery ticket"

RANGING_GUILD_SOURCE = (
    "RuneScape Wiki Ranging Guild oldid=6372385 (2012-10-09T03:01:36Z); "
    "Competition Judge oldid=6454773 (2012-10-22); Ticket Merchant "
    "oldid=6226065 (2012-09-09); Archery ticket oldid=6534408 "
    "(2012-11-04T20:38:51Z); rev-742 items 47, 829, 882, 892, 1133, "
    "1135, 1169, 1464; Darkan RangingGuildCompetition.java at tree "
    "28b377b417e1999c131b49f00b5fce782d5a90ff; "
    "Darkan memory-bank/audit/evidence/static/ranging-guild-target-contract.json"
)


@dataclass(frozen=True)
class RangingGuildBand:
    id: str
    display_name: str
    score: int
    ranged_xp: float


RANGING_GUILD_BANDS = (
    RangingGuildBand("miss", "Missed", 0, 0.0),
    RangingGuildBand("black", "Black", 10, 5.0),
    RangingGuildBand("blue", "Blue", 20, 10.0),
    RangingGuildBand("red", "Red", 30, 15.0),
    RangingGuildBand("yellow", "Yellow", 50, 25.0),
    RangingGuildBand("bullseye", "Bull's-eye", 100, 50.0),
)
RANGING_GUILD_BANDS_BY_ID = {row.id: row for row in RANGING_GUILD_BANDS}


@dataclass(frozen=True)
class RangingGuildReward:
    id: str
    display_name: str
    item_name: str
    quantity: int
    ticket_cost: int
    source_item_id: int


RANGING_GUILD_REWARDS = (
    RangingGuildReward("barb_bolttips", "30 Barb bolttips", "Barb bolttips", 30, 114, 47),
    RangingGuildReward("studded_body", "Studded body", "Studded body", 1, 51, 1133),
    RangingGuildReward("rune_arrows", "50 Rune arrows", "Rune arrows", 50, 1_020, 892),
    RangingGuildReward("coif", "Coif", "Coif", 1, 12, 1169),
    RangingGuildReward(
        "green_dhide_body",
        "Green d'hide body",
        "Green d'hide body",
        1,
        856,
        1135,
    ),
    RangingGuildReward(
        "adamant_javelins",
        "20 Adamant javelins",
        "Adamant javelin",
        20,
        292,
        829,
    ),
)
RANGING_GUILD_REWARDS_BY_ID = {row.id: row for row in RANGING_GUILD_REWARDS}

# The frozen Darkan contract uses this deterministic provisional resolver while
# the period server-side probability remains source-blocked.
# PLACEHOLDER(ranging_guild.hit_quality_resolver): authentic target hit
# probability and band thresholds.
RANGING_GUILD_QUALITY_THRESHOLDS = (
    (75, "miss"),
    (110, "black"),
    (140, "blue"),
    (165, "red"),
    (190, "yellow"),
)

RANGING_GUILD_ASSET_MANIFEST = (
    {
        "item_name": RANGING_GUILD_TICKET_ITEM,
        "wiki_title": "Archery ticket.png",
        "output_path": "activityicons/ranging_guild.png",
        "size": 64,
    },
)


def ranging_guild_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        RANGING_GUILD_ACTIVITY_ID: {
            "display_name": "Ranging Guild",
            "requirements": {"Coins": RANGING_GUILD_ENTRY_COINS},
            "skill_requirements": {"ranged": RANGING_GUILD_ENTRY_LEVEL},
            "outputs": (
                RANGING_GUILD_TICKET_ITEM,
                *(row.item_name for row in RANGING_GUILD_REWARDS),
            ),
            "batch_size": 1,
            "group": "minigames",
            "source": RANGING_GUILD_SOURCE,
        }
    }


def ranging_guild_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    rows = {
        RANGING_GUILD_TICKET_ITEM: {
            "category": "material",
            "source_item_id": 1464,
            "stackable": True,
            "tradeable": True,
        },
        "Barb bolttips": {
            "category": "material",
            "source_item_id": 47,
            "stackable": True,
            "tradeable": True,
        },
        "Rune arrows": {
            "category": "equipment",
            "source_item_id": 892,
            "stackable": True,
            "tradeable": True,
        },
        "Studded body": {
            "category": "equipment",
            "source_item_id": 1133,
            "stackable": False,
            "tradeable": True,
        },
        "Coif": {
            "category": "equipment",
            "source_item_id": 1169,
            "stackable": False,
            "tradeable": True,
        },
        "Green d'hide body": {
            "category": "equipment",
            "source_item_id": 1135,
            "stackable": False,
            "tradeable": True,
        },
        "Adamant javelin": {
            "category": "equipment",
            "source_item_id": 829,
            "stackable": True,
            "tradeable": True,
        },
    }
    return {
        item_name: {**spec, "source": RANGING_GUILD_SOURCE}
        for item_name, spec in rows.items()
    }
