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
    from aqt.qt import QApplication, Qt, QWidget

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class DistractionHUDBadgeTest(unittest.TestCase):
    """The reviewer surface for the three review-clock Distractions.

    Before this badge existed, the same state was three HUD notice lines plus
    five floating popups fired outside the per-review coalescing.
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        from ankiscape.ui import ui

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
        ui._DISTRACTION_BADGE = None
        ui._FARM_STATUS_DIALOG = None

    def tearDown(self) -> None:
        self.ui.close_farming_status_dialog()
        for widget in (
            self.ui._DISTRACTION_BADGE,
            self.ui._FARMING_BADGE,
            self.ui._REVIEW_HUD,
        ):
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        self.ui._DISTRACTION_BADGE = None
        self.ui._FARMING_BADGE = None
        self.ui._REVIEW_HUD = None
        self.ui._FARM_STATUS_DIALOG = None
        self.ui.mw = self.old_mw
        self.ui.get_config_bool = self.old_config
        self.parent.hide()
        self.parent.deleteLater()
        for _ in range(3):
            QApplication.processEvents()

    def _quiet_state(self) -> dict:
        from ankiscape.logic.big_chinchompa_logic import default_big_chinchompa_state_pure
        from ankiscape.logic.evil_tree_logic import default_evil_tree_state_pure
        from ankiscape.logic.shooting_star_logic import default_shooting_star_state_pure

        state = {
            "inventory": {},
            "woodcutting_level": 99,
            "mining_level": 99,
            "toolbelt": {
                "woodcutting": ["bronze_hatchet"],
                "mining": ["bronze_pickaxe"],
            },
            "world_population_profile": "normal",
        }
        state["evil_tree"] = default_evil_tree_state_pure()
        state["shooting_star"] = default_shooting_star_state_pure()
        state["big_chinchompa"] = default_big_chinchompa_state_pure()
        return state

    def _with_live_evil_tree(self, state: dict) -> dict:
        from ankiscape.logic.evil_tree_logic import advance_evil_tree_world_clock_pure

        state = dict(state)
        state["shop_market_clock"] = {"answered_cards": 20, "market_tick": 20}
        updated, _events = advance_evil_tree_world_clock_pure(
            state,
            tier_roll=0.0,
            location_roll=0.0,
        )
        state.update(updated)
        return state

    def _with_live_big_chinchompa(self, state: dict) -> dict:
        from ankiscape.logic.big_chinchompa_logic import advance_big_chinchompa_world_clock_pure

        state = dict(state)
        state["shop_market_clock"] = {"answered_cards": 60, "market_tick": 60}
        updated, _events = advance_big_chinchompa_world_clock_pure(state)
        state.update(updated)
        return state

    def test_badge_reserves_no_space_when_nothing_is_live(self) -> None:
        state = self._quiet_state()

        self.ui.update_distraction_hud_badge(state)
        for _ in range(3):
            QApplication.processEvents()

        badge = self.ui._DISTRACTION_BADGE
        self.assertIsNotNone(badge)
        self.assertFalse(badge.isVisible())
        self.assertEqual(self.ui._world_event_rows(state), ())

    def test_badge_counts_live_events_and_lists_them_in_its_tooltip(self) -> None:
        state = self._with_live_evil_tree(self._quiet_state())
        rows = self.ui._world_event_rows(state)
        self.assertTrue(rows, "the fixture must put an Evil Tree in the world")

        self.ui.update_distraction_hud_badge(state)
        for _ in range(3):
            QApplication.processEvents()

        badge = self.ui._DISTRACTION_BADGE
        self.assertTrue(badge.isVisible())
        self.assertEqual(badge.badge.text(), str(len(rows)))
        for _activity_id, text in rows:
            self.assertIn(text, badge.toolTip())
        # A single "&" would be read as a keyboard mnemonic.
        self.assertEqual(badge.button.text(), "D&&D")

    def test_badge_is_an_interactive_sibling_of_the_mouse_transparent_hud(self) -> None:
        review_hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = review_hud
        review_hud.show()
        self.ui.ensure_distraction_hud_badge()
        first = self.ui._DISTRACTION_BADGE
        self.ui.ensure_distraction_hud_badge()
        for _ in range(4):
            QApplication.processEvents()

        self.assertIs(first, self.ui._DISTRACTION_BADGE)
        self.assertIs(first.parentWidget(), self.parent)
        self.assertFalse(
            first.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        )
        self.assertTrue(first.testAttribute(Qt.WidgetAttribute.WA_StyledBackground))
        self.assertEqual(
            len(self.parent.findChildren(QWidget, "AnkiScapeDistractionBadge")),
            1,
        )
        self.assertNotIn(first, QApplication.topLevelWidgets())

    def test_badge_stacks_under_the_farming_badge_beside_the_hud(self) -> None:
        from ankiscape.logic.farming_logic import default_farming_state_pure

        review_hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = review_hud
        review_hud.move(400, 300)
        review_hud.show()

        state = self._with_live_evil_tree(self._quiet_state())
        state.update(default_farming_state_pure())
        state["farming_level"] = 99
        state["farming_exp"] = 0.0
        self.ui.update_farming_hud_badge(state)
        self.ui.update_distraction_hud_badge(state)
        for _ in range(4):
            QApplication.processEvents()

        farming = self.ui._FARMING_BADGE
        distraction = self.ui._DISTRACTION_BADGE
        self.assertTrue(farming.isVisible())
        self.assertTrue(distraction.isVisible())
        self.assertEqual(farming.x(), distraction.x())
        self.assertGreater(distraction.y(), farming.y())
        self.assertLess(
            farming.x() + farming.width(),
            review_hud.x() + 1,
            "the column belongs to the left of the HUD",
        )

    def test_one_live_event_opens_its_card_and_several_open_the_hub(self) -> None:
        from ankiscape.data.big_chinchompa_data import BIG_CHINCHOMPA_UTILITY_ID

        opened = []
        state = self._with_live_big_chinchompa(self._quiet_state())
        self.assertEqual(len(self.ui._world_event_rows(state)), 1)

        self.ui.update_distraction_hud_badge(state, opened.append)
        self.ui._DISTRACTION_BADGE.button.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(opened, [BIG_CHINCHOMPA_UTILITY_ID])

        crowded = self._with_live_evil_tree(state)
        crowded = self._with_live_big_chinchompa(crowded)
        self.assertGreater(len(self.ui._world_event_rows(crowded)), 1)
        self.ui.update_distraction_hud_badge(crowded, opened.append)
        self.ui._DISTRACTION_BADGE.button.click()
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(opened[-1], None)

    def test_hide_lifecycle_and_hud_setting_both_take_the_badge_away(self) -> None:
        state = self._with_live_evil_tree(self._quiet_state())
        self.ui.update_distraction_hud_badge(state)
        badge = self.ui._DISTRACTION_BADGE
        self.assertTrue(badge.isVisible())

        self.ui.hide_review_hud()
        QApplication.processEvents()
        self.assertFalse(badge.isVisible())

        self.ui.get_config_bool = lambda key, default=True: False
        self.ui.update_distraction_hud_badge(state)
        QApplication.processEvents()
        self.assertFalse(badge.isVisible())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
