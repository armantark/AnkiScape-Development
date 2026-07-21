#!/usr/bin/env python3
"""Render the mechanic-complete Penguin Hide and Seek activity card."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QWidget  # type: ignore

from penguin_hide_and_seek_logic import default_penguin_state_pure
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _utility_row,
)
from tools.render_big_chinchompa_ui import _dark_palette


def _active_player_data() -> dict:
    player_data = _make_player_data()
    player_data.update(
        {
            "shop_market_clock": {"answered_cards": 1_680},
            "current_utility": "penguin_hide_and_seek",
            "penguin_hide_and_seek": default_penguin_state_pure(),
        }
    )
    player_data["penguin_hide_and_seek"]["points"] = 7
    player_data["quests"]["cold_war"]["completed"] = True
    player_data["quests"]["hunt_for_red_raktuber"]["completed"] = True
    return player_data


def render(output_path: Path, *, width: int = 1200, height: int = 760) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_penguin_card_selects_spy_and_redeems_points_without_scroll"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    dialog = case._open(_active_player_data())
    tree = case._open_activities(dialog)
    tree.setCurrentItem(_utility_row(tree, "penguin_hide_and_seek"))
    dialog.show()
    dialog.resize(width, height)
    for _ in range(10):
        app.processEvents()
    panel = dialog.findChild(QWidget, "penguinHideAndSeekPanel")
    if panel is None or not panel.isVisible():
        raise RuntimeError("Penguin Hide and Seek panel was not rendered")
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
        default=Path("/tmp/ankiscape-penguin-hide-and-seek-ui.png"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    print(render(args.output, width=args.width, height=args.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
