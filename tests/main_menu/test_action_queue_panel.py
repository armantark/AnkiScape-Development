"""The queue panel through the real main menu widgets: add, count, the five-entry cap, Clear.

The menu's queue command here applies the real queue state functions to the
save, as the add-on's command does after its undo step; the add-on's own
command is driven through the review handler in tests/action_queue.
"""

from __future__ import annotations

import unittest

from tests.main_menu import fixtures
from tests.main_menu.test_wheel_guard import _wheel
from tests.test_main_menu_widget import HAS_AQT, _goto_smithing, _make_player_data, _open_quests_tab

if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QPushButton, QSpinBox, QWidget

_SMELT_IRON = {"kind": "skill", "skill": "Smithing", "target": "smelt_iron_bar"}


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ActionQueuePanelTest(fixtures.MainMenuWidgetTest):
    def _queue_command(self, player_data):
        from ankiscape.core.action_queue import ACTION_QUEUE_KEY, action_queue_pure, add_queue_entry_pure
        from ankiscape.ui.ui_action_queue import notify_action_queue_changed

        def command(name, payload):
            self.commands.append((name, payload))
            queue, ok = action_queue_pure(player_data), True
            if name == "add":
                queue, ok = add_queue_entry_pure(queue, payload["action"], payload["count"])
            elif name == "clear":
                queue = {"entries": [], "index": 0, "done": 0, "paused": False}
            player_data[ACTION_QUEUE_KEY] = queue
            notify_action_queue_changed()
            return {"ok": ok, "active": "Mining", "message": ""}

        return command

    def _smithing_menu(self, **inventory):
        self.commands = []
        pd = _make_player_data()
        pd["smithing_level"] = 40
        pd["current_smith"] = "smelt_iron_bar"
        pd["inventory"] = dict(inventory)
        dialog = self._open(pd, on_action_queue_command=self._queue_command(pd))
        dialog.show()
        dialog.resize(900, 560)
        _goto_smithing(dialog)
        QApplication.processEvents()
        return pd, dialog

    def _rows(self, dialog):
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        return [label.text() for label in panel.findChildren(QLabel, "actionQueueRowText") if label.isVisibleTo(panel)]

    def test_the_count_box_starts_at_what_the_bank_allows_and_takes_a_typed_count(self):
        from ankiscape.ui.ui import update_review_hud

        pd, dialog = self._smithing_menu(**{"Iron ore": 37})
        count = dialog.findChild(QSpinBox, "queueCountBox")
        add = dialog.findChild(QPushButton, "queueAddButton")
        panel = dialog.findChild(QWidget, "actionQueuePanel")

        self.assertEqual((count.value(), count.suffix()), (37, " Iron bar"))
        self.assertIn("Your Bank holds enough for 37 Iron bar", count.toolTip())
        self.assertFalse(panel.isVisible())

        count.setValue(100)
        add.click()
        QApplication.processEvents()

        self.assertEqual(self.commands, [("add", {"action": _SMELT_IRON, "count": 100})])
        self.assertTrue(panel.isVisible())
        self.assertEqual(self._rows(dialog), ["Smithing: Iron bar · 0 / 100 Iron bar"])

        # Picking another target re-reads the Bank for it, as the HUD refresh does.
        pd["current_smith"] = "smelt_bronze_bar"
        pd["inventory"].update({"Tin ore": 4, "Copper ore": 9})
        update_review_hud(pd, "Smithing")
        self.assertEqual((count.value(), count.suffix()), (4, " Bronze bar"))

    def test_the_fifth_entry_fills_the_queue_and_clear_empties_it(self):
        _pd, dialog = self._smithing_menu(**{"Iron ore": 3})
        add = dialog.findChild(QPushButton, "queueAddButton")
        for _ in range(5):
            add.click()
        QApplication.processEvents()

        self.assertEqual(len(self._rows(dialog)), 5)
        self.assertEqual(dialog.findChild(QLabel, "actionQueueTitle").text(), "Queue 5/5")
        self.assertFalse(add.isEnabled())
        self.assertEqual(add.toolTip(), "The queue holds 5 entries. Clear it to plan again.")

        dialog.findChild(QPushButton, "actionQueueClear").click()
        QApplication.processEvents()

        self.assertFalse(dialog.findChild(QWidget, "actionQueuePanel").isVisible())
        self.assertTrue(add.isEnabled())

    def test_the_wheel_leaves_the_count_box_alone(self):
        _pd, dialog = self._smithing_menu(**{"Iron ore": 37})
        count = dialog.findChild(QSpinBox, "queueCountBox")
        _wheel(count, 120)
        _wheel(count, -120)
        self.assertEqual(count.value(), 37)

    def test_a_quest_card_queues_its_quest_without_a_count(self):
        self.commands = []
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
