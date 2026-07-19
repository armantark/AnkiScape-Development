#!/usr/bin/env python3
"""Render the live Livid Farm Utility panel for visual review."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication, QColor, QPalette  # type: ignore

from livid_farm_data import LIVID_FARM_UNLOCKS
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


def render(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(methodName="test_livid_farm_panel_exposes_progress_and_persists_routine")
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())
    player_data = _make_player_data()
    player_data.update(
        {
            "magic_level": 99,
            "agility_level": 60,
            "crafting_level": 60,
            "farming_level": 60,
            "construction_level": 50,
            "current_utility": "livid_farm",
        }
    )
    player_data["quests"]["lunar_diplomacy"] = {"completed": True}
    player_data["livid_farm"] = {
        "farm_routine": "complete",
        "produce_points": 73_000,
        "lifetime_produce_points": 923_000,
        "cycles_completed": 584,
        "borrowed_power_claimed": True,
        "more_planks_reviews_remaining": 7,
        "unlocked_spells": tuple(
            unlock_id
            for unlock_id, _name, _threshold in LIVID_FARM_UNLOCKS
        ),
    }
    for rune_name in (
        "Astral rune",
        "Nature rune",
        "Law rune",
        "Earth rune",
        "Water rune",
    ):
        player_data["inventory"][rune_name] = 20_000

    dialog = case._open(player_data)
    case._open_utility(dialog)
    dialog.show()

    paths = []
    for width, height, suffix in (
        (1100, 650, "wide"),
        (900, 560, "laptop"),
    ):
        dialog.resize(width, height)
        for _ in range(8):
            app.processEvents()
        path = output_dir / f"livid-farm-{suffix}.png"
        if not dialog.grab().save(str(path)):
            raise RuntimeError(f"Could not save {path}")
        paths.append(path)
    dialog.close()
    case.tearDown()
    return paths[0], paths[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-livid-farm-ui"),
    )
    args = parser.parse_args()
    for path in render(args.output_dir):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
