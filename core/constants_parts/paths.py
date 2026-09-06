import os as _os

# Base probabilities and factors
BASE_WOODCUTTING_PROBABILITY = 0.8
BASE_MINING_PROBABILITY = 0.8
LEVEL_BONUS_FACTOR = 0.02

# File paths
current_dir = _os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
ores_folder = _os.path.join(current_dir, "ores")
trees_folder = _os.path.join(current_dir, "trees")
GEMS_FOLDER = _os.path.join(current_dir, "gems")
bars_folder = _os.path.join(current_dir, "bars")
FLETCHED_ITEMS_FOLDER = _os.path.join(current_dir, "fletcheditems")
# Woodcutting bank items (hatchets, bird nests, seed contents). Logs reuse the
# trees/ sprites — those files are the log item art (see WIKI_TITLE_OVERRIDES in
# tools/fetch_assets.py) — so only non-log Woodcutting items live here.
WOODCUTTING_ITEMS_FOLDER = _os.path.join(current_dir, "woodcuttingitems")
# Mining bank items that aren't ores/gems: pickaxes (and future bonus equipables).
# Fetched into miningitems/ by tools/fetch_mining_assets.py.
MINING_ITEMS_FOLDER = _os.path.join(current_dir, "miningitems")
# Forged Smithing outputs (weapons/armour/tools/ammo). Bars reuse bars_folder via
# BAR_IMAGES; everything anvil-made is fetched here by tools/fetch_smithing_assets.py.
# Optional: any output without a file degrades to an iconless row.
SMITHING_ITEMS_FOLDER = _os.path.join(current_dir, "smithingitems")
UTILITY_ACTIVITY_ICONS_FOLDER = _os.path.join(current_dir, "activityicons")
FIREMAKING_ITEMS_FOLDER = _os.path.join(current_dir, "firemakingitems")
FISHING_ITEMS_FOLDER = _os.path.join(current_dir, "fishingitems")
HUNTER_ITEMS_FOLDER = _os.path.join(current_dir, "hunteritems")
COOKING_ITEMS_FOLDER = _os.path.join(current_dir, "cookingitems")
RUNECRAFTING_ITEMS_FOLDER = _os.path.join(current_dir, "runecraftingitems")
HERBLORE_ITEMS_FOLDER = _os.path.join(current_dir, "herbloreitems")
QUEST_ITEMS_FOLDER = _os.path.join(current_dir, "questitems")
COMBAT_ITEMS_FOLDER = _os.path.join(current_dir, "combatitems")
COMBAT_ENEMIES_FOLDER = _os.path.join(current_dir, "combatenemies")
BRAWLING_ITEMS_FOLDER = _os.path.join(current_dir, "brawlingitems")
SHOP_ITEMS_FOLDER = _os.path.join(current_dir, "shopitems")
PRAYER_ITEMS_FOLDER = _os.path.join(current_dir, "prayeritems")
MAGIC_ITEMS_FOLDER = _os.path.join(current_dir, "magicitems")
MAGIC_SPELLS_FOLDER = _os.path.join(current_dir, "magicspells")
CONSTRUCTION_ITEMS_FOLDER = _os.path.join(current_dir, "constructionitems")
SUMMONING_ITEMS_FOLDER = _os.path.join(current_dir, "summoningitems")
FARMING_ITEMS_FOLDER = _os.path.join(current_dir, "farmingitems")
FARMING_HUD_SPROUT_ICON = _os.path.join(current_dir, "icon", "farming_icon.png")

# Image dictionaries
# New constants for Crafting
CRAFTED_ITEMS_FOLDER = _os.path.join(current_dir, "crafteditems")


__all__ = [
    "BASE_WOODCUTTING_PROBABILITY",
    "BASE_MINING_PROBABILITY",
    "LEVEL_BONUS_FACTOR",
    "current_dir",
    "ores_folder",
    "trees_folder",
    "GEMS_FOLDER",
    "bars_folder",
    "FLETCHED_ITEMS_FOLDER",
    "WOODCUTTING_ITEMS_FOLDER",
    "MINING_ITEMS_FOLDER",
    "SMITHING_ITEMS_FOLDER",
    "UTILITY_ACTIVITY_ICONS_FOLDER",
    "FIREMAKING_ITEMS_FOLDER",
    "FISHING_ITEMS_FOLDER",
    "HUNTER_ITEMS_FOLDER",
    "COOKING_ITEMS_FOLDER",
    "RUNECRAFTING_ITEMS_FOLDER",
    "HERBLORE_ITEMS_FOLDER",
    "QUEST_ITEMS_FOLDER",
    "COMBAT_ITEMS_FOLDER",
    "COMBAT_ENEMIES_FOLDER",
    "BRAWLING_ITEMS_FOLDER",
    "SHOP_ITEMS_FOLDER",
    "PRAYER_ITEMS_FOLDER",
    "MAGIC_ITEMS_FOLDER",
    "MAGIC_SPELLS_FOLDER",
    "CONSTRUCTION_ITEMS_FOLDER",
    "SUMMONING_ITEMS_FOLDER",
    "FARMING_ITEMS_FOLDER",
    "FARMING_HUD_SPROUT_ICON",
    "CRAFTED_ITEMS_FOLDER",
]
