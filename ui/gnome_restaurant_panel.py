"""Compact Gnome Restaurant panel; the pure view owns every UI rule.

Layout answer for design fork 3.19: one delivery ticket at a time. The order line
says what to do next, the bar shows what is left of the source delivery window, and
the reward ledger is a single line because it changes once every twelve deliveries.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..core.constants import UTILITY_ACTIVITY_DATA
from ..data.gnome_restaurant_data import (
    GNOME_RESTAURANT_ACTIVITY_ID,
    GNOME_RESTAURANT_DIFFICULTIES,
)
from ..logic.gnome_restaurant_logic import gnome_restaurant_view_pure

try:
    from aqt.qt import (  # type: ignore
        QComboBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPixmap,
        QProgressBar,
        QPushButton,
        Qt,
        QVBoxLayout,
        QWidget,
    )

    HAS_QT = True
except Exception:
    HAS_QT = False


if HAS_QT:

    class GnomeRestaurantPanel(QFrame):
        def __init__(
            self,
            player_data: Mapping[str, Any],
            *,
            on_command: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
            on_select: Callable[[str], bool] | None = None,
            on_changed: Callable[[], None] | None = None,
            game_speed: Callable[[], int] = lambda: 1,
            parent: QWidget | None = None,
        ) -> None:
            super().__init__(parent)
            self._player_data = player_data
            self._game_speed = game_speed
            self._on_command = on_command
            self._on_select = on_select
            self._on_changed = on_changed
            self.setObjectName("gnomeRestaurantPanel")
            self.setStyleSheet(
                "QFrame#gnomeRestaurantPanel { border: 1px solid palette(mid); "
                "border-radius: 8px; background: palette(base); }"
            )
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(5)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            icon = QLabel(header)
            icon.setFixedSize(32, 32)
            icon_path = str(
                UTILITY_ACTIVITY_DATA[GNOME_RESTAURANT_ACTIVITY_ID].get("icon_path", "")
            )
            if icon_path:
                icon.setPixmap(
                    QPixmap(icon_path).scaled(
                        32,
                        32,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            title = QLabel("Gnome Restaurant", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status_chip = QLabel(header)
            self.status_chip.setObjectName("gnomeRestaurantStatusChip")
            self.status_chip.setStyleSheet("font-size: 11px; color: palette(text);")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status_chip)
            layout.addWidget(header)

            self.ticket = QLabel(self)
            self.ticket.setObjectName("gnomeRestaurantTicket")
            self.ticket.setWordWrap(True)
            self.ticket.setStyleSheet("color: palette(text);")
            layout.addWidget(self.ticket)

            self.window_bar = QProgressBar(self)
            self.window_bar.setObjectName("gnomeRestaurantWindowBar")
            self.window_bar.setTextVisible(True)
            layout.addWidget(self.window_bar)

            self.ledger = QLabel(self)
            self.ledger.setObjectName("gnomeRestaurantLedger")
            self.ledger.setWordWrap(True)
            self.ledger.setStyleSheet("font-size: 11px; color: palette(text);")
            layout.addWidget(self.ledger)

            plan = QWidget(self)
            plan_layout = QHBoxLayout(plan)
            plan_layout.setContentsMargins(0, 0, 0, 0)
            plan_layout.setSpacing(6)
            self.difficulty_combo = QComboBox(plan)
            self.difficulty_combo.setObjectName("gnomeRestaurantDifficultyCombo")
            self.difficulty_combo.setAccessibleName("Gnome Restaurant job difficulty")
            for difficulty, label in GNOME_RESTAURANT_DIFFICULTIES:
                self.difficulty_combo.addItem(label, difficulty)
            self.save_button = QPushButton("Save", plan)
            self.save_button.setObjectName("gnomeRestaurantSaveButton")
            plan_layout.addWidget(QLabel("Jobs", plan))
            plan_layout.addWidget(self.difficulty_combo, 1)
            plan_layout.addWidget(self.save_button)
            layout.addWidget(plan)

            self.requirements = QLabel(self)
            self.requirements.setObjectName("gnomeRestaurantRequirements")
            self.requirements.setWordWrap(True)
            self.requirements.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.requirements)

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("gnomeRestaurantPrimaryButton")
            self.decline_button = QPushButton("Decline", actions)
            self.decline_button.setObjectName("gnomeRestaurantDeclineButton")
            self.leave_button = QPushButton("Quit job", actions)
            self.leave_button.setObjectName("gnomeRestaurantLeaveButton")
            self.leave_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.decline_button)
            actions_layout.addWidget(self.leave_button)
            layout.addWidget(actions)

            token = QWidget(self)
            token_layout = QHBoxLayout(token)
            token_layout.setContentsMargins(0, 0, 0, 0)
            token_layout.setSpacing(6)
            self.token_button = QPushButton("Order free food", token)
            self.token_button.setObjectName("gnomeRestaurantTokenButton")
            self.reclaim_button = QPushButton("Replace token", token)
            self.reclaim_button.setObjectName("gnomeRestaurantReclaimButton")
            token_layout.addWidget(self.token_button, 1)
            token_layout.addWidget(self.reclaim_button)
            layout.addWidget(token)

            self.save_button.clicked.connect(lambda _checked=False: self._save_plan())
            self.primary_button.clicked.connect(lambda _checked=False: self._primary())
            self.decline_button.clicked.connect(
                lambda _checked=False: self._run_command("decline_order")
            )
            self.leave_button.clicked.connect(lambda _checked=False: self._confirm_leave())
            self.token_button.clicked.connect(
                lambda _checked=False: self._run_command("activate_token")
            )
            self.reclaim_button.clicked.connect(
                lambda _checked=False: self._run_command("reclaim_token")
            )
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def _run_command(
            self, action_id: str, payload: Mapping[str, Any] | None = None
        ) -> dict[str, Any]:
            result = (
                dict(self._on_command(action_id, payload or {}) or {})
                if self._on_command is not None
                else {"ok": False, "message": "Gnome Restaurant actions are unavailable."}
            )
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Gnome Restaurant",
                    str(result.get("message", "Action failed.")),
                )
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _save_plan(self) -> None:
            self._run_command(
                "set_policy",
                {"difficulty_policy": str(self.difficulty_combo.currentData() or "")},
            )

        def _primary(self) -> None:
            view = gnome_restaurant_view_pure(self._player_data, speed=self._game_speed())
            if not view["service_open"]:
                self._run_command("open_service")
                return
            if not view["order"] and not self._run_command("accept_order").get("ok", False):
                return
            if self._on_select is not None:
                self._on_select(GNOME_RESTAURANT_ACTIVITY_ID)
            self.refresh()

        def _confirm_leave(self) -> None:
            answer = QMessageBox.question(
                self,
                "Quit the delivery job?",
                "Hand the delivery box back and drop the outstanding order?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("leave")

        def refresh(self) -> None:
            view = gnome_restaurant_view_pure(self._player_data, speed=self._game_speed())
            enabled = self._on_command is not None
            blocked = self.difficulty_combo.blockSignals(True)
            index = self.difficulty_combo.findData(str(view["difficulty_policy"]))
            if index >= 0:
                self.difficulty_combo.setCurrentIndex(index)
            self.difficulty_combo.blockSignals(blocked)
            self.difficulty_combo.setEnabled(
                enabled and bool(view["policy_controls_enabled"])
            )
            self.save_button.setEnabled(enabled and bool(view["policy_controls_enabled"]))

            self.status_chip.setText(
                "ON A JOB"
                if view["order"]
                else "HIRED"
                if view["service_open"]
                else "CLOSED"
            )
            if view["order"]:
                self.ticket.setText(
                    f"{view['order_text']} · {view['order_item_held']} held"
                )
            else:
                training = view["training"]
                self.ticket.setText(
                    str(view["status_text"])
                    if view["service_open"]
                    else f"{view['status_text']} "
                    f"({training['dishes_prepared']}/{training['dishes_required']} dishes, "
                    f"{training['cocktails_prepared']}/{training['cocktails_required']} cocktails)"
                )
            self.window_bar.setVisible(bool(view["order"]))
            self.window_bar.setRange(0, max(1, int(view["order_limit_minutes"])))
            self.window_bar.setValue(int(view["order_minutes_left"]))
            self.window_bar.setFormat(
                f"{view['order_minutes_left']} of {view['order_limit_minutes']} "
                "delivery minutes left"
            )
            self.ledger.setText(str(view["ledger_text"]))

            reasons = (
                view["review_reasons"] if view["service_open"] else view["entry_reasons"]
            )
            self.requirements.setText(" · ".join(str(value) for value in reasons))
            self.requirements.setVisible(bool(reasons))

            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(enabled and bool(view["primary_enabled"]))
            self.decline_button.setEnabled(enabled and bool(view["decline_enabled"]))
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_visible"]))
            self.token_button.setEnabled(enabled and bool(view["token_activate_enabled"]))
            self.token_button.setToolTip(str(view["token_activate_reason"]))
            self.reclaim_button.setVisible(bool(view["token_reclaim_enabled"]))
            self.reclaim_button.setEnabled(
                enabled and bool(view["token_reclaim_enabled"])
            )

else:

    class GnomeRestaurantPanel:
        def __init__(self, player_data: Mapping[str, Any], **kwargs: Any) -> None:
            self._player_data = player_data

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
