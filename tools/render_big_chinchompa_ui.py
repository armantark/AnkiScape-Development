#!/usr/bin/env python3
"""Render Big Chinchompa and its Hunter private-ground control."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QColor, QPalette  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.big_chinchompa_logic import (
    advance_big_chinchompa_world_clock_pure,
    default_big_chinchompa_state_pure,
)
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _goto_hunter,
    _make_player_data,
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


def _active_player_data() -> dict:
    player_data = _make_player_data()
    player_data.update(
        {
            "hunter_level": 99,
            "shop_market_clock": {"answered_cards": 60},
            "world_population_profile": "normal",
            "big_chinchompa": default_big_chinchompa_state_pure(),
        }
    )
    player_data["big_chinchompa"]["competence_points"] = 1_280
    player_data, _ = advance_big_chinchompa_world_clock_pure(player_data)
    return player_data


def render(
    output_dir: Path,
    *,
    width: int = 1200,
    height: int = 760,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName=(
            "test_big_chinchompa_panel_selects_event_and_runs_reward_shop"
        )
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    utility_dialog = case._open(_active_player_data())
    case._open_utility(utility_dialog)
    utility_dialog.show()
    utility_dialog.resize(width, height)
    for _ in range(8):
        app.processEvents()
    utility_path = output_dir / "big-chinchompa-utility.png"
    if not utility_dialog.grab().save(str(utility_path)):
        raise RuntimeError(f"Could not save {utility_path}")
    utility_dialog.close()

    ticket = "Swamp lizard quota ticket"
    hunter_data = _make_player_data()
    hunter_data.update(
        {
            "hunter_level": 99,
            "current_hunter": "catch_swamp_lizard",
            "carried_inventory": {
                "catch_swamp_lizard": {ticket: 2},
            },
            "hunter_private_ground_targets": ["catch_swamp_lizard"],
        }
    )
    hunter_data["inventory"].update(
        {ticket: 2, "Small fishing net": 1, "Rope": 1}
    )
    hunter_data["quests"]["priest_in_peril"] = {
        "started": True,
        "progress": 1,
        "completed": True,
    }
    hunter_dialog = case._open(hunter_data)
    _goto_hunter(hunter_dialog)
    hunter_dialog.show()
    hunter_dialog.resize(width, height)
    for _ in range(8):
        app.processEvents()
    hunter_path = output_dir / "hunter-private-ground.png"
    if not hunter_dialog.grab().save(str(hunter_path)):
        raise RuntimeError(f"Could not save {hunter_path}")
    hunter_dialog.close()

    case.tearDown()
    return utility_path, hunter_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-big-chinchompa-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(
        args.output_dir,
        width=args.width,
        height=args.height,
    ):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
