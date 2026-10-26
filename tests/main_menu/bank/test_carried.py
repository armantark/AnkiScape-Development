from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_bank_tab
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPushButton, QSpinBox
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_bank_carried_inventory_panel_is_present_and_collapsible(self) -> None:
        _open_bank_tab(self.dialog)
        summary = self.dialog.findChild(QLabel, "carriedInventorySummary")
        self.assertIsNotNone(summary)
        self.assertIn("bank run", summary.text().lower())

        # The loot-threshold spinner moved to the Equipment tab's combat controls;
        # the Bank keeps a pointer to it instead.
        self.assertIsNone(self.dialog.findChild(QSpinBox, "carriedLootThresholdSpin"))
        self.assertIsNotNone(self.dialog.findChild(QSpinBox, "combatLootThresholdSpin"))
        self.assertIsNotNone(self.dialog.findChild(QLabel, "carriedEquipmentPointer"))
        # No packing-mode dropdown: skilling packs are inferred, not player-picked.
        self.assertIsNone(self.dialog.findChild(QComboBox, "carriedPackModeCombo"))

        header = self.dialog.findChild(QPushButton, "carriedInventoryHeader")
        self.assertIsNotNone(header)
        self.assertTrue(header.isCheckable())
        body = summary.parentWidget()  # carried_summary lives directly on carried_body
        # Collapsed by default; toggling the header reveals the body. Use
        # isVisibleTo (local intent) since the Bank tab itself may be inactive.
        self.assertFalse(body.isVisibleTo(body.parentWidget()))
        self.assertIn("▸", header.text())
        header.setChecked(True)
        QApplication.processEvents()
        self.assertTrue(body.isVisibleTo(body.parentWidget()))
        self.assertIn("▾", header.text())

    def test_bank_run_refreshes_collapsed_carried_header_slot_count(self) -> None:
        carried_items = []
        dialog = self._open(
            _make_player_data(),
            get_carried_inventory_items=lambda: tuple(carried_items),
        )
        dialog.show()
        dialog.resize(900, 560)
        _open_bank_tab(dialog)
        for _ in range(4):
            QApplication.processEvents()

        header = dialog.findChild(QPushButton, "carriedInventoryHeader")
        body = dialog.findChild(QLabel, "carriedInventorySummary").parentWidget()
        self.assertFalse(header.isChecked())
        self.assertFalse(body.isVisibleTo(body.parentWidget()))

        carried_items[:] = [("Shark", 24)]
        self._ui._MAIN_MENU_CTX["refresh_carried_inventory"]()
        for _ in range(4):
            QApplication.processEvents()

        self.assertEqual(header.text(), "▸ Carried — 24/28 slots")
        self.assertFalse(body.isVisibleTo(body.parentWidget()))
        dialog.deleteLater()

    def test_bank_carried_summary_counts_stackable_quantities_as_one_slot(self) -> None:
        player_data = _make_player_data()
        player_data["carried_inventory"] = {
            "combat_target": {"Air rune": 5000, "Lobster": 2}
        }
        dialog = self._open(
            player_data,
            carried_stackable_names=frozenset({"Air rune"}),
        )
        _open_bank_tab(dialog)

        summary = dialog.findChild(QLabel, "carriedInventorySummary")
        self.assertIsNotNone(summary)
        self.assertIn("3 slot(s) held", summary.text())
        dialog.deleteLater()
