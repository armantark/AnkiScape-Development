"""The action queue in the main menu: "Add to queue" beside each Start, and the queue box.

Both draw what ``core.menu_action_queue`` decides. Any save change that the
review HUD shows also reaches them through ``notify_action_queue_changed``, so a
target picked in a list updates the count box, and an entry a review finished
updates the list, without each list knowing about the queue.
"""

from __future__ import annotations

from ..core.action_queue import MAX_QUEUE_ENTRIES, action_queue_pure, queue_notice_view_pure
from ..core.menu_action_queue import (
    activity_started_by_add_pure,
    activity_started_by_move_pure,
    menu_action_record_pure,
    queue_add_view_pure,
    queue_panel_view_pure,
    queue_runs_surface_pure,
    utility_action_record_pure,
)
from .ui_palette import dim_text_css

try:
    from aqt import mw  # type: ignore
    from aqt.qt import (  # type: ignore
        QEasingCurve,
        QFrame,
        QGridLayout,
        QHBoxLayout,
        QLabel,
        QObject,
        QPainter,
        QPalette,
        QPushButton,
        QRect,
        QSpinBox,
        Qt,
        QTimer,
        QToolButton,
        QVariantAnimation,
        QVBoxLayout,
        QWidget,
        pyqtSignal,
    )

    HAS_QT = True
except Exception:  # pragma: no cover - non-Qt environment keeps the module importable
    mw = None
    HAS_QT = False

_BUTTON_STYLE = (
    "QPushButton { padding: 4px 10px; border: 1px solid palette(mid);"
    " border-radius: 6px; color: palette(text); background: palette(base); }"
    " QPushButton:hover { border-color: #4CAF50; }"
)
# How long an add shows on its button and its new entry line (owner, Pass 18: about 1.5 s).
_CONFIRM_MS = 1500
_MOVE_STYLE = _BUTTON_STYLE.replace("padding: 4px 10px", "padding: 0 6px")
# Anki's profile config keeps the fold across menus, as it keeps the tool belt's.
_FOLDED_CONFIG_KEY = "ankiscape_action_queue_folded"
# The band reaches this far past a line's text; the box's side margins give the room back.
_BAND_PAD = 4


def _record_key(record) -> tuple:
    return tuple(sorted(record.items()))


def _without_widow(text: str) -> str:
    """Glue the last two words, so a wrapped line never ends on one word alone."""
    head, _space, tail = text.rpartition(" ")
    return f"{head}\u00a0{tail}" if head else text


