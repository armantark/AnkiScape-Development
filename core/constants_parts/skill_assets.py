import os
import re

from .skill_sources import *
from .competitive_minigame_sources import *
from .combat_minigame_sources import *
from .skill_minigame_sources import *
from .distraction_sources import *
from .landmark_and_boss_sources import *
from .utility_sources import *
from .equipment_sources import *
from .equipment_sources import _BASE_EQUIPMENT_DATA
from .registry_sources import *
from .paths import *
from .hunter_assets import HUNTER_SHARED_ITEM_IMAGES
from .skill_catalog import *


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
    "Unholy mould": os.path.join(CRAFTED_ITEMS_FOLDER, "unholy_mould.png"),
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
    "Raw cave eel": os.path.join(COOKING_ITEMS_FOLDER, "raw_cave_eel.png"),
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
    _path = HUNTER_SHARED_ITEM_IMAGES.get(
        _item_name,
        os.path.join(HUNTER_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png"),
    )
    if os.path.exists(_path):
        HUNTER_ITEM_IMAGES[_item_name] = _path
for _item_name in hunter_supply_item_names():
    _path = HUNTER_ITEM_IMAGES.get(_item_name)
    if _path:
        UTILITY_ITEM_IMAGES[_item_name] = _path

COOKING_EXTRA_ITEM_DATA = cooking_extra_items_as_dict()
COOKING_ITEM_IMAGES = {}
COOKING_SHARED_ITEM_IMAGES = {
    "Ashes": os.path.join(FIREMAKING_ITEMS_FOLDER, "ashes.png"),
    "Barley": os.path.join(SHOP_ITEMS_FOLDER, "barley.png"),
    "Barley malt": os.path.join(FARMING_ITEMS_FOLDER, "barley_malt.png"),
    "Cooked karambwan": os.path.join(SHOP_ITEMS_FOLDER, "cooked_karambwan.png"),
    "Lava eel": os.path.join(QUEST_ITEMS_FOLDER, "lava_eel.png"),
    "Bucket of milk": os.path.join(QUEST_ITEMS_FOLDER, "bucket_of_milk.png"),
    "Jug of water": os.path.join(QUEST_ITEMS_FOLDER, "jug_of_water.png"),
    "Jug of wine": os.path.join(COMBAT_ITEMS_FOLDER, "jug_of_wine.png"),
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
BONE_SOURCE_EXTRA_ITEM_DATA = bone_source_extra_items_as_dict()
THIEVING_EXTRA_ITEM_DATA = thieving_extra_items_as_dict()
PRAYER_ITEM_IMAGES = {}
for _item_name in PRAYER_EXTRA_ITEM_DATA:
    _path = CRAFTED_ITEM_IMAGES.get(_item_name) or os.path.join(PRAYER_ITEMS_FOLDER, f"{_asset_slug(_item_name)}.png")
    if os.path.exists(_path):
        PRAYER_ITEM_IMAGES[_item_name] = _path
UTILITY_ITEM_IMAGES.update(PRAYER_ITEM_IMAGES)
UTILITY_ITEM_IMAGES["Raw chompy"] = COOKING_ITEM_IMAGES["Raw chompy"]

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
# activity_assets fills this shared map; its binding preserves facade export order.
QUEST_ITEM_IMAGES = {}
QUEST_ITEM_IMAGE_FILE_OVERRIDES = {
    "Lever": "temple_lever.png",
    "Kitten": "pet_kitten.png",
    "Holy symbol (Icthlarin's Little Helper)": "holy_symbol.png",
    "Unholy symbol (Icthlarin's Little Helper)": "unholy_symbol.png",
}
# activity_assets fills both Combat maps after these facade bindings.
COMBAT_ITEM_IMAGES = {}
COMBAT_ENEMY_IMAGES = {}


def _equipment_data_before_diaries():
    equipment_data = dict(_BASE_EQUIPMENT_DATA)
    equipment_data.update(barrows_equipment_data_as_dict())
    equipment_data.update(fish_flingers_equipment_data_as_dict())
    equipment_data.update(great_orb_project_equipment_data_as_dict())
    equipment_data.update(runecrafting_equipment_data_as_dict())
    equipment_data.update(cooking_gauntlets_equipment_data_as_dict())
    equipment_data.update(brawling_gloves_equipment_data_as_dict())
    equipment_data.update(trouble_brewing_equipment_data_as_dict())
    equipment_data.update(castle_wars_equipment_data_as_dict())
    equipment_data.update(pest_control_equipment_data_as_dict())
    equipment_data.update(conquest_equipment_data_as_dict())
    equipment_data.update(barbarian_assault_equipment_data_as_dict())
    equipment_data.update(stronghold_player_safety_equipment_data_as_dict())
    equipment_data.update(penguin_hide_and_seek_equipment_data_as_dict())
    equipment_data.update(duel_arena_equipment_data_as_dict())
    equipment_data.update(mage_training_arena_equipment_data_as_dict())
    equipment_data.update(mobilising_armies_equipment_data_as_dict())
    equipment_data.update(dominion_tower_equipment_data_as_dict())
    equipment_data.update(crucible_equipment_data_as_dict())
    equipment_data.update(goblin_raids_equipment_data_as_dict())
    return equipment_data


def _add_post_diary_equipment_data(equipment_data):
    equipment_data.update(milestone_cape_equipment_data_as_dict())
    equipment_data.update(cape_equipment_data_as_dict())
    equipment_data.update(crystal_chest_equipment_data_as_dict())


__all__ = [
    "FLETCHED_ITEM_IMAGES",
    "LOG_IMAGES",
    "FIREMAKING_EXTRA_ITEM_DATA",
    "FIREMAKING_ITEM_IMAGES",
    "FISHING_EXTRA_ITEM_DATA",
    "FISHING_ITEM_IMAGES",
    "FISHING_SHARED_ITEM_IMAGES",
    "HUNTER_EXTRA_ITEM_DATA",
    "HUNTER_ITEM_IMAGES",
    "HUNTER_SHARED_ITEM_IMAGES",
    "COOKING_EXTRA_ITEM_DATA",
    "COOKING_ITEM_IMAGES",
    "COOKING_SHARED_ITEM_IMAGES",
    "RUNECRAFTING_EXTRA_ITEM_DATA",
    "RUNECRAFTING_ITEM_IMAGES",
    "HERBLORE_EXTRA_ITEM_DATA",
    "HERBLORE_ITEM_IMAGES",
    "URN_ITEM_DATA",
    "PRAYER_PASSIVE_ITEM_DATA",
    "PRAYER_EXTRA_ITEM_DATA",
    "BONE_SOURCE_EXTRA_ITEM_DATA",
    "THIEVING_EXTRA_ITEM_DATA",
    "PRAYER_ITEM_IMAGES",
    "MAGIC_EXTRA_ITEM_DATA",
    "MAGIC_ITEM_IMAGES",
    "MAGIC_SPELL_IMAGES",
    "CONSTRUCTION_EXTRA_ITEM_DATA",
    "CONSTRUCTION_ASSET_ITEM_DATA",
    "CONSTRUCTION_ITEM_IMAGES",
    "SUMMONING_EXTRA_ITEM_DATA",
    "SUMMONING_ITEM_IMAGES",
    "WOODCUTTING_EXTRA_ITEM_IMAGES",
    "MINING_EXTRA_ITEM_IMAGES",
    "SMITHING_EXTRA_ITEM_DATA",
    "SMITHING_EXTRA_ITEM_IMAGES",
    "QUEST_ITEM_IMAGES",
    "QUEST_ITEM_IMAGE_FILE_OVERRIDES",
    "COMBAT_ITEM_IMAGES",
    "COMBAT_ENEMY_IMAGES",
]
