"""Offscreen Qt coverage for the Slayer Masters tab and the master that the
Assignment tab's Get assignment button asks, at the owner's 720x560 dialog."""

import unittest

import pkg_alias  # noqa: F401
from tests import test_main_menu_widget as _main_menu

if _main_menu.HAS_AQT:
    from aqt.qt import QApplication, QGraphicsColorizeEffect, QLabel, QPushButton, QTabWidget, QWidget

    from tests.ui_flows.qt_text_fit import text_fit_defects

_OWNER_SIZE = (720, 560)
_ROSTER = ("turael_spria", "mazchna_achtryn", "vannaka")


def _pump() -> None:
    for _ in range(6):
        QApplication.processEvents()


@unittest.skipUnless(_main_menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class SlayerMasterPickerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _open_tab(self, data, index):
        dialog = self.menu._open(data, current_skill="Mining")
        dialog.show()
        dialog.resize(*_OWNER_SIZE)
        _pump()
        self.menu._goto_slayer(dialog)
        tabs = dialog.findChild(QTabWidget, "slayerManagementTabs")
        tabs.setCurrentIndex(index)
        _pump()
        return dialog, tabs

    def _card(self, dialog, master_id):
        return dialog.findChild(QWidget, f"slayerMaster_{master_id}")

    def _card_texts(self, card) -> list:
        return [label.text() for label in card.findChildren(QLabel) if label.text()]

    def test_masters_tab_lists_every_live_master_and_greys_unmet_combat_levels(self) -> None:
        # The fixture player is combat level 26: Mazchna is open, Vannaka is not.
        dialog, tabs = self._open_tab(_main_menu._make_player_data(), 1)
        masters = tabs.currentWidget()
        cards = [
            widget.objectName().removeprefix("slayerMaster_")
            for widget in masters.findChildren(QWidget)
            if widget.objectName().startswith("slayerMaster_")
        ]
        self.assertEqual(tuple(cards), _ROSTER)
        for master_id, name in zip(_ROSTER, ("Turael", "Mazchna", "Vannaka")):
            card = self._card(dialog, master_id)
            self.assertEqual(card.findChild(QLabel, "slayerMasterName").text(), name)
            chathead = card.findChild(QLabel, "slayerMasterChathead").pixmap()
            self.assertFalse(chathead is None or chathead.isNull(), name)
        mazchna = self._card(dialog, "mazchna_achtryn")
        self.assertTrue(mazchna.findChild(QPushButton).isEnabled())
        self.assertIsNone(mazchna.findChild(QLabel, "slayerMasterLockedReasons"))
        vannaka = self._card(dialog, "vannaka")
        self.assertFalse(vannaka.findChild(QPushButton).isEnabled())
        opacity = vannaka.findChild(QLabel, "slayerMasterChathead").graphicsEffect()
        self.assertIsInstance(opacity, QGraphicsColorizeEffect)
        self.assertEqual(opacity.strength(), 1)
        self.assertIn("Assignment range: 10–70 creatures", "\n".join(self._card_texts(mazchna)))
        self.assertIn("No Slayer points", "\n".join(self._card_texts(self._card(dialog, "turael_spria"))))
        self.assertEqual(
            vannaka.findChild(QLabel, "slayerMasterLockedReasons").text(),
            "Requires: Combat level 40",
        )
        self.assertFalse(
            any("More masters unlock" in text for text in self._card_texts(masters))
        )
        self.assertEqual(text_fit_defects(masters), [])

        mazchna.findChild(QPushButton).click()
        _pump()
        self.assertEqual(
            self.menu._slayer_command_calls[-1],
            ("get_assignment", {"master_id": "mazchna_achtryn"}),
        )
        progress = dialog.findChild(QLabel, "slayerAssignmentProgress")
        self.assertIn("assigned by Mazchna", progress.text())

    def test_below_combat_20_mazchna_is_greyed_with_its_reason(self) -> None:
        data = _main_menu._make_player_data()
        data.update(magic_level=1, prayer_level=1, summoning_level=1)
        dialog, tabs = self._open_tab(data, 1)

        mazchna = self._card(dialog, "mazchna_achtryn")
        self.assertFalse(mazchna.findChild(QPushButton).isEnabled())
        self.assertEqual(
            mazchna.findChild(QLabel, "slayerMasterLockedReasons").text(),
            "Requires: Combat level 20",
        )
        self.assertTrue(self._card(dialog, "turael_spria").findChild(QPushButton).isEnabled())
        self.assertEqual(text_fit_defects(tabs.currentWidget()), [])

    def test_assignment_and_rewards_follow_the_view_after_state_sanitization(self) -> None:
        data = _main_menu._make_player_data()
        data["slayer_assignment"] = {"master_id": "mazchna_achtryn", "family_id": "bats", "remaining": 12, "initial_count": 40}
        data["quests"]["smoking_kills"] = {"completed": True}
        data["slayer_points"] = 25
        dialog, tabs = self._open_tab(data, 0)
        self.assertIsNotNone(dialog.findChild(QWidget, "slayerActiveAssignmentCard"))
        self.assertIsNone(dialog.findChild(QLabel, "slayerAssignmentEmptyState"))
        tabs.setCurrentIndex(2)
        _pump()
        self.assertEqual(dialog.findChild(QLabel, "slayerPointsBalance").text(), "Slayer points: 25")
        self.assertIsNone(dialog.findChild(QLabel, "slayerRewardsSmokingKillsLock"))

    def test_get_assignment_asks_the_last_eligible_master(self) -> None:
        for magic, expected_id, expected_text in (
            (33, "mazchna_achtryn", "Ask Mazchna for a new task."),
            (1, "turael_spria", "Ask Turael for a beginner task"),
        ):
            with self.subTest(magic=magic):
                data = _main_menu._make_player_data()
                data.update(magic_level=magic, prayer_level=magic, summoning_level=magic)
                data["slayer_assignment"] = {
                    "master_id": "mazchna_achtryn",
                    "family_id": "bats",
                    "initial_count": 40,
                    "remaining": 0,
                }
                dialog, tabs = self._open_tab(data, 0)

                empty = dialog.findChild(QLabel, "slayerAssignmentEmptyState")
                self.assertIn(expected_text, empty.text())
                self.assertEqual(text_fit_defects(tabs.currentWidget()), [])
                dialog.findChild(QPushButton, "slayerGetAssignmentButton").click()
                _pump()
                self.assertEqual(
                    self.menu._slayer_command_calls[-1],
                    ("get_assignment", {"master_id": expected_id}),
                )


if __name__ == "__main__":
    unittest.main()
