# constants.py

import os
import re

try:
    from .achievement_metadata import achievements_as_dict, build_achievement_definitions
except ImportError:
    from achievement_metadata import achievements_as_dict, build_achievement_definitions

try:
    from .cooking_data import (
        DEFAULT_COOKING_TARGET,
        cooking_burnt_items,
        cooking_extra_items_as_dict,
        cooking_output_items,
        cooking_prep_activities_as_dict,
        cooking_raw_items,
        cooking_targets_as_dict,
    )
    from .combat_data import (
        COMBAT_ATTACK_STYLE_DATA,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COMBAT_EXTRA_ITEM_DATA,
        COMBAT_FOOD_DATA,
        COMBAT_TARGET_GROUP_ORDER,
        DEFAULT_COMBAT_ATTACK_STYLE,
        DEFAULT_COMBAT_TARGET,
    )
    from .crafting_data import crafting_output_items, crafting_recipes_as_dict
    from .equipment_data import EQUIPMENT_DATA, EQUIPMENT_SLOTS, equipment_items_as_dict
    from .firemaking_data import (
        DEFAULT_FIREMAKING_TARGET,
        firemaking_extra_items_as_dict,
        firemaking_input_items,
        firemaking_output_items,
        firemaking_targets_as_dict,
    )
    from .fletching_data import (
        DEFAULT_FLETCHING_TARGET,
        FLETCHING_GROUP_LABELS,
        FLETCHING_GROUP_ORDER,
        fletching_item_names,
        fletching_output_items,
        fletching_targets_as_dict,
    )
    from .fishing_data import (
        DEFAULT_FISHING_TARGET,
        FISHING_BAIT_SHOP_SOURCE_PATH,
        fishing_extra_items_as_dict,
        fishing_methods_as_dict,
        fishing_output_items,
    )
    from .hunter_data import (
        DEFAULT_HUNTER_TARGET,
        HUNTER_GROUP_LABELS,
        HUNTER_GROUP_ORDER,
        hunter_extra_items_as_dict,
        hunter_item_names,
        hunter_output_items,
        hunter_supply_activities_as_dict,
        hunter_supply_item_names,
        hunter_targets_as_dict,
    )
    from .item_registry import build_item_definitions
    from .quest_data import (
        CLAIMS_BY_ID,
        QUESTS_BY_ID,
        claims_as_dict,
        quest_reward_items_as_dict,
        quest_references_as_dict,
        quest_unlock_rules_as_dict,
        quests_as_dict,
    )
    from .runecrafting_data import (
        DEFAULT_RUNECRAFTING_TARGET,
        BINDING_NECKLACE_ITEM,
        RUNECRAFTING_GROUP_LABELS,
        WICKED_HOOD_ITEM,
        runecrafting_access_items,
        runecrafting_extra_items_as_dict,
        runecrafting_output_items,
        runecrafting_pouches_as_dict,
        runecrafting_targets_as_dict,
    )
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
    from cooking_data import (
        DEFAULT_COOKING_TARGET,
        cooking_burnt_items,
        cooking_extra_items_as_dict,
        cooking_output_items,
        cooking_prep_activities_as_dict,
        cooking_raw_items,
        cooking_targets_as_dict,
    )
    from combat_data import (
        COMBAT_ATTACK_STYLE_DATA,
        COMBAT_BURST_TICKS,
        COMBAT_ENEMY_DATA,
        COMBAT_EXTRA_ITEM_DATA,
        COMBAT_FOOD_DATA,
        COMBAT_TARGET_GROUP_ORDER,
        DEFAULT_COMBAT_ATTACK_STYLE,
        DEFAULT_COMBAT_TARGET,
    )
    from crafting_data import crafting_output_items, crafting_recipes_as_dict
    from equipment_data import EQUIPMENT_DATA, EQUIPMENT_SLOTS, equipment_items_as_dict
    from firemaking_data import (
        DEFAULT_FIREMAKING_TARGET,
        firemaking_extra_items_as_dict,
        firemaking_input_items,
        firemaking_output_items,
        firemaking_targets_as_dict,
    )
    from fletching_data import (
        DEFAULT_FLETCHING_TARGET,
        FLETCHING_GROUP_LABELS,
        FLETCHING_GROUP_ORDER,
        fletching_item_names,
        fletching_output_items,
        fletching_targets_as_dict,
    )
    from fishing_data import (
        DEFAULT_FISHING_TARGET,
        FISHING_BAIT_SHOP_SOURCE_PATH,
        fishing_extra_items_as_dict,
        fishing_methods_as_dict,
        fishing_output_items,
    )
    from hunter_data import (
        DEFAULT_HUNTER_TARGET,
        HUNTER_GROUP_LABELS,
        HUNTER_GROUP_ORDER,
        hunter_extra_items_as_dict,
        hunter_item_names,
        hunter_output_items,
        hunter_supply_activities_as_dict,
        hunter_supply_item_names,
        hunter_targets_as_dict,
    )
    from item_registry import build_item_definitions
    from quest_data import (
        CLAIMS_BY_ID,
        QUESTS_BY_ID,
        claims_as_dict,
        quest_reward_items_as_dict,
        quest_references_as_dict,
        quest_unlock_rules_as_dict,
        quests_as_dict,
    )
    from runecrafting_data import (
        DEFAULT_RUNECRAFTING_TARGET,
        BINDING_NECKLACE_ITEM,
        RUNECRAFTING_GROUP_LABELS,
        WICKED_HOOD_ITEM,
        runecrafting_access_items,
        runecrafting_extra_items_as_dict,
        runecrafting_output_items,
        runecrafting_pouches_as_dict,
        runecrafting_targets_as_dict,
    )
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
UTILITY_ACTIVITY_ICONS_FOLDER = os.path.join(current_dir, "activityicons")
FIREMAKING_ITEMS_FOLDER = os.path.join(current_dir, "firemakingitems")
FISHING_ITEMS_FOLDER = os.path.join(current_dir, "fishingitems")
HUNTER_ITEMS_FOLDER = os.path.join(current_dir, "hunteritems")
COOKING_ITEMS_FOLDER = os.path.join(current_dir, "cookingitems")
RUNECRAFTING_ITEMS_FOLDER = os.path.join(current_dir, "runecraftingitems")
QUEST_ITEMS_FOLDER = os.path.join(current_dir, "questitems")

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
        "icon_path": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "make_soft_clay.png"),
        "group": "material_processing",
        "source": "OSRS Soft clay > Creation > Container",
    },
    "gather_wool": {
        "display_name": "Gather wool",
        "requirements": {},
        "output_item": "Wool",
        "output_qty": 1,
        "batch_size": 28,
        "icon_path": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "gather_wool.png"),
        "group": "gathering",
        "source": "Material source for OSRS Ball of wool > Creation",
    },
    "gather_flax": {
        "display_name": "Gather flax",
        "requirements": {},
        "output_item": "Flax",
        "output_qty": 1,
        "batch_size": 28,
        "icon_path": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "gather_flax.png"),
        "group": "gathering",
        "source": "OSRS Bow string > Strategy > Manual Spinning",
    },
    "scavenge_chicken_feathers": {
        "display_name": "Scavenge chicken feathers",
        "requirements": {},
        "output_item": "Feather",
        "output_qty": 1,
        "batch_size": 28,
        "icon_path": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "scavenge_chicken_feathers.png"),
        "group": "gathering",
        "source": (
            "2011Scape ranged_instructor.plugin.kts says arrows need chickens for feathers; "
            "chicken_level_1.plugin.kts drops Feather. AnkiScape temporary scavenging bridge until Combat/GE."
        ),
    },
    "gather_fishing_bait": {
        "display_name": "Gather fishing bait",
        "requirements": {},
        "output_item": "Fishing bait",
        "output_qty": 1,
        "batch_size": 28,
        "icon_path": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "gather_fishing_bait.png"),
        "group": "gathering",
        "source": f"{FISHING_BAIT_SHOP_SOURCE_PATH}: Lumbridge Fishing Supplies stock, temporary no-XP bridge.",
    },
    "open_bird_nest": {
        "display_name": "Open bird nests",
        "requirements": {},
        "openable_items": tuple(BIRD_NEST_OPEN_TABLES_BY_INPUT.keys()),
        "batch_size": 28,
        "icon_path": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "open_bird_nest.png"),
        "group": "containers_opening",
        "source": "2011Scape bird_nest.plugin.kts",
    },
}
UTILITY_ACTIVITY_DATA.update(cooking_prep_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(hunter_supply_activities_as_dict())

CRAFTING_DATA = crafting_recipes_as_dict()

CRAFTED_ITEM_IMAGES = {}
UTILITY_ITEM_IMAGES = {
    "Soft clay": os.path.join(CRAFTED_ITEMS_FOLDER, "soft_clay.png"),
    "Wool": os.path.join(CRAFTED_ITEMS_FOLDER, "wool.png"),
    "Flax": os.path.join(CRAFTED_ITEMS_FOLDER, "flax.png"),
    "Feather": os.path.join(FLETCHED_ITEMS_FOLDER, "feather.png"),
    "Fishing bait": os.path.join(FISHING_ITEMS_FOLDER, "fishing_bait.png"),
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
RUNECRAFTING_ACCESS_ITEMS = runecrafting_access_items()
QUEST_DATA = quests_as_dict()
QUEST_REFERENCE_DATA = quest_references_as_dict()
QUEST_UNLOCK_RULES = quest_unlock_rules_as_dict()
QUEST_REWARD_ITEM_DATA = quest_reward_items_as_dict()
CLAIM_DATA = claims_as_dict()


def _asset_slug(name: str) -> str:
    return "_".join(re.findall(r"[a-z0-9]+", name.lower()))


# Crafting icons cover both outputs (the craft-target row art) and the
# crafting-specific raw materials (Leather, Molten glass, orbs, runes, ...) so
# the Bank can show them too. Cross-skill materials (ores/gems/bars/logs) keep
# their own folders' art and simply have no file here. Existence-guarded:
# tools/fetch_crafting_assets.py fills crafteditems/, and an unfetched icon
# leaves that one row text-only rather than pointing at a dead path.
_crafting_item_names = set(crafting_output_items())
for _spec in CRAFTING_DATA.values():
    _crafting_item_names.update(str(_material) for _material in _spec.get("requirements", {}))
for _item_name in _crafting_item_names:
    _path = os.path.join(CRAFTED_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        CRAFTED_ITEM_IMAGES[_item_name] = _path


_FLETCHING_ITEM_NAMES = set(fletching_item_names())
_FLETCHING_ITEM_NAMES.difference_update(TREE_DATA)

FLETCHED_ITEM_IMAGES = {}
for _item_name in _FLETCHING_ITEM_NAMES:
    _path = os.path.join(FLETCHED_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        FLETCHED_ITEM_IMAGES[_item_name] = _path

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

FIREMAKING_EXTRA_ITEM_DATA = firemaking_extra_items_as_dict()
FIREMAKING_ITEM_IMAGES = dict(LOG_IMAGES)
for _item_name in FIREMAKING_EXTRA_ITEM_DATA:
    _path = FIREMAKING_ITEM_IMAGES.get(_item_name)
    if not _path:
        _path = os.path.join(FIREMAKING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if _path and os.path.exists(_path):
        FIREMAKING_ITEM_IMAGES[_item_name] = _path

FISHING_EXTRA_ITEM_DATA = fishing_extra_items_as_dict()
FISHING_ITEM_IMAGES = {}
for _item_name in set(FISHING_OUTPUT_ITEMS) | set(FISHING_EXTRA_ITEM_DATA):
    _path = os.path.join(FISHING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        FISHING_ITEM_IMAGES[_item_name] = _path

HUNTER_EXTRA_ITEM_DATA = hunter_extra_items_as_dict()
HUNTER_ITEM_IMAGES = {}
for _item_name in set(hunter_item_names()) | set(HUNTER_OUTPUT_ITEMS) | set(HUNTER_EXTRA_ITEM_DATA):
    _path = os.path.join(HUNTER_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        HUNTER_ITEM_IMAGES[_item_name] = _path
for _item_name in hunter_supply_item_names():
    _path = HUNTER_ITEM_IMAGES.get(_item_name)
    if _path:
        UTILITY_ITEM_IMAGES[_item_name] = _path

COOKING_EXTRA_ITEM_DATA = cooking_extra_items_as_dict()
COOKING_ITEM_IMAGES = {}
for _item_name in COOKING_EXTRA_ITEM_DATA:
    _path = (
        FISHING_ITEM_IMAGES.get(_item_name)
        or CRAFTED_ITEM_IMAGES.get(_item_name)
        or ORE_IMAGES.get(_item_name)
        or BAR_IMAGES.get(_item_name)
        or os.path.join(COOKING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    )
    if _path and os.path.exists(_path):
        COOKING_ITEM_IMAGES[_item_name] = _path

RUNECRAFTING_EXTRA_ITEM_DATA = runecrafting_extra_items_as_dict()
RUNECRAFTING_ITEM_IMAGES = {}
for _item_name in set(RUNECRAFTING_OUTPUT_ITEMS) | set(RUNECRAFTING_ACCESS_ITEMS) | set(RUNECRAFTING_EXTRA_ITEM_DATA):
    _path = (
        ORE_IMAGES.get(_item_name)
        or CRAFTED_ITEM_IMAGES.get(_item_name)
        or os.path.join(RUNECRAFTING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    )
    if _path and os.path.exists(_path):
        RUNECRAFTING_ITEM_IMAGES[_item_name] = _path

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
QUEST_ITEM_IMAGES = {}
QUEST_ITEM_IMAGE_FILE_OVERRIDES = {
    "Lever": "temple_lever.png",
}
for _item_name in QUEST_REWARD_ITEM_DATA:
    _path = os.path.join(
        QUEST_ITEMS_FOLDER,
        QUEST_ITEM_IMAGE_FILE_OVERRIDES.get(_item_name, f"{_asset_slug(_item_name)}.png"),
    )
    if os.path.exists(_path):
        QUEST_ITEM_IMAGES[_item_name] = _path
EQUIPMENT_ITEM_DATA = equipment_items_as_dict()


def _apply_equipment_metadata(extra_item_data):
    enriched = {item_name: dict(spec) for item_name, spec in extra_item_data.items()}
    for item_name, equipment_spec in EQUIPMENT_ITEM_DATA.items():
        if item_name not in enriched:
            continue
        enriched[item_name]["equipment_slot"] = equipment_spec["slot"]
        enriched[item_name]["equipment_type"] = equipment_spec["equipment_type"]
        enriched[item_name]["equipment_required_level"] = equipment_spec["required_level"]
        enriched[item_name]["equipment_combat_skill"] = equipment_spec["combat_skill"]
        # ItemDefinition already has a generic equipment_tier field; for smithed
        # gear this stores combat equipment requirement, while Mining bonus gear
        # keeps its Varrock/glory-specific tier from mining_data.
        enriched[item_name].setdefault("tier", equipment_spec["required_level"])
    return enriched


EXTRA_ITEM_DATA = _apply_equipment_metadata({
    **QUEST_REWARD_ITEM_DATA,
    **WOODCUTTING_EXTRA_ITEM_DATA,
    **MINING_EXTRA_ITEM_DATA,
    **SMITHING_EXTRA_ITEM_DATA,
    **FIREMAKING_EXTRA_ITEM_DATA,
    **FISHING_EXTRA_ITEM_DATA,
    **HUNTER_EXTRA_ITEM_DATA,
    **COOKING_EXTRA_ITEM_DATA,
    **RUNECRAFTING_EXTRA_ITEM_DATA,
    **COMBAT_EXTRA_ITEM_DATA,
})
EXTRA_ITEM_IMAGES = {
    **WOODCUTTING_EXTRA_ITEM_IMAGES,
    **MINING_EXTRA_ITEM_IMAGES,
    **SMITHING_EXTRA_ITEM_IMAGES,
    **FIREMAKING_ITEM_IMAGES,
    **FISHING_ITEM_IMAGES,
    **HUNTER_ITEM_IMAGES,
    **COOKING_ITEM_IMAGES,
    **RUNECRAFTING_ITEM_IMAGES,
    **QUEST_ITEM_IMAGES,
}

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
    HUNTER_DATA,
    HUNTER_ITEM_IMAGES,
    FISHING_DATA,
    FISHING_ITEM_IMAGES,
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

# Achievement metadata
ACHIEVEMENT_DEFINITIONS = build_achievement_definitions(
    MINING_OUTPUT_ITEMS,
    WOODCUTTING_LOG_ITEMS,
    GEM_DATA,
    RUNECRAFTING_OUTPUT_ITEMS,
    BAR_DATA,
    FISHING_OUTPUT_ITEMS,
    HUNTER_OUTPUT_ITEMS,
)
ACHIEVEMENTS = achievements_as_dict(ACHIEVEMENT_DEFINITIONS)
