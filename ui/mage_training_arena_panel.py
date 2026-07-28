"""Compact Mage Training Arena panel; the pure view owns every UI rule."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..core.constants import UTILITY_ACTIVITY_DATA
from ..data.mage_training_arena_data import (
    MAGE_TRAINING_ARENA_ACTIVITY_ID,
    MAGE_TRAINING_ARENA_APPROACHES,
    MAGE_TRAINING_ARENA_REWARDS,
    MAGE_TRAINING_ARENA_ROOM_POLICIES,
)
from ..logic.mage_training_arena_logic import mage_training_arena_view_pure

try:
    from aqt.qt import (  # type: ignore
        QComboBox,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPixmap,
        QPushButton,
        Qt,
        QVBoxLayout,
        QWidget,
    )

    HAS_QT = True
except Exception:
    HAS_QT = False


if HAS_QT:

    class MageTrainingArenaPanel(QFrame):
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
            self.setObjectName("mageTrainingArenaPanel")
            self.setStyleSheet(
                "QFrame#mageTrainingArenaPanel { border: 1px solid palette(mid); "
                "border-radius: 8px; background: palette(base); }"
            )
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(6)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            icon = QLabel(header)
            icon.setFixedSize(32, 32)
            icon_path = str(
                UTILITY_ACTIVITY_DATA[MAGE_TRAINING_ARENA_ACTIVITY_ID].get(
                    "icon_path",
                    "",
                )
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
            title = QLabel("Mage Training Arena", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status_chip = QLabel(header)
            self.status_chip.setObjectName("mageTrainingArenaStatusChip")
            self.status_chip.setStyleSheet("font-size: 11px; color: palette(text);")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status_chip)
            layout.addWidget(header)

            self.wallets = QLabel(self)
            self.wallets.setObjectName("mageTrainingArenaWallets")
            self.wallets.setWordWrap(True)
            self.wallets.setStyleSheet("color: palette(text); font-size: 11px;")
            layout.addWidget(self.wallets)
            self.status = QLabel(self)
            self.status.setWordWrap(True)
            self.status.setStyleSheet("color: palette(text);")
            layout.addWidget(self.status)

            plan = QWidget(self)
            plan_layout = QGridLayout(plan)
            plan_layout.setContentsMargins(0, 0, 0, 0)
            plan_layout.setHorizontalSpacing(6)
            plan_layout.setVerticalSpacing(4)
            self.goal_combo = QComboBox(plan)
            self.goal_combo.setObjectName("mageTrainingArenaGoalCombo")
            self.goal_combo.setAccessibleName("Mage Training Arena reward goal")
            self.room_combo = QComboBox(plan)
            self.room_combo.setObjectName("mageTrainingArenaRoomCombo")
            self.room_combo.setAccessibleName("Mage Training Arena room policy")
            self.approach_combo = QComboBox(plan)
            self.approach_combo.setObjectName("mageTrainingArenaApproachCombo")
            self.approach_combo.setAccessibleName("Mage Training Arena approach")
            self.save_button = QPushButton("Save plan", plan)
            self.save_button.setObjectName("mageTrainingArenaSaveButton")
            for reward in MAGE_TRAINING_ARENA_REWARDS:
                self.goal_combo.addItem(reward.display_name, reward.id)
            for room_id, label in MAGE_TRAINING_ARENA_ROOM_POLICIES:
                self.room_combo.addItem(label, room_id)
            for approach_id, label in MAGE_TRAINING_ARENA_APPROACHES:
                self.approach_combo.addItem(label, approach_id)
            plan_layout.addWidget(QLabel("Goal", plan), 0, 0)
            plan_layout.addWidget(self.goal_combo, 0, 1)
            plan_layout.addWidget(QLabel("Room", plan), 1, 0)
            plan_layout.addWidget(self.room_combo, 1, 1)
            plan_layout.addWidget(QLabel("Approach", plan), 2, 0)
            plan_layout.addWidget(self.approach_combo, 2, 1)
            plan_layout.addWidget(self.save_button, 3, 1)
            layout.addWidget(plan)

            self.requirements = QLabel(self)
            self.requirements.setWordWrap(True)
            self.requirements.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.requirements)

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("mageTrainingArenaPrimaryButton")
            self.purchase_button = QPushButton("Purchase goal", actions)
            self.purchase_button.setObjectName("mageTrainingArenaPurchaseButton")
            self.leave_button = QPushButton("Leave", actions)
            self.leave_button.setObjectName("mageTrainingArenaLeaveButton")
            self.leave_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.purchase_button)
            actions_layout.addWidget(self.leave_button)
            layout.addWidget(actions)

            self.save_button.clicked.connect(lambda _checked=False: self._save_plan())
            self.primary_button.clicked.connect(lambda _checked=False: self._enter_or_select())
            self.purchase_button.clicked.connect(lambda _checked=False: self._purchase())
            self.leave_button.clicked.connect(lambda _checked=False: self._confirm_leave())
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def _run_command(self, action_id: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
            if self._on_command is None:
                result = {"ok": False, "message": "Mage Training Arena actions are unavailable."}
            else:
                result = dict(self._on_command(action_id, payload or {}) or {})
            if not result.get("ok", False):
                QMessageBox.warning(self, "Mage Training Arena", str(result.get("message", "Action failed.")))
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _save_plan(self) -> None:
            self._run_command(
                "set_policy",
                {
                    "reward_goal": str(self.goal_combo.currentData() or ""),
                    "room_policy": str(self.room_combo.currentData() or ""),
                    "approach": str(self.approach_combo.currentData() or ""),
                },
            )

        def _enter_or_select(self) -> None:
            view = mage_training_arena_view_pure(self._player_data)
            if not view["active"] and not self._run_command("enter").get("ok", False):
                return
            if self._on_select is not None:
                self._on_select(MAGE_TRAINING_ARENA_ACTIVITY_ID)
            self.refresh()

        def _purchase(self) -> None:
            reward_id = str(mage_training_arena_view_pure(self._player_data)["reward_goal"])
            self._run_command("purchase", {"reward_id": reward_id})

        def _confirm_leave(self) -> None:
            answer = QMessageBox.question(
                self,
                "Leave the Mage Training Arena?",
                "Return to the lobby and stop Arena training?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("leave")

        @staticmethod
        def _select(combo: QComboBox, value: str) -> None:
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        def refresh(self) -> None:
            view = mage_training_arena_view_pure(self._player_data)
            enabled = self._on_command is not None
            for combo, value in (
                (self.goal_combo, str(view["reward_goal"])),
                (self.room_combo, str(view["room_policy"])),
                (self.approach_combo, str(view["approach"])),
            ):
                blocked = combo.blockSignals(True)
                self._select(combo, value)
                combo.blockSignals(blocked)
                combo.setEnabled(enabled and bool(view["policy_controls_enabled"]))
            self.save_button.setEnabled(enabled and bool(view["policy_controls_enabled"]))
            self.status_chip.setText("ACTIVE" if view["active"] else "LOBBY")
            self.wallets.setText(str(view["wallet_text"]))
            self.status.setText(str(view["status_text"]))
            reasons = view["review_reasons"] if view["active"] else view["entry_reasons"]
            self.requirements.setText(" · ".join(str(value) for value in reasons))
            self.requirements.setVisible(bool(reasons))
            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(enabled and bool(view["primary_enabled"]))
            self.purchase_button.setEnabled(enabled and bool(view["purchase_enabled"]))
            self.purchase_button.setToolTip(str(view["purchase_reason"]))
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_visible"]))

else:

    class MageTrainingArenaPanel:
        def __init__(self, player_data: Mapping[str, Any], **kwargs: Any) -> None:
            self._player_data = player_data

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
