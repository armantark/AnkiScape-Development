"""2011Scape-sourced Firemaking data for AnkiScape.

The source rows come from the local 2011Scape rev 667 Firemaking plugin. The
2012 bonfire update is historically pre-EOC, but it is intentionally recorded as
a deferred extension because it adds a separate training method, reward table,
and cross-skill effects rather than changing the base log-burning table.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Tuple


FIREMAKING_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/firemaking/FiremakingData.kt"
)
FIREMAKING_RUNTIME_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/firemaking/FiremakingAction.kt"
)
FIREMAKING_PLUGIN_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/firemaking/firemaking.plugin.kts"
)
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
BONFIRE_SOURCE = "https://runescape.fandom.com/wiki/Update:Bonfires"


@dataclass(frozen=True)
class FiremakingTarget:
    id: str
    display_name: str
    input_item: str
    source_item_id: int
    level: int
    base_exp: float
    output_item: str = "Ashes"
    output_qty: int = 1
    low_chance: int = 65
    high_chance: int = 513
    source: str = FIREMAKING_SOURCE_PATH
    runtime_source: str = FIREMAKING_RUNTIME_SOURCE_PATH
    status: str = "implemented"
    tradeable: bool = True
    notes: str = ""


@dataclass(frozen=True)
class DeferredFiremakingContent:
    id: str
    display_name: str
    status: str
    reason: str
    source: str


FIREMAKING_TARGETS: Tuple[FiremakingTarget, ...] = (
    FiremakingTarget("logs", "Logs", "Logs", 1511, 1, 40.0),
    FiremakingTarget("achey_logs", "Achey tree logs", "Achey tree logs", 2862, 1, 40.0),
    FiremakingTarget("oak_logs", "Oak logs", "Oak logs", 1521, 15, 60.0),
    FiremakingTarget("willow_logs", "Willow logs", "Willow logs", 1519, 30, 90.0),
    FiremakingTarget("teak_logs", "Teak logs", "Teak logs", 6333, 35, 105.0),
    FiremakingTarget("arctic_pine_logs", "Arctic pine logs", "Arctic pine logs", 10810, 42, 125.0),
    FiremakingTarget("maple_logs", "Maple logs", "Maple logs", 1517, 45, 135.0),
    FiremakingTarget("mahogany_logs", "Mahogany logs", "Mahogany logs", 6332, 50, 157.5),
    FiremakingTarget("eucalyptus_logs", "Eucalyptus logs", "Eucalyptus logs", 12581, 58, 193.5),
    FiremakingTarget("yew_logs", "Yew logs", "Yew logs", 1515, 60, 202.5),
    FiremakingTarget("magic_logs", "Magic logs", "Magic logs", 1513, 75, 303.8),
    FiremakingTarget("curly_root", "Curly root", "Curly root", 21350, 75, 161.6),
    FiremakingTarget(
        "cursed_magic_logs",
        "Cursed magic logs",
        "Cursed magic logs",
        13567,
        82,
        303.8,
        tradeable=False,
    ),
)

DEFERRED_FIREMAKING_CONTENT: Tuple[DeferredFiremakingContent, ...] = (
    DeferredFiremakingContent(
        id="bonfires",
        display_name="Bonfires and fire spirits",
        status="deferred_2012_extension",
        reason=(
            "Pre-EOC 2012 content, but absent from the rev-667 source baseline; "
            "needs separate batch-log, bonus-XP, fire-spirit rewards, Cooking "
            "boost, and temporary-health design."
        ),
        source=BONFIRE_SOURCE,
    ),
)

FIREMAKING_TARGETS_BY_ID: Dict[str, FiremakingTarget] = {target.id: target for target in FIREMAKING_TARGETS}
DEFAULT_FIREMAKING_TARGET = "logs"
FIREMAKING_OUTPUT_ITEM_ID = 592


def firemaking_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        target.id: {
            "display_name": target.display_name,
            "level": target.level,
            "exp": target.base_exp,
            "requirements": {target.input_item: 1},
            "input_item": target.input_item,
            "source_item_id": target.source_item_id,
            "output_item": target.output_item,
            "output_qty": target.output_qty,
            "output_item_id": FIREMAKING_OUTPUT_ITEM_ID,
            "low_chance": target.low_chance,
            "high_chance": target.high_chance,
            "source": target.source,
            "runtime_source": target.runtime_source,
            "status": target.status,
            "tradeable": target.tradeable,
            "notes": target.notes,
        }
        for target in FIREMAKING_TARGETS
    }


def firemaking_input_items() -> Tuple[str, ...]:
    return tuple(target.input_item for target in FIREMAKING_TARGETS)


def firemaking_output_items() -> Tuple[str, ...]:
    return ("Ashes",)


def firemaking_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    items: Dict[str, Dict[str, object]] = {
        "Ashes": {
            "category": "material",
            "level": 1,
            "exp": 0.0,
            "source": FIREMAKING_RUNTIME_SOURCE_PATH,
            "item_id": FIREMAKING_OUTPUT_ITEM_ID,
            "tradeable": True,
        }
    }
    for target in FIREMAKING_TARGETS:
        items[target.input_item] = {
            "category": "log",
            "level": target.level,
            "exp": target.base_exp,
            "source": target.source,
            "item_id": target.source_item_id,
            "tradeable": target.tradeable,
        }
    return items


def firemaking_deferred_content_as_dict() -> Mapping[str, Dict[str, str]]:
    return {
        item.id: {
            "display_name": item.display_name,
            "status": item.status,
            "reason": item.reason,
            "source": item.source,
        }
        for item in DEFERRED_FIREMAKING_CONTENT
    }
