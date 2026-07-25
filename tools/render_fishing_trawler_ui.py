#!/usr/bin/env python3
"""Render docked and active Fishing Trawler activity cards."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QColor, QPalette  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.fishing_trawler_logic import enter_fishing_trawler_pure
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _utility_row,
)


def _dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.Text, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(55, 130, 70))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    return palette


def _player() -> dict:
    player = _make_player_data()
    player.update(
        {
            "current_utility": "bankstanding",
            "fishing_level": 81,
            "activity_session": {"active_id": ""},
        }
    )
    player["inventory"].update(
        {"Swamp paste": 60, "Rope": 4, "Bailing bucket": 1}
    )
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    dialog = case._open(player)
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "fishing_trawler")
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
        methodName=(
            "test_fishing_trawler_card_saves_plan_boards_and_returns_supplies_on_leave"
        )
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    docked = _show_card(case, _player(), width, height)
    docked_path = output_dir / "fishing-trawler-docked.png"
    if not docked.grab().save(str(docked_path)):
        raise RuntimeError(f"Could not save {docked_path}")
    docked.close()

    active_player, ok, info = enter_fishing_trawler_pure(_player())
    if not ok:
        raise RuntimeError(str(info))
    active_player["fishing_trawler"].update(
        {"review": 5, "water": 58, "leaks": 2, "net_intact": False, "contribution": 11}
    )
    active = _show_card(case, active_player, width, height)
    active_path = output_dir / "fishing-trawler-active.png"
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
        default=Path("/tmp/ankiscape-fishing-trawler-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
