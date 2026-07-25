"""Period-pinned data and explicit breadth abstractions for Vinesweeper."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VINESWEEPER_ACTIVITY_ID = "vinesweeper"
VINESWEEPER_FLAG_CAP = 10
VINESWEEPER_FREE_FLAGS = 10
VINESWEEPER_FLAG_COIN_PRICE = 500
VINESWEEPER_FLAG_POINT_PRICE = 50
VINESWEEPER_OGLEROOT_COIN_PRICE = 10
VINESWEEPER_RABBIT_HUNTER_XP = 30.0
COMPOST_POTION_ACTIVITY_ID = "use_compost_potion"
COMPOST_POTION_DOSES = (
    "Compost potion (4)",
    "Compost potion (3)",
    "Compost potion (2)",
    "Compost potion (1)",
)

VINESWEEPER_SOURCE = (
    "RuneScape Wiki Vinesweeper oldid=6288368 "
    "(2012-09-24T04:55:21Z); hidden outcome weights source_blocked, "
    "bounded abstraction recorded in memory-bank/source-audits/"
    "vinesweeper-loop-2026-07-18.md"
)


@dataclass(frozen=True)
class VinesweeperReward:
    id: str
    display_name: str
    item_name: str
    point_price: int


VINESWEEPER_REWARDS = (
    VinesweeperReward("flag", "Flag", "Flag", 50),
    VinesweeperReward("cabbage_seed", "Cabbage seed", "Cabbage seed", 10),
    VinesweeperReward("tomato_seed", "Tomato seed", "Tomato seed", 10),
    VinesweeperReward("sweetcorn_seed", "Sweetcorn seed", "Sweetcorn seed", 150),
    VinesweeperReward("strawberry_seed", "Strawberry seed", "Strawberry seed", 165),
    VinesweeperReward("watermelon_seed", "Watermelon seed", "Watermelon seed", 680),
    VinesweeperReward("guam_seed", "Guam seed", "Guam seed", 10),
    VinesweeperReward("marrentill_seed", "Marrentill seed", "Marrentill seed", 10),
    VinesweeperReward("tarromin_seed", "Tarromin seed", "Tarromin seed", 10),
    VinesweeperReward("avantoe_seed", "Avantoe seed", "Avantoe seed", 1_250),
    VinesweeperReward("wergali_seed", "Wergali seed", "Wergali seed", 3_800),
    VinesweeperReward("ranarr_seed", "Ranarr seed", "Ranarr seed", 4_000),
    VinesweeperReward("kwuarm_seed", "Kwuarm seed", "Kwuarm seed", 1_000),
    VinesweeperReward("cadantine_seed", "Cadantine seed", "Cadantine seed", 1_000),
    VinesweeperReward("snapdragon_seed", "Snapdragon seed", "Snapdragon seed", 16_000),
    VinesweeperReward("lantadyme_seed", "Lantadyme seed", "Lantadyme seed", 7_500),
    VinesweeperReward("dwarf_weed_seed", "Dwarf weed seed", "Dwarf weed seed", 9_000),
    VinesweeperReward("torstol_seed", "Torstol seed", "Torstol seed", 45_000),
    VinesweeperReward("rosemary_seed", "Rosemary seed", "Rosemary seed", 10),
    VinesweeperReward("nasturtium_seed", "Nasturtium seed", "Nasturtium seed", 10),
    VinesweeperReward("woad_seed", "Woad seed", "Woad seed", 30),
    VinesweeperReward("limpwurt_seed", "Limpwurt seed", "Limpwurt seed", 70),
    VinesweeperReward("cactus_seed", "Cactus seed", "Cactus seed", 1_200),
    VinesweeperReward("bittercap_spore", "Bittercap mushroom spore", "Bittercap mushroom spore", 800),
    VinesweeperReward("belladonna_seed", "Belladonna seed", "Belladonna seed", 300),
    VinesweeperReward("asgarnian_seed", "Asgarnian seed", "Asgarnian seed", 5),
    VinesweeperReward("jute_seed", "Jute seed", "Jute seed", 50),
    VinesweeperReward("yanillian_seed", "Yanillian seed", "Yanillian seed", 60),
    VinesweeperReward("krandorian_seed", "Krandorian seed", "Krandorian seed", 20),
    VinesweeperReward("wildblood_seed", "Wildblood seed", "Wildblood seed", 100),
    VinesweeperReward("redberry_seed", "Redberry seed", "Redberry seed", 5),
    VinesweeperReward("cadavaberry_seed", "Cadavaberry seed", "Cadavaberry seed", 5),
    VinesweeperReward("dwellberry_seed", "Dwellberry seed", "Dwellberry seed", 5),
    VinesweeperReward("jangerberry_seed", "Jangerberry seed", "Jangerberry seed", 10),
    VinesweeperReward("whiteberry_seed", "Whiteberry seed", "Whiteberry seed", 25),
    VinesweeperReward("poison_ivy_seed", "Poison ivy seed", "Poison ivy seed", 30),
    VinesweeperReward("acorn", "Acorn", "Acorn", 100),
    VinesweeperReward("willow_seed", "Willow seed", "Willow seed", 1_800),
    VinesweeperReward("maple_seed", "Maple seed", "Maple seed", 12_000),
    VinesweeperReward("yew_seed", "Yew seed", "Yew seed", 29_000),
    VinesweeperReward("pineapple_seed", "Pineapple seed", "Pineapple seed", 10_000),
    VinesweeperReward("papaya_tree_seed", "Papaya tree seed", "Papaya tree seed", 20_000),
    VinesweeperReward("palm_tree_seed", "Palm tree seed", "Palm tree seed", 35_000),
    VinesweeperReward("calquat_tree_seed", "Calquat tree seed", "Calquat tree seed", 35_000),
    VinesweeperReward("spirit_tree_seed", "Spirit tree seed", "Spirit seed", 55_000),
    VinesweeperReward("compost_potion_4", "Compost potion (4)", "Compost potion (4)", 5_000),
)
VINESWEEPER_REWARDS_BY_ID = {reward.id: reward for reward in VINESWEEPER_REWARDS}

VINESWEEPER_EXTRA_ITEM_DATA = {
    name: {
        "category": "material",
        "item_id": item_id,
        "stackable": False,
        "tradeable": True,
        "source": (
            "RuneScape Wiki Compost potion oldid=6357928; "
            f"OpenRS2 rev-742 item {item_id}"
        ),
    }
    for name, item_id in zip(COMPOST_POTION_DOSES, (6470, 6472, 6474, 6476))
}


def vinesweeper_extra_items_as_dict() -> dict[str, dict[str, Any]]:
    return {name: dict(spec) for name, spec in VINESWEEPER_EXTRA_ITEM_DATA.items()}


def compost_potion_activities_as_dict() -> dict[str, dict[str, Any]]:
    return {
        COMPOST_POTION_ACTIVITY_ID: {
            "display_name": "Upgrade compost with compost potion",
            "requirements": {"Compost": 1},
            "any_requirements": COMPOST_POTION_DOSES,
            "outputs": {"Supercompost": 1},
            "batch_size": 1,
            "group": "material_processing",
            "source": "RuneScape Wiki Compost potion oldid=6357928",
        }
    }


def vinesweeper_activity_as_dict() -> dict[str, dict[str, Any]]:
    return {
        VINESWEEPER_ACTIVITY_ID: {
            "display_name": "Vinesweeper",
            "requirements": {},
            "batch_size": 1,
            "group": "minigames",
            "source": VINESWEEPER_SOURCE,
        }
    }
