from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_a_higher_tier_clue_shows_a_reason_instead_of_doing_nothing(self) -> None:
        from ankiscape.logic.treasure_trails_logic import (
            default_treasure_trails_state_pure,
        )

        pd = _make_player_data()
        pd.update(default_treasure_trails_state_pure())
        pd["inventory"] = {"Clue scroll (hard)": 1}
        pd["equipment"] = {}
        pd["activity_session"] = {"active_id": ""}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_treasure_trails_command=lambda *_args: {"ok": True},
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "treasure_trail"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "treasureTrailsPanel")
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QPushButton, "treasureTrailsPrimary").isEnabled()
        )
        self.assertIn(
            "not built yet", panel.findChild(QLabel, "treasureTrailsStep").text()
        )
        self.assertIn(
            "already have a clue scroll",
            panel.findChild(QLabel, "treasureTrailsSummary").text(),
        )
        dialog.close()
