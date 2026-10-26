from __future__ import annotations
import unittest
from tests.test_main_menu_widget import HAS_AQT, _make_player_data, _tree_items
if HAS_AQT:
    from tests.test_main_menu_widget import QApplication, QCheckBox, QLabel, QPushButton, QWidget, Qt
from tests.main_menu import fixtures


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class MainMenuWidgetTest(fixtures.MainMenuWidgetTest):
    def test_shattered_heart_card_claims_the_real_bag_and_updates_policy(self) -> None:
        from ankiscape.data.shattered_heart_data import SHATTERED_HEART_BAG_ITEM
        from ankiscape.logic.shattered_heart_logic import (
            apply_shattered_heart_command_pure,
            default_shattered_heart_state_pure,
        )

        pd = _make_player_data()
        pd["shattered_heart"] = default_shattered_heart_state_pure()
        pd["shop_market_clock"] = {"answered_cards": 0}
        pd["house_owned"] = False
        pd["house_rooms_bought"] = {}
        command_calls = []

        def shattered_command(action_id, payload):
            command_calls.append((action_id, dict(payload)))
            updated, ok, info = apply_shattered_heart_command_pure(
                pd, action_id, payload
            )
            if ok:
                pd.clear()
                pd.update(updated)
            return {"ok": ok, "message": info.get("reason", ""), **info}

        dialog = self._open(
            pd,
            current_skill="Activities",
            on_shattered_heart_command=shattered_command,
        )
        dialog.show()
        dialog.resize(760, 560)
        for _ in range(4):
            QApplication.processEvents()
        tree = self._open_activities(dialog)
        item = next(
            row
            for row in _tree_items(tree)
            if row.data(0, Qt.ItemDataRole.UserRole) == "shattered_heart"
        )
        tree.itemClicked.emit(item, 0)
        QApplication.processEvents()
        panel = next(
            widget
            for widget in dialog.findChildren(QWidget, "shatteredHeartPanel")
            if widget.isVisible()
        )
        self.assertFalse(panel.findChild(QLabel, "shatteredHeartIcon").pixmap().isNull())
        panel.findChild(QPushButton, "shatteredHeartClaimBagButton").click()
        QApplication.processEvents()
        self.assertEqual(command_calls[-1][0], "claim_bag")
        self.assertEqual(pd["inventory"][SHATTERED_HEART_BAG_ITEM], 1)
        self.assertTrue(
            panel.findChild(QPushButton, "shatteredHeartDestroyBagButton").isVisible()
        )
        discard = panel.findChild(QCheckBox, "shatteredHeartAutoDiscardCheck")
        discard.setChecked(True)
        QApplication.processEvents()
        self.assertEqual(command_calls[-1], ("set_auto_discard", {"enabled": True}))
        self.assertTrue(pd["shattered_heart"]["auto_discard"])
        self.assertLessEqual(panel.sizeHint().height(), 560)
        dialog.close()
