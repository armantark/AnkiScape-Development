"""Spend the advance and prepare through ordinary shop and review owners."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS
from ankiscape.logic.shop_logic import apply_shop_buy_pure
from ankiscape.runtime.runtime_actions import (
    handle_quest_answer, handle_utility_answer, handle_cooking_answer,
    handle_woodcutting_answer, handle_firemaking_answer,
)
from tests.test_runtime_actions import _context
from tests.quest_catalog.another_cook.test_another_cook_transactions import player, QUEST_ID, COMMISSION, PREPARATION


class AnotherCookOrdinaryRouteTest(unittest.TestCase):
    def test_79_coin_shopping_slicing_mixing_logs_ashes_then_prepare(self):
        data = player()
        self.assertEqual(data['inventory']['Coins'], 0)
        self.assertFalse(data['quests']['the_dig_site']['completed'])
        for name in ('Ashes', 'Fruit blast', 'Cocktail shaker', 'Cocktail glass', 'Lemon', 'Lemon slices', 'Pineapple', 'Orange'):
            self.assertEqual(data['inventory'].get(name, 0), 0)
        self.assertTrue(handle_quest_answer(_context(data, random_values=[0.0, 0.99, 0.99, 0.99])))
        self.assertEqual(data['quest_action_proofs'], [COMMISSION])
        self.assertEqual(data['inventory']['Coins'], 100)
        bill = 0
        for suffix, quantity in (('4:2114', 1), ('6:2108', 1), ('7:2102', 1), ('10:2025', 1), ('17:2026', 1)):
            data, result = apply_shop_buy_pure(data, 'funchs_fine_groceries', 'funchs_fine_groceries:' + suffix, quantity)
            self.assertTrue(result['allowed'], result)
            self.assertEqual(result['quantity'], quantity)
            bill += result['total_price']
        self.assertEqual(bill, 77)
        self.assertEqual(data['inventory']['Coins'], 23)
        self.assertEqual(data['inventory']['Lemon'], 1)
        belt = data['toolbelt'].copy()
        data['current_utility'] = 'slice_lemon'
        before_slicing_xp = data['cooking_exp']
        self.assertTrue(handle_utility_answer(_context(data, random_values=[0.0, 0.99, 0.99, 0.99])))
        self.assertEqual(data['inventory']['Lemon'], 0)
        self.assertEqual(data['inventory']['Lemon slices'], 1)
        self.assertEqual(data['cooking_exp'], before_slicing_xp)
        self.assertEqual(data['toolbelt'], belt)
        # Utility slices every available lemon, so buy the whole mixing lemon
        # afterwards. Both lemons still come from Funch for the same 79-Coin bill.
        data, result = apply_shop_buy_pure(data, 'funchs_fine_groceries', 'funchs_fine_groceries:7:2102', 1)
        self.assertTrue(result['allowed'], result)
        self.assertEqual(result['quantity'], 1)
        bill += result['total_price']
        self.assertEqual(bill, 79)
        self.assertEqual(data['inventory']['Lemon'], 1)
        self.assertEqual(data['inventory']['Coins'], 21)
        data['current_cooking'] = 'mix_fruit_blast'
        before_xp = data['cooking_exp']
        self.assertTrue(handle_cooking_answer(_context(data, random_values=[0.0, 0.99, 0.99, 0.99])))
        self.assertEqual(data['cooking_exp'] - before_xp, 50.0)
        self.assertEqual(data['inventory']['Fruit blast'], 1)
        self.assertEqual(data['inventory']['Lemon'], 0)
        self.assertEqual(data['inventory']['Lemon slices'], 0)
        self.assertEqual(data['inventory']['Cocktail glass'], 0)
        self.assertEqual(data['inventory']['Cocktail shaker'], 1)
        data['current_tree'] = 'tree'
        self.assertTrue(handle_woodcutting_answer(_context(data, random_values=[0.0, 0.99, 0.99, 0.99])))
        self.assertGreaterEqual(data['inventory']['Logs'], 1)
        data['current_firemaking'] = 'logs'
        self.assertTrue(handle_firemaking_answer(_context(data, random_values=[0.0, 0.99, 0.99, 0.99])))
        self.assertEqual(data['inventory']['Ashes'], 1)
        self.assertTrue(handle_quest_answer(_context(data, random_values=[0.0, 0.99, 0.99, 0.99])))
        self.assertEqual(data['inventory']['Ashes'], 0)
        self.assertEqual(data['inventory']['Fruit blast'], 0)
        self.assertEqual(data['inventory']['Dirty blast'], 1)
        self.assertEqual(data['cooking_exp'] - before_xp, 55.0)
        self.assertEqual(data['inventory']['Coins'], 21)
        self.assertEqual(data['inventory']['Cocktail shaker'], 1)
        self.assertEqual(data['toolbelt'], belt)
        self.assertEqual(data['quests'][QUEST_ID]['progress'], 2)
        self.assertFalse(data['quests'][QUEST_ID]['completed'])
        self.assertEqual(set(data['quest_action_proofs']), {COMMISSION, PREPARATION})
        items = {item.storage_key: item.source_item_id for item in ITEM_DEFINITIONS}
        self.assertEqual(tuple(items[name] for name in ('Fruit blast', 'Ashes', 'Dirty blast')), (2084, 592, 7497))

    def test_slice_lemon_preserves_ordinary_batch_outside_the_quest(self):
        data = player(inventory={'Lemon': 28})
        data['current_utility'] = 'slice_lemon'
        before_xp = data['cooking_exp']
        belt = data['toolbelt'].copy()
        self.assertTrue(handle_utility_answer(_context(data, random_values=[0.0, 0.99, 0.99, 0.99])))
        self.assertEqual(data['inventory']['Lemon'], 0)
        self.assertEqual(data['inventory']['Lemon slices'], 28)
        self.assertEqual(data['cooking_exp'], before_xp)
        self.assertEqual(data['toolbelt'], belt)
        self.assertEqual(data['inventory']['Coins'], 0)
        self.assertEqual(data['quest_action_proofs'], [])
        self.assertFalse(data['quests'][QUEST_ID]['started'])
