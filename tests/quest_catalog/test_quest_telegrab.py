"""The shrine-key cast earns its quest proof through review, and Undo retracts it."""

from __future__ import annotations

import copy
import sys
import types
import unittest
from pathlib import Path

import pkg_alias  # noqa: F401
from ankiscape.core.constants import MAGIC_DATA, MAGIC_ITEM_IMAGES, QUEST_DATA
from ankiscape.core.constants_parts.skill_assets import MAGIC_SPELL_IMAGES
from ankiscape.logic_pure.logic_pure_quest import apply_quest_progress_pure, quest_current_stage_blockers_pure
from ankiscape.core.target_metadata import magic_target_rows
from tests.test_combat_quest_gate import _answer_review, _maxed_player_for_quest
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package


PROOF = "Cast Telegrab for the water channel puzzle"
TARGET = "telegrab_ancestral_key"
QUEST = "spirits_of_the_elid"


class TestQuestTelegrab(unittest.TestCase):
    def setUp(self):
        self._original_modules = dict(sys.modules)
        _install_runtime_fakes()
        self.addon = _load_addon_as_package("ankiscape_quest_telegrab_review")
        self.saved = []
        self.errors = []
        self.addon.check_achievements = lambda _data: None
        self.addon.save_player_data = lambda: self.saved.append(copy.deepcopy(self.addon._state.player_data))
        self.addon._refresh_skill_availability = lambda: None
        self.addon._show_activity_gain = lambda _text: None
        self.addon._show_exp = lambda _amount: None
        self.addon.level_up_check = lambda _skill, _data: None
        self.addon.update_review_hud = lambda _data, _skill: None
        self.addon.show_error_message = lambda title, message: self.errors.append((title, message))
        player = _maxed_player_for_quest(QUEST)
        player["quests"][QUEST] = {"started": True, "progress": 2, "completed": False}
        player["inventory"].update({"Air rune": 1, "Law rune": 1, "Thread": 1})
        player["current_magic"] = TARGET
        self.addon._state.player_data = player
        self.addon._state.current_skill = "Magic"
        self.addon._state.review_undo_stack.clear()

    def tearDown(self):
        sys.modules.clear()
        sys.modules.update(self._original_modules)

    def _blockers(self):
        return {row.get("action_id") for row in quest_current_stage_blockers_pure(self.addon._state.player_data, QUEST, QUEST_DATA)}

    def test_review_acquires_key_records_proof_and_undo_restores_cast(self):
        before = copy.deepcopy(self.addon._state.player_data)
        self.assertIn(PROOF, self._blockers())
        rows = magic_target_rows(before, MAGIC_DATA, MAGIC_ITEM_IMAGES, TARGET, {}, MAGIC_SPELL_IMAGES)
        row = next(row for row in rows if row.target_id == TARGET)
        self.assertTrue(row.enabled)
        self.assertTrue(Path(row.icon_path).is_file())

        _answer_review(self.addon)

        player = self.addon._state.player_data
        self.assertFalse(self.errors)
        self.assertEqual({name: player["inventory"].get(name, 0) for name in ("Air rune", "Law rune", "Thread", "Ancestral key")}, {"Air rune": 0, "Law rune": 0, "Thread": 1, "Ancestral key": 1})
        self.assertIn(PROOF, player["quest_action_proofs"])
        self.assertIn(PROOF, self.saved[-1]["quest_action_proofs"])
        self.assertNotIn(PROOF, self._blockers())
        self.assertEqual(len(self.addon._state.review_undo_stack), 1)

        advanced, ok, completed = apply_quest_progress_pure(player, QUEST, QUEST_DATA)
        self.assertTrue(ok, self._blockers())
        self.assertFalse(completed)
        self.assertEqual(advanced["quests"][QUEST]["progress"], 3)

        player["current_quest"] = QUEST
        self.addon._state.current_skill = "Quests"
        _answer_review(self.addon)
        self.assertEqual(self.addon._state.player_data["quests"][QUEST]["progress"], 3)

        self.addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)))
        self.assertEqual(self.addon._state.player_data["quests"][QUEST]["progress"], 2)
        self.assertIn(PROOF, self.addon._state.player_data["quest_action_proofs"])

        self.addon._on_state_did_undo(types.SimpleNamespace(operation="Answer Card", changes=types.SimpleNamespace(study_queues=True, card=True)))

        player = self.addon._state.player_data
        self.assertEqual(player["quests"][QUEST]["progress"], 2)
        self.assertEqual(player["inventory"], before["inventory"])
        self.assertEqual(player["magic_exp"], before["magic_exp"])
        self.assertNotIn(PROOF, player["quest_action_proofs"])
        self.assertIn(PROOF, self._blockers())

    def test_missing_rune_refuses_even_with_owned_key(self):
        for missing in ("Air rune", "Law rune"):
            with self.subTest(missing=missing):
                player = self.addon._state.player_data
                player["inventory"].update({"Air rune": 1, "Law rune": 1, "Ancestral key": 1})
                player["inventory"][missing] = 0
                before = copy.deepcopy(player["inventory"])
                self.addon._state.current_skill = "Magic"

                _answer_review(self.addon)

                self.assertEqual(self.addon._state.player_data["inventory"], before)
                self.assertNotIn(PROOF, self.addon._state.player_data["quest_action_proofs"])
                self.assertIn(PROOF, self._blockers())

    def test_wine_telegrab_cannot_earn_shrine_key_proof(self):
        self.addon._state.player_data["current_magic"] = "telegrab_wine_of_zamorak"

        _answer_review(self.addon)

        player = self.addon._state.player_data
        self.assertFalse(self.errors)
        self.assertEqual(player["inventory"]["Wine of zamorak"], 1)
        self.assertEqual(player["inventory"].get("Ancestral key", 0), 0)
        self.assertNotIn(PROOF, player["quest_action_proofs"])
        self.assertIn(PROOF, self._blockers())
