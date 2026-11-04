"""Quest reviews make a missing stage item from the supplies the player brought."""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, UTILITY_ACTIVITY_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_quest import start_quest_pure
from ankiscape.logic_pure.quest.card_view import quest_supply_step_text_pure
from ankiscape.runtime import runtime_actions_quest
from tests import test_main_menu_widget as menu_fixture
from tests.main_menu.fixtures import MainMenuWidgetTest
from tests.test_runtime_actions import _context

QUEST_ID = 'goblin_diplomacy'
SUPPLIES = {'Redberries': 3, 'Onion': 2, 'Woad leaf': 2, 'Coins': 15}


def started(inventory, quest_id=QUEST_ID):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player['inventory'].update(inventory)
    player, ok = start_quest_pure(player, quest_id, QUEST_DATA)
    if not ok:
        raise AssertionError(f'{quest_id} did not start')
    return player


def held(player):
    return {item: amount for item, amount in player['inventory'].items() if amount}


class SupplyStepReviewTest(unittest.TestCase):
    def review(self, player):
        calls = {'xp': [], 'saves': 0, 'errors': []}
        with patch.object(runtime_actions_quest, '_record_action'):
            handled = runtime_actions_quest.handle_quest_answer(_context(player, calls))
        return handled, calls

    def run_quest(self, player, quest_id=QUEST_ID):
        """Each review's card line before it and its notice, until the quest completes."""
        rows = []
        while not player['quests'][quest_id]['completed']:
            self.assertLess(len(rows), 12, rows)
            line = quest_supply_step_text_pure(player, quest_id, QUEST_DATA)
            handled, calls = self.review(player)
            self.assertTrue(handled, calls['errors'])
            self.assertEqual(calls['saves'], 1)
            rows.append((line, *calls['activity']))
        return rows

    def test_raw_supplies_finish_the_quest_in_ten_reviews_and_spend_every_supply(self):
        player = started(SUPPLIES)
        self.assertEqual(self.run_quest(player), [
            ('Next: Goblin mail from the crates', '+3 Goblin mail'),
            ("Next: Aggie's red dye", '+1 Red dye'),
            ("Next: Aggie's yellow dye", '+1 Yellow dye'),
            ('Next: Orange dye', '+1 Orange dye'),
            ('Next: Orange goblin mail', '+1 Orange goblin mail'),
            ('', 'Goblin Diplomacy 2/4'),
            ("Next: Aggie's blue dye", '+1 Blue dye'),
            ('Next: Blue goblin mail', '+1 Blue goblin mail'),
            ('', 'Goblin Diplomacy 3/4'),
            ('', 'Goblin Diplomacy complete'),
        ])
        self.assertEqual(held(player), {'Gold bar': 1})
        self.assertEqual(player['quest_points'], 5)
        self.assertEqual(player['crafting_exp'], 200.0)

    def test_held_dyes_and_mail_skip_the_steps_that_make_them(self):
        cases = (
            ({'Orange dye': 1, 'Woad leaf': 2, 'Coins': 5},
             ['+3 Goblin mail', '+1 Orange goblin mail', 'Goblin Diplomacy 2/4',
              '+1 Blue dye', '+1 Blue goblin mail', 'Goblin Diplomacy 3/4', 'Goblin Diplomacy complete']),
            ({'Orange goblin mail': 1, 'Woad leaf': 2, 'Coins': 5},
             ['Goblin Diplomacy 2/4', '+3 Goblin mail', '+1 Blue dye', '+1 Blue goblin mail',
              'Goblin Diplomacy 3/4', 'Goblin Diplomacy complete']),
            ({'Orange goblin mail': 1, 'Blue goblin mail': 1, 'Goblin mail': 1},
             ['Goblin Diplomacy 2/4', 'Goblin Diplomacy 3/4', 'Goblin Diplomacy complete']),
        )
        for inventory, notices in cases:
            with self.subTest(inventory=inventory):
                player = started(inventory)
                self.assertEqual([row[1] for row in self.run_quest(player)], notices)
                self.assertEqual(player['quest_points'], 5)

    def test_a_missing_supply_stops_the_quest_before_any_supply_is_spent(self):
        player = started(dict(SUPPLIES, Redberries=2))
        before = copy.deepcopy(player)
        handled, calls = self.review(player)
        self.assertFalse(handled)
        self.assertEqual(player, before)
        self.assertEqual(calls['saves'], 0)
        self.assertTrue(calls['deactivated'])
        title, message = calls['errors'][0]
        self.assertEqual(title, 'Quest blocked')
        self.assertIn("Needs Redberries x3 for Aggie's red dye", message)

    def test_a_second_quest_makes_its_stage_item_from_declared_recipes_alone(self):
        stage = dict(QUEST_DATA[QUEST_ID]['stage_requirements'][0], consumed_inventory={'Bread dough': 1})
        recipes = (('wet_flour_to_bread_dough', 'bread dough'), ('grind_grain_to_flour', 'a pot of flour'),
                   ('draw_bucket_of_water', 'a bucket of water'))
        quest = dict(
            QUEST_DATA[QUEST_ID], id='bread_errand', display_name='Bread Errand', stages=1,
            stage_requirements=(stage,), journal_stages={},
            supply_recipes=tuple(
                {'utility_id': key, 'step': step, 'action': UTILITY_ACTIVITY_DATA[key]} for key, step in recipes
            ),
        )
        with patch.dict(QUEST_DATA, {'bread_errand': quest}):
            player = started({'Wheat': 1, 'Empty pot': 1, 'Bucket': 1}, 'bread_errand')
            self.assertEqual(self.run_quest(player, 'bread_errand'), [
                ('Next: A pot of flour', '+1 Pot of flour'),
                ('Next: A bucket of water', '+1 Bucket of water'),
                ('Next: Bread dough', '+1 Bread dough'),
                ('', 'Bread Errand complete'),
            ])
        self.assertEqual(held(player), {'Empty pot': 1, 'Bucket': 1, 'Gold bar': 1})


@unittest.skipUnless(menu_fixture.HAS_AQT, 'aqt/PyQt6 required')
class SupplyStepCardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        MainMenuWidgetTest.setUpClass()

    def setUp(self):
        self.fixture = MainMenuWidgetTest(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.tearDown)

    def test_card_names_the_next_supply_step_or_the_missing_supply(self):
        cases = ((SUPPLIES, 'Next: Goblin mail from the crates', True),
                 (dict(SUPPLIES, Redberries=2), "Blocked: Needs Redberries x3 for Aggie's red dye", False))
        for inventory, text, enabled in cases:
            with self.subTest(text=text):
                dialog = self.fixture._open(started(inventory))
                menu_fixture._open_quests_tab(dialog)
                status = dialog.findChild(menu_fixture.QLabel, f'questStatus_{QUEST_ID}')
                action = dialog.findChild(menu_fixture.QPushButton, f'questAction_{QUEST_ID}')
                self.assertEqual(status.text(), text)
                self.assertEqual(action.isEnabled(), enabled)
                dialog.close()
