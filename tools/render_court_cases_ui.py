#!/usr/bin/env python3
"""Render idle and Advanced-trial Court Cases cards for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

from court_cases_logic import (
    apply_court_case_review_pure,
    apply_court_cases_command_pure,
)
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _utility_row
from tools.render_fishing_trawler_ui import _dark_palette


def _player() -> dict:
    player = _make_player_data()
    player.update(
        {
            "current_utility": "bankstanding",
            "activity_session": {"active_id": ""},
            "attack_level": 65,
            "defense_level": 65,
        }
    )
    player["quests"]["kings_ransom"] = {"completed": True}
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_court_cases_command_pure(
            player, action_id, payload
        )
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(player, on_court_cases_command=command)
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "court_cases")
    tree.setCurrentItem(row)
    tree.itemActivated.emit(row, 0)
    dialog.show()
    dialog.resize(width, height)
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    for _ in range(8):
        app.processEvents()
    return dialog


def render(output_dir: Path, *, width: int = 1200, height: int = 760) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_court_cases_detail_is_compact_and_advanced_discloses_one_choice"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    idle = _show_card(case, _player(), width, height)
    idle_path = output_dir / "court-cases-idle.png"
    if not idle.grab().save(str(idle_path)):
        raise RuntimeError(f"Could not save {idle_path}")
    idle.close()

    advanced = _player()
    advanced, ok, info = apply_court_cases_command_pure(
        advanced,
        "enter",
        {"role": "defence", "automation_mode": "advanced"},
    )
    if not ok:
        raise RuntimeError(str(info))
    for _ in range(4):
        advanced, _result = apply_court_case_review_pure(advanced)
    trial = _show_card(case, advanced, width, height)
    trial_path = output_dir / "court-cases-advanced-trial.png"
    if not trial.grab().save(str(trial_path)):
        raise RuntimeError(f"Could not save {trial_path}")
    trial.close()

    case.tearDown()
    return idle_path, trial_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-court-cases-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
