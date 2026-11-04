"""Target clicks, the header button and the count, through the real add-on and the real menu.

The owner's case (Pass 20, the Jungle Potion herbs): a click could change the
Add record but not training, the header stayed disabled, the count could read
0, and a refused 0 came back. Each flow here clicks the real rows and buttons of
the menu the add-on opens, then answers cards through the real review handler.
"""

from __future__ import annotations

import sys
import unittest
from unittest.mock import patch

from tests.action_queue.test_queue_reviews import QueueProfile
from tests.test_main_menu_widget import HAS_AQT, _find_artisan_skill_list, _find_tree_with_user_role, _tree_row

if HAS_AQT:
    from aqt.qt import QApplication, QLabel, QPushButton, QSpinBox, Qt, QToolButton, QWidget
    from PyQt6.QtTest import QTest

_SNAKE_WEED = {"kind": "skill", "skill": "Herblore", "target": "clean_snake_weed"}
_ARDRIGAL = {"kind": "skill", "skill": "Herblore", "target": "clean_ardrigal"}
_VINES = {"kind": "utility", "utility_id": "search_marshy_jungle_vines"}
_HERBS = {"Grimy snake weed": 2, "Grimy ardrigal": 3}
_JUNGLE_POTION_DONE = {
    "druidic_ritual": {"completed": True, "started": True, "progress": 4},
    "jungle_potion": {"completed": True, "started": True, "progress": 6},
}


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class TargetClickTest(QueueProfile):
    def setUp(self):
        # The real aqt in place of the review fakes, because these flows open the real menu.
        self._orig_modules = dict(sys.modules)
        self.app = QApplication.instance() or QApplication([])

    def _herblore_addon(self, name, *entries, inventory=None):
        addon = self._queue_addon(
            f"ankiscape_target_click_{name}", *entries,
            herblore_level=99, current_herblore="clean_snake_weed",
            quests=dict(_JUNGLE_POTION_DONE), inventory=dict(_HERBS if inventory is None else inventory),
        )
        self.opened = []
        opened = self.opened

        class CapturingDialog(addon.ui.QDialog):
            def exec(instance):
                opened.append(instance)
                return 0

        addon.ui.QDialog = CapturingDialog
        return addon

    def _menu(self, addon, surface="Herblore"):
        addon._on_main_menu()
        dialog = self.opened[-1]
        self.addCleanup(dialog.close)
        dialog.show()
        dialog.resize(900, 560)
        category = "Artisan" if surface in {"Herblore", "Smithing"} else surface
        next(b for b in dialog.findChildren(QPushButton) if b.text() == category).click()
        if surface in {"Herblore", "Smithing"}:
            skills = _find_artisan_skill_list(dialog)
            skills.setCurrentRow(next(i for i in range(skills.count()) if skills.item(i).text() == surface))
        self._settle()
        return dialog

    def _settle(self):
        for _ in range(4):
            QApplication.processEvents()

    def _visible(self, dialog, kind, name):
        return next(widget for widget in dialog.findChildren(kind, name) if widget.isVisible())

    def _count(self, dialog):
        return self._visible(dialog, QSpinBox, "queueCountBox")

    def _header(self, dialog):
        texts = {"Train this skill", "Currently training", "Start utility", "Currently active"}
        return next(b for b in dialog.findChildren(QPushButton) if b.isVisible() and b.text() in texts)

    def _click_row(self, dialog, target):
        tree = _find_tree_with_user_role(dialog, target)
        row = _tree_row(tree, target)
        tree.expandAll()
        tree.scrollToItem(row)
        self._settle()
        QTest.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=tree.visualItemRect(row).center())
        self._settle()
        return tree, row

    def _add(self, dialog):
        self._visible(dialog, QPushButton, "queueAddButton").click()
        self._settle()

    def _start_ahead_of_queue(self, dialog):
        header = self._header(dialog)
        self.assertTrue(header.isEnabled())
        header.click()
        self._settle()

    def _queue_lines(self, addon):
        return [(row["name"], row["state"], row["done"]) for row in self._view(addon)["entries"]]

    def _view(self, addon):
        from ankiscape.core.action_queue import action_queue_view_pure

        return action_queue_view_pure(addon._state.player_data)

    def test_the_owners_herbs_click_add_and_train_each_do_what_they_show(self):
        addon = self._herblore_addon("herbs")
        save = addon._state.player_data
        dialog = self._menu(addon)

        # Nothing runs on Herblore yet, so the click saves the target and needs no typed count.
        self._click_row(dialog, "clean_ardrigal")
        self.assertEqual(save["current_herblore"], "clean_ardrigal")
        self.assertEqual((self._count(dialog).value(), self._count(dialog).suffix()), (3, " Clean ardrigal"))
        self._click_row(dialog, "clean_snake_weed")
        self.assertEqual((self._count(dialog).value(), self._count(dialog).suffix()), (2, " Clean snake weed"))

        self._add(dialog)
        self.assertEqual(self._queue_lines(addon), [("Herblore: Clean snake weed", "current", 0)])
        self.assertEqual((addon._state.current_skill, self._header(dialog).text()), ("Herblore", "Currently training"))
        self.assertFalse(self._header(dialog).isEnabled())

        # A click during the entry selects for Add only, and the header offers the pick.
        tree, row = self._click_row(dialog, "clean_ardrigal")
        self.assertEqual(save["current_herblore"], "clean_snake_weed")
        self.assertEqual((self._count(dialog).value(), self._count(dialog).suffix()), (3, " Clean ardrigal"))
        self.assertEqual(self._header(dialog).text(), "Train this skill")
        self.assertEqual(tree.selectedItems(), [row])
        self.assertIn("✓", _tree_row(tree, "clean_snake_weed").text(0))
        self.assertNotIn("✓", row.text(0))

        self._add(dialog)
        self.assertEqual(
            self._queue_lines(addon),
            [("Herblore: Clean snake weed", "current", 0), ("Herblore: Clean ardrigal", "waiting", 0)],
        )
        self.assertEqual(save["current_herblore"], "clean_snake_weed")

        # Both entries make exactly what the box offered.
        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
            self._answer(addon)
        self.assertEqual(self._queue_lines(addon), [])
        self.assertEqual((save["inventory"]["Clean snake weed"], save["inventory"]["Clean ardrigal"]), (2, 3))

    def test_the_header_starts_a_held_pick_ahead_of_the_queue_which_then_returns(self):
        addon = self._herblore_addon("detour", (_SNAKE_WEED, 2))
        save = addon._state.player_data
        dialog = self._menu(addon)
        self.assertEqual(self._header(dialog).text(), "Currently training")

        self._click_row(dialog, "clean_ardrigal")
        self.assertEqual(save["current_herblore"], "clean_snake_weed")
        self._start_ahead_of_queue(dialog)

        self.assertEqual(save["current_herblore"], "clean_ardrigal")
        self.assertEqual(self._header(dialog).text(), "Currently training")
        self.assertIn("✓", _tree_row(_find_tree_with_user_role(dialog, "clean_ardrigal"), "clean_ardrigal").text(0))
        self.assertTrue(self._view(addon)["suspended"])

        with patch.object(addon.random, "random", lambda: 0.5):
            self._answer(addon)
            self.assertEqual(save["inventory"]["Clean ardrigal"], 3)
            # The pick ran out of herbs, so the queue continues from its top entry.
            self._answer(addon)
            self.assertEqual((addon._state.current_skill, save["current_herblore"]), ("Herblore", "clean_snake_weed"))
            self.assertFalse(self._view(addon)["suspended"])
            self._answer(addon)
        self.assertEqual(save["inventory"]["Clean snake weed"], 2)
        self.assertEqual(self._log(addon)[-1], "Switched to Bankstanding · Queue finished after Herblore: Clean snake weed.")

    def test_a_click_back_on_the_training_row_returns_the_header_and_the_add_record(self):
        addon = self._herblore_addon("click_back", (_SNAKE_WEED, 2))
        dialog = self._menu(addon)

        self._click_row(dialog, "clean_ardrigal")
        self.assertEqual(self._header(dialog).text(), "Train this skill")
        self._click_row(dialog, "clean_snake_weed")

        self.assertEqual(self._header(dialog).text(), "Currently training")
        self.assertFalse(self._header(dialog).isEnabled())
        self.assertEqual(self._count(dialog).suffix(), " Clean snake weed")

    def test_a_held_pick_keeps_its_row_after_the_list_is_drawn_again(self):
        addon = self._herblore_addon("rebuild", (_SNAKE_WEED, 2))
        dialog = self._menu(addon)
        self._click_row(dialog, "clean_ardrigal")

        self._visible(dialog, QWidget, "herbloreTargetSearchInput").setText("clean")
        self._settle()

        tree = _find_tree_with_user_role(dialog, "clean_ardrigal")
        self.assertEqual(tree.selectedItems(), [_tree_row(tree, "clean_ardrigal")])
        self.assertIn("✓", _tree_row(tree, "clean_snake_weed").text(0))
        self.assertEqual((self._count(dialog).suffix(), self._header(dialog).text()), (" Clean ardrigal", "Train this skill"))

    def test_a_click_saves_the_target_when_the_queue_does_not_really_run_that_skill(self):
        from ankiscape.core.action_queue import ACTION_QUEUE_KEY

        addon = self._herblore_addon("mismatch", (_SNAKE_WEED, 2))
        save = addon._state.player_data
        # A save from before the hand-start mark, with Mining really running and the entry still unmarked.
        addon._state.current_skill = "Mining"
        self.assertFalse(save[ACTION_QUEUE_KEY]["paused"] or save[ACTION_QUEUE_KEY]["suspended"])
        dialog = self._menu(addon)

        self._click_row(dialog, "clean_ardrigal")

        self.assertEqual(save["current_herblore"], "clean_ardrigal")
        self.assertEqual(self._header(dialog).text(), "Train this skill")

    def test_a_utility_click_during_its_entry_holds_and_start_runs_it_until_stop_returns(self):
        addon = self._herblore_addon("utility", (_VINES, 500))
        save = addon._state.player_data
        dialog = self._menu(addon, "Utilities")
        self.assertEqual((addon._state.current_skill, self._header(dialog).text()), ("Utilities", "Currently active"))

        tree, pick = self._click_row(dialog, "search_jungle_palm_trees")
        self.assertEqual(save["current_utility"], "search_marshy_jungle_vines")
        self.assertEqual((self._count(dialog).suffix(), self._header(dialog).text()), (" Grimy ardrigal", "Start utility"))
        # This list marks its running row by selection, so the running row takes a tick while another row is picked.
        running = _tree_row(tree, "search_marshy_jungle_vines")
        self.assertEqual((tree.selectedItems(), tree.property("heldPick")), ([pick], True))
        self.assertEqual(running.text(0), "✓ Search marshy jungle vines")

        self._click_row(dialog, "search_marshy_jungle_vines")
        self.assertEqual((self._header(dialog).text(), tree.property("heldPick")), ("Currently active", False))
        self.assertEqual(running.text(0), "Search marshy jungle vines")

        self._click_row(dialog, "search_jungle_palm_trees")

        self._start_ahead_of_queue(dialog)
        self.assertEqual(save["current_utility"], "search_jungle_palm_trees")
        self.assertEqual(self._header(dialog).text(), "Currently active")

        # A free pickup has no end of its own: Stop returns to the queue.
        next(b for b in dialog.findChildren(QPushButton) if b.text() == "Stop training").click()
        self._settle()
        self.assertEqual(save["current_utility"], "search_marshy_jungle_vines")
        self.assertEqual(self._queue_lines(addon), [("Search marshy jungle vines", "current", 0)])

    def test_a_refused_header_start_preserves_the_running_target_and_held_pick(self):
        addon = self._herblore_addon("refused", (_SNAKE_WEED, 20))
        save = addon._state.player_data
        dialog = self._menu(addon)
        self._click_row(dialog, "clean_ardrigal")
        save["inventory"].clear()
        self._start_ahead_of_queue(dialog)
        self.assertEqual(save["current_herblore"], "clean_snake_weed")
        self.assertFalse(self._view(addon)["suspended"])
        self.assertEqual(self._count(dialog).suffix(), " Clean ardrigal")
        save["inventory"].update(_HERBS)
        self._start_ahead_of_queue(dialog)
        self.assertEqual(save["current_herblore"], "clean_ardrigal")
        self.assertTrue(self._view(addon)["suspended"])

    def test_utility_prefix_search_keeps_its_order_while_a_pick_is_held(self):
        addon = self._herblore_addon("search_held", (_VINES, 500))
        dialog = self._menu(addon, "Utilities")
        tree = _find_tree_with_user_role(dialog, "search_marshy_jungle_vines")
        search = self._visible(dialog, QWidget, "utilityActivityTargetSearchInput")

        def order():
            parent = _tree_row(tree, "search_marshy_jungle_vines").parent() or tree.invisibleRootItem()
            return [parent.child(i).data(0, Qt.ItemDataRole.UserRole) for i in range(parent.childCount())]

        search.setText("search")
        self._settle()
        before = order()
        self._click_row(dialog, "search_jungle_palm_trees")
        search.setText("")
        search.setText("search")
        self._settle()
        self.assertEqual(order(), before)

    def test_up_and_down_between_smithing_targets_refresh_the_skill_panel(self):
        from tests.action_queue.test_queue_reviews import _SMELT_IRON, _SMITH_PLATEBODY

        addon = self._herblore_addon("smith_move", (_SMELT_IRON, 5), (_SMITH_PLATEBODY, 1),
                                     inventory={"Iron ore": 50, "Iron bar": 50})
        save = addon._state.player_data
        dialog = self._menu(addon, "Smithing")
        for control, target, suffix in (
            ("actionQueueMoveUp", "forge_iron_platebody", " Iron platebody"),
            ("actionQueueMoveDown", "smelt_iron_bar", " Iron bar"),
        ):
            panel = dialog.findChild(QWidget, "actionQueuePanel")
            next(b for b in panel.findChildren(QPushButton, control) if b.isVisible() and b.isEnabled()).click()
            self._settle()
            self.assertEqual(save["current_smith"], target)
            self.assertEqual(self._count(dialog).suffix(), suffix)
            self.assertEqual(self._header(dialog).text(), "Currently training")
            tree = _find_tree_with_user_role(dialog, target)
            self.assertIn("✓", _tree_row(tree, target).text(0))

    def test_the_default_count_adds_earlier_entries_to_the_bank_and_is_never_below_one(self):
        addon = self._herblore_addon("default", inventory={})
        dialog = self._menu(addon)
        self.assertEqual(self._count(dialog).value(), 1)
        self.assertEqual(self._visible(dialog, QLabel, "queueMaterials").text(), "Grimy snake weed: 0 in Bank")

        addon = self._herblore_addon("promised", (_VINES, 5), inventory={"Grimy snake weed": 2})
        dialog = self._menu(addon)
        self.assertEqual(self._count(dialog).value(), 7)
        self.assertEqual(
            self._visible(dialog, QLabel, "queueMaterials").text().replace(" ", " "),
            "Grimy snake weed: 2 in Bank, 5 from entry 1",
        )
        self._add(dialog)
        self.assertEqual(addon._state.player_data["action_queue"]["entries"][1], {"action": _SNAKE_WEED, "count": 7})

    def test_a_supply_change_moves_an_untouched_default_and_not_a_typed_count(self):
        addon = self._herblore_addon("supplies")
        save = addon._state.player_data
        dialog = self._menu(addon)
        self.assertEqual(self._count(dialog).value(), 2)

        save["inventory"]["Grimy snake weed"] = 9
        addon.update_review_hud(save, addon._state.current_skill)
        self.assertEqual(self._count(dialog).value(), 9)

        self._count(dialog).setValue(4)
        save["inventory"]["Grimy snake weed"] = 20
        addon.update_review_hud(save, addon._state.current_skill)
        self.assertEqual(self._count(dialog).value(), 4)

        # The typed number clears with the target; nothing was added, so nothing comes back.
        self._click_row(dialog, "clean_ardrigal")
        self.assertEqual(self._count(dialog).value(), 3)
        self._click_row(dialog, "clean_snake_weed")
        self.assertEqual(self._count(dialog).value(), 20)

    def test_a_typed_count_stays_through_a_panel_redraw_until_the_target_changes(self):
        addon = self._herblore_addon("redraw", (_ARDRIGAL, 1), (_ARDRIGAL, 1))
        addon._state.player_data["inventory"]["Grimy snake weed"] = 2
        dialog = self._menu(addon)
        self._click_row(dialog, "clean_snake_weed")
        self._count(dialog).setValue(6)

        # Every queue command redraws the panel, and this one has nothing to do with the box.
        panel = dialog.findChild(QWidget, "actionQueuePanel")
        next(b for b in panel.findChildren(QToolButton, "actionQueueRemove") if b.isVisible()).click()
        self._settle()
        self.assertEqual(len(self._queue_lines(addon)), 1)
        self.assertEqual(self._count(dialog).value(), 6)

        self._click_row(dialog, "clean_ardrigal")
        self._click_row(dialog, "clean_snake_weed")
        self.assertEqual(self._count(dialog).value(), 2)

    def test_only_an_accepted_add_is_remembered(self):
        addon = self._herblore_addon("remember", (_ARDRIGAL, 1))
        addon._state.player_data["inventory"]["Grimy snake weed"] = 2
        dialog = self._menu(addon)

        self._click_row(dialog, "clean_snake_weed")
        self._count(dialog).setValue(0)
        self._add(dialog)
        self.assertEqual(self._queue_lines(addon), [("Herblore: Clean ardrigal", "current", 0)])
        self._click_row(dialog, "clean_ardrigal")
        self._click_row(dialog, "clean_snake_weed")
        self.assertEqual(self._count(dialog).value(), 2)

        self._count(dialog).setValue(6)
        self._add(dialog)
        self.assertEqual(len(self._queue_lines(addon)), 2)
        self._click_row(dialog, "clean_ardrigal")
        self._click_row(dialog, "clean_snake_weed")
        self.assertEqual(self._count(dialog).value(), 6)


if __name__ == "__main__":
    unittest.main()
