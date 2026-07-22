#!/usr/bin/env python3
"""Render ready and active Soul Wars surfaces for visual QA."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aqt.qt import QApplication  # type: ignore

from soul_wars_logic import apply_soul_wars_command_pure, apply_soul_wars_review_pure
from tests.test_main_menu_widget import MainMenuWidgetTest, _make_player_data, _utility_row
from tools.render_fishing_trawler_ui import _dark_palette


def _player() -> dict:
    player = _make_player_data()
    player.update(
        {
            "attack_level": 80,
            "strength_level": 80,
            "defense_level": 80,
            "constitution_level": 80,
            "ranged_level": 80,
            "magic_level": 80,
            "prayer_level": 80,
            "slayer_level": 80,
            "summoning_level": 1,
            "combat_supply_loadout": {"food": {}},
            "soul_wars_zeal": 42,
            "soul_wars_games_played": 9,
            "soul_wars_wins": 5,
            "soul_wars_draws": 2,
            "soul_wars_losses": 2,
        }
    )
    return player


def _show_card(case: MainMenuWidgetTest, player: dict, width: int, height: int):
    def command(action_id, payload):
        updated, ok, info = apply_soul_wars_command_pure(player, action_id, payload)
        if ok:
            player.clear()
            player.update(updated)
        return {"ok": ok, "message": info.get("reason", ""), **info}

    dialog = case._open(
        player,
        current_skill="Activities",
        on_soul_wars_command=command,
    )
    tree = case._open_activities(dialog)
    row = _utility_row(tree, "soul_wars")
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
        methodName="test_soul_wars_detail_plan_shop_and_active_state_are_live"
    )
    case.setUp()
    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication was not created by the Qt test harness")
    app.setPalette(_dark_palette())

    ready_card = _show_card(case, _player(), width, height)
    ready_path = output_dir / "soul-wars-ready.png"
    if not ready_card.grab().save(str(ready_path)):
        raise RuntimeError(f"Could not save {ready_path}")
    ready_card.close()

    active, ok, info = apply_soul_wars_command_pure(
        _player(),
        "enter",
        {"automation_mode": "advanced", "team": "creation", "duty": "defend"},
    )
    if not ok:
        raise RuntimeError(str(info))
    for _ in range(4):
        active, ok, result = apply_soul_wars_review_pure(
            active,
            lambda: 0.49,
            productive=True,
        )
        if not ok:
            raise RuntimeError(str(result))
    active_card = _show_card(case, active, width, height)
    active_path = output_dir / "soul-wars-active.png"
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
        default=Path("/tmp/ankiscape-soul-wars-ui"),
    )
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=760)
    args = parser.parse_args()
    for path in render(args.output_dir, width=args.width, height=args.height):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
