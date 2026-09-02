import os

from .skill_foundations import *
from .competitive_activities import *
from .world_activities import *
from .catalog_sources import *
from .gathering_sources import *
from .production_sources import *
from .paths import *

CRAFTING_DATA = crafting_recipes_as_dict()
CRAFTING_REQUIRED_ITEM_DATA = crafting_required_items_as_dict()
CRAFTING_SPECIAL_ITEM_DATA = crafting_special_items_as_dict()

CRAFTED_ITEM_IMAGES = {}
UTILITY_ITEM_IMAGES = {
    "Soft clay": os.path.join(CRAFTED_ITEMS_FOLDER, "soft_clay.png"),
    "Robust glass": os.path.join(CRAFTED_ITEMS_FOLDER, "robust_glass.png"),
    "Wool": os.path.join(CRAFTED_ITEMS_FOLDER, "wool.png"),
    "Flax": os.path.join(CRAFTED_ITEMS_FOLDER, "flax.png"),
    "Swamp toad": os.path.join(SUMMONING_ITEMS_FOLDER, "swamp_toad.png"),
    "Toad's legs": os.path.join(HERBLORE_ITEMS_FOLDER, "toad_s_legs.png"),
    "Blue dragon scale": os.path.join(HERBLORE_ITEMS_FOLDER, "blue_dragon_scale.png"),
    "Dragon scale dust": os.path.join(HERBLORE_ITEMS_FOLDER, "dragon_scale_dust.png"),
    "Potato cactus": os.path.join(SUMMONING_ITEMS_FOLDER, "potato_cactus.png"),
    "Black mushroom": os.path.join(HERBLORE_ITEMS_FOLDER, "black_mushroom.png"),
    "Black mushroom ink": os.path.join(HERBLORE_ITEMS_FOLDER, "black_mushroom_ink.png"),
    "Goblin mail": os.path.join(QUEST_ITEMS_FOLDER, "goblin_mail.png"),
    "Red dye": os.path.join(CONSTRUCTION_ITEMS_FOLDER, "red_dye.png"),
    "Yellow dye": os.path.join(SHOP_ITEMS_FOLDER, "yellow_dye.png"),
    "Orange dye": os.path.join(SHOP_ITEMS_FOLDER, "orange_dye.png"),
    "Blue dye": os.path.join(SHOP_ITEMS_FOLDER, "blue_dye.png"),
    "Orange goblin mail": os.path.join(QUEST_ITEMS_FOLDER, "orange_goblin_mail.png"),
    "Blue goblin mail": os.path.join(QUEST_ITEMS_FOLDER, "blue_goblin_mail.png"),
    "Phoenix feather": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "desert_phoenix.png"),
    "Feather": os.path.join(FLETCHED_ITEMS_FOLDER, "feather.png"),
    "Fishing bait": os.path.join(FISHING_ITEMS_FOLDER, "fishing_bait.png"),
    # Coin-paid conversion outputs (art shared with the folders that first
    # fetched it; keeps these registered even if no shop stocks them).
    "Leather": os.path.join(CRAFTED_ITEMS_FOLDER, "leather.png"),
    "Hard leather": os.path.join(CRAFTED_ITEMS_FOLDER, "hard_leather.png"),
    "Snakeskin": os.path.join(CRAFTED_ITEMS_FOLDER, "snakeskin.png"),
    "Green dragon leather": os.path.join(CRAFTED_ITEMS_FOLDER, "green_dragon_leather.png"),
    "Blue dragon leather": os.path.join(CRAFTED_ITEMS_FOLDER, "blue_dragon_leather.png"),
    "Red dragon leather": os.path.join(CRAFTED_ITEMS_FOLDER, "red_dragon_leather.png"),
    "Black dragon leather": os.path.join(CRAFTED_ITEMS_FOLDER, "black_dragon_leather.png"),
    "Plank": os.path.join(QUEST_ITEMS_FOLDER, "plank.png"),
    "Oak plank": os.path.join(SHOP_ITEMS_FOLDER, "oak_plank.png"),
}

TREE_IMAGES = {tree.split('.')[0]: os.path.join(trees_folder, tree) for tree in os.listdir(trees_folder) if tree.endswith('.png')}
TREE_IMAGES.update(
    {
        "Arctic pine": os.path.join(FIREMAKING_ITEMS_FOLDER, "arctic_pine_logs.png"),
        "Eucalyptus": os.path.join(FIREMAKING_ITEMS_FOLDER, "eucalyptus_logs.png"),
        "Curly jade root": os.path.join(FIREMAKING_ITEMS_FOLDER, "curly_root.png"),
    }
)

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
    "Runite ore": os.path.join(ores_folder, "Runite.png"),
    "Living minerals": os.path.join(FISHING_ITEMS_FOLDER, "living_minerals.png"),
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
    "Red sandstone": "red_sandstone.png",
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
MINING_EXTRA_ITEM_DATA.update(shooting_star_extra_items_as_dict())
MINING_OUTPUT_ITEMS = mining_output_items()

