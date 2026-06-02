# constants.py

import os
import re

try:
    from .item_registry import build_item_definitions
    from .mining_data import (
        DEFAULT_MINING_TARGET,
        GLORY_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_TABLE as SOURCE_INCIDENTAL_GEM_DROP_TABLE,
        mining_bonus_items_as_dict,
        mining_extra_items_as_dict,
        mining_output_items,
        mining_pickaxes_as_dict,
        mining_targets_as_dict,
    )
    from .smithing_data import (
        DEFAULT_SMITHING_TARGET,
        smithing_bars_as_dict,
        smithing_extra_items_as_dict,
        smithing_output_items,
        smithing_recipes_as_dict,
    )
    from .woodcutting_data import (
        BIRD_NEST_DROP_CHANCE,
        BIRD_NEST_DROP_TABLE as SOURCE_BIRD_NEST_DROP_TABLE,
        BIRD_NEST_OPEN_TABLES_BY_INPUT as SOURCE_BIRD_NEST_OPEN_TABLES_BY_INPUT,
        BIRD_NEST_OPEN_TABLES_BY_INPUT,
        DEFAULT_WOODCUTTING_TARGET,
        woodcutting_axes_as_dict,
        woodcutting_extra_items_as_dict,
        woodcutting_targets_as_dict,
    )
except ImportError:
    from item_registry import build_item_definitions
    from mining_data import (
        DEFAULT_MINING_TARGET,
        GLORY_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_CHANCE,
        INCIDENTAL_GEM_DROP_TABLE as SOURCE_INCIDENTAL_GEM_DROP_TABLE,
        mining_bonus_items_as_dict,
        mining_extra_items_as_dict,
        mining_output_items,
        mining_pickaxes_as_dict,
        mining_targets_as_dict,
    )
    from smithing_data import (
        DEFAULT_SMITHING_TARGET,
        smithing_bars_as_dict,
        smithing_extra_items_as_dict,
        smithing_output_items,
        smithing_recipes_as_dict,
    )
    from woodcutting_data import (
        BIRD_NEST_DROP_CHANCE,
        BIRD_NEST_DROP_TABLE as SOURCE_BIRD_NEST_DROP_TABLE,
        BIRD_NEST_OPEN_TABLES_BY_INPUT as SOURCE_BIRD_NEST_OPEN_TABLES_BY_INPUT,
        BIRD_NEST_OPEN_TABLES_BY_INPUT,
        DEFAULT_WOODCUTTING_TARGET,
        woodcutting_axes_as_dict,
        woodcutting_extra_items_as_dict,
        woodcutting_targets_as_dict,
    )

# Base probabilities and factors
BASE_WOODCUTTING_PROBABILITY = 0.8
BASE_MINING_PROBABILITY = 0.8
LEVEL_BONUS_FACTOR = 0.02

# File paths
current_dir = os.path.dirname(os.path.abspath(__file__))
ores_folder = os.path.join(current_dir, "ores")
trees_folder = os.path.join(current_dir, "trees")
GEMS_FOLDER = os.path.join(current_dir, "gems")
bars_folder = os.path.join(current_dir, "bars")
FLETCHED_ITEMS_FOLDER = os.path.join(current_dir, "fletcheditems")
# Woodcutting bank items (hatchets, bird nests, seed contents). Logs reuse the
# trees/ sprites — those files are the log item art (see WIKI_TITLE_OVERRIDES in
# tools/fetch_assets.py) — so only non-log Woodcutting items live here.
WOODCUTTING_ITEMS_FOLDER = os.path.join(current_dir, "woodcuttingitems")
# Mining bank items that aren't ores/gems: pickaxes (and future bonus equipables).
# Fetched into miningitems/ by tools/fetch_mining_assets.py.
MINING_ITEMS_FOLDER = os.path.join(current_dir, "miningitems")
# Forged Smithing outputs (weapons/armour/tools/ammo). Bars reuse bars_folder via
# BAR_IMAGES; everything anvil-made is fetched here by tools/fetch_smithing_assets.py.
# Optional: any output without a file degrades to an iconless row.
SMITHING_ITEMS_FOLDER = os.path.join(current_dir, "smithingitems")

# Image dictionaries
# New constants for Crafting
CRAFTED_ITEMS_FOLDER = os.path.join(current_dir, "crafteditems")

DEFAULT_UTILITY_ACTIVITY = "make_soft_clay"
UTILITY_ACTIVITY_DATA = {
    "make_soft_clay": {
        "display_name": "Make soft clay",
        "requirements": {"Clay": 1},
        "output_item": "Soft clay",
        "output_qty": 1,
        "batch_size": 28,
        "source": "OSRS Soft clay > Creation > Container",
    },
    "gather_wool": {
        "display_name": "Gather wool",
        "requirements": {},
        "output_item": "Wool",
        "output_qty": 1,
        "batch_size": 28,
        "source": "Material source for OSRS Ball of wool > Creation",
    },
    "gather_flax": {
        "display_name": "Gather flax",
        "requirements": {},
        "output_item": "Flax",
        "output_qty": 1,
        "batch_size": 28,
        "source": "OSRS Bow string > Strategy > Manual Spinning",
    },
    "open_bird_nest": {
        "display_name": "Open bird nests",
        "requirements": {},
        "openable_items": tuple(BIRD_NEST_OPEN_TABLES_BY_INPUT.keys()),
        "batch_size": 28,
        "source": "2011Scape bird_nest.plugin.kts",
    },
}

