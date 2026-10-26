from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_varrock_museum_landmark_card_routes_claims_and_kit(self) -> None:
        from ankiscape.logic.varrock_museum_logic import apply_varrock_museum_command_pure

        pd = _make_player_data()

        def museum_command(action_id, payload):
            updated, ok, info = apply_varrock_museum_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_varrock_museum_command=museum_command,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "varrock_museum"
        )
        self.assertEqual(
            item.parent().data(0, Qt.ItemDataRole.UserRole),
            "__utility_group__:landmarks",
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "varrockMuseumPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "varrockMuseumIcon").pixmap().isNull())
        self.assertIn("0/183 Kudos", panel.findChild(QLabel, "varrockMuseumSummary").text())

        route = panel.findChild(QComboBox, "varrockMuseumRouteCombo")
        route.setCurrentIndex(route.findData("cleaning"))
        QApplication.processEvents()
        self.assertEqual(pd["varrock_museum"]["route"], "cleaning")
        self.assertIn(
            "complete The Dig Site",
            panel.findChild(QLabel, "varrockMuseumNote").text(),
        )

        panel.findChild(QPushButton, "varrockMuseumKitButton").click()
        QApplication.processEvents()
        self.assertEqual(
            set(pd["inventory"]),
            {"Trowel", "Rock pick", "Specimen brush", "Leather gloves", "Leather boots"},
        )

        route.setCurrentIndex(route.findData("quiz"))
        QApplication.processEvents()
        panel.findChild(QPushButton, "varrockMuseumPrimaryButton").click()
        QApplication.processEvents()
        self.assertEqual(self._activity_start_calls[-1], "varrock_museum")
        dialog.close()
