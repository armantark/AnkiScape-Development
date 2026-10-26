from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_named_button,
    _find_named_label,
    _find_named_widget,
    _make_player_data,
    _open_reward_target,
    _utility_row,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QProgressBar, QScrollArea, QToolButton, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_fist_of_guthix_card_tutorial_policy_live_state_and_shop(self) -> None:
        from ankiscape.logic.fist_of_guthix_logic import (
            default_fist_of_guthix_state_pure,
            start_fist_of_guthix_match_pure,
        )

        pd = _make_player_data()
        pd.update(
            {
                "fist_of_guthix": default_fist_of_guthix_state_pure(),
                "equipment_instances": {},
                "equipment_instance_next_id": 1,
            }
        )
        pd["fist_of_guthix"]["tokens"] = 100
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        fog_row = _utility_row(activity_tree, "fist_of_guthix")
        activity_tree.setCurrentItem(fog_row)
        activity_tree.itemActivated.emit(fog_row, 0)
        QApplication.processEvents()

        details = _find_named_widget(dialog, "utilityActivityDetailsStack")
        panel = _find_named_widget(dialog, "fistOfGuthixPanel")
        primary = _find_named_button(dialog, "fistOfGuthixPrimaryButton")
        self.assertEqual(details.currentWidget(), panel)
        self.assertEqual(primary.text(), "Talk to Fiara")
        self.assertFalse(panel.findChild(QProgressBar, "fistOfGuthixChargeProgress").isVisible())

        primary.click()
        QApplication.processEvents()
        self.assertTrue(pd["fist_of_guthix"]["tutorial_complete"])
        self.assertEqual(primary.text(), "Start activity")
        self.assertNotIn("current_utility", pd)
        self.assertEqual(self._activity_start_calls, [])

        primary.click()
        QApplication.processEvents()
        self.assertEqual(self._activity_start_calls, ["fist_of_guthix"])
        self.assertEqual(pd["current_utility"], "fist_of_guthix")
        self.assertEqual(primary.text(), "Active for reviews")

        mode = dialog.findChild(QComboBox, "fistOfGuthixAutomationMode")
        stance = dialog.findChild(QComboBox, "fistOfGuthixStance")
        mode.setCurrentIndex(mode.findData("advanced"))
        stance.setCurrentIndex(stance.findData("centre"))
        QApplication.processEvents()
        self.assertEqual(pd["fist_of_guthix"]["automation_mode"], "advanced")
        self.assertEqual(pd["fist_of_guthix"]["selected_stance"], "centre")

        self.assertIsNone(dialog.findChild(QToolButton, "fistOfGuthixShopToggle"))
        reward_page = _open_reward_target(dialog, "fist_of_guthix")
        shop = reward_page.findChild(QWidget, "fistOfGuthixShop")
        self.assertTrue(shop.isVisibleTo(dialog))
        buy = _find_named_button(dialog, "fistOfGuthixBuyButton")
        self.assertTrue(buy.isEnabled())
        buy.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Combat hood 100"], 1)

        active, ok, _ = start_fist_of_guthix_match_pure(
            pd, iter((0.3, 0.5, 0.2, 0.8, 0.1)).__next__
        )
        self.assertTrue(ok)
        match = active["fist_of_guthix"]["active_match"]
        match["first_player_role"] = "hunted"
        match["player_role"] = "hunted"
        match["player_stance"] = "centre"
        match["player_charges"] = 1_240
        pd.clear()
        pd.update(active)
        live_dialog = self._open(pd)
        live_tree = self._open_activities(live_dialog)
        live_fog_row = _utility_row(live_tree, "fist_of_guthix")
        live_tree.setCurrentItem(live_fog_row)
        live_tree.itemActivated.emit(live_fog_row, 0)
        QApplication.processEvents()
        status = _find_named_label(live_dialog, "fistOfGuthixStatusChip")
        charge = live_dialog.findChild(
            QProgressBar, "fistOfGuthixChargeProgress"
        )
        self.assertEqual(status.text(), "HUNTED · ROUND 1/2")
        self.assertFalse(charge.isHidden())
        self.assertEqual(charge.value(), 1_240)
        self.assertIsNone(panel.findChild(QScrollArea))
