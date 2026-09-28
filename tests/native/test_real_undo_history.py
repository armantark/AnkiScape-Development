"""Interleaved reviews and a reward purchase must follow Anki's real history."""

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


@unittest.skipIf(Collection is None, "Anki runtime is not installed")
class RealUndoHistoryTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ankiscape-undo-")
        self.addCleanup(temporary.cleanup)
        self.collection = Collection(str(Path(temporary.name) / "collection.anki2"))
        self.addCleanup(self.collection.close)
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        self.addCleanup(random.setstate, random.getstate())
        random.seed(260926)
        runtime_fixture._install_runtime_fakes()
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(self.collection)
        reviewer_type = sys.modules["aqt.reviewer"].Reviewer
        reviewer_type._answerCard = self._scheduler_answer
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_real_undo")
        self.reviewer = reviewer_type()
        self._prepare_player()
        self.cards = [self._new_card(front) for front in ("first", "second")]

    def _prepare_player(self):
        addon = self.addon
        addon.load_player_data()
        addon._state.current_skill = "Prayer"
        addon._state.player_data.update(
            current_prayer="bury_bones", dungeoneering_level=35, mining_level=35
        )
        addon._state.player_data["dungeoneering"]["tokens"] = 10_000
        addon._state.player_data["inventory"]["Bones"] = 10
        self.collection.set_config("ankiscape_review_action_multiplier", 1)
        self.collection.set_config("ankiscape_floating_xp_enabled", False)
        self.collection.set_config("ankiscape_popups_enabled", False)
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.purchase = captured["on_dungeoneering_command"]
        addon.save_player_data()

    def _new_card(self, front):
        note = self.collection.new_note(self.collection.models.by_name("Basic"))
        note["Front"] = front
        note["Back"] = "answer"
        self.collection.add_note(note, 1)
        return note.cards()[0]

    def _scheduler_answer(self, reviewer, ease):
        return self.collection.sched.answerCard(reviewer.card, ease)

    def _answer(self, card):
        self.reviewer.card = card
        card.start_timer()
        hooks = sys.modules["aqt"].gui_hooks
        for callback in hooks.reviewer_did_show_question:
            callback(card)
        for callback in hooks.reviewer_did_show_answer:
            callback(card)
        self.reviewer._answerCard(3)
        self.assertEqual(self.collection.get_card(card.id).reps, 1)

    def _checkpoint(self, depths):
        state = self.addon._state
        self.assertEqual(
            (len(state.review_undo_stack), len(state.direct_action_undo_stack)), depths
        )
        saved = json.loads(json.dumps(state.player_data))
        self.assertEqual(self.collection.get_config("ankiscape_player_data"), saved)
        self.assertEqual(self.collection.get_config("ankiscape_current_skill"), "Prayer")
        return copy.deepcopy(state.player_data), random.getstate()

    def _undo(self, operation, expected, depths):
        self.assertEqual(self.collection.undo_status().undo, operation)
        changes = self.collection.undo()
        self.assertEqual(changes.operation, operation)
        # AQT delivers this backend result to the registered hook after undo.
        for callback in sys.modules["aqt"].gui_hooks.state_did_undo:
            callback(changes)
        self.assertEqual(self._checkpoint(depths), expected)

    def test_answers_and_purchase_undo_in_collection_order(self):
        initial = self._checkpoint((0, 0))
        setup_operation = self.collection.undo_status().undo
        self._answer(self.cards[0])
        first = self._checkpoint((1, 0))
        self.assertGreater(first[0]["prayer_exp"], initial[0]["prayer_exp"])
        self.assertLess(first[0]["inventory"]["Bones"], 10)

        result = self.purchase("purchase_reward", {"reward_id": "coal_bag"})
        self.assertTrue(result["ok"], result)
        purchased = self._checkpoint((1, 1))
        self.assertTrue(purchased[0]["dungeoneering"]["coal_bag_owned"])
        self.assertEqual(purchased[0]["dungeoneering"]["tokens"], 6000)

        self._answer(self.cards[1])
        second = self._checkpoint((2, 1))
        self.assertGreater(second[0]["prayer_exp"], first[0]["prayer_exp"])
        self._undo("Answer Card", purchased, (1, 1))
        self.assertEqual(self.collection.get_card(self.cards[1].id).reps, 0)
        self.assertEqual(self.collection.get_card(self.cards[0].id).reps, 1)
        self._undo("AnkiScape direct action", first, (1, 0))
        self.assertEqual(self.collection.get_card(self.cards[0].id).reps, 1)
        self._undo("Answer Card", initial, (0, 0))
        self.assertEqual(self.collection.get_card(self.cards[0].id).reps, 0)
        self.assertEqual(self.collection.undo_status().undo, setup_operation)

        self.collection.close()
        self.collection.reopen()
        self.assertEqual(self._checkpoint((0, 0)), initial)
