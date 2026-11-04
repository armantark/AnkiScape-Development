from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _goto_runecrafting, _make_player_data
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QComboBox, QLabel, QPushButton, QWidget
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_wicked_hood_card_exposes_live_allowances_and_manual_actions(self) -> None:
        from ankiscape.logic.wicked_hood_logic import apply_wicked_hood_command_pure

        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["quests"]["rune_mysteries"] = {
            "started": True,
            "progress": 6,
            "completed": True,
        }
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["air"],
            "allowance_day": 0,
            "essence_remaining": 100,
            "rune_withdrawals_remaining": 1,
            "teleports_remaining": 2,
        }
        calls = []

        def _hood_command(action_id, payload):
            calls.append((action_id, dict(payload)))
            updated, ok, info = apply_wicked_hood_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("message", info.get("reason", "")), **info}

        dialog = self._open(pd, on_wicked_hood_command=_hood_command)
        _goto_runecrafting(dialog)

        card = dialog.findChild(QWidget, "wickedHoodCard")
        remaining = dialog.findChild(QLabel, "wickedHoodRemainingLabel")
        essence = dialog.findChild(QPushButton, "wickedHoodEssenceButton")
        rune_combo = dialog.findChild(QComboBox, "wickedHoodRuneCombo")
        teleport = dialog.findChild(QPushButton, "wickedHoodTeleportButton")
        self.assertIsNotNone(card)
        self.assertEqual(
            remaining.text(),
            "100/100 essence · 1/1 rune withdrawals · 2/2 teleports",
        )
        self.assertTrue(essence.isEnabled())
        self.assertEqual(rune_combo.currentData(), "air")
        self.assertTrue(teleport.isEnabled())

        essence.click()
        QApplication.processEvents()

        self.assertEqual(calls[-1], ("essence", {}))
        self.assertEqual(pd["inventory"]["Rune essence"], 100)
        refreshed = dialog.findChild(QLabel, "wickedHoodRemainingLabel")
        self.assertEqual(
            refreshed.text(),
            "0/100 essence · 1/1 rune withdrawals · 2/2 teleports",
        )
        feedback = dialog.findChild(QLabel, "wickedHoodFeedbackLabel")
        self.assertEqual(feedback.text(), "Sent 100 Rune essence to the Bank.")

        teleport = dialog.findChild(QPushButton, "wickedHoodTeleportButton")
        teleport.click()
        QApplication.processEvents()
        guidance = dialog.findChild(QLabel, "wickedHoodGuidanceLabel")
        teleport_choice = dialog.findChild(QComboBox, "wickedHoodTeleportCombo")
        self.assertIn("Queued for Air altar", guidance.text())
        self.assertEqual(teleport_choice.currentData(), "air")
        self.assertFalse(teleport_choice.isEnabled())
        self.assertFalse(
            dialog.findChild(QPushButton, "wickedHoodTeleportButton").isEnabled()
        )

    def test_wicked_hood_card_labels_exhausted_allowances(self) -> None:
        pd = _make_player_data()
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["air"],
            "allowance_day": 0,
            "essence_remaining": 0,
            "rune_withdrawals_remaining": 0,
            "teleports_remaining": 0,
        }
        pd["world_clock"] = {"day": 0, "day_start_card": 0, "day_length": 100, "in_day_ticks": 0}
        dialog = self._open(pd, on_wicked_hood_command=lambda *_args: {})
        _goto_runecrafting(dialog)

        guidance = dialog.findChild(QLabel, "wickedHoodGuidanceLabel")
        self.assertEqual(
            guidance.text(),
            "Allowances exhausted · refills every 100 answered cards",
        )

    def test_wicked_hood_card_hides_before_claim(self) -> None:
        pd = _make_player_data()

        dialog = self._open(pd)
        _goto_runecrafting(dialog)

        card = dialog.findChild(QWidget, "wickedHoodCard")
        self.assertIsNotNone(card)
        self.assertTrue(card.isHidden())

    def test_wicked_hood_teleport_exposes_selected_altar_level_gate(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 1
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["nature"],
            "allowance_day": 0,
            "essence_remaining": 100,
            "rune_withdrawals_remaining": 1,
            "teleports_remaining": 2,
        }

        dialog = self._open(pd, on_wicked_hood_command=lambda *_args: {})
        _goto_runecrafting(dialog)

        choice = dialog.findChild(QComboBox, "wickedHoodTeleportCombo")
        button = dialog.findChild(QPushButton, "wickedHoodTeleportButton")
        self.assertEqual(choice.currentData(), "nature")
        self.assertIn("Lv 44", choice.currentText())
        self.assertFalse(button.isEnabled())
        self.assertEqual(button.toolTip(), "Requires level 44 Runecrafting.")

    def test_wicked_hood_actions_fit_the_narrow_skills_panel(self) -> None:
        pd = _make_player_data()
        pd["runecrafting_level"] = 99
        pd["claims"]["wicked_hood"] = {"claimed": True}
        pd["equipment"] = {"head": "Wicked hood"}
        pd["wicked_hood"] = {
            "fed_altars": ["air", "nature"],
            "allowance_day": 0,
            "essence_remaining": 100,
            "rune_withdrawals_remaining": 1,
            "teleports_remaining": 2,
        }
        dialog = self._open(pd, on_wicked_hood_command=lambda *_args: {})
        dialog.resize(820, 620)
        _goto_runecrafting(dialog)
        QApplication.processEvents()

        card = dialog.findChild(QWidget, "wickedHoodCard")
        remaining = dialog.findChild(QLabel, "wickedHoodRemainingLabel")
        buttons = [
            dialog.findChild(QPushButton, "wickedHoodEssenceButton"),
            dialog.findChild(QPushButton, "wickedHoodRunesButton"),
            dialog.findChild(QPushButton, "wickedHoodTeleportButton"),
        ]
        self.assertLessEqual(remaining.geometry().right(), card.rect().right())
        for button in buttons:
            self.assertGreaterEqual(button.width(), button.sizeHint().width(), button.text())
