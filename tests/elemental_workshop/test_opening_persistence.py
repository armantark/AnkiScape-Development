"""Real answer/Undo plus JSON migration never infer an unperformed book deed."""

import copy
import json
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.data.quest.elemental_workshop_iii import QUEST_ID, RAGGED_BOOK, READ_PROOF, ACQUIRE_PROOF
from ankiscape.logic_pure.logic_pure_quest import apply_quest_progress_pure, quest_journal_rows_pure
from ankiscape.logic_pure.quest import elemental_workshop as opening
from tests.test_combat_quest_gate import _answer_review
from tests.test_integration_smoke import _install_runtime_fakes, _load_addon_as_package
from . import OLD_PROOF, player

PRESERVED_KEYS = (
    "inventory", "quests", "quest_action_proofs", "quest_route_states",
    "quest_combat_encounters", "quest_combat_encounter_counts", "quest_combat_active_encounters",
    "quest_points", "smithing_exp", "pending_skill_exp_rewards",
)


def reload(data):
    return migrate_loaded_data(json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS)


def journal(data):
    return quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)


class OpeningPersistenceTest(unittest.TestCase):
    def test_real_quest_answer_undo_restores_complete_snapshot_and_replays_once(self):
        original_modules = dict(sys.modules)
        try:
            _install_runtime_fakes()
            addon = _load_addon_as_package("ankiscape_chapel_opening_e2e")
            saved, errors = [], []
            addon.show_error_message = lambda title, message: errors.append((title, message))
            addon.save_player_data = lambda: saved.append(copy.deepcopy(addon._state.player_data))
            addon.check_achievements = lambda _data: None
            addon._refresh_skill_availability = lambda: None
            addon._show_activity_gain = lambda _text: None
            addon._show_exp = lambda _amount: None
            addon.level_up_check = lambda *_args: None
            addon.update_review_hud = lambda *_args: None
            for quantity in (0, 3):
                with self.subTest(quantity=quantity):
                    data = player()
                    data["inventory"][RAGGED_BOOK] = quantity
                    addon._state.player_data = data
                    addon._state.current_skill = "Quests"
                    addon._state.review_undo_stack.clear()
                    before = copy.deepcopy(data)
                    _answer_review(addon)
                    earned = copy.deepcopy(addon._state.player_data)
                    self.assertEqual(earned["quests"][QUEST_ID]["progress"], 2, errors)
                    self.assertEqual(earned["inventory"][RAGGED_BOOK], quantity or 1)
                    self.assertIn(READ_PROOF, earned["quest_action_proofs"])
                    self.assertEqual(ACQUIRE_PROOF in earned["quest_action_proofs"], quantity == 0)
                    self.assertEqual(saved[-1], earned)
                    addon._on_state_did_undo(SimpleNamespace(operation="Answer Card"))
                    self.assertEqual(addon._state.player_data, before)
                    addon._state.current_skill = "Quests"
                    _answer_review(addon)
                    self.assertEqual(addon._state.player_data, earned)
                    later = copy.deepcopy(addon._state.player_data)
                    _answer_review(addon)
                    for key in PRESERVED_KEYS:
                        self.assertEqual(addon._state.player_data[key], later[key], key)
        finally:
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_fresh_owned_and_legacy_save_load_never_backfill_new_deeds(self):
        for case in ("fresh", "owned", "old", "later", "completed"):
            with self.subTest(case=case):
                data = player()
                if case == "owned":
                    data["inventory"][RAGGED_BOOK] = 3
                if case == "old":
                    data["quest_action_proofs"] = sorted([*data["quest_action_proofs"], OLD_PROOF])
                if case in ("later", "completed"):
                    data["quests"][QUEST_ID].update(progress=6 if case == "later" else 8,
                                                     completed=case == "completed")
                before = copy.deepcopy(data)
                with patch.object(opening, "record_runtime_quest_action_proofs_pure") as record:
                    loaded = reload(data)
                    for _ in range(3):
                        journal(loaded)
                        loaded = reload(loaded)
                    record.assert_not_called()
                self.assertEqual(data, before)
                for key in PRESERVED_KEYS:
                    self.assertEqual(loaded[key], before[key], (case, key))
                self.assertNotIn(READ_PROOF, loaded["quest_action_proofs"])
                self.assertNotIn(ACQUIRE_PROOF, loaded["quest_action_proofs"])
                self.assertEqual(reload(loaded), loaded)

    def test_earned_fresh_or_owned_opening_survives_repeated_load_with_exact_later_state(self):
        for owned in (False, True):
            with self.subTest(owned=owned):
                data = player()
                if owned:
                    data["inventory"][RAGGED_BOOK] = 4
                earned, ok, completed = apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA)
                self.assertTrue(ok)
                self.assertFalse(completed)
                loaded = earned
                for _ in range(3):
                    loaded = reload(loaded)
                    for key in PRESERVED_KEYS:
                        self.assertEqual(loaded[key], earned[key], key)
                    self.assertTrue(journal(loaded)[0]["completed"])
                    self.assertFalse(journal(loaded)[1]["completed"])
                self.assertEqual(reload(loaded), loaded)

    def test_journal_records_only_performed_opening_and_pending_preparation(self):
        for owned in (False, True):
            data = player()
            if owned:
                data["inventory"][RAGGED_BOOK] = 2
            earned = apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA)[0]
            before = copy.deepcopy(earned)
            rows = journal(earned)
            line = "I read my Ragged book." if owned else (
                "I searched the chapel bookcase, obtained the Ragged book and read it."
            )
            self.assertEqual(rows[0], dict(stage=1, lines=(line,), completed=True, current=False))
            self.assertFalse(rows[1]["completed"])
            self.assertTrue(rows[1]["current"])
            self.assertEqual(rows, journal(earned))
            self.assertEqual(earned, before)

    def test_legacy_later_and_completed_journal_never_infers_a_deed(self):
        for stage, completed in ((2, False), (6, False), (8, True)):
            data = player(stage, completed=completed)
            data["inventory"][RAGGED_BOOK] = 1
            data["quest_action_proofs"].append(OLD_PROOF)
            before = copy.deepcopy(data)
            rows = journal(data)
            self.assertEqual(rows[0], dict(stage=1, completed=False, current=False,
                lines=("The chapel search and Ragged book reading have no recorded deed.",)))
            self.assertFalse(rows[1]["completed"])
            for row in rows[2:]:
                self.assertEqual(row["lines"], QUEST_DATA[QUEST_ID]["journal_stages"][row["stage"]])
                self.assertEqual(row["completed"], completed or row["stage"] < stage)
                self.assertEqual(row["current"], not completed and row["stage"] == stage)
            self.assertEqual(data, before)

    def test_read_proof_alone_is_the_journal_completion_authority(self):
        for proof in (None, OLD_PROOF, ACQUIRE_PROOF, READ_PROOF):
            data = player()
            if proof:
                data["quest_action_proofs"].append(proof)
            row = journal(data)[0]
            self.assertEqual(row["completed"], proof == READ_PROOF)
            if proof == READ_PROOF:
                self.assertEqual(row["lines"], ("I read my Ragged book.",))
            else:
                self.assertEqual(row["lines"], QUEST_DATA[QUEST_ID]["journal_stages"][1])
