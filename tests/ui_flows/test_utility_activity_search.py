"""Search over the Utilities and Activities lists, driven through the real main menu."""

from __future__ import annotations

import unittest

from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_widget,
    _make_player_data,
    _tree_items,
    _utility_row,
)

if HAS_AQT:
    from aqt.qt import (
        QApplication,
        QEvent,
        QKeyEvent,
        QLabel,
        QLineEdit,
        QMenu,
        Qt,
        QWidget,
    )

_SEARCH = "utilityActivityTargetSearchInput"


def _pump(times: int = 4) -> None:
    for _ in range(times):
        QApplication.processEvents()


def _search_bar(tree) -> "tuple[QLineEdit, QLabel]":
    # The persistent Activities panel and the Utilities panel can both exist,
    # so the bar is read from the surface that holds this tree.
    surface = tree.parentWidget()
    return (
        surface.findChild(QLineEdit, _SEARCH),
        surface.findChild(QLabel, f"{_SEARCH}Summary"),
    )


def _is_shown(item) -> bool:
    while item is not None:
        if item.isHidden():
            return False
        item = item.parent()
    return True


def _shown_rows(tree) -> list:
    return [
        item.data(0, Qt.ItemDataRole.UserRole)
        for item in _tree_items(tree)
        if not item.childCount() and _is_shown(item)
    ]


def _header(tree, group: str):
    return _utility_row(tree, f"__utility_group__:{group}")


