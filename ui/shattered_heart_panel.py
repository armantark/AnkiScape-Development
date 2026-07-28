"""Dedicated Shattered Heart activity panel with a Qt-free import fallback.

The panel renders flags. Every enable, visibility and gating decision is
owned by ``shattered_heart_view_pure``; nothing here re-derives a weekly
gate, a bag rule, or a plinth requirement.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from ..logic.shattered_heart_logic import shattered_heart_view_pure

try:
    from aqt.qt import (  # type: ignore
        QCheckBox,
        QFrame,
        QHBoxLayout,
        QLabel,
        QMessageBox,
        QPalette,
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

    class ShatteredHeartPanel(QFrame):
        """Statue bag state, weekly gate, and replica plinth controls."""

        def __init__(
            self,
            player_data: Mapping[str, Any],
            *,
            on_command: Callable[[str, Mapping[str, Any]], Mapping[str, Any]]
            | None = None,
            on_changed: Callable[[], None] | None = None,
            parent: QWidget | None = None,
        ) -> None:
            super().__init__(parent)
            self._player_data = player_data
            self._on_command = on_command
            self._on_changed = on_changed
            self.setObjectName("shatteredHeartPanel")
            self.setStyleSheet(
                "QFrame#shatteredHeartPanel { border: 1px solid palette(mid);"
                " border-radius: 8px; background: palette(base); }"
            )

            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(7)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            header_layout.setSpacing(8)
            icon = QLabel(header)
            icon.setObjectName("shatteredHeartIcon")
            icon.setFixedSize(32, 32)
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "activityicons",
                "shattered_heart.png",
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
            title = QLabel("Shattered Heart", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status = QLabel(header)
            self.status.setObjectName("shatteredHeartStatus")
            self.status.setStyleSheet(
                "color: palette(text); font-size: 11px; font-weight: 700;"
            )
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status)
            layout.addWidget(header)

            self.summary = QLabel(self)
            self.summary.setObjectName("shatteredHeartSummary")
            self.summary.setWordWrap(True)
            self.summary.setStyleSheet("color: palette(text);")
            layout.addWidget(self.summary)

            self.progress = QProgressBar(self)
            self.progress.setObjectName("shatteredHeartProgress")
            self.progress.setTextVisible(True)
            layout.addWidget(self.progress)

            self.weekly_gate = QLabel(self)
            self.weekly_gate.setObjectName("shatteredHeartWeeklyGate")
            self.weekly_gate.setWordWrap(True)
            self.weekly_gate.setStyleSheet(
                "color: palette(text); font-size: 11px;"
            )
            layout.addWidget(self.weekly_gate)

            bag = QWidget(self)
            bag_layout = QHBoxLayout(bag)
            bag_layout.setContentsMargins(0, 0, 0, 0)
            bag_layout.setSpacing(6)
            self.claim_bag_button = QPushButton("Claim statue bag", bag)
            self.claim_bag_button.setObjectName("shatteredHeartClaimBagButton")
            self.destroy_bag_button = QPushButton("Destroy bag", bag)
            self.destroy_bag_button.setObjectName(
                "shatteredHeartDestroyBagButton"
            )
            self.destroy_bag_button.setStyleSheet("color: #ef5350;")
            bag_layout.addWidget(self.claim_bag_button, 1)
            bag_layout.addWidget(self.destroy_bag_button)
            layout.addWidget(bag)

            self.add_pairs_button = QPushButton(self)
            self.add_pairs_button.setObjectName("shatteredHeartAddPairsButton")
            layout.addWidget(self.add_pairs_button)

            self.auto_discard_check = QCheckBox(
                "Auto-discard strange rocks", self
            )
            self.auto_discard_check.setObjectName(
                "shatteredHeartAutoDiscardCheck"
            )
            self.auto_discard_check.setStyleSheet("color: palette(text);")
            layout.addWidget(self.auto_discard_check)

            self.replica_progress = QProgressBar(self)
            self.replica_progress.setObjectName("shatteredHeartReplicaProgress")
            self.replica_progress.setTextVisible(True)
            layout.addWidget(self.replica_progress)

            replica = QWidget(self)
            replica_layout = QHBoxLayout(replica)
            replica_layout.setContentsMargins(0, 0, 0, 0)
            replica_layout.setSpacing(6)
            self.build_plinth_button = QPushButton("Build replica plinth", replica)
            self.build_plinth_button.setObjectName(
                "shatteredHeartBuildPlinthButton"
            )
            self.add_replica_button = QPushButton("Add replica pairs", replica)
            self.add_replica_button.setObjectName(
                "shatteredHeartAddReplicaButton"
            )
            replica_layout.addWidget(self.build_plinth_button, 1)
            replica_layout.addWidget(self.add_replica_button, 1)
            layout.addWidget(replica)

            self.claim_bag_button.clicked.connect(
                lambda _checked=False: self._run_command("claim_bag")
            )
            self.destroy_bag_button.clicked.connect(
                lambda _checked=False: self._confirm_destroy_bag()
            )
            self.auto_discard_check.toggled.connect(self._toggle_auto_discard)
            self.add_pairs_button.clicked.connect(
                lambda _checked=False: self._run_command("add_completed_pairs")
            )
            self.build_plinth_button.clicked.connect(
                lambda _checked=False: self._run_command("build_replica_plinth")
            )
            self.add_replica_button.clicked.connect(
                lambda _checked=False: self._run_command("add_replica_pairs")
            )
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def _run_command(
            self,
            action_id: str,
            payload: Mapping[str, Any] | None = None,
        ) -> dict[str, Any]:
            if self._on_command is None:
                result = {
                    "ok": False,
                    "message": "Shattered Heart actions are unavailable.",
                }
            else:
                result = dict(self._on_command(action_id, payload or {}) or {})
            if not result.get("ok", False):
                self.refresh()
                QMessageBox.warning(
                    self,
                    "Shattered Heart",
                    str(
                        result.get("message", "Shattered Heart action failed.")
                    ),
                )
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _confirm_destroy_bag(self) -> None:
            answer = QMessageBox.question(
                self,
                "Destroy statue bag?",
                "Destroy the statue bag and every strange rock inside it?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("destroy_bag")

        def _toggle_auto_discard(self, checked: bool) -> None:
            view = shattered_heart_view_pure(self._player_data)
            if bool(checked) == bool(view["auto_discard"]):
                return
            self._run_command("set_auto_discard", {"enabled": bool(checked)})

        def refresh(self) -> None:
            view = shattered_heart_view_pure(self._player_data)
            enabled = self._on_command is not None
            for button in (
                self.claim_bag_button,
                self.destroy_bag_button,
                self.add_pairs_button,
                self.build_plinth_button,
                self.add_replica_button,
            ):
                palette = button.palette()
                dimmed = palette.color(QPalette.ColorRole.Text)
                dimmed.setAlpha(115)
                palette.setColor(
                    QPalette.ColorGroup.Disabled,
                    QPalette.ColorRole.ButtonText,
                    dimmed,
                )
                button.setPalette(palette)

            self.status.setText(str(view["status_label"]))
            self.summary.setText(str(view["summary_text"]))
            self.progress.setRange(0, int(view["progress_max"]))
            self.progress.setValue(int(view["progress_value"]))
            self.progress.setFormat(str(view["progress_format"]))

            self.weekly_gate.setText(str(view["weekly_gate_text"]))
            self.weekly_gate.setVisible(bool(view["weekly_gate_visible"]))

            self.claim_bag_button.setVisible(bool(view["claim_bag_visible"]))
            self.claim_bag_button.setEnabled(
                enabled and bool(view["claim_bag_enabled"])
            )
            self.destroy_bag_button.setVisible(
                bool(view["destroy_bag_visible"])
            )
            self.destroy_bag_button.setEnabled(
                enabled and bool(view["destroy_bag_enabled"])
            )

            self.add_pairs_button.setText(str(view["add_pairs_label"]))
            self.add_pairs_button.setEnabled(
                enabled and bool(view["add_pairs_enabled"])
            )

            blocked = self.auto_discard_check.blockSignals(True)
            self.auto_discard_check.setChecked(bool(view["auto_discard"]))
            self.auto_discard_check.blockSignals(blocked)
            self.auto_discard_check.setEnabled(
                enabled and bool(view["auto_discard_enabled"])
            )

            self.replica_progress.setRange(0, int(view["replica_progress_max"]))
            self.replica_progress.setValue(
                int(view["replica_progress_value"])
            )
            self.replica_progress.setFormat(
                str(view["replica_progress_format"])
            )

            self.build_plinth_button.setVisible(
                bool(view["build_plinth_visible"])
            )
            self.build_plinth_button.setEnabled(
                enabled and bool(view["build_plinth_enabled"])
            )
            self.add_replica_button.setVisible(
                bool(view["add_replica_visible"])
            )
            self.add_replica_button.setEnabled(
                enabled and bool(view["add_replica_enabled"])
            )

else:

    class ShatteredHeartPanel:
        """Non-Qt placeholder with the same public control surface."""

        def __init__(
            self,
            player_data: Mapping[str, Any],
            *,
            on_command: Callable[[str, Mapping[str, Any]], Mapping[str, Any]]
            | None = None,
            on_changed: Callable[[], None] | None = None,
            parent: Any = None,
        ) -> None:
            self._player_data = player_data
            self._on_command = on_command
            self._on_changed = on_changed

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
