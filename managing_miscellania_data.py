"""Pinned pre-EOC Managing Miscellania horizontal activity data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MANAGING_MISCELLANIA_ACTIVITY_ID = "managing_miscellania"
MANAGING_MISCELLANIA_SOURCE = (
    "RuneScape Wiki Managing Miscellania oldid=6500793 "
    "(2012-10-30T06:29:55Z)"
)
MANAGING_MISCELLANIA_QUEST_ID = "throne_of_miscellania"
ROYAL_TROUBLE_QUEST_ID = "royal_trouble"
MISCELLANIA_REVIEWS_PER_DAY = 240
MISCELLANIA_CREDIT_SCALE = 1_000_000


@dataclass(frozen=True)
class MiscellaniaResourceVariant:
    id: str
    label: str
    outputs_per_full_day: tuple[tuple[str, int], ...]
    note: str = ""


@dataclass(frozen=True)
class MiscellaniaResourceFamily:
    id: str
    label: str
    variants: tuple[MiscellaniaResourceVariant, ...]


# The horizontal catalog deliberately keeps the three easiest exact cutoff
# resource rows. Together they exercise fixed outputs, bonus outputs, and a
# player-selected output variant without guessing the unresolved herb/seed
# distributions.
MISCELLANIA_RESOURCE_FAMILIES = (
    MiscellaniaResourceFamily(
        "mining",
        "Mining",
        (
            MiscellaniaResourceVariant(
                "coal",
                "Coal",
                (("Coal", 546), ("Uncut sapphire", 3)),
                "Three source gems are represented by the lowest-value cutoff gem; "
                "the hidden gem selector remains data depth.",
            ),
        ),
    ),
    MiscellaniaResourceFamily(
        "wood",
        "Woodcutting",
        (
            MiscellaniaResourceVariant(
                "maple",
                "Maple logs",
                (("Maple logs", 892),),
                "Bird nests are derived exactly as floor(total maple logs / 100).",
            ),
        ),
    ),
    MiscellaniaResourceFamily(
        "hardwood",
        "Hardwood",
        (
            MiscellaniaResourceVariant("teak", "Teak", (("Teak logs", 301),)),
            MiscellaniaResourceVariant(
                "mahogany", "Mahogany", (("Mahogany logs", 204),)
            ),
            MiscellaniaResourceVariant(
                "mixed",
                "Mixed",
                (("Teak logs", 121), ("Mahogany logs", 121)),
            ),
        ),
    ),
)

MISCELLANIA_RESOURCE_BY_ID = {
    family.id: family for family in MISCELLANIA_RESOURCE_FAMILIES
}

# One exact, self-contained approval chore proves the review target without
# flattening unlike chores to invented equal XP. The source gives one approval
# point per maple log; ordinary Maple Woodcutting supplies the 100 XP value.
MISCELLANIA_APPROVAL_CHORES = (
    {
        "id": "chop_maple",
        "label": "Chop maple for the subjects",
        "skill": "woodcutting",
        "skill_label": "Woodcutting",
        "level": 45,
        "xp": 100.0,
        "approval_basis_points": 100,
    },
)


def managing_miscellania_activity_as_dict() -> dict[str, dict[str, Any]]:
    outputs = tuple(
        dict.fromkeys(
            item
            for family in MISCELLANIA_RESOURCE_FAMILIES
            for variant in family.variants
            for item, _quantity in variant.outputs_per_full_day
        )
    ) + ("Bird's nest (seeds)",)
    return {
        MANAGING_MISCELLANIA_ACTIVITY_ID: {
            "display_name": "Managing Miscellania",
            "requirements": {},
            "outputs": outputs,
            "batch_size": 1,
            "group": "landmarks",
            "source": MANAGING_MISCELLANIA_SOURCE,
        }
    }
