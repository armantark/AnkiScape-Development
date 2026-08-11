"""Immutable, source-cited backend data for pre-EOC Farming.

The executable rows follow the closed Farming contract and its 2026-07-11
wiki-pin ledger.  Values that the ledger could not settle remain present as
``source_blocked`` metadata and are deliberately not executable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Optional, Tuple


FARM_MINUTES_PER_ANSWER = 6
COMPOST_BIN_CAPACITY = 15
LIVID_FARM_ALLOTMENT_PATCH_ID = "livid_farm_allotment"
LIVID_FARM_PROTECTION_SCROLL = "Patch protection scroll"


@dataclass(frozen=True)
class ProtectionPayment:
    items: Tuple[Tuple[str, int], ...]
    source: str


@dataclass(frozen=True)
class CropDefinition:
    id: str
    display_name: str
    patch_type: str
    seed_item: str
    output_item: Optional[str]
    level: int
    seeds: int
    planting_xp: Optional[float]
    harvest_xp: Optional[float]
    check_health_xp: Optional[float]
    stages: Optional[int]
    stage_minutes: Optional[int]
    disease_slots: Optional[int]
    base_lives: int = 0
    min_save_slots: int = 0
    max_save_slots: int = 0
    fixed_yield: Optional[int] = None
    regrowth_minutes: Optional[int] = None
    regrowth_range_minutes: Optional[Tuple[int, int]] = None
    protection: Optional[ProtectionPayment] = None
    disease_immune: bool = False
    magic_secateurs_eligible: bool = False
    source_blocked: Tuple[str, ...] = ()
    sources: Tuple[str, ...] = ()
    tree_id: Optional[str] = None
    root_item: Optional[str] = None
    harvest_tool: Optional[str] = "Spade"

    @property
    def runnable(self) -> bool:
        required = {"planting_xp", "stages", "stage_minutes", "yield", "harvest_xp", "quest_gate"}
        return not bool(required.intersection(self.source_blocked))


@dataclass(frozen=True)
class AccessGate:
    kind: str
    key: Optional[str] = None
    minimum: int = 0
    gates: Tuple["AccessGate", ...] = ()


@dataclass(frozen=True)
class PatchDefinition:
    id: str
    display_name: str
    complex_id: str
    patch_type: str
    access_gate: Optional[AccessGate] = None
    disease_free: bool = False
    crop_whitelist: Tuple[str, ...] = ()
    location_options: Tuple[str, ...] = ()
    fixed_crop_id: Optional[str] = None
    sources: Tuple[str, ...] = ("Farming/Patch locations oldid 6552430",)


@dataclass(frozen=True)
class CompostTier:
    id: str
    item: Optional[str]
    application_xp: float
    disease_factor: float
    extra_lives: int
    maturation_minutes: int
    source_range_minutes: Optional[Tuple[int, int]]
    sources: Tuple[str, ...]


@dataclass(frozen=True)
class CompostBinDefinition:
    id: str
    display_name: str
    complex_id: str
    access_gate: Optional[AccessGate] = None
    sources: Tuple[str, ...] = ("Farming/Patch locations oldid 6552430",)


@dataclass(frozen=True)
class FarmingItem:
    id: str
    display_name: str
    category: str
    source: str
    tradeable: bool = True


@dataclass(frozen=True)
class FarmingAsset:
    item_id: str
    item_name: str
    relative_path: str
    source_hint: str


@dataclass(frozen=True)
class FarmingInterfaceAsset:
    id: str
    display_name: str
    relative_path: Optional[str] = None
    wiki_title: Optional[str] = None
    reuse_item: Optional[str] = None


GM_SEED = "2011Scape rev-667 Seed.kt and SeedType.kt"
GM_HARVEST = "2011Scape rev-667 HarvestingHandler.kt"
SEEDS_PIN = "Seeds oldid 6565109"
WILLOW_BRANCH_PIN = "Willow branch oldid 6092914 (2012-08-14T16:12:52Z)"
FARMING_PIN = "Farming oldid 6565110"
HABITAT_PIN = "Herblore Habitat oldid 6513740"

# PLACEHOLDER(farming.vine_herb_base_lives): a period vine-herb harvest
# routine or qualified cutoff sample would settle the base lives.
VINE_HERB_BASE_LIVES = 3
VINE_HERB_MIN_SAVE_SLOTS = 67
VINE_HERB_MAX_SAVE_SLOTS = 80
# Darkan FarmPatch.java:468-470 rolls Utils.random(128) < (6 - compostLevel).
VINE_HERB_DISEASE_SLOTS = 6

FARMING_SOURCE_BLOCKED: Mapping[str, str] = MappingProxyType({
    "watering_growth_multiplier": "The ledger does not settle an exact pre-EOC growth multiplier.",
    "watering_yield_effect": "The ledger does not settle an exact pre-EOC yield effect.",
})


def _payment(source: str, **items: int) -> ProtectionPayment:
    return ProtectionPayment(tuple(items.items()), source)


def _crop(
    crop_id: str,
    display_name: str,
    patch_type: str,
    seed_item: str,
    output_item: Optional[str],
    level: int,
    seeds: int,
    planting_xp: Optional[float],
    harvest_xp: Optional[float],
    stages: Optional[int],
    stage_minutes: Optional[int],
    *,
    check: Optional[float] = None,
    disease_slots: Optional[int] = None,
    base_lives: int = 0,
    min_slots: int = 0,
    max_slots: int = 0,
    fixed_yield: Optional[int] = None,
    regrowth: Optional[int] = None,
    regrowth_range: Optional[Tuple[int, int]] = None,
    protection: Optional[ProtectionPayment] = None,
    immune: bool = False,
    secateurs: bool = False,
    blocked: Tuple[str, ...] = (),
    sources: Tuple[str, ...] = (GM_SEED, SEEDS_PIN),
    tree_id: Optional[str] = None,
    root_item: Optional[str] = None,
    harvest_tool: Optional[str] = "Spade",
) -> CropDefinition:
    return CropDefinition(
        crop_id, display_name, patch_type, seed_item, output_item, level, seeds,
        planting_xp, harvest_xp, check, stages, stage_minutes, disease_slots,
        base_lives, min_slots, max_slots, fixed_yield, regrowth, regrowth_range,
        protection, immune, secateurs, blocked, sources, tree_id, root_item,
        harvest_tool,
    )


_ALLOTMENTS = (
    _crop("potato", "Potato", "allotment", "Potato seed", "Potato", 1, 3, 8.0, 9.0, 4, 10, disease_slots=30, base_lives=3, min_slots=130, max_slots=200, protection=_payment(SEEDS_PIN, Compost=2), secateurs=True),
    _crop("onion", "Onion", "allotment", "Onion seed", "Onion", 5, 3, 9.5, 10.5, 4, 10, disease_slots=30, base_lives=3, min_slots=130, max_slots=200, protection=_payment(SEEDS_PIN, **{"Potatoes (10)": 1}), secateurs=True),
    _crop("cabbage", "Cabbage", "allotment", "Cabbage seed", "Cabbage", 7, 3, 10.0, 11.5, 4, 10, disease_slots=30, base_lives=3, min_slots=130, max_slots=200, protection=_payment(SEEDS_PIN, **{"Onions (10)": 1}), secateurs=True),
    _crop("tomato", "Tomato", "allotment", "Tomato seed", "Tomato", 12, 3, 12.5, 14.0, 4, 10, disease_slots=30, base_lives=3, min_slots=130, max_slots=200, protection=_payment(SEEDS_PIN, **{"Cabbages (10)": 2}), secateurs=True),
    _crop("sweetcorn", "Sweetcorn", "allotment", "Sweetcorn seed", "Sweetcorn", 20, 3, 17.0, 19.0, 6, 10, disease_slots=30, base_lives=3, min_slots=130, max_slots=200, protection=_payment(SEEDS_PIN, **{"Jute fibre": 10}), secateurs=True),
    _crop("strawberry", "Strawberry", "allotment", "Strawberry seed", "Strawberry", 31, 3, 26.0, 29.0, 6, 10, disease_slots=30, base_lives=3, min_slots=130, max_slots=200, protection=_payment(SEEDS_PIN, **{"Apples (5)": 1}), secateurs=True),
    _crop("watermelon", "Watermelon", "allotment", "Watermelon seed", "Watermelon", 47, 3, 48.5, 54.5, 8, 10, disease_slots=30, base_lives=3, min_slots=130, max_slots=200, protection=_payment(SEEDS_PIN, **{"Curry leaf": 10}), secateurs=True),
)

_FLOWERS = (
    _crop("marigold", "Marigold", "flower", "Marigold seed", "Marigolds", 2, 1, 8.5, 47.0, 4, 5, disease_slots=30, fixed_yield=1),
    _crop("rosemary", "Rosemary", "flower", "Rosemary seed", "Rosemary", 11, 1, 12.0, 66.5, 4, 5, disease_slots=25, fixed_yield=1),
    _crop("nasturtium", "Nasturtium", "flower", "Nasturtium seed", "Nasturtiums", 24, 1, 19.5, 111.0, 4, 5, disease_slots=20, fixed_yield=1),
    _crop("woad", "Woad", "flower", "Woad seed", "Woad leaf", 25, 1, 20.5, 115.5, 4, 5, disease_slots=15, fixed_yield=3),
    _crop("limpwurt", "Limpwurt", "flower", "Limpwurt seed", "Limpwurt root", 26, 1, 21.5, 120.0, 4, 5, disease_slots=10, fixed_yield=3),
    _crop("scarecrow", "Scarecrow", "flower", "Scarecrow", None, 23, 1, 0.0, 0.0, 0, 0, fixed_yield=0, immune=True, sources=("Scarecrow oldid 6487851",)),
    _crop("white_lily", "White lily", "flower", "White lily seed", "White lily", 52, 1, None, 250.0, 4, 20, fixed_yield=1, blocked=("planting_xp",), sources=("White lily oldid 6579222", SEEDS_PIN)),
)


def _herb(crop_id: str, name: str, level: int, plant: float, harvest: Optional[float], minimum: int, *, maximum: int = 80, blocked: Tuple[str, ...] = ()) -> CropDefinition:
    return _crop(crop_id, name, "herb", f"{name} seed", f"Grimy {name.lower()}", level, 1, plant, harvest, 4, 20, disease_slots=27, base_lives=3, min_slots=minimum, max_slots=maximum, secateurs=True, blocked=blocked)


_HERBS = (
    _herb("guam", "Guam", 9, 11.0, 12.5, 24),
    _herb("marrentill", "Marrentill", 14, 13.5, 15.0, 28),
    _herb("tarromin", "Tarromin", 19, 16.0, 18.0, 31),
    _herb("harralander", "Harralander", 26, 21.5, 24.0, 36),
    _herb("ranarr", "Ranarr", 32, 27.0, 30.5, 39),
    _herb("spirit_weed", "Spirit weed", 36, 32.0, 36.0, 43),
    _herb("toadflax", "Toadflax", 38, 34.0, 38.5, 43),
    _herb("irit", "Irit", 44, 43.0, 48.5, 46),
    _herb("avantoe", "Avantoe", 50, 54.5, 61.5, 50),
    _herb("kwuarm", "Kwuarm", 56, 69.0, 78.0, 54),
    _herb("snapdragon", "Snapdragon", 62, 87.5, 98.5, 57),
    _herb("cadantine", "Cadantine", 67, 106.5, 120.0, 60),
    _herb("lantadyme", "Lantadyme", 73, 134.5, 151.5, 64),
    _herb("dwarf_weed", "Dwarf weed", 79, 170.5, 192.0, 67),
    _herb("torstol", "Torstol", 85, 199.5, 224.5, 71),
    _herb("wergali", "Wergali", 46, 52.8, None, 48, blocked=("harvest_xp",)),
    _herb("fellstalk", "Fellstalk", 91, 225.0, 315.6, 15, maximum=90),
    _crop("goutweed", "Goutweed", "herb", "Gout tuber", "Goutweed", 29, 1, 105.0, 45.0, 4, 20, disease_slots=27, base_lives=3, min_slots=57, max_slots=80, blocked=("yield", "quest_gate"), sources=("Goutweed oldid 5668713", SEEDS_PIN)),
)


def _hops(crop_id: str, name: str, seed_item: str, level: int, plant: float, harvest: float, stages: int, disease: int, protection: ProtectionPayment, seeds: int = 4) -> CropDefinition:
    return _crop(crop_id, name, "hops", seed_item, "Jute fibre" if crop_id == "jute" else ("Barley" if crop_id == "barley" else name), level, seeds, plant, harvest, stages, 10, disease_slots=disease, base_lives=3, min_slots=100, max_slots=180, protection=protection, secateurs=True)


_HOPS = (
    _hops("barley", "Barley", "Barley seed", 3, 8.5, 9.5, 4, 15, _payment(SEEDS_PIN, Compost=3)),
    _hops("hammerstone", "Hammerstone hops", "Hammerstone seed", 4, 9.0, 10.0, 4, 14, _payment(SEEDS_PIN, Marigolds=1)),
    _hops("asgarnian", "Asgarnian hops", "Asgarnian seed", 8, 10.9, 12.0, 5, 13, _payment(SEEDS_PIN, **{"Onions (10)": 1})),
    _hops("jute", "Jute", "Jute seed", 13, 13.0, 14.5, 5, 12, _payment(SEEDS_PIN, **{"Barley malt": 6}), seeds=3),
    _hops("yanillian", "Yanillian hops", "Yanillian seed", 16, 14.5, 16.0, 6, 11, _payment(SEEDS_PIN, **{"Tomatoes (5)": 1})),
    _hops("krandorian", "Krandorian hops", "Krandorian seed", 21, 17.5, 19.5, 7, 10, _payment(SEEDS_PIN, **{"Cabbages (10)": 3})),
    _hops("wildblood", "Wildblood hops", "Wildblood seed", 28, 23.0, 26.0, 8, 9, _payment(SEEDS_PIN, Nasturtiums=1)),
)


def _bush(crop_id: str, name: str, output: str, level: int, plant: float, check: float, harvest: float, stages: int, protection: Optional[ProtectionPayment], *, immune: bool = False) -> CropDefinition:
    return _crop(crop_id, name, "bush", f"{name} seed", output, level, 1, plant, harvest, stages, 20, check=check, disease_slots=0 if immune else 15, fixed_yield=4, regrowth=20, protection=protection, immune=immune)


_BUSHES = (
    _bush("redberry", "Redberry", "Redberries", 10, 11.5, 64.0, 4.5, 5, _payment(SEEDS_PIN, **{"Cabbages (10)": 4})),
    _bush("cadavaberry", "Cadavaberry", "Cadava berries", 22, 18.0, 102.5, 7.0, 6, _payment(SEEDS_PIN, **{"Tomatoes (5)": 3})),
    _bush("dwellberry", "Dwellberry", "Dwellberries", 36, 31.5, 177.5, 12.0, 7, _payment(SEEDS_PIN, **{"Strawberries (5)": 3})),
    _bush("jangerberry", "Jangerberry", "Jangerberries", 48, 50.5, 284.5, 19.0, 8, _payment(SEEDS_PIN, Watermelon=6)),
    _bush("whiteberry", "Whiteberry", "White berries", 59, 78.0, 437.5, 29.0, 8, _payment(SEEDS_PIN, **{"Bittercap mushroom": 8})),
    _bush("poison_ivy", "Poison ivy", "Poison ivy berries", 70, 120.0, 675.0, 45.0, 8, None, immune=True),
)


def _tree(crop_id: str, name: str, seed: str, level: int, plant: float, check: float, stages: int, disease: int, protection: ProtectionPayment) -> CropDefinition:
    return _crop(crop_id, name, "tree", f"{name} sapling", None, level, 1, plant, 0.0, stages, 40, check=check, disease_slots=disease, fixed_yield=0, protection=protection, tree_id=crop_id, root_item=f"{name} roots", sources=(GM_SEED, "Tree patch oldid 6531843", SEEDS_PIN))


_TREES = (
    _tree("oak", "Oak", "Acorn", 15, 14.0, 467.3, 5, 17, _payment(SEEDS_PIN, **{"Tomatoes (5)": 1})),
    _crop(
        "willow",
        "Willow",
        "tree",
        "Willow sapling",
        "Willow branch",
        30,
        1,
        25.0,
        0.0,
        6,
        40,
        check=1456.3,
        disease_slots=15,
        fixed_yield=6,
        regrowth=5,
        protection=_payment(SEEDS_PIN, **{"Apples (5)": 1}),
        sources=(
            GM_SEED,
            "Tree patch oldid 6531843",
            SEEDS_PIN,
            WILLOW_BRANCH_PIN,
            "Darkan FarmPatch.java / HarvestPatch.java @ ee180fe",
        ),
        tree_id="willow",
        root_item="Willow roots",
        harvest_tool="Secateurs",
    ),
    _tree("maple", "Maple", "Maple seed", 45, 45.0, 3403.4, 8, 13, _payment(SEEDS_PIN, **{"Oranges (5)": 1})),
    _tree("yew", "Yew", "Yew seed", 60, 81.0, 7069.9, 10, 11, _payment(SEEDS_PIN, **{"Cactus spine": 10})),
    _tree("magic", "Magic", "Magic seed", 75, 145.5, 13768.3, 12, 9, _payment(SEEDS_PIN, Coconut=25)),
)


def _fruit(crop_id: str, name: str, sapling_name: str, output: str, level: int, plant: float, check: float, harvest: float, protection: ProtectionPayment) -> CropDefinition:
    return _crop(crop_id, name, "fruit_tree", sapling_name, output, level, 1, plant, harvest, 6, 160, check=check, disease_slots=18, fixed_yield=6, regrowth=40, protection=protection, sources=(GM_SEED, SEEDS_PIN, HABITAT_PIN))


_FRUIT_TREES = (
    _fruit("apple", "Apple tree", "Apple sapling", "Cooking apple", 27, 22.0, 1199.5, 8.5, _payment(SEEDS_PIN, Sweetcorn=9)),
    _fruit("banana", "Banana tree", "Banana sapling", "Banana", 33, 28.0, 1750.5, 10.5, _payment(SEEDS_PIN, **{"Apples (5)": 4})),
    _fruit("orange", "Orange tree", "Orange sapling", "Orange", 39, 35.5, 2470.2, 13.0, _payment(SEEDS_PIN, **{"Strawberries (5)": 3})),
    _fruit("curry", "Curry tree", "Curry sapling", "Curry leaf", 42, 40.0, 2906.9, 15.0, _payment(SEEDS_PIN, **{"Bananas (5)": 5})),
    _fruit("pineapple", "Pineapple plant", "Pineapple sapling", "Pineapple", 51, 57.0, 4605.7, 21.5, _payment(SEEDS_PIN, Watermelon=10)),
    _fruit("papaya", "Papaya tree", "Papaya sapling", "Papaya fruit", 57, 72.0, 6146.4, 27.0, _payment(SEEDS_PIN, Pineapple=10)),
    _fruit("palm", "Palm tree", "Palm sapling", "Coconut", 68, 110.5, 10150.1, 41.5, _payment(SEEDS_PIN, **{"Papaya fruit": 15})),
)


_SPECIAL = (
    _crop("calquat", "Calquat", "calquat", "Calquat sapling", "Calquat fruit", 72, 1, 129.5, 48.5, 8, 160, check=12096.0, disease_slots=18, fixed_yield=6, regrowth=40, protection=_payment(SEEDS_PIN, **{"Poison ivy berries": 8}), sources=(SEEDS_PIN, "Calquat Tree oldid 5539026")),
    _crop("cactus", "Cactus", "cactus", "Cactus seed", "Cactus spine", 55, 1, 66.5, 25.0, 7, 80, check=374.0, disease_slots=6, fixed_yield=3, regrowth=25, protection=_payment(SEEDS_PIN, **{"Cadava berries": 6}), sources=(SEEDS_PIN, "Cactus oldid 6125072", "Darkan 7e7d67b FarmPatch.java:455-483")),
    _crop("bittercap", "Bittercap mushroom", "mushroom", "Mushroom spore", "Bittercap mushroom", 53, 1, 61.5, 57.7, 6, 40, disease_slots=6, fixed_yield=6, sources=(SEEDS_PIN, "Mushroom patch oldid 5432839", "Darkan 7e7d67b FarmPatch.java:455-483")),
    _crop("morchella", "Morchella mushroom", "mushroom", "Morchella mushroom spore", "Morchella mushroom", 74, 1, 160.0, 77.7, 6, 40, disease_slots=6, fixed_yield=9, sources=(SEEDS_PIN, "Mushroom patch oldid 5432839", "Darkan 7e7d67b FarmPatch.java:455-483")),
    _crop("belladonna", "Belladonna", "belladonna", "Belladonna seed", "Cave nightshade", 63, 1, 91.0, 512.0, 4, 80, disease_slots=6, fixed_yield=1, sources=(SEEDS_PIN, "Darkan 7e7d67b FarmPatch.java:455-483")),
    _crop("evil_turnip", "Evil turnip", "evil_turnip", "Evil turnip seed", "Evil turnip", 42, 1, 41.0, 46.0, 1, 5, fixed_yield=1, immune=True, sources=(SEEDS_PIN, "Evil turnip oldid 6538769", "Darkan 7e7d67b disease immunity")),
    _crop("spirit_tree", "Spirit tree", "spirit_tree", "Spirit sapling", None, 83, 1, 199.5, 0.0, None, None, check=19301.8, fixed_yield=0, protection=_payment(SEEDS_PIN, **{"Monkey nuts": 5, "Monkey bar": 1, "Ground Suqah tooth": 1}), blocked=("stages", "stage_minutes"), sources=(SEEDS_PIN, "Spirit tree oldid 6549224")),
    _crop("jade_vine", "Jade vine", "jade_vine", "Jade vine seed", "Jade vine branch", 53, 1, 50.0, 30.0, 6, 160, check=1500.0, disease_slots=6, fixed_yield=6, regrowth_range=(30, 60), protection=_payment(SEEDS_PIN, **{"Wildblood hops": 10}), sources=(SEEDS_PIN, "Jade vine oldid 6579442", "Darkan 7e7d67b FarmPatch.java:455-483")),
    _crop(
        "white_tree",
        "White tree",
        "white_tree",
        "White tree sapling",
        "White tree fruit",
        25,
        1,
        0.0,
        12.0,
        0,
        0,
        fixed_yield=4,
        regrowth=FARM_MINUTES_PER_ANSWER,
        immune=True,
        sources=(
            "White tree fruit oldid 5838367, 2012-06-26T04:41:55Z",
            "One fruit per answered card is the disclosed fast-respawn abstraction",
        ),
        harvest_tool=None,
    ),
)


def _habitat(crop_id: str, name: str, patch_type: str, level: int, plant: Optional[float], harvest: Optional[float], check: Optional[float], protection: Optional[ProtectionPayment], blocked: Tuple[str, ...]) -> CropDefinition:
    vine_herb = patch_type == "vine_herb"
    return _crop(
        crop_id,
        name,
        patch_type,
        f"{name} seed",
        name if not vine_herb else f"Grimy {name.lower()}",
        level,
        1,
        plant,
        harvest,
        4 if vine_herb else None,
        20 if vine_herb else None,
        check=check,
        disease_slots=VINE_HERB_DISEASE_SLOTS if vine_herb else None,
        base_lives=VINE_HERB_BASE_LIVES if vine_herb else 0,
        min_slots=VINE_HERB_MIN_SAVE_SLOTS if vine_herb else 0,
        max_slots=VINE_HERB_MAX_SAVE_SLOTS if vine_herb else 0,
        fixed_yield=None,
        protection=protection,
        blocked=blocked,
        sources=(HABITAT_PIN, SEEDS_PIN, "Darkan 7e7d67b ProduceType.java:27-121, PatchType.java, and FarmPatch.java:468-470") if vine_herb else (HABITAT_PIN, SEEDS_PIN),
    )


_HABITAT = (
    *(_habitat(f"{color}_blossom", f"{color.title()} blossom", "vine_flower", 54, 52.0, 255.0, None, None, ("stages", "stage_minutes", "yield")) for color in ("red", "blue", "green")),
    _habitat("erzille", "Erzille", "vine_herb", 58, 87.0, 87.0, None, _payment(HABITAT_PIN, **{"Green blossom": 3}), ()),
    _habitat("argway", "Argway", "vine_herb", 65, 110.0, 125.0, None, _payment(HABITAT_PIN, **{"Red blossom": 4}), ()),
    _habitat("ugune", "Ugune", "vine_herb", 70, 135.0, 152.0, None, _payment(HABITAT_PIN, **{"Blue blossom": 3}), ()),
    _habitat("shengo", "Shengo", "vine_herb", 76, 140.5, 160.0, None, _payment(HABITAT_PIN, Lergberry=5), ()),
    _habitat("samaden", "Samaden", "vine_herb", 80, 170.0, 190.0, None, _payment(HABITAT_PIN, Kalferberry=5), ()),
    _habitat("lergberry", "Lergberry", "vine_bush", 61, 145.5, 31.5, 236.3, _payment(HABITAT_PIN, **{"Red blossom": 3}), ("stages", "stage_minutes", "yield")),
    _habitat("kalferberry", "Kalferberry", "vine_bush", 77, None, 52.5, None, _payment(HABITAT_PIN, Lergberry=3), ("planting_xp", "stages", "stage_minutes", "yield")),
)


FARMING_CROPS: Tuple[CropDefinition, ...] = _ALLOTMENTS + _FLOWERS + _HERBS + _HOPS + _BUSHES + _TREES + _FRUIT_TREES + _SPECIAL + _HABITAT
FARMING_CROPS_BY_ID: Mapping[str, CropDefinition] = MappingProxyType({crop.id: crop for crop in FARMING_CROPS})


def _quest(quest_id: str) -> AccessGate:
    return AccessGate("quest", quest_id)


def _skill(skill_id: str, minimum: int) -> AccessGate:
    return AccessGate("skill", skill_id, minimum)


def _region(region_id: str) -> AccessGate:
    return AccessGate("region", region_id)


def _all(*gates: AccessGate) -> AccessGate:
    return AccessGate("all", gates=gates)


def _state(key: str) -> AccessGate:
    return AccessGate("state", key)


def _patch(
    patch_id: str,
    name: str,
    complex_id: str,
    patch_type: str,
    gate: Optional[AccessGate] = None,
    *,
    disease_free: bool = False,
    whitelist: Tuple[str, ...] = (),
    locations: Tuple[str, ...] = (),
    fixed_crop_id: Optional[str] = None,
    sources: Tuple[str, ...] = ("Farming/Patch locations oldid 6552430",),
) -> PatchDefinition:
    return PatchDefinition(
        patch_id,
        name,
        complex_id,
        patch_type,
        gate,
        disease_free,
        whitelist,
        locations,
        fixed_crop_id,
        sources,
    )


_PATCHES = []
for _complex_id, _name, _gate in (
    ("falador", "South Falador", None),
    ("phasmatys", "West of Port Phasmatys", _region("morytania")),
    ("catherby", "North Catherby", None),
    ("ardougne", "North Ardougne", None),
):
    _PATCHES.extend((
        _patch(f"{_complex_id}_allotment_north", f"{_name} allotment north", _complex_id, "allotment", _gate),
        _patch(f"{_complex_id}_allotment_south", f"{_name} allotment south", _complex_id, "allotment", _gate),
        _patch(f"{_complex_id}_flower", f"{_name} flower", _complex_id, "flower", _gate),
        _patch(f"{_complex_id}_herb", f"{_name} herb", _complex_id, "herb", _gate),
    ))

_PATCHES.extend((
    _patch("wilderness_limpwurt", "Wilderness western ruins flower", "wilderness", "flower", _quest("spirit_of_summer"), whitelist=("limpwurt",)),
    _patch("harmony_allotment", "Harmony Island allotment", "harmony", "allotment", _quest("the_great_brain_robbery")),
    _patch("taverley_potato", "Taverley potato patch", "taverley", "allotment", disease_free=True, whitelist=("potato",)),
    _patch(
        LIVID_FARM_ALLOTMENT_PATCH_ID,
        "Livid Farm allotment",
        "livid_farm",
        "allotment",
        _state("farm_livid_patch_active"),
        sources=("Livid Farm oldid 6569596, 2012-11-17T21:40:18Z",),
    ),
    _patch("trollheim_herb", "Troll Stronghold herb", "trollheim", "herb", _quest("my_arms_big_adventure"), disease_free=True),
    _patch("lumbridge_hops", "North Lumbridge hops", "lumbridge", "hops"),
    _patch("mcgrubor_hops", "North McGrubor's Wood hops", "mcgrubor", "hops"),
    _patch("yanille_hops", "Yanille hops", "yanille", "hops"),
    _patch("entrana_hops", "Entrana hops", "entrana", "hops"),
    _patch("champions_bush", "West Champions' Guild bush", "champions", "bush"),
    _patch("rimmington_bush", "Rimmington bush", "rimmington", "bush"),
    _patch("ardougne_bush", "South Ardougne bush", "south_ardougne", "bush"),
    _patch("etceteria_bush", "Etceteria bush", "etceteria", "bush", _quest("throne_of_miscellania")),
    _patch("lumbridge_tree", "West Lumbridge tree", "lumbridge", "tree"),
    _patch("varrock_tree", "Varrock Castle tree", "varrock", "tree"),
    _patch(
        "varrock_white_tree",
        "Varrock Palace White Tree",
        "varrock",
        "white_tree",
        _quest("garden_of_tranquillity"),
        disease_free=True,
        whitelist=("white_tree",),
        fixed_crop_id="white_tree",
        sources=("White tree fruit oldid 5838367, 2012-06-26T04:41:55Z",),
    ),
    _patch("falador_tree", "Falador Park tree", "falador_park", "tree"),
    _patch("taverley_tree", "Taverley tree", "taverley", "tree"),
    _patch("gnome_stronghold_tree", "Tree Gnome Stronghold tree", "gnome_stronghold", "tree"),
    _patch("gnome_stronghold_fruit", "Tree Gnome Stronghold fruit tree", "gnome_stronghold", "fruit_tree"),
    _patch("catherby_fruit", "East Catherby fruit tree", "catherby", "fruit_tree"),
    _patch("gnome_village_fruit", "Tree Gnome Village fruit tree", "gnome_village", "fruit_tree"),
    _patch("brimhaven_fruit", "North Brimhaven fruit tree", "brimhaven", "fruit_tree"),
    _patch("lletya_fruit", "Lletya fruit tree", "lletya", "fruit_tree", _quest("mournings_end_part_i")),
    _patch("habitat_fruit", "Herblore Habitat fruit tree", "habitat", "fruit_tree"),
    _patch("habitat_vine_flower", "Herblore Habitat vine flower", "habitat", "vine_flower"),
    _patch("habitat_vine_bush", "Herblore Habitat vine bush", "habitat", "vine_bush"),
    _patch("habitat_vine_herb_west", "Herblore Habitat west vine herb", "habitat", "vine_herb"),
    _patch("habitat_vine_herb_east", "Herblore Habitat east vine herb", "habitat", "vine_herb", _skill("agility", 55)),
    _patch("spirit_tree_primary", "Spirit tree slot 1", "spirit_tree", "spirit_tree", _skill("farming", 83), locations=("Etceteria", "East Port Sarim", "North Brimhaven")),
    _patch("spirit_tree_secondary", "Spirit tree slot 2", "spirit_tree", "spirit_tree", _all(_skill("farming", 86), _quest("the_prisoner_of_glouphrie")), locations=("Etceteria", "East Port Sarim", "North Brimhaven")),
    _patch("draynor_evil_turnip", "Draynor Manor evil turnip", "draynor", "evil_turnip"),
    _patch("canifis_mushroom", "West Canifis mushroom", "canifis", "mushroom", _region("morytania")),
    _patch("al_kharid_cactus", "Al Kharid cactus", "al_kharid", "cactus"),
    _patch("draynor_belladonna", "Draynor Manor belladonna", "draynor", "belladonna"),
    _patch("tai_bwo_calquat", "Tai Bwo Wannai calquat", "tai_bwo", "calquat"),
    _patch("handelmort_jade_vine", "Handelmort Mansion jade vine", "ardougne", "jade_vine", _quest("back_to_my_roots")),
))

FARMING_PATCHES: Tuple[PatchDefinition, ...] = tuple(_PATCHES)
FARMING_PATCHES_BY_ID: Mapping[str, PatchDefinition] = MappingProxyType({patch.id: patch for patch in FARMING_PATCHES})

FARMING_COMPOST_BINS: Tuple[CompostBinDefinition, ...] = (
    CompostBinDefinition("falador_bin", "South Falador compost bin", "falador"),
    CompostBinDefinition("phasmatys_bin", "Port Phasmatys compost bin", "phasmatys", _region("morytania")),
    CompostBinDefinition("catherby_bin", "North Catherby compost bin", "catherby"),
    CompostBinDefinition("ardougne_bin", "North Ardougne compost bin", "ardougne"),
    CompostBinDefinition("taverley_bin", "Taverley compost bin", "taverley"),
    CompostBinDefinition("habitat_bin", "Herblore Habitat compost bin", "habitat", sources=(HABITAT_PIN,)),
)
FARMING_COMPOST_BINS_BY_ID: Mapping[str, CompostBinDefinition] = MappingProxyType({row.id: row for row in FARMING_COMPOST_BINS})

COMPOST_TIERS: Mapping[str, CompostTier] = MappingProxyType({
    "none": CompostTier("none", None, 0.0, 1.0, 0, 0, None, (GM_SEED,)),
    "compost": CompostTier("compost", "Compost", 18.0, 0.28, 1, 45, (35, 50), ("Compost oldid 6337625", "GM CompostState.kt")),
    "supercompost": CompostTier("supercompost", "Supercompost", 26.0, 0.14, 2, 90, (90, 90), ("Supercompost oldid 6337626", "GM CompostState.kt")),
})

REGULAR_COMPOST_INPUTS = frozenset({"Weeds", "Potato", "Onion", "Cabbage", "Tomato", "Barley", "Hammerstone hops"})
SUPERCOMPOST_INPUTS = frozenset(
    {
        "Pineapple",
        "Watermelon",
        "Papaya fruit",
        "Coconut",
        "Jangerberries",
        "Poison ivy berries",
        "White tree fruit",
    }
)

FLOWER_PROTECTION: Mapping[str, frozenset[str]] = MappingProxyType({
    "marigold": frozenset({"potato", "onion", "tomato"}),
    "rosemary": frozenset({"cabbage"}),
    "nasturtium": frozenset({"watermelon"}),
    "scarecrow": frozenset({"sweetcorn"}),
    "white_lily": frozenset(crop.id for crop in _ALLOTMENTS),
})

SAPLING_RECIPES: Mapping[str, Tuple[str, str, str]] = MappingProxyType({
    "oak": ("Acorn", "Oak seedling", "Oak sapling"),
    "willow": ("Willow seed", "Willow seedling", "Willow sapling"),
    "maple": ("Maple seed", "Maple seedling", "Maple sapling"),
    "yew": ("Yew seed", "Yew seedling", "Yew sapling"),
    "magic": ("Magic seed", "Magic seedling", "Magic sapling"),
    "apple": ("Apple tree seed", "Apple seedling", "Apple sapling"),
    "banana": ("Banana tree seed", "Banana seedling", "Banana sapling"),
    "orange": ("Orange tree seed", "Orange seedling", "Orange sapling"),
    "curry": ("Curry tree seed", "Curry seedling", "Curry sapling"),
    "pineapple": ("Pineapple seed", "Pineapple seedling", "Pineapple sapling"),
    "papaya": ("Papaya tree seed", "Papaya seedling", "Papaya sapling"),
    "palm": ("Palm tree seed", "Palm seedling", "Palm sapling"),
    "calquat": ("Calquat tree seed", "Calquat seedling", "Calquat sapling"),
    "spirit_tree": ("Spirit seed", "Spirit seedling", "Spirit sapling"),
})


def _slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


_item_names = {
    "Rake", "Seed dibber", "Spade", "Gardening trowel", "Watering can", "Watering can (8)",
    "Plant cure", "Secateurs", "Magic secateurs", "Plant pot", "Bucket", "Compost", "Supercompost", "Weeds",
    LIVID_FARM_PROTECTION_SCROLL,
}
for _crop_row in FARMING_CROPS:
    _item_names.add(_crop_row.seed_item)
    if _crop_row.output_item:
        _item_names.add(_crop_row.output_item)
    if _crop_row.root_item:
        _item_names.add(_crop_row.root_item)
    if _crop_row.protection:
        _item_names.update(item for item, _ in _crop_row.protection.items)
for _seed, _seedling, _sapling in SAPLING_RECIPES.values():
    _item_names.update((_seed, _seedling, _sapling))

FARMING_ITEMS: Tuple[FarmingItem, ...] = tuple(
    FarmingItem(
        f"farming_{_slug(name)}",
        name,
        "tool" if name in {"Rake", "Seed dibber", "Spade", "Gardening trowel", "Watering can", "Watering can (8)", "Secateurs", "Magic secateurs"} else "material",
        (
            "Livid Farm oldid 6569596; OpenRS2 rev 736/741/742 item 21515"
            if name == LIVID_FARM_PROTECTION_SCROLL
            else "Farming ledger oldids 6565109/6565110 and cited crop rows"
        ),
        name not in {"Magic secateurs"},
    )
    for name in sorted(_item_names)
)
_FARMING_ITEM_OVERRIDES: Mapping[str, Mapping[str, object]] = MappingProxyType(
    {
        "Secateurs": MappingProxyType(
            {
                "source_item_id": 5329,
                "stackable": False,
                "tradeable": True,
                "source": "OpenRS2 rev-742 item 5329; Willow branch oldid 6092914",
            }
        ),
        "Magic secateurs": MappingProxyType(
            {
                "source_item_id": 7409,
                "stackable": False,
                "tradeable": False,
                "source": "OpenRS2 rev-742 item 7409; Willow branch oldid 6092914",
            }
        ),
        "Willow branch": MappingProxyType(
            {
                "source_item_id": 5933,
                "stackable": False,
                "tradeable": True,
                "source": "Willow branch oldid 6092914; OpenRS2 rev-742 item 5933",
            }
        ),
    }
)

FARMING_ITEM_DATA: Mapping[str, Mapping[str, object]] = MappingProxyType({
    item.display_name: MappingProxyType({
        "category": item.category,
        "tradeable": item.tradeable,
        "source": item.source,
        "farming_item_id": item.id,
        **_FARMING_ITEM_OVERRIDES.get(item.display_name, {}),
    })
    for item in FARMING_ITEMS
})

FARMING_ASSET_MANIFEST: Tuple[FarmingAsset, ...] = tuple(
    FarmingAsset(item.id, item.display_name, f"farmingitems/{_slug(item.display_name)}.png", "Pinned pre-EOC RuneScape Wiki or period cache")
    for item in FARMING_ITEMS
)

FARMING_INTERFACE_ASSET_MANIFEST: Tuple[FarmingInterfaceAsset, ...] = (
    FarmingInterfaceAsset(
        "farming_skill_icon",
        "Farming skill icon",
        "icon/farming_icon.png",
        "Farming icon (detail).png",
    ),
    FarmingInterfaceAsset("farming_hud_sprout", "Farming sprout HUD icon", reuse_item="Oak seedling"),
    FarmingInterfaceAsset("farming_patch_empty", "Empty Farming patch", reuse_item="Weeds"),
    FarmingInterfaceAsset("farming_patch_growing", "Growing Farming patch", reuse_item="Oak seedling"),
    FarmingInterfaceAsset("farming_patch_ready", "Ready Farming patch", reuse_item="Potato"),
    FarmingInterfaceAsset("farming_patch_diseased", "Diseased Farming patch", reuse_item="Plant cure"),
    FarmingInterfaceAsset("farming_patch_dead", "Dead Farming patch", reuse_item="Spade"),
    FarmingInterfaceAsset("farming_patch_stump", "Farming tree stump", reuse_item="Oak roots"),
    FarmingInterfaceAsset("farming_compost_empty", "Empty compost bin", reuse_item="Bucket"),
    FarmingInterfaceAsset("farming_compost_filling", "Filling compost bin", reuse_item="Compost"),
    FarmingInterfaceAsset("farming_compost_ready", "Ready compost bin", reuse_item="Supercompost"),
)

FARMING_PATCH_VISUAL_ITEMS: Mapping[str, str] = MappingProxyType({
    "empty": "Weeds",
    "growing": "Oak seedling",
    "ready": "Potato",
    "diseased": "Plant cure",
    "dead": "Spade",
    "stump": "Oak roots",
})
FARMING_COMPOST_VISUAL_ITEMS: Mapping[str, str] = MappingProxyType({
    "empty": "Bucket",
    "filling": "Compost",
    "ready": "Supercompost",
})


assert len(FARMING_PATCHES) == 53
assert len(FARMING_COMPOST_BINS) == 6
assert "Patch bomb" not in FARMING_ITEM_DATA