CRAFTING_DATA = {
    "Unfired pot": {"level": 1, "exp": 6.3, "requirements": {"Soft clay": 1}, "source": "OSRS Crafting > Pottery"},
    "Pot": {"level": 1, "exp": 6.3, "requirements": {"Unfired pot": 1}, "source": "OSRS Crafting > Pottery"},
    "Ball of wool": {"level": 1, "exp": 2.5, "requirements": {"Wool": 1}, "batch_size": 28, "source": "OSRS Ball of wool > Creation"},
    "Gold ring": {"level": 5, "exp": 15, "requirements": {"Gold bar": 1}},
    "Gold necklace": {"level": 6, "exp": 20, "requirements": {"Gold bar": 1}},
    "Unfired pie dish": {"level": 7, "exp": 15, "requirements": {"Soft clay": 1}, "source": "OSRS Crafting > Pottery"},
    "Pie dish": {"level": 7, "exp": 10, "requirements": {"Unfired pie dish": 1}, "source": "OSRS Crafting > Pottery"},
    "Unfired bowl": {"level": 8, "exp": 18, "requirements": {"Soft clay": 1}, "source": "OSRS Crafting > Pottery"},
    "Bowl": {"level": 8, "exp": 15, "requirements": {"Unfired bowl": 1}, "source": "OSRS Crafting > Pottery"},
    "Bow string": {"level": 10, "exp": 15, "requirements": {"Flax": 1}, "batch_size": 28, "source": "OSRS Bow string > Creation"},
    "Unstrung symbol": {"level": 16, "exp": 50, "requirements": {"Silver bar": 1}},
    "Sapphire ring": {"level": 20, "exp": 40, "requirements": {"Gold bar": 1, "Sapphire": 1}},
    "Sapphire": {"level": 20, "exp": 50, "requirements": {"Uncut sapphire": 1}},
    "Silver bolts (unf)": {
        "level": 21,
        "exp": 50,
        "requirements": {"Silver bar": 1},
        "output_qty": 10,
        "source": "OSRS Silver bolts (unf) > Creation",
    },
    "Sapphire necklace": {"level": 22, "exp": 60, "requirements": {"Gold bar": 1, "Sapphire": 1}},
    "Tiara": {"level": 23, "exp": 52.5, "requirements": {"Silver bar": 1}},
    "Emerald": {"level": 27, "exp": 67.5, "requirements": {"Uncut emerald": 1}},
    "Emerald ring": {"level": 27, "exp": 55, "requirements": {"Gold bar": 1, "Emerald": 1}},
    "Emerald necklace": {"level": 29, "exp": 60, "requirements": {"Gold bar": 1, "Emerald": 1}},
    "Ruby ring": {"level": 34, "exp": 70, "requirements": {"Gold bar": 1, "Ruby": 1}},
    "Ruby": {"level": 34, "exp": 85, "requirements": {"Uncut ruby": 1}},
    "Ruby necklace": {"level": 40, "exp": 75, "requirements": {"Gold bar": 1, "Ruby": 1}},
    "Diamond ring": {"level": 43, "exp": 85, "requirements": {"Gold bar": 1, "Diamond": 1}},
    "Diamond": {"level": 43, "exp": 107.5, "requirements": {"Uncut diamond": 1}},
    "Diamond necklace": {"level": 56, "exp": 90, "requirements": {"Gold bar": 1, "Diamond": 1}},
}

CRAFTED_ITEM_IMAGES = {item: os.path.join(CRAFTED_ITEMS_FOLDER, f"{item.lower().replace(' ', '_')}.png") for item in CRAFTING_DATA}
UTILITY_ITEM_IMAGES = {
    "Soft clay": os.path.join(CRAFTED_ITEMS_FOLDER, "soft_clay.png"),
    "Wool": os.path.join(CRAFTED_ITEMS_FOLDER, "wool.png"),
    "Flax": os.path.join(CRAFTED_ITEMS_FOLDER, "flax.png"),
}

TREE_IMAGES = {tree.split('.')[0]: os.path.join(trees_folder, tree) for tree in os.listdir(trees_folder) if tree.endswith('.png')}

