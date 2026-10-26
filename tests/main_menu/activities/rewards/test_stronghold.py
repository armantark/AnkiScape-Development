from __future__ import annotations
import unittest
from tests.test_main_menu_widget import (
    HAS_AQT,
    _bank_grid_button,
    _bank_grid_buttons,
    _make_player_data,
    _open_bank_tab,
    _tree_items,
    _utility_row,
    patch,
)
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QLabel, QProgressBar, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_stronghold_landmark_row_starts_activity_when_unfinished(self) -> None:
        pd = _make_player_data()
        pd["stronghold_of_security"] = {"step": 1, "completed": False, "boots_choice": None}
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)

        row = _utility_row(utility_tree, "stronghold_of_security")
        self.assertTrue(row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("1/4", row.text(0))
        self.assertFalse(row.icon(0).isNull())

        self._activity_start_calls.clear()
        utility_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._activity_start_calls, ["stronghold_of_security"])
        self.assertEqual(pd["current_utility"], "stronghold_of_security")
        self.assertEqual(self._stronghold_claim_calls, [])

    def test_stronghold_landmark_row_claims_reward_when_completed_unclaimed(self) -> None:
        pd = _make_player_data()
        pd["stronghold_of_security"] = {"step": 4, "completed": True, "boots_choice": None}
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)

        row = _utility_row(utility_tree, "stronghold_of_security")
        self.assertIn("Claim", row.text(0))

        self._utility_calls.clear()
        utility_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        # A completed-but-unclaimed landmark opens the reward dialog rather than
        # (re)selecting the activity.
        self.assertEqual(self._stronghold_claim_calls, [True])
        self.assertEqual(self._utility_calls, [])

    def test_stronghold_landmark_row_is_inert_once_claimed(self) -> None:
        pd = _make_player_data()
        pd["stronghold_of_security"] = {"step": 4, "completed": True, "boots_choice": "Fancy boots"}
        dialog = self._open(pd)
        utility_tree = self._open_activities(dialog)

        row = _utility_row(utility_tree, "stronghold_of_security")
        self.assertFalse(row.flags() & Qt.ItemFlag.ItemIsEnabled)
        self.assertIn("Fancy boots", row.text(0))

        utility_tree.itemClicked.emit(row, 0)
        QApplication.processEvents()
        self.assertEqual(self._stronghold_claim_calls, [])
        self.assertEqual(self._utility_calls, [])

    def test_stronghold_player_safety_claims_lamps_then_marks_complete(self) -> None:
        from ankiscape.core.constants import CLAIM_DATA
        from ankiscape.data.stronghold_player_safety_data import (
            STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS,
        )
        from ankiscape.logic.stronghold_player_safety_logic import (
            apply_stronghold_player_safety_command_pure,
        )
        from ankiscape.logic_pure.logic_pure_claims import apply_claim_pure

        pd = _make_player_data()
        pd["stronghold_player_safety"] = {
            "version": 2,
            "stage": 3,
            "crevice_unlocked": True,
            "chest_claimed": False,
            "safety_first_emote_unlocked": False,
            "last_result": "Reached the reward passage.",
        }

        def stronghold_command(action_id, payload):
            updated, ok, info = apply_stronghold_player_safety_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        def claim_reward(claim_id, selected_skill_id=None):
            self._claim_calls.append((claim_id, selected_skill_id))
            updated, ok = apply_claim_pure(
                pd,
                claim_id,
                CLAIM_DATA,
                selected_skill_id=selected_skill_id,
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return ok

        saved_skills = []
        dialog = self._open(
            pd,
            current_skill="Activities",
            on_stronghold_player_safety_command=stronghold_command,
            on_claim_reward=claim_reward,
            on_save_skill=saved_skills.append,
        )
        dialog.show()
        QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole)
            == "stronghold_player_safety"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(
                QWidget, "strongholdPlayerSafetyPanel"
            )
            if widget.isVisible()
        )
        self.assertFalse(
            panel.findChild(QLabel, "strongholdPlayerSafetyIcon").pixmap().isNull()
        )
        self.assertEqual(
            panel.findChild(QProgressBar, "strongholdPlayerSafetyProgress").value(),
            3,
        )
        title = panel.findChild(QLabel, "strongholdPlayerSafetyTitle")
        self.assertTrue(title.wordWrap())
        self.assertGreaterEqual(title.height(), title.sizeHint().height())
        status = panel.findChild(QLabel, "strongholdPlayerSafetyStatus")
        self.assertEqual(status.text(), "CHEST READY")
        self.assertGreaterEqual(status.width(), status.sizeHint().width())
        self.assertLess(title.geometry().right(), status.geometry().left())
        fight = panel.findChild(QPushButton, "strongholdPlayerSafetyFightButton")
        self.assertTrue(fight.isVisible())
        self.assertTrue(fight.isEnabled())

        panel.findChild(QPushButton, "strongholdPlayerSafetyClaimButton").click()
        QApplication.processEvents()
        self.assertEqual(pd["inventory"]["Coins"], 10_000)
        self.assertEqual(pd["inventory"]["Safety gloves"], 1)
        self.assertEqual(status.text(), "2 LAMPS LEFT")
        self.assertIn(
            "Two 500-XP Antique lamps are ready in Bank Claims",
            panel.findChild(QLabel, "strongholdPlayerSafetySummary").text(),
        )
        self.assertEqual(
            [
                state
                for claim_id, state in pd["claims"].items()
                if claim_id in STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS
            ],
            [
                {"claimed": False, "delivered": True},
                {"claimed": False, "delivered": True},
            ],
        )
        _open_bank_tab(dialog)
        bank_claim_titles = [
            label.text()
            for label in dialog.findChildren(QLabel, "bankClaimTitle")
        ]
        self.assertIn(
            "Stronghold of Player Safety: Antique lamp 1 (500 XP)",
            bank_claim_titles,
        )
        self.assertIn(
            "Stronghold of Player Safety: Antique lamp 2 (500 XP)",
            bank_claim_titles,
        )
        tree = self._open_activities(dialog)
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()

        lamp = panel.findChild(QPushButton, "strongholdPlayerSafetyLampButton")
        self.assertEqual(lamp.text(), "Use 500-XP lamp (2)")
        with patch.object(
            self._ui,
            "_choose_xp_lamp_skill",
            side_effect=("agility", "dungeoneering"),
        ) as chooser:
            lamp.click()
            QApplication.processEvents()
            self.assertEqual(pd["agility_exp"], 1500.0)
            self.assertEqual(lamp.text(), "Use 500-XP lamp (1)")
            self.assertEqual(status.text(), "1 LAMP LEFT")
            lamp.click()
            QApplication.processEvents()

        self.assertEqual(pd["dungeoneering_exp"], 500.0)
        self.assertEqual(lamp.text(), "Use 500-XP lamp (0)")
        self.assertEqual(status.text(), "COMPLETE")
        self.assertEqual(
            self._claim_calls[-2:],
            [
                (STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS[0], "agility"),
                (
                    STRONGHOLD_PLAYER_SAFETY_LAMP_CLAIM_IDS[1],
                    "dungeoneering",
                ),
            ],
        )
        self.assertEqual(chooser.call_count, 2)
        parent, chooser_title, eligible_skill_ids = chooser.call_args_list[0].args
        self.assertEqual(parent.objectName(), "strongholdPlayerSafetyPanel")
        self.assertEqual(chooser_title, "Use Stronghold XP lamp")
        self.assertEqual(len(eligible_skill_ids), 25)
        self.assertIn("attack", eligible_skill_ids)
        self.assertIn("dungeoneering", eligible_skill_ids)

        fight.click()
        QApplication.processEvents()
        self.assertEqual(saved_skills, ["Combat"])
        self.assertEqual(pd["current_combat_target"], "cockroach_soldier")
        self.assertEqual(pd["combat_encounter"]["enemy_lifepoints"], 960)

    def test_stronghold_reclaim_refreshes_an_initialized_bank_view(self) -> None:
        from ankiscape.logic.stronghold_player_safety_logic import (
            apply_stronghold_player_safety_command_pure,
        )

        pd = _make_player_data()
        pd["stronghold_player_safety"] = {
            "version": 2,
            "stage": 3,
            "crevice_unlocked": True,
            "chest_claimed": True,
            "safety_first_emote_unlocked": True,
            "last_result": "Opened the chest.",
        }

        def stronghold_command(action_id, payload):
            updated, ok, info = apply_stronghold_player_safety_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_stronghold_player_safety_command=stronghold_command,
        )
        dialog.show()
        dialog.resize(900, 560)
        for _ in range(3):
            QApplication.processEvents()

        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole)
            == "stronghold_player_safety"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(
                QWidget, "strongholdPlayerSafetyPanel"
            )
            if widget.isVisible()
        )
        reclaim = panel.findChild(
            QPushButton, "strongholdPlayerSafetyReclaimButton"
        )
        self.assertTrue(reclaim.isVisible())
        self.assertTrue(reclaim.isEnabled())

        _open_bank_tab(dialog)
        self.assertNotIn(
            "Safety gloves",
            [button.property("bankItemName") for button in _bank_grid_buttons(dialog)],
        )

        reclaim.click()
        QApplication.processEvents()

        self.assertEqual(pd["inventory"]["Safety gloves"], 1)
        gloves = _bank_grid_button(dialog, "Safety gloves")
        self.assertTrue(gloves.isVisibleTo(dialog))
        self.assertEqual(gloves.property("bankQuantity"), 1)
