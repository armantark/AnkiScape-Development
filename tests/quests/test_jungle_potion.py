"""The quest review owns search, cleaning and hand-in, including resumed saves."""

import copy
import json
import sys
import unittest
from dataclasses import replace
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA, UTILITY_ACTIVITY_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.contract import QuestSkillRequirement, QuestSupplyRecipe, QuestXpReward
from ankiscape.data.quest.serializers import _supply_recipe_dict
from ankiscape.logic_pure.logic_pure_quest import start_quest_pure
from ankiscape.logic_pure.quest.card_view import quest_supply_step_text_pure
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer
from tests.test_runtime_actions import _context

QUEST_ID = 'jungle_potion'
HERBS = ('snake weed', 'ardrigal', 'sito foil', 'volencia moss', "rogue's purse")


def jungle_player():
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player.update(current_quest=QUEST_ID, current_skill='Quests', herblore_level=3, herblore_exp=250.0)
    player['quests']['druidic_ritual'] = dict(started=True, progress=8, completed=True)
    player, ok = start_quest_pure(player, QUEST_ID, QUEST_DATA)
    assert ok
    return player


def review(player, speed=1):
    calls = dict(xp=[], saves=0, errors=[])
    ctx = _context(player, calls, review_action_multiplier=speed)
    ctx = replace(ctx, implemented_exp_keys_snapshot=lambda: {'herblore_exp': player['herblore_exp']},
                  show_quest_exp_delta=lambda before: calls['xp'].append(player['herblore_exp'] - before['herblore_exp']))
    handled = handle_quest_answer(ctx)
    return handled, calls


def play(player, speed=1):
    rows = []
    while not player['quests'][QUEST_ID]['completed']:
        assert len(rows) < 16
        before = player['herblore_exp']
        line = quest_supply_step_text_pure(player, QUEST_ID, QUEST_DATA)
        handled, calls = review(player, speed)
        assert handled, calls
        rows.append((line, calls, player['herblore_exp'] - before))
    return rows


class JunglePotionReviewTest(unittest.TestCase):
    def test_fifteen_cards_at_both_speeds_with_only_the_completion_dialog(self):
        for speed in (1, 10):
            with self.subTest(speed=speed):
                player = jungle_player()
                rows = play(player, speed)
                self.assertEqual(len(rows), 15)
                self.assertEqual([row[2] for row in rows], [0, 2.5, 0] * 4 + [0, 2.5, 775])
                self.assertEqual(player['herblore_exp'], 1037.5)
                self.assertEqual(player['quest_points'], 1)
                self.assertEqual(player['current_skill'], 'Quests')
                self.assertEqual([call['errors'][0][0] for _, call, _ in rows if call['errors']], ['Quest complete'])
                self.assertTrue(all(call['saves'] == 1 for _, call, _ in rows))
                self.assertFalse(any(call.get('deactivated') for _, call, _ in rows[:-1]))
                for index, herb in enumerate(HERBS):
                    self.assertEqual(rows[index * 3][1]['activity'], [f'+1 Grimy {herb}'])
                    self.assertEqual(rows[index * 3 + 1][1]['activity'], [f'+1 Clean {herb}'])
                    self.assertEqual(rows[index * 3 + 1][1]['xp'], [2.5])
                    self.assertEqual(player['inventory'][f'Grimy {herb}'], 0)
                    self.assertEqual(player['inventory'][f'Clean {herb}'], 0)

    def test_held_herbs_skip_search_or_cleaning_and_only_pay_xp_for_cleaning(self):
        for prefix, cards, xp in (('Grimy', 10, 12.5), ('Clean', 5, 0)):
            with self.subTest(prefix=prefix):
                player = jungle_player()
                player['inventory'].update({f'{prefix} {herb}': 1 for herb in HERBS})
                self.assertEqual(len(play(player)), cards)
                self.assertEqual(player['herblore_exp'], 250 + 775 + xp)

    def test_save_reload_after_each_search_cleaning_and_hand_in_keeps_the_remaining_work(self):
        for played in range(1, 15):
            with self.subTest(played=played):
                player = jungle_player()
                for _ in range(played):
                    self.assertTrue(review(player)[0])
                player = json.loads(json.dumps(player))
                self.assertEqual(len(play(player)), 15 - played)
                self.assertEqual(player['herblore_exp'], 1037.5)

    def test_started_below_level_stops_before_search_or_cleaning_without_spending(self):
        for inventory in ({}, {'Grimy snake weed': 1}, {'Clean snake weed': 1}):
            with self.subTest(inventory=inventory):
                player = jungle_player()
                player['inventory'].update(inventory)
                player['herblore_level'] = 2
                before = copy.deepcopy(player)
                handled, calls = review(player)
                self.assertFalse(handled)
                self.assertEqual(player, before)
                self.assertTrue(calls['deactivated'])
                self.assertIn('Herblore 3', calls['errors'][0][1])

    def test_new_save_below_level_cannot_start(self):
        player = jungle_player()
        del player['quests'][QUEST_ID]
        player['herblore_level'] = 2
        self.assertFalse(start_quest_pure(player, QUEST_ID, QUEST_DATA)[1])


