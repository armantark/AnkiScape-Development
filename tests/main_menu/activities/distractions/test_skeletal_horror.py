from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _utility_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QColor, QLabel, QPalette, QProgressBar, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_skeletal_horror_card_unlocks_enters_and_fits_a_dark_laptop_view(self) -> None:
        from ankiscape.logic.skeletal_horror_logic import (
            default_skeletal_horror_state_pure,
        )

        original_palette = QApplication.palette()
        original_style = QApplication.style().objectName()
        dark = QPalette(original_palette)
        dark.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
        dark.setColor(QPalette.ColorRole.WindowText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
        dark.setColor(QPalette.ColorRole.Text, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
        dark.setColor(QPalette.ColorRole.ButtonText, QColor(235, 235, 235))
        dark.setColor(QPalette.ColorRole.Mid, QColor(95, 95, 95))
        QApplication.setStyle("Fusion")
        QApplication.setPalette(dark)
        dialog = None
        try:
            pd = _make_player_data()
            pd["skeletal_horror"] = default_skeletal_horror_state_pure()
            pd["activity_session"] = {"active_id": ""}
            pd["combat_encounter"] = {}
            for quest_id in ("rag_and_bone_man", "fur_n_seek"):
                pd["quests"][quest_id] = {
                    "started": True,
                    "progress": 1,
                    "completed": True,
                }
            pd["slayer_level"] = 99
            dialog = self._open(pd)
            dialog.show()
            dialog.resize(900, 560)
            for _ in range(4):
                QApplication.processEvents()

            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "skeletal_horror")
            self.assertFalse(row.icon(0).isNull())
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            panel = _find_named_widget(dialog, "skeletalHorrorPanel")
            icon = panel.findChild(QLabel, "skeletalHorrorIcon")
            status = _find_named_label(dialog, "skeletalHorrorStatusChip")
            summary = _find_named_label(dialog, "skeletalHorrorSummary")
            rag_wish = _find_named_button(
                dialog, "skeletalHorrorRagWishButton"
            )
            fur_wish = _find_named_button(
                dialog, "skeletalHorrorFurWishButton"
            )
            primary = _find_named_button(
                dialog, "skeletalHorrorPrimaryButton"
            )
            leave = _find_named_button(dialog, "skeletalHorrorLeaveButton")
            progress = panel.findChild(QProgressBar, "skeletalHorrorProgress")
            self.assertIsNone(panel.findChild(QScrollArea))
            self.assertIsNotNone(icon.pixmap())
            self.assertFalse(icon.pixmap().isNull())
            self.assertEqual(status.text(), "LOCKED")
            self.assertIn("wish list", summary.text())
            self.assertTrue(rag_wish.isEnabled())
            self.assertTrue(fur_wish.isEnabled())

            rag_wish.click()
            fur_wish.click()
            QApplication.processEvents()
            self.assertEqual(
                [call[0] for call in self._skeletal_horror_calls[-2:]],
                ["complete_rag_wish_list", "complete_fur_wish_list"],
            )
            self.assertEqual(status.text(), "FIRST FIGHT READY")

            primary.click()
            QApplication.processEvents()
            self.assertEqual(self._skeletal_horror_calls[-1], ("enter", {}))
            self.assertTrue(pd["skeletal_horror"]["active"])
            self.assertEqual(pd["current_utility"], "skeletal_horror")
            self.assertEqual(status.text(), "LEVEL 320")
            self.assertEqual(progress.value(), 3500)
            self.assertFalse(leave.isHidden())
            self.assertLessEqual(
                panel.mapTo(dialog, panel.rect().bottomRight()).y(),
                dialog.contentsRect().bottom(),
            )
        finally:
            if dialog is not None:
                dialog.deleteLater()
            QApplication.setPalette(original_palette)
            QApplication.setStyle(original_style)

    def test_skeletal_horror_wish_list_buttons_follow_the_view_not_a_panel_rule(
        self,
    ) -> None:
        """The panel must render the gate the logic layer owns, never re-derive
        it; a panel-side copy of the Slayer wall drifts without any test
        noticing."""
        from ankiscape.data.skeletal_horror_data import (
            SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL,
        )
        from ankiscape.logic.skeletal_horror_logic import (
            default_skeletal_horror_state_pure,
            skeletal_horror_view_pure,
        )

        dialog = None
        try:
            pd = _make_player_data()
            pd["skeletal_horror"] = default_skeletal_horror_state_pure()
            pd["activity_session"] = {"active_id": ""}
            for quest_id in ("rag_and_bone_man", "fur_n_seek"):
                pd["quests"][quest_id] = {
                    "started": True,
                    "progress": 1,
                    "completed": True,
                }
            pd["slayer_level"] = SKELETAL_HORROR_FUR_WISH_LIST_SLAYER_LEVEL - 1
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "skeletal_horror")
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            rag_wish = _find_named_button(dialog, "skeletalHorrorRagWishButton")
            fur_wish = _find_named_button(dialog, "skeletalHorrorFurWishButton")
            view = skeletal_horror_view_pure(pd)
            self.assertEqual(rag_wish.isEnabled(), view["rag_wish_list_ready"])
            self.assertEqual(fur_wish.isEnabled(), view["fur_wish_list_ready"])
            self.assertTrue(rag_wish.isEnabled())
            self.assertFalse(fur_wish.isEnabled())
        finally:
            if dialog is not None:
                dialog.deleteLater()
