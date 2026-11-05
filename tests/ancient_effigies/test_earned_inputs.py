"""Effigies earned by unchanged producers reach the controller's complete use path.

Nothing here injects an effigy: Bork drops one through the real Combat kernel,
and the Abyssal demon's own drop row credits one through production drop
settlement and banking. The shared save then gives each its identity.
"""

from __future__ import annotations

import random
import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.core.constants import COMBAT_ENEMY_DATA, EQUIPMENT_DATA
from ankiscape.data.ancient_effigies.catalog import SKILL_PAIRS
from ankiscape.data.bork_data import BORK_EFFIGY_ITEM, BORK_RARE_DROPS
from ankiscape.logic.ancient_effigies.custody import INSTANCES_KEY
from ankiscape.logic.bork_logic import apply_bork_review_pure
from ankiscape.logic_pure.logic_pure_combat_outcome import _combat_bank_burst_rewards, _combat_settle_kill_rewards
from tests.ancient_effigies.test_runtime_undo import load_feature
from tests.test_bork import _loaded_player

_PAIR_SKILLS = sorted({skill for pair in SKILL_PAIRS for skill in pair})


def _effigy_slot(enemy_id):
    """The Abyssal demon main table's Starved effigy slot: (first index, width, total)."""
    table = COMBAT_ENEMY_DATA[enemy_id]["drops"]["tables"][0]
    cursor = 0
    for row in table["slots"]:
        if row.get("item") == "Starved ancient effigy":
            return cursor, row["slots"], table["total"]
        cursor += row.get("slots", 0)
    raise AssertionError("no effigy slot")


class EarnedEffigyTest(unittest.TestCase):
    def setUp(self):
        self.addon, self.feature, self.controller, self.collection = load_feature(self, "ankiscape_effigy_earned")

    def _use_through_the_controller(self, earned):
        """Save the earned state through the shared seam, then inspect and investigate."""
        self.assertNotIn(INSTANCES_KEY, {key for key, value in earned.items() if value})
        self.addon._state.player_data = earned
        self.addon._state.current_skill = "None"
        self.addon.save_player_data()
        live = self.addon._state.player_data
        self.assertEqual(list(live[INSTANCES_KEY]), ["ancient-effigy-1"])
        self.assertEqual(self.collection.values["ankiscape_player_data"][INSTANCES_KEY], live[INSTANCES_KEY])
        rows = self.controller.rows()
        self.assertEqual([(row["name"], row["usable"]) for row in rows], [("Starved ancient effigy", True)])
        inspected = self.controller.inspect("ancient-effigy-1")
        self.assertTrue(inspected.ok, inspected.message)
        detail = self.controller.detail("ancient-effigy-1")
        skill_id = detail["choices"][0]["skill_id"]
        exp_before = live.get(f"{skill_id}_exp", 0)
        result = self.controller.investigate(detail["token"], skill_id)
        self.assertTrue(result.ok, result.message)
        live = self.addon._state.player_data
        self.assertEqual(live[f"{skill_id}_exp"] - exp_before, 15000)
        self.assertEqual(live["inventory"].get("Starved ancient effigy", 0), 0)
        self.assertEqual(live["inventory"]["Nourished ancient effigy"], 1)
        self.assertEqual(live[INSTANCES_KEY]["ancient-effigy-1"]["item_id"], 18779)

    def test_bork_rare_drop_row_is_unchanged(self):
        self.assertEqual(BORK_EFFIGY_ITEM, "Starved ancient effigy")
        self.assertEqual(
            BORK_RARE_DROPS,
            (
                ("Starved ancient effigy", 1.0 / 64.0),
                ("Clue scroll (elite)", 1.0 / 32.0),
                ("Clue scroll (hard)", 1.0 / 16.0),
            ),
        )

    def test_a_bork_kill_through_the_real_kernel_earns_a_usable_effigy(self):
        data = _loaded_player(**{f"{skill_id}_level": 91 for skill_id in _PAIR_SKILLS})
        self.assertEqual(data["inventory"].get("Starved ancient effigy", 0), 0)
        rng = random.Random(183).random
        for review in range(1, 60):
            data, ok, result = apply_bork_review_pure(data, rng, equipment_data=EQUIPMENT_DATA)
            self.assertTrue(ok, result)
            if result.get("outcome"):
                break
        else:
            self.fail("the real kernel never resolved the fight")
        self.assertEqual(review, 25)
        self.assertIn("Bork defeated", result["outcome"])
        self.assertEqual(result["coins"], 3227)
        self.assertEqual(result["rare_drops"], {"Starved ancient effigy": 1})
        self.assertEqual(data["inventory"]["Starved ancient effigy"], 1)
        self._use_through_the_controller(data)

    def test_the_abyssal_demon_effigy_row_reaches_the_same_use_path(self):
        first, width, total = _effigy_slot("abyssal_demon")
        self.assertEqual((first, width, total), (667, 8, 1024))
        rolls = iter([(first + width / 2) / total])
        rng = lambda: next(rolls, 0.5)  # noqa: E731
        data = _loaded_player(**{f"{skill_id}_level": 91 for skill_id in _PAIR_SKILLS})
        drops, xp_rewards = {}, {}
        data, _refused_clue, _ticks = _combat_settle_kill_rewards(
            data, COMBAT_ENEMY_DATA["abyssal_demon"], "abyssal_demon", rng, drops, xp_rewards, {}
        )
        self.assertEqual(drops.get("Starved ancient effigy"), 1)
        data, _events = _combat_bank_burst_rewards(data, 0, drops, xp_rewards)
        self.assertEqual(data["inventory"]["Starved ancient effigy"], 1)
        self._use_through_the_controller(data)


if __name__ == "__main__":
    unittest.main()
