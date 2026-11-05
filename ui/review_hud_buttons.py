"""The review HUD's action buttons: banking, ammo pickup and Resume."""

from __future__ import annotations

from ..logic_pure.combat.ammunition import ammo_pickup_button_view_pure
from ..core.last_action import resume_button_view_pure
from ..logic.review_strip_logic import REVIEW_BANK_RUN_LABEL, REVIEW_BANK_RUN_TOOLTIP

try:
    from aqt.qt import QHBoxLayout, QLabel, QPushButton, QSizePolicy, Qt, QVBoxLayout  # type: ignore

    HAS_QT = True
except Exception:
    HAS_QT = False


if HAS_QT:

    class ReviewBankRunButton(QPushButton):
        """Always-present strip action backed by the runtime bank-run seam."""

        def __init__(self, parent=None):
            super().__init__(REVIEW_BANK_RUN_LABEL, parent)
            self.setObjectName("reviewBankRunButton")
            self.setToolTip(REVIEW_BANK_RUN_TOOLTIP)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self._action_callback = None
            self.clicked.connect(self._activate)

        def set_data(self, view: dict, action_callback=None) -> None:
            self._action_callback = action_callback
            self.setText(str(view.get("text", REVIEW_BANK_RUN_LABEL)))
            self.setToolTip(str(view.get("tooltip", REVIEW_BANK_RUN_TOOLTIP)))
            self.setEnabled(bool(view.get("enabled")) and action_callback is not None)
            visible = bool(view.get("visible", True))
            self.setProperty("ankiscapeOverlayRequested", visible)
            self.setVisible(visible)

        def _activate(self) -> None:
            if self._action_callback is not None:
                self._action_callback()

    class ReviewAmmoPickupButton(ReviewBankRunButton):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("reviewAmmoPickupButton")
            self.setStyleSheet("QPushButton { color: palette(text); background: palette(base); font-size: 10px; padding: 1px 6px; }")
            self.hide()

        def set_player_data(self, data, action_callback=None):
            self.set_data(ammo_pickup_button_view_pure(data), action_callback)
            self.setFixedSize(self.sizeHint())

    class ReviewResumeButton(QPushButton):
        """Restart the action the switch to Bankstanding stopped.

        The label carries the whole action name, and quest names run past 45
        characters, so the text sits in a word-wrapping label that the button
        sizes itself around instead of a one-line button text that would clip.
        """

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("reviewResumeButton")
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self._text = QLabel(self)
            self._text.setObjectName("reviewResumeButtonText")
            self._text.setWordWrap(True)
            self._text.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout = QHBoxLayout(self)
            layout.setContentsMargins(10, 4, 10, 4)
            layout.addWidget(self._text)
            policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            policy.setHeightForWidth(True)
            self.setSizePolicy(policy)
            # The HUD box is dark in both themes, so the button carries its own
            # colours like the rest of the HUD instead of the native palette.
            self.setStyleSheet(
                """
                QPushButton#reviewResumeButton {
                    background-color: #2E7D32;
                    border: 1px solid rgba(255, 255, 255, 60);
                    border-radius: 6px;
                }
                QPushButton#reviewResumeButton:hover { background-color: #388E3C; }
                QPushButton#reviewResumeButton:pressed { background-color: #1B5E20; }
                QLabel#reviewResumeButtonText { color: white; font-weight: 600; }
                """
            )
            self._action_callback = None
            self.bank_status = ""
            self.clicked.connect(self._activate)
            self.setVisible(False)

        def sizeHint(self):
            return self.layout().sizeHint()

        def minimumSizeHint(self):
            return self.layout().minimumSize()

        def hasHeightForWidth(self) -> bool:
            return True

        def heightForWidth(self, width: int) -> int:
            return self.layout().totalHeightForWidth(width)

        def set_action(self, action_callback) -> None:
            self._action_callback = action_callback
            self.setEnabled(action_callback is not None)

        def set_data(self, player_data: dict, current_skill: str) -> None:
            view = resume_button_view_pure(player_data, current_skill)
            self._text.setText(view["text"])
            self.setToolTip(view["tooltip"])
            self.setAccessibleName(view["text"])
            self.bank_status = view["bank_status"]
            self.setEnabled(self._action_callback is not None)
            self.setVisible(view["visible"])

        def _activate(self) -> None:
            if self._action_callback is not None:
                self._action_callback()

else:

    class ReviewBankRunButton:
        def __init__(self, parent=None):
            pass
        def set_data(self, view: dict, action_callback=None) -> None:
            pass

    class ReviewAmmoPickupButton(ReviewBankRunButton):
        def set_player_data(self, data, action_callback=None):
            pass


def build_review_hud_action_row(hud):
    hud.chips_lbl = QLabel("")
    hud.chips_lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 10px;")
    hud.slayer_lbl = QLabel("")
    hud.slayer_lbl.setObjectName("slayerAssignmentProgress")
    hud.slayer_lbl.setStyleSheet(hud.chips_lbl.styleSheet())
    hud.slayer_lbl.setVisible(False)
    # Slayer progress stacks under the chips beside the Bank run
    # button: a row of its own overflows the fixed-height card.
    chips_column = QVBoxLayout()
    chips_column.setContentsMargins(0, 0, 0, 0)
    chips_column.setSpacing(1)
    chips_column.addWidget(hud.chips_lbl)
    chips_column.addWidget(hud.slayer_lbl)
    # Resume shows only at Bankstanding, where the chips are empty.
    hud.resume_button = ReviewResumeButton(hud)
    chips_column.addWidget(hud.resume_button)
    bottom_row = QHBoxLayout()
    bottom_row.setContentsMargins(0, 0, 0, 0)
    bottom_row.setSpacing(6)
    bottom_row.addLayout(chips_column, 1)
    hud.action_column = QHBoxLayout()
    hud.action_column.setContentsMargins(0, 0, 0, 0)
    hud.ammo_pickup_button = ReviewAmmoPickupButton(hud)
    hud.action_column.addWidget(hud.ammo_pickup_button)
    bottom_row.addLayout(hud.action_column)
    return bottom_row


def attach_review_bank_run_button(hud, button):
    button.setParent(hud)
    button.setFixedSize(button.sizeHint())
    hud.action_column.addWidget(
        button, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
