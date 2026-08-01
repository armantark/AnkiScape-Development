"""Troll Invasion panel; every rule and control flag comes from the pure view."""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from ..data.troll_invasion_data import TROLL_INVASION_ACTIVITY_ID
from ..logic.troll_invasion_logic import troll_invasion_view_pure

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

    class TrollInvasionPanel(QFrame):
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
            self.setObjectName("trollInvasionPanel")
            self.setStyleSheet("QFrame#trollInvasionPanel { border: 1px solid palette(mid); border-radius: 8px; background: palette(base); }")
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(7)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            icon = QLabel(header)
            icon.setObjectName("trollInvasionIcon")
            icon.setFixedSize(32, 32)
            path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "activityicons", "troll_invasion.png")
            if os.path.exists(path):
                icon.setPixmap(QPixmap(path).scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            title = QLabel("Troll Invasion", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status = QLabel(header)
            self.status.setObjectName("trollInvasionStatus")
            self.status.setStyleSheet("color: palette(text); font-size: 11px; font-weight: 700;")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status)
            layout.addWidget(header)

            self.summary = QLabel(self)
            self.summary.setObjectName("trollInvasionSummary")
            self.summary.setWordWrap(True)
            self.summary.setStyleSheet("color: palette(text);")
            layout.addWidget(self.summary)
            self.progress = QProgressBar(self)
            self.progress.setObjectName("trollInvasionProgress")
            layout.addWidget(self.progress)

            policy = QWidget(self)
            policy_layout = QHBoxLayout(policy)
            policy_layout.setContentsMargins(0, 0, 0, 0)
            self.mode_combo = QComboBox(policy)
            self.mode_combo.setObjectName("trollInvasionModeCombo")
            self.difficulty_combo = QComboBox(policy)
            self.difficulty_combo.setObjectName("trollInvasionDifficultyCombo")
            self.save_button = QPushButton("Save plan", policy)
            self.save_button.setObjectName("trollInvasionSaveButton")
            policy_layout.addWidget(self.mode_combo, 1)
            policy_layout.addWidget(self.difficulty_combo, 1)
            policy_layout.addWidget(self.save_button)
            layout.addWidget(policy)

            reward_policy = QWidget(self)
            reward_policy_layout = QHBoxLayout(reward_policy)
            reward_policy_layout.setContentsMargins(0, 0, 0, 0)
            self.reward_combo = QComboBox(reward_policy)
            self.reward_combo.setObjectName("trollInvasionRewardSkillCombo")
            reward_policy_layout.addWidget(self.reward_combo, 1)
            layout.addWidget(reward_policy)

            reward_shop = QWidget(self)
            reward_shop.setObjectName("trollInvasionRewardShop")
            reward_shop_layout = QGridLayout(reward_shop)
            reward_shop_layout.setContentsMargins(0, 0, 0, 0)
            reward_shop_layout.setHorizontalSpacing(6)
            reward_shop_layout.setVerticalSpacing(4)
            self.reward_wallet = QLabel(reward_shop)
            self.reward_wallet.setObjectName("trollInvasionRewardWallet")
            self.shop_reward_combo = QComboBox(reward_shop)
            self.shop_reward_combo.setObjectName("trollInvasionShopRewardSkillCombo")
            self.redeem_button = QPushButton("Read reward book", reward_shop)
            self.redeem_button.setObjectName("trollInvasionRedeemButton")
            reward_shop_layout.addWidget(self.reward_wallet, 0, 0, 1, 2)
            reward_shop_layout.addWidget(self.shop_reward_combo, 1, 0)
            reward_shop_layout.addWidget(self.redeem_button, 1, 1)
            layout.addWidget(reward_shop)
            reward_shop.hide()

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("trollInvasionPrimaryButton")
            self.leave_button = QPushButton("Leave and cash out", actions)
            self.leave_button.setObjectName("trollInvasionLeaveButton")
            self.leave_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.leave_button)
            layout.addWidget(actions)

            self.mode_combo.currentIndexChanged.connect(lambda _index: self.refresh())
            self.save_button.clicked.connect(lambda _checked=False: self._save())
            self.redeem_button.clicked.connect(lambda _checked=False: self._redeem())
            self.primary_button.clicked.connect(lambda _checked=False: self._enter_or_select())
            self.leave_button.clicked.connect(lambda _checked=False: self._confirm_leave())
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def _run(self, action_id: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
            result = dict(self._on_command(action_id, payload or {}) or {}) if self._on_command is not None else {"ok": False, "message": "Troll Invasion actions are unavailable."}
            if not result.get("ok", False):
                QMessageBox.warning(self, "Troll Invasion", str(result.get("message", "Troll Invasion action failed.")))
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _save(self) -> None:
            self._run("set_policy", {"mode": self.mode_combo.currentData(), "difficulty": self.difficulty_combo.currentData(), "reward_skill": self.reward_combo.currentData()})

        def _redeem(self) -> None:
            self._run("redeem_book", {"skill_id": self.shop_reward_combo.currentData()})

        def _enter_or_select(self) -> None:
            if not self._view["active"]:
                result = self._run("enter", {"mode": self.mode_combo.currentData(), "difficulty": self.difficulty_combo.currentData()})
                if not result.get("ok", False):
                    return
            if self._on_select is not None:
                self._on_select(TROLL_INVASION_ACTIVITY_ID)
            self.refresh()

        def _confirm_leave(self) -> None:
            answer = QMessageBox.question(
                self,
                "Leave Troll Invasion?",
                "End the safe run and cash out its current partial completion?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run("leave")

        def refresh(self) -> None:
            view = troll_invasion_view_pure(self._player_data)
            self._view = view
            enabled = self._on_command is not None
            selected_shop_skill = str(
                self.shop_reward_combo.currentData()
                or view["troll_invasion_policy"]["reward_skill"]
            )
            for combo, rows, selected in (
                (self.mode_combo, view["mode_options"], view["selected_mode"]),
                (self.difficulty_combo, view["difficulty_options"], view["selected_difficulty"]),
                (self.reward_combo, view["reward_skill_options"], view["troll_invasion_policy"]["reward_skill"]),
                (self.shop_reward_combo, view["reward_skill_options"], selected_shop_skill),
            ):
                blocked = combo.blockSignals(True)
                combo.clear()
                for row in rows:
                    if row.get("selectable", True):
                        combo.addItem(str(row["display_name"]), row["id"])
                index = combo.findData(selected)
                if index >= 0:
                    combo.setCurrentIndex(index)
                combo.blockSignals(blocked)
            self.status.setText(str(view["status_label"]))
            self.summary.setText(str(view["summary_text"]))
            self.progress.setRange(0, int(view["progress_maximum"]))
            self.progress.setValue(int(view["progress_value"]))
            self.progress.setFormat(str(view["progress_format"]))
            self.mode_combo.setEnabled(enabled and bool(view["policy_controls_enabled"]))
            self.difficulty_combo.setVisible(bool(view["difficulty_visible"]))
            self.difficulty_combo.setEnabled(enabled and bool(view["policy_controls_enabled"]))
            self.save_button.setEnabled(enabled and bool(view["policy_controls_enabled"]))
            self.reward_combo.setVisible(bool(view["reward_visible"]))
            self.reward_combo.setEnabled(enabled and bool(view["reward_enabled"]))
            book_count = int(view["reward_book_count"])
            self.reward_wallet.setText(
                f"{book_count} reward book{'s' if book_count != 1 else ''}"
            )
            self.shop_reward_combo.setEnabled(
                enabled and bool(view["reward_enabled"])
            )
            self.redeem_button.setEnabled(enabled and bool(view["reward_enabled"]))
            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(enabled and bool(view["primary_enabled"]))
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_enabled"]))

else:

    class TrollInvasionPanel:
        def __init__(self, player_data: Mapping[str, Any], *, on_command=None, on_select=None, on_changed=None, parent=None) -> None:
            self._player_data = player_data
            self._on_command = on_command
            self._on_select = on_select
            self._on_changed = on_changed

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
