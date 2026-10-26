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
    from tests.test_main_menu_widget import QApplication, QLabel, QProgressBar
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_tears_of_guthix_card_renders_the_view_flags_and_enters(self) -> None:
        """The panel must render the gates the view owns, never re-derive them."""
        from ankiscape.data.tears_of_guthix_data import (
            ORNATE_BOWL_CRAFTING_LEVEL,
            ORNATE_BOWL_MINING_LEVEL,
            ORNATE_BOWL_TOOL,
        )
        from ankiscape.logic.tears_of_guthix_logic import (
            default_tears_of_guthix_state_pure,
            tears_of_guthix_view_pure,
        )

        dialog = None
        try:
            pd = _make_player_data()
            pd["tears_of_guthix"] = default_tears_of_guthix_state_pure()
            pd["activity_session"] = {"active_id": ""}
            pd["quest_points"] = 44
            dialog = self._open(pd)
            activity_tree = self._open_activities(dialog)
            row = _utility_row(activity_tree, "tears_of_guthix")
            self.assertFalse(row.icon(0).isNull())
            activity_tree.setCurrentItem(row)
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()

            panel = _find_named_widget(dialog, "tearsOfGuthixPanel")
            icon = panel.findChild(QLabel, "tearsOfGuthixIcon")
            status = _find_named_label(dialog, "tearsOfGuthixStatusChip")
            summary = _find_named_label(dialog, "tearsOfGuthixSummary")
            ornate = _find_named_button(dialog, "tearsOfGuthixOrnateButton")
            primary = _find_named_button(dialog, "tearsOfGuthixPrimaryButton")
            leave = _find_named_button(dialog, "tearsOfGuthixLeaveButton")
            progress = panel.findChild(QProgressBar, "tearsOfGuthixProgress")

            self.assertIsNotNone(icon.pixmap())
            self.assertFalse(icon.pixmap().isNull())
            self.assertEqual(status.text(), "LOCKED")
            self.assertIn("Tears of Guthix quest", summary.text())
            view = tears_of_guthix_view_pure(pd)
            self.assertEqual(primary.isEnabled(), view["enter_enabled"])
            self.assertEqual(ornate.isEnabled(), view["craft_ornate_enabled"])
            self.assertFalse(primary.isEnabled())
            self.assertTrue(leave.isHidden())
            self.assertTrue(progress.isHidden())

            pd["quests"]["tears_of_guthix"] = {
                "started": True,
                "progress": 3,
                "completed": True,
            }
            pd["mining_level"] = ORNATE_BOWL_MINING_LEVEL
            pd["crafting_level"] = ORNATE_BOWL_CRAFTING_LEVEL
            pd["inventory"][ORNATE_BOWL_TOOL] = 1
            activity_tree.itemActivated.emit(row, 0)
            QApplication.processEvents()
            self.assertEqual(status.text(), "FIRST VISIT READY")
            self.assertTrue(primary.isEnabled())
            self.assertTrue(ornate.isEnabled())

            ornate.click()
            QApplication.processEvents()
            self.assertEqual(
                self._tears_of_guthix_calls[-1], ("craft_ornate_bowl", {})
            )
            self.assertTrue(pd["tears_of_guthix"]["ornate_bowl"])
            self.assertTrue(ornate.isHidden())

            primary.click()
            QApplication.processEvents()
            self.assertEqual(self._tears_of_guthix_calls[-1], ("enter", {}))
            self.assertTrue(pd["tears_of_guthix"]["active"])
            self.assertEqual(pd["current_utility"], "tears_of_guthix")
            self.assertEqual(status.text(), "0 TEARS")
            self.assertFalse(progress.isHidden())
            self.assertFalse(leave.isHidden())
        finally:
            if dialog is not None:
                dialog.deleteLater()
