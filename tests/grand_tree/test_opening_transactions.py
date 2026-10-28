"""Custody, ordering, admission and all-or-nothing opening execution."""

import copy
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data
from ankiscape.data.quest.grand_tree import (
    QUEST_ID, BARK_SAMPLE as BARK, TRANSLATION_BOOK as BOOK, HAZELMERES_SCROLL as SCROLL,
    PROOFS, EVENTS,
)
from ankiscape.logic_pure.quest import grand_tree as opening
from ankiscape.logic_pure.quest.eligibility import quest_eligibility_reasons_pure as eligibility
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, can_attempt_quest_review_pure, quest_current_stage_blockers_pure,
    quest_journal_rows_pure,
)

BOUNDARIES = ((0, 0), (1, 1), (2, 2), (2, 3), (3, 5))


def player_at(boundary=0):
    player = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    player['agility_level'] = 25
    progress, count = BOUNDARIES[boundary]
    player['quests'][QUEST_ID] = dict(started=True, completed=False, progress=progress)
    player['quest_action_proofs'] = sorted(PROOFS[:count])
    if boundary == 1:
        player['inventory'].update({BARK: 1, BOOK: 1})
    elif boundary >= 2:
        player['inventory'].update({BARK: 0, BOOK: 1, SCROLL: 1})
    return player


def blockers(player, quests=QUEST_DATA):
    return quest_current_stage_blockers_pure(player, QUEST_ID, quests)


def perform(player, quests=QUEST_DATA, extra=()):
    return opening.apply_grand_tree_review_pure(player, QUEST_ID, quests, (*blockers(player, quests), *extra), eligibility)


