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
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QMessageBox, QPushButton, QScrollArea
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_penguin_card_keeps_bank_only_visibility_ring_locked(self) -> None:
        from ankiscape.logic.penguin_hide_and_seek_logic import default_penguin_state_pure

        pd = _make_player_data()
        pd["shop_market_clock"] = {"answered_cards": 0}
        pd["penguin_hide_and_seek"] = default_penguin_state_pure()
        pd["quests"] = {
            "some_like_it_cold": {"completed": True},
            "desert_treasure": {"started": True},
        }
        pd["inventory"]["Ring of visibility"] = 1

        bank_dialog = self._open(pd)
        bank_tree = self._open_activities(bank_dialog)
        bank_tree.setCurrentItem(
            _utility_row(bank_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()
        bank_panel = _find_named_widget(bank_dialog, "penguinHideAndSeekPanel")
        bank_roster = bank_panel.findChild(QComboBox, "penguinHideAndSeekRoster")
        bank_detail = _find_named_label(bank_dialog, "penguinHideAndSeekDetail")
        self.assertEqual(bank_roster.count(), 10)
        self.assertIn("Invisible penguin locked", bank_detail.text())

        pd["carried_inventory"] = {
            "penguin_hide_and_seek": {"Ring of visibility": 1}
        }
        carried_dialog = self._open(pd)
        carried_tree = self._open_activities(carried_dialog)
        carried_tree.setCurrentItem(
            _utility_row(carried_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()
        carried_panel = _find_named_widget(
            carried_dialog,
            "penguinHideAndSeekPanel",
        )
        carried_roster = carried_panel.findChild(
            QComboBox,
            "penguinHideAndSeekRoster",
        )
        carried_detail = _find_named_label(
            carried_dialog,
            "penguinHideAndSeekDetail",
        )
        self.assertEqual(carried_roster.count(), 11)
        self.assertIn("Invisible penguin active", carried_detail.text())

        pd["carried_inventory"] = {}
        pd["equipment"]["ring"] = "Ring of visibility"
        equipped_dialog = self._open(pd)
        equipped_tree = self._open_activities(equipped_dialog)
        equipped_tree.setCurrentItem(
            _utility_row(equipped_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()
        equipped_panel = _find_named_widget(
            equipped_dialog,
            "penguinHideAndSeekPanel",
        )
        equipped_roster = equipped_panel.findChild(
            QComboBox,
            "penguinHideAndSeekRoster",
        )
        equipped_detail = _find_named_label(
            equipped_dialog,
            "penguinHideAndSeekDetail",
        )
        self.assertEqual(equipped_roster.count(), 11)
        self.assertIn("Invisible penguin active", equipped_detail.text())

    def test_penguin_selection_cancelled_by_activity_conflict_is_not_saved(self) -> None:
        from ankiscape.logic.gnome_ball_logic import enter_gnome_ball_pure

        pd = _make_player_data()
        pd.update({"equipment": {}, "activity_session": {"active_id": ""}})
        pd, ok, _info = enter_gnome_ball_pure(pd)
        self.assertTrue(ok)
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        activity_tree.setCurrentItem(
            _utility_row(activity_tree, "penguin_hide_and_seek")
        )
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "penguinHideAndSeekPanel")
        primary = _find_named_button(dialog, "penguinHideAndSeekPrimaryButton")
        calls_before = len(self._penguin_calls)
        with patch.object(
            QMessageBox,
            "question",
            return_value=QMessageBox.StandardButton.No,
        ):
            primary.click()
        QApplication.processEvents()

        self.assertEqual(len(self._penguin_calls), calls_before)
        self.assertEqual(pd["current_utility"], "gnome_ball")
        self.assertTrue(pd["gnome_ball"])
        self.assertEqual(
            pd.get("penguin_hide_and_seek", {}).get("selected_id", ""),
            "",
        )

    def test_penguin_card_selects_spy_and_redeems_points_without_scroll(self) -> None:
        from ankiscape.logic.penguin_hide_and_seek_logic import default_penguin_state_pure

        pd = _make_player_data()
        pd["shop_market_clock"] = {"answered_cards": 0}
        pd["penguin_hide_and_seek"] = default_penguin_state_pure()
        pd["penguin_hide_and_seek"]["points"] = 2
        dialog = self._open(pd)
        activity_tree = self._open_activities(dialog)
        penguin_row = _utility_row(activity_tree, "penguin_hide_and_seek")
        activity_tree.setCurrentItem(penguin_row)
        QApplication.processEvents()

        panel = _find_named_widget(dialog, "penguinHideAndSeekPanel")
        roster = panel.findChild(QComboBox, "penguinHideAndSeekRoster")
        primary = _find_named_button(dialog, "penguinHideAndSeekPrimaryButton")
        status = _find_named_label(dialog, "penguinHideAndSeekStatusChip")
        self.assertEqual(roster.count(), 10)
        self.assertIsNone(panel.findChild(QScrollArea))
        self.assertEqual(status.text(), "READY")
        self.assertEqual(status.toolTip(), "Answered-card week 1")

        selected_id = str(roster.currentData())
        primary.click()
        QApplication.processEvents()
        self.assertEqual(
            self._penguin_calls[-1],
            ("select_spy", {"spawn_id": selected_id}),
        )
        self.assertEqual(pd["current_utility"], "penguin_hide_and_seek")
        self.assertEqual(self._activity_start_calls[-1], "penguin_hide_and_seek")
        self.assertEqual(primary.text(), "Selected for next review")
        self.assertEqual(status.text(), "ACTIVE")

        next_index = 1 if roster.currentIndex() == 0 else 0
        next_id = str(roster.itemData(next_index))
        roster.setCurrentIndex(next_index)
        QApplication.processEvents()
        self.assertEqual(str(roster.currentData()), next_id)
        self.assertEqual(primary.text(), "Select for next review")
        self.assertEqual(primary.accessibleName(), primary.text())

        reward_page = _open_reward_target(dialog, "penguin_hide_and_seek")
        redeem_coins = reward_page.findChild(QPushButton, "penguinRedeemCoinsButton")
        reward_skill = reward_page.findChild(QComboBox, "penguinRewardSkill")
        self.assertTrue(redeem_coins.isVisibleTo(dialog))
        redeem_coins.click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Coins"], 13_000)
        self.assertEqual(pd["penguin_hide_and_seek"]["points"], 0)
        self.assertFalse(redeem_coins.isEnabled())
        self.assertTrue(reward_skill.isEnabled())
        self.assertNotIn("0 points for 0 coins", redeem_coins.toolTip())

        activity_tree = self._open_activities(dialog)
        activity_tree.setCurrentItem(penguin_row)
        activity_tree.itemActivated.emit(penguin_row, 0)
        QApplication.processEvents()
        dialog.resize(900, 560)
        for _ in range(6):
            QApplication.processEvents()
        panel_bottom = panel.mapTo(
            dialog,
            panel.rect().bottomRight(),
        ).y()
        self.assertLessEqual(panel_bottom, dialog.contentsRect().bottom())
