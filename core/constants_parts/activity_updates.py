import os

from .skill_foundations import *
from .competitive_activities import *
from .world_activities import *
from .catalog_sources import *
from .gathering_sources import *
from .production_sources import *
from .paths import *
from .activity_base import *

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
    "FAMILIARISATION_ACTIVITY_ID",
    "UTILITY_SURFACE_ID",
    "ACTIVITY_SURFACE_ID",
    "UTILITY_ACTIVITY_GROUPS",
    "ACTIVITY_GROUPS",
]
