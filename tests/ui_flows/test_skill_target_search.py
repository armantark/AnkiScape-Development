"""Search over the Skills-tab target lists, driven through the real main menu."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import (
    HAS_AQT,
    _craft_family_node,
    _find_named_line_edit,
    _goto_crafting,
    _make_player_data,
)

if HAS_AQT:
    from aqt.qt import (
        QApplication,
        QEvent,
        QKeyEvent,
        QLabel,
        QListWidget,
        Qt,
        QTreeWidget,
        QWidget,
    )


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class SkillTargetSearchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()

    def tearDown(self) -> None:
        self.menu.tearDown()

    def test_every_skill_target_list_filters_through_its_own_search_bar(self) -> None:
        for skill in (
            "Mining", "Woodcutting", "Smithing", "Crafting", "Fletching",
            "Firemaking", "Fishing", "Hunter", "Cooking", "Runecrafting",
            "Herblore", "Prayer", "Magic", "Construction", "Thieving",
            "Agility", "Summoning", "Combat",
        ):
            with self.subTest(skill=skill):
                dialog = self.menu._open(_make_player_data(), current_skill=skill)
                key = skill.lower()
                search = _find_named_line_edit(dialog, f"{key}TargetSearchInput")
                summary = dialog.findChild(QLabel, f"{key}TargetSearchInputSummary")
                total = int(summary.text().rsplit("/", 1)[1])
                self.assertGreater(total, 0)
                self.assertEqual(summary.text(), f"Showing {total}/{total}")

                search.setText("no-such-target-anywhere")
                QApplication.processEvents()
                self.assertEqual(summary.text(), f"Showing 0/{total}")
                selector = dialog.findChild(QListWidget, f"{key}TargetTree")
                self.assertEqual(selector.count(), 1)
                self.assertEqual(selector.item(0).flags(), Qt.ItemFlag.NoItemFlags)
                dialog.deleteLater()

    def test_nettle_tea_search_names_the_product_and_readable_drinks_group(self) -> None:
        from tests.test_main_menu_widget import _cooking_family_node, _goto_cooking
        from tests.ui_flows.qt_text_fit import text_fit_defects

        data = _make_player_data()
        data["cooking_level"] = 20
        data["inventory"]["Nettle-water"] = 1
        dialog = self.menu._open(data, current_skill="Cooking")
        dialog.show()
        dialog.resize(720, 560)
        tree = _goto_cooking(dialog)
        self.assertEqual(_cooking_family_node(tree, "drinks").text(0), "Drinks  (1)")
        search = _find_named_line_edit(dialog, "cookingTargetSearchInput")
        search.setText("nettle tea")
        for _ in range(6):
            QApplication.processEvents()
        selector = dialog.findChild(QListWidget, "cookingTargetTree")
        self.assertEqual(selector.count(), 1)
        row = selector.item(0)
        self.assertEqual(row.data(Qt.ItemDataRole.UserRole), "cook_nettle_tea")
        self.assertEqual(row.text(), "Make nettle tea (Lvl 20)")
        self.assertTrue(row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertEqual(text_fit_defects(selector.parentWidget()), [])

    def test_snape_grass_gathering_names_the_site_and_is_selectable(self) -> None:
        from tests.test_main_menu_widget import _utility_row
        from tests.ui_flows.qt_text_fit import text_fit_defects

        dialog = self.menu._open(_make_player_data())
        dialog.show()
        dialog.resize(720, 560)
        tree = self.menu._open_utility(dialog)
        row = _utility_row(tree, "gather_snape_grass")
        row.parent().setExpanded(True)
        tree.scrollToItem(row)
        for _ in range(6):
            QApplication.processEvents()
        self.assertEqual(row.text(0), "Gather snape grass")
        self.assertIn("Hobgoblin Peninsula", row.toolTip(0))
        self.assertTrue(row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertFalse(row.icon(0).isNull())
        rect = tree.visualItemRect(row)
        metrics = tree.fontMetrics()
        text_width = max(metrics.horizontalAdvance(line) for line in row.text(0).splitlines())
        self.assertLessEqual(text_width + tree.iconSize().width() + 12, rect.width())
        self.assertIn("Processes up to 3 per successful card. No skill XP.", row.toolTip(0))
        self.assertIn("No materials required", row.toolTip(0))
        self.assertEqual(text_fit_defects(tree.parentWidget()), [])
        tree.itemClicked.emit(row, 0)
        self.assertEqual(self.menu._utility_calls, ["gather_snape_grass"])

    def test_crafting_search_opens_matching_families_without_selecting_or_saving(self) -> None:
        ui = self.menu._ui

        class _FakeCol:
            def __init__(self) -> None:
                self._cfg: dict = {"ankiscape_craft_expanded_families": ["pottery"]}
                # Settings suggests a world-day length from an empty review log.
                self.sched = SimpleNamespace(day_cutoff=0)
                self.db = SimpleNamespace(all=lambda *_query: [])

            def get_config(self, key, default=None):
                return self._cfg.get(key, default)

            def set_config(self, key, value):
                self._cfg[key] = value

        # Subclass QWidget so show_main_menu can still parent its QDialog to mw.
        class _FakeMw(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.col = _FakeCol()

        orig_mw = ui.mw
        ui.mw = _FakeMw()
        try:
            pd = _make_player_data()
            pd["inventory"] = {"Gold bar": 5, "Ring mould": 1}
            pd["crafting_level"] = 99
            pd["current_craft"] = "jewellery_gold_ring"
            dialog = self.menu._open(pd)
            _goto_crafting(dialog)
            search = _find_named_line_edit(dialog, "craftingTargetSearchInput")
            summary = dialog.findChild(QLabel, "craftingTargetSearchInputSummary")
            total = int(summary.text().rsplit("/", 1)[1])
            # A group the player opens before searching stays open after it.
            tree = dialog.findChild(QTreeWidget, "craftingTargetTree")
            _craft_family_node(tree, "leather").setExpanded(True)
            QApplication.processEvents()

            # A family name matches every row in it, although no row label says it.
            search.setText("combinations")
            QApplication.processEvents()
            tree = dialog.findChild(QTreeWidget, "craftingTargetTree")
            self.assertEqual(tree.topLevelItemCount(), 1)
            combinations = _craft_family_node(tree, "combination")
            self.assertTrue(combinations.isExpanded())
            self.assertEqual(summary.text(), f"Showing {combinations.childCount()}/{total}")
            self.assertIsNone(tree.currentItem())
            self.assertEqual(
                ui.mw.col.get_config("ankiscape_craft_expanded_families"),
                ["leather", "pottery"],
            )

            search.setText("sapphire necklace")
            QApplication.processEvents()
            flat = dialog.findChild(QListWidget, "craftingTargetTree")
            self.assertEqual(
                [flat.item(i).data(Qt.ItemDataRole.UserRole) for i in range(flat.count())],
                ["jewellery_sapphire_necklace"],
            )

            QApplication.sendEvent(
                search,
                QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Escape, Qt.KeyboardModifier.NoModifier),
            )
            QApplication.processEvents()
            self.assertEqual(search.text(), "")
            self.assertEqual(summary.text(), f"Showing {total}/{total}")
            tree = dialog.findChild(QTreeWidget, "craftingTargetTree")
            self.assertEqual(
                tree.currentItem().data(0, Qt.ItemDataRole.UserRole), "jewellery_gold_ring"
            )
            self.assertTrue(_craft_family_node(tree, "jewellery").isExpanded())
            self.assertTrue(_craft_family_node(tree, "pottery").isExpanded())
            self.assertTrue(_craft_family_node(tree, "leather").isExpanded())
            self.assertFalse(_craft_family_node(tree, "combination").isExpanded())
            self.assertEqual(pd["current_craft"], "jewellery_gold_ring")
            self.assertEqual(self.menu._craft_calls, [])
            dialog.deleteLater()
        finally:
            ui.mw = orig_mw


if __name__ == "__main__":
    unittest.main()