if HAS_QT:

    class _QueueSignals(QObject):
        changed = pyqtSignal()

    _SIGNALS = _QueueSignals()

    def notify_action_queue_changed() -> None:
        _SIGNALS.changed.emit()

    class MenuQueue(QObject):
        """The menu's queue command and what the menu does around it.

        An add or move that starts an activity at once first asks to leave a
        running session, as Start does. A count the player added keeps its box after
        the panel rebuilds, and each result goes to the menu's follow-up. For
        ``_CONFIRM_MS`` after an add, ``confirmed`` names the action and the
        entry total its Add button confirms, also on a control the follow-up
        rebuilt, and ``added`` tells the queue box which line is new.
        """

        added = pyqtSignal(int)

        def __init__(self, player_data: dict, current_skill, on_command, on_result, leave_running_activity):
            super().__init__()
            self._player_data = player_data
            self._current_skill = current_skill
            self._on_command = on_command
            self._on_result = on_result
            self._leave_running_activity = leave_running_activity
            self.typed: dict = {}
            self.confirmed: tuple | None = None
            self._confirm_timer = QTimer(self)
            self._confirm_timer.setSingleShot(True)
            self._confirm_timer.setInterval(_CONFIRM_MS)
            self._confirm_timer.timeout.connect(self._end_confirmation)

        def __call__(self, command: str, payload: dict) -> None:
            if command == "move":
                activity = activity_started_by_move_pure(
                    self._player_data, self._current_skill(), payload["position"], payload["new_index"]
                )
                if activity and not self._leave_running_activity(activity):
                    return
            if command == "add":
                activity = activity_started_by_add_pure(
                    self._player_data, self._current_skill(), payload["action"], payload["count"]
                )
                if activity and not self._leave_running_activity(activity):
                    return
                if payload["count"] is not None:
                    self.typed[_record_key(payload["action"])] = payload["count"]
            result = self._on_command(command, payload)
            if command == "add" and result["ok"]:
                self._confirm(payload["action"])
            self._on_result(result)

        def _confirm(self, action) -> None:
            entries = len(action_queue_pure(self._player_data)["entries"])
            # An entry that could not start at once already left the queue, so there is no line to confirm.
            if not entries:
                return
            self.confirmed = (_record_key(action), entries)
            self._confirm_timer.start()
            notify_action_queue_changed()
            self.added.emit(entries - 1)

        def confirmation(self, record) -> str:
            """What the Add button for ``record`` reads while it confirms an add; empty otherwise."""
            if self.confirmed is None or self.confirmed[0] != _record_key(record):
                return ""
            return f"Added ✓ ({self.confirmed[1]} of {MAX_QUEUE_ENTRIES})"

        def _end_confirmation(self) -> None:
            self.confirmed = None
            notify_action_queue_changed()

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
            # Its own full-width line, so a long "Iron ore: 37 in Bank, 28 from entry 1" never squeezes the count box.
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
            self.add_button = QPushButton()
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
            self.materials.setText(_without_widow(view["materials"]))
            self.materials.setVisible(bool(view["materials"]))
            self.count_box.setVisible(view["has_count"])
            self.count_box.setSuffix(f" {view['unit']}")
            self.count_box.setToolTip(view["count_tooltip"])
            self.add_button.setToolTip(view["tooltip"])
            self.add_button.setEnabled(view["enabled"] and self._queue is not None)
            confirmation = self._queue.confirmation(record) if self._queue is not None else ""
            self.add_button.setText(confirmation or "Add to queue")

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

    def _queue_box_folded() -> bool:
        col = getattr(mw, "col", None)
        return bool(col.get_config(_FOLDED_CONFIG_KEY, False)) if col else False

    def _set_queue_box_folded(folded: bool) -> None:
        col = getattr(mw, "col", None)
        if col:
            col.set_config(_FOLDED_CONFIG_KEY, folded)

    class _EntryLines(QWidget):
        """The entry lines; ``flash`` lays a band of the theme's accent across one line that fades out."""

        def __init__(self):
            super().__init__()
            self.setObjectName("actionQueueRows")
            self._band: QWidget | None = None
            self.fade = QVariantAnimation(self)
            self.fade.setDuration(_CONFIRM_MS)
            self.fade.setStartValue(0.45)
            self.fade.setEndValue(0.0)
            # Stays strong at first, so the eye finds the line, then fades out.
            self.fade.setEasingCurve(QEasingCurve.Type.InQuad)
            self.fade.valueChanged.connect(self.update)

        def flash(self, line: QWidget) -> None:
            self._band = line
            self.fade.stop()
            self.fade.start()

        def paintEvent(self, event) -> None:
            if self._band is None or self.fade.state() != QVariantAnimation.State.Running:
                return
            line = self._band.geometry()
            colour = self.palette().color(QPalette.ColorRole.Highlight)
            colour.setAlphaF(self.fade.currentValue())
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(colour)
            painter.drawRoundedRect(QRect(0, line.top(), self.width(), line.height()), 4, 4)

    class ActionQueuePanel(QFrame):
        """The queue box: a title that folds it, and each entry's state and count.

        The box is as tall as its entries, so every entry shows and the tab
        page above gives up the height. An empty queue folds into
        ``empty_line``, which the menu lays in its footer row, so the box costs
        the lists above no height until it holds an entry.
        """

        def __init__(self, player_data: dict, queue, parent=None):
            super().__init__(parent)
            self.setObjectName("actionQueuePanel")
            self.setStyleSheet(
                "QFrame#actionQueuePanel { border: 1px solid palette(mid);"
                " border-radius: 8px; background: palette(base); }"
            )
            self._player_data = player_data
            self._queue = queue
            layout = QVBoxLayout(self)
            layout.setContentsMargins(10 - _BAND_PAD, 3, 10 - _BAND_PAD, 3)
            layout.setSpacing(0)
            header = QHBoxLayout()
            header.setContentsMargins(_BAND_PAD, 0, _BAND_PAD, 0)
            header.setSpacing(8)
            self._title = QPushButton()
            self._title.setObjectName("actionQueueTitle")
            self._title.setCheckable(True)
            self._title.setStyleSheet(
                "QPushButton { font-weight: 700; color: palette(text); text-align: left;"
                " border: none; padding: 0; background: transparent; }"
            )
            self._resume = QPushButton("Resume queue")
            self._resume.setObjectName("actionQueueResume")
            self._clear = QPushButton("Clear queue")
            self._clear.setObjectName("actionQueueClear")
            self._clear.setToolTip("Also stops an action you started yourself.")
            for button, command in ((self._resume, "resume"), (self._clear, "clear")):
                # Slimmer than the Start-row buttons: the box's height comes out of the lists above it.
                button.setStyleSheet(_BUTTON_STYLE.replace("padding: 4px 10px", "padding: 2px 10px"))
                button.setEnabled(queue is not None)
                button.clicked.connect(lambda _=False, c=command: queue(c, {}))
            header.addWidget(self._title)
            header.addStretch(1)
            header.addWidget(self._resume)
            header.addWidget(self._clear)
            layout.addLayout(header)
            self._lines = _EntryLines()
            # One grid, so each column is as wide as its widest entry and the counts line up.
            rows_layout = QGridLayout(self._lines)
            rows_layout.setContentsMargins(_BAND_PAD, 0, _BAND_PAD, 0)
            rows_layout.setHorizontalSpacing(4)
            rows_layout.setVerticalSpacing(2)
            rows_layout.setColumnStretch(1, 1)
            self._rows = [self._row(rows_layout, position) for position in range(MAX_QUEUE_ENTRIES)]
            layout.addWidget(self._lines)
            self.empty_line = QLabel()
            self.empty_line.setObjectName("actionQueueEmptyLine")
            self.empty_line.setWordWrap(True)
            self.empty_line.setStyleSheet(f"color: {dim_text_css(self.empty_line)}; font-size: 12px;")
            self._title.setChecked(not _queue_box_folded())
            self._title.toggled.connect(self._fold)
            if queue is not None:
                queue.added.connect(self._flash)
            _SIGNALS.changed.connect(self.refresh)
            self.refresh()

        def _row(self, layout, position: int) -> tuple:
            state = QLabel()
            state.setObjectName("actionQueueRowState")
            text = QLabel()
            text.setObjectName("actionQueueRowText")
            text.setWordWrap(True)
            remove = QToolButton()
            remove.setObjectName("actionQueueRemove")
            remove.setText("✕")
            remove.setAutoRaise(True)
            remove.setToolTip("Remove")
            remove.setAccessibleName(f"Remove entry {position + 1}")
            remove.setFixedSize(text.fontMetrics().lineSpacing(), text.fontMetrics().lineSpacing())
            remove.setEnabled(self._queue is not None)
            remove.clicked.connect(lambda _=False: self._queue("remove", {"position": position}))
            up = self._move_button("Up", position, position - 1)
            down = self._move_button("Down", position, position + 1)
            state.setContentsMargins(0, 1, 12, 1)
            text.setContentsMargins(0, 1, 0, 1)
            for column, widget in enumerate((state, text, up, down, remove)):
                layout.addWidget(widget, position, column)
            return state, text, up, down, remove

        def _move_button(self, label: str, position: int, new_index: int):
            button = QPushButton(label)
            button.setObjectName(f"actionQueueMove{label}")
            button.setAccessibleName(f"Move entry {position + 1} {label.lower()}")
            button.setStyleSheet(_MOVE_STYLE + f" QPushButton:disabled {{ color: {dim_text_css(self)}; }}")
            button.clicked.connect(lambda _=False: self._queue("move", {"position": position, "new_index": new_index}))
            return button

        def _flash(self, position: int) -> None:
            self._lines.flash(self._rows[position][1])

        def _fold(self, unfolded: bool) -> None:
            _set_queue_box_folded(not unfolded)
            self.refresh()

        def refresh(self) -> None:
            view = queue_panel_view_pure(self._player_data)
            self.setVisible(bool(view["rows"]))
            # The line keeps its footer slot while the box shows, so Help and Close stay put.
            self.empty_line.setText("" if view["rows"] else view["title"])
            self._title.setText(f"{'▾' if self._title.isChecked() else '▸'} {view['title']}")
            self._resume.setText(view["resume_text"])
            self._resume.setVisible(bool(view["resume_text"]))
            self._lines.setVisible(self._title.isChecked())
            for position, (state, text, up, down, remove) in enumerate(self._rows):
                row = view["rows"][position] if position < len(view["rows"]) else None
                for widget in (state, text, up, down):
                    widget.setVisible(row is not None)
                remove.setVisible(row is not None and row["removable"])
                if row is not None:
                    up.setEnabled(row["can_move_up"] and self._queue is not None)
                    down.setEnabled(row["can_move_down"] and self._queue is not None)
                    self._show_row(row, state, text)

        def _show_row(self, row: dict, state, text) -> None:
            # The running entry reads in full text colour; the others are dimmed, never palette(mid).
            colour = "palette(text)" if row["current"] else dim_text_css(state)
            state.setText(f"{row['position']} {row['state']}")
            state.setStyleSheet(f"color: {colour}; font-size: 12px; font-weight: 600;")
            text.setText(row["text"])
            text.setStyleSheet(f"color: {colour}; font-weight: {600 if row['current'] else 400};")

else:

    def notify_action_queue_changed() -> None:
        pass
