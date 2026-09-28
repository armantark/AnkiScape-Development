"""Offscreen Qt coverage for Slayer assignment progress in the review HUD."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu
from tests import test_review_strip as _review_strip

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QPoint, QRect


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


@unittest.skipUnless(
    _review_strip.HAS_AQT,
    "aqt/PyQt6 not installed (use .venv-qt)",
)
class SlayerProgressTextFitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _review_strip.ReviewStripTest.setUpClass()

    def setUp(self) -> None:
        self.strip = _review_strip.ReviewStripTest(methodName="runTest")
        self.strip.setUp()

    def tearDown(self) -> None:
        self.strip.tearDown()

    def test_combat_hud_keeps_every_text_whole_in_the_strip_at_both_parent_sizes(
        self,
    ) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        ui = self.strip.ui
        player = self.strip._state()
        player.update(
            {
                "current_combat_target": "black_bear",
                "combat_action": "attack",
                "combat_attack_style": "aggressive",
                "combat_attack_style_type": "crush",
                "attack_level": 31,
                "strength_level": 26,
                "defense_level": 21,
                "constitution_level": 28,
                "combat_lifepoints": 280,
                "combat_kill_counts": {"black_bear": 13},
                "slayer_assignment": {
                    "master_id": "turael_spria",
                    "family_id": "bears",
                    "initial_count": 17,
                    "remaining": 4,
                },
            }
        )
        ui.update_review_hud(player, "Combat")
        hud = ui._REVIEW_HUD
        hud.show()
        for parent_size in ((1000, 700), (900, 560)):
            with self.subTest(parent_size=parent_size):
                self.strip.parent.resize(*parent_size)
                for _ in range(4):
                    QApplication.processEvents()
                self.assertEqual(hud.slayer_lbl.text(), "Slayer: 4 of 17 left")
                self.assertTrue(hud.slayer_lbl.isVisible())
                for container in (self.strip.parent, ui._REVIEW_STRIP):
                    self.assertTrue(
                        container.rect().contains(
                            QRect(hud.mapTo(container, QPoint(0, 0)), hud.size())
                        )
                    )
                self.assertEqual(text_fit_defects(hud), [])
