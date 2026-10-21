"""Game speed and world-day rows in Settings, and the pace dialog that reuses them.

The rows render ``world_day_setting_view_pure``; whether the length is editable,
which number it shows and when the suggestion hint appears are decided there.
The copy model wrote the texts below (owner Q8); "Game speed", "Follow my study
volume" and "Keep my current settings" come from owner decisions 2 and 8.
"""

from __future__ import annotations

from collections.abc import Callable

from ..core.study_volume import (
    WORLD_DAY_CARDS_CONFIG_KEY,
    WORLD_DAY_FOLLOW_CONFIG_KEY,
    suggested_world_day_cards,
    world_day_settings,
)
from ..logic.pace.onboarding import (
    PaceOnboardingPlan,
    PaceSettings,
    pace_onboarding_plan_pure,
    pace_text_fields_pure,
)
from ..logic.pace.world_clock import DEFAULT_WORLD_DAY_CARDS, world_day_setting_view_pure
from ..logic_pure.logic_pure import sanitize_review_action_multiplier

try:
    from aqt import mw  # type: ignore
    from ..core.storage import saved_player_record  # reads the profile through aqt
    from aqt.qt import (  # type: ignore
        QCheckBox,
        QDialog,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QSpinBox,
        QVBoxLayout,
        QWidget,
    )

    HAS_QT = True
except Exception:
    mw = None
    HAS_QT = False

_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY = "ankiscape_review_action_multiplier"
# Read once, so an existing player is shown the speed the save was played at.
_LEGACY_XP_MULTIPLIER_CONFIG_KEY = "ankiscape_xp_multiplier"
_PACE_DIALOG_ANSWERED_CONFIG_KEY = "ankiscape_pace_dialog_answered"

GAME_SPEED_TOOLTIP = (
    "One card buys 3.6 seconds of play per point of game speed (1x = 3.6 seconds, 10x = 36 seconds,"
    " 20x = 72 seconds).\n10x is recommended. A speed change applies from the next card."
)
GAME_SPEED_HELP = "Speed sets how much game time each card buys; a world day is a number of cards."
CARDS_SUFFIX = " cards"
WORLD_DAY_SUGGESTION_HINT = "Suggested: {cards} cards."
PACE_DIALOG_TITLE = "Pick your game speed and world day"
# A new player has no earlier pace; an existing save keeps its pace unless the new one is applied.
PACE_DIALOG_REASON_NEW = (
    "We recommend 10x with the world day following your study volume. Keep my current settings gives 1x"
    " and a fixed 240-card day. Closing this window applies the recommendation. Change it in Settings."
)
PACE_DIALOG_REASON_EXISTING = (
    "The recommended speed changed from 1x to 10x, so the game asks once. Keep my current settings and"
    " closing the window keep your pace. Recommended: 10x with the world day following your study volume."
)
PACE_DIALOG_CURRENT_LINE = (
    "Your current pace: {speed}x, {cards} cards per world day, {hours} h ({minutes} min) of play."
    " One Fish Flingers game takes {fish_flingers_cards} cards."
)
PACE_DIALOG_HOURS_LINE = (
    "Selected settings: {speed}x, {cards} cards per world day, {hours} h ({minutes} min) of play."
    " One Fish Flingers game takes {fish_flingers_cards} cards."
)
PACE_DIALOG_APPLY = "Apply these settings"


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


def run_pace_onboarding() -> None:
    """Profile-load step: each profile answers the pace question once (decision 10).

    The dialog is modal, so no card is answered at a speed the player has not
    confirmed. Every answer writes all three settings, the current ones included.
    """
    collection = getattr(mw, "col", None)
    if collection is None or collection.get_config(_PACE_DIALOG_ANSWERED_CONFIG_KEY, None) is not None:
        return
    follow_study_volume, world_day_cards = world_day_settings(collection)
    suggestion = suggested_world_day_cards(collection)
    plan = pace_onboarding_plan_pure(
        # Nothing before this step in the profile-load hooks writes the save.
        existing_player=bool(saved_player_record(collection)),
        speed=collection.get_config(_REVIEW_ACTION_MULTIPLIER_CONFIG_KEY, None),
        legacy_speed=collection.get_config(_LEGACY_XP_MULTIPLIER_CONFIG_KEY, None),
        follow_study_volume=follow_study_volume,
        world_day_cards=world_day_cards,
        suggestion=suggestion,
    )
    dialog = PaceDialog(plan, suggestion, parent=mw)
    dialog.exec()
    write_pace_settings(collection, dialog.choice())
    collection.set_config(_PACE_DIALOG_ANSWERED_CONFIG_KEY, True)


if HAS_QT:

    class PaceDialog(QDialog):
        """Shows the current pace and the recommended one; the plan decides what each answer writes."""

        def __init__(self, plan: PaceOnboardingPlan, suggestion: int, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            self.setObjectName("paceDialog")
            self.setWindowTitle(PACE_DIALOG_TITLE)
            self.setMinimumWidth(460)
            self._suggestion = suggestion
            # Closing with X or Esc is the answer until a button is pressed.
            self._choice = plan.on_close
            layout = QVBoxLayout(self)
            layout.setContentsMargins(16, 16, 16, 16)
            layout.setSpacing(12)

            reason = _wrapped_label(
                PACE_DIALOG_REASON_EXISTING if plan.existing_player else PACE_DIALOG_REASON_NEW, "paceDialogReason"
            )
            current = _wrapped_label(
                PACE_DIALOG_CURRENT_LINE.format(**pace_text_fields_pure(plan.current, suggestion)),
                "paceDialogCurrentLine",
            )
            self.rows = PaceSettingsRows(plan.recommended, suggestion, on_change=self._show_hours)
            self.hours_line = _wrapped_label("", "paceDialogHoursLine")
            self._show_hours(self.rows.settings())

            keep = QPushButton("Keep my current settings")
            keep.setObjectName("paceDialogKeepButton")
            keep.clicked.connect(lambda _checked=False: self._choose(plan.current))
            apply = QPushButton(PACE_DIALOG_APPLY)
            apply.setObjectName("paceDialogApplyButton")
            apply.setDefault(True)
            apply.clicked.connect(lambda _checked=False: self._choose(self.rows.settings()))
            buttons = QHBoxLayout()
            buttons.addStretch(1)
            buttons.addWidget(keep)
            buttons.addWidget(apply)

            for widget in (reason, current, self.rows, self.hours_line):
                layout.addWidget(widget)
            # A taller window keeps the text together above the buttons.
            layout.addStretch(1)
            layout.addLayout(buttons)

        def choice(self) -> PaceSettings:
            return self._choice

        def _show_hours(self, settings: PaceSettings) -> None:
            self.hours_line.setText(PACE_DIALOG_HOURS_LINE.format(**pace_text_fields_pure(settings, self._suggestion)))
            # An open window does not grow by itself when the suggestion hint
            # appears or the hours line wraps again, so the rows would be squeezed.
            if self.isVisible():
                self.layout().activate()
                self.resize(self.width(), max(self.height(), self.heightForWidth(self.width())))

        def _choose(self, settings: PaceSettings) -> None:
            self._choice = settings
            self.accept()

    def _wrapped_label(text: str, object_name: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName(object_name)
        label.setWordWrap(True)
        return label
