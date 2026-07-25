#!/usr/bin/env python3
"""Render ready and active Shades of Mort'ton surfaces for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.shades_of_mortton_logic import (
    apply_shades_of_mortton_command_pure,
    default_shades_of_mortton_state_pure,
)
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _utility_row
from tools.render_fishing_trawler_ui import _dark_palette


def _player() -> dict:
    player = _make_player_data()
    player.update(default_shades_of_mortton_state_pure())
    player.update(
        {
            "quests": {"shades_of_mortton": {"completed": True}},
            "crafting_level": 80,
            "firemaking_level": 80,
            "prayer_level": 80,
            "inventory": {
                "Bronze key red": 1,
                "Hammer": 1,
                "Limestone brick": 2,
                "Logs": 2,
                "Olive oil (4)": 1,
                "Sacred oil (4)": 1,
                "Swamp paste": 10,
                "Timber beam": 2,
                "Tinderbox": 1,
            },
        }
    )
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_shades_of_mortton_command_pure(
            player,
            action_id,
            payload,
            rng=lambda: 0.0,
        )
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_shades_of_mortton_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "shades_of_mortton")
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
    case = MainMenuWidgetTest(
        methodName="test_shades_of_mortton_detail_routes_plan_and_direct_actions"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    ready_card = _show_card(case, _player(), width, height)
    ready_path = output_dir / "shades-of-mortton-ready.png"
    if not ready_card.grab().save(str(ready_path)):
        raise RuntimeError(f"Could not save {ready_path}")
    ready_card.close()

    active, ok, info = apply_shades_of_mortton_command_pure(
        _player(),
        "enter",
        {"automation_mode": "advanced", "duty": "repair"},
    )
    if not ok:
        raise RuntimeError(str(info))
    active["shades_of_mortton"].update(
        {
            "temple_repair": 72,
            "sanctity_tenths": 430,
            "resources": 3,
        }
    )
    active["shades_of_mortton_repairs"] = 7
    active["shades_of_mortton_cremations"] = 2
    active["shades_of_mortton_chests_opened"] = 1
    active["shades_of_mortton_last_result"] = "Repaired the temple to 72%"
    active_card = _show_card(case, active, width, height)
    active_path = output_dir / "shades-of-mortton-active.png"
    if not active_card.grab().save(str(active_path)):
        raise RuntimeError(f"Could not save {active_path}")
    active_card.close()

    case.tearDown()
    return ready_path, active_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-shades-of-mortton-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
