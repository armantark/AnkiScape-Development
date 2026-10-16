"""A fed hood reserves a carried slot and grants only that pack's altar access."""

import unittest

import pkg_alias  # noqa: F401
from ankiscape.logic_pure.logic_pure_runecrafting import runecrafting_altar_access_source_pure
from ankiscape.runtime.runtime_actions import handle_runecrafting_answer, run_answer_with_carried_overlay
from tests.test_runtime_actions import _context


def _player():
    return {
        "inventory": {"Wicked hood": 1, "Rune essence": 100},
        "equipment": {},
        "quests": {"rune_mysteries": {"completed": True}},
        "current_runecrafting": "craft_air_runes",
        "runecrafting_level": 1, "runecrafting_exp": 0,
        "wicked_hood": {"fed_altars": ["air"]},
        "completed_achievements": [],
    }


def _review(player, calls=None):
    return run_answer_with_carried_overlay(_context(player, calls, random_values=[1.0] * 300), "runecrafting", handle_runecrafting_answer)


class WickedHoodPackTest(unittest.TestCase):
    def test_auto_pack_keeps_hood_through_crafting_and_refill(self):
        player = _player()
        self.assertEqual(runecrafting_altar_access_source_pure(player, "air"), "hood")
        self.assertTrue(_review(player))
        self.assertEqual(player["inventory"]["Air rune"], 27)
        self.assertEqual(player["inventory"]["Wicked hood"], 1)
        self.assertEqual(player["carried_inventory"]["craft_air_runes"], {"Wicked hood": 1})
        self.assertTrue(_review(player))
        for _ in range(player["skilling_bank_run"]["reviews_remaining"]):
            self.assertTrue(_review(player))
        self.assertEqual(player["carried_inventory"]["craft_air_runes"], {"Wicked hood": 1, "Rune essence": 27})
        self.assertTrue(_review(player))
        self.assertEqual(player["inventory"]["Air rune"], 54)

    def test_tiara_staff_or_worn_hood_keeps_all_essence_slots(self):
        for equipment in ({"head": "Air tiara"}, {"weapon": "Air talisman staff"}, {"head": "Wicked hood"}):
            with self.subTest(equipment=equipment):
                player = _player()
                player["equipment"] = equipment
                self.assertTrue(_review(player))
                self.assertEqual(player["inventory"]["Air rune"], 28)
                self.assertNotIn("Wicked hood", player.get("carried_inventory", {}).get("craft_air_runes", {}))

    def test_unfed_or_custom_unpacked_hood_cannot_open_altar(self):
        for custom in (False, True):
            with self.subTest(custom=custom):
                player = _player()
                if custom:
                    player["carried_advanced_targets"] = {"craft_air_runes": True}
                    player["carried_layout"] = {"craft_air_runes": {"Rune essence": 28}}
                else:
                    player["wicked_hood"]["fed_altars"] = ["water"]
                calls = {"xp": [], "saves": 0, "errors": []}
                self.assertFalse(_review(player, calls))
                self.assertEqual(calls["errors"], [(
                    "Runecrafting unavailable",
                    "Air runes cannot run right now, so Runecrafting has been switched off.",
                )])
                self.assertTrue(calls["deactivated"])
                self.assertEqual(player["inventory"].get("Air rune", 0), 0)
                self.assertEqual(player["runecrafting_exp"], 0)

    def test_custom_carried_hood_grants_entry(self):
        player = _player()
        player["carried_advanced_targets"] = {"craft_air_runes": True}
        player["carried_layout"] = {"craft_air_runes": {"Wicked hood": 1, "Rune essence": 4}}
        self.assertTrue(_review(player))
        self.assertEqual(player["inventory"]["Air rune"], 4)
        self.assertEqual(player["carried_inventory"]["craft_air_runes"], {"Wicked hood": 1})

    def test_custom_talisman_pack_does_not_require_banked_hood(self):
        player = _player()
        player["inventory"]["Air talisman"] = 1
        player["carried_advanced_targets"] = {"craft_air_runes": True}
        player["carried_layout"] = {"craft_air_runes": {"Air talisman": 1, "Rune essence": 4}}
        self.assertTrue(_review(player))
        self.assertEqual(player["inventory"]["Air rune"], 4)
        self.assertEqual(player["carried_inventory"]["craft_air_runes"], {"Air talisman": 1})
