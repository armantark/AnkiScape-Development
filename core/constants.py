# constants.py

import os
import re

from .constants_parts.skill_foundations import *
from .constants_parts.competitive_activities import *
from .constants_parts.world_activities import *
from ..data.achievement_diary_data import (
    ACHIEVEMENT_DIARY_CATALOG,
    diary_equipment_data_as_dict,
)
from .constants_parts.catalog_sources import *
from .constants_parts.gathering_sources import *
from ..data.quest_data import (
    BLUE_DYE_WIKI_SOURCE,
    BLUE_GOBLIN_MAIL_WIKI_SOURCE,
    CLAIMS_BY_ID,
    GERTRUDES_CAT_WIKI_SOURCE,
    GOBLIN_DIPLOMACY_WIKI_SOURCE,
    GOBLIN_MAIL_WIKI_SOURCE,
    ORANGE_DYE_WIKI_SOURCE,
    ORANGE_GOBLIN_MAIL_WIKI_SOURCE,
    QUESTS_BY_ID,
    claims_as_dict,
    quest_reward_items_as_dict,
    quest_references_as_dict,
    quest_unlock_rules_as_dict,
    quests_as_dict,
)
from .constants_parts.production_sources import *
from .constants_parts.paths import *
from .constants_parts.activity_base import *

UTILITY_ACTIVITY_DATA.update({
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
})

from .constants_parts.activity_updates import *

from .constants_parts.skill_catalog import *

QUEST_DATA = quests_as_dict()
QUEST_REFERENCE_DATA = quest_references_as_dict()
QUEST_UNLOCK_RULES = quest_unlock_rules_as_dict()
QUEST_REWARD_ITEM_DATA = {**quest_reward_items_as_dict(), **quest_item_acquisition_extra_items_as_dict()}
CLAIM_DATA = claims_as_dict()

from .constants_parts.skill_assets import *
from .constants_parts.skill_assets import _asset_slug

for _item_name in QUEST_REWARD_ITEM_DATA:
    _path = os.path.join(
        QUEST_ITEMS_FOLDER,
        QUEST_ITEM_IMAGE_FILE_OVERRIDES.get(_item_name, f"{_asset_slug(_item_name)}.png"),
    )
    if os.path.exists(_path):
        QUEST_ITEM_IMAGES[_item_name] = _path
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
for _activity_spec in UTILITY_ACTIVITY_DATA.values():
    _icon_item = _activity_spec.get("icon_item")
    if not isinstance(_icon_item, str) or _icon_item in UTILITY_ITEM_IMAGES:
        continue
    _icon_path = COMBAT_ITEM_IMAGES.get(_icon_item) or PRAYER_ITEM_IMAGES.get(_icon_item)
    if _icon_path:
        UTILITY_ITEM_IMAGES[_icon_item] = _icon_path
_fungicide_spray_path = os.path.join(SHOP_ITEMS_FOLDER, "fungicide_spray_10.png")
if os.path.exists(_fungicide_spray_path):
    for _charges in range(11):
        COMBAT_ITEM_IMAGES[f"Fungicide spray {_charges}"] = _fungicide_spray_path
_fungicide_path = os.path.join(SHOP_ITEMS_FOLDER, "fungicide.png")
if os.path.exists(_fungicide_path):
    COMBAT_ITEM_IMAGES["Fungicide"] = _fungicide_path
_period_clue_scroll_path = os.path.join(
    current_dir, "activityitems", "clue_scroll_hard.png"
)
if os.path.exists(_period_clue_scroll_path):
    # Rev-742 easy, medium, and hard clues all use client model 3374.
    COMBAT_ITEM_IMAGES["Clue scroll (medium)"] = _period_clue_scroll_path
for _target_id in COMBAT_ENEMY_DATA:
    _path = os.path.join(COMBAT_ENEMIES_FOLDER, f"{_asset_slug(_target_id)}.png")
    if os.path.exists(_path):
        COMBAT_ENEMY_IMAGES[_target_id] = _path
# Goblin Raids' unnamed village goblin has no wiki image of its own, so it shows
# the art of the registered goblin row it inherits its stats from.
for _row in GOBLIN_RAID_ENEMIES:
    if _row.id not in COMBAT_ENEMY_IMAGES and _row.base in COMBAT_ENEMY_IMAGES:
        COMBAT_ENEMY_IMAGES[_row.id] = COMBAT_ENEMY_IMAGES[_row.base]

EQUIPMENT_DATA.update(diary_equipment_data_as_dict())

from .constants_parts.activity_assets import *

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
UTILITY_ITEM_IMAGES["Ogre arrow"] = SHOP_ITEM_IMAGES["Ogre arrow"]

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
        GREAT_ORB_PROJECT_EXTRA_ITEM_DATA,
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
    return names - ({spec.get("output_item") for spec in UTILITY_ACTIVITY_DATA.values() if spec.get("group") == "material_processing"} & SHOP_EXTRA_ITEM_DATA.keys())


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
CRYSTAL_CHEST_EXTRA_ITEM_DATA = crystal_chest_extra_items_as_dict()


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
    **COOKING_EXTRA_ITEM_DATA,
    **CRAFTING_REQUIRED_ITEM_DATA,
    **CRAFTING_SPECIAL_ITEM_DATA,
    **RUNECRAFTING_EXTRA_ITEM_DATA,
    **GREAT_ORB_PROJECT_EXTRA_ITEM_DATA,
    **HERBLORE_EXTRA_ITEM_DATA,
    **PRAYER_EXTRA_ITEM_DATA,
    **BONE_SOURCE_EXTRA_ITEM_DATA,
    **COMBAT_EXTRA_ITEM_DATA,
    **BRAWLING_GLOVES_EXTRA_ITEM_DATA,
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
    **RANGING_GUILD_EXTRA_ITEM_DATA,
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
    **CRYSTAL_CHEST_EXTRA_ITEM_DATA,
    **HUNTER_EXTRA_ITEM_DATA,
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
    **BRAWLING_GLOVE_ITEM_IMAGES,
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
    **RANGING_GUILD_ITEM_IMAGES,
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

__all__ = [name for name in globals() if not name.startswith("_")]
