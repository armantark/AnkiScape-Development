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
    from aqt.qt import QApplication, QWidget

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


_PROJECTION = {
    "active": {
        "family_id": "pit_reward",
        "label": "Fight Pit reward",
        "detail": "Choose your payout",
        "options": (
            {"id": "take_xp", "label": "Take XP"},
            {"id": "gamble", "label": "Gamble"},
        ),
    },
    "queued_count": 0,
}


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ExpPopupOverlayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        import ui

        self.ui = ui
        self.parent = QWidget()
        self.parent.resize(1000, 560)
        self.parent.show()
        for _ in range(5):
            QApplication.processEvents()
        self.old_mw = ui.mw
        self.old_config = ui.get_config_bool
        ui.mw = self.parent
        ui.get_config_bool = lambda key, default=True: True
        ui._REVIEW_HUD = None
        ui._REVIEW_CONTEXT_STRIP = None
        ui._FARMING_BADGE = None
        # Creation order matters: in production the popup is built at profile
        # load, before the lazily created HUD cluster, so it is the earliest
        # sibling and therefore the bottom of the paint order.
        self.popup = ui.ExpPopup(self.parent)
        self.parent.exp_popup = self.popup
        self.strip = ui.ReviewContextActionStrip(self.parent)
        ui._REVIEW_CONTEXT_STRIP = self.strip
        self.strip.set_data(_PROJECTION)
        for _ in range(5):
            QApplication.processEvents()

    def tearDown(self) -> None:
        for widget in (self.popup, self.strip, self.ui._REVIEW_HUD):
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        self.ui._REVIEW_HUD = None
        self.ui._REVIEW_CONTEXT_STRIP = None
        self.ui._FARMING_BADGE = None
        self.ui.mw = self.old_mw
        self.ui.get_config_bool = self.old_config
        self.parent.hide()
        self.parent.deleteLater()
        for _ in range(3):
            QApplication.processEvents()

    def test_bubble_clears_the_context_strip_and_its_shadow(self) -> None:
        self.popup.show_text("+25 XP")
        for _ in range(5):
            QApplication.processEvents()

        self.assertTrue(self.strip.isVisible())
        overlap = self.popup.geometry().intersected(self.strip.geometry())
        self.assertTrue(
            overlap.isEmpty(),
            f"bubble overlaps the strip by {overlap}",
        )
        self.assertGreaterEqual(
            self.strip.geometry().top() - self.popup.geometry().bottom(),
            20,
            "bubble sits inside the strip's 16px drop-shadow bleed",
        )

    def test_bubble_stays_above_a_re_raised_hud(self) -> None:
        self.popup.show_text("+25 XP")
        for _ in range(5):
            QApplication.processEvents()

        self.ui.ensure_review_hud()
        self.ui.ensure_review_context_action_strip()
        for _ in range(3):
            QApplication.processEvents()

        siblings = [
            child
            for child in self.parent.children()
            if isinstance(child, QWidget)
        ]
        self.assertIs(siblings[-1], self.popup)


if __name__ == "__main__":
    unittest.main()
