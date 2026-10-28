"""Literal catalog, ordinary generation, save compatibility and reused artwork."""

import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, UTILITY_ACTIVITY_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.treasure_trails_data import TREASURE_TRAILS_EASY_STEPS, TREASURE_TRAILS_SOURCE
from ankiscape.logic.treasure_trails_logic import (
    apply_treasure_trails_command_pure, apply_treasure_trail_review_pure,
    treasure_trails_view_pure,
)

ROOT = Path(__file__).resolve().parents[2]
CLUE = "Clue scroll (easy)"
CASKET = "Casket (easy)"

EXPECTED_SOURCE = (
    "RuneScape Wiki Treasure Trails oldid=6473708 (2012-10-26T00:01:09Z); "
    "Clue scroll (easy) oldid=6333359 (2012-10-02T09:39:55Z); "
    "Treasure Trails/Guide/Simple clues oldid=6579176 (2012-11-18T16:48:49Z); "
    "Treasure Trails/Guide/Emotes oldid=6538968 (2012-11-06T15:34:10Z); "
    "Treasure Trails/Guide/Maps oldid=6362741 (2012-10-07T05:35:23Z); "
    "Darkan TreasureTrailsManager.java and data/npcs/drops/treasure_trails/easy_casket.json"
)

# Frozen ordered integration baseline at b6059099cd6efb4af9fe8188ef17324322f4a784.
# (ID, kind, exact text, equipment, bare)
BASELINE = (
    ('simple_port_sarim_sailor', 'simple', 'One of the sailors in Port Sarim is your next destination.', (), False),
    ('simple_varrock_palace_crate', 'simple', 'Search for a crate in Varrock Palace.', (), False),
    ('simple_lumbridge_goblin_house', 'simple', 'Search the boxes in the Goblin house near Lumbridge.', (), False),
    ('simple_grand_tree_mushrooms', 'simple', 'Dig near some giant mushrooms behind the Grand Tree.', (), False),
    ('map_clock_tower_crates', 'map', 'Map: crates stacked behind the Clock tower building south of Ardougne Castle.', (), False),
    ('map_lumberyard_crate', 'map', 'Map: the crate in the storage area behind the Lumberyard sawmill operator, north-east of Varrock.', (), False),
    ('emote_duel_arena_bow', 'emote', 'Bow or curtsy in the lobby of the Duel Arena. Equip an iron chainbody, leather chaps and a coif.', ('Iron chainbody', 'Leather chaps', 'Coif'), False),
    ('emote_port_sarim_cheer', 'emote', 'Cheer for the monks at Port Sarim. Equip a coif, steel plateskirt and a sapphire necklace.', ('Coif', 'Steel plateskirt', 'Sapphire necklace'), False),
    ('emote_burthorpe_games_room_cheer', 'emote', 'Cheer at the Burthorpe Games Room. Have nothing equipped at all when you do.', (), True),
    ('simple_lumbridge_hans', 'simple', 'Speak to Hans.', (), False),
    ('simple_camelot_sir_kay', 'simple', 'Speak to Sir Kay in Camelot Castle.', (), False),
    ('simple_varrock_blue_moon_bartender', 'simple', 'Speak to the bartender of the Blue Moon Inn in Varrock.', (), False),
    ('simple_port_sarim_rusty_anchor_bartender', 'simple', 'Talk to the bartender of the Rusty Anchor in Port Sarim.', (), False),
    ('simple_falador_squire', 'simple', "Talk to the Squire in the White Knights' castle in Falador.", (), False),
    ('simple_al_kharid_zeke', 'simple', 'Talk to Zeke in Al Kharid.', (), False),
    ('simple_sinclair_mansion_donovan', 'simple', 'Speak to Donovan the Family Handyman.', (), False),
    ('simple_sinclair_mansion_staff', 'simple', 'Speak to the staff of Sinclair Mansion.', (), False),
    ('simple_falador_general_store_crates', 'simple', "Search the crates of Falador's general store.", (), False),
    ('simple_lumbridge_duke_bedroom_chest', 'simple', "Search the chest in the Duke of Lumbridge's bedroom.", (), False),
    ('simple_draynor_manor_crates', 'simple', 'Search the crates in Draynor Manor.', (), False),
    ('simple_varrock_horvik_armoury_crates', 'simple', "Search the crates in Horvik's armoury.", (), False),
    ('simple_port_sarim_fishing_shop_crates', 'simple', 'Search the crates in the Port Sarim fishing shop.', (), False),
    ('simple_catherby_archery_shop_drawers', 'simple', "Search the drawers in Catherby's Archery Shop.", (), False),
    ('simple_hemenster_crate', 'simple', 'Search for a crate in a building in Hemenster.', (), False),
    ('simple_seers_village_ground_floor_crate', 'simple', "Search for a crate on the ground floor of a house in Seers' Village.", (), False),
    ('simple_varrock_south_entrance_boxes', 'simple', 'Search the boxes in the house near the South entrance of Varrock.', (), False),
    ('simple_east_ardougne_armour_shop_boxes', 'simple', 'Search the boxes just outside the Armour shop in east Ardougne.', (), False),
    ('simple_camelot_left_tower_chest', 'simple', 'Search the chest in the left-hand tower of Camelot castle.', (), False),
    ('simple_dwarven_mine_chests', 'simple', 'Search the chests in the Dwarven Mine.', (), False),
    ('simple_port_khazard_cart_crate', 'simple', 'Search the crate near a cart in Port Khazard.', (), False),
)

