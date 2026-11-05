"""The real review strip exposes pickup only for ammunition weapons."""

import unittest

from tests import test_review_strip as strip_fixtures


@unittest.skipUnless(strip_fixtures.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class AmmunitionHudTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        strip_fixtures.ReviewStripTest.setUpClass()

    def setUp(self):
        self.strip = strip_fixtures.ReviewStripTest()
        self.strip.setUp()
        self.addCleanup(self.strip.tearDown)
        self.ui = self.strip.ui

    def test_ammo_pickup_only_shows_for_weapons_that_use_ammo_and_click_refreshes(self):
        state = self.strip._state()
        state.update(ground_ammunition_tick=0, ground_ammunition=[{"name": "Bronze arrows", "count": 42, "expires_at": 350}])
        self.ui.update_review_hud(state, "Combat")
        from ankiscape.logic_pure.combat.ammunition import pickup_ground_ammo_pure
        clicks = []

        def pickup():
            updated, ok = pickup_ground_ammo_pure(state)
            self.assertTrue(ok)
            state.update(updated)
            clicks.append(True)
            self.ui.update_review_bank_run_button(state, "combat", ammo_pickup_action=pickup)
        for weapon in ("Iron sword", "Staff", "Crystal bow"):
            with self.subTest(weapon=weapon):
                state["equipment"] = {"weapon": weapon}
                self.ui.update_review_bank_run_button(state, "combat", ammo_pickup_action=pickup)
                self.assertTrue(self.ui._REVIEW_HUD.ammo_pickup_button.isHidden())
        state["equipment"] = {"weapon": "Shortbow", "ammunition": "Bronze arrows"}
        state["equipment_ammunition_count"] = 7
        self.ui.update_review_bank_run_button(state, "combat", ammo_pickup_action=pickup)
        button = self.ui._REVIEW_HUD.ammo_pickup_button
        self.assertFalse(button.isHidden())
        self.assertTrue(button.isEnabled())
        self.assertEqual(button.text(), "Pick up ammo (42)")
        button.click()
        self.assertEqual(clicks, [True])
        self.assertEqual(state["equipment_ammunition_count"], 49)
        self.assertEqual(button.text(), "Pick up ammo (0)")
        self.assertFalse(button.isEnabled())
        self.assertFalse(button.isHidden())
