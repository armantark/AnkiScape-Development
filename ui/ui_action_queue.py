"""The action queue in the main menu: "Add to queue" beside each Start, and the queue list.

Both draw what ``core.menu_action_queue`` decides. Any save change that the
review HUD shows also reaches them through ``notify_action_queue_changed``, so a
target picked in a list updates the count box, and an entry a review finished
updates the list, without each list knowing about the queue.
"""

from __future__ import annotations

from ..core.action_queue import MAX_QUEUE_ENTRIES
from ..core.menu_action_queue import (
    menu_action_record_pure,
    queue_add_view_pure,
    queue_panel_view_pure,
    utility_action_record_pure,
)
from .ui_palette import dim_text_css

try:
    from aqt.qt import (  # type: ignore
        QFrame,
        QHBoxLayout,
        QLabel,
        QObject,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
        pyqtSignal,
    )

    HAS_QT = True
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    HAS_QT = False

_BUTTON_STYLE = (
    "QPushButton { padding: 4px 10px; border: 1px solid palette(mid);"
    " border-radius: 6px; color: palette(text); background: palette(base); }"
    " QPushButton:hover { border-color: #4CAF50; }"
)


if HAS_QT:

    class _QueueSignals(QObject):
        changed = pyqtSignal()

    _SIGNALS = _QueueSignals()

    def notify_action_queue_changed() -> None:
        _SIGNALS.changed.emit()

    def menu_queue_command(on_command, on_result):
        """``on_command`` with the menu's follow-up on its result; None when the menu has no queue."""
        if on_command is None:
            return None
        return lambda command, payload: on_result(on_command(command, payload))

    class QueueAddControl(QWidget):
        """A count box and "Add to queue" for the action ``record_for()`` names now."""

        def __init__(self, player_data: dict, on_command, record_for, parent=None):
            super().__init__(parent)
            self.setObjectName("queueAddControl")
            self._player_data = player_data
            self._on_command = on_command
            self._record_for = record_for
            self._record = None
            self._has_count = False
            layout = QHBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)
            self.count_box = QSpinBox()
            self.count_box.setObjectName("queueCountBox")
            self.count_box.setAccessibleName("How many to queue")
            # The owner set no limit on an entry's count, only on the entry total.
            self.count_box.setRange(0, 2_147_483_647)
            self.count_box.setGroupSeparatorShown(True)
            self.add_button = QPushButton("Add to queue")
            self.add_button.setObjectName("queueAddButton")
            self.add_button.setStyleSheet(
                _BUTTON_STYLE + f" QPushButton:disabled {{ color: {dim_text_css(self)}; }}"
            )
            self.add_button.clicked.connect(self._add)
            layout.addWidget(self.count_box)
            layout.addWidget(self.add_button)
            _SIGNALS.changed.connect(self.refresh)
            self.refresh()

        def refresh(self) -> None:
            record = self._record_for()
            view = queue_add_view_pure(self._player_data, record)
            if record != self._record:
                # A typed count belongs to the action it was typed for.
                self._record = record
                self.count_box.setValue(view["count"])
            self._has_count = view["has_count"]
            self.count_box.setVisible(view["has_count"])
            self.count_box.setSuffix(f" {view['unit']}")
            self.count_box.setToolTip(view["count_tooltip"])
            self.add_button.setToolTip(view["tooltip"])
            self.add_button.setEnabled(view["enabled"] and self._on_command is not None)

        def _add(self) -> None:
            count = self.count_box.value() if self._has_count else None
            self._on_command("add", {"action": self._record, "count": count})

    def surface_queue_control(player_data: dict, on_command, surface: str) -> QueueAddControl:
        """The control beside a skill panel's Start: it queues what that Start would run now."""
        return QueueAddControl(player_data, on_command, lambda: menu_action_record_pure(player_data, surface))

    def activity_queue_control(player_data: dict, on_command, activity_id) -> QueueAddControl:
        """The control on the Activities card that ``activity_id()`` names, empty when none is open."""
        return QueueAddControl(player_data, on_command, lambda: utility_action_record_pure(activity_id()))

    class ActionQueuePanel(QFrame):
        """The compact queue list: each entry's state and count, with Resume and Clear."""

        def __init__(self, player_data: dict, on_command, parent=None):
            super().__init__(parent)
            self.setObjectName("actionQueuePanel")
            self.setStyleSheet(
                "QFrame#actionQueuePanel { border: 1px solid palette(mid);"
                " border-radius: 8px; background: palette(base); }"
            )
            self._player_data = player_data
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 6, 10, 6)
            layout.setSpacing(2)
            header = QHBoxLayout()
            header.setSpacing(8)
            self._title = QLabel()
            self._title.setObjectName("actionQueueTitle")
            self._title.setStyleSheet("font-weight: 700; color: palette(text);")
            self._status = QLabel()
            self._status.setObjectName("actionQueueStatus")
            self._status.setStyleSheet(f"color: {dim_text_css(self._status)}; font-size: 11px;")
            self._resume = QPushButton("Resume queue")
            self._resume.setObjectName("actionQueueResume")
            self._clear = QPushButton("Clear queue")
            self._clear.setObjectName("actionQueueClear")
            for button, command in ((self._resume, "resume"), (self._clear, "clear")):
                button.setStyleSheet(_BUTTON_STYLE)
                button.setEnabled(on_command is not None)
                button.clicked.connect(lambda _=False, c=command: on_command(c, {}))
            header.addWidget(self._title)
            header.addWidget(self._status, 1)
            header.addWidget(self._resume)
            header.addWidget(self._clear)
            layout.addLayout(header)
            self._rows = [self._row(layout) for _ in range(MAX_QUEUE_ENTRIES)]
            _SIGNALS.changed.connect(self.refresh)
            self.refresh()

        def _row(self, layout) -> tuple:
            line = QWidget()
            line_layout = QHBoxLayout(line)
            line_layout.setContentsMargins(0, 0, 0, 0)
            state = QLabel()
            state.setObjectName("actionQueueRowState")
            state.setFixedWidth(state.fontMetrics().horizontalAdvance("Stopped") + 8)
            state.setStyleSheet(f"color: {dim_text_css(state)}; font-size: 11px;")
            text = QLabel()
            text.setObjectName("actionQueueRowText")
            text.setWordWrap(True)
            text.setStyleSheet("color: palette(text);")
            line_layout.addWidget(state)
            line_layout.addWidget(text, 1)
            layout.addWidget(line)
            return line, state, text

        def refresh(self) -> None:
            view = queue_panel_view_pure(self._player_data)
            self.setVisible(view["visible"])
            self._title.setText(view["title"])
            self._status.setText(view["status"])
            self._resume.setVisible(view["can_resume"])
            for position, (line, state, text) in enumerate(self._rows):
                shown = position < len(view["rows"])
                line.setVisible(shown)
                if shown:
                    state.setText(view["rows"][position]["state"])
                    text.setText(view["rows"][position]["text"])

else:

    def notify_action_queue_changed() -> None:
        pass
