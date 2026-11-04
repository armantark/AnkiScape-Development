from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _find_list_with_user_role,
    _make_player_data,
    _open_equipment_tab,
    _open_shop_tab,
    _panel_title,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QComboBox, QLabel, QListWidget, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_agility_panel_renders_flat_targets_locks_icon_and_commands(self) -> None:
        player_data = _make_player_data()
        player_data["agility_level"] = 1
        player_data["current_agility"] = "burthorpe_course"
        dialog = self._open(player_data, current_skill="Agility")
        try:
            dialog.show()
            QApplication.processEvents()
            self.assertEqual(_panel_title(dialog), "Agility — Lv 1")

            panel = dialog.findChild(QWidget, "agilitySkillPanel")
            target_list = _find_list_with_user_role(dialog, "burthorpe_course")
            self.assertIsNotNone(panel)
            self.assertEqual(
                target_list.currentItem().data(Qt.ItemDataRole.UserRole),
                "burthorpe_course",
            )

            locked = next(
                target_list.item(index)
                for index in range(target_list.count())
                if target_list.item(index).data(Qt.ItemDataRole.UserRole) == "gnome_advanced"
            )
            self.assertFalse(locked.flags() & Qt.ItemFlag.ItemIsEnabled)
            before = list(self._agility_calls)
            target_list.itemClicked.emit(locked)
            QApplication.processEvents()
            self.assertEqual(self._agility_calls, before)

            gnome = next(
                target_list.item(index)
                for index in range(target_list.count())
                if target_list.item(index).data(Qt.ItemDataRole.UserRole) == "gnome_normal"
            )
            self.assertTrue(gnome.flags() & Qt.ItemFlag.ItemIsEnabled)
            target_list.itemClicked.emit(gnome)
            QApplication.processEvents()
            self.assertEqual(self._agility_calls[-1], "gnome_normal")

            skill_list = next(
                widget
                for widget in dialog.findChildren(QListWidget)
                if "Agility" in [widget.item(i).text() for i in range(widget.count())]
            )
            agility_item = next(
                skill_list.item(i) for i in range(skill_list.count())
                if skill_list.item(i).text() == "Agility"
            )
            self.assertFalse(agility_item.icon().isNull())
            self.assertIsNotNone(dialog.findChild(QLabel, "agilityStatusLine"))
            self.assertIsNotNone(dialog.findChild(QLabel, "agilityBenefitsLine"))
            # The control row is an activity-only surface: on a course the
            # panel has no command buttons at all. Shop purchases, ticket
            # redemptions and aura activation live in the Shop and Equipment
            # tabs now.
            controls = dialog.findChild(QWidget, "agilityRewardControls")
            self.assertTrue(controls is None or not controls.isVisibleTo(dialog))
            self.assertEqual(
                [
                    button.objectName()
                    for button in dialog.findChildren(QPushButton)
                    if button.objectName().startswith("agilityCommand::")
                ],
                [],
            )
            danger_auto_stop = dialog.findChild(
                QCheckBox, "activityDangerAutoStopCheckBox"
            )
            self.assertIsNotNone(danger_auto_stop)
            self.assertTrue(danger_auto_stop.isChecked())
            self.assertIn("AnkiScape safety option", danger_auto_stop.toolTip())
            danger_auto_stop.click()
            QApplication.processEvents()
            self.assertEqual(
                self._agility_command_calls[-1],
                ("set_activity_auto_stop", {"enabled": False}),
            )
            self.assertFalse(player_data["activity_auto_stop_on_danger"])

            auto_accept = dialog.findChild(
                QCheckBox, "agilityPitAutoAcceptCheckBox"
            )
            self.assertIsNotNone(auto_accept)
            self.assertTrue(auto_accept.isChecked())
            auto_accept.click()
            QApplication.processEvents()
            self.assertEqual(
                self._agility_command_calls[-1],
                ("set_pit_auto_accept", {"enabled": False}),
            )
            self.assertFalse(player_data["agility_pit_auto_accept"])
            self.assertFalse(
                any(
                    button.text() in {"Claim Pit XP", "Gamble Pit XP"}
                    for button in dialog.findChildren(QPushButton)
                )
            )

            self.assertIsNone(
                dialog.findChild(
                    QPushButton,
                    "agilityCommand::activate_agility_cape",
                )
            )
            # While the selected target is an activity, the row appears with
            # that activity's verbs. The Pit is invitation-gated, so drive it
            # through the pending-offer flow rather than forcing state.
            player_data["agility_level"] = 99
            player_data["agility_pit_offer"] = True
            player_data["agility_pit_origin_course"] = "burthorpe_course"
            player_data["inventory"] = {"Toy mouse": 1}
            player_data["equipment"] = {}
            accept_dialog = self._open(player_data, current_skill="Agility")
            try:
                accept = accept_dialog.findChild(QPushButton, "agilityPitAcceptButton")
                self.assertIsNotNone(accept)
                accept.click()
                QApplication.processEvents()
                self.assertEqual(player_data["current_agility"], "the_pit")

                controls = accept_dialog.findChild(QWidget, "agilityRewardControls")
                self.assertIsNotNone(controls)
                self.assertTrue(controls.isVisibleTo(accept_dialog))
                toy_button = accept_dialog.findChild(QPushButton, "agilityCommand::wind_toy_mouse")
                self.assertIsNotNone(toy_button)
                toy_button.click()
                QApplication.processEvents()
                self.assertEqual(self._agility_command_calls[-1], ("wind_toy_mouse", {}))
                leave_button = accept_dialog.findChild(QPushButton, "agilityCommand::abandon")
                self.assertIsNotNone(leave_button)
                self.assertEqual(leave_button.text(), "Leave The Pit")
            finally:
                accept_dialog.deleteLater()
            for label in (
                dialog.findChild(QLabel, "agilityStatusLine"),
                dialog.findChild(QLabel, "agilityBenefitsLine"),
            ):
                self.assertIn("palette(text)", label.styleSheet())
                self.assertNotIn("palette(mid)", label.styleSheet().lower())
        finally:
            dialog.deleteLater()

    def test_agility_panel_accepts_or_declines_pending_talent_scout_offer(self) -> None:
        player_data = _make_player_data()
        player_data.update(
            {
                "agility_level": 99,
                "current_agility": "gnome_normal",
                "agility_pit_offer": True,
                "agility_pit_origin_course": "gnome_normal",
                "agility_pit_auto_accept": False,
                "equipment": {"weapon": "Dragon longsword"},
            }
        )
        dialog = self._open(player_data, current_skill="Agility")

        invitation = dialog.findChild(QWidget, "agilityPitInvitationRow")
        self.assertIsNotNone(invitation)
        accept = dialog.findChild(QPushButton, "agilityPitAcceptButton")
        self.assertIsNotNone(accept)
        accept.click()
        QApplication.processEvents()

        self.assertEqual(
            self._agility_command_calls[-1],
            ("accept_pit_offer", {}),
        )
        self.assertEqual(player_data["current_agility"], "the_pit")
        self.assertEqual(player_data["inventory"]["Dragon longsword"], 1)

        declined_data = _make_player_data()
        declined_data.update(
            {
                "agility_level": 99,
                "current_agility": "gnome_normal",
                "agility_pit_offer": True,
                "agility_pit_origin_course": "gnome_normal",
                "agility_pit_auto_accept": False,
            }
        )
        declined_dialog = self._open(declined_data, current_skill="Agility")
        decline = declined_dialog.findChild(
            QPushButton, "agilityPitDeclineButton"
        )
        self.assertIsNotNone(decline)
        decline.click()
        QApplication.processEvents()

        self.assertEqual(
            self._agility_command_calls[-1],
            ("decline_pit_offer", {}),
        )
        self.assertFalse(declined_data["agility_pit_offer"])
        self.assertIsNone(
            declined_dialog.findChild(QWidget, "agilityPitInvitationRow")
        )

    def test_agility_auto_pack_summary_replaces_combat_only_controls(self) -> None:
        from aqt.qt import QLabel, QPushButton, QComboBox

        dialog = self._open(
            _make_player_data(),
            current_skill="Agility",
            get_carried_auto_summary=lambda: (
                "Wilderness Agility Course Auto pack · 28/28 slots\n"
                "Food: Shark x28\nRequirements: ready\n"
                "Weight: 16.8 kg carried · 16.8 kg effective"
            ),
            get_carried_bank_run_summary=lambda: "Bank run: ready",
            carried_auto_is_combat=False,
        )
        dialog.show()
        _open_equipment_tab(dialog)
        QApplication.processEvents()

        summary = dialog.findChild(QLabel, "combatLoadoutSummaryLabel")
        bank_run = dialog.findChild(QLabel, "combatBankRunLabel")
        supply_mode = dialog.findChild(QComboBox, "combatPackModeCombo")
        clear_button = dialog.findChild(QPushButton, "combatClearInventoryButton")
        self.assertIn("Food: Shark x28", summary.text())
        self.assertIn("Weight: 16.8 kg carried", summary.text())
        self.assertEqual(bank_run.text(), "Bank run: ready")
        self.assertFalse(supply_mode.isVisibleTo(dialog))
        self.assertFalse(clear_button.isVisibleTo(dialog))
        dialog.deleteLater()

    def test_agility_reward_shops_report_failures_and_expose_every_ticket_bundle(self) -> None:
        # The ticket redemptions and the skillcape purchase moved from the
        # Agility panel's button grid to the Shop tab's reward-shops area; the
        # same commands run, now with a labelled home.
        pd = _make_player_data()
        pd["agility_level"] = 1
        dialog = self._open(pd, current_skill="Agility")
        dialog.show()
        QApplication.processEvents()
        _open_shop_tab(dialog)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "shopAgilityRewardsPanel")
        self.assertIsNotNone(panel)
        labels = {button.text() for button in panel.findChildren(QPushButton)}
        for tickets in (1, 10, 25, 100, 1000):
            self.assertIn(f"Redeem {tickets} ticket{'s' if tickets != 1 else ''} for XP", labels)

        dialog.findChild(QPushButton, "shopAgilityCapeButton").click()
        QApplication.processEvents()
        status = dialog.findChild(QLabel, "shopAgilityRewardStatus")
        self.assertIsNotNone(status)
        self.assertEqual(status.text(), "Requires level 99 Agility")

    def test_agility_reward_shops_drive_every_relocated_row(self) -> None:
        # Each row that left the Agility panel is reachable from its new home
        # and forwards its exact command payload.
        pd = _make_player_data()
        pd.update(
            {
                "agility_level": 99,
                "inventory": {
                    "Coins": 200_000,
                    "Agility arena ticket": 1_000,
                    "Pyramid top": 1,
                },
                "agility_lap_counts": {
                    "agile_top_unlocked": True,
                    "agile_legs_unlocked": True,
                },
            }
        )
        dialog = self._open(pd, current_skill="Agility")
        dialog.show()
        QApplication.processEvents()
        _open_shop_tab(dialog)
        QApplication.processEvents()

        panel = dialog.findChild(QWidget, "shopAgilityRewardsPanel")
        by_text = {
            button.text(): button for button in panel.findChildren(QPushButton)
        }

        cases = [
            ("Redeem 10 tickets for XP", ("redeem_brimhaven_xp", {"tickets": 10})),
            ("Toadflax (3 tickets)", ("redeem_brimhaven_item", {"tickets": 3})),
            ("Wergali (5 tickets)", ("redeem_brimhaven_item", {"tickets": 5})),
            ("Snapdragon (10 tickets)", ("redeem_brimhaven_item", {"tickets": 10})),
            ("Pirate's hook (800 tickets)", ("redeem_brimhaven_item", {"tickets": 800})),
            ("Claim Agile top", ("claim_agile_piece", {"piece": "Agile top"})),
            ("Claim Agile legs", ("claim_agile_piece", {"piece": "Agile legs"})),
            ("Agility cape · 99,000 coins", ("purchase_agility_cape", {})),
            ("Pyramid top · 1,000 coins", ("sell_pyramid_top", {"count": 1})),
        ]
        for label, expected_call in cases:
            button = by_text.get(label)
            self.assertIsNotNone(button, f"missing shop row: {label}")
            button.click()
            QApplication.processEvents()
            self.assertEqual(self._agility_command_calls[-1], expected_call, label)

        self.assertIn("Agile top", pd["inventory"])
        self.assertIn("Agility cape", pd["inventory"])
        self.assertEqual(pd["inventory"].get("Pyramid top", 0), 0)

    def test_switching_from_brimhaven_ends_the_paid_stint(self) -> None:
        pd = _make_player_data()
        pd.update({
            "agility_level": 99,
            "current_agility": "brimhaven_arena",
            "agility_activity_state": {
                "brimhaven": {"stint_active": True, "activated": True}
            },
        })
        dialog = self._open(pd, current_skill="Agility")
        target_list = _find_list_with_user_role(dialog, "burthorpe_course")
        burthorpe = next(
            target_list.item(index)
            for index in range(target_list.count())
            if target_list.item(index).data(Qt.ItemDataRole.UserRole) == "burthorpe_course"
        )
        target_list.itemClicked.emit(burthorpe)
        QApplication.processEvents()

        self.assertEqual(pd["current_agility"], "burthorpe_course")
        self.assertNotIn("brimhaven", pd.get("agility_activity_state", {}))
        self.assertEqual(self._agility_command_calls[-1][0], "abandon")

    def test_stopping_agility_ends_the_brimhaven_stint(self) -> None:
        pd = _make_player_data()
        pd.update({
            "agility_level": 99,
            "current_agility": "brimhaven_arena",
            "agility_activity_state": {"brimhaven": {"stint_active": True}},
        })

        def stop_training():
            pd["agility_activity_state"].pop("brimhaven")
            pd["current_utility"] = "bankstanding"
            self._agility_command_calls.append(("abandon", {}))
            return "Utilities"

        dialog = self._open(
            pd,
            current_skill="Agility",
            on_stop_training=stop_training,
        )
        next(
            button for button in dialog.findChildren(QPushButton)
            if button.text() == "Stop training"
        ).click()
        QApplication.processEvents()

        self.assertNotIn("brimhaven", pd.get("agility_activity_state", {}))
        self.assertEqual(self._agility_command_calls[-1][0], "abandon")
