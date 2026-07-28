"""Offscreen Qt cover for the always-visible reviewer strip.

This replaces `test_farming_hud.py` and `test_distraction_hud.py`, whose two
badges design-thread section 4.8 merged into one persistent seat: every case
they pinned is carried over here against the merged widget, alongside the
experience bars, the Grand Exchange drawer, and the pin that fills the badge.

Offscreen rule (.claude/rules/qt-offscreen-screenshots.md): show the parent and
pump events before trusting any geometry.
"""

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
    from aqt.qt import (
        QApplication,
        QListWidget,
        QProgressBar,
        QPushButton,
        Qt,
        QWidget,
    )

    HAS_AQT = True
except Exception:  # pragma: no cover - environment without aqt installed
    HAS_AQT = False


import pkg_alias  # noqa: F401  (installs the ankiscape package alias)


def _live_star(state: dict) -> dict:
    from ankiscape.logic.shooting_star_logic import (
        advance_shooting_star_world_clock_pure,
        shooting_star_view_pure,
    )

    for tick in range(1, 500):
        state["shop_market_clock"] = {"answered_cards": tick, "market_tick": tick}
        updated, _events = advance_shooting_star_world_clock_pure(state)
        state.update(updated)
        if shooting_star_view_pure(state, has_usable_pickaxe=True)["active"]:
            return state
    raise AssertionError("the world clock produced no shooting star")


