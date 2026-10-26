"""Hazeel opening catalog, identities and truthful read-only journals."""

import copy
import hashlib
import json
from pathlib import Path
import struct
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA, ITEM_DEFINITIONS, QUEST_REWARD_ITEM_DATA
from ankiscape.data.quest.hazeel_opening import (
    ACTIONS, PROOFS, REQUIRED_PROOFS, VALVES, VALVE_KEY, SHARED, BRANCH_DEEDS,
    BRANCH_ROUTES, CORRECT_VALVE_ACTIONS, ENDPOINTS, ENDPOINT_SENTENCES,
    POISON, MARK, OWNED_SENTENCES, VALVE_CONTEXT, HAZEEL_OPENING_ITEMS,
)
from ankiscape.data.quest.item_names import QUEST_REWARD_ITEM_NAME_OVERRIDES, QUEST_STAGE_ITEM_NAME_OVERRIDES
from ankiscape.generated.quest_catalog_generated import PRE_EOC_QUEST_CATALOG
from ankiscape.logic_pure.logic_pure_quest import (
    quest_journal_rows_pure, quest_current_stage_choices_pure, apply_quest_route_choice_pure,
    can_attempt_quest_review_pure,
)
from ankiscape.logic_pure.quest.hazeel import apply_hazeel_opening_action_pure
from tests.quest_catalog.hazeel_helpers import (
    fresh_player, started_player, review, choose, shared_player, branch_player, complete_opening,
)

QUEST_ID = 'hazeel_cult'
ROOT = Path(__file__).resolve().parents[2]


def first_journal(player):
    return quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[0]


