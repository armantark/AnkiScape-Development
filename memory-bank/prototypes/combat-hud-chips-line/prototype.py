"""PROTOTYPE ONLY (ruling 4.29.6): three ways to stop the review HUD combat
chips line ("Kills: N · Trains ...") clipping beside Bank run, applied to the
real ReviewHUD inside the real review strip.

Run from the repo root:
    .venv-qt/bin/python memory-bank/prototypes/combat-hud-chips-line/prototype.py
    (add --style aggressive, --no-slayer, --dark, or --capture to write the PNGs offscreen)
"""

from __future__ import annotations

import argparse
import os
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import qt_variant_switcher as sw  # noqa: E402

VARIANTS = {
    "A": "Wrap beside Bank run, Slayer up by the enemy",
    "B": "Bank run up by the enemy, full-width lines",
    "C": "Skill icons, full text in tooltip",
}
# Highest real kill count is player state, so a heavy grinder's four digits.
KILLS = 1386
SKILL_ICONS = {
    "Attack": "attack_icon.png",
    "Strength": "strength_icon.png",
    "Defence": "defense_icon.png",
    "Ranged": "ranged_icon.png",
    "Magic": "magic_icon.png",
    "Constitution": "constitution_icon.png",
}


def player_state(harness, style: str, slayer: bool) -> dict:
    player = harness._state()
    player.update(
        {
            "current_combat_target": "black_bear",
            "combat_action": "attack",
            "equipment": {"weapon": "Rune longsword"},
            "combat_attack_style": style,
            "combat_attack_style_type": "slash" if style == "aggressive" else "stab",
            "attack_level": 60,
            "strength_level": 60,
            "defense_level": 55,
            "constitution_level": 58,
            "prayer_level": 43,
            "summoning_level": 40,
            "combat_prayer_points": 370,
            "summoning_state": {"summoning_points_current": 40},
            "combat_lifepoints": 580,
            "combat_kill_counts": {"black_bear": KILLS},
            "slayer_assignment": (
                {"master_id": "turael_spria", "family_id": "bears", "initial_count": 17, "remaining": 4}
                if slayer
                else {}
            ),
        }
    )
    return player


def fresh_strip(harness) -> None:
    """Drop the strip singletons so the next update builds a pristine HUD."""
    ui = harness.ui
    for widget in (ui._REVIEW_STRIP, ui._REVIEW_CONTEXT_STRIP):
        if widget is not None:
            widget.hide()
            widget.deleteLater()
    for name in ("_REVIEW_HUD", "_REVIEW_STRIP", "_BANK_RUN_BUTTON", "_MAIN_MENU_BUTTON", "_REVIEW_CONTEXT_STRIP",
                 "_SHOOTING_STAR_NOTICE_BAND", "_DND_BADGE", "_FARMING_BADGE", "_STATUS_POPOVER",
                 "_STATUS_POPOVER_BADGE", "_FILL_DRAWER", "_EVENT_LOG_DRAWER"):
        setattr(ui, name, None)
    sw.pump()


def render(harness, player) -> None:
    ui = harness.ui
    ui.update_review_hud(player, "Combat")
    ui.update_review_bank_run_button(player, "combat", lambda: None)
    ui._REVIEW_HUD.show()
    sw.pump()


def _chips_column(hud):
    for index in range(hud._info_layout.count()):
        layout = hud._info_layout.itemAt(index).layout()
        if layout is not None and layout.indexOf(hud.action_column) >= 0:
            return layout.itemAt(0).layout()
    raise LookupError("bottom row not found")