ORE_IMAGES = {
    "Rune essence": os.path.join(ores_folder, "RuneEssence.png"),
    "Clay": os.path.join(ores_folder, "Clay.png"),
    "Copper ore": os.path.join(ores_folder, "Copper.png"),
    "Tin ore": os.path.join(ores_folder, "Tin.png"),
    "Iron ore": os.path.join(ores_folder, "Iron.png"),
    "Silver ore": os.path.join(ores_folder, "Silver.png"),
    "Coal": os.path.join(ores_folder, "Coal.png"),
    "Gold ore": os.path.join(ores_folder, "Gold.png"),
    "Mithril ore": os.path.join(ores_folder, "Mithril.png"),
    "Adamantite ore": os.path.join(ores_folder, "Adamantite.png"),
    "Runite ore": os.path.join(ores_folder, "Runite.png")
}
for _item_name, _filename in {
    "Pure essence": "pure_essence.png",
    "Blurite ore": "blurite_ore.png",
    "Limestone": "limestone.png",
    "Sandstone (1kg)": "sandstone_1kg.png",
    "Sandstone (2kg)": "sandstone_2kg.png",
    "Sandstone (5kg)": "sandstone_5kg.png",
    "Sandstone (10kg)": "sandstone_10kg.png",
    "Granite (500g)": "granite_500g.png",
    "Granite (2kg)": "granite_2kg.png",
    "Granite (5kg)": "granite_5kg.png",
}.items():
    _path = os.path.join(ores_folder, _filename)
    if os.path.exists(_path):
        ORE_IMAGES[_item_name] = _path

GEM_IMAGES = {
    "Uncut sapphire": os.path.join(GEMS_FOLDER, "sapphire.png"),
    "Uncut emerald": os.path.join(GEMS_FOLDER, "emerald.png"),
    "Uncut ruby": os.path.join(GEMS_FOLDER, "ruby.png"),
    "Uncut diamond": os.path.join(GEMS_FOLDER, "diamond.png"),
}
# Gem-rock outputs fetched by tools/fetch_mining_assets.py. Existence-guarded so
# a missing file leaves the row iconless instead of pointing at an absent path
# (which would trip missing_required_asset_paths()).
for _gem_name, _gem_file in {
    "Uncut opal": "opal.png",
    "Uncut jade": "jade.png",
    "Uncut red topaz": "red_topaz.png",
}.items():
    _gem_path = os.path.join(GEMS_FOLDER, _gem_file)
    if os.path.exists(_gem_path):
        GEM_IMAGES[_gem_name] = _gem_path

BAR_IMAGES = {
    "Bronze bar": os.path.join(bars_folder, "bronzebar.png"),
    "Iron bar": os.path.join(bars_folder, "ironbar.png"),
    "Silver bar": os.path.join(bars_folder, "silverbar.png"),
    "Steel bar": os.path.join(bars_folder, "steelbar.png"),
    "Gold bar": os.path.join(bars_folder, "goldbar.png"),
    "Mithril bar": os.path.join(bars_folder, "mithrilbar.png"),
    "Adamant bar": os.path.join(bars_folder, "adamantitebar.png"),
    "Rune bar": os.path.join(bars_folder, "runitebar.png"),
}
_blurite_bar_image = os.path.join(bars_folder, "bluritebar.png")
if os.path.exists(_blurite_bar_image):
    BAR_IMAGES["Blurite bar"] = _blurite_bar_image

# Data dictionaries
ORE_DATA = mining_targets_as_dict()
MINING_PICKAXE_DATA = mining_pickaxes_as_dict()
MINING_BONUS_ITEM_DATA = mining_bonus_items_as_dict()
MINING_EXTRA_ITEM_DATA = mining_extra_items_as_dict()
MINING_OUTPUT_ITEMS = mining_output_items()

TREE_DATA = woodcutting_targets_as_dict()
WOODCUTTING_AXE_DATA = woodcutting_axes_as_dict()
WOODCUTTING_EXTRA_ITEM_DATA = woodcutting_extra_items_as_dict()
BIRD_NEST_DROP_TABLE = tuple({"item": item.item, "weight": item.weight} for item in SOURCE_BIRD_NEST_DROP_TABLE)
INCIDENTAL_GEM_DROP_TABLE = tuple({"item": item.item, "weight": item.weight} for item in SOURCE_INCIDENTAL_GEM_DROP_TABLE)
BIRD_NEST_OPEN_TABLES = {
    input_item: {
        "guaranteed_item": table.guaranteed_item,
        "rolls": tuple({"item": item.item, "weight": item.weight} for item in table.rolls),
        "total_weight": table.total_weight,
        "source": table.source,
    }
    for input_item, table in SOURCE_BIRD_NEST_OPEN_TABLES_BY_INPUT.items()
}
WOODCUTTING_LOG_ITEMS = tuple(
    str(spec["output_item"])
    for spec in TREE_DATA.values()
    if isinstance(spec.get("output_item"), str)
)

GEM_DATA = {
    "Uncut sapphire": {"probability": 1 / 4, "exp": 50},
    "Uncut emerald": {"probability": 1 / 8, "exp": 67.5},
    "Uncut ruby": {"probability": 1 / 16, "exp": 85},
    "Uncut diamond": {"probability": 1 / 64, "exp": 107.5},
}

SMITHING_DATA = smithing_recipes_as_dict()
BAR_DATA = smithing_bars_as_dict()
SMITHING_OUTPUT_ITEMS = smithing_output_items()

