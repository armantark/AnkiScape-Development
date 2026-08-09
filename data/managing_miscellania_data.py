"""Pinned pre-EOC Managing Miscellania activity data."""

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


MISCELLANIA_REPRESENTATIVE_GEM = "Uncut sapphire"
# PLACEHOLDER(managing_miscellania.gem_identity): recover the source gem selector
MISCELLANIA_REPRESENTATIVE_NEST = "Bird's nest (seeds)"
# PLACEHOLDER(managing_miscellania.nest_identity): recover the source nest selector
MISCELLANIA_REPRESENTATIVE_HERB_SEED = "Guam seed"
# PLACEHOLDER(managing_miscellania.herb_seed_identity): recover both herb-seed selectors
MISCELLANIA_REPRESENTATIVE_HERB_MIX = (
    ("Grimy tarromin", 17),
    ("Grimy harralander", 15),
    ("Grimy ranarr", 3),
    ("Grimy irit", 10),
    ("Grimy avantoe", 9),
    ("Grimy kwuarm", 3),
    ("Grimy cadantine", 2),
    ("Grimy lantadyme", 1),
    ("Grimy dwarf weed", 1),
)
# PLACEHOLDER(managing_miscellania.herb_mix): recover the within-range herb distribution
MISCELLANIA_REPRESENTATIVE_FARMING_SEED_MIX = (
    ("Potato seed", 95),
    ("Onion seed", 71),
    ("Cabbage seed", 35),
    ("Tomato seed", 34),
    ("Sweetcorn seed", 10),
    ("Strawberry seed", 2),
    ("Watermelon seed", 1),
    ("Barley seed", 18),
    ("Hammerstone seed", 32),
    ("Asgarnian seed", 18),
    ("Jute seed", 21),
    ("Yanillian seed", 6),
    ("Krandorian seed", 5),
    ("Wildblood seed", 4),
    ("Marigold seed", 31),
    ("Rosemary seed", 7),
    ("Nasturtium seed", 10),
    ("Woad seed", 3),
    ("Limpwurt seed", 7),
    ("Guam seed", 5),
    ("Marrentill seed", 6),
    ("Tarromin seed", 3),
    ("Irit seed", 1),
    ("Ranarr seed", 1),
    ("Avantoe seed", 1),
    ("Snapdragon seed", 1),
    ("Torstol seed", 1),
    ("Redberry seed", 22),
    ("Cadavaberry seed", 11),
    ("Dwellberry seed", 3),
    ("Jangerberry seed", 1),
    ("Poison ivy seed", 1),
    ("Mushroom spore", 1),
    ("Cactus seed", 1),
    ("Belladonna seed", 1),
    ("Willow seed", 1),
    ("Apple tree seed", 1),
)
# PLACEHOLDER(managing_miscellania.farming_seed_mix): recover the within-range seed distribution


MISCELLANIA_RESOURCE_FAMILIES = (
    MiscellaniaResourceFamily(
        "mining",
        "Mining",
        (
            MiscellaniaResourceVariant(
                "coal",
                "Coal",
                (("Coal", 546), (MISCELLANIA_REPRESENTATIVE_GEM, 3)),
                "The source fixes three gems but not their identities.",
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
        "harvesting",
        "Flax / Herbs",
        (
            MiscellaniaResourceVariant(
                "flax",
                "Flax",
                (("Flax", 1250), (MISCELLANIA_REPRESENTATIVE_HERB_SEED, 2)),
                "The source fixes two herb seeds but not their identities.",
            ),
            MiscellaniaResourceVariant(
                "herbs",
                "Herbs",
                MISCELLANIA_REPRESENTATIVE_HERB_MIX
                + ((MISCELLANIA_REPRESENTATIVE_HERB_SEED, 1),),
                "The representative mix preserves the exact total and every source range.",
            ),
        ),
    ),
    MiscellaniaResourceFamily(
        "fishing",
        "Fishing",
        (
            MiscellaniaResourceVariant(
                "raw",
                "Raw fish",
                (
                    ("Raw tuna", 440),
                    ("Raw swordfish", 131),
                    ("Casket", 4),
                    (MISCELLANIA_REPRESENTATIVE_GEM, 4),
                ),
                "The source names assorted extras but gives no quantities or selector.",
            ),
            MiscellaniaResourceVariant(
                "cooked",
                "Cooked fish",
                (
                    ("Tuna", 440),
                    ("Swordfish", 131),
                    ("Casket", 4),
                    (MISCELLANIA_REPRESENTATIVE_GEM, 4),
                ),
                "Cooked fish uses the same source quantities as raw fish.",
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
    MiscellaniaResourceFamily(
        "farming",
        "Farming",
        (
            MiscellaniaResourceVariant(
                "seeds",
                "Seeds",
                MISCELLANIA_REPRESENTATIVE_FARMING_SEED_MIX,
                "The representative mix preserves every source category total and item range.",
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
    ) + (MISCELLANIA_REPRESENTATIVE_NEST,)
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
