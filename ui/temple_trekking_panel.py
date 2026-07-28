"""Compact Temple Trekking panel; the pure view owns every UI rule."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..core.constants import UTILITY_ACTIVITY_DATA
from ..data.temple_trekking_data import TEMPLE_TREKKING_ACTIVITY_ID
from ..logic.temple_trekking_logic import temple_trekking_view_pure

try:
    from aqt.qt import (  # type: ignore
        QComboBox,
        QFrame,
        QGridLayout,
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

    class TempleTrekkingPanel(QFrame):
        def __init__(
            self,
            player_data: Mapping[str, Any],
            *,
            on_command: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
            on_select: Callable[[str], bool] | None = None,
            on_changed: Callable[[], None] | None = None,
            parent: QWidget | None = None,
        ) -> None:
            super().__init__(parent)
            self._player_data = player_data
            self._on_command = on_command
            self._on_select = on_select
            self._on_changed = on_changed
            self.setObjectName("templeTrekkingPanel")
            self.setStyleSheet(
                "QFrame#templeTrekkingPanel { border: 1px solid palette(mid); "
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
                UTILITY_ACTIVITY_DATA[TEMPLE_TREKKING_ACTIVITY_ID].get("icon_path", "")
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
            title = QLabel("Temple Trekking", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status_chip = QLabel(header)
            self.status_chip.setStyleSheet("font-size: 11px; color: palette(text);")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status_chip)
            layout.addWidget(header)

            self.event_status = QLabel(self)
            self.event_status.setWordWrap(True)
            self.event_status.setStyleSheet("color: palette(text);")
            layout.addWidget(self.event_status)
            self.companion_status = QLabel(self)
            self.companion_status.setStyleSheet("font-size: 11px; color: palette(text);")
            layout.addWidget(self.companion_status)
            self.companion_health = QProgressBar(self)
            self.companion_health.setObjectName("templeTrekkingCompanionHealth")
            self.companion_health.setTextVisible(True)
            layout.addWidget(self.companion_health)

            plan = QWidget(self)
            grid = QGridLayout(plan)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(6)
            grid.setVerticalSpacing(3)
            self.direction_combo = QComboBox(plan)
            self.route_combo = QComboBox(plan)
            self.companion_combo = QComboBox(plan)
            self.reward_combo = QComboBox(plan)
            self.save_button = QPushButton(plan)
            for widget, name in (
                (self.direction_combo, "Temple Trekking direction"),
                (self.route_combo, "Temple Trekking next route"),
                (self.companion_combo, "Temple Trekking companion"),
                (self.reward_combo, "Temple Trekking token reward"),
            ):
                widget.setAccessibleName(name)
            grid.addWidget(QLabel("Direction", plan), 0, 0)
            grid.addWidget(self.direction_combo, 0, 1)
            grid.addWidget(QLabel("Route", plan), 1, 0)
            grid.addWidget(self.route_combo, 1, 1)
            grid.addWidget(QLabel("Companion", plan), 2, 0)
            grid.addWidget(self.companion_combo, 2, 1)
            grid.addWidget(QLabel("Reward", plan), 3, 0)
            grid.addWidget(self.reward_combo, 3, 1)
            grid.addWidget(self.save_button, 4, 1)
            layout.addWidget(plan)

            self.supplies = QLabel(self)
            self.supplies.setWordWrap(True)
            self.supplies.setStyleSheet("font-size: 11px; color: palette(text);")
            layout.addWidget(self.supplies)
            supply_actions = QWidget(self)
            supply_layout = QHBoxLayout(supply_actions)
            supply_layout.setContentsMargins(0, 0, 0, 0)
            self.food_button = QPushButton("Load Lobster", supply_actions)
            self.pouch_button = QPushButton("Fill Druid pouch", supply_actions)
            supply_layout.addWidget(self.food_button)
            supply_layout.addWidget(self.pouch_button)
            layout.addWidget(supply_actions)

            redemption = QWidget(self)
            redemption_layout = QHBoxLayout(redemption)
            redemption_layout.setContentsMargins(0, 0, 0, 0)
            self.token_combo = QComboBox(redemption)
            self.redeem_button = QPushButton("Redeem token", redemption)
            redemption_layout.addWidget(self.token_combo, 1)
            redemption_layout.addWidget(self.redeem_button)
            layout.addWidget(redemption)

            self.requirements = QLabel(self)
            self.requirements.setWordWrap(True)
            self.requirements.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.requirements)
            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.primary_button = QPushButton(actions)
            self.abandon_button = QPushButton("Abandon", actions)
            self.abandon_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.abandon_button)
            layout.addWidget(actions)

            self.direction_combo.currentIndexChanged.connect(self._direction_changed)
            self.save_button.clicked.connect(lambda _checked=False: self._save_plan())
            self.food_button.clicked.connect(
                lambda _checked=False: self._run_command("stock_food", {"quantity": 28})
            )
            self.pouch_button.clicked.connect(
                lambda _checked=False: self._run_command("prepare_pouch")
            )
            self.primary_button.clicked.connect(
                lambda _checked=False: self._enter_or_select()
            )
            self.redeem_button.clicked.connect(lambda _checked=False: self._redeem())
            self.abandon_button.clicked.connect(
                lambda _checked=False: self._confirm_abandon()
            )
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        @staticmethod
        def _select(combo: QComboBox, value: str) -> None:
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        def _run_command(
            self, action_id: str, payload: Mapping[str, Any] | None = None
        ) -> dict[str, Any]:
            result = (
                dict(self._on_command(action_id, payload or {}) or {})
                if self._on_command is not None
                else {"ok": False, "message": "Temple Trekking actions are unavailable."}
            )
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Temple Trekking",
                    str(result.get("message", "Action failed.")),
                )
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _populate_companions(self, view: Mapping[str, Any]) -> None:
            direction = str(self.direction_combo.currentData() or "trek")
            selected = str(self.companion_combo.currentData() or "")
            blocked = self.companion_combo.blockSignals(True)
            self.companion_combo.clear()
            for row in view["companion_options_by_direction"].get(direction, ()):
                self.companion_combo.addItem(
                    f"{row['display_name']} · {row['difficulty']} · L{row['level']}",
                    row["id"],
                )
            self._select(self.companion_combo, selected)
            self.companion_combo.blockSignals(blocked)

        def _direction_changed(self) -> None:
            self._populate_companions(temple_trekking_view_pure(self._player_data))

        def _save_plan(self) -> None:
            view = temple_trekking_view_pure(self._player_data)
            payload = {}
            if view["direction_control_enabled"]:
                payload["direction"] = str(self.direction_combo.currentData() or "")
            if view["route_control_enabled"]:
                payload["route"] = str(self.route_combo.currentData() or "")
            if view["companion_control_enabled"]:
                payload["companion"] = str(self.companion_combo.currentData() or "")
            if view["reward_control_enabled"]:
                payload["reward"] = str(self.reward_combo.currentData() or "")
            self._run_command("set_policy", payload)

        def _enter_or_select(self) -> None:
            view = temple_trekking_view_pure(self._player_data)
            if not view["active"] and not self._run_command("enter").get("ok", False):
                return
            if self._on_select is not None:
                self._on_select(TEMPLE_TREKKING_ACTIVITY_ID)

        def _redeem(self) -> None:
            self._run_command(
                "redeem",
                {
                    "color": str(self.token_combo.currentData() or ""),
                    "reward_id": str(self.reward_combo.currentData() or ""),
                },
            )

        def _confirm_abandon(self) -> None:
            answer = QMessageBox.question(
                self,
                "Abandon this trek?",
                "Return to the start point without a reward token?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("abandon")

        def refresh(self) -> None:
            view = temple_trekking_view_pure(self._player_data)
            enabled = self._on_command is not None
            combo_rows = (
                (self.direction_combo, view["direction_options"], view["policy"]["direction"]),
                (self.route_combo, view["route_options"], view["policy"]["route"]),
                (self.reward_combo, view["reward_options"], view["policy"]["reward"]),
            )
            for combo, rows, selected in combo_rows:
                blocked = combo.blockSignals(True)
                combo.clear()
                for row in rows:
                    combo.addItem(str(row["display_name"]), row["id"])
                    if combo is self.direction_combo and not row.get("unlocked", True):
                        item = combo.model().item(combo.count() - 1)
                        if item is not None:
                            item.setEnabled(False)
                self._select(combo, str(selected))
                combo.blockSignals(blocked)
            self._populate_companions(view)
            self._select(self.companion_combo, str(view["policy"]["companion"]))
            self.direction_combo.setEnabled(enabled and bool(view["direction_control_enabled"]))
            self.route_combo.setEnabled(enabled and bool(view["route_control_enabled"]))
            self.companion_combo.setEnabled(enabled and bool(view["companion_control_enabled"]))
            self.reward_combo.setEnabled(enabled and bool(view["reward_control_enabled"]))
            self.save_button.setText(str(view["save_plan_label"]))
            self.save_button.setEnabled(enabled and bool(view["save_plan_enabled"]))

            self.status_chip.setText("ACTIVE" if view["active"] else "READY")
            self.event_status.setText(
                f"{view['event_name']} · {view['event_index']}/{view['event_count']} · {view['route_name']}"
            )
            self.companion_status.setText(
                f"{view['companion_name']} · level {view['companion_level']}"
            )
            maximum = max(1, int(view["companion_max_lifepoints"]))
            current = max(0, min(maximum, int(view["companion_lifepoints"])))
            self.companion_health.setRange(0, maximum)
            self.companion_health.setValue(current)
            self.companion_health.setFormat(f"Companion LP {current}/{maximum}")
            self.supplies.setText(
                f"Follower food {view['companion_food']}/28 · "
                f"Druid pouch {view['pouch_charges']}/{view['pouch_charge_cap']} · "
                + " · ".join(
                    f"{color.title()} tokens {count}"
                    for color, count in view["token_counts"].items()
                )
            )
            self.food_button.setEnabled(enabled and bool(view["food_load_enabled"]))
            self.pouch_button.setEnabled(enabled and bool(view["pouch_prepare_enabled"]))
            blocked = self.token_combo.blockSignals(True)
            selected_color = str(self.token_combo.currentData() or "")
            self.token_combo.clear()
            for color in view["available_token_colors"]:
                self.token_combo.addItem(color.title(), color)
            self._select(self.token_combo, selected_color)
            self.token_combo.blockSignals(blocked)
            self.token_combo.setEnabled(enabled and bool(view["redeem_enabled"]))
            self.redeem_button.setEnabled(enabled and bool(view["redeem_enabled"]))
            self.redeem_button.setToolTip(str(view["redeem_reason"]))
            reasons = (
                view["review_reasons"] if view["active"] else view["entry_reasons"]
            )
            self.requirements.setText(" · ".join(str(value) for value in reasons))
            self.requirements.setVisible(bool(reasons))
            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(enabled and bool(view["primary_enabled"]))
            self.abandon_button.setVisible(bool(view["abandon_visible"]))
            self.abandon_button.setEnabled(enabled and bool(view["abandon_visible"]))

else:

    class TempleTrekkingPanel:
        def __init__(self, player_data: Mapping[str, Any], **kwargs: Any) -> None:
            self._player_data = player_data

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
