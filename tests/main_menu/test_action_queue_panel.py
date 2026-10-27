"""The queue panel through the real main menu widgets: add, count, the five-entry cap, Clear.

The menu's queue command here applies the real queue state functions to the
save and, like the add-on's, reports the action an add to an empty queue
starts; the add-on's own command is driven through the review handler in
tests/action_queue.
"""

from __future__ import annotations

import unittest

from tests.main_menu import fixtures
from tests.main_menu.test_wheel_guard import _wheel
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_smith_tree,
    _goto_smithing,
    _make_player_data,
    _open_quests_tab,
    _smith_row,
    patch,
)

if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QMessageBox, QPushButton, QSpinBox, QToolButton, QWidget

_SMELT_IRON = {"kind": "skill", "skill": "Smithing", "target": "smelt_iron_bar"}


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ActionQueuePanelTest(fixtures.MainMenuWidgetTest):
    def _queue_command(self, player_data):
        from ankiscape.core.action_queue import (
            ACTION_QUEUE_KEY,
            action_queue_pure,
            add_queue_entry_pure,
            current_queue_entry_pure,
        )
        from ankiscape.ui.ui_action_queue import notify_action_queue_changed

        self.commands = []
        active = {"skill": "Mining"}

        def command(name, payload):
            self.commands.append((name, payload))
            queue, ok = action_queue_pure(player_data), True
            if name == "add":
                idle = current_queue_entry_pure(queue) is None
                queue, ok = add_queue_entry_pure(queue, payload["action"], payload["count"])
                if ok and idle:
                    active["skill"] = payload["action"].get("skill", "Activities")
            elif name == "clear":
                queue = {"entries": [], "index": 0, "done": 0, "paused": False}
            player_data[ACTION_QUEUE_KEY] = queue
            notify_action_queue_changed()
            return {"ok": ok, "active": active["skill"], "message": ""}

        return command

    def _smithing_menu(self, queue=None, **inventory):
        pd = _make_player_data()
        pd["smithing_level"] = 40
        pd["current_smith"] = "smelt_iron_bar"
        pd["inventory"] = dict(inventory)
        if queue is not None:
            pd["action_queue"] = queue
        dialog = self._open(pd, on_action_queue_command=self._queue_command(pd))
        dialog.show()
        dialog.resize(900, 560)
        _goto_smithing(dialog)
        QApplication.processEvents()
        return pd, dialog

    def _visible(self, dialog, kind, name):
        return next(widget for widget in dialog.findChildren(kind, name) if widget.isVisible())

    def _rows(self, dialog):
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        return [label.text() for label in panel.findChildren(QLabel, "actionQueueRowText") if label.isVisibleTo(panel)]

    def test_the_count_box_starts_at_what_the_bank_allows_and_keeps_a_typed_count(self):
        from ankiscape.ui.ui import update_review_hud

        pd, dialog = self._smithing_menu(**{"Iron ore": 37})
        count = self._visible(dialog, QSpinBox, "queueCountBox")
        panel = dialog.findChild(QWidget, "actionQueuePanel")

        self.assertEqual((count.value(), count.suffix()), (37, " Iron bar"))
        self.assertEqual(self._visible(dialog, QLabel, "queueMaterials").text(), "Iron ore: 37 in Bank")
        self.assertFalse(panel.isVisible())
        self.assertEqual(
            dialog.findChild(QLabel, "actionQueueEmptyLine").text(),
            "Queue: empty. Set a count and choose Add to queue on a skill, or Add to queue on a quest."
            " Up to 5 entries run from top to bottom once.",
        )

        count.setValue(100)
        self._visible(dialog, QPushButton, "queueAddButton").click()
        QApplication.processEvents()

        self.assertEqual(self.commands, [("add", {"action": _SMELT_IRON, "count": 100})])
        self.assertTrue(panel.isVisible())
        self.assertEqual(self._rows(dialog), ["Smithing: Iron bar · 0 / 100 Iron bar"])
        # Smithing started, so the panel was rebuilt; the new box keeps the count.
        self.assertEqual(self._visible(dialog, QSpinBox, "queueCountBox").value(), 100)

        # Another target re-reads the Bank, and the queued bars show as its input.
        pd["current_smith"] = "forge_iron_platebody"
        update_review_hud(pd, "Smithing")
        count = self._visible(dialog, QSpinBox, "queueCountBox")
        self.assertEqual((count.value(), count.suffix()), (0, " Iron platebody"))
        self.assertEqual(self._visible(dialog, QLabel, "queueMaterials").text(), "Iron bar: 0 in Bank, 100 made by entry 1")

    def test_the_fifth_entry_fills_the_queue_and_clear_empties_it(self):
        _pd, dialog = self._smithing_menu(**{"Iron ore": 3})
        for _ in range(5):
            self._visible(dialog, QPushButton, "queueAddButton").click()
            QApplication.processEvents()
        add = self._visible(dialog, QPushButton, "queueAddButton")

        self.assertEqual(len(self._rows(dialog)), 5)
        self.assertEqual(dialog.findChild(QLabel, "actionQueueTitle").text(), "Queue: 5 of 5 entries")
        self.assertFalse(add.isEnabled())
        self.assertEqual(add.toolTip(), "The queue holds 5 entries. Clear it to plan again.")
        # Five entries scroll inside the box instead of pushing the lists away.
        self.assertLess(dialog.findChild(QWidget, "actionQueueRows").height(), 5 * 18)

        dialog.findChild(QPushButton, "actionQueueClear").click()
        QApplication.processEvents()

        self.assertFalse(dialog.findChild(QWidget, "actionQueuePanel").isVisible())
        self.assertTrue(add.isEnabled())

    def test_each_entry_that_is_not_running_has_a_remove_control(self):
        from ankiscape.core.action_queue import action_queue_pure, add_queue_entry_pure

        queue = action_queue_pure({})
        for count in (50, 60):
            queue, _ok = add_queue_entry_pure(queue, _SMELT_IRON, count)
        _pd, dialog = self._smithing_menu(queue=queue)
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        removes = panel.findChildren(QToolButton, "actionQueueRemove")

        self.assertEqual([button.isVisibleTo(panel) for button in removes[:2]], [False, True])
        self.assertEqual(
            [label.text() for label in panel.findChildren(QLabel, "actionQueueRowState")][:2], ["1. Now", "2. Next"]
        )
        removes[1].click()
        self.assertEqual(self.commands[-1], ("remove", {"position": 1}))

    def test_a_waiting_plan_offers_start_now(self):
        from ankiscape.core.action_queue import action_queue_pure, add_queue_entry_pure

        queue, _ok = add_queue_entry_pure(action_queue_pure({}), _SMELT_IRON, 50)
        _pd, dialog = self._smithing_menu(queue={**queue, "waiting": True})
        start_now = dialog.findChild(QPushButton, "actionQueueResume")

        self.assertEqual((start_now.text(), start_now.isVisible()), ("Start now", True))
        self.assertEqual(dialog.findChild(QLabel, "actionQueueHint").text(), "Starts when Mining stops. Start now begins it at once.")
        start_now.click()
        self.assertEqual(self.commands[-1], ("resume", {}))

    def test_a_target_picked_while_the_queue_runs_that_skill_is_held_for_the_queue(self):
        from ankiscape.core.action_queue import action_queue_pure, add_queue_entry_pure

        queue, _ok = add_queue_entry_pure(action_queue_pure({}), _SMELT_IRON, 50)
        pd, dialog = self._smithing_menu(queue=queue, **{"Iron ore": 37, "Tin ore": 4, "Copper ore": 9})
        tree = _find_smith_tree(dialog)

        tree.itemClicked.emit(_smith_row(tree, "smelt_bronze_bar"), 0)
        QApplication.processEvents()

        self.assertEqual(self._smith_calls, [])
        self.assertEqual(pd["current_smith"], "smelt_iron_bar")
        self.assertNotIn("✓", _smith_row(tree, "smelt_bronze_bar").text(0))
        count = self._visible(dialog, QSpinBox, "queueCountBox")
        self.assertEqual((count.value(), count.suffix()), (4, " Bronze bar"))

        self._visible(dialog, QPushButton, "queueAddButton").click()
        self.assertEqual(
            self.commands[-1],
            ("add", {"action": {"kind": "skill", "skill": "Smithing", "target": "smelt_bronze_bar"}, "count": 4}),
        )

    def test_an_add_that_starts_an_activity_asks_to_leave_a_running_session(self):
        from ankiscape.logic.agility_logic import default_agility_state_pure
        from ankiscape.logic.flash_powder_factory_logic import enter_flash_powder_factory_pure

        pd = _make_player_data()
        pd.update(default_agility_state_pure())
        pd.update({"agility_level": 99, "thieving_level": 99, "herblore_level": 99,
                   "activity_session": {"active_id": ""}, "summoning_state": {"active_follower": {}}})
        pd, ok, _info = enter_flash_powder_factory_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd, on_action_queue_command=self._queue_command(pd))
        dialog.show()
        self._open_activity_detail(dialog, "castle_wars")
        add = self._visible(dialog, QPushButton, "queueAddButton")

        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.No) as asked:
            add.click()
        self.assertEqual(asked.call_args.args[1], "Leave Flash Powder Factory?")
        self.assertEqual(self.commands, [])

        with patch.object(QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes):
            add.click()
        self.assertEqual(self._agility_command_calls[-1], ("leave_flash_powder_factory", {}))
        self.assertEqual(self.commands[-1][1]["action"], {"kind": "utility", "utility_id": "castle_wars"})

    def test_the_wheel_leaves_the_count_box_alone(self):
        _pd, dialog = self._smithing_menu(**{"Iron ore": 37})
        count = self._visible(dialog, QSpinBox, "queueCountBox")
        _wheel(count, 120)
        _wheel(count, -120)
        self.assertEqual(count.value(), 37)

    def test_a_quest_card_queues_its_quest_without_a_count(self):
        pd = _make_player_data()
        dialog = self._open(pd, on_action_queue_command=self._queue_command(pd))
        _open_quests_tab(dialog)
        card = dialog.findChild(QWidget, "questCard_rune_mysteries")
        self.assertFalse(card.findChild(QSpinBox, "queueCountBox").isVisibleTo(card))

        card.findChild(QPushButton, "queueAddButton").click()
        QApplication.processEvents()

        self.assertEqual(self.commands, [("add", {"action": {"kind": "quest", "quest_id": "rune_mysteries"}, "count": None})])
        self.assertEqual(self._rows(dialog), ["Rune Mysteries · until the quest stops"])


if __name__ == "__main__":
    unittest.main()
