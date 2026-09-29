#!/usr/bin/env python3
"""Render ready, active, and shop Castle Wars surfaces for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

import pkg_alias  # noqa: F401  (installs the ankiscape package alias)
from ankiscape.data.castle_wars_data import CASTLE_WARS_BALLISTA_PARTS
from ankiscape.logic.castle_wars_logic import (
    apply_castle_wars_command_pure,
    apply_castle_wars_review_pure,
)
from tests.test_main_menu_widget import (
    MainMenuWidgetTest,
    _make_player_data,
    _open_reward_target,
    _utility_row,
)
from tools.render_fishing_trawler_ui import _dark_palette


def _player() -> dict:
    player = _make_player_data()
    player["castle_wars_tickets"] = 320
    player["castle_wars_games_played"] = 500
    for item_name in CASTLE_WARS_BALLISTA_PARTS:
        player["inventory"][item_name] = 1
    player["inventory"]["Ballista ammo"] = 100
    player["inventory"]["Castlewars chinchompa"] = 3
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_castle_wars_command_pure(player, action_id, payload)
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_castle_wars_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "castle_wars")
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
        methodName="test_castle_wars_detail_shop_plan_and_siege_actions_are_live"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    ready_card = _show_card(case, _player(), width, height)
    ready_path = output_dir / "castle-wars-ready.png"
    if not ready_card.grab().save(str(ready_path)):
        raise RuntimeError(f"Could not save {ready_path}")
    _open_reward_target(ready_card, "castle_wars")
    for _ in range(4):
        app.processEvents()
    shop_path = output_dir / "castle-wars-shop.png"
    if not ready_card.grab().save(str(shop_path)):
        raise RuntimeError(f"Could not save {shop_path}")
    ready_card.close()

    active = _player()
    active, ok, info = apply_castle_wars_command_pure(
        active,
        "enter",
        {"automation_mode": "advanced", "duty": "capture", "team": "zamorak"},
    )
    if not ok:
        raise RuntimeError(str(info))
    for _ in range(5):
        active, ok, result = apply_castle_wars_review_pure(
            active,
            lambda: 0.5,
            productive=True,
            duty="capture",
            opponent_roll=0.2,
        )
        if not ok:
            raise RuntimeError(str(result))
    active_card = _show_card(case, active, width, height)
    active_path = output_dir / "castle-wars-active.png"
    if not active_card.grab().save(str(active_path)):
        raise RuntimeError(f"Could not save {active_path}")
    active_card.close()

    case.tearDown()
    return ready_path, active_path, shop_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/tmp/ankiscape-castle-wars-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