FLETCHING_DATA = {
    "arrow_shafts": {
        "display_name": "Arrow shafts (Logs)",
        "level": 1,
        "exp": 5.0,
        "requirements": {"Logs": 1},
        "output_item": "Arrow shafts",
        "output_qty": 15,
    },
    "oak_arrow_shafts": {
        "display_name": "Arrow shafts (Oak logs)",
        "level": 15,
        "exp": 10.0,
        "requirements": {"Oak logs": 1},
        "output_item": "Arrow shafts",
        "output_qty": 30,
    },
    "willow_arrow_shafts": {
        "display_name": "Arrow shafts (Willow logs)",
        "level": 30,
        "exp": 15.0,
        "requirements": {"Willow logs": 1},
        "output_item": "Arrow shafts",
        "output_qty": 45,
    },
    "maple_arrow_shafts": {
        "display_name": "Arrow shafts (Maple logs)",
        "level": 45,
        "exp": 20.0,
        "requirements": {"Maple logs": 1},
        "output_item": "Arrow shafts",
        "output_qty": 60,
    },
    "yew_arrow_shafts": {
        "display_name": "Arrow shafts (Yew logs)",
        "level": 60,
        "exp": 25.0,
        "requirements": {"Yew logs": 1},
        "output_item": "Arrow shafts",
        "output_qty": 75,
    },
    "magic_arrow_shafts": {
        "display_name": "Arrow shafts (Magic logs)",
        "level": 75,
        "exp": 30.0,
        "requirements": {"Magic logs": 1},
        "output_item": "Arrow shafts",
        "output_qty": 90,
    },
    "headless_arrows": {
        "display_name": "Headless arrows",
        "level": 1,
        "exp": 15.0,
        "requirements": {"Arrow shafts": 15, "Feather": 15},
        "output_item": "Headless arrows",
        "output_qty": 15,
    },
    "bronze_arrows": {
        "display_name": "Bronze arrows",
        "level": 1,
        "exp": 19.5,
        "requirements": {"Headless arrows": 15, "Bronze arrowtips": 15},
        "output_item": "Bronze arrows",
        "output_qty": 15,
    },
    "iron_arrows": {
        "display_name": "Iron arrows",
        "level": 15,
        "exp": 37.5,
        "requirements": {"Headless arrows": 15, "Iron arrowtips": 15},
        "output_item": "Iron arrows",
        "output_qty": 15,
    },
    "steel_arrows": {
        "display_name": "Steel arrows",
        "level": 30,
        "exp": 75.0,
        "requirements": {"Headless arrows": 15, "Steel arrowtips": 15},
        "output_item": "Steel arrows",
        "output_qty": 15,
    },
    "mithril_arrows": {
        "display_name": "Mithril arrows",
        "level": 45,
        "exp": 112.5,
        "requirements": {"Headless arrows": 15, "Mithril arrowtips": 15},
        "output_item": "Mithril arrows",
        "output_qty": 15,
    },
    "adamant_arrows": {
        "display_name": "Adamant arrows",
        "level": 60,
        "exp": 150.0,
        "requirements": {"Headless arrows": 15, "Adamant arrowtips": 15},
        "output_item": "Adamant arrows",
        "output_qty": 15,
    },
    "rune_arrows": {
        "display_name": "Rune arrows",
        "level": 75,
        "exp": 187.5,
        "requirements": {"Headless arrows": 15, "Rune arrowtips": 15},
        "output_item": "Rune arrows",
        "output_qty": 15,
    },
    "shortbow_u": {"display_name": "Shortbow (u)", "level": 5, "exp": 5.0, "requirements": {"Logs": 1}, "output_item": "Shortbow (u)", "output_qty": 1},
    "oak_shortbow_u": {"display_name": "Oak shortbow (u)", "level": 20, "exp": 16.5, "requirements": {"Oak logs": 1}, "output_item": "Oak shortbow (u)", "output_qty": 1},
    "willow_shortbow_u": {"display_name": "Willow shortbow (u)", "level": 35, "exp": 33.3, "requirements": {"Willow logs": 1}, "output_item": "Willow shortbow (u)", "output_qty": 1},
    "maple_shortbow_u": {"display_name": "Maple shortbow (u)", "level": 50, "exp": 50.0, "requirements": {"Maple logs": 1}, "output_item": "Maple shortbow (u)", "output_qty": 1},
    "yew_shortbow_u": {"display_name": "Yew shortbow (u)", "level": 65, "exp": 67.5, "requirements": {"Yew logs": 1}, "output_item": "Yew shortbow (u)", "output_qty": 1},
    "magic_shortbow_u": {"display_name": "Magic shortbow (u)", "level": 80, "exp": 83.3, "requirements": {"Magic logs": 1}, "output_item": "Magic shortbow (u)", "output_qty": 1},
}


def _asset_slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


_FLETCHING_ITEM_NAMES = {
    str(spec["output_item"])
    for spec in FLETCHING_DATA.values()
    if isinstance(spec.get("output_item"), str)
}
for _spec in FLETCHING_DATA.values():
    _FLETCHING_ITEM_NAMES.update(str(requirement) for requirement in _spec.get("requirements", {}))
