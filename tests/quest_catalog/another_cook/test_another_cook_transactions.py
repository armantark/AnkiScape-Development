"""Atomic commission and performed preparation, bounded to the unfinished opening."""

import copy
import json
import unittest
from unittest.mock import patch

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXP_TABLE, ITEM_DEFINITIONS, ORE_DATA, QUEST_DATA
from ankiscape.core.storage_pure import default_player_data, migrate_loaded_data
from ankiscape.data.quest.another_cook import QUEST_ID, STATIC_JOURNAL, COMMISSION_JOURNAL, PREPARED_LINE
from ankiscape.data.quest_action_proof_data import ANOTHER_COOK_COMMISSION_PROOF as COMMISSION, ANOTHER_COOK_DIRTY_BLAST_PROOF as PREPARATION
from ankiscape.logic_pure.logic_pure_quest import (
    apply_quest_progress_pure, start_quest_pure, can_attempt_quest_review_pure,
    quest_current_stage_blockers_pure, quest_journal_rows_pure,
)
from ankiscape.logic_pure.quest import another_cook as opening


def player(commissioned=False, inventory=None):
    data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    data = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
    data.update(cooking_level=10, cooking_exp=EXP_TABLE[9], current_quest=QUEST_ID)
    data['quests']['cooks_assistant'] = dict(started=True, completed=True, progress=4)
    data['inventory'].update(dict(inventory or {}, Coins=0))
    if commissioned:
        data['quest_action_proofs'] = [COMMISSION]
        data['quests'][QUEST_ID] = dict(started=True, completed=False, progress=1)
        data['inventory']['Coins'] = 100
    return data


def advance(data, **kwargs):
    return apply_quest_progress_pure(data, QUEST_ID, QUEST_DATA, **kwargs)


def blockers(data):
    return quest_current_stage_blockers_pure(data, QUEST_ID, QUEST_DATA)


def journal(data):
    return quest_journal_rows_pure(data, QUEST_ID, QUEST_DATA)


def reload_player(data):
    return migrate_loaded_data(json.loads(json.dumps(data)), ORE_DATA, ITEM_DEFINITIONS)


def transaction_snapshot(data):
    return ({key: copy.deepcopy(data.get(key)) for key in (
        'inventory', 'quests', 'quest_action_proofs', 'cooking_exp', 'cooking_level',
        'quest_points', 'pending_skill_exp_rewards', 'claims',
    )}, journal(data))


