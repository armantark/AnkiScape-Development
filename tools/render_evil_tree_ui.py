#!/usr/bin/env python3
"""Render the real Evil Tree Utility surface for repeatable visual review."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QColor, QPalette  # type: ignore

from evil_tree_logic import (
    advance_evil_tree_world_clock_pure,
    default_evil_tree_state_pure,
)
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data


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


def _scenario_player_data(scenario: str) -> dict:
    player_data = _make_player_data()
    player_data["shop_market_clock"] = {"answered_cards": 0}
    player_data["evil_tree"] = default_evil_tree_state_pure()
    if scenario == "countdown":
        return player_data

    player_data["shop_market_clock"]["answered_cards"] = 20
    if scenario == "nurture-only":
        player_data.update(
            {
                "farming_level": 99,
                "woodcutting_level": 1,
                "firemaking_level": 1,
            }
        )
        tier_roll = 0.8
    else:
        player_data.update(
            {
                "farming_level": 99,
                "woodcutting_level": 99,
                "firemaking_level": 99,
            }
        )
        tier_roll = 0.0
    player_data, _ = advance_evil_tree_world_clock_pure(
        player_data,
        tier_roll=tier_roll,
        location_roll=0.0,
    )
    return player_data


def render(output_dir: Path) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName=(
            "test_evil_tree_panel_reports_countdown_and_selects_active_event"
        )
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    paths = []
    for scenario in ("countdown", "active", "nurture-only"):
        dialog = case._open(_scenario_player_data(scenario))
        case._open_utility(dialog)
        dialog.resize(1000, 650)
        dialog.show()
        for _ in range(8):
            app.processEvents()
        path = output_dir / f"evil-tree-{scenario}.png"
        if not dialog.grab().save(str(path)):
            raise RuntimeError(f"Could not save {path}")
        paths.append(path)
        dialog.close()

    case.tearDown()
    return tuple(paths)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-evil-tree-ui"),
    )
    args = parser.parse_args()
    for path in render(args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
