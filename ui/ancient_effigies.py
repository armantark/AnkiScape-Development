"""Ancient Effigies window: inspect effigies, feed them skills, rub the lamp.

The window owns no game state. Every row and detail is read from the live save
through the feature controller, and every change goes back through it, so a
close and reopen, a focus change or an Undo always shows current ownership.
"""

from __future__ import annotations

from aqt.qt import (  # type: ignore
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QEvent,
    QFrame,
    QHBoxLayout,
    QIcon,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPixmap,
    QPushButton,
    QScrollArea,
    QSize,
    QSizePolicy,
    Qt,
    QVBoxLayout,
    QWidget,
)

from . import ui as _ui


WINDOW_TITLE = "Ancient Effigies"
DEFAULT_SIZE = (680, 560)
EMPTY_TEXT = "You do not own an Ancient Effigy or Dragonkin lamp."
INTRO_TEXT = (
    "Each effigy wants knowledge from one of two skills. Investigate it with "
    "either skill at the level shown to gain experience in that skill; after "
    "four investigations it leaves a Dragonkin lamp."
)
LAMP_TEXT = (
    "Rub the lamp to gain experience in any one of 25 skills. The reward is "
    "(L³ − 2L² + 100L) ÷ 20, rounded down, where L is your permanent level in "
    "that skill when you confirm."
)
_ROW_ID_ROLE = Qt.ItemDataRole.UserRole


def _action_button_css(widget: QWidget) -> str:
    return (
        "QPushButton { color: palette(text); background: palette(base); "
        "border: 1px solid palette(mid); border-radius: 5px; padding: 6px 14px; }"
        "QPushButton:hover { border-color: palette(highlight); }"
        "QPushButton:focus { border: 2px solid palette(highlight); }"
        f"QPushButton:disabled {{ color: {_ui.dim_text_css(widget)}; }}"
    )


def _wrapped_label(text: str, object_name: str, *, dim: bool = False) -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    label.setWordWrap(True)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    if dim:
        label.setStyleSheet(f"color: {_ui.dim_text_css(label)};")
    else:
        label.setStyleSheet("color: palette(text);")
    return label


def _action_button(text: str, object_name: str) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName(object_name)
    button.setAutoDefault(False)
    button.setStyleSheet(_action_button_css(button))
    button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    return button


def _row_text(row) -> str:
    return f"{row['name']} · Copy {row['copy_number']} · {row['location_label']}"


