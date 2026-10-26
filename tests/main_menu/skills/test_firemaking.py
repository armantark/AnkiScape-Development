from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_artisan_skill_list,
    _find_list_with_user_role,
    _make_player_data,
    _panel_title,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QPushButton, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_firemaking_is_selectable_and_shows_source_backed_target_list(self) -> None:
        pd = _make_player_data()
        pd["firemaking_level"] = 45
        pd["inventory"] = {"Logs": 2, "Oak logs": 1}
        pd["current_firemaking"] = "oak_logs"
        dialog = self._open(pd)
        artisan = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan"
        )
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fm_row = next(
            (i for i in range(skill_list.count()) if skill_list.item(i).text() == "Firemaking"),
            None,
        )
        self.assertIsNotNone(fm_row, "Firemaking is missing from the Artisan skill list")
        skill_list.setCurrentRow(fm_row)
        QApplication.processEvents()

        title = _panel_title(dialog)
        self.assertTrue(
            title.startswith("Firemaking"),
            f"panel did not switch to Firemaking; still shows {title!r}",
        )
        target_list = _find_list_with_user_role(dialog, "logs")
        logs_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "logs"
        )
        oak_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "oak_logs"
        )
        self.assertEqual(target_list.currentItem().data(Qt.ItemDataRole.UserRole), "oak_logs")
        self.assertIn("Base XP: 40", logs_row.toolTip())
        self.assertIn("Input: Logs x1 (you have 2)", logs_row.toolTip())
        self.assertIn("Output: Ashes x1", logs_row.toolTip())
        self.assertIn("Success chance:", logs_row.toolTip())
        self.assertNotIn("FiremakingData.kt", logs_row.toolTip())

        target_list.itemClicked.emit(logs_row)
        QApplication.processEvents()
        self.assertEqual(self._firemaking_calls[-1], "logs")
        self.assertTrue(oak_row.flags() & Qt.ItemFlag.ItemIsEnabled)

    def test_firemaking_locked_or_missing_material_rows_are_inert(self) -> None:
        pd = _make_player_data()
        pd["firemaking_level"] = 1
        pd["inventory"] = {"Logs": 1}
        dialog = self._open(pd)
        artisan = next(
            b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan"
        )
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fm_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Firemaking")
        skill_list.setCurrentRow(fm_row)
        QApplication.processEvents()
        target_list = _find_list_with_user_role(dialog, "oak_logs")
        oak_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "oak_logs"
        )

        self.assertFalse(oak_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Locked due to:", oak_row.toolTip())
        target_list.itemClicked.emit(oak_row)
        QApplication.processEvents()
        self.assertEqual(self._firemaking_calls, [])

    def test_firemaking_region_quest_locks_are_inert(self) -> None:
        pd = _make_player_data()
        pd["firemaking_level"] = 99
        pd["inventory"] = {"Arctic pine logs": 1}
        pd["current_firemaking"] = "arctic_pine_logs"
        dialog = self._open(pd)
        artisan = next(b for b in dialog.findChildren(QPushButton) if b.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        skill_list = _find_artisan_skill_list(dialog)
        fm_row = next(i for i in range(skill_list.count()) if skill_list.item(i).text() == "Firemaking")
        skill_list.setCurrentRow(fm_row)
        QApplication.processEvents()
        target_list = _find_list_with_user_role(dialog, "arctic_pine_logs")
        arctic_row = next(
            target_list.item(i) for i in range(target_list.count())
            if target_list.item(i).data(Qt.ItemDataRole.UserRole) == "arctic_pine_logs"
        )

        self.assertFalse(arctic_row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("The Fremennik Isles", arctic_row.toolTip())
        target_list.itemClicked.emit(arctic_row)
        QApplication.processEvents()
        self.assertEqual(self._firemaking_calls, [])

        pd["quests"]["the_fremennik_isles"] = {"started": True, "progress": 6, "completed": True}
        unlocked_dialog = self._open(pd)
        artisan = next(b for b in unlocked_dialog.findChildren(QPushButton) if b.text() == "Artisan")
        artisan.click()
        QApplication.processEvents()
        unlocked_skill_list = _find_artisan_skill_list(unlocked_dialog)
        unlocked_fm_row = next(i for i in range(unlocked_skill_list.count()) if unlocked_skill_list.item(i).text() == "Firemaking")
        unlocked_skill_list.setCurrentRow(unlocked_fm_row)
        QApplication.processEvents()
        unlocked_list = _find_list_with_user_role(unlocked_dialog, "arctic_pine_logs")
        unlocked_arctic = next(
            unlocked_list.item(i) for i in range(unlocked_list.count())
            if unlocked_list.item(i).data(Qt.ItemDataRole.UserRole) == "arctic_pine_logs"
        )
        self.assertTrue(unlocked_arctic.flags() & Qt.ItemFlag.ItemIsEnabled)
