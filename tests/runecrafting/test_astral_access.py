"""The Astral altar is gated by Lunar Diplomacy alone.

The altar definition carries no talisman or tiara, so no item can be the
key; a player past the quest walks up with Pure essence and crafts a full
28-essence load, the same base as a tiara, hood or talisman staff.
"""

import unittest

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from tests.test_runtime_actions import _context
from ankiscape.core.constants import (
    ITEM_DEFINITIONS,
    ORE_DATA,
    QUEST_UNLOCK_RULES,
    RUNECRAFTING_DATA,
    RUNECRAFTING_POUCH_DATA,
)
from ankiscape.core.storage_pure import default_player_data
from ankiscape.logic_pure.logic_pure_runecrafting import runecrafting_locked_reasons_pure
from ankiscape.runtime.runtime_actions import handle_runecrafting_answer


def _astral_player(*completed_quests):
    player_data = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
    for quest_id in completed_quests:
        player_data["quests"][quest_id] = {"started": True, "completed": True}
    player_data["runecrafting_level"] = 40
    player_data["inventory"]["Pure essence"] = 100
    player_data["current_runecrafting"] = "craft_astral_runes"
    return player_data


def _astral_locked_reasons(player_data):
    return runecrafting_locked_reasons_pure(
        player_data,
        "craft_astral_runes",
        RUNECRAFTING_DATA,
        RUNECRAFTING_POUCH_DATA,
        QUEST_UNLOCK_RULES,
    )


class AstralAltarAccessTest(unittest.TestCase):
    def test_lunar_diplomacy_opens_the_altar_without_an_access_item(self):
        player_data = _astral_player("rune_mysteries", "lunar_diplomacy")
        self.assertNotIn("head", player_data["equipment"])
        self.assertNotIn("weapon", player_data["equipment"])

        self.assertEqual(_astral_locked_reasons(player_data), ())

        calls = {"xp": [], "saves": 0, "errors": []}
        ok = handle_runecrafting_answer(
            _context(player_data, calls, random_values=[0.999] * 128)
        )

        self.assertTrue(ok)
        self.assertEqual(calls["errors"], [])
        self.assertEqual(player_data["inventory"]["Astral rune"], 28)
        self.assertEqual(player_data["inventory"]["Pure essence"], 72)
        self.assertAlmostEqual(player_data["runecrafting_exp"], 28 * 8.7)

    def test_the_altar_stays_locked_before_lunar_diplomacy(self):
        player_data = _astral_player("rune_mysteries")

        self.assertEqual(_astral_locked_reasons(player_data), ("Lunar Diplomacy",))


if __name__ == "__main__":
    unittest.main()
