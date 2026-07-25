#!/usr/bin/env python3
"""Render the mechanic-complete Vinesweeper activity card."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QWidget  # type: ignore

from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _utility_row,
)
from tools.render_big_chinchompa_ui import _dark_palette
import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.vinesweeper_logic import default_vinesweeper_state_pure


def _active_player_data() -> dict:
    player_data = _make_player_data()
    player_data.update(
        {
            "current_utility": "vinesweeper",
            "farming_level": 40,
            "vinesweeper": default_vinesweeper_state_pure(),
        }
    )
    player_data["inventory"]["Spade"] = 1
    player_data["vinesweeper"].update(
        {
            "active": True,
            "free_flags_claimed": True,
            "flags": 7,
            "points": 4_320,
            "ogleroots": 2,
            "last_result": "Correctly flagged a seed (+180 points)",
        }
    )
    return player_data


def render(output_path: Path, *, width: int = 1200, height: int = 760) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_vinesweeper_card_enters_buys_real_rewards_and_redeems_xp"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    dialog = case._open(_active_player_data())
    tree = case._open_activities(dialog)
    vinesweeper_row = _utility_row(tree, "vinesweeper")
    tree.setCurrentItem(vinesweeper_row)
    tree.itemActivated.emit(vinesweeper_row, 0)
    dialog.show()
    dialog.resize(width, height)
    for _ in range(10):
        app.processEvents()
    panel = dialog.findChild(QWidget, "vinesweeperPanel")
    if panel is None or not panel.isVisible():
        raise RuntimeError("Vinesweeper panel was not rendered")
    if not dialog.grab().save(str(output_path)):
        raise RuntimeError(f"Could not save {output_path}")
    dialog.close()
    case.tearDown()
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/ankiscape-vinesweeper-ui.png"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    print(render(args.output, width=args.width, height=args.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
