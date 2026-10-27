"""Three Al Kharid/Varrock searches: exact catalog, ordinary flow and saves."""

import ast
import copy
import hashlib
import json
from pathlib import Path
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core import constants
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data import treasure_trails_data as catalog
from ankiscape.logic import treasure_trails_logic as trails

ROOT = Path(__file__).resolve().parents[2]
CLUE = "Clue scroll (easy)"
CASKET = "Casket (easy)"
SAILOR = "simple_port_sarim_sailor"
EXPECTED_TOTAL = 33

EXPECTED_SOURCE = 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 (2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'

BASELINE = ({'step_id': 'simple_port_sarim_sailor',
  'kind': 'simple',
  'text': 'One of the sailors in Port Sarim is your next destination.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_varrock_palace_crate',
  'kind': 'simple',
  'text': 'Search for a crate in Varrock Palace.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_lumbridge_goblin_house',
  'kind': 'simple',
  'text': 'Search the boxes in the Goblin house near Lumbridge.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_grand_tree_mushrooms',
  'kind': 'simple',
  'text': 'Dig near some giant mushrooms behind the Grand Tree.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'map_clock_tower_crates',
  'kind': 'map',
  'text': 'Map: crates stacked behind the Clock tower building south of Ardougne Castle.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'map_lumberyard_crate',
  'kind': 'map',
  'text': 'Map: the crate in the storage area behind the Lumberyard sawmill operator, north-east of Varrock.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'emote_duel_arena_bow',
  'kind': 'emote',
  'text': 'Bow or curtsy in the lobby of the Duel Arena. Equip an iron chainbody, leather chaps and a coif.',
  'equipment': ('Iron chainbody', 'Leather chaps', 'Coif'),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'emote_port_sarim_cheer',
  'kind': 'emote',
  'text': 'Cheer for the monks at Port Sarim. Equip a coif, steel plateskirt and a sapphire necklace.',
  'equipment': ('Coif', 'Steel plateskirt', 'Sapphire necklace'),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'emote_burthorpe_games_room_cheer',
  'kind': 'emote',
  'text': 'Cheer at the Burthorpe Games Room. Have nothing equipped at all when you do.',
  'equipment': (),
  'bare': True,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_lumbridge_hans',
  'kind': 'simple',
  'text': 'Speak to Hans.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_camelot_sir_kay',
  'kind': 'simple',
  'text': 'Speak to Sir Kay in Camelot Castle.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_varrock_blue_moon_bartender',
  'kind': 'simple',
  'text': 'Speak to the bartender of the Blue Moon Inn in Varrock.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_port_sarim_rusty_anchor_bartender',
  'kind': 'simple',
  'text': 'Talk to the bartender of the Rusty Anchor in Port Sarim.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_falador_squire',
  'kind': 'simple',
  'text': "Talk to the Squire in the White Knights' castle in Falador.",
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_al_kharid_zeke',
  'kind': 'simple',
  'text': 'Talk to Zeke in Al Kharid.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_sinclair_mansion_donovan',
  'kind': 'simple',
  'text': 'Speak to Donovan the Family Handyman.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_sinclair_mansion_staff',
  'kind': 'simple',
  'text': 'Speak to the staff of Sinclair Mansion.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_falador_general_store_crates',
  'kind': 'simple',
  'text': "Search the crates of Falador's general store.",
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_lumbridge_duke_bedroom_chest',
  'kind': 'simple',
  'text': "Search the chest in the Duke of Lumbridge's bedroom.",
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_draynor_manor_crates',
  'kind': 'simple',
  'text': 'Search the crates in Draynor Manor.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_varrock_horvik_armoury_crates',
  'kind': 'simple',
  'text': "Search the crates in Horvik's armoury.",
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_port_sarim_fishing_shop_crates',
  'kind': 'simple',
  'text': 'Search the crates in the Port Sarim fishing shop.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_catherby_archery_shop_drawers',
  'kind': 'simple',
  'text': "Search the drawers in Catherby's Archery Shop.",
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_hemenster_crate',
  'kind': 'simple',
  'text': 'Search for a crate in a building in Hemenster.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_seers_village_ground_floor_crate',
  'kind': 'simple',
  'text': "Search for a crate on the ground floor of a house in Seers' Village.",
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_varrock_south_entrance_boxes',
  'kind': 'simple',
  'text': 'Search the boxes in the house near the South entrance of Varrock.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_east_ardougne_armour_shop_boxes',
  'kind': 'simple',
  'text': 'Search the boxes just outside the Armour shop in east Ardougne.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_camelot_left_tower_chest',
  'kind': 'simple',
  'text': 'Search the chest in the left-hand tower of Camelot castle.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_dwarven_mine_chests',
  'kind': 'simple',
  'text': 'Search the chests in the Dwarven Mine.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'},
 {'step_id': 'simple_port_khazard_cart_crate',
  'kind': 'simple',
  'text': 'Search the crate near a cart in Port Khazard.',
  'equipment': (),
  'bare': False,
  'source': 'RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); Clue scroll (easy) '
            'oldid=6333359 (2012-10-02T09:39:55Z); Treasure Trails/Guide/Simple clues oldid=6579176 '
            '(2012-11-18T16:48:49Z); Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); '
            'Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); Darkan '
            'TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json'})

PRIOR_ASSIGNMENTS = (('simple_lumbridge_hans', 'Speak to Hans.'),
 ('simple_camelot_sir_kay', 'Speak to Sir Kay in Camelot Castle.'),
 ('simple_varrock_blue_moon_bartender', 'Speak to the bartender of the Blue Moon Inn in Varrock.'),
 ('simple_port_sarim_rusty_anchor_bartender', 'Talk to the bartender of the Rusty Anchor in Port Sarim.'),
 ('simple_falador_squire', "Talk to the Squire in the White Knights' castle in Falador."),
 ('simple_al_kharid_zeke', 'Talk to Zeke in Al Kharid.'),
 ('simple_duel_arena_jeed', 'Someone watching the fights in the duel arena is your next destination.'),
 ('simple_catherby_arhein', 'Speak to Arhein in Catherby.'),
 ('simple_falador_doric', 'Speak to Doric who lives north of Falador.'),
 ('simple_al_kharid_ellis', 'Speak to Ellis in Al Kharid.'),
 ('simple_burthorpe_gaius', 'Speak to Gaius in Burthorpe.'),
 ('simple_draynor_ned', 'Speak to Ned in Draynor Village.'),
 ('simple_sinclair_mansion_donovan', 'Speak to Donovan the Family Handyman.'),
 ('simple_sinclair_mansion_staff', 'Speak to the staff of Sinclair Mansion.'),
 ('simple_falador_general_store_crates', "Search the crates of Falador's general store."),
 ('simple_lumbridge_duke_bedroom_chest', "Search the chest in the Duke of Lumbridge's bedroom."),
 ('simple_draynor_manor_crates', 'Search the crates in Draynor Manor.'),
 ('simple_varrock_horvik_armoury_crates', "Search the crates in Horvik's armoury."),
 ('simple_port_sarim_fishing_shop_crates', 'Search the crates in the Port Sarim fishing shop.'),
 ('simple_catherby_archery_shop_drawers', "Search the drawers in Catherby's Archery Shop."),
 ('simple_hemenster_crate', 'Search for a crate in a building in Hemenster.'),
 ('simple_seers_village_ground_floor_crate',
  "Search for a crate on the ground floor of a house in Seers' Village."),
 ('simple_varrock_south_entrance_boxes', 'Search the boxes in the house near the South entrance of Varrock.'),
 ('simple_east_ardougne_armour_shop_boxes',
  'Search the boxes just outside the Armour shop in east Ardougne.'),
 ('simple_camelot_left_tower_chest', 'Search the chest in the left-hand tower of Camelot castle.'),
 ('simple_dwarven_mine_chests', 'Search the chests in the Dwarven Mine.'),
 ('simple_port_khazard_cart_crate', 'Search the crate near a cart in Port Khazard.'),
 ('simple_east_ardougne_church_tower_crate', 'A crate found in the tower of a church is your next location.'),
 ('simple_falador_east_bank_house_crates', 'Look in the ground floor crates of houses in Falador.'),
 ('simple_port_sarim_food_shop_upstairs_chests',
  'Search chests found in the upstairs of shops in Port Sarim.'),
 ('simple_al_kharid_tent_boxes', 'Search the boxes in one of the tents in Al Kharid.'),
 ('simple_lumbridge_left_hand_tower_crate', 'Search the crate in the left-hand tower of Lumbridge castle.'),
 ('simple_yanille_piano_house_crates', 'Search the crates in a house in Yanille that has a piano.'),
 ('simple_east_ardougne_general_store_crates', "Search the crates in East Ardougne's general store."),
 ('simple_gunnarsgrunn_helmet_shop_crates',
  'Search the crates in Gunnarsgrunn (Barbarian Village) helmet shop.'),
 ('simple_burthorpe_combat_training_barrel',
  'Search a barrel near the Combat Skill Master at the combat training area, in Burthorpe.'),
 ('simple_taverley_pick_and_lute_barrel', 'Search a barrel outside the Pick and Lute inn, in Taverley.'),
 ('simple_taverley_mill_barrel', 'Search a barrel outside the mill, in Taverley.'),
 ('simple_falador_artisan_workshop_basement',
  "Search in the basement of the Artisan Dwarves' workshop in Falador."),
 ('simple_taverley_sword_shop_crates', 'Search the crates in a shop in Taverley.'),
 ('simple_canifis_meat_shop_crates', 'Search the crates in Canifis.'),
 ('simple_east_ardougne_north_guard_house_crates',
  'Search the crates in the guard house of the northern gate of East Ardougne.'),
 ('simple_east_ardougne_north_shed_crates', 'Search the crates in the shed just north of east Ardougne.'),
 ('simple_varrock_shops_upstairs_drawers', "Search the drawers above Varrock's shops."),
 ('simple_east_ardougne_houses_upstairs_drawers',
  'Search the drawers found upstairs in the houses of East Ardougne.'),
 ('simple_draynor_village_house_drawers', 'Search the drawers in a house in Draynor Village.'),
 ('simple_falador_chainmail_shop_drawers', "Search the drawers in Falador's chainmail shop."),
 ('simple_gertrude_bedroom_drawers', "Search the drawers in one of Gertrude's bedrooms."),
 ('simple_yanille_ground_floor_shop_drawers', 'Search the drawers in the ground floor of a shop in Yanille.'),
 ('simple_catherby_house_upstairs_drawers', 'Search the drawers in the upstairs of a house in Catherby.'),
 ('simple_varrock_east_bank_upstairs_drawers',
  'Search the drawers upstairs in the bank to the East of Varrock.'),
 ('simple_burthorpe_house_drawers', 'Search the drawers of houses in Burthorpe.'),
 ('simple_ardougne_market_overlooking_drawers',
  'Search the drawers on the first floor of a building overlooking Ardougne market.'),
 ('simple_falador_shield_shop_upstairs_drawers', "Search the drawers upstairs in Falador's shield shop."),
 ('simple_east_falador_upstairs_drawers',
  'Search the drawers upstairs of houses in eastern part of Falador.'),
 ('simple_burthorpe_imperial_guard_tent_boxes',
  'Search the tents in the imperial guard camp in Burthorpe for some boxes.'),
 ('simple_east_falador_upstairs_chests',
  'Search through chests found in the upstairs of houses in eastern Falador.'),
 ('simple_taverley_house_drawers', "Search through some drawers found in Taverley's houses."),
 ('simple_rimmington_upstairs_drawers',
  'Search through some drawers in the upstairs of a house in Rimmington.'),
 ('simple_seers_village_upstairs_drawers',
  "Search upstairs in the houses of Seers' Village for some drawers."))

NEW_ROWS = (('simple_al_kharid_palace_chests', 'Search the chests upstairs in Al Kharid palace.'), ('simple_al_kharid_northernmost_house_crates', 'Search the crates in the northernmost house in Al Kharid.'), ('simple_varrock_cart_crates', 'Search the crates near a cart in Varrock.'))

ASSET_RECEIPT = (('activityicons/treasure_trail.png',
  'b4a46740be3354a77543cfed31eb5b2756ebd74fb6c3a57c69cd808cc3c0bee0',
  {'file_page_url': 'https://runescape.wiki/wiki/File:Mg_treasuretrails.jpg',
   'file_title': 'Mg treasuretrails.jpg',
   'image_url': 'https://runescape.wiki/images/Mg_treasuretrails.jpg?de6ba',
   'license_string': 'unknown',
   'mediatype': 'BITMAP',
   'mime': 'image/jpeg',
   'sha1': '8ff0d3877e1cba096b981d16a92f826b99164fbb',
   'size': 2678,
   'source_wiki': 'rs3',
   'timestamp': '2008-07-28T14:53:49Z'}),
 ('activityitems/casket_easy.png',
  'a4f404b09451717e98434baa18564747af28d87d72eaf74f97e1b25dab73123a',
  {'file_page_url': 'https://runescape.wiki/wiki/File:Casket.png',
   'file_title': 'Casket.png',
   'image_url': 'https://runescape.wiki/images/archive/20140511081506%21Casket.png?fc642',
   'license_string': 'unknown',
   'mediatype': 'BITMAP',
   'mime': 'image/png',
   'sha1': '2a6827c6747909115aea6ca8479cbc68b43e8b00',
   'size': 627,
   'source_wiki': 'rs3',
   'timestamp': '2010-10-04T04:04:13Z'}),
 ('combatitems/clue_scroll_easy.png',
  '9ec85a114b04bf018311457874f959f8b64eb7b13a3abba52f5bf4815fcc7278',
  {'file_page_url': 'https://oldschool.runescape.wiki/wiki/File:Clue_scroll_%28easy%29.png',
   'file_title': 'Clue scroll (easy).png',
   'image_url': 'https://oldschool.runescape.wiki/images/Clue_scroll_%28easy%29.png?e29cd',
   'license_string': 'unknown',
   'mediatype': 'BITMAP',
   'mime': 'image/png',
   'sha1': 'e94b0fe55f7371cfabf60e60c11c650b3148d0a0',
   'size': 477,
   'source_wiki': 'osrs',
   'timestamp': '2019-04-11T12:15:25Z'}))

SEARCH_ROWS = (
    ("simple_hemenster_crate", "Search for a crate in a building in Hemenster."),
    ("simple_seers_village_ground_floor_crate", "Search for a crate on the ground floor of a house in Seers' Village."),
    ("simple_varrock_south_entrance_boxes", "Search the boxes in the house near the South entrance of Varrock."),
    ("simple_east_ardougne_armour_shop_boxes", "Search the boxes just outside the Armour shop in east Ardougne."),
    ("simple_camelot_left_tower_chest", "Search the chest in the left-hand tower of Camelot castle."),
    ("simple_dwarven_mine_chests", "Search the chests in the Dwarven Mine."),
    ("simple_port_khazard_cart_crate", "Search the crate near a cart in Port Khazard."),
)


def finite_draws(values):
    """Unexpected generation/reward draws fail instead of silently repeating."""
    stream = iter(values)
    return lambda: next(stream)


def fresh_player():
    save = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
    save.update(inventory={CLUE: 1, 'Coins': 73, 'Logs': 4}, equipment={},
                treasure_trail={}, treasure_trail_retained={},
                activity_session={'active_id': ''})
    return migrate_loaded_data(save, constants.ORE_DATA, constants.ITEM_DEFINITIONS)


def selection_draws(step_ids):
    keys = list(catalog.TREASURE_TRAILS_EASY_STEPS)
    return finite_draws((0.0 if len(step_ids) == 1 else 0.25,) + tuple(
        (keys.index(step_id) + 0.5) / EXPECTED_TOTAL for step_id in step_ids
    ))


def command(test, save, action, rng=None):
    before = copy.deepcopy(save)
    result, ok, info = trails.apply_treasure_trails_command_pure(
        save, action, {'tier': 'easy'}, rng
    )
    test.assertTrue(ok, info)
    test.assertEqual(save, before)
    return result


def generate(test, step_ids):
    held = fresh_player()
    test.assertEqual(held['treasure_trail'], {})
    test.assertEqual(held['treasure_trail_retained'], {})
    test.assertEqual(held['activity_session'], {'active_id': ''})
    save = command(test, held, 'start_from_bank', selection_draws(step_ids))
    test.assertEqual(save['treasure_trail'], {
        'version': 1, 'tier': 'easy', 'steps': list(step_ids), 'index': 0,
    })
    test.assertEqual(save['inventory'], held['inventory'])
    test.assertEqual(save['treasure_trails_started'], 1)
    test.assertEqual(save['activity_session'], {'active_id': 'treasure_trail'})
    test.assertEqual(save['current_utility'], 'treasure_trail')
    return save


def resolve(test, save, terminal=False):
    before = copy.deepcopy(save)
    result, ok, info = trails.apply_treasure_trail_review_pure(save)
    test.assertTrue(ok, info)
    test.assertEqual(info['terminal'], terminal)
    test.assertFalse(info['blocked'])
    test.assertEqual(save, before)
    return result


def assert_terminal(test, save):
    expected = fresh_player()['inventory']
    expected.pop(CLUE)
    expected[CASKET] = 1
    test.assertEqual(save['inventory'], expected)
    test.assertEqual(save['treasure_trail'], {})
    test.assertEqual(save['treasure_trail_retained'], {})
    test.assertEqual(save['activity_session'], {'active_id': ''})
    test.assertEqual(save['treasure_trails_started'], 1)
    test.assertEqual(save['treasure_trails_completed'], 1)
    test.assertEqual(save['treasure_trails_caskets_opened'], 0)


def reopen(save):
    return migrate_loaded_data(json.loads(json.dumps(save)), constants.ORE_DATA,
                               constants.ITEM_DEFINITIONS)


def assert_persisted(test, before, after):
    for key in ('treasure_trail', 'treasure_trail_retained', 'inventory',
                'activity_session', 'current_utility', 'treasure_trails_started',
                'treasure_trails_completed', 'treasure_trails_caskets_opened',
                'treasure_trails_last_result'):
        test.assertEqual(after[key], before[key], key)


class ThreeSearchesTest(unittest.TestCase):
    def test_exact_registry_extension(self):
        expected = list(BASELINE) + [
            dict(step_id=step_id, kind='simple', text=text, equipment=(),
                 bare=False, source=EXPECTED_SOURCE) for step_id, text in NEW_ROWS
        ]
        registry = catalog.TREASURE_TRAILS_EASY_STEPS
        self.assertEqual(len(BASELINE), 30)
        self.assertEqual(len(registry), 33)
        self.assertEqual(list(registry), [row['step_id'] for row in expected])
        self.assertEqual(list(registry.values()), expected)
        module = ast.parse(Path(catalog.__file__).read_text())
        assignment = next(node for node in module.body if isinstance(node, ast.AnnAssign)
                          and getattr(node.target, 'id', '') == 'TREASURE_TRAILS_EASY_STEPS')
        calls = assignment.value.generators[0].iter.elts
        raw_ids = [ast.literal_eval(call.args[0]) for call in calls]
        self.assertEqual(len(raw_ids), 33)
        self.assertEqual(raw_ids, list(registry))
        self.assertEqual(len(raw_ids), len(set(raw_ids)))
        self.assertEqual(len(PRIOR_ASSIGNMENTS), 60)
        for step_id, text in NEW_ROWS:
            with self.subTest(step_id=step_id):
                self.assertNotIn(step_id, dict(PRIOR_ASSIGNMENTS))
                self.assertNotIn(text, dict(PRIOR_ASSIGNMENTS).values())
                self.assertEqual([row['text'] for row in registry.values()].count(text), 1)

    def test_each_search_is_selected_and_displayed_by_bank_start(self):
        for step_id, text in NEW_ROWS:
            with self.subTest(step_id=step_id):
                save = generate(self, [step_id])
                view = trails.treasure_trails_view_pure(save)['step']
                self.assertEqual(view['step_id'], step_id)
                self.assertEqual(view['text'], text)
                self.assertEqual((view['number'], view['total']), (1, 1))
                self.assertEqual(view['blocked_reason'], '')

    def test_each_search_advances_once_then_earns_a_casket(self):
        for step_id, _ in NEW_ROWS:
            with self.subTest(step_id=step_id):
                save = generate(self, [step_id, SAILOR])
                advanced = resolve(self, save)
                self.assertEqual(advanced['treasure_trail'], {
                    **save['treasure_trail'], 'index': 1,
                })
                self.assertEqual(advanced['inventory'], save['inventory'])
                self.assertEqual(advanced['activity_session'], save['activity_session'])
                self.assertEqual(advanced['treasure_trails_completed'], 0)
                self.assertEqual(advanced['treasure_trails_caskets_opened'], 0)
                assert_terminal(self, resolve(self, advanced, terminal=True))

    def test_each_terminal_search_consumes_the_scroll_and_settles_its_earned_casket(self):
        for step_id, _ in NEW_ROWS:
            with self.subTest(step_id=step_id):
                completed = resolve(self, generate(self, [step_id]), terminal=True)
                assert_terminal(self, completed)
                opened = command(self, completed, 'open_casket',
                                 finite_draws((0.0, 0.99, 0.0, 0.0, 0.99, 0.0, 0.0)))
                expected = dict(completed['inventory'])
                expected.pop(CASKET)
                expected['Coins'] += 100
                self.assertEqual(opened['inventory'], expected)
                self.assertEqual(opened['treasure_trails_caskets_opened'], 1)
                self.assertEqual(opened['treasure_trails_completed'], 1)

    def test_new_active_and_retained_progress_survives_saved_reopen(self):
        def unexpected_draw():
            raise AssertionError('Retained progress must resume without rerolling')

        for step_id, _ in NEW_ROWS:
            with self.subTest(step_id=step_id):
                active = resolve(self, generate(self, [SAILOR, step_id]))
                loaded = reopen(active)
                assert_persisted(self, active, loaded)
                self.assertEqual(loaded['treasure_trail']['index'], 1)
                self.assertEqual(loaded['treasure_trail']['steps'], [SAILOR, step_id])
                abandoned = command(self, loaded, 'abandon')
                retained = reopen(abandoned)
                assert_persisted(self, abandoned, retained)
                resumed = command(self, retained, 'start_from_bank', unexpected_draw)
                self.assertEqual(resumed['treasure_trail'], active['treasure_trail'])
                self.assertEqual(resumed['treasure_trail_retained'], {})
                self.assertEqual(resumed['treasure_trails_started'], 1)

    def test_preexisting_active_and_retained_ids_survive_saved_reopen(self):
        for row in BASELINE:
            for retained in (False, True):
                for version in (fresh_player()['config_version'], 82):
                    with self.subTest(step_id=row['step_id'], retained=retained, version=version):
                        self.assert_old_reopen(row['step_id'], retained, version)

    def assert_old_reopen(self, step_id, retained, version):
        save = fresh_player()
        save['config_version'] = version
        trail = {'version': 1, 'tier': 'easy', 'steps': [SAILOR, step_id], 'index': 1}
        key = 'treasure_trail_retained' if retained else 'treasure_trail'
        save[key] = trail
        if not retained:
            save['activity_session'] = {'active_id': 'treasure_trail'}
            save['current_utility'] = 'treasure_trail'
        loaded = reopen(save)
        self.assertEqual(loaded[key], trail)
        other = 'treasure_trail' if retained else 'treasure_trail_retained'
        self.assertEqual(loaded[other], {})

    def test_existing_art_paths_bindings_and_provenance(self):
        bindings = {
            'activityicons/treasure_trail.png': constants.UTILITY_ACTIVITY_DATA['treasure_trail']['icon_path'],
            'combatitems/clue_scroll_easy.png': constants.COMBAT_ITEM_IMAGES[CLUE],
            'activityitems/casket_easy.png': constants.TREASURE_TRAILS_ITEM_IMAGES[CASKET],
        }
        provenance = json.loads((ROOT / 'assets_provenance.json').read_text())
        # Frozen complete receipt entries; the OSRS scroll upload is post-cutoff art.
        for relative, digest, entry in ASSET_RECEIPT:
            with self.subTest(asset=relative):
                path = ROOT / relative
                self.assertEqual(Path(bindings[relative]).resolve(), path.resolve())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                self.assertEqual(provenance[relative], entry)