def _press_escape(widget) -> None:
    QApplication.sendEvent(
        widget,
        QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier),
    )
    _pump()


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class UtilityActivitySearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_utilities_search_filters_the_tree_and_clearing_restores_it(self) -> None:
        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        dialog = self.menu._open(pd)
        tree = self.menu._open_utility(dialog)
        self.assertEqual(tree.currentItem().data(0, Qt.ItemDataRole.UserRole), "bankstanding")
        search, summary = _search_bar(tree)
        self.assertEqual(search.placeholderText(), "Search utilities")
        every_row = _shown_rows(tree)
        total = len(every_row)
        self.assertEqual(summary.text(), f"Showing {total}/{total}")
        opened = {
            item.data(0, Qt.ItemDataRole.UserRole): item.isExpanded()
            for item in _tree_items(tree)
            if item.childCount()
        }

        search.setText("bowl")
        _pump()
        shown = _shown_rows(tree)
        self.assertIn("fill_bowl_of_water", shown)
        self.assertNotIn("bankstanding", shown)
        self.assertEqual(summary.text(), f"Showing {len(shown)}/{total}")
        cooking_prep = _header(tree, "cooking_prep")
        self.assertTrue(cooking_prep.isExpanded())
        visible_prep = [
            cooking_prep.child(index)
            for index in range(cooking_prep.childCount())
            if not cooking_prep.child(index).isHidden()
        ]
        self.assertEqual(cooking_prep.text(0), f"Cooking prep  ({len(visible_prep)})")

        search.setText("zzzqx")
        _pump()
        empty = [tree.topLevelItem(i) for i in range(tree.topLevelItemCount()) if not tree.topLevelItem(i).isHidden()]
        self.assertEqual([item.text(0) for item in empty], ["No utilities match this search."])
        self.assertEqual(empty[0].flags(), Qt.ItemFlag.NoItemFlags)
        self.assertEqual(summary.text(), f"Showing 0/{total}")

        _press_escape(search)
        self.assertEqual(search.text(), "")
        self.assertEqual(_shown_rows(tree), every_row)
        self.assertEqual(summary.text(), f"Showing {total}/{total}")
        self.assertEqual(
            {
                item.data(0, Qt.ItemDataRole.UserRole): item.isExpanded()
                for item in _tree_items(tree)
                if item.childCount()
            },
            opened,
        )
        self.assertEqual(tree.currentItem().data(0, Qt.ItemDataRole.UserRole), "bankstanding")
        # Typing never selects or starts a utility.
        self.assertEqual(pd["current_utility"], "bankstanding")
        self.assertEqual(self.menu._utility_calls, [])
        dialog.deleteLater()

    def test_utilities_search_ranks_within_group_and_clearing_restores_order(self) -> None:
        from ankiscape.core.search_match import match_rank

        dialog = self.menu._open(_make_player_data())
        tree = self.menu._open_utility(dialog)
        search, _summary = _search_bar(tree)
        original = _shown_rows(tree)
        search.setText("gather")
        _pump()
        group = _header(tree, "gathering")
        shown = [group.child(index) for index in range(group.childCount()) if not group.child(index).isHidden()]
        ranks = [match_rank("gather", row.text(0), "gathering") for row in shown]
        self.assertEqual(ranks, sorted(ranks))
        keys = [row.data(0, Qt.ItemDataRole.UserRole) for row in shown]
        self.assertLess(keys.index("gather_snape_grass"), keys.index("pick_nettles"))
        search.clear()
        _pump()
        self.assertEqual(_shown_rows(tree), original)
        self.assertEqual(self.menu._utility_calls, [])

    def test_activities_search_ranks_within_flat_group_and_clearing_restores_order(self) -> None:
        dialog = self.menu._open(_make_player_data())
        tree = self.menu._open_activities(dialog)
        selection = _find_named_widget(dialog, "skillListWidget")
        selection.setCurrentItem(selection.item(2))
        _pump()
        search, _summary = _search_bar(tree)
        original = _shown_rows(tree)
        search.setText("and")
        _pump()
        self.assertEqual(_shown_rows(tree)[0], "penguin_hide_and_seek")
        self.assertEqual(set(_shown_rows(tree)), set(original))
        search.clear()
        _pump()
        self.assertEqual(_shown_rows(tree), original)
        self.assertEqual(self.menu._utility_calls, [])

    def test_mage_arena_nested_rows_rank_and_restore_without_changing_activity(self) -> None:
        from ankiscape.core.search_match import match_rank
        pd = _make_player_data()
        pd["current_utility"] = "bankstanding"
        pd["mage_arena"] = {"completed": True, "step": 5, "alignment": "guthix"}
        pd["magic_level"] = 60
        dialog = self.menu._open(pd)
        tree = self.menu._open_activities(dialog)
        dialog.show()
        dialog.resize(720, 560)
        _pump(8)
        group = next(item for item in _tree_items(tree) if item.text(0) == "Mage Arena statues")
        original = [group.child(i).text(0) for i in range(group.childCount())]
        search, _summary = _search_bar(tree)
        search.setText("s")
        _pump()
        shown = [group.child(i) for i in range(group.childCount()) if _is_shown(group.child(i))]
        ranks = [match_rank("s", item.text(0), "landmarks", "Landmarks", "Mage Arena statues") for item in shown]
        self.assertGreater(len(set(ranks)), 1)
        self.assertEqual(ranks, sorted(ranks))
        self.assertEqual(shown[0].data(0, Qt.ItemDataRole.UserRole), "__mage_cape__:saradomin")
        search.clear()
        _pump()
        self.assertEqual([group.child(i).text(0) for i in range(group.childCount())], original)
        self.assertEqual(self.menu._utility_calls, [])
        self.assertEqual(pd["current_utility"], "bankstanding")

    def test_activities_search_keeps_slices_menus_cards_and_saved_collapses(self) -> None:
        from ankiscape.data.evil_tree_data import EVIL_TREE_UTILITY_ID
        from ankiscape.logic.dnd_favourites_logic import toggle_dnd_favourite_pure

        ui = self.menu._ui

        class _FakeCol:
            def __init__(self) -> None:
                self._cfg: dict = {}

            def get_config(self, key, default=None):
                return self._cfg.get(key, default)

            def set_config(self, key, value):
                self._cfg[key] = value

        # Subclass QWidget so show_main_menu can still parent its QDialog to mw.
        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()

        pd = _make_player_data()
        pd["current_utility"] = "livid_farm"

        def _favourite(activity_id):
            updated, ok, info = toggle_dnd_favourite_pure(pd, activity_id)
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, **info}

        orig_mw = ui.mw
        ui.mw = _FakeMw()
        try:
            dialog = self.menu._open(pd, on_favourite_dnd=_favourite)
            tree = self.menu._open_activities(dialog)
            dialog.show()
            dialog.resize(1000, 560)
            _pump(8)
            search, summary = _search_bar(tree)
            self.assertEqual(search.placeholderText(), "Search activities")
            _header(tree, "warriors_guild").setExpanded(False)
            _pump()
            saved = ui.mw.col.get_config("ankiscape_activity_collapsed_groups")
            self.assertEqual(saved, ["warriors_guild"])

            # A match inside a collapsed group opens it without saving that.
            search.setText("keg")
            _pump()
            self.assertIn("warriors_guild_keg_balance", _shown_rows(tree))
            self.assertTrue(_header(tree, "warriors_guild").isExpanded())
            # A group's label finds every row in the group.
            search.setText("landmarks")
            _pump()
            landmarks = _header(tree, "landmarks")
            self.assertTrue(_is_shown(landmarks))
            self.assertIn("stronghold_of_security", _shown_rows(tree))
            self.assertEqual(summary.text().split("/")[0], f"Showing {len(_shown_rows(tree))}")
            self.assertEqual(ui.mw.col.get_config("ankiscape_activity_collapsed_groups"), saved)

            # The hub's D&D slice filters through the same query.
            selection = _find_named_widget(dialog, "skillListWidget")
            selection.setCurrentItem(selection.item(2))
            _pump()
            search.setText("evil")
            _pump()
            self.assertIn(EVIL_TREE_UTILITY_ID, _shown_rows(tree))
            self.assertNotIn("stronghold_of_security", _shown_rows(tree))

            shown_menus: list = []
            original_exec = QMenu.exec
            QMenu.exec = lambda menu, *_args: shown_menus.append(menu)  # type: ignore[method-assign]
            try:
                evil_row = _utility_row(tree, EVIL_TREE_UTILITY_ID)
                tree.scrollToItem(evil_row)
                _pump()
                tree.customContextMenuRequested.emit(tree.visualItemRect(evil_row).center())
                _pump()
            finally:
                QMenu.exec = original_exec  # type: ignore[method-assign]
            action = shown_menus[-1].actions()[0]
            self.assertEqual(action.text(), "Add to notifications")
            action.trigger()
            _pump()
            self.assertEqual(pd["dnd_favourites"], [EVIL_TREE_UTILITY_ID])

            # Its detail card replaces the list and the bar; going back keeps the query.
            tree.itemClicked.emit(evil_row, 0)
            _pump()
            self.assertTrue(_find_named_widget(dialog, "evilTreePanel").isVisible())
            self.assertFalse(search.isVisible())
            _find_named_button(dialog, "activityChooseAnotherButton").click()
            _pump()
            self.assertTrue(search.isVisible())
            self.assertEqual(search.text(), "evil")
            self.assertIn(EVIL_TREE_UTILITY_ID, _shown_rows(tree))

            selection.setCurrentItem(selection.item(0))
            _pump()
            _press_escape(search)
            self.assertFalse(_header(tree, "warriors_guild").isExpanded())
            self.assertEqual(ui.mw.col.get_config("ankiscape_activity_collapsed_groups"), saved)
            self.assertEqual(pd["current_utility"], "livid_farm")
            self.assertEqual(self.menu._utility_calls, [])
            dialog.deleteLater()
        finally:
            ui.mw = orig_mw


if __name__ == "__main__":
    unittest.main()
