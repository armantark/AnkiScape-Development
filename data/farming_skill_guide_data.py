"""Period cache spine for the Farming Stats skill guide."""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Mapping, Optional


FARMING_GUIDE_KEY: Final = 21
FARMING_GUIDE_ENTRY_ENUM: Final = 5463
FARMING_GUIDE_CATEGORY_ENUM: Final = 5438
FARMING_GUIDE_SOURCE: Final = (
    "OpenRS2 rev-727 and rev-742 cache enums 5438/5463 and structs 3439-3548; "
    "memory-bank/source-audits/farming-skill-guide-2026-08-12.md"
)


@dataclass(frozen=True)
class FarmingGuideRequirement:
    kind: str
    key: str
    minimum: int = 0
    label: Optional[str] = None


@dataclass(frozen=True)
class FarmingGuideSourceRow:
    struct_id: int
    name: str
    level: int
    icon_item_id: int
    guide_key: int
    category_id: int
    requirement_text: Optional[str] = None
    requirements: tuple[FarmingGuideRequirement, ...] = ()


def _quest(key: str, label: str) -> FarmingGuideRequirement:
    return FarmingGuideRequirement("quest", key, label=label)


def _skill(key: str, minimum: int) -> FarmingGuideRequirement:
    return FarmingGuideRequirement("skill", key, minimum)


FARMING_GUIDE_ICON_STORAGE_KEYS: Final[Mapping[int, str]] = MappingProxyType({
    1942: "Potato", 1957: "Onion", 1965: "Cabbage", 1982: "Tomato",
    5986: "Sweetcorn", 5504: "Strawberry", 5982: "Watermelon", 6006: "Barley",
    5994: "Hammerstone hops", 5996: "Asgarnian hops", 5931: "Jute fibre",
    5998: "Yanillian hops", 6000: "Krandorian hops", 6002: "Wildblood hops",
    1521: "Oak logs", 1519: "Willow logs", 1517: "Maple logs", 1515: "Yew logs",
    1513: "Magic logs", 1955: "Cooking apple", 1963: "Banana", 2108: "Orange",
    5970: "Curry leaf", 2114: "Pineapple", 5972: "Papaya fruit", 5974: "Coconut",
    1951: "Redberries", 753: "Cadava berries", 2126: "Dwellberries",
    247: "Jangerberries", 239: "White berries", 6018: "Poison ivy berries",
    6010: "Marigolds", 6014: "Rosemary", 6059: "Scarecrow", 6012: "Nasturtiums",
    5738: "Woad leaf", 225: "Limpwurt root", 14583: "White lily", 249: "Clean guam",
    251: "Clean marrentill", 253: "Clean tarromin", 255: "Clean harralander",
    3261: "Goutweed", 257: "Clean ranarr", 12172: "Clean spirit weed",
    2998: "Clean toadflax", 259: "Clean irit", 14854: "Clean wergali",
    261: "Clean avantoe", 263: "Clean kwuarm", 19989: "Clean erzille",
    3000: "Clean snapdragon", 19990: "Clean argway", 265: "Clean cadantine",
    19991: "Clean ugune", 2481: "Clean lantadyme", 19992: "Clean shengo",
    267: "Clean dwarf weed", 19993: "Clean samaden", 269: "Clean torstol",
    21624: "Clean fellstalk", 12134: "Evil turnip", 6004: "Bittercap mushroom",
    11779: "Jade vine branch", 19962: "Red blossom", 6016: "Cactus spine",
    19969: "Lergberry", 2398: "Cave nightshade", 5980: "Calquat fruit",
    21622: "Morchella mushroom", 19970: "Kalferberry", 6063: "Spirit sapling",
})
FARMING_GUIDE_MISSING_ICON_ITEM_IDS: Final = frozenset({
    18336, 20704, 22494, 18778, 18779, 18780, 18781, 14667, 9810,
})


FARMING_GUIDE_CACHE_CATEGORIES: Final = (
    ("everything", "Everything", 0),
    ("milestones", "Milestones", 1),
    ("produce", "Produce", 2),
    ("trees", "Trees", 3),
    ("special", "Special", 4),
    ("other", "Other", 5),
    ("dungeoneering", "Dungeoneering", 6),
)
FARMING_GUIDE_SECTIONS: Final = FARMING_GUIDE_CACHE_CATEGORIES[1:6]

