"""Dedicated Goblin Raids activity panel with a Qt-free import fallback.

The panel renders flags. Every enable, visibility and stage decision is owned by
``goblin_raids_view_pure``; nothing here re-derives a threshold or a count.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Mapping
from typing import Any

from ..data.goblin_raids_data import (
    GOBLIN_RAIDS_ACTIVITY_ID,
    GOBLIN_RAIDS_RAID_MODE,
    GOBLIN_RAIDS_VILLAGE_MODE,
)
from ..logic.goblin_raids_logic import goblin_raids_view_pure

try:
    from aqt.qt import (  # type: ignore
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

    class GoblinRaidsPanel(QFrame):
        """Visible announcement clock, raid stage, village duty and rewards."""

        def __init__(
            self,
            player_data: Mapping[str, Any],
            *,
            on_command: Callable[[str, Mapping[str, Any]], Mapping[str, Any]]
            | None = None,
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
            self.setObjectName("goblinRaidsPanel")
            self.setStyleSheet(
                "QFrame#goblinRaidsPanel { border: 1px solid palette(mid);"
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
            icon.setObjectName("goblinRaidsIcon")
            icon.setFixedSize(32, 32)
            icon_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "activityicons",
                "goblin_raids.png",
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
            title = QLabel("Goblin Raids", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status = QLabel(header)
            self.status.setObjectName("goblinRaidsStatusChip")
            self.status.setStyleSheet(
                "color: palette(text); font-size: 11px; font-weight: 700;"
            )
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status)
            layout.addWidget(header)

            self.summary = QLabel(self)
            self.summary.setObjectName("goblinRaidsSummary")
            self.summary.setWordWrap(True)
            self.summary.setStyleSheet("color: palette(text);")
            layout.addWidget(self.summary)

            self.detail = QLabel(self)
            self.detail.setObjectName("goblinRaidsDetail")
            self.detail.setWordWrap(True)
            self.detail.setStyleSheet("color: palette(text); font-size: 11px;")
            layout.addWidget(self.detail)

            self.progress = QProgressBar(self)
            self.progress.setObjectName("goblinRaidsProgress")
            self.progress.setTextVisible(True)
            layout.addWidget(self.progress)

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("goblinRaidsPrimaryButton")
            self.village_button = QPushButton("Goblin Village duty", actions)
            self.village_button.setObjectName("goblinRaidsVillageButton")
            self.intimidate_button = QPushButton("Intimidate Hollowtoof", actions)
            self.intimidate_button.setObjectName("goblinRaidsIntimidateButton")
            self.claim_button = QPushButton("Claim spoils", actions)
            self.claim_button.setObjectName("goblinRaidsClaimButton")
            self.leave_button = QPushButton("Leave", actions)
            self.leave_button.setObjectName("goblinRaidsLeaveButton")
            self.leave_button.setStyleSheet("color: #ef5350;")
            for widget in (
                self.primary_button,
                self.village_button,
                self.intimidate_button,
                self.claim_button,
                self.leave_button,
            ):
                actions_layout.addWidget(widget)
            layout.addWidget(actions)

            self.primary_button.clicked.connect(
                lambda _checked=False: self._join_or_select()
            )
            self.village_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "join", {"mode": GOBLIN_RAIDS_VILLAGE_MODE}
                )
            )
            self.intimidate_button.clicked.connect(
                lambda _checked=False: self._run_command("intimidate")
            )
            self.claim_button.clicked.connect(
                lambda _checked=False: self._run_command("claim_spoils")
            )
            self.leave_button.clicked.connect(
                lambda _checked=False: self._confirm_leave()
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
                    "message": "Goblin Raids actions are unavailable.",
                }
            else:
                result = dict(self._on_command(action_id, payload or {}) or {})
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Goblin Raids",
                    str(result.get("message", "Goblin Raids action failed.")),
                )
                self.refresh()
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _join_or_select(self) -> None:
            view = goblin_raids_view_pure(self._player_data, speed=self._game_speed())
            if not view["active"]:
                mode = (
                    GOBLIN_RAIDS_RAID_MODE
                    if view["raid_announced"]
                    else GOBLIN_RAIDS_VILLAGE_MODE
                )
                if not self._run_command("join", {"mode": mode}).get("ok", False):
                    return
            if self._on_select is not None:
                self._on_select(GOBLIN_RAIDS_ACTIVITY_ID)
            self.refresh()

        def _confirm_leave(self) -> None:
            view = goblin_raids_view_pure(self._player_data, speed=self._game_speed())
            question = "Walk away from the goblins?"
            if view["pending_spoils"]:
                question += " The spoils you have not claimed will be lost."
            answer = QMessageBox.question(
                self,
                "Leave Goblin Raids?",
                question,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("leave")

        def refresh(self) -> None:
            view = goblin_raids_view_pure(self._player_data, speed=self._game_speed())
            enabled = self._on_command is not None

            self.status.setText(
                "RAID UNDER WAY"
                if view["raid_announced"]
                else "IN THE VILLAGE"
                if view["active"]
                else "NO NOTICE YET"
            )
            self.summary.setText(str(view["summary_text"]))

            details = [str(view["stage_label"])]
            if view["raid_announced"]:
                details.append(
                    f"{view['raid_reviews_remaining']} reviews before the "
                    f"raid on {view['raid_site']} is over"
                )
            else:
                details.append(
                    f"Next notice in {view['next_raid_reviews']} reviews"
                )
            if view["raider_set_complete"]:
                details.append("Raider set complete")
            elif view["raider_set_owned"]:
                details.append(
                    "Raider set: " + ", ".join(view["raider_set_owned"])
                )
            if view["cower_shield_held"]:
                details.append(
                    "Goblin cower shield spent"
                    if view["cower_shield_cosmetic"]
                    else (
                        f"Goblin cower shield has "
                        f"{int(view['cower_shield_bonus_remaining'])} bonus "
                        f"experience left"
                    )
                )
            else:
                details.append(
                    f"{view['village_kills_to_boss']} more village goblins "
                    f"summon a boss"
                )
            if view["pending_spoils"]:
                details.append(
                    "Unclaimed: "
                    + ", ".join(
                        f"{count} × {item}"
                        for item, count in sorted(view["pending_spoils"].items())
                    )
                )
            self.detail.setText(" · ".join(details))

            self.progress.setRange(0, int(view["progress_maximum"]))
            self.progress.setValue(
                min(int(view["progress_value"]), int(view["progress_maximum"]))
            )
            self.progress.setFormat(str(view["progress_format"]))

            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(
                enabled
                and (
                    view["active"]
                    or view["can_join_raid"]
                    or view["can_join_village"]
                )
            )
            self.village_button.setVisible(
                not view["active"] and bool(view["raid_announced"])
            )
            self.village_button.setEnabled(
                enabled and bool(view["can_join_village"])
            )
            self.intimidate_button.setVisible(bool(view["intimidate_visible"]))
            self.intimidate_button.setEnabled(
                enabled and bool(view["intimidate_enabled"])
            )
            self.intimidate_button.setToolTip(str(view["intimidate_reason"]))
            self.claim_button.setVisible(bool(view["claim_visible"]))
            self.claim_button.setEnabled(enabled and bool(view["claim_enabled"]))
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_visible"]))

else:

    class GoblinRaidsPanel:
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

        def refresh(self) -> None:
            return None
