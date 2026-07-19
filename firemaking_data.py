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
LIGHT_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/mechanics/lightsource/LightSource.kt"
)
LIGHT_SOURCE_PLUGIN_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/mechanics/lightsource/light_source.plugin.kts"
)
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
BONFIRE_SOURCE = "https://runescape.fandom.com/wiki/Update:Bonfires"
CANDLE_LANTERN_SOURCE = "https://runescape.wiki/w/Candle_lantern?oldid=5962978"
LAMP_OIL_SOURCE = "https://runescape.wiki/w/Lamp_oil?oldid=6241595"
SAPPHIRE_LANTERN_SOURCE = "https://runescape.wiki/w/Sapphire_lantern_(lit)?oldid=6092552"
BUG_LANTERN_SOURCE = "https://runescape.wiki/w/Lit_bug_lantern?oldid=6591557"
LIGHT_SOURCES_SOURCE = "https://runescape.wiki/w/Light_sources?oldid=6581760"


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


@dataclass(frozen=True)
class LightSourceActivity:
    id: str
    display_name: str
    raw_item: str
    raw_item_id: int
    lit_item: str
    lit_item_id: int
    level: int
    source_enum: str
    raw_tradeable: bool
    lit_tradeable: bool
    source: str = LIGHT_SOURCE_PATH


@dataclass(frozen=True)
class LightSourcePreparation:
    id: str
    display_name: str
    input_item: str
    input_item_id: int
    reagent_item: str
    output_item: str
    output_item_id: int
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

LIGHT_SOURCE_ACTIVITIES: Tuple[LightSourceActivity, ...] = (
    LightSourceActivity("light_unlit_torch", "Light unlit torch", "Unlit torch", 596, "Lit torch", 594, 1, "UNLIT_TORCH", True, False),
    LightSourceActivity("light_candle", "Light candle", "Candle", 36, "Lit candle", 33, 1, "CANDLE", True, True),
    LightSourceActivity("light_black_candle", "Light black candle", "Black candle", 38, "Lit black candle", 32, 1, "BLACK_CANDLE", False, False),
    # Keep the stable action id even though the old implementation incorrectly
    # used the empty frame (4527) instead of the white-candle state (4529).
    LightSourceActivity("light_candle_lantern_4527", "Light candle lantern (white)", "Candle lantern (unlit, 4529)", 4529, "Candle lantern (lit, 4531)", 4531, 4, "CANDLE_LANTERN", True, True, source=CANDLE_LANTERN_SOURCE),
    LightSourceActivity("light_candle_lantern_4532", "Light candle lantern (4532)", "Candle lantern (unlit, 4532)", 4532, "Candle lantern (lit, 4534)", 4534, 4, "CANDLE_LANTERN_4532", True, True),
    LightSourceActivity("light_oil_lamp", "Light oil lamp", "Oil lamp (unlit)", 4522, "Oil lamp (lit)", 4524, 12, "OIL_LAMP", True, True),
    LightSourceActivity("light_oil_lantern", "Light oil lantern", "Oil lantern (unlit)", 4537, "Oil lantern (lit)", 4539, 26, "OIL_LANTERN", True, True, source="https://runescape.wiki/w/Oil_lantern?oldid=5372911"),
    LightSourceActivity("light_bug_lantern", "Light bug lantern", "Unlit bug lantern", 7051, "Lit bug lantern", 7053, 33, "BUG_LANTERN", True, False, source=BUG_LANTERN_SOURCE),
    LightSourceActivity("light_bullseye_lantern", "Light bullseye lantern", "Bullseye lantern (unlit)", 4548, "Bullseye lantern (lit)", 4550, 49, "BULLSEYE_LANTERN", False, False),
    LightSourceActivity("light_sapphire_lantern", "Light sapphire lantern", "Sapphire lantern (unlit)", 4701, "Sapphire lantern (lit)", 4702, 49, "SAPPHIRE_LANTERN", False, False),
    LightSourceActivity("light_emerald_lantern", "Light emerald lantern", "Emerald lantern (unlit)", 9064, "Emerald lantern (lit)", 9065, 49, "EMERALD_LANTERN", False, False),
    LightSourceActivity("light_mining_helmet", "Light mining helmet", "Mining helmet (unlit)", 5014, "Mining helmet (lit)", 5013, 65, "MINING_HELMET", True, True),
)

LIT_LIGHT_SOURCE_ITEMS: Tuple[str, ...] = tuple(
    activity.lit_item
    for activity in LIGHT_SOURCE_ACTIVITIES
    if activity.source_enum != "BUG_LANTERN"
)

