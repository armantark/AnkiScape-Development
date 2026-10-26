from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QLabel, QPushButton, QScrollArea, QToolButton
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_farming_jade_vine_policy_and_seed_recovery_are_visible_direct_actions(self) -> None:
        player_data = _make_player_data()
        player_data["quests"]["back_to_my_roots"] = {"completed": True}
        player_data["farming_level"] = 53
        player_data["inventory"]["Jade vine seed"] = 0
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(
            QToolButton, "farmingLocationToggle::ardougne"
        ).click()
        QApplication.processEvents()
        dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::handelmort_jade_vine",
        ).click()
        QApplication.processEvents()
        policy = dialog.findChild(
            QComboBox,
            "farmingJadeVinePolicyCombo::handelmort_jade_vine",
        )
        status = dialog.findChild(
            QLabel,
            "farmingJadeVineStatus::handelmort_jade_vine",
        )
        claim = dialog.findChild(
            QPushButton,
            "farmingJadeVineClaimSeed::handelmort_jade_vine",
        )
        self.assertIsNotNone(policy)
        self.assertEqual(policy.count(), 3)
        self.assertIn("Keep tame", status.text())
        self.assertTrue(claim.isEnabled())

        policy.setCurrentIndex(policy.findData("train_slayer"))
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["farm_jade_vine_policy"], "train_slayer")
        claim = dialog.findChild(
            QPushButton,
            "farmingJadeVineClaimSeed::handelmort_jade_vine",
        )
        claim.click()
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["inventory"]["Jade vine seed"], 1)
        dialog.deleteLater()

    def test_farming_jade_vine_horacio_payment_is_disclosed_and_confirmed(self) -> None:
        from ankiscape.logic.farming_logic import default_farming_state_pure

        player_data = _make_player_data()
        player_data.update(default_farming_state_pure())
        player_data["quests"]["back_to_my_roots"] = {"completed": True}
        player_data["farming_level"] = 53
        player_data["inventory"].update({
            "Coconut": 5,
            "Watermelon": 5,
        })
        player_data["farm_patches"]["handelmort_jade_vine"].update({
            "crop_id": "jade_vine",
            "last_crop_id": "jade_vine",
            "stage": 6,
            "health_checked": True,
            "jade_state": "prunable",
            "produce_count": 0,
            "next_regrowth_at": 60,
            "plan": {
                "crop_id": "jade_vine",
                "compost_tier": "none",
                "protection_intent": False,
                "watering_intent": False,
                "cure_intent": True,
                "cure_route_preference": "item_first",
            },
        })
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::ardougne").click()
        QApplication.processEvents()
        dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::handelmort_jade_vine",
        ).click()
        QApplication.processEvents()
        policy = dialog.findChild(
            QComboBox,
            "farmingJadeVinePolicyCombo::handelmort_jade_vine",
        )
        self.assertIn("5 coconuts + 5 watermelons", policy.itemText(2))

        original_question = self._ui.QMessageBox.question
        try:
            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.No
            )
            policy.setCurrentIndex(policy.findData("train_farming"))
            QApplication.processEvents()
            self.assertEqual(player_data["farm_jade_vine_policy"], "keep_tame")
            self.assertEqual(player_data["inventory"]["Coconut"], 5)

            self._ui.QMessageBox.question = (
                lambda *a, **k: self._ui.QMessageBox.StandardButton.Yes
            )
            policy.setCurrentIndex(policy.findData("train_farming"))
            for _ in range(5):
                QApplication.processEvents()
            self.assertEqual(player_data["farm_jade_vine_policy"], "train_farming")
            self.assertEqual(player_data["inventory"]["Coconut"], 0)
            self.assertEqual(player_data["inventory"]["Watermelon"], 0)
            self.assertIsNone(
                player_data["farm_patches"]["handelmort_jade_vine"]["crop_id"]
            )
        finally:
            self._ui.QMessageBox.question = original_question
            dialog.deleteLater()

    def test_farming_willow_branch_action_is_visible_enabled_and_queueable(
        self,
    ) -> None:
        from ankiscape.logic.farming_logic import (
            advance_farm_clock_pure,
            default_farming_state_pure,
            execute_farm_field_step_pure,
        )

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        player_data.update(default_farming_state_pure())
        player_data["inventory"] = {
            "Rake": 1,
            "Spade": 1,
            "Magic secateurs": 1,
            "Willow sapling": 1,
        }
        player_data, ok, _ = execute_farm_field_step_pure(
            player_data,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "willow",
            },
        )
        self.assertTrue(ok)
        player_data, _ = advance_farm_clock_pure(
            player_data, 240, lambda: 1.0
        )
        player_data, ok, _ = execute_farm_field_step_pure(
            player_data,
            {"kind": "check_health", "patch_id": "lumbridge_tree"},
        )
        self.assertTrue(ok)
        player_data, _ = advance_farm_clock_pure(
            player_data, 30, lambda: 1.0
        )

        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(
            QToolButton,
            "farmingLocationToggle::lumbridge",
        )
        if not location.isChecked():
            location.click()
            QApplication.processEvents()
        expand = dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::lumbridge_tree",
        )
        if not expand.isChecked():
            expand.click()
            QApplication.processEvents()

        branch = dialog.findChild(
            QPushButton,
            "farmingPatchBranchButton::lumbridge_tree",
        )
        primary = dialog.findChild(
            QPushButton,
            "farmingPatchPrimaryAction::lumbridge_tree",
        )
        self.assertIsNotNone(branch)
        self.assertTrue(branch.isVisible())
        self.assertTrue(branch.isEnabled())
        self.assertEqual(branch.text(), "Queue prune 6 branches")
        self.assertEqual(primary.text(), "Queue chop")
        scroll = dialog.findChild(QScrollArea, "farmingFarmScroll")
        self.assertIsNotNone(scroll)
        scroll.ensureWidgetVisible(branch)
        for _ in range(3):
            QApplication.processEvents()
        branch_top = branch.mapTo(
            scroll.viewport(),
            branch.rect().topLeft(),
        ).y()
        branch_bottom = branch.mapTo(
            scroll.viewport(),
            branch.rect().bottomLeft(),
        ).y()
        self.assertGreaterEqual(branch_top, 0)
        self.assertLess(branch_bottom, scroll.viewport().height())

        branch.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(
            self._farming_calls[-1],
            (
                "queue_action",
                {
                    "patch_id": "lumbridge_tree",
                    "kind": "harvest",
                    "details": {},
                },
            ),
        )
        self.assertEqual(
            player_data["farm_queue"][0]["kind"],
            "harvest",
        )
        dialog.deleteLater()

    def test_farming_protection_checkbox_defers_payment_until_full_run(self) -> None:
        player_data = _make_player_data()
        player_data["farming_level"] = 1
        player_data["inventory"] = {
            "Rake": 1,
            "Seed dibber": 1,
            "Spade": 1,
            "Potato seed": 3,
            "Compost": 2,
        }
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::falador").click()
        QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingPatchExpandButton::falador_allotment_north").click()
        QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingPatchCropCombo::falador_allotment_north")
        combo.setCurrentIndex(combo.findData("potato"))
        for _ in range(4):
            QApplication.processEvents()
        protect = dialog.findChild(QCheckBox, "farmingPatchProtectionCheck::falador_allotment_north")
        protect.setChecked(True)
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(self._farming_calls[-1][0], "set_plan")
        self.assertTrue(self._farming_calls[-1][1]["protection_intent"])
        self.assertEqual(player_data["inventory"]["Compost"], 2)
        self.assertFalse(player_data["farm_plans"]["falador_allotment_north"]["protection_paid"])
        full_run = dialog.findChild(QPushButton, "farmingQueueFullRunButton")
        self.assertTrue(full_run.isEnabled())
        full_run.click()
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(player_data["inventory"]["Compost"], 0)
        self.assertFalse(player_data["farm_plans"]["falador_allotment_north"]["protection_paid"])
        self.assertTrue(player_data["farm_queue"][0]["protection_paid"])
        self.assertEqual(player_data["farm_queue"][0]["protection_payment"], {"Compost": 2})
        protect = dialog.findChild(QCheckBox, "farmingPatchProtectionCheck::falador_allotment_north")
        self.assertTrue(protect.isChecked())
        self.assertTrue(protect.isEnabled())
        dialog.deleteLater()

    def test_farming_cure_preference_is_a_compact_saved_toggle(self) -> None:
        from ankiscape.logic.farming_logic import CURE_PLANT_SPELL_FIRST, set_farm_plan_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        planned, ok, _ = set_farm_plan_pure(
            player_data,
            "falador_allotment_north",
            "potato",
        )
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(planned)
        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        dialog.findChild(QToolButton, "farmingLocationToggle::falador").click()
        QApplication.processEvents()
        dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::falador_allotment_north",
        ).click()
        QApplication.processEvents()

        combo = dialog.findChild(
            QComboBox,
            "farmingPatchCurePreferenceCombo::falador_allotment_north",
        )
        self.assertEqual(combo.count(), 2)
        self.assertEqual(combo.itemText(0), "Plant cure first")
        self.assertEqual(combo.itemText(1), "Cure Plant first")
        combo.setCurrentIndex(combo.findData(CURE_PLANT_SPELL_FIRST))
        for _ in range(5):
            QApplication.processEvents()
        self.assertEqual(
            player_data["farm_plans"]["falador_allotment_north"][
                "cure_route_preference"
            ],
            CURE_PLANT_SPELL_FIRST,
        )
        self.assertEqual(
            self._farming_calls[-1][1]["cure_route_preference"],
            CURE_PLANT_SPELL_FIRST,
        )
        dialog.deleteLater()

    def test_farming_compost_bin_selects_an_available_input_and_gates_fill_by_selection(self) -> None:
        player_data = _make_player_data()
        player_data["inventory"] = {"Potato": 15}
        dialog = self._open(player_data, current_skill="Mining", initial_skill="Farming")
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        combo = dialog.findChild(QComboBox, "farmingCompostBinInputCombo::falador_bin")
        fill = dialog.findChild(QPushButton, "farmingCompostBinFillButton::falador_bin")
        self.assertEqual(combo.currentData(), "Potato")
        self.assertTrue(fill.isEnabled())

        barley_index = combo.findData("Barley")
        self.assertGreaterEqual(barley_index, 0)
        combo.setCurrentIndex(barley_index)
        QApplication.processEvents()
        self.assertFalse(fill.isEnabled())
        combo.setCurrentIndex(combo.findData("Potato"))
        QApplication.processEvents()
        self.assertTrue(fill.isEnabled())
        fill.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(player_data["inventory"]["Potato"], 0)
        self.assertEqual(player_data["farm_compost_bins"]["falador_bin"]["status"], "filling")
        dialog.deleteLater()

    def test_farming_livid_scroll_button_activates_and_reports_remaining_uses(self) -> None:
        from ankiscape.data.farming_data import LIVID_FARM_PROTECTION_SCROLL
        from ankiscape.logic.farming_logic import execute_farm_field_step_pure

        player_data = _make_player_data()
        player_data["farming_level"] = 99
        player_data["inventory"] = {
            "Rake": 1,
            "Spade": 1,
            "Oak sapling": 1,
            LIVID_FARM_PROTECTION_SCROLL: 1,
        }
        updated, ok, _ = execute_farm_field_step_pure(
            player_data,
            {
                "kind": "plant",
                "patch_id": "lumbridge_tree",
                "crop_id": "oak",
            },
        )
        self.assertTrue(ok)
        player_data.clear()
        player_data.update(updated)

        dialog = self._open(
            player_data,
            current_skill="Mining",
            initial_skill="Farming",
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(5):
            QApplication.processEvents()
        location = dialog.findChild(
            QToolButton,
            "farmingLocationToggle::lumbridge",
        )
        if not location.isChecked():
            location.click()
            QApplication.processEvents()
        expand = dialog.findChild(
            QToolButton,
            "farmingPatchExpandButton::lumbridge_tree",
        )
        if not expand.isChecked():
            expand.click()
            QApplication.processEvents()

        button = dialog.findChild(
            QPushButton,
            "farmingPatchLividProtectionButton::lumbridge_tree",
        )
        self.assertIsNotNone(button)
        self.assertTrue(button.isEnabled())
        self.assertGreaterEqual(button.width(), button.sizeHint().width())
        self.assertIn("next nine plantings", button.toolTip())
        button.click()
        for _ in range(5):
            QApplication.processEvents()

        self.assertTrue(
            player_data["farm_patches"]["lumbridge_tree"]["livid_protected"]
        )
        self.assertEqual(
            player_data["farm_livid_protection_uses_remaining"],
            9,
        )
        status = dialog.findChild(QLabel, "farmingLividProtectionStatus")
        self.assertTrue(status.isVisible())
        self.assertIn("Oak", status.text())
        self.assertIn("9 plantings left", status.text())
        current = dialog.findChild(
            QLabel,
            "farmingPatchCurrent::lumbridge_tree",
        )
        self.assertIn("Protection: Livid scroll", current.text())
        refreshed = dialog.findChild(
            QPushButton,
            "farmingPatchLividProtectionButton::lumbridge_tree",
        )
        self.assertFalse(refreshed.isEnabled())
        dialog.deleteLater()
