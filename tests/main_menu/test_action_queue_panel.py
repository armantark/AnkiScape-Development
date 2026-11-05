"""The queue panel through the real main menu widgets: add, count, the five-entry cap, Clear, the fold.

The menu's queue command here applies the real queue state functions to the
save and, like the add-on's, reports the action an add to an empty queue
starts; the add-on's own command is driven through the review handler in
tests/action_queue.
"""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from tests.main_menu import fixtures
from tests.main_menu.test_wheel_guard import _wheel
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_main_tabs,
    _find_smith_tree,
    _goto_smithing,
    _make_player_data,
    _open_quests_tab,
    _smith_row,
    patch,
)

if HAS_AQT:
    from aqt.qt import QPoint, QScrollBar
    from tests.test_main_menu_widget import QApplication, QLabel, QMessageBox, QPushButton, QSpinBox, QTest, QToolButton, QWidget
    from tests.ui_flows.qt_text_fit import text_fit_defects

_SMELT_IRON = {"kind": "skill", "skill": "Smithing", "target": "smelt_iron_bar"}
# Five entries of every kind, the last the longest line a queue can show.
_ENTRIES = (
    (_SMELT_IRON, 20),
    ({"kind": "skill", "skill": "Mining", "target": "iron"}, 28),
    ({"kind": "quest", "quest_id": "recipe_for_disaster_defeating_the_culinaromancer"}, None),
    ({"kind": "combat", "target": "chicken", "combat_action": "attack"}, 50),
    ({"kind": "utility", "utility_id": "convert_mahogany_logs_to_mahogany_planks"}, 2_000_000_000),
)


