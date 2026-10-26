"""Persistence and the existing review/direct Undo owners retain exact custody."""

import copy
import json
import random
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tests.one_small_favour.test_opening_transactions import player, progress
from tests.one_small_favour.test_review_dispatch import RuntimeFixture
from tests.test_combat_quest_gate import _answer_review
from tests.test_storage_runtime import _load_storage_module
from tests.test_integration_smoke import _DummyCol
from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.data.quest.one_small_favour import QUEST_ID, BLUNT_HATCHET, OPENING_PROOFS
from ankiscape.logic_pure.quest.one_small_favour import apply_opening_review_pure, opening_hatchet_custody_pure
from ankiscape.logic.summoning_logic import familiar_storage_transfer_pure, dismiss_familiar_pure, reclaim_familiar_cargo_pure


def encoded(value):
    return json.loads(json.dumps(value))


def checkpoint(addon):
    return (copy.deepcopy(addon._state.player_data), addon._state.current_skill,
            encoded(addon.mw.col.get_config('ankiscape_player_data')), random.getstate())


class SaveOpeningTest(unittest.TestCase):
    def test_save_load_migrate_every_prefix_and_replacement_checkpoint(self):
        with patch.dict(sys.modules):
            collection = _DummyCol()
            storage = _load_storage_module(collection)
            data = player(started=False)
            for index in range(7):
                data, ok, _ = progress(data)
                self.assertTrue(ok)
                self._round_trip(storage, data)
                if index == 2:
                    data['inventory'][BLUNT_HATCHET] = 0
                    data, status = apply_opening_review_pure(data)
                    self.assertEqual(status, 'partial')
                    self.assertEqual(set(data['quest_action_proofs']), set(OPENING_PROOFS[:3]))
                    self._round_trip(storage, data)

    def _round_trip(self, storage, data):
        before = copy.deepcopy(data)
        storage.save_player_data(data, 'Quests')
        loaded, skill = storage.load_player_data()
        expected = migrate_loaded_data(copy.deepcopy(before), ORE_DATA, ITEM_DEFINITIONS)
        self.assertEqual(loaded, expected)
        self.assertEqual(skill, 'Quests')
        self.assertEqual(data, before)
        self.assertEqual(loaded['quests'], data['quests'])
        self.assertEqual(loaded['quest_action_proofs'], sorted(data['quest_action_proofs']))
        self.assertEqual(loaded['inventory'][BLUNT_HATCHET], data['inventory'][BLUNT_HATCHET])
        loaded['inventory'][BLUNT_HATCHET] += 10
        self.assertEqual(data, before)

    def test_recoverable_custody_survives_reload_and_still_prevents_replacement(self):
        with patch.dict(sys.modules):
            storage = _load_storage_module(_DummyCol())
            data = player(3)
            data['summoning_state']['active_follower'] = {
                'kind': 'familiar', 'entity_id': 'spiritterrorbird', 'storage': {},
                'remaining_ticks': 1000, 'max_ticks': 1000,
            }
            data, ok = familiar_storage_transfer_pure(data, BLUNT_HATCHET, 1, to_familiar=True)
            self.assertTrue(ok)
            self._assert_recoverable_reload(storage, data)
            data, ok, _ = dismiss_familiar_pure(data)
            self.assertTrue(ok)
            self._assert_recoverable_reload(storage, data)
            event = data['summoning_state']['cargo_events'][0]
            data, ok, _ = reclaim_familiar_cargo_pure(data, event['event_id'])
            self.assertTrue(ok)
            self._round_trip(storage, data)
            for key in ('combat_grave', 'death_office'):
                stored = player(3)
                stored['inventory'][BLUNT_HATCHET] = 0
                stored[key] = {'items': [BLUNT_HATCHET], 'loadout': {'weapon': BLUNT_HATCHET}}
                self._assert_recoverable_reload(storage, stored)

    def _assert_recoverable_reload(self, storage, data):
        storage.save_player_data(data, 'Quests')
        loaded, skill = storage.load_player_data()
        self.assertEqual(skill, 'Quests')
        self.assertEqual(opening_hatchet_custody_pure(loaded), (0, 1))
        before = copy.deepcopy(loaded)
        after, status = apply_opening_review_pure(loaded)
        self.assertIs(after, loaded)
        self.assertEqual(status, 'unchanged')
        self.assertEqual(loaded, before)

    def test_legacy_later_and_completed_saves_are_never_backfilled_or_rewound(self):
        sentinel = 'Complete One Small Favour stage 1 objective'
        for stage, completed in ((1, False), (2, False), (5, False), (8, True)):
            data = player()
            data['quests'][QUEST_ID].update(progress=stage, completed=completed)
            data['quest_action_proofs'] = [sentinel]
            before = copy.deepcopy(data)
            loaded = migrate_loaded_data(data, ORE_DATA, ITEM_DEFINITIONS)
            self.assertEqual(loaded['quests'][QUEST_ID], before['quests'][QUEST_ID])
            self.assertFalse(set(loaded['quest_action_proofs']) & set(OPENING_PROOFS))
            if stage > 1 or completed:
                result, status = apply_opening_review_pure(loaded)
                self.assertIs(result, loaded)
                self.assertEqual(status, 'unchanged')


