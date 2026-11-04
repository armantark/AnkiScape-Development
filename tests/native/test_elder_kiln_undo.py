"""Hatching Answers must follow Anki's real Undo history and survive collection reopen."""

import copy
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

from tests import test_integration_smoke as runtime_fixture
from tests.quest_openings.test_elder_kiln_data import ENTRY_LEVELS, PROOF, QUEST_ID
from tests.quest_openings.test_elder_kiln_logic import best_command
from tests.test_storage_runtime import Collection

STATE_KEY = "elder_kiln_hatching"


def until(phase, chooser=best_command):
    def run(command, observation):
        for _ in range(600):
            if observation["phase"] == phase:
                return observation
            observation = command("offer" if observation["can_offer"] else chooser(observation))
        raise AssertionError(f"never reached {phase}")
    return run


def sink(observation):
    return "cast:water_wave" if observation["phase"] == "active" else "wait_step"


def presenter(*steps):
    """The same scripted player on first play and on replay: real commands only."""
    def present(command, observation):
        for step in steps:
            observation = step(command, observation) if callable(step) else command(step)
    return present


PHASES = (
    ("pause", presenter("offer", "cast:fire_blast", "wait_step"), "preparing"),
    ("active progress", presenter(until("active"), "cast:fire_bolt", "wait_change"), "active"),
    ("failure", presenter(until("failed", sink)), "failed"),
    ("retry", presenter("retry", "wait_step"), "preparing"),
    ("hatch", presenter(until("hatched")), "hatched"),
)


