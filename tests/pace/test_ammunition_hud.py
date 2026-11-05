"""The real review strip exposes pickup only for ammunition weapons."""

import unittest
from itertools import product

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

    def test_combat_title_fits_with_and_without_pickup_at_laptop_size(self):
        from aqt.qt import QApplication, QColor, QFont, QPalette

        app = self.strip.app
        original_font, original_palette = app.font(), app.palette()
        original_style = app.style().objectName()
        self.addCleanup(app.setFont, original_font)
        self.addCleanup(app.setPalette, original_palette)
        self.addCleanup(app.setStyle, original_style)
        app.setStyle("Fusion")
        # A larger Mac font exposes compression that offscreen's small
        # default font hides inside the fixed-height reviewer strip.
        app.setFont(QFont("Helvetica Neue", 13))
        state = self.strip._state()
        for skill in ("attack", "strength", "defense", "ranged", "magic", "constitution"):
            state[skill + "_level"] = 45
        state.update(combat_lifepoints=450, current_combat_target="chicken")
        themes = (("light", "#f0f0f0", "#101010"), ("dark", "#202020", "#f0f0f0"))
        sizes = ((1000, 700), (667, 602), (720, 560))
        for (theme, background, text), (width, height), weapon, count in product(themes, sizes, ("Shortbow", "Iron sword"), (0, 42)):
            palette = app.style().standardPalette()
            for role in (QPalette.ColorRole.Window, QPalette.ColorRole.Base, QPalette.ColorRole.Button):
                palette.setColor(role, QColor(background))
            for role in (QPalette.ColorRole.WindowText, QPalette.ColorRole.Text, QPalette.ColorRole.ButtonText):
                palette.setColor(role, QColor(text))
            app.setPalette(palette)
            with self.subTest(theme=theme, size=(width, height), weapon=weapon, count=count):
                state["equipment"] = {"weapon": weapon}
                state["ground_ammunition"] = [{"name": "Bronze arrows", "count": count, "expires_at": 350}]
                self.ui.update_review_hud(state, "Combat")
                self.ui.update_review_status_badge(state)
                self.ui.update_review_bank_run_button(state, "combat", ammo_pickup_action=lambda: None)
                self.strip.parent.show()
                self.strip.parent.resize(width, height)
                for _ in range(5):
                    QApplication.processEvents()
                hud = self.ui._REVIEW_HUD
                title, button = hud.title_lbl, hud.ammo_pickup_button
                self.assertTrue(hud.isVisible())
                self.assertEqual(title.text(), "Combat — Lv 51")
                self.assertGreaterEqual(title.height(), title.sizeHint().height())
                self.assertGreaterEqual(title.height(), title.fontMetrics().height())
                self.assertGreaterEqual(title.width(), title.sizeHint().width())
                self.assertTrue(hud.rect().contains(title.geometry()))
                self.assertLess(title.geometry().bottom(), hud.progress.y())
                self.assertEqual(hud.height(), self.ui.REVIEW_STRIP_HEIGHT)
                self.assertEqual(button.isVisible(), weapon == "Shortbow")
                if button.isVisible():
                    self.assertEqual(button.text(), f"Pick up ammo ({count})")
                    self.assertFalse(title.geometry().intersects(button.geometry()))
                    self.assertLess(title.geometry().bottom(), button.y())
                    self.assertTrue(hud.rect().contains(button.geometry()))
                    bank = self.ui._BANK_RUN_BUTTON
                    self.assertFalse(button.geometry().intersects(bank.geometry()))
                    self.assertLess(button.geometry().right(), bank.x())
                    self.assertLessEqual(button.y(), bank.geometry().bottom())
                    self.assertLessEqual(bank.y(), button.geometry().bottom())

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
