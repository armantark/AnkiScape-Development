"""Period-pinned data for the Shattered Heart passive overlay."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SHATTERED_HEART_ACTIVITY_ID = "shattered_heart"
SHATTERED_HEART_BAG_ITEM = "Statue collection bag"
SHATTERED_HEART_BAG_ITEM_ID = 19_704
SHATTERED_HEART_PLINTH_ITEM = "Statue plinth"
SHATTERED_HEART_PLINTH_ITEM_ID = 15_521
SHATTERED_HEART_REVIEWS_PER_DAY = 240
SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS = 7
SHATTERED_HEART_REPLICA_PIECE_LIMIT = 30
SHATTERED_HEART_KUDOS_REWARD = 10
# PLACEHOLDER(shattered_heart.rock_chance): no recovered cutoff server or cache
# routine states the base chance. Breadth one uses one global value rather than
# inventing fifteen skill-specific rates; the second-rock modifier stays exact.
SHATTERED_HEART_ROCK_CHANCE = 0.01
SHATTERED_HEART_SECOND_ROCK_MODIFIER = 0.5
SHATTERED_HEART_SOURCE = (
    "https://runescape.wiki/w/Shattered_Heart?oldid=6514590; "
    "https://runescape.wiki/w/Statue_collection_bag?oldid=6134494; "
    "https://runescape.wiki/w/Statue_plinth_(item)?oldid=5758422; "
    "OpenRS2 rev-742 item and enum definitions; game-main item constants"
)


@dataclass(frozen=True)
class ShatteredHeartSkill:
    id: str
    display_name: str
    rock_item_ids: tuple[int, int]
    replica_item_ids: tuple[int, int]

    @property
    def rock_items(self) -> tuple[str, str]:
        return (
            f"Strange rock ({self.display_name} 1)",
            f"Strange rock ({self.display_name} 2)",
        )

    @property
    def replica_items(self) -> tuple[str, str]:
        return (
            f"Replica statue piece ({self.display_name} 1)",
            f"Replica statue piece ({self.display_name} 2)",
        )


# Cache enum order. Golden rocks are intentionally absent: they post-date the
# cutoff and have no identity in the cutoff caches or emulators.
SHATTERED_HEART_SKILLS: tuple[ShatteredHeartSkill, ...] = (
    ShatteredHeartSkill("agility", "Agility", (15_522, 15_523), (15_552, 15_553)),
    ShatteredHeartSkill("herblore", "Herblore", (15_524, 15_525), (15_554, 15_555)),
    ShatteredHeartSkill("thieving", "Thieving", (15_526, 15_527), (15_556, 15_557)),
    ShatteredHeartSkill("crafting", "Crafting", (15_528, 15_529), (15_558, 15_559)),
    ShatteredHeartSkill("runecrafting", "Runecrafting", (15_530, 15_531), (15_560, 15_561)),
    ShatteredHeartSkill("mining", "Mining", (15_532, 15_533), (15_562, 15_563)),
    ShatteredHeartSkill("smithing", "Smithing", (15_534, 15_535), (15_564, 15_565)),
    ShatteredHeartSkill("fishing", "Fishing", (15_536, 15_537), (15_566, 15_567)),
    ShatteredHeartSkill("cooking", "Cooking", (15_538, 15_539), (15_568, 15_569)),
    ShatteredHeartSkill("firemaking", "Firemaking", (15_540, 15_541), (15_570, 15_571)),
    ShatteredHeartSkill("woodcutting", "Woodcutting", (15_542, 15_543), (15_572, 15_573)),
    ShatteredHeartSkill("fletching", "Fletching", (15_544, 15_545), (15_574, 15_575)),
    ShatteredHeartSkill("farming", "Farming", (15_546, 15_547), (15_576, 15_577)),
    ShatteredHeartSkill("construction", "Construction", (15_548, 15_549), (15_578, 15_579)),
    ShatteredHeartSkill("hunter", "Hunter", (15_550, 15_551), (15_580, 15_581)),
)
SHATTERED_HEART_SKILLS_BY_ID = {row.id: row for row in SHATTERED_HEART_SKILLS}
SHATTERED_HEART_ELIGIBLE_SKILLS = tuple(row.id for row in SHATTERED_HEART_SKILLS)
SHATTERED_HEART_ROCK_ITEMS = tuple(
    item_name for row in SHATTERED_HEART_SKILLS for item_name in row.rock_items
)
SHATTERED_HEART_REPLICA_ITEMS = tuple(
    item_name for row in SHATTERED_HEART_SKILLS for item_name in row.replica_items
)


SHATTERED_HEART_ASSET_MANIFEST = (
    {
        "item_name": "Shattered Heart",
        "wiki_title": "Statue of Dahmaroc (completed).png",
        "output_path": "activityicons/shattered_heart.png",
        "size": 64,
    },
    {
        "item_name": SHATTERED_HEART_BAG_ITEM,
        "wiki_title": "Statue collection bag.png",
        "output_path": "activityitems/statue_collection_bag.png",
        "size": 64,
    },
    {
        "item_name": SHATTERED_HEART_PLINTH_ITEM,
        "wiki_title": "Statue plinth (item).png",
        "output_path": "activityitems/statue_plinth.png",
        "size": 64,
    },
    *(
        {
            "item_name": f"Strange rock ({row.display_name})",
            "wiki_title": f"Strange rock ({row.display_name}).png",
            "output_path": f"activityitems/strange_rock_{row.id}.png",
            "size": 64,
        }
        for row in SHATTERED_HEART_SKILLS
    ),
    *(
        {
            "item_name": f"Replica statue piece ({row.display_name})",
            "wiki_title": f"Replica statue piece ({row.display_name}).png",
            "output_path": f"activityitems/replica_statue_piece_{row.id}.png",
            "size": 64,
        }
        for row in SHATTERED_HEART_SKILLS
    ),
)


def shattered_heart_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        SHATTERED_HEART_ACTIVITY_ID: {
            "display_name": "Shattered Heart",
            "requirements": {},
            "skill_requirements": {},
            "outputs": SHATTERED_HEART_ROCK_ITEMS,
            "batch_size": 1,
            "group": "distractions_and_diversions",
            "source": SHATTERED_HEART_SOURCE,
        }
    }


def shattered_heart_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    items: dict[str, dict[str, Any]] = {
        SHATTERED_HEART_BAG_ITEM: {
            "category": "material",
            "source_item_id": SHATTERED_HEART_BAG_ITEM_ID,
            "stackable": False,
            "tradeable": False,
            "weight_kg": 10.0,
            "source": SHATTERED_HEART_SOURCE,
        },
        SHATTERED_HEART_PLINTH_ITEM: {
            "category": "material",
            "source_item_id": SHATTERED_HEART_PLINTH_ITEM_ID,
            "stackable": False,
            "tradeable": False,
            "source": SHATTERED_HEART_SOURCE,
        },
    }
    for row in SHATTERED_HEART_SKILLS:
        for item_name, item_id in zip(row.rock_items, row.rock_item_ids):
            items[item_name] = {
                "category": "material",
                "source_item_id": item_id,
                "stackable": False,
                "tradeable": False,
                "source": SHATTERED_HEART_SOURCE,
            }
        for item_name, item_id in zip(row.replica_items, row.replica_item_ids):
            items[item_name] = {
                "category": "material",
                "source_item_id": item_id,
                "stackable": False,
                "tradeable": False,
                "source": SHATTERED_HEART_SOURCE,
            }
    return items


__all__ = [
    "SHATTERED_HEART_ACTIVITY_ID",
    "SHATTERED_HEART_ASSET_MANIFEST",
    "SHATTERED_HEART_BAG_ITEM",
    "SHATTERED_HEART_BAG_ITEM_ID",
    "SHATTERED_HEART_ELIGIBLE_SKILLS",
    "SHATTERED_HEART_FINAL_PAIR_COOLDOWN_DAYS",
    "SHATTERED_HEART_KUDOS_REWARD",
    "SHATTERED_HEART_PLINTH_ITEM",
    "SHATTERED_HEART_PLINTH_ITEM_ID",
    "SHATTERED_HEART_REPLICA_ITEMS",
    "SHATTERED_HEART_REPLICA_PIECE_LIMIT",
    "SHATTERED_HEART_REVIEWS_PER_DAY",
    "SHATTERED_HEART_ROCK_CHANCE",
    "SHATTERED_HEART_ROCK_ITEMS",
    "SHATTERED_HEART_SECOND_ROCK_MODIFIER",
    "SHATTERED_HEART_SKILLS",
    "SHATTERED_HEART_SKILLS_BY_ID",
    "ShatteredHeartSkill",
    "shattered_heart_activity_as_dict",
    "shattered_heart_extra_items_as_dict",
]
