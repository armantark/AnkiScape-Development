"""Both opening owners survive the shared review-seam merge."""

import copy
import unittest

from tests.one_small_favour.test_opening_transactions import player
from tests.one_small_favour.test_review_dispatch import RuntimeFixture
from tests.quest_catalog.test_toktz_opening import player as toktz_player
from tests.test_combat_quest_gate import _answer_review
from ankiscape.data.quest.one_small_favour import (
    QUEST_ID, BLUNT_HATCHET, OPENING_PROOFS, REPLACEMENT_MESSAGE,
)
from ankiscape.data.quest.toktz_opening import (
    QUEST_ID as TOKTZ_ID, TABLET, GUIDE, PROOFS, COMPLETED_LINES, RECOVERY_MESSAGE,
)


class MergedOpeningDispatchTest(RuntimeFixture, unittest.TestCase):
    def prepare_both(self, favour_prefix=0, toktz_prefix=0):
        data = player(favour_prefix)
        toktz = toktz_player(toktz_prefix, progress=1 if toktz_prefix else 0)
        data['quests'][TOKTZ_ID] = toktz['quests'][TOKTZ_ID]
        data['quest_action_proofs'] = sorted([*data['quest_action_proofs'], *PROOFS[:toktz_prefix]])
        data['inventory'].update(toktz['inventory'])
        for key, value in toktz.items():
            if key.endswith(('_level', '_exp')):
                data[key] = max(data[key], value)
        self.addon._state.player_data = data
        return data

    def answer(self, quest_id, notice, proof, expected_progress):
        data = self.addon._state.player_data
        data['current_quest'] = quest_id
        other_id = TOKTZ_ID if quest_id == QUEST_ID else QUEST_ID
        before = copy.deepcopy(data)
        saves, messages = len(self.saved), len(self.messages)
        _answer_review(self.addon)
        self.assertEqual(len(self.saved), saves + 1)
        self.assertEqual(len(self.messages), messages + 1)
        self.assertTrue(' '.join(self.messages[-1].splitlines()).startswith(notice))
        self.assertEqual(data['quests'][quest_id]['progress'], expected_progress)
        self.assertEqual(data['quests'][other_id], before['quests'][other_id])
        self.assertEqual(set(data['quest_action_proofs']) - set(before['quest_action_proofs']),
                         {proof} if proof else set())
        self.assertEqual(self.saved[-1]['inventory'], data['inventory'])
        self.assertEqual(self.saved[-1]['quests'], data['quests'])
        self.assertEqual(self.errors, [])

    def test_registered_answers_interleave_without_cross_credit_or_extra_notices(self):
        data = self.prepare_both()
        for index in range(5):
            self.answer(QUEST_ID, OPENING_PROOFS[index], OPENING_PROOFS[index], 1)
            self.answer(TOKTZ_ID, COMPLETED_LINES[index], PROOFS[index], 2 if index == 4 else 1)
        self.answer(QUEST_ID, OPENING_PROOFS[5], OPENING_PROOFS[5], 1)
        self.answer(QUEST_ID, OPENING_PROOFS[6], OPENING_PROOFS[6], 2)
        self.assertEqual(set(data['quest_action_proofs']), set((*OPENING_PROOFS, *PROOFS)))
        self.assertEqual(data['inventory'][BLUNT_HATCHET], 0)
        self.assertEqual(data['inventory'][TABLET], 1)
        self.assertEqual(data['inventory'][GUIDE], 1)
        self.assertEqual(len(self.saved), 12)

    def test_each_recovery_costs_its_own_answer_when_switching_quests(self):
        data = self.prepare_both(3, 2)
        data['inventory'].pop(BLUNT_HATCHET)
        data['inventory'].pop(TABLET)
        self.answer(QUEST_ID, REPLACEMENT_MESSAGE, None, 1)
        self.assertEqual(data['inventory'][BLUNT_HATCHET], 1)
        self.assertNotIn(TABLET, data['inventory'])
        self.answer(TOKTZ_ID, RECOVERY_MESSAGE, None, 1)
        self.assertEqual(data['inventory'][TABLET], 1)
        self.assertEqual(data['inventory'][BLUNT_HATCHET], 1)
        self.answer(QUEST_ID, OPENING_PROOFS[3], OPENING_PROOFS[3], 1)
        self.answer(TOKTZ_ID, COMPLETED_LINES[2], PROOFS[2], 1)
        self.assertEqual(data['inventory'][BLUNT_HATCHET], 0)
        self.assertEqual(data['inventory'][TABLET], 1)
