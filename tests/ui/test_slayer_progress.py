"""Offscreen Qt coverage for Slayer assignment progress in the review HUD."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication


@unittest.skipUnless(
    _main_menu.HAS_AQT,
    "aqt/PyQt6 not installed (use .venv-qt)",
)
class SlayerProgressWidgetTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_hud_reads_slayer_assignment_and_hides_it_when_combat_or_task_ends(
        self,
    ) -> None:
        player = _main_menu._make_player_data()
        player["slayer_assignment"] = {
            "master_id": "turael_spria",
            "family_id": "bears",
            "initial_count": 17,
            "remaining": 4,
        }
        hud = self.menu._ui.ReviewHUD(None)
        self.addCleanup(hud.close)
        hud.set_data(player, "Combat")
        QApplication.processEvents()
        self.assertEqual(hud.slayer_lbl.text(), "Slayer: 4 of 17 left")
        self.assertTrue(hud.slayer_lbl.isVisible())
        self.assertGreaterEqual(
            hud.slayer_lbl.y(),
            hud.chips_lbl.y() + hud.chips_lbl.height(),
        )

        hud.set_data(player, "Mining")
        self.assertFalse(hud.slayer_lbl.isVisible())
        hud.set_data(player, "Combat")
        self.assertTrue(hud.slayer_lbl.isVisible())
        player["slayer_assignment"]["remaining"] = 0
        hud.set_data(player, "Combat")
        self.assertFalse(hud.slayer_lbl.isVisible())
        player["slayer_assignment"] = {}
        hud.set_data(player, "Combat")
        self.assertFalse(hud.slayer_lbl.isVisible())