@unittest.skipUnless(HAS_AQT, "aqt/PyQt6 not installed (use .venv-qt)")
class ReviewStripTest(unittest.TestCase):
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
        ui._STATUS_BADGE = None
        ui._STATUS_POPOVER = None
        ui._FILL_DRAWER = None

    def tearDown(self) -> None:
        self.ui.close_review_status_popover()
        for widget in (
            self.ui._STATUS_BADGE,
            self.ui._FILL_DRAWER,
            self.ui._REVIEW_HUD,
        ):
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        self.ui._STATUS_BADGE = None
        self.ui._FILL_DRAWER = None
        self.ui._REVIEW_HUD = None
        self.ui._STATUS_POPOVER = None
        self.ui.mw = self.old_mw
        self.ui.get_config_bool = self.old_config
        self.parent.hide()
        self.parent.deleteLater()
        for _ in range(3):
            QApplication.processEvents()

    def _state(self) -> dict:
        from ankiscape.core.constants import ITEM_DEFINITIONS, ORE_DATA
        from ankiscape.core.storage_pure import default_player_data

        state = default_player_data(ORE_DATA, ITEM_DEFINITIONS)
        state["farming_level"] = 99
        state["woodcutting_level"] = 99
        state["mining_level"] = 30
        state["mining_exp"] = 14_000.0
        state["toolbelt"] = {
            "woodcutting": ["bronze_hatchet"],
            "mining": ["bronze_pickaxe"],
        }
        return state

    def _ripe_crop(self, state: dict) -> dict:
        from ankiscape.logic.farming_logic import (
            advance_farm_clock_pure,
            execute_farm_field_step_pure,
        )

        state["inventory"].update(
            {"Rake": 1, "Seed dibber": 1, "Spade": 1, "Potato seed": 3}
        )
        state, ok, _info = execute_farm_field_step_pure(
            state,
            {
                "kind": "plant",
                "patch_id": "falador_allotment_north",
                "crop_id": "potato",
            },
        )
        self.assertTrue(ok)
        state, _events = advance_farm_clock_pure(state, 7, lambda: 1.0)
        return state

    # ---- the badge -------------------------------------------------------

    def test_badge_is_a_single_clickable_sibling_of_mouse_transparent_review_hud(
        self,
    ) -> None:
        review_hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = review_hud
        review_hud.show()
        self.ui.ensure_review_status_badge()
        first = self.ui._STATUS_BADGE
        self.ui.ensure_review_status_badge()
        second = self.ui._STATUS_BADGE
        for _ in range(4):
            QApplication.processEvents()

        self.assertIs(first, second)
        self.assertIs(first.parentWidget(), self.parent)
        self.assertIs(review_hud.parentWidget(), self.parent)
        self.assertTrue(
            review_hud.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        )
        self.assertFalse(
            first.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        )
        self.assertTrue(first.testAttribute(Qt.WidgetAttribute.WA_StyledBackground))
        self.assertEqual(
            len(self.parent.findChildren(QWidget, "AnkiScapeStatusBadge")), 1
        )
        self.assertNotIn(first, QApplication.topLevelWidgets())

    def test_badge_keeps_its_seat_when_nothing_is_live(self) -> None:
        # The Farming badge always showed and the D&D badge never did; section
        # 4.8 gives the merged seat the permanent one.
        self.ui.update_review_status_badge(self._state())
        for _ in range(3):
            QApplication.processEvents()

        badge = self.ui._STATUS_BADGE
        self.assertTrue(badge.isVisible())
        self.assertFalse(badge.badge.isVisible())
        # A single "&" would be read as a keyboard mnemonic.
        self.assertEqual(badge.button.text(), "D&&D · Farming")

    def test_badge_counts_a_live_world_event_and_lists_it_in_its_tooltip(self) -> None:
        state = _live_star(self._state())
        rows = self.ui._world_event_rows(state)
        self.assertTrue(rows, "the fixture must put a star in the world")

        self.ui.update_review_status_badge(state)
        for _ in range(3):
            QApplication.processEvents()

        badge = self.ui._STATUS_BADGE
        self.assertTrue(badge.isVisible())
        self.assertEqual(badge.badge.text(), str(len(rows)))
        for _activity_id, text in rows:
            self.assertIn(text, badge.toolTip())

    def test_badge_renders_ready_and_urgent_crops_and_retains_the_queue_count(
        self,
    ) -> None:
        from ankiscape.logic.farming_logic import add_farm_queue_step_pure

        state = self._ripe_crop(self._state())
        state, step_id, _info = add_farm_queue_step_pure(
            state, "plant", "falador_allotment_south", crop_id="potato"
        )
        self.assertIsNotNone(step_id)

        self.ui.update_review_status_badge(state)
        for _ in range(3):
            QApplication.processEvents()
        badge = self.ui._STATUS_BADGE
        self.assertEqual(badge.badge.text(), "1")
        self.assertEqual(badge.queue_badge.text(), "Q1")
        self.assertTrue(badge.queue_badge.isVisible())
        self.assertIn("ready", badge.toolTip().lower())

        state["farm_patches"]["falador_allotment_north"].update(
            {"diseased": True, "dead": False}
        )
        self.ui.update_review_status_badge(state)
        QApplication.processEvents()
        self.assertEqual(badge.badge.text(), "!1")
        self.assertEqual(badge.queue_badge.text(), "Q1")

    def test_badge_column_sits_to_the_left_of_the_experience_hud(self) -> None:
        review_hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = review_hud
        review_hud.move(400, 300)
        review_hud.show()

        self.ui.update_review_status_badge(self._state())
        for _ in range(4):
            QApplication.processEvents()

        badge = self.ui._STATUS_BADGE
        self.assertTrue(badge.isVisible())
        self.assertLess(
            badge.x() + badge.width(),
            review_hud.x() + 1,
            "the badge belongs to the left of the HUD",
        )

    # ---- the popover -----------------------------------------------------

    def test_click_toggles_the_popover_and_a_crop_line_opens_its_patch(self) -> None:
        opened: list = []
        state = self._ripe_crop(self._state())
        self.ui.update_review_status_badge(
            state, None, lambda patch_id=None: opened.append(patch_id)
        )
        badge = self.ui._STATUS_BADGE
        badge.button.click()
        for _ in range(5):
            QApplication.processEvents()

        popover = self.ui._STATUS_POPOVER
        self.assertIsNotNone(popover)
        self.assertTrue(popover.isVisible())
        self.assertIs(popover.parentWidget(), self.parent)
        rows = popover.findChild(QListWidget, "reviewStatusList")
        self.assertEqual(rows.count(), 1)
        self.assertEqual(
            rows.item(0).data(Qt.ItemDataRole.UserRole),
            ("farming", "falador_allotment_north"),
        )
        rows.itemActivated.emit(rows.item(0))
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(opened, ["falador_allotment_north"])
        self.assertIsNone(self.ui._STATUS_POPOVER)

        badge.button.click()
        for _ in range(3):
            QApplication.processEvents()
        self.ui._STATUS_POPOVER.findChild(
            QPushButton, "reviewStatusOpenFarmButton"
        ).click()
        QApplication.processEvents()
        self.assertEqual(opened, ["falador_allotment_north", None])
        self.assertIsNone(self.ui._STATUS_POPOVER)

        badge.button.click()
        QApplication.processEvents()
        self.assertTrue(self.ui._STATUS_POPOVER.isVisible())
        badge.button.click()
        QApplication.processEvents()
        self.assertIsNone(self.ui._STATUS_POPOVER)

    def test_a_favourited_distraction_lists_its_status_and_its_line_navigates(
        self,
    ) -> None:
        from ankiscape.data.tears_of_guthix_data import TEARS_OF_GUTHIX_ACTIVITY_ID

        opened: list = []
        state = _live_star(self._state())
        state["dnd_favourites"] = [TEARS_OF_GUTHIX_ACTIVITY_ID]

        self.ui.update_review_status_badge(
            state, lambda activity_id=None: opened.append(activity_id), None
        )
        self.ui._STATUS_BADGE.button.click()
        for _ in range(4):
            QApplication.processEvents()

        rows = self.ui._STATUS_POPOVER.findChild(QListWidget, "reviewStatusList")
        labels = [rows.item(index).text() for index in range(rows.count())]
        self.assertTrue(
            any("Shooting Stars" in label and "stardust" in label for label in labels),
            labels,
        )
        watched = [
            index
            for index in range(rows.count())
            if rows.item(index).data(Qt.ItemDataRole.UserRole)
            == ("distraction", TEARS_OF_GUTHIX_ACTIVITY_ID)
        ]
        self.assertEqual(len(watched), 1)
        self.assertIn("Tears of Guthix", rows.item(watched[0]).text())

        rows.itemActivated.emit(rows.item(watched[0]))
        for _ in range(3):
            QApplication.processEvents()
        self.assertEqual(opened, [TEARS_OF_GUTHIX_ACTIVITY_ID])
        self.assertIsNone(self.ui._STATUS_POPOVER)

    def test_hide_lifecycle_closes_the_popover_and_the_setting_removes_the_seat(
        self,
    ) -> None:
        state = self._state()
        self.ui.update_review_status_badge(state)
        badge = self.ui._STATUS_BADGE
        badge.button.click()
        QApplication.processEvents()
        self.assertTrue(badge.isVisible())
        self.assertIsNotNone(self.ui._STATUS_POPOVER)

        self.ui.hide_review_hud()
        QApplication.processEvents()
        self.assertFalse(badge.isVisible())
        self.assertIsNone(self.ui._STATUS_POPOVER)

        self.ui.get_config_bool = lambda key, default=True: False
        self.ui.update_review_status_badge(state)
        QApplication.processEvents()
        self.assertFalse(badge.isVisible())

    # ---- the experience bars --------------------------------------------

    def test_a_live_star_puts_the_real_mining_bar_in_the_strip(self) -> None:
        state = _live_star(self._state())
        state["current_utility"] = "shooting_stars"
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud

        hud.set_data(state, "Utility / Activities")
        for _ in range(3):
            QApplication.processEvents()

        self.assertTrue(hud.progress.isVisible())
        self.assertIn("Mining Lv 30", hud.progress.format())
        self.assertFalse(hud.second_progress.isVisible())
        # The activity caption is untouched: the bar carries the skill.
        self.assertIn("stardust", hud.sub_lbl.text())

        state["shooting_star"]["active_event"] = None
        hud.set_data(state, "Utility / Activities")
        for _ in range(3):
            QApplication.processEvents()
        self.assertFalse(hud.progress.isVisible())

    def test_a_two_skill_activity_fills_both_bars_and_names_the_rest(self) -> None:
        state = self._state()
        state["current_utility"] = "pyramid_plunder"
        state["activity_session"] = {"active_id": "pyramid_plunder"}
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud

        hud.set_data(state, "Utility / Activities")
        for _ in range(3):
            QApplication.processEvents()

        self.assertTrue(hud.progress.isVisible())
        self.assertTrue(hud.second_progress.isVisible())
        self.assertIn("Thieving", hud.progress.format())
        self.assertIn("Strength", hud.second_progress.format())
        self.assertIn("Runecrafting", hud.target_lbl.text())

    def test_the_second_bar_and_in_bar_text_never_leak_into_another_branch(
        self,
    ) -> None:
        state = self._state()
        state["current_utility"] = "pyramid_plunder"
        state["activity_session"] = {"active_id": "pyramid_plunder"}
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Utility / Activities")
        QApplication.processEvents()
        self.assertTrue(hud.second_progress.isVisible())

        hud.set_data(state, "Mining")
        for _ in range(3):
            QApplication.processEvents()

        self.assertFalse(hud.second_progress.isVisible())
        self.assertFalse(hud.progress.isTextVisible())

    # ---- the Grand Exchange drawer --------------------------------------

    def _open_offer(self, state: dict) -> dict:
        state["ge_player_orders"] = [
            {
                "id": 1,
                "side": "buy",
                "item_name": "Iron ore",
                "status": "open",
                "original_quantity": 5,
                "remaining_quantity": 5,
                "submitted_unit_price": 100,
                "escrow_coins": 500,
            }
        ]
        state["ge_fill_log"] = [
            {
                "card": 8,
                "side": "buy",
                "item_name": "Iron ore",
                "completed_quantity": 3,
                "original_quantity": 5,
            },
            {
                "card": 10,
                "side": "sell",
                "item_name": "Yew logs",
                "completed_quantity": 4,
                "original_quantity": 4,
            },
        ]
        state["shop_market_clock"] = {"answered_cards": 10, "market_tick": 10}
        return state

    def test_the_drawer_holds_no_seat_until_an_offer_is_open(self) -> None:
        state = self._state()
        self.ui.update_review_fill_drawer(state)
        for _ in range(3):
            QApplication.processEvents()
        drawer = self.ui._FILL_DRAWER
        self.assertIsNotNone(drawer)
        self.assertFalse(drawer.isVisible())

        self.ui.update_review_fill_drawer(self._open_offer(state))
        for _ in range(3):
            QApplication.processEvents()
        self.assertTrue(drawer.isVisible())
        self.assertEqual(drawer.toggle.text(), "Recent fills (2)")

    def test_the_drawer_starts_collapsed_and_expands_under_the_experience_box(
        self,
    ) -> None:
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(self._state(), "Mining")
        self.ui.update_review_fill_drawer(self._open_offer(self._state()))
        for _ in range(4):
            QApplication.processEvents()

        drawer = self.ui._FILL_DRAWER
        self.assertFalse(drawer.rows.isVisible())
        collapsed_height = drawer.height()
        self.assertGreaterEqual(
            drawer.y(),
            hud.y() + hud.height(),
            "the drawer belongs under the experience bars",
        )

        drawer.toggle.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(drawer.rows.isVisible())
        self.assertGreater(drawer.height(), collapsed_height)
        self.assertLessEqual(
            drawer.y() + drawer.height(),
            self.parent.height(),
            "an expanded drawer must not run off the review screen",
        )

    def test_the_rows_run_newest_first_with_the_settled_two_tones(self) -> None:
        self.ui.update_review_fill_drawer(self._open_offer(self._state()))
        for _ in range(3):
            QApplication.processEvents()

        rows = self.ui._FILL_DRAWER.rows
        self.assertEqual(rows.count(), 2)
        self.assertEqual(rows.item(0).text(), "Now: Yew logs - 4/4 sold")
        self.assertEqual(rows.item(1).text(), "2 cards ago: Iron ore - 3/5 bought")
        # A fully filled offer is green; a partial fill is yellow.
        self.assertEqual(rows.item(0).foreground().color().name(), "#85c54b")
        self.assertEqual(rows.item(1).foreground().color().name(), "#e0b341")

    # ---- offscreen light and dark verification --------------------------

    def test_the_strip_renders_in_both_themes_without_clipping(self) -> None:
        from aqt.qt import QColor, QPalette

        state = _live_star(self._state())
        state["current_utility"] = "shooting_stars"
        state["dnd_favourites"] = ["shooting_stars"]
        state = self._open_offer(state)
        original = QApplication.palette()
        try:
            for theme, window, text in (
                ("light", "#f0f0f0", "#101010"),
                ("dark", "#202020", "#f0f0f0"),
            ):
                palette = QPalette(original)
                palette.setColor(QPalette.ColorRole.Window, QColor(window))
                palette.setColor(QPalette.ColorRole.Base, QColor(window))
                palette.setColor(QPalette.ColorRole.Text, QColor(text))
                QApplication.setPalette(palette)
                with self.subTest(theme=theme):
                    hud = self.ui.ReviewHUD(self.parent)
                    self.ui._REVIEW_HUD = hud
                    hud.set_data(state, "Utility / Activities")
                    self.ui.update_review_status_badge(state)
                    self.ui.update_review_fill_drawer(state)
                    self.ui._STATUS_BADGE.button.click()
                    for _ in range(6):
                        QApplication.processEvents()

                    badge = self.ui._STATUS_BADGE
                    drawer = self.ui._FILL_DRAWER
                    popover = self.ui._STATUS_POPOVER
                    # Geometry probes, not pixels: an offscreen grab of a widget
                    # that was never laid out reports stale child geometry.
                    self.assertTrue(hud.isVisible())
                    self.assertTrue(badge.isVisible())
                    self.assertTrue(drawer.isVisible())
                    self.assertTrue(popover.isVisible())
                    self.assertGreater(hud.height(), 0)
                    self.assertLessEqual(
                        hud.height(), 160, "the strip must stay one compact block"
                    )
                    self.assertGreaterEqual(badge.x(), 0)
                    self.assertGreaterEqual(badge.y(), 0)
                    self.assertLessEqual(
                        drawer.y() + drawer.height(), self.parent.height()
                    )
                    self.assertLessEqual(
                        popover.x() + popover.width(), self.parent.width()
                    )
                    for bar in hud.findChildren(QProgressBar):
                        if bar.isVisible():
                            self.assertGreater(bar.height(), 0)
                    rows = popover.findChild(QListWidget, "reviewStatusList")
                    for index in range(rows.count()):
                        colour = rows.item(index).foreground().color()
                        # palette(mid) as text is banned; a dimmed line keeps
                        # the theme's own text hue with reduced alpha.
                        self.assertGreater(colour.alpha(), 100)
                    self.ui.close_review_status_popover()
                    hud.hide()
                    hud.deleteLater()
                    self.ui._REVIEW_HUD = None
        finally:
            QApplication.setPalette(original)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
