"""The chapel opening runs atomically through ordinary quest review owners."""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.elemental_workshop_iii import (
    QUEST_ID, RAGGED_BOOK, ACQUIRE_PROOF, READ_PROOF, ACQUIRE_EVENT, READ_EVENT,
    ELIGIBILITY_SOURCE,
)
from ankiscape.logic_pure import logic_pure_quest as quests
from ankiscape.logic_pure.quest import elemental_workshop as opening
from ankiscape.logic_pure.quest_action_proofs import record_runtime_quest_action_proofs_pure
from ankiscape.runtime.runtime_actions_quest import handle_quest_answer
from tests.test_runtime_actions import _context
from . import OLD_PROOF, expected_opening, player


def progress(data, **kwargs):
    return quests.apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA, **kwargs)


def blockers(data):
    return quests.quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA)


class OpeningReviewTest(unittest.TestCase):
    def assert_refused(self, data):
        before = copy.deepcopy(data)
        for include in (False, True):
            result = progress(data, include_clue_refusal=include)
            self.assertEqual(result, (before, False, False, *(("",) if include else ())))
            self.assertIs(result[0], data)
            self.assertEqual(data, before)
        self.assertFalse(quests.can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
        calls = {"xp": [], "saves": 0, "errors": []}
        self.assertFalse(handle_quest_answer(_context(data, calls)))
        self.assertEqual(calls["saves"], 0)
        self.assertEqual(data, before)
        return calls

    def test_fresh_and_owned_copy_exact_deltas_and_both_return_forms(self):
        for quantity in (None, 0, 1, 4):
            for include in (False, True):
                with self.subTest(quantity=quantity, include=include):
                    data = player()
                    if quantity is None:
                        data["inventory"].pop(RAGGED_BOOK, None)
                    else:
                        data["inventory"][RAGGED_BOOK] = quantity
                    before = copy.deepcopy(data)
                    result = progress(data, include_clue_refusal=include)
                    self.assertEqual(result[1:], (True, False, *(("",) if include else ())))
                    self.assertEqual(result[0], expected_opening(before, acquired=not quantity))
                    self.assertEqual(data, before)

    def test_ordinary_handler_records_success_saves_and_preserves_unrelated_state(self):
        data = player()
        before = copy.deepcopy(data)
        calls = {"xp": [], "saves": 0, "errors": []}
        with patch("ankiscape.runtime.runtime_actions_quest._record_action") as record:
            self.assertTrue(handle_quest_answer(_context(data, calls)))
        self.assertEqual(data, expected_opening(before))
        record.assert_called_once()
        self.assertEqual(record.call_args.args[1:], ("quest", QUEST_ID, True))
        self.assertEqual(calls["saves"], 1)
        self.assertEqual(calls["xp"], [])
        self.assertEqual(calls["errors"], [])

    def test_acquisition_event_precedes_validated_read_on_copies(self):
        data = player()
        seen = []

        def record(copied, event_type, event_id):
            self.assertIsNot(copied, data)
            self.assertEqual(copied["inventory"][RAGGED_BOOK], 1)
            seen.append((event_type, event_id))
            return record_runtime_quest_action_proofs_pure(copied, event_type, event_id)

        with patch.object(opening, "record_runtime_quest_action_proofs_pure", side_effect=record):
            result = progress(data)
        self.assertTrue(result[1])
        self.assertEqual(seen, [ACQUIRE_EVENT, READ_EVENT])
        owned = player()
        owned["inventory"][RAGGED_BOOK] = 3
        with patch.object(opening, "record_runtime_quest_action_proofs_pure",
                          wraps=record_runtime_quest_action_proofs_pure) as record_owned:
            self.assertTrue(progress(owned)[1])
        self.assertEqual([c.args[1:] for c in record_owned.call_args_list], [READ_EVENT])

    def test_each_prerequisite_rechecked_after_selection(self):
        for prerequisite in ("elemental_workshop_i", "elemental_workshop_ii"):
            for missing in ("incomplete", "absent"):
                with self.subTest(prerequisite=prerequisite, missing=missing):
                    data = player()
                    if missing == "absent":
                        del data["quests"][prerequisite]
                    else:
                        data["quests"][prerequisite]["completed"] = False
                    expected_reason = f"Requires {QUEST_DATA[prerequisite]['display_name']}"
                    eligibility = [b for b in blockers(data) if b["kind"] == "opening_requirement"]
                    self.assertEqual(eligibility, [dict(kind="opening_requirement", stage=1,
                                                       source=ELIGIBILITY_SOURCE, reason=expected_reason)])
                    calls = self.assert_refused(data)
                    self.assertIn(expected_reason, str(calls["errors"]))

    def test_each_skill_below_and_at_boundary(self):
        for skill_id, level, label in (("mining", 20, "Mining"), ("defense", 33, "Defence"),
                                       ("smithing", 33, "Smithing")):
            with self.subTest(skill=skill_id):
                data = player()
                data[f"{skill_id}_level"] = level - 1
                self.assertIn(f"Requires {label} {level}", tuple(b["reason"] for b in blockers(data)))
                self.assert_refused(data)
                data[f"{skill_id}_level"] = level
                self.assertTrue(quests.can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
                self.assertTrue(progress(data)[1])

    def test_effective_boosts_allow_start_and_review_without_changing_base_levels(self):
        data = player(started=False, stage=0)
        data.update(mining_level=19, smithing_level=32, defense_level=32)
        data["skilling_current_levels"] = {"mining": 20, "smithing": 33}
        data["combat_current_levels"] = {"defense": 33}
        before = copy.deepcopy(data)
        self.assertEqual(quests.quest_locked_reasons_pure(data, QUEST_ID, QUEST_DATA), ())
        started, ok = quests.start_quest_pure(data, QUEST_ID, QUEST_DATA)
        self.assertTrue(ok)
        result = progress(started)
        self.assertTrue(result[1])
        for key in ("mining_level", "smithing_level", "defense_level",
                    "skilling_current_levels", "combat_current_levels"):
            self.assertEqual(result[0][key], before[key])
        self.assertEqual(data, before)
        other = dict(QUEST_DATA, other=dict(QUEST_DATA[QUEST_ID]))
        self.assertEqual(quests.quest_locked_reasons_pure(data, "other", other),
                         ("Defence 33", "Mining 20", "Smithing 33"))

    def test_each_boost_lost_between_selection_and_review_refuses(self):
        for skill_id in ("mining", "smithing", "defense"):
            with self.subTest(skill=skill_id):
                data = player(started=False, stage=0)
                level = data[f"{skill_id}_level"]
                data[f"{skill_id}_level"] -= 1
                boost_key = "combat_current_levels" if skill_id == "defense" else "skilling_current_levels"
                data[boost_key] = {skill_id: level}
                selected, ok = quests.start_quest_pure(data, QUEST_ID, QUEST_DATA)
                self.assertTrue(ok)
                selected[boost_key] = {}
                self.assert_refused(selected)

    def test_direct_read_refuses_wrong_items_and_missing_exact_book_without_mutation(self):
        for owned in (False, True):
            for item_name in ("Slashed book", "Beaten book", "Coal", RAGGED_BOOK):
                if owned and item_name == RAGGED_BOOK:
                    continue
                with self.subTest(owned=owned, item=item_name):
                    data = player()
                    if owned:
                        data["inventory"][RAGGED_BOOK] = 2
                    before = copy.deepcopy(data)
                    same, ok = opening.read_ragged_book_pure(data, item_name)
                    self.assertFalse(ok)
                    self.assertIs(same, data)
                    self.assertEqual(data, before)

    def test_direct_exact_book_read_emits_only_read_and_preserves_quantity(self):
        data = player()
        data["inventory"][RAGGED_BOOK] = 3
        before = copy.deepcopy(data)
        result, ok = opening.read_ragged_book_pure(data, RAGGED_BOOK)
        self.assertTrue(ok)
        expected = copy.deepcopy(before)
        expected["quest_action_proofs"] = sorted([*before["quest_action_proofs"], READ_PROOF])
        self.assertEqual(result, expected)
        self.assertEqual(data, before)

    def test_read_or_search_failure_discards_even_provisional_start_and_acquisition(self):
        for started in (False, True):
            for operation in ("search_chapel_bookcase_pure", "read_ragged_book_pure"):
                with self.subTest(started=started, operation=operation):
                    data = player(stage=0, started=started)
                    before = copy.deepcopy(data)
                    observed = []

                    def fail(copied, *args):
                        observed.append(copy.deepcopy(copied))
                        copied["inventory"]["Coal"] = 999
                        return copied, False

                    with patch.object(opening, operation, side_effect=fail):
                        self.assertEqual(progress(data, include_clue_refusal=True), (before, False, False, ""))
                    self.assertEqual(data, before)
                    if operation == "read_ragged_book_pure":
                        self.assertEqual(observed[0]["inventory"][RAGGED_BOOK], 1)
                        self.assertIn(ACQUIRE_PROOF, observed[0]["quest_action_proofs"])
                        self.assertNotIn(READ_PROOF, observed[0]["quest_action_proofs"])

    def test_eligibility_failure_after_provisional_start_publishes_nothing(self):
        data = player(stage=0, started=False)
        before = copy.deepcopy(data)
        with patch.object(quests, "quest_eligibility_reasons_pure", return_value=("Mining 20",)):
            result = progress(data)
        self.assertEqual(result, (before, False, False))
        self.assertIs(result[0], data)
        self.assertEqual(data, before)

    def test_full_carried_pack_does_not_prevent_unified_quest_item_custody(self):
        data = player()
        data["inventory"]["Logs"] = 28
        data["carried_inventory"] = {"tree": {"Logs": 28}}
        data["carried_churn"] = {"tree": 28}
        before = copy.deepcopy(data)
        result, ok, completed = progress(data)
        self.assertTrue(ok)
        self.assertFalse(completed)
        self.assertEqual(result, expected_opening(before))

    def test_readiness_starting_journal_and_possession_emit_nothing(self):
        for book in (None, RAGGED_BOOK, "Slashed book", "Beaten book"):
            data = player(started=False, stage=0)
            if book:
                data["inventory"][book] = 1
            before = copy.deepcopy(data)
            with patch.object(opening, "record_runtime_quest_action_proofs_pure") as record:
                for _ in range(2):
                    self.assertTrue(quests.can_attempt_quest_review_pure(data, QUEST_ID, QUEST_DATA))
                    quests.quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)
                    started, ok = quests.start_quest_pure(data, QUEST_ID, QUEST_DATA)
                    self.assertTrue(ok)
                    self.assertTrue(quests.can_attempt_quest_review_pure(started, QUEST_ID, QUEST_DATA))
                    self.assertFalse(quests.can_progress_quest_pure(started, QUEST_ID, QUEST_DATA))
                    quests.quest_journal_rows_pure(started, QUEST_ID, QUEST_DATA)
                record.assert_not_called()
            self.assertEqual(data, before)
            self.assertEqual(started["quest_action_proofs"], before["quest_action_proofs"])

    def test_later_review_completed_or_other_quest_never_replays_opening(self):
        fresh = progress(player())[0]
        for data in (fresh, player(6), player(8, completed=True)):
            before = copy.deepcopy(data)
            with patch.object(opening, "search_chapel_bookcase_pure") as search:
                self.assertFalse(progress(data)[1])
                search.assert_not_called()
            self.assertEqual(data, before)
        other = player()
        self.assertEqual(opening.apply_opening_review_pure(other, "elemental_workshop_ii", QUEST_DATA, (), quests.quest_eligibility_reasons_pure),
                         (other, True))

    def test_unrelated_blockers_are_retained_and_cannot_be_serviced(self):
        data = player()
        quest_data = copy.deepcopy(QUEST_DATA)
        quest_data[QUEST_ID]["stage_requirements"][0]["required_inventory"] = {"Soft clay": 1}
        before = copy.deepcopy(data)
        ordinary = quests.quest_current_stage_blockers_pure(data, QUEST_ID, quest_data)
        self.assertIn("missing_item", {b["kind"] for b in ordinary})
        self.assertFalse(quests.can_attempt_quest_review_pure(data, QUEST_ID, quest_data))
        self.assertEqual(quests.apply_quest_progress_pure(data, QUEST_ID, quest_data), (before, False, False))
        self.assertEqual(data, before)

    def test_old_automatic_proof_does_not_satisfy_read_requirement(self):
        data = player()
        data["quest_action_proofs"].append(OLD_PROOF)
        self.assertEqual({b.get("action_id") for b in blockers(data)}, {READ_PROOF})
        result = progress(data)[0]
        self.assertIn(OLD_PROOF, result["quest_action_proofs"])
        self.assertIn(READ_PROOF, result["quest_action_proofs"])
