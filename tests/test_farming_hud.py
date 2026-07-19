from __future__ import annotations

import os
import sys
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

try:
    import aqt  # noqa: F401
    from aqt.qt import QApplication, QListWidget, QPushButton, Qt, QWidget

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class FarmingHUDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        import ui

        self.ui = ui
        self.parent = QWidget()
        self.parent.resize(1000, 700)
        self.parent.show()
        for _ in range(4):
            QApplication.processEvents()
        self.old_mw = ui.mw
        self.old_config = ui.get_config_bool
        ui.mw = self.parent
        ui.get_config_bool = lambda key, default=True: True
        ui._REVIEW_HUD = None
        ui._FARMING_BADGE = None
        ui._FARM_STATUS_DIALOG = None

    def tearDown(self) -> None:
        self.ui.close_farming_status_dialog()
        for widget in (self.ui._FARMING_BADGE, self.ui._REVIEW_HUD):
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        self.ui._FARMING_BADGE = None
        self.ui._REVIEW_HUD = None
        self.ui._FARM_STATUS_DIALOG = None
        self.ui.mw = self.old_mw
        self.ui.get_config_bool = self.old_config
        self.parent.hide()
        self.parent.deleteLater()
        for _ in range(3):
            QApplication.processEvents()

    def _state(self):
        from farming_logic import default_farming_state_pure

        state = {
            "inventory": {},
            "farming_level": 99,
            "farming_exp": 0.0,
            "woodcutting_level": 99,
            "woodcutting_exp": 0.0,
            "toolbelt": {"woodcutting": ["bronze_hatchet"]},
        }
        state.update(default_farming_state_pure())
        return state

    def test_badge_is_a_single_clickable_sibling_of_mouse_transparent_review_hud(self) -> None:
        review_hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = review_hud
        review_hud.show()
        self.ui.ensure_farming_hud_badge()
        first = self.ui._FARMING_BADGE
        self.ui.ensure_farming_hud_badge()
        second = self.ui._FARMING_BADGE
        for _ in range(4):
            QApplication.processEvents()

        self.assertIs(first, second)
        self.assertIs(first.parentWidget(), self.parent)
        self.assertIs(review_hud.parentWidget(), self.parent)
        self.assertTrue(review_hud.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))
        self.assertFalse(first.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents))
        self.assertTrue(first.testAttribute(Qt.WidgetAttribute.WA_StyledBackground))
        self.assertEqual(len(self.parent.findChildren(QWidget, "AnkiScapeFarmingBadge")), 1)
        self.assertNotIn(first, QApplication.topLevelWidgets())

    def test_badge_renders_backend_priority_and_retains_queue_count(self) -> None:
        from farming_logic import (
            add_farm_queue_step_pure,
            advance_farm_clock_pure,
            execute_farm_field_step_pure,
        )

        state = self._state()
        state["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3})
        state, step_id, _ = add_farm_queue_step_pure(
            state, "plant", "falador_allotment_south", crop_id="potato"
        )
        self.assertIsNotNone(step_id)
        self.ui.update_farming_hud_badge(state)
        badge = self.ui._FARMING_BADGE
        self.assertEqual(badge.badge.text(), "1")
        self.assertFalse(badge.queue_badge.isVisible())

        state, ok, _ = execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        state, _ = advance_farm_clock_pure(state, 7, lambda: 1.0)
        self.ui.update_farming_hud_badge(state)
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(badge.badge.text(), "1")
        self.assertEqual(badge.queue_badge.text(), "Q1")
        self.assertTrue(badge.queue_badge.isVisible())
        self.assertIn("ready", badge.toolTip().lower())

        state["farm_patches"]["falador_allotment_north"].update({"diseased": True, "dead": False})
        self.ui.update_farming_hud_badge(state)
        self.assertEqual(badge.badge.text(), "!1")
        self.assertEqual(badge.queue_badge.text(), "Q1")
        self.assertIn("attention", badge.toolTip().lower())

    def test_click_toggles_compact_status_and_deep_links_to_selected_patch(self) -> None:
        from farming_logic import advance_farm_clock_pure, execute_farm_field_step_pure

        state = self._state()
        state["inventory"].update({"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3})
        state, ok, _ = execute_farm_field_step_pure(
            state,
            {"kind": "plant", "patch_id": "falador_allotment_north", "crop_id": "potato"},
        )
        self.assertTrue(ok)
        state, _ = advance_farm_clock_pure(state, 7, lambda: 1.0)
        opened = []
        self.ui.update_farming_hud_badge(state, lambda patch_id=None: opened.append(patch_id))
        badge = self.ui._FARMING_BADGE
        badge.button.click()
        for _ in range(5):
            QApplication.processEvents()
        status = self.ui._FARM_STATUS_DIALOG
        self.assertIsNotNone(status)
        self.assertTrue(status.isVisible())
        self.assertIs(status.parentWidget(), self.parent)
        rows = status.findChild(QListWidget, "farmingStatusList")
        self.assertEqual(rows.count(), 1)
        self.assertEqual(rows.item(0).data(Qt.ItemDataRole.UserRole), "falador_allotment_north")
        rows.itemActivated.emit(rows.item(0))
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(opened, ["falador_allotment_north"])
        self.assertIsNone(self.ui._FARM_STATUS_DIALOG)

        badge.button.click()
        for _ in range(3):
            QApplication.processEvents()
        status = self.ui._FARM_STATUS_DIALOG
        self.assertTrue(status.isVisible())
        status.findChild(QPushButton, "farmingOpenFarmButton").click()
        QApplication.processEvents()
        self.assertEqual(opened, ["falador_allotment_north", None])
        self.assertIsNone(self.ui._FARM_STATUS_DIALOG)

        badge.button.click()
        QApplication.processEvents()
        self.assertTrue(self.ui._FARM_STATUS_DIALOG.isVisible())
        badge.button.click()
        QApplication.processEvents()
        self.assertIsNone(self.ui._FARM_STATUS_DIALOG)

    def test_hide_lifecycle_closes_status_and_setting_disables_badge(self) -> None:
        state = self._state()
        self.ui.update_farming_hud_badge(state)
        badge = self.ui._FARMING_BADGE
        badge.button.click()
        QApplication.processEvents()
        self.assertTrue(badge.isVisible())
        self.assertIsNotNone(self.ui._FARM_STATUS_DIALOG)

        self.ui.hide_review_hud()
        QApplication.processEvents()
        self.assertFalse(badge.isVisible())
        self.assertIsNone(self.ui._FARM_STATUS_DIALOG)

        self.ui.get_config_bool = lambda key, default=True: False
        self.ui.update_farming_hud_badge(state)
        QApplication.processEvents()
        self.assertFalse(badge.isVisible())


if __name__ == "__main__":
    unittest.main()
