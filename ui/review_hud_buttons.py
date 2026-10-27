"""The review HUD's action buttons: Bank run, and Resume at Bankstanding."""

from __future__ import annotations

from ..core.last_action import resume_button_view_pure
from ..logic.review_strip_logic import REVIEW_BANK_RUN_LABEL, REVIEW_BANK_RUN_TOOLTIP

try:
    from aqt.qt import QHBoxLayout, QLabel, QPushButton, QSizePolicy, Qt  # type: ignore

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