class QuestLocalSupplyTest(unittest.TestCase):
    def test_local_recipe_pays_xp_and_checks_coins_level_and_equipment_through_the_handler(self):
        recipe = QuestSupplyRecipe(
            step='prepare the herb', product='Clean snake weed', inputs=(('Grimy snake weed', 1),), coins=3,
            required_skills=(QuestSkillRequirement('herblore', 'Herblore', 4),),
            required_tools=(('Silver sickle', 1),), xp_rewards=(QuestXpReward('herblore', 2.5),),
            source='Synthetic handler fixture',
        )
        quest = dict(QUEST_DATA[QUEST_ID], supply_recipes=(_supply_recipe_dict(recipe),))
        supplies = {'Grimy snake weed': 1, 'Coins': 3, 'Silver sickle': 1}
        for missing, reason in ((None, None), ('Coins', 'Needs Coins x3'),
                                ('Silver sickle', 'Needs Silver sickle'), ('level', 'Herblore 4')):
            with self.subTest(missing=missing), patch.dict(QUEST_DATA, {QUEST_ID: quest}):
                player = jungle_player()
                player['inventory'].update(supplies)
                player['herblore_level'] = 4
                if missing == 'level':
                    player['herblore_level'] = 3
                elif missing:
                    player['inventory'][missing] = 0
                before = copy.deepcopy(player)
                handled, calls = review(player)
                self.assertEqual(handled, missing is None)
                if missing:
                    self.assertEqual(player, before)
                    self.assertIn(reason, calls['errors'][0][1])
                else:
                    self.assertEqual(player['inventory']['Clean snake weed'], 1)
                    self.assertEqual(player['inventory']['Coins'], 0)
                    self.assertEqual(player['inventory']['Silver sickle'], 1)
                    self.assertEqual(player['herblore_exp'], 252.5)
                    self.assertEqual(calls['xp'], [2.5])
                self.assertFalse(any(row.get('output_item') == 'Clean snake weed' for row in UTILITY_ACTIVITY_DATA.values()))


class JunglePotionReviewLoopTest(unittest.TestCase):
    def test_real_answers_finish_in_fifteen_cards_without_action_switches_at_both_speeds(self):
        from tests.quest_catalog.test_murder_mystery_review import review_session
        from tests.test_early_quest_item_routes import _answer_review

        for speed in (1, 10):
            with self.subTest(speed=speed), review_session() as (addon, collection, errors):
                addon._state.player_data.update(jungle_player())
                collection.set_config('ankiscape_review_action_multiplier', speed)
                addon._select_review_action('Quests')
                core_logic = sys.modules[f'{addon.__name__}.core.logic']
                self.enterContext(patch.object(core_logic, 'show_level_up_dialog'))
                for card in range(15):
                    self.assertEqual(addon._state.current_skill, 'Quests')
                    _answer_review(addon)
                    self.assertEqual(addon._state.player_data['quests'][QUEST_ID]['completed'], card == 14)
                self.assertEqual(addon._state.player_data['herblore_exp'], 1037.5)
                self.assertEqual([title for title, _ in errors], ['Quest complete'])
                self.assertEqual(collection._store['ankiscape_player_data'], addon._state.player_data)

    def test_undo_of_cleaning_restores_the_grimy_herb_xp_and_quest_stage(self):
        from types import SimpleNamespace
        from tests.quest_catalog.test_murder_mystery_review import review_session
        from tests.test_early_quest_item_routes import _answer_review

        with review_session() as (addon, collection, errors):
            addon._state.player_data.update(jungle_player())
            addon._select_review_action('Quests')
            core_logic = sys.modules[f'{addon.__name__}.core.logic']
            self.enterContext(patch.object(core_logic, 'show_level_up_dialog'))
            _answer_review(addon)
            before = copy.deepcopy(addon._state.player_data)
            _answer_review(addon)
            self.assertEqual(addon._state.player_data['herblore_exp'], 252.5)
            self.assertEqual(addon._state.player_data['inventory']['Clean snake weed'], 1)
            addon._on_state_did_undo(SimpleNamespace(
                operation='Answer Card', changes=SimpleNamespace(study_queues=True, card=True),
            ))
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store['ankiscape_player_data'], before)
            self.assertEqual(addon._state.current_skill, 'Quests')
            _answer_review(addon)
            self.assertEqual(addon._state.player_data['herblore_exp'], 252.5)
            self.assertEqual(errors, [])
