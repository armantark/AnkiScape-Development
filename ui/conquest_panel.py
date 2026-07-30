"""Compact paginated Conquest card driven entirely by its pure view."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from ..data.conquest_data import CONQUEST_ACTIVITY_ID, CONQUEST_DOCTRINES
from ..logic.conquest_logic import conquest_view_pure

try:
    from aqt.qt import (  # type: ignore
        QCheckBox,
        QComboBox,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPixmap,
        QPushButton,
        QSpinBox,
        QStackedWidget,
        Qt,
        QVBoxLayout,
        QWidget,
    )

    HAS_QT = True
except Exception:
    HAS_QT = False


if HAS_QT:

    class ConquestPanel(QFrame):
        """Setup, match status, and direct actions without a rendered board."""

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
            self._syncing = False
            self.setObjectName("conquestPanel")
            self.setStyleSheet(
                "QFrame#conquestPanel { border: 1px solid palette(mid);"
                " border-radius: 8px; background: palette(base); }"
            )
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(6)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            icon = QLabel(header)
            icon.setObjectName("conquestIcon")
            icon.setFixedSize(30, 30)
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "activityicons",
                "conquest.png",
            )
            if os.path.exists(icon_path):
                icon.setPixmap(
                    QPixmap(icon_path).scaled(
                        30,
                        30,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            title = QLabel("Conquest", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.rating = QLabel(header)
            self.rating.setObjectName("conquestRating")
            self.rating.setStyleSheet("font-size: 11px; font-weight: 700;")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.rating)
            layout.addWidget(header)

            self.status = QLabel(self)
            self.status.setObjectName("conquestStatus")
            self.status.setWordWrap(True)
            layout.addWidget(self.status)
            self.summary = QLabel(self)
            self.summary.setObjectName("conquestSummary")
            self.summary.setWordWrap(True)
            self.summary.setStyleSheet("color: palette(mid); font-size: 11px;")
            layout.addWidget(self.summary)
            self.warning = QLabel(self)
            self.warning.setObjectName("conquestWarning")
            self.warning.setWordWrap(True)
            self.warning.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.warning)

            self.pages = QStackedWidget(self)
            self.pages.setObjectName("conquestPages")
            layout.addWidget(self.pages)
            self._build_overview_page()
            self._build_squad_page()
            self._build_commands_page()

            pager = QWidget(self)
            pager_layout = QHBoxLayout(pager)
            pager_layout.setContentsMargins(0, 0, 0, 0)
            self.previous_button = QPushButton("‹", pager)
            self.previous_button.setObjectName("conquestPreviousPage")
            self.page_label = QLabel(pager)
            self.page_label.setObjectName("conquestPageLabel")
            self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.next_button = QPushButton("›", pager)
            self.next_button.setObjectName("conquestNextPage")
            pager_layout.addWidget(self.previous_button)
            pager_layout.addWidget(self.page_label, 1)
            pager_layout.addWidget(self.next_button)
            layout.addWidget(pager)

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.save_button = QPushButton("Save setup", actions)
            self.save_button.setObjectName("conquestSaveButton")
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("conquestPrimaryButton")
            self.resign_button = QPushButton("Resign", actions)
            self.resign_button.setObjectName("conquestResignButton")
            self.resign_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.save_button)
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.resign_button)
            layout.addWidget(actions)

            self.previous_button.clicked.connect(
                lambda _checked=False: self._change_page(-1)
            )
            self.next_button.clicked.connect(
                lambda _checked=False: self._change_page(1)
            )
            self.save_button.clicked.connect(
                lambda _checked=False: self._run_command("set_policy", self._draft())
            )
            self.primary_button.clicked.connect(
                lambda _checked=False: self._enter_or_select()
            )
            self.resign_button.clicked.connect(
                lambda _checked=False: self._confirm_resign()
            )
            self.mode.currentIndexChanged.connect(
                lambda _index: self._render_draft()
            )
            self.doctrine.currentIndexChanged.connect(
                lambda _index: self._render_draft()
            )
            self.refresh()

        def _build_overview_page(self) -> None:
            page = QWidget(self.pages)
            grid = QGridLayout(page)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setVerticalSpacing(6)
            grid.addWidget(QLabel("Setup"), 0, 0)
            self.mode = QComboBox(page)
            self.mode.setObjectName("conquestMode")
            self.mode.addItem("Casual · default squad", "casual")
            self.mode.addItem("Advanced · custom squad", "advanced")
            grid.addWidget(self.mode, 0, 1)
            grid.addWidget(QLabel("Doctrine"), 1, 0)
            self.doctrine = QComboBox(page)
            self.doctrine.setObjectName("conquestDoctrine")
            for doctrine_id, label in CONQUEST_DOCTRINES:
                self.doctrine.addItem(label, doctrine_id)
            grid.addWidget(self.doctrine, 1, 1)
            self.opponent = QLabel(page)
            self.opponent.setObjectName("conquestOpponent")
            self.opponent.setWordWrap(True)
            grid.addWidget(self.opponent, 2, 0, 1, 2)
            self.pages.addWidget(page)

        def _build_squad_page(self) -> None:
            page = QWidget(self.pages)
            grid = QGridLayout(page)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(8)
            grid.setVerticalSpacing(3)
            self.squad_spins: dict[str, QSpinBox] = {}
            self.squad_stats: dict[str, QLabel] = {}
            for row, spec in enumerate(
                conquest_view_pure(self._player_data)["squad_rows"]
            ):
                label = QLabel(str(spec["label"]), page)
                spin = QSpinBox(page)
                spin.setObjectName(f"conquestSquad_{spec['id']}")
                spin.setRange(0, 10)
                stat = QLabel(str(spec["stat_text"]), page)
                stat.setStyleSheet("color: palette(mid); font-size: 10px;")
                grid.addWidget(label, row, 0)
                grid.addWidget(spin, row, 1)
                grid.addWidget(stat, row, 2)
                self.squad_spins[str(spec["id"])] = spin
                self.squad_stats[str(spec["id"])] = stat
                spin.valueChanged.connect(lambda _value: self._render_draft())
            self.pages.addWidget(page)

        def _build_commands_page(self) -> None:
            page = QWidget(self.pages)
            grid = QGridLayout(page)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(10)
            grid.setVerticalSpacing(3)
            self.command_checks: dict[str, QCheckBox] = {}
            for index, spec in enumerate(
                conquest_view_pure(self._player_data)["command_rows"]
            ):
                checkbox = QCheckBox(str(spec["label"]), page)
                checkbox.setObjectName(f"conquestCommand_{spec['id']}")
                checkbox.setToolTip(str(spec["tooltip"]))
                grid.addWidget(checkbox, index // 2, index % 2)
                self.command_checks[str(spec["id"])] = checkbox
                checkbox.toggled.connect(lambda _checked: self._render_draft())
            self.pages.addWidget(page)

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def _draft(self) -> dict[str, Any]:
            return {
                "automation_mode": str(self.mode.currentData() or "casual"),
                "doctrine": str(self.doctrine.currentData() or "balanced"),
                "squad": {
                    unit_id: spin.value()
                    for unit_id, spin in self.squad_spins.items()
                },
                "commands": [
                    command_id
                    for command_id, checkbox in self.command_checks.items()
                    if checkbox.isChecked()
                ],
            }

        def _run_command(
            self,
            action_id: str,
            payload: Mapping[str, Any] | None = None,
        ) -> dict[str, Any]:
            result = (
                dict(self._on_command(action_id, payload or {}) or {})
                if self._on_command is not None
                else {"ok": False, "message": "Conquest actions are unavailable."}
            )
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Conquest",
                    str(result.get("message", "Conquest action failed.")),
                )
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _enter_or_select(self) -> None:
            if not conquest_view_pure(self._player_data)["active"]:
                if not self._run_command("enter", self._draft()).get("ok", False):
                    return
            if self._on_select is not None:
                self._on_select(CONQUEST_ACTIVITY_ID)
            self.refresh()

        def _confirm_resign(self) -> None:
            answer = QMessageBox.question(
                self,
                "Resign Conquest?",
                "Resignation ends the match immediately.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("resign")

        def _change_page(self, delta: int) -> None:
            self.pages.setCurrentIndex(
                max(0, min(self.pages.count() - 1, self.pages.currentIndex() + delta))
            )
            self._render_page_controls()

        def _render_page_controls(self) -> None:
            index = self.pages.currentIndex()
            self.page_label.setText(
                ("Overview", "Squad", "Commands")[index] + f" · {index + 1}/3"
            )
            self.previous_button.setEnabled(index > 0)
            self.next_button.setEnabled(index + 1 < self.pages.count())

        def _render_draft(self) -> None:
            if self._syncing:
                return
            self._render_view(conquest_view_pure(self._player_data, self._draft()))

        def _render_view(self, view: Mapping[str, Any]) -> None:
            enabled = self._on_command is not None
            self.rating.setText(
                f"Rating {int(view['rating']):,} · {int(view['commendations'])}/500 comm."
            )
            self.status.setText(str(view["status_text"]))
            self.summary.setText(str(view["summary_text"]))
            warning = " ".join((*view["entry_reasons"], *view["setup_errors"]))
            self.warning.setText(warning)
            self.warning.setVisible(bool(warning))
            self.opponent.setText(f"Opponent: {view['opponent_label']}")
            self.mode.setEnabled(enabled and bool(view["setup_controls_enabled"]))
            self.doctrine.setEnabled(enabled and bool(view["setup_controls_enabled"]))
            for row in view["squad_rows"]:
                spin = self.squad_spins[str(row["id"])]
                spin.setEnabled(enabled and bool(row["enabled"]))
            for row in view["command_rows"]:
                checkbox = self.command_checks[str(row["id"])]
                checkbox.setEnabled(enabled and bool(row["enabled"]))
                checkbox.setToolTip(str(row["tooltip"]))
            self.save_button.setVisible(not bool(view["active"]))
            self.save_button.setEnabled(enabled and bool(view["save_enabled"]))
            self.primary_button.setText(str(view["primary_text"]))
            self.primary_button.setEnabled(enabled and bool(view["primary_enabled"]))
            self.resign_button.setVisible(bool(view["resign_visible"]))
            self.resign_button.setEnabled(enabled and bool(view["resign_enabled"]))
            self._render_page_controls()

        def refresh(self) -> None:
            view = conquest_view_pure(self._player_data)
            self._syncing = True
            self.mode.setCurrentIndex(
                max(0, self.mode.findData(view["conquest_policy"]["automation_mode"]))
            )
            self.doctrine.setCurrentIndex(
                max(0, self.doctrine.findData(view["conquest_policy"]["doctrine"]))
            )
            for row in view["squad_rows"]:
                self.squad_spins[str(row["id"])].setValue(int(row["count"]))
            for row in view["command_rows"]:
                self.command_checks[str(row["id"])].setChecked(bool(row["selected"]))
            self._syncing = False
            self._render_view(view)

else:

    class ConquestPanel:
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

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
