"""2011Scape-sourced Fishing data for AnkiScape.

The source rows come from the local 2011Scape rev 667 Fishing plugin. Fishing
implements source-backed spot/tool bindings as AnkiScape target methods, but
player-facing labels are output-first and deliberately omit reusable implements.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple


FISH_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/fishing/Fish.kt"
)
FISHING_TOOL_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/fishing/FishingTool.kt"
)
FISHING_SPOT_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/fishing/FishingSpot.kt"
)
FISHING_RUNTIME_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/fishing/Fishing.kt"
)
FISHING_BAIT_SHOP_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/areas/lumbridge/lumbridge_fishing_supplies.plugin.kts"
)
ITEMS_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/api/cfg/Items.kt"
)


@dataclass(frozen=True)
class FishingFish:
    id: str
    source_enum: str
    output_item: str
    source_item_id: int
    level: int
    min_chance: int
    max_chance: int
    base_exp: float
    strength_level: Optional[int] = None
    strength_exp: float = 0.0
    agility_level: Optional[int] = None
    agility_exp: float = 0.0
    source: str = FISH_SOURCE_PATH
    tradeable: bool = True


@dataclass(frozen=True)
class FishingMethod:
    id: str
    display_name: str
    source_tool: str
    fish_ids: Tuple[str, ...]
    bait_items: Tuple[str, ...] = ()
    source_spots: Tuple[str, ...] = ()
    source: str = FISHING_TOOL_SOURCE_PATH
    runtime_source: str = FISHING_RUNTIME_SOURCE_PATH
    status: str = "implemented"
    notes: str = ""


@dataclass(frozen=True)
class DeferredFishingContent:
    id: str
    display_name: str
    status: str
    reason: str
    source: str


FISHING_FISH: Tuple[FishingFish, ...] = (
    FishingFish("crayfish", "CRAYFISH", "Raw crayfish", 13435, 1, 58, 256, 10.0),
    FishingFish("shrimp", "SHRIMP", "Raw shrimps", 317, 1, 48, 256, 10.0),
    FishingFish("sardine", "SARDINE", "Raw sardine", 327, 5, 32, 192, 20.0),
    FishingFish("herring", "HERRING", "Raw herring", 345, 10, 24, 128, 30.0),
    FishingFish("anchovies", "ANCHOVIES", "Raw anchovies", 321, 15, 24, 128, 40.0),
    FishingFish("mackerel", "MACKEREL", "Raw mackerel", 353, 16, 5, 65, 20.0),
    FishingFish("cod", "COD", "Raw cod", 341, 23, 4, 55, 45.0),
    FishingFish("bass", "BASS", "Raw bass", 363, 46, 3, 40, 100.0),
    FishingFish("trout", "TROUT", "Raw trout", 335, 20, 32, 192, 50.0),
    FishingFish("pike", "PIKE", "Raw pike", 349, 25, 16, 96, 60.0),
    FishingFish("salmon", "SALMON", "Raw salmon", 331, 30, 16, 96, 70.0),
    FishingFish("tuna", "TUNA", "Raw tuna", 359, 35, 4, 48, 80.0),
    FishingFish("swordfish", "SWORDFISH", "Raw swordfish", 371, 50, 4, 48, 100.0),
    FishingFish("lobster", "LOBSTER", "Raw lobster", 377, 40, 6, 95, 90.0),
    FishingFish("shark", "SHARK", "Raw shark", 383, 76, 3, 40, 110.0),
    FishingFish(
        "leaping_trout",
        "LEAPING_TROUT",
        "Leaping trout",
        11328,
        48,
        20,
        40,
        50.0,
        strength_level=15,
        strength_exp=5.0,
        agility_level=15,
        agility_exp=5.0,
    ),
    FishingFish(
        "leaping_salmon",
        "LEAPING_SALMON",
        "Leaping salmon",
        11330,
        58,
        30,
        75,
        70.0,
        strength_level=30,
        strength_exp=6.0,
        agility_level=30,
        agility_exp=6.0,
    ),
    FishingFish(
        "leaping_sturgeon",
        "LEAPING_STURGEON",
        "Leaping sturgeon",
        11332,
        70,
        25,
        70,
        90.0,
        strength_level=45,
        strength_exp=7.0,
        agility_level=45,
        agility_exp=7.0,
    ),
    FishingFish("raw_karambwan", "RAW_KARAMBWAN", "Raw karambwan", 3142, 65, 5, 160, 50.0),
    FishingFish("rainbow_fish", "RAINBOW_FISH", "Raw rainbow fish", 10138, 38, 8, 64, 80.0),
    FishingFish("monkfish", "MONKFISH", "Raw monkfish", 7944, 62, 48, 90, 120.0),
    FishingFish("karambwanji", "KARAMBWANJI", "Raw karambwanji", 3150, 5, 100, 256, 5.0),
    FishingFish("slimy_eel", "SLIMY_EEL", "Slimy eel", 3379, 38, 10, 80, 65.0),
    FishingFish("cave_eel", "CAVE_EEL", "Raw cave eel", 5001, 28, 10, 80, 80.0),
    FishingFish("lava_eel", "LAVA_EEL", "Raw lava eel", 2148, 53, 16, 96, 60.0),
    FishingFish("frog_spawn", "FROG_SPAWN", "Frog spawn", 5004, 33, 16, 96, 75.0),
    FishingFish("cavefish", "CAVEFISH", "Raw cavefish", 15264, 85, 5, 17, 300.0),
    FishingFish("rocktail", "ROCKTAIL", "Raw rocktail", 15270, 90, 5, 15, 380.0),
)

FISH_BY_ID: Dict[str, FishingFish] = {fish.id: fish for fish in FISHING_FISH}

FISHING_METHODS: Tuple[FishingMethod, ...] = (
    FishingMethod(
        "catch_crayfish",
        "Catch crayfish",
        "CRAYFISH_CAGE",
        ("crayfish",),
        source_spots=("CRAYFISH_CAGE",),
    ),
    FishingMethod(
        "catch_shrimp_anchovies",
        "Catch shrimp/anchovies",
        "SMALL_FISHING_NET",
        ("anchovies", "shrimp"),
        source_spots=("NET_AND_BAIT",),
    ),
    FishingMethod(
        "catch_sardine_herring",
        "Catch sardine/herring",
        "FISHING_ROD_SEA",
        ("sardine", "herring"),
        bait_items=("Fishing bait",),
        source_spots=("NET_AND_BAIT",),
    ),
    FishingMethod(
        "catch_pike",
        "Catch pike",
        "FISHING_ROD_RIVER",
        ("pike",),
        bait_items=("Fishing bait",),
        source_spots=("LURE_AND_BAIT",),
    ),
    FishingMethod(
        "catch_trout_salmon",
        "Catch trout/salmon",
        "FLY_FISHING_ROD",
        ("salmon", "trout"),
        bait_items=("Feather",),
        source_spots=("LURE_AND_BAIT",),
    ),
    FishingMethod(
        "catch_mackerel_cod_bass",
        "Catch mackerel/cod/bass",
        "BIG_FISHING_NET",
        ("mackerel", "cod", "bass"),
        source_spots=("NET_HARPOON",),
    ),
    FishingMethod(
        "catch_sharks",
        "Catch sharks",
        "HARPOON_SHARK",
        ("shark",),
        source_spots=("NET_HARPOON",),
    ),
    FishingMethod(
        "catch_lobsters",
        "Catch lobsters",
        "LOBSTER_POT",
        ("lobster",),
        source_spots=("CAGE_AND_HARPOON",),
    ),
    FishingMethod(
        "catch_tuna_swordfish",
        "Catch tuna/swordfish",
        "HARPOON_NON_SHARK",
        ("tuna", "swordfish"),
        source_spots=("CAGE_AND_HARPOON", "HAPOON_FISHING"),
        notes="HAPOON_FISHING duplicates this same source tool behavior and is collapsed into one AnkiScape target.",
    ),
    FishingMethod(
        "catch_cavefish",
        "Catch cavefish",
        "FISHING_ROD_CAVEFISH",
        ("cavefish",),
        bait_items=("Fishing bait",),
        source_spots=("FISHING_ROD_CAVEFISH",),
    ),
    FishingMethod(
        "catch_rocktail",
        "Catch rocktail",
        "FISHING_ROD_ROCKTAIL",
        ("rocktail",),
        bait_items=("Living minerals",),
        source_spots=("FISHING_ROD_ROCKTAIL",),
    ),
    FishingMethod(
        "catch_monkfish",
        "Catch monkfish",
        "MONKFISH_NET",
        ("monkfish",),
        source_spots=("SMALL_FISHING_NET_MONKFISH",),
    ),
    FishingMethod(
        "catch_karambwan",
        "Catch karambwan",
        "KARAMBWAN_VESSEL",
        ("raw_karambwan",),
        source_spots=("KARAMBWAN",),
        notes="The rev-667 source binds the vessel without a karambwanji bait check.",
    ),
    FishingMethod(
        "catch_slimy_eel",
        "Catch slimy eel",
        "MORTMYRE_ROD",
        ("slimy_eel",),
        bait_items=("Fishing bait",),
        source_spots=("MORTMYRE_ROD",),
    ),
    FishingMethod(
        "catch_leaping_fish",
        "Catch leaping fish",
        "BARBARIAN_ROD",
        ("leaping_trout", "leaping_salmon", "leaping_sturgeon"),
        bait_items=("Feather", "Fishing bait", "Fish offcuts", "Roe", "Caviar"),
        source_spots=("BARBARIAN_ROD",),
    ),
)

FISHING_METHODS_BY_ID: Dict[str, FishingMethod] = {method.id: method for method in FISHING_METHODS}
DEFAULT_FISHING_TARGET = "catch_crayfish"

FISHING_MATERIAL_ITEM_IDS: Mapping[str, int] = {
    "Fishing bait": 313,
    "Feather": 314,
    "Fish offcuts": 11334,
    "Roe": 11324,
    "Caviar": 11326,
    "Living minerals": 15263,
}

DEFERRED_FISHING_CONTENT: Tuple[DeferredFishingContent, ...] = (
    DeferredFishingContent(
        "karambwanji_net",
        "Catch karambwanji",
        "source_unbound",
        "FishingTool.KBWANJI_NET has source data, but no FishingSpot.kt binding in the rev-667 plugin.",
        FISHING_TOOL_SOURCE_PATH,
    ),
    DeferredFishingContent(
        "rainbow_fish",
        "Catch rainbow fish",
        "source_unbound",
        "FishingTool.FLY_FISHING_ROD_RAINBOW_FISH has source data, but no FishingSpot.kt binding in the rev-667 plugin.",
        FISHING_TOOL_SOURCE_PATH,
    ),
    DeferredFishingContent(
        "lava_eel",
        "Catch lava eel",
        "source_unbound",
        "FishingTool.OILY_FISHING_ROD has source data, but no FishingSpot.kt binding in the rev-667 plugin.",
        FISHING_TOOL_SOURCE_PATH,
    ),
    DeferredFishingContent(
        "lumbridge_swamp_eel_spawn",
        "Catch slimy eel/frog spawn",
        "source_unbound",
        "FishingTool.LUMBDSWAMP_ROD has source data, but no FishingSpot.kt binding in the rev-667 plugin.",
        FISHING_TOOL_SOURCE_PATH,
    ),
    DeferredFishingContent(
        "cave_eel",
        "Catch cave eel",
        "source_unbound",
        "Fish.CAVE_EEL has source data, but no bound FishingTool/FishingSpot pair in the rev-667 plugin.",
        FISH_SOURCE_PATH,
    ),
)


def _fish_as_dict(fish: FishingFish) -> Dict[str, object]:
    return {
        "id": fish.id,
        "source_enum": fish.source_enum,
        "output_item": fish.output_item,
        "source_item_id": fish.source_item_id,
        "level": fish.level,
        "min_chance": fish.min_chance,
        "max_chance": fish.max_chance,
        "exp": fish.base_exp,
        "strength_level": fish.strength_level,
        "strength_exp": fish.strength_exp,
        "agility_level": fish.agility_level,
        "agility_exp": fish.agility_exp,
        "source": fish.source,
        "tradeable": fish.tradeable,
    }


def fishing_methods_as_dict() -> Dict[str, Dict[str, object]]:
    rows: Dict[str, Dict[str, object]] = {}
    for method in FISHING_METHODS:
        fish_rows = tuple(_fish_as_dict(FISH_BY_ID[fish_id]) for fish_id in method.fish_ids)
        level = min(int(fish["level"]) for fish in fish_rows) if fish_rows else 1
        requirements = {method.bait_items[0]: 1} if len(method.bait_items) == 1 else {}
        rows[method.id] = {
            "display_name": method.display_name,
            "level": level,
            "fish_ids": method.fish_ids,
            "fish": fish_rows,
            "bait_options": method.bait_items,
            "requirements": requirements,
            "source_tool": method.source_tool,
            "source_spots": method.source_spots,
            "source": method.source,
            "spot_source": FISHING_SPOT_SOURCE_PATH,
            "runtime_source": method.runtime_source,
            "status": method.status,
            "notes": method.notes,
        }
    return rows


def fishing_output_items() -> Tuple[str, ...]:
    seen: Dict[str, None] = {}
    for method in FISHING_METHODS:
        for fish_id in method.fish_ids:
            seen.setdefault(FISH_BY_ID[fish_id].output_item, None)
    return tuple(seen.keys())


def fishing_fish_as_dict() -> Dict[str, Dict[str, object]]:
    return {fish.id: _fish_as_dict(fish) for fish in FISHING_FISH}


def fishing_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    rows: Dict[str, Dict[str, object]] = {}
    for item_name, item_id in FISHING_MATERIAL_ITEM_IDS.items():
        source = FISHING_BAIT_SHOP_SOURCE_PATH if item_name in {"Fishing bait", "Feather"} else ITEMS_SOURCE_PATH
        rows[item_name] = {
            "category": "material",
            "level": 1,
            "exp": 0.0,
            "source": source,
            "item_id": item_id,
            "tradeable": True,
        }
    return rows


def deferred_fishing_content_as_dict() -> Mapping[str, Dict[str, str]]:
    return {
        item.id: {
            "display_name": item.display_name,
            "status": item.status,
            "reason": item.reason,
            "source": item.source,
        }
        for item in DEFERRED_FISHING_CONTENT
    }