TREE_DATA = woodcutting_targets_as_dict()
WOODCUTTING_AXE_DATA = woodcutting_axes_as_dict()
WOODCUTTING_EXTRA_ITEM_DATA = woodcutting_extra_items_as_dict()
WOODCUTTING_EXTRA_ITEM_DATA.update(evil_tree_extra_items_as_dict())
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

FLETCHING_DATA = fletching_targets_as_dict()
FLETCHING_OUTPUT_ITEMS = fletching_output_items()

HUNTER_DATA = hunter_targets_as_dict()
HUNTER_OUTPUT_ITEMS = hunter_output_items()

FIREMAKING_DATA = firemaking_targets_as_dict()
FIREMAKING_LOG_ITEMS = firemaking_input_items()
FIREMAKING_OUTPUT_ITEMS = firemaking_output_items()

FISHING_DATA = fishing_methods_as_dict()
FISHING_OUTPUT_ITEMS = fishing_output_items()

COOKING_DATA = cooking_targets_as_dict()
COOKING_OUTPUT_ITEMS = cooking_output_items()
COOKING_BURNT_ITEMS = cooking_burnt_items()
COOKING_RAW_ITEMS = cooking_raw_items()

RUNECRAFTING_DATA = runecrafting_targets_as_dict()
RUNECRAFTING_POUCH_DATA = runecrafting_pouches_as_dict()
RUNECRAFTING_OUTPUT_ITEMS = runecrafting_output_items()
RUNECRAFTING_RUNE_OUTPUT_ITEMS = runecrafting_rune_output_items()
RUNECRAFTING_ACCESS_ITEMS = runecrafting_access_items()
HERBLORE_DATA = herblore_targets_as_dict()
HERBLORE_OUTPUT_ITEMS = herblore_output_items()
HERBLORE_FINISHED_OUTPUT_ITEMS = herblore_finished_output_items()
PRAYER_DATA = prayer_targets_as_dict()
MAGIC_DATA = magic_targets_as_dict()

__all__ = [
    "CRAFTING_DATA",
    "CRAFTING_REQUIRED_ITEM_DATA",
    "CRAFTING_SPECIAL_ITEM_DATA",
    "CRAFTED_ITEM_IMAGES",
    "UTILITY_ITEM_IMAGES",
    "TREE_IMAGES",
    "ORE_IMAGES",
    "GEM_IMAGES",
    "BAR_IMAGES",
    "ORE_DATA",
    "MINING_PICKAXE_DATA",
    "MINING_BONUS_ITEM_DATA",
    "MINING_EXTRA_ITEM_DATA",
    "MINING_OUTPUT_ITEMS",
    "TREE_DATA",
    "WOODCUTTING_AXE_DATA",
    "WOODCUTTING_EXTRA_ITEM_DATA",
    "BIRD_NEST_DROP_TABLE",
    "INCIDENTAL_GEM_DROP_TABLE",
    "BIRD_NEST_OPEN_TABLES",
    "WOODCUTTING_LOG_ITEMS",
    "GEM_DATA",
    "SMITHING_DATA",
    "BAR_DATA",
    "SMITHING_OUTPUT_ITEMS",
    "FLETCHING_DATA",
    "FLETCHING_OUTPUT_ITEMS",
    "HUNTER_DATA",
    "HUNTER_OUTPUT_ITEMS",
    "FIREMAKING_DATA",
    "FIREMAKING_LOG_ITEMS",
    "FIREMAKING_OUTPUT_ITEMS",
    "FISHING_DATA",
    "FISHING_OUTPUT_ITEMS",
    "COOKING_DATA",
    "COOKING_OUTPUT_ITEMS",
    "COOKING_BURNT_ITEMS",
    "COOKING_RAW_ITEMS",
    "RUNECRAFTING_DATA",
    "RUNECRAFTING_POUCH_DATA",
    "RUNECRAFTING_OUTPUT_ITEMS",
    "RUNECRAFTING_RUNE_OUTPUT_ITEMS",
    "RUNECRAFTING_ACCESS_ITEMS",
    "HERBLORE_DATA",
    "HERBLORE_OUTPUT_ITEMS",
    "HERBLORE_FINISHED_OUTPUT_ITEMS",
    "PRAYER_DATA",
    "MAGIC_DATA",
]
