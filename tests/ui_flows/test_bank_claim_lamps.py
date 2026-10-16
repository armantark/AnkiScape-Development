"""Bank Claims lamp rows: Claim pays a fixed-skill lamp, Destroy forfeits any lamp after a warning."""

from __future__ import annotations

import copy
import unittest
from unittest import mock

from tests import allow_modal_dialogs
from tests import test_main_menu_widget as _main_menu
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _open_bank_tab

if HAS_AQT:
    from aqt.qt import QApplication, QLabel, QMessageBox, QPushButton, QTimer, QToolButton, QWidget


def _pump() -> None:
    for _ in range(4):
        QApplication.processEvents()


def _rows(dialog) -> dict:
    """Each visible claim row by title, with its button texts."""
    return {
        row.findChild(QLabel, "bankClaimTitle").text(): row
        for row in dialog.findChildren(QWidget, "bankClaimRow")
        if not row.isHidden()
    }


def _button(row, text: str):
    return next(button for button in row.findChildren(QPushButton) if button.text() == text)


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class BankClaimLampsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _main_menu.MainMenuWidgetTest.setUpClass()

    def setUp(self) -> None:
        self.menu = _main_menu.MainMenuWidgetTest(methodName="runTest")
        self.menu.setUp()
        self.data = _make_player_data()
        self.data["claims"]["tutorial_island_starter_kit"] = {"claimed": True}
        for quest_id in ("stolen_hearts", "the_elder_kiln"):
            self.data["quests"][quest_id] = {"started": True, "progress": 99, "completed": True}
        self.data["attack_level"] = 75

    def tearDown(self) -> None:
        self.menu.tearDown()

    def _open_bank(self, width: int = 900):
        from ankiscape.core.constants import CLAIM_DATA
        from ankiscape.logic_pure.logic_pure import apply_claim_pure, apply_destroy_claim_pure

        def _commit(updated_ok) -> bool:
            self.data.update(updated_ok[0])
            return updated_ok[1]

        dialog = self.menu._open(
            self.data,
            on_claim_reward=lambda claim_id, skill_id=None: _commit(apply_claim_pure(self.data, claim_id, CLAIM_DATA, skill_id)),
            on_destroy_claim=lambda claim_id: _commit(apply_destroy_claim_pure(self.data, claim_id, CLAIM_DATA)),
        )
        dialog.show()
        dialog.resize(width, 560)
        _pump()
        _open_bank_tab(dialog)
        _pump()
        return dialog

    def _destroy(self, row, answer) -> str:
        """Click Destroy, answer the confirmation, and return its text."""
        seen = []

        def _answer() -> None:
            box = next(w for w in QApplication.topLevelWidgets() if isinstance(w, QMessageBox) and w.isVisible())
            seen.append(box.text())
            box.button(answer).click()

        QTimer.singleShot(0, _answer)
        with allow_modal_dialogs():
            _button(row, "Destroy").click()
        _pump()
        return seen[0]

    def test_fixed_skill_lamps_claim_without_the_skill_grid(self) -> None:
        dialog = self._open_bank()
        buttons = sorted(
            tuple(button.text() for button in row.findChildren(QPushButton))
            for row in dialog.findChildren(QWidget, "bankClaimRow")
        )
        self.assertEqual(
            buttons,
            [("Destroy", "Choose skill"), ("Destroy", "Choose skill"), ("Destroy", "Claim"), ("Destroy", "Claim")],
        )
        agility = next(
            row for row in dialog.findChildren(QWidget, "bankClaimRow")
            if row.findChild(QLabel, "bankClaimMetadata").text() == "250 XP lamp · Pays Agility."
        )
        agility_before = self.data["agility_exp"]
        with mock.patch.object(self.menu._ui, "_choose_xp_lamp_skill", side_effect=AssertionError("grid opened")):
            _button(agility, "Claim").click()
            _pump()

        self.assertEqual(self.data["agility_exp"] - agility_before, 250)
        self.assertNotIn(
            "250 XP lamp · Pays Agility.",
            [label.text() for label in dialog.findChildren(QLabel, "bankClaimMetadata") if not label.isHidden()],
        )

    def _choose_lamp(self, row, *, cancel=False):
        seen = {}

        def _answer():
            modal = QApplication.activeModalWidget()
            skills = modal.findChildren(QToolButton, "xpLampSkillButton")
            seen["skills"] = [button.property("skillId") for button in skills]
            claim = modal.findChild(QPushButton, "xpLampClaimButton")
            seen["initially_enabled"] = claim.isEnabled()
            next(button for button in skills if button.property("skillId") == "attack").click()
            seen["selected_enabled"] = claim.isEnabled()
            action = modal.findChild(QPushButton, "xpLampCancelButton") if cancel else claim
            action.click()

        QTimer.singleShot(0, _answer)
        with mock.patch.object(self.menu._ui, "QDialog", self.menu._orig_dialog), allow_modal_dialogs():
            _button(row, "Choose skill").click()
        _pump()
        return seen

    def test_a_choice_lamp_opens_the_grid_even_with_one_eligible_skill(self) -> None:
        dialog = self._open_bank(720)
        elder_kiln = _rows(dialog)["The Elder Kiln: XP lamp (100,000 XP)"]
        self.assertIn("Minimum level: 75.", elder_kiln.findChild(QLabel, "bankClaimMetadata").text())
        before = self.data.get("attack_exp", 0)
        other_xp = {key: value for key, value in self.data.items() if key.endswith("_exp") and key != "attack_exp"}
        seen = self._choose_lamp(elder_kiln)

        self.assertEqual(seen, {"skills": ["attack"], "initially_enabled": False, "selected_enabled": True})
        self.assertEqual(self.data["attack_exp"] - before, 100_000)
        self.assertEqual({key: self.data[key] for key in other_xp}, other_xp)
        self.assertTrue(self.data["claims"]["the_elder_kiln_xp_lamp_1"]["claimed"])

    def test_cancelling_the_real_choice_grid_preserves_the_lamp_and_xp(self) -> None:
        dialog = self._open_bank(720)
        before = copy.deepcopy(self.data)
        seen = self._choose_lamp(_rows(dialog)["The Elder Kiln: XP lamp (100,000 XP)"], cancel=True)
        self.assertEqual(seen["skills"], ["attack"])
        self.assertEqual(self.data, before)
        self.assertIn("The Elder Kiln: XP lamp (100,000 XP)", _rows(dialog))

    def test_destroy_warns_then_removes_the_lamp_for_good(self) -> None:
        from tests.ui_flows.qt_text_fit import text_fit_defects

        title = "The Elder Kiln: XP lamp (100,000 XP)"
        dialog = self._open_bank()
        for width in (900, 720):
            dialog.resize(width, 560)
            _pump()
            self.assertEqual(text_fit_defects(dialog.findChild(QWidget, "bankClaimsBox")), [], width)

        warning = self._destroy(_rows(dialog)[title], QMessageBox.StandardButton.No)
        self.assertEqual(
            warning,
            f"{title}\n\nAre you sure you want to destroy the lamp? You won't be able to get another one.",
        )
        self.assertIn(title, _rows(dialog))

        self._destroy(_rows(dialog)[title], QMessageBox.StandardButton.Yes)
        self.assertNotIn(title, _rows(dialog))
        self.assertTrue(self.data["claims"]["the_elder_kiln_xp_lamp_1"]["forfeited"])
        self.assertNotIn(title, _rows(self._open_bank()))


if __name__ == "__main__":
    unittest.main()