class HazeelOpeningTest(unittest.TestCase):
    def test_exact_branch_rows_and_empty_start_gates(self):
        quest = QUEST_DATA[QUEST_ID]
        rows = quest['stage_requirements']
        first = [row for row in rows if row['stage'] == 1]
        self.assertEqual([row['variant'] for row in first], ['carnillean', 'hazeel'])
        for row, branch, total in zip(first, BRANCH_DEEDS, (9, 12)):
            expected = tuple(PROOFS[key] for key in (*BRANCH_DEEDS[branch], *CORRECT_VALVE_ACTIONS, ENDPOINTS[branch]))
            self.assertEqual(row['required_actions'], expected)
            self.assertEqual(len(row['required_actions']), total)
            self.assertEqual(row['required_routes'], (BRANCH_ROUTES[branch],))
            for key in ('auto_actions', 'consumed_inventory', 'produced_inventory'):
                self.assertFalse(row[key])
        self.assertEqual(first[0]['description'], "Complete Ceril's commission, refuse Clivet and set all five valves correctly.")
        self.assertEqual(first[1]['description'], "Complete Ceril's commission, Clivet's poison-and-Mark task and all five correct valve settings.")
        self.assertEqual(quest['stages'], 4)
        for key in ('required_quests', 'required_skills', 'required_items', 'required_quest_points'):
            self.assertFalse(quest[key])
        self._assert_later_rows(quest)

    def _assert_later_rows(self, quest):
        later = sorted((row for row in quest['stage_requirements'] if row['stage'] > 1), key=lambda row: (row['stage'], row['variant']))
        self.assertEqual([(row['stage'], row['variant']) for row in later], [(2, 'carnillean'), (2, 'hazeel'), (3, 'carnillean'), (3, 'hazeel')])
        self.assertEqual(later[0]['produced_inventory'], {'Carnillean armour': 2})
        self.assertEqual(later[0]['combat_encounters'][0]['quantity'], 2)
        self.assertEqual(later[2]['consumed_inventory'], {'Carnillean armour': 1})
        self.assertEqual(later[2]['produced_inventory'], {'Carnillean armour': 2})
        self.assertTrue(later[2]['repeatable_until_consumed'])
        self.assertFalse(later[3]['produced_inventory'])
        for row in later:
            self.assertEqual(row['required_actions'], (f"Complete Hazeel Cult stage {row['stage']} objective",))
        raw = next(row for row in PRE_EOC_QUEST_CATALOG if row['id'] == QUEST_ID)
        for stage in raw['journal_stages'][1:]:
            self.assertEqual(quest['journal_stages'][stage['stage']], stage['journal'])

    def test_period_item_and_valve_bindings(self):
        for name, item_id, model in ((POISON, 273, 2714), (MARK, 2406, 40909)):
            spec = HAZEEL_OPENING_ITEMS[name]
            self.assertEqual((spec['item_id'], spec['model_id'], spec['category']), (item_id, model, 'material'))
            self.assertIs(spec['stackable'], False)
            self.assertIs(spec['tradeable'], False)
            self.assertEqual(QUEST_REWARD_ITEM_DATA[name]['item_id'], item_id)
            self.assertEqual([item.storage_key for item in ITEM_DEFINITIONS if item.source_item_id == item_id], [name])
        for aliases in (QUEST_REWARD_ITEM_NAME_OVERRIDES, QUEST_STAGE_ITEM_NAME_OVERRIDES):
            self.assertEqual(aliases["Hazeel's mark"], MARK)
        self.assertEqual([(v.number, v.object_id, v.varbit, v.correct, v.opposite_option) for v in VALVES], [
            (1,2844,4846,'right','Turn-left'), (2,2845,4847,'right','Turn-left'),
            (3,2846,4848,'left','Turn-right'), (4,2847,4849,'right','Turn-left'), (5,2848,4850,'right','Turn-left'),
        ])
        for item in ITEM_DEFINITIONS:
            if 'weapon poison' in item.storage_key.lower():
                self.assertNotEqual(item.source_item_id, 273)

    def test_choice_waits_for_real_briefing(self):
        player = fresh_player()
        for player in (player, started_player(), review(started_player())):
            before = copy.deepcopy(player)
            self.assertEqual(quest_current_stage_choices_pure(player, QUEST_ID, QUEST_DATA), ())
            result, ok = apply_quest_route_choice_pure(player, QUEST_ID, QUEST_DATA, BRANCH_ROUTES['hazeel'])
            self.assertFalse(ok)
            self.assertIs(result, player)
            self.assertEqual(player, before)
        player = shared_player()
        choices = quest_current_stage_choices_pure(player, QUEST_ID, QUEST_DATA)
        self.assertEqual([x['label'] for x in choices[0]['options']], ['Ceril Carnillean', "Hazeel's cult"])
        self.assertFalse(can_attempt_quest_review_pure(player, QUEST_ID, QUEST_DATA))
        before = copy.deepcopy(player)
        selected = choose(player, 'hazeel')
        expected = copy.deepcopy(before)
        expected['quest_route_states'][QUEST_ID] = [BRANCH_ROUTES['hazeel']]
        self.assertEqual(selected, expected)
        self.assertEqual(player, before)
        rejected, ok = apply_quest_route_choice_pure(selected, QUEST_ID, QUEST_DATA, BRANCH_ROUTES['carnillean'])
        self.assertFalse(ok)
        self.assertIs(rejected, selected)

    def _assert_journal_trace(self, branch):
        player = started_player()
        neutral = first_journal(player)
        self.assertIn('Carnillean route, if chosen', neutral['lines'])
        self.assertIn("Hazeel's cult route, if chosen", neutral['lines'])
        expected_ids = (*BRANCH_DEEDS[branch], *CORRECT_VALVE_ACTIONS)
        for index, action_id in enumerate(expected_ids):
            if index == 2:
                player = choose(player, branch)
            row = first_journal(player)
            self.assertIn('Pending: ' + ACTIONS[action_id].pending, row['lines'])
            self.assertFalse(row['completed'])
            self.assertTrue(row['current'])
            player = review(player)
            row = first_journal(player)
            self.assertIn('<s>Done: ' + ACTIONS[action_id].completed + '</s>', row['lines'])
            self.assertTrue(all(text in row['lines'] for text in VALVE_CONTEXT))
        row = first_journal(player)
        self.assertFalse(row['current'])
        self.assertIn(ENDPOINT_SENTENCES[branch], row['lines'])
        self.assertEqual(sum(line.startswith('<s>Done: ') for line in row['lines']), len(expected_ids))
        self.assertFalse(any('Pending:' in line for line in row['lines']))
        if branch == 'carnillean':
            self.assertIn('Clivet departs after refusal.', row['lines'])
            self.assertFalse(any('Scruffy' in line for line in row['lines']))
        else:
            self.assertFalse(any('Refused' in line for line in row['lines']))

    def test_branch_journals_follow_only_performed_deeds(self):
        for branch in BRANCH_DEEDS:
            with self.subTest(branch=branch):
                self._assert_journal_trace(branch)
        player = branch_player('hazeel')
        # Explicit owned-item fixture, with all deeds still performed normally.
        player['inventory'].update({POISON: 3, MARK: 4})
        for _ in range(4):
            player = review(player)
        for sentence in OWNED_SENTENCES.values():
            self.assertIn('<s>Done: ' + sentence + '</s>', first_journal(player)['lines'])
        # Explicit legacy state with no detailed opening evidence.
        for stage in (2, 3, 4):
            legacy = fresh_player()
            legacy['quests'][QUEST_ID] = dict(started=True, completed=stage==4, progress=stage)
            row = first_journal(legacy)
            self.assertEqual(row['lines'], ('I have already progressed beyond this opening.',))
            self.assertFalse(row['current'])
            self.assertFalse(row['completed'])

    def test_journal_and_inspect_are_read_only(self):
        for player in (started_player(), branch_player('carnillean'), complete_opening('hazeel')):
            before = copy.deepcopy(player)
            for _ in range(3):
                quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)
                for valve in VALVES:
                    result, ok, _ = apply_hazeel_opening_action_pure(player, f'valve_{valve.object_id}_{valve.correct}', valve.object_id, 'Inspect')
                    self.assertFalse(ok)
                    self.assertIs(result, player)
            self.assertEqual(player, before)

    def test_icons_and_provenance_resolve(self):
        for name, digest in ((POISON, '2f6fa9efec0a044592de05a8e31b419158651baed1d8ba5e03a408a4578fe07c'),
                             (MARK, '7727f58e3597f1c0e5038e5474c99f6ddcf2a7abd47db14d3373ddcda7b8b8f5')):
            item = next(item for item in ITEM_DEFINITIONS if item.storage_key == name)
            body = Path(item.asset_path).read_bytes()
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
            if name == MARK:
                self.assertEqual(struct.unpack('>II', body[16:24]), (28,29))
                self.assertEqual(len(body), 253)
                self.assertEqual(hashlib.sha1(body).hexdigest(), '11fd466e741dcffce5e3db4fefe6dd39ebba2296')
                provenance = json.loads((ROOT/'data/quest/hazeel_assets/assets_provenance.json').read_text())['data/quest/hazeel_assets/mark_of_hazeel.png']
                self.assertEqual(provenance['timestamp'], '2010-04-04T00:52:14Z')
                self.assertEqual(provenance['file_page_oldid'], 6412175)
                self.assertEqual(provenance['sha256'], digest)
                self.assertEqual(provenance['license_string'], 'unknown')
            else:
                provenance = json.loads((ROOT/'assets_provenance.json').read_text())['questitems/poison.png']
                self.assertEqual(provenance['timestamp'], '2011-08-17T01:05:38Z')
