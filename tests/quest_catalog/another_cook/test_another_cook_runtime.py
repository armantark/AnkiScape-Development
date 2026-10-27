"""The existing answer commit and snapshot Undo own both opening transactions."""

import copy
import random
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tests.quest_catalog.test_murder_mystery_review import review_session, prepare_answer
from tests.test_integration_smoke import _FakeReviewer
from tests.test_early_quest_item_routes import _answer_review
from tests.quest_catalog.another_cook.test_another_cook_transactions import (
    player, transaction_snapshot, QUEST_ID, COMMISSION, PREPARATION,
)


def configure(addon, inventory=None):
    sys.modules['aqt'].mw = addon.mw
    addon.mw.col.set_config('ankiscape_popups_enabled', False)
    addon._state.player_data = player(inventory=inventory)
    addon.check_achievements(addon._state.player_data)
    addon._state.current_skill = 'None'
    assert addon.on_set_quest(QUEST_ID)
    addon._select_review_action('Quests')
    addon.save_player_data()


def snapshot(addon):
    return transaction_snapshot(addon._state.player_data)


def undo_answer(addon):
    addon._on_state_did_undo(SimpleNamespace(
        operation='Answer Card', changes=SimpleNamespace(study_queues=True, card=True),
    ))


class AnotherCookRuntimeTest(unittest.TestCase):
    def test_one_phase_each_card_at_speeds_1_and_20_duplicate_and_later_blocker(self):
        for speed in (1, 20):
            with self.subTest(speed=speed), review_session(activity_feedback=True) as (addon, collection, errors):
                configure(addon, {'Ashes': 2, 'Fruit blast': 2, 'Fruit blast (9514)': 1})
                collection.set_config('ankiscape_review_action_multiplier', speed)
                popup = Mock()
                addon.mw.exp_popup = popup
                before_xp = addon._state.player_data['cooking_exp']
                _answer_review(addon)
                data = addon._state.player_data
                self.assertEqual(data['inventory']['Coins'], 100)
                self.assertEqual(data['inventory']['Ashes'], 2)
                self.assertEqual(data['quest_action_proofs'], [COMMISSION])
                self.assertEqual(data['quests'][QUEST_ID]['progress'], 1)
                self.assertEqual(data['cooking_exp'], before_xp)
                commission_notice = popup.show_text.call_args.args[0]
                self.assertEqual(' '.join(commission_notice.splitlines()[:-1]),
                                 "The Cook asked for 1 Eye of newt, 1 Greenman's ale, 1 Rotten tomato and 1 Dirty blast. "
                                 "+100 Coins for ingredients; keep the change. Add Ashes to a Fruit blast; "
                                 "Blurberry's premade drink will not work.")
                self.assertEqual(commission_notice.splitlines()[-1], "Recipe for Disaster: Another Cook's Quest 1/4")
                self.assertEqual(popup.show_text.call_count, 1)
                self.assertEqual(data['review_event_log'][-1]['text'], commission_notice)
                self.assertEqual(collection.get_config('ankiscape_player_data')['review_event_log'], data['review_event_log'])
                committed = snapshot(addon)
                addon.on_answer_card(_FakeReviewer(), 4, lambda *_args: 'answered')
                self.assertEqual(snapshot(addon), committed)
                self.assertEqual(popup.show_text.call_count, 1)
                _answer_review(addon)
                self.assertEqual(data['inventory']['Coins'], 100)
                self.assertEqual(data['inventory']['Fruit blast'], 1)
                self.assertEqual(data['inventory']['Fruit blast (9514)'], 1)
                self.assertEqual(data['inventory']['Dirty blast'], 1)
                self.assertEqual(data['cooking_exp'], before_xp + 5)
                self.assertEqual(data['quests'][QUEST_ID]['progress'], 2)
                self.assertEqual(set(data['quest_action_proofs']), {COMMISSION, PREPARATION})
                self.assertEqual(errors, [])
                preparation_notice = data['review_event_log'][-1]['text']
                self.assertEqual(' '.join(preparation_notice.splitlines()[:-1]),
                                 '+1 Dirty blast: added Ashes to a Fruit blast.')
                self.assertEqual(preparation_notice.splitlines()[-1], "Recipe for Disaster: Another Cook's Quest 2/4")
                self.assertEqual(collection.get_config('ankiscape_player_data')['review_event_log'], data['review_event_log'])
                boundary = snapshot(addon)
                _answer_review(addon)
                self.assertEqual(snapshot(addon), boundary)
                self.assertFalse(data['quests'][QUEST_ID]['completed'])
                self.assertEqual(data['inventory'].get('An invitation to the feast', 0), 0)
                self.assertEqual(data['quest_points'], 0)
                self.assertFalse(data['quests']['recipe_for_disaster_freeing_evil_dave']['started'])
                quest_logic = sys.modules[f'{addon.__name__}.logic_pure.logic_pure_quest']
                self.assertIn(addon.QUEST_DATA[QUEST_ID]['display_name'], quest_logic.quest_locked_reasons_pure(
                    data, 'recipe_for_disaster_freeing_evil_dave', addon.QUEST_DATA,
                ))

    def test_again_at_either_boundary_grants_neither_phase(self):
        with review_session() as (addon, _collection, _errors):
            configure(addon, {'Ashes': 1, 'Fruit blast': 1})
            for _ in range(2):
                before = snapshot(addon)
                prepare_answer(addon)
                addon.on_answer_card(_FakeReviewer(), 1, lambda *_args: 'answered')
                self.assertEqual(snapshot(addon), before)
                _answer_review(addon)

    def test_failed_and_vetoed_answers_rollback_each_transaction(self):
        for phase in ('commission', 'prepare'):
            for raises in (False, True):
                with self.subTest(phase=phase, raises=raises):
                    self._assert_rejection(phase, raises)

    def _assert_rejection(self, phase, raises):
        with review_session() as (addon, collection, _errors):
            configure(addon, {'Ashes': 1, 'Fruit blast (9514)': 1})
            if phase == 'prepare':
                _answer_review(addon)
            before = copy.deepcopy(addon._state.player_data)
            before_snapshot, rng = snapshot(addon), random.getstate()
            undo_depth = len(addon._state.review_undo_stack)
            prepare_answer(addon)

            def reject(_reviewer, _ease):
                expected = COMMISSION if phase == 'commission' else PREPARATION
                self.assertIn(expected, addon._state.player_data['quest_action_proofs'])
                if raises:
                    raise RuntimeError('scheduler rejected answer')
                return 'vetoed'

            reviewer = SimpleNamespace(state='answer')
            if raises:
                with self.assertRaisesRegex(RuntimeError, 'scheduler rejected'):
                    addon.on_answer_card(reviewer, 3, reject)
            else:
                self.assertEqual(addon.on_answer_card(reviewer, 3, reject), 'vetoed')
            self.assertEqual(addon._state.player_data, before)
            self.assertEqual(collection._store['ankiscape_player_data'], before)
            self.assertEqual(snapshot(addon), before_snapshot)
            self.assertEqual(random.getstate(), rng)
            self.assertEqual(len(addon._state.review_undo_stack), undo_depth)

    def test_save_migrate_reopen_both_boundaries_and_missing_retry_no_repayment(self):
        with review_session() as (addon, collection, _errors):
            configure(addon)
            _answer_review(addon)
            commission = snapshot(addon)
            clock_before = addon._state.player_data['world_clock']['in_day_ticks']
            with patch.object(addon, '_advance_clocks_for_answer', wraps=addon._advance_clocks_for_answer) as clock:
                _answer_review(addon)
            clock.assert_called_once_with(True)
            self.assertEqual(addon._state.player_data['world_clock']['in_day_ticks'], clock_before + 6)
            self.assertEqual(snapshot(addon), commission)
            addon.load_player_data()
            self.assertEqual(snapshot(addon), commission)
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            data = addon._state.player_data
            data['inventory'].update({'Ashes': 1, 'Fruit blast (9514)': 1})
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            addon._select_review_action('Quests')
            _answer_review(addon)
            prepared = snapshot(addon)
            addon.save_player_data()
            persisted = copy.deepcopy(collection._store['ankiscape_player_data'])
            addon._state.player_data = {}
            addon.load_player_data()
            self.assertEqual(snapshot(addon), prepared)
            self.assertEqual(collection._store['ankiscape_player_data'], persisted)
            self.assertTrue(addon.on_set_quest(QUEST_ID))
            self.assertEqual(snapshot(addon), prepared)

    def test_full_snapshot_undo_reanswer_at_each_boundary_exact_variant_and_level(self):
        for cocktail in ('Fruit blast', 'Fruit blast (9514)'):
            with self.subTest(cocktail=cocktail), review_session() as (addon, collection, _errors):
                configure(addon, {'Ashes': 1, cocktail: 1, 'Logs': 28})
                addon._state.player_data['carried_inventory'] = {'quest:' + QUEST_ID: {'Logs': 28}}
                constants = sys.modules[f'{addon.__name__}.core.constants']
                addon._state.player_data['cooking_exp'] = constants.EXP_TABLE[10] - 1
                addon.save_player_data()
                for phase in ('commission', 'prepare'):
                    before = copy.deepcopy(addon._state.player_data)
                    before_snapshot = snapshot(addon)
                    _answer_review(addon)
                    after = copy.deepcopy(addon._state.player_data)
                    undo_answer(addon)
                    self.assertEqual(addon._state.player_data, before)
                    self.assertEqual(collection._store['ankiscape_player_data'], before)
                    self.assertEqual(snapshot(addon), before_snapshot)
                    _answer_review(addon)
                    self.assertEqual(addon._state.player_data, after)
                    self.assertEqual(addon._state.player_data['inventory']['Coins'], 100)
                self.assertEqual(addon._state.player_data['cooking_level'], 11)
                self.assertEqual(addon._state.player_data['inventory'][cocktail], 0)

    def test_legacy_reopen_never_invents_receipts(self):
        with review_session() as (addon, _collection, _errors):
            configure(addon)
            data = addon._state.player_data
            data['quests'][QUEST_ID].update(progress=2)
            data['inventory'].update({'Coins': 876, 'Dirty blast': 2, 'Ashes': 1, 'Fruit blast': 1})
            addon.save_player_data()
            before = snapshot(addon)
            addon.load_player_data()
            _answer_review(addon)
            self.assertEqual(snapshot(addon), before)
            self.assertEqual(addon._state.player_data['quest_action_proofs'], [])
