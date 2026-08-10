"""Compact Ranging Guild competition and ticket-exchange panel."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..core.constants import EXTRA_ITEM_IMAGES, UTILITY_ACTIVITY_DATA
from ..data.ranging_guild_data import (
    RANGING_GUILD_ACTIVITY_ID,
    RANGING_GUILD_BANDS,
    RANGING_GUILD_REWARDS,
)
from ..logic.ranging_guild_logic import ranging_guild_view_pure

try:
    from aqt.qt import (  # type: ignore
        QComboBox,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QIcon,
        QLabel,
        QMessageBox,
        QPixmap,
        QPushButton,
        QSize,
        Qt,
        QVBoxLayout,
        QWidget,
    )

    HAS_QT = True
except Exception:
    HAS_QT = False


if HAS_QT:

    class RangingGuildPanel(QFrame):
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
            self.setObjectName("rangingGuildPanel")
            self.setStyleSheet(
                "QFrame#rangingGuildPanel { border: 1px solid palette(mid); "
                "border-radius: 8px; background: palette(base); }"
            )
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 8, 10, 8)
            layout.setSpacing(6)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            icon = QLabel(header)
            icon.setObjectName("rangingGuildIcon")
            icon.setFixedSize(32, 32)
            icon_path = str(
                UTILITY_ACTIVITY_DATA[RANGING_GUILD_ACTIVITY_ID].get("icon_path", "")
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
            title = QLabel("Ranging Guild", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status_chip = QLabel(header)
            self.status_chip.setObjectName("rangingGuildStatusChip")
            self.status_chip.setStyleSheet("font-size: 11px; color: palette(text);")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status_chip)
            layout.addWidget(header)

            self.progress = QLabel(self)
            self.progress.setObjectName("rangingGuildProgress")
            self.progress.setStyleSheet("font-weight: 600; color: palette(text);")
            layout.addWidget(self.progress)

            bands = " · ".join(
                f"{row.display_name} {row.score}/{row.ranged_xp:g} XP"
                for row in RANGING_GUILD_BANDS
            )
            self.band_legend = QLabel(
                f"Score/XP per hit: {bands} · Score ÷ 10 = tickets",
                self,
            )
            self.band_legend.setObjectName("rangingGuildBandLegend")
            self.band_legend.setWordWrap(True)
            self.band_legend.setStyleSheet("font-size: 11px; color: palette(text);")
            layout.addWidget(self.band_legend)

            self.last_result = QLabel(self)
            self.last_result.setObjectName("rangingGuildLastResult")
            self.last_result.setWordWrap(True)
            self.last_result.setStyleSheet("color: palette(text);")
            layout.addWidget(self.last_result)

            shop = QWidget(self)
            shop_layout = QGridLayout(shop)
            shop_layout.setContentsMargins(0, 0, 0, 0)
            shop_layout.setHorizontalSpacing(6)
            shop_layout.setVerticalSpacing(4)
            shop_layout.setColumnStretch(0, 1)
            self.ticket_wallet = QLabel(shop)
            self.ticket_wallet.setObjectName("rangingGuildTicketWallet")
            self.ticket_wallet.setStyleSheet("font-size: 11px; color: palette(text);")
            self.reward_combo = QComboBox(shop)
            self.reward_combo.setObjectName("rangingGuildRewardCombo")
            self.reward_combo.setAccessibleName("Ranging Guild reward to purchase")
            self.reward_combo.setIconSize(QSize(24, 24))
            for reward in RANGING_GUILD_REWARDS:
                icon_path = EXTRA_ITEM_IMAGES.get(reward.item_name, "")
                self.reward_combo.addItem(
                    QIcon(icon_path) if icon_path else QIcon(),
                    f"{reward.display_name} — {reward.ticket_cost:,} tickets",
                    reward.id,
                )
            self.purchase_button = QPushButton("Purchase", shop)
            self.purchase_button.setObjectName("rangingGuildPurchaseButton")
            shop_layout.addWidget(self.ticket_wallet, 0, 0, 1, 2)
            shop_layout.addWidget(self.reward_combo, 1, 0)
            shop_layout.addWidget(self.purchase_button, 1, 1)
            layout.addWidget(shop)

            self.requirements = QLabel(self)
            self.requirements.setObjectName("rangingGuildRequirements")
            self.requirements.setWordWrap(True)
            self.requirements.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.requirements)

            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(6)
            self.primary_button = QPushButton(actions)
            self.primary_button.setObjectName("rangingGuildPrimaryButton")
            self.leave_button = QPushButton("Leave", actions)
            self.leave_button.setObjectName("rangingGuildLeaveButton")
            self.leave_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.leave_button)
            layout.addWidget(actions)

            self.primary_button.clicked.connect(lambda _checked=False: self._primary())
            self.purchase_button.clicked.connect(lambda _checked=False: self._purchase())
            self.reward_combo.currentIndexChanged.connect(lambda _index: self.refresh())
            self.leave_button.clicked.connect(lambda _checked=False: self._confirm_leave())
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        def _run_command(
            self,
            action_id: str,
            payload: Mapping[str, Any] | None = None,
        ) -> dict[str, Any]:
            result = (
                dict(self._on_command(action_id, payload or {}) or {})
                if self._on_command is not None
                else {"ok": False, "message": "Ranging Guild actions are unavailable."}
            )
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Ranging Guild",
                    str(result.get("message", "Action failed.")),
                )
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _primary(self) -> None:
            view = ranging_guild_view_pure(self._player_data)
            if view["pending_claim"]:
                self._run_command("claim")
                return
            if not view["active"] and not self._run_command("enter").get("ok", False):
                return
            if self._on_select is not None:
                self._on_select(RANGING_GUILD_ACTIVITY_ID)
            self.refresh()

        def _purchase(self) -> None:
            self._run_command(
                "purchase",
                {"reward_id": str(self.reward_combo.currentData() or "")},
            )

        def _confirm_leave(self) -> None:
            answer = QMessageBox.question(
                self,
                "Leave the Ranging Guild competition?",
                "Your unfinished score will be forfeited, and arrows already "
                "fired are not refunded.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("leave")

        def refresh(self) -> None:
            view = ranging_guild_view_pure(self._player_data)
            enabled = self._on_command is not None
            if view["pending_claim"]:
                state_label = "CLAIM READY"
            elif view["active"]:
                state_label = "ACTIVE"
            else:
                state_label = "LOBBY"
            self.status_chip.setText(state_label)
            self.status_chip.setStyleSheet(
                "background: #ffb300; color: #000; border-radius: 4px; "
                "padding: 1px 6px; font-size: 11px; font-weight: 700;"
                if view["pending_claim"]
                else "font-size: 11px; color: palette(text);"
            )
            self.progress.setText(
                f"Shots {view['shots_fired']}/10 · Score {view['score']}"
            )
            self.progress.setVisible(bool(view["active"] or view["pending_claim"]))
            self.last_result.setText(
                str(
                    view["last_result"]
                    or "Pay 200 coins for 10 scored shots. One review fires one arrow."
                )
            )
            self.ticket_wallet.setText(f"Archery tickets: {view['tickets']}")
            selected_id = str(self.reward_combo.currentData() or "")
            reward = next(
                (row for row in view["reward_options"] if row["id"] == selected_id),
                None,
            )
            self.reward_combo.setEnabled(enabled)
            self.purchase_button.setEnabled(
                enabled and bool(reward and reward["purchase_enabled"])
            )
            self.purchase_button.setToolTip(
                str(reward["purchase_reason"] if reward else "Choose a reward.")
            )
            reasons = (
                view["shot_reasons"]
                if view["active"]
                else ()
                if view["pending_claim"]
                else view["entry_reasons"]
            )
            self.requirements.setText(" · ".join(map(str, reasons)))
            self.requirements.setVisible(bool(reasons))
            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(enabled and bool(view["primary_enabled"]))
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_visible"]))

else:

    class RangingGuildPanel:
        def __init__(self, player_data: Mapping[str, Any], **kwargs: Any) -> None:
            self._player_data = player_data

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
