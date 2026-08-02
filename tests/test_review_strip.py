"""Offscreen Qt cover for the always-visible reviewer strip.

This replaces `test_farming_hud.py` and `test_distraction_hud.py`. The badges
and XP box live in a native row below Anki's answer bar; translucent drawers
remain upward-opening overlays over the card viewport.

Offscreen rule (.claude/rules/qt-offscreen-screenshots.md): show the parent and
pump events before trusting any geometry.
"""

from __future__ import annotations

import os
import sys
import types
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ADDON_DIR = os.path.dirname(_THIS_DIR)
if _ADDON_DIR not in sys.path:
    sys.path.insert(0, _ADDON_DIR)

try:
    import aqt  # noqa: F401
    from aqt.qt import (
        QApplication,
        QLabel,
        QListWidget,
        QPoint,
        QMainWindow,
        QProgressBar,
        QPushButton,
        Qt,
        QVBoxLayout,
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
        self.parent = QMainWindow()
        self.central = QWidget(self.parent)
        self.parent.setCentralWidget(self.central)
        self.parent.form = types.SimpleNamespace(centralwidget=self.central)
        self.parent.mainLayout = QVBoxLayout()
        self.parent.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.parent.mainLayout.setSpacing(0)
        self.card_web = QWidget(self.parent)
        self.card_web.setObjectName("reviewCardWeb")
        self.bottom_web = QWidget(self.parent)
        self.bottom_web.setObjectName("bottomWeb")
        self.bottom_web.setFixedHeight(72)
        self.parent.mainLayout.addWidget(self.card_web, 1)
        self.parent.mainLayout.addWidget(self.bottom_web, 0)
        self.central.setLayout(self.parent.mainLayout)
        self.parent.bottomWeb = self.bottom_web
        self.parent.reviewer = types.SimpleNamespace(web=self.card_web)
        self.parent.show()
        self.parent.resize(1000, 700)
        for _ in range(4):
            QApplication.processEvents()
        self.old_mw = ui.mw
        self.old_config = ui.get_config_bool
        ui.mw = self.parent
        ui.get_config_bool = lambda key, default=True: True
        ui._REVIEW_HUD = None
        ui._REVIEW_STRIP = None
        ui._BANK_RUN_BUTTON = None
        ui._MAIN_MENU_BUTTON = None
        ui._REVIEW_CONTEXT_STRIP = None
        ui._DND_BADGE = None
        ui._FARMING_BADGE = None
        ui._STATUS_POPOVER = None
        ui._STATUS_POPOVER_BADGE = None
        ui._FILL_DRAWER = None
        ui._EVENT_LOG_DRAWER = None

    def tearDown(self) -> None:
        self.ui.close_review_status_popover()
        for widget in (
            self.ui._REVIEW_STRIP,
            self.ui._REVIEW_CONTEXT_STRIP,
            self.ui._FILL_DRAWER,
            self.ui._EVENT_LOG_DRAWER,
        ):
            if widget is not None:
                widget.hide()
                widget.deleteLater()
        self.ui._DND_BADGE = None
        self.ui._FARMING_BADGE = None
        self.ui._FILL_DRAWER = None
        self.ui._EVENT_LOG_DRAWER = None
        self.ui._REVIEW_HUD = None
        self.ui._REVIEW_STRIP = None
        self.ui._BANK_RUN_BUTTON = None
        self.ui._MAIN_MENU_BUTTON = None
        self.ui._REVIEW_CONTEXT_STRIP = None
        self.ui._STATUS_POPOVER = None
        self.ui._STATUS_POPOVER_BADGE = None
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

    # ---- the badges ------------------------------------------------------

    def test_two_clickable_badges_are_siblings_of_the_mouse_transparent_hud(self) -> None:
        review_hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = review_hud
        review_hud.set_data(self._state(), "Mining")
        self.ui.update_review_status_badge(self._state())
        for _ in range(4):
            QApplication.processEvents()

        dnd = self.ui._DND_BADGE
        farming = self.ui._FARMING_BADGE
        self.assertIs(dnd.parentWidget(), self.ui._REVIEW_STRIP)
        self.assertIs(farming.parentWidget(), self.ui._REVIEW_STRIP)
        self.assertFalse(
            review_hud.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        )
        for badge in (dnd, farming):
            self.assertFalse(
                badge.testAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            )
            self.assertNotIn(badge, QApplication.topLevelWidgets())
        self.assertEqual(dnd._view["title"], "D&D")
        self.assertEqual(dnd.button.text(), "D&&D")
        self.assertEqual(farming.button.text(), "Farming")

    def test_both_badges_keep_their_seats_when_nothing_is_live(self) -> None:
        self.ui.update_review_status_badge(self._state())
        for _ in range(3):
            QApplication.processEvents()

        self.assertTrue(self.ui._DND_BADGE.isVisible())
        self.assertTrue(self.ui._FARMING_BADGE.isVisible())
        self.assertFalse(self.ui._DND_BADGE.badge.isVisible())
        self.assertFalse(self.ui._FARMING_BADGE.badge.isVisible())

    def test_dnd_counts_only_opted_in_world_events_without_polluting_farming(self) -> None:
        state = _live_star(self._state())
        self.ui.update_review_status_badge(state)
        for _ in range(3):
            QApplication.processEvents()

        self.assertFalse(self.ui._DND_BADGE.badge.isVisible())
        self.assertIn("Notification set is empty", self.ui._DND_BADGE.toolTip())
        self.assertFalse(self.ui._FARMING_BADGE.badge.isVisible())

        state["dnd_favourites"] = ["shooting_stars"]
        self.ui.update_review_status_badge(state)
        for _ in range(3):
            QApplication.processEvents()

        self.assertEqual(self.ui._DND_BADGE.badge.text(), "1")
        self.assertIn("stardust", self.ui._DND_BADGE.toolTip())

    def test_farming_renders_crops_and_queue_without_polluting_dnd(self) -> None:
        from ankiscape.logic.farming_logic import add_farm_queue_step_pure

        state = self._ripe_crop(self._state())
        state, step_id, _info = add_farm_queue_step_pure(
            state, "plant", "falador_allotment_south", crop_id="potato"
        )
        self.assertIsNotNone(step_id)
        self.ui.update_review_status_badge(state)
        for _ in range(3):
            QApplication.processEvents()

        farming = self.ui._FARMING_BADGE
        self.assertEqual(farming.badge.text(), "1")
        self.assertEqual(farming.queue_badge.text(), "Q1")
        self.assertFalse(self.ui._DND_BADGE.badge.isVisible())
        state["farm_patches"]["falador_allotment_north"].update(
            {"diseased": True, "dead": False}
        )
        self.ui.update_review_status_badge(state)
        QApplication.processEvents()
        self.assertEqual(farming.badge.text(), "!1")

    def test_both_badges_stay_left_of_the_experience_hud_without_fallback(self) -> None:
        review_hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = review_hud
        review_hud.set_data(self._state(), "Mining")
        self.ui.update_review_status_badge(self._state())
        for _ in range(4):
            QApplication.processEvents()

        dnd = self.ui._DND_BADGE
        farming = self.ui._FARMING_BADGE
        self.assertLess(dnd.x() + dnd.width(), farming.x() + 1)
        self.assertLess(farming.x() + farming.width(), review_hud.x() + 1)

        self.ui.update_review_bank_run_button(
            self._state(), "mining", lambda: None
        )
        QApplication.processEvents()
        bank = self.ui._BANK_RUN_BUTTON
        self.assertIs(bank.parentWidget(), review_hud)
        self.assertEqual(bank.text(), "Bank run")
        self.assertEqual(
            bank.toolTip(), "Deposit inventory and restock same supplies"
        )
        self.assertGreater(bank.x(), review_hud.width() // 2)
        self.assertGreater(bank.y(), review_hud.height() // 2)
        self.assertEqual(
            self.ui._REVIEW_STRIP.height(), self.ui.REVIEW_STRIP_HEIGHT
        )

    def test_strip_seats_and_nested_bank_button_fit_narrow_reviewers(self) -> None:
        state = self._state()
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_bank_run_button(state, "mining", lambda: None)

        for width in (900, 760, 640, 560, 480):
            with self.subTest(width=width):
                self.parent.resize(width, 700)
                for _ in range(5):
                    QApplication.processEvents()
                strip = self.ui._REVIEW_STRIP
                seats = (
                    self.ui._DND_BADGE,
                    self.ui._FARMING_BADGE,
                    hud,
                    self.ui._MAIN_MENU_BUTTON,
                )
                for left, right in zip(seats, seats[1:]):
                    self.assertLessEqual(
                        left.geometry().right(), right.geometry().left() - 1
                    )
                self.assertGreaterEqual(seats[0].geometry().left(), 0)
                self.assertLess(seats[-1].geometry().right(), strip.width())
                self.assertGreater(hud.width(), 0)

    def test_bank_run_button_uses_compact_native_styling(self) -> None:
        state = self._state()
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_bank_run_button(state, "mining", lambda: None)
        for _ in range(5):
            QApplication.processEvents()

        bank = self.ui._BANK_RUN_BUTTON
        self.assertEqual(bank.styleSheet(), "")
        self.assertEqual(bank.text(), "Bank run")
        self.assertEqual(bank.size(), bank.sizeHint())

    def test_native_strip_owns_the_main_menu_button_and_routes_its_click(self) -> None:
        state = self._state()
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Mining")
        with patch(
            "ankiscape.core.injectors.open_main_menu_from_reviewer"
        ) as open_menu:
            self.ui.update_review_status_badge(state)
            for _ in range(4):
                QApplication.processEvents()

            button = self.ui._MAIN_MENU_BUTTON
            self.assertIs(button.parentWidget(), self.ui._REVIEW_STRIP)
            self.assertFalse(button.icon().isNull())
            self.assertEqual(button.toolTip(), "AnkiScape")
            self.assertEqual(button.accessibleName(), "AnkiScape")
            button.click()
            QApplication.processEvents()
        open_menu.assert_called_once_with(False)

    def test_native_menu_button_honours_the_floating_widget_setting(self) -> None:
        config = {"ankiscape_floating_enabled": False}
        self.ui.get_config_bool = lambda key, default=True: config.get(key, default)
        self.ui.ensure_review_strip()
        QApplication.processEvents()

        button = self.ui._MAIN_MENU_BUTTON
        self.assertFalse(button.property("ankiscapeOverlayRequested"))
        self.assertTrue(button.isHidden())

        config["ankiscape_floating_enabled"] = True
        self.ui.ensure_review_strip()
        QApplication.processEvents()
        self.assertTrue(button.property("ankiscapeOverlayRequested"))
        self.assertFalse(button.isHidden())

    # ---- the split popovers ---------------------------------------------

    def test_farming_popover_opens_crop_rows_and_the_full_farm(self) -> None:
        opened: list = []
        state = self._ripe_crop(self._state())
        self.ui.update_review_status_badge(
            state, None, lambda patch_id=None: opened.append(patch_id)
        )
        badge = self.ui._FARMING_BADGE
        badge.button.click()
        for _ in range(5):
            QApplication.processEvents()

        rows = self.ui._STATUS_POPOVER.findChild(QListWidget, "reviewStatusList")
        self.assertEqual(rows.count(), 1)
        self.assertEqual(
            rows.item(0).data(Qt.ItemDataRole.UserRole),
            "falador_allotment_north",
        )
        rows.itemActivated.emit(rows.item(0))
        QApplication.processEvents()
        self.assertEqual(opened, ["falador_allotment_north"])

        badge.button.click()
        QApplication.processEvents()
        self.ui._STATUS_POPOVER.findChild(
            QPushButton, "reviewStatusOpenFarmButton"
        ).click()
        QApplication.processEvents()
        self.assertEqual(opened, ["falador_allotment_north", None])

    def test_active_fish_flingers_notification_opens_status_and_navigates(self) -> None:
        from ankiscape.data.fish_flingers_data import FISH_FLINGERS_ACTIVITY_ID
        from ankiscape.logic.fish_flingers_logic import enter_fish_flingers_pure

        opened: list = []
        state, ok, info = enter_fish_flingers_pure(self._state())
        self.assertTrue(ok, info)
        state["dnd_favourites"] = [FISH_FLINGERS_ACTIVITY_ID]
        self.ui.update_review_status_badge(
            state, lambda activity_id=None: opened.append(activity_id), None
        )
        self.assertEqual(self.ui._DND_BADGE.badge.text(), "1")

        self.ui._DND_BADGE.button.click()
        for _ in range(4):
            QApplication.processEvents()

        rows = self.ui._STATUS_POPOVER.findChild(QListWidget, "reviewStatusList")
        self.assertEqual(rows.count(), 1)
        self.assertIn("Fish Flingers · Review 1/8", rows.item(0).text())
        self.assertIn("stock", rows.item(0).text())
        self.assertIn("tickets remaining", rows.item(0).text())
        self.assertEqual(
            rows.item(0).data(Qt.ItemDataRole.UserRole),
            FISH_FLINGERS_ACTIVITY_ID,
        )
        rows.itemActivated.emit(rows.item(0))
        QApplication.processEvents()
        self.assertEqual(opened, [FISH_FLINGERS_ACTIVITY_ID])

    def test_hide_lifecycle_closes_popovers_and_removes_both_seats(self) -> None:
        state = self._state()
        self.ui.update_review_status_badge(state)
        self.ui._DND_BADGE.button.click()
        QApplication.processEvents()
        self.assertIsNotNone(self.ui._STATUS_POPOVER)

        self.ui.hide_review_hud()
        QApplication.processEvents()
        self.assertFalse(self.ui._DND_BADGE.isVisible())
        self.assertFalse(self.ui._FARMING_BADGE.isVisible())
        self.assertIsNone(self.ui._STATUS_POPOVER)

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

    def test_combat_hud_renders_red_resources_and_the_simulated_clock(self) -> None:
        state = self._state()
        state.update(
            {
                "current_combat_target": "chicken",
                "constitution_level": 73,
                "combat_lifepoints": 512,
                "prayer_level": 50,
                "combat_prayer_points": 310,
                "summoning_level": 42,
                "summoning_state": {"summoning_points_current": 17},
                "shop_market_clock": {"answered_cards": 9, "market_tick": 9},
            }
        )
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Combat")
        self.assertEqual(hud.clock_lbl.text(), "12:00 PM")
        state["shop_market_clock"] = {"answered_cards": 10, "market_tick": 10}
        hud.set_data(state, "Combat")
        self.parent.resize(1000, 560)
        hud.show()
        for _ in range(4):
            QApplication.processEvents()

        self.assertEqual(hud.progress.styleSheet(), hud.enemy_progress.styleSheet())
        self.assertTrue(hud.combat_resources.isVisible())
        self.assertEqual(hud.combat_resource_labels["lifepoints"].text(), "512/730")
        self.assertEqual(hud.combat_resource_labels["prayer"].text(), "31/50")
        self.assertEqual(hud.combat_resource_labels["summoning"].text(), "17/42")
        for resource_id in ("lifepoints", "prayer", "summoning"):
            icon = hud.findChild(QLabel, f"combatHudResourceIcon_{resource_id}")
            self.assertIsNotNone(icon)
            self.assertIsNotNone(icon.pixmap())
            self.assertFalse(icon.pixmap().isNull())

        self.assertEqual(hud.clock_lbl.text(), "1:00 PM")
        self.assertEqual(hud.clock_lbl.toolTip(), "10 cards = 1 hour")
        clock_pos = hud.clock_lbl.mapTo(hud, QPoint(0, 0))
        progress_pos = hud.progress.mapTo(hud, QPoint(0, 0))
        self.assertLess(clock_pos.x() + hud.clock_lbl.width(), progress_pos.x())
        self.assertLess(clock_pos.y(), progress_pos.y())
        self.assertLessEqual(hud.height(), 128)

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

    def test_translucent_drawers_expand_upward_without_moving_the_native_strip(
        self,
    ) -> None:
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        state = self._event_log_state(2)
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_bank_run_button(state, "mining", lambda: None)
        self.ui.update_review_event_log_drawer(state)
        self.ui.update_review_fill_drawer(self._open_offer(state))
        for _ in range(4):
            QApplication.processEvents()

        strip = self.ui._REVIEW_STRIP
        event = self.ui._EVENT_LOG_DRAWER
        ge = self.ui._FILL_DRAWER
        strip_geometry = strip.geometry()
        strip_top = strip.mapTo(self.parent, QPoint(0, 0)).y()
        self.assertLessEqual(event.y() + event.height(), strip_top)
        self.assertLessEqual(ge.y() + ge.height(), event.y())
        self.assertIn(self.ui._HUD_BG, event.styleSheet())
        self.assertIn(self.ui._HUD_BG, ge.styleSheet())

        event.toggle.click()
        ge.toggle.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(event.rows.isVisible())
        self.assertTrue(ge.rows.isVisible())
        self.assertEqual(strip.geometry(), strip_geometry)
        strip_top = strip.mapTo(self.parent, QPoint(0, 0)).y()
        self.assertLessEqual(event.y() + event.height(), strip_top)
        self.assertLessEqual(ge.y() + ge.height(), event.y())

        self.parent.resize(667, 602)
        for _ in range(6):
            QApplication.processEvents()
        self.assertTrue(event.geometry().intersects(self.card_web.geometry()))
        self.assertFalse(event.geometry().intersects(self.bottom_web.geometry()))
        self.assertFalse(strip.geometry().intersects(self.card_web.geometry()))

    def test_drawer_reparents_when_bottom_web_moves_into_centralwidget(self) -> None:
        late_window = QMainWindow()
        late_bottom_web = QWidget(late_window)
        late_window.bottomWeb = late_bottom_web
        self.ui.mw = late_window
        try:
            self.ui.ensure_review_fill_drawer()
            self.ui.ensure_review_event_log_drawer()
            drawers = (self.ui._FILL_DRAWER, self.ui._EVENT_LOG_DRAWER)
            for drawer in drawers:
                self.assertIs(drawer.parentWidget(), late_window)

            central = QWidget(late_window)
            late_window.setCentralWidget(central)
            late_window.mainLayout = QVBoxLayout()
            late_window.mainLayout.addWidget(QWidget(late_window), 1)
            late_window.mainLayout.addWidget(late_bottom_web, 0)
            central.setLayout(late_window.mainLayout)
            late_window.show()
            late_window.resize(760, 560)
            for _ in range(4):
                QApplication.processEvents()

            self.ui.ensure_review_fill_drawer()
            self.ui.ensure_review_event_log_drawer()
            for drawer in drawers:
                self.assertIs(drawer.parentWidget(), central)
        finally:
            self.ui.mw = self.parent
            late_window.hide()
            late_window.deleteLater()

    def test_drawer_sibling_stacking_follows_each_toggle_state(self) -> None:
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        state = self._event_log_state(2)
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_event_log_drawer(state)
        self.ui.update_review_fill_drawer(self._open_offer(state))
        for _ in range(4):
            QApplication.processEvents()

        for drawer in (self.ui._EVENT_LOG_DRAWER, self.ui._FILL_DRAWER):
            with self.subTest(drawer=drawer.objectName()):
                parent = self.bottom_web.parentWidget()
                self.assertIs(drawer.parentWidget(), parent)
                siblings = parent.children()
                self.assertLess(
                    siblings.index(drawer), siblings.index(self.bottom_web)
                )
                drawer.toggle.click()
                for _ in range(3):
                    QApplication.processEvents()
                siblings = parent.children()
                self.assertGreater(
                    siblings.index(drawer), siblings.index(self.bottom_web)
                )
                drawer.toggle.click()
                for _ in range(3):
                    QApplication.processEvents()
                siblings = parent.children()
                self.assertLess(
                    siblings.index(drawer), siblings.index(self.bottom_web)
                )

    def test_two_expanded_drawers_stay_reachable_at_reviewer_height(self) -> None:
        self.parent.resize(760, 560)
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        state = self._event_log_state()
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_bank_run_button(state, "mining", lambda: None)
        self.ui.update_review_event_log_drawer(state)
        self.ui.update_review_fill_drawer(self._open_offer(state))
        self.ui._EVENT_LOG_DRAWER.toggle.click()
        self.ui._FILL_DRAWER.toggle.click()
        for _ in range(6):
            QApplication.processEvents()

        event = self.ui._EVENT_LOG_DRAWER
        ge = self.ui._FILL_DRAWER
        answer_bar_top = self.bottom_web.mapTo(self.parent, QPoint(0, 0)).y()
        self.assertGreaterEqual(ge.y(), 8)
        self.assertLessEqual(ge.y() + ge.height(), event.y())
        self.assertLessEqual(event.y() + event.height(), answer_bar_top)

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

    def test_ge_rows_open_the_exchange_and_hidden_state_is_cleared(self) -> None:
        opened = []
        self.ui.update_review_fill_drawer(
            self._open_offer(self._state()), lambda: opened.append(True)
        )
        for _ in range(3):
            QApplication.processEvents()

        drawer = self.ui._FILL_DRAWER
        drawer.rows.itemClicked.emit(drawer.rows.item(0))
        self.assertEqual(opened, [True])
        drawer.toggle.setChecked(True)

        self.ui.update_review_fill_drawer(self._state())
        for _ in range(3):
            QApplication.processEvents()
        self.assertFalse(drawer.isVisible())
        self.assertEqual(drawer.rows.count(), 0)
        self.assertFalse(drawer.toggle.isChecked())

    # ---- event log drawer ------------------------------------------------

    def _event_log_state(self, count: int = 25) -> dict:
        from ankiscape.logic.review_strip_logic import record_review_event_pure

        state = self._state()
        for review in range(count):
            state["shop_market_clock"] = {
                "answered_cards": review,
                "market_tick": review,
            }
            kind = ("xp", "achievement", "activity")[review % 3]
            state = record_review_event_pure(state, kind, f"event {review}")
        return state

    def test_event_log_starts_collapsed_at_ten_and_lazily_shows_more(self) -> None:
        self.ui.update_review_event_log_drawer(self._event_log_state())
        for _ in range(4):
            QApplication.processEvents()

        drawer = self.ui._EVENT_LOG_DRAWER
        self.assertTrue(drawer.isVisible())
        self.assertFalse(drawer.rows.isVisible())
        drawer.toggle.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertTrue(drawer.rows.isVisible())
        self.assertEqual(drawer.rows.count(), 10)
        self.assertEqual(drawer.rows.item(0).text(), "")
        row_label = drawer.rows.itemWidget(drawer.rows.item(0))
        self.assertIsInstance(row_label, QLabel)
        self.assertEqual(row_label.text(), "0 reviews ago · event 24")
        self.assertTrue(row_label.wordWrap())
        self.assertTrue(
            row_label.textInteractionFlags()
            & Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.assertTrue(drawer.show_more.isVisible())
        drawer.show_more.click()
        for _ in range(4):
            QApplication.processEvents()
        self.assertEqual(drawer.rows.count(), 20)

    def test_event_log_row_density_stays_compact_for_the_default_ten(self) -> None:
        self.parent.resize(760, 560)
        self.ui.update_review_event_log_drawer(self._event_log_state(10))
        for _ in range(4):
            QApplication.processEvents()
        drawer = self.ui._EVENT_LOG_DRAWER
        drawer.toggle.click()
        for _ in range(6):
            QApplication.processEvents()

        self.assertEqual(drawer.rows.count(), 10)
        self.assertLessEqual(drawer.rows.item(0).sizeHint().height(), 18)
        self.assertEqual(drawer.height(), 186)

    def test_xp_rows_are_not_coloured_like_ge_status(self) -> None:
        state = self._state()
        from ankiscape.logic.review_strip_logic import record_review_event_pure

        state = record_review_event_pure(
            state,
            "xp",
            "+25 XP · Mining and Woodcutting from a deliberately long aggregate",
        )
        self.ui.update_review_event_log_drawer(state)
        self.ui._EVENT_LOG_DRAWER.toggle.click()
        for _ in range(4):
            QApplication.processEvents()

        label = self.ui._EVENT_LOG_DRAWER.rows.itemWidget(
            self.ui._EVENT_LOG_DRAWER.rows.item(0)
        )
        style = label.styleSheet().lower()
        self.assertNotIn("#85c54b", style)
        self.assertNotIn("#e0b341", style)

    # ---- card-safe geometry ---------------------------------------------

    def test_native_strip_never_intersects_the_card_at_both_probe_geometries(self) -> None:
        state = self._event_log_state(3)
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_bank_run_button(state, "mining", lambda: None)
        self.ui.update_review_event_log_drawer(state)

        for width, height in ((667, 602), (1366, 768)):
            with self.subTest(size=(width, height)):
                self.parent.resize(width, height)
                for _ in range(6):
                    QApplication.processEvents()
                strip = self.ui._REVIEW_STRIP
                self.assertIsNot(strip.parentWidget(), self.card_web)
                self.assertLess(
                    self.parent.mainLayout.indexOf(self.card_web),
                    self.parent.mainLayout.indexOf(self.bottom_web),
                )
                self.assertLess(
                    self.parent.mainLayout.indexOf(self.bottom_web),
                    self.parent.mainLayout.indexOf(strip),
                )
                self.assertFalse(strip.geometry().intersects(self.card_web.geometry()))
                self.assertLessEqual(
                    self.card_web.geometry().bottom(),
                    self.bottom_web.geometry().top(),
                )
                self.assertLessEqual(
                    self.bottom_web.geometry().bottom(), strip.geometry().top()
                )

                before = strip.geometry()
                self.ui._EVENT_LOG_DRAWER.toggle.setChecked(True)
                for _ in range(6):
                    QApplication.processEvents()
                self.assertEqual(strip.geometry(), before)
                self.assertFalse(strip.geometry().intersects(self.card_web.geometry()))
                self.ui._EVENT_LOG_DRAWER.toggle.setChecked(False)

    def test_floating_xp_popup_reanchors_to_the_native_strip(self) -> None:
        state = self._state()
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_bank_run_button(state, "mining", lambda: None)

        popup = self.ui.ExpPopup(self.parent)
        self.parent.exp_popup = popup
        popup.show_text("+25 XP")
        for _ in range(5):
            QApplication.processEvents()
        first_anchor = popup._last_strip_anchor

        self.parent.resize(667, 602)
        for _ in range(5):
            QApplication.processEvents()
        self.assertNotEqual(popup._last_strip_anchor, first_anchor)
        hud_top = hud.mapTo(self.parent, QPoint(0, 0)).y()
        self.assertLessEqual(popup.y() + popup.height(), hud_top)
        popup.hide()
        popup.deleteLater()

    def test_native_strip_and_bank_button_stay_visible_in_a_short_window(self) -> None:
        state = self._state()
        hud = self.ui.ReviewHUD(self.parent)
        self.ui._REVIEW_HUD = hud
        hud.set_data(state, "Mining")
        self.ui.update_review_status_badge(state)
        self.ui.update_review_bank_run_button(state, "mining", lambda: None)

        self.parent.resize(1000, 190)
        for _ in range(5):
            QApplication.processEvents()
        self.assertTrue(self.ui._REVIEW_STRIP.isVisible())
        self.assertTrue(self.ui._BANK_RUN_BUTTON.isVisible())
        self.assertFalse(
            self.ui._REVIEW_STRIP.geometry().intersects(self.card_web.geometry())
        )

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
                    self.ui._DND_BADGE.button.click()
                    for _ in range(6):
                        QApplication.processEvents()

                    badge = self.ui._DND_BADGE
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
