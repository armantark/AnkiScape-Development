import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

try:
    from aqt.qt import QApplication, QDialog, QMainWindow, QMessageBox, QTimer

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False

import pkg_alias  # noqa: F401


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class DialogLifecycleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        from ankiscape.ui import ui

        self.ui = ui
        self.parent = QMainWindow()
        self.parent.show()
        self.parent.resize(900, 560)
        for _ in range(4):
            QApplication.processEvents()
        self.old_mw = ui.mw
        self.old_dialog = ui.QDialog
        self.old_message_box = ui.QMessageBox
        self.held = []
        held = self.held

        class CapturingDialog(QDialog):
            def __init__(instance, *args, **kwargs):
                super().__init__(*args, **kwargs)
                held.append(instance)

        class CapturingMessageBox(QMessageBox):
            def __init__(instance, *args, **kwargs):
                super().__init__(*args, **kwargs)
                held.append(instance)

        ui.mw = self.parent
        ui.QDialog = CapturingDialog
        ui.QMessageBox = CapturingMessageBox

    def tearDown(self) -> None:
        self.ui.mw = self.old_mw
        self.ui.QDialog = self.old_dialog
        self.ui.QMessageBox = self.old_message_box
        self.parent.hide()
        self.parent.deleteLater()
        for _ in range(4):
            QApplication.processEvents()

    @staticmethod
    def _close_modal() -> None:
        modal = QApplication.activeModalWidget()
        if modal is not None:
            modal.close()

    def _assert_deleted_on_close(self, open_dialog) -> None:
        start = len(self.held)
        QTimer.singleShot(0, self._close_modal)
        open_dialog()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(len(self.held), start + 1)
        with self.assertRaises(RuntimeError):
            self.held[-1].objectName()

    def test_selection_is_captured_before_the_dialog_is_destroyed(self):
        QTimer.singleShot(
            0,
            lambda: QApplication.activeModalWidget().accept(),
        )
        selected = self.ui.show_skill_selection_dialog("Mining", True)
        for _ in range(4):
            QApplication.processEvents()

        self.assertEqual(selected, "Mining")
        with self.assertRaises(RuntimeError):
            self.held[-1].objectName()

    def test_xp_lamp_chooser_returns_the_confirmed_stable_skill_id(self):
        captured = {}

        def _select_and_confirm() -> None:
            modal = QApplication.activeModalWidget()
            self.assertIsNotNone(modal)
            title = modal.findChild(
                self.ui.QLabel,
                "xpLampSkillChooserTitle",
            )
            captured["title"] = title.text()
            captured["title_width"] = title.width()
            captured["minimum_width"] = modal.minimumWidth()
            attack = next(
                button
                for button in modal.findChildren(
                    self.ui.QToolButton,
                    "xpLampSkillButton",
                )
                if button.property("skillId") == "attack"
            )
            claim = modal.findChild(
                self.ui.QPushButton,
                "xpLampClaimButton",
            )
            captured["claim_initially_enabled"] = claim.isEnabled()
            attack.click()
            claim.click()

        QTimer.singleShot(0, _select_and_confirm)
        selected = self.ui._choose_xp_lamp_skill(
            self.parent,
            "Stronghold of Player Safety: Antique lamp 1 (500 XP)",
            ("attack", "agility"),
        )
        for _ in range(4):
            QApplication.processEvents()

        self.assertEqual(selected, "attack")
        self.assertEqual(
            captured["title"],
            "Stronghold of Player Safety: Antique lamp 1 (500 XP)",
        )
        self.assertEqual(captured["minimum_width"], 600)
        self.assertGreater(captured["title_width"], 188)
        self.assertFalse(captured["claim_initially_enabled"])
        with self.assertRaises(RuntimeError):
            self.held[-1].objectName()

    def test_xp_lamp_chooser_cancel_returns_none_and_deletes_the_dialog(self):
        def _cancel() -> None:
            modal = QApplication.activeModalWidget()
            self.assertIsNotNone(modal)
            modal.findChild(
                self.ui.QPushButton,
                "xpLampCancelButton",
            ).click()

        QTimer.singleShot(0, _cancel)
        selected = self.ui._choose_xp_lamp_skill(
            self.parent,
            "Claim XP lamp",
            ("attack", "agility"),
        )
        for _ in range(4):
            QApplication.processEvents()

        self.assertIsNone(selected)
        with self.assertRaises(RuntimeError):
            self.held[-1].objectName()

    def test_parented_dialogs_destroy_their_qt_objects_on_close(self):
        cases = (
            lambda: self.ui.show_level_up_dialog("Mining", 32, 33),
            lambda: self.ui.show_achievement_dialog(
                "First Ore", {"description": "Mine one ore."}
            ),
            lambda: self.ui.show_error_message("Unavailable", "Try again."),
            self.ui.show_stronghold_reward_dialog,
            lambda: self.ui.show_tree_selection_dialog("", 1, {}, {}),
            lambda: self.ui.show_ore_selection_dialog("", 1, {}, {}),
            lambda: self.ui.show_bar_selection_dialog("", 1, {}, {}),
            lambda: self.ui.show_craft_selection_dialog("", 1, {}, {}, {}),
            lambda: self.ui.show_skill_selection_dialog("None", False),
            lambda: self.ui.show_stats({}, "None"),
        )
        for open_dialog in cases:
            with self.subTest(open_dialog=open_dialog):
                self._assert_deleted_on_close(open_dialog)
        self.assertEqual(len(self.held), len(cases))

    def test_level_up_dialog_names_the_exact_level_transition(self) -> None:
        captured = {}

        def _capture_and_close() -> None:
            modal = QApplication.activeModalWidget()
            if modal is None:
                return
            captured["message"] = modal.findChild(
                self.ui.QLabel,
                "levelUpMessage",
            ).text()
            captured["transition"] = modal.findChild(
                self.ui.QLabel,
                "levelUpTransition",
            ).text()
            modal.accept()

        QTimer.singleShot(0, _capture_and_close)
        self.ui.show_level_up_dialog("Attack", 8, 9)

        self.assertEqual(captured["message"], "Your Attack level increased.")
        self.assertEqual(captured["transition"], "Level 8 → 9")

    def test_combat_level_popup_uses_the_shared_level_up_dialog(self) -> None:
        captured = {}

        def _capture_and_close() -> None:
            modal = QApplication.activeModalWidget()
            if modal is None:
                return
            captured["message"] = modal.findChild(
                self.ui.QLabel,
                "levelUpMessage",
            ).text()
            captured["transition"] = modal.findChild(
                self.ui.QLabel,
                "levelUpTransition",
            ).text()
            modal.accept()

        QTimer.singleShot(0, _capture_and_close)
        self.ui.show_level_up_dialog("Combat", 3, 4)

        self.assertEqual(captured["message"], "Your Combat level increased.")
        self.assertEqual(captured["transition"], "Level 3 → 4")


if __name__ == "__main__":
    unittest.main()
