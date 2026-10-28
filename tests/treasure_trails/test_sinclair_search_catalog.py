"""Sinclair and search clues preserve the catalog, Bank flow and saved trails."""

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core import constants
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.treasure_trails_data import TREASURE_TRAILS_EASY_STEPS
from ankiscape.logic import treasure_trails_logic as trails
from tests import test_storage_runtime as storage_fixture
from tests.test_treasure_trails import _draws
from tests.treasure_trails.test_three_searches import SEARCH_ROWS, NEW_ROWS

EXPECTED_SOURCE = (
    "RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); "
    "Clue scroll (easy) oldid=6333359 (2012-10-02T09:39:55Z); "
    "Treasure Trails/Guide/Simple clues oldid=6579176 (2012-11-18T16:48:49Z); "
    "Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); "
    "Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); "
    "Darkan TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json"
)

BASELINE_EXPECTED = {
    "simple_port_sarim_sailor": {
        "step_id": "simple_port_sarim_sailor",
        "kind": "simple",
        "text": "One of the sailors in Port Sarim is your next destination.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_varrock_palace_crate": {
        "step_id": "simple_varrock_palace_crate",
        "kind": "simple",
        "text": "Search for a crate in Varrock Palace.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_lumbridge_goblin_house": {
        "step_id": "simple_lumbridge_goblin_house",
        "kind": "simple",
        "text": "Search the boxes in the Goblin house near Lumbridge.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_grand_tree_mushrooms": {
        "step_id": "simple_grand_tree_mushrooms",
        "kind": "simple",
        "text": "Dig near some giant mushrooms behind the Grand Tree.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "map_clock_tower_crates": {
        "step_id": "map_clock_tower_crates",
        "kind": "map",
        "text": "Map: crates stacked behind the Clock tower building south of Ardougne Castle.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "map_lumberyard_crate": {
        "step_id": "map_lumberyard_crate",
        "kind": "map",
        "text": "Map: the crate in the storage area behind the Lumberyard sawmill operator, north-east of Varrock.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "emote_duel_arena_bow": {
        "step_id": "emote_duel_arena_bow",
        "kind": "emote",
        "text": "Bow or curtsy in the lobby of the Duel Arena. Equip an iron chainbody, leather chaps and a coif.",
        "equipment": ('Iron chainbody', 'Leather chaps', 'Coif'),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "emote_port_sarim_cheer": {
        "step_id": "emote_port_sarim_cheer",
        "kind": "emote",
        "text": "Cheer for the monks at Port Sarim. Equip a coif, steel plateskirt and a sapphire necklace.",
        "equipment": ('Coif', 'Steel plateskirt', 'Sapphire necklace'),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "emote_burthorpe_games_room_cheer": {
        "step_id": "emote_burthorpe_games_room_cheer",
        "kind": "emote",
        "text": "Cheer at the Burthorpe Games Room. Have nothing equipped at all when you do.",
        "equipment": (),
        "bare": True,
        "source": EXPECTED_SOURCE,
    },

    "simple_lumbridge_hans": {
        "step_id": "simple_lumbridge_hans",
        "kind": "simple",
        "text": "Speak to Hans.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_camelot_sir_kay": {
        "step_id": "simple_camelot_sir_kay",
        "kind": "simple",
        "text": "Speak to Sir Kay in Camelot Castle.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_varrock_blue_moon_bartender": {
        "step_id": "simple_varrock_blue_moon_bartender",
        "kind": "simple",
        "text": "Speak to the bartender of the Blue Moon Inn in Varrock.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_port_sarim_rusty_anchor_bartender": {
        "step_id": "simple_port_sarim_rusty_anchor_bartender",
        "kind": "simple",
        "text": "Talk to the bartender of the Rusty Anchor in Port Sarim.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_falador_squire": {
        "step_id": "simple_falador_squire",
        "kind": "simple",
        "text": "Talk to the Squire in the White Knights' castle in Falador.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
    "simple_al_kharid_zeke": {
        "step_id": "simple_al_kharid_zeke",
        "kind": "simple",
        "text": "Talk to Zeke in Al Kharid.",
        "equipment": (),
        "bare": False,
        "source": EXPECTED_SOURCE,
    },
}


NEW_EXPECTED = {
    "simple_sinclair_mansion_donovan": "Speak to Donovan the Family Handyman.",
    "simple_sinclair_mansion_staff": "Speak to the staff of Sinclair Mansion.",
    "simple_falador_general_store_crates": "Search the crates of Falador's general store.",
    "simple_lumbridge_duke_bedroom_chest": "Search the chest in the Duke of Lumbridge's bedroom.",
    "simple_draynor_manor_crates": "Search the crates in Draynor Manor.",
    "simple_varrock_horvik_armoury_crates": "Search the crates in Horvik's armoury.",
    "simple_port_sarim_fishing_shop_crates": "Search the crates in the Port Sarim fishing shop.",
    "simple_catherby_archery_shop_drawers": "Search the drawers in Catherby's Archery Shop.",
}

FINAL_CENSUS = 33


def fresh_player():
    data = default_player_data(constants.ORE_DATA, constants.ITEM_DEFINITIONS)
    data['inventory'].update({'Clue scroll (easy)': 1, 'Logs': 2})
    return data


def owned_items(data):
    return {item: amount for item, amount in data['inventory'].items() if amount}


def contact_draws(index, length=2):
    fraction = (index + 0.5) / FINAL_CENSUS
    return _draws((0.3, fraction, fraction) if length == 2 else (0.0, fraction))


def storage_round_trip(data, skill='Utilities'):
    """Use real storage twice, with JSON and a fresh collection between modules."""
    with patch.dict(sys.modules):
        collection = storage_fixture._LegacyTextCollection()
        collection.legacy_row = False
        storage = storage_fixture._load_storage_module(collection)
        storage.save_player_data(copy.deepcopy(data), skill)
        encoded = json.dumps(collection.values)
        for name in tuple(sys.modules):
            if name.startswith('ankiscape_storage_runtime_test'):
                del sys.modules[name]
        fresh_collection = storage_fixture._LegacyTextCollection()
        fresh_collection.legacy_row = False
        fresh_collection.values = json.loads(encoded)
        fresh_storage = storage_fixture._load_storage_module(fresh_collection)
        return fresh_storage.load_player_data()


class SinclairSearchCatalogTest(unittest.TestCase):
    def command(self, data, action, rng=None):
        before = copy.deepcopy(data)
        updated, ok, info = trails.apply_treasure_trails_command_pure(
            data, action, {'tier': 'easy'}, rng
        )
        self.assertTrue(ok, info)
        self.assertEqual(data, before, 'command mutated its input')
        if action == 'open_casket':
            self.assertTrue(info['rewards'])
        return updated

    def generate(self, index, length=2):
        data = fresh_player()
        self.assertEqual(len(TREASURE_TRAILS_EASY_STEPS), FINAL_CENSUS)
        self.assertEqual(data['treasure_trail'], {})
        self.assertEqual(data['activity_session']['active_id'], '')
        return self.command(data, 'start_from_bank', contact_draws(index, length))

    def resolve(self, data, terminal=False):
        before = copy.deepcopy(data)
        updated, ok, info = trails.apply_treasure_trail_review_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(info['terminal'], terminal)
        self.assertFalse(info['blocked'])
        self.assertEqual(data, before, 'resolution mutated its input')
        return updated

    def assert_view(self, data, step_id, text, number=1, total=2):
        before = copy.deepcopy(data)
        step = trails.treasure_trails_view_pure(data)['step']
        self.assertEqual(data, before, 'view mutated its input')
        self.assertEqual(step['step_id'], step_id)
        self.assertEqual(step['text'], text)
        self.assertEqual((step['number'], step['total']), (number, total))
        self.assertEqual(step['blocked_reason'], '')

    def assert_settled(self, data):
        self.assertEqual(owned_items(data), {'Logs': 2, 'Casket (easy)': 1})
        self.assertNotIn('Clue scroll (easy)', data['inventory'])
        self.assertEqual(data['treasure_trail'], {})
        self.assertEqual(data['activity_session']['active_id'], '')
        self.assertEqual(data['treasure_trails_started'], 1)
        self.assertEqual(data['treasure_trails_completed'], 1)
        self.assertEqual(data['treasure_trails_caskets_opened'], 0)

    def assert_persisted(self, before, after, skill):
        keys = (
            'config_version', 'treasure_trail', 'treasure_trail_retained',
            'activity_session', 'current_utility', 'treasure_trails_started',
            'treasure_trails_completed', 'treasure_trails_caskets_opened',
            'treasure_trails_last_result',
        )
        for key in keys:
            with self.subTest(saved_key=key):
                self.assertEqual(after[key], before[key])
        # Existing migration drops the obsolete zero-count Pot row. Compare
        # every item count, including empty slots, across that representation.
        items = before['inventory'].keys() | after['inventory'].keys()
        self.assertEqual({item: before['inventory'].get(item, 0) for item in items},
                         {item: after['inventory'].get(item, 0) for item in items})
        self.assertEqual(skill, 'Utilities')

    def test_pool_adds_exactly_eight_and_preserves_prior_rows(self):
        self.assertEqual(list(TREASURE_TRAILS_EASY_STEPS),
                         [*BASELINE_EXPECTED, *NEW_EXPECTED, *(step_id for step_id, _ in (*SEARCH_ROWS, *NEW_ROWS))])
        self.assertEqual(len(TREASURE_TRAILS_EASY_STEPS), 33)
        self.assertEqual(FINAL_CENSUS, 33)
        for step_id, definition in BASELINE_EXPECTED.items():
            with self.subTest(prior_id=step_id):
                self.assertEqual(TREASURE_TRAILS_EASY_STEPS[step_id], definition)
        for step_id, text in (*NEW_EXPECTED.items(), *SEARCH_ROWS, *NEW_ROWS):
            with self.subTest(new_id=step_id):
                self.assertEqual(TREASURE_TRAILS_EASY_STEPS[step_id], {
                    'step_id': step_id, 'kind': 'simple', 'text': text,
                    'equipment': (), 'bare': False, 'source': EXPECTED_SOURCE,
                })
        self.assertTrue(all(key == row['step_id']
                            for key, row in TREASURE_TRAILS_EASY_STEPS.items()))
        kinds = [row['kind'] for row in TREASURE_TRAILS_EASY_STEPS.values()]
        self.assertEqual({kind: kinds.count(kind) for kind in ('simple', 'map', 'emote')},
                         {'simple': 28, 'map': 2, 'emote': 3})

    def test_each_new_clue_is_selected_displayed_and_resolved_from_bank(self):
        for step_id, text in NEW_EXPECTED.items():
            index = list(TREASURE_TRAILS_EASY_STEPS).index(step_id)
            with self.subTest(step_id=step_id):
                data = self.generate(index)
                self.assertEqual(data['treasure_trail'], {
                    'version': 1, 'tier': 'easy', 'steps': [step_id, step_id], 'index': 0,
                })
                self.assertEqual(data['treasure_trails_started'], 1)
                self.assertEqual(data['activity_session'], {'active_id': 'treasure_trail'})
                self.assert_view(data, step_id, text)
                advanced = self.resolve(data)
                self.assertEqual(advanced['treasure_trail']['index'], 1)
                self.assertEqual(owned_items(advanced), {'Clue scroll (easy)': 1, 'Logs': 2})
                self.assertEqual(advanced['treasure_trails_completed'], 0)
                self.assert_view(advanced, step_id, text, number=2)
                settled = self.resolve(advanced, terminal=True)
                self.assert_settled(settled)
                opened = self.command(settled, 'open_casket', _draws([0.0] * 7))
                self.assertNotIn('Casket (easy)', opened['inventory'])
                self.assertEqual(opened['treasure_trails_caskets_opened'], 1)
                self.assertNotEqual(owned_items(opened), {'Logs': 2})
                self.assertEqual(opened['inventory']['Logs'], 2)

    def test_each_new_clue_can_complete_a_generated_one_step_trail(self):
        for step_id, text in NEW_EXPECTED.items():
            index = list(TREASURE_TRAILS_EASY_STEPS).index(step_id)
            with self.subTest(step_id=step_id):
                data = self.generate(index, length=1)
                self.assertEqual(data['treasure_trail']['steps'], [step_id])
                self.assert_view(data, step_id, text, total=1)
                self.assert_settled(self.resolve(data, terminal=True))

    def test_each_new_active_clue_survives_storage_reload(self):
        for step_id, text in NEW_EXPECTED.items():
            index = list(TREASURE_TRAILS_EASY_STEPS).index(step_id)
            with self.subTest(step_id=step_id):
                advanced = self.resolve(self.generate(index))
                loaded, skill = storage_round_trip(advanced)
                self.assert_persisted(advanced, loaded, skill)
                self.assertEqual(loaded['treasure_trail'], {
                    'version': 1, 'tier': 'easy', 'steps': [step_id, step_id], 'index': 1,
                })
                self.assert_view(loaded, step_id, text, number=2)
                self.assert_settled(self.resolve(loaded, terminal=True))

    def test_each_new_retained_clue_survives_storage_reload_and_resumes(self):
        for step_id, text in NEW_EXPECTED.items():
            index = list(TREASURE_TRAILS_EASY_STEPS).index(step_id)
            with self.subTest(step_id=step_id):
                advanced = self.resolve(self.generate(index))
                retained = self.command(advanced, 'abandon')
                loaded, skill = storage_round_trip(retained)
                self.assert_persisted(retained, loaded, skill)
                self.assertEqual(loaded['treasure_trail'], {})
                self.assertEqual(loaded['treasure_trail_retained'], advanced['treasure_trail'])
                self.assertEqual(owned_items(loaded), {'Clue scroll (easy)': 1, 'Logs': 2})
                resumed = self.command(loaded, 'start_from_bank', self.fail_draw)
                self.assertEqual(resumed['treasure_trail'], advanced['treasure_trail'])
                self.assertEqual(resumed['treasure_trail_retained'], {})
                self.assertEqual(resumed['treasure_trails_started'], 1)
                self.assert_view(resumed, step_id, text, number=2)
                self.assert_settled(self.resolve(resumed, terminal=True))

    def fail_draw(self):
        self.fail('resuming a retained trail must not draw or reroll')

    def assert_prior_reload(self, step_id, row, retained):
        index = list(TREASURE_TRAILS_EASY_STEPS).index(step_id)
        generated = self.generate(index)
        trail = {'version': 1, 'tier': 'easy',
                 'steps': [step_id, step_id], 'index': 0}
        self.assertEqual(generated['treasure_trail'], trail)
        data = self.command(generated, 'abandon') if retained else generated
        loaded, skill = storage_round_trip(data)
        self.assert_persisted(data, loaded, skill)
        key = 'treasure_trail_retained' if retained else 'treasure_trail'
        self.assertEqual(loaded[key], trail)
        self.assertEqual(loaded['treasure_trail'], {} if retained else trail)
        self.assertEqual(loaded['activity_session']['active_id'],
                         '' if retained else 'treasure_trail')
        self.assertEqual(owned_items(loaded), {'Clue scroll (easy)': 1, 'Logs': 2})
        if retained:
            loaded = self.command(loaded, 'start_from_bank', self.fail_draw)
            self.assertEqual(loaded['treasure_trail_retained'], {})
            self.assertEqual(loaded['treasure_trails_started'], 1)
        self.assertEqual(loaded['treasure_trail'], trail)
        self.assertEqual(loaded['activity_session']['active_id'], 'treasure_trail')
        self.assertEqual(trails.treasure_trails_view_pure(loaded)['step']['text'], row['text'])

    def test_every_prior_id_survives_active_and_retained_reload(self):
        for step_id, row in BASELINE_EXPECTED.items():
            for retained in (False, True):
                with self.subTest(step_id=step_id, retained=retained):
                    self.assert_prior_reload(step_id, row, retained)

    def test_registered_art_paths_and_provenance_are_reused(self):
        root = Path(__file__).resolve().parents[2]
        provenance = json.loads((root / 'assets_provenance.json').read_text())
        # Existing modern art: the 2019 Easy clue image is NOT period-verified art.
        assets = (
            ('activityicons/treasure_trail.png',
             'b4a46740be3354a77543cfed31eb5b2756ebd74fb6c3a57c69cd808cc3c0bee0',
             constants.UTILITY_ACTIVITY_DATA['treasure_trail']['icon_path'],
             'Mg treasuretrails.jpg', 'rs3', '2008-07-28T14:53:49Z',
             '8ff0d3877e1cba096b981d16a92f826b99164fbb'),
            ('activityitems/casket_easy.png',
             'a4f404b09451717e98434baa18564747af28d87d72eaf74f97e1b25dab73123a',
             constants.TREASURE_TRAILS_ITEM_IMAGES['Casket (easy)'],
             'Casket.png', 'rs3', '2010-10-04T04:04:13Z',
             '2a6827c6747909115aea6ca8479cbc68b43e8b00'),
            ('combatitems/clue_scroll_easy.png',
             '9ec85a114b04bf018311457874f959f8b64eb7b13a3abba52f5bf4815fcc7278',
             constants.COMBAT_ITEM_IMAGES['Clue scroll (easy)'],
             'Clue scroll (easy).png', 'osrs', '2019-04-11T12:15:25Z',
             'e94b0fe55f7371cfabf60e60c11c650b3148d0a0'),
        )
        for relative, digest, binding, title, wiki, timestamp, sha1 in assets:
            with self.subTest(asset=relative):
                path = root / relative
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                self.assertEqual(Path(binding).resolve(), path)
                entry = provenance[relative]
                self.assertEqual(
                    (entry['file_title'], entry['source_wiki'], entry['timestamp'], entry['sha1']),
                    (title, wiki, timestamp, sha1),
                )
                urls = {
                    'activityicons/treasure_trail.png': (
                        'https://runescape.wiki/wiki/File:Mg_treasuretrails.jpg',
                        'https://runescape.wiki/images/Mg_treasuretrails.jpg?de6ba'),
                    'activityitems/casket_easy.png': (
                        'https://runescape.wiki/wiki/File:Casket.png',
                        'https://runescape.wiki/images/archive/20140511081506%21Casket.png?fc642'),
                    'combatitems/clue_scroll_easy.png': (
                        'https://oldschool.runescape.wiki/wiki/File:Clue_scroll_%28easy%29.png',
                        'https://oldschool.runescape.wiki/images/Clue_scroll_%28easy%29.png?e29cd'),
                }
                self.assertEqual((entry['file_page_url'], entry['image_url']), urls[relative])
