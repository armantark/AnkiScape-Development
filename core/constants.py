# constants.py

import os
import re

from ..data.agility_data import (
    AGILITY_EXTRA_ITEM_DATA,
    AGILITY_ITEM_IMAGES,
    AGILITY_TARGETS_BY_ID,
)
from ..data.dungeoneering_data import (
    DUNGEONEERING_ITEM_IMAGES,
    dungeoneering_extra_items_as_dict,
)
from ..data.fist_of_guthix_data import (
    fist_of_guthix_activity_as_dict,
    fist_of_guthix_extra_items_as_dict,
)

from ..data.court_cases_data import (
    COURT_CASES_ACTIVITY_ID,
    court_cases_activity_as_dict,
    court_cases_extra_items_as_dict,
)

from ..data.circus_data import (
    CIRCUS_ACTIVITY_ID,
    circus_activity_as_dict,
    circus_extra_items_as_dict,
)

from ..data.trouble_brewing_data import (
    TROUBLE_BREWING_ACTIVITY_ID,
    trouble_brewing_activity_as_dict,
    trouble_brewing_equipment_data_as_dict,
    trouble_brewing_extra_items_as_dict,
)

from ..data.castle_wars_data import (
    CASTLE_WARS_ACTIVITY_ID,
    castle_wars_activity_as_dict,
    castle_wars_equipment_data_as_dict,
    castle_wars_extra_items_as_dict,
)

from ..data.pest_control_data import (
    PEST_CONTROL_ACTIVITY_ID,
    pest_control_activity_as_dict,
    pest_control_equipment_data_as_dict,
    pest_control_extra_items_as_dict,
)
from ..data.conquest_data import (
    CONQUEST_ACTIVITY_ID,
    conquest_activity_as_dict,
    conquest_equipment_data_as_dict,
    conquest_extra_items_as_dict,
)

from ..data.barbarian_assault_data import (
    BARBARIAN_ASSAULT_ACTIVITY_ID,
    barbarian_assault_activity_as_dict,
    barbarian_assault_equipment_data_as_dict,
    barbarian_assault_extra_items_as_dict,
)

from ..data.stronghold_player_safety_data import (
    STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID,
    stronghold_player_safety_activity_as_dict,
    stronghold_player_safety_equipment_data_as_dict,
    stronghold_player_safety_extra_items_as_dict,
)

from ..data.stronghold_of_security_data import (
    stronghold_of_security_extra_items_as_dict,
)

from ..data.soul_wars_data import (
    SOUL_WARS_ACTIVITY_ID,
    soul_wars_activity_as_dict,
)

from ..data.shades_of_mortton_data import (
    SHADES_OF_MORTTON_ACTIVITY_ID,
    shades_of_mortton_activity_as_dict,
    shades_of_mortton_extra_items_as_dict,
)

from ..data.tzhaar_fight_pit_data import (
    TZHAAR_FIGHT_PIT_ACTIVITY_ID,
    tzhaar_fight_pit_activity_as_dict,
)
from ..data.duel_arena_data import (
    DUEL_ARENA_ACTIVITY_ID,
    DUELLISTS_CAP_TIERS,
    duel_arena_activity_as_dict,
    duel_arena_equipment_data_as_dict,
    duel_arena_extra_items_as_dict,
)
from ..data.clan_wars_data import (
    CLAN_WARS_ACTIVITY_ID,
    clan_wars_activity_as_dict,
)
from ..data.troll_invasion_data import (
    TROLL_INVASION_ACTIVITY_ID,
    TROLL_INVASION_REWARD_BOOK,
    troll_invasion_activity_as_dict,
    troll_invasion_extra_items_as_dict,
)
from ..data.shattered_heart_data import (
    SHATTERED_HEART_ACTIVITY_ID,
    SHATTERED_HEART_BAG_ITEM,
    SHATTERED_HEART_PLINTH_ITEM,
    SHATTERED_HEART_SKILLS,
    shattered_heart_activity_as_dict,
    shattered_heart_extra_items_as_dict,
)
from ..data.mage_training_arena_data import (
    MAGE_TRAINING_ARENA_ACTIVITY_ID,
    MAGE_TRAINING_ARENA_ASSET_MANIFEST,
    mage_training_arena_activity_as_dict,
    mage_training_arena_equipment_data_as_dict,
    mage_training_arena_extra_items_as_dict,
)
from ..data.gnome_restaurant_data import (
    GNOME_RESTAURANT_ACTIVITY_ID,
    GNOME_RESTAURANT_ASSET_MANIFEST,
    gnome_restaurant_activity_as_dict,
    gnome_restaurant_extra_items_as_dict,
)
from ..data.temple_trekking_data import (
    TEMPLE_TREKKING_ACTIVITY_ID,
    TEMPLE_TREKKING_ASSET_MANIFEST,
    temple_trekking_activity_as_dict,
    temple_trekking_extra_items_as_dict,
)
from ..data.mobilising_armies_data import (
    MOBILISING_ARMIES_ACTIVITY_ID,
    MOBILISING_ARMIES_ASSET_MANIFEST,
    mobilising_armies_activity_as_dict,
    mobilising_armies_equipment_data_as_dict,
    mobilising_armies_extra_items_as_dict,
)
from ..data.dominion_tower_data import (
    DOMINION_TOWER_ACTIVITY_ID,
    DOMINION_TOWER_ASSET_MANIFEST,
    dominion_tower_activity_as_dict,
    dominion_tower_equipment_data_as_dict,
    dominion_tower_extra_items_as_dict,
)
from ..data.goblin_raids_data import (
    GOBLIN_RAID_ENEMIES,
    GOBLIN_RAIDS_ACTIVITY_ID,
    goblin_raids_activity_as_dict,
    goblin_raids_equipment_data_as_dict,
    goblin_raids_extra_items_as_dict,
)
from ..data.crucible_data import (
    CRUCIBLE_ACTIVITY_ID,
    crucible_activity_as_dict,
    crucible_equipment_data_as_dict,
    crucible_extra_items_as_dict,
)

from ..data.daily_challenges_data import (
    daily_challenge_extra_items_as_dict,
)

from ..data.treasure_trails_data import (
    TREASURE_TRAILS_ACTIVITY_ID,
    TREASURE_TRAILS_ART_ITEMS,
    treasure_trails_activity_as_dict,
    treasure_trails_extra_items_as_dict,
)

from ..data.varrock_museum_data import (
    VARROCK_MUSEUM_ACTIVITY_ID,
    varrock_museum_activity_as_dict,
    varrock_museum_extra_items_as_dict,
)

from ..data.fight_caves_data import (
    FIGHT_CAVES_ACTIVITY_ID,
    fight_caves_activity_as_dict,
    fight_caves_extra_items_as_dict,
)

from ..data.phoenix_lair_data import (
    PHOENIX_LAIR_ACTIVITY_ID,
    phoenix_lair_activity_as_dict,
    phoenix_lair_extra_items_as_dict,
)
from ..data.enchanted_key_data import (
    ENCHANTED_KEY_ACTIVITY_ID,
    ENCHANTED_KEY_MJOLNIRS,
    enchanted_key_activity_as_dict,
    enchanted_key_extra_items_as_dict,
)
from ..data.tears_of_guthix_data import (
    TEARS_OF_GUTHIX_ACTIVITY_ID,
    tears_of_guthix_activity_as_dict,
)
from ..data.bork_data import (
    BORK_ACTIVITY_ID,
    bork_activity_as_dict,
    bork_extra_items_as_dict,
)
from ..data.skeletal_horror_data import (
    SKELETAL_HORROR_ACTIVITY_ID,
    skeletal_horror_activity_as_dict,
    skeletal_horror_extra_items_as_dict,
)

from ..data.stealing_creation_data import (
    STEALING_CREATION_ACTIVITY_ID,
    stealing_creation_activity_as_dict,
    stealing_creation_extra_items_as_dict,
)

from ..data.sorceress_garden_data import (
    SORCERESS_GARDEN_ACTIVITY_ID,
    sorceress_garden_activity_as_dict,
    sorceress_garden_extra_items_as_dict,
)

from ..data.achievement_diary_data import (
    ACHIEVEMENT_DIARY_CATALOG,
    diary_equipment_data_as_dict,
)
from ..data.achievement_cape_data import (
    cape_equipment_data_as_dict,
    milestone_cape_equipment_data_as_dict,
)
from ..data.penguin_hide_and_seek_data import (
    PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID,
    penguin_hide_and_seek_activity_as_dict,
    penguin_hide_and_seek_equipment_data_as_dict,
)

from ..data.vinesweeper_data import (
    COMPOST_POTION_ACTIVITY_ID,
    VINESWEEPER_ACTIVITY_ID,
    compost_potion_activities_as_dict,
    vinesweeper_activity_as_dict,
    vinesweeper_extra_items_as_dict,
)

from ..data.construction_data import (
    CONSTRUCTION_DATA,
    DEFAULT_CONSTRUCTION_TARGET,
    construction_asset_items_as_dict,
    construction_extra_items_as_dict,
)

from .achievement_metadata import achievements_as_dict, build_achievement_definitions

