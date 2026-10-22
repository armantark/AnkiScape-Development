"""Saved drink drains render through the existing Stats current/base reader."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from tests import test_main_menu_widget as menu
from tests.bar_crawl.test_drink_review import review, started_player


@unittest.skipUnless(menu.HAS_AQT, "requires the offscreen Qt interpreter")
class TestDrinkStats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = menu.QApplication.instance() or menu.QApplication([])

    def setUp(self):
        self.dialogs = []

    def tearDown(self):
        for dialog in self.dialogs:
            dialog.close()
            dialog.deleteLater()
        menu.QApplication.sendPostedEvents(None, menu.QEvent.Type.DeferredDelete)

    def _open_after_review(self, stage):
        from ankiscape.ui import ui
        player = started_player(stage)
        ok, calls, _rng = review(player)
        self.assertTrue(ok)
        self.assertEqual(calls["saves"], 1)
        dialogs = self.dialogs

        class CapturingDialog(ui.QDialog):
            def exec(dialog):
                dialog.setAttribute(menu.Qt.WidgetAttribute.WA_DeleteOnClose, False)
                dialogs.append(dialog)
                return 0

        with patch.object(ui, "QDialog", CapturingDialog):
            ui.show_main_menu(
                player_data=player,
                current_skill="Mining",
                on_save_skill=lambda skill: None,
                on_set_ore=lambda ore: None,
                on_set_tree=lambda tree: None,
                on_set_bar=lambda bar: None,
                on_set_craft=lambda craft: None,
            )
        dialog = self.dialogs[-1]
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(3):
            menu.QApplication.processEvents()
        return dialog

    def _assert_pairs(self, dialog, expected):
        for skill, text in expected.items():
            with self.subTest(skill=skill):
                button = dialog.findChild(menu.QToolButton, f"statsSkillButton_{skill}")
                self.assertIsNotNone(button)
                self.assertEqual(button.text(), text)
                if skill == "defense":
                    self.assertIn("Defence", button.accessibleName())
        self.assertIsNone(dialog.findChild(menu.QToolButton, "statsSkillButton_defence"))

    def test_gutrot_stats_show_saved_current_and_earned_levels(self):
        self._assert_pairs(self._open_after_review(2), {
            "attack": "42 / 50", "defense": "43 / 50", "strength": "43 / 50",
            "smithing": "44 / 50", "mining": "50 / 50", "prayer": "50 / 50",
        })

    def test_olde_suspiciouse_stats_show_all_seven_saved_drains(self):
        self._assert_pairs(self._open_after_review(8), {
            "attack": "42 / 50", "defense": "43 / 50", "strength": "44 / 50",
            "smithing": "44 / 50", "mining": "44 / 50", "crafting": "44 / 50",
            "magic": "44 / 50", "prayer": "50 / 50",
        })
