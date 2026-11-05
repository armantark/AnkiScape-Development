"""Pass 21 review regressions through the shown menu widgets."""

import unittest
from tests import test_main_menu_widget as menu
from tests.main_menu import fixtures

if menu.HAS_AQT:
    from aqt.qt import QApplication, QLabel, QScrollArea, QSpinBox, QToolButton, Qt


@unittest.skipUnless(menu.HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ReviewFixWidgetTest(fixtures.MainMenuWidgetTest):
    def _pump(self):
        for _ in range(8):
            QApplication.processEvents()

    def _shown(self, player, skill="Mining", size=(900, 560)):
        dialog = self._open(player, current_skill=skill)
        dialog.show()
        dialog.resize(*size)
        self._pump()
        return dialog

    def test_shop_viewport_shows_a_complete_card_row_after_purchase(self):
        for size in ((720, 540), (900, 560)):
            with self.subTest(size=size):
                player = menu._make_player_data()
                player["inventory"]["Coins"] = 20000
                dialog = self._shown(player, size=size)
                menu._open_shop_tab(dialog)
                menu._find_named_line_edit(dialog, "shopSearchInput").setText("hatchet")
                selector = menu._find_named_list(dialog, "shopSelectionList")
                item = next(selector.item(i) for i in range(selector.count())
                            if (selector.item(i).data(Qt.ItemDataRole.UserRole) or {}).get("shop_id") == "bobs_brilliant_axes")
                selector.setCurrentItem(item)
                selector.itemClicked.emit(item)
                self._pump()
                menu._find_named_button(dialog, "shopTransactionButton").click()
                self._pump()
                scroll = dialog.findChild(QScrollArea, "shopStockScroll")
                first = next(button for button in scroll.findChildren(QToolButton) if button.property("shopRowId"))
                self.assertLessEqual(first.geometry().bottom(), scroll.parentWidget().height() - scroll.y() - scroll.frameWidth() - 1)
                self.assertLessEqual(first.geometry().bottom(), scroll.viewport().height() - 1)

    def test_utilities_viewport_ends_after_a_whole_sawmill_row(self):
        dialog = self._shown(menu._make_player_data())
        tree = self._open_utility(dialog)
        menu._find_named_line_edit(tree.parentWidget(), "utilityActivityTargetSearchInput").setText("sawmill")
        self._pump()
        for position in (0, tree.verticalScrollBar().maximum()):
            tree.verticalScrollBar().setValue(position)
            self._pump()
            for item in menu._tree_items(tree):
                rect = tree.visualItemRect(item)
                if not item.isHidden() and rect.top() < tree.viewport().height() and rect.bottom() >= 0:
                    self.assertLessEqual(rect.bottom(), tree.viewport().height() - 1, item.text(0))

    def test_construction_add_counts_all_nail_types(self):
        player = menu._make_player_data()
        player.update(construction_level=99, house_owned=True, house_rooms_bought={"parlour": True},
                      current_construction="crude_wooden_chair", inventory={"Plank": 20, "Bronze nails": 6, "Iron nails": 8})
        dialog = self._shown(player, "Construction")
        materials = next(label for label in dialog.findChildren(QLabel, "queueMaterials") if label.isVisible())
        count = next(box for box in dialog.findChildren(QSpinBox, "queueCountBox") if box.isVisible())
        self.assertIn("Nails: 14 in Bank", materials.text().replace("\xa0", " "))
        self.assertEqual(count.value(), 28)

    def test_flat_quest_lock_uses_the_same_dim_color_as_a_plan_row(self):
        from ankiscape.ui.ui_palette import dim_text_css

        dialog = self._shown(menu._make_player_data(), "Firemaking")
        target = menu._find_list_with_user_role(dialog, "logs")
        self.assertIn(f"QListWidget::item:disabled {{ color: {dim_text_css(target)}; }}", target.styleSheet())

    def test_diary_deed_has_one_shared_access_gates_label(self):
        dialog = self._shown(menu._make_player_data())
        menu._open_achievements_tab(dialog)
        menu._find_named_line_edit(dialog, "cabinetSearch").setText("Moon Over Catherby")
        self._pump()
        labels = [label.text() for label in dialog.findChildren(QLabel)]
        self.assertTrue(any("Access gates — Level 87 Magic · Complete Lunar Diplomacy" in text for text in labels), [text for text in labels if "Access gate" in text])
