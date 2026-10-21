"""Game speed and world-day rows, shared by the Settings tab and the pace dialog.

The rows render ``world_day_setting_view_pure``; whether the length is editable,
which number it shows and when the suggestion hint appears are decided there.
Strings marked ``<<COPY:...>>`` are written by the copy model (owner Q8); the
fixed texts come from owner decisions 2 and 8.
"""

from __future__ import annotations

from collections.abc import Callable

from ..core.study_volume import (
    WORLD_DAY_CARDS_CONFIG_KEY,
    WORLD_DAY_FOLLOW_CONFIG_KEY,
    suggested_world_day_cards,
    world_day_settings,
)
from ..logic.pace.onboarding import PaceSettings
from ..logic.pace.world_clock import DEFAULT_WORLD_DAY_CARDS, world_day_setting_view_pure
from ..logic_pure.logic_pure import sanitize_review_action_multiplier

try:
    from aqt.qt import (  # type: ignore
        QCheckBox,
        QHBoxLayout,
        QLabel,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    HAS_QT = True
except Exception:
    HAS_QT = False

_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY = "ankiscape_review_action_multiplier"

GAME_SPEED_TOOLTIP = "<<COPY:game_speed_tooltip>>"
GAME_SPEED_HELP = "<<COPY:game_speed_help>>"
CARDS_SUFFIX = "<<COPY:cards_suffix>>"
WORLD_DAY_SUGGESTION_HINT = "<<COPY:world_day_suggestion_hint|cards={cards}>>"


def stored_pace_settings(collection) -> tuple[PaceSettings, int]:
    """The pace the game plays and the suggested world-day length; x1 with no profile."""
    if collection is None:
        return PaceSettings(1, False, DEFAULT_WORLD_DAY_CARDS), DEFAULT_WORLD_DAY_CARDS
    speed = sanitize_review_action_multiplier(collection.get_config(_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY, 1))
    return PaceSettings(speed, *world_day_settings(collection)), suggested_world_day_cards(collection)


def write_pace_settings(collection, settings: PaceSettings) -> None:
    collection.set_config(_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY, settings.speed)
    collection.set_config(WORLD_DAY_FOLLOW_CONFIG_KEY, settings.follow_study_volume)
    collection.set_config(WORLD_DAY_CARDS_CONFIG_KEY, settings.world_day_cards)


if HAS_QT:

    class PaceSettingsRows(QWidget):
        """The speed row, the world-day row under it, and the suggestion hint."""

        def __init__(
            self,
            settings: PaceSettings,
            suggestion: int,
            *,
            on_change: Callable[[PaceSettings], None] | None = None,
            parent: QWidget | None = None,
        ) -> None:
            super().__init__(parent)
            self._suggestion = suggestion
            self._fixed_cards = settings.world_day_cards
            self._on_change = on_change
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(6)

            speed_label = QLabel("Game speed:")
            speed_label.setToolTip(GAME_SPEED_TOOLTIP)
            self.speed_spin = QSpinBox()
            self.speed_spin.setObjectName("settingsActionMultiplierSpin")
            self.speed_spin.setRange(1, 20)
            self.speed_spin.setSuffix("x")
            self.speed_spin.setValue(settings.speed)
            self.speed_spin.setToolTip(GAME_SPEED_TOOLTIP)
            self.speed_spin.setMaximumWidth(120)
            layout.addWidget(_row(speed_label, self.speed_spin))

            self.follow_toggle = QCheckBox("Follow my study volume")
            self.follow_toggle.setObjectName("settingsWorldDayFollowToggle")
            self.follow_toggle.setChecked(settings.follow_study_volume)
            self.cards_spin = QSpinBox()
            self.cards_spin.setObjectName("settingsWorldDayCardsSpin")
            self.cards_spin.setRange(100, 1_000)
            self.cards_spin.setSuffix(CARDS_SUFFIX)
            layout.addWidget(_row(self.follow_toggle, self.cards_spin))

            self.suggestion_hint = QLabel(WORLD_DAY_SUGGESTION_HINT.format(cards=suggestion))
            self.suggestion_hint.setObjectName("settingsWorldDaySuggestionHint")
            self.suggestion_hint.setWordWrap(True)
            layout.addWidget(self.suggestion_hint)
            self._render()

            self.speed_spin.valueChanged.connect(lambda _value: self._changed())
            self.follow_toggle.toggled.connect(lambda _checked: self._render_and_report())
            self.cards_spin.valueChanged.connect(lambda _value: self._changed())

        def settings(self) -> PaceSettings:
            return PaceSettings(self.speed_spin.value(), self.follow_toggle.isChecked(), self._fixed_cards)

        def _render(self) -> None:
            view = world_day_setting_view_pure(self.follow_toggle.isChecked(), self._fixed_cards, self._suggestion)
            self.cards_spin.blockSignals(True)
            self.cards_spin.setValue(view.cards_value)
            self.cards_spin.blockSignals(False)
            self.cards_spin.setEnabled(view.cards_editable)
            self.suggestion_hint.setVisible(view.cards_editable)
            # ui.py imports this module while it loads, so its helpers arrive late.
            from .ui import dim_text_css

            self.suggestion_hint.setStyleSheet(f"color: {dim_text_css(self.suggestion_hint)}; font-size: 11px;")

        def _render_and_report(self) -> None:
            self._render()
            self._report()

        def _changed(self) -> None:
            if self.cards_spin.isEnabled():
                self._fixed_cards = self.cards_spin.value()
            self._report()

        def _report(self) -> None:
            if self._on_change is not None:
                self._on_change(self.settings())


def _row(*widgets: QWidget) -> QWidget:
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(8)
    for widget in widgets:
        layout.addWidget(widget)
    layout.addStretch(1)
    return row


def pace_settings_section(collection) -> QWidget:
    """The Settings tab's pace rows; each change is saved at once and played from the next card."""
    settings, suggestion = stored_pace_settings(collection)
    section = QWidget()
    layout = QVBoxLayout(section)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addWidget(
        PaceSettingsRows(
            settings,
            suggestion,
            on_change=None if collection is None else (lambda chosen: write_pace_settings(collection, chosen)),
        )
    )
    speed_help = QLabel(GAME_SPEED_HELP)
    speed_help.setObjectName("settingsGameSpeedHelp")
    speed_help.setWordWrap(True)
    speed_help.setStyleSheet("color: palette(text); font-size: 11px;")
    layout.addWidget(speed_help)
    return section
