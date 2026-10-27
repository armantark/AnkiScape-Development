"""Additive valve sanitation and custody-preserving save/reopen."""

import copy
import json
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import ORE_DATA, ITEM_DEFINITIONS
from ankiscape.core.storage_pure import migrate_loaded_data
from ankiscape.data.quest.hazeel_opening import (
    VALVE_KEY, POISON, MARK, PROOFS, BRANCH_ROUTES, POISON_RECEIPT, MARK_RECEIPT,
)
from ankiscape.logic_pure.quest.hazeel import sanitize_hazeel_valve_states_pure
from tests.quest_catalog.hazeel_helpers import fresh_player, started_player, review, choose

QUEST_ID = 'hazeel_cult'


def reopen(player):
    return migrate_loaded_data(json.loads(json.dumps(player)), ORE_DATA, ITEM_DEFINITIONS)


class HazeelPersistenceTest(unittest.TestCase):
    def test_default_and_malformed_valve_state(self):
        self.assertEqual(fresh_player()[VALVE_KEY], {})
        for raw in (None, [], 'left', 2844, True):
            self.assertEqual(sanitize_hazeel_valve_states_pure(raw), {})
            player = fresh_player()
            player[VALVE_KEY] = raw
            self.assertEqual(reopen(player)[VALVE_KEY], {})
        raw = {'2844':'right', '2845':'left', '2846':None, '2847':True, '2848':'Right', '2859':'right', 2846:'left'}
        self.assertEqual(sanitize_hazeel_valve_states_pure(raw), {'2844':'right','2845':'left'})
        player = fresh_player()
        player[VALVE_KEY] = {'2844':'right', '2845':'left', '2846':{}, '2847':[], '2848':'left'}
        self.assertEqual(reopen(player)[VALVE_KEY], {'2844':'right','2845':'left','2848':'left'})

    def _assert_reopen_trace(self, branch):
        player = reopen(started_player())
        total = 8 if branch == 'carnillean' else 11
        for index in range(total):
            if index == 2:
                player = reopen(choose(player, branch))
            continuous = review(copy.deepcopy(player))
            player = reopen(review(player))
            for key in ('quests', 'inventory', 'equipment', 'quest_action_proofs', VALVE_KEY, 'quest_route_states'):
                self.assertEqual(player[key], continuous[key], (branch, index, key))
        self.assertEqual(player['quests'][QUEST_ID]['progress'], 2)
        if branch == 'hazeel':
            self.assertEqual(player['inventory'][POISON], 0)
            self.assertEqual(player['inventory'][MARK], 1)
            self.assertEqual(player['quest_action_proofs'].count(POISON_RECEIPT), 1)
            self.assertEqual(player['quest_action_proofs'].count(MARK_RECEIPT), 1)
        self.assertEqual(reopen(player), player)

    def test_save_reopen_each_action_and_endpoint(self):
        for branch in ('carnillean', 'hazeel'):
            with self.subTest(branch=branch):
                self._assert_reopen_trace(branch)

    def test_legacy_progress_items_and_proofs_are_preserved(self):
        # Explicit legacy fixtures: migration may not invent detailed new history.
        for progress, started, completed in ((0,False,False), (0,True,False), (1,True,False), (2,True,False), (3,True,False), (4,True,True)):
            for mark in (0, 4):
                player = reopen(fresh_player())
                player['quests'][QUEST_ID] = dict(started=started, completed=completed, progress=progress)
                player['quest_route_states'][QUEST_ID] = [BRANCH_ROUTES['hazeel']]
                player['inventory'].update({MARK:mark, POISON:3})
                player['quest_action_proofs'] = sorted(['Unrelated genuine proof', PROOFS['ceril_commission']])
                player[VALVE_KEY] = {'2844':'right'}
                before = copy.deepcopy(player)
                migrated = reopen(player)
                for key in ('quests', 'inventory', 'quest_route_states', 'quest_action_proofs', VALVE_KEY):
                    self.assertEqual(migrated[key], before[key])
                self.assertNotIn(MARK_RECEIPT, migrated['quest_action_proofs'])
                self.assertNotIn(POISON_RECEIPT, migrated['quest_action_proofs'])
                if started and progress <= 1:
                    migrated = review(migrated)
                    self.assertIn(PROOFS['clivet_briefing'], migrated['quest_action_proofs'])
                    self.assertNotIn(PROOFS['cult_acceptance'], migrated['quest_action_proofs'])
                    self.assertEqual(migrated['inventory'][MARK], mark)

    def test_alias_migration_preserves_mark_quantity(self):
        player = fresh_player()
        player['inventory'].update({"Hazeel's mark":3, MARK:4})
        player['equipment']['neck'] = "Hazeel's mark"
        migrated = reopen(player)
        self.assertEqual(migrated['inventory'][MARK], 7)
        self.assertNotIn("Hazeel's mark", migrated['inventory'])
        self.assertEqual(migrated['equipment']['neck'], MARK)
        self.assertEqual(migrated['quest_action_proofs'], player['quest_action_proofs'])
        self.assertEqual(reopen(migrated)['inventory'][MARK], 7)
