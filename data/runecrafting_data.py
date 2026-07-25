"""2011Scape-sourced Runecrafting data for AnkiScape.

The rows here are transcribed from the local 2011Scape rev 667 Runecrafting
plugin. Runtime imports only this checked-in Python data; the emulator checkout
is a development-time source audit input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


RUNECRAFTING_SOURCE_ROOT = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/runecrafting"
RUNE_SOURCE_PATH = f"{RUNECRAFTING_SOURCE_ROOT}/Rune.kt"
ALTAR_SOURCE_PATH = f"{RUNECRAFTING_SOURCE_ROOT}/Altar.kt"
COMBINATION_SOURCE_PATH = f"{RUNECRAFTING_SOURCE_ROOT}/CombinationRune.kt"
TIARA_SOURCE_PATH = f"{RUNECRAFTING_SOURCE_ROOT}/Tiara.kt"
TIARA_PLUGIN_SOURCE_PATH = f"{RUNECRAFTING_SOURCE_ROOT}/tiara.plugin.kts"
POUCH_SOURCE_PATH = f"{RUNECRAFTING_SOURCE_ROOT}/pouches.plugin.kts"
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt"
RUNEMYSTERIES_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/RuneMysteries.kt"

DEFAULT_RUNECRAFTING_TARGET = "craft_air_runes"
WICKED_HOOD_CLAIM_ID = "wicked_hood"
WICKED_HOOD_ITEM = "Wicked hood"
BINDING_NECKLACE_ITEM = "Binding necklace"
BINDING_NECKLACE_MAX_CHARGES = 15


@dataclass(frozen=True)
class AltarDefinition:
    id: str
    display_name: str
    talisman_item: Optional[str]
    tiara_item: Optional[str]
    rune_item: str
    source: str = ALTAR_SOURCE_PATH


@dataclass(frozen=True)
class StandardRuneTarget:
    id: str
    display_name: str
    altar_id: str
    output_item: str
    level: int
    base_exp: float
    essence_items: Tuple[str, ...]
    source_item_id: int
    source: str = RUNE_SOURCE_PATH
    group: str = "standard"
    kind: str = "standard"


@dataclass(frozen=True)
class CombinationRuneTarget:
    id: str
    display_name: str
    altar_id: str
    output_item: str
    level: int
    base_exp: float
    consumed_talisman: str
    component_rune: str
    source_item_id: int
    source: str = COMBINATION_SOURCE_PATH
    group: str = "combination"
    kind: str = "combination"


@dataclass(frozen=True)
class TiaraBindingTarget:
    id: str
    display_name: str
    altar_id: str
    output_item: str
    base_exp: float
    talisman_item: str
    source_item_id: int
    source: str = TIARA_SOURCE_PATH
    group: str = "tiara"
    kind: str = "tiara"
    level: int = 1


@dataclass(frozen=True)
class HoodFeedTarget:
    id: str
    display_name: str
    altar_id: str
    input_item: str
    input_kind: str
    source_item_id: int
    source: str = "https://runescape.wiki/w/Wicked_hood"
    group: str = "hood"
    kind: str = "hood_feed"
    level: int = 1
    base_exp: float = 0.0


@dataclass(frozen=True)
class PouchDefinition:
    id: str
    display_name: str
    degraded_item: Optional[str]
    capacity: int
    required_level: int
    degradation_threshold: Optional[int]
    source_item_id: int
    degraded_source_item_id: Optional[int] = None
    source: str = POUCH_SOURCE_PATH


def _altar_id(name: str) -> str:
    return name.lower()


_STANDARD_ESSENCE = ("Rune essence", "Pure essence")
_PURE_ESSENCE = ("Pure essence",)


ALTARS: Tuple[AltarDefinition, ...] = (
    AltarDefinition("air", "Air altar", "Air talisman", "Air tiara", "Air rune"),
    AltarDefinition("mind", "Mind altar", "Mind talisman", "Mind tiara", "Mind rune"),
    AltarDefinition("water", "Water altar", "Water talisman", "Water tiara", "Water rune"),
    AltarDefinition("earth", "Earth altar", "Earth talisman", "Earth tiara", "Earth rune"),
    AltarDefinition("fire", "Fire altar", "Fire talisman", "Fire tiara", "Fire rune"),
    AltarDefinition("body", "Body altar", "Body talisman", "Body tiara", "Body rune"),
    AltarDefinition("cosmic", "Cosmic altar", "Cosmic talisman", "Cosmic tiara", "Cosmic rune"),
    AltarDefinition("chaos", "Chaos altar", "Chaos talisman", "Chaos tiara", "Chaos rune"),
    AltarDefinition("astral", "Astral altar", None, None, "Astral rune"),
    AltarDefinition("nature", "Nature altar", "Nature talisman", "Nature tiara", "Nature rune"),
    AltarDefinition("law", "Law altar", "Law talisman", "Law tiara", "Law rune"),
    AltarDefinition("death", "Death altar", "Death talisman", "Death tiara", "Death rune"),
    AltarDefinition("blood", "Blood altar", "Blood talisman", "Blood tiara", "Blood rune"),
)
ALTARS_BY_ID: Dict[str, AltarDefinition] = {altar.id: altar for altar in ALTARS}


STANDARD_RUNE_TARGETS: Tuple[StandardRuneTarget, ...] = (
    StandardRuneTarget("craft_air_runes", "Air runes", "air", "Air rune", 1, 5.0, _STANDARD_ESSENCE, 556),
    StandardRuneTarget("craft_mind_runes", "Mind runes", "mind", "Mind rune", 2, 5.5, _STANDARD_ESSENCE, 558),
    StandardRuneTarget("craft_water_runes", "Water runes", "water", "Water rune", 5, 6.0, _STANDARD_ESSENCE, 555),
    StandardRuneTarget("craft_earth_runes", "Earth runes", "earth", "Earth rune", 9, 6.5, _STANDARD_ESSENCE, 557),
    StandardRuneTarget("craft_fire_runes", "Fire runes", "fire", "Fire rune", 14, 7.0, _STANDARD_ESSENCE, 554),
    StandardRuneTarget("craft_body_runes", "Body runes", "body", "Body rune", 20, 7.5, _STANDARD_ESSENCE, 559),
    StandardRuneTarget("craft_cosmic_runes", "Cosmic runes", "cosmic", "Cosmic rune", 27, 8.0, _PURE_ESSENCE, 564),
    StandardRuneTarget("craft_chaos_runes", "Chaos runes", "chaos", "Chaos rune", 35, 8.5, _PURE_ESSENCE, 562),
    StandardRuneTarget("craft_astral_runes", "Astral runes", "astral", "Astral rune", 40, 8.7, _PURE_ESSENCE, 9075),
    StandardRuneTarget("craft_nature_runes", "Nature runes", "nature", "Nature rune", 44, 9.0, _PURE_ESSENCE, 561),
    StandardRuneTarget("craft_law_runes", "Law runes", "law", "Law rune", 54, 9.5, _PURE_ESSENCE, 563),
    StandardRuneTarget("craft_death_runes", "Death runes", "death", "Death rune", 65, 10.0, _PURE_ESSENCE, 560),
    StandardRuneTarget("craft_blood_runes", "Blood runes", "blood", "Blood rune", 77, 10.5, _PURE_ESSENCE, 565),
)
STANDARD_RUNE_TARGETS_BY_ID: Dict[str, StandardRuneTarget] = {target.id: target for target in STANDARD_RUNE_TARGETS}


COMBINATION_RUNE_TARGETS: Tuple[CombinationRuneTarget, ...] = (
    CombinationRuneTarget("combo_mist_at_air", "Mist runes at Air altar", "air", "Mist rune", 6, 8.0, "Water talisman", "Water rune", 4695),
    CombinationRuneTarget("combo_mist_at_water", "Mist runes at Water altar", "water", "Mist rune", 6, 8.5, "Air talisman", "Air rune", 4695),
    CombinationRuneTarget("combo_dust_at_air", "Dust runes at Air altar", "air", "Dust rune", 10, 8.3, "Earth talisman", "Earth rune", 4696),
    CombinationRuneTarget("combo_dust_at_earth", "Dust runes at Earth altar", "earth", "Dust rune", 10, 9.0, "Air talisman", "Air rune", 4696),
    CombinationRuneTarget("combo_mud_at_water", "Mud runes at Water altar", "water", "Mud rune", 13, 9.3, "Earth talisman", "Earth rune", 4698),
    CombinationRuneTarget("combo_mud_at_earth", "Mud runes at Earth altar", "earth", "Mud rune", 13, 9.5, "Water talisman", "Water rune", 4698),
    CombinationRuneTarget("combo_smoke_at_air", "Smoke runes at Air altar", "air", "Smoke rune", 15, 8.5, "Fire talisman", "Fire rune", 4697),
    CombinationRuneTarget("combo_smoke_at_fire", "Smoke runes at Fire altar", "fire", "Smoke rune", 15, 9.5, "Air talisman", "Air rune", 4697),
    CombinationRuneTarget("combo_steam_at_water", "Steam runes at Water altar", "water", "Steam rune", 19, 9.5, "Fire talisman", "Fire rune", 4694),
    CombinationRuneTarget("combo_steam_at_fire", "Steam runes at Fire altar", "fire", "Steam rune", 19, 10.0, "Water talisman", "Water rune", 4694),
    CombinationRuneTarget("combo_lava_at_earth", "Lava runes at Earth altar", "earth", "Lava rune", 23, 10.0, "Fire talisman", "Fire rune", 4699),
    CombinationRuneTarget("combo_lava_at_fire", "Lava runes at Fire altar", "fire", "Lava rune", 23, 10.5, "Earth talisman", "Earth rune", 4699),
)
COMBINATION_RUNE_TARGETS_BY_ID: Dict[str, CombinationRuneTarget] = {target.id: target for target in COMBINATION_RUNE_TARGETS}


TIARA_BINDING_TARGETS: Tuple[TiaraBindingTarget, ...] = (
    TiaraBindingTarget("bind_air_tiara", "Bind air tiara", "air", "Air tiara", 25.0, "Air talisman", 5527),
    TiaraBindingTarget("bind_mind_tiara", "Bind mind tiara", "mind", "Mind tiara", 27.5, "Mind talisman", 5529),
    TiaraBindingTarget("bind_water_tiara", "Bind water tiara", "water", "Water tiara", 30.0, "Water talisman", 5531),
    TiaraBindingTarget("bind_earth_tiara", "Bind earth tiara", "earth", "Earth tiara", 32.5, "Earth talisman", 5535),
    TiaraBindingTarget("bind_fire_tiara", "Bind fire tiara", "fire", "Fire tiara", 35.0, "Fire talisman", 5537),
    TiaraBindingTarget("bind_body_tiara", "Bind body tiara", "body", "Body tiara", 37.5, "Body talisman", 5533),
    TiaraBindingTarget("bind_cosmic_tiara", "Bind cosmic tiara", "cosmic", "Cosmic tiara", 40.0, "Cosmic talisman", 5539),
    TiaraBindingTarget("bind_chaos_tiara", "Bind chaos tiara", "chaos", "Chaos tiara", 42.5, "Chaos talisman", 5543),
    TiaraBindingTarget("bind_nature_tiara", "Bind nature tiara", "nature", "Nature tiara", 45.0, "Nature talisman", 5541),
    TiaraBindingTarget("bind_law_tiara", "Bind law tiara", "law", "Law tiara", 47.5, "Law talisman", 5545),
    TiaraBindingTarget("bind_death_tiara", "Bind death tiara", "death", "Death tiara", 50.0, "Death talisman", 5547),
    TiaraBindingTarget("bind_blood_tiara", "Bind blood tiara", "blood", "Blood tiara", 52.5, "Blood talisman", 5549, source="2012-era RuneScape tiara set; local Altar.kt includes BLOOD tiara/talisman"),
)
TIARA_BINDING_TARGETS_BY_ID: Dict[str, TiaraBindingTarget] = {target.id: target for target in TIARA_BINDING_TARGETS}


HOOD_FEED_TARGETS: Tuple[HoodFeedTarget, ...] = tuple(
    HoodFeedTarget(
        id=f"feed_{altar.id}_{kind}_to_hood",
        display_name=f"Feed {altar.display_name.replace(' altar', '')} {kind} to hood",
        altar_id=altar.id,
        input_item=item,
        input_kind=kind,
        source_item_id=0,
    )
    for altar in ALTARS
    for kind, item in (("talisman", altar.talisman_item), ("tiara", altar.tiara_item))
    if item is not None
) + (
    HoodFeedTarget(
        "feed_elemental_talisman_to_hood",
        "Feed Elemental talisman to hood",
        "elemental",
        "Elemental talisman",
        "talisman",
        5516,
        source="https://runescape.wiki/w/Wicked_hood?oldid=6564747",
    ),
    HoodFeedTarget(
        "feed_omni_talisman_to_hood",
        "Feed Omni-talisman to hood",
        "omni",
        "Omni-talisman",
        "talisman",
        13649,
        source="https://runescape.wiki/w/Wicked_hood?oldid=6564747",
    ),
    HoodFeedTarget(
        "feed_omni_tiara_to_hood",
        "Feed Omni-tiara to hood",
        "omni",
        "Omni-tiara",
        "tiara",
        13655,
        source="https://runescape.wiki/w/Wicked_hood?oldid=6564747",
    ),
)
HOOD_FEED_TARGETS_BY_ID: Dict[str, HoodFeedTarget] = {target.id: target for target in HOOD_FEED_TARGETS}


POUCHES: Tuple[PouchDefinition, ...] = (
    PouchDefinition("small", "Small pouch", None, 3, 1, None, 5509),
    PouchDefinition("medium", "Medium pouch", "Medium pouch (worn)", 6, 25, 44, 5510, 5511),
    PouchDefinition("large", "Large pouch", "Large pouch (worn)", 9, 50, 34, 5512, 5513),
    PouchDefinition("giant", "Giant pouch", "Giant pouch (worn)", 12, 75, 10, 5514, 5515),
)
POUCHES_BY_ID: Dict[str, PouchDefinition] = {pouch.id: pouch for pouch in POUCHES}


RUNECRAFTING_TARGETS = STANDARD_RUNE_TARGETS + COMBINATION_RUNE_TARGETS + TIARA_BINDING_TARGETS + HOOD_FEED_TARGETS
RUNECRAFTING_TARGETS_BY_ID = {target.id: target for target in RUNECRAFTING_TARGETS}

RUNECRAFTING_GROUP_LABELS: Dict[str, str] = {
    "standard": "Standard runes",
    "combination": "Combination runes",
    "tiara": "Tiara binding",
    "hood": "Hood feeding",
}

_TARGET_GROUP_ORDER = ("standard", "combination", "tiara", "hood")


def _target_as_dict(target) -> Dict[str, object]:
    data = dict(target.__dict__)
    data["base_exp"] = data.pop("base_exp", data.get("base_exp", 0.0))
    return data


def runecrafting_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {target.id: _target_as_dict(target) for target in RUNECRAFTING_TARGETS}


def runecrafting_output_items() -> Tuple[str, ...]:
    items = [target.output_item for target in STANDARD_RUNE_TARGETS]
    items.extend(target.output_item for target in COMBINATION_RUNE_TARGETS)
    items.extend(target.output_item for target in TIARA_BINDING_TARGETS)
    return tuple(dict.fromkeys(items))


def runecrafting_rune_output_items() -> Tuple[str, ...]:
    """Rune products only; tiaras remain outputs but are not crafted runes."""
    return tuple(
        dict.fromkeys(
            target.output_item
            for target in STANDARD_RUNE_TARGETS + COMBINATION_RUNE_TARGETS
        )
    )


def runecrafting_access_items() -> Tuple[str, ...]:
    items = []
    for altar in ALTARS:
        if altar.talisman_item:
            items.append(altar.talisman_item)
        if altar.tiara_item:
            items.append(altar.tiara_item)
    return tuple(dict.fromkeys(items))


def runecrafting_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    data: Dict[str, Dict[str, object]] = {}

    def add_item(
        name: str,
        item_id: int,
        source: str,
        *,
        category: str = "runecrafting",
        tradeable: bool = True,
        stackable: bool = False,
    ) -> None:
        data[name] = {
            "display_name": name,
            "output_item": name,
            "level": 1,
            "exp": 0.0,
            "source": source,
            "source_item_id": item_id,
            "category": category,
            "tradeable": tradeable,
            "stackable": stackable,
        }

    item_ids = {
        "Air rune": 556,
        "Mind rune": 558,
        "Water rune": 555,
        "Earth rune": 557,
        "Fire rune": 554,
        "Body rune": 559,
        "Cosmic rune": 564,
        "Chaos rune": 562,
        "Astral rune": 9075,
        "Nature rune": 561,
        "Law rune": 563,
        "Death rune": 560,
        "Blood rune": 565,
        "Mist rune": 4695,
        "Dust rune": 4696,
        "Mud rune": 4698,
        "Smoke rune": 4697,
        "Steam rune": 4694,
        "Lava rune": 4699,
        "Air talisman": 1438,
        "Earth talisman": 1440,
        "Fire talisman": 1442,
        "Water talisman": 1444,
        "Body talisman": 1446,
        "Mind talisman": 1448,
        "Blood talisman": 1450,
        "Chaos talisman": 1452,
        "Cosmic talisman": 1454,
        "Death talisman": 1456,
        "Law talisman": 1458,
        "Nature talisman": 1462,
        "Air tiara": 5527,
        "Mind tiara": 5529,
        "Water tiara": 5531,
        "Body tiara": 5533,
        "Earth tiara": 5535,
        "Fire tiara": 5537,
        "Cosmic tiara": 5539,
        "Nature tiara": 5541,
        "Chaos tiara": 5543,
        "Law tiara": 5545,
        "Death tiara": 5547,
        "Blood tiara": 5549,
        "Elemental talisman": 5516,
        "Omni-talisman": 13649,
        "Omni-tiara": 13655,
        "Small pouch": 5509,
        "Medium pouch": 5510,
        "Medium pouch (worn)": 5511,
        "Large pouch": 5512,
        "Large pouch (worn)": 5513,
        "Giant pouch": 5514,
        "Giant pouch (worn)": 5515,
        BINDING_NECKLACE_ITEM: 5521,
        WICKED_HOOD_ITEM: 22332,
    }
    rune_item_names = set(runecrafting_rune_output_items())
    for name, item_id in item_ids.items():
        hood_items = {WICKED_HOOD_ITEM, "Elemental talisman", "Omni-talisman", "Omni-tiara"}
        source = (
            "https://runescape.wiki/w/Wicked_hood?oldid=6564747"
            if name in hood_items
            else ITEMS_SOURCE_PATH
        )
        add_item(
            name,
            item_id,
            source,
            tradeable=name not in {WICKED_HOOD_ITEM, "Omni-talisman", "Omni-tiara"},
            stackable=name in rune_item_names,
        )
    return data


def runecrafting_pouches_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        pouch.id: {
            "id": pouch.id,
            "display_name": pouch.display_name,
            "degraded_item": pouch.degraded_item,
            "capacity": pouch.capacity,
            "required_level": pouch.required_level,
            "degradation_threshold": pouch.degradation_threshold,
            "source_item_id": pouch.source_item_id,
            "degraded_source_item_id": pouch.degraded_source_item_id,
            "source": pouch.source,
        }
        for pouch in POUCHES
    }
