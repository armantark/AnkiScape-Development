"""The Elder Kiln's egg-hatching review exercise.

Every control sends one command to the owning quest Answer and repaints from the
observation it returns; no control sets an outcome itself. Closing, Escape and
the window's close button all pause the attempt for that Answer to keep.
"""

from aqt.qt import (  # type: ignore
    QColor, QDialog, QGridLayout, QHBoxLayout, QLabel, QPainter, QPen, QProgressBar, QPushButton,
    QRectF, QSizePolicy, Qt, QVBoxLayout, QWidget,
)

from ..data.quest.elder_kiln import (
    AFTER_OFFER_COPY, EXERCISE_COPY, FAILURE_COPY, HELPER_NAMES, INSTRUCTIONS_COPY, REQUEST_COPY,
    SPELL_IDS, SPELL_LABELS, SUCCESS_COPY,
)
from .ui import dim_text_css

WINDOW_TITLE = "The Elder Kiln — egg-hatching review exercise"
_EVENT_TEXT = {
    "activated": "The hatching percentage has started to rise.",
    "left_band": "The temperature has left the markers.",
    "marker": "The markers have moved.",
    "retried": "A fresh attempt has begun.",
}
# The gauge's fire colour only fills the bar; all text uses palette roles.
_HEAT_FILL = QColor(214, 96, 40, 170)


def _event_line(event):
    kind = event[0]
    if kind == "helper_impact":
        return f"{event[1]}’s fire spell warmed the egg."
    if kind == "helper_skip":
        return f"{event[1]} held the spell: the egg was warm enough."
    return _EVENT_TEXT.get(kind, "")


