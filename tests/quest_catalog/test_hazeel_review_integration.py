"""The merged review adapter preserves each quest's transaction vocabulary."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.hazeel_opening import QUEST_ID, POISON, PROOFS
from ankiscape.logic_pure.logic_pure_quest import quest_current_stage_blockers_pure
from ankiscape.logic_pure.quest.eligibility import quest_eligibility_reasons_pure
from ankiscape.logic_pure.quest.review_steps import (
    apply_quest_review_step_pure, quest_review_phase_pure, quest_review_ready_pure,
)
from tests.quest_catalog.hazeel_helpers import branch_player
from tests.quest_catalog.test_hazeel_stage_eligibility import injected_catalog
from tests.quest_catalog.test_oronwen_repair import _player as oronwen_player
from tests.quest_catalog.test_enakhra_opening import _player as enakhra_player


def adapter_step(player, quest_id, catalog=QUEST_DATA):
    blockers = quest_current_stage_blockers_pure(player, quest_id, catalog)
    return apply_quest_review_step_pure(
        player, quest_id, blockers, quest_data=catalog,
        eligibility_reasons=quest_eligibility_reasons_pure,
    )


class HazeelReviewIntegrationTest(unittest.TestCase):
    def test_adapter_preserves_hazeel_oronwen_and_enakhra_pending_results(self):
        cases = (
            (branch_player('hazeel'), QUEST_ID, 'pending'),
            (oronwen_player(), 'mournings_end_part_i', 'pending'),
            (enakhra_player(), 'enakhras_lament', 'partial'),
        )
        for player, quest_id, expected in cases:
            with self.subTest(quest=quest_id):
                before = copy.deepcopy(player)
                after, result = adapter_step(player, quest_id)
                self.assertEqual(result, expected)
                self.assertEqual(player, before)
                self.assertEqual(after['quests'][quest_id], before['quests'][quest_id])
                self.assertNotEqual(after, before)
        after, result = adapter_step(cases[0][0], QUEST_ID)
        self.assertEqual(after['inventory'][POISON], 1)
        self.assertIn(PROOFS['cult_acceptance'], after['quest_action_proofs'])

    def test_adapter_passes_external_stage_obligations_before_cult_supply(self):
        player = branch_player('hazeel')
        before = copy.deepcopy(player)
        catalog = injected_catalog('required_inventory', {'Feather': 999}, 'hazeel')
        blockers = quest_current_stage_blockers_pure(player, QUEST_ID, catalog)
        self.assertEqual(quest_review_phase_pure(player, QUEST_ID).action_id, 'cult_acceptance')
        self.assertFalse(quest_review_ready_pure(
            player, QUEST_ID, blockers, quest_data=catalog,
            eligibility_reasons=quest_eligibility_reasons_pure,
        ))
        after, result = adapter_step(player, QUEST_ID, catalog)
        self.assertIs(after, player)
        self.assertEqual(result, 'unchanged')
        self.assertEqual(player, before)

    def test_unrelated_quest_cannot_execute_another_quests_pending_deed(self):
        player = branch_player('hazeel')
        before = copy.deepcopy(player)
        self.assertIsNone(quest_review_phase_pure(player, 'rune_mysteries'))
        self.assertFalse(quest_review_ready_pure(player, 'rune_mysteries', ()))
        after, result = apply_quest_review_step_pure(player, 'rune_mysteries', ())
        self.assertIs(after, player)
        self.assertEqual(result, 'unchanged')
        self.assertEqual(player, before)
