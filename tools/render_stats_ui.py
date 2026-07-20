#!/usr/bin/env python3
"""Render the real Stats tab for repeatable Qt visual review."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _find_main_tabs,
    _make_player_data,
)
from tools.render_skill_panel_ui import _dark_palette, _light_palette


def render(args: argparse.Namespace) -> Path:
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_stats_tab_uses_period_three_column_grid_with_dungeoneering"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(
        _dark_palette() if args.theme == "dark" else _light_palette()
    )

    dialog = case._open(_make_player_data(), current_skill=args.skill)
    tabs = _find_main_tabs(dialog)
    stats_index = next(
        index
        for index in range(tabs.count())
        if tabs.tabText(index) == "Stats"
    )
    tabs.setCurrentIndex(stats_index)
    dialog.show()
    dialog.resize(args.width, args.height)
    for _ in range(8):
        app.processEvents()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not dialog.grab().save(str(args.output)):
        raise RuntimeError(f"Could not save {args.output}")
    dialog.close()
    case.tearDown()
    return args.output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skill", default="Mining")
    parser.add_argument("--width", type=int, default=900)
    parser.add_argument("--height", type=int, default=560)
    parser.add_argument("--theme", choices=("dark", "light"), default="dark")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(render(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
