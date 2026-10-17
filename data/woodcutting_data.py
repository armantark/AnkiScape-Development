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
SPLIT_LOG_SOURCE = "https://runescape.wiki/w/Split_log?oldid=5505475"
ARCTIC_PINE_SOURCE = "https://runescape.wiki/w/Arctic_Pine?oldid=6069429"
EUCALYPTUS_SOURCE = "https://runescape.wiki/w/Eucalyptus_tree?oldid=6491980"
CURLY_ROOT_SOURCE = "https://runescape.wiki/w/Curly_root?oldid=6518326"
EGG_NEST_SOURCE = "https://runescape.wiki/w/Bird%27s_nests?oldid=6550484"


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
    action_type: str = "gathering"
    requirements: Tuple[Tuple[str, int], ...] = ()
    output_quantity: int = 1
    output_stackable: bool = False
    output_tradeable: bool = True


@dataclass(frozen=True)
class WoodcuttingAxe:
    id: str
    display_name: str
    item_id: int
    level: int
    ratio: float
    incinerates_logs: bool = False
    incinerate_chance: float = 0.0
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
    # PLACEHOLDER(woodcutting.arctic_pine_rolls): authentic Arctic-pine chop,
    # depletion, and respawn rolls; nearest-level Mahogany keeps the mechanic
    # ordered without claiming a recovered server table.
    WoodcuttingTarget(
        "arctic_pine",
        "Arctic pine",
        54,
        140.2,
        "Arctic pine logs",
        10810,
        8,
        14,
        8,
        25,
        source=ARCTIC_PINE_SOURCE,
    ),
    WoodcuttingTarget(
        "split_arctic_pine_logs",
        "Split Arctic pine logs",
        54,
        42.5,
        "Split log",
        10812,
        0,
        0,
        0,
        0,
        source=SPLIT_LOG_SOURCE,
        action_type="processing",
        requirements=(("Arctic pine logs", 1),),
    ),
    # PLACEHOLDER(woodcutting.eucalyptus_rolls): authentic Eucalyptus chop,
    # depletion, and respawn rolls; nearest-level Yew supplies the bounded
    # review behavior until a period server table survives.
    WoodcuttingTarget(
        "eucalyptus",
        "Eucalyptus",
        58,
        165.0,
        "Eucalyptus logs",
        12581,
        8,
        99,
        4,
        12,
        source=EUCALYPTUS_SOURCE,
    ),
    WoodcuttingTarget("yew", "Yew", 60, 175.0, "Yew logs", 1515, 8, 99, 4, 12),
    WoodcuttingTarget("ivy", "Ivy", 68, 332.5, None, None, 8, 36, 7, 11),
    WoodcuttingTarget("magic", "Magic", 75, 250.0, "Magic logs", 1513, 8, 199, 6, 6),
    # PLACEHOLDER(woodcutting.curly_jade_root_success_curve): period sources fix
    # level 83, both 80.8-XP stages, and the four-root collection, but no hidden
    # success curve. The generic review adapter needs endpoints, so the shared
    # Hunter fallback keeps the route live without adopting Darkan's unproven
    # 6/35 rates or 72-tick respawn value.
    WoodcuttingTarget(
        "curly_jade_root",
        "Curly jade root",
        83,
        161.6,
        "Curly root",
        21350,
        0,
        0,
        128,
        256,
        source=CURLY_ROOT_SOURCE,
        output_quantity=4,
        output_stackable=False,
        output_tradeable=False,
    ),
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
    WoodcuttingAxe("inferno_adze", "Inferno adze", 13661, 61, 3.75, True, 1 / 2),
)

DEFERRED_WOODCUTTING_AXES: Tuple[WoodcuttingAxe, ...] = ()

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
            "action_type": target.action_type,
            "requirements": dict(target.requirements),
            "output_quantity": target.output_quantity,
            "stackable": target.output_stackable,
            "tradeable": target.output_tradeable,
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
            "incinerates_logs": axe.incinerates_logs,
            "incinerate_chance": axe.incinerate_chance,
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
    for item_name, item_id in (
        ("Bird's nest (Zamorak egg)", 5070),
        ("Bird's nest (Guthix egg)", 5071),
        ("Bird's nest (Saradomin egg)", 5072),
    ):
        items[item_name].update(
            item_id=item_id, tradeable=False, stackable=False, source=EGG_NEST_SOURCE,
        )
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