SEARCH_CASES = (
    # Wiki 13–16; RuneHQ 956–957.
    ('simple_east_ardougne_church_tower_crate', 'A crate found in the tower of a church is your next location.'),
    # Wiki 53–55; RuneHQ 1162–1163.
    ('simple_falador_east_bank_house_crates', 'Look in the ground floor crates of houses in Falador.'),
    # Wiki 102–104; RuneHQ 1316–1317.
    ('simple_port_sarim_food_shop_upstairs_chests', 'Search chests found in the upstairs of shops in Port Sarim.'),
    # Wiki 122–125; RuneHQ 1256–1257.
    ('simple_al_kharid_tent_boxes', 'Search the boxes in one of the tents in Al Kharid.'),
    # Wiki 166–168; RuneHQ 1331–1332.
    ('simple_lumbridge_left_hand_tower_crate', 'Search the crate in the left-hand tower of Lumbridge castle.'),
    # Wiki 174–176; RuneHQ 1346–1347.
    ('simple_yanille_piano_house_crates', 'Search the crates in a house in Yanille that has a piano.'),
    # Wiki 190–192; RuneHQ 1351–1352.
    ('simple_east_ardougne_general_store_crates', "Search the crates in East Ardougne's general store."),
    # Wiki 198–200; RuneHQ 1376–1377.
    ('simple_gunnarsgrunn_helmet_shop_crates', 'Search the crates in Gunnarsgrunn (Barbarian Village) helmet shop.'),
)


def fresh_player():
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data['inventory'] = {CLUE: 1}
    return data


def search_draws(step_id, length=2):
    pool = list(TREASURE_TRAILS_EASY_STEPS)
    q = (pool.index(step_id) + 0.5) / len(pool)
    stream = iter((0.0, q) if length == 1 else (0.25, q, q))
    return lambda: next(stream)


def no_draw():
    raise AssertionError('resumption must not consume a draw')


def reopen(data):
    return migrate_loaded_data(json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS)


def definition(step_id, kind, text, equipment=(), bare=False):
    return dict(step_id=step_id, kind=kind, text=text, equipment=equipment,
                bare=bare, source=EXPECTED_SOURCE)


