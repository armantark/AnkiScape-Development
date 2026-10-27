"""The action queue in the main menu: "Add to queue" beside each Start, and the queue box.

Both draw what ``core.menu_action_queue`` decides. Any save change that the
review HUD shows also reaches them through ``notify_action_queue_changed``, so a
target picked in a list updates the count box, and an entry a review finished
updates the list, without each list knowing about the queue.
"""

from __future__ import annotations

from ..core.action_queue import MAX_QUEUE_ENTRIES
from ..core.menu_action_queue import (
    activity_started_by_add_pure,
    menu_action_record_pure,
    queue_add_view_pure,
    queue_panel_view_pure,
    queue_runs_surface_pure,
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
        QScrollArea,
        QSpinBox,
        Qt,
        QToolButton,
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
# Entry lines the queue box shows before it scrolls, so the lists above keep their height.
_VISIBLE_ROWS = 2


def _record_key(record) -> tuple:
    return tuple(sorted(record.items()))


if HAS_QT:

    class _QueueSignals(QObject):
        changed = pyqtSignal()

    _SIGNALS = _QueueSignals()

    def notify_action_queue_changed() -> None:
        _SIGNALS.changed.emit()

    class MenuQueue:
        """The menu's queue command and what the menu does around it.

        An add that starts an activity at once first asks to leave a running
        session, as Start does. A count the player added keeps its box after
        the panel rebuilds, and each result goes to the menu's follow-up.
        """

        def __init__(self, player_data: dict, current_skill, on_command, on_result, leave_running_activity):
            self._player_data = player_data
            self._current_skill = current_skill
            self._on_command = on_command
            self._on_result = on_result
            self._leave_running_activity = leave_running_activity
            self.typed: dict = {}

        def __call__(self, command: str, payload: dict) -> None:
            if command == "add":
                activity = activity_started_by_add_pure(self._player_data, self._current_skill(), payload["action"])
                if activity and not self._leave_running_activity(activity):
                    return
                if payload["count"] is not None:
                    self.typed[_record_key(payload["action"])] = payload["count"]
            self._on_result(self._on_command(command, payload))

    def menu_queue(player_data: dict, current_skill, on_command, on_result, leave_running_activity):
        """The menu's MenuQueue, which reads the running action from ``current_skill()``; None without a queue command."""
        if on_command is None:
            return None
        return MenuQueue(player_data, current_skill, on_command, on_result, leave_running_activity)

    class QueueAddControl(QWidget):
        """Where the entry's inputs come from, a count box and "Add to queue", for ``record_for()``."""

        def __init__(self, player_data: dict, queue, record_for, parent=None):
            super().__init__(parent)
            self.setObjectName("queueAddControl")
            self._player_data = player_data
            self._queue = queue
            self._record_for = record_for
            self._record = None
            self._has_count = False
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(2)
            # Its own full-width line, so a long "to be mined by entry 1" never squeezes the count box.
            self.materials = QLabel()
            self.materials.setObjectName("queueMaterials")
            self.materials.setWordWrap(True)
            self.materials.setStyleSheet(f"color: {dim_text_css(self.materials)};")
            controls = QHBoxLayout()
            controls.setSpacing(6)
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
            layout.addWidget(self.materials)
            controls.addStretch(1)
            controls.addWidget(self.count_box)
            controls.addWidget(self.add_button)
            layout.addLayout(controls)
            _SIGNALS.changed.connect(self.refresh)
            self.refresh()

        def refresh(self) -> None:
            record = self._record_for()
            view = queue_add_view_pure(self._player_data, record)
            if record != self._record:
                self._record = record
                typed = self._queue.typed if self._queue is not None else {}
                self.count_box.setValue(typed.get(_record_key(record), view["count"]))
            self._has_count = view["has_count"]
            self.materials.setText(view["materials"])
            self.materials.setVisible(bool(view["materials"]))
            self.count_box.setVisible(view["has_count"])
            self.count_box.setSuffix(f" {view['unit']}")
            self.count_box.setToolTip(view["count_tooltip"])
            self.add_button.setToolTip(view["tooltip"])
            self.add_button.setEnabled(view["enabled"] and self._queue is not None)

        def _add(self) -> None:
            count = self.count_box.value() if self._has_count else None
            self._queue("add", {"action": self._record, "count": count})

    def surface_queue_control(player_data: dict, queue, surface: str, picked) -> QueueAddControl:
        """The control under a skill panel's Start: it queues what that Start would run, or ``picked()``."""
        return QueueAddControl(player_data, queue, lambda: menu_action_record_pure(player_data, surface, picked()))

    def activity_queue_control(player_data: dict, queue, activity_id) -> QueueAddControl:
        """The control on the Activities card that ``activity_id()`` names, empty when none is open."""
        return QueueAddControl(player_data, queue, lambda: utility_action_record_pure(activity_id()))

    def held_by_queue(player_data: dict, held: dict, surface: str, apply, target) -> bool:
        """Hold a target picked while the queue runs this panel's action, for the queue controls only.

        True when held: the running entry keeps its target, and the panel's
        Start applies the pick through ``apply`` when the player presses it.
        """
        if not queue_runs_surface_pure(player_data, surface):
            held.pop(surface, None)
            return False
        held[surface] = (apply, target)
        notify_action_queue_changed()
        return True

    class ActionQueuePanel(QFrame):
        """The queue box: a title, what Stop and Clear do to it, and each entry's state and count.

        An empty queue folds into ``empty_line``, which the menu lays in its
        footer row, so the box costs the lists above no height until it holds
        an entry, yet the player still reads what an empty queue means.
        """

        def __init__(self, player_data: dict, queue, current_skill, parent=None):
            super().__init__(parent)
            self.setObjectName("actionQueuePanel")
            self.setStyleSheet(
                "QFrame#actionQueuePanel { border: 1px solid palette(mid);"
                " border-radius: 8px; background: palette(base); }"
            )
            self._player_data = player_data
            self._current_skill = current_skill
            self._queue = queue
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10, 3, 10, 3)
            layout.setSpacing(0)
            header = QHBoxLayout()
            header.setSpacing(8)
            self._title = QLabel()
            self._title.setObjectName("actionQueueTitle")
            self._title.setStyleSheet("font-weight: 700; color: palette(text);")
            self._resume = QPushButton("Resume queue")
            self._resume.setObjectName("actionQueueResume")
            self._clear = QPushButton("Clear queue")
            self._clear.setObjectName("actionQueueClear")
            self._clear.setToolTip(
                "Cancel the plan: remove every entry and stop the entry the queue is running."
                " Resume on the study screen offers it back. An action you started yourself keeps running."
            )
            for button, command in ((self._resume, "resume"), (self._clear, "clear")):
                # Slimmer than the Start-row buttons: the box's height comes out of the lists above it.
                button.setStyleSheet(_BUTTON_STYLE.replace("padding: 4px 10px", "padding: 2px 10px"))
                button.setEnabled(queue is not None)
                button.clicked.connect(lambda _=False, c=command: queue(c, {}))
            self._hint = QLabel()
            self._hint.setObjectName("actionQueueHint")
            self._hint.setWordWrap(True)
            self._hint.setStyleSheet(f"color: {dim_text_css(self._hint)}; font-size: 12px;")
            header.addWidget(self._title)
            header.addWidget(self._hint, 1)
            header.addWidget(self._resume)
            header.addWidget(self._clear)
            layout.addLayout(header)
            rows = QWidget()
            rows_layout = QVBoxLayout(rows)
            rows_layout.setContentsMargins(0, 0, 0, 0)
            rows_layout.setSpacing(0)
            self._rows = [self._row(rows_layout, position) for position in range(MAX_QUEUE_ENTRIES)]
            rows_layout.addStretch(1)
            self._scroll = QScrollArea()
            self._scroll.setObjectName("actionQueueRows")
            self._scroll.setWidgetResizable(True)
            self._scroll.setFrameShape(QFrame.Shape.NoFrame)
            self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self._scroll.setStyleSheet("QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; }")
            self._scroll.setWidget(rows)
            layout.addWidget(self._scroll)
            self.empty_line = QLabel()
            self.empty_line.setObjectName("actionQueueEmptyLine")
            self.empty_line.setWordWrap(True)
            self.empty_line.setStyleSheet(f"color: {dim_text_css(self.empty_line)}; font-size: 12px;")
            _SIGNALS.changed.connect(self.refresh)
            self.refresh()

        def _row(self, layout, position: int) -> tuple:
            line = QWidget()
            line.setObjectName("actionQueueRow")
            line_layout = QHBoxLayout(line)
            line_layout.setContentsMargins(0, 1, 0, 1)
            state = QLabel()
            state.setObjectName("actionQueueRowState")
            state.setFixedWidth(state.fontMetrics().horizontalAdvance("5. Stopped") + 16)
            text = QLabel()
            text.setObjectName("actionQueueRowText")
            text.setWordWrap(True)
            remove = QToolButton()
            remove.setObjectName("actionQueueRemove")
            remove.setText("✕")
            remove.setAutoRaise(True)
            remove.setToolTip(f"Remove entry {position + 1} from the queue.")
            remove.setAccessibleName(f"Remove entry {position + 1}")
            remove.setFixedSize(text.fontMetrics().lineSpacing(), text.fontMetrics().lineSpacing())
            remove.setEnabled(self._queue is not None)
            # The running line hides its button but keeps the space, so the counts stay in one column.
            policy = remove.sizePolicy()
            policy.setRetainSizeWhenHidden(True)
            remove.setSizePolicy(policy)
            remove.clicked.connect(lambda _=False: self._queue("remove", {"position": position}))
            line_layout.addWidget(state)
            line_layout.addWidget(text, 1)
            line_layout.addWidget(remove)
            layout.addWidget(line)
            return line, state, text, remove

        def refresh(self) -> None:
            view = queue_panel_view_pure(self._player_data, self._current_skill())
            self.setVisible(bool(view["rows"]))
            # The line keeps its footer slot while the box shows, so Help and Close stay put.
            self.empty_line.setText("" if view["rows"] else f"{view['title']}. {view['hint']}")
            self._title.setText(view["title"])
            self._hint.setText(view["hint"])
            self._resume.setText(view["resume_text"])
            self._resume.setVisible(bool(view["resume_text"]))
            for position, (line, state, text, remove) in enumerate(self._rows):
                line.setVisible(position < len(view["rows"]))
                if position < len(view["rows"]):
                    self._show_row(view["rows"][position], state, text, remove)
            # One text line plus the row's 1 px margins; a longer list scrolls inside the box.
            line_height = self._rows[0][2].fontMetrics().lineSpacing() + 2
            self._scroll.setFixedHeight(min(len(view["rows"]), _VISIBLE_ROWS) * line_height)
            current = next((position for position, row in enumerate(view["rows"]) if row["current"]), None)
            if current is not None:
                self._scroll.ensureWidgetVisible(self._rows[current][0])

        def _show_row(self, row: dict, state, text, remove) -> None:
            # The running entry reads in full text colour; the others are dimmed, never palette(mid).
            colour = "palette(text)" if row["current"] else dim_text_css(state)
            remove.setVisible(row["removable"])
            state.setText(f"{row['position']} {row['state']}")
            state.setStyleSheet(f"color: {colour}; font-size: 12px; font-weight: 600;")
            text.setText(row["text"])
            text.setStyleSheet(f"color: {colour}; font-weight: {600 if row['current'] else 400};")

else:

    def notify_action_queue_changed() -> None:
        pass