_FLETCHING_ITEM_NAMES.difference_update(TREE_DATA)

FLETCHED_ITEM_IMAGES = {
    item_name: os.path.join(FLETCHED_ITEMS_FOLDER, f"{_asset_slug(item_name)}.png")
    for item_name in _FLETCHING_ITEM_NAMES
}

# Logs are item drops, but their art already ships in trees/ (the row sprite IS
# the log icon). Re-key those files by log item name so the Bank/Stats item
# registry can give logs an asset_path without a second fetch. Existence-guarded
# so missing files never trip missing_required_asset_paths().
LOG_IMAGES = {}
for _spec in TREE_DATA.values():
    _output = _spec.get("output_item")
    _display = _spec.get("display_name")
    if isinstance(_output, str) and isinstance(_display, str):
        _path = TREE_IMAGES.get(_display)
        if _path and os.path.exists(_path):
            LOG_IMAGES[_output] = _path

# Hatchets + bird nests + seed contents fetched into woodcuttingitems/ by
# tools/fetch_woodcutting_assets.py. Slug matches _asset_slug so the keys line
# up; only files that actually exist are wired (rare egg nests/eggs stay
# iconless rather than pointing at absent files).
WOODCUTTING_EXTRA_ITEM_IMAGES = {}
for _item_name in WOODCUTTING_EXTRA_ITEM_DATA:
    _path = os.path.join(WOODCUTTING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        WOODCUTTING_EXTRA_ITEM_IMAGES[_item_name] = _path

MINING_EXTRA_ITEM_IMAGES = {}
for _item_name in MINING_EXTRA_ITEM_DATA:
    # Ores/gems reuse the ORE_IMAGES/GEM_IMAGES maps; pickaxes (and other tools)
    # come from miningitems/ keyed by _asset_slug. Existence-guarded throughout so
    # an unfetched icon leaves the row iconless instead of pointing at a dead path.
    _path = (
        ORE_IMAGES.get(_item_name)
        or GEM_IMAGES.get(_item_name)
        or os.path.join(MINING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    )
    if _path and os.path.exists(_path):
        MINING_EXTRA_ITEM_IMAGES[_item_name] = _path

SMITHING_EXTRA_ITEM_DATA = smithing_extra_items_as_dict()
# Forged outputs (anvil) keyed by item name. Bars (furnace) are not here — they
# come from BAR_IMAGES. Icons are looked up in smithingitems/ by _asset_slug and
# existence-guarded, so the ~150-row forge table renders fine with only a handful
# of high-value icons present and the rest degrading to text-only rows.
SMITHING_EXTRA_ITEM_IMAGES = {}
for _item_name in SMITHING_EXTRA_ITEM_DATA:
    _path = os.path.join(SMITHING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        SMITHING_EXTRA_ITEM_IMAGES[_item_name] = _path
EXTRA_ITEM_DATA = {**WOODCUTTING_EXTRA_ITEM_DATA, **MINING_EXTRA_ITEM_DATA, **SMITHING_EXTRA_ITEM_DATA}
EXTRA_ITEM_IMAGES = {**WOODCUTTING_EXTRA_ITEM_IMAGES, **MINING_EXTRA_ITEM_IMAGES, **SMITHING_EXTRA_ITEM_IMAGES}

ITEM_DEFINITIONS = build_item_definitions(
    ORE_DATA,
    # Weighted gem-rock outputs (Uncut opal/jade/red topaz) are Mining "ore_data"
    # outputs but their art lives in gems/. Merge GEM_IMAGES in so those rows get
    # an asset_path here; the earlier dedup would otherwise pin them iconless.
    {**ORE_IMAGES, **GEM_IMAGES},
    TREE_DATA,
    {**TREE_IMAGES, **LOG_IMAGES},
    GEM_DATA,
    GEM_IMAGES,
    BAR_DATA,
    BAR_IMAGES,
    CRAFTING_DATA,
    CRAFTED_ITEM_IMAGES,
    FLETCHING_DATA,
    FLETCHED_ITEM_IMAGES,
    UTILITY_ACTIVITY_DATA,
    UTILITY_ITEM_IMAGES,
    EXTRA_ITEM_DATA,
    EXTRA_ITEM_IMAGES,
)

# Experience table
EXP_TABLE = [
    0, 83, 174, 276, 388, 512, 650, 801, 969, 1154, 1358, 1584, 1833, 2107, 2411, 2746, 3115, 3523, 3973, 4470,
    5018, 5624, 6291, 7028, 7842, 8740, 9730, 10824, 12031, 13363, 14833, 16456, 18247, 20224, 22406, 24815,
    27473, 30408, 33648, 37224, 41171, 45529, 50339, 55649, 61512, 67983, 75127, 83014, 91721, 101333, 111945,
    123660, 136594, 150872, 166636, 184040, 203254, 224466, 247886, 273742, 302288, 333804, 368599, 407015,
    449428, 496254, 547953, 605032, 668051, 737627, 814445, 899257, 992895, 1096278, 1210421, 1336443, 1475581,
    1629200, 1798808, 1986068, 2192818, 2421087, 2673114, 2951373, 3258594, 3597792, 3972294, 4385776, 4842295,
    5346332, 5902831, 6517253, 7195629, 7944614, 8771558, 9684577, 10692629, 11805606, 13034431
]

# Achievements dictionary
ACHIEVEMENTS = {
    # Easy Achievements
    "First Steps": {"description": "Mine your first ore", "difficulty": "Easy",
                    "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in MINING_OUTPUT_ITEMS) > 0},
    "Novice Miner": {"description": "Reach Mining level 10", "difficulty": "Easy",
                     "condition": lambda player: player["mining_level"] >= 10},
    "Ore Collector": {"description": "Collect 100 total ores", "difficulty": "Easy",
                      "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in MINING_OUTPUT_ITEMS) >= 100},
    "Jack of All Ores": {"description": "Mine at least one of each ore type", "difficulty": "Easy",
                         "condition": lambda player: all(player["inventory"].get(ore, 0) > 0 for ore in MINING_OUTPUT_ITEMS)},
    "Rune Essence Enthusiast": {"description": "Mine 500 Rune Essence", "difficulty": "Easy",
                                "condition": lambda player: player["inventory"]["Rune essence"] >= 500},
    "Clay Modeler": {"description": "Mine 500 Clay", "difficulty": "Easy",
                     "condition": lambda player: player["inventory"]["Clay"] >= 500},
    "Copper Collector": {"description": "Mine 250 Copper ore", "difficulty": "Easy",
                         "condition": lambda player: player["inventory"]["Copper ore"] >= 250},
    "Tin Trader": {"description": "Mine 250 Tin ore", "difficulty": "Easy",
                   "condition": lambda player: player["inventory"]["Tin ore"] >= 250},
    "Iron Initiate": {"description": "Mine 100 Iron ore", "difficulty": "Easy",
                      "condition": lambda player: player["inventory"]["Iron ore"] >= 100},
    "Silver Seeker": {"description": "Mine 50 Silver ore", "difficulty": "Easy",
                      "condition": lambda player: player["inventory"]["Silver ore"] >= 50},

    # Moderate Achievements
    "Intermediate Miner": {"description": "Reach Mining level 30", "difficulty": "Moderate",
                           "condition": lambda player: player["mining_level"] >= 30},
    "Ore Hoarder": {"description": "Collect 1,000 total ores", "difficulty": "Moderate",
                    "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in MINING_OUTPUT_ITEMS) >= 1000},
    "Coal Connoisseur": {"description": "Mine 500 Coal", "difficulty": "Moderate",
                         "condition": lambda player: player["inventory"]["Coal"] >= 500},
    "Golden Touch": {"description": "Mine 100 Gold ore", "difficulty": "Moderate",
                     "condition": lambda player: player["inventory"]["Gold ore"] >= 100},
    "Mithril Mastery": {"description": "Mine 250 Mithril ore", "difficulty": "Moderate",
                        "condition": lambda player: player["inventory"]["Mithril ore"] >= 250},
    "Adamantite Adept": {"description": "Mine 100 Adamantite ore", "difficulty": "Moderate",
                         "condition": lambda player: player["inventory"]["Adamantite ore"] >= 100},
    "Runite Rookie": {"description": "Mine 50 Runite ore", "difficulty": "Moderate",
                      "condition": lambda player: player["inventory"]["Runite ore"] >= 50},
    "Diverse Miner": {"description": "Mine 100 of each ore type", "difficulty": "Moderate",
                      "condition": lambda player: all(player["inventory"].get(ore, 0) >= 100 for ore in MINING_OUTPUT_ITEMS)},
    "XP Chaser": {"description": "Gain 100,000 total Mining experience", "difficulty": "Moderate",
                  "condition": lambda player: player["mining_exp"] >= 100000},

    # Difficult Achievements
    "Expert Miner": {"description": "Reach Mining level 60", "difficulty": "Difficult",
                     "condition": lambda player: player["mining_level"] >= 60},
    "Ore Magnate": {"description": "Collect 10,000 total ores", "difficulty": "Difficult",
                    "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in MINING_OUTPUT_ITEMS) >= 10000},
    "Rune Essence Baron": {"description": "Mine 10,000 Rune Essence", "difficulty": "Difficult",
                           "condition": lambda player: player["inventory"]["Rune essence"] >= 10000},
    "Clay Empire": {"description": "Mine 10,000 Clay", "difficulty": "Difficult",
                    "condition": lambda player: player["inventory"]["Clay"] >= 10000},
    "Copper King": {"description": "Mine 5,000 Copper ore", "difficulty": "Difficult",
                    "condition": lambda player: player["inventory"]["Copper ore"] >= 5000},
    "Tin Tycoon": {"description": "Mine 5,000 Tin ore", "difficulty": "Difficult",
                   "condition": lambda player: player["inventory"]["Tin ore"] >= 5000},
    "Iron Imperator": {"description": "Mine 2,500 Iron ore", "difficulty": "Difficult",
                       "condition": lambda player: player["inventory"]["Iron ore"] >= 2500},
    "Silver Sovereign": {"description": "Mine 1,000 Silver ore", "difficulty": "Difficult",
                         "condition": lambda player: player["inventory"]["Silver ore"] >= 1000},
    "Coal Commander": {"description": "Mine 5,000 Coal", "difficulty": "Difficult",
                       "condition": lambda player: player["inventory"]["Coal"] >= 5000},
    "Golden Empire": {"description": "Mine 1,000 Gold ore", "difficulty": "Difficult",
                      "condition": lambda player: player["inventory"]["Gold ore"] >= 1000},

    # Very Challenging Achievements
    "Master Miner": {"description": "Reach Mining level 99", "difficulty": "Very Challenging",
                     "condition": lambda player: player["mining_level"] >= 99},
    "Ore Tycoon": {"description": "Collect 100,000 total ores", "difficulty": "Very Challenging",
                   "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in MINING_OUTPUT_ITEMS) >= 100000},
    "Mithril Monarch": {"description": "Mine 10,000 Mithril ore", "difficulty": "Very Challenging",
                        "condition": lambda player: player["inventory"]["Mithril ore"] >= 10000},
    "Adamantite Overlord": {"description": "Mine 5,000 Adamantite ore", "difficulty": "Very Challenging",
                            "condition": lambda player: player["inventory"]["Adamantite ore"] >= 5000},
    "Runite Ruler": {"description": "Mine 2,500 Runite ore", "difficulty": "Very Challenging",
                     "condition": lambda player: player["inventory"]["Runite ore"] >= 2500},
    "Ore Completionist": {"description": "Mine 10,000 of each ore type", "difficulty": "Very Challenging",
                          "condition": lambda player: all(
                              player["inventory"].get(ore, 0) >= 10000 for ore in MINING_OUTPUT_ITEMS)},
    "XP Master": {"description": "Gain 1,000,000 total Mining experience", "difficulty": "Very Challenging",
                  "condition": lambda player: player["mining_exp"] >= 1000000},

    # New Woodcutting Achievements
    "First Chop": {"description": "Cut your first log", "difficulty": "Easy",
                   "condition": lambda player: any(player["inventory"].get(item, 0) > 0 for item in WOODCUTTING_LOG_ITEMS)},
    "Novice Woodcutter": {"description": "Reach Woodcutting level 10", "difficulty": "Easy",
                          "condition": lambda player: player["woodcutting_level"] >= 10},
    "Log Collector": {"description": "Collect 100 total logs", "difficulty": "Easy",
                      "condition": lambda player: sum(player["inventory"].get(item, 0) for item in WOODCUTTING_LOG_ITEMS) >= 100},
    "Jack of All Trees": {"description": "Cut at least one log from each tree type", "difficulty": "Easy",
                          "condition": lambda player: all(player["inventory"].get(item, 0) > 0 for item in WOODCUTTING_LOG_ITEMS)},
    "Oak Enthusiast": {"description": "Cut 500 Oak logs", "difficulty": "Easy",
                       "condition": lambda player: player["inventory"].get("Oak logs", 0) >= 500},
    "Willow Whisperer": {"description": "Cut 500 Willow logs", "difficulty": "Easy",
                         "condition": lambda player: player["inventory"].get("Willow logs", 0) >= 500},

    "Intermediate Woodcutter": {"description": "Reach Woodcutting level 30", "difficulty": "Moderate",
                                "condition": lambda player: player["woodcutting_level"] >= 30},
    "Log Hoarder": {"description": "Collect 1,000 total logs", "difficulty": "Moderate",
                    "condition": lambda player: sum(player["inventory"].get(item, 0) for item in WOODCUTTING_LOG_ITEMS) >= 1000},
    "Maple Master": {"description": "Cut 500 Maple logs", "difficulty": "Moderate",
                     "condition": lambda player: player["inventory"].get("Maple logs", 0) >= 500},
    "Yew Yeoman": {"description": "Cut 250 Yew logs", "difficulty": "Moderate",
                   "condition": lambda player: player["inventory"].get("Yew logs", 0) >= 250},

    "Expert Woodcutter": {"description": "Reach Woodcutting level 60", "difficulty": "Difficult",
                          "condition": lambda player: player["woodcutting_level"] >= 60},
    "Log Magnate": {"description": "Collect 10,000 total logs", "difficulty": "Difficult",
                    "condition": lambda player: sum(player["inventory"].get(item, 0) for item in WOODCUTTING_LOG_ITEMS) >= 10000},
    "Magic Logger": {"description": "Cut 1,000 Magic logs", "difficulty": "Difficult",
                     "condition": lambda player: player["inventory"].get("Magic logs", 0) >= 1000},

    "Master Woodcutter": {"description": "Reach Woodcutting level 99", "difficulty": "Very Challenging",
                          "condition": lambda player: player["woodcutting_level"] >= 99},

    # Combined Achievements
    "Jack of Two Trades": {"description": "Reach level 50 in both Mining and Woodcutting", "difficulty": "Moderate",
                           "condition": lambda player: player["mining_level"] >= 50 and player[
                               "woodcutting_level"] >= 50},
    "Resource Baron": {"description": "Collect 10,000 total ores and 10,000 total logs", "difficulty": "Difficult",
                       "condition": lambda player: sum(
                           player["inventory"].get(ore, 0) for ore in MINING_OUTPUT_ITEMS) >= 10000 and sum(
                           player["inventory"].get(item, 0) for item in WOODCUTTING_LOG_ITEMS) >= 10000},
    "Skilling Prodigy": {"description": "Reach level 80 in both Mining and Woodcutting",
                         "difficulty": "Very Challenging",
                         "condition": lambda player: player["mining_level"] >= 80 and player[
                             "woodcutting_level"] >= 80},
    "Master of Resources": {"description": "Reach level 99 in both Mining and Woodcutting",
                            "difficulty": "Very Challenging",
                            "condition": lambda player: player["mining_level"] >= 99 and player[
                                "woodcutting_level"] >= 99},

    # Update the "Living Legend" achievement to include all new achievements
    "Living Legend": {"description": "Complete all other achievements", "difficulty": "Very Challenging",
                      "condition": lambda player: len(player["completed_achievements"]) >= len(ACHIEVEMENTS) - 1}
}

ACHIEVEMENTS.update({
    "Gem Finder": {
        "description": "Mine your first gem",
        "difficulty": "Easy",
        "condition": lambda player: any(player["inventory"].get(gem, 0) > 0 for gem in GEM_DATA)
    },
    "Sapphire Collector": {
        "description": "Mine 10 uncut sapphires",
        "difficulty": "Moderate",
        "condition": lambda player: player["inventory"].get("Uncut sapphire", 0) >= 10
    },
    "Emerald Hunter": {
        "description": "Mine 10 uncut emeralds",
        "difficulty": "Moderate",
        "condition": lambda player: player["inventory"].get("Uncut emerald", 0) >= 10
    },
    "Ruby Seeker": {
        "description": "Mine 10 uncut rubies",
        "difficulty": "Difficult",
        "condition": lambda player: player["inventory"].get("Uncut ruby", 0) >= 10
    },
    "Diamond Prospector": {
        "description": "Mine 10 uncut diamonds",
        "difficulty": "Very Challenging",
        "condition": lambda player: player["inventory"].get("Uncut diamond", 0) >= 10
    },
    "Gem Master": {
        "description": "Mine 100 gems in total",
        "difficulty": "Very Challenging",
        "condition": lambda player: sum(player["inventory"].get(gem, 0) for gem in GEM_DATA) >= 100
    },
})

ACHIEVEMENTS.update({
    "Novice Smith": {"description": "Smelt your first bar", "difficulty": "Easy",
                     "condition": lambda player: any(player["inventory"].get(bar, 0) > 0 for bar in BAR_DATA)},
    "Bronze Master": {"description": "Smelt 100 Bronze bars", "difficulty": "Easy",
                      "condition": lambda player: player["inventory"].get("Bronze bar", 0) >= 100},
    "Iron Forger": {"description": "Smelt 500 Iron bars", "difficulty": "Moderate",
                    "condition": lambda player: player["inventory"].get("Iron bar", 0) >= 500},
    "Steel Specialist": {"description": "Smelt 1000 Steel bars", "difficulty": "Moderate",
                         "condition": lambda player: player["inventory"].get("Steel bar", 0) >= 1000},
    "Mithril Maestro": {"description": "Smelt 500 Mithril bars", "difficulty": "Difficult",
                        "condition": lambda player: player["inventory"].get("Mithril bar", 0) >= 500},
    "Adamantite Artisan": {"description": "Smelt 250 Adamantite bars", "difficulty": "Very Challenging",
                           "condition": lambda player: player["inventory"].get("Adamantite bar", 0) >= 250},
    "Runite Refiner": {"description": "Smelt 100 Runite bars", "difficulty": "Very Challenging",
                       "condition": lambda player: player["inventory"].get("Runite bar", 0) >= 100},
})


# Add new Crafting achievements
ACHIEVEMENTS.update({
    "Novice Crafter": {"description": "Reach level 2 in Crafting", "difficulty": "Easy", "condition": lambda player: player["crafting_level"] > 1},
    "Pottery Apprentice": {"description": "Craft 100 pots", "difficulty": "Easy", "condition": lambda player: player["inventory"].get("Pot", 0) >= 100},
    "Jewelry Novice": {"description": "Craft 50 gold rings", "difficulty": "Moderate", "condition": lambda player: player["inventory"].get("Gold ring", 0) >= 50},
    "Gem Cutter": {"description": "Cut 10 of each gem type", "difficulty": "Difficult", "condition": lambda player: all(player["inventory"].get(gem, 0) >= 10 for gem in ["Sapphire", "Emerald", "Ruby", "Diamond"])},
    "Master Crafter": {"description": "Reach Crafting level 99", "difficulty": "Very Challenging", "condition": lambda player: player["crafting_level"] >= 99},
})
