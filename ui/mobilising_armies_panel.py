"""Compact Mobilising Armies panel; the pure view owns every UI rule."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from ..core.constants import UTILITY_ACTIVITY_DATA
from ..data.mobilising_armies_data import MOBILISING_ARMIES_ACTIVITY_ID
from ..logic.mobilising_armies_logic import mobilising_armies_view_pure

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
        QSpinBox,
        Qt,
        QVBoxLayout,
        QWidget,
    )

    HAS_QT = True
except Exception:
    HAS_QT = False


if HAS_QT:

    class MobilisingArmiesPanel(QFrame):
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
            self.setObjectName("mobilisingArmiesPanel")
            self.setStyleSheet(
                "QFrame#mobilisingArmiesPanel { border: 1px solid palette(mid); "
                "border-radius: 8px; background: palette(base); }"
            )
            layout = QVBoxLayout(self)
            # Three surfaces share one card — command centre, battle and Officer
            # Tower — so the spacing is tight enough to keep even the idle state
            # inside the ~560 logical points an Anki dialog actually has.
            layout.setContentsMargins(10, 6, 10, 6)
            layout.setSpacing(3)

            header = QWidget(self)
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(0, 0, 0, 0)
            icon = QLabel(header)
            icon.setFixedSize(32, 32)
            icon_path = str(
                UTILITY_ACTIVITY_DATA[MOBILISING_ARMIES_ACTIVITY_ID].get("icon_path", "")
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
            title = QLabel("Mobilising Armies", header)
            title.setStyleSheet("font-weight: 700; color: palette(text);")
            self.status_chip = QLabel(header)
            self.status_chip.setStyleSheet("font-size: 11px; color: palette(text);")
            header_layout.addWidget(icon)
            header_layout.addWidget(title)
            header_layout.addStretch(1)
            header_layout.addWidget(self.status_chip)
            layout.addWidget(header)

            self.wallets = QLabel(self)
            self.wallets.setObjectName("mobilisingArmiesRewardWallet")
            self.wallets.setWordWrap(True)
            self.wallets.setStyleSheet("color: palette(text); font-weight: 600;")
            self.battle_status = QLabel(self)
            self.battle_status.setWordWrap(True)
            self.battle_status.setStyleSheet("font-size: 11px; color: palette(text);")
            layout.addWidget(self.battle_status)
            self.objective_bar = QProgressBar(self)
            self.objective_bar.setObjectName("mobilisingArmiesObjective")
            self.objective_bar.setTextVisible(True)
            layout.addWidget(self.objective_bar)

            plan = QWidget(self)
            grid = QGridLayout(plan)
            grid.setContentsMargins(0, 0, 0, 0)
            grid.setHorizontalSpacing(6)
            grid.setVerticalSpacing(3)
            self.scenario_combo = QComboBox(plan)
            self.formation_combo = QComboBox(plan)
            self.order_combo = QComboBox(plan)
            self.route_combo = QComboBox(plan)
            self.investment_spin = QSpinBox(plan)
            self.investment_spin.setSingleStep(500)
            self.save_button = QPushButton("Save battle plan", plan)
            for widget, name in (
                (self.scenario_combo, "Mobilising Armies scenario"),
                (self.formation_combo, "Mobilising Armies formation"),
                (self.order_combo, "Mobilising Armies squad order"),
                (self.route_combo, "Mobilising Armies siege route"),
                (self.investment_spin, "Mobilising Armies stake"),
            ):
                widget.setAccessibleName(name)
            grid.addWidget(QLabel("Scenario", plan), 0, 0)
            grid.addWidget(self.scenario_combo, 0, 1)
            grid.addWidget(QLabel("Formation", plan), 1, 0)
            grid.addWidget(self.formation_combo, 1, 1)
            grid.addWidget(QLabel("Orders", plan), 2, 0)
            grid.addWidget(self.order_combo, 2, 1)
            grid.addWidget(QLabel("Siege route", plan), 3, 0)
            grid.addWidget(self.route_combo, 3, 1)
            grid.addWidget(QLabel("Stake", plan), 4, 0)
            grid.addWidget(self.investment_spin, 4, 1)
            grid.addWidget(self.save_button, 5, 1)
            layout.addWidget(plan)

            muster = QWidget(self)
            muster_layout = QGridLayout(muster)
            muster_layout.setContentsMargins(0, 0, 0, 0)
            muster_layout.setHorizontalSpacing(6)
            muster_layout.setVerticalSpacing(3)
            self.invest_combo = QComboBox(muster)
            self.invest_combo.setAccessibleName("Mobilising Armies investment item")
            self.invest_button = QPushButton("Invest", muster)
            self.squad_combo = QComboBox(muster)
            self.squad_combo.setAccessibleName("Mobilising Armies squad")
            self.recruit_button = QPushButton("Recruit", muster)
            self.unit_combo = QComboBox(muster)
            self.unit_combo.setAccessibleName("Mobilising Armies special unit")
            self.unit_button = QPushButton("Hire", muster)
            self.deploy_button = QPushButton("Deploy", muster)
            muster_layout.addWidget(self.invest_combo, 0, 0)
            muster_layout.addWidget(self.invest_button, 0, 1)
            muster_layout.addWidget(self.squad_combo, 1, 0)
            muster_layout.addWidget(self.recruit_button, 1, 1)
            muster_layout.addWidget(self.unit_combo, 2, 0)
            muster_layout.addWidget(self.unit_button, 2, 1)
            muster_layout.addWidget(self.deploy_button, 2, 2)
            layout.addWidget(muster)

            tower = QWidget(self)
            tower.setObjectName("mobilisingArmiesRewardShop")
            tower_layout = QGridLayout(tower)
            tower_layout.setContentsMargins(0, 0, 0, 0)
            tower_layout.setHorizontalSpacing(6)
            tower_layout.setVerticalSpacing(3)
            self.floor_combo = QComboBox(tower)
            self.floor_combo.setAccessibleName("Officer Tower floor")
            self.spoils_button = QPushButton("View spoils", tower)
            self.claim_button = QPushButton("Take three lots", tower)
            self.reward_combo = QComboBox(tower)
            self.reward_combo.setAccessibleName("Officer Tower reward")
            self.buy_button = QPushButton("Buy", tower)
            self.refund_button = QPushButton("Refund", tower)
            self.prefix_combo = QComboBox(tower)
            self.prefix_combo.setAccessibleName("Mobilising Armies name prefix")
            self.prefix_button = QPushButton("Set prefix", tower)
            tower_layout.addWidget(self.wallets, 0, 0, 1, 3)
            tower_layout.addWidget(self.floor_combo, 1, 0)
            tower_layout.addWidget(self.spoils_button, 1, 1)
            tower_layout.addWidget(self.claim_button, 1, 2)
            tower_layout.addWidget(self.reward_combo, 2, 0)
            tower_layout.addWidget(self.buy_button, 2, 1)
            tower_layout.addWidget(self.refund_button, 2, 2)
            tower_layout.addWidget(self.prefix_combo, 3, 0)
            tower_layout.addWidget(self.prefix_button, 3, 1)
            layout.addWidget(tower)
            self.spoils_label = QLabel(self)
            self.spoils_label.setWordWrap(True)
            self.spoils_label.setStyleSheet("font-size: 11px; color: palette(text);")
            layout.addWidget(self.spoils_label)

            gear = QWidget(self)
            gear_layout = QGridLayout(gear)
            gear_layout.setContentsMargins(0, 0, 0, 0)
            gear_layout.setHorizontalSpacing(6)
            self.locator_combo = QComboBox(gear)
            self.locator_combo.setAccessibleName("Mobilising Armies locator")
            self.locator_skill_combo = QComboBox(gear)
            self.locator_skill_combo.setAccessibleName("Locator resource kind")
            self.locator_button = QPushButton("Locate", gear)
            self.kit_combo = QComboBox(gear)
            self.kit_combo.setAccessibleName("Mobilising Armies quest kit")
            self.kit_button = QPushButton("Empty kit", gear)
            gear_layout.addWidget(self.locator_combo, 0, 0)
            gear_layout.addWidget(self.locator_skill_combo, 0, 1)
            gear_layout.addWidget(self.locator_button, 0, 2)
            gear_layout.addWidget(self.kit_combo, 1, 0)
            gear_layout.addWidget(self.kit_button, 1, 1)
            layout.addWidget(gear)

            self.requirements = QLabel(self)
            self.requirements.setWordWrap(True)
            self.requirements.setStyleSheet("color: #ef5350; font-size: 11px;")
            layout.addWidget(self.requirements)
            actions = QWidget(self)
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self.primary_button = QPushButton(actions)
            self.forfeit_button = QPushButton("Forfeit", actions)
            self.forfeit_button.setStyleSheet("color: #ef5350;")
            actions_layout.addWidget(self.primary_button, 1)
            actions_layout.addWidget(self.forfeit_button)
            layout.addWidget(actions)

            self.save_button.clicked.connect(lambda _checked=False: self._save_plan())
            self.invest_button.clicked.connect(lambda _checked=False: self._invest())
            self.recruit_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "recruit",
                    {"squad": str(self.squad_combo.currentData() or ""), "quantity": 10},
                )
            )
            self.unit_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "buy_special_unit",
                    {"unit": str(self.unit_combo.currentData() or ""), "quantity": 1},
                )
            )
            self.deploy_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "deploy", {"unit": str(self.unit_combo.currentData() or "")}
                )
            )
            self.spoils_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "roll_spoils", {"floor": str(self.floor_combo.currentData() or "")}
                )
            )
            self.claim_button.clicked.connect(lambda _checked=False: self._claim_spoils())
            self.buy_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "buy_reward",
                    {"item_name": str(self.reward_combo.currentData() or "")},
                )
            )
            self.refund_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "refund_reward",
                    {"item_name": str(self.reward_combo.currentData() or "")},
                )
            )
            self.prefix_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "set_prefix", {"prefix": str(self.prefix_combo.currentData() or "")}
                )
            )
            self.locator_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "use_locator",
                    {
                        "item_name": str(self.locator_combo.currentData() or ""),
                        "skill": str(self.locator_skill_combo.currentData() or ""),
                    },
                )
            )
            self.kit_button.clicked.connect(
                lambda _checked=False: self._run_command(
                    "open_quest_kit",
                    {"item_name": str(self.kit_combo.currentData() or "")},
                )
            )
            self.primary_button.clicked.connect(lambda _checked=False: self._enter_or_select())
            self.forfeit_button.clicked.connect(lambda _checked=False: self._confirm_forfeit())
            self.refresh()

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data
            self.refresh()

        @staticmethod
        def _select(combo: QComboBox, value: str) -> None:
            index = combo.findData(value)
            if index >= 0:
                combo.setCurrentIndex(index)

        @staticmethod
        def _fill(combo: QComboBox, rows, label_key: str = "display_name") -> None:
            selected = str(combo.currentData() or "")
            blocked = combo.blockSignals(True)
            combo.clear()
            for row in rows:
                combo.addItem(str(row[label_key]), row["id"])
                if not row.get("unlocked", True):
                    item = combo.model().item(combo.count() - 1)
                    if item is not None:
                        item.setEnabled(False)
            MobilisingArmiesPanel._select(combo, selected)
            combo.blockSignals(blocked)

        def _run_command(
            self, action_id: str, payload: Mapping[str, Any] | None = None
        ) -> dict[str, Any]:
            result = (
                dict(self._on_command(action_id, payload or {}) or {})
                if self._on_command is not None
                else {"ok": False, "message": "Mobilising Armies actions are unavailable."}
            )
            if not result.get("ok", False):
                QMessageBox.warning(
                    self,
                    "Mobilising Armies",
                    str(result.get("message", "Action failed.")),
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
                    "scenario": str(self.scenario_combo.currentData() or ""),
                    "formation": str(self.formation_combo.currentData() or ""),
                    "order": str(self.order_combo.currentData() or ""),
                    "siege_route": str(self.route_combo.currentData() or ""),
                    "investment": int(self.investment_spin.value()),
                },
            )

        def _invest(self) -> None:
            item_name = str(self.invest_combo.currentData() or "")
            if not item_name:
                return
            view = mobilising_armies_view_pure(self._player_data)
            held = next(
                (
                    int(row["held"])
                    for row in view["investment_options"]
                    if str(row["id"]) == item_name
                ),
                0,
            )
            self._run_command("invest", {"item_name": item_name, "quantity": held})

        def _claim_spoils(self) -> None:
            view = mobilising_armies_view_pure(self._player_data)
            chosen = [str(row["item"]) for row in view["spoils_offer"]][:3]
            self._run_command("claim_spoils", {"items": chosen})

        def _enter_or_select(self) -> None:
            view = mobilising_armies_view_pure(self._player_data)
            if not view["active"] and not self._run_command("enter").get("ok", False):
                return
            if self._on_select is not None:
                self._on_select(MOBILISING_ARMIES_ACTIVITY_ID)

        def _confirm_forfeit(self) -> None:
            answer = QMessageBox.question(
                self,
                "Forfeit this scenario?",
                "Forfeiting pays no rank points and no reward credits.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                self._run_command("forfeit")

        def refresh(self) -> None:
            view = mobilising_armies_view_pure(self._player_data)
            enabled = self._on_command is not None
            policy = view["mobilising_armies_policy"]
            self._fill(self.scenario_combo, view["scenario_options"])
            self._fill(self.formation_combo, view["formation_options"])
            self._fill(self.order_combo, view["order_options"])
            self._fill(self.route_combo, view["siege_route_options"])
            self._fill(self.prefix_combo, view["prefix_options"])
            self._fill(self.locator_skill_combo, view["locator_skill_options"])
            self._select(self.scenario_combo, str(policy["scenario"]))
            self._select(self.formation_combo, str(policy["formation"]))
            self._select(self.order_combo, str(policy["order"]))
            self._select(self.route_combo, str(policy["siege_route"]))

            for combo, rows in (
                (self.invest_combo, view["investment_options"]),
                (self.squad_combo, view["squad_options"]),
                (self.floor_combo, view["floor_options"]),
            ):
                self._fill(combo, rows)
            self._fill(
                self.unit_combo,
                [
                    {
                        "id": row["id"],
                        "display_name": f"{row['display_name']} ({int(row['held'])})",
                        "unlocked": bool(row["deployable"] or row["affordable"]),
                    }
                    for row in view["special_unit_options"]
                ],
            )
            reward_rows = [
                {
                    "id": row["item"],
                    "display_name": (
                        f"{row['item']} · {int(row['cost']):,} rc"
                        + (f" · rank {int(row['minimum_rank'])}" if row["minimum_rank"] else "")
                        + (f" · needs {row['base_item']}" if row["base_item"] else "")
                    ),
                    "unlocked": bool(row["unlocked"]),
                }
                for row in view["reward_options"]
            ]
            self._fill(self.reward_combo, reward_rows)
            locator_rows = [
                {
                    "id": row["item"],
                    "display_name": f"{row['item']} ({int(row['held'])})",
                    "unlocked": bool(row["usable"]),
                }
                for row in view["locator_options"]
            ]
            self._fill(self.locator_combo, locator_rows)
            kit_rows = [
                {
                    "id": row["item"],
                    "display_name": f"{row['item']} ({int(row['held'])})",
                    "unlocked": bool(row["openable"]),
                }
                for row in view["quest_kit_options"]
            ]
            self._fill(self.kit_combo, kit_rows)

            self.investment_spin.setRange(0, int(view["maximum_investment"]))
            self.investment_spin.setValue(int(policy["investment"]))
            self.investment_spin.setEnabled(enabled and not view["active"])
            for combo in (
                self.scenario_combo,
                self.formation_combo,
                self.investment_spin,
                self.invest_combo,
                self.squad_combo,
                self.floor_combo,
            ):
                combo.setEnabled(enabled and not view["active"])
            self.order_combo.setEnabled(enabled)
            self.route_combo.setEnabled(enabled and bool(view["siege_route_control_enabled"]))
            self.save_button.setEnabled(enabled)

            self.status_chip.setText("IN BATTLE" if view["active"] else "READY")
            wallet_text = (
                f"{int(view['mobilising_armies_investment_credits']):,} investment · "
                f"{int(view['mobilising_armies_reward_credits']):,} reward credits · "
                f"rank {int(view['mobilising_armies_rank'])}"
                + (f" ({view['rank_prefix_band']})" if view["rank_prefix_band"] else "")
            )
            self.wallets.setText(wallet_text)
            self.battle_status.setText(
                f"{view['scenario_name']} · order {int(view['beat'])}/{int(view['beat_count'])} · "
                f"orders given {int(view['commands'])}/{int(view['commands_required'])}"
                f"{' (rank earned)' if view['rank_eligible'] else ''} · "
                f"squads {int(view['squads_alive'])} v {int(view['rivals_alive'])} · "
                f"contracts {int(view['squad_contracts'])}/"
                f"{int(view['squad_contracts_required'])} · "
                f"specials {int(view['special_units_held'])}/{int(view['special_unit_cap'])} · "
                f"rank left this hour {int(view['rank_points_left_this_window'])}"
            )
            target = max(1, int(view["objective_target"]))
            self.objective_bar.setRange(0, target)
            self.objective_bar.setValue(max(0, min(target, int(view["objective"]))))
            self.objective_bar.setFormat(
                f"{view['objective_label']} {int(view['objective']):,}/{target:,} "
                f"(rival {int(view['opponent_objective']):,})"
            )

            offer = view["spoils_offer"]
            self.spoils_label.setText(
                " · ".join(f"{int(row['quantity']):,} {row['item']}" for row in offer)
                if offer
                else "No Spoils of War stall is laid out."
            )
            self.spoils_button.setEnabled(enabled and not view["active"])
            self.claim_button.setEnabled(enabled and bool(view["spoils_claim_enabled"]))
            selected_reward = str(self.reward_combo.currentData() or "")
            reward_row = next(
                (row for row in view["reward_options"] if str(row["item"]) == selected_reward),
                None,
            )
            self.buy_button.setEnabled(
                enabled and bool(reward_row and reward_row["affordable"])
            )
            self.refund_button.setEnabled(
                enabled and bool(reward_row and reward_row["refundable"])
            )
            selected_prefix = str(self.prefix_combo.currentData() or "")
            self.prefix_button.setEnabled(
                enabled
                and any(
                    str(row["id"]) == selected_prefix and row["unlocked"]
                    for row in view["prefix_options"]
                )
            )
            selected_locator = str(self.locator_combo.currentData() or "")
            self.locator_button.setEnabled(
                enabled
                and any(
                    str(row["item"]) == selected_locator and row["usable"]
                    for row in view["locator_options"]
                )
            )
            selected_kit = str(self.kit_combo.currentData() or "")
            self.kit_button.setEnabled(
                enabled
                and any(
                    str(row["item"]) == selected_kit and row["openable"]
                    for row in view["quest_kit_options"]
                )
            )
            selected_unit = str(self.unit_combo.currentData() or "")
            unit_row = next(
                (row for row in view["special_unit_options"] if str(row["id"]) == selected_unit),
                None,
            )
            self.unit_button.setEnabled(enabled and bool(unit_row and unit_row["affordable"]))
            self.deploy_button.setEnabled(enabled and bool(unit_row and unit_row["deployable"]))
            squad_row = next(
                (
                    row
                    for row in view["squad_options"]
                    if str(row["id"]) == str(self.squad_combo.currentData() or "")
                ),
                None,
            )
            self.recruit_button.setEnabled(enabled and bool(squad_row and squad_row["affordable"]))
            invest_row = next(
                (
                    row
                    for row in view["investment_options"]
                    if str(row["id"]) == str(self.invest_combo.currentData() or "")
                ),
                None,
            )
            self.invest_button.setEnabled(
                enabled and not view["active"] and bool(invest_row and invest_row["investable"])
            )

            reasons = view["entry_reasons"]
            self.requirements.setText(" · ".join(str(value) for value in reasons))
            self.requirements.setVisible(bool(reasons))
            self.primary_button.setText(str(view["primary_label"]))
            self.primary_button.setEnabled(enabled and bool(view["primary_enabled"]))
            self.forfeit_button.setVisible(bool(view["forfeit_visible"]))
            self.forfeit_button.setEnabled(enabled and bool(view["forfeit_visible"]))

else:

    class MobilisingArmiesPanel:
        def __init__(self, player_data: Mapping[str, Any], **kwargs: Any) -> None:
            self._player_data = player_data

        def set_player_data(self, player_data: Mapping[str, Any]) -> None:
            self._player_data = player_data

        def refresh(self) -> None:
            return None
