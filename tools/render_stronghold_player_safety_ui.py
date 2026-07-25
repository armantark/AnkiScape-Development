#!/usr/bin/env python3
"""Render route and reward Stronghold of Player Safety surfaces for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.logic.stronghold_player_safety_logic import (
    apply_stronghold_player_safety_command_pure,
)
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _utility_row,
)
from tools.render_fishing_trawler_ui import _dark_palette


def _player(stage: int, *, claimed: bool = False) -> dict:
    player = _make_player_data()
    player["stronghold_player_safety"] = {
        "version": 1,
        "stage": stage,
        "crevice_unlocked": stage >= 2,
        "chest_claimed": claimed,
        "lamps_remaining": 2 if claimed else 0,
        "safety_first_emote_unlocked": claimed,
        "last_result": (
            "Opened the chest and unlocked the Safety First emote."
            if claimed
            else "Follow the jail-cell poster route to the reward chest."
        ),
    }
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_stronghold_player_safety_command_pure(
            player, action_id, payload
        )
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_stronghold_player_safety_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "stronghold_player_safety")
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


def render(
    output_dir: Path, *, width: int = 1200, height: int = 760
) -> tuple[Path, ...]:
    output_dir.mkdir(parents=True, exist_ok=True)
    MainMenuWidgetTest.setUpClass()
    case = MainMenuWidgetTest(
        methodName=(
            "test_stronghold_player_safety_chest_lamp_and_combat_entry_are_live"
        )
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    route_card = _show_card(case, _player(1), width, height)
    route_path = output_dir / "stronghold-player-safety-route.png"
    if not route_card.grab().save(str(route_path)):
        raise RuntimeError(f"Could not save {route_path}")
    route_card.close()

    reward_card = _show_card(case, _player(3, claimed=True), width, height)
    reward_path = output_dir / "stronghold-player-safety-rewards.png"
    if not reward_card.grab().save(str(reward_path)):
        raise RuntimeError(f"Could not save {reward_path}")
    reward_card.close()

    case.tearDown()
    return route_path, reward_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-stronghold-player-safety-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
