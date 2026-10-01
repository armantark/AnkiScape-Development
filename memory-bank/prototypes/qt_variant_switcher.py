"""PROTOTYPE ONLY: floating A/B/C switcher and capture helpers shared by the
Qt prototypes in this folder. Never imported by the add-on."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def prepare_qt(capture: bool) -> None:
    """Pick the Qt platform before anything imports aqt.

    The test harness defaults to offscreen; a live run needs the real one.
    """
    if capture:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        # Retina-sharp PNGs; layout stays in logical pixels, so geometry is unchanged.
        os.environ["QT_SCALE_FACTOR"] = "2"
    elif sys.platform == "darwin":
        os.environ.setdefault("QT_QPA_PLATFORM", "cocoa")
    sys.path.insert(0, str(REPO_ROOT))


def themed_palette(theme: str):
    from aqt.qt import QColor, QPalette  # type: ignore

    dark = theme == "dark"
    colors = {
        QPalette.ColorRole.Window: (45, 45, 45) if dark else (245, 245, 245),
        QPalette.ColorRole.WindowText: (238, 238, 238) if dark else (28, 28, 28),
        QPalette.ColorRole.Base: (35, 35, 35) if dark else (255, 255, 255),
        QPalette.ColorRole.AlternateBase: (45, 45, 45) if dark else (242, 242, 242),
        QPalette.ColorRole.Text: (238, 238, 238) if dark else (28, 28, 28),
        QPalette.ColorRole.Button: (55, 55, 55) if dark else (245, 245, 245),
        QPalette.ColorRole.ButtonText: (238, 238, 238) if dark else (28, 28, 28),
        QPalette.ColorRole.Highlight: (55, 130, 70) if dark else (74, 143, 84),
        QPalette.ColorRole.HighlightedText: (255, 255, 255),
    }
    palette = QPalette()
    for role, rgb in colors.items():
        palette.setColor(role, QColor(*rgb))
    disabled = (130, 130, 130) if dark else (160, 160, 160)
    for role in (QPalette.ColorRole.Text, QPalette.ColorRole.WindowText, QPalette.ColorRole.ButtonText):
        palette.setColor(QPalette.ColorGroup.Disabled, role, QColor(*disabled))
    return palette


def apply_theme(theme: str) -> None:
    """Fusion plus an explicit palette: offscreen never inherits the OS theme."""
    from aqt.qt import QApplication  # type: ignore

    app = QApplication.instance()
    app.setStyle("Fusion")
    app.setPalette(themed_palette(theme))


def pump(times: int = 6) -> None:
    from aqt.qt import QApplication  # type: ignore

    for _ in range(times):
        QApplication.processEvents()


def make_switcher(variants: dict, apply, anchor):
    """Floating pill below ``anchor``: arrows, one button per variant, the
    variant name. Left/Right cycle unless a text field has focus.

    ``apply(key)`` rebuilds the variant and returns the visible state to print.
    """
    from aqt.qt import (  # type: ignore
        QAbstractSpinBox,
        QApplication,
        QEvent,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QObject,
        QPushButton,
        Qt,
        QTextEdit,
        QWidget,
    )

    keys = list(variants)
    bar = QWidget(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    bar.setObjectName("prototypeSwitcher")
    bar.setStyleSheet(
        "QWidget#prototypeSwitcher { background: #111; border: 2px solid #ff3d7f; border-radius: 16px; }"
        " QPushButton { color: white; background: #333; border: none; border-radius: 10px; padding: 4px 10px; font-weight: 700; }"
        " QPushButton:checked { background: #ff3d7f; }"
        " QLabel { color: white; padding: 0 6px; }"
    )
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(8, 6, 8, 6)
    previous = QPushButton("←")
    layout.addWidget(previous)
    buttons = {}
    for key in keys:
        button = QPushButton(key)
        button.setCheckable(True)
        button.setToolTip(variants[key])
        layout.addWidget(button)
        buttons[key] = button
    following = QPushButton("→")
    layout.addWidget(following)
    name = QLabel("")
    layout.addWidget(name)
    current = {"key": keys[0]}

    def place() -> None:
        bar.adjustSize()
        frame = anchor.frameGeometry()
        bar.move(frame.center().x() - bar.width() // 2, frame.bottom() + 8)

    def select(key: str) -> None:
        current["key"] = key
        for other, button in buttons.items():
            button.setChecked(other == key)
        name.setText(f"{key} ({variants[key]})")
        state = apply(key)
        print(f"\n=== Variant {key}: {variants[key]} ===\n{state}", flush=True)
        place()

    def step(delta: int) -> None:
        select(keys[(keys.index(current["key"]) + delta) % len(keys)])

    previous.clicked.connect(lambda: step(-1))
    following.clicked.connect(lambda: step(1))
    for key, button in buttons.items():
        button.clicked.connect(lambda _=False, k=key: select(k))

    class _Arrows(QObject):
        def eventFilter(self, obj, event):  # type: ignore[no-untyped-def]
            if event.type() == QEvent.Type.KeyPress and event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
                focus = QApplication.focusWidget()
                if not isinstance(focus, (QLineEdit, QTextEdit, QAbstractSpinBox)):
                    step(-1 if event.key() == Qt.Key.Key_Left else 1)
                    return True
            return False

    bar._arrows = _Arrows(bar)
    QApplication.instance().installEventFilter(bar._arrows)
    bar.select = select
    select(keys[0])
    bar.show()
    return bar
