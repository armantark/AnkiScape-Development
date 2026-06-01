"""2011Scape-sourced Mining data for AnkiScape.

The plugin-backed rows come from the local 2011Scape rev 667 Mining source.
Ordinary rocks that are present in the 2011-era item/cache data but not
implemented by that plugin are added only when the historical wiki gives a
clear level/XP/output contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional, Tuple


ROCK_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/mining/RockType.kt"
)
PICKAXE_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/mining/PickaxeType.kt"
)
MINING_RUNTIME_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/skills/mining/Mining.kt"
)
ITEMS_SOURCE_PATH = "/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml"
HISTORICAL_MINING_SOURCE = "https://runescape.wiki/w/Mining_(Historical)"
OSRS_GEM_ROCK_SOURCE = "https://oldschool.runescape.wiki/w/Gem_rocks"


@dataclass(frozen=True)
class WeightedMiningOutput:
    item: str
    weight: int
    base_exp: float
    source_item_id: Optional[int] = None
    tradeable: bool = True


@dataclass(frozen=True)
class MiningTarget:
    id: str
    display_name: str
    level: int
    base_exp: float
    output_item: Optional[str]
    source_item_id: Optional[int]
    low_chance: int
    high_chance: int
    respawn_time: int
    varrock_armour_tier: Optional[int]
    source: str = ROCK_SOURCE_PATH
    status: str = "implemented"
    alternate_output_item: Optional[str] = None
    alternate_output_level: Optional[int] = None
    weighted_outputs: Tuple[WeightedMiningOutput, ...] = ()
    allows_random_gems: bool = True
    notes: str = ""
    output_tradeable: bool = True
    alternate_output_tradeable: bool = True


@dataclass(frozen=True)
class MiningPickaxe:
    id: str
    display_name: str
    item_id: int
    level: int
    ticks_between_rolls: int
    source_level: Optional[int] = None
    source: str = PICKAXE_SOURCE_PATH
    status: str = "implemented"
    notes: str = ""
    tradeable: bool = True


@dataclass(frozen=True)
class MiningBonusItem:
    id: str
    display_name: str
    item_id: int
    slot: str
    bonus_type: str
    tier: int = 1
    source: str = MINING_RUNTIME_SOURCE_PATH
    status: str = "implemented"
    notes: str = ""
    tradeable: bool = False


@dataclass(frozen=True)
class DeferredMiningContent:
    id: str
    display_name: str
    status: str
    reason: str
    source: str


def _target(
    id: str,
    display_name: str,
    level: int,
    base_exp: float,
    output_item: Optional[str],
    source_item_id: Optional[int],
    low_chance: int,
    high_chance: int,
    respawn_time: int,
    varrock_armour_tier: Optional[int],
    **kwargs: object,
) -> MiningTarget:
    return MiningTarget(
        id=id,
        display_name=display_name,
        level=level,
        base_exp=base_exp,
        output_item=output_item,
        source_item_id=source_item_id,
        low_chance=low_chance,
        high_chance=high_chance,
        respawn_time=respawn_time,
        varrock_armour_tier=varrock_armour_tier,
        **kwargs,
    )


MINING_TARGETS: Tuple[MiningTarget, ...] = (
    _target(
        "rune_essence",
        "Rune essence",
        1,
        5.0,
        "Rune essence",
        1436,
        255,
        392,
        -1,
        None,
        alternate_output_item="Pure essence",
        alternate_output_level=30,
        allows_random_gems=False,
        notes="2011Scape uses one essence rock; level 30+ receives pure essence.",
    ),
    _target("clay", "Clay", 1, 5.0, "Clay", 434, 128, 392, 2, 1),
    _target("copper", "Copper", 1, 17.5, "Copper ore", 436, 102, 379, 4, 1),
    _target("tin", "Tin", 1, 17.5, "Tin ore", 438, 102, 379, 4, 1),
    _target("blurite", "Blurite", 10, 17.5, "Blurite ore", 668, 106, 365, 25, 3, output_tradeable=False),
    _target("limestone", "Limestone", 10, 26.5, "Limestone", 3211, 106, 365, 25, 1, source=HISTORICAL_MINING_SOURCE),
    _target("iron", "Iron", 15, 35.0, "Iron ore", 440, 109, 346, 9, 1),
    _target("silver", "Silver", 20, 40.0, "Silver ore", 442, 24, 200, 100, 1),
    _target("coal", "Coal", 30, 50.0, "Coal", 453, 15, 100, 50, 1),
    _target(
        "sandstone",
        "Sandstone",
        35,
        0.0,
        None,
        None,
        15,
        100,
        8,
        1,
        source=HISTORICAL_MINING_SOURCE,
        weighted_outputs=(
            WeightedMiningOutput("Sandstone (1kg)", 1, 30.0, 6971),
            WeightedMiningOutput("Sandstone (2kg)", 1, 40.0, 6973),
            WeightedMiningOutput("Sandstone (5kg)", 1, 50.0, 6975),
            WeightedMiningOutput("Sandstone (10kg)", 1, 60.0, 6977),
        ),
        allows_random_gems=False,
        notes="Weights are not available in 2011Scape plugin; equal weights keep the target playable until a cache/source table is found.",
    ),
    _target("gold", "Gold", 40, 65.0, "Gold ore", 444, 6, 75, 100, 1),
    _target(
        "gem_rocks",
        "Gem rocks",
        40,
        65.0,
        None,
        None,
        46,
        71,
        99,
        None,
        source=HISTORICAL_MINING_SOURCE,
        weighted_outputs=(
            WeightedMiningOutput("Uncut opal", 60, 65.0, 1625),
            WeightedMiningOutput("Uncut jade", 30, 65.0, 1627),
            WeightedMiningOutput("Uncut red topaz", 15, 65.0, 1629),
            WeightedMiningOutput("Uncut sapphire", 9, 65.0, 1623),
            WeightedMiningOutput("Uncut emerald", 5, 65.0, 1621),
            WeightedMiningOutput("Uncut ruby", 5, 65.0, 1619),
            WeightedMiningOutput("Uncut diamond", 4, 65.0, 1617),
        ),
        allows_random_gems=False,
        notes="Historical source gives level/XP; OSRS gem-rate weights are used as a practical 2007/2011-shared cross-check.",
    ),
    _target(
        "granite",
        "Granite",
        45,
        0.0,
        None,
        None,
        33,
        65,
        8,
        1,
        source=HISTORICAL_MINING_SOURCE,
        weighted_outputs=(
            WeightedMiningOutput("Granite (500g)", 1, 50.0, 6979),
            WeightedMiningOutput("Granite (2kg)", 1, 60.0, 6981),
            WeightedMiningOutput("Granite (5kg)", 1, 75.0, 6983),
        ),
        allows_random_gems=False,
        notes="Historical source confirms sizes/XP; equal weights are a conservative AnkiScape simplification.",
    ),
    _target("mithril", "Mithril", 55, 80.0, "Mithril ore", 447, 2, 50, 200, 2),
    _target("adamantite", "Adamantite", 70, 95.0, "Adamantite ore", 449, 1, 25, 400, 3),
    _target("runite", "Runite", 85, 125.0, "Runite ore", 451, 1, 18, 1200, 4),
)


DEFERRED_MINING_CONTENT: Tuple[DeferredMiningContent, ...] = (
    DeferredMiningContent(
        "concentrated_coal",
        "Concentrated coal",
        "deferred_dependency",
        "Source distinction is Living Rock Caverns/depletion behavior; output and XP match coal in the current review loop.",
        ROCK_SOURCE_PATH,
    ),
    DeferredMiningContent(
        "concentrated_gold",
        "Concentrated gold",
        "deferred_dependency",
        "Source distinction is Living Rock Caverns/depletion behavior; output and XP match gold in the current review loop.",
        ROCK_SOURCE_PATH,
    ),
    DeferredMiningContent(
        "shooting_stars",
        "Shooting Stars",
        "future_content",
        "Distraction and Diversion with world timing, stardust, and reward exchange; needs its own activity design.",
        HISTORICAL_MINING_SOURCE,
    ),
    DeferredMiningContent(
        "random_events",
        "Mining random events",
        "not_applicable",
        "Rock golem and pickaxe-head events were discontinued before the target era and do not fit review rewards.",
        HISTORICAL_MINING_SOURCE,
    ),
)


MINING_PICKAXES: Tuple[MiningPickaxe, ...] = (
    MiningPickaxe("bronze_pickaxe", "Bronze pickaxe", 1265, 1, 8),
    MiningPickaxe("iron_pickaxe", "Iron pickaxe", 1267, 1, 7),
    MiningPickaxe("steel_pickaxe", "Steel pickaxe", 1269, 6, 6),
    MiningPickaxe("mithril_pickaxe", "Mithril pickaxe", 1273, 21, 5),
    MiningPickaxe("adamant_pickaxe", "Adamant pickaxe", 1271, 31, 4),
    MiningPickaxe("rune_pickaxe", "Rune pickaxe", 1275, 41, 3),
    MiningPickaxe(
        "dragon_pickaxe",
        "Dragon pickaxe",
        15261,
        61,
        3,
        notes="2011Scape PickaxeType points at item 15259, but items.yml marks 15261 as the tradeable Used for mining item; AnkiScape uses 15261.",
    ),
    MiningPickaxe("gilded_bronze_pickaxe", "Gilded bronze pickaxe", 20780, 1, 8),
    MiningPickaxe("gilded_iron_pickaxe", "Gilded iron pickaxe", 20781, 1, 7),
    MiningPickaxe("gilded_steel_pickaxe", "Gilded steel pickaxe", 20782, 6, 6, source_level=1, notes="Local source lists level 1; normalized to steel pickaxe requirement."),
    MiningPickaxe("gilded_mithril_pickaxe", "Gilded mithril pickaxe", 20784, 21, 5),
    MiningPickaxe("gilded_adamant_pickaxe", "Gilded adamant pickaxe", 20783, 31, 4, source_level=1, notes="Local source lists level 1; normalized to adamant pickaxe requirement."),
    MiningPickaxe("gilded_rune_pickaxe", "Gilded rune pickaxe", 20785, 41, 3, source_level=1, notes="Local source lists level 1; normalized to rune pickaxe requirement."),
    MiningPickaxe("gilded_dragon_pickaxe", "Gilded dragon pickaxe", 20786, 61, 3, notes="Shares Dragon-tier Anki behavior."),
)


DEFERRED_MINING_PICKAXES: Tuple[MiningPickaxe, ...] = (
    MiningPickaxe(
        "inferno_adze",
        "Inferno adze",
        13661,
        41,
        3,
        status="deferred_special",
        notes="Requires broader All Fired Up / Firemaking reward handling.",
        tradeable=False,
    ),
)


MINING_BONUS_ITEMS: Tuple[MiningBonusItem, ...] = (
    MiningBonusItem("amulet_of_glory", "Amulet of glory", 1704, "amulet", "gem_chance"),
    MiningBonusItem("amulet_of_glory_1", "Amulet of glory (1)", 1706, "amulet", "gem_chance"),
    MiningBonusItem("amulet_of_glory_2", "Amulet of glory (2)", 1708, "amulet", "gem_chance"),
    MiningBonusItem("amulet_of_glory_3", "Amulet of glory (3)", 1710, "amulet", "gem_chance"),
    MiningBonusItem("amulet_of_glory_4", "Amulet of glory (4)", 1712, "amulet", "gem_chance"),
    MiningBonusItem("varrock_armour_1", "Varrock armour 1", 11756, "chest", "extra_ore", tier=1),
    MiningBonusItem("varrock_armour_2", "Varrock armour 2", 11757, "chest", "extra_ore", tier=2),
    MiningBonusItem("varrock_armour_3", "Varrock armour 3", 11758, "chest", "extra_ore", tier=3),
    MiningBonusItem(
        "varrock_armour_4",
        "Varrock armour 4",
        19757,
        "chest",
        "extra_ore",
        tier=4,
        notes="items.yml marks this tradeable, but Varrock armour is diary reward equipment; AnkiScape normalizes it to non-tradeable.",
    ),
)


INCIDENTAL_GEM_DROP_CHANCE = 1 / 256
GLORY_GEM_DROP_CHANCE = 1 / 86
INCIDENTAL_GEM_DROP_TABLE: Tuple[WeightedMiningOutput, ...] = (
    WeightedMiningOutput("Uncut diamond", 1, 0.0, 1617),
    WeightedMiningOutput("Uncut ruby", 1, 0.0, 1619),
    WeightedMiningOutput("Uncut emerald", 1, 0.0, 1621),
    WeightedMiningOutput("Uncut sapphire", 1, 0.0, 1623),
)


MINING_TARGETS_BY_ID: Dict[str, MiningTarget] = {target.id: target for target in MINING_TARGETS}
MINING_PICKAXES_BY_ID: Dict[str, MiningPickaxe] = {pickaxe.id: pickaxe for pickaxe in MINING_PICKAXES}
MINING_BONUS_ITEMS_BY_ID: Dict[str, MiningBonusItem] = {item.id: item for item in MINING_BONUS_ITEMS}

DEFAULT_MINING_TARGET = "rune_essence"
DEFAULT_MINING_TOOLBELT: Mapping[str, Tuple[str, ...]] = {"mining": ("bronze_pickaxe",)}

LEGACY_ORE_TARGETS: Mapping[str, str] = {
    "Rune essence": "rune_essence",
    "Pure essence": "rune_essence",
    "Clay": "clay",
    "Copper ore": "copper",
    "Tin ore": "tin",
    "Blurite ore": "blurite",
    "Limestone": "limestone",
    "Iron ore": "iron",
    "Silver ore": "silver",
    "Coal": "coal",
    "Sandstone": "sandstone",
    "Gold ore": "gold",
    "Gem Rock": "gem_rocks",
    "Gem rocks": "gem_rocks",
    "Granite": "granite",
    "Mithril ore": "mithril",
    "Adamantite ore": "adamantite",
    "Runite ore": "runite",
}


def mining_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        target.id: {
            "display_name": target.display_name,
            "level": target.level,
            "exp": target.base_exp,
            "output_item": target.output_item,
            "output_tradeable": target.output_tradeable,
            "source_item_id": target.source_item_id,
            "low_chance": target.low_chance,
            "high_chance": target.high_chance,
            "respawn_time": target.respawn_time,
            "varrock_armour_tier": target.varrock_armour_tier,
            "source": target.source,
            "status": target.status,
            "alternate_output_item": target.alternate_output_item,
            "alternate_output_level": target.alternate_output_level,
            "alternate_output_tradeable": target.alternate_output_tradeable,
            "weighted_outputs": tuple(
                {
                    "item": output.item,
                    "weight": output.weight,
                    "exp": output.base_exp,
                    "source_item_id": output.source_item_id,
                    "tradeable": output.tradeable,
                }
                for output in target.weighted_outputs
            ),
            "allows_random_gems": target.allows_random_gems,
            "notes": target.notes,
        }
        for target in MINING_TARGETS
    }


def mining_pickaxes_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        pickaxe.id: {
            "display_name": pickaxe.display_name,
            "item_id": pickaxe.item_id,
            "level": pickaxe.level,
            "source_level": pickaxe.source_level,
            "ticks_between_rolls": pickaxe.ticks_between_rolls,
            "ratio": 8 / pickaxe.ticks_between_rolls,
            "source": pickaxe.source,
            "status": pickaxe.status,
            "notes": pickaxe.notes,
            "tradeable": pickaxe.tradeable,
        }
        for pickaxe in MINING_PICKAXES
    }


def mining_bonus_items_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        bonus_item.id: {
            "display_name": bonus_item.display_name,
            "item_id": bonus_item.item_id,
            "equipment_slot": bonus_item.slot,
            "equipment_type": bonus_item.bonus_type,
            "tier": bonus_item.tier,
            "source": bonus_item.source,
            "status": bonus_item.status,
            "notes": bonus_item.notes,
            "tradeable": bonus_item.tradeable,
        }
        for bonus_item in MINING_BONUS_ITEMS
    }


def mining_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    items: Dict[str, Dict[str, object]] = {}
    for target in MINING_TARGETS:
        if target.output_item:
            items.setdefault(
                target.output_item,
                {
                    "category": "ore",
                    "level": target.level,
                    "exp": target.base_exp,
                    "source": target.source,
                    "item_id": target.source_item_id,
                    "tradeable": target.output_tradeable,
                },
            )
        if target.alternate_output_item:
            items.setdefault(
                target.alternate_output_item,
                {
                    "category": "ore",
                    "level": target.alternate_output_level or target.level,
                    "exp": target.base_exp,
                    "source": target.source,
                    "tradeable": target.alternate_output_tradeable,
                },
            )
        for output in target.weighted_outputs:
            items.setdefault(
                output.item,
                {
                    "category": "gem" if output.item.startswith("Uncut ") else "ore",
                    "level": target.level,
                    "exp": output.base_exp,
                    "source": target.source,
                    "item_id": output.source_item_id,
                    "tradeable": output.tradeable,
                },
            )
    for output in INCIDENTAL_GEM_DROP_TABLE:
        items.setdefault(
            output.item,
            {
                "category": "gem",
                "source": MINING_RUNTIME_SOURCE_PATH,
                "item_id": output.source_item_id,
                "tradeable": output.tradeable,
            },
        )
    for pickaxe in MINING_PICKAXES + DEFERRED_MINING_PICKAXES:
        items[pickaxe.display_name] = {
            "category": "tool",
            "level": pickaxe.level,
            "source": pickaxe.source,
            "item_id": pickaxe.item_id,
            "status": pickaxe.status,
            "tradeable": pickaxe.tradeable,
        }
    for bonus_item in MINING_BONUS_ITEMS:
        items[bonus_item.display_name] = {
            "category": "equipment",
            "source": bonus_item.source,
            "item_id": bonus_item.item_id,
            "equipment_slot": bonus_item.slot,
            "equipment_type": bonus_item.bonus_type,
            "tier": bonus_item.tier,
            "status": bonus_item.status,
            "tradeable": bonus_item.tradeable,
        }
    return items


def mining_output_items() -> Tuple[str, ...]:
    seen: Dict[str, None] = {}
    for target in MINING_TARGETS:
        if target.output_item:
            seen.setdefault(target.output_item, None)
        if target.alternate_output_item:
            seen.setdefault(target.alternate_output_item, None)
        for output in target.weighted_outputs:
            seen.setdefault(output.item, None)
    return tuple(seen)