class OpeningTransactionsTest(unittest.TestCase):
    def test_four_exact_deltas_preserve_input_surplus_and_unrelated_state(self):
        player = player_at()
        player['inventory'].update({BARK: 4, BOOK: 3, SCROLL: 2, 'Coins': 93})
        player['quest_action_proofs'] = ['unrelated deed']
        inventories = ((5, 4, 2), (4, 4, 3), (4, 4, 3), (4, 4, 3))
        for boundary, counts in enumerate(inventories, 1):
            before = copy.deepcopy(player)
            data, ok = perform(player)
            self.assertTrue(ok)
            self.assertEqual(player, before)
            expected = copy.deepcopy(before)
            expected['inventory'].update(dict(zip((BARK, BOOK, SCROLL), counts)))
            progress, proof_count = BOUNDARIES[boundary]
            expected['quests'][QUEST_ID] = dict(started=True, progress=progress, completed=False)
            expected['quest_action_proofs'] = sorted(('unrelated deed', *PROOFS[:proof_count]))
            self.assertEqual(data, expected)
            player = data
        self.assertIsNone(perform(player))
        self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))

    def test_examination_requires_only_one_bark_without_book(self):
        player = player_at(1)
        player['inventory'].pop(BOOK)
        data, ok = perform(player)
        self.assertTrue(ok)
        self.assertEqual(data['inventory'][BARK], 0)
        self.assertEqual(data['inventory'][SCROLL], 1)
        self.assertNotIn(BOOK, data['inventory'])
        self.assertEqual(data['quests'][QUEST_ID]['progress'], 2)
        self.assertEqual(data['quest_action_proofs'], sorted(PROOFS[:2]))
        refused, ok = perform(data)
        self.assertFalse(ok)
        self.assertIs(refused, data)
        self.assertIn('Missing Translation book x1', [b['reason'] for b in blockers(data)])

    def test_missing_phase_materials_refuse_atomically(self):
        for boundary, name in ((1, BARK), (2, BOOK), (2, SCROLL)):
            with self.subTest(boundary=boundary, name=name):
                player = player_at(boundary)
                player['inventory'].pop(name, None)
                before = copy.deepcopy(player)
                data, ok = perform(player)
                self.assertFalse(ok)
                self.assertIs(data, player)
                self.assertEqual(player, before)
                self.assertIn(f'Missing {name} x1', [b['reason'] for b in blockers(player)])
                self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))

    def test_report_warning_has_no_inventory_gate_and_records_in_order(self):
        player = player_at(3)
        player['inventory'] = {'Coins': 13}
        observed = []
        recorder = opening.record_runtime_quest_action_proofs_pure

        def observe(data, *event):
            observed.append((event, tuple(data['quest_action_proofs'])))
            return recorder(data, *event)

        with patch.object(opening, 'record_runtime_quest_action_proofs_pure', side_effect=observe):
            data, ok = perform(player)
        self.assertTrue(ok)
        self.assertEqual(observed, [(EVENTS[3], tuple(sorted(PROOFS[:3]))), (EVENTS[4], tuple(sorted(PROOFS[:4])))])
        self.assertEqual(data['inventory'], player['inventory'])
        self.assertEqual(data['quest_action_proofs'], sorted(PROOFS))
        self.assertEqual(data['quests'][QUEST_ID], dict(started=True, progress=3, completed=False))

    def test_late_grant_and_warning_failures_discard_all_provisional_changes(self):
        player = player_at()
        before = copy.deepcopy(player)
        change = opening._change_item

        def refuse_book(inventory, name, delta):
            if name == BOOK:
                self.assertEqual(inventory[BARK], 1)
                return False
            return change(inventory, name, delta)

        with patch.object(opening, '_change_item', side_effect=refuse_book):
            data, ok = perform(player)
        self.assertFalse(ok)
        self.assertIs(data, player)
        self.assertEqual(player, before)
        self._assert_warning_refusal()

    def _assert_warning_refusal(self):
        player = player_at(3)
        before = copy.deepcopy(player)
        recorder = opening.record_runtime_quest_action_proofs_pure

        def refuse_warning(data, *event):
            if event == EVENTS[4]:
                self.assertIn(PROOFS[3], data['quest_action_proofs'])
                return False
            return recorder(data, *event)

        with patch.object(opening, 'record_runtime_quest_action_proofs_pure', side_effect=refuse_warning):
            data, ok = perform(player)
        self.assertFalse(ok)
        self.assertIs(data, player)
        self.assertEqual(player, before)

    def test_recorder_must_actually_record_expected_new_proof(self):
        for boundary in range(4):
            player = player_at(boundary)
            before = copy.deepcopy(player)
            with patch.object(opening, 'record_runtime_quest_action_proofs_pure', return_value=True):
                data, ok = perform(player)
            self.assertFalse(ok)
            self.assertIs(data, player)
            self.assertEqual(player, before)

    def test_invalid_touched_quantities_refuse_unchanged(self):
        for boundary, names in ((0, (BARK, BOOK)), (1, (BARK, SCROLL)), (2, (BOOK, SCROLL))):
            self._assert_invalid_quantities(boundary, names)

    def _assert_invalid_quantities(self, boundary, names):
        for name in names:
            for value in (-1, True, False, 1.0, '1', None):
                with self.subTest(boundary=boundary, name=name, value=value):
                    player = player_at(boundary)
                    player['inventory'][name] = value
                    before = copy.deepcopy(player)
                    data, ok = perform(player)
                    self.assertFalse(ok)
                    self.assertIs(data, player)
                    self.assertEqual(player, before)
                    self.assertTrue(any(b['kind'] == 'opening_inventory' for b in blockers(player)))

    def test_wrong_order_progress_and_proof_gaps_are_never_repaired(self):
        cases = ((0, 1), (1, 2), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5))
        for progress, count in cases:
            self._assert_inconsistent(progress, PROOFS[:count])
        for proofs in ((PROOFS[1],), (PROOFS[0], PROOFS[2]), (PROOFS[0], PROOFS[1], PROOFS[4])):
            self._assert_inconsistent(2, proofs)

    def _assert_inconsistent(self, progress, proofs):
        player = player_at()
        player['quests'][QUEST_ID]['progress'] = progress
        player['quest_action_proofs'] = list(proofs)
        before = copy.deepcopy(player)
        self.assertEqual(opening.grand_tree_phase_pure(player), 'inconsistent')
        self.assertIn('The Grand Tree opening has inconsistent progress.', [b['reason'] for b in blockers(player)])
        data, ok, completed = apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)
        self.assertEqual((ok, completed), (False, False))
        self.assertIs(data, player)
        self.assertEqual(player, before)

    def test_any_unrelated_blocker_still_blocks_readiness(self):
        for boundary in range(4):
            player = player_at(boundary)
            for kind in ('required_action', 'missing_item', 'missing_skill', 'missing_tool', 'quest_choice', 'unmet_route', 'combat'):
                extra = dict(kind=kind, action_id='unrelated deed', stage=1, reason='blocked')
                data, ok = perform(player, extra=(extra,))
                self.assertFalse(ok)
                self.assertIs(data, player)

    def test_eligibility_rechecked_including_late_loss(self):
        player = player_at(2)
        player['agility_level'] = 24
        self.assertIn('Requires Agility 25', [b['reason'] for b in blockers(player)])
        self.assertFalse(perform(player)[1])
        player['agility_level'] = 25
        before = copy.deepcopy(player)
        with patch.object(opening, 'grand_tree_review_ready_pure', return_value=True):
            result = opening.apply_grand_tree_review_pure(player, QUEST_ID, QUEST_DATA, (), lambda *_: ('Agility 25',))
        self.assertEqual(result, (player, False))
        self.assertEqual(player, before)

    def test_possession_and_retired_objectives_do_not_supply_deeds(self):
        player = player_at()
        player['inventory'].update({BARK: 3, BOOK: 4, SCROLL: 5})
        player['quest_action_proofs'] = ['Complete The Grand Tree stage 1 objective', 'Complete The Grand Tree stage 2 objective']
        before = copy.deepcopy(player)
        for _ in range(3):
            quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
            can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA)
        self.assertEqual(player, before)
        data, ok = perform(player)
        self.assertTrue(ok)
        self.assertEqual(data['inventory'][BARK], 4)
        self.assertEqual(data['inventory'][BOOK], 5)
        self.assertEqual(set(data['quest_action_proofs']) & set(PROOFS), {PROOFS[0]})

    def test_completed_grants_never_repeat_after_output_loss(self):
        for boundary, removed in ((1, (BARK, BOOK)), (2, (BOOK, SCROLL))):
            player = player_at(boundary)
            for name in removed:
                player['inventory'].pop(name, None)
            before = copy.deepcopy(player)
            self.assertFalse(perform(player)[1])
            self.assertEqual(player, before)
        for boundary in (3, 4):
            player = player_at(boundary)
            player['inventory'] = {}
            result = perform(player)
            self.assertTrue(result is None or result[0]['inventory'] == {})

    def test_outside_opening_and_both_orchestrator_return_arities(self):
        for state in (dict(started=False, progress=0, completed=False), dict(started=True, progress=3, completed=False),
                      dict(started=True, progress=7, completed=True)):
            player = player_at()
            player['quests'][QUEST_ID] = state
            self.assertIsNone(perform(player))
        player = player_at()
        self.assertIsNone(opening.apply_grand_tree_review_pure(player, 'rune_mysteries', QUEST_DATA, (), eligibility))
        self.assertEqual(len(apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA)), 3)
        self.assertEqual(len(apply_quest_progress_pure(player, QUEST_ID, QUEST_DATA, include_clue_refusal=True)), 4)
