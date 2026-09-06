import os

from ...data.quest_data import (
    BLUE_DYE_WIKI_SOURCE,
    BLUE_GOBLIN_MAIL_WIKI_SOURCE,
    GERTRUDES_CAT_WIKI_SOURCE,
    GOBLIN_DIPLOMACY_WIKI_SOURCE,
    GOBLIN_MAIL_WIKI_SOURCE,
    ORANGE_DYE_WIKI_SOURCE,
    ORANGE_GOBLIN_MAIL_WIKI_SOURCE,
)

from .skill_sources import *
from .competitive_minigame_sources import *
from .combat_minigame_sources import *
from .skill_minigame_sources import *
from .distraction_sources import *
from .landmark_and_boss_sources import *
from .utility_sources import *
from .equipment_sources import *
from .registry_sources import *
from .paths import *

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
    "gather_blue_dragon_scales": {
        "display_name": "Gather blue dragon scales",
        "requirements": {},
        "output_item": "Blue dragon scale",
        "output_qty": 1,
        "batch_size": 7,
        "icon_path": os.path.join(HERBLORE_ITEMS_FOLDER, "blue_dragon_scale.png"),
        "group": "gathering",
        "source": "https://runescape.wiki/w/Blue_dragon_scale?oldid=6169064",
    },
    "gather_potato_cacti": {
        "display_name": "Gather potato cacti",
        "requirements": {},
        "output_item": "Potato cactus",
        "output_qty": 1,
        "batch_size": 3,
        "icon_path": os.path.join(SUMMONING_ITEMS_FOLDER, "potato_cactus.png"),
        "group": "gathering",
        "source": (
            "https://runescape.wiki/w/Potato_cactus?oldid=6543078; "
            "https://runescape.wiki/w/Kalphite_Hive?oldid=6529999"
        ),
    },
    "gather_black_mushrooms": {
        "display_name": "Gather black mushrooms",
        "requirements": {},
        "output_item": "Black mushroom",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(HERBLORE_ITEMS_FOLDER, "black_mushroom.png"),
        "group": "gathering",
        "source": "https://runescape.wiki/w/Black_mushroom?oldid=5513228",
    },
    "gather_doogle_leaves": {
        "display_name": "Gather Doogle leaves",
        "requirements": {},
        "output_item": "Doogle leaves",
        "output_qty": 1,
        "batch_size": 2,
        "icon_path": os.path.join(QUEST_ITEMS_FOLDER, "doogle_leaves.png"),
        "group": "gathering",
        "source": GERTRUDES_CAT_WIKI_SOURCE,
    },
    "gather_goblin_mail": {
        "display_name": "Search Goblin Village crates",
        "requirements": {},
        "output_item": "Goblin mail",
        "output_qty": 1,
        "batch_size": 3,
        "icon_path": os.path.join(QUEST_ITEMS_FOLDER, "goblin_mail.png"),
        "group": "gathering",
        "source": f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {GOBLIN_MAIL_WIKI_SOURCE}",
    },
    "aggie_make_red_dye": {
        "display_name": "Ask Aggie to make red dye",
        "requirements": {"Redberries": 3, "Coins": 5},
        "output_item": "Red dye",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(CONSTRUCTION_ITEMS_FOLDER, "red_dye.png"),
        "group": "material_processing",
        "source": GOBLIN_DIPLOMACY_WIKI_SOURCE,
    },
    "aggie_make_yellow_dye": {
        "display_name": "Ask Aggie to make yellow dye",
        "requirements": {"Onion": 2, "Coins": 5},
        "output_item": "Yellow dye",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(SHOP_ITEMS_FOLDER, "yellow_dye.png"),
        "group": "material_processing",
        "source": GOBLIN_DIPLOMACY_WIKI_SOURCE,
    },
    "mix_orange_dye": {
        "display_name": "Mix orange dye",
        "requirements": {"Red dye": 1, "Yellow dye": 1},
        "output_item": "Orange dye",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(SHOP_ITEMS_FOLDER, "orange_dye.png"),
        "group": "material_processing",
        "source": f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {ORANGE_DYE_WIKI_SOURCE}",
    },
    "aggie_make_blue_dye": {
        "display_name": "Ask Aggie to make blue dye",
        "requirements": {"Woad leaf": 2, "Coins": 5},
        "output_item": "Blue dye",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(SHOP_ITEMS_FOLDER, "blue_dye.png"),
        "group": "material_processing",
        "source": f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {BLUE_DYE_WIKI_SOURCE}",
    },
    "dye_goblin_mail_orange": {
        "display_name": "Dye goblin mail orange",
        "requirements": {"Goblin mail": 1, "Orange dye": 1},
        "output_item": "Orange goblin mail",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(QUEST_ITEMS_FOLDER, "orange_goblin_mail.png"),
        "group": "material_processing",
        "source": (
            f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {ORANGE_GOBLIN_MAIL_WIKI_SOURCE}"
        ),
    },
    "dye_goblin_mail_blue": {
        "display_name": "Dye goblin mail blue",
        "requirements": {"Goblin mail": 1, "Blue dye": 1},
        "output_item": "Blue goblin mail",
        "output_qty": 1,
        "batch_size": 1,
        "icon_path": os.path.join(QUEST_ITEMS_FOLDER, "blue_goblin_mail.png"),
        "group": "material_processing",
        "source": f"{GOBLIN_DIPLOMACY_WIKI_SOURCE}; {BLUE_GOBLIN_MAIL_WIKI_SOURCE}",
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
UTILITY_ACTIVITY_DATA.update({**grind_source_activities_as_dict(), **quest_item_acquisition_activities_as_dict()})
UTILITY_ACTIVITY_DATA.update(jungle_potion_search_activities_as_dict())
for _activity_id, _icon_name in zip(
    JUNGLE_POTION_SEARCH_ACTIVITY_IDS,
    (
        "clean_snake_weed.png",
        "clean_ardrigal.png",
        "clean_sito_foil.png",
        "clean_volencia_moss.png",
        "clean_rogue_s_purse.png",
    ),
):
    UTILITY_ACTIVITY_DATA[_activity_id]["icon_path"] = os.path.join(
        HERBLORE_ITEMS_FOLDER,
        _icon_name,
    )
UTILITY_ACTIVITY_DATA.update(prayer_utility_activities_as_dict())
UTILITY_ACTIVITY_DATA.update(bone_source_utility_activities_as_dict())
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
UTILITY_ACTIVITY_DATA.update(ranging_guild_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(temple_trekking_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(mobilising_armies_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(gnome_restaurant_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(dominion_tower_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(crucible_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(goblin_raids_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(treasure_trails_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(varrock_museum_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(fight_caves_activity_as_dict())
UTILITY_ACTIVITY_DATA.update(dagannoth_kings_activity_as_dict())
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
UTILITY_ACTIVITY_DATA.update({**compost_potion_activities_as_dict(), **chompy_hunting_activity_as_dict()})
COMBAT_ENEMY_DATA.update(bone_source_enemies_as_dict())
UTILITY_ACTIVITY_DATA[CRYSTAL_CHEST_ACTIVITY_ID] = {
    **crystal_chest_utility_spec(),
    "icon_path": os.path.join(CRAFTED_ITEMS_FOLDER, "crystal_key.png"),
}
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
_ranging_guild_icon = os.path.join(
    UTILITY_ACTIVITY_ICONS_FOLDER,
    "ranging_guild.png",
)
if os.path.exists(_ranging_guild_icon):
    UTILITY_ACTIVITY_DATA[RANGING_GUILD_ACTIVITY_ID]["icon_path"] = (
        _ranging_guild_icon
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
_dagannoth_kings_icon = os.path.join(
    current_dir, "combatenemies", "dagannoth_rex.png"
)
if os.path.exists(_dagannoth_kings_icon):
    UTILITY_ACTIVITY_DATA[DAGANNOTH_KINGS_ACTIVITY_ID]["icon_path"] = (
        _dagannoth_kings_icon
    )
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
        "weapon_preparation",
    }
)
ACTIVITY_GROUPS = frozenset(
    {
        "warriors_guild",
        "minigames",
        "distractions_and_diversions",
        "landmarks",
        "bosses",
    }
)
for _activity_spec in UTILITY_ACTIVITY_DATA.values():
    _activity_group = str(_activity_spec.get("group", "material_processing"))
    if _activity_group in ACTIVITY_GROUPS:
        _activity_spec["surface"] = ACTIVITY_SURFACE_ID
    elif _activity_group in UTILITY_ACTIVITY_GROUPS:
        _activity_spec["surface"] = UTILITY_SURFACE_ID

__all__ = [
    "DEFAULT_UTILITY_ACTIVITY",
    "UTILITY_ACTIVITY_DATA",
    "FAMILIARISATION_ACTIVITY_ID",
    "UTILITY_SURFACE_ID",
    "ACTIVITY_SURFACE_ID",
    "UTILITY_ACTIVITY_GROUPS",
    "ACTIVITY_GROUPS",
]
