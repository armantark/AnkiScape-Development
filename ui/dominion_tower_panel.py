"""Compact Dominion Tower panel; the pure view owns every UI rule."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..core.constants import UTILITY_ACTIVITY_DATA
from ..data.dominion_tower_data import DOMINION_TOWER_ACTIVITY_ID
from ..logic.dominion_tower_logic import dominion_tower_view_pure

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

    class DominionTowerPanel(QFrame):
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
            self.setObjectName("dominionTowerPanel")
            self.setStyleSheet(
                "QFrame#dominionTowerPanel { border: 1px solid palette(mid); "
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
                UTILITY_ACTIVITY_DATA[DOMINION_TOWER_ACTIVITY_ID].get("icon_path", "")
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
            title = QLabel("Dominion Tower", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status_chip = QLabel(header)
            self.status_chip.setStyleSheet("font-size: 11px; color: palette(text);")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status_chip)
            layout.addWidget(header)

            self.arena_status = QLabel(self)
            self.arena_status.setWordWrap(True)
            self.arena_status.setStyleSheet("color: palette(text);")
            layout.addWidget(self.arena_status)
            self.enemy_health = QProgressBar(self)
            self.enemy_health.setObjectName("dominionTowerEnemyHealth")
            self.enemy_health.setTextVisible(True)
            layout.addWidget(self.enemy_health)

            plan = QWidget(self)
            grid = QGridLayout(plan)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(6)
            grid.setVerticalSpacing(3)
            self.mode_combo = QComboBox(plan)
            self.target_combo = QComboBox(plan)
            self.mode_combo.setAccessibleName("Dominion Tower mode")
            self.target_combo.setAccessibleName("Dominion Tower match")
            grid.addWidget(QLabel("Mode", plan), 0, 0)
            grid.addWidget(self.mode_combo, 0, 1)
            grid.addWidget(QLabel("Match", plan), 1, 0)
            grid.addWidget(self.target_combo, 1, 1)
            layout.addWidget(plan)

            self.handicap_status = QLabel(self)
            self.handicap_status.setWordWrap(True)
            self.handicap_status.setStyleSheet("font-size: 11px; color: palette(text);")
            layout.addWidget(self.handicap_status)
            spinner = QWidget(self)
            spinner_layout = QHBoxLayout(spinner)
            spinner_layout.setContentsMargins(0, 0, 0, 0)
            self.accept_button = QPushButton("Take handicap", spinner)
            self.respin_button = QPushButton("Respin", spinner)
            self.nudge_button = QPushButton("Nudge", spinner)
            for button in (self.accept_button, self.respin_button, self.nudge_button):
                spinner_layout.addWidget(button)
            layout.addWidget(spinner)

            supplies = QWidget(self)
            supplies_layout = QHBoxLayout(supplies)
            supplies_layout.setContentsMargins(0, 0, 0, 0)
            self.powerup_combo = QComboBox(supplies)
            self.powerup_combo.setAccessibleName("Dominion Tower power-up")
            self.use_button = QPushButton("Use", supplies)
            self.eat_button = QPushButton("Eat meat", supplies)
            supplies_layout.addWidget(self.powerup_combo, 1)
            supplies_layout.addWidget(self.use_button)
            supplies_layout.addWidget(self.eat_button)
            layout.addWidget(supplies)

            rewards = QWidget(self)
            rewards_layout = QHBoxLayout(rewards)
            rewards_layout.setContentsMargins(0, 0, 0, 0)
            self.claim_box_button = QPushButton("Claim reward box", rewards)
            self.exchange_button = QPushButton("Exchange", rewards)
            self.skill_combo = QComboBox(rewards)
            self.skill_combo.setAccessibleName("Xp book skill")
            self.read_button = QPushButton("Read book", rewards)
            for widget in (
                self.claim_box_button,
                self.exchange_button,
                self.skill_combo,
                self.read_button,
            ):
                rewards_layout.addWidget(widget)
            layout.addWidget(rewards)

            unlocks = QWidget(self)
            unlocks_layout = QHBoxLayout(unlocks)
            unlocks_layout.setContentsMargins(0, 0, 0, 0)
            self.reward_combo = QComboBox(unlocks)
            self.reward_combo.setAccessibleName("Dominion Tower reward")
            self.claim_reward_button = QPushButton("Claim", unlocks)
            self.mines_button = QPushButton("Buy 10 mines", unlocks)
            self.spectate_button = QPushButton("Spectate", unlocks)
            for widget in (
                self.reward_combo,
                self.claim_reward_button,
                self.mines_button,
                self.spectate_button,
            ):
                unlocks_layout.addWidget(widget)
            layout.addWidget(unlocks)

            self.requirements = QLabel(self)
            self.requirements.setWordWrap(True)
            self.requirements.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.requirements)
            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.primary_button = QPushButton(actions)
            self.leave_button = QPushButton("Leave", actions)
            self.leave_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.leave_button)
            layout.addWidget(actions)

            self.mode_combo.currentIndexChanged.connect(
                lambda _index=0: self._populate_targets(
                    dominion_tower_view_pure(self._player_data)
                )
            )
            self.accept_button.clicked.connect(
                lambda _checked=False: self._run_command("accept_handicap")
            )
            self.respin_button.clicked.connect(
                lambda _checked=False: self._run_command("respin_handicap")
            )
            self.nudge_button.clicked.connect(
                lambda _checked=False: self._run_command("nudge_handicap")
            )
            self.use_button.clicked.connect(lambda _checked=False: self._use_selected())
            self.eat_button.clicked.connect(
                lambda _checked=False: self._run_command("eat_scorpion_meat")
            )
            self.claim_box_button.clicked.connect(
                lambda _checked=False: self._run_command("claim_rewards")
            )
            self.exchange_button.clicked.connect(
                lambda _checked=False: self._run_command("exchange_rewards")
            )
            self.read_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "read_xp_book", {"skill": str(self.skill_combo.currentData() or "")}
                )
            )
            self.claim_reward_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "claim_reward",
                    {"reward_id": str(self.reward_combo.currentData() or "")},
                )
            )
            self.mines_button.clicked.connect(
                lambda _checked=False: self._run_command("buy_mines", {"quantity": 10})
            )
            self.spectate_button.clicked.connect(
                lambda _checked=False: self._run_command("spectate")
            )
            self.primary_button.clicked.connect(
                lambda _checked=False: self._primary_clicked()
            )
            self.leave_button.clicked.connect(lambda _checked=False: self._confirm_leave())
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
                else {"ok": False, "message": "Dominion Tower actions are unavailable."}
            )
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Dominion Tower",
                    str(result.get("message", "Action failed.")),
                )
                return result
            self.refresh()
            if self._on_changed is not None:
                self._on_changed()
            return result

        def _populate_targets(self, view: Mapping[str, Any]) -> None:
            mode = str(self.mode_combo.currentData() or "")
            selected = str(self.target_combo.currentData() or "")
            blocked = self.target_combo.blockSignals(True)
            self.target_combo.clear()
            if mode == "special":
                for row in view["special_rows"]:
                    label = row["display_name"] + ("" if row["unlocked"] else " (locked)")
                    self.target_combo.addItem(label, row["id"])
                    if not row["unlocked"]:
                        item = self.target_combo.model().item(self.target_combo.count() - 1)
                        if item is not None:
                            item.setEnabled(False)
            elif mode == "freestyle":
                for row in view["available_encounter_rows"]:
                    if row["defeated"] > 0:
                        self.target_combo.addItem(row["display_name"], row["id"])
            else:
                self.target_combo.addItem("Randomly chosen by the tower", "")
            self._select(self.target_combo, selected)
            self.target_combo.blockSignals(blocked)
            self.target_combo.setEnabled(
                self._on_command is not None and mode in ("special", "freestyle")
            )

        def _use_selected(self) -> None:
            item_name = str(self.powerup_combo.currentData() or "")
            action = "drink_potion" if item_name.startswith("Dom ") else "use_powerup"
            self._run_command(action, {"item": item_name})

        def _primary_clicked(self) -> None:
            """One button, two jobs: meet the face, then enter the tower."""
            if not dominion_tower_view_pure(self._player_data)["talked_with_face"]:
                self._run_command("talk_to_face")
                return
            self._enter_or_select()

        def _enter_or_select(self) -> None:
            view = dominion_tower_view_pure(self._player_data)
            if not view["active"]:
                mode = str(self.mode_combo.currentData() or "")
                payload: dict[str, Any] = {"mode": mode}
                if mode == "special":
                    payload["special_id"] = str(self.target_combo.currentData() or "")
                elif mode == "freestyle":
                    payload["encounter_id"] = str(self.target_combo.currentData() or "")
                if not self._run_command("start_mode", payload).get("ok", False):
                    return
            if self._on_select is not None:
                self._on_select(DOMINION_TOWER_ACTIVITY_ID)

        def _confirm_leave(self) -> None:
            answer = QMessageBox.question(
                self,
                "Leave the Dominion Tower?",
                "End this run and return to the lobby with the factor you hold?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("leave")

        def refresh(self) -> None:
            view = dominion_tower_view_pure(self._player_data)
            enabled = self._on_command is not None
            blocked = self.mode_combo.blockSignals(True)
            selected_mode = str(self.mode_combo.currentData() or "")
            self.mode_combo.clear()
            for row in view["mode_rows"]:
                self.mode_combo.addItem(row["display_name"], row["id"])
            self._select(self.mode_combo, selected_mode or view["mode"])
            self.mode_combo.blockSignals(blocked)
            self.mode_combo.setEnabled(enabled and not view["active"])
            self._populate_targets(view)

            self.status_chip.setText(
                view["mode"].upper() if view["mode"] else "LOBBY"
            )
            self.arena_status.setText(
                f"{view['encounter_name'] or 'No match'} · floor {view['floor']} · "
                f"Dominion Factor {view['dominion_factor']:,} "
                f"(next win {view['round_factor']:,}) · "
                f"{view['boss_kills']:,} boss kills · "
                f"{view['journal_pages']}/20 journal pages"
            )
            maximum = max(1, int(view["engaged_max_lifepoints"]))
            current = max(0, min(maximum, int(view["engaged_lifepoints"])))
            self.enemy_health.setRange(0, maximum)
            self.enemy_health.setValue(current)
            self.enemy_health.setFormat(
                f"{view['engaged_name'] or 'Arena empty'} {current}/{maximum} LP"
                + (
                    f" · {len(view['roster_names'])} in the arena"
                    if view["roster_names"]
                    else ""
                )
            )

            offer = view["offer_row"]
            active_handicaps = ", ".join(
                str(row["display_name"]) for row in view["handicap_rows"]
            )
            self.handicap_status.setText(
                (
                    f"Spinner: {offer['display_name']} ({offer['factor_delta']:+d} factor)"
                    if offer
                    else f"Handicaps: {active_handicaps or 'none'}"
                )
                + f" · suffered {len(view['suffered_handicaps'])}/22"
            )
            self.accept_button.setEnabled(enabled and bool(offer))
            self.respin_button.setEnabled(enabled and bool(offer.get("can_respin")))
            self.nudge_button.setEnabled(enabled and bool(offer.get("can_nudge")))

            blocked = self.powerup_combo.blockSignals(True)
            selected_item = str(self.powerup_combo.currentData() or "")
            self.powerup_combo.clear()
            inventory = self._player_data.get("inventory") or {}
            for item_name in view["exchangeable_items"]:
                self.powerup_combo.addItem(
                    f"{item_name} ×{int(inventory.get(item_name, 0))}", item_name
                )
            self._select(self.powerup_combo, selected_item)
            self.powerup_combo.blockSignals(blocked)
            self.powerup_combo.setEnabled(enabled and self.powerup_combo.count() > 0)
            self.use_button.setEnabled(
                enabled and view["active"] and self.powerup_combo.count() > 0
            )
            self.eat_button.setEnabled(enabled and view["active"])

            blocked = self.skill_combo.blockSignals(True)
            selected_skill = str(self.skill_combo.currentData() or "")
            self.skill_combo.clear()
            for skill_id in view["xp_book_skills"]:
                self.skill_combo.addItem(skill_id.title(), skill_id)
            self._select(self.skill_combo, selected_skill)
            self.skill_combo.blockSignals(blocked)
            self.claim_box_button.setEnabled(enabled and bool(view["claim_enabled"]))
            self.exchange_button.setEnabled(
                enabled and bool(view["exchangeable_items"])
            )
            self.read_button.setEnabled(enabled and view["xp_books_held"] > 0)

            blocked = self.reward_combo.blockSignals(True)
            selected_reward = str(self.reward_combo.currentData() or "")
            self.reward_combo.clear()
            reward_rows = [
                (item_name, reward_id)
                for item_name, reward_id in (
                    ("Goliath gloves", "goliath_gloves"),
                    ("Spellcaster gloves", "spellcaster_gloves"),
                    ("Swift gloves", "swift_gloves"),
                    ("Dreadnip ×100", "dreadnip"),
                    ("Ascendancy mines ×10", "ascendancy_mines"),
                )
                if reward_id in view["unlocked_rewards"]
            ]
            for item_name, reward_id in reward_rows:
                self.reward_combo.addItem(item_name, reward_id)
            self._select(self.reward_combo, selected_reward)
            self.reward_combo.blockSignals(blocked)
            self.reward_combo.setEnabled(enabled and bool(reward_rows))
            self.claim_reward_button.setEnabled(enabled and bool(reward_rows))
            self.claim_reward_button.setToolTip(
                f"{view['reward_credits']}/15 reward credits banked"
            )
            self.mines_button.setEnabled(enabled and bool(view["mines_ready"]))
            self.spectate_button.setEnabled(
                enabled and not view["spectated"] and view["talked_with_face"]
            )

            reasons = view["entry_reasons"]
            self.requirements.setText(" · ".join(str(value) for value in reasons))
            self.requirements.setVisible(bool(reasons))
            self.primary_button.setText(
                "Talk to the Strange face"
                if not view["talked_with_face"]
                else str(view["primary_label"])
            )
            self.primary_button.setEnabled(
                enabled
                and (
                    not view["talked_with_face"]
                    or bool(view["primary_enabled"])
                )
            )
            self.leave_button.setVisible(bool(view["leave_visible"]))
            self.leave_button.setEnabled(enabled and bool(view["leave_visible"]))

else:

    class DominionTowerPanel:
        def __init__(self, player_data: Mapping[str, Any], **kwargs: Any) -> None:
            self._player_data = player_data

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
