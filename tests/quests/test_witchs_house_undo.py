"""Real Anki review history restores whole Witch transactions and saved custody."""

import copy
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests import test_integration_smoke as runtime_fixture
from tests.test_storage_runtime import Collection
from .test_witchs_house import (
    QUEST_ID, DIARY, MAGNET, BACKROOM_KEY, BALL, READ_DIARY, PASS_GATE,
    TAKE_DIARY, TAKE_GLOVES, TAKE_KEY, TAKE_BALL, RESUME_KEY, EXPERIMENTS,
    player_at, buy_cheese, wear_leather, train_for_experiments,
)

PLAYER_KEY = 'ankiscape_player_data'
TRANSACTION_KEYS = (
    'inventory', 'equipment', 'quests', 'quest_action_proofs', 'quest_points',
    'quest_combat_encounters', 'quest_combat_encounter_counts',
    'quest_combat_active_encounters', 'quest_combat_encounter', 'combat_encounter', 'combat_current_levels',
    'combat_lifepoints', 'combat_last_result', 'combat_supply_loadout', 'pending_skill_exp_rewards',
    RESUME_KEY, 'witchs_house_legacy_completed', 'attack_exp', 'strength_exp',
    'defense_exp', 'constitution_exp',
)


@unittest.skipIf(Collection is None, 'Real Anki Collection is required')
class WitchsHouseRealUndoTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='witch-undo-')
        self.addCleanup(temporary.cleanup)
        self.collection = Collection(str(Path(temporary.name) / 'collection.anki2'))
        self.addCleanup(self.collection.close)
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        self.addCleanup(random.setstate, random.getstate())
        random.seed(1470)
        rolls = patch.object(random, "random", return_value=0.5)
        rolls.start()
        self.addCleanup(rolls.stop)
        runtime_fixture._install_runtime_fakes()
        sys.modules['aqt'].mw = runtime_fixture._DummyMW(self.collection)
        reviewer_type = sys.modules['aqt.reviewer'].Reviewer
        reviewer_type._answerCard = self._scheduler_answer
        self.addon = runtime_fixture._load_addon_as_package('ankiscape_witch_real_undo')
        self.reviewer = reviewer_type()
        self.collection.set_config('ankiscape_review_action_multiplier', 1)
        self.collection.set_config('ankiscape_floating_xp_enabled', False)
        self.collection.set_config('ankiscape_popups_enabled', False)
        self.addon.show_error_message = lambda *_args: None
        self.addon._show_activity_gain = lambda *_args: None
        self.addon.update_review_hud = lambda *_args: None
        self.addon._show_exp = lambda *_args: None
        self.addon.ui.update_menu_visibility = lambda *_args: None
        self.addon.load_player_data()
        self.set_player(buy_cheese(train_for_experiments(player_at())))

    def set_player(self, player):
        self.addon._state.player_data = player
        self.addon._state.current_skill = 'Quests'
        self.addon._state.review_undo_stack.clear()
        self.addon._state.direct_action_undo_stack.clear()
        self.addon.save_player_data()
        self.addon.load_player_data()
        self.addon._state.current_skill = 'Quests'
        self.addon.save_player_data()

    @property
    def player(self):
        return self.addon._state.player_data

    def _scheduler_answer(self, reviewer, ease):
        return self.collection.sched.answerCard(reviewer.card, ease)

    def _new_card(self):
        note = self.collection.new_note(self.collection.models.by_name('Basic'))
        note['Front'] = str(self.collection.note_count())
        note['Back'] = 'answer'
        self.collection.add_note(note, 1)
        return note.cards()[0]

    def _answer(self, card):
        self.reviewer.card = self.collection.get_card(card.id)
        self.reviewer.card.start_timer()
        hooks = sys.modules['aqt'].gui_hooks
        for callback in hooks.reviewer_did_show_question:
            callback(self.reviewer.card)
        for callback in hooks.reviewer_did_show_answer:
            callback(self.reviewer.card)
        self.reviewer._answerCard(3)
        self.assertEqual(self.collection.get_card(card.id).reps, 1)

    def checkpoint(self):
        saved = json.loads(json.dumps(self.player))
        self.assertEqual(self.collection.get_config(PLAYER_KEY), saved)
        return {key: copy.deepcopy(saved.get(key)) for key in TRANSACTION_KEYS}

    def review_undo_replay(self):
        card = self._new_card()
        self.addon._state.current_skill = 'Quests'
        self.addon.save_player_data()
        before = self.checkpoint()
        before_rng = random.getstate()
        depth = len(self.addon._state.review_undo_stack)
        self._answer(card)
        earned = self.checkpoint()
        earned_rng = random.getstate()
        self.assertEqual(len(self.addon._state.review_undo_stack), min(30, depth + 1))
        self.assertEqual(self.collection.undo_status().undo, 'Answer Card')
        changes = self.collection.undo()
        self.assertEqual(changes.operation, 'Answer Card')
        for callback in sys.modules['aqt'].gui_hooks.state_did_undo:
            callback(changes)
        self.assertEqual(self.collection.get_card(card.id).reps, 0)
        self.assertEqual(self.checkpoint(), before)
        self.assertEqual(random.getstate(), before_rng)
        self.assertEqual(len(self.addon._state.review_undo_stack), min(29, depth))
        self._answer(card)
        self.assertEqual(self.checkpoint(), earned)
        self.assertEqual(random.getstate(), earned_rng)
        return before, earned

    def reopen(self):
        before = self.checkpoint()
        self.collection.close()
        self.collection.reopen()
        self.addon.load_player_data()
        self.assertEqual(self.checkpoint(), before)
        return before

    def advance_to_fights(self, until=12):
        while self.player['quests'][QUEST_ID]['progress'] < until:
            stage = max(1, self.player['quests'][QUEST_ID]['progress'])
            if stage == 6:
                wear_leather(self.player)
            before, after = self.review_undo_replay()
            if stage == 3:
                self.assertEqual(after['inventory'][DIARY], 1)
                self.assertNotIn(TAKE_DIARY, before['quest_action_proofs'])
                self.assertIn(TAKE_DIARY, after['quest_action_proofs'])
                self.assertNotIn(READ_DIARY, after['quest_action_proofs'])
            if stage == 4:
                self.assertEqual(after['inventory'][DIARY], before['inventory'][DIARY])
                self.assertIn(READ_DIARY, after['quest_action_proofs'])
            if stage == 5:
                self.assertIn(TAKE_GLOVES, after['quest_action_proofs'])
            if stage == 6:
                self.assertIn(PASS_GATE, after['quest_action_proofs'])
            if stage == 10:
                self.assertEqual(after['inventory'][BACKROOM_KEY], 1)
                self.assertIn(TAKE_KEY, after['quest_action_proofs'])

    def resolve_fights(self):
        for eid, _ in EXPERIMENTS:
            observed_partial = False
            for _ in range(300):
                before, after = self.review_undo_replay()
                self.assertEqual(after['quests'][QUEST_ID]['progress'], 12)
                if eid in after['quest_combat_encounters'].get(QUEST_ID, ()):
                    break
                lifepoints = after['quest_combat_active_encounters'].get(QUEST_ID, {}).get(eid, 0)
                if lifepoints:
                    observed_partial = True
                    self.assertGreater(lifepoints, 0)
                else:
                    self.assertEqual(after['combat_last_result']['reason'], 'quest_combat_bank_run')
            else:
                self.fail(f'Fight did not complete: {eid}')
            self.assertTrue(observed_partial, f'Must exercise partial combat Undo for {eid}')
            self.reopen()

    def test_route_deeds_each_fight_and_hand_in_use_real_collection_undo_and_persist(self):
        self.advance_to_fights()
        self.reopen()
        self.resolve_fights()
        self.review_undo_replay()  # all fights complete -> Ball pickup stage
        self.assertEqual(self.player['quests'][QUEST_ID]['progress'], 13)
        self.review_undo_replay()
        self.assertEqual(self.player['inventory'][BALL], 1)
        self.assertIn(TAKE_BALL, self.player['quest_action_proofs'])
        before, after = self.review_undo_replay()
        self.assertEqual(after['inventory'][BALL], 0)
        self.assertTrue(after['quests'][QUEST_ID]['completed'])
        self.assertEqual(after['quest_points'] - before['quest_points'], 4)
        self.assertEqual(after['constitution_exp'] - before['constitution_exp'], 6325)
        self.reopen()

    def test_distinct_key_and_postfight_ball_recoveries_undo_and_replay_without_combat_replay(self):
        self.advance_to_fights(until=11)
        self.player['inventory'][BACKROOM_KEY] = 0
        before, recovered = self.review_undo_replay()
        self.assertEqual(recovered['inventory'][BACKROOM_KEY], 1)
        self.assertEqual(recovered['quests'], before['quests'])
        self.assertEqual(recovered['constitution_exp'], before['constitution_exp'])
        self.reopen()
        self.review_undo_replay()  # unlock with recovered key
        self.resolve_fights()
        self.review_undo_replay()
        self.review_undo_replay()
        self.player['inventory'][BALL] = 0
        self.player['inventory'][BACKROOM_KEY] = 0
        before, recovered = self.review_undo_replay()
        self.assertEqual(recovered['inventory'][BALL], 1)
        self.assertEqual(recovered['inventory'][BACKROOM_KEY], 0)
        self.assertEqual(recovered['quests'], before['quests'])
        self.assertEqual(recovered['quest_combat_encounters'], before['quest_combat_encounters'])
        self.assertEqual(recovered['quest_combat_encounter_counts'], before['quest_combat_encounter_counts'])
        self.assertEqual(recovered['constitution_exp'], before['constitution_exp'])
        self.assertEqual(recovered['quest_points'], before['quest_points'])
        self.reopen()
        before, after = self.review_undo_replay()
        self.assertEqual(after['quest_points'] - before['quest_points'], 4)
        self.reopen()

    def test_migrated_gate_resume_scalar_undo_replay_and_reopen_are_one_transaction(self):
        old = train_for_experiments(player_at(9))
        old['inventory'][MAGNET] = 1
        old['config_version'] = 125
        self.collection.set_config(PLAYER_KEY, old)
        self.addon.load_player_data()
        self.assertEqual(self.player['quests'][QUEST_ID]['progress'], 3)
        self.assertEqual(self.player[RESUME_KEY], 12)
        self.addon.save_player_data()
        for step in (3, 4, 5):
            self.assertEqual(self.player['quests'][QUEST_ID]['progress'], step)
            self.review_undo_replay()
            self.reopen()
        wear_leather(self.player)
        before, after = self.review_undo_replay()
        self.assertEqual(before[RESUME_KEY], 12)
        self.assertEqual(after[RESUME_KEY], 0)
        self.assertEqual(before['quests'][QUEST_ID]['progress'], 6)
        self.assertEqual(after['quests'][QUEST_ID]['progress'], 12)
        self.assertNotIn(PASS_GATE, before['quest_action_proofs'])
        self.assertIn(PASS_GATE, after['quest_action_proofs'])
        self.assertEqual(after['inventory'][MAGNET], 1)
        self.reopen()
