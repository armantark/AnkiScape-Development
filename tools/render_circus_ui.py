#!/usr/bin/env python3
"""Render Casual and Advanced Big Top Bonanza cards for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.circus_logic import apply_circus_command_pure, default_circus_state_pure
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _utility_row
from tools.render_fishing_trawler_ui import _dark_palette


def _player() -> dict:
    player = _make_player_data()
    player["current_utility"] = "big_top_bonanza"
    player["agility_level"] = 99
    player["quests"]["the_firemakers_curse"] = {"completed": True}
    player["quests"]["some_like_it_cold"] = {"completed": True}
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_circus_command_pure(player, action_id, payload)
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_circus_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "big_top_bonanza")
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


def render(output_dir: Path, *, width: int = 1200, height: int = 760) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    # The default runTest name needs no test method, so renaming a test cannot break this render.
    case = MainMenuWidgetTest()
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    casual = _show_card(case, _player(), width, height)
    casual_path = output_dir / "circus-casual.png"
    if not casual.grab().save(str(casual_path)):
        raise RuntimeError(f"Could not save {casual_path}")
    casual.close()

    advanced = _player()
    advanced, ok, info = apply_circus_command_pure(
        advanced,
        "set_routine",
        {
            "performance_id": "agility",
            "routine": [
                "tightrope_99",
                "juggle_90",
                "tightrope_80",
                "juggle_70",
                "tightrope_60",
                "juggle_50",
                "tightrope_40",
                "juggle_30",
                "tightrope_20",
                "juggle_10",
            ],
        },
    )
    if not ok:
        raise RuntimeError(str(info))
    advanced_card = _show_card(case, advanced, width, height)
    advanced_path = output_dir / "circus-advanced.png"
    if not advanced_card.grab().save(str(advanced_path)):
        raise RuntimeError(f"Could not save {advanced_path}")
    advanced_card.close()

    firemaking = _player()
    firemaking, ok, info = apply_circus_command_pure(
        firemaking,
        "set_policy",
        {
            "performance_id": "fire_breathing",
            "automation_mode": "casual",
            "strategy": "entertain",
        },
    )
    if not ok:
        raise RuntimeError(str(info))
    firemaking_card = _show_card(case, firemaking, width, height)
    firemaking_path = output_dir / "circus-firemaking.png"
    if not firemaking_card.grab().save(str(firemaking_path)):
        raise RuntimeError(f"Could not save {firemaking_path}")
    firemaking_card.close()

    locked = _make_player_data()
    locked["current_utility"] = "big_top_bonanza"
    locked["circus"] = default_circus_state_pure()
    locked["circus"]["selected_performance"] = "fire_breathing"
    locked_card = _show_card(case, locked, width, height)
    locked_path = output_dir / "circus-locked.png"
    if not locked_card.grab().save(str(locked_path)):
        raise RuntimeError(f"Could not save {locked_path}")
    locked_card.close()

    case.tearDown()
    return casual_path, advanced_path, firemaking_path, locked_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-circus-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
