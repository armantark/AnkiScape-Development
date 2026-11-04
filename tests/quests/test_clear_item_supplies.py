"""The taught quest route prepares its items without a hand-started Utility action."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_quest import start_quest_pure, quest_current_stage_pure
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer
from tests.test_runtime_actions import _context


# Only supplies the period guide tells the player to bring; folded products are absent.
SUPPLIES = {
    'black_knights_fortress': {'Iron chainbody': 1, 'Bronze med helm': 1},
    'cooks_assistant': {},
    'demon_slayer': {'Coins': 1, 'Bones': 25},
    'ernest_the_chicken': {'Spade': 1},
    'fishing_contest': {'Coins': 5, 'Fishing rod': 1, 'Spade': 1},
    'gertrudes_cat': {'Coins': 100, 'Bucket of milk': 1, 'Raw sardine': 1},
    'merlins_crystal': {'Bread': 1, 'Bat bones': 1},
    'pirates_treasure': {'Coins': 30, 'Spade': 1},
    'plague_city': {'Dwellberries': 1, 'Rope': 1, 'Coins': 20},
    'skippy_and_the_mogres': {'Leather gloves': 1, 'Coins': 20},
    'the_knights_sword': {'Redberry pie': 1, 'Iron bar': 2},
}
# Exact card counts; Merlin includes its existing fight with deterministic mid rolls.
CARDS = {'black_knights_fortress': 5, 'cooks_assistant': 6, 'ernest_the_chicken': 10,
         'fishing_contest': 8, 'gertrudes_cat': 10, 'pirates_treasure': 4,
         'merlins_crystal': 10, 'plague_city': 28, 'skippy_and_the_mogres': 17, 'the_knights_sword': 7}


def player_for(quest_id, supplies=None):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for key in player:
        if key.endswith('_level'):
            player[key] = 99
    player['quest_points'] = 1000
    player['combat_lifepoints'] = 990
    player['quests'].update({key: dict(started=True, completed=True, progress=row['stages'])
                             for key, row in QUEST_DATA.items() if key != quest_id})
    player['inventory'] = dict(SUPPLIES[quest_id] if supplies is None else supplies)
    player['current_quest'] = quest_id
    player['current_skill'] = 'Quests'
    player, ok = start_quest_pure(player, quest_id, QUEST_DATA)
    assert ok, quest_id
    return player


def answer(player, speed=1):
    calls = dict(xp=[], saves=0, errors=[])
    handled = handle_quest_answer(_context(player, calls, random_values=(0.5,) * 10000, review_action_multiplier=speed))
    return handled, calls


class ClearItemSupplyReviewTest(unittest.TestCase):
    def test_brought_supplies_finish_quests_at_both_speeds(self):
        for quest_id, cards in CARDS.items():
            for speed in (1, 10):
                with self.subTest(quest=quest_id, speed=speed):
                    self.assert_quest_finishes(quest_id, cards, speed)

    def assert_quest_finishes(self, quest_id, cards, speed):
        player = player_for(quest_id)
        before_mining = player['mining_exp']
        before_cooking = player['cooking_exp']
        notices = []
        for card in range(cards):
            handled, calls = answer(player, speed)
            self.assertTrue(handled, (card, calls))
            self.assertEqual(calls['saves'], 1)
            self.assertEqual(player['quests'][quest_id]['completed'], card == cards - 1)
            notices.extend(calls.get('activity', ()))
        self.assertEqual(player['current_skill'], 'Quests')
        self.assertEqual(sum(n == '+1 Blurite ore' for n in notices), int(quest_id == 'the_knights_sword'))
        if quest_id == 'the_knights_sword':
            self.assertEqual(player['mining_exp'] - before_mining, 17.5)
        if quest_id == 'skippy_and_the_mogres':
            self.assertEqual(player['cooking_exp'] - before_cooking, 61)
            self.assertEqual(notices.count('+1 Nettles'), 1)
        if quest_id == 'pirates_treasure':
            self.assertEqual(player['inventory']['Coins'], 0)
        if quest_id == 'plague_city':
            self.assertEqual(player['inventory']['Bucket'], 3)

    def test_demon_slayer_plays_from_start_past_its_folded_row(self):
        player = player_for('demon_slayer')
        for _ in range(5):
            handled, calls = answer(player)
            self.assertTrue(handled, calls)
        self.assertEqual(quest_current_stage_pure(player, 'demon_slayer', QUEST_DATA), 4)
        self.assertEqual(player['inventory']['Silverlight key'], 1)
        self.assertEqual(player['inventory']['Bucket'], 1)

    def test_held_products_skip_pickups_and_preparation(self):
        cases = (
            ('cooks_assistant', {'Bucket': 1, 'Empty pot': 1}, 4),
            ('ernest_the_chicken', {'Fish food': 1, 'Poison': 1}, 8),
            ('pirates_treasure', {'Karamjan rum': 1}, 3),
            ('fishing_contest', {'Garlic': 1, 'Fishing bait': 1}, 6),
            ('the_knights_sword', {'Blurite ore': 1}, 6),
            ('skippy_and_the_mogres', {'Nettle tea': 1}, 12),
        )
        for quest_id, products, cards in cases:
            with self.subTest(quest=quest_id):
                player = player_for(quest_id, dict(SUPPLIES[quest_id], **products))
                if quest_id == 'skippy_and_the_mogres':
                    player['inventory'].pop('Leather gloves')
                mining = player['mining_exp']
                for card in range(cards):
                    handled, calls = answer(player)
                    self.assertTrue(handled, calls)
                    self.assertEqual(player['quests'][quest_id]['completed'], card == cards - 1)
                self.assertEqual(player['mining_exp'], mining)

    def test_started_quest_stops_for_missing_coins_level_tools_or_brought_material(self):
        cases = (
            ('pirates_treasure', 1, 'Coins', 'Needs Coins x30'),
            ('the_knights_sword', 6, 'level', 'Mining 10'),
            ('the_knights_sword', 6, 'pickaxe', 'Needs Pickaxe'),
            ('skippy_and_the_mogres', 2, 'Leather gloves', 'Needs Leather gloves'),
            ('plague_city', 14, 'Coins', 'Needs Coins x20'),
        )
        for quest_id, stage, missing, reason in cases:
            with self.subTest(quest=quest_id, missing=missing):
                player = player_for(quest_id)
                player['quests'][quest_id]['progress'] = stage
                if missing == 'level':
                    player['mining_level'] = 9
                elif missing == 'pickaxe':
                    player['toolbelt']['mining'] = []
                else:
                    player['inventory'].pop(missing, None)
                before = copy.deepcopy(player)
                handled, calls = answer(player)
                self.assertFalse(handled)
                self.assertEqual(player, before)
                self.assertTrue(calls['deactivated'])
                self.assertIn(reason, calls['errors'][0][1])
