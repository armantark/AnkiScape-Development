"""Up, Down and remove on the queue box's rows: the real menu widgets on the add-on's real queue command."""

from __future__ import annotations

import sys
import unittest
from functools import partial
from unittest.mock import patch

from tests.action_queue.test_queue_reviews import _MINE_IRON, _SMELT_IRON, _SMITH_PLATEBODY, QueueProfile
from tests.main_menu import fixtures
from tests.test_main_menu_widget import HAS_AQT

if HAS_AQT:
    from aqt.qt import QLabel, QMainWindow, QMessageBox, QPushButton, QScrollBar, QToolButton, QWidget
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

    def _menu(self, addon, size=(900, 560), **callbacks):
        from ankiscape.ui.ui_action_queue import notify_action_queue_changed

        def command(name, payload):
            result = addon.apply_action_queue_command(addon, name, payload)
            notify_action_queue_changed()
            return result

        dialog = self._open(
            addon._state.player_data, current_skill=addon._state.current_skill, on_action_queue_command=command, **callbacks
        )
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

    def test_moves_show_chevrons_and_keep_their_names(self):
        addon = self._played("ankiscape_move_chevrons", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        dialog = self._menu(addon)
        ups, downs = self._moves(dialog, "actionQueueMoveUp"), self._moves(dialog, "actionQueueMoveDown")
        self.assertEqual([button.text() for button in ups + downs], ["∧", "∧", "∨", "∨"])
        self.assertEqual(
            [button.accessibleName() for button in ups + downs],
            ["Move entry 1 up", "Move entry 2 up", "Move entry 1 down", "Move entry 2 down"],
        )
        self.assertEqual(self._enabled(dialog, "actionQueueMoveUp"), [False, True])
        self.assertEqual(self._enabled(dialog, "actionQueueMoveDown"), [True, False])
        dialog.close()

    def _flashed(self, dialog):
        """The text of the line under a running band; None when no band runs."""
        lines = dialog.findChild(QWidget, "actionQueuePanel")._lines
        running = lines.fade.state() == lines.fade.State.Running
        return lines._band.text() if running else None

    def test_a_move_flashes_the_row_at_its_new_place_and_never_says_added(self):
        addon = self._played("ankiscape_move_flash", (_MINE_IRON, 30), (_SMELT_IRON, 5), (_SMITH_PLATEBODY, 1))
        dialog = self._menu(addon)
        platebody = "Smithing: Iron platebody · 0 / 1 Iron platebody"
        self.assertIsNone(self._flashed(dialog))

        self._click(dialog, "actionQueueMoveUp", 2)

        self.assertEqual(self._rows(dialog)[1], platebody)
        self.assertEqual(self._flashed(dialog), platebody)
        self.assertEqual(
            [button.text() for button in dialog.findChildren(QPushButton, "queueAddButton") if button.isVisible()],
            ["Add to queue"],
        )

        self._click(dialog, "actionQueueMoveUp", 1)
        self.assertEqual(self._rows(dialog)[0], platebody)
        self.assertEqual(self._flashed(dialog), platebody)
        dialog.close()

    def test_a_refused_move_does_not_flash(self):
        addon = self._played("ankiscape_move_refused", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        dialog = self._menu(addon)
        queue = dialog._ankiscape_menu_ctx.on_action_queue_command
        queue("move", {"position": 0, "new_index": -1})
        queue("move", {"position": 1, "new_index": 2})
        QApplication.processEvents()
        self.assertIsNone(self._flashed(dialog))
        dialog.close()

    def test_a_flash_follows_the_row_when_the_new_first_entry_could_not_start(self):
        quest = {"kind": "quest", "quest_id": "cooks_assistant"}
        for position, new_index, flashed in ((1, 0, None), (0, 1, "Mining: Iron · 0 / 30 Iron ore")):
            with self.subTest(position=position, new_index=new_index):
                addon = self._played(f"ankiscape_move_passed_{position}", (_MINE_IRON, 30), (quest, None))
                addon._state.player_data["quests"]["cooks_assistant"] = {"completed": True}
                dialog = self._menu(addon)
                dialog._ankiscape_menu_ctx.on_action_queue_command("move", {"position": position, "new_index": new_index})
                QApplication.processEvents()
                self.assertEqual(self._rows(dialog), ["Mining: Iron · 0 / 30 Iron ore"])
                self.assertEqual(self._flashed(dialog), flashed)
                dialog.close()

    def _removes(self, dialog):
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        return [button for button in panel.findChildren(QToolButton, "actionQueueRemove") if button.isVisibleTo(panel)]

    def test_entry_one_has_the_remove_control_and_its_click_runs_the_next_entry_on_the_next_card(self):
        addon = self._played("ankiscape_remove_click", (_MINE_IRON, 30), (_SMELT_IRON, 5))
        addon._state.player_data["inventory"]["Iron ore"] = 5
        dialog = self._menu(addon)
        self.assertEqual(
            [button.accessibleName() for button in self._removes(dialog)], ["Remove entry 1", "Remove entry 2"]
        )

        self._removes(dialog)[0].click()
        QApplication.processEvents()

        self.assertEqual(self._rows(dialog), ["Smithing: Iron bar · 0 / 5 Iron bar"])
        self.assertEqual(addon._state.current_skill, "Smithing")
        with patch.object(addon.random, "random", lambda: 0.5):
            self.profile._answer(addon)
        self.assertEqual(addon._state.player_data["inventory"]["Iron bar"], 5)
        dialog.close()

    def test_removing_the_last_entry_empties_the_box(self):
        addon = self._played("ankiscape_remove_click_last", (_MINE_IRON, 30))
        dialog = self._menu(addon)

        self._removes(dialog)[0].click()
        QApplication.processEvents()

        self.assertFalse(dialog.findChild(QWidget, "actionQueuePanel").isVisible())
        self.assertEqual(dialog.findChild(QLabel, "actionQueueEmptyLine").text(), "Queue: empty")
        self.assertEqual(addon._state.player_data["current_utility"], "bankstanding")
        dialog.close()

    def test_a_removal_that_would_end_a_running_session_asks_first_and_no_keeps_the_entry(self):
        from ankiscape.logic.flash_powder_factory_logic import enter_flash_powder_factory_pure

        addon = self._played("ankiscape_remove_session", (_MINE_IRON, 30))
        save = addon._state.player_data
        save.update({"agility_level": 99, "thieving_level": 99, "herblore_level": 99})
        entered, ok, info = enter_flash_powder_factory_pure(save)
        self.assertTrue(ok, info)
        save.update(entered)
        dialog = self._menu(addon)

        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as asked:
            self._removes(dialog)[0].click()

        self.assertEqual(asked.call_args.args[1], "Leave Flash Powder Factory?")
        self.assertEqual(len(self._rows(dialog)), 1)
        self.assertEqual(addon._state.current_skill, "Mining")
        dialog.close()

    def test_a_session_left_for_a_removal_passes_the_entry_once_and_the_next_entry_stays(self):
        from ankiscape.logic.flash_powder_factory_logic import (
            FLASH_POWDER_FACTORY_ACTIVITY_ID,
            enter_flash_powder_factory_pure,
            flash_powder_factory_view_pure,
        )
        from ankiscape.ui.ui_action_queue import menu_queue

        factory = {"kind": "utility", "utility_id": FLASH_POWDER_FACTORY_ACTIVITY_ID}
        addon = self._played("ankiscape_remove_session_yes", (factory, 5), (_PICKUP, 5))
        save = addon._state.player_data
        save.update({"agility_level": 99, "thieving_level": 99, "herblore_level": 99})
        entered, ok, info = enter_flash_powder_factory_pure(save)
        self.assertTrue(ok, info)
        save.update(entered)
        captured = {}
        with patch.object(addon.ui, "show_main_menu", lambda *args, **kwargs: captured.update(kwargs)):
            addon._on_main_menu()

        def leave(_activity):
            return captured["on_agility_command"]("leave_flash_powder_factory", {})["ok"]

        results = []
        queue = menu_queue(
            save, lambda: addon._state.current_skill, partial(addon.apply_action_queue_command, addon), results.append, leave
        )
        queue("remove", {"position": 0})

        self.assertFalse(flash_powder_factory_view_pure(save)["active"])
        self.assertEqual([row[0] for row in self.profile._rows(addon)], ["Pick onions"])
        self.assertEqual(save["current_utility"], _PICKUP["utility_id"])
        self.assertFalse(results[0]["ok"])

    def test_the_review_hud_drops_the_stale_next_line_after_a_move(self):
        quest = {"kind": "quest", "quest_id": "pirates_treasure"}
        rune_mysteries = {"kind": "quest", "quest_id": "rune_mysteries"}
        combat = {"kind": "combat", "target": "cow", "combat_action": "attack"}
        addon = self._played("ankiscape_move_hud", (quest, None), (combat, 100), (rune_mysteries, None))
        addon._state.player_data["inventory"].update({"Karamjan rum": 1, "Spade": 1})
        with patch.object(addon.random, "random", lambda: 0.5):
            for _card in range(3):
                self.profile._answer(addon)
        line = "Pirate's Treasure complete. Next: Combat."
        parent = QMainWindow()
        parent.show()
        parent.resize(900, 560)
        hud = self._ui.ReviewHUD(parent)
        hud.set_data(addon._state.player_data, addon._state.current_skill)
        self.assertEqual(hud.world_notice_lbl.text(), line)

        self.assertTrue(addon.apply_action_queue_command(addon, "move", {"position": 1, "new_index": 0})["ok"])
        hud.set_data(addon._state.player_data, addon._state.current_skill)

        self.assertEqual(addon._state.current_skill, "Quests")
        self.assertEqual(hud.world_notice_lbl.text(), "")
        self.assertFalse(hud.world_notice_lbl.isVisibleTo(parent))
        self.assertIn(line, self.profile._log(addon))
        parent.close()

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
