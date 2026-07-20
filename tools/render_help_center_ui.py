#!/usr/bin/env python3
"""Render the real in-menu Help Center for repeatable visual review."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QColor, QLineEdit, QPalette, QTabWidget, QToolButton  # type: ignore

from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data


def _dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.Text, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(238, 238, 238))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(55, 130, 70))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(76, 175, 80))
    return palette


def _main_tabs(dialog) -> QTabWidget:  # type: ignore[no-untyped-def]
    return next(
        tabs
        for tabs in dialog.findChildren(QTabWidget)
        if "Skills" in [tabs.tabText(index) for index in range(tabs.count())]
        and "Grand Exchange" in [tabs.tabText(index) for index in range(tabs.count())]
    )


def render(args: argparse.Namespace) -> Path:
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_contextual_help_maps_every_primary_tab_without_changing_page"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    original_palette = app.palette()
    if args.theme == "dark":
        app.setPalette(_dark_palette())

    dialog = case._open(_make_player_data())
    tabs = _main_tabs(dialog)
    tab_index = next(
        index for index in range(tabs.count()) if tabs.tabText(index) == args.tab
    )
    tabs.setCurrentIndex(tab_index)
    dialog.show()
    dialog.findChild(QToolButton, "mainMenuHelpButton").click()
    dialog.resize(args.width, args.height)
    if args.query:
        dialog.findChild(QLineEdit, "helpSearch").setText(args.query)
    for _ in range(10):
        app.processEvents()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not dialog.grab().save(str(args.output)):
        raise RuntimeError(f"Could not save {args.output}")
    dialog.close()
    case.tearDown()
    app.setPalette(original_palette)
    return args.output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tab", default="Skills")
    parser.add_argument("--query", default="")
    parser.add_argument("--theme", choices=("light", "dark"), default="dark")
    parser.add_argument("--width", type=int, default=1400)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(render(args))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