# The cutoff-era light-source table also names achievement headbands and the
# expired Gielinor Games torches. Keep that complete source set explicit, while
# runtime quest gates use only states the current item graph can award.
PERIOD_LIT_LIGHT_SOURCE_ITEMS: Tuple[str, ...] = (
    *LIT_LIGHT_SOURCE_ITEMS,
    "Seer's headband 1",
    "Seer's headband 2",
    "Seer's headband 3",
    "Seer's headband 4",
    "Bronze torch",
    "Silver torch",
    "Gold torch",
)

LIGHT_SOURCE_PREPARATIONS: Tuple[LightSourcePreparation, ...] = (
    LightSourcePreparation("insert_white_candle", "Put white candle in lantern", "Candle lantern (empty)", 4527, "Candle", "Candle lantern (unlit, 4529)", 4529, CANDLE_LANTERN_SOURCE),
    LightSourcePreparation("insert_black_candle", "Put black candle in lantern", "Candle lantern (empty)", 4527, "Black candle", "Candle lantern (unlit, 4532)", 4532, CANDLE_LANTERN_SOURCE),
    LightSourcePreparation("fill_oil_lamp", "Fill oil lamp with lamp oil", "Oil lamp (empty)", 4525, "Swamp tar", "Oil lamp (unlit)", 4522, LAMP_OIL_SOURCE),
    LightSourcePreparation("fill_oil_lantern", "Fill oil lantern with lamp oil", "Oil lantern (empty)", 4535, "Swamp tar", "Oil lantern (unlit)", 4537, LAMP_OIL_SOURCE),
    LightSourcePreparation("fill_bullseye_lantern", "Fill bullseye lantern with lamp oil", "Bullseye lantern (empty)", 4546, "Swamp tar", "Bullseye lantern (unlit)", 4548, LAMP_OIL_SOURCE),
    LightSourcePreparation("fill_sapphire_lantern", "Fill sapphire lantern with lamp oil", "Sapphire lantern (empty)", 4700, "Swamp tar", "Sapphire lantern (unlit)", 4701, SAPPHIRE_LANTERN_SOURCE),
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


def light_source_activities_as_dict() -> Dict[str, Dict[str, object]]:
    activities: Dict[str, Dict[str, object]] = {}
    for preparation in LIGHT_SOURCE_PREPARATIONS:
        activities[preparation.id] = {
            "display_name": preparation.display_name,
            "requirements": {
                preparation.input_item: 1,
                preparation.reagent_item: 1,
            },
            "output_item": preparation.output_item,
            "output_qty": 1,
            "batch_size": 1,
            "group": "light_sources",
            "source_item_id": preparation.input_item_id,
            "output_item_id": preparation.output_item_id,
            "source": preparation.source,
        }
    for activity in LIGHT_SOURCE_ACTIVITIES:
        activities[activity.id] = {
            "display_name": activity.display_name,
            "requirements": {activity.raw_item: 1},
            "output_item": activity.lit_item,
            "output_qty": 1,
            "batch_size": 1,
            "group": "light_sources",
            "firemaking_level": activity.level,
            "source_item_id": activity.raw_item_id,
            "output_item_id": activity.lit_item_id,
            "source": activity.source,
            "source_enum": activity.source_enum,
        }
        activities[f"extinguish_{activity.id[6:]}"] = {
            "display_name": f"Extinguish {activity.lit_item.lower()}",
            "requirements": {activity.lit_item: 1},
            "output_item": activity.raw_item,
            "output_qty": 1,
            "batch_size": 1,
            "group": "light_sources",
            "source_item_id": activity.lit_item_id,
            "output_item_id": activity.raw_item_id,
            "source": LIGHT_SOURCE_PLUGIN_PATH,
            "source_enum": activity.source_enum,
        }
    return activities


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
    for activity in LIGHT_SOURCE_ACTIVITIES:
        item_category = (
            "equipment"
            if activity.source_enum in {"BUG_LANTERN", "MINING_HELMET"}
            else "material"
        )
        items[activity.raw_item] = {
            "category": item_category,
            "level": activity.level,
            "exp": 0.0,
            "source": activity.source,
            "item_id": activity.raw_item_id,
            "tradeable": activity.raw_tradeable,
        }
        items[activity.lit_item] = {
            "category": item_category,
            "level": activity.level,
            "exp": 0.0,
            "source": activity.source,
            "item_id": activity.lit_item_id,
            "tradeable": activity.lit_tradeable,
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
