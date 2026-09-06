"""Dedicated Clan Wars activity panel with a Qt-free import fallback.

The panel renders flags. Every enable, visibility and warning decision is
owned by ``clan_wars_view_pure``; nothing here re-derives a portal rule.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from ..data.clan_wars_data import CLAN_WARS_ACTIVITY_ID
from ..logic.clan_wars_logic import clan_wars_view_pure

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

    class ClanWarsPanel(QFrame):
        """Visible portal policy, match state, and direct-action controls."""

        def __init__(
            self,
            player_data: Mapping[str, Any],
            *,
            on_command: Callable[[str, Mapping[str, Any]], Mapping[str, Any]]
            | None = None,
            on_select: Callable[[str], bool] | None = None,
            on_changed: Callable[[], None] | None = None,
            parent: QWidget | None = None,
        ) -> None:
            super().__init__(parent)
            self._player_data = player_data
            self._on_command = on_command
            self._on_select = on_select
            self._on_changed = on_changed
            self.setObjectName("clanWarsPanel")
            self.setStyleSheet(
                "QFrame#clanWarsPanel { border: 1px solid palette(mid);"
                " border-radius: 8px; background: palette(base); }"
            )

            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(8)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(8)
            icon = QLabel(header)
            icon.setObjectName("clanWarsIcon")
            icon.setFixedSize(32, 32)
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "activityicons",
                "clan_wars.png",
            )
            if os.path.exists(icon_path):
                icon.setPixmap(
                    QPixmap(icon_path).scaled(
                        32,
                        32,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            title = QLabel("Clan Wars", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status = QLabel(header)
            self.status.setObjectName("clanWarsStatusChip")
            self.status.setStyleSheet(
                "color: palette(text); font-size: 11px; font-weight: 700;"
            )
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status)
            layout.addWidget(header)

            self.summary = QLabel(self)
            self.summary.setObjectName("clanWarsSummary")
            self.summary.setWordWrap(True)
            self.summary.setStyleSheet("color: palette(text);")
            layout.addWidget(self.summary)

            self.warning = QLabel(self)
            self.warning.setObjectName("clanWarsWarning")
            self.warning.setWordWrap(True)
            self.warning.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.warning)

            self.progress = QProgressBar(self)
            self.progress.setObjectName("clanWarsProgress")
            self.progress.setTextVisible(True)
            layout.addWidget(self.progress)

            plan = QWidget(self)
            plan_layout = QHBoxLayout(plan)
            plan_layout.setContentsMargins(0, 0, 0, 0)
            plan_layout.setSpacing(6)
            self.mode_combo = QComboBox(plan)
            self.mode_combo.setObjectName("clanWarsModeCombo")
            self.mode_combo.setAccessibleName("Clan Wars portal mode")
            self.save_button = QPushButton("Save plan", plan)
            self.save_button.setObjectName("clanWarsSavePlanButton")
            plan_layout.addWidget(self.mode_combo, 1)
            plan_layout.addWidget(self.save_button)
            layout.addWidget(plan)

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("clanWarsPrimaryButton")
            self.teleport_button = QPushButton("Teleport escape", actions)
            self.teleport_button.setObjectName("clanWarsTeleportButton")
            self.leave_button = QPushButton("Leave portal", actions)
            self.leave_button.setObjectName("clanWarsLeaveButton")
            self.leave_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.teleport_button)
            actions_layout.addWidget(self.leave_button)
            layout.addWidget(actions)

            self.mode_combo.currentIndexChanged.connect(
                lambda _index: self._render_pending_selection()
            )
            self.save_button.clicked.connect(
                lambda _checked=False: self._save_plan()
            )
            self.primary_button.clicked.connect(
                lambda _checked=False: self._enter_or_select()
            )
            self.teleport_button.clicked.connect(
                lambda _checked=False: self._run_command("teleport_escape")
            )
            self.leave_button.clicked.connect(
                lambda _checked=False: self._confirm_leave()
            )
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def selected_mode(self) -> str:
            return str(self.mode_combo.currentData() or "")

        def _mode_option(self, mode_id: str) -> Mapping[str, Any]:
            view = clan_wars_view_pure(self._player_data)
            return next(
                row for row in view["mode_options"] if row["id"] == mode_id
            )

        def _run_command(
            self,
            action_id: str,
            payload: Mapping[str, Any] | None = None,
        ) -> dict[str, Any]:
            if self._on_command is None:
                result = {
                    "ok": False,
                    "message": "Clan Wars actions are unavailable.",
                }
            else:
                result = dict(
                    self._on_command(action_id, payload or {}) or {}
                )
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Clan Wars",
                    str(result.get("message", "Clan Wars action failed.")),
                )
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _save_plan(self) -> None:
            self._run_command("set_policy", {"mode": self.selected_mode()})

        def _enter_or_select(self) -> None:
            if not clan_wars_view_pure(self._player_data)["active"]:
                option = self._mode_option(self.selected_mode())
                warning = str(option["entry_warning"])
                if warning:
                    answer = QMessageBox.question(
                        self,
                        f"Enter the {option['display_name']}?",
                        warning,
                        QMessageBox.StandardButton.Yes
                        | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if answer != QMessageBox.StandardButton.Yes:
                        return
                if not self._run_command(
                    "enter",
                    {"mode": self.selected_mode()},
                ).get("ok", False):
                    return
            if self._on_select is not None:
                self._on_select(CLAN_WARS_ACTIVITY_ID)
            self.refresh()

        def _confirm_leave(self) -> None:
            answer = QMessageBox.question(
                self,
                "Leave Clan Wars?",
                "Leave through the portal and end the bounded match?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("leave")

        def _render_pending_selection(self) -> None:
            """Preview the portal the player is about to save or enter."""
            view = clan_wars_view_pure(self._player_data)
            if view["active"]:
                return
            option = self._mode_option(self.selected_mode())
            self.status.setText(
                "DANGEROUS" if option["dangerous"] else "SAFE"
            )
            self.summary.setText(str(option["description"]))
            self.warning.setText(str(option["entry_warning"]))
            self.warning.setVisible(bool(option["entry_warning"]))

        def refresh(self) -> None:
            view = clan_wars_view_pure(self._player_data)
            blocked = self.mode_combo.blockSignals(True)
            self.mode_combo.clear()
            for option in view["mode_options"]:
                if option["selectable"]:
                    self.mode_combo.addItem(
                        str(option["display_name"]), option["id"]
                    )
            index = self.mode_combo.findData(view["selected_mode"])
            if index >= 0:
                self.mode_combo.setCurrentIndex(index)
            self.mode_combo.blockSignals(blocked)

            self.status.setText(str(view["status_label"]))
            self.summary.setText(str(view["summary_text"]))
            self.warning.setText(str(view["entry_warning"]))
            self.warning.setVisible(bool(view["entry_warning"]))
            self.progress.setRange(0, int(view["progress_maximum"]))
            self.progress.setValue(int(view["progress_value"]))
            self.progress.setFormat(str(view["progress_format"]))

            enabled = self._on_command is not None
            self.mode_combo.setEnabled(
                enabled and bool(view["mode_controls_enabled"])
            )
            self.save_button.setEnabled(
                enabled and bool(view["mode_controls_enabled"])
            )
            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(
                enabled and bool(view["primary_enabled"])
            )
            self.teleport_button.setVisible(
                bool(view["teleport_escape_visible"])
            )
            self.teleport_button.setEnabled(
                enabled and bool(view["teleport_escape_allowed"])
            )
            self.teleport_button.setToolTip(
                str(view["teleport_escape_reason"])
            )
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_visible"]))

else:

    class ClanWarsPanel:
        """Non-Qt placeholder with the same public control surface."""

        def __init__(
            self,
            player_data: Mapping[str, Any],
            *,
            on_command: Callable[[str, Mapping[str, Any]], Mapping[str, Any]]
            | None = None,
            on_select: Callable[[str], bool] | None = None,
            on_changed: Callable[[], None] | None = None,
            parent: Any = None,
        ) -> None:
            self._player_data = player_data
            self._on_command = on_command
            self._on_select = on_select
            self._on_changed = on_changed

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def selected_mode(self) -> str:
            return str(clan_wars_view_pure(self._player_data)["selected_mode"])

        def refresh(self) -> None:
            return None