class OpeningUndoTest(RuntimeFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.addCleanup(random.setstate, random.getstate())
        timer = patch('time.time', return_value=1_793_000_000.0)
        timer.start()
        self.addCleanup(timer.stop)
        # The dummy Collection uses the installed JSON representation just as Anki does.
        self.collection.set_config = lambda key, value: self.collection._store.__setitem__(key, encoded(value))
        self.addon.save_player_data()
        self.addon.load_player_data()
        self.addon.save_player_data()

    def _undo(self, operation, expected):
        self.addon._on_state_did_undo(SimpleNamespace(operation=operation))
        self.assertEqual(checkpoint(self.addon), expected)

    def _answer_undo_reanswer(self):
        addon = self.addon
        before = checkpoint(addon)
        _answer_review(addon)
        after = checkpoint(addon)
        snapshot = copy.deepcopy(addon._state.review_undo_stack[-1])
        self._undo('Answer Card', before)
        self.assertEqual(snapshot['values'].get('inventory', before[0]['inventory']), before[0]['inventory'])
        _answer_review(addon)
        self.assertEqual(checkpoint(addon), after)
        return before, after

    def test_undo_and_reanswer_entire_opening_with_actual_discard_and_replacement(self):
        addon = self.addon
        history = []
        for index in range(7):
            before, _ = self._answer_undo_reanswer()
            history.append(('Answer Card', before))
            if index == 2:
                owned = checkpoint(addon)
                self.assertTrue(addon.on_discard_item(BLUNT_HATCHET, 1))
                lost = checkpoint(addon)
                self.assertEqual(lost[0]['inventory'][BLUNT_HATCHET], 0)
                self._undo('AnkiScape direct action', owned)
                self.assertTrue(addon.on_discard_item(BLUNT_HATCHET, 1))
                self.assertEqual(checkpoint(addon), lost)
                history.append(('AnkiScape direct action', owned))
                before_replacement, replacement = self._answer_undo_reanswer()
                self.assertEqual(replacement[0]['quest_action_proofs'], before_replacement[0]['quest_action_proofs'])
                self.assertEqual(replacement[0]['inventory'][BLUNT_HATCHET], 1)
                history.append(('Answer Card', before_replacement))
        self.assertEqual(addon._state.player_data['quests'][QUEST_ID]['progress'], 2)
        for operation, before in reversed(history):
            self._undo(operation, before)
        self.assertEqual(addon._state.review_undo_stack, [])
        self.assertEqual(addon._state.direct_action_undo_stack, [])