class HeatGauge(QWidget):
    """A thermometer: the band between the two markers and the egg's current heat."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("elderKilnGauge")
        self.setMinimumHeight(36)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._reading = (0, 0, 100, (0, 100))

    def set_reading(self, heat, low, high, bounds):
        self._reading = (heat, low, high, bounds)
        self.update()

    def _x(self, track, value):
        start, end = self._reading[3]
        return track.left() + track.width() * (value - start) / max(1, end - start)

    def paintEvent(self, _event):
        heat, low, high, _bounds = self._reading
        palette = self.palette()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        track = QRectF(6, 8, self.width() - 12, self.height() - 16)
        painter.setPen(QPen(palette.color(palette.ColorRole.Mid), 1))
        painter.setBrush(palette.color(palette.ColorRole.Base))
        painter.drawRoundedRect(track, 4, 4)
        band = palette.color(palette.ColorRole.Highlight)
        band.setAlpha(90)
        painter.fillRect(QRectF(self._x(track, low), track.top(), self._x(track, high) - self._x(track, low), track.height()), band)
        painter.fillRect(QRectF(track.left(), track.top() + 6, self._x(track, heat) - track.left(), track.height() - 12), _HEAT_FILL)
        painter.setPen(QPen(palette.color(palette.ColorRole.Text), 2))
        for marker in (low, high):
            painter.drawLine(int(self._x(track, marker)), 2, int(self._x(track, marker)), self.height() - 2)
        painter.setPen(QPen(palette.color(palette.ColorRole.Text), 4))
        painter.drawLine(int(self._x(track, heat)), 6, int(self._x(track, heat)), self.height() - 6)
        painter.end()


def _wrapped_label(object_name, text=""):
    label = QLabel(text)
    label.setObjectName(object_name)
    label.setWordWrap(True)
    label.setStyleSheet("color: palette(text);")
    return label


class ElderKilnHatchingDialog(QDialog):
    def __init__(self, command, observation, parent=None):
        super().__init__(parent if isinstance(parent, QWidget) else None)
        self._command = command
        self.setObjectName("elderKilnHatchingDialog")
        self.setWindowTitle(WINDOW_TITLE)
        self.setModal(True)
        self.setMinimumWidth(600)
        self.resize(720, 540)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        self._build_story(layout)
        self._build_gauges(layout)
        self._build_spells(layout)
        self._build_actions(layout)
        self.render_observation(observation)

    def _build_story(self, layout):
        self.story = _wrapped_label("elderKilnStory")
        self.offer_button = QPushButton("Offer to help")
        self.offer_button.setObjectName("elderKilnOffer")
        self.offer_button.clicked.connect(lambda: self._send("offer"))
        self.instructions = _wrapped_label("elderKilnInstructions", INSTRUCTIONS_COPY)
        self.exercise = _wrapped_label("elderKilnExercise", EXERCISE_COPY)
        self.exercise.setStyleSheet(f"color: {dim_text_css(self.exercise)};")
        story_row = QHBoxLayout()
        story_row.addWidget(self.story, 1)
        story_row.addWidget(self.offer_button, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(story_row)
        layout.addWidget(self.instructions)
        layout.addWidget(self.exercise)

    def _build_gauges(self, layout):
        self.gauge = HeatGauge()
        self.heat_label = _wrapped_label("elderKilnHeat")
        self.progress = QProgressBar()
        self.progress.setObjectName("elderKilnProgress")
        self.progress.setRange(0, 100)
        # Native macOS bars never draw their text, so the percentage is a label.
        self.progress.setTextVisible(False)
        self.progress_label = _wrapped_label("elderKilnProgressText")
        self.helper_labels = [_wrapped_label(f"elderKilnHelper_{index}") for index in range(len(HELPER_NAMES))]
        self.event_label = _wrapped_label("elderKilnEvents")
        helpers = QHBoxLayout()
        for label in self.helper_labels:
            helpers.addWidget(label, 1)
        layout.addWidget(self.gauge)
        layout.addWidget(self.heat_label)
        progress_row = QHBoxLayout()
        progress_row.addWidget(self.progress_label)
        progress_row.addWidget(self.progress, 1)
        layout.addLayout(progress_row)
        layout.addLayout(helpers)
        layout.addWidget(self.event_label)

    def _build_spells(self, layout):
        grid = QGridLayout()
        self.spell_buttons = []
        for index, (spell_id, label) in enumerate(zip(SPELL_IDS, SPELL_LABELS)):
            button = QPushButton(label)
            button.setObjectName(f"elderKilnSpell_{spell_id}")
            button.clicked.connect(lambda _checked=False, spell=spell_id: self._send(f"cast:{spell}"))
            grid.addWidget(button, index // 3, index % 3)
            self.spell_buttons.append(button)
        layout.addLayout(grid)

    def _build_actions(self, layout):
        waits = QHBoxLayout()
        self.wait_step_button = self._action_button(waits, "Wait one step", "elderKilnWaitStep", "wait_step")
        self.wait_change_button = self._action_button(waits, "Wait until a change", "elderKilnWaitChange", "wait_change")
        self.retry_button = self._action_button(waits, "Retry", "elderKilnRetry", "retry")
        waits.addStretch(1)
        layout.addLayout(waits)
        layout.addStretch(1)
        closing = QHBoxLayout()
        closing.addStretch(1)
        self.close_button = QPushButton("Close")
        self.close_button.setObjectName("elderKilnClose")
        self.close_button.clicked.connect(self.reject)
        closing.addWidget(self.close_button)
        layout.addLayout(closing)

    def _action_button(self, row, text, object_name, command):
        button = QPushButton(text)
        button.setObjectName(object_name)
        button.clicked.connect(lambda: self._send(command))
        row.addWidget(button)
        return button

    def _send(self, command):
        self.render_observation(self._command(command))

    def _story_text(self, phase):
        return {
            "request": REQUEST_COPY,
            "failed": FAILURE_COPY,
            "hatched": SUCCESS_COPY,
        }.get(phase, AFTER_OFFER_COPY)

    def render_observation(self, observation):
        phase = observation["phase"]
        self.story.setText(self._story_text(phase))
        self.gauge.set_reading(observation["heat"], observation["band_low"], observation["band_high"], observation["heat_bounds"])
        place = "between" if observation["in_band"] else "outside"
        self.heat_label.setText(
            f"Heat {observation['heat']}, {place} the markers at {observation['band_low']} and {observation['band_high']}."
        )
        self.progress.setValue(observation["progress"])
        self.progress_label.setText(f"Hatching {observation['progress']}%")
        self.progress.setAccessibleName(self.progress_label.text())
        self._render_helpers(observation["warnings"])
        lines = tuple(dict.fromkeys(line for line in map(_event_line, observation["events"]) if line))
        self.event_label.setText(" ".join(lines))
        self.offer_button.setVisible(observation["can_offer"])
        for button in (*self.spell_buttons, self.wait_step_button, self.wait_change_button):
            button.setEnabled(observation["can_play"])
        self.retry_button.setEnabled(observation["can_retry"])

    def _render_helpers(self, warnings):
        for name, label in zip(HELPER_NAMES, self.helper_labels):
            warning = next((text for text in warnings if text.startswith(f"{name}:")), "")
            label.setText(warning or f"{name} is watching the egg.")
            weight = "font-weight: 700; color: palette(text);" if warning else f"color: {dim_text_css(label)};"
            label.setStyleSheet(weight)
