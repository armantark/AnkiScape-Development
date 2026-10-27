"""Witch recovery survives the shared Hazeel and service review adapter."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import QUEST_DATA
from ankiscape.data.quest.hazeel_opening import VALVES
from ankiscape.data.quest.witchs_house import (
    QUEST_ID, BACKROOM_KEY, BALL, TAKE_KEY, TAKE_BALL, RESUME_KEY,
)
from ankiscape.logic_pure.quest.eligibility import quest_eligibility_reasons_pure
from ankiscape.logic_pure.quest.review_steps import (
    apply_quest_review_step_pure, quest_review_ready_pure,
)
from .test_witchs_house import blockers, progress
from .test_witchs_house_runtime import runtime_player
from .test_witchs_house_storage import reload_player


class WitchsHouseMergedReviewTest(unittest.TestCase):
    def test_both_recoveries_keep_deed_only_through_shared_adapter(self):
        for stage, item, proof in ((11, BACKROOM_KEY, TAKE_KEY), (14, BALL, TAKE_BALL)):
            with self.subTest(stage=stage):
                player = runtime_player(stage)
                before = copy.deepcopy(player)
                reasons = blockers(player)
                self.assertTrue(quest_review_ready_pure(
                    player, QUEST_ID, reasons, quest_data=QUEST_DATA,
                    eligibility_reasons=quest_eligibility_reasons_pure,
                ))
                recovered, result = apply_quest_review_step_pure(
                    player, QUEST_ID, reasons, quest_data=QUEST_DATA,
                    eligibility_reasons=quest_eligibility_reasons_pure,
                )
                self.assertEqual(result, 'deed_only')
                self.assertEqual(player, before)
                self.assertEqual(recovered['quests'], before['quests'])
                self.assertEqual(recovered['inventory'][item], 1)
                self.assertIn(proof, recovered['quest_action_proofs'])
                expected, ok, complete = progress(player)
                self.assertTrue(ok)
                self.assertFalse(complete)
                self.assertEqual(expected, recovered)
                for key in ('quest_points', 'constitution_exp', 'quest_combat_encounters',
                            'quest_combat_encounter_counts', 'quest_combat_active_encounters'):
                    self.assertEqual(expected[key], before[key])
                if stage == 14:
                    self.assertEqual(expected['inventory'].get(BACKROOM_KEY, 0), 0)
                advanced, ok, complete = progress(expected)
                self.assertTrue(ok)
                self.assertEqual(advanced['quests'][QUEST_ID]['progress'], stage + 1)
                self.assertEqual(complete, stage == 14)

    def test_hazeel_valve_sanitation_and_witch_remediation_survive_one_load(self):
        player = runtime_player(9)
        valve_id = str(VALVES[0].object_id)
        player['hazeel_cult_valve_states'] = {valve_id: 'left', 'bad': 'right'}
        loaded = reload_player(player, 125)
        self.assertEqual(loaded['hazeel_cult_valve_states'], {valve_id: 'left'})
        self.assertEqual(loaded['quests'][QUEST_ID]['progress'], 3)
        self.assertEqual(loaded[RESUME_KEY], 12)
        self.assertEqual(reload_player(loaded), loaded)
