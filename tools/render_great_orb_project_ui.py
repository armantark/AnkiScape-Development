#!/usr/bin/env python3
"""Render docked and active Great Orb Project activity cards."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.great_orb_project_logic import enter_great_orb_project_pure
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _utility_row,
)
from tools.render_fishing_trawler_ui import _dark_palette


def _player() -> dict:
    player = _make_player_data()
    player.update(
        {
            "current_utility": "bankstanding",
            "runecrafting_level": 72,
            "activity_session": {"active_id": ""},
            "great_orb_project": {
                "tokens": 485,
                "games_completed": 7,
                "games_won": 4,
                "automation_mode": "advanced",
                "doctrine": "repel",
                "crafting_policy": "save_for_nature",
                "active": {},
            },
        }
    )
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    dialog = case._open(player)
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "great_orb_project")
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
        methodName="test_great_orb_project_card_saves_buys_enters_and_leaves"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    docked = _show_card(case, _player(), width, height)
    docked_path = output_dir / "great-orb-project-docked.png"
    if not docked.grab().save(str(docked_path)):
        raise RuntimeError(f"Could not save {docked_path}")
    docked.close()

    active_player, ok, info = enter_great_orb_project_pure(_player())
    if not ok:
        raise RuntimeError(str(info))
    active_player["great_orb_project"]["active"].update(
        {
            "round": 4,
            "rounds_won": 3,
            "rounds_lost": 1,
            "pending_tokens": 310,
            "saved_essence": 24,
            "xp_earned": 0.0,
        }
    )
    active = _show_card(case, active_player, width, height)
    active_path = output_dir / "great-orb-project-active.png"
    if not active.grab().save(str(active_path)):
        raise RuntimeError(f"Could not save {active_path}")
    active.close()

    case.tearDown()
    return docked_path, active_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-great-orb-project-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
