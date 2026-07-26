"""Dedicated Clan Wars activity panel with a Qt-free import fallback."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from ..data.clan_wars_data import (
    CLAN_WARS_ACTIVITY_ID,
    CLAN_WARS_MAX_REVIEWS,
    CLAN_WARS_MODES,
    CLAN_WARS_POLICIES,
    CLAN_WARS_RED_MODE,
)
from ..logic.clan_wars_logic import clan_wars_view_pure

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
                "color: palette(mid); font-size: 11px; font-weight: 700;"
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

            self.progress = QProgressBar(self)
            self.progress.setObjectName("clanWarsProgress")
            self.progress.setRange(0, CLAN_WARS_MAX_REVIEWS)
            self.progress.setTextVisible(True)
            layout.addWidget(self.progress)

            plan = QWidget(self)
            plan_layout = QGridLayout(plan)
            plan_layout.setContentsMargins(0, 0, 0, 0)
            plan_layout.setHorizontalSpacing(6)
            plan_layout.setVerticalSpacing(5)
            self.mode_combo = QComboBox(plan)
            self.mode_combo.setObjectName("clanWarsModeCombo")
            self.mode_combo.setAccessibleName("Clan Wars portal mode")
            for mode in CLAN_WARS_MODES:
                self.mode_combo.addItem(mode.display_name, mode.id)
            self.policy_combo = QComboBox(plan)
            self.policy_combo.setObjectName("clanWarsPolicyCombo")
            self.policy_combo.setAccessibleName("Clan Wars combat policy")
            for policy in CLAN_WARS_POLICIES:
                self.policy_combo.addItem(policy.display_name, policy.id)
            self.save_button = QPushButton("Save plan", plan)
            self.save_button.setObjectName("clanWarsSavePlanButton")
            plan_layout.addWidget(self.mode_combo, 0, 0)
            plan_layout.addWidget(self.policy_combo, 0, 1)
            plan_layout.addWidget(self.save_button, 0, 2)
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
                lambda _index: self._render_selection()
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

        def selected_policy(self) -> str:
            return str(self.policy_combo.currentData() or "")

        def _set_combo_value(self, combo: QComboBox, value: str) -> None:
            index = combo.findData(value)
            if index < 0:
                return
            blocked = combo.blockSignals(True)
            combo.setCurrentIndex(index)
            combo.blockSignals(blocked)

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
            self._run_command(
                "set_policy",
                {
                    "mode": self.selected_mode(),
                    "strategy": self.selected_policy(),
                },
            )

        def _enter_or_select(self) -> None:
            view = clan_wars_view_pure(self._player_data)
            if not view["active"]:
                if self.selected_mode() == CLAN_WARS_RED_MODE:
                    answer = QMessageBox.question(
                        self,
                        "Enter the dangerous red portal?",
                        "On death, all carried and worn items are destroyed "
                        "except one highest-value slot when Protect Item applies. "
                        "There is no gravestone or Death's Office recovery, and "
                        "teleport escape is forbidden.",
                        QMessageBox.StandardButton.Yes
                        | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if answer != QMessageBox.StandardButton.Yes:
                        return
                result = self._run_command(
                    "enter",
                    {
                        "mode": self.selected_mode(),
                        "strategy": self.selected_policy(),
                    },
                )
                if not result.get("ok", False):
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

        def _render_selection(self) -> None:
            if clan_wars_view_pure(self._player_data)["active"]:
                return
            mode_id = self.selected_mode()
            mode = next(row for row in CLAN_WARS_MODES if row.id == mode_id)
            self.status.setText("DANGEROUS" if mode.dangerous else "SAFE")
            self.summary.setText(mode.description)

        def refresh(self) -> None:
            view = clan_wars_view_pure(self._player_data)
            session = view["clan_wars"]
            active = bool(session)
            if active:
                mode_id = str(session["mode"])
                policy_id = str(session["strategy"])
            else:
                mode_id = str(view["selected_mode"])
                policy_id = str(view["selected_strategy"])
            self._set_combo_value(self.mode_combo, mode_id)
            self._set_combo_value(self.policy_combo, policy_id)
            dangerous = mode_id == CLAN_WARS_RED_MODE
            self.status.setText(
                "ACTIVE · DANGEROUS"
                if active and dangerous
                else "ACTIVE · SAFE"
                if active
                else "DANGEROUS"
                if dangerous
                else "SAFE"
            )
            if active:
                review = int(session["review"])
                self.summary.setText(
                    f"{view['mode_display_name']} · "
                    f"{int(session['player_score'])}-"
                    f"{int(session['opponent_score'])} · "
                    f"{session['opponent']['display_name']}"
                )
                self.progress.setValue(review)
                self.progress.setFormat(
                    f"{review}/{CLAN_WARS_MAX_REVIEWS} successful reviews"
                )
            else:
                history = str(view["clan_wars_last_result"])
                record = (
                    f"{int(view['clan_wars_wins'])}W/"
                    f"{int(view['clan_wars_draws'])}D/"
                    f"{int(view['clan_wars_losses'])}L · "
                    f"{int(view['clan_wars_kills'])} kills"
                )
                self.summary.setText(
                    history or f"{view['mode_description']} {record}"
                )
                self.progress.setValue(0)
                self.progress.setFormat(
                    f"Bounded at {CLAN_WARS_MAX_REVIEWS} successful reviews"
                )
            enabled = self._on_command is not None
            self.mode_combo.setEnabled(not active and enabled)
            self.policy_combo.setEnabled(not active and enabled)
            self.save_button.setEnabled(not active and enabled)
            is_selected = (
                str(self._player_data.get("current_utility", ""))
                == CLAN_WARS_ACTIVITY_ID
            )
            self.primary_button.setText(
                "Selected for reviews"
                if active and is_selected
                else "Select for reviews"
                if active
                else "Enter portal"
            )
            self.primary_button.setEnabled(
                enabled
                and not is_selected
                and (active or bool(view["can_enter"]))
            )
            self.teleport_button.setVisible(active)
            self.teleport_button.setEnabled(
                active and bool(view["teleport_escape_allowed"]) and enabled
            )
            self.teleport_button.setToolTip(
                "Teleport escape is forbidden in the dangerous red portal."
                if active and dangerous
                else ""
            )
            self.leave_button.setVisible(active)
            self.leave_button.setEnabled(active and enabled)

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

        def selected_policy(self) -> str:
            return str(
                clan_wars_view_pure(self._player_data)["selected_strategy"]
            )

        def refresh(self) -> None:
            return None
