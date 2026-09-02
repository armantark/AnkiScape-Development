import os
import re

from .skill_foundations import *
from .competitive_activities import *
from .world_activities import *
from .catalog_sources import *
from .gathering_sources import *
from .production_sources import *
from .paths import *
from .skill_catalog import *
from .skill_assets import *
from .skill_assets import _asset_slug

EQUIPMENT_DATA.update(milestone_cape_equipment_data_as_dict())
EQUIPMENT_DATA.update(cape_equipment_data_as_dict())
EQUIPMENT_DATA.update(crystal_chest_equipment_data_as_dict())
EQUIPMENT_ITEM_DATA = equipment_items_as_dict(EQUIPMENT_DATA)
FIST_OF_GUTHIX_EXTRA_ITEM_DATA = fist_of_guthix_extra_items_as_dict()
BRAWLING_GLOVES_EXTRA_ITEM_DATA = brawling_gloves_extra_items_as_dict()
BRAWLING_GLOVE_ITEM_IMAGES = {}
for _item_name in BRAWLING_GLOVES_EXTRA_ITEM_DATA:
    _path = os.path.join(BRAWLING_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        BRAWLING_GLOVE_ITEM_IMAGES[_item_name] = _path
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
RANGING_GUILD_EXTRA_ITEM_DATA = ranging_guild_extra_items_as_dict()
RANGING_GUILD_ITEM_IMAGES = {
    str(row["item_name"]): os.path.join(current_dir, str(row["output_path"]))
    for row in RANGING_GUILD_ASSET_MANIFEST
    if os.path.exists(os.path.join(current_dir, str(row["output_path"])))
}
RANGING_GUILD_ITEM_IMAGES.update(
    {
        "Barb bolttips": os.path.join(current_dir, "fletcheditems", "barb_bolttips.png"),
        "Rune arrows": os.path.join(current_dir, "fletcheditems", "rune_arrows.png"),
        "Studded body": os.path.join(current_dir, "crafteditems", "studded_body.png"),
        "Coif": os.path.join(current_dir, "shopitems", "coif.png"),
        "Green d'hide body": os.path.join(current_dir, "crafteditems", "green_d_hide_body.png"),
        "Adamant javelin": os.path.join(current_dir, "shopitems", "adamant_javelin.png"),
    }
)
RANGING_GUILD_ITEM_IMAGES = {
    item_name: path
    for item_name, path in RANGING_GUILD_ITEM_IMAGES.items()
    if os.path.exists(path)
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
GREAT_ORB_PROJECT_EXTRA_ITEM_DATA = great_orb_project_extra_items_as_dict()
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
    item_name: os.path.join(
        current_dir,
        "activityitems",
        (
            "blue_tricorn_hat.png"
            if item_name == "Blue tricorn hat"
            else f"trouble_brewing_{_asset_slug(item_name)}.png"
        ),
    )
    for item_name in TROUBLE_BREWING_EXTRA_ITEM_DATA
}
TROUBLE_BREWING_ITEM_IMAGES["Clue scroll (medium)"] = COMBAT_ITEM_IMAGES[
    "Clue scroll (medium)"
]
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
GREAT_ORB_PROJECT_ITEM_IMAGES = {
    _item_name: os.path.join(
        current_dir,
        "activityitems",
        f"{_asset_slug(_item_name)}.png",
    )
    for _item_name in GREAT_ORB_PROJECT_EXTRA_ITEM_DATA
}
GREAT_ORB_PROJECT_ITEM_IMAGES = {
    _item_name: _path
    for _item_name, _path in GREAT_ORB_PROJECT_ITEM_IMAGES.items()
    if os.path.exists(_path)
}
UTILITY_ITEM_IMAGES.update(GREAT_ORB_PROJECT_ITEM_IMAGES)
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

__all__ = [
    "EQUIPMENT_ITEM_DATA",
    "FIST_OF_GUTHIX_EXTRA_ITEM_DATA",
    "BRAWLING_GLOVES_EXTRA_ITEM_DATA",
    "BRAWLING_GLOVE_ITEM_IMAGES",
    "COURT_CASES_EXTRA_ITEM_DATA",
    "CIRCUS_EXTRA_ITEM_DATA",
    "TROUBLE_BREWING_EXTRA_ITEM_DATA",
    "CASTLE_WARS_EXTRA_ITEM_DATA",
    "PEST_CONTROL_EXTRA_ITEM_DATA",
    "CONQUEST_EXTRA_ITEM_DATA",
    "BARBARIAN_ASSAULT_EXTRA_ITEM_DATA",
    "STRONGHOLD_PLAYER_SAFETY_EXTRA_ITEM_DATA",
    "STRONGHOLD_OF_SECURITY_EXTRA_ITEM_DATA",
    "SHADES_OF_MORTTON_EXTRA_ITEM_DATA",
    "VARROCK_MUSEUM_EXTRA_ITEM_DATA",
    "SHADES_OF_MORTTON_ITEM_IMAGES",
    "SORCERESS_GARDEN_EXTRA_ITEM_DATA",
    "VINESWEEPER_EXTRA_ITEM_DATA",
    "FIGHT_CAVES_EXTRA_ITEM_DATA",
    "PHOENIX_LAIR_EXTRA_ITEM_DATA",
    "SKELETAL_HORROR_EXTRA_ITEM_DATA",
    "BORK_EXTRA_ITEM_DATA",
    "TROLL_INVASION_EXTRA_ITEM_DATA",
    "SHATTERED_HEART_EXTRA_ITEM_DATA",
    "SHATTERED_HEART_ITEM_IMAGES",
    "MAGE_TRAINING_ARENA_EXTRA_ITEM_DATA",
    "MAGE_TRAINING_ARENA_ITEM_IMAGES",
    "RANGING_GUILD_EXTRA_ITEM_DATA",
    "RANGING_GUILD_ITEM_IMAGES",
    "MOBILISING_ARMIES_EXTRA_ITEM_DATA",
    "MOBILISING_ARMIES_ITEM_IMAGES",
    "GNOME_RESTAURANT_EXTRA_ITEM_DATA",
    "GNOME_RESTAURANT_ITEM_IMAGES",
    "DOMINION_TOWER_EXTRA_ITEM_DATA",
    "DOMINION_TOWER_ITEM_IMAGES",
    "TEMPLE_TREKKING_EXTRA_ITEM_DATA",
    "TEMPLE_TREKKING_ITEM_IMAGES",
    "ENCHANTED_KEY_EXTRA_ITEM_DATA",
    "ENCHANTED_KEY_ITEM_IMAGES",
    "STEALING_CREATION_EXTRA_ITEM_DATA",
    "BARROWS_EXTRA_ITEM_DATA",
    "FLASH_POWDER_FACTORY_EXTRA_ITEM_DATA",
    "PYRAMID_PLUNDER_EXTRA_ITEM_DATA",
    "WEREWOLF_SKULLBALL_EXTRA_ITEM_DATA",
    "GNOME_BALL_EXTRA_ITEM_DATA",
    "FISH_FLINGERS_EXTRA_ITEM_DATA",
    "GREAT_ORB_PROJECT_EXTRA_ITEM_DATA",
    "DUEL_ARENA_EXTRA_ITEM_DATA",
    "CRUCIBLE_EXTRA_ITEM_DATA",
    "GOBLIN_RAIDS_EXTRA_ITEM_DATA",
    "DAILY_CHALLENGE_EXTRA_ITEM_DATA",
    "TREASURE_TRAILS_EXTRA_ITEM_DATA",
    "DUNGEONEERING_EXTRA_ITEM_DATA",
    "COURT_CASES_ITEM_IMAGES",
    "CIRCUS_ITEM_IMAGES",
    "TROUBLE_BREWING_ITEM_IMAGES",
    "CASTLE_WARS_ITEM_IMAGES",
    "PEST_CONTROL_ITEM_IMAGES",
    "CONQUEST_ITEM_IMAGES",
    "BARBARIAN_ASSAULT_ITEM_IMAGES",
    "STRONGHOLD_PLAYER_SAFETY_ITEM_IMAGES",
    "STRONGHOLD_OF_SECURITY_ITEM_IMAGES",
    "VARROCK_MUSEUM_ITEM_IMAGES",
    "FISH_FLINGERS_ITEM_IMAGES",
    "GREAT_ORB_PROJECT_ITEM_IMAGES",
    "DUEL_ARENA_ITEM_IMAGES",
    "TREASURE_TRAILS_ITEM_IMAGES",
    "DAILY_CHALLENGE_ITEM_IMAGES",
    "VINESWEEPER_ITEM_IMAGES",
    "FIGHT_CAVES_ITEM_IMAGES",
    "PHOENIX_LAIR_ITEM_IMAGES",
    "SKELETAL_HORROR_ITEM_IMAGES",
    "TROLL_INVASION_ITEM_IMAGES",
    "STEALING_CREATION_ITEM_IMAGES",
    "BARROWS_ITEM_IMAGES",
    "SORCERESS_GARDEN_ITEM_IMAGES",
    "PYRAMID_PLUNDER_ITEM_IMAGES",
    "WEREWOLF_SKULLBALL_ITEM_IMAGES",
]
