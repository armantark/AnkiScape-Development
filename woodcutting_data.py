"""2011Scape-sourced Woodcutting data for AnkiScape.

The source values in this module come from the local 2011Scape rev 667
Woodcutting plugin. AnkiScape may tune review-scale probabilities at runtime,
but level requirements, base XP, item IDs, and drop weights stay source-audited.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple


TREE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/woodcutting/TreeType.kt"
)
AXE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/woodcutting/AxeType.kt"
)
WOODCUTTING_RUNTIME_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/woodcutting/Woodcutting.kt"
)
BIRD_NEST_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/items/birdnests/bird_nest.plugin.kts"
)


@dataclass(frozen=True)
class WoodcuttingTarget:
    id: str
    display_name: str
    level: int
    base_exp: float
    output_item: Optional[str]
    source_item_id: Optional[int]
    deplete_chance: int
    respawn_time: int
    low_chance: int
    high_chance: int
    source: str = TREE_SOURCE_PATH
    status: str = "implemented"


@dataclass(frozen=True)
class WoodcuttingAxe:
    id: str
    display_name: str
    item_id: int
    level: int
    ratio: float
    source: str = AXE_SOURCE_PATH
    status: str = "implemented"


@dataclass(frozen=True)
class WeightedItem:
    item: str
    weight: int


@dataclass(frozen=True)
class BirdNestOpenTable:
    input_item: str
    guaranteed_item: str
    rolls: Tuple[WeightedItem, ...]
    total_weight: int
    source: str = BIRD_NEST_SOURCE_PATH


WOODCUTTING_TARGETS: Tuple[WoodcuttingTarget, ...] = (
    WoodcuttingTarget("tree", "Tree", 1, 25.0, "Logs", 1511, 0, 59, 64, 200),
    WoodcuttingTarget("achey", "Achey", 1, 25.0, "Achey tree logs", 2862, 0, 59, 64, 200),
    WoodcuttingTarget("oak", "Oak", 15, 37.5, "Oak logs", 1521, 8, 14, 32, 100),
    WoodcuttingTarget("willow", "Willow", 30, 67.5, "Willow logs", 1519, 8, 14, 16, 50),
    WoodcuttingTarget("teak", "Teak", 35, 85.0, "Teak logs", 6333, 8, 15, 15, 46),
    WoodcuttingTarget("maple", "Maple", 45, 100.0, "Maple logs", 1517, 8, 59, 8, 25),
    WoodcuttingTarget("hollow", "Hollow", 45, 82.0, "Bark", 3239, 8, 44, 18, 26),
    WoodcuttingTarget("mahogany", "Mahogany", 50, 125.0, "Mahogany logs", 6332, 8, 14, 8, 25),
    WoodcuttingTarget("yew", "Yew", 60, 175.0, "Yew logs", 1515, 8, 99, 4, 12),
    WoodcuttingTarget("ivy", "Ivy", 68, 332.5, None, None, 8, 36, 7, 11),
    WoodcuttingTarget("magic", "Magic", 75, 250.0, "Magic logs", 1513, 8, 199, 6, 6),
)

WOODCUTTING_AXES: Tuple[WoodcuttingAxe, ...] = (
    WoodcuttingAxe("bronze_hatchet", "Bronze hatchet", 1351, 1, 1.0),
    WoodcuttingAxe("iron_hatchet", "Iron hatchet", 1349, 1, 1.5),
    WoodcuttingAxe("steel_hatchet", "Steel hatchet", 1353, 6, 2.0),
    WoodcuttingAxe("black_hatchet", "Black hatchet", 1361, 6, 2.25),
    WoodcuttingAxe("mithril_hatchet", "Mithril hatchet", 1355, 21, 2.5),
    WoodcuttingAxe("adamant_hatchet", "Adamant hatchet", 1357, 31, 3.0),
    WoodcuttingAxe("rune_hatchet", "Rune hatchet", 1359, 41, 3.5),
    WoodcuttingAxe("dragon_hatchet", "Dragon hatchet", 6739, 61, 3.75),
)

DEFERRED_WOODCUTTING_AXES: Tuple[WoodcuttingAxe, ...] = (
    WoodcuttingAxe("inferno_adze", "Inferno adze", 13661, 61, 3.75, status="deferred_special"),
)

WOODCUTTING_TARGETS_BY_ID: Dict[str, WoodcuttingTarget] = {target.id: target for target in WOODCUTTING_TARGETS}
WOODCUTTING_AXES_BY_ID: Dict[str, WoodcuttingAxe] = {axe.id: axe for axe in WOODCUTTING_AXES}
WOODCUTTING_AXES_BY_ITEM: Dict[str, WoodcuttingAxe] = {axe.display_name: axe for axe in WOODCUTTING_AXES}

DEFAULT_WOODCUTTING_TARGET = "tree"
DEFAULT_WOODCUTTING_TOOLBELT: Mapping[str, Tuple[str, ...]] = {"woodcutting": ("bronze_hatchet",)}

LEGACY_TREE_TARGETS: Mapping[str, str] = {
    "Tree": "tree",
    "Achey": "achey",
    "Oak": "oak",
    "Willow": "willow",
    "Teak": "teak",
    "Maple": "maple",
    "Hollow": "hollow",
    "Mahogany": "mahogany",
    "Yew": "yew",
    "Ivy": "ivy",
    "Magic": "magic",
    "Redwood": DEFAULT_WOODCUTTING_TARGET,
}

LEGACY_LOG_STORAGE_MIGRATIONS: Mapping[str, Optional[str]] = {
    "Tree": "Logs",
    "Achey": "Achey tree logs",
    "Oak": "Oak logs",
    "Willow": "Willow logs",
    "Teak": "Teak logs",
    "Maple": "Maple logs",
    "Hollow": "Bark",
    "Mahogany": "Mahogany logs",
    "Yew": "Yew logs",
    "Magic": "Magic logs",
    "Redwood": None,
}

BIRD_NEST_DROP_CHANCE = 1 / 257
BIRD_NEST_DROP_TABLE: Tuple[WeightedItem, ...] = (
    WeightedItem("Bird's nest (seeds)", 65),
    WeightedItem("Bird's nest (Zamorak egg)", 1),
    WeightedItem("Bird's nest (Guthix egg)", 1),
    WeightedItem("Bird's nest (Saradomin egg)", 1),
    WeightedItem("Bird's nest (ring)", 32),
)

SEED_NEST_OPEN_TABLE = BirdNestOpenTable(
    input_item="Bird's nest (seeds)",
    guaranteed_item="Bird's nest (empty)",
    total_weight=1024,
    rolls=(
        WeightedItem("Acorn", 218),
        WeightedItem("Apple tree seed", 174),
        WeightedItem("Willow seed", 147),
        WeightedItem("Banana tree seed", 114),
        WeightedItem("Orange tree seed", 87),
        WeightedItem("Curry tree seed", 69),
        WeightedItem("Maple seed", 57),
        WeightedItem("Pineapple seed", 42),
        WeightedItem("Papaya tree seed", 34),
        WeightedItem("Yew seed", 27),
        WeightedItem("Palm tree seed", 22),
        WeightedItem("Calquat tree seed", 17),
        WeightedItem("Spirit seed", 11),
        WeightedItem("Magic seed", 5),
    ),
)

RING_NEST_OPEN_TABLE = BirdNestOpenTable(
    input_item="Bird's nest (ring)",
    guaranteed_item="Bird's nest (empty)",
    total_weight=100,
    rolls=(
        WeightedItem("Sapphire ring", 40),
        WeightedItem("Gold ring", 35),
        WeightedItem("Emerald ring", 15),
        WeightedItem("Ruby ring", 9),
        WeightedItem("Diamond ring", 1),
    ),
)

EGG_NEST_OPEN_TABLES: Tuple[BirdNestOpenTable, ...] = (
    BirdNestOpenTable("Bird's nest (Zamorak egg)", "Bird's nest (empty)", (WeightedItem("Zamorak bird's egg", 1),), 1),
    BirdNestOpenTable("Bird's nest (Guthix egg)", "Bird's nest (empty)", (WeightedItem("Guthix bird's egg", 1),), 1),
    BirdNestOpenTable("Bird's nest (Saradomin egg)", "Bird's nest (empty)", (WeightedItem("Saradomin bird's egg", 1),), 1),
)

BIRD_NEST_OPEN_TABLES: Tuple[BirdNestOpenTable, ...] = (
    SEED_NEST_OPEN_TABLE,
    RING_NEST_OPEN_TABLE,
) + EGG_NEST_OPEN_TABLES

BIRD_NEST_OPEN_TABLES_BY_INPUT: Dict[str, BirdNestOpenTable] = {
    table.input_item: table for table in BIRD_NEST_OPEN_TABLES
}


def woodcutting_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        target.id: {
            "display_name": target.display_name,
            "level": target.level,
            "exp": target.base_exp,
            "output_item": target.output_item,
            "source_item_id": target.source_item_id,
            "deplete_chance": target.deplete_chance,
            "respawn_time": target.respawn_time,
            "low_chance": target.low_chance,
            "high_chance": target.high_chance,
            "source": target.source,
            "status": target.status,
        }
        for target in WOODCUTTING_TARGETS
    }


def woodcutting_axes_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        axe.id: {
            "display_name": axe.display_name,
            "item_id": axe.item_id,
            "level": axe.level,
            "ratio": axe.ratio,
            "source": axe.source,
            "status": axe.status,
        }
        for axe in WOODCUTTING_AXES
    }


def woodcutting_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    items: Dict[str, Dict[str, object]] = {}
    for axe in WOODCUTTING_AXES + DEFERRED_WOODCUTTING_AXES:
        items[axe.display_name] = {
            "category": "tool",
            "level": axe.level,
            "source": axe.source,
            "item_id": axe.item_id,
            "status": axe.status,
        }
    for weighted in BIRD_NEST_DROP_TABLE:
        items[weighted.item] = {
            "category": "material",
            "source": BIRD_NEST_SOURCE_PATH,
        }
    for table in BIRD_NEST_OPEN_TABLES:
        items[table.guaranteed_item] = {
            "category": "material",
            "source": table.source,
        }
        for weighted in table.rolls:
            items[weighted.item] = {
                "category": "material",
                "source": table.source,
            }
    return items
