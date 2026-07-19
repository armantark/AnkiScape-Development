"""AnkiScape Herblore data, transcribed from the local 2011Scape/Darkan checkout.

Parity sources (runtime imports only this checked-in Python; the emulator
checkout is a development-time audit input):
  HerbData.kt   -- grimy/clean/unf identities + herb level & clean XP
  PotionData.kt -- finished recipe primary/secondary/product, level & XP

The ordinary Herblore catalog deliberately excludes Daemonheim-only targets.
Their source rows remain registered below so existing saves keep their item
identities while Dungeoneering's temporary inventory/session model is deferred.

Three-stage pipeline, each stage a menu action:
  clean    grimy herb            -> clean herb    (awards HerbData.experience)
  unf      clean herb + Vial of water -> unf potion (zero XP; clean_herb has the
           XP, the unf step in CreateUnfinishedPotionAction.kt awards none)
  finished unf/base potion + secondary -> potion  (awards PotionData.experience,
           CreateFinishedPotionAction.kt:39)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


HERBLORE_SOURCE_ROOT = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/herblore"
)
HERB_DATA_SOURCE_PATH = f"{HERBLORE_SOURCE_ROOT}/HerbData.kt"
POTION_DATA_SOURCE_PATH = f"{HERBLORE_SOURCE_ROOT}/mixing/PotionData.kt"
OVERLOAD_WIKI_SOURCE = "https://runescape.wiki/w/Overload?oldid=6552017"
EXTREME_ATTACK_WIKI_SOURCE = "https://runescape.wiki/w/Extreme_attack?oldid=6462605"
EXTREME_STRENGTH_WIKI_SOURCE = "https://runescape.wiki/w/Extreme_strength?oldid=6474549"
EXTREME_DEFENCE_WIKI_SOURCE = "https://runescape.wiki/w/Extreme_defence?oldid=6462607"
EXTREME_MAGIC_WIKI_SOURCE = "https://runescape.wiki/w/Extreme_magic?oldid=6462609"
EXTREME_RANGING_WIKI_SOURCE = "https://runescape.wiki/w/Extreme_ranging?oldid=6462610"
SHRINK_ME_QUICK_WIKI_SOURCE = "https://runescape.wiki/w/Shrink-me-quick?oldid=6333484"
PESTLE_AND_MORTAR_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/items/pestle_and_mortar/PestleAndMortarData.kt"
)
WATER_CONTAINER_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/watersource/WaterContainerData.kt"
)
FILL_WATER_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/objs/watersource/fill_water.plugin.kts"
)
SWAMP_TOAD_SOURCE_PATH = (
    "/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/"
    "gg/rsmod/plugins/content/items/swamp_toad.plugin.kts"
)

DEFAULT_HERBLORE_TARGET = "clean_guam"
VIAL_OF_WATER_ITEM = "Vial of water"


@dataclass(frozen=True)
class HerbloreTarget:
    id: str
    display_name: str
    group: str  # clean | unf | finished
    subgroup: str  # herb | standard | barbarian | juju | dungeoneering
    level: int
    exp: float
    requirements: Tuple[Tuple[str, int], ...]
    output_item: str
    output_qty: int = 1
    byproducts: Tuple[Tuple[str, int], ...] = ()
    source: str = HERB_DATA_SOURCE_PATH


@dataclass(frozen=True)
class PestleAndMortarActivity:
    id: str
    display_name: str
    source_item: str
    source_item_id: int
    output_item: str
    output_item_id: int
    source_enum: str
    source: str = PESTLE_AND_MORTAR_SOURCE_PATH


@dataclass(frozen=True)
class InputPreparationActivity:
    id: str
    display_name: str
    source_item: str
    source_item_id: int
    output_item: str
    output_item_id: int
    source: str


_SOURCE_CLEAN_TARGETS: Tuple[HerbloreTarget, ...] = (
    HerbloreTarget('clean_guam', 'Clean guam', "clean", "herb", 3, 2.5, (('Grimy guam', 1),), 'Clean guam'),
    HerbloreTarget('clean_marrentill', 'Clean marrentill', "clean", "herb", 5, 3.8, (('Grimy marrentill', 1),), 'Clean marrentill'),
    HerbloreTarget('clean_tarromin', 'Clean tarromin', "clean", "herb", 11, 5.0, (('Grimy tarromin', 1),), 'Clean tarromin'),
    HerbloreTarget('clean_harralander', 'Clean harralander', "clean", "herb", 20, 6.3, (('Grimy harralander', 1),), 'Clean harralander'),
    HerbloreTarget('clean_ranarr', 'Clean ranarr', "clean", "herb", 25, 7.5, (('Grimy ranarr', 1),), 'Clean ranarr'),
    HerbloreTarget('clean_toadflax', 'Clean toadflax', "clean", "herb", 30, 8.0, (('Grimy toadflax', 1),), 'Clean toadflax'),
    HerbloreTarget('clean_spirit_weed', 'Clean spirit weed', "clean", "herb", 35, 7.8, (('Grimy spirit weed', 1),), 'Clean spirit weed'),
    HerbloreTarget('clean_irit', 'Clean irit', "clean", "herb", 40, 8.8, (('Grimy irit', 1),), 'Clean irit'),
    HerbloreTarget('clean_wergali', 'Clean wergali', "clean", "herb", 41, 9.5, (('Grimy wergali', 1),), 'Clean wergali'),
    HerbloreTarget('clean_avantoe', 'Clean avantoe', "clean", "herb", 48, 10.0, (('Grimy avantoe', 1),), 'Clean avantoe'),
    HerbloreTarget('clean_kwuarm', 'Clean kwuarm', "clean", "herb", 54, 11.3, (('Grimy kwuarm', 1),), 'Clean kwuarm'),
    HerbloreTarget('clean_snapdragon', 'Clean snapdragon', "clean", "herb", 59, 11.8, (('Grimy snapdragon', 1),), 'Clean snapdragon'),
    HerbloreTarget('clean_cadantine', 'Clean cadantine', "clean", "herb", 65, 12.5, (('Grimy cadantine', 1),), 'Clean cadantine'),
    HerbloreTarget('clean_lantadyme', 'Clean lantadyme', "clean", "herb", 67, 13.1, (('Grimy lantadyme', 1),), 'Clean lantadyme'),
    HerbloreTarget('clean_dwarf_weed', 'Clean dwarf weed', "clean", "herb", 70, 13.8, (('Grimy dwarf weed', 1),), 'Clean dwarf weed'),
    HerbloreTarget('clean_torstol', 'Clean torstol', "clean", "herb", 75, 15.0, (('Grimy torstol', 1),), 'Clean torstol'),
    HerbloreTarget('clean_fellstalk', 'Clean fellstalk', "clean", "herb", 91, 16.8, (('Grimy fellstalk', 1),), 'Clean fellstalk'),
    HerbloreTarget('clean_erzille', 'Clean erzille', "clean", "herb", 54, 10.0, (('Grimy erzille', 1),), 'Clean erzille'),
    HerbloreTarget('clean_argway', 'Clean argway', "clean", "herb", 56, 11.6, (('Grimy argway', 1),), 'Clean argway'),
    HerbloreTarget('clean_ugune', 'Clean ugune', "clean", "herb", 55, 11.5, (('Grimy ugune', 1),), 'Clean ugune'),
    HerbloreTarget('clean_shengo', 'Clean shengo', "clean", "herb", 57, 11.7, (('Grimy shengo', 1),), 'Clean shengo'),
    HerbloreTarget('clean_samaden', 'Clean samaden', "clean", "herb", 58, 11.7, (('Grimy samaden', 1),), 'Clean samaden'),
    HerbloreTarget('clean_sagawort', 'Clean sagewort', "clean", "dungeoneering", 3, 2.1, (('Grimy sagewort', 1),), 'Clean sagewort'),
    HerbloreTarget('clean_featherfoil', 'Clean featherfoil', "clean", "dungeoneering", 41, 8.6, (('Grimy featherfoil', 1),), 'Clean featherfoil'),
    HerbloreTarget('clean_valerian', 'Clean valerian', "clean", "dungeoneering", 4, 3.2, (('Grimy valerian', 1),), 'Clean valerian'),
    HerbloreTarget('clean_aloe', 'Clean aloe', "clean", "dungeoneering", 8, 4.0, (('Grimy aloe', 1),), 'Clean aloe'),
    HerbloreTarget('clean_wormwood', 'Clean wormwood leaf', "clean", "dungeoneering", 34, 7.2, (('Grimy wormwood leaf', 1),), 'Clean wormwood leaf'),
    HerbloreTarget('clean_magebane', 'Clean magebane', "clean", "dungeoneering", 37, 7.7, (('Grimy magebane', 1),), 'Clean magebane'),
    HerbloreTarget('clean_winter_grip', "Clean winter's grip", "clean", "dungeoneering", 67, 12.7, (("Grimy winter's grip", 1),), "Clean winter's grip"),
    HerbloreTarget('clean_lycopus', 'Clean lycopus', "clean", "dungeoneering", 70, 13.1, (('Grimy lycopus', 1),), 'Clean lycopus'),
    HerbloreTarget('clean_buckthorn', 'Clean buckthorn', "clean", "dungeoneering", 74, 13.8, (('Grimy buckthorn', 1),), 'Clean buckthorn'),
)

_SOURCE_UNF_TARGETS: Tuple[HerbloreTarget, ...] = (
    HerbloreTarget('unf_guam', 'Guam potion (unf)', "unf", "herb", 3, 0.0, (('Clean guam', 1), ('Vial of water', 1)), 'Guam potion (unf)'),
    HerbloreTarget('unf_marrentill', 'Marrentill potion (unf)', "unf", "herb", 5, 0.0, (('Clean marrentill', 1), ('Vial of water', 1)), 'Marrentill potion (unf)'),
    HerbloreTarget('unf_tarromin', 'Tarromin potion (unf)', "unf", "herb", 11, 0.0, (('Clean tarromin', 1), ('Vial of water', 1)), 'Tarromin potion (unf)'),
    HerbloreTarget('unf_harralander', 'Harralander potion (unf)', "unf", "herb", 20, 0.0, (('Clean harralander', 1), ('Vial of water', 1)), 'Harralander potion (unf)'),
    HerbloreTarget('unf_ranarr', 'Ranarr potion (unf)', "unf", "herb", 25, 0.0, (('Clean ranarr', 1), ('Vial of water', 1)), 'Ranarr potion (unf)'),
    HerbloreTarget('unf_toadflax', 'Toadflax potion (unf)', "unf", "herb", 30, 0.0, (('Clean toadflax', 1), ('Vial of water', 1)), 'Toadflax potion (unf)'),
    HerbloreTarget('unf_spirit_weed', 'Spirit weed potion (unf)', "unf", "herb", 35, 0.0, (('Clean spirit weed', 1), ('Vial of water', 1)), 'Spirit weed potion (unf)'),
    HerbloreTarget('unf_irit', 'Irit potion (unf)', "unf", "herb", 40, 0.0, (('Clean irit', 1), ('Vial of water', 1)), 'Irit potion (unf)'),
    HerbloreTarget('unf_wergali', 'Wergali potion (unf)', "unf", "herb", 41, 0.0, (('Clean wergali', 1), ('Vial of water', 1)), 'Wergali potion (unf)'),
    HerbloreTarget('unf_avantoe', 'Avantoe potion (unf)', "unf", "herb", 48, 0.0, (('Clean avantoe', 1), ('Vial of water', 1)), 'Avantoe potion (unf)'),
    HerbloreTarget('unf_kwuarm', 'Kwuarm potion (unf)', "unf", "herb", 54, 0.0, (('Clean kwuarm', 1), ('Vial of water', 1)), 'Kwuarm potion (unf)'),
    HerbloreTarget('unf_snapdragon', 'Snapdragon potion (unf)', "unf", "herb", 59, 0.0, (('Clean snapdragon', 1), ('Vial of water', 1)), 'Snapdragon potion (unf)'),
    HerbloreTarget('unf_cadantine', 'Cadantine potion (unf)', "unf", "herb", 65, 0.0, (('Clean cadantine', 1), ('Vial of water', 1)), 'Cadantine potion (unf)'),
    HerbloreTarget('unf_lantadyme', 'Lantadyme potion (unf)', "unf", "herb", 67, 0.0, (('Clean lantadyme', 1), ('Vial of water', 1)), 'Lantadyme potion (unf)'),
    HerbloreTarget('unf_dwarf_weed', 'Dwarf weed potion (unf)', "unf", "herb", 70, 0.0, (('Clean dwarf weed', 1), ('Vial of water', 1)), 'Dwarf weed potion (unf)'),
    HerbloreTarget('unf_torstol', 'Torstol potion (unf)', "unf", "herb", 75, 0.0, (('Clean torstol', 1), ('Vial of water', 1)), 'Torstol potion (unf)'),
    HerbloreTarget('unf_fellstalk', 'Fellstalk potion (unf)', "unf", "herb", 91, 0.0, (('Clean fellstalk', 1), ('Vial of water', 1)), 'Fellstalk potion (unf)'),
    HerbloreTarget('unf_erzille', 'Erzille potion (unf)', "unf", "herb", 54, 0.0, (('Clean erzille', 1), ('Vial of water', 1)), 'Erzille potion (unf)'),
    HerbloreTarget('unf_argway', 'Argway potion (unf)', "unf", "herb", 56, 0.0, (('Clean argway', 1), ('Vial of water', 1)), 'Argway potion (unf)'),
    HerbloreTarget('unf_ugune', 'Ugune potion (unf)', "unf", "herb", 55, 0.0, (('Clean ugune', 1), ('Vial of water', 1)), 'Ugune potion (unf)'),
    HerbloreTarget('unf_shengo', 'Shengo potion (unf)', "unf", "herb", 57, 0.0, (('Clean shengo', 1), ('Vial of water', 1)), 'Shengo potion (unf)'),
    HerbloreTarget('unf_samaden', 'Samaden potion (unf)', "unf", "herb", 58, 0.0, (('Clean samaden', 1), ('Vial of water', 1)), 'Samaden potion (unf)'),
    HerbloreTarget('unf_sagawort', 'Sagewort potion (unf)', "unf", "dungeoneering", 3, 0.0, (('Clean sagewort', 1), ('Vial of water', 1)), 'Sagewort potion (unf)'),
    HerbloreTarget('unf_featherfoil', 'Featherfoil potion (unf)', "unf", "dungeoneering", 41, 0.0, (('Clean featherfoil', 1), ('Vial of water', 1)), 'Featherfoil potion (unf)'),
    HerbloreTarget('unf_valerian', 'Valerian potion (unf)', "unf", "dungeoneering", 4, 0.0, (('Clean valerian', 1), ('Vial of water', 1)), 'Valerian potion (unf)'),
    HerbloreTarget('unf_aloe', 'Aloe potion (unf)', "unf", "dungeoneering", 8, 0.0, (('Clean aloe', 1), ('Vial of water', 1)), 'Aloe potion (unf)'),
    HerbloreTarget('unf_wormwood', 'Wormwood potion (unf)', "unf", "dungeoneering", 34, 0.0, (('Clean wormwood leaf', 1), ('Vial of water', 1)), 'Wormwood potion (unf)'),
    HerbloreTarget('unf_magebane', 'Magebane potion (unf)', "unf", "dungeoneering", 37, 0.0, (('Clean magebane', 1), ('Vial of water', 1)), 'Magebane potion (unf)'),
    HerbloreTarget('unf_winter_grip', "Winter's grip potion (unf)", "unf", "dungeoneering", 67, 0.0, (("Clean winter's grip", 1), ('Vial of water', 1)), "Winter's grip potion (unf)"),
    HerbloreTarget('unf_lycopus', 'Lycopus potion (unf)', "unf", "dungeoneering", 70, 0.0, (('Clean lycopus', 1), ('Vial of water', 1)), 'Lycopus potion (unf)'),
    HerbloreTarget('unf_buckthorn', 'Buckthorn potion (unf)', "unf", "dungeoneering", 74, 0.0, (('Clean buckthorn', 1), ('Vial of water', 1)), 'Buckthorn potion (unf)'),
)

_SOURCE_FINISHED_TARGETS: Tuple[HerbloreTarget, ...] = (
    HerbloreTarget('finished_attack_potion', 'Attack potion (3)', "finished", 'standard', 3, 25.0, (('Guam potion (unf)', 1), ('Eye of newt', 1)), 'Attack potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_antipoison', 'Antipoison (3)', "finished", 'standard', 5, 37.5, (('Marrentill potion (unf)', 1), ('Unicorn horn dust', 1)), 'Antipoison (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strength_potion', 'Strength potion (3)', "finished", 'standard', 12, 50.0, (('Tarromin potion (unf)', 1), ('Limpwurt root', 1)), 'Strength potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_restore_potion', 'Restore potion (3)', "finished", 'standard', 22, 62.5, (('Harralander potion (unf)', 1), ("Red spiders' eggs", 1)), 'Restore potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_energy_potion', 'Energy potion (3)', "finished", 'standard', 26, 67.5, (('Harralander potion (unf)', 1), ('Chocolate dust', 1)), 'Energy potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_defence_potion', 'Defence potion (3)', "finished", 'standard', 30, 75.0, (('Ranarr potion (unf)', 1), ('White berries', 1)), 'Defence potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_agility_potion', 'Agility potion (3)', "finished", 'standard', 34, 80.0, (('Toadflax potion (unf)', 1), ("Toad's legs", 1)), 'Agility potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_combat_potion', 'Combat potion (3)', "finished", 'standard', 36, 84.0, (('Harralander potion (unf)', 1), ('Goat horn dust', 1)), 'Combat potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_prayer_potion', 'Prayer potion (3)', "finished", 'standard', 38, 87.5, (('Ranarr potion (unf)', 1), ('Snape grass', 1)), 'Prayer potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_summoning_potion', 'Summoning potion (3)', "finished", 'standard', 40, 92.0, (('Spirit weed potion (unf)', 1), ('Cockatrice egg', 1)), 'Summoning potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_crafting_potion', 'Crafting potion (3)', "finished", 'standard', 42, 95.0, (('Wergali potion (unf)', 1), ('Frog spawn', 1)), 'Crafting potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_attack', 'Super attack (3)', "finished", 'standard', 45, 100.0, (('Irit potion (unf)', 1), ('Eye of newt', 1)), 'Super attack (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_antipoison', 'Super antipoison (3)', "finished", 'standard', 48, 106.3, (('Irit potion (unf)', 1), ('Unicorn horn dust', 1)), 'Super antipoison (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_fishing_potion', 'Fishing potion (3)', "finished", 'standard', 50, 112.5, (('Avantoe potion (unf)', 1), ('Snape grass', 1)), 'Fishing potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_energy', 'Super energy (3)', "finished", 'standard', 52, 117.5, (('Avantoe potion (unf)', 1), ('Mort myre fungus', 1)), 'Super energy (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_shrink_me_quick', 'Shrink-me-quick', "finished", 'standard', 52, 6.0, (('Tarromin potion (unf)', 1), ('Shrunk ogleroot', 1)), 'Shrink-me-quick', source=SHRINK_ME_QUICK_WIKI_SOURCE),
    HerbloreTarget('finished_hunter_potion', 'Hunter potion (3)', "finished", 'standard', 53, 120.0, (('Avantoe potion (unf)', 1), ('Kebbit teeth dust', 1)), 'Hunter potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_strength', 'Super strength (3)', "finished", 'standard', 55, 125.0, (('Kwuarm potion (unf)', 1), ('Limpwurt root', 1)), 'Super strength (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_fletching_potion', 'Fletching potion (3)', "finished", 'standard', 58, 132.0, (('Wergali potion (unf)', 1), ('Wimpy feather', 1)), 'Fletching potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weapon_poison', 'Weapon poison', "finished", 'standard', 60, 137.5, (('Kwuarm potion (unf)', 1), ('Dragon scale dust', 1)), 'Weapon poison', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_restore', 'Super restore (3)', "finished", 'standard', 63, 142.5, (('Snapdragon potion (unf)', 1), ("Red spiders' eggs", 1)), 'Super restore (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_defence', 'Super defence (3)', "finished", 'standard', 66, 150.0, (('Cadantine potion (unf)', 1), ('White berries', 1)), 'Super defence (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_antifire', 'Antifire (3)', "finished", 'standard', 69, 157.5, (('Lantadyme potion (unf)', 1), ('Dragon scale dust', 1)), 'Antifire (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_ranging_potion', 'Ranging potion (3)', "finished", 'standard', 72, 162.5, (('Dwarf weed potion (unf)', 1), ('Wine of zamorak', 1)), 'Ranging potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_magic_potion', 'Magic potion (3)', "finished", 'standard', 76, 172.5, (('Lantadyme potion (unf)', 1), ('Potato cactus', 1)), 'Magic potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_zamorak_brew', 'Zamorak brew (3)', "finished", 'standard', 78, 175.0, (('Torstol potion (unf)', 1), ('Jangerberries', 1)), 'Zamorak brew (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_saradomin_brew', 'Saradomin brew (3)', "finished", 'standard', 81, 180.0, (('Toadflax potion (unf)', 1), ('Crushed nest', 1)), 'Saradomin brew (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_recover_special', 'Recover special (3)', "finished", 'standard', 84, 200.0, (('Super energy (3)', 1), ('Papaya fruit', 1)), 'Recover special (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_antifire', 'Super antifire (3)', "finished", 'standard', 85, 210.0, (('Antifire (3)', 1), ('Phoenix feather', 1)), 'Super antifire (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_extreme_attack', 'Extreme attack (3)', "finished", 'standard', 88, 220.0, (('Super attack (3)', 1), ('Clean avantoe', 1)), 'Extreme attack (3)', source=EXTREME_ATTACK_WIKI_SOURCE),
    HerbloreTarget('finished_extreme_strength', 'Extreme strength (3)', "finished", 'standard', 89, 230.0, (('Super strength (3)', 1), ('Clean dwarf weed', 1)), 'Extreme strength (3)', source=EXTREME_STRENGTH_WIKI_SOURCE),
    HerbloreTarget('finished_extreme_defence', 'Extreme defence (3)', "finished", 'standard', 90, 240.0, (('Super defence (3)', 1), ('Clean lantadyme', 1)), 'Extreme defence (3)', source=EXTREME_DEFENCE_WIKI_SOURCE),
    HerbloreTarget('finished_extreme_magic', 'Extreme magic (3)', "finished", 'standard', 91, 250.0, (('Magic potion (3)', 1), ('Ground mud runes', 1)), 'Extreme magic (3)', source=EXTREME_MAGIC_WIKI_SOURCE),
    HerbloreTarget('finished_extreme_ranging', 'Extreme ranging (3)', "finished", 'standard', 92, 260.0, (('Ranging potion (3)', 1), ('Grenwall spikes', 5)), 'Extreme ranging (3)', source=EXTREME_RANGING_WIKI_SOURCE),
    HerbloreTarget(
        'finished_overload',
        'Overload (3)',
        "finished",
        'standard',
        96,
        1000.0,
        (
            ('Extreme attack (3)', 1),
            ('Extreme strength (3)', 1),
            ('Extreme defence (3)', 1),
            ('Extreme magic (3)', 1),
            ('Extreme ranging (3)', 1),
            ('Clean torstol', 1),
        ),
        'Overload (3)',
        byproducts=(('Vial', 4),),
        source=OVERLOAD_WIKI_SOURCE,
    ),
    HerbloreTarget('finished_super_prayer', 'Super prayer (3)', "finished", 'standard', 94, 270.0, (('Prayer potion (3)', 1), ('Wyvern bonemeal', 1)), 'Super prayer (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_prayer_renewal', 'Prayer renewal (3)', "finished", 'standard', 94, 190.0, (('Fellstalk potion (unf)', 1), ('Morchella mushroom', 1)), 'Prayer renewal (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_agility_mix', 'Agility mix (2)', "finished", 'barbarian', 37, 27.0, (('Agility potion (2)', 1), ('Caviar', 1)), 'Agility mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_attack_mix', 'Attack mix (2)', "finished", 'barbarian', 4, 7.0, (('Attack potion (2)', 1), ('Caviar', 1)), 'Attack mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_antipoison_mix', 'Antipoison mix (2)', "finished", 'barbarian', 6, 12.0, (('Antipoison (2)', 1), ('Caviar', 1)), 'Antipoison mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_antip_supermix', 'Anti-p supermix (2)', "finished", 'barbarian', 51, 35.0, (('Super antipoison (2)', 1), ('Caviar', 1)), 'Anti-p supermix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_antifire_mix', 'Antifire mix (2)', "finished", 'barbarian', 75, 53.0, (('Antifire (2)', 1), ('Caviar', 1)), 'Antifire mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_combat_mix', 'Combat mix (2)', "finished", 'barbarian', 40, 28.0, (('Combat potion (2)', 1), ('Caviar', 1)), 'Combat mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_defence_mix', 'Defence mix (2)', "finished", 'barbarian', 33, 25.0, (('Defence potion (2)', 1), ('Caviar', 1)), 'Defence mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_energy_mix', 'Energy mix (2)', "finished", 'barbarian', 29, 23.0, (('Energy potion (2)', 1), ('Caviar', 1)), 'Energy mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_fishing_mix', 'Fishing mix (2)', "finished", 'barbarian', 53, 38.0, (('Fishing potion (2)', 1), ('Caviar', 1)), 'Fishing mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_hunting_mix', 'Hunting mix (2)', "finished", 'barbarian', 58, 40.0, (('Hunter potion (2)', 1), ('Caviar', 1)), 'Hunting mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_magic_essence_mix', 'Magic essence mix (2)', "finished", 'barbarian', 61, 43.0, (('Magic essence (2)', 1), ('Caviar', 1)), 'Magic essence mix (2)', source="Darkan CraftablePotion.MAGIC_ESSENCE_MIX; cache item 11489 (2011Scape PotionData product is mis-transcribed)"),
    HerbloreTarget('finished_magic_mix', 'Magic mix (2)', "finished", 'barbarian', 83, 57.0, (('Magic potion (2)', 1), ('Caviar', 1)), 'Magic mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_prayer_mix', 'Prayer mix (2)', "finished", 'barbarian', 42, 29.0, (('Prayer potion (2)', 1), ('Caviar', 1)), 'Prayer mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_ranging_mix', 'Ranging mix (2)', "finished", 'barbarian', 80, 54.0, (('Ranging potion (2)', 1), ('Caviar', 1)), 'Ranging mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_relicyms_mix', "Relicym's mix (2)", "finished", 'barbarian', 9, 14.0, (("Relicym's balm (2)", 1), ('Roe', 1)), "Relicym's mix (2)", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_restore_mix', 'Restore mix (2)', "finished", 'barbarian', 24, 21.0, (('Restore potion (2)', 1), ('Roe', 1)), 'Restore mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strength_mix', 'Strength mix (2)', "finished", 'barbarian', 14, 17.0, (('Strength potion (2)', 1), ('Caviar', 1)), 'Strength mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_defence_mix', 'Super defence mix (2)', "finished", 'barbarian', 71, 50.0, (('Super defence (2)', 1), ('Caviar', 1)), 'Super defence mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_energy_mix', 'Super energy mix (2)', "finished", 'barbarian', 56, 39.0, (('Super energy (2)', 1), ('Caviar', 1)), 'Super energy mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_restore_mix', 'Super restore mix (2)', "finished", 'barbarian', 67, 48.0, (('Super restore (2)', 1), ('Caviar', 1)), 'Super restore mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_strength_mix', 'Super strength mix (2)', "finished", 'barbarian', 59, 42.0, (('Super strength (2)', 1), ('Caviar', 1)), 'Super strength mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_super_attack_mix', 'Super attack mix (2)', "finished", 'barbarian', 47, 33.0, (('Super attack (2)', 1), ('Caviar', 1)), 'Super attack mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_zamorak_mix', 'Zamorak mix (2)', "finished", 'barbarian', 85, 58.0, (('Zamorak brew (2)', 1), ('Caviar', 1)), 'Zamorak mix (2)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_juju_hunting', 'Juju hunter potion (3)', "finished", 'juju', 54, 123.0, (('Erzille potion (unf)', 1), ('Corrupt vine', 1)), 'Juju hunter potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_scentless', 'Scentless potion (3)', "finished", 'juju', 59, 135.0, (('Argway potion (unf)', 1), ('Shadow vine', 1)), 'Scentless potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_juju_farming', 'Juju farming potion (3)', "finished", 'juju', 64, 146.0, (('Ugune potion (unf)', 1), ('Marble vine', 1)), 'Juju farming potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_juju_cooking', 'Juju cooking potion (3)', "finished", 'juju', 67, 152.0, (('Shengo potion (unf)', 1), ('Plant teeth', 1)), 'Juju cooking potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_juju_fishing', 'Juju fishing potion (3)', "finished", 'juju', 70, 158.0, (('Shengo potion (unf)', 1), ('Aquatic vine', 1)), 'Juju fishing potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_juju_woodcutting', 'Juju woodcutting potion (3)', "finished", 'juju', 71, 160.0, (('Samaden potion (unf)', 1), ('Oily vine', 1)), 'Juju woodcutting potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_juju_mining', 'Juju mining potion (3)', "finished", 'juju', 74, 168.0, (('Samaden potion (unf)', 1), ('Draconic vine', 1)), 'Juju mining potion (3)', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_saradomin_blessing', "Saradomin's blessing (3)", "finished", 'juju', 75, 179.0, (('Samaden potion (unf)', 1), ('Saradomin vine', 1)), "Saradomin's blessing (3)", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_guthix_gift', "Guthix's gift (3)", "finished", 'juju', 75, 179.0, (('Samaden potion (unf)', 1), ('Guthix vine', 1)), "Guthix's gift (3)", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_zamorak_favour', "Zamorak's favour (3)", "finished", 'juju', 75, 179.0, (('Samaden potion (unf)', 1), ('Zamorak vine', 1)), "Zamorak's favour (3)", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_magic', 'Weak magic potion', "finished", 'dungeoneering', 3, 23.0, (('Sagewort potion (unf)', 1), ('Void dust', 1)), 'Weak magic potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_rejuvenation', 'Weak rejuvenation potion', "finished", 'dungeoneering', 3, 57.0, (('Aloe potion (unf)', 1), ('Misshapen claw', 1)), 'Weak rejuvenation potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_ranged', 'Weak ranged potion', "finished", 'dungeoneering', 5, 34.0, (('Valerian potion (unf)', 1), ('Void dust', 1)), 'Weak ranged potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_melee', 'Weak melee potion', "finished", 'dungeoneering', 7, 37.5, (('Valerian potion (unf)', 1), ('Misshapen claw', 1)), 'Weak melee potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_defence', 'Weak defence potion', "finished", 'dungeoneering', 9, 41.0, (('Aloe potion (unf)', 1), ('Void dust', 1)), 'Weak defence potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_stat_restore', 'Weak stat restore potion', "finished", 'dungeoneering', 12, 47.0, (('Aloe potion (unf)', 1), ('Red moss', 1)), 'Weak stat restore potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_cure', 'Weak cure potion', "finished", 'dungeoneering', 15, 53.5, (('Aloe potion (unf)', 1), ('Firebreath whiskey', 1)), 'Weak cure potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_weapon_poison', 'Weak weapon poison', "finished", 'dungeoneering', 21, 61.0, (('Sagewort potion (unf)', 1), ('Firebreath whiskey', 1)), 'Weak weapon poison', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_gatherer', "Weak gatherer's potion", "finished", 'dungeoneering', 24, 65.0, (('Sagewort potion (unf)', 1), ('Red moss', 1)), "Weak gatherer's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_artisan', "Weak artisan's potion", "finished", 'dungeoneering', 27, 68.5, (('Valerian potion (unf)', 1), ('Red moss', 1)), "Weak artisan's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_naturalist', "Weak naturalist's potion", "finished", 'dungeoneering', 30, 72.0, (('Sagewort potion (unf)', 1), ('Misshapen claw', 1)), "Weak naturalist's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weak_survivalist', "Weak survivalist's potion", "finished", 'dungeoneering', 33, 75.0, (('Valerian potion (unf)', 1), ('Firebreath whiskey', 1)), "Weak survivalist's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_magic', 'Magic potion', "finished", 'dungeoneering', 36, 79.5, (('Wormwood potion (unf)', 1), ('Void dust', 1)), 'Magic potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_ranged', 'Ranged potion', "finished", 'dungeoneering', 38, 83.0, (('Magebane potion (unf)', 1), ('Void dust', 1)), 'Ranged potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_melee', 'Melee potion', "finished", 'dungeoneering', 40, 86.5, (('Magebane potion (unf)', 1), ('Misshapen claw', 1)), 'Melee potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_defence', 'Defence potion', "finished", 'dungeoneering', 42, 89.0, (('Featherfoil potion (unf)', 1), ('Void dust', 1)), 'Defence potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_stat_restore', 'Stat restore potion', "finished", 'dungeoneering', 45, 93.0, (('Featherfoil potion (unf)', 1), ('Red moss', 1)), 'Stat restore potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_cure', 'Cure potion', "finished", 'dungeoneering', 48, 98.5, (('Featherfoil potion (unf)', 1), ('Firebreath whiskey', 1)), 'Cure potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_rejuvenation', 'Rejuvenation potion', "finished", 'dungeoneering', 51, 105.5, (('Featherfoil potion (unf)', 1), ('Misshapen claw', 1)), 'Rejuvenation potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_weapon_p', 'Weapon poison', "finished", 'dungeoneering', 54, 114.0, (('Wormwood potion (unf)', 1), ('Firebreath whiskey', 1)), 'Weapon poison', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_gatherer', "Gatherer's potion", "finished", 'dungeoneering', 57, 123.5, (('Wormwood potion (unf)', 1), ('Red moss', 1)), "Gatherer's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_artisan', "Artisan's potion", "finished", 'dungeoneering', 60, 131.0, (('Magebane potion (unf)', 1), ('Red moss', 1)), "Artisan's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_naturalist', "Naturalist's potion", "finished", 'dungeoneering', 63, 139.5, (('Wormwood potion (unf)', 1), ('Misshapen claw', 1)), "Naturalist's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_survivalist', "Survivalist's potion", "finished", 'dungeoneering', 66, 147.0, (('Magebane potion (unf)', 1), ('Firebreath whiskey', 1)), "Survivalist's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_magic', 'Strong magic potion', "finished", 'dungeoneering', 69, 155.5, (("Winter's grip potion (unf)", 1), ('Void dust', 1)), 'Strong magic potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_ranged', 'Strong ranged potion', "finished", 'dungeoneering', 71, 160.0, (('Lycopus potion (unf)', 1), ('Void dust', 1)), 'Strong ranged potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_melee', 'Strong melee potion', "finished", 'dungeoneering', 73, 164.0, (('Lycopus potion (unf)', 1), ('Misshapen claw', 1)), 'Strong melee potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_defence', 'Strong defence potion', "finished", 'dungeoneering', 75, 170.5, (('Buckthorn potion (unf)', 1), ('Void dust', 1)), 'Strong defence potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_stat_restore', 'Strong stat restore potion', "finished", 'dungeoneering', 78, 173.5, (('Buckthorn potion (unf)', 1), ('Red moss', 1)), 'Strong stat restore potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_cure', 'Strong cure potion', "finished", 'dungeoneering', 81, 178.0, (('Buckthorn potion (unf)', 1), ('Firebreath whiskey', 1)), 'Strong cure potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_rejuvenation', 'Strong rejuvenation potion', "finished", 'dungeoneering', 84, 189.5, (('Buckthorn potion (unf)', 1), ('Misshapen claw', 1)), 'Strong rejuvenation potion', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_weapon_poison', 'Strong weapon poison', "finished", 'dungeoneering', 87, 205.5, (("Winter's grip potion (unf)", 1), ('Firebreath whiskey', 1)), 'Strong weapon poison', source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_gatherer', "Strong gatherer's potion", "finished", 'dungeoneering', 90, 234.0, (("Winter's grip potion (unf)", 1), ('Red moss', 1)), "Strong gatherer's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_artisan', "Strong artisan's potion", "finished", 'dungeoneering', 93, 253.0, (('Lycopus potion (unf)', 1), ('Red moss', 1)), "Strong artisan's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_naturalist', "Strong naturalist's potion", "finished", 'dungeoneering', 96, 279.0, (("Winter's grip potion (unf)", 1), ('Misshapen claw', 1)), "Strong naturalist's potion", source=POTION_DATA_SOURCE_PATH),
    HerbloreTarget('finished_strong_survivalist', "Strong survivalist's potion", "finished", 'dungeoneering', 99, 315.5, (('Lycopus potion (unf)', 1), ('Firebreath whiskey', 1)), "Strong survivalist's potion", source=POTION_DATA_SOURCE_PATH),
)

# HerbData.kt labels these nine herb families as Dungeoneering herbs, and
# PotionData.kt labels all 36 consumers as tier 1-3 Dungeoneering potions. Keep
# the transcribed rows available for a future Daemonheim session catalog, but do
# not expose its temporary-resource economy through ordinary Herblore.
DUNGEONEERING_CLEAN_TARGETS: Tuple[HerbloreTarget, ...] = tuple(
    target for target in _SOURCE_CLEAN_TARGETS if target.subgroup == "dungeoneering"
)
DUNGEONEERING_UNF_TARGETS: Tuple[HerbloreTarget, ...] = tuple(
    target for target in _SOURCE_UNF_TARGETS if target.subgroup == "dungeoneering"
)
DUNGEONEERING_FINISHED_TARGETS: Tuple[HerbloreTarget, ...] = tuple(
    target for target in _SOURCE_FINISHED_TARGETS if target.subgroup == "dungeoneering"
)
DUNGEONEERING_HERBLORE_TARGETS: Tuple[HerbloreTarget, ...] = (
    DUNGEONEERING_CLEAN_TARGETS
    + DUNGEONEERING_UNF_TARGETS
    + DUNGEONEERING_FINISHED_TARGETS
)

CLEAN_TARGETS: Tuple[HerbloreTarget, ...] = tuple(
    target for target in _SOURCE_CLEAN_TARGETS if target.subgroup != "dungeoneering"
)
UNF_TARGETS: Tuple[HerbloreTarget, ...] = tuple(
    target for target in _SOURCE_UNF_TARGETS if target.subgroup != "dungeoneering"
)
FINISHED_TARGETS: Tuple[HerbloreTarget, ...] = tuple(
    target for target in _SOURCE_FINISHED_TARGETS if target.subgroup != "dungeoneering"
)

PESTLE_AND_MORTAR_ACTIVITIES: Tuple[PestleAndMortarActivity, ...] = (
    PestleAndMortarActivity('grind_anchovies', 'Grind anchovies', 'Anchovies', 319, 'Anchovy paste', 11266, 'AnchovyPaste'),
    PestleAndMortarActivity('grind_tchiki_monkey_nuts', 'Grind tchiki monkey nuts', 'Tchiki monkey nuts', 7573, 'Tchiki nut paste', 7575, 'TchikiMonkeyNuts'),
    PestleAndMortarActivity('grind_dramen_branch', 'Grind dramen branch', 'Dramen branch', 771, 'Cinnamon', 7472, 'DramenBranch'),
    PestleAndMortarActivity('grind_garlic', 'Grind garlic', 'Garlic', 1550, 'Garlic powder', 4668, 'Garlic'),
    PestleAndMortarActivity('grind_astral_rune_shards', 'Grind astral rune shards', 'Astral rune shards', 11156, 'Ground astral rune', 11155, 'AstralRuneShards'),
    PestleAndMortarActivity('grind_bat_bones', 'Grind bat bones', 'Bat bones', 530, 'Ground bat bones', 2391, 'BatBones'),
    PestleAndMortarActivity('grind_charcoal', 'Grind charcoal', 'Charcoal', 973, 'Ground charcoal', 704, 'Charcoal'),
    PestleAndMortarActivity('grind_clean_guam', 'Grind clean guam', 'Clean guam', 249, 'Ground guam', 6681, 'Guam'),
    PestleAndMortarActivity('grind_crab_meat', 'Grind crab meat', 'Crab meat', 7518, 'Ground crab meat', 7527, 'CrabMeat'),
    PestleAndMortarActivity('grind_raw_cod', 'Grind raw cod', 'Raw cod', 341, 'Ground cod', 7528, 'Cod'),
    PestleAndMortarActivity('grind_suqah_tooth', 'Grind suqah tooth', 'Suqah tooth', 9079, 'Ground tooth', 9082, 'SuqahTooth'),
    PestleAndMortarActivity('grind_kelp', 'Grind kelp', 'Kelp', 7516, 'Ground kelp', 7517, 'Kelp'),
    PestleAndMortarActivity('grind_rune_shards', 'Grind rune shards', 'Rune shards', 6466, 'Rune dust', 6467, 'RuneShards'),
    PestleAndMortarActivity('grind_dried_thistle', 'Grind dried thistle', 'Dried thistle', 3263, 'Ground thistle', 3264, 'DriedThistle'),
    PestleAndMortarActivity('grind_gorak_claws', 'Grind gorak claws', 'Gorak claws', 9016, 'Gorak claw powder', 9018, 'GorakClaw'),
    PestleAndMortarActivity('grind_ashes', 'Grind ashes', 'Ashes', 592, 'Ground ashes', 8865, 'Ashes'),
    PestleAndMortarActivity('grind_raw_karambwan', 'Grind raw karambwan', 'Raw karambwan', 3142, 'Karambwan paste', 3152, 'RawKarambwan'),
    PestleAndMortarActivity('grind_cooked_karambwan', 'Grind cooked karambwan', 'Cooked karambwan', 3144, 'Karambwan paste', 3154, 'CookedKarambwan'),
    PestleAndMortarActivity('grind_poison_karambwan', 'Grind poison karambwan', 'Poison karambwan', 3146, 'Karambwan paste', 3153, 'PoisonKarambwan'),
    PestleAndMortarActivity('grind_diamond_root', 'Grind diamond root', 'Diamond root', 14703, 'Diamond root dust', 14704, 'DiamondRoot'),
    PestleAndMortarActivity('grind_black_mushroom', 'Grind black mushroom', 'Black mushroom', 4620, 'Black mushroom ink', 4622, 'BlackMushroom'),
    PestleAndMortarActivity('grind_shards_of_armadyl', 'Grind shards of armadyl', 'Shards of armadyl', 21776, 'Dust of armadyl', 21774, 'ShardOfArmadyl'),
    PestleAndMortarActivity('grind_fishing_bait', 'Grind fishing bait', 'Fishing bait', 313, 'Ground fishing bait', 12129, 'FishingBait'),
    PestleAndMortarActivity('grind_seaweed', 'Grind seaweed', 'Seaweed', 401, 'Ground seaweed', 6683, 'SeaWeed'),
)

INPUT_PREPARATION_ACTIVITIES: Tuple[InputPreparationActivity, ...] = (
    InputPreparationActivity(
        'fill_vial_of_water',
        'Fill vial with water',
        'Vial',
        229,
        'Vial of water',
        227,
        f'{WATER_CONTAINER_SOURCE_PATH}: WaterContainerData.VIAL_OF_WATER; {FILL_WATER_SOURCE_PATH}',
    ),
    InputPreparationActivity(
        'remove_swamp_toad_legs',
        "Remove swamp toad's legs",
        'Swamp toad',
        2150,
        "Toad's legs",
        2152,
        f'{SWAMP_TOAD_SOURCE_PATH}: Remove-legs',
    ),
)

HERBLORE_TARGETS: Tuple[HerbloreTarget, ...] = CLEAN_TARGETS + UNF_TARGETS + FINISHED_TARGETS
HERBLORE_TARGETS_BY_ID: Dict[str, HerbloreTarget] = {t.id: t for t in HERBLORE_TARGETS}
_REGISTERED_HERBLORE_TARGETS: Tuple[HerbloreTarget, ...] = (
    HERBLORE_TARGETS + DUNGEONEERING_HERBLORE_TARGETS
)

HERBLORE_GROUP_LABELS: Dict[str, str] = {
    "clean": "Clean herbs",
    "unf": "Unfinished potions",
    "finished": "Finished potions",
}

# Item 6810 is Super prayer's distinct Wyvern-bonemeal secondary. Herblore
# registers the identity here without adding a migration or acquisition route.
_HERBLORE_UNCACHED_ITEMS = ("Wyvern bonemeal",)


def _target_as_dict(target: HerbloreTarget) -> Dict[str, object]:
    return {
        "id": target.id,
        "display_name": target.display_name,
        "group": target.group,
        "subgroup": target.subgroup,
        "level": target.level,
        "exp": target.exp,
        "requirements": {name: qty for name, qty in target.requirements},
        "output_item": target.output_item,
        "output_qty": target.output_qty,
        "byproducts": {name: qty for name, qty in target.byproducts},
        "source": target.source,
    }


def herblore_targets_as_dict() -> Dict[str, Dict[str, object]]:
    return {t.id: _target_as_dict(t) for t in HERBLORE_TARGETS}


def herblore_output_items() -> Tuple[str, ...]:
    return tuple(dict.fromkeys(t.output_item for t in HERBLORE_TARGETS))


def herblore_finished_output_items() -> Tuple[str, ...]:
    """Only the finished-potion products (group == "finished"), excluding the
    clean-herb and unfinished-potion intermediates, for the "mix a potion"
    achievements."""
    return tuple(
        dict.fromkeys(t.output_item for t in HERBLORE_TARGETS if t.group == "finished")
    )


def herblore_item_names() -> Tuple[str, ...]:
    """Every item the skill references: grimy/clean/unf herbs, secondaries,
    products, and Vial of water.

    Deferred Daemonheim items stay registered so existing inventory quantities
    remain typed and visible when old saves are loaded, even though their action
    targets are absent from the ordinary Herblore catalog.
    """
    names = []
    for t in _REGISTERED_HERBLORE_TARGETS:
        names.append(t.output_item)
        names.extend(name for name, _qty in t.requirements)
        names.extend(name for name, _qty in t.byproducts)
    for activity in PESTLE_AND_MORTAR_ACTIVITIES:
        names.extend((activity.source_item, activity.output_item))
    for activity in INPUT_PREPARATION_ACTIVITIES:
        names.extend((activity.source_item, activity.output_item))
    names.extend(_HERBLORE_UNCACHED_ITEMS)
    return tuple(dict.fromkeys(names))


def pestle_and_mortar_activities_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        activity.id: {
            "display_name": activity.display_name,
            "requirements": {activity.source_item: 1},
            "output_item": activity.output_item,
            "output_qty": 1,
            "batch_size": 28,
            "group": "grinding",
            "source_item_id": activity.source_item_id,
            "output_item_id": activity.output_item_id,
            "source": activity.source,
        }
        for activity in PESTLE_AND_MORTAR_ACTIVITIES
    }


def input_preparation_activities_as_dict() -> Dict[str, Dict[str, object]]:
    return {
        activity.id: {
            "display_name": activity.display_name,
            "requirements": {activity.source_item: 1},
            "output_item": activity.output_item,
            "output_qty": 1,
            "batch_size": 28,
            "group": "input_preparation",
            "source_item_id": activity.source_item_id,
            "output_item_id": activity.output_item_id,
            "source": activity.source,
        }
        for activity in INPUT_PREPARATION_ACTIVITIES
    }


def herblore_extra_items_as_dict() -> Dict[str, Dict[str, object]]:
    """Register every herblore item name (category material). Items already
    registered by another system dedupe by storage key at build time, so this
    introduces the herblore-native herbs, unfinished potions, and products.
    Deferred Daemonheim identities remain here for save compatibility."""
    pestle_item_ids = {
        item_name: item_id
        for activity in PESTLE_AND_MORTAR_ACTIVITIES
        for item_name, item_id in (
            (activity.source_item, activity.source_item_id),
            (activity.output_item, activity.output_item_id),
        )
    }
    input_preparation_item_data = {
        item_name: (item_id, activity.source)
        for activity in INPUT_PREPARATION_ACTIVITIES
        for item_name, item_id in (
            (activity.source_item, activity.source_item_id),
            (activity.output_item, activity.output_item_id),
        )
    }
    canonical_item_ids = {
        "Agility potion (3)": 3034,
        "Agility potion (2)": 3036,
        "Agility mix (2)": 11461,
        "Shrink-me-quick": 11204,
        "Shrunk ogleroot": 11205,
    }
    result = {}
    for name in herblore_item_names():
        item = {
            "display_name": name,
            "output_item": name,
            "level": 1,
            "exp": 0.0,
            "source": (
                PESTLE_AND_MORTAR_SOURCE_PATH
                if name in pestle_item_ids
                else input_preparation_item_data.get(name, (0, HERB_DATA_SOURCE_PATH))[1]
            ),
            "category": "material",
            "tradeable": True,
        }
        if name in pestle_item_ids:
            item["item_id"] = pestle_item_ids[name]
        elif name in input_preparation_item_data:
            item["item_id"] = input_preparation_item_data[name][0]
        elif name == "Wyvern bonemeal":
            item["item_id"] = 6810
        elif name == "Overload (3)":
            item["item_id"] = 15333
            item["tradeable"] = False
        elif name == "Magic essence mix (2)":
            item["item_id"] = 11489
        elif name == "Shrink-me-quick":
            item["tradeable"] = False
            item["stackable"] = False
        elif name == "Shrunk ogleroot":
            item["stackable"] = True
        elif name.startswith("Juju farming potion ("):
            dose = int(name.removeprefix("Juju farming potion (").removesuffix(")"))
            item["item_id"] = {1: 20014, 2: 20013, 3: 20012, 4: 20011}[dose]
        elif name in {
            "Extreme attack (3)",
            "Extreme strength (3)",
            "Extreme defence (3)",
            "Extreme magic (3)",
            "Extreme ranging (3)",
        }:
            item["tradeable"] = False
        if name in canonical_item_ids:
            item["item_id"] = canonical_item_ids[name]
        result[name] = item
    for dose, item_id in {1: 20014, 2: 20013, 3: 20012, 4: 20011}.items():
        name = f"Juju farming potion ({dose})"
        result.setdefault(name, {
            "display_name": name,
            "output_item": name,
            "level": 1,
            "exp": 0.0,
            "source": "Darkan item config: Juju farming potion dose family",
            "category": "material",
            "tradeable": True,
            "item_id": item_id,
        })
    return result
