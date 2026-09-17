from __future__ import annotations

from .dependencies import *
from .catalog_overrides import *
from .catalog import _quest_reward_item_name

from . import definitions as _definitions
from . import stage_overrides as _stage_overrides

from .reward_item_fragments import _BAR_CRAWL_FRAGMENT, _COINS_FRAGMENT, _LET_THEM_EAT_PIE_FRAGMENT, _EAGLES_PEAK_FRAGMENT

_QUEST_REWARD_ITEM_FRAGMENTS = (
    _BAR_CRAWL_FRAGMENT,
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['druidic_ritual'][0],
    _COINS_FRAGMENT,
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['some_like_it_cold'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['stolen_hearts'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['diamond_in_the_rough'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['icthlarins_little_helper'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['smoking_kills'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['shilo_village'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['fishing_contest'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['heroes_quest'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['gertrudes_cat'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['clock_tower'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['heroes_quest'][1],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['family_crest'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['temple_of_ikov'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['monks_friend'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['tribal_totem'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['scorpion_catcher'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['sheep_herder'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['plague_city'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['biohazard'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['waterfall_quest'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['dwarf_cannon'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['shield_of_arrav'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['lost_city'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['demon_slayer'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['goblin_diplomacy'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['ernest_the_chicken'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['dragon_slayer'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['fight_arena'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['witchs_house'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['merlins_crystal'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['holy_grail'][0],
    _stage_overrides._REWARD_ITEM_FRAGMENTS_BY_QUEST['tree_gnome_village'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['merlins_crystal'][1],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['tai_bwo_wannai_trio'][0],
    _definitions._REWARD_ITEM_FRAGMENTS_BY_QUEST['legacy_of_seergaze'][0],
    _LET_THEM_EAT_PIE_FRAGMENT,
    _EAGLES_PEAK_FRAGMENT,
)


def _catalog_reward_items() -> Dict[str, Dict[str, object]]:
    generated_items: Dict[str, Dict[str, object]] = {}
    for row in PRE_EOC_QUEST_CATALOG:
        for reward in row.get("item_rewards", ()) or ():
            if not isinstance(reward, dict):
                continue
            item_name = _quest_reward_item_name(reward.get("item_name"))
            if not isinstance(item_name, str) or not item_name:
                continue
            generated_items[item_name] = {
                "category": str(reward.get("category", "material")),
                "source": str(reward.get("source", row.get("reward_source", row.get("source", "")))),
            }
    return generated_items


def quest_reward_items_as_dict() -> Dict[str, Dict[str, object]]:
    generated_items = _catalog_reward_items()
    for rewards in QUEST_ITEM_REWARD_ADDITIONS_BY_ID.values():
        for reward in rewards:
            item_name = _quest_reward_item_name(reward.get("item_name"))
            if not isinstance(item_name, str) or not item_name:
                continue
            generated_items[item_name] = {
                "category": str(reward.get("category", "material")),
                "source": str(reward.get("source", "")),
            }
    for _fragment in _QUEST_REWARD_ITEM_FRAGMENTS:
        generated_items.update({name: metadata.copy() for name, metadata in _fragment.items()})
    for non_item_name in (
        "Queen Black Dragon",
        "Penguin Hide and Seek",
        "Combat Training Camp",
        "Coin",
        "Law Rune",
        "Construction",
        "Piscatoris - South of Falconry",
        "2,100 Cooking",
        "3,000 Thieving",
        "3,350 Crafting",
        "5,000 Magic",
        "6,500 Prayer",
        "Brimhaven Agility Arena",
        "Bank deposit box",
        "Castle Wars",
        "Charter ship",
        "Decaying Avatar",
        "Dorgesh-Kaan - Keldagrim Train System",
        "Eagles' Peak",
        "East Ardougne",
        "Expensive spices (necklace) (page does not exist)",
        "Ferret",
        "File:Apmeken's tomb entrance.jpg",
        "Giant ant soldier",
        "Jade vine maze",
        "Lunar Spells",
        "Magic carpet",
        "Martin the Master Gardener",
        "North-East of Pollnivneach",
        "North-west of Bedabin Camp",
        "Pyramid Plunder",
        "Soul Wars",
        "South Coast of Ape Atoll",
        "South of Brimhaven",
        "South of Elf Camp",
        "Spirit Realm",
        "The Apmeken tomb.",
        "The concept art for Jones the fisherman",
        "The concept art for Thalassus",
        "Tome of Experience, 2nd Ed.",
        "Varrock Museum",
        "West Coast of Harmony Island",
        "West Coast of Mort Myre Swamp",
        "Zanaris Market",
        "Zeal points",
    ):
        generated_items.pop(non_item_name, None)
    return generated_items


quest_reward_items_as_dict.__module__ = "ankiscape.data.quest_data"

__all__ = (
    'quest_reward_items_as_dict',
)