# Source order is the enum-5463 order. The period client opened this guide on
# Milestones; AnkiScape deliberately renders every populated section together.
# Dungeoneering structs 3526-3547 remain pinned below for source completeness,
# but are excluded from the rendered section projection above.
FARMING_GUIDE_ROWS: Final = tuple(
    FarmingGuideSourceRow(*row)
    for row in (
        (3439, "Potato", 1, 1942, 21, 2, None),
        (3440, "Onion", 5, 1957, 21, 2, None),
        (3441, "Cabbage", 7, 1965, 21, 2, None),
        (3442, "Tomato", 12, 1982, 21, 2, None),
        (3443, "Sweetcorn", 20, 5986, 21, 2, None),
        (3444, "Strawberry", 31, 5504, 21, 2, None),
        (3445, "Watermelon", 47, 5982, 21, 2, None),
        (3446, "Barley", 3, 6006, 21, 2, None),
        (3447, "Hammerstone hop", 4, 5994, 21, 2, None),
        (3448, "Asgarnian hop", 8, 5996, 21, 2, None),
        (3449, "Jute plant", 13, 5931, 21, 2, None),
        (3450, "Yanillian hop", 16, 5998, 21, 2, None),
        (3451, "Krandorian hop", 21, 6000, 21, 2, None),
        (3452, "Wildblood hop", 28, 6002, 21, 2, None),
        (3453, "Oak tree", 15, 1521, 21, 3, None),
        (3454, "Willow tree", 30, 1519, 21, 3, None),
        (3455, "Maple tree", 45, 1517, 21, 3, None),
        (3456, "Yew tree", 60, 1515, 21, 3, None),
        (3457, "Magic tree", 75, 1513, 21, 3, None),
        (3458, "Apple tree", 27, 1955, 21, 3, None),
        (3459, "Banana tree", 33, 1963, 21, 3, None),
        (3460, "Orange tree", 39, 2108, 21, 3, None),
        (3461, "Curry tree", 42, 5970, 21, 3, None),
        (3462, "Pineapple plant", 51, 2114, 21, 3, None),
        (3463, "Papaya tree", 57, 5972, 21, 3, None),
        (3464, "Palm tree", 68, 5974, 21, 3, None),
        (3465, "Redberry bush", 10, 1951, 21, 2, None),
        (3466, "Cadavaberry bush", 22, 753, 21, 2, None),
        (3467, "Dwellberry bush", 36, 2126, 21, 2, None),
        (3468, "Jangerberry bush", 48, 247, 21, 2, None),
        (3469, "White berry bush", 59, 239, 21, 2, None),
        (3470, "Poison ivy bush", 70, 6018, 21, 2, None),
        (3471, "Marigold", 2, 6010, 21, 2, None),
        (3472, "Rosemary", 11, 6014, 21, 2, None),
        (3473, "Make and place a scarecrow", 23, 6059, 21, 5, None),
        (3474, "Nasturtium", 24, 6012, 21, 2, None),
        (3475, "Woad", 25, 5738, 21, 5, None),
        (3476, "Limpwurt", 26, 225, 21, 5, None),
        (3477, "White lily", 52, 14583, 21, 2, None),
        (3478, "Guam", 9, 249, 21, 2, None),
        (3479, "Marrentill", 14, 251, 21, 2, None),
        (3480, "Tarromin", 19, 253, 21, 2, None),
        (3481, "Harralander", 26, 255, 21, 2, None),
        (3482, "Goutweed", 29, 3261, 21, 2, "Quest requirement: Eadgar's Ruse", (_quest("eadgars_ruse", "Eadgar's Ruse"),)),
        (3483, "Ranarr", 32, 257, 21, 2, None),
        (3484, "Spirit weed", 36, 12172, 21, 2, None),
        (3485, "Toadflax", 38, 2998, 21, 2, None),
        (3486, "Irit", 44, 259, 21, 2, None),
        (3487, "Wergali", 46, 14854, 21, 2, None),
        (3488, "Avantoe", 50, 261, 21, 2, None),
        (3489, "Kwuarm", 56, 263, 21, 2, None),
        (3490, "Erzille", 58, 19989, 21, 2, None),
        (3491, "Snapdragon", 62, 3000, 21, 2, None),
        (3492, "Argway", 65, 19990, 21, 2, None),
        (3493, "Cadantine", 67, 265, 21, 2, None),
        (3494, "Ugune", 70, 19991, 21, 2, None),
        (3495, "Lantadyme", 73, 2481, 21, 2, None),
        (3496, "Shengo", 76, 19992, 21, 2, None),
        (3497, "Dwarf weed", 79, 267, 21, 2, None),
        (3498, "Samaden", 80, 19993, 21, 2, None),
        (3499, "Torstol", 85, 269, 21, 2, None),
        (3500, "Fellstalk", 91, 21624, 21, 2, None),
        (3501, "Evil turnip", 42, 12134, 21, 4, None),
        (3502, "Bittercap mushroom", 53, 6004, 21, 4, None),
        (3503, "Jade Vine", 53, 11779, 21, 4, "Quest requirement: Back to My Roots", (_quest("back_to_my_roots", "Back to My Roots"),)),
        (3504, "Vine blossoms", 54, 19962, 21, 4, None),
        (3505, "Cactus", 55, 6016, 21, 4, None),
        (3506, "Lergberry bush", 61, 19969, 21, 4, None),
        (3507, "Belladonna", 63, 2398, 21, 4, None),
        (3508, "Calquat tree", 72, 5980, 21, 4, None),
        (3509, "Morchella mushroom", 74, 21622, 21, 4, None),
        (3510, "Kalferberry bush", 77, 19970, 21, 4, None),
        (3511, "Spirit tree", 83, 6063, 21, 4, None),
        (3512, "Ability to plant a second spirit tree", 86, 6063, 21, 4, "Quest requirement: Prisoner of Glouphrie", (_quest("the_prisoner_of_glouphrie", "Prisoner of Glouphrie"),)),
        (3513, "Scroll of life", 25, 18336, 21, 5, "Also requires: 25 Dungeoneering", (_skill("dungeoneering", 25),)),
        (3514, "Access to the Livid Farm", 60, 20704, 21, 1, "Quest requirement: Lunar Diplomacy", (_quest("lunar_diplomacy", "Lunar Diplomacy"), _skill("magic", 70), _skill("agility", 60), _skill("crafting", 60), _skill("construction", 50))),
        (3515, "Polypore staff", 80, 22494, 21, 5, None),
        (3516, "Starved ancient effigy", 91, 18778, 21, 5, None),
        (3517, "Nourished ancient effigy", 93, 18779, 21, 5, None),
        (3518, "Sated ancient effigy", 95, 18780, 21, 5, None),
        (3519, "Gorged ancient effigy", 97, 18781, 21, 5, None),
        (3520, "Nurture evil oak tree saplings", 7, 14667, 21, 5, None, (_skill("woodcutting", 15), _skill("firemaking", 15))),
        (3521, "Nurture evil willow tree saplings", 15, 14667, 21, 5, None, (_skill("woodcutting", 30), _skill("firemaking", 30))),
        (3522, "Nurture evil maple tree saplings", 22, 14667, 21, 5, None, (_skill("woodcutting", 45), _skill("firemaking", 45))),
        (3523, "Nurture evil yew tree saplings", 30, 14667, 21, 5, None, (_skill("woodcutting", 60), _skill("firemaking", 60))),
        (3524, "Nurture evil magic tree saplings", 37, 14667, 21, 5, None, (_skill("woodcutting", 75), _skill("firemaking", 75))),
        (3525, "Nurture elder evil tree saplings", 42, 14667, 21, 5, None, (_skill("woodcutting", 85), _skill("firemaking", 85))),
        (3526, "Salve nettles in Daemonheim", 1, 17448, 21, 6, None),
        (3527, "Cave potato in Daemonheim", 1, 17823, 21, 6, None),
        (3528, "Sagewort in Daemonheim", 7, 17826, 21, 6, None),
        (3529, "Wildercress in Daemonheim", 10, 17450, 21, 6, None),
        (3530, "Valerian in Daemonheim", 18, 17827, 21, 6, None),
        (3531, "Blightleaf in Daemonheim", 20, 17452, 21, 6, None),
        (3532, "Aloe in Daemonheim", 29, 17828, 21, 6, None),
        (3533, "Roseblood in Daemonheim", 30, 17454, 21, 6, None),
        (3534, "Gissel mushroom in Daemonheim", 34, 17824, 21, 6, None),
        (3535, "Wormwood in Daemonheim", 40, 17829, 21, 6, None),
        (3536, "Bryll in Daemonheim", 40, 17456, 21, 6, None),
        (3537, "Duskweed in Daemonheim", 50, 17458, 21, 6, None),
        (3538, "Magebane in Daemonheim", 51, 17830, 21, 6, None),
        (3539, "Soulbell in Daemonheim", 60, 17460, 21, 6, None),
        (3540, "Featherfoil in Daemonheim", 62, 17831, 21, 6, None),
        (3541, "Edicap mushroom in Daemonheim", 68, 17825, 21, 6, None),
        (3542, "Ectograss in Daemonheim", 70, 17462, 21, 6, None),
        (3543, "Winter's grip in Daemonheim", 73, 17832, 21, 6, None),
        (3544, "Runeleaf in Daemonheim", 80, 17464, 21, 6, None),
        (3545, "Lycopus in Daemonheim", 84, 17833, 21, 6, None),
        (3546, "Spiritbloom in Daemonheim", 90, 17466, 21, 6, None),
        (3547, "Buckthorn in Daemonheim", 95, 17834, 21, 6, None),
        (3548, "Skill mastery", 99, 9810, 21, 1, None),
    )
)
