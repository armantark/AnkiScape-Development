from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _utility_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QMessageBox, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_livid_farm_panel_exposes_progress_and_persists_routine(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "magic_level": 99,
                "agility_level": 60,
                "crafting_level": 60,
                "farming_level": 60,
                "construction_level": 50,
                "current_utility": "livid_farm",
            }
        )
        pd["quests"]["lunar_diplomacy"] = {"completed": True}
        pd["livid_farm"] = {
            "farm_routine": "complete",
            "produce_points": 227_900,
            "lifetime_produce_points": 227_900,
            "cycles_completed": 8,
            "unlocked_spells": [
                "south_falador_teleport",
                "repair_rune_pouch",
                "north_ardougne_teleport",
            ],
        }
        dialog = self._open(pd)
        utility_tree = self._open_activity_detail(dialog, "livid_farm")
        dialog.show()
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "lividFarmPanel")
        self.assertTrue(panel.isVisible())
        status = _find_named_label(dialog, "lividFarmStatus")
        self.assertIn("227,900 banked", status.text())
        self.assertIn("8 cycles", status.text())
        progress = _find_named_widget(dialog, "lividFarmUnlockProgress")
        self.assertEqual(progress.maximum(), 87_360)
        self.assertEqual(progress.value(), 780)
        self.assertIn("Next: Remote Farm", progress.format())
        self.assertIn("text-align: center", progress.styleSheet())
        row = _utility_row(utility_tree, "livid_farm")
        self.assertFalse(row.icon(0).isNull())

        routine = _find_named_widget(dialog, "lividFarmRoutine")
        self.assertIsInstance(routine, QComboBox)
        routine.setCurrentIndex(routine.findData("conserve"))
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            ("set_routine", {"routine": "conserve"}),
        )
        self.assertEqual(pd["livid_farm"]["farm_routine"], "conserve")

    def test_livid_farm_wish_surface_is_compact_honest_and_actionable(self) -> None:
        pd = _make_player_data()
        pd.update(
            {
                "magic_level": 99,
                "agility_level": 60,
                "crafting_level": 60,
                "farming_level": 60,
                "construction_level": 50,
                "current_utility": "livid_farm",
            }
        )
        pd["quests"]["lunar_diplomacy"] = {"completed": True}
        pd["livid_farm"] = {
            "borrowed_power_claimed": True,
            "produce_points": 73_000,
            "lifetime_produce_points": 900_000,
            "unlocked_spells": ["borrowed_power"],
        }
        dialog = self._open(pd)
        self._open_activity_detail(dialog, "livid_farm")
        dialog.show()
        QApplication.processEvents()

        picker = _find_named_widget(dialog, "lividFarmWishPicker")
        button = _find_named_widget(dialog, "lividFarmWishButton")
        status = _find_named_label(dialog, "lividFarmStatus")
        panel = _find_named_widget(dialog, "lividFarmPanel")
        self.assertIsInstance(picker, QComboBox)
        self.assertEqual(picker.count(), 10)
        self.assertTrue(button.isVisible())
        dialog.resize(900, 560)
        for _ in range(8):
            QApplication.processEvents()
        button_right = button.mapTo(
            panel,
            button.rect().bottomRight(),
        ).x()
        self.assertLessEqual(button_right, panel.contentsRect().right())
        button_bottom = button.mapTo(
            panel,
            button.rect().bottomRight(),
        ).y()
        self.assertLessEqual(button_bottom, panel.contentsRect().bottom())
        self.assertGreaterEqual(button.height(), 28)
        self.assertGreaterEqual(picker.height(), 28)

        blocked_index = picker.findData("rain_seeds")
        picker.setCurrentIndex(blocked_index)
        QApplication.processEvents()
        self.assertFalse(button.isEnabled())
        self.assertIn("not sourced", status.text())
        self.assertIsNotNone(
            picker.itemData(
                blocked_index,
                Qt.ItemDataRole.ForegroundRole,
            )
        )

        ready_index = picker.findData("gimme_herbs")
        picker.setCurrentIndex(ready_index)
        QApplication.processEvents()
        self.assertTrue(button.isEnabled())
        self.assertIn("18,000", button.text())
        button.click()
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            ("buy_wish", {"wish_id": "gimme_herbs"}),
        )
        self.assertEqual(pd["inventory"]["Grimy kwuarm"], 3)
        self.assertEqual(pd["livid_farm"]["produce_points"], 55_000)

    def test_livid_farm_capacitor_surface_charges_and_removes_atomically(self) -> None:
        from ankiscape.data.livid_farm_data import (
            ARCANE_CAPACITOR_CHARGED,
            ARCANE_CAPACITOR_UNCHARGED,
        )

        pd = _make_player_data()
        pd.update(
            {
                "magic_level": 98,
                "agility_level": 60,
                "crafting_level": 60,
                "farming_level": 60,
                "construction_level": 50,
                "current_utility": "livid_farm",
            }
        )
        pd["quests"]["lunar_diplomacy"] = {"completed": True}
        pd["inventory"].update(
            {
                ARCANE_CAPACITOR_UNCHARGED: 1,
                "Air rune": 1_000,
                "Earth rune": 1_000,
                "Law rune": 1_000,
            }
        )
        pd["livid_farm"] = {
            "borrowed_power_claimed": True,
            "produce_points": 0,
            "unlocked_spells": ["borrowed_power"],
        }
        dialog = self._open(pd)
        self._open_activity_detail(dialog, "livid_farm")
        dialog.show()
        QApplication.processEvents()

        row = _find_named_widget(dialog, "lividFarmCapacitorRow")
        status = _find_named_label(dialog, "lividFarmCapacitorStatus")
        picker = _find_named_widget(dialog, "lividFarmCapacitorSpell")
        charge = _find_named_widget(dialog, "lividFarmCapacitorCharge")
        remove = _find_named_widget(dialog, "lividFarmCapacitorRemove")
        self.assertTrue(row.isVisible())
        self.assertEqual(status.text(), "Capacitor · Uncharged")
        house_index = picker.findData("teleport_to_house")
        self.assertGreaterEqual(house_index, 0)
        picker.setCurrentIndex(house_index)
        QApplication.processEvents()
        self.assertFalse(charge.isEnabled())
        self.assertEqual(charge.toolTip(), "Requires Magic level 99.")

        pd["magic_level"] = 99
        picker.setCurrentIndex((house_index + 1) % picker.count())
        picker.setCurrentIndex(house_index)
        QApplication.processEvents()
        self.assertTrue(charge.isEnabled())
        self.assertEqual(charge.toolTip(), "")

        charge.click()
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            (
                "charge_capacitor",
                {"spell_id": "teleport_to_house"},
            ),
        )
        self.assertEqual(pd["inventory"][ARCANE_CAPACITOR_CHARGED], 1)
        self.assertNotIn(ARCANE_CAPACITOR_UNCHARGED, pd["inventory"])
        self.assertEqual(status.text(), "Capacitor · 1,000")
        self.assertIn("1,000 charges remaining", status.toolTip())
        self.assertTrue(remove.isEnabled())

        calls_before_cancel = len(self._livid_farm_calls)
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            remove.click()
        QApplication.processEvents()
        self.assertEqual(len(self._livid_farm_calls), calls_before_cancel)
        self.assertEqual(pd["inventory"][ARCANE_CAPACITOR_CHARGED], 1)

        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            remove.click()
        QApplication.processEvents()

        self.assertEqual(
            self._livid_farm_calls[-1],
            ("remove_capacitor_charge", {}),
        )
        self.assertNotIn(ARCANE_CAPACITOR_CHARGED, pd["inventory"])
        self.assertEqual(pd["inventory"]["Air rune"], 1_000)
        self.assertEqual(pd["inventory"]["Earth rune"], 1_000)
        self.assertEqual(pd["inventory"]["Law rune"], 1_000)