class AncientEffigiesWindow(QDialog):
    """One list row per owned copy; the detail area acts on the selected copy."""

    def __init__(self, controller, parent=None) -> None:
        super().__init__(parent)
        self.controller = controller
        self._selected_id = None
        self.setObjectName("ancientEffigiesWindow")
        self.setWindowTitle(WINDOW_TITLE)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setSizeGripEnabled(True)
        self.resize(*DEFAULT_SIZE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 12)
        layout.setSpacing(8)
        layout.addWidget(_wrapped_label(INTRO_TEXT, "ancientEffigiesIntro", dim=True))

        self.list = QListWidget(self)
        self.list.setObjectName("ancientEffigiesList")
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.list.setIconSize(QSize(24, 24))
        self.list.setMinimumHeight(84)
        self.list.setAccessibleName("Owned effigies and lamps")
        self.list.currentItemChanged.connect(self._on_current_item_changed)
        layout.addWidget(self.list, 2)

        self.empty_label = _wrapped_label(EMPTY_TEXT, "ancientEffigiesEmpty")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.empty_label, 5)

        self.detail_scroll = QScrollArea(self)
        self.detail_scroll.setObjectName("ancientEffigiesDetailScroll")
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.detail_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.detail_scroll, 3)

        self.feedback = _wrapped_label("", "ancientEffigiesFeedback")
        self.feedback.setVisible(False)
        layout.addWidget(self.feedback)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close, parent=self)
        buttons.setObjectName("ancientEffigiesButtons")
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)

    # Reading live state

    def refresh(self) -> None:
        """Rebuild rows from live ownership, keeping the selected copy selected."""
        rows = self.controller.rows()
        previous_row = max(0, self.list.currentRow())
        self.list.blockSignals(True)
        self.list.clear()
        for row in rows:
            item = QListWidgetItem(QIcon(row["icon"]), _row_text(row))
            item.setData(_ROW_ID_ROLE, row["instance_id"])
            item.setToolTip(f"{row['name']}, copy {row['copy_number']}: {row['pair_text']}")
            self.list.addItem(item)
        ids = [row["instance_id"] for row in rows]
        if self._selected_id in ids:
            self.list.setCurrentRow(ids.index(self._selected_id))
        elif ids:
            self.list.setCurrentRow(min(previous_row, len(ids) - 1))
        self.list.blockSignals(False)
        current = self.list.currentItem()
        self._selected_id = current.data(_ROW_ID_ROLE) if current is not None else None
        self.list.setVisible(bool(rows))
        self.empty_label.setVisible(not rows)
        self._show_detail()

    def _on_current_item_changed(self, current, _previous) -> None:
        self._selected_id = current.data(_ROW_ID_ROLE) if current is not None else None
        self._set_feedback("")
        self._show_detail()

    def changeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        super().changeEvent(event)
        if event.type() == QEvent.Type.ActivationChange and self.isActiveWindow():
            self.refresh()

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt override)
        self.controller.window_closed(self)
        super().closeEvent(event)

    def _set_feedback(self, message: str) -> None:
        self.feedback.setText(message)
        self.feedback.setVisible(bool(message))

    # Detail area

    def _show_detail(self) -> None:
        detail = self.controller.detail(self._selected_id) if self._selected_id else None
        panel = QWidget()
        panel.setObjectName("ancientEffigiesDetail")
        body = QVBoxLayout(panel)
        body.setContentsMargins(2, 4, 2, 4)
        body.setSpacing(8)
        if detail is not None:
            body.addLayout(self._header(detail))
            if detail["kind"] == "lamp":
                self._lamp_detail(body, detail)
            else:
                self._stage_detail(body, detail)
        body.addStretch(1)
        self.detail_scroll.setWidget(panel)
        self.detail_scroll.setVisible(detail is not None)

    def _header(self, detail) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setSpacing(10)
        icon = QLabel()
        icon.setObjectName("ancientEffigiesIcon")
        icon.setPixmap(QPixmap(detail["icon"]))
        icon.setFixedSize(36, 36)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)
        titles = QVBoxLayout()
        titles.setSpacing(2)
        name = _wrapped_label(detail["name"], "ancientEffigiesName")
        name.setStyleSheet("color: palette(text); font-size: 15px; font-weight: 600;")
        titles.addWidget(name)
        titles.addWidget(
            _wrapped_label(f"Copy {detail['copy_number']} · {detail['location_label']}", "ancientEffigiesLocation", dim=True)
        )
        header.addLayout(titles, 1)
        return header

    def _stage_detail(self, body: QVBoxLayout, detail) -> None:
        if detail["output_name"] == "Dragonkin lamp":
            outcome = "then it crumbles to dust and leaves a Dragonkin lamp"
        else:
            outcome = f"then it becomes a {detail['output_name'].lower()}"
        body.addWidget(
            _wrapped_label(
                f"Requires level {detail['required_level']} in one requested skill. "
                f"Rewards {detail['reward_xp']:,} XP in the skill you use, {outcome}.",
                "ancientEffigiesRequirement",
            )
        )
        if detail["recovery_text"]:
            body.addWidget(_wrapped_label(detail["recovery_text"], "ancientEffigiesRecovery"))
        if not detail["revealed"]:
            body.addWidget(_wrapped_label(detail["pair_text"], "ancientEffigiesPair", dim=True))
            if detail["usable"]:
                inspect = _action_button("Inspect", "ancientEffigiesInspect")
                inspect.clicked.connect(lambda _checked=False, instance_id=detail["instance_id"]: self._inspect(instance_id))
                body.addWidget(inspect)
            return
        body.addWidget(_wrapped_label(f"Requested skills: {detail['pair_text']}", "ancientEffigiesPair"))
        if not detail["usable"]:
            return
        for choice in detail["choices"]:
            body.addLayout(self._choice_row(detail, choice))

    def _choice_row(self, detail, choice) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)
        button = _action_button(f"Investigate with {choice['skill_name']}", "ancientEffigiesInvestigate")
        button.setProperty("skillId", choice["skill_id"])
        button.setEnabled(choice["eligible"])
        button.clicked.connect(
            lambda _checked=False, token=detail["token"], skill_id=choice["skill_id"]: self._investigate(token, skill_id)
        )
        row.addWidget(button, 0, Qt.AlignmentFlag.AlignTop)
        reason = _wrapped_label(choice["reason"], "ancientEffigiesChoiceReason", dim=choice["eligible"])
        reason.setProperty("skillId", choice["skill_id"])
        row.addWidget(reason, 1)
        return row

    def _lamp_detail(self, body: QVBoxLayout, detail) -> None:
        body.addWidget(_wrapped_label(LAMP_TEXT, "ancientEffigiesLampText"))
        if detail["recovery_text"]:
            body.addWidget(_wrapped_label(detail["recovery_text"], "ancientEffigiesRecovery"))
        if not detail["usable"]:
            return
        row = QHBoxLayout()
        row.setSpacing(10)
        rub = _action_button("Rub", "ancientEffigiesRub")
        rub.clicked.connect(lambda _checked=False, token=detail["token"]: self._rub(token))
        destroy = _action_button("Destroy", "ancientEffigiesDestroy")
        destroy.clicked.connect(
            lambda _checked=False, token=detail["token"], warning=detail["destroy_warning"]: self._destroy(token, warning)
        )
        row.addWidget(rub)
        row.addWidget(destroy)
        row.addStretch(1)
        body.addLayout(row)

    # Actions

    def _after_action(self, result) -> None:
        self.refresh()
        self._set_feedback(result.message)

    def _inspect(self, instance_id: str) -> None:
        self._after_action(self.controller.inspect(instance_id))

    def _investigate(self, token, skill_id: str) -> None:
        self._after_action(self.controller.investigate(token, skill_id))

    def _confirm(self, title: str, text: str, detail: str, accept_text: str, *, destructive: bool) -> bool:
        box = QMessageBox(self)
        box.setObjectName("ancientEffigiesConfirm")
        box.setIcon(QMessageBox.Icon.Warning if destructive else QMessageBox.Icon.Question)
        box.setWindowTitle(title)
        box.setText(text)
        box.setInformativeText(detail)
        role = QMessageBox.ButtonRole.DestructiveRole if destructive else QMessageBox.ButtonRole.AcceptRole
        accept = box.addButton(accept_text, role)
        cancel = box.addButton(QMessageBox.StandardButton.Cancel)
        box.setDefaultButton(cancel if destructive else accept)
        box.setEscapeButton(cancel)
        box.exec()
        return box.clickedButton() is accept

    def _rub(self, token) -> None:
        skill_id = _ui._choose_xp_lamp_skill(self, "Rub the Dragonkin lamp", self.controller.lamp_skill_ids)
        if not skill_id:
            self._set_feedback("You put the lamp away. It is still yours.")
            return
        preview = self.controller.lamp_confirmation(skill_id)
        if not self._confirm(
            "Rub the Dragonkin lamp",
            f"Gain {preview['xp']:,} {preview['skill_name']} XP?",
            f"Your permanent {preview['skill_name']} level is {preview['level']}. "
            "The lamp is used up when you confirm.",
            "Rub lamp",
            destructive=False,
        ):
            self._set_feedback("You put the lamp away. It is still yours.")
            return
        self._after_action(self.controller.redeem_lamp(token, skill_id))

    def _destroy(self, token, warning: str) -> None:
        if not self._confirm("Destroy the Dragonkin lamp", "Destroy this lamp?", warning, "Destroy", destructive=True):
            self._set_feedback("The lamp is unchanged.")
            return
        self._after_action(self.controller.destroy_lamp(token))