def variant_a(hud, ui) -> None:
    """Chips wrap to two lines in place; Slayer moves up to the enemy line."""
    from aqt.qt import QHBoxLayout, Qt

    chips_column = _chips_column(hud)
    info = hud._info_layout
    at = info.indexOf(hud.target_lbl)
    info.removeWidget(hud.target_lbl)
    chips_column.removeWidget(hud.slayer_lbl)
    enemy_row = QHBoxLayout()
    enemy_row.setSpacing(6)
    enemy_row.addWidget(hud.target_lbl, 1)
    enemy_row.addWidget(hud.slayer_lbl, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    info.insertLayout(at, enemy_row)
    original = hud._set_combat_chips

    def chips(state, player_data):
        original(state, player_data)
        hud.chips_lbl.setWordWrap(True)
        hud._info_layout.setSpacing(2)

    hud._set_combat_chips = chips


def variant_b(hud, ui) -> None:
    """Bank run sits beside the enemy name and bar; the counts and the trained
    skills each get a full-width line underneath."""
    from aqt.qt import QGridLayout, Qt
    from ankiscape.ui.ui import slayer_assignment_progress_pure

    info = hud._info_layout
    at = info.indexOf(hud.target_lbl)
    info.removeWidget(hud.target_lbl)
    info.removeWidget(hud.enemy_progress)
    button = ui._BANK_RUN_BUTTON
    hud.action_column.removeWidget(button)
    enemy = QGridLayout()
    enemy.setContentsMargins(0, 0, 0, 0)
    enemy.setHorizontalSpacing(6)
    enemy.setVerticalSpacing(2)
    enemy.addWidget(hud.target_lbl, 0, 0)
    enemy.addWidget(hud.enemy_progress, 1, 0)
    enemy.addWidget(button, 0, 1, 2, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    info.insertLayout(at, enemy)
    original = hud._set_combat_chips

    def chips(state, player_data):
        original(state, player_data)
        if state["finisher_notice"]:
            return
        slayer = slayer_assignment_progress_pure(player_data)
        hud.chips_lbl.setText(f"Kills: {state['kills_total']}" + (f" · {slayer}" if slayer else ""))
        hud.slayer_lbl.setText("Trains " + " • ".join(state["trained_skills"]))
        hud.slayer_lbl.setVisible(True)
        hud._info_layout.setSpacing(2)

    hud._set_combat_chips = chips


def variant_c(hud, ui) -> None:
    """Same row, shorter form: the trained skills become their skill icons and
    the full sentence moves to the tooltip."""
    from ankiscape.ui.ui import current_dir

    original = hud._set_combat_chips

    def chips(state, player_data):
        original(state, player_data)
        if state["finisher_notice"]:
            hud.chips_lbl.setToolTip("")
            return
        full = hud.chips_lbl.text()
        icons = "".join(
            f'<img src="{os.path.join(current_dir, "icon", SKILL_ICONS[skill])}" width="12" height="12">&nbsp;'
            for skill in state["trained_skills"]
        )
        hud.chips_lbl.setText(f"Kills: {state['kills_total']} · Trains&nbsp;{icons}")
        hud.chips_lbl.setToolTip(full)

    hud._set_combat_chips = chips


def apply_variant(harness, player, key: str):
    fresh_strip(harness)
    render(harness, player)
    ui = harness.ui
    {"A": variant_a, "B": variant_b, "C": variant_c}[key](ui._REVIEW_HUD, ui)
    render(harness, player)
    return ui._REVIEW_HUD


def describe(hud) -> str:
    from aqt.qt import QLabel, QPushButton, Qt
    from tests.ui_flows.qt_text_fit import text_fit_defects

    rich = [label for label in hud.findChildren(QLabel) if label.textFormat() != Qt.TextFormat.PlainText and "<img" in label.text()]
    defects = [d for d in text_fit_defects(hud) if not any(label.text()[:20] in d for label in rich)]
    for label in rich:
        # The plain-text probe measures raw HTML; a rich label fits when Qt's own size hint does.
        if label.sizeHint().width() > label.width() or label.sizeHint().height() > label.height():
            defects.append(f"rich chips {label.sizeHint()} clipped in {label.size()}")
    lines = [f"HUD {hud.width()}x{hud.height()}"]
    widgets = [w for w in hud.findChildren(QLabel) + hud.findChildren(QPushButton) if w.text() and w.isVisibleTo(hud)]
    for widget in sorted(widgets, key=lambda w: (w.geometry().y(), w.geometry().x())):
        g = widget.geometry()
        text = widget.text() if "<img" not in widget.text() else f"[icons] tooltip={widget.toolTip()!r}"
        lines.append(f"  y={g.y():>3} x={g.x():>3} {g.width():>3}x{g.height():<3} {text!r}")
    lines.append("clipped or overlapping text: " + ("none" if not defects else "; ".join(defects)))
    return "\n".join(lines)


def make_harness():
    from tests import test_review_strip as strip_tests

    strip_tests.ReviewStripTest.setUpClass()
    harness = strip_tests.ReviewStripTest(methodName="runTest")
    harness.setUp()
    # On main the HUD builds its state without equipment data, so every weapon
    # reads as bare fists and "controlled" can never show its four skills. Feed
    # the real equipment table so the prototype carries the longest real chips.
    from ankiscape.data.equipment_data import EQUIPMENT_DATA

    unarmed = harness.ui.combat_hud_state_pure
    harness.ui.combat_hud_state_pure = lambda player_data: unarmed(player_data, equipment_data=EQUIPMENT_DATA)
    return harness


def capture() -> None:
    harness = make_harness()
    harness.parent.resize(900, 560)
    failures = []
    for theme in ("light", "dark"):
        sw.apply_theme(theme)
        for style in ("controlled", "aggressive"):
            for key in VARIANTS:
                player = player_state(harness, style, slayer=True)
                hud = apply_variant(harness, player, key)
                for size in ((900, 560), (1000, 700)):
                    harness.parent.resize(*size)
                    sw.pump()
                    state = describe(hud)
                    if not state.endswith("none"):
                        failures.append(f"{style}-{key}-{theme}-{size}")
                name = f"hud-{style}-{key}-{theme}.png"
                hud.grab().save(str(HERE / name))
                print(f"--- {name}\n{state}")
    print("FAILURES:", failures or "none")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--style", choices=("controlled", "aggressive"), default="controlled")
    parser.add_argument("--no-slayer", action="store_true", help="hide the Slayer assignment line")
    parser.add_argument("--dark", action="store_true", help="Fusion dark palette instead of the OS look")
    parser.add_argument("--capture", action="store_true", help="write every variant PNG offscreen and exit")
    args = parser.parse_args()
    sw.prepare_qt(args.capture)
    if args.capture:
        capture()
        return
    from aqt.qt import QApplication

    harness = make_harness()
    if args.dark:
        sw.apply_theme("dark")
    window = harness.parent
    window.setWindowTitle("PROTOTYPE 4.29.6 — review HUD combat chips")
    window.resize(900, 560)
    player = player_state(harness, args.style, slayer=not args.no_slayer)

    def _apply(key: str) -> str:
        return describe(apply_variant(harness, player, key))

    window._switcher = sw.make_switcher(VARIANTS, _apply, window)
    QApplication.instance().exec()


if __name__ == "__main__":
    main()
