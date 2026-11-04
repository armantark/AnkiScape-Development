"""The real menu and Review HUD expose queue notices without clipped text."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from tests.main_menu import fixtures
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _goto_smithing, _find_smith_tree, _smith_row

if HAS_AQT:
    from aqt.qt import QApplication, QMainWindow, QMessageBox, QPushButton
    from tests.ui_flows.qt_text_fit import text_fit_defects


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class QueueNoticeWidgetTest(fixtures.MainMenuWidgetTest):
    def test_wilderness_add_confirms_the_current_kept_and_lost_preview(self):
        from tests.action_queue.test_queue_notices import _WILD

        player = _make_player_data()
        player["equipment"] = {"weapon": "Bronze sword"}
        with patch.object(self._ui.QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as question:
            self.assertFalse(self._ui.confirm_wilderness_queue_action(player, _WILD))
        self.assertEqual(question.call_args.args[1], "Confirm Wilderness combat")
        self.assertIn("Kept: Bronze sword.", question.call_args.args[2])
        self.assertIn("Lost: nothing.", question.call_args.args[2])
        with patch.object(self._ui.QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
            self.assertTrue(self._ui.confirm_wilderness_queue_action(player, _WILD))
        with patch.object(self._ui.QMessageBox, "question") as question:
            self.assertTrue(self._ui.confirm_wilderness_queue_action(player, _WILD))
        question.assert_not_called()

    def test_review_hud_shows_the_notice_in_full(self):
        from ankiscape.core.review_event_log import record_review_event_pure

        parent = QMainWindow()
        parent.show()
        parent.resize(900, 560)
        hud = self._ui.ReviewHUD(parent)
        player = _make_player_data()
        text = "Pirate's Treasure complete. Next: Mining. An XP lamp (10,000 XP) is waiting in Bank Claims."
        player = record_review_event_pure(player, "queue", text)
        hud.set_data(player, "Mining")
        for _pass in range(5):
            QApplication.processEvents()
        self.assertEqual(hud.world_notice_lbl.text(), text)
        self.assertTrue(hud.world_notice_lbl.isVisible())
        self.assertEqual(text_fit_defects(hud), [])

    def test_a_same_surface_takeover_rebuilds_the_selected_recipe(self):
        player = _make_player_data()
        player.update(current_smith="smelt_iron_bar", smithing_level=40, inventory={"Iron ore": 5, "Iron bar": 5})

        def command(_name, payload):
            player["current_smith"] = payload["action"]["target"]
            return {"ok": True, "active": "Smithing", "message": ""}

        player["action_queue"] = {"entries": [{"action": {"kind": "skill", "skill": "Smithing", "target": "smelt_iron_bar"}, "count": 5}]}
        dialog = self._open(player, current_skill="Smithing", on_action_queue_command=command)
        dialog.show()
        dialog.resize(900, 560)
        QApplication.processEvents()
        _goto_smithing(dialog)
        tree = _find_smith_tree(dialog)
        item = _smith_row(tree, "forge_iron_platebody")
        tree.itemClicked.emit(item, 0)
        add = next(button for button in dialog.findChildren(QPushButton, "queueAddButton") if button.isVisible())
        add.click()
        QApplication.processEvents()
        current = _find_smith_tree(dialog).currentItem()
        self.assertIn("Iron platebody", current.text(0))