class AnotherCookTransactionsTest(unittest.TestCase):
    def test_start_and_material_rich_first_review_only_commission(self):
        for inventory in ({}, {'Ashes': 3, 'Fruit blast': 2, 'Dirty blast': 1}):
            original = player(inventory=inventory)
            before = copy.deepcopy(original)
            started, ok = start_quest_pure(original, QUEST_ID, QUEST_DATA)
            self.assertTrue(ok)
            self.assertEqual(original, before)
            self.assertEqual(started['inventory'], before['inventory'])
            self.assertEqual(started['quest_action_proofs'], [])
            self.assertEqual(journal(started)[0]['lines'], STATIC_JOURNAL)
            self.assertTrue(can_attempt_quest_review_pure(started, QUEST_ID, QUEST_DATA))
            result, ok, completed = advance(started)
            self.assertTrue(ok)
            self.assertFalse(completed)
            self.assertEqual(result['inventory'], dict(before['inventory'], Coins=100))
            self.assertEqual(result['quest_action_proofs'], [COMMISSION])
            self.assertEqual(result['cooking_exp'], before['cooking_exp'])
            self.assertEqual(result['quests'][QUEST_ID], dict(started=True, completed=False, progress=1))
            self.assertEqual(journal(result)[0]['lines'], COMMISSION_JOURNAL)
            self.assertFalse(journal(result)[0]['completed'])

    def test_repeat_start_load_and_missing_input_retries_never_repay(self):
        data, ok, _ = advance(player())
        self.assertTrue(ok)
        for _ in range(3):
            before = transaction_snapshot(data)
            data, ok = start_quest_pure(reload_player(data), QUEST_ID, QUEST_DATA)
            self.assertTrue(ok)
            data, ok, _ = advance(data)
            self.assertFalse(ok)
            self.assertEqual(transaction_snapshot(data), before)

    def test_level_and_prerequisite_refuse_even_started(self):
        for commissioned in (False, True):
            for gate in ('level', 'prerequisite'):
                data = player(commissioned, {'Ashes': 1, 'Fruit blast': 1})
                if gate == 'level':
                    data['cooking_level'] = 9
                else:
                    data['quests']['cooks_assistant']['completed'] = False
                before = copy.deepcopy(data)
                result, ok, _ = advance(data)
                self.assertFalse(ok)
                self.assertEqual(result, before)
                self.assertEqual(data, before)

    def test_each_variant_exact_deltas_surplus_tools_other_ingredients_and_tuple_shapes(self):
        for cocktail in ('Fruit blast', 'Fruit blast (9514)'):
            for include in (False, True):
                with self.subTest(cocktail=cocktail, include=include):
                    self._assert_preparation(cocktail, include)

    def _assert_preparation(self, cocktail, include):
        inventory = {'Ashes': 3, cocktail: 2, "Premade fr' blast": 4, 'Knife': 1,
                     'Cocktail shaker': 1, 'Cocktail glass': 1, 'Eye of newt': 1,
                     "Greenman's ale": 1, 'Rotten tomato': 1, 'Dirty blast': 2}
        data = player(True, inventory)
        before = copy.deepcopy(data)
        result = advance(data, include_clue_refusal=include)
        self.assertEqual(len(result), 4 if include else 3)
        prepared, ok, completed = result[:3]
        self.assertTrue(ok)
        self.assertFalse(completed)
        expected = dict(data['inventory'])
        expected['Ashes'] -= 1
        expected[cocktail] -= 1
        expected['Dirty blast'] += 1
        self.assertEqual(prepared['inventory'], expected)
        self.assertEqual(prepared['cooking_exp'], data['cooking_exp'] + 5.0)
        self.assertEqual(set(prepared['quest_action_proofs']), {COMMISSION, PREPARATION})
        self.assertEqual(prepared['quests'][QUEST_ID]['progress'], 2)
        self.assertEqual(journal(prepared)[0]['lines'], COMMISSION_JOURNAL[:2] + (PREPARED_LINE,))
        self.assertTrue(journal(prepared)[0]['completed'])
        self.assertEqual(data, before)
        self.assertEqual(prepared['quest_points'], before['quest_points'])
        self.assertEqual(prepared['pending_skill_exp_rewards'], before['pending_skill_exp_rewards'])
        self.assertEqual(prepared['inventory'].get('An invitation to the feast', 0), 0)

    def test_normal_first_and_consumed_inputs_no_longer_block_stage(self):
        data = player(True, {'Ashes': 1, 'Fruit blast': 1, 'Fruit blast (9514)': 2})
        prepared, status = opening.apply_another_cook_review_pure(data, QUEST_ID, blockers(data))
        self.assertEqual(status, 'prepared')
        self.assertEqual(prepared['inventory']['Fruit blast'], 0)
        self.assertEqual(prepared['inventory']['Fruit blast (9514)'], 2)
        self.assertEqual(blockers(prepared), ())
        prepared, ok, _ = advance(prepared)
        self.assertTrue(ok)
        self.assertEqual(prepared['quests'][QUEST_ID]['progress'], 2)
        unchanged, ok, _ = advance(prepared)
        self.assertFalse(ok)
        self.assertEqual(unchanged, prepared)

    def test_missing_invalid_quantities_and_wrong_keys_do_not_prove_preparation(self):
        inventories = [{'Ashes': 1}, {'Fruit blast': 1}, {'Dirty blast': 1},
                       {'Ashes': 1, "Premade fr' blast": 1}, {'Ashes': 1, 'Fruit Blast': 1},
                       {'Ashes': 1, 'Fruit blast (unknown)': 1},
                       {'Ashes': 1, 'Fruit blast': True, 'Fruit blast (9514)': 1}]
        for value in (0, -1, True, False, 1.0, '1', None):
            inventories.extend(({'Ashes': value, 'Fruit blast': 1}, {'Ashes': 1, 'Fruit blast': value}))
        for inventory in inventories:
            with self.subTest(inventory=inventory):
                data = player(True, inventory)
                before = copy.deepcopy(data)
                result, ok, _ = advance(data)
                self.assertFalse(ok)
                self.assertEqual(result, before)
                self.assertEqual(data, before)

    def test_no_unrelated_blocker_is_waived_or_tentative_changes_published(self):
        data = player(True, {'Ashes': 1, 'Fruit blast': 1})
        unrelated = (*blockers(data), dict(kind='required_action', action_id='unrelated'))
        self.assertFalse(opening.another_cook_review_ready_pure(data, QUEST_ID, unrelated))
        with patch('ankiscape.logic_pure.logic_pure_quest.quest_current_stage_blockers_pure',
                   side_effect=[blockers(data), (dict(kind='missing_tool', reason='Needs unrelated tool'),)]):
            result, ok, _ = advance(data)
        self.assertFalse(ok)
        self.assertIs(result, data)
        self.assertEqual(data['inventory']['Ashes'], 1)

    def test_failure_after_writes_keeps_caller_unchanged(self):
        for commissioned in (False, True):
            data = player(commissioned, {'Ashes': 1, 'Fruit blast (9514)': 1})
            before = copy.deepcopy(data)
            with patch.object(opening, 'record_runtime_quest_action_proofs_pure', side_effect=RuntimeError('injected before publication')):
                with self.assertRaisesRegex(RuntimeError, 'before publication'):
                    advance(data)
            self.assertEqual(data, before)

    def test_full_carried_subset_does_not_gate_canonical_transaction(self):
        data = player(True, {'Ashes': 1, 'Fruit blast': 1, 'Logs': 28})
        data['carried_inventory'] = {'quest:' + QUEST_ID: {'Logs': 28}}
        prepared, ok, _ = advance(data)
        self.assertTrue(ok)
        self.assertEqual(prepared['carried_inventory'], data['carried_inventory'])
        self.assertEqual(prepared['inventory']['Dirty blast'], 1)

    def test_legacy_states_no_receipts_no_replay_no_invented_journal_credit(self):
        for progress, completed in ((2, False), (3, False), (4, True)):
            data = player(inventory={'Dirty blast': 2, 'Ashes': 3, 'Fruit blast': 4})
            data['quests'][QUEST_ID] = dict(started=True, completed=completed, progress=progress)
            before = transaction_snapshot(data)
            self.assertEqual(journal(data)[0]['lines'], ('These opening deeds have not been recorded.',))
            self.assertFalse(journal(data)[0]['completed'])
            self.assertEqual(transaction_snapshot(reload_player(data)), before)
            result, ok, _ = advance(data)
            self.assertFalse(ok)
            self.assertEqual(transaction_snapshot(result), before)
        for progress in (0, 1):
            data = player()
            data['quests'][QUEST_ID] = dict(started=True, completed=False, progress=progress)
            result, ok, _ = advance(data)
            self.assertTrue(ok)
            self.assertEqual(result['inventory']['Coins'], 100)