def _words(label):
    """A wrapped label's text as the player reads it; the last two words are glued so they wrap together."""
    return label.text().replace("\u00a0", " ")


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ActionQueuePanelTest(fixtures.MainMenuWidgetTest):
    def _queue_command(self, player_data, running="Mining"):
        from ankiscape.core.action_queue import (
            ACTION_QUEUE_KEY,
            action_queue_pure,
            add_queue_entry_pure,
            current_queue_entry_pure,
        )
        from ankiscape.ui.ui_action_queue import notify_action_queue_changed

        self.commands = []
        active = {"skill": running}

        def command(name, payload):
            self.commands.append((name, payload))
            queue, ok = action_queue_pure(player_data), True
            if name == "add":
                idle = current_queue_entry_pure(queue) is None
                queue, ok = add_queue_entry_pure(queue, payload["action"], payload["count"])
                if ok and idle:
                    active["skill"] = payload["action"].get("skill", "Activities")
            elif name == "clear":
                queue = {"entries": [], "done": 0, "paused": False}
            player_data[ACTION_QUEUE_KEY] = queue
            notify_action_queue_changed()
            return {"ok": ok, "active": active["skill"], "message": ""}

        return command

    def _smithing_menu(self, queue=None, size=(900, 560), running="Mining", **inventory):
        pd = _make_player_data()
        pd["smithing_level"] = 40
        pd["current_smith"] = "smelt_iron_bar"
        pd["inventory"] = dict(inventory)
        if queue is not None:
            pd["action_queue"] = queue
        dialog = self._open(pd, running, on_action_queue_command=self._queue_command(pd, running))
        dialog.show()
        dialog.resize(*size)
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
        self.assertEqual(_words(self._visible(dialog, QLabel, "queueMaterials")), "Iron ore: 37 in Bank")
        self.assertFalse(panel.isVisible())
        self.assertEqual(_words(dialog.findChild(QLabel, "actionQueueEmptyLine")), "Queue: empty")

        count.setValue(100)
        self._visible(dialog, QPushButton, "queueAddButton").click()
        QApplication.processEvents()

        self.assertEqual(self.commands, [("add", {"action": _SMELT_IRON, "count": 100})])
        self.assertTrue(panel.isVisible())
        self.assertEqual(self._rows(dialog), ["Smithing: Iron bar · 0 / 100 Iron bar"])
        # Smithing started, so the panel was rebuilt; the new box keeps the count.
        self.assertEqual(self._visible(dialog, QSpinBox, "queueCountBox").value(), 100)

        # Another target re-reads the Bank, and the queued bars count as its input.
        pd["current_smith"] = "forge_iron_platebody"
        update_review_hud(pd, "Smithing")
        count = self._visible(dialog, QSpinBox, "queueCountBox")
        # Five bars make a platebody, so the 100 queued bars offer 20.
        self.assertEqual((count.value(), count.suffix()), (20, " Iron platebody"))
        self.assertEqual(_words(self._visible(dialog, QLabel, "queueMaterials")), "Iron bar: 0 in Bank, 100 from entry 1")

    def test_the_fifth_entry_fills_the_queue_and_clear_empties_it(self):
        _pd, dialog = self._smithing_menu(**{"Iron ore": 3})
        for _ in range(5):
            self._visible(dialog, QPushButton, "queueAddButton").click()
            QApplication.processEvents()
        add = self._visible(dialog, QPushButton, "queueAddButton")

        self.assertEqual(len(self._rows(dialog)), 5)
        self.assertEqual(dialog.findChild(QPushButton, "actionQueueTitle").text(), "▾ Queue: 5 of 5")
        self.assertFalse(add.isEnabled())
        self.assertEqual(add.toolTip(), "The queue is full.")

        dialog.findChild(QPushButton, "actionQueueClear").click()
        QApplication.processEvents()

        self.assertFalse(dialog.findChild(QWidget, "actionQueuePanel").isVisible())
        self.assertTrue(add.isEnabled())

    def _queue_of(self, count):
        from ankiscape.core.action_queue import action_queue_pure, add_queue_entry_pure

        queue = action_queue_pure({})
        for action, entry_count in _ENTRIES[:count]:
            queue, _ok = add_queue_entry_pure(queue, action, entry_count)
        return queue

    def test_every_entry_shows_whole_with_no_scroll_bar_and_a_short_menu_scrolls_the_page(self):
        for size in ((720, 540), (900, 560)):
            heights = []
            for count in (1, 3, 5):
                with self.subTest(size=size, entries=count):
                    _pd, dialog = self._smithing_menu(queue=self._queue_of(count), size=size)
                    panel = dialog.findChild(QWidget, "actionQueuePanel")

                    self.assertEqual(len(self._rows(dialog)), count)
                    self.assertEqual([bar for bar in panel.findChildren(QScrollBar) if bar.isVisible()], [])
                    # Every line, the long one too, sits whole inside the box.
                    self.assertEqual(text_fit_defects(panel), [])
                    heights.append(panel.height())
                    # The page gives up the height and scrolls; it is never squeezed below its content.
                    skills_page = _find_main_tabs(dialog).widget(0).widget()
                    self.assertGreaterEqual(skills_page.height(), skills_page.heightForWidth(skills_page.width()))
                    dialog.close()
            self.assertEqual(heights, sorted(set(heights)))

    def test_the_title_folds_the_box_to_its_line_and_the_fold_outlasts_the_menu(self):
        from ankiscape.ui import ui_action_queue

        config = {}
        with patch.object(ui_action_queue, "mw", SimpleNamespace(col=SimpleNamespace(get_config=config.get, set_config=config.__setitem__))):
            _pd, dialog = self._smithing_menu(queue=self._queue_of(3))
            panel = dialog.findChild(QWidget, "actionQueuePanel")
            title = panel.findChild(QPushButton, "actionQueueTitle")
            open_height = panel.height()

            title.click()
            for _ in range(3):
                QApplication.processEvents()

            self.assertEqual((title.text(), self._rows(dialog)), ("▸ Queue: 3 of 5", []))
            self.assertLess(panel.height(), open_height)
            dialog.close()

            _pd, reopened = self._smithing_menu(queue=self._queue_of(3))
            self.assertEqual(self._rows(reopened), [])
            reopened.findChild(QPushButton, "actionQueueTitle").click()
            QApplication.processEvents()
            self.assertEqual(len(self._rows(reopened)), 3)

    def test_an_add_confirms_on_its_button_and_marks_its_new_line_for_a_moment(self):
        _pd, dialog = self._smithing_menu(**{"Iron ore": 37})
        # The first add starts Smithing and rebuilds the panel; the new button still confirms it.
        for entries in (1, 2):
            self._visible(dialog, QPushButton, "queueAddButton").click()
            QApplication.processEvents()
            self.assertEqual(self._visible(dialog, QPushButton, "queueAddButton").text(), f"Added ✓ ({entries} of 5)")
        lines = dialog.findChild(QWidget, "actionQueueRows")

        def line_colours():
            image = lines.grab().toImage()
            return [
                image.pixelColor(QPoint(1, label.geometry().center().y()))
                for label in lines.findChildren(QLabel, "actionQueueRowState")[:2]
            ]

        first, new = line_colours()
        self.assertNotEqual(new, first)

        QTest.qWait(1600)

        self.assertEqual(self._visible(dialog, QPushButton, "queueAddButton").text(), "Add to queue")
        first, new = line_colours()
        self.assertEqual(new, first)

    def test_a_quest_card_that_cannot_queue_names_why(self):
        pd = _make_player_data()
        pd["quests"] = {"rune_mysteries": {"completed": True}}
        dialog = self._open(pd, on_action_queue_command=self._queue_command(pd))
        _open_quests_tab(dialog)

        for quest_id, reason in (("rune_mysteries", "This quest is complete."), ("dragon_slayer", "Requires: 32 quest points")):
            add = dialog.findChild(QWidget, f"questCard_{quest_id}").findChild(QPushButton, "queueAddButton")
            self.assertEqual((add.isEnabled(), add.toolTip()), (False, reason))

    def test_each_entry_has_a_remove_control(self):
        from ankiscape.core.action_queue import action_queue_pure, add_queue_entry_pure

        queue = action_queue_pure({})
        for count in (50, 60):
            queue, _ok = add_queue_entry_pure(queue, _SMELT_IRON, count)
        _pd, dialog = self._smithing_menu(queue=queue)
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        removes = panel.findChildren(QToolButton, "actionQueueRemove")

        self.assertEqual([button.isVisibleTo(panel) for button in removes[:3]], [True, True, False])
        self.assertEqual(
            [label.text() for label in panel.findChildren(QLabel, "actionQueueRowState")][:2], ["1. Now", "2. Next"]
        )
        removes[1].click()
        self.assertEqual(self.commands[-1], ("remove", {"position": 1, "entry": queue["entries"][1]}))

    def test_a_target_picked_while_the_queue_runs_that_skill_is_held_for_the_queue(self):
        from ankiscape.core.action_queue import action_queue_pure, add_queue_entry_pure

        queue, _ok = add_queue_entry_pure(action_queue_pure({}), _SMELT_IRON, 50)
        pd, dialog = self._smithing_menu(queue=queue, running="Smithing", **{"Iron ore": 37, "Tin ore": 4, "Copper ore": 9})
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

    def _castle_wars_add_in_flash_powder_factory(self, current_skill, current_utility):
        from ankiscape.logic.agility_logic import default_agility_state_pure
        from ankiscape.logic.flash_powder_factory_logic import enter_flash_powder_factory_pure

        pd = _make_player_data()
        pd.update(default_agility_state_pure())
        pd.update({"agility_level": 99, "thieving_level": 99, "herblore_level": 99,
                   "activity_session": {"active_id": ""}, "summoning_state": {"active_follower": {}}})
        pd, ok, _info = enter_flash_powder_factory_pure(pd)
        self.assertTrue(ok)
        pd["current_utility"] = current_utility
        dialog = self._open(pd, current_skill, on_action_queue_command=self._queue_command(pd))
        dialog.show()
        self._open_activity_detail(dialog, "castle_wars")
        return self._visible(dialog, QPushButton, "queueAddButton")

    def test_an_add_that_starts_an_activity_asks_to_leave_a_running_session(self):
        # An add starts the queue also over the factory the player runs by hand (owner, Pass 19).
        for current_skill, current_utility in (("Utilities", "bankstanding"), ("Activities", "flash_powder_factory")):
            with self.subTest(current_utility=current_utility):
                # An add the queue refuses ends no session.
                add = self._castle_wars_add_in_flash_powder_factory(current_skill, current_utility)
                add.parent().findChild(QSpinBox, "queueCountBox").setValue(0)
                with patch.object(QMessageBox, "question") as asked:
                    add.click()
                asked.assert_not_called()

                add = self._castle_wars_add_in_flash_powder_factory(current_skill, current_utility)
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
        self.assertEqual(self._rows(dialog), ["Rune Mysteries · until it stops"])


if __name__ == "__main__":
    unittest.main()