class SearchCatalogTest(unittest.TestCase):
    def command(self, data, action, rng=None):
        before = copy.deepcopy(data)
        after, ok, info = apply_treasure_trails_command_pure(data, action, {'tier': 'easy'}, rng)
        self.assertTrue(ok, info)
        self.assertEqual(data, before, 'command mutated its input save')
        return after

    def generate(self, step_id, length=2):
        data = fresh_player()
        self.assertEqual(data['treasure_trail'], {})
        self.assertEqual(data['treasure_trail_retained'], {})
        self.assertEqual(data['inventory'].get(CASKET, 0), 0)
        after = self.command(data, 'start_from_bank', search_draws(step_id, length))
        self.assertEqual(after['treasure_trail'], dict(
            version=1, tier='easy', steps=[step_id] * length, index=0,
        ))
        self.assertEqual(after['activity_session'], {'active_id': 'treasure_trail'})
        self.assertEqual(after['treasure_trails_started'], 1)
        return after

    def resolve(self, data, step_id, text, terminal):
        before = copy.deepcopy(data)
        after, ok, info = apply_treasure_trail_review_pure(data)
        self.assertTrue(ok, info)
        self.assertEqual(data, before, 'review mutated its input save')
        self.assertEqual(info['terminal'], terminal)
        self.assertFalse(info['blocked'])
        self.assertEqual((info['step']['step_id'], info['step']['text']), (step_id, text))
        return after

    def assert_view(self, data, step_id, text):
        step = treasure_trails_view_pure(data)['step']
        self.assertEqual((step['step_id'], step['text']), (step_id, text))
        self.assertEqual(step['blocked_reason'], '')

    def assert_finished(self, data):
        self.assertNotIn(CLUE, data['inventory'])
        self.assertEqual(data['inventory'], {CASKET: 1})
        self.assertEqual(data['treasure_trail'], {})
        self.assertEqual(data['treasure_trail_retained'], {})
        self.assertEqual(data['activity_session'], {'active_id': ''})
        self.assertEqual(data['treasure_trails_started'], 1)
        self.assertEqual(data['treasure_trails_completed'], 1)
        self.assertEqual(data['treasure_trails_caskets_opened'], 0)

    def assert_preserved(self, before, after):
        for key in ('treasure_trail', 'treasure_trail_retained', 'activity_session',
                    'treasure_trails_started', 'treasure_trails_completed',
                    'treasure_trails_caskets_opened'):
            self.assertEqual(after[key], before[key], key)
        self.assertEqual(after['inventory'].get(CLUE, 0), 1)
        self.assertEqual(after['inventory'].get(CASKET, 0), 0)

    def test_registry_contains_exact_eight_additions(self):
        expected = [definition(*row) for row in BASELINE]
        expected.extend(definition(step_id, 'simple', text) for step_id, text in SEARCH_CASES)
        self.assertEqual(len(TREASURE_TRAILS_EASY_STEPS), 38)
        self.assertEqual(list(TREASURE_TRAILS_EASY_STEPS.values()), expected)
        self.assertEqual(list(TREASURE_TRAILS_EASY_STEPS), [row['step_id'] for row in expected])
        self.assertEqual(TREASURE_TRAILS_SOURCE, EXPECTED_SOURCE)
        self.assertIn('oldid=6579176', TREASURE_TRAILS_SOURCE)
        tree = ast.parse((ROOT / 'data/treasure_trails_data.py').read_text())
        registry = next(node for node in tree.body if isinstance(node, ast.AnnAssign)
                        and getattr(node.target, 'id', '') == 'TREASURE_TRAILS_EASY_STEPS')
        calls = registry.value.generators[0].iter.elts
        ids = [ast.literal_eval(call.args[0]) for call in calls]
        self.assertEqual(len(calls), 38)
        self.assertEqual(len(set(ids)), 38, 'duplicate IDs can hide in a dict comprehension')
        self.assertEqual(ids, list(TREASURE_TRAILS_EASY_STEPS))
        self.assert_ast_additions(calls[-8:])

    def assert_ast_additions(self, calls):
        for call, (step_id, text) in zip(calls, SEARCH_CASES):
            self.assertEqual(call.func.id, '_step')
            self.assertEqual([ast.literal_eval(arg) for arg in call.args], [step_id, 'simple', text])
            self.assertEqual(call.keywords, [])

    def test_each_new_search_is_read_and_finishes(self):
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id):
                data = self.generate(step_id, length=1)
                self.assert_view(data, step_id, text)
                self.assert_finished(self.resolve(data, step_id, text, terminal=True))

    def test_each_new_search_advances_once_before_finishing(self):
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id):
                data = self.generate(step_id)
                advanced = self.resolve(data, step_id, text, terminal=False)
                self.assertEqual(advanced['treasure_trail']['index'], 1)
                self.assertEqual(advanced['treasure_trail']['steps'], [step_id, step_id])
                self.assertEqual(advanced['inventory'], {CLUE: 1})
                self.assertEqual(advanced['treasure_trails_completed'], 0)
                self.assert_view(advanced, step_id, text)
                self.assert_finished(self.resolve(advanced, step_id, text, terminal=True))

    def test_generated_search_active_save_roundtrip(self):
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id):
                advanced = self.resolve(self.generate(step_id), step_id, text, terminal=False)
                loaded = reopen(advanced)
                self.assert_preserved(advanced, loaded)
                self.assertEqual(loaded['treasure_trail']['index'], 1)
                self.assert_view(loaded, step_id, text)

    def test_generated_search_retained_save_roundtrip(self):
        for step_id, text in SEARCH_CASES:
            with self.subTest(step_id=step_id):
                advanced = self.resolve(self.generate(step_id), step_id, text, terminal=False)
                retained = self.command(advanced, 'abandon')
                loaded = reopen(retained)
                self.assert_preserved(retained, loaded)
                self.assertEqual(loaded['treasure_trail_retained'], advanced['treasure_trail'])
                resumed = self.command(loaded, 'start_from_bank', no_draw)
                self.assertEqual(resumed['treasure_trail'], advanced['treasure_trail'])
                self.assertEqual(resumed['treasure_trail_retained'], {})
                self.assertEqual(resumed['inventory'], loaded['inventory'])
                self.assertEqual(resumed['treasure_trails_started'], 1)
                self.assertEqual(resumed['treasure_trails_completed'], 0)
                self.assertEqual(resumed['treasure_trails_caskets_opened'], 0)
                self.assert_view(resumed, step_id, text)

    def test_prior_active_and_retained_ids_survive_reopen(self):
        for row in BASELINE:
            for retained in (False, True):
                with self.subTest(step_id=row[0], retained=retained):
                    self.assert_prior_save(row, retained)

    def assert_prior_save(self, row, retained):
        data = fresh_player()
        key = 'treasure_trail_retained' if retained else 'treasure_trail'
        # A pre-addition save fixture, including a nonzero cursor and mixed order.
        data[key] = dict(version=1, tier='easy', steps=[BASELINE[0][0], row[0], BASELINE[-1][0]], index=1)
        data['activity_session'] = {'active_id': '' if retained else 'treasure_trail'}
        data['current_utility'] = 'bankstanding' if retained else 'treasure_trail'
        data['treasure_trails_started'] = 7
        data['treasure_trails_completed'] = 3
        loaded = reopen(data)
        self.assert_preserved(data, loaded)
        self.assertEqual(TREASURE_TRAILS_EASY_STEPS[row[0]], definition(*row))
        if retained:
            loaded = self.command(loaded, 'start_from_bank', no_draw)
        self.assertEqual(loaded['treasure_trail'], data[key])
        self.assertEqual(loaded['treasure_trails_started'], 7)
        self.assertEqual(treasure_trails_view_pure(loaded)['step']['text'], row[2])

    def test_existing_treasure_art_bindings_match_receipts(self):
        provenance = json.loads((ROOT / 'assets_provenance.json').read_text())
        assets = (
            ('activityicons/treasure_trail.png',
             'b4a46740be3354a77543cfed31eb5b2756ebd74fb6c3a57c69cd808cc3c0bee0',
             UTILITY_ACTIVITY_DATA['treasure_trail']['icon_path'],
             'Mg treasuretrails.jpg', 'rs3', '2008-07-28T14:53:49Z'),
            ('activityitems/casket_easy.png',
             'a4f404b09451717e98434baa18564747af28d87d72eaf74f97e1b25dab73123a',
             next(item.asset_path for item in ITEM_DEFINITIONS if item.storage_key == CASKET),
             'Casket.png', 'rs3', '2010-10-04T04:04:13Z'),
            # Existing reusable OSRS art; this upload is not period authority.
            ('combatitems/clue_scroll_easy.png',
             '9ec85a114b04bf018311457874f959f8b64eb7b13a3abba52f5bf4815fcc7278',
             next(item.asset_path for item in ITEM_DEFINITIONS if item.storage_key == CLUE),
             'Clue scroll (easy).png', 'osrs', '2019-04-11T12:15:25Z'),
        )
        for relative, digest, binding, title, wiki, timestamp in assets:
            with self.subTest(asset=relative):
                path = ROOT / relative
                self.assertEqual(Path(binding).resolve(), path)
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)
                entry = provenance[relative]
                self.assertEqual((entry['file_title'], entry['source_wiki'], entry['timestamp']),
                                 (title, wiki, timestamp))
