# constants.py

import os

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

# Image dictionaries
# New constants for Crafting
CRAFTED_ITEMS_FOLDER = os.path.join(current_dir, "crafteditems")

CRAFTING_DATA = {
    "None": {"level": 1, "exp": 0, "requirements": {}},
    "Soft clay": {"level": 1, "exp": 0, "requirements": {"Clay": 1}},
    "Unfired pot": {"level": 1, "exp": 6.3, "requirements": {"Soft clay": 1}},
    "Pot": {"level": 1, "exp": 6.3, "requirements": {"Unfired pot": 1}},
    "Pie dish": {"level": 1, "exp": 10, "requirements": {"Unfired pie dish": 1}},
    "Bowl": {"level": 1, "exp": 15, "requirements": {"Unfired bowl": 1}},
    "Gold ring": {"level": 5, "exp": 15, "requirements": {"Gold bar": 1}},
    "Gold necklace": {"level": 6, "exp": 20, "requirements": {"Gold bar": 1}},
    "Unfired pie dish": {"level": 7, "exp": 15, "requirements": {"Soft clay": 1}},
    "Unfired bowl": {"level": 8, "exp": 18, "requirements": {"Soft clay": 1}},
    "Unstrung symbol": {"level": 16, "exp": 50, "requirements": {"Silver bar": 1}},
    "Sapphire ring": {"level": 20, "exp": 40, "requirements": {"Gold bar": 1, "Sapphire": 1}},
    "Sapphire": {"level": 20, "exp": 50, "requirements": {"Uncut sapphire": 1}},
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

GEM_IMAGES = {
    "Uncut sapphire": os.path.join(GEMS_FOLDER, "sapphire.png"),
    "Uncut emerald": os.path.join(GEMS_FOLDER, "emerald.png"),
    "Uncut ruby": os.path.join(GEMS_FOLDER, "ruby.png"),
    "Uncut diamond": os.path.join(GEMS_FOLDER, "diamond.png"),
}

BAR_IMAGES = {
    "Bronze bar": os.path.join(bars_folder, "bronzebar.png"),
    "Iron bar": os.path.join(bars_folder, "ironbar.png"),
    "Silver bar": os.path.join(bars_folder, "silverbar.png"),
    "Steel bar": os.path.join(bars_folder, "steelbar.png"),
    "Gold bar": os.path.join(bars_folder, "goldbar.png"),
    "Mithril bar": os.path.join(bars_folder, "mithrilbar.png"),
    "Adamantite bar": os.path.join(bars_folder, "adamantitebar.png"),
    "Runite bar": os.path.join(bars_folder, "runitebar.png"),
}

# Data dictionaries
ORE_DATA = {
    "Rune essence": {"level": 1, "exp": 5.0, "probability": 0.95},
    "Clay": {"level": 1, "exp": 5.0, "probability": 0.90},
    "Copper ore": {"level": 1, "exp": 17.5, "probability": 0.85},
    "Tin ore": {"level": 1, "exp": 17.5, "probability": 0.85},
    "Iron ore": {"level": 15, "exp": 35, "probability": 0.80},
    "Silver ore": {"level": 20, "exp": 40, "probability": 0.75},
    "Coal": {"level": 30, "exp": 50, "probability": 0.70},
    "Gold ore": {"level": 40, "exp": 65.0, "probability": 0.65},
    "Mithril ore": {"level": 55, "exp": 80, "probability": 0.60},
    "Adamantite ore": {"level": 70, "exp": 95.0, "probability": 0.55},
    "Runite ore": {"level": 85, "exp": 125, "probability": 0.50}
}

TREE_DATA = {
    "Tree": {"level": 1, "exp": 25, "probability": 0.90},
    "Oak": {"level": 15, "exp": 37.5, "probability": 0.85},
    "Willow": {"level": 30, "exp": 67.5, "probability": 0.80},
    "Teak": {"level": 35, "exp": 85, "probability": 0.75},
    "Maple": {"level": 45, "exp": 100, "probability": 0.70},
    "Mahogany": {"level": 50, "exp": 125, "probability": 0.65},
    "Yew": {"level": 60, "exp": 175, "probability": 0.60},
    "Magic": {"level": 75, "exp": 250, "probability": 0.55},
    "Redwood": {"level": 90, "exp": 380, "probability": 0.50},
}

GEM_DATA = {
    "Uncut sapphire": {"probability": 1 / 4, "exp": 50},
    "Uncut emerald": {"probability": 1 / 8, "exp": 67.5},
    "Uncut ruby": {"probability": 1 / 16, "exp": 85},
    "Uncut diamond": {"probability": 1 / 64, "exp": 107.5},
}

BAR_DATA = {
    "Bronze bar": {"level": 1, "exp": 6.2, "ore_required": {"Copper ore": 1, "Tin ore": 1}},
    "Iron bar": {"level": 15, "exp": 12.5, "ore_required": {"Iron ore": 1}},
    "Silver bar": {"level": 20, "exp": 13.67, "ore_required": {"Silver ore": 1}},
    "Steel bar": {"level": 30, "exp": 17.5, "ore_required": {"Iron ore": 1, "Coal": 2}},
    "Gold bar": {"level": 40, "exp": 22.5, "ore_required": {"Gold ore": 1}},
    "Mithril bar": {"level": 50, "exp": 30.0, "ore_required": {"Mithril ore": 1, "Coal": 4}},
    "Adamantite bar": {"level": 70, "exp": 37.5, "ore_required": {"Adamantite ore": 1, "Coal": 6}},
    "Runite bar": {"level": 85, "exp": 50.0, "ore_required": {"Runite ore": 1, "Coal": 8}},
}

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
                    "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in ORE_DATA) > 0},
    "Novice Miner": {"description": "Reach Mining level 10", "difficulty": "Easy",
                     "condition": lambda player: player["mining_level"] >= 10},
    "Ore Collector": {"description": "Collect 100 total ores", "difficulty": "Easy",
                      "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in ORE_DATA) >= 100},
    "Jack of All Ores": {"description": "Mine at least one of each ore type", "difficulty": "Easy",
                         "condition": lambda player: all(player["inventory"].get(ore, 0) > 0 for ore in ORE_DATA)},
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
                    "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in ORE_DATA) >= 1000},
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
                      "condition": lambda player: all(player["inventory"].get(ore, 0) >= 100 for ore in ORE_DATA)},
    "XP Chaser": {"description": "Gain 100,000 total Mining experience", "difficulty": "Moderate",
                  "condition": lambda player: player["mining_exp"] >= 100000},

    # Difficult Achievements
    "Expert Miner": {"description": "Reach Mining level 60", "difficulty": "Difficult",
                     "condition": lambda player: player["mining_level"] >= 60},
    "Ore Magnate": {"description": "Collect 10,000 total ores", "difficulty": "Difficult",
                    "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in ORE_DATA) >= 10000},
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
                   "condition": lambda player: sum(player["inventory"].get(ore, 0) for ore in ORE_DATA) >= 100000},
    "Mithril Monarch": {"description": "Mine 10,000 Mithril ore", "difficulty": "Very Challenging",
                        "condition": lambda player: player["inventory"]["Mithril ore"] >= 10000},
    "Adamantite Overlord": {"description": "Mine 5,000 Adamantite ore", "difficulty": "Very Challenging",
                            "condition": lambda player: player["inventory"]["Adamantite ore"] >= 5000},
    "Runite Ruler": {"description": "Mine 2,500 Runite ore", "difficulty": "Very Challenging",
                     "condition": lambda player: player["inventory"]["Runite ore"] >= 2500},
    "Ore Completionist": {"description": "Mine 10,000 of each ore type", "difficulty": "Very Challenging",
                          "condition": lambda player: all(
                              player["inventory"].get(ore, 0) >= 10000 for ore in ORE_DATA)},
    "XP Master": {"description": "Gain 1,000,000 total Mining experience", "difficulty": "Very Challenging",
                  "condition": lambda player: player["mining_exp"] >= 1000000},

    # New Woodcutting Achievements
    "First Chop": {"description": "Cut your first log", "difficulty": "Easy",
                   "condition": lambda player: any(player["inventory"].get(tree, 0) > 0 for tree in TREE_DATA)},
    "Novice Woodcutter": {"description": "Reach Woodcutting level 10", "difficulty": "Easy",
                          "condition": lambda player: player["woodcutting_level"] >= 10},
    "Log Collector": {"description": "Collect 100 total logs", "difficulty": "Easy",
                      "condition": lambda player: sum(player["inventory"].get(tree, 0) for tree in TREE_DATA) >= 100},
    "Jack of All Trees": {"description": "Cut at least one log from each tree type", "difficulty": "Easy",
                          "condition": lambda player: all(player["inventory"].get(tree, 0) > 0 for tree in TREE_DATA)},
    "Oak Enthusiast": {"description": "Cut 500 Oak logs", "difficulty": "Easy",
                       "condition": lambda player: player["inventory"].get("Oak", 0) >= 500},
    "Willow Whisperer": {"description": "Cut 500 Willow logs", "difficulty": "Easy",
                         "condition": lambda player: player["inventory"].get("Willow", 0) >= 500},

    "Intermediate Woodcutter": {"description": "Reach Woodcutting level 30", "difficulty": "Moderate",
                                "condition": lambda player: player["woodcutting_level"] >= 30},
    "Log Hoarder": {"description": "Collect 1,000 total logs", "difficulty": "Moderate",
                    "condition": lambda player: sum(player["inventory"].get(tree, 0) for tree in TREE_DATA) >= 1000},
    "Maple Master": {"description": "Cut 500 Maple logs", "difficulty": "Moderate",
                     "condition": lambda player: player["inventory"].get("Maple", 0) >= 500},
    "Yew Yeoman": {"description": "Cut 250 Yew logs", "difficulty": "Moderate",
                   "condition": lambda player: player["inventory"].get("Yew", 0) >= 250},

    "Expert Woodcutter": {"description": "Reach Woodcutting level 60", "difficulty": "Difficult",
                          "condition": lambda player: player["woodcutting_level"] >= 60},
    "Log Magnate": {"description": "Collect 10,000 total logs", "difficulty": "Difficult",
                    "condition": lambda player: sum(player["inventory"].get(tree, 0) for tree in TREE_DATA) >= 10000},
    "Magic Logger": {"description": "Cut 1,000 Magic logs", "difficulty": "Difficult",
                     "condition": lambda player: player["inventory"].get("Magic", 0) >= 1000},

    "Master Woodcutter": {"description": "Reach Woodcutting level 99", "difficulty": "Very Challenging",
                          "condition": lambda player: player["woodcutting_level"] >= 99},
    "Redwood Ruler": {"description": "Cut 2,500 Redwood logs", "difficulty": "Very Challenging",
                      "condition": lambda player: player["inventory"].get("Redwood", 0) >= 2500},

    # Combined Achievements
    "Jack of Two Trades": {"description": "Reach level 50 in both Mining and Woodcutting", "difficulty": "Moderate",
                           "condition": lambda player: player["mining_level"] >= 50 and player[
                               "woodcutting_level"] >= 50},
    "Resource Baron": {"description": "Collect 10,000 total ores and 10,000 total logs", "difficulty": "Difficult",
                       "condition": lambda player: sum(
                           player["inventory"].get(ore, 0) for ore in ORE_DATA) >= 10000 and sum(
                           player["inventory"].get(tree, 0) for tree in TREE_DATA) >= 10000},
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
