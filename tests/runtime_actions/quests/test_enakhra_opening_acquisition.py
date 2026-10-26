"""Real Mining events and ordinary quest reviews preserve acquisition truth."""

import copy
import unittest

import pkg_alias  # noqa: F401
from ankiscape.core.constants import EXP_TABLE, QUEST_DATA
from ankiscape.data.quest.enakhra_opening import QUEST_ID, MASS_KEY, BLOCK, BASE
from ankiscape.logic_pure.logic_pure_quest import quest_journal_rows_pure
from ankiscape.runtime.runtime_actions import answer_handler_for_key, run_answer_with_carried_overlay
from tests.runtime_actions.quests import test_enakhra_opening as harness
from tests.test_combat_quest_gate import _answer_review
from tests.test_runtime_actions import _context


class EnakhraAcquisitionTest(unittest.TestCase):
    setUp = harness.EnakhraRuntimeTest.setUp
    tearDown = harness.EnakhraRuntimeTest.tearDown
    _reset = harness.EnakhraRuntimeTest._reset
    _assert_one_review = harness.EnakhraRuntimeTest._assert_one_review

    def _mine(self, output_roll, *, success=True, ore="sandstone"):
        player = self.addon._state.player_data
        player["current_ore"] = ore
        calls = {"xp": [], "saves": 0, "errors": []}
        values = [0.0 if success else 0.999999, output_roll, 0.99, 0.99] + [0.99] * 40
        ctx = _context(player, calls, random_values=values)
        handler = answer_handler_for_key("mining")
        self.assertTrue(run_answer_with_carried_overlay(ctx, "mining", handler))
        self.assertEqual(calls["errors"], [])
        return calls

    def _finish_base(self):
        for action in ("chisel_base", "talk_after_base", "place_base"):
            self._assert_one_review(action, 2 if action == "place_base" else 1)
        player = self.addon._state.player_data
        self.assertEqual(player[MASS_KEY], 32)
        self.assertEqual(player["inventory"].get(BLOCK, 0), 0)
        self.assertEqual(player["inventory"].get(BASE, 0), 0)
        return player

    def _set_mining_level(self):
        player = self.addon._state.player_data
        player["mining_level"] = 35
        player["mining_exp"] = EXP_TABLE[34]

    def test_all_real_mining_sizes_award_existing_source_experience_and_only_mining_proof(self):
        self._reset({})
        self._set_mining_level()
        player = self.addon._state.player_data
        belt = copy.deepcopy(player["toolbelt"])
        for roll, size, xp in ((0.125, 1, 30.0), (0.375, 2, 40.0), (0.625, 5, 50.0), (0.875, 10, 60.0)):
            previous = player["mining_exp"]
            calls = self._mine(roll)
            name = f"Sandstone ({size}kg)"
            self.assertEqual(player["inventory"][name], 1)
            self.assertEqual(player["carried_inventory"]["sandstone"][name], 1)
            self.assertEqual(player["mining_exp"] - previous, xp)
            self.assertEqual(calls["xp"], [xp])
            self.assertEqual(player["quest_action_proofs"], ["Mine sandstone"])
            self.assertEqual(player[MASS_KEY], 0)
            self.assertNotIn(BLOCK, player["inventory"])
            self.assertNotIn(BASE, player["inventory"])
        self.assertEqual(player["toolbelt"], belt)
        self.assertNotIn("Chisel", player["inventory"])
        self.assertNotIn("Bronze pickaxe", player["inventory"])

    def test_mine_and_deliver_route_reaches_base_without_coal_and_retains_normal_tools(self):
        self._reset({})
        self._set_mining_level()
        player = self.addon._state.player_data
        belt = copy.deepcopy(player["toolbelt"])
        crafting_exp = player["crafting_exp"]
        mining_exp = player["mining_exp"]
        self._assert_one_review("offer_help")
        for roll, total in ((0.875, 10), (0.875, 20), (0.875, 30), (0.375, 32)):
            self._mine(roll)
            self._assert_one_review("receive_32kg" if total == 32 else "deliver_sandstone")
            self.assertEqual(player[MASS_KEY], total)
        player = self._finish_base()
        self.assertEqual(player["mining_exp"] - mining_exp, 220.0)
        self.assertEqual(player["crafting_exp"], crafting_exp)
        self.assertEqual(player["toolbelt"], belt)
        self.assertEqual(player["inventory"].get("Coal", 0), 0)
        lines = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[0]["lines"]
        self.assertIn("I have mined sandstone.", lines)
        self.assertNotIn("I have mined coal.", lines)
        self.assertNotIn("Mine 1 coal if you did not bring one; it is needed later.", lines)

    def test_failed_mining_has_no_proof_then_brought_stock_completes_at_mining_one(self):
        self._reset({})
        self._set_mining_level()
        player = self.addon._state.player_data
        before_xp = player["mining_exp"]
        self._mine(0.875, success=False)
        self.assertEqual(player["quest_action_proofs"], [])
        self.assertEqual(player["mining_exp"], before_xp)
        self.assertEqual(player["inventory"].get("Sandstone (10kg)", 0), 0)
        self._reset({"Sandstone (10kg)": 3, "Sandstone (2kg)": 1, "Coal": 1})
        self.assertEqual(self.addon._state.player_data["mining_level"], 1)
        for action in ("offer_help", "deliver_sandstone", "deliver_sandstone", "deliver_sandstone", "receive_32kg"):
            self._assert_one_review(action)
        player = self._finish_base()
        self.assertEqual(player["inventory"]["Coal"], 1)
        self.assertNotIn("Mine sandstone", player["quest_action_proofs"])
        self.assertNotIn("Mine coal", player["quest_action_proofs"])
        text = " ".join(quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[0]["lines"])
        self.assertNotIn("I have mined", text)

    def test_mixed_stock_and_real_coal_do_not_attribute_every_delivery_to_mining(self):
        self._reset({"Sandstone (10kg)": 2, "Sandstone (2kg)": 1})
        self._set_mining_level()
        self._mine(0.875)
        coal = self._mine(0.5, ore="coal")
        self.assertEqual(coal["xp"], [50.0])
        for _ in range(5):
            _answer_review(self.addon)
        player = self._finish_base()
        self.assertEqual(player["inventory"]["Coal"], 1)
        lines = quest_journal_rows_pure(player, QUEST_ID, QUEST_DATA)[0]["lines"]
        self.assertIn("I have mined sandstone.", lines)
        self.assertIn("I have mined coal.", lines)
        self.assertIn("Sandstone given to Lazim: 32/32 kg.", lines)
        self.assertFalse(any("mined 32" in line.lower() for line in lines))
        self.assertEqual(player["mining_exp"], EXP_TABLE[34] + 110.0)