from ..data.cooking_data import (
    DEFAULT_COOKING_TARGET,
    cooking_burnt_items,
    cooking_extra_items_as_dict,
    cooking_output_items,
    cooking_prep_activities_as_dict,
    cooking_raw_items,
    cooking_targets_as_dict,
)
from ..data.combat_data import (
    COMBAT_ATTACK_STYLE_DATA,
    COMBAT_BURST_TICKS,
    COMBAT_ENEMY_DATA,
    COMBAT_EXTRA_ITEM_DATA,
    COMBAT_FOOD_DATA,
    CONSUMABLE_DATA,
    COMBAT_MAGIC_SPELL_DATA,
    COMBAT_TARGET_GROUP_ORDER,
    DEFAULT_COMBAT_ATTACK_STYLE,
    DEFAULT_COMBAT_SPELL,
    DEFAULT_COMBAT_TARGET,
)
from ..data.crafting_data import crafting_output_items, crafting_recipes_as_dict, crafting_required_items_as_dict, crafting_special_items_as_dict, tanning_activities_as_dict
from ..data.equipment_data import EQUIPMENT_DATA, EQUIPMENT_SLOTS, equipment_items_as_dict
from ..data.flash_powder_factory_data import (
    FLASH_POWDER_FACTORY_ACTIVITY_ID,
    flash_powder_factory_activity_as_dict,
    flash_powder_factory_extra_items_as_dict,
)
from ..data.pyramid_plunder_data import (
    PYRAMID_PLUNDER_ACTIVITY_ID,
    pyramid_plunder_activity_as_dict,
    pyramid_plunder_extra_items_as_dict,
)
from ..data.werewolf_skullball_data import (
    WEREWOLF_SKULLBALL_ACTIVITY_ID,
    werewolf_skullball_activity_as_dict,
    werewolf_skullball_extra_items_as_dict,
)
from ..data.gnome_ball_data import (
    GNOME_BALL_ACTIVITY_ID,
    gnome_ball_activity_as_dict,
    gnome_ball_extra_items_as_dict,
)
from ..data.fish_flingers_data import (
    FISH_FLINGERS_ACTIVITY_ID,
    fish_flingers_activity_as_dict,
    fish_flingers_equipment_data_as_dict,
    fish_flingers_extra_items_as_dict,
)
from ..data.fishing_trawler_data import (
    FISHING_TRAWLER_ACTIVITY_ID,
    fishing_trawler_activity_as_dict,
)
from ..data.great_orb_project_data import (
    GREAT_ORB_PROJECT_ACTIVITY_ID,
    great_orb_project_activity_as_dict,
)
from ..data.managing_miscellania_data import (
    MANAGING_MISCELLANIA_ACTIVITY_ID,
    managing_miscellania_activity_as_dict,
)
from ..data.barrows_data import (
    BARROWS_ACTIVITY_ID,
    barrows_activity_as_dict,
    barrows_equipment_data_as_dict,
    barrows_extra_items_as_dict,
)
from ..data.big_chinchompa_data import (
    BIG_CHINCHOMPA_UTILITY_ID,
    big_chinchompa_activity_as_dict,
    big_chinchompa_extra_items_as_dict,
)
from ..data.evil_tree_data import evil_tree_extra_items_as_dict
from ..data.shooting_star_data import (
    SHOOTING_STAR_ACTIVITY_ID,
    shooting_star_activity_as_dict,
    shooting_star_extra_items_as_dict,
)
from ..data.firemaking_data import (
    DEFAULT_FIREMAKING_TARGET,
    firemaking_extra_items_as_dict,
    firemaking_input_items,
    firemaking_output_items,
    firemaking_targets_as_dict,
    light_source_activities_as_dict,
)
from ..data.fletching_data import (
    DEFAULT_FLETCHING_TARGET,
    FLETCHING_GROUP_LABELS,
    FLETCHING_GROUP_ORDER,
    fletching_item_names,
    fletching_output_items,
    fletching_targets_as_dict,
)
from ..data.fishing_data import (
    DEFAULT_FISHING_TARGET,
    fishing_extra_items_as_dict,
    fishing_methods_as_dict,
    fishing_output_items,
)
from ..data.farming_data import FARMING_COMPOST_VISUAL_ITEMS, FARMING_ITEM_DATA, FARMING_PATCH_VISUAL_ITEMS
from ..data.hunter_data import (
    DEFAULT_HUNTER_TARGET,
    HUNTER_GROUP_LABELS,
    HUNTER_GROUP_ORDER,
    hunter_extra_items_as_dict,
    hunter_item_names,
    hunter_output_items,
    hunter_supply_item_names,
    hunter_targets_as_dict,
)
from .item_registry import apply_item_asset_overrides, build_item_definitions, slugify_item_id
from ..data.quest_data import (
    CLAIMS_BY_ID,
    QUESTS_BY_ID,
    claims_as_dict,
    quest_reward_items_as_dict,
    quest_references_as_dict,
    quest_unlock_rules_as_dict,
    quests_as_dict,
)
from ..data.runecrafting_data import (
    DEFAULT_RUNECRAFTING_TARGET,
    BINDING_NECKLACE_ITEM,
    RUNECRAFTING_GROUP_LABELS,
    WICKED_HOOD_ITEM,
    runecrafting_access_items,
    runecrafting_extra_items_as_dict,
    runecrafting_output_items,
    runecrafting_rune_output_items,
    runecrafting_pouches_as_dict,
    runecrafting_targets_as_dict,
)
from ..data.herblore_data import (
    DEFAULT_HERBLORE_TARGET,
    HERBLORE_GROUP_LABELS,
    herblore_extra_items_as_dict,
    herblore_finished_output_items,
    herblore_item_names,
    herblore_output_items,
    herblore_targets_as_dict,
    input_preparation_activities_as_dict,
    pestle_and_mortar_activities_as_dict,
)
from ..data.shop_data import shop_extra_items_as_dict
from ..data.summoning_data import summoning_extra_items_as_dict
from ..data.potion_data import potion_items_as_dict, potion_item_names
from ..data.prayer_data import (
    DEFAULT_PRAYER_TARGET,
    PRAYER_GROUP_ORDER,
    prayer_extra_items_as_dict,
    prayer_targets_as_dict,
    prayer_utility_activities_as_dict,
)
from ..data.prayer_passive_data import prayer_passive_items_as_dict
from ..data.thieving_data import thieving_extra_items_as_dict
from ..data.urn_data import URN_TIERS, urn_extra_items_as_dict
from ..data.warriors_guild_data import WARRIORS_GUILD_ACTIVITIES
from ..data.livid_farm_data import livid_farm_activity_as_dict
from ..data.magic_data import (
    DEFAULT_MAGIC_TARGET,
    MAGIC_GROUP_ORDER,
    magic_extra_items_as_dict,
    magic_targets_as_dict,
)
from ..data.mining_data import (
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
from ..data.smithing_data import (
    DEFAULT_SMITHING_TARGET,
    smithing_bars_as_dict,
    smithing_extra_items_as_dict,
    smithing_output_items,
    smithing_recipes_as_dict,
)
from ..data.woodcutting_data import (
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
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
HERBLORE_ITEMS_FOLDER = os.path.join(current_dir, "herbloreitems")
QUEST_ITEMS_FOLDER = os.path.join(current_dir, "questitems")
COMBAT_ITEMS_FOLDER = os.path.join(current_dir, "combatitems")
COMBAT_ENEMIES_FOLDER = os.path.join(current_dir, "combatenemies")
SHOP_ITEMS_FOLDER = os.path.join(current_dir, "shopitems")
PRAYER_ITEMS_FOLDER = os.path.join(current_dir, "prayeritems")
MAGIC_ITEMS_FOLDER = os.path.join(current_dir, "magicitems")
MAGIC_SPELLS_FOLDER = os.path.join(current_dir, "magicspells")
CONSTRUCTION_ITEMS_FOLDER = os.path.join(current_dir, "constructionitems")
SUMMONING_ITEMS_FOLDER = os.path.join(current_dir, "summoningitems")
FARMING_ITEMS_FOLDER = os.path.join(current_dir, "farmingitems")
FARMING_HUD_SPROUT_ICON = os.path.join(current_dir, "icon", "farming_icon.png")

# Image dictionaries
# New constants for Crafting
CRAFTED_ITEMS_FOLDER = os.path.join(current_dir, "crafteditems")

DEFAULT_UTILITY_ACTIVITY = "make_soft_clay"
UTILITY_ACTIVITY_DATA = {
    "bankstanding": {
        "display_name": "Bankstanding",
        "requirements": {},
        "batch_size": 1,
        "no_op": True,
        "icon_path": os.path.join(current_dir, "combatitems", "coins.png"),
        "group": "economy",
        "source": "memory-bank/fake-grand-exchange-design.md:61-67",
    },
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
    "make_robust_glass": {
        "display_name": "Make robust glass",
        "requirements": {"Red sandstone": 1},
        "output_item": "Robust glass",
        "output_qty": 1,
        "batch_size": 28,
        "icon_path": os.path.join(CRAFTED_ITEMS_FOLDER, "robust_glass.png"),
        "group": "material_processing",
        "source": "https://runescape.wiki/w/Robust_glass?oldid=6504157",
    },
    "convert_logs_to_planks": {
        "display_name": "Convert logs to planks",
        "requirements": {"Logs": 1, "Coins": 100},
        "output_item": "Plank",
        "output_qty": 1,
        "batch_size": 28,
        "group": "material_processing",
        "source": "Darkan SawmillOperator planks and LunarSpellbook plank-make cost path",
    },
    "convert_oak_logs_to_oak_planks": {
        "display_name": "Convert oak logs to oak planks",
        "requirements": {"Oak logs": 1, "Coins": 250},
        "output_item": "Oak plank",
        "output_qty": 1,
        "batch_size": 28,
        "group": "material_processing",
        "source": "Darkan SawmillOperator planks and LunarSpellbook plank-make cost path",
    },
    "convert_teak_logs_to_teak_planks": {
        "display_name": "Convert teak logs to teak planks",
        "requirements": {"Teak logs": 1, "Coins": 500},
        "output_item": "Teak plank", "output_qty": 1, "batch_size": 28,
        "group": "material_processing",
        "icon_path": os.path.join(CONSTRUCTION_ITEMS_FOLDER, "teak_plank.png"),
        "source": "Darkan SawmillOperator.java @ 7e7d67b481f1b94599de38a98c470419ab7c96b3",
    },
    "convert_mahogany_logs_to_mahogany_planks": {
        "display_name": "Convert mahogany logs to mahogany planks",
        "requirements": {"Mahogany logs": 1, "Coins": 1500},
        "output_item": "Mahogany plank", "output_qty": 1, "batch_size": 28,
        "group": "material_processing",
        "icon_path": os.path.join(CONSTRUCTION_ITEMS_FOLDER, "mahogany_plank.png"),
        "source": "Darkan SawmillOperator.java @ 7e7d67b481f1b94599de38a98c470419ab7c96b3",
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
    "gather_swamp_toads": {
        "display_name": "Gather swamp toads",
        "requirements": {},
        "output_item": "Swamp toad",
        "output_qty": 1,
        "batch_size": 28,
        "group": "gathering",
        "source": "https://runescape.wiki/w/Swamp_toad?oldid=6088673",
    },
    "grab_desert_phoenix_feather": {
        "display_name": "Grab Desert Phoenix feather",
        "requirements": {},
        "output_item": "Phoenix feather",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "desert_phoenix.png"),
        "group": "gathering",
        "source": "https://runescape.wiki/w/Desert_Phoenix?oldid=6295341",
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
    # Pestle-and-mortar grinding. Zero XP and toolless, following the make_soft_clay
    # convention; these produce the crushed/dust secondaries the Herblore finished
    # recipes consume. Parity: PestleAndMortarData.kt (1:1 source -> product).
    "grind_unicorn_horn": {
        "display_name": "Grind unicorn horn",
        "requirements": {"Unicorn horn": 1},
        "output_item": "Unicorn horn dust",
        "output_qty": 1,
        "batch_size": 28,
        "group": "grinding",
        "source": "2011Scape PestleAndMortarData.UNICORN_HORN",
    },
    "grind_chocolate_bar": {
        "display_name": "Grind chocolate bar",
        "requirements": {"Chocolate bar": 1},
        "output_item": "Chocolate dust",
        "output_qty": 1,
        "batch_size": 28,
        "group": "grinding",
        "source": "2011Scape PestleAndMortarData.CHOCOLATE_BAR",
    },
    "grind_kebbit_teeth": {
        "display_name": "Grind kebbit teeth",
        "requirements": {"Kebbit teeth": 1},
        "output_item": "Kebbit teeth dust",
        "output_qty": 1,
        "batch_size": 28,
        "group": "grinding",
        "source": "2011Scape PestleAndMortarData.KEBBIT_TEETH",
    },
    "grind_birds_nest": {
        "display_name": "Grind bird's nest",
        "requirements": {"Bird's nest (empty)": 1},
        "output_item": "Crushed nest",
        "output_qty": 1,
        "batch_size": 28,
        "group": "grinding",
        "source": "2011Scape PestleAndMortarData.BirdNest: item 5075 -> Crushed nest",
    },
    "grind_desert_goat_horn": {
        "display_name": "Grind desert goat horn",
        "requirements": {"Desert goat horn": 1},
        "output_item": "Goat horn dust",
        "output_qty": 1,
        "batch_size": 28,
        "group": "grinding",
        "source": "2011Scape PestleAndMortarData.DESERT_GOAT_HORN",
    },
    "grind_blue_dragon_scale": {
        "display_name": "Grind blue dragon scale",
        "requirements": {"Blue dragon scale": 1},
        "output_item": "Dragon scale dust",
        "output_qty": 1,
        "batch_size": 28,
        "group": "grinding",
        "source": "2011Scape PestleAndMortarData.BLUE_DRAGON_SCALE",
    },
    "grind_mud_rune": {
        "display_name": "Grind mud rune",
        "requirements": {"Mud rune": 1},
        "output_item": "Ground mud runes",
        "output_qty": 1,
        "batch_size": 28,
        "group": "grinding",
        "source": "2011Scape PestleAndMortarData.MUD_RUNE",
    },
}
UTILITY_ACTIVITY_DATA.update(tanning_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(cooking_prep_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(pestle_and_mortar_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(light_source_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(input_preparation_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(prayer_utility_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(WARRIORS_GUILD_ACTIVITIES)
UTILITY_ACTIVITY_DATA.update(big_chinchompa_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(shooting_star_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(fist_of_guthix_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(court_cases_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(circus_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(trouble_brewing_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(castle_wars_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(pest_control_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(conquest_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(barbarian_assault_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(stronghold_player_safety_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(soul_wars_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(shades_of_mortton_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(tzhaar_fight_pit_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(duel_arena_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(clan_wars_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(troll_invasion_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(shattered_heart_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(mage_training_arena_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(temple_trekking_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(mobilising_armies_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(gnome_restaurant_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(dominion_tower_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(crucible_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(goblin_raids_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(treasure_trails_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(varrock_museum_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(fight_caves_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(phoenix_lair_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(skeletal_horror_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(bork_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(tears_of_guthix_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(enchanted_key_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(stealing_creation_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(barrows_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(flash_powder_factory_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(pyramid_plunder_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(werewolf_skullball_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(gnome_ball_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(fish_flingers_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(fishing_trawler_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(great_orb_project_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(managing_miscellania_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(sorceress_garden_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(penguin_hide_and_seek_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(vinesweeper_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(compost_potion_activities_as_dict())
FAMILIARISATION_ACTIVITY_ID = "familiarisation"
UTILITY_ACTIVITY_DATA[FAMILIARISATION_ACTIVITY_ID] = {
    "display_name": "Familiarisation",
    "requirements": {},
    "batch_size": 1,
    "group": "distractions_and_diversions",
    "source": (
        "memory-bank/summoning-skill-contract-2026-07-17.md "
        "(owner-settled review-driven session)"
    ),
}
UTILITY_ACTIVITY_DATA.update(
    livid_farm_activity_as_dict(
        os.path.join(current_dir, "icon", "magic_icon.png")
    )
)
for _activity_id in WARRIORS_GUILD_ACTIVITIES:
    _activity_icon = os.path.join(
        UTILITY_ACTIVITY_ICONS_FOLDER,
        f"{_activity_id}.png",
    )
    if os.path.exists(_activity_icon):
        UTILITY_ACTIVITY_DATA[_activity_id]["icon_path"] = _activity_icon
_big_chinchompa_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "big_chinchompa.png",
)
if os.path.exists(_big_chinchompa_icon):
    UTILITY_ACTIVITY_DATA[BIG_CHINCHOMPA_UTILITY_ID]["icon_path"] = (
        _big_chinchompa_icon
    )
_shooting_star_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "shooting_stars.png",
)
if os.path.exists(_shooting_star_icon):
    UTILITY_ACTIVITY_DATA[SHOOTING_STAR_ACTIVITY_ID]["icon_path"] = (
        _shooting_star_icon
    )
_fist_of_guthix_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "fist_of_guthix.png",
)
if os.path.exists(_fist_of_guthix_icon):
    UTILITY_ACTIVITY_DATA["fist_of_guthix"]["icon_path"] = (
        _fist_of_guthix_icon
    )
_court_cases_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "court_cases.png",
)
if os.path.exists(_court_cases_icon):
    UTILITY_ACTIVITY_DATA[COURT_CASES_ACTIVITY_ID]["icon_path"] = (
        _court_cases_icon
    )
_circus_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "big_top_bonanza.png",
)
if os.path.exists(_circus_icon):
    UTILITY_ACTIVITY_DATA[CIRCUS_ACTIVITY_ID]["icon_path"] = _circus_icon
_trouble_brewing_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "trouble_brewing.png",
)
if os.path.exists(_trouble_brewing_icon):
    UTILITY_ACTIVITY_DATA[TROUBLE_BREWING_ACTIVITY_ID]["icon_path"] = (
        _trouble_brewing_icon
    )
_castle_wars_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "castle_wars.png",
)
if os.path.exists(_castle_wars_icon):
    UTILITY_ACTIVITY_DATA[CASTLE_WARS_ACTIVITY_ID]["icon_path"] = _castle_wars_icon
_pest_control_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "pest_control.png",
)
if os.path.exists(_pest_control_icon):
    UTILITY_ACTIVITY_DATA[PEST_CONTROL_ACTIVITY_ID]["icon_path"] = _pest_control_icon
_conquest_icon = os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "conquest.png")
if os.path.exists(_conquest_icon):
    UTILITY_ACTIVITY_DATA[CONQUEST_ACTIVITY_ID]["icon_path"] = _conquest_icon
_barbarian_assault_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "barbarian_assault.png",
)
if os.path.exists(_barbarian_assault_icon):
    UTILITY_ACTIVITY_DATA[BARBARIAN_ASSAULT_ACTIVITY_ID]["icon_path"] = (
        _barbarian_assault_icon
    )
_stronghold_player_safety_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "stronghold_player_safety.png",
)
if os.path.exists(_stronghold_player_safety_icon):
    UTILITY_ACTIVITY_DATA[STRONGHOLD_PLAYER_SAFETY_ACTIVITY_ID]["icon_path"] = (
        _stronghold_player_safety_icon
    )
_soul_wars_icon = os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "soul_wars.png")
if os.path.exists(_soul_wars_icon):
    UTILITY_ACTIVITY_DATA[SOUL_WARS_ACTIVITY_ID]["icon_path"] = _soul_wars_icon
_shades_of_mortton_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "shades_of_mortton.png",
)
if os.path.exists(_shades_of_mortton_icon):
    UTILITY_ACTIVITY_DATA[SHADES_OF_MORTTON_ACTIVITY_ID]["icon_path"] = (
        _shades_of_mortton_icon
    )
_treasure_trails_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "treasure_trail.png",
)
if os.path.exists(_treasure_trails_icon):
    UTILITY_ACTIVITY_DATA[TREASURE_TRAILS_ACTIVITY_ID]["icon_path"] = (
        _treasure_trails_icon
    )

_tzhaar_fight_pit_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "tzhaar_fight_pit.png",
)
if os.path.exists(_tzhaar_fight_pit_icon):
    UTILITY_ACTIVITY_DATA[TZHAAR_FIGHT_PIT_ACTIVITY_ID]["icon_path"] = (
        _tzhaar_fight_pit_icon
    )
_duel_arena_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "duel_arena.png",
)
if os.path.exists(_duel_arena_icon):
    UTILITY_ACTIVITY_DATA[DUEL_ARENA_ACTIVITY_ID]["icon_path"] = _duel_arena_icon
_clan_wars_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "clan_wars.png",
)
if os.path.exists(_clan_wars_icon):
    UTILITY_ACTIVITY_DATA[CLAN_WARS_ACTIVITY_ID]["icon_path"] = _clan_wars_icon
_troll_invasion_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "troll_invasion.png",
)
if os.path.exists(_troll_invasion_icon):
    UTILITY_ACTIVITY_DATA[TROLL_INVASION_ACTIVITY_ID]["icon_path"] = (
        _troll_invasion_icon
    )
_shattered_heart_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "shattered_heart.png",
)
if os.path.exists(_shattered_heart_icon):
    UTILITY_ACTIVITY_DATA[SHATTERED_HEART_ACTIVITY_ID]["icon_path"] = (
        _shattered_heart_icon
    )
_mage_training_arena_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "mage_training_arena.png",
)
if os.path.exists(_mage_training_arena_icon):
    UTILITY_ACTIVITY_DATA[MAGE_TRAINING_ARENA_ACTIVITY_ID]["icon_path"] = (
        _mage_training_arena_icon
    )
_gnome_restaurant_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "gnome_restaurant.png",
)
if os.path.exists(_gnome_restaurant_icon):
    UTILITY_ACTIVITY_DATA[GNOME_RESTAURANT_ACTIVITY_ID]["icon_path"] = (
        _gnome_restaurant_icon
    )
_temple_trekking_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "temple_trekking.png",
)
if os.path.exists(_temple_trekking_icon):
    UTILITY_ACTIVITY_DATA[TEMPLE_TREKKING_ACTIVITY_ID]["icon_path"] = (
        _temple_trekking_icon
    )
_mobilising_armies_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "mobilising_armies.png",
)
if os.path.exists(_mobilising_armies_icon):
    UTILITY_ACTIVITY_DATA[MOBILISING_ARMIES_ACTIVITY_ID]["icon_path"] = (
        _mobilising_armies_icon
    )
_dominion_tower_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "dominion_tower.png",
)
if os.path.exists(_dominion_tower_icon):
    UTILITY_ACTIVITY_DATA[DOMINION_TOWER_ACTIVITY_ID]["icon_path"] = (
        _dominion_tower_icon
    )
_crucible_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "crucible.png",
)
if os.path.exists(_crucible_icon):
    UTILITY_ACTIVITY_DATA[CRUCIBLE_ACTIVITY_ID]["icon_path"] = _crucible_icon
_goblin_raids_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "goblin_raids.png",
)
if os.path.exists(_goblin_raids_icon):
    UTILITY_ACTIVITY_DATA[GOBLIN_RAIDS_ACTIVITY_ID]["icon_path"] = (
        _goblin_raids_icon
    )
_varrock_museum_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "varrock_museum.png",
)
if os.path.exists(_varrock_museum_icon):
    UTILITY_ACTIVITY_DATA[VARROCK_MUSEUM_ACTIVITY_ID]["icon_path"] = (
        _varrock_museum_icon
    )
_fight_caves_icon = os.path.join(current_dir, "constructionitems", "fire_cape.png")
if os.path.exists(_fight_caves_icon):
    UTILITY_ACTIVITY_DATA[FIGHT_CAVES_ACTIVITY_ID]["icon_path"] = _fight_caves_icon
_phoenix_lair_icon = os.path.join(current_dir, "activityitems", "phoenix_quill.png")
if os.path.exists(_phoenix_lair_icon):
    UTILITY_ACTIVITY_DATA[PHOENIX_LAIR_ACTIVITY_ID]["icon_path"] = _phoenix_lair_icon
_skeletal_horror_icon = os.path.join(
    current_dir, "combatenemies", "skeletal_horror.png"
)
if os.path.exists(_skeletal_horror_icon):
    UTILITY_ACTIVITY_DATA[SKELETAL_HORROR_ACTIVITY_ID]["icon_path"] = (
        _skeletal_horror_icon
    )
_bork_icon = os.path.join(current_dir, "combatenemies", "bork.png")
if os.path.exists(_bork_icon):
    UTILITY_ACTIVITY_DATA[BORK_ACTIVITY_ID]["icon_path"] = _bork_icon
_enchanted_key_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "enchanted_key.png",
)
if os.path.exists(_enchanted_key_icon):
    UTILITY_ACTIVITY_DATA[ENCHANTED_KEY_ACTIVITY_ID]["icon_path"] = (
        _enchanted_key_icon
    )
_tears_of_guthix_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "tears_of_guthix.png",
)
if os.path.exists(_tears_of_guthix_icon):
    UTILITY_ACTIVITY_DATA[TEARS_OF_GUTHIX_ACTIVITY_ID]["icon_path"] = (
        _tears_of_guthix_icon
    )
_stealing_creation_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "stealing_creation.png",
)
if os.path.exists(_stealing_creation_icon):
    UTILITY_ACTIVITY_DATA[STEALING_CREATION_ACTIVITY_ID]["icon_path"] = (
        _stealing_creation_icon
    )
_barrows_icon = os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "barrows.png")
if os.path.exists(_barrows_icon):
    UTILITY_ACTIVITY_DATA[BARROWS_ACTIVITY_ID]["icon_path"] = _barrows_icon
_flash_powder_factory_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "flash_powder_factory.png",
)
if os.path.exists(_flash_powder_factory_icon):
    UTILITY_ACTIVITY_DATA[FLASH_POWDER_FACTORY_ACTIVITY_ID]["icon_path"] = (
        _flash_powder_factory_icon
    )
_pyramid_plunder_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "pyramid_plunder.png",
)
if os.path.exists(_pyramid_plunder_icon):
    UTILITY_ACTIVITY_DATA[PYRAMID_PLUNDER_ACTIVITY_ID]["icon_path"] = (
        _pyramid_plunder_icon
    )
_werewolf_skullball_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "werewolf_skullball.png",
)
if os.path.exists(_werewolf_skullball_icon):
    UTILITY_ACTIVITY_DATA[WEREWOLF_SKULLBALL_ACTIVITY_ID]["icon_path"] = (
        _werewolf_skullball_icon
    )
_gnome_ball_icon = os.path.join(
    current_dir,
    "agilityitems",
    "gnomeball.png",
)
if os.path.exists(_gnome_ball_icon):
    UTILITY_ACTIVITY_DATA[GNOME_BALL_ACTIVITY_ID]["icon_path"] = _gnome_ball_icon
_fish_flingers_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "fish_flingers.png",
)
if os.path.exists(_fish_flingers_icon):
    UTILITY_ACTIVITY_DATA[FISH_FLINGERS_ACTIVITY_ID]["icon_path"] = (
        _fish_flingers_icon
    )
_fishing_trawler_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "fishing_trawler.png",
)
if os.path.exists(_fishing_trawler_icon):
    UTILITY_ACTIVITY_DATA[FISHING_TRAWLER_ACTIVITY_ID]["icon_path"] = (
        _fishing_trawler_icon
    )
_great_orb_project_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "great_orb_project.png",
)
if os.path.exists(_great_orb_project_icon):
    UTILITY_ACTIVITY_DATA[GREAT_ORB_PROJECT_ACTIVITY_ID]["icon_path"] = (
        _great_orb_project_icon
    )
_managing_miscellania_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "managing_miscellania.png",
)
if os.path.exists(_managing_miscellania_icon):
    UTILITY_ACTIVITY_DATA[MANAGING_MISCELLANIA_ACTIVITY_ID]["icon_path"] = (
        _managing_miscellania_icon
    )
_sorceress_garden_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "sorceress_garden.png",
)
if os.path.exists(_sorceress_garden_icon):
    UTILITY_ACTIVITY_DATA[SORCERESS_GARDEN_ACTIVITY_ID]["icon_path"] = (
        _sorceress_garden_icon
    )
_penguin_hide_and_seek_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "penguin_hide_and_seek.png",
)
if os.path.exists(_penguin_hide_and_seek_icon):
    UTILITY_ACTIVITY_DATA[PENGUIN_HIDE_AND_SEEK_ACTIVITY_ID]["icon_path"] = (
        _penguin_hide_and_seek_icon
    )
_vinesweeper_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "vinesweeper.png",
)
if os.path.exists(_vinesweeper_icon):
    UTILITY_ACTIVITY_DATA[VINESWEEPER_ACTIVITY_ID]["icon_path"] = (
        _vinesweeper_icon
    )
_compost_potion_icon = os.path.join(
    current_dir,
    "activityitems",
    "compost_potion_4.png",
)
if os.path.exists(_compost_potion_icon):
    UTILITY_ACTIVITY_DATA[COMPOST_POTION_ACTIVITY_ID]["icon_path"] = (
        _compost_potion_icon
    )
_familiarisation_icon = os.path.join(
    current_dir,
    "icon",
    "summoning_icon.png",
)
if os.path.exists(_familiarisation_icon):
    UTILITY_ACTIVITY_DATA[FAMILIARISATION_ACTIVITY_ID]["icon_path"] = (
        _familiarisation_icon
    )

UTILITY_SURFACE_ID = "utilities"
ACTIVITY_SURFACE_ID = "activities"
UTILITY_ACTIVITY_GROUPS = frozenset(
    {
        "economy",
        "cooking_prep",
        "gathering",
        "material_processing",
        "containers_opening",
        "grinding",
        "light_sources",
        "input_preparation",
        "prayer_preparation",
    }
)
ACTIVITY_GROUPS = frozenset(
    {"warriors_guild", "minigames", "distractions_and_diversions", "landmarks"}
)
for _activity_spec in UTILITY_ACTIVITY_DATA.values():
    _activity_group = str(_activity_spec.get("group", "material_processing"))
    if _activity_group in ACTIVITY_GROUPS:
        _activity_spec["surface"] = ACTIVITY_SURFACE_ID
    elif _activity_group in UTILITY_ACTIVITY_GROUPS:
        _activity_spec["surface"] = UTILITY_SURFACE_ID

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
_crafting_item_names.update(CRAFTING_REQUIRED_ITEM_DATA)
for _item_name in _crafting_item_names:
    _path = os.path.join(CRAFTED_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        CRAFTED_ITEM_IMAGES[_item_name] = _path

# The existing finished-urn sprites are shared by their runed, active, and full
# storage states until a state-specific historical art pass is needed.
for _urn_tier in URN_TIERS:
    _path = os.path.join(CRAFTED_ITEMS_FOLDER, f"{_asset_slug(_urn_tier.item_active)}.png")
    if os.path.exists(_path):
        for _item_name in (_urn_tier.item_r, _urn_tier.item_active, _urn_tier.item_full):
            CRAFTED_ITEM_IMAGES[_item_name] = _path

# The complete leather table reuses its closest existing family art until a
# later local asset pass can add item-specific sprites without a network fetch.
for _item_name, _fallback_item in {
    "Snakeskin boots": "Leather body",
    "Snakeskin vambraces": "Leather body",
    "Snakeskin bandana": "Leather body",
    "Snakeskin chaps": "Leather body",
    "Snakeskin body": "Leather body",
    "Yak-hide armour": "Leather",
    "Blue d'hide vambraces": "Blue d'hide body",
    "Blue d'hide chaps": "Blue d'hide body",
    "Red d'hide vambraces": "Black d'hide body",
    "Red d'hide chaps": "Black d'hide body",
    "Red d'hide body": "Black d'hide body",
    "Black d'hide vambraces": "Black d'hide body",
    "Black d'hide chaps": "Black d'hide body",
    "Dragon bracelet": "Dragon necklace",
    "Onyx bracelet": "Onyx necklace",
    "Earth battlestaff": "Air battlestaff",
}.items():
    _path = CRAFTED_ITEM_IMAGES.get(_fallback_item)
    if _path:
        CRAFTED_ITEM_IMAGES[_item_name] = _path

for _item_name, _fallback_path in {
    "Ring mould": os.path.join(QUEST_ITEMS_FOLDER, "ring_mould.png"),
    "Necklace mould": os.path.join(QUEST_ITEMS_FOLDER, "necklace_mould.png"),
    "Bracelet mould": os.path.join(SHOP_ITEMS_FOLDER, "bracelet_mould.png"),
    "Amulet mould": os.path.join(SHOP_ITEMS_FOLDER, "amulet_mould.png"),
    "Tiara mould": os.path.join(SHOP_ITEMS_FOLDER, "tiara_mould.png"),
    "Unholy mould": os.path.join(SHOP_ITEMS_FOLDER, "holy_mould.png"),
    "Holy mould": os.path.join(SHOP_ITEMS_FOLDER, "holy_mould.png"),
    "Sickle mould": os.path.join(SHOP_ITEMS_FOLDER, "sickle_mould.png"),
    "Demonic sigil mould": os.path.join(SHOP_ITEMS_FOLDER, "holy_mould.png"),
    "Chain link mould": os.path.join(QUEST_ITEMS_FOLDER, "necklace_mould.png"),
    "Conductor mould": os.path.join(SHOP_ITEMS_FOLDER, "amulet_mould.png"),
    "Rod clay mould": os.path.join(SHOP_ITEMS_FOLDER, "amulet_mould.png"),
    "Bolt mould": os.path.join(SHOP_ITEMS_FOLDER, "bolt_mould.png"),
    "Glassblowing pipe": os.path.join(SHOP_ITEMS_FOLDER, "glassblowing_pipe.png"),
}.items():
    if os.path.exists(_fallback_path):
        CRAFTED_ITEM_IMAGES[_item_name] = _fallback_path

_path = os.path.join(HUNTER_ITEMS_FOLDER, "small_fishing_net.png")
if os.path.exists(_path):
    CRAFTED_ITEM_IMAGES["Unfinished net"] = _path

# Combination and lantern-state outputs use their exact checked-in sprites.
for _item_name, _path in {
    "Strange skull": os.path.join(SHOP_ITEMS_FOLDER, "lizard_skull.png"),
    "Runed sceptre": os.path.join(COMBAT_ITEMS_FOLDER, "staff.png"),
    "Skull sceptre": os.path.join(COMBAT_ITEMS_FOLDER, "staff.png"),
    "Candle lantern (empty)": os.path.join(FIREMAKING_ITEMS_FOLDER, "candle_lantern_empty.png"),
    "Oil lamp (empty)": os.path.join(FIREMAKING_ITEMS_FOLDER, "oil_lamp_empty.png"),
    "Oil lantern (empty)": os.path.join(FIREMAKING_ITEMS_FOLDER, "oil_lantern_empty.png"),
    "Oil lantern (unlit)": os.path.join(FIREMAKING_ITEMS_FOLDER, "oil_lantern_unlit.png"),
    "Bullseye lantern (unf)": os.path.join(FIREMAKING_ITEMS_FOLDER, "bullseye_lantern_unf.png"),
    "Bullseye lantern (empty)": os.path.join(FIREMAKING_ITEMS_FOLDER, "bullseye_lantern_empty.png"),
    "Emerald lantern (unlit)": os.path.join(FIREMAKING_ITEMS_FOLDER, "emerald_lantern_unlit.png"),
    "Sapphire lantern (empty)": os.path.join(FIREMAKING_ITEMS_FOLDER, "sapphire_lantern_empty.png"),
    "Spiky vambraces": os.path.join(CRAFTED_ITEMS_FOLDER, "leather_vambraces.png"),
    "Green spiky vambraces": os.path.join(CRAFTED_ITEMS_FOLDER, "green_d_hide_vambraces.png"),
    "Blue spiky vambraces": os.path.join(CRAFTED_ITEMS_FOLDER, "blue_d_hide_vambraces.png"),
    "Red spiky vambraces": os.path.join(CRAFTED_ITEMS_FOLDER, "red_d_hide_vambraces.png"),
    "Black spiky vambraces": os.path.join(CRAFTED_ITEMS_FOLDER, "black_d_hide_vambraces.png"),
    "Crab helmet": os.path.join(SHOP_ITEMS_FOLDER, "lizard_skull.png"),
    "Crab claw": os.path.join(SHOP_ITEMS_FOLDER, "lizard_skull.png"),
    "Empty seaweed net": os.path.join(HUNTER_ITEMS_FOLDER, "small_fishing_net.png"),
    "Armadyl battlestaff": os.path.join(QUEST_ITEMS_FOLDER, "staff_of_armadyl.png"),
    "Unblessed symbol": os.path.join(SHOP_ITEMS_FOLDER, "holy_symbol.png"),
    "Unpowered symbol": os.path.join(SHOP_ITEMS_FOLDER, "holy_symbol.png"),
    "Polished buttons": os.path.join(COMBAT_ITEMS_FOLDER, "buttons.png"),
    "Kebbit claws": os.path.join(HUNTER_ITEMS_FOLDER, "kebbit_claws.png"),
}.items():
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
FIREMAKING_ITEM_IMAGES.update({
    "Unlit torch": os.path.join(SHOP_ITEMS_FOLDER, "unlit_torch.png"),
    "Lit torch": os.path.join(SHOP_ITEMS_FOLDER, "unlit_torch.png"),
    "Unlit bug lantern": os.path.join(SHOP_ITEMS_FOLDER, "unlit_bug_lantern.png"),
    "Lit bug lantern": os.path.join(SHOP_ITEMS_FOLDER, "lit_bug_lantern.png"),
    "Candle": os.path.join(SHOP_ITEMS_FOLDER, "candle.png"),
    "Lit candle": os.path.join(SHOP_ITEMS_FOLDER, "candle.png"),
    "Black candle": os.path.join(QUEST_ITEMS_FOLDER, "black_candle.png"),
    "Lit black candle": os.path.join(QUEST_ITEMS_FOLDER, "lit_black_candle.png"),
})
for _item_name in (
    "Candle lantern (empty)",
    "Candle lantern (unlit, 4529)",
    "Candle lantern (lit, 4531)",
    "Candle lantern (unlit, 4532)",
    "Candle lantern (lit, 4534)",
    "Oil lamp (empty)",
    "Oil lamp (unlit)",
    "Oil lamp (lit)",
    "Oil lantern (empty)",
    "Oil lantern (unlit)",
    "Oil lantern (lit)",
    "Bullseye lantern (unf)",
    "Bullseye lantern (empty)",
    "Bullseye lantern (unlit)",
    "Bullseye lantern (lit)",
    "Sapphire lantern (empty)",
    "Sapphire lantern (unlit)",
    "Sapphire lantern (lit)",
    "Emerald lantern (unlit)",
    "Emerald lantern (lit)",
    "Mining helmet (unlit)",
    "Mining helmet (lit)",
):
    FIREMAKING_ITEM_IMAGES[_item_name] = os.path.join(
        FIREMAKING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png"
    )
for _item_name in FIREMAKING_EXTRA_ITEM_DATA:
    _path = FIREMAKING_ITEM_IMAGES.get(_item_name)
    if not _path:
        _path = os.path.join(FIREMAKING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if _path and os.path.exists(_path):
        FIREMAKING_ITEM_IMAGES[_item_name] = _path
UTILITY_ITEM_IMAGES.update(FIREMAKING_ITEM_IMAGES)

FISHING_EXTRA_ITEM_DATA = fishing_extra_items_as_dict()
FISHING_ITEM_IMAGES = {}
FISHING_SHARED_ITEM_IMAGES = {
    "Raw lava eel": os.path.join(QUEST_ITEMS_FOLDER, "raw_lava_eel.png"),
    "Raw rainbow fish": os.path.join(COOKING_ITEMS_FOLDER, "raw_rainbow_fish.png"),
}
for _item_name in set(FISHING_OUTPUT_ITEMS) | set(FISHING_EXTRA_ITEM_DATA):
    _path = FISHING_SHARED_ITEM_IMAGES.get(
        _item_name,
        os.path.join(FISHING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png"),
    )
    if os.path.exists(_path):
        FISHING_ITEM_IMAGES[_item_name] = _path

HUNTER_EXTRA_ITEM_DATA = hunter_extra_items_as_dict()
HUNTER_EXTRA_ITEM_DATA.update(big_chinchompa_extra_items_as_dict())
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
COOKING_SHARED_ITEM_IMAGES = {
    "Lava eel": os.path.join(QUEST_ITEMS_FOLDER, "lava_eel.png"),
    "Bucket of milk": os.path.join(QUEST_ITEMS_FOLDER, "bucket_of_milk.png"),
    "Raw spider on stick": os.path.join(SHOP_ITEMS_FOLDER, "spider_on_stick.png"),
    "Burnt spider": os.path.join(SHOP_ITEMS_FOLDER, "spider_on_stick.png"),
    "Skewer stick": os.path.join(SHOP_ITEMS_FOLDER, "skewer.png"),
}
_COOKING_ITEM_NAMES = set(COOKING_EXTRA_ITEM_DATA)
_COOKING_ITEM_NAMES.update(COOKING_RAW_ITEMS)
_COOKING_ITEM_NAMES.update(COOKING_OUTPUT_ITEMS)
for _item_name in _COOKING_ITEM_NAMES:
    _path = (
        COOKING_SHARED_ITEM_IMAGES.get(_item_name)
        or FISHING_ITEM_IMAGES.get(_item_name)
        or CRAFTED_ITEM_IMAGES.get(_item_name)
        or ORE_IMAGES.get(_item_name)
        or BAR_IMAGES.get(_item_name)
        or next(
            (
                candidate
                for candidate in (
                    os.path.join(COOKING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png"),
                    os.path.join(SHOP_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png"),
                )
                if os.path.exists(candidate)
            ),
            None,
        )
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

# Herblore: every grimy/clean/unf herb, secondary, and finished product. Icons
# reuse cross-skill art where an item is shared (crafting/combat/cooking maps)
# and otherwise come from herbloreitems/ keyed by _asset_slug. Existence-guarded
# so an unfetched icon leaves the row text-only instead of a dead path.
HERBLORE_EXTRA_ITEM_DATA = herblore_extra_items_as_dict()
HERBLORE_ITEM_IMAGES = {}
for _item_name in (
    set(HERBLORE_OUTPUT_ITEMS)
    | set(HERBLORE_EXTRA_ITEM_DATA)
    | set(potion_item_names())
):
    _path = (
        ORE_IMAGES.get(_item_name)
        or CRAFTED_ITEM_IMAGES.get(_item_name)
        or os.path.join(HERBLORE_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    )
    if _path and os.path.exists(_path):
        HERBLORE_ITEM_IMAGES[_item_name] = _path

# Potion flasks are blown through Crafting but already have one canonical
# Herblore container sprite. Share it instead of fetching a duplicate asset.
if HERBLORE_ITEM_IMAGES.get("Potion flask"):
    CRAFTED_ITEM_IMAGES["Potion flask"] = HERBLORE_ITEM_IMAGES["Potion flask"]

URN_ITEM_DATA = urn_extra_items_as_dict()
PRAYER_PASSIVE_ITEM_DATA = prayer_passive_items_as_dict()
PRAYER_EXTRA_ITEM_DATA = {
    **prayer_extra_items_as_dict(),
    **PRAYER_PASSIVE_ITEM_DATA,
    **URN_ITEM_DATA,
}
THIEVING_EXTRA_ITEM_DATA = thieving_extra_items_as_dict()
PRAYER_ITEM_IMAGES = {}
for _item_name in PRAYER_EXTRA_ITEM_DATA:
    _path = CRAFTED_ITEM_IMAGES.get(_item_name) or os.path.join(PRAYER_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        PRAYER_ITEM_IMAGES[_item_name] = _path
UTILITY_ITEM_IMAGES.update(PRAYER_ITEM_IMAGES)

MAGIC_EXTRA_ITEM_DATA = magic_extra_items_as_dict()
MAGIC_ITEM_IMAGES = {}
for _item_name in MAGIC_EXTRA_ITEM_DATA:
    _path = (
        ORE_IMAGES.get(_item_name)
        or CRAFTED_ITEM_IMAGES.get(_item_name)
        or RUNECRAFTING_ITEM_IMAGES.get(_item_name)
        or PRAYER_ITEM_IMAGES.get(_item_name)
        or os.path.join(MAGIC_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    )
    if _path and os.path.exists(_path):
        MAGIC_ITEM_IMAGES[_item_name] = _path

MAGIC_SPELL_IMAGES = {
    _target_id: _path
    for _target_id in MAGIC_DATA
    if os.path.exists(
        _path := os.path.join(
            MAGIC_SPELLS_FOLDER,
            f"{_target_id}.png",
        )
    )
}

CONSTRUCTION_EXTRA_ITEM_DATA = construction_extra_items_as_dict()
CONSTRUCTION_ASSET_ITEM_DATA = construction_asset_items_as_dict()
CONSTRUCTION_ITEM_IMAGES = {}
for _item_name in CONSTRUCTION_ASSET_ITEM_DATA:
    _path = os.path.join(CONSTRUCTION_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        CONSTRUCTION_ITEM_IMAGES[_item_name] = _path

SUMMONING_EXTRA_ITEM_DATA = summoning_extra_items_as_dict()
SUMMONING_ITEM_IMAGES = {}
for _item_name in SUMMONING_EXTRA_ITEM_DATA:
    _path = os.path.join(
        SUMMONING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png"
    )
    if os.path.exists(_path):
        SUMMONING_ITEM_IMAGES[_item_name] = _path

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
SMITHING_EXTRA_ITEM_IMAGES["Dragon sq shield"] = SMITHING_EXTRA_ITEM_IMAGES["Rune sq shield"]
QUEST_ITEM_IMAGES = {}
QUEST_ITEM_IMAGE_FILE_OVERRIDES = {
    "Lever": "temple_lever.png",
    "Kitten": "pet_kitten.png",
    "Holy symbol (Icthlarin's Little Helper)": "holy_symbol.png",
    "Unholy symbol (Icthlarin's Little Helper)": "unholy_symbol.png",
}
for _item_name in QUEST_REWARD_ITEM_DATA:
    _path = os.path.join(
        QUEST_ITEMS_FOLDER,
        QUEST_ITEM_IMAGE_FILE_OVERRIDES.get(_item_name, f"{_asset_slug(_item_name)}.png"),
    )
    if os.path.exists(_path):
        QUEST_ITEM_IMAGES[_item_name] = _path
COMBAT_ITEM_IMAGES = {}
for _item_name in COMBAT_EXTRA_ITEM_DATA:
    _path = (
        QUEST_ITEM_IMAGES.get(_item_name)
        or SMITHING_EXTRA_ITEM_IMAGES.get(_item_name)
        or FLETCHED_ITEM_IMAGES.get(_item_name)
        or RUNECRAFTING_ITEM_IMAGES.get(_item_name)
        or MINING_EXTRA_ITEM_IMAGES.get(_item_name)
        or WOODCUTTING_EXTRA_ITEM_IMAGES.get(_item_name)
        or HUNTER_ITEM_IMAGES.get(_item_name)
        or os.path.join(COMBAT_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    )
    if _path and os.path.exists(_path):
        COMBAT_ITEM_IMAGES[_item_name] = _path
for _item_name, _path in {
    "Kebab": os.path.join(SHOP_ITEMS_FOLDER, "kebab.png"),
    "Half a summer pie": os.path.join(COOKING_ITEMS_FOLDER, "summer_pie.png"),
}.items():
    if os.path.exists(_path):
        COMBAT_ITEM_IMAGES[_item_name] = _path
_fungicide_spray_path = os.path.join(SHOP_ITEMS_FOLDER, "fungicide_spray_10.png")
if os.path.exists(_fungicide_spray_path):
    for _charges in range(11):
        COMBAT_ITEM_IMAGES[f"Fungicide spray {_charges}"] = _fungicide_spray_path
_fungicide_path = os.path.join(SHOP_ITEMS_FOLDER, "fungicide.png")
if os.path.exists(_fungicide_path):
    COMBAT_ITEM_IMAGES["Fungicide"] = _fungicide_path
COMBAT_ENEMY_IMAGES = {}
for _target_id in COMBAT_ENEMY_DATA:
    _path = os.path.join(COMBAT_ENEMIES_FOLDER, f"{_asset_slug(_target_id)}.png")
    if os.path.exists(_path):
        COMBAT_ENEMY_IMAGES[_target_id] = _path
# Goblin Raids' unnamed village goblin has no wiki image of its own, so it shows
# the art of the registered goblin row it inherits its stats from.
for _row in GOBLIN_RAID_ENEMIES:
    if _row.id not in COMBAT_ENEMY_IMAGES and _row.base in COMBAT_ENEMY_IMAGES:
        COMBAT_ENEMY_IMAGES[_row.id] = COMBAT_ENEMY_IMAGES[_row.base]
EQUIPMENT_DATA = dict(EQUIPMENT_DATA)
EQUIPMENT_DATA.update(barrows_equipment_data_as_dict())
EQUIPMENT_DATA.update(fish_flingers_equipment_data_as_dict())
EQUIPMENT_DATA.update(trouble_brewing_equipment_data_as_dict())
EQUIPMENT_DATA.update(castle_wars_equipment_data_as_dict())
EQUIPMENT_DATA.update(pest_control_equipment_data_as_dict())
EQUIPMENT_DATA.update(conquest_equipment_data_as_dict())
EQUIPMENT_DATA.update(barbarian_assault_equipment_data_as_dict())
EQUIPMENT_DATA.update(stronghold_player_safety_equipment_data_as_dict())
EQUIPMENT_DATA.update(penguin_hide_and_seek_equipment_data_as_dict())
EQUIPMENT_DATA.update(duel_arena_equipment_data_as_dict())
EQUIPMENT_DATA.update(mage_training_arena_equipment_data_as_dict())
EQUIPMENT_DATA.update(mobilising_armies_equipment_data_as_dict())
EQUIPMENT_DATA.update(dominion_tower_equipment_data_as_dict())
EQUIPMENT_DATA.update(crucible_equipment_data_as_dict())
EQUIPMENT_DATA.update(goblin_raids_equipment_data_as_dict())
EQUIPMENT_DATA.update(diary_equipment_data_as_dict())
EQUIPMENT_DATA.update(milestone_cape_equipment_data_as_dict())
EQUIPMENT_DATA.update(cape_equipment_data_as_dict())
EQUIPMENT_ITEM_DATA = equipment_items_as_dict(EQUIPMENT_DATA)
FIST_OF_GUTHIX_EXTRA_ITEM_DATA = fist_of_guthix_extra_items_as_dict()
COURT_CASES_EXTRA_ITEM_DATA = court_cases_extra_items_as_dict()
CIRCUS_EXTRA_ITEM_DATA = circus_extra_items_as_dict()
TROUBLE_BREWING_EXTRA_ITEM_DATA = trouble_brewing_extra_items_as_dict()
CASTLE_WARS_EXTRA_ITEM_DATA = castle_wars_extra_items_as_dict()
PEST_CONTROL_EXTRA_ITEM_DATA = pest_control_extra_items_as_dict()
CONQUEST_EXTRA_ITEM_DATA = conquest_extra_items_as_dict()
BARBARIAN_ASSAULT_EXTRA_ITEM_DATA = barbarian_assault_extra_items_as_dict()
STRONGHOLD_PLAYER_SAFETY_EXTRA_ITEM_DATA = (
    stronghold_player_safety_extra_items_as_dict()
)
STRONGHOLD_OF_SECURITY_EXTRA_ITEM_DATA = (
    stronghold_of_security_extra_items_as_dict()
)
SHADES_OF_MORTTON_EXTRA_ITEM_DATA = shades_of_mortton_extra_items_as_dict()
VARROCK_MUSEUM_EXTRA_ITEM_DATA = varrock_museum_extra_items_as_dict()

SHADES_OF_MORTTON_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        "shades_of_mortton_"
        + "_".join(re.findall(r"[a-z0-9]+", item_name.lower()))
        + ".png",
    )
    for item_name in SHADES_OF_MORTTON_EXTRA_ITEM_DATA
}
SHADES_OF_MORTTON_ITEM_IMAGES = {
    item_name: path
    for item_name, path in SHADES_OF_MORTTON_ITEM_IMAGES.items()
    if os.path.exists(path)
}
SORCERESS_GARDEN_EXTRA_ITEM_DATA = sorceress_garden_extra_items_as_dict()
VINESWEEPER_EXTRA_ITEM_DATA = vinesweeper_extra_items_as_dict()
FIGHT_CAVES_EXTRA_ITEM_DATA = fight_caves_extra_items_as_dict()
PHOENIX_LAIR_EXTRA_ITEM_DATA = phoenix_lair_extra_items_as_dict()
SKELETAL_HORROR_EXTRA_ITEM_DATA = skeletal_horror_extra_items_as_dict()
BORK_EXTRA_ITEM_DATA = bork_extra_items_as_dict()
TROLL_INVASION_EXTRA_ITEM_DATA = troll_invasion_extra_items_as_dict()
SHATTERED_HEART_EXTRA_ITEM_DATA = shattered_heart_extra_items_as_dict()
SHATTERED_HEART_ITEM_IMAGES = {}
for _item_name, _path in (
    (
        SHATTERED_HEART_BAG_ITEM,
        os.path.join(current_dir, "activityitems", "statue_collection_bag.png"),
    ),
    (
        SHATTERED_HEART_PLINTH_ITEM,
        os.path.join(current_dir, "activityitems", "statue_plinth.png"),
    ),
):
    if os.path.exists(_path):
        SHATTERED_HEART_ITEM_IMAGES[_item_name] = _path
for _row in SHATTERED_HEART_SKILLS:
    _rock_path = os.path.join(
        current_dir, "activityitems", f"strange_rock_{_row.id}.png"
    )
    if os.path.exists(_rock_path):
        for _item_name in _row.rock_items:
            SHATTERED_HEART_ITEM_IMAGES[_item_name] = _rock_path
    _replica_path = os.path.join(
        current_dir, "activityitems", f"replica_statue_piece_{_row.id}.png"
    )
    if os.path.exists(_replica_path):
        for _item_name in _row.replica_items:
            SHATTERED_HEART_ITEM_IMAGES[_item_name] = _replica_path
MAGE_TRAINING_ARENA_EXTRA_ITEM_DATA = mage_training_arena_extra_items_as_dict()
MAGE_TRAINING_ARENA_ITEM_IMAGES = {
    str(row["item_name"]): os.path.join(current_dir, str(row["output_path"]))
    for row in MAGE_TRAINING_ARENA_ASSET_MANIFEST
    if str(row["output_path"]).startswith("activityitems/")
}
MAGE_TRAINING_ARENA_ITEM_IMAGES = {
    item_name: path
    for item_name, path in MAGE_TRAINING_ARENA_ITEM_IMAGES.items()
    if os.path.exists(path)
}
MOBILISING_ARMIES_EXTRA_ITEM_DATA = mobilising_armies_extra_items_as_dict()
MOBILISING_ARMIES_ITEM_IMAGES = {
    str(row["item_name"]): os.path.join(current_dir, str(row["output_path"]))
    for row in MOBILISING_ARMIES_ASSET_MANIFEST
    if str(row["output_path"]).startswith("activityitems/")
}
MOBILISING_ARMIES_ITEM_IMAGES = {
    item_name: path
    for item_name, path in MOBILISING_ARMIES_ITEM_IMAGES.items()
    if os.path.exists(path)
}
GNOME_RESTAURANT_EXTRA_ITEM_DATA = gnome_restaurant_extra_items_as_dict()
GNOME_RESTAURANT_ITEM_IMAGES = {
    str(row["item_name"]): os.path.join(current_dir, str(row["output_path"]))
    for row in GNOME_RESTAURANT_ASSET_MANIFEST
    if str(row["output_path"]).startswith("activityitems/")
}
GNOME_RESTAURANT_ITEM_IMAGES = {
    item_name: path
    for item_name, path in GNOME_RESTAURANT_ITEM_IMAGES.items()
    if os.path.exists(path)
}
DOMINION_TOWER_EXTRA_ITEM_DATA = dominion_tower_extra_items_as_dict()
DOMINION_TOWER_ITEM_IMAGES = {
    str(row["item_name"]): os.path.join(current_dir, str(row["output_path"]))
    for row in DOMINION_TOWER_ASSET_MANIFEST
    if str(row["output_path"]).startswith("activityitems/")
}
DOMINION_TOWER_ITEM_IMAGES = {
    item_name: path
    for item_name, path in DOMINION_TOWER_ITEM_IMAGES.items()
    if os.path.exists(path)
}
TEMPLE_TREKKING_EXTRA_ITEM_DATA = temple_trekking_extra_items_as_dict()
TEMPLE_TREKKING_ITEM_IMAGES = {
    str(row["item_name"]): os.path.join(current_dir, str(row["output_path"]))
    for row in TEMPLE_TREKKING_ASSET_MANIFEST
    if str(row["output_path"]).startswith("activityitems/")
}
TEMPLE_TREKKING_ITEM_IMAGES = {
    item_name: path
    for item_name, path in TEMPLE_TREKKING_ITEM_IMAGES.items()
    if os.path.exists(path)
}
ENCHANTED_KEY_EXTRA_ITEM_DATA = enchanted_key_extra_items_as_dict()
ENCHANTED_KEY_ITEM_IMAGES = {
    _item_name: os.path.join(
        current_dir,
        "activityitems",
        _item_name.lower().replace(" ", "_") + ".png",
    )
    for _item_name in ENCHANTED_KEY_MJOLNIRS
}
ENCHANTED_KEY_ITEM_IMAGES = {
    _item_name: _path
    for _item_name, _path in ENCHANTED_KEY_ITEM_IMAGES.items()
    if os.path.exists(_path)
}
STEALING_CREATION_EXTRA_ITEM_DATA = stealing_creation_extra_items_as_dict()
BARROWS_EXTRA_ITEM_DATA = barrows_extra_items_as_dict()
FLASH_POWDER_FACTORY_EXTRA_ITEM_DATA = flash_powder_factory_extra_items_as_dict()
PYRAMID_PLUNDER_EXTRA_ITEM_DATA = pyramid_plunder_extra_items_as_dict()
WEREWOLF_SKULLBALL_EXTRA_ITEM_DATA = werewolf_skullball_extra_items_as_dict()
GNOME_BALL_EXTRA_ITEM_DATA = gnome_ball_extra_items_as_dict()
FISH_FLINGERS_EXTRA_ITEM_DATA = fish_flingers_extra_items_as_dict()
DUEL_ARENA_EXTRA_ITEM_DATA = duel_arena_extra_items_as_dict()
CRUCIBLE_EXTRA_ITEM_DATA = crucible_extra_items_as_dict()
GOBLIN_RAIDS_EXTRA_ITEM_DATA = goblin_raids_extra_items_as_dict()
DAILY_CHALLENGE_EXTRA_ITEM_DATA = daily_challenge_extra_items_as_dict()
TREASURE_TRAILS_EXTRA_ITEM_DATA = treasure_trails_extra_items_as_dict()
DUNGEONEERING_EXTRA_ITEM_DATA = dungeoneering_extra_items_as_dict()
COURT_CASES_ITEM_IMAGES = {
    "Court summons": os.path.join(
        UTILITY_ACTIVITY_ICONS_FOLDER,
        "court_cases.png",
    ),
    "Rainbow afro": os.path.join(
        current_dir,
        "activityitems",
        "rainbow_afro.png",
    ),
}
COURT_CASES_ITEM_IMAGES = {
    item_name: path
    for item_name, path in COURT_CASES_ITEM_IMAGES.items()
    if os.path.exists(path)
}
CIRCUS_ITEM_IMAGES = {
    "Giant's hand": os.path.join(current_dir, "activityitems", "giants_hand.png"),
    "Acrobat hood": os.path.join(current_dir, "activityitems", "acrobat_hood.png"),
    "Firemaker's tabard": os.path.join(current_dir, "activityitems", "firemakers_tabard.png"),
    "Clown hat": os.path.join(current_dir, "activityitems", "clown_hat.png"),
    "Ringmaster hat": os.path.join(current_dir, "activityitems", "ringmaster_hat.png"),
}
CIRCUS_ITEM_IMAGES = {
    item_name: path
    for item_name, path in CIRCUS_ITEM_IMAGES.items()
    if os.path.exists(path)
}
TROUBLE_BREWING_ITEM_IMAGES = {
    "Blue tricorn hat": os.path.join(
        current_dir,
        "activityitems",
        "blue_tricorn_hat.png",
    ),
}
TROUBLE_BREWING_ITEM_IMAGES = {
    item_name: path
    for item_name, path in TROUBLE_BREWING_ITEM_IMAGES.items()
    if os.path.exists(path)
}
CASTLE_WARS_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"castle_wars_{_asset_slug(item_name)}.png",
    )
    for item_name in CASTLE_WARS_EXTRA_ITEM_DATA
}
CASTLE_WARS_ITEM_IMAGES = {
    item_name: path
    for item_name, path in CASTLE_WARS_ITEM_IMAGES.items()
    if os.path.exists(path)
}
PEST_CONTROL_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"pest_control_{_asset_slug(item_name)}.png",
    )
    for item_name in PEST_CONTROL_EXTRA_ITEM_DATA
}
CONQUEST_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"conquest_{_asset_slug(item_name)}.png",
    )
    for item_name in CONQUEST_EXTRA_ITEM_DATA
}
CONQUEST_ITEM_IMAGES = {
    item_name: path
    for item_name, path in CONQUEST_ITEM_IMAGES.items()
    if os.path.exists(path)
}
PEST_CONTROL_ITEM_IMAGES = {
    item_name: path
    for item_name, path in PEST_CONTROL_ITEM_IMAGES.items()
    if os.path.exists(path)
}
BARBARIAN_ASSAULT_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"barbarian_assault_{_asset_slug(item_name)}.png",
    )
    for item_name in BARBARIAN_ASSAULT_EXTRA_ITEM_DATA
}
BARBARIAN_ASSAULT_ITEM_IMAGES = {
    item_name: path
    for item_name, path in BARBARIAN_ASSAULT_ITEM_IMAGES.items()
    if os.path.exists(path)
}
STRONGHOLD_PLAYER_SAFETY_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"stronghold_player_safety_{_asset_slug(item_name)}.png",
    )
    for item_name in STRONGHOLD_PLAYER_SAFETY_EXTRA_ITEM_DATA
}
STRONGHOLD_PLAYER_SAFETY_ITEM_IMAGES = {
    item_name: path
    for item_name, path in STRONGHOLD_PLAYER_SAFETY_ITEM_IMAGES.items()
    if os.path.exists(path)
}
# The two Stronghold of Security boots have no art on disk yet, so this map is
# empty and the items stay iconless-but-registered until the sprites are fetched.
STRONGHOLD_OF_SECURITY_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"stronghold_of_security_{_asset_slug(item_name)}.png",
    )
    for item_name in STRONGHOLD_OF_SECURITY_EXTRA_ITEM_DATA
}
STRONGHOLD_OF_SECURITY_ITEM_IMAGES = {
    item_name: path
    for item_name, path in STRONGHOLD_OF_SECURITY_ITEM_IMAGES.items()
    if os.path.exists(path)
}
VARROCK_MUSEUM_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"varrock_museum_{_asset_slug(item_name)}.png",
    )
    for item_name in VARROCK_MUSEUM_EXTRA_ITEM_DATA
}
VARROCK_MUSEUM_ITEM_IMAGES = {
    item_name: path
    for item_name, path in VARROCK_MUSEUM_ITEM_IMAGES.items()
    if os.path.exists(path)
}
FISH_FLINGERS_ITEM_IMAGES = {}
for _item_name in FISH_FLINGERS_EXTRA_ITEM_DATA:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        FISH_FLINGERS_ITEM_IMAGES[_item_name] = _path
DUEL_ARENA_ITEM_IMAGES = {
    tier.item_name: os.path.join(current_dir, "activityitems", tier.asset_filename)
    for tier in DUELLISTS_CAP_TIERS
}
DUEL_ARENA_ITEM_IMAGES = {
    item_name: path
    for item_name, path in DUEL_ARENA_ITEM_IMAGES.items()
    if os.path.exists(path)
}
UTILITY_ITEM_IMAGES.update(DUEL_ARENA_ITEM_IMAGES)
TREASURE_TRAILS_ITEM_IMAGES = {}
for _item_name in TREASURE_TRAILS_ART_ITEMS:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        TREASURE_TRAILS_ITEM_IMAGES[_item_name] = _path
DAILY_CHALLENGE_ITEM_IMAGES = {}
for _item_name in DAILY_CHALLENGE_EXTRA_ITEM_DATA:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        DAILY_CHALLENGE_ITEM_IMAGES[_item_name] = _path
VINESWEEPER_ITEM_IMAGES = {}
for _item_name in VINESWEEPER_EXTRA_ITEM_DATA:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        VINESWEEPER_ITEM_IMAGES[_item_name] = _path
FIGHT_CAVES_ITEM_IMAGES = {
    "Fire cape": os.path.join(current_dir, "constructionitems", "fire_cape.png"),
    "Tokkul": os.path.join(current_dir, "combatitems", "tokkul.png"),
}
PHOENIX_LAIR_ITEM_IMAGES = {
    item_name: os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(item_name)}.png",
    )
    for item_name in PHOENIX_LAIR_EXTRA_ITEM_DATA
}
_phoenix_quill_activity_path = os.path.join(
    current_dir, "activityitems", "phoenix_quill.png"
)
if os.path.exists(_phoenix_quill_activity_path):
    PHOENIX_LAIR_ITEM_IMAGES["Phoenix quill"] = _phoenix_quill_activity_path
PHOENIX_LAIR_ITEM_IMAGES = {
    item_name: path
    for item_name, path in PHOENIX_LAIR_ITEM_IMAGES.items()
    if os.path.exists(path)
}
SKELETAL_HORROR_ITEM_IMAGES = {
    "Clue scroll (elite)": os.path.join(
        current_dir, "combatitems", "clue_scroll_elite.png"
    ),
}
SKELETAL_HORROR_ITEM_IMAGES = {
    item_name: path
    for item_name, path in SKELETAL_HORROR_ITEM_IMAGES.items()
    if os.path.exists(path)
}
TROLL_INVASION_ITEM_IMAGES = {
    TROLL_INVASION_REWARD_BOOK: os.path.join(
        current_dir, "activityitems", "troll_invasion_reward_book.png"
    )
}
TROLL_INVASION_ITEM_IMAGES = {
    item_name: path
    for item_name, path in TROLL_INVASION_ITEM_IMAGES.items()
    if os.path.exists(path)
}
STEALING_CREATION_ITEM_IMAGES = {}
for _item_name in STEALING_CREATION_EXTRA_ITEM_DATA:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        STEALING_CREATION_ITEM_IMAGES[_item_name] = _path
BARROWS_ITEM_IMAGES = {}
for _item_name in BARROWS_EXTRA_ITEM_DATA:
    _base_name = re.sub(r" (?:100|75|50|25|0)$", "", _item_name)
    _path = os.path.join(COMBAT_ITEMS_FOLDER, f"{_asset_slug(_base_name)}.png")
    if os.path.exists(_path):
        BARROWS_ITEM_IMAGES[_item_name] = _path
FIGHT_CAVES_ITEM_IMAGES = {
    item_name: path
    for item_name, path in FIGHT_CAVES_ITEM_IMAGES.items()
    if os.path.exists(path)
}
SORCERESS_GARDEN_ITEM_IMAGES = {}
for _item_name in SORCERESS_GARDEN_EXTRA_ITEM_DATA:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        SORCERESS_GARDEN_ITEM_IMAGES[_item_name] = _path
PYRAMID_PLUNDER_ITEM_IMAGES = {}
for _item_name in PYRAMID_PLUNDER_EXTRA_ITEM_DATA:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        PYRAMID_PLUNDER_ITEM_IMAGES[_item_name] = _path
WEREWOLF_SKULLBALL_ITEM_IMAGES = {}
for _item_name in WEREWOLF_SKULLBALL_EXTRA_ITEM_DATA:
    _path = os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    if os.path.exists(_path):
        WEREWOLF_SKULLBALL_ITEM_IMAGES[_item_name] = _path
for _item_name, _file_name in {
    **{
        f"Combat hood {_percent}": "combat_hood.png"
        for _percent in (100, 80, 60, 40, 20, 0)
    },
    "Bronze gauntlets": "bronze_gauntlets.png",
    "Worn-out bronze gauntlets": "bronze_gauntlets.png",
    "Fist of guthix token": "fist_of_guthix.png",
}.items():
    _folder = (
        UTILITY_ACTIVITY_ICONS_FOLDER
        if _item_name == "Fist of guthix token"
        else COMBAT_ITEMS_FOLDER
    )
    _path = os.path.join(_folder, _file_name)
    if os.path.exists(_path):
        COMBAT_ITEM_IMAGES[_item_name] = _path
SHOP_EXTRA_ITEM_DATA = shop_extra_items_as_dict()
SHOP_ITEM_IMAGES = {}
for _item_name in SHOP_EXTRA_ITEM_DATA:
    _path = os.path.join(SHOP_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        SHOP_ITEM_IMAGES[_item_name] = _path

# Farming owns a broad cross-skill inventory surface. Reuse already-audited art
# first, then fill Farming-only rows from the data-derived farmingitems manifest.
_FARMING_SHARED_IMAGE_MAPS = (
    ORE_IMAGES,
    TREE_IMAGES,
    LOG_IMAGES,
    GEM_IMAGES,
    BAR_IMAGES,
    CRAFTED_ITEM_IMAGES,
    FLETCHED_ITEM_IMAGES,
    FIREMAKING_ITEM_IMAGES,
    FISHING_ITEM_IMAGES,
    HUNTER_ITEM_IMAGES,
    COOKING_ITEM_IMAGES,
    RUNECRAFTING_ITEM_IMAGES,
    HERBLORE_ITEM_IMAGES,
    PRAYER_ITEM_IMAGES,
    MAGIC_ITEM_IMAGES,
    CONSTRUCTION_ITEM_IMAGES,
    UTILITY_ITEM_IMAGES,
    QUEST_ITEM_IMAGES,
    COMBAT_ITEM_IMAGES,
    SHOP_ITEM_IMAGES,
    WOODCUTTING_EXTRA_ITEM_IMAGES,
    MINING_EXTRA_ITEM_IMAGES,
    SMITHING_EXTRA_ITEM_IMAGES,
)
FARMING_ITEM_IMAGES = {}
for _item_name in FARMING_ITEM_DATA:
    _path = next(
        (
            _image_map[_item_name]
            for _image_map in _FARMING_SHARED_IMAGE_MAPS
            if _image_map.get(_item_name) and os.path.exists(_image_map[_item_name])
        ),
        os.path.join(FARMING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png"),
    )
    if os.path.exists(_path):
        FARMING_ITEM_IMAGES[_item_name] = _path

_path = os.path.join(SHOP_ITEMS_FOLDER, "iron_limbs.png")
if os.path.exists(_path):
    SMITHING_EXTRA_ITEM_IMAGES["Iron limbs"] = _path

# Crossbow assembly consumes Crafting and Smithing outputs, while its unstrung
# intermediates share the finished crossbow art already checked into shopitems/.
# No assets are fetched for this parity pass.
for _item_name in (
    "Crossbow string",
    "Bronze limbs",
    "Blurite limbs",
    "Iron limbs",
    "Steel limbs",
    "Mithril limbs",
    "Adamantite limbs",
    "Runite limbs",
):
    _path = (
        CRAFTED_ITEM_IMAGES.get(_item_name)
        or SMITHING_EXTRA_ITEM_IMAGES.get(_item_name)
        or os.path.join(SHOP_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    )
    if not os.path.exists(_path):
        continue
    if _path:
        FLETCHED_ITEM_IMAGES[_item_name] = _path
for _item_name, _finished_item in {
    "Bronze crossbow": "Bronze crossbow",
    "Bronze c'bow (u)": "Bronze crossbow",
    "Iron crossbow": "Iron crossbow",
    "Blurite c'bow (u)": "Bronze crossbow",
    "Iron c'bow (u)": "Iron crossbow",
    "Steel crossbow": "Steel crossbow",
    "Steel c'bow (u)": "Steel crossbow",
    "Mith crossbow": "Mith crossbow",
    "Mithril c'bow (u)": "Mith crossbow",
    "Adamant crossbow": "Adamant crossbow",
    "Adamant c'bow (u)": "Adamant crossbow",
    "Rune crossbow": "Rune crossbow",
    "Runite c'bow (u)": "Rune crossbow",
    "Blurite crossbow": "Bronze crossbow",
}.items():
    _path = SHOP_ITEM_IMAGES.get(_finished_item) or os.path.join(
        SHOP_ITEMS_FOLDER,
        f"{_asset_slug(_finished_item)}.png",
    )
    if not os.path.exists(_path):
        continue
    if _path:
        FLETCHED_ITEM_IMAGES[_item_name] = _path

# Pestle-and-mortar grinding and Herblore input preparation route their
# inputs/outputs through the utility-material registration, so surface any icon
# we already resolved elsewhere — shop stock, combat drops, herblore art — into
# UTILITY_ITEM_IMAGES rather than leave those rows iconless.
_grind_image_sources = (
    HERBLORE_ITEM_IMAGES,
    SUMMONING_ITEM_IMAGES,
    SHOP_ITEM_IMAGES,
    COMBAT_ITEM_IMAGES,
    HUNTER_ITEM_IMAGES,
    WOODCUTTING_EXTRA_ITEM_IMAGES,
    RUNECRAFTING_ITEM_IMAGES,
)
# These Utility rows key their icon off the output item. Surface any icon already
# resolved elsewhere for their inputs/outputs, then fall back the output to an
# input icon and finally to the generic material-processing icon.
_GRIND_FALLBACK_ICON = os.path.join(UTILITY_ACTIVITY_ICONS_FOLDER, "make_soft_clay.png")
for _spec in UTILITY_ACTIVITY_DATA.values():
    if _spec.get("group") not in {"grinding", "input_preparation"}:
        continue
    _requirements = list(_spec.get("requirements", {}))
    _output = _spec.get("output_item")
    _grind_items = _requirements + ([_output] if isinstance(_output, str) else [])
    for _item_name in _grind_items:
        if _item_name in UTILITY_ITEM_IMAGES:
            continue
        for _source_map in _grind_image_sources:
            _path = _source_map.get(_item_name)
            if _path and os.path.exists(_path):
                UTILITY_ITEM_IMAGES[_item_name] = _path
                break
    if isinstance(_output, str) and _output not in UTILITY_ITEM_IMAGES:
        _fallback = next(
            (UTILITY_ITEM_IMAGES[_item] for _item in _requirements if UTILITY_ITEM_IMAGES.get(_item)),
            None,
        )
        UTILITY_ITEM_IMAGES[_output] = _fallback or _GRIND_FALLBACK_ICON


def _known_non_shop_item_names():
    names = set()
    for mapping in (
        QUEST_REWARD_ITEM_DATA,
        WOODCUTTING_EXTRA_ITEM_DATA,
        MINING_EXTRA_ITEM_DATA,
        SMITHING_EXTRA_ITEM_DATA,
        FIREMAKING_EXTRA_ITEM_DATA,
        FISHING_EXTRA_ITEM_DATA,
        HUNTER_EXTRA_ITEM_DATA,
        COOKING_EXTRA_ITEM_DATA,
        CRAFTING_REQUIRED_ITEM_DATA,
        CRAFTING_SPECIAL_ITEM_DATA,
        RUNECRAFTING_EXTRA_ITEM_DATA,
        HERBLORE_EXTRA_ITEM_DATA,
        COMBAT_EXTRA_ITEM_DATA,
        CONSTRUCTION_EXTRA_ITEM_DATA,
        FARMING_ITEM_DATA,
        THIEVING_EXTRA_ITEM_DATA,
        FISH_FLINGERS_EXTRA_ITEM_DATA,
        DUEL_ARENA_EXTRA_ITEM_DATA,
        CRUCIBLE_EXTRA_ITEM_DATA,
        GOBLIN_RAIDS_EXTRA_ITEM_DATA,
        SHADES_OF_MORTTON_EXTRA_ITEM_DATA,
    ):
        names.update(mapping)
    names.update(MINING_OUTPUT_ITEMS)
    names.update(WOODCUTTING_LOG_ITEMS)
    names.update(FIREMAKING_LOG_ITEMS)
    names.update(FIREMAKING_OUTPUT_ITEMS)
    names.update(BAR_DATA)
    names.update(GEM_DATA)
    names.update(FISHING_OUTPUT_ITEMS)
    names.update(COOKING_OUTPUT_ITEMS)
    names.update(RUNECRAFTING_OUTPUT_ITEMS)
    names.update(RUNECRAFTING_ACCESS_ITEMS)
    names.update(HERBLORE_OUTPUT_ITEMS)
    names.update(HUNTER_OUTPUT_ITEMS)
    for spec in CRAFTING_DATA.values():
        if isinstance(spec.get("output_item"), str):
            names.add(spec["output_item"])
        names.update(spec.get("requirements", {}))
    for spec in FLETCHING_DATA.values():
        if isinstance(spec.get("output_item"), str):
            names.add(spec["output_item"])
        names.update(spec.get("requirements", {}))
    for spec in HUNTER_DATA.values():
        names.update(spec.get("requirements", {}))
    for spec in UTILITY_ACTIVITY_DATA.values():
        if isinstance(spec.get("output_item"), str):
            names.add(spec["output_item"])
        outputs = spec.get("outputs", {})
        if isinstance(outputs, dict):
            names.update(outputs)
        names.update(spec.get("requirements", {}))
    return names


def _extra_item_category(spec):
    category = spec.get("category", "material")
    if category in {
        "ore",
        "log",
        "fish",
        "food",
        "gem",
        "bar",
        "crafted",
        "fletched",
        "hunter",
        "runecrafting",
        "material",
        "tool",
        "equipment",
        "smithed",
    }:
        return category
    return "material"


def _known_non_shop_item_ids(names):
    ids = {slugify_item_id("material", name) for name in names}
    for mapping in (
        QUEST_REWARD_ITEM_DATA,
        WOODCUTTING_EXTRA_ITEM_DATA,
        MINING_EXTRA_ITEM_DATA,
        SMITHING_EXTRA_ITEM_DATA,
        FIREMAKING_EXTRA_ITEM_DATA,
        FISHING_EXTRA_ITEM_DATA,
        HUNTER_EXTRA_ITEM_DATA,
        COOKING_EXTRA_ITEM_DATA,
        CRAFTING_REQUIRED_ITEM_DATA,
        CRAFTING_SPECIAL_ITEM_DATA,
        RUNECRAFTING_EXTRA_ITEM_DATA,
        HERBLORE_EXTRA_ITEM_DATA,
        COMBAT_EXTRA_ITEM_DATA,
        CONSTRUCTION_EXTRA_ITEM_DATA,
        THIEVING_EXTRA_ITEM_DATA,
        FARMING_ITEM_DATA,
        FISH_FLINGERS_EXTRA_ITEM_DATA,
    ):
        for item_name, spec in mapping.items():
            ids.add(slugify_item_id(_extra_item_category(spec), item_name))
    return ids


_KNOWN_NON_SHOP_ITEM_NAMES = _known_non_shop_item_names()
_KNOWN_NON_SHOP_ITEM_IDS = _known_non_shop_item_ids(_KNOWN_NON_SHOP_ITEM_NAMES)
SHOP_ONLY_EXTRA_ITEM_DATA = {
    item_name: spec
    for item_name, spec in SHOP_EXTRA_ITEM_DATA.items()
    if item_name not in _KNOWN_NON_SHOP_ITEM_NAMES
    and slugify_item_id(_extra_item_category(spec), item_name) not in _KNOWN_NON_SHOP_ITEM_IDS
}


def _apply_equipment_metadata(extra_item_data):
    enriched = {item_name: dict(spec) for item_name, spec in extra_item_data.items()}
    for item_name, equipment_spec in EQUIPMENT_ITEM_DATA.items():
        if item_name not in enriched:
            continue
        if enriched[item_name].get("category", "material") == "material":
            enriched[item_name]["category"] = "equipment"
        enriched[item_name]["equipment_slot"] = equipment_spec["slot"]
        enriched[item_name]["equipment_type"] = equipment_spec["equipment_type"]
        enriched[item_name]["equipment_required_level"] = equipment_spec["required_level"]
        enriched[item_name]["equipment_combat_skill"] = equipment_spec["combat_skill"]
        # ItemDefinition already has a generic equipment_tier field; for smithed
        # gear this stores combat equipment requirement, while Mining bonus gear
        # keeps its Varrock/glory-specific tier from mining_data.
        enriched[item_name].setdefault("tier", equipment_spec["required_level"])
    return enriched


_QUEST_MERGED_EXTRA_ITEM_DATA = {
    **SUMMONING_EXTRA_ITEM_DATA,
    **THIEVING_EXTRA_ITEM_DATA,
    **AGILITY_EXTRA_ITEM_DATA,
    **CONSTRUCTION_EXTRA_ITEM_DATA,
    **MAGIC_EXTRA_ITEM_DATA,
}
for _item_name, _quest_spec in QUEST_REWARD_ITEM_DATA.items():
    # Quest catalog rows often carry only a category and provenance. Overlay
    # those fields without erasing an owning system's item identity metadata.
    _QUEST_MERGED_EXTRA_ITEM_DATA.setdefault(_item_name, {}).update(
        _quest_spec
    )

EXTRA_ITEM_DATA = _apply_equipment_metadata({
    **_QUEST_MERGED_EXTRA_ITEM_DATA,
    **FARMING_ITEM_DATA,
    **WOODCUTTING_EXTRA_ITEM_DATA,
    **MINING_EXTRA_ITEM_DATA,
    **SMITHING_EXTRA_ITEM_DATA,
    **FIREMAKING_EXTRA_ITEM_DATA,
    **FISHING_EXTRA_ITEM_DATA,
    **HUNTER_EXTRA_ITEM_DATA,
    **COOKING_EXTRA_ITEM_DATA,
    **CRAFTING_REQUIRED_ITEM_DATA,
    **CRAFTING_SPECIAL_ITEM_DATA,
    **RUNECRAFTING_EXTRA_ITEM_DATA,
    **HERBLORE_EXTRA_ITEM_DATA,
    **PRAYER_EXTRA_ITEM_DATA,
    **COMBAT_EXTRA_ITEM_DATA,
    **FIST_OF_GUTHIX_EXTRA_ITEM_DATA,
    **COURT_CASES_EXTRA_ITEM_DATA,
    **CIRCUS_EXTRA_ITEM_DATA,
    **TROUBLE_BREWING_EXTRA_ITEM_DATA,
    **CASTLE_WARS_EXTRA_ITEM_DATA,
    **PEST_CONTROL_EXTRA_ITEM_DATA,
    **CONQUEST_EXTRA_ITEM_DATA,
    **BARBARIAN_ASSAULT_EXTRA_ITEM_DATA,
    **STRONGHOLD_PLAYER_SAFETY_EXTRA_ITEM_DATA,
    **STRONGHOLD_OF_SECURITY_EXTRA_ITEM_DATA,
    **SHADES_OF_MORTTON_EXTRA_ITEM_DATA,
    **VARROCK_MUSEUM_EXTRA_ITEM_DATA,
    **SORCERESS_GARDEN_EXTRA_ITEM_DATA,
    **VINESWEEPER_EXTRA_ITEM_DATA,
    **FIGHT_CAVES_EXTRA_ITEM_DATA,
    **PHOENIX_LAIR_EXTRA_ITEM_DATA,
    **SKELETAL_HORROR_EXTRA_ITEM_DATA,
    **BORK_EXTRA_ITEM_DATA,
    **TROLL_INVASION_EXTRA_ITEM_DATA,
    **SHATTERED_HEART_EXTRA_ITEM_DATA,
    **MAGE_TRAINING_ARENA_EXTRA_ITEM_DATA,
    **TEMPLE_TREKKING_EXTRA_ITEM_DATA,
    **MOBILISING_ARMIES_EXTRA_ITEM_DATA,
    **GNOME_RESTAURANT_EXTRA_ITEM_DATA,
    **DOMINION_TOWER_EXTRA_ITEM_DATA,
    **ENCHANTED_KEY_EXTRA_ITEM_DATA,
    **STEALING_CREATION_EXTRA_ITEM_DATA,
    **BARROWS_EXTRA_ITEM_DATA,
    **FLASH_POWDER_FACTORY_EXTRA_ITEM_DATA,
    **PYRAMID_PLUNDER_EXTRA_ITEM_DATA,
    **WEREWOLF_SKULLBALL_EXTRA_ITEM_DATA,
    **GNOME_BALL_EXTRA_ITEM_DATA,
    **FISH_FLINGERS_EXTRA_ITEM_DATA,
    **DUEL_ARENA_EXTRA_ITEM_DATA,
    **CRUCIBLE_EXTRA_ITEM_DATA,
    **GOBLIN_RAIDS_EXTRA_ITEM_DATA,
    **DAILY_CHALLENGE_EXTRA_ITEM_DATA,
    **TREASURE_TRAILS_EXTRA_ITEM_DATA,
    **DUNGEONEERING_EXTRA_ITEM_DATA,
    **potion_items_as_dict(),
    **SHOP_ONLY_EXTRA_ITEM_DATA,
})
EXTRA_ITEM_IMAGES = {
    **SUMMONING_ITEM_IMAGES,
    **CONSTRUCTION_ITEM_IMAGES,
    **AGILITY_ITEM_IMAGES,
    **FARMING_ITEM_IMAGES,
    **WOODCUTTING_EXTRA_ITEM_IMAGES,
    **MINING_EXTRA_ITEM_IMAGES,
    **SMITHING_EXTRA_ITEM_IMAGES,
    **FIREMAKING_ITEM_IMAGES,
    **FISHING_ITEM_IMAGES,
    **HUNTER_ITEM_IMAGES,
    **COOKING_ITEM_IMAGES,
    **CRAFTED_ITEM_IMAGES,
    **RUNECRAFTING_ITEM_IMAGES,
    **HERBLORE_ITEM_IMAGES,
    **PRAYER_ITEM_IMAGES,
    **MAGIC_ITEM_IMAGES,
    **UTILITY_ITEM_IMAGES,
    **QUEST_ITEM_IMAGES,
    **COMBAT_ITEM_IMAGES,
    **COURT_CASES_ITEM_IMAGES,
    **CIRCUS_ITEM_IMAGES,
    **TROUBLE_BREWING_ITEM_IMAGES,
    **CASTLE_WARS_ITEM_IMAGES,
    **PEST_CONTROL_ITEM_IMAGES,
    **CONQUEST_ITEM_IMAGES,
    **BARBARIAN_ASSAULT_ITEM_IMAGES,
    **STRONGHOLD_PLAYER_SAFETY_ITEM_IMAGES,
    **STRONGHOLD_OF_SECURITY_ITEM_IMAGES,
    **SHADES_OF_MORTTON_ITEM_IMAGES,
    **VARROCK_MUSEUM_ITEM_IMAGES,
    **SORCERESS_GARDEN_ITEM_IMAGES,
    **VINESWEEPER_ITEM_IMAGES,
    **FIGHT_CAVES_ITEM_IMAGES,
    **PHOENIX_LAIR_ITEM_IMAGES,
    **SKELETAL_HORROR_ITEM_IMAGES,
    **TROLL_INVASION_ITEM_IMAGES,
    **SHATTERED_HEART_ITEM_IMAGES,
    **MAGE_TRAINING_ARENA_ITEM_IMAGES,
    **TEMPLE_TREKKING_ITEM_IMAGES,
    **MOBILISING_ARMIES_ITEM_IMAGES,
    **GNOME_RESTAURANT_ITEM_IMAGES,
    **DOMINION_TOWER_ITEM_IMAGES,
    **ENCHANTED_KEY_ITEM_IMAGES,
    **STEALING_CREATION_ITEM_IMAGES,
    **BARROWS_ITEM_IMAGES,
    **PYRAMID_PLUNDER_ITEM_IMAGES,
    **WEREWOLF_SKULLBALL_ITEM_IMAGES,
    **FISH_FLINGERS_ITEM_IMAGES,
    **DAILY_CHALLENGE_ITEM_IMAGES,
    **TREASURE_TRAILS_ITEM_IMAGES,
    **DUNGEONEERING_ITEM_IMAGES,
    **SHOP_ITEM_IMAGES,
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
    # Glassmaking inputs (Soda ash, Bucket of sand) are Crafting materials
    # whose art was fetched as shop stock; merge so their registration keeps
    # an asset. Crafted art wins on collisions.
    {**SHOP_ITEM_IMAGES, **CRAFTED_ITEM_IMAGES},
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
ITEM_DEFINITIONS = apply_item_asset_overrides(
    ITEM_DEFINITIONS,
    FARMING_ITEM_IMAGES,
    only_missing=True,
)
FARMING_ITEM_IMAGES = {
    _definition.storage_key: _definition.asset_path
    for _definition in ITEM_DEFINITIONS
    if _definition.storage_key in FARMING_ITEM_DATA and _definition.asset_path
}
FARMING_PATCH_STATE_IMAGES = {
    _status: FARMING_ITEM_IMAGES[_item_name]
    for _status, _item_name in FARMING_PATCH_VISUAL_ITEMS.items()
    if FARMING_ITEM_IMAGES.get(_item_name)
}
FARMING_COMPOST_STATE_IMAGES = {
    _status: FARMING_ITEM_IMAGES[_item_name]
    for _status, _item_name in FARMING_COMPOST_VISUAL_ITEMS.items()
    if FARMING_ITEM_IMAGES.get(_item_name)
}
FARMING_HUD_SPROUT_ICON = FARMING_ITEM_IMAGES.get(
    "Oak seedling",
    FARMING_HUD_SPROUT_ICON,
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

CONSTITUTION_STARTING_LEVEL = 10
CONSTITUTION_STARTING_EXP = EXP_TABLE[CONSTITUTION_STARTING_LEVEL - 1]

# Dungeoneering continues the standard period curve through level 120.
# Source: RuneScape Wiki Dungeoneering oldid=6579699, pinned in
# data/dungeoneering_data.py SOURCE_REVISIONS.
DUNGEONEERING_EXP_TABLE = EXP_TABLE + [
    14391160,
    15889109,
    17542976,
    19368992,
    21385073,
    23611006,
    26068632,
    28782069,
    31777943,
    35085654,
    38737661,
    42769801,
    47221641,
    52136869,
    57563718,
    63555443,
    70170840,
    77474828,
    85539082,
    94442737,
    104273167,
]


def exp_table_for_skill(skill_id):
    return (
        DUNGEONEERING_EXP_TABLE
        if str(skill_id).strip().lower() == "dungeoneering"
        else EXP_TABLE
    )

# Achievement metadata
ACHIEVEMENT_DEFINITIONS = build_achievement_definitions(
    MINING_OUTPUT_ITEMS,
    WOODCUTTING_LOG_ITEMS,
    GEM_DATA,
    RUNECRAFTING_RUNE_OUTPUT_ITEMS,
    BAR_DATA,
    FISHING_OUTPUT_ITEMS,
    HERBLORE_FINISHED_OUTPUT_ITEMS,
    (
        target.activity_kind
        for target in AGILITY_TARGETS_BY_ID.values()
        if target.activity_kind
    ),
)
ACHIEVEMENTS = achievements_as_dict(ACHIEVEMENT_DEFINITIONS)
