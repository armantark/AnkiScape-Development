"""Up and Down on the queue box's rows: the real menu widgets on the add-on's real queue command."""

from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMELT_IRON, _SMITH_PLATEBODY, QueueProfile
from tests.main_menu import fixtures
from tests.test_main_menu_widget import HAS_AQT

if HAS_AQT:
    from aqt.qt import QLabel, QMessageBox, QPushButton, QScrollBar, QWidget
    from tests.test_main_menu_widget import QApplication
    from tests.ui_flows.qt_text_fit import text_fit_defects

_REAL_QT_MODULES = ("aqt", "aqt.qt", "aqt.reviewer", "anki.hooks")
_PICKUP = {"kind": "utility", "utility_id": "pick_onions"}


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class QueueRowMoveWidgetTest(fixtures.MainMenuWidgetTest):
    def _played(self, name, *entries):
        """A real add-on on a fake Anki, whose queue command the real menu widgets call."""
        real_qt = {module: sys.modules.get(module) for module in _REAL_QT_MODULES}
        self.profile = QueueProfile()
        self.profile.setUp()
        self.addCleanup(self.profile.tearDown)
        addon = self.profile._queue_addon(name, *entries)
        sys.modules.update({module: loaded for module, loaded in real_qt.items() if loaded is not None})
        return addon

    def _menu(self, addon, size=(900, 560)):
        from ankiscape.ui.ui_action_queue import notify_action_queue_changed

        def command(name, payload):
            result = addon.apply_action_queue_command(addon, name, payload)
            notify_action_queue_changed()
            return result

        dialog = self._open(addon._state.player_data, current_skill=addon._state.current_skill, on_action_queue_command=command)
        dialog.show()
        dialog.resize(*size)
        for _pass in range(4):
            QApplication.processEvents()
        return dialog

    def _rows(self, dialog):
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        return [label.text() for label in panel.findChildren(QLabel, "actionQueueRowText") if label.isVisibleTo(panel)]

    def _moves(self, dialog, name):
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        return [button for button in panel.findChildren(QPushButton, name) if button.isVisibleTo(panel)]

    def _enabled(self, dialog, name):
        return [button.isEnabled() for button in self._moves(dialog, name)]

    def _click(self, dialog, name, row):
        self._moves(dialog, name)[row].click()
        QApplication.processEvents()

    def test_clicks_move_rows_and_the_top_click_changes_what_the_next_card_runs(self):
        addon = self._played("ankiscape_move_widget", (_MINE_IRON, 30), (_SMELT_IRON, 5), (_SMITH_PLATEBODY, 1))
        with patch.object(addon.random, "random", lambda: 0.5):
            self.profile._answer(addon)
        dialog = self._menu(addon)
        mining, smelt, platebody = (
            "Mining: Iron · 10 / 30 Iron ore", "Smithing: Iron bar · 0 / 5 Iron bar", "Smithing: Iron platebody · 0 / 1 Iron platebody"
        )
        self.assertEqual(self._rows(dialog), [mining, smelt, platebody])
        self.assertEqual(self._enabled(dialog, "actionQueueMoveUp"), [False, True, True])
        self.assertEqual(self._enabled(dialog, "actionQueueMoveDown"), [True, True, False])

        self._click(dialog, "actionQueueMoveDown", 1)
        self.assertEqual(self._rows(dialog), [mining, platebody, smelt])
        self.assertEqual(addon._state.current_skill, "Mining")

        self._click(dialog, "actionQueueMoveUp", 2)
        self._click(dialog, "actionQueueMoveUp", 1)
        self.assertEqual(self._rows(dialog), [smelt, "Mining: Iron · 0 / 20 Iron ore", platebody])
        self.assertEqual(addon._state.current_skill, "Smithing")
        self.assertEqual(self._enabled(dialog, "actionQueueMoveUp"), [False, True, True])

        addon._state.player_data["inventory"]["Iron ore"] = 5
        with patch.object(addon.random, "random", lambda: 0.5):
            self.profile._answer(addon)
        self.assertEqual(addon._state.player_data["inventory"]["Iron bar"], 5)
        dialog.close()

    def test_a_move_that_would_end_a_running_session_asks_first_and_no_keeps_the_order(self):
        from ankiscape.logic.flash_powder_factory_logic import enter_flash_powder_factory_pure

        addon = self._played("ankiscape_move_session", (_MINE_IRON, 30), (_PICKUP, 5))
        save = addon._state.player_data
        save.update({"agility_level": 99, "thieving_level": 99, "herblore_level": 99})
        entered, ok, info = enter_flash_powder_factory_pure(save)
        self.assertTrue(ok, info)
        save.update(entered)
        dialog = self._menu(addon)
        before = self._rows(dialog)

        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as asked:
            self._moves(dialog, "actionQueueMoveUp")[1].click()

        self.assertEqual(asked.call_args.args[1], "Leave Flash Powder Factory?")
        self.assertEqual(self._rows(dialog), before)
        self.assertEqual(addon._state.current_skill, "Mining")
        dialog.close()

    def test_five_rows_with_their_moves_fit_at_the_short_size(self):
        addon = self._played("ankiscape_move_five", *[(_MINE_IRON, 2_000_000_000 - i) for i in range(5)])
        for size in ((720, 540), (900, 560)):
            with self.subTest(size=size):
                dialog = self._menu(addon, size)
                panel = dialog.findChild(QWidget, "actionQueuePanel")
                self.assertEqual(len(self._rows(dialog)), 5)
                self.assertEqual([bar for bar in panel.findChildren(QScrollBar) if bar.isVisible()], [])
                self.assertEqual(text_fit_defects(panel), [])
                dialog.close()
