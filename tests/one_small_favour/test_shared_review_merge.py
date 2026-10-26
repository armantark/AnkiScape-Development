"""The shared review seam preserves both openings when switching quests."""

import copy
import unittest

from tests.one_small_favour.test_opening_transactions import player
from tests.one_small_favour.test_review_dispatch import RuntimeFixture
from tests.quest_catalog.test_enakhra_opening import _player as enakhra_player
from tests.test_combat_quest_gate import _answer_review
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.one_small_favour import QUEST_ID, BLUNT_HATCHET, OPENING_PROOFS
from ankiscape.data.quest.enakhra_opening import QUEST_ID as ENAKHRA_ID, BASE
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blockers_pure
from ankiscape.logic_pure.quest.review_steps import (
    quest_review_phase_pure, quest_review_message_pure, quest_review_ready_pure,
    apply_quest_review_step_pure,
)


class SharedOpeningReviewTest(RuntimeFixture, unittest.TestCase):
    def test_registered_answers_interleave_both_openings_without_shared_credit(self):
        data = player(started=False)
        enakhra = enakhra_player()
        data['quests'][ENAKHRA_ID] = enakhra['quests'][ENAKHRA_ID]
        data['inventory'].update(enakhra['inventory'])
        for key in ('crafting_level', 'firemaking_level', 'prayer_level', 'magic_level'):
            data[key] = max(data[key], enakhra[key])
        self.addon._state.player_data = data
        for index, proof in enumerate(OPENING_PROOFS):
            self._answer(QUEST_ID, (proof,), 2 if index == 6 else 1)
            self.assertEqual(data['inventory'][BLUNT_HATCHET], int(index in (1, 2)))
            self.assertEqual(set(data['quest_action_proofs']) & set(OPENING_PROOFS),
                             set(OPENING_PROOFS[:index + 1]))
            descriptor = quest_review_phase_pure(data, ENAKHRA_ID)
            self._answer(ENAKHRA_ID, (descriptor['notice'],), 1)
        descriptor = quest_review_phase_pure(data, ENAKHRA_ID)
        self._answer(ENAKHRA_ID, (descriptor['notice'],), 2)
        self.assertEqual(data['quests'][QUEST_ID]['progress'], 2)
        self.assertEqual(data['inventory'][BASE], 0)
        self.assertEqual(len(self.saved), 15)
        self.assertEqual(self.errors, [])

    def _answer(self, quest_id, notices, expected_progress):
        data = self.addon._state.player_data
        data['current_quest'] = quest_id
        before = copy.deepcopy(data)
        other_id = ENAKHRA_ID if quest_id == QUEST_ID else QUEST_ID
        saves, messages = len(self.saved), len(self.messages)
        _answer_review(self.addon)
        self.assertEqual(len(self.saved), saves + 1)
        words = ' '.join('\n'.join(self.messages[messages:]).splitlines())
        self.assertTrue(words.startswith(' '.join(notices)))
        self.assertEqual(data['quests'][other_id], before['quests'][other_id])
        self.assertEqual(data['quests'][quest_id]['progress'], expected_progress)

    def test_enakhra_service_results_and_notices_survive_adapter_normalization(self):
        data = enakhra_player()
        for index in range(8):
            original = data
            before = copy.deepcopy(data)
            blockers = quest_current_stage_blockers_pure(data, ENAKHRA_ID, QUEST_DATA)
            descriptor = quest_review_phase_pure(data, ENAKHRA_ID)
            self.assertTrue(quest_review_ready_pure(data, ENAKHRA_ID, blockers))
            self.assertEqual(quest_review_message_pure(descriptor),
                             ((descriptor['notice'],), False))
            data, result = apply_quest_review_step_pure(data, ENAKHRA_ID, blockers)
            self.assertEqual(result, 'ready' if index == 7 else 'partial')
            self.assertEqual(original, before)
            self.assertEqual(before['quests'][ENAKHRA_ID]['progress'], 1)
            self.assertEqual(data['quests'][ENAKHRA_ID]['progress'], 1)
        self.assertEqual(data['inventory'][BASE], 0)
