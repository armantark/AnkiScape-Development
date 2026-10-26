from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _utility_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPoint, QProgressBar, QScrollArea, QSpinBox, QTabWidget, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_managing_miscellania_card_funds_allocates_collects_and_selects(self) -> None:
        from ankiscape.logic.managing_miscellania_logic import default_managing_miscellania_state_pure

        pd = _make_player_data()
        pd.update(default_managing_miscellania_state_pure())
        pd.update(
            {
                "current_utility": "bankstanding",
                "woodcutting_level": 45,
                "inventory": {"Coins": 1_000_000},
                "shop_market_clock": {"answered_cards": 0},
            }
        )
        pd["quests"]["throne_of_miscellania"] = {"completed": True}
        pd["managing_miscellania"]["approval_basis_points"] = 9_900
        pd["managing_miscellania"]["production_credit"] = 1_000_000
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "managing_miscellania")
        self.assertFalse(row.isDisabled())
        self.assertFalse(row.icon(0).isNull())
        activity_tree.setCurrentItem(row)
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "managingMiscellaniaPanel")
        self.assertIsNone(panel.findChild(QScrollArea))
        pages = panel.findChild(QTabWidget, "managingMiscellaniaTabs")
        self.assertEqual(
            tuple(pages.tabText(index) for index in range(pages.count())),
            ("Kingdom", "Resources"),
        )
        self.assertEqual(pages.currentIndex(), 0)
        self.assertFalse(
            panel.findChild(QLabel, "managingMiscellaniaIcon").pixmap().isNull()
        )
        approval = panel.findChild(QProgressBar, "managingMiscellaniaApproval")
        chore = panel.findChild(QComboBox, "managingMiscellaniaApprovalChore")
        clock = panel.findChild(QLabel, "managingMiscellaniaClock")
        summary = panel.findChild(QLabel, "managingMiscellaniaSummary")
        preview = panel.findChild(QLabel, "managingMiscellaniaPreview")
        self.assertEqual(approval.value(), 9_900)
        self.assertEqual(chore.count(), 1)
        self.assertEqual(chore.currentData(), "chop_maple")
        self.assertIn("240 reviews", clock.text())
        self.assertIn("2.5% per day", clock.text())
        self.assertIn("Unclaimed production follows", summary.text())

        fund = _find_named_button(dialog, "managingMiscellaniaFund7Button")
        self.assertEqual(fund.text(), "7 days · +800,000")
        fund.click()
        QApplication.processEvents()
        self.assertEqual(pd["managing_miscellania"]["coffer"], 800_000)
        self.assertEqual(pd["inventory"]["Coins"], 200_000)

        pages.setCurrentIndex(1)
        QApplication.processEvents()
        wood = panel.findChild(QSpinBox, "managingMiscellaniaWorkers_wood")
        _find_named_button(dialog, "managingMiscellaniaMax_wood").click()
        QApplication.processEvents()
        self.assertEqual(wood.value(), 10)
        self.assertEqual(pd["managing_miscellania"]["allocations"]["wood"], 10)
        self.assertEqual(
            panel.findChild(QLabel, "managingMiscellaniaPips_wood").text(),
            "●" * 10,
        )
        self.assertEqual(
            _find_named_label(dialog, "managingMiscellaniaStatusChip").text(),
            "FULLY ASSIGNED",
        )
        self.assertFalse(
            panel.findChild(QComboBox, "managingMiscellaniaVariant_mining").isEnabled()
        )
        self.assertTrue(
            panel.findChild(QComboBox, "managingMiscellaniaVariant_harvesting").isEnabled()
        )
        page_one_combo_x = panel.findChild(
            QComboBox, "managingMiscellaniaVariant_harvesting"
        ).geometry().x()
        page_one_max_x = _find_named_button(
            dialog, "managingMiscellaniaMax_harvesting"
        ).geometry().x()
        self.assertIn("Maple logs ×892", preview.text())

        wood.setValue(0)
        QApplication.processEvents()
        _find_named_widget(dialog, "managingMiscellaniaWorkersNext").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(dialog, "managingMiscellaniaWorkersPage").text(),
            "2 / 2",
        )
        self.assertEqual(
            panel.findChild(
                QComboBox, "managingMiscellaniaVariant_fishing"
            ).geometry().x(),
            page_one_combo_x,
        )
        self.assertEqual(
            _find_named_button(dialog, "managingMiscellaniaMax_fishing").geometry().x(),
            page_one_max_x,
        )
        _find_named_button(dialog, "managingMiscellaniaMax_farming").click()
        QApplication.processEvents()
        self.assertIn("+32 more", preview.text())
        self.assertIn("Apple tree seed ×1", preview.toolTip())
        self.assertIn("Apple tree seed ×1", preview.accessibleDescription())
        self.assertFalse(
            _find_named_button(dialog, "managingMiscellaniaMax_farming").isEnabled()
        )

        _find_named_widget(dialog, "managingMiscellaniaWorkersNext").click()
        QApplication.processEvents()
        self.assertEqual(
            _find_named_label(dialog, "managingMiscellaniaWorkersPage").text(),
            "1 / 2",
        )
        self.assertIn(
            "10 on other page",
            _find_named_label(dialog, "managingMiscellaniaWorkersCount").text(),
        )

        panel = _find_named_widget(dialog, "managingMiscellaniaPanel")
        panel.adjustSize()
        QApplication.processEvents()
        self.assertLessEqual(panel.height(), dialog.contentsRect().height())

        _find_named_widget(dialog, "managingMiscellaniaWorkersPrevious").click()
        QApplication.processEvents()
        panel.findChild(QSpinBox, "managingMiscellaniaWorkers_farming").setValue(0)
        QApplication.processEvents()
        _find_named_widget(dialog, "managingMiscellaniaWorkersPrevious").click()
        QApplication.processEvents()
        _find_named_button(dialog, "managingMiscellaniaMax_wood").click()
        QApplication.processEvents()

        collect = _find_named_button(dialog, "managingMiscellaniaCollectButton")
        self.assertTrue(collect.isEnabled())
        collect.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Maple logs"], 892)
        self.assertEqual(pd["inventory"]["Bird's nest (seeds)"], 8)
        self.assertIn("0.00 full-output days", preview.text())

        select = _find_named_button(dialog, "managingMiscellaniaSelectButton")
        select.click()
        QApplication.processEvents()
        self.assertEqual(pd["current_utility"], "managing_miscellania")
        self.assertEqual(select.text(), "Active for reviews")

        activity_tree = _find_named_widget(dialog, "utilityActivityTree")
        landmark_groups = [
            item
            for item in (
                activity_tree.topLevelItem(index)
                for index in range(activity_tree.topLevelItemCount())
            )
            if item.data(0, Qt.ItemDataRole.UserRole)
            == "__utility_group__:landmarks"
        ]
        self.assertEqual(len(landmark_groups), 1)

        dialog.resize(1000, 560)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()
        visible_children = [
            child
            for child in panel.findChildren(
                QWidget,
                options=Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if child.isVisible()
        ]
        self.assertTrue(visible_children)
        self.assertLessEqual(
            max(child.geometry().bottom() for child in visible_children),
            panel.contentsRect().bottom(),
        )
        select_bottom = select.mapTo(dialog, QPoint(0, select.height())).y()
        chooser_top = _find_named_button(
            dialog, "activityChooseAnotherButton"
        ).mapTo(dialog, QPoint(0, 0)).y()
        self.assertLessEqual(select_bottom, chooser_top)

    def test_managing_miscellania_quest_gate_is_visible_without_hover(self) -> None:
        from ankiscape.logic.managing_miscellania_logic import default_managing_miscellania_state_pure

        pd = _make_player_data()
        pd.update(default_managing_miscellania_state_pure())
        pd["current_utility"] = "bankstanding"
        pd["quests"]["throne_of_miscellania"] = {"completed": False}
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        row = _utility_row(activity_tree, "managing_miscellania")
        self.assertFalse(row.isDisabled())
        activity_tree.itemActivated.emit(row, 0)
        QApplication.processEvents()

        self.assertEqual(
            _find_named_label(dialog, "managingMiscellaniaStatusChip").text(),
            "LOCKED",
        )
        self.assertIn(
            "Requires Throne of Miscellania",
            _find_named_label(dialog, "managingMiscellaniaSummary").text(),
        )
        self.assertIn(
            "Six cutoff resource families are available",
            _find_named_label(dialog, "managingMiscellaniaSummary").text(),
        )
        panel = _find_named_widget(dialog, "managingMiscellaniaPanel")
        self.assertFalse(
            _find_named_widget(dialog, "managingMiscellaniaCoffer").isVisible()
        )
        self.assertFalse(
            _find_named_button(dialog, "managingMiscellaniaDepositButton").isEnabled()
        )
        self.assertFalse(
            _find_named_button(dialog, "managingMiscellaniaSelectButton").isEnabled()
        )
        dialog.resize(1186, 768)
        dialog.show()
        for _ in range(8):
            QApplication.processEvents()
        visible_children = [
            child
            for child in panel.findChildren(
                QWidget,
                options=Qt.FindChildOption.FindDirectChildrenOnly,
            )
            if child.isVisible()
        ]
        self.assertTrue(visible_children)
        self.assertLessEqual(
            max(child.geometry().bottom() for child in visible_children),
            panel.contentsRect().bottom(),
        )
