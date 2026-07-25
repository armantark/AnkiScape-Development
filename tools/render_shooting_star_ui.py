#!/usr/bin/env python3
"""Render the mechanic-complete Shooting Stars activity card."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QWidget  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.shooting_star_logic import (
    advance_shooting_star_world_clock_pure,
    default_shooting_star_state_pure,
)
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data
from tools.render_big_chinchompa_ui import _dark_palette


def _active_player_data() -> dict:
    player_data = _make_player_data()
    player_data.update(
        {
            "mining_level": 72,
            "shop_market_clock": {"answered_cards": 20},
            "world_population_profile": "normal",
            "current_utility": "shooting_stars",
            "shooting_star": default_shooting_star_state_pure(),
        }
    )
    player_data, _ = advance_shooting_star_world_clock_pure(player_data)
    return player_data


def render(output_path: Path, *, width: int = 1200, height: int = 760) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName="test_shooting_star_panel_selects_configures_and_exchanges"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    dialog = case._open(_active_player_data())
    case._open_activities(dialog)
    dialog.show()
    dialog.resize(width, height)
    for _ in range(8):
        app.processEvents()
    star_panel = dialog.findChild(QWidget, "shootingStarPanel")
    if star_panel is None:
        raise RuntimeError("Shooting Star panel was not rendered")
    for _ in range(4):
        app.processEvents()
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
        default=Path("/tmp/ankiscape-shooting-star-ui.png"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    print(render(args.output, width=args.width, height=args.height))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