@unittest.skipIf(Collection is None, "Anki runtime is not installed")
class ElderKilnUndoTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="ankiscape-elder-kiln-")
        self.addCleanup(temporary.cleanup)
        self.collection = Collection(str(Path(temporary.name) / "collection.anki2"))
        self.addCleanup(self.collection.close)
        modules = patch.dict(sys.modules)
        modules.start()
        self.addCleanup(modules.stop)
        self.addCleanup(random.setstate, random.getstate())
        random.seed(1440)
        runtime_fixture._install_runtime_fakes()
        sys.modules["aqt"].mw = runtime_fixture._DummyMW(self.collection)
        reviewer_type = sys.modules["aqt.reviewer"].Reviewer
        reviewer_type._answerCard = self._scheduler_answer
        self.addon = runtime_fixture._load_addon_as_package("ankiscape_elder_kiln_undo")
        self.dialog = sys.modules["ankiscape_elder_kiln_undo.core.logic"]
        self.reviewer = reviewer_type()
        self._prepare_player()
        self.cards = [self._new_card(str(index)) for index in range(len(PHASES) + 1)]

    def _prepare_player(self):
        from ankiscape.core.constants import EXP_TABLE

        addon = self.addon
        addon.load_player_data()
        addon._state.current_skill = "Quests"
        data = addon._state.player_data
        for skill_id, level in ENTRY_LEVELS.items():
            data[f"{skill_id}_level"], data[f"{skill_id}_exp"] = level, EXP_TABLE[level - 1]
        data.update(current_quest=QUEST_ID, dungeoneering_level=35, dungeoneering_exp=EXP_TABLE[34])
        data["dungeoneering"]["tokens"] = 10_000
        for key, value in (("ankiscape_review_action_multiplier", 1), ("ankiscape_floating_xp_enabled", False),
                           ("ankiscape_popups_enabled", False)):
            self.collection.set_config(key, value)
        captured = {}
        addon.ui.show_main_menu = lambda *args, **kwargs: captured.update(kwargs)
        addon._on_main_menu()
        self.purchase = captured["on_dungeoneering_command"]
        addon.save_player_data()
        # Establish canonical persisted defaults through the real load path.
        addon.load_player_data()
        addon.save_player_data()

    def _new_card(self, front):
        note = self.collection.new_note(self.collection.models.by_name("Basic"))
        note["Front"], note["Back"] = front, "answer"
        self.collection.add_note(note, 1)
        return note.cards()[0]

    def _scheduler_answer(self, reviewer, ease):
        return self.collection.sched.answerCard(reviewer.card, ease)

    def _answer(self, card, script):
        self.reviewer.card = card
        card.start_timer()
        hooks = sys.modules["aqt"].gui_hooks
        for callback in hooks.reviewer_did_show_question:
            callback(card)
        for callback in hooks.reviewer_did_show_answer:
            callback(card)
        with patch.object(self.dialog, "present_elder_kiln_hatching", script):
            self.reviewer._answerCard(3)
        self.assertEqual(self.collection.get_card(card.id).reps, 1)

    def _checkpoint(self, depths=None):
        state = self.addon._state
        if depths is not None:
            self.assertEqual((len(state.review_undo_stack), len(state.direct_action_undo_stack)), depths)
        saved = self.collection.get_config("ankiscape_player_data")
        canonical = json.loads(json.dumps(state.player_data))
        self.assertEqual({key: (saved.get(key), canonical.get(key)) for key in set(saved) | set(canonical)
                          if saved.get(key) != canonical.get(key)}, {})
        self.assertEqual(self.collection.get_config("ankiscape_current_skill"), "Quests")
        return copy.deepcopy(state.player_data), random.getstate(), state.current_skill

    def _undo(self, operation, expected, depths=None):
        self.assertEqual(self.collection.undo_status().undo, operation)
        changes = self.collection.undo()
        self.assertEqual(changes.operation, operation)
        for callback in sys.modules["aqt"].gui_hooks.state_did_undo:
            callback(changes)
        self.assertEqual(self._checkpoint(depths), expected)

    def _reopen(self, expected):
        self.collection.close()
        self.collection.reopen()
        self.addon._state.player_data = {}
        self.addon._state.current_skill = "None"
        self.addon.load_player_data()
        self.assertEqual(self._checkpoint(), expected)

    def test_every_phase_undoes_and_replays_identically(self):
        for index, (label, script, phase) in enumerate(PHASES):
            with self.subTest(phase=label):
                card = self.cards[index]
                before = self._checkpoint()
                self._answer(card, script)
                earned = self._checkpoint()
                data = earned[0]
                self.assertEqual(data[STATE_KEY]["phase"], phase)
                self.assertEqual(data["quests"][QUEST_ID]["progress"], 2 if phase == "hatched" else 0)
                self.assertEqual(data["quest_action_proofs"].count(PROOF), 1 if phase == "hatched" else 0)
                self._undo("Answer Card", before)
                self.assertEqual(self.collection.get_card(card.id).reps, 0)
                self._answer(self.collection.get_card(card.id), script)
                self.assertEqual(self._checkpoint(), earned)
        self.assertEqual(self.addon._state.player_data["quests"][QUEST_ID],
                         dict(started=True, completed=False, progress=2))

    def test_direct_action_between_openings_undoes_in_collection_order(self):
        initial = self._checkpoint((0, 0))
        self._answer(self.cards[0], PHASES[0][1])
        paused = self._checkpoint((1, 0))
        result = self.purchase("purchase_reward", {"reward_id": "coal_bag"})
        self.assertTrue(result["ok"], result)
        purchased = self._checkpoint((1, 1))
        self.assertTrue(purchased[0]["dungeoneering"]["coal_bag_owned"])
        self.assertEqual(purchased[0][STATE_KEY], paused[0][STATE_KEY])
        self._answer(self.cards[1], PHASES[1][1])
        active = self._checkpoint((2, 1))
        self.assertEqual(active[0][STATE_KEY]["phase"], "active")
        self.assertTrue(active[0]["dungeoneering"]["coal_bag_owned"])
        self._undo("Answer Card", purchased, (1, 1))
        self._undo("AnkiScape direct action", paused, (1, 0))
        self._undo("Answer Card", initial, (0, 0))
        self.assertEqual(self.collection.get_card(self.cards[0].id).reps, 0)

    def test_active_and_hatched_attempts_survive_collection_reopen(self):
        self._answer(self.cards[0], PHASES[1][1])
        active = self._checkpoint()
        self.assertEqual(active[0][STATE_KEY]["phase"], "active")
        self._reopen(active)
        self._reopen(active)
        self._answer(self.cards[1], PHASES[4][1])
        hatched = self._checkpoint()
        self.assertEqual(hatched[0][STATE_KEY]["phase"], "hatched")
        self.assertEqual(hatched[0]["quests"][QUEST_ID]["progress"], 2)
        self._reopen(hatched)


if __name__ == "__main__":
    unittest.main()
