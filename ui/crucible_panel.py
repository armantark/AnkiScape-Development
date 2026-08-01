"""Dedicated Crucible activity panel with a Qt-free import fallback.

The panel renders flags. Every enable, visibility and warning decision is owned
by ``crucible_view_pure``; nothing here re-derives a gate, a fee or a price.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from ..data.crucible_data import CRUCIBLE_ACTIVITY_ID
from ..logic.crucible_logic import crucible_view_pure

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

    class CruciblePanel(QFrame):
        """Visible arena state, bounty fee, lessons and the Trophy bone shop."""

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
            self.setObjectName("cruciblePanel")
            self.setStyleSheet(
                "QFrame#cruciblePanel { border: 1px solid palette(mid);"
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
            icon.setObjectName("crucibleIcon")
            icon.setFixedSize(32, 32)
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "activityicons",
                "crucible.png",
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
            title = QLabel("The Crucible", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status = QLabel(header)
            self.status.setObjectName("crucibleStatusChip")
            self.status.setStyleSheet(
                "color: palette(mid); font-size: 11px; font-weight: 700;"
            )
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status)
            layout.addWidget(header)

            self.summary = QLabel(self)
            self.summary.setObjectName("crucibleSummary")
            self.summary.setWordWrap(True)
            self.summary.setStyleSheet("color: palette(text);")
            layout.addWidget(self.summary)

            self.fee = QLabel(self)
            self.fee.setObjectName("crucibleFeeLabel")
            self.fee.setWordWrap(True)
            self.fee.setStyleSheet("color: palette(mid); font-size: 11px;")
            layout.addWidget(self.fee)

            self.warning = QLabel(self)
            self.warning.setObjectName("crucibleWarning")
            self.warning.setWordWrap(True)
            self.warning.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.warning)

            self.progress = QProgressBar(self)
            self.progress.setObjectName("crucibleProgress")
            self.progress.setTextVisible(True)
            layout.addWidget(self.progress)

            lessons = QWidget(self)
            lessons_layout = QHBoxLayout(lessons)
            lessons_layout.setContentsMargins(0, 0, 0, 0)
            lessons_layout.setSpacing(6)
            self.lesson_combo = QComboBox(lessons)
            self.lesson_combo.setObjectName("crucibleLessonCombo")
            self.lesson_combo.setAccessibleName("Crucible lesson")
            self.lesson_button = QPushButton("Take lesson", lessons)
            self.lesson_button.setObjectName("crucibleLessonButton")
            lessons_layout.addWidget(self.lesson_combo, 1)
            lessons_layout.addWidget(self.lesson_button)
            layout.addWidget(lessons)

            shop = QWidget(self)
            shop.setObjectName("crucibleRewardShop")
            shop_layout = QHBoxLayout(shop)
            shop_layout.setContentsMargins(0, 0, 0, 0)
            shop_layout.setSpacing(6)
            self.shop_combo = QComboBox(shop)
            self.shop_combo.setObjectName("crucibleShopCombo")
            self.shop_combo.setAccessibleName("Crucible reward")
            self.buy_button = QPushButton("Buy", shop)
            self.buy_button.setObjectName("crucibleBuyButton")
            self.helm_button = QPushButton("Buy helm", shop)
            self.helm_button.setObjectName("crucibleHelmButton")
            shop_layout.addWidget(self.shop_combo, 1)
            shop_layout.addWidget(self.buy_button)
            shop_layout.addWidget(self.helm_button)
            layout.addWidget(shop)

            cosmetics = QWidget(self)
            cosmetics_layout = QHBoxLayout(cosmetics)
            cosmetics_layout.setContentsMargins(0, 0, 0, 0)
            cosmetics_layout.setSpacing(6)
            self.taunt_combo = QComboBox(cosmetics)
            self.taunt_combo.setObjectName("crucibleTauntCombo")
            self.taunt_combo.setAccessibleName("Crucible death taunt")
            self.title_combo = QComboBox(cosmetics)
            self.title_combo.setObjectName("crucibleTitleCombo")
            self.title_combo.setAccessibleName("Crucible death title")
            cosmetics_layout.addWidget(self.taunt_combo, 1)
            cosmetics_layout.addWidget(self.title_combo, 1)
            layout.addWidget(cosmetics)

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("cruciblePrimaryButton")
            self.leave_button = QPushButton("Leave arena", actions)
            self.leave_button.setObjectName("crucibleLeaveButton")
            self.leave_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.leave_button)
            layout.addWidget(actions)

            self.lesson_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "take_lesson", {"lesson": self.selected_lesson()}
                )
            )
            self.buy_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "buy_unlock", {"unlock_id": self.selected_unlock()}
                )
            )
            self.helm_button.clicked.connect(
                lambda _checked=False: self._run_command("buy_supreme_helm")
            )
            self.taunt_combo.activated.connect(
                lambda _index: self._run_command(
                    "set_taunt",
                    {"unlock_id": str(self.taunt_combo.currentData() or "")},
                )
            )
            self.title_combo.activated.connect(
                lambda _index: self._run_command(
                    "set_title",
                    {"unlock_id": str(self.title_combo.currentData() or "")},
                )
            )
            self.primary_button.clicked.connect(
                lambda _checked=False: self._enter_or_select()
            )
            self.leave_button.clicked.connect(
                lambda _checked=False: self._confirm_leave()
            )
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def selected_lesson(self) -> str:
            return str(self.lesson_combo.currentData() or "")

        def selected_unlock(self) -> str:
            return str(self.shop_combo.currentData() or "")

        def _run_command(
            self,
            action_id: str,
            payload: Mapping[str, Any] | None = None,
        ) -> dict[str, Any]:
            if self._on_command is None:
                result = {
                    "ok": False,
                    "message": "Crucible actions are unavailable.",
                }
            else:
                result = dict(self._on_command(action_id, payload or {}) or {})
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "The Crucible",
                    str(result.get("message", "Crucible action failed.")),
                )
                self.refresh()
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _enter_or_select(self) -> None:
            view = crucible_view_pure(self._player_data)
            if not view["active"]:
                warning = str(view["entry_warning"])
                if warning:
                    answer = QMessageBox.question(
                        self,
                        f"Pay {view['fee']['total']} coins and enter the arena?",
                        warning,
                        QMessageBox.StandardButton.Yes
                        | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if answer != QMessageBox.StandardButton.Yes:
                        return
                if not self._run_command("enter").get("ok", False):
                    return
            if self._on_select is not None:
                self._on_select(CRUCIBLE_ACTIVITY_ID)
            self.refresh()

        def _confirm_leave(self) -> None:
            view = crucible_view_pure(self._player_data)
            answer = QMessageBox.question(
                self,
                "Leave the arena?",
                (
                    "Leaving abandons your bounty target, so the "
                    f"{view['fee']['abandon_component']} coin abandonment part "
                    "of your fee goes to the opponent."
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("leave")

        def _fill(self, combo, rows, current: str) -> None:
            blocked = combo.blockSignals(True)
            combo.clear()
            for label, value in rows:
                combo.addItem(label, value)
            index = combo.findData(current)
            combo.setCurrentIndex(index if index >= 0 else 0)
            combo.blockSignals(blocked)

        def refresh(self) -> None:
            view = crucible_view_pure(self._player_data)
            enabled = self._on_command is not None

            self.status.setText(str(view["status_label"]))
            self.summary.setText(str(view["summary_text"]))
            fee = view["fee"]
            self.fee.setText(
                f"Bounty fee {fee['total']} coins = risk {fee['risk_component']} "
                f"+ abandonment {fee['abandon_component']} · "
                f"{view['bones']} Trophy bones held"
            )
            self.warning.setText(str(view["entry_warning"]))
            self.warning.setVisible(bool(view["entry_warning"]))
            if view["entry_reasons"]:
                self.warning.setText("\n".join(view["entry_reasons"]))
                self.warning.setVisible(True)
            self.progress.setRange(0, int(view["progress_maximum"]))
            self.progress.setValue(
                min(int(view["progress_value"]), int(view["progress_maximum"]))
            )
            self.progress.setFormat(str(view["progress_format"]))

            lessons = [
                row for row in view["lesson_options"] if row["enabled"]
            ]
            self._fill(
                self.lesson_combo,
                [
                    (f"{row['lesson']} · +{row['award']} bones", row["lesson"])
                    for row in lessons
                ],
                self.selected_lesson(),
            )
            self.lesson_combo.setEnabled(enabled and bool(lessons))
            self.lesson_button.setEnabled(enabled and bool(lessons))

            purchasable = [
                row for row in view["shop_options"] if not row["owned"]
            ]
            self._fill(
                self.shop_combo,
                [
                    (
                        f"{row['display_name']} · {row['cost']} bones"
                        + ("" if row["affordable"] else " (short)"),
                        row["id"],
                    )
                    for row in purchasable
                ],
                self.selected_unlock(),
            )
            self.shop_combo.setEnabled(
                enabled and bool(purchasable) and bool(view["shop_controls_enabled"])
            )
            selected = next(
                (
                    row
                    for row in purchasable
                    if row["id"] == self.selected_unlock()
                ),
                purchasable[0] if purchasable else None,
            )
            self.buy_button.setEnabled(
                enabled
                and bool(view["shop_controls_enabled"])
                and bool(selected and selected["enabled"])
            )
            helm = view["supreme_helm"]
            self.helm_button.setText(f"{helm['item_name']} · {helm['cost']}")
            self.helm_button.setVisible(not helm["owned"])
            self.helm_button.setEnabled(
                enabled
                and bool(view["shop_controls_enabled"])
                and bool(helm["enabled"])
            )
            self.helm_button.setToolTip(str(helm["reason"]))

            owned_taunts = [
                row
                for row in view["shop_options"]
                if row["owned"] and row["kind"] == "taunt"
            ]
            owned_titles = [
                row
                for row in view["shop_options"]
                if row["owned"] and row["kind"] == "title"
            ]
            self._fill(
                self.taunt_combo,
                [("No death taunt", "")]
                + [(row["display_name"], row["id"]) for row in owned_taunts],
                str(view["crucible_taunt"]),
            )
            self._fill(
                self.title_combo,
                [("No death title", "")]
                + [(row["display_name"], row["id"]) for row in owned_titles],
                str(view["crucible_title"]),
            )
            self.taunt_combo.setEnabled(enabled and bool(owned_taunts))
            self.title_combo.setEnabled(enabled and bool(owned_titles))

            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(
                enabled and bool(view["primary_enabled"])
            )
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_visible"]))

else:

    class CruciblePanel:
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

        def selected_lesson(self) -> str:
            options = crucible_view_pure(self._player_data)["lesson_options"]
            return next(
                (str(row["lesson"]) for row in options if row["enabled"]), ""
            )

        def selected_unlock(self) -> str:
            options = crucible_view_pure(self._player_data)["shop_options"]
            return next((str(row["id"]) for row in options if row["enabled"]), "")

        def refresh(self) -> None:
            return None
